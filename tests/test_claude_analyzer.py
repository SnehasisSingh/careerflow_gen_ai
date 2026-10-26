
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.services.claude_analyzer import (
    ClaudeAnalysisError,
    analyze_resume_with_claude,
)


class ClaudeAnalyzerTests(unittest.TestCase):

    def setUp(self):
        self.expected_result = {
            "summary": "Good match for a Python developer role.",
            "strengths": ["Python", "SQL"],
            "improvement_areas": ["Terraform"],
            "suggested_resume_bullets": [
                "Describe relevant Python development work."
            ],
            "interview_questions": [
                "How have you used Python in a project?"
            ],
        }

    def mock_response(self, content):
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text=content)
            ]
        )

    @patch("backend.services.claude_analyzer.anthropic.Anthropic")
    def test_successful_analysis(self, mock_anthropic):
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = self.mock_response(
            json.dumps(self.expected_result)
        )

        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "test-key"},
        ):
            result = analyze_resume_with_claude(
                "Python developer with SQL experience",
                "Looking for Python, SQL and Terraform",
            )

        self.assertEqual(result, self.expected_result)
        mock_client.messages.create.assert_called_once()

    @patch("backend.services.claude_analyzer.anthropic.Anthropic")
    def test_missing_api_key(self, mock_anthropic):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ClaudeAnalysisError):
                analyze_resume_with_claude(
                    "Python developer",
                    "Python developer required",
                )

        mock_anthropic.assert_not_called()

    @patch("backend.services.claude_analyzer.anthropic.Anthropic")
    def test_invalid_json_response(self, mock_anthropic):
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = self.mock_response(
            "This is not valid JSON"
        )

        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "test-key"},
        ):
            with self.assertRaises(ClaudeAnalysisError):
                analyze_resume_with_claude(
                    "Python developer",
                    "Python developer required",
                )

    @patch("backend.services.claude_analyzer.anthropic.Anthropic")
    def test_invalid_response_schema(self, mock_anthropic):
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = self.mock_response(
            json.dumps({"summary": "Incomplete response"})
        )

        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "test-key"},
        ):
            with self.assertRaises(ClaudeAnalysisError):
                analyze_resume_with_claude(
                    "Python developer",
                    "Python developer required",
                )


if __name__ == "__main__":
    unittest.main()
