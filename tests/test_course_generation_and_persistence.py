"""Comprehensive verification tests for:
1. Skill Gap Analysis -> 'Generate AI Course' skill fidelity (Spring, Spring Boot, Hibernate, Maven, C++, Node.js).
2. YouTube tutorial videos relevant to each skill and chapter.
3. Course persistence linked to user account in MongoDB.
4. User authorization and cross-user course isolation (no data leakage).
5. Chapter progress persistence (completed_chapters).
6. Duplicate course handling.
7. Job Title and JD gibberish / personal name validation.
"""
import pytest
from services.course_content_catalog import get_curated_course, generate_smart_curriculum
from services.course_service import CourseService
from services.job_validator_service import JobValidatorService


class TestCourseSkillFidelity:
    def setup_method(self):
        self.service = CourseService()

    def test_spring_course_fidelity_never_returns_java(self):
        """Spring course must have Spring title, Spring chapters, and Spring videos."""
        res = self.service.generate_course_layout("Spring", user_id="user_test_spring")
        course = res["course"]

        # Name and chapters must be about Spring
        assert "Spring" in course["name"]
        chapter_names = [ch["name"] for ch in course["chapters_outline"]]
        assert any("IoC" in n or "Spring" in n for n in chapter_names)
        assert not any("Java Basics" in n or "Java Syntax" in n for n in chapter_names)

        # Video must be Spring tutorial, not Java tutorial
        video = self.service.fetch_youtube_video("Spring Framework Architecture & IoC Container")
        assert video is not None
        assert video["video_id"] != "eIrMbAQSU34"  # NOT Java for beginners!
        assert "Spring" in video["title"]

    def test_spring_boot_course_fidelity(self):
        """Spring Boot course must focus on Spring Boot, Starters, Actuator."""
        res = self.service.generate_course_layout("Spring Boot", user_id="user_test_boot")
        course = res["course"]
        assert "Spring Boot" in course["name"]
        chapter_names = [ch["name"] for ch in course["chapters_outline"]]
        assert any("Auto-Configuration" in n or "Spring Boot" in n for n in chapter_names)

    def test_hibernate_course_fidelity(self):
        """Hibernate course must focus on ORM, JPA, Criteria API."""
        res = self.service.generate_course_layout("Hibernate", user_id="user_test_hib")
        course = res["course"]
        assert "Hibernate" in course["name"] or "ORM" in course["name"]
        chapter_names = [ch["name"] for ch in course["chapters_outline"]]
        assert any("ORM" in n or "Hibernate" in n or "JPA" in n for n in chapter_names)

    def test_maven_and_node_fidelity(self):
        """Maven and Node.js each produce dedicated matching curricula."""
        res_maven = self.service.generate_course_layout("Maven", user_id="user_test_maven")
        assert "Maven" in res_maven["course"]["name"]

        res_node = self.service.generate_course_layout("Node.js", user_id="user_test_node")
        assert "Node" in res_node["course"]["name"]
        node_chapters = [ch["name"] for ch in res_node["course"]["chapters_outline"]]
        assert any("Node" in n or "Express" in n for n in node_chapters)

    def test_cpp_special_characters(self):
        """C++ produces a dedicated course without regex or escaping issues."""
        res_cpp = self.service.generate_course_layout("C++", user_id="user_test_cpp")
        assert "C++" in res_cpp["course"]["name"]
        video = self.service.fetch_youtube_video("C++ Fundamentals")
        assert video is not None
        assert video["video_id"] == "vLnPwxZdW4Y"


class TestCoursePersistenceAndAuthorization:
    def setup_method(self):
        self.service = CourseService()

    def test_course_persisted_to_user_account(self):
        """Course is saved with user_id and can be retrieved by owner."""
        user_id = "user_persisted_123"
        res = self.service.generate_course_layout("FastAPI", user_id=user_id)
        course_id = res["course_id"]

        details = self.service.get_course_details(course_id, user_id=user_id)
        assert details is not None
        assert details["course_id"] == course_id
        assert details["user_id"] == user_id
        assert details["name"] == "FastAPI"

    def test_cross_user_isolation_forbidden(self):
        """Another user cannot view or access the first user's course."""
        owner_id = "user_alice"
        attacker_id = "user_bob"

        res = self.service.generate_course_layout("Docker", user_id=owner_id)
        course_id = res["course_id"]

        # Owner can view
        owner_view = self.service.get_course_details(course_id, user_id=owner_id)
        assert owner_view is not None

        # Attacker cannot view - raises PermissionError
        with pytest.raises(PermissionError):
            self.service.get_course_details(course_id, user_id=attacker_id)

    def test_user_course_listing_isolation(self):
        """User course listing only returns courses owned by that user."""
        u1 = "user_list_1"
        u2 = "user_list_2"

        self.service.generate_course_layout("Git", user_id=u1)
        self.service.generate_course_layout("MySQL", user_id=u2)

        u1_courses = self.service.list_courses(user_id=u1)
        u1_skills = [c.get("skill") or c.get("name") for c in u1_courses]
        assert "Git" in u1_skills
        assert "MySQL" not in u1_skills

    def test_chapter_progress_persistence(self):
        """Mark as completed persists across sessions in user account."""
        user_id = "user_progress_test"
        res = self.service.generate_course_layout("Django", user_id=user_id)
        course_id = res["course_id"]

        # Complete chapter 1 and 2
        p1 = self.service.update_chapter_progress(course_id, user_id, chapter_id=1, completed=True)
        assert 1 in p1["completed_chapters"]

        p2 = self.service.update_chapter_progress(course_id, user_id, chapter_id=2, completed=True)
        assert 1 in p2["completed_chapters"]
        assert 2 in p2["completed_chapters"]

        # Retrieve course details and verify completed_chapters exists
        details = self.service.get_course_details(course_id, user_id=user_id)
        assert 1 in details.get("completed_chapters", [])
        assert 2 in details.get("completed_chapters", [])

    def test_duplicate_course_lookup(self):
        """Existing course for the same skill is identified for duplicate prompting."""
        user_id = "user_dup_test"
        skill = "PostgreSQL"
        res = self.service.generate_course_layout(skill, user_id=user_id)
        course_id = res["course_id"]

        dup = self.service.get_user_course_by_skill(user_id, skill)
        assert dup is not None
        assert dup["course_id"] == course_id

        # Case-insensitive duplicate check
        dup_lower = self.service.get_user_course_by_skill(user_id, "postgresql")
        assert dup_lower is not None
        assert dup_lower["course_id"] == course_id


class TestJobRoleAndJDValidationEdgeCases:
    def setup_method(self):
        self.validator = JobValidatorService()

    def test_reject_gibberish_job_description(self):
        """Target role driver with nonsense keyboard mashing is rejected."""
        valid, msg, _ = self.validator.validate_title_and_description(
            "driver",
            "manohar is a goodf aijdnia iuendijnsdc iuebenfijsdij iunfsdj h scc"
        )
        assert valid is False
        assert "nonsense" in msg.lower() or "gibberish" in msg.lower()

    def test_reject_personal_name_as_job_title(self):
        """Candidate name manohar entered as a job title is rejected."""
        valid, msg, _ = self.validator.validate_title_and_description(
            "manohar",
            "Fresher Java Developer requirements: Core Java, Spring Boot, Hibernate, MySQL, REST APIs"
        )
        assert valid is False
        assert "personal name" in msg.lower() or "not a recognized" in msg.lower()

    def test_driver_with_vehicle_requirements_accepted(self):
        """Legitimate driver job description is accepted."""
        valid, _, _ = self.validator.validate_title_and_description(
            "Delivery Driver",
            "We are looking for a reliable Delivery Driver. Responsibilities include transporting goods, following delivery routes, maintaining vehicle safety, and holding a valid driving license."
        )
        assert valid is True
