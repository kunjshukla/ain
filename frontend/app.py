import streamlit as st
import requests
from datetime import datetime

# Replace with your deployed Railway backend URL
BACKEND_URL = "https://aininjacoach-v2-backend.railway.app"

st.set_page_config(page_title="AI NinjaCoach", layout="wide")
st.title("🤖 AI NinjaCoach - Smart Interview Prep")

# Tabs for each agent functionality
tab1, tab2, tab3, tab4 = st.tabs(["🧑‍💼 Interview", "💻 DSA", "📄 Resume Analyzer", "📊 Past Performance"])

# ------------------ Interview Tab ------------------ #
with tab1:
    st.header("Mock Interview Questions")
    q1 = st.text_area("Tell me about yourself")
    q2 = st.text_area("What is your greatest strength?")
    q3 = st.text_area("Describe a challenge you faced and how you overcame it")

    if st.button("Analyze Interview Answers"):
        st.info("Calling Mock Interviewer Agent...")
        try:
            payload = {"q1": q1, "q2": q2, "q3": q3}
            response = requests.post(f"{BACKEND_URL}/analyze/answers", json=payload)
            result = response.json()
            st.success("✅ Feedback:")
            st.write(result.get("feedback", "No feedback returned."))
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------ DSA Tab ------------------ #
with tab2:
    st.header("DSA Challenge")
    st.markdown("Write code to solve the following:")
    st.code("Reverse a String", language="text")

    dsa_code = st.text_area("Your Python solution")

    if st.button("Analyze Code"):
        st.info("Calling DSA Evaluator Agent...")
        try:
            response = requests.post(f"{BACKEND_URL}/analyze/code", json={"code": dsa_code})
            result = response.json()
            st.success("✅ Feedback:")
            st.write(result.get("analysis", "No feedback returned."))
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------ Resume Analyzer Tab ------------------ #
with tab3:
    st.header("Upload Your Resume")
    uploaded_file = st.file_uploader("Upload PDF or paste resume text below")
    resume_text = st.text_area("OR paste your resume text")

    if st.button("Analyze Resume"):
        st.info("Calling Resume Analyzer Agent...")
        try:
            if uploaded_file:
                st.warning("PDF analysis not yet supported. Use text input for now.")
            payload = {"resume_text": resume_text}
            response = requests.post(f"{BACKEND_URL}/analyze/resume", json=payload)
            result = response.json()
            st.success("✅ Analysis:")
            st.write(result.get("insights", "No insights returned."))
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------ Past Performance Tab ------------------ #
with tab4:
    st.header("Retrieve Past Session")
    session_id = st.text_input("Enter your Session ID")

    if st.button("Retrieve Report"):
        st.info("Calling Performance Tracker Agent...")
        try:
            response = requests.get(f"{BACKEND_URL}/session/{session_id}")
            result = response.json()
            st.success("✅ Session Summary:")
            st.json(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.subheader("Example Performance Graph")
    st.line_chart({"Mock Score": [60, 75, 82], "DSA Score": [50, 65, 80]})
