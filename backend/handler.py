
import base64
import json

try:
    from services.career_analyzer import analyze_career
    from services.claude_analyzer import (
        ClaudeAnalysisError,
        analyze_resume_with_claude,
    )
except ModuleNotFoundError as exc:
    if exc.name != "services":
        raise
    from backend.services.career_analyzer import analyze_career
    from backend.services.claude_analyzer import (
        ClaudeAnalysisError,
        analyze_resume_with_claude,
    )


def response(status_code, data):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(data),
    }


def lambda_handler(event, context):
    path = event.get("path", "/health")
    method = event.get("httpMethod", "GET")

    if path.endswith("/health") and method == "GET":
        return response(200, {
            "message": "CareerFlow AI API is running",
            "modules": ["CareerLens", "KnowFlow"],
        })

    if path.endswith("/career/analyze") and method == "POST":
        try:
            body = event.get("body") or "{}"

            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")

            if isinstance(body, str):
                body = json.loads(body)

            if not isinstance(body, dict):
                return response(400, {
                    "error": "Request body must be a JSON object"
                })

            resume_text = body.get("resume_text", "")
            job_description = body.get("job_description", "")

            if not isinstance(resume_text, str) or not isinstance(
                job_description, str
            ):
                return response(400, {
                    "error": (
                        "resume_text and job_description must be strings"
                    )
                })

            if not resume_text.strip() or not job_description.strip():
                return response(400, {
                    "error": (
                        "Both resume_text and job_description are required"
                    )
                })

            # Preserve the existing deterministic skill analysis.
            result = analyze_career(
                resume_text,
                job_description,
            )

            # Claude analysis is opt-in to control API costs.
            use_claude = body.get("use_claude", False)

            if not isinstance(use_claude, bool):
                return response(400, {
                    "error": "use_claude must be a boolean"
                })

            if use_claude:
                try:
                    claude_feedback = analyze_resume_with_claude(
                        resume_text,
                        job_description,
                    )
                    result["claude_feedback"] = claude_feedback

                except ClaudeAnalysisError:
                    # Do not silently report a successful AI analysis.
                    return response(502, {
                        "error": (
                            "Claude analysis failed. Check the API "
                            "configuration and try again."
                        ),
                        "skill_analysis": result,
                    })

            return response(200, result)

        except (json.JSONDecodeError, UnicodeDecodeError):
            return response(400, {
                "error": "Invalid JSON request body"
            })

        except (ValueError, TypeError):
            return response(400, {
                "error": "Invalid request data"
            })

    return response(404, {
        "error": "Endpoint not found"
    })
