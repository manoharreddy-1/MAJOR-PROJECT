"""Comprehensive Unit Tests for Academic Parser, Normalization & Bulk Screening Cutoffs."""
import os
import pytest
from parsers.academic_parser import AcademicParser, parse_numeric_score, clean_spaced_digits
from services.bulk_screening_service import BulkScreeningService


class TestAcademicScoreParser:
    """Test individual score standardization across all formats and scales."""

    def test_direct_cgpa(self):
        s = parse_numeric_score("CGPA: 8.7")
        assert s["standardized_cgpa"] == 8.70
        assert s["original_type"] == "cgpa"

        s2 = parse_numeric_score("9.8 GPA")
        assert s2["standardized_cgpa"] == 9.80

        s3 = parse_numeric_score("8.7/10")
        assert s3["standardized_cgpa"] == 8.70

    def test_percentage_conversion(self):
        # 95% / 9.5 = 10.00
        s = parse_numeric_score("95%")
        assert s["standardized_cgpa"] == 10.00
        assert s["original_type"] == "percentage"

        # 85% / 9.5 = 8.95
        s2 = parse_numeric_score("85%")
        assert s2["standardized_cgpa"] == 8.95

        # 92.8% / 9.5 = 9.77
        s3 = parse_numeric_score("92.8%")
        assert s3["standardized_cgpa"] == 9.77

        # Spaced percentage
        s4 = parse_numeric_score("Percentage: 92.8")
        assert s4["standardized_cgpa"] == 9.77

    def test_marks_out_of_total(self):
        # 470/500 = 94.0% -> 94.0 / 9.5 = 9.89
        s = parse_numeric_score("470/500")
        assert s["standardized_cgpa"] == 9.89
        assert s["original_type"] == "marks"

        # 960/1000 = 96.0% -> 96.0 / 9.5 = 10.00
        s2 = parse_numeric_score("960/1000")
        assert s2["standardized_cgpa"] == 10.00

        s3 = parse_numeric_score("980 out of 1000")
        assert s3["standardized_cgpa"] == 10.00

    def test_other_scales(self):
        # 3.6/4 -> (3.6/4)*10 = 9.00
        s1 = parse_numeric_score("3.6/4")
        assert s1["standardized_cgpa"] == 9.00

        # 4.2/5 -> (4.2/5)*10 = 8.40
        s2 = parse_numeric_score("4.2/5")
        assert s2["standardized_cgpa"] == 8.40

    def test_spaced_digits(self):
        assert clean_spaced_digits("8 . 7") == "8.7"
        assert clean_spaced_digits("9 . 8 / 10") == "9.8/10"
        assert clean_spaced_digits("9 2 . 8 %") == "92.8%"
        # Ensure 4-digit years are NEVER mashed with scores
        assert clean_spaced_digits("2024 8.83") == "2024 8.83"
        assert clean_spaced_digits("2020   9.5") == "2020   9.5"

        s = parse_numeric_score("8 . 7 CGPA")
        assert s["standardized_cgpa"] == 8.70

    def test_integer_10_cgpa(self):
        s1 = parse_numeric_score("10")
        assert s1["standardized_cgpa"] == 10.00
        assert s1["original_type"] == "assumed"

        s2 = parse_numeric_score("10.0")
        assert s2["standardized_cgpa"] == 10.00

        # Class 10 is class level, not CGPA
        assert parse_numeric_score("Class 10 2018") is None

    def test_rank_and_year_rejection(self):
        # Must not misinterpret Rank 17/100 as 17%
        assert parse_numeric_score("Rank 17/100") is None
        assert parse_numeric_score("2016-17/100") is None
        assert parse_numeric_score("2020/2024") is None

    def test_dash_separated_scores(self):
        s = parse_numeric_score("Secondary Education - 9.8 GPA")
        assert s["standardized_cgpa"] == 9.80

    def test_invalid_values(self):
        assert parse_numeric_score("-5.0") is None
        assert parse_numeric_score("0.0") is None
        # Year should not be treated as mark
        assert parse_numeric_score("2024") is None


class TestAcademicSectionExtraction:
    """Test full resume text parsing across 10th, 12th, degree, and diploma."""

    @pytest.fixture
    def parser(self):
        return AcademicParser()

    @pytest.mark.parametrize("line,expected_cgpa", [
        ("10th: 98%", 10.00),
        ("SSC – 9.8 GPA", 9.80),
        ("Class X: CGPA 9.8/10", 9.80),
        ("Secondary School Certificate 470/500", 9.89),
        ("Matriculation 92.8 %", 9.77),
        ("X (CBSE) 94.2", 9.92),
        ("Tenth – 9.5 CGPA", 9.50),
        ("High School: 85%", 8.95),
        ("Class 10th: 9.8/10.0", 9.80),
    ])
    def test_tenth_variants(self, parser, line, expected_cgpa):
        text = f"Education Background:\n{line}\nSkills: Python"
        res = parser.extract_academics(text, fallback_to_ai=False)
        actual = res["tenth"]["standardized_cgpa"]
        assert actual is not None
        assert abs(actual - expected_cgpa) <= 0.05

    @pytest.mark.parametrize("line,expected_cgpa,is_diploma", [
        ("Intermediate (MPC): 960/1000", 10.00, False),
        ("12th Board: 92.8%", 9.77, False),
        ("XII – 9.2 GPA", 9.20, False),
        ("HSC 83.3%", 8.77, False),
        ("Diploma in CSE: 85%", 8.95, True),
        ("Plus Two 95.3 %", 10.00, False),
        ("Senior Secondary: 88%", 9.26, False),
    ])
    def test_twelfth_and_diploma_variants(self, parser, line, expected_cgpa, is_diploma):
        text = f"Education:\n{line}\nProjects: Machine Learning"
        res = parser.extract_academics(text, fallback_to_ai=False)
        actual = res["twelfth"]["standardized_cgpa"]
        assert actual is not None
        assert abs(actual - expected_cgpa) <= 0.05
        assert res["twelfth"]["is_diploma"] == is_diploma

    def test_table_layout_pipe_delimited(self, parser):
        table_text = """
        Education:
        Examination | Institution | Board | Year | Percentage/CGPA
        B.Tech CSE | ABC Institute of Tech | Autonomous | 2024 | 8.75 CGPA
        Class XII | XYZ Junior College | State Board | 2020 | 94.5%
        Class X | ZPH High School | BSE | 2018 | 9.8 GPA
        """
        res = parser.extract_academics(table_text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.75
        assert res["twelfth"]["standardized_cgpa"] == 9.95
        assert res["tenth"]["standardized_cgpa"] == 9.80

    def test_value_on_next_line(self, parser):
        text = """
        Education:
        B.Tech in Computer Science
        Vellore Institute of Technology
        CGPA: 8.9 / 10

        Higher Secondary Certificate (HSC)
        91.5%

        Secondary School Certificate (SSC)
        88.0%
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.90
        assert res["twelfth"]["standardized_cgpa"] == 9.63
        assert res["tenth"]["standardized_cgpa"] == 9.26

    def test_space_separated_table_resumes(self, parser):
        # Space-separated / borderless table format
        text = """
        Education
        B. Tech in Computer Science and Engineering   Pragati Engineering College   2024   8.64/10
        Intermediate (MPC)   Sri Chaitanya Junior College   2020   960/1000
        Secondary School Certificate   Z.P. High School   2018   10.0
        Skills: Java, React, SQL
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.64
        assert res["twelfth"]["standardized_cgpa"] == 10.00
        assert res["tenth"]["standardized_cgpa"] == 10.00

    def test_b_tech_and_secondary_formats(self, parser):
        text = """
        Education:
        B. Tech in Artificial Intelligence and Machine Learning
        Pragati Engineering College, CGPA: 8.77/10
        Intermediate Education (BIEAP)
        Aditya Junior College, 2018-2020: 95.8%
        Secondary Education (SSC)
        ZPH School, 2016-17: 9.8 CGPA (Rank 17/100)
        Skills: Java, Python, SQL
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.77
        assert res["twelfth"]["standardized_cgpa"] == 10.00
        assert res["tenth"]["standardized_cgpa"] == 9.80

    def test_value_before_label(self, parser):
        text = """
        Education:
        Graduated with 8.6 CGPA in B.Tech Mechanical Engineering.
        Secured 91.2% in Class 12th Board examinations.
        Scored 94.0% in Class 10th High School.
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.60
        assert res["twelfth"]["standardized_cgpa"] == 9.60
        assert res["tenth"]["standardized_cgpa"] == 9.89

    def test_degree_present_school_absent(self, parser):
        text = """
        John Doe
        john@example.com
        Education:
        B.Tech Computer Science & Engineering - CGPA: 8.2 / 10
        Skills: Java, Spring Boot, MySQL
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.20
        assert res["tenth"]["standardized_cgpa"] is None
        assert res["tenth"]["original_text"] == "Not found"
        assert res["tenth"]["needs_review"] is True
        assert res["twelfth"]["standardized_cgpa"] is None
        assert res["twelfth"]["original_text"] == "Not found"
        assert res["twelfth"]["needs_review"] is True

    def test_similar_numbers_no_mixups(self, parser):
        text = """
        Education:
        B.Tech Computer Science: CGPA 8.5
        12th Standard: 85%
        10th Standard: 85%
        """
        res = parser.extract_academics(text, fallback_to_ai=False)
        assert res["degree"]["standardized_cgpa"] == 8.50
        assert res["twelfth"]["original_text"] == "85%"
        assert res["twelfth"]["standardized_cgpa"] == 8.95
        assert res["tenth"]["original_text"] == "85%"
        assert res["tenth"]["standardized_cgpa"] == 8.95


class TestBulkCutoffsAndRanking:
    """Verify cutoff logic, missing data policy, and ATS score ordering."""

    def test_cutoffs_missing_data_review_policy(self):
        service = BulkScreeningService()
        job_desc = "Software Engineer. Required: Python, SQL, REST APIs."

        res_complete = "Cand Complete\nEmail: c1@test.com\nEducation:\nB.Tech CSE: 8.5 CGPA\n12th: 90%\n10th: 90%\nSkills: Python, SQL, REST APIs"
        res_missing_school = "Cand Missing School\nEmail: c2@test.com\nEducation:\nB.Tech CSE: 8.8 CGPA\nSkills: Python, SQL, REST APIs"
        res_low_cgpa = "Cand Low CGPA\nEmail: c3@test.com\nEducation:\nB.Tech CSE: 6.0 CGPA\n12th: 90%\n10th: 90%\nSkills: Python, SQL, REST APIs"

        files = [
            ("cand_complete.txt", res_complete.encode("utf-8")),
            ("cand_missing.txt", res_missing_school.encode("utf-8")),
            ("cand_low.txt", res_low_cgpa.encode("utf-8")),
        ]

        # Cutoffs: Min CGPA 7.5, Min 10th 70%, Min 12th 70%
        # Default policy: missing_policy = "review"
        batch = service.process_batch(
            job_description=job_desc,
            files=files,
            job_title="Software Engineer",
            cutoffs={"min_cgpa": 7.5, "min_tenth": 70, "min_twelfth": 70, "missing_policy": "review"}
        )

        candidates = {c["filename"]: c for c in batch["candidates"]}

        # Complete candidate meets all cutoffs -> Eligible
        assert candidates["cand_complete.txt"]["is_eligible"] is True
        assert candidates["cand_complete.txt"]["eligibility_category"] == "eligible"

        # Missing candidate must NOT be labeled Below Cutoff!
        assert candidates["cand_missing.txt"]["eligibility_category"] == "review"
        assert "Needs Review" in candidates["cand_missing.txt"]["cutoff_status"]
        assert candidates["cand_missing.txt"]["needs_review"] is True

        # Low CGPA candidate is confirmed below cutoff
        assert candidates["cand_low.txt"]["is_eligible"] is False
        assert candidates["cand_low.txt"]["eligibility_category"] == "below"
        assert "Below Cutoff" in candidates["cand_low.txt"]["cutoff_status"]

    def test_cutoffs_missing_data_ineligible_policy(self):
        service = BulkScreeningService()
        job_desc = "Software Engineer. Required: Python, SQL."
        res_missing = "Cand Missing\nEmail: m@test.com\nEducation:\nB.Tech: 8.0 CGPA\nSkills: Python, SQL"

        batch = service.process_batch(
            job_description=job_desc,
            files=[("m.txt", res_missing.encode("utf-8"))],
            job_title="Software Engineer",
            cutoffs={"min_tenth": 70, "missing_policy": "ineligible"}
        )
        cand = batch["candidates"][0]
        assert cand["is_eligible"] is False
        assert cand["eligibility_category"] == "below"

    def test_cutoffs_missing_data_ignore_policy(self):
        service = BulkScreeningService()
        job_desc = "Software Engineer. Required: Python, SQL."
        res_missing = "Cand Missing\nEmail: m@test.com\nEducation:\nB.Tech: 8.0 CGPA\nSkills: Python, SQL"

        batch = service.process_batch(
            job_description=job_desc,
            files=[("m.txt", res_missing.encode("utf-8"))],
            job_title="Software Engineer",
            cutoffs={"min_tenth": 70, "missing_policy": "ignore"}
        )
        cand = batch["candidates"][0]
        assert cand["is_eligible"] is True
        assert cand["eligibility_category"] == "eligible"

    def test_ranking_highest_ats_score_first(self):
        service = BulkScreeningService()
        job_desc = "AI Engineer. Required: Python, PyTorch, LLMs, NLP, Docker."

        # High ATS score (has all skills) but lower CGPA (7.6)
        res_high_ats = "High ATS\nEmail: h@test.com\nEducation:\nB.Tech: 7.6 CGPA\nSkills: Python, PyTorch, LLMs, NLP, Docker"

        # Med ATS score (missing Docker) but high CGPA (9.5)
        res_high_cgpa = "High CGPA\nEmail: c@test.com\nEducation:\nB.Tech: 9.5 CGPA\nSkills: Python, PyTorch"

        files = [
            ("high_cgpa.txt", res_high_cgpa.encode("utf-8")),
            ("high_ats.txt", res_high_ats.encode("utf-8")),
        ]

        batch = service.process_batch(
            job_description=job_desc,
            files=files,
            job_title="AI Engineer",
            cutoffs={"min_cgpa": 7.0}
        )

        candidates = batch["candidates"]
        assert len(candidates) == 2
        # Rank 1 must be High ATS candidate!
        assert candidates[0]["candidate_name"] == "High ATS"
        assert candidates[0]["rank"] == 1
        assert candidates[1]["candidate_name"] == "High CGPA"
        assert candidates[1]["rank"] == 2
