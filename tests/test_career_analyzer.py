
import json
import unittest

from backend.services.career_analyzer import analyze_career
from backend.handler import lambda_handler


class CareerAnalyzerTests(unittest.TestCase):

    def test_skill_match_percentage(self):
        result = analyze_career(
            "Python SQL AWS Docker Git",
            "Python SQL AWS Terraform Kubernetes",
        )

        self.assertEqual(result["match_percentage"], 60.0)
        self.assertEqual(
            result["matched_skills"],
            ["Python", "SQL", "AWS"],
        )
        self.assertEqual(
            result["missing_skills"],
            ["Terraform", "Kubernetes"],
        )

    def test_no_required_skills(self):
        result = analyze_career(
            "Python developer",
            "Excellent communication and teamwork",
        )

        self.assertEqual(result["match_percentage"], 0)
        self.assertEqual(result["required_skills"], [])

    def test_health_endpoint(self):
        result = lambda_handler(
            {"path": "/health", "httpMethod": "GET"},
            None,
        )

        self.assertEqual(result["statusCode"], 200)

        body = json.loads(result["body"])
        self.assertEqual(
            body["message"],
            "CareerFlow AI API is running",
        )

    def test_missing_request_fields(self):
        event = {
            "path": "/career/analyze",
            "httpMethod": "POST",
            "body": json.dumps({
                "resume_text": "Python developer",
            }),
        }

        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 400)

    def test_invalid_json(self):
        event = {
            "path": "/career/analyze",
            "httpMethod": "POST",
            "body": "{invalid-json",
        }

        result = lambda_handler(event, None)

        self.assertEqual(result["statusCode"], 400)

    def test_unknown_endpoint(self):
        result = lambda_handler(
            {"path": "/unknown", "httpMethod": "GET"},
            None,
        )

        self.assertEqual(result["statusCode"], 404)


if __name__ == "__main__":
    unittest.main()
