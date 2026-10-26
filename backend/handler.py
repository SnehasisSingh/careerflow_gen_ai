
import base64
import json
import logging

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


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    logger.info(
        "Request received: method=%s, path=%s",
        method,
        path,
    )

    # Health check endpoint
    if path.endswith("/health") and method == "GET":
        logger.info("Health check successful")

        return response(200, {
            "message": "CareerFlow AI API is running",
            "modules": ["CareerLens", "KnowFlow"],
        })

    # Resume and job description analysis endpoint
    if path.endswith("/career/analyze") and method == "POST":
        try:
            body = event.get("body") or "{}"

            # Decode Base64-encoded request bodies
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")

            if isinstance(body, str):
                body = json.loads(body)

            if not isinstance(body, dict):
                logger.warning("Invalid request: body must be a JSON object")

                return response(400, {
                    "error": "Request body must be a JSON object"
                })

            resume_text = body.get("resume_text", "")
            job_description = body.get("job_description", "")

            # Validate input types
            if not isinstance(resume_text, str) or not isinstance(
                job_description, str
            ):
                logger.warning(
                    "Invalid request: resume_text and job_description "
                    "must be strings"
                )

                return response(400, {
                    "error": (
                        "resume_text and job_description must be strings"
                    )
                })

            # Validate required fields
            if not resume_text.strip() or not job_description.strip():
                logger.warning(
                    "Invalid request: resume_text or job_description "
                    "is missing"
                )

                return response(400, {
                    "error": (
                        "Both resume_text and job_description are required"
                    )
                })

            # Validate Claude opt-in flag before running analysis
            use_claude = body.get("use_claude", False)

            if not isinstance(use_claude, bool):
                logger.warning(
                    "Invalid request: use_claude must be a boolean"
                )

                return response(400, {
                    "error": "use_claude must be a boolean"
                })

            # Preserve deterministic skill analysis
            logger.info("Starting deterministic career analysis")

            result = analyze_career(
                resume_text,
                job_description,
            )

            logger.info("Deterministic career analysis completed")

            # Claude analysis is optional to control API costs
            if use_claude:
                logger.info("Claude resume analysis requested")

                try:
                    claude_feedback = analyze_resume_with_claude(
                        resume_text,
                        job_description,
                    )

                    result["claude_feedback"] = claude_feedback

                    logger.info("Claude resume analysis completed")

                except ClaudeAnalysisError:
                    logger.exception("Claude resume analysis failed")

                    return response(502, {
                        "error": (
                            "Claude analysis failed. Check the API "
                            "configuration and try again."
                        ),
                        "skill_analysis": result,
                    })

            else:
                logger.info(
                    "Claude analysis skipped; use_claude is false"
                )

            logger.info("Career analysis request completed successfully")

            return response(200, result)

        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.warning(
                "Invalid JSON request body",
                exc_info=True,
            )

            return response(400, {
                "error": "Invalid JSON request body"
            })

        except (ValueError, TypeError):
            logger.exception("Invalid request data")

            return response(400, {
                "error": "Invalid request data"
            })

        except Exception:
            logger.exception("Unexpected error during career analysis")

            return response(500, {
                "error": "Internal server error"
            })

    logger.warning(
        "Endpoint not found: method=%s, path=%s",
        method,
        path,
    )

    return response(404, {
        "error": "Endpoint not found"
    })
