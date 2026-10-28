import io
import logging
import os

import requests
import streamlit as st
from pypdf import PdfReader

logger = logging.getLogger(__name__)

DEFAULT_API_URL = (
    "https://uy0pxf91sl.execute-api.ap-southeast-2.amazonaws.com"
    "/Stage/career/analyze"
)

st.set_page_config(
    page_title="CareerFlow AI | CareerLens",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 CareerFlow AI")
st.subheader("CareerLens — Resume & Job Match Analyzer")

st.write(
    "Compare your resume with a job description, identify skill gaps, "
    "and understand how well your skills match the role."
)

resume_input_method = st.radio(
    "How would you like to provide your resume?",
    options=["Upload PDF", "Paste resume text"],
    horizontal=True,
)
resume_text = ""

api_url = st.sidebar.text_input(
    "CareerLens API URL",
    value=os.getenv("CAREERFLOW_API_URL", DEFAULT_API_URL),
)

# Claude is optional to help control API costs.
use_claude = st.toggle(
    "Enable Claude AI Feedback",
    value=False,
    help=(
        "Get AI-generated resume feedback, strengths, improvement areas, "
        "suggested resume bullets, and interview questions. "
        "Enabling this makes a paid Claude API request."
    ),
)

if use_claude:
    st.info("Claude AI feedback is enabled. This may incur API charges.")
else:
    st.caption("Claude AI feedback is off. Only skill matching will run.")


if resume_input_method == "Upload PDF":
    uploaded_pdf = st.file_uploader(
        "Upload your resume",
        type=["pdf"],
        help="Upload a text-based PDF up to 5 MB.",
        key="resume_pdf",
    )

    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.getvalue()

        if len(pdf_bytes) > 5 * 1024 * 1024:
            st.error("PDF must be 5 MB or smaller.")

        else:
            try:
                reader = PdfReader(io.BytesIO(pdf_bytes))

                if reader.is_encrypted:
                    st.error(
                        "This PDF is password-protected. "
                        "Please upload an unlocked PDF."
                    )

                elif len(reader.pages) > 30:
                    st.error(
                        "Please upload a PDF with 30 pages or fewer."
                    )

                else:
                    resume_text = "\n".join(
                        page.extract_text() or ""
                        for page in reader.pages
                    ).strip()

                    if resume_text:
                        st.success("Resume text extracted successfully.")

                        with st.expander("Preview extracted resume text"):
                            st.text(resume_text)

                    else:
                        st.warning(
                            "No selectable text found. "
                            "If this is a scanned PDF, paste the text "
                            "or use OCR to extract it."
                        )

            except Exception:
                st.error(
                    "Unable to read this PDF. "
                    "Please try another PDF."
                )

else:
    resume_text = st.text_area(
        "Paste your resume text",
        height=250,
        placeholder="Paste your complete resume here...",
        key="resume_manual_text",
    )


job_description = st.text_area(
    "Paste the job description",
    height=250,
    placeholder="Paste the target job description here...",
)

if st.button("Analyze Resume", type="primary"):
    if not resume_text.strip() or not job_description.strip():
        st.warning("Please provide both your resume and the job description.")

    elif not api_url.strip():
        st.warning("Please provide the CareerLens API URL.")

    else:
        payload = {
            "resume_text": resume_text,
            "job_description": job_description,
            "use_claude": use_claude,
        }

        try:
            with st.spinner(
                "Analyzing resume with Claude..."
                if use_claude
                else "Analyzing your resume..."
            ):
                response = requests.post(
                    api_url.strip(),
                    json=payload,
                    timeout=90 if use_claude else 30,
                )

            if response.ok:
                result = response.json()

                st.divider()
                st.header("Analysis Results")

                percentage = result.get("match_percentage", 0)
                st.metric("Skill Match", f"{percentage}%")
                st.progress(
                    max(0.0, min(float(percentage) / 100, 1.0))
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("✅ Matched Skills")
                    matched = result.get("matched_skills", [])
                    if matched:
                        for skill in matched:
                            st.write(f"- {skill}")
                    else:
                        st.info("No matching skills found.")

                with col2:
                    st.subheader("📌 Missing Skills")
                    missing = result.get("missing_skills", [])
                    if missing:
                        for skill in missing:
                            st.write(f"- {skill}")
                    else:
                        st.success("No missing recognized skills.")

                with st.expander("All detected skills"):
                    st.write("**Resume skills**")
                    st.write(result.get("resume_skills", []))

                    st.write("**Required skills**")
                    st.write(result.get("required_skills", []))

                # Display Claude's qualitative feedback if requested.
                claude_feedback = result.get("claude_feedback")

                if use_claude:
                    st.divider()
                    st.header("🤖 Claude AI Resume Feedback")

                    if claude_feedback:
                        st.write("### Summary")
                        st.write(claude_feedback.get("summary", ""))

                        st.write("### 💪 Strengths")
                        strengths = claude_feedback.get("strengths", [])
                        if strengths:
                            for item in strengths:
                                st.write(f"- {item}")
                        else:
                            st.info("No strengths returned.")

                        st.write("### 🎯 Improvement Areas")
                        improvements = claude_feedback.get(
                            "improvement_areas", []
                        )
                        if improvements:
                            for item in improvements:
                                st.write(f"- {item}")
                        else:
                            st.info("No improvement areas returned.")

                        st.write("### 📝 Suggested Resume Bullets")
                        bullets = claude_feedback.get(
                            "suggested_resume_bullets", []
                        )
                        if bullets:
                            for item in bullets:
                                st.write(f"- {item}")
                        else:
                            st.info("No suggested bullets returned.")

                        st.write("### 🎤 Interview Questions")
                        questions = claude_feedback.get(
                            "interview_questions", []
                        )
                        if questions:
                            for index, question in enumerate(
                                questions, start=1
                            ):
                                st.write(f"{index}. {question}")
                        else:
                            st.info("No interview questions returned.")

                    else:
                        st.warning(
                            "The API did not return Claude feedback. "
                            "Check the API response and backend logs."
                        )

                st.caption(
                    "The skill-match score measures recognized keyword "
                    "overlap. It is not a complete assessment of "
                    "candidate suitability."
                )

            else:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                st.error(
                    f"API request failed ({response.status_code})."
                )

                if error_data.get("error"):
                    st.write(error_data["error"])

                if error_data.get("skill_analysis"):
                    st.info(
                        "The regular skill analysis succeeded, but "
                        "Claude feedback could not be generated."
                    )

        except requests.RequestException:
            st.error(
                "Could not connect to the CareerLens API. "
                "Check your connection and API URL, then try again."
            )

        except (ValueError, TypeError):
            st.error("The API returned an invalid response.")
