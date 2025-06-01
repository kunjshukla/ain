import streamlit as st
import requests

# Ensure user_id is always initialized in session state
if "user_id" not in st.session_state:
    st.session_state.user_id = "user123"
import json
import random
from datetime import datetime
from requests.exceptions import JSONDecodeError

def get_fallback_questions(category=None):
    """Provide fallback interview questions if backend fails"""
    question_bank = {
        "behavioral": [
            "Tell me about yourself and your background.",
            "Describe a challenging situation you faced at work and how you handled it.",
            "Give an example of a time you showed leadership skills.",
            "How do you handle stress and pressure?",
            "Describe a time when you had to work with a difficult team member."
        ],
        "technical": [
            "Explain your approach to problem-solving in your technical work.",
            "Describe a complex technical project you worked on and your role in it.",
            "How do you stay updated with the latest technologies in your field?",
            "Explain a technical concept you understand well to a non-technical person.",
            "What's your process for debugging a complex issue?"
        ],
        "situational": [
            "How would you handle a situation where you disagree with your manager's approach?",
            "If you were assigned a project with an impossible deadline, what would you do?",
            "How would you prioritize multiple urgent tasks with conflicting deadlines?",
            "What would you do if you noticed a colleague was struggling with their work?",
            "How would you approach a situation where requirements change midway through a project?"
        ]
    }
    
    if category and category in question_bank:
        questions = question_bank[category]
    else:
        # Mix questions from all categories
        questions = []
        for cat_questions in question_bank.values():
            questions.extend(cat_questions)
    
    # Shuffle and return 3 questions
    random.shuffle(questions)
    return questions[:3]
    
def get_simulated_resume_result(resume_text=""):
    """Provide simulated resume analysis results when backend is unavailable"""
    return {
        "skills": {
            "technical": ["python", "javascript", "react", "node.js", "sql", "aws", "docker", "git"],
            "soft": ["communication", "teamwork", "leadership", "problem solving", "adaptability"]
        },
        "role_match": {
            "software_engineer": 0.85,
            "data_scientist": 0.65,
            "web_developer": 0.78,
            "devops_engineer": 0.72,
            "product_manager": 0.58
        },
        "suggested_questions": [
            "Tell me about your experience with Python and JavaScript.",
            "How have you used React in your previous projects?",
            "Describe a challenging problem you solved using your technical skills.",
            "How do you approach learning new technologies?",
            "What experience do you have with cloud services like AWS?"
        ],
        "strengths": [
            "Strong technical skills across multiple languages",
            "Experience with both frontend and backend technologies",
            "Familiarity with cloud platforms and containerization",
            "Good balance of technical and soft skills",
            "Collaborative team player with leadership abilities"
        ],
        "weaknesses": [
            "Consider adding more specific project examples",
            "Could benefit from more quantifiable achievements",
            "Add more details about your role in team projects",
            "Consider highlighting more domain-specific expertise",
            "Add more information about your education and certifications"
        ],
        "extracted_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
    }

# Backend URL configuration
import os

# Get the backend URL from environment variable or use the default
BACKEND_URL = os.environ.get("BACKEND_URL", "https://ain-backend-v3.onrender.com")

# For local testing, uncomment the line below
# BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="AI NinjaCoach", layout="wide")
st.title("🤖 AI NinjaCoach - Smart Interview Prep")

# Tabs for each agent functionality
tab1, tab2, tab3, tab4 = st.tabs(["🧑‍💼 Interview", "💻 DSA", "📄 Resume Analyzer", "🤖 Career Coach"])


# ------------------ Interview Tab ------------------ #
with tab1:
    st.header("Mock Interview Questions")
    
    # Dynamic question/answer pairs
    num_questions = st.number_input("Number of questions to answer", min_value=1, max_value=5, value=3)
    
    questions = [
        "Tell me about yourself",
        "What is your greatest strength?",
        "Describe a challenge you faced and how you overcame it",
        "Why do you want to work for this company?",
        "Where do you see yourself in 5 years?"
    ]
    
    responses = []
    for i in range(num_questions):
        q_text = questions[i] if i < len(questions) else f"Question {i+1}"
        responses.append(st.text_area(f"{q_text}", key=f"q{i}"))
    
    user_id = st.text_input("Your User ID (for tracking progress)", value="user123")
    
    if st.button("Analyze Interview Answers"):
        st.info("Calling Mock Interviewer Agent...")
        try:
            # Filter out empty responses
            valid_responses = [r for r in responses if r.strip()]
            
            if not valid_responses:
                st.warning("Please provide at least one answer")
            else:
                payload = {"responses": valid_responses}
                response = requests.post(f"{BACKEND_URL}/analyze/interview", json=payload)
                result = response.json()
                
                # Track the session
                session_data = {
                    "user_id": user_id,
                    "session_data": {
                        "session_id": f"interview_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "interview_score": result.get("average_score", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                requests.post(f"{BACKEND_URL}/track/session", json=session_data)
                
                # Display results
                st.success("✅ Analysis Complete")
                
                # Show evaluations
                st.subheader("Question-by-Question Evaluation")
                for eval in result.get("evaluations", []):
                    with st.expander(f"Q: {eval['question']}"):
                        st.write(f"**Your Answer:** {eval['answer']}")
                        st.write(f"**Score:** {eval['evaluation']['score']:.2f}/1.0")
                        st.write(f"**Feedback:** {eval['evaluation']['feedback']}")
                
                # Show overall results
                st.subheader("Overall Assessment")
                st.metric("Average Score", f"{result.get('average_score', 0):.2f}/1.0")
                
                st.subheader("Areas for Improvement")
                for area in result.get("improvement_areas", []):
                    st.markdown(f"- {area}")
                
                st.subheader("Overall Feedback")
                st.write(result.get("overall_feedback", "No feedback available"))
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.error(f"Response: {response.text if 'response' in locals() else 'No response'}")


# ------------------ DSA Tab ------------------ #
with tab2:
    st.header("DSA Challenge")
    
    # Problem selection
    problem_options = {
        "reverse_string": "Reverse a String",
        "fibonacci": "Generate Fibonacci Sequence",
        "palindrome": "Check if String is Palindrome",
        "two_sum": "Two Sum Problem",
        "binary_search": "Binary Search Implementation",
        "merge_sort": "Merge Sort Algorithm",
        "linked_list_cycle": "Detect Cycle in Linked List",
        "valid_parentheses": "Valid Parentheses",
        "lru_cache": "LRU Cache Implementation",
        "bst_traversal": "Binary Search Tree Traversal",
        "max_subarray": "Maximum Subarray Sum",
        "word_frequency": "Word Frequency Counter",
        "longest_substring": "Longest Substring Without Repeating Characters",
        "rotate_array": "Rotate Array",
        "merge_intervals": "Merge Intervals"
    }
    
    selected_problem = st.selectbox(
        "Select a coding problem:",
        options=list(problem_options.keys()),
        format_func=lambda x: problem_options[x]
    )
    
    # Problem descriptions
    problem_descriptions = {
        "reverse_string": "Write a function that reverses a string. The input is a string, and the output should be the reversed string.",
        "fibonacci": "Write a function to generate the first n numbers in the Fibonacci sequence.",
        "palindrome": "Write a function to check if a given string is a palindrome (reads the same forward and backward).",
        "two_sum": "Given an array of integers and a target sum, return the indices of the two numbers that add up to the target.",
        "binary_search": "Implement binary search to find the position of a target value within a sorted array.",
        "merge_sort": "Implement the merge sort algorithm to sort an array of integers in ascending order.",
        "linked_list_cycle": "Given a linked list, determine if it has a cycle. Return True if there is a cycle, False otherwise.",
        "valid_parentheses": "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if opening brackets are closed by the same type of brackets and in the correct order.",
        "lru_cache": "Implement an LRU (Least Recently Used) cache with get and put operations in O(1) time complexity.",
        "bst_traversal": "Implement in-order, pre-order, and post-order traversal of a binary search tree.",
        "max_subarray": "Given an integer array, find the contiguous subarray with the largest sum and return the sum.",
        "word_frequency": "Given a text string, count the frequency of each word and return a dictionary with words as keys and their frequencies as values.",
        "longest_substring": "Given a string, find the length of the longest substring without repeating characters.",
        "rotate_array": "Given an array, rotate the array to the right by k steps, where k is non-negative.",
        "merge_intervals": "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals and return the non-overlapping intervals."
    }
    
    st.markdown(f"**Problem:** {problem_descriptions[selected_problem]}")
    
    # Code input
    dsa_code = st.text_area("Your Python solution", height=300)
    user_id = st.text_input("Your User ID (for tracking progress)", value=st.session_state.user_id, key="dsa_user_id")
    
    if st.button("Analyze Code"):
        if not dsa_code.strip():
            st.warning("Please enter your code solution")
        else:
            st.info("Calling DSA Evaluator Agent...")
            try:
                # Send code for evaluation
                payload = {
                    "code": dsa_code,
                    "problem": selected_problem
                }
                response = requests.post(f"{BACKEND_URL}/analyze/code", json=payload)
                result = response.json()
                
                # Track the session
                session_data = {
                    "user_id": user_id,
                    "session_data": {
                        "session_id": f"dsa_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "code_correctness": result.get("correctness", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                requests.post(f"{BACKEND_URL}/track/session", json=session_data)
                
                # Display results
                st.success("✅ Analysis Complete")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Correctness", f"{result.get('correctness', 0):.2f}/1.0")
                with col2:
                    st.metric("Time Complexity", result.get('time_complexity', 'N/A'))
                with col3:
                    st.metric("Space Complexity", result.get('space_complexity', 'N/A'))
                
                # Show suggestions
                st.subheader("Suggestions for Improvement")
                for suggestion in result.get("suggestions", ["No suggestions available"]):
                    st.markdown(f"- {suggestion}")
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.error(f"Response: {response.text if 'response' in locals() else 'No response'}")


# ------------------ Resume Analyzer Tab ------------------ #
with tab3:
    st.header("Resume Analysis")
    
    # Resume input options
    input_method = st.radio("Input Method", ["Paste Resume Text", "Upload PDF"])
    
    # Initialize variables
    resume_text = ""
    uploaded_file = None
    
    # Create separate containers for each input method
    if input_method == "Paste Resume Text":
        resume_text = st.text_area("Paste your resume text here", height=300)
    else:
        uploaded_file = st.file_uploader("Upload your resume PDF", type=["pdf"])
        if uploaded_file is not None:
            if uploaded_file.type != "application/pdf":
                st.error("Please upload a valid PDF file")
                st.stop()
            st.success(f"✅ PDF uploaded: {uploaded_file.name}")
    
    user_id = st.text_input("Your User ID (for tracking progress)", value="user123", key="resume_user_id")
    
    if st.button("Analyze Resume"):
        if not resume_text.strip() and input_method == "Paste Resume Text":
            st.warning("Please enter your resume text")
        elif not uploaded_file and input_method == "Upload PDF":
            st.warning("Please upload a PDF file")
        else:
            st.info("Analyzing your resume...")
            try:
                result = None
                if input_method == "Paste Resume Text":
                    # Send resume text for analysis
                    st.info("Sending resume to local backend for analysis...")
                    payload = {"text": resume_text}
                    try:
                        response = requests.post(f"{BACKEND_URL}/analyze/resume", json=payload)
                        response.raise_for_status()
                        result = response.json()
                        st.success("Resume analysis completed successfully!")
                    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
                        st.warning(f"Local backend error: {str(e)}. Trying deployed backend...")
                        try:
                            fallback_url = "https://ain-backend-v3.onrender.com"
                            response = requests.post(f"{fallback_url}/analyze/resume", json=payload)
                            response.raise_for_status()
                            result = response.json()
                            st.success("Resume analysis completed successfully!")
                        except Exception as e2:
                            st.error(f"Deployed backend error: {str(e2)}")
                else:
                    # Send PDF for analysis
                    st.info("Sending PDF to local backend for analysis...")
                    try:
                        pdf_content = uploaded_file.getvalue()
                        if not pdf_content:
                            st.error("Could not read PDF content. Please try again.")
                        else:
                            files = {"file": (uploaded_file.name, pdf_content, "application/pdf")}
                            response = requests.post(f"{BACKEND_URL}/analyze/resume/pdf", files=files, timeout=30)
                            response.raise_for_status()
                            result = response.json()
                            st.success("Resume analysis completed successfully!")
                            # Display extracted text preview if available
                            if "extracted_text" in result:
                                with st.expander("View extracted text from PDF"):
                                    st.text(result["extracted_text"])
                    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
                        st.warning(f"Local backend error: {str(e)}. Trying deployed backend...")
                        try:
                            fallback_url = "https://ain-backend-v3.onrender.com"
                            files = {"file": (uploaded_file.name, pdf_content, "application/pdf")}
                            response = requests.post(f"{fallback_url}/analyze/resume/pdf", files=files, timeout=30)
                            response.raise_for_status()
                            result = response.json()
                            st.success("Resume analysis completed successfully!")
                            if "extracted_text" in result:
                                with st.expander("View extracted text from PDF"):
                                    st.text(result["extracted_text"])
                        except Exception as e2:
                            st.error(f"Deployed backend error: {str(e2)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            
            # Display results
            st.success("✅ Analysis Complete")
            
            # Show skills
            st.subheader("Skills Identified")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Technical Skills:**")
                for skill in result.get("skills", {}).get("technical", []):
                    st.markdown(f"- {skill}")
            with col2:
                st.write("**Soft Skills:**")
                for skill in result.get("skills", {}).get("soft", []):
                    st.markdown(f"- {skill}")
            
            # Show role match
            st.subheader("Role Match Percentage")
            role_match = result.get("role_match", {})
            if role_match:
                # Create a bar chart for role matches
                role_data = {"Role": list(role_match.keys()), "Match %": [v*100 for v in role_match.values()]}
                st.bar_chart(role_data, x="Role", y="Match %")
                
                # If session tracking fails, don't interrupt the user experience
                pass
                
                # Display results
                st.success("✅ Analysis Complete")
                
                # Show skills
                st.subheader("Skills Identified")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Technical Skills:**")
                    for skill in result.get("skills", {}).get("technical", []):
                        st.markdown(f"- {skill}")
                with col2:
                    st.write("**Soft Skills:**")
                    for skill in result.get("skills", {}).get("soft", []):
                        st.markdown(f"- {skill}")
                
                # Show role match
                st.subheader("Role Match Percentage")
                role_match = result.get("role_match", {})
                if role_match:
                    # Create a bar chart for role matches
                    role_data = {"Role": list(role_match.keys()), "Match %": [v*100 for v in role_match.values()]}
                    st.bar_chart(role_data, x="Role", y="Match %")
                else:
                    st.write("No role match data available")
                
                # Show strengths and weaknesses
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Strengths")
                    for strength in result.get("strengths", []):
                        st.markdown(f"- {strength}")
                with col2:
                    st.subheader("Areas for Improvement")
                    for weakness in result.get("weaknesses", []):
                        st.markdown(f"- {weakness}")
                
                # Show suggested questions
                st.subheader("Suggested Interview Questions")
                for i, question in enumerate(result.get("suggested_questions", [])):
                    st.markdown(f"{i+1}. {question}")
                    

# ========== End of Career Coach (AI Orchestrator) Tab ==========

# ========== Performance Dashboard & Coding Challenge ==========

st.markdown("## 📈 Your Performance Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Coding Score", "85", "+5")
col2.metric("Communication", "92", "+3")
col3.metric("Resume Score", "78", "-2")

user_id = st.text_input("User ID for Performance Report", value="user123", key="perf_dash_user_id")

def load_performance_report(user_id):
    st.info(f"Loading performance report for {user_id} (stub function)")
    # Here you would call backend and display results

if st.button("📥 Load Performance Report"):
    load_performance_report(user_id)

st.bar_chart(data={"Scores": [78, 85, 92]}, use_container_width=True)

st.markdown("## 🧩 Coding Challenge")
problem = st.selectbox("Select a coding problem", ["Reverse String", "Two Sum", "Binary Search"])
code_input = st.text_area("Your Solution (Python)", height=200)

def evaluate_code(problem, code_input):
    # Placeholder for backend code evaluation
    return f"Feedback for {problem}:\n- Code looks good!\n- Remember to handle edge cases."

if st.button("✅ Evaluate Code"):
    feedback = evaluate_code(problem, code_input)
    st.success("Evaluation Complete")
    st.code(feedback, language="markdown")

# ------------------ Career Coach (Orchestrator) Tab ------------------ #
with tab4:
    st.markdown("""
    <h2 style='color:#00FFFF'>🎯 Career Coach (AI Orchestrator)</h2>
    <p style='color:#AAAAAA'>Let the AI Orchestrator guide your end-to-end interview prep journey.</p>
    <hr style='border-color: #333;'>
    """, unsafe_allow_html=True)
    def run_orchestrator(user_id, career_goal, resume, code_solution, interview_answers):
        st.info("Calling Orchestrator Agent...")
        try:
            payload = {
                "user_id": user_id,
                "goal": career_goal,
                "resume_text": resume,
                "code": code_solution,
                "interview_answers": interview_answers
            }
            response = requests.post(f"{BACKEND_URL}/orchestrate", json=payload)
            result = response.json()
            if response.status_code == 200:
                st.success("Orchestrator Results:")
                # Show each agent's output in expandable sections
                if result.get("resume"):
                    with st.expander("Resume Analysis"):
                        st.json(result["resume"])
                if result.get("dsa"):
                    with st.expander("Coding Evaluation"):
                        st.json(result["dsa"])
                if result.get("interview"):
                    with st.expander("Mock Interview Feedback"):
                        st.json(result["interview"])
                if result.get("behavioral"):
                    with st.expander("Behavioral Coaching"):
                        st.json(result["behavioral"])
                if result.get("performance"):
                    with st.expander("Performance Dashboard"):
                        st.json(result["performance"])
            else:
                st.error(f"Backend error: {response.text}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    with st.expander("📋 Career Details"):
        user_id = st.text_input("User ID", value="user123")
        career_goal = st.text_input("Career Goal", placeholder="e.g., Backend Developer at Google")
        resume = st.text_area("Paste your Resume (Optional)")
        code_solution = st.text_area("Paste your Code Solution (Optional)")
        interview_answers = st.text_area("Paste your Interview Answers (comma-separated)")

        if st.button("🚀 Run Orchestrator Analysis"):
            run_orchestrator(user_id, career_goal, resume, code_solution, interview_answers)
                    
            if dsa_scores:
                st.subheader("DSA Performance")
                dsa_data = {"Date": dates[:len(dsa_scores)], "Score": dsa_scores}
                st.line_chart(dsa_data, x="Date", y="Score")
                    
                # Recent sessions
                st.subheader("Recent Sessions")
                recent_sessions = sessions[-5:] if len(sessions) > 5 else sessions
                recent_sessions.reverse()  # Most recent first
                
                for i, session in enumerate(recent_sessions):
                    session_type = "Unknown"
                    if "interview_score" in session:
                            session_type = "Interview"
                    elif "code_correctness" in session:
                            session_type = "DSA Challenge"
                    elif "resume_skills" in session:
                            session_type = "Resume Analysis"
                            
                    with st.expander(f"{session_type} Session - {session.get('timestamp', '').split('T')[0]}"):
                        st.json(session)
                else:
                    st.info("No session data available yet. Complete some exercises to see your progress!")
                    
                # Skill inventory from resume analysis
                skills = result.get("skills", [])
                if skills:
                    st.subheader("Your Skill Inventory")
                    st.write("Based on your resume analysis:")
                    # Display as tags
                    st.write(', '.join([f"`{skill}`" for skill in skills]))

    st.subheader("Coding Challenge")
    coding_problem = st.selectbox(
        "Select a coding problem",
        ["Reverse String", "Two Sum", "Palindrome Check", "Valid Parentheses", "Merge Sort", "Linked List Cycle"],
        key="combined_problem"
    )
    
    code_solution = st.text_area("Your solution (Python):", height=150, key="combined_code")
    
    st.subheader("Video Interview")
    st.write("Upload a video of yourself answering an interview question for comprehensive feedback.")
    video_question = st.selectbox(
        "Select a video interview question",
        [
            "Describe a challenging situation you faced at work and how you handled it.",
            "Give an example of a time you showed leadership skills.",
            "How do you handle stress and pressure?",
            "Explain your approach to problem-solving in your technical work."
        ],
        key="combined_video_question"
    )
    
    uploaded_video = st.file_uploader("Upload your video response (MP4 format)", type=["mp4"], key="combined_video")
    
    if st.button("Run Combined Analysis"):
        if not resume_text.strip() or not interview_response.strip() or not code_solution.strip():
            st.warning("Please fill in all required fields (resume, interview answer, and code solution)")
        else:
            st.info("Running comprehensive analysis...")
            
            try:
                # Process resume, interview, and code
                payload = {
                    "resume": resume_text,
                    "answers": [interview_response],
                    "code": code_solution
                }
                
                response = requests.post(f"{BACKEND_URL}/analyze/combined", json=payload)
                result = response.json()
                
                # Process video interview if provided
                video_analysis = None
                if uploaded_video is not None:
                    st.info("Processing video interview...")
                    # Read video file
                    video_bytes = uploaded_video.read()
                    
                    # Convert to base64
                    import base64
                    video_b64 = base64.b64encode(video_bytes).decode()
                    
                    # Send to backend
                    video_payload = {
                        "video_data": video_b64,
                        "question": video_question,
                        "user_id": user_id
                    }
                    
                    # This would be the actual API call in a complete implementation
                    # video_response = requests.post(f"{BACKEND_URL}/analyze/video-interview", json=video_payload)
                    # video_analysis = video_response.json()
                    
                    # For demonstration, show a simulated response
                    # Video analysis removed
                
                st.success("✅ Combined Analysis Complete")
                
                # Display comprehensive results
                st.subheader("Overall Assessment")
                st.progress(result.get("overall_score", 0))
                st.metric("Overall Score", f"{result.get('overall_score', 0):.2f}/1.0")
                
                # Individual component scores
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Resume Score", f"{result.get('resume_score', 0):.2f}/1.0")
                with col2:
                    st.metric("Interview Score", f"{result.get('interview_score', 0):.2f}/1.0")
                with col3:
                    st.metric("Code Score", f"{result.get('code_score', 0):.2f}/1.0")
                
                # Detailed feedback
                st.subheader("Detailed Feedback")
                st.write(result.get("feedback", "No feedback available"))
                
                # Improvement plan
                st.subheader("Improvement Plan")
                for i, item in enumerate(result.get("improvement_plan", ["No improvement plan available"])):
                    st.markdown(f"{i+1}. {item}")
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.error(f"Response: {response.text if 'response' in locals() else 'No response'}")
