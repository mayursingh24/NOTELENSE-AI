import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, build_local_study_material


class StudyMaterialFallbackTests(unittest.TestCase):
    def test_fallback_contains_expected_sections(self):
        notes = "Photosynthesis is the process by which plants make food using sunlight."
        result = build_local_study_material(notes)

        self.assertIn("## Summary", result)
        self.assertIn("## Important Key Points", result)
        self.assertIn("Photosynthesis", result)


class RouteTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_keeps_upload_form_available(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analyze With Gemini', response.data)
        self.assertIn(b'id="uploadForm"', response.data)

    def test_login_page_renders_when_database_is_unavailable(self):
        response = self.client.get("/login")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login To NoteLense", response.data)

    def test_analyze_requires_login(self):
        response = self.client.post("/analyze")

        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Please login or signup", response.data)

    def test_healthz_endpoint(self):
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data["status"], "healthy")
        self.assertEqual(json_data["service"], "NoteLense-AI")


if __name__ == "__main__":
    unittest.main()
