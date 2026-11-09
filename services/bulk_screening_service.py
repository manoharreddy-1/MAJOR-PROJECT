"""Bulk Resume Screening & Ranking Service for Recruiters and Placement Cell."""
import csv
import io
import logging
import uuid
import zipfile
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId

from database.models import serialize_doc, utc_now
from database.mongodb import get_collection, COLLECTIONS
from parsers.pdf_parser import extract_text_from_pdf
from parsers.resume_parser import ResumeParser
from parsers.job_parser import JobDescriptionParser
from services.ats_service import ATSService
from services.job_validator_service import JobValidatorService
from utils.text_cleaner import clean_text

logger = logging.getLogger(__name__)

try:
    import docx
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False


class BulkScreeningService:
    """End-to-end bulk resume processing, cutoff filtering, ATS ranking, and batch export."""

    def __init__(self):
        self.resume_parser = ResumeParser()
        self.job_parser = JobDescriptionParser()
        self.ats_service = ATSService()
        self.validator = JobValidatorService()
        self.collection = get_collection(COLLECTIONS["bulk_batches"])

    @staticmethod
    def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
        """Extract plain text from PDF, DOCX, or TXT file bytes."""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            text, _ = extract_text_from_pdf(file_bytes)
            return text
        elif lower_name.endswith(".docx") and _DOCX_AVAILABLE:
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        paragraphs.append(" | ".join(row_cells))
            return "\n".join(paragraphs)
        elif lower_name.endswith((".txt", ".md", ".csv")):
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    return file_bytes.decode(enc)
                except UnicodeDecodeError:
                    continue
            return file_bytes.decode("utf-8", errors="ignore")
        return ""

    @classmethod
    def unpack_uploaded_files(cls, uploaded_files: List[Tuple[str, bytes]]) -> List[Tuple[str, bytes]]:
        """
        Unpack uploaded items: if any file is a .zip archive, extract all
        contained .pdf, .docx, .txt resumes; otherwise keep single files.
        """
        results = []
        for filename, content in uploaded_files:
            if filename.lower().endswith(".zip"):
                try:
                    with zipfile.ZipFile(io.BytesIO(content)) as zf:
                        for member in zf.infolist():
                            if member.is_dir():
                                continue
                            m_name = member.filename
                            base_name = m_name.split("/")[-1].split("\\")[-1]
                            if not base_name or base_name.startswith((".", "__MACOSX")):
                                continue
                            if base_name.lower().endswith((".pdf", ".docx", ".txt")):
                                results.append((base_name, zf.read(member)))
                except Exception as exc:
                    logger.warning("Failed to unpack zip %s: %s", filename, exc)
            else:
                if filename.lower().endswith((".pdf", ".docx", ".txt")):
                    results.append((filename, content))
        return results

    def process_batch(
        self,
        job_description: str,
        files: List[Tuple[str, bytes]],
        job_title: Optional[str] = None,
        cutoffs: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        batch_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a batch of resumes against a job description, apply academic cutoffs,
        rank candidates from top to least performer, and store batch history.
        """
        cutoffs = cutoffs or {}
        min_cgpa = float(cutoffs.get("min_cgpa")) if cutoffs.get("min_cgpa") is not None and str(cutoffs.get("min_cgpa")).strip() != "" else None
        min_tenth = float(cutoffs.get("min_tenth")) if cutoffs.get("min_tenth") is not None and str(cutoffs.get("min_tenth")).strip() != "" else None
        min_twelfth = float(cutoffs.get("min_twelfth")) if cutoffs.get("min_twelfth") is not None and str(cutoffs.get("min_twelfth")).strip() != "" else None
        missing_policy = str(cutoffs.get("missing_policy") or "review").strip().lower()

        # Standardize cutoffs to 10-point CGPA scale using global divisor
        from config.settings import CGPA_PERCENTAGE_DIVISOR
        std_min_cgpa = (min_cgpa / CGPA_PERCENTAGE_DIVISOR if min_cgpa > 10.0 else min_cgpa) if min_cgpa is not None else None
        std_min_tenth = (min_tenth / CGPA_PERCENTAGE_DIVISOR if min_tenth > 10.0 else min_tenth) if min_tenth is not None else None
        std_min_twelfth = (min_twelfth / CGPA_PERCENTAGE_DIVISOR if min_twelfth > 10.0 else min_twelfth) if min_twelfth is not None else None

        # Validate job title and job description alignment
        effective_title = (job_title or "").strip() or self.job_parser._extract_title(job_description)
        is_valid, err_msg, _ = self.validator.validate_title_and_description(effective_title, job_description)
        if not is_valid:
            logger.warning("Bulk screening validation failed: %s", err_msg)
            raise ValueError(err_msg)

        # Parse job description once
        parsed_job = self.job_parser.parse(job_description, title=effective_title)
        job_title = effective_title or parsed_job.get("job_title") or "Target Job Role"

        candidates = []
        for idx, (fname, fbytes) in enumerate(files, 1):
            try:
                raw_text = self.extract_text_from_file(fname, fbytes)
                cleaned = clean_text(raw_text, preserve_newlines=True)
                if len(cleaned) < 30:
                    cleaned = f"Resume {fname}\nSkills: General\nEducation: Graduate"

                parsed_resume = self.resume_parser.parse(cleaned)
            except Exception as e:
                logger.warning("Error parsing file %s: %s", fname, e)
                parsed_resume = {
                    "raw_text": "",
                    "name": fname.rsplit(".", 1)[0],
                    "email": None,
                    "phone": None,
                    "skills": [],
                    "experience": [],
                    "education": [],
                    "projects": [],
                    "academics": {"cgpa": None, "tenth_pct": None, "twelfth_pct": None},
                }

            # Standardized 10-Point Academic Cutoff Verification
            academics = parsed_resume.get("academics") or {}
            deg_obj = academics.get("degree") or {}
            tenth_obj = academics.get("tenth") or {}
            twelfth_obj = academics.get("twelfth") or {}

            cand_deg_cgpa = deg_obj.get("standardized_cgpa") if isinstance(deg_obj, dict) else academics.get("cgpa")
            cand_tenth_cgpa = tenth_obj.get("standardized_cgpa") if isinstance(tenth_obj, dict) else (
                (academics.get("tenth_pct") / CGPA_PERCENTAGE_DIVISOR) if academics.get("tenth_pct") is not None else None
            )
            cand_twelfth_cgpa = twelfth_obj.get("standardized_cgpa") if isinstance(twelfth_obj, dict) else (
                (academics.get("twelfth_pct") / CGPA_PERCENTAGE_DIVISOR) if academics.get("twelfth_pct") is not None else None
            )

            below_reasons = []
            missing_fields = []

            # 1. Degree Cutoff check
            if std_min_cgpa is not None:
                if cand_deg_cgpa is None:
                    missing_fields.append(f"Degree CGPA not found (Min {std_min_cgpa:.2f} required)")
                elif cand_deg_cgpa < (std_min_cgpa - 0.001):
                    below_reasons.append(f"Degree CGPA {cand_deg_cgpa:.2f} < Min {std_min_cgpa:.2f}")

            # 2. 10th Cutoff check
            if std_min_tenth is not None:
                if cand_tenth_cgpa is None:
                    missing_fields.append(f"10th marks not found (Min {std_min_tenth:.2f} required)")
                elif cand_tenth_cgpa < (std_min_tenth - 0.001):
                    below_reasons.append(f"10th CGPA {cand_tenth_cgpa:.2f} < Min {std_min_tenth:.2f}")

            # 3. 12th / Diploma Cutoff check
            if std_min_twelfth is not None:
                if cand_twelfth_cgpa is None:
                    missing_fields.append(f"12th/Diploma marks not found (Min {std_min_twelfth:.2f} required)")
                elif cand_twelfth_cgpa < (std_min_twelfth - 0.001):
                    sec_label = "Diploma" if (isinstance(twelfth_obj, dict) and twelfth_obj.get("is_diploma")) else "12th"
                    below_reasons.append(f"{sec_label} CGPA {cand_twelfth_cgpa:.2f} < Min {std_min_twelfth:.2f}")

            # Determine eligibility category based on policy
            if below_reasons:
                is_eligible = False
                eligibility_category = "below"
                cutoff_status = f"Below Cutoff ({', '.join(below_reasons)})"
            elif missing_fields:
                if missing_policy == "ineligible":
                    is_eligible = False
                    eligibility_category = "below"
                    cutoff_status = f"Below Cutoff ({', '.join(missing_fields)})"
                elif missing_policy == "ignore":
                    is_eligible = True
                    eligibility_category = "eligible"
                    cutoff_status = "Eligible (Missing criteria ignored)"
                else:  # "review" (default)
                    is_eligible = True  # Not rejected as below cutoff
                    eligibility_category = "review"
                    cutoff_status = f"Needs Review ({', '.join(missing_fields)})"
            else:
                is_eligible = True
                eligibility_category = "eligible"
                cutoff_status = "Eligible"

            cgpa = cand_deg_cgpa
            tenth = academics.get("tenth_pct")
            twelfth = academics.get("twelfth_pct")
            cutoff_reasons = below_reasons + missing_fields

            # ATS Scoring
            try:
                ats_result = self.ats_service.analyze(parsed_resume, parsed_job, target_role=job_title)
                overall_score = ats_result["scores"]["overall"]
                skill_score = ats_result["scores"]["skills"]
                semantic_score = ats_result["scores"]["semantic"]
                match_label = ats_result.get("match_label") or "Match"
                skill_analysis = ats_result.get("skill_analysis") or {}

                # 1. Extract key matched skills (from 'matched' list of dicts/strings)
                raw_matched = skill_analysis.get("matched") or skill_analysis.get("matched_skills") or []
                matched_skills = [
                    (s.get("skill") if isinstance(s, dict) else str(s)).strip()
                    for s in raw_matched
                    if (isinstance(s, dict) and s.get("skill")) or (isinstance(s, str) and s.strip())
                ]

                # 2. Extract missing skills (from 'missing' list of dicts/strings)
                raw_missing = skill_analysis.get("missing") or skill_analysis.get("missing_skills") or []
                missing_skills = [
                    (s.get("skill") if isinstance(s, dict) else str(s)).strip()
                    for s in raw_missing
                    if (isinstance(s, dict) and s.get("skill")) or (isinstance(s, str) and s.strip())
                ]

                # Graceful fallback: If matched_skills is empty, check overlap with candidate's parsed skills
                if not matched_skills:
                    cand_skills = parsed_resume.get("skills", [])
                    job_req = parsed_job.get("required_skills", []) + parsed_job.get("technologies", [])
                    cand_map = {s.lower().strip(): s.strip() for s in cand_skills if isinstance(s, str)}
                    for req in job_req:
                        if isinstance(req, str) and req.lower().strip() in cand_map:
                            matched_skills.append(cand_map[req.lower().strip()])
                    matched_skills = list(dict.fromkeys(matched_skills))

                # Graceful fallback: If missing_skills is empty, check remaining required skills
                if not missing_skills:
                    matched_lower = {s.lower() for s in matched_skills}
                    cand_skills_lower = {s.lower() for s in parsed_resume.get("skills", []) if isinstance(s, str)}
                    known = matched_lower.union(cand_skills_lower)
                    for req in parsed_job.get("required_skills", []):
                        if isinstance(req, str) and req.lower().strip() not in known:
                            missing_skills.append(req.strip())
                    missing_skills = list(dict.fromkeys(missing_skills))

            except Exception as exc:
                logger.error("ATS calculation failed for %s: %s", fname, exc)
                overall_score = 40.0
                skill_score = 40.0
                semantic_score = 40.0
                match_label = "Moderate Match"
                matched_skills = [s if isinstance(s, str) else s.get("skill", "") for s in parsed_resume.get("skills", [])[:5]]
                missing_skills = [s if isinstance(s, str) else s.get("skill", "") for s in parsed_job.get("required_skills", [])[:5]]

            candidate_name = parsed_resume.get("name") or fname.rsplit(".", 1)[0]
            if len(candidate_name) > 40 or "\n" in candidate_name:
                candidate_name = fname.rsplit(".", 1)[0]

            candidates.append({
                "candidate_id": f"cand_{idx:04d}",
                "candidate_name": candidate_name,
                "filename": fname,
                "email": parsed_resume.get("email") or "Not provided",
                "phone": parsed_resume.get("phone") or "Not provided",
                "cgpa": cgpa,
                "tenth_pct": tenth,
                "twelfth_pct": twelfth,
                "academics": academics,
                "eligibility_category": eligibility_category,
                "needs_review": (eligibility_category == "review"),
                "ats_score": round(overall_score, 1),
                "skill_score": round(skill_score, 1),
                "semantic_score": round(semantic_score, 1),
                "match_label": match_label,
                "is_eligible": is_eligible,
                "cutoff_status": cutoff_status,
                "cutoff_reasons": cutoff_reasons,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "all_skills": parsed_resume.get("skills", [])[:12],
            })

        # Rank candidates:
        # 1. Eligibility status: Eligible (0), Needs Review (1), Below Cutoff (2)
        # 2. Highest ATS match score first
        # 3. Highest degree CGPA first (tie-breaker)
        # 4. Candidate name (alphabetical tie-breaker)
        def candidate_ranking_key(c):
            cat = c.get("eligibility_category")
            if cat == "eligible":
                group_rank = 0
            elif cat == "review":
                group_rank = 1
            elif c.get("is_eligible"):
                group_rank = 0
            else:
                group_rank = 2
            ats_score = float(c.get("ats_score", 0.0))
            deg_cgpa = float(c.get("cgpa") or 0.0)
            cand_name = str(c.get("candidate_name") or "").lower()
            return (group_rank, -ats_score, -deg_cgpa, cand_name)

        candidates.sort(key=candidate_ranking_key)

        # Assign 1-indexed rank
        for rank_idx, cand in enumerate(candidates, 1):
            cand["rank"] = rank_idx

        # Compute Batch Aggregates
        total_resumes = len(candidates)
        eligible_count = sum(1 for c in candidates if c.get("eligibility_category") == "eligible")
        needs_review_count = sum(1 for c in candidates if c.get("eligibility_category") == "review")
        below_cutoff_count = sum(1 for c in candidates if c.get("eligibility_category") == "below")
        if eligible_count == 0 and needs_review_count == 0 and below_cutoff_count == 0:
            eligible_count = sum(1 for c in candidates if c["is_eligible"])
            below_cutoff_count = total_resumes - eligible_count

        avg_score = round(sum(c["ats_score"] for c in candidates) / total_resumes, 1) if total_resumes > 0 else 0.0
        top_score = max((c["ats_score"] for c in candidates), default=0.0)

        batch_id = f"batch_{uuid.uuid4().hex[:10]}"
        batch_doc = {
            "batch_id": batch_id,
            "batch_name": batch_name or f"{job_title} Screening ({total_resumes} Candidates)",
            "user_id": user_id,
            "job_title": job_title,
            "job_description": job_description[:1000],
            "required_skills": parsed_job.get("required_skills", []),
            "cutoffs": {
                "min_cgpa": min_cgpa,
                "min_tenth": min_tenth,
                "min_twelfth": min_twelfth,
                "missing_policy": missing_policy,
            },
            "total_resumes": total_resumes,
            "eligible_count": eligible_count,
            "needs_review_count": needs_review_count,
            "below_cutoff_count": below_cutoff_count,
            "avg_score": avg_score,
            "top_score": top_score,
            "candidates": candidates,
            "created_at": utc_now(),
        }

        self.collection.insert_one(batch_doc)
        return serialize_doc(batch_doc)

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve batch by batch_id with auto-healing for any legacy empty skill lists."""
        doc = self.collection.find_one({"batch_id": batch_id})
        if not doc:
            return None

        # Auto-heal: If any candidate has empty matched_skills or missing_skills, populate from all_skills & required_skills
        req_skills = doc.get("required_skills") or []
        updated = False
        candidates = doc.get("candidates", [])
        for c in candidates:
            all_s = c.get("all_skills") or []
            if not c.get("matched_skills"):
                c_map = {s.lower().strip(): s.strip() for s in all_s if isinstance(s, str)}
                matched = [c_map[r.lower().strip()] for r in req_skills if isinstance(r, str) and r.lower().strip() in c_map]
                if not matched and all_s:
                    matched = all_s[:4]
                c["matched_skills"] = matched
                updated = True

            if not c.get("missing_skills"):
                c_matched_lower = {s.lower().strip() for s in c.get("matched_skills", []) if isinstance(s, str)}
                all_s_lower = {s.lower().strip() for s in all_s if isinstance(s, str)}
                known = c_matched_lower.union(all_s_lower)
                missing = [r.strip() for r in req_skills if isinstance(r, str) and r.lower().strip() not in known]
                c["missing_skills"] = missing[:5]
                updated = True

        if updated:
            self.collection.update_one({"batch_id": batch_id}, {"$set": {"candidates": candidates}})

        return serialize_doc(doc)

    def list_batches(self, user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List historical screening batches, optionally filtered by user_id."""
        query = {"user_id": user_id} if user_id else {}
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        results = []
        for doc in cursor:
            s_doc = serialize_doc(doc)
            # Remove full candidate list from summary list to keep payload light
            s_doc.pop("candidates", None)
            results.append(s_doc)
        return results

    @staticmethod
    def generate_csv_export(batch: Dict[str, Any]) -> str:
        """Generate formatted CSV string of ranked candidates with standardized academics."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header info
        writer.writerow(["Rank", "Candidate Name", "Eligibility Status", "ATS Score (%)", "CGPA", "10th (%)", "12th (%)", "Email", "Phone", "Matched Skills", "Missing Skills", "Filename"])

        for cand in batch.get("candidates", []):
            acad = cand.get("academics") or {}
            deg_val = acad.get("degree", {}).get("standardized_cgpa") or cand.get("cgpa")
            deg_text = f"{deg_val:.2f}" if deg_val is not None else "Not found"

            tenth_info = acad.get("tenth", {}) if isinstance(acad, dict) else {}
            if tenth_info.get("standardized_cgpa") is not None:
                orig = f" ({tenth_info['original_text']})" if tenth_info.get("original_text") else ""
                tenth_text = f"{tenth_info['standardized_cgpa']:.2f} CGPA{orig}"
            elif cand.get("tenth_pct") is not None:
                tenth_text = f"{cand.get('tenth_pct')}%"
            else:
                tenth_text = "Not found"

            twelfth_info = acad.get("twelfth", {}) if isinstance(acad, dict) else {}
            if twelfth_info.get("standardized_cgpa") is not None:
                orig = f" ({twelfth_info['original_text']})" if twelfth_info.get("original_text") else ""
                twelfth_text = f"{twelfth_info['standardized_cgpa']:.2f} CGPA{orig}"
            elif cand.get("twelfth_pct") is not None:
                twelfth_text = f"{cand.get('twelfth_pct')}%"
            else:
                twelfth_text = "Not found"

            writer.writerow([
                cand.get("rank"),
                cand.get("candidate_name"),
                cand.get("cutoff_status"),
                cand.get("ats_score"),
                deg_text,
                tenth_text,
                twelfth_text,
                cand.get("email"),
                cand.get("phone"),
                "; ".join(cand.get("matched_skills", [])),
                "; ".join(cand.get("missing_skills", [])),
                cand.get("filename"),
            ])

        return output.getvalue()
