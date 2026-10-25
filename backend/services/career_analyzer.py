
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


def extract_skills(text: str) -> list[str]:
    """Extract recognized skills from text."""
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)

    return found


def analyze_career(
    resume_text: str,
    job_description: str,
) -> dict:
    """Compare resume skills with job requirements."""
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
        round(
            len(matched_skills) / len(required_skills) * 100,
            2,
        )
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
