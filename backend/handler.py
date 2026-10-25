
import json
import re


SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "SQL",
    "PL/SQL",
    "AWS",
    "Azure",
    "GCP",
    "Terraform",
    "Docker",
    "Kubernetes",
    "Databricks",
    "Django",
    "Flask",
    "FastAPI",
    "Machine Learning",
    "Deep Learning",
    "Generative AI",
    "LLM",
    "REST API",
    "Git",
    "Linux",
    "Oracle",
    "PostgreSQL",
    "MongoDB",
]


def extract_skills(text):
    """Extract recognized skills from the supplied text."""
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def analyze_career(resume_text, job_description):
    """Compare resume skills with job-description skills."""
    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    match_percentage = (
        round(len(matched_skills) / len(required_skills) * 100, 2)
        if required_skills
        else 0
    )

    return {
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
    }


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
    method = event.get(
        "httpMethod",
        "GET"
    )

    if path.endswith("/health") and method == "GET":
        return response(200, {
            "message": "CareerFlow AI API is running",
            "modules": ["CareerLens", "KnowFlow"],
        })

    if path.endswith("/career/analyze") and method == "POST":
        try:
            body = event.get("body") or "{}"

            if event.get("isBase64Encoded"):
                import base64
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
                    "error": "resume_text and job_description must be strings"
                })

            if not resume_text.strip() or not job_description.strip():
                return response(400, {
                    "error": (
                        "Both resume_text and job_description are required"
                    )
                })

            return response(
                200,
                analyze_career(resume_text, job_description)
            )

        except (json.JSONDecodeError, UnicodeDecodeError):
            return response(400, {
                "error": "Invalid JSON request body"
            })

    return response(404, {
        "error": "Endpoint not found"
    })
