
import base64
import json

try:
    from services.career_analyzer import analyze_career
except ModuleNotFoundError as exc:
    if exc.name != "services":
        raise
    from backend.services.career_analyzer import analyze_career


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

            result = analyze_career(resume_text, job_description)
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
