# AI NinjaCoach Frontend

This is the frontend for the AI NinjaCoach platform, a multi-agent interview coaching system designed to help users prepare for technical interviews through resume analysis, mock interviews, DSA evaluations, and performance tracking.

## Features

- **Mock Interview**: Practice answering behavioral interview questions and receive AI-powered feedback
- **DSA Challenges**: Solve coding problems and get evaluations on correctness, complexity, and style
- **Resume Analysis**: Upload or paste your resume to get insights on skills, role matches, and suggested interview questions
- **Performance Dashboard**: Track your progress over time with detailed metrics and visualizations
- **Combined Analysis**: Get comprehensive feedback by analyzing your resume, interview answers, and code solutions together

## Getting Started

### Prerequisites

- Python 3.10+
- Streamlit
- Requests

### Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Make sure the backend server is running (either locally or deployed on Railway)

3. Update the `BACKEND_URL` in `app.py` to point to your backend server:

```python
# For deployed backend
BACKEND_URL = "https://ain-v2-production.up.railway.app"

# For local development
# BACKEND_URL = "http://localhost:8000"
```

### Running the Frontend

Run the Streamlit app:

```bash
streamlit run app.py
```

The app will be available at http://localhost:8501

## Usage

### Mock Interview

1. Select the "Interview" tab
2. Choose the number of questions to answer
3. Provide your responses to the interview questions
4. Enter your User ID for tracking progress
5. Click "Analyze Interview Answers" to get feedback

### DSA Challenge

1. Select the "DSA" tab
2. Choose a coding problem from the dropdown
3. Write your Python solution in the code editor
4. Enter your User ID for tracking progress
5. Click "Analyze Code" to evaluate your solution

### Resume Analysis

1. Select the "Resume Analysis" tab
2. Paste your resume text in the text area
3. Enter your User ID for tracking progress
4. Click "Analyze Resume" to get insights

### Performance Dashboard

1. Select the "Past Performance" tab
2. Enter your User ID
3. Click "Load Performance Report" to view your progress

### Combined Analysis

1. Select the "Combined Analysis" tab
2. Fill in all three sections: resume, interview answer, and code solution
3. Enter your User ID for tracking progress
4. Click "Run Combined Analysis" for comprehensive feedback

## Integration with Backend

The frontend communicates with the backend through REST API calls to the following endpoints:

- `/analyze/interview`: Evaluates interview answers
- `/analyze/code`: Analyzes code solutions
- `/analyze/resume`: Processes resume text
- `/performance/{user_id}`: Retrieves user performance data
- `/track/session`: Records session data
- `/analyze/combined`: Performs comprehensive analysis

## Deployment

The frontend can be deployed to various platforms:

### Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Set the build command to `pip install -r requirements.txt`
4. Set the start command to `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

### Streamlit Cloud

1. Push your code to GitHub
2. Sign in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect to your repository
4. Configure the app settings and deploy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
