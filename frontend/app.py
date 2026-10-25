
import os

import requests
import streamlit as st


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

api_url = st.sidebar.text_input(
    "CareerLens API URL",
    value=os.getenv("CAREERFLOW_API_URL", DEFAULT_API_URL),
)

resume_text = st.text_area(
    "Paste your resume",
    height=250,
    placeholder="Paste your resume text here...",
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
        }

        try:
            with st.spinner("Analyzing your resume..."):
                response = requests.post(
                    api_url.strip(),
                    json=payload,
                    timeout=30,
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

                st.caption(
                    "This score measures recognized keyword overlap. "
                    "It is not a complete assessment of candidate suitability."
                )

            else:
                st.error(
                    f"API request failed ({response.status_code}). "
                    "Check the API URL and try again."
                )

        except requests.RequestException as exc:
            st.error(f"Could not connect to the CareerLens API: {exc}")

        except (ValueError, TypeError):
            st.error("The API returned an invalid response.")
