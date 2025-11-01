# AI NinjaCoach

AI NinjaCoach is a comprehensive AI-powered interview preparation platform. It helps users prepare for technical interviews through resume analysis, mock interviews, DSA/code evaluation, and performance tracking. The platform uses robust fallback mechanisms to ensure reliability across various environments.

## Deployment Overview

- **Frontend**: Streamlit app (deployable on Streamlit Cloud, Render, or locally)
- **Backend**: FastAPI app (deployable on Render, Heroku, or any cloud provider)

**Live Demo:**
- Backend API: Deploy your own instance (instructions below)

## Features

- **Resume Analysis**: Upload or paste your resume to get insights on skills, role matches, strengths, weaknesses, and suggested interview questions.
- **Mock Interview**: Practice answering behavioral interview questions and receive AI-powered feedback.
- **DSA Challenges**: Solve coding problems and get evaluations on correctness, complexity, and style.
- **Performance Dashboard**: Track your progress over time with detailed metrics and visualizations.
- **Combined Analysis**: Get comprehensive feedback by analyzing your resume, interview answers, and code solutions together.

## Project Structure

```
/ain
├── backend/                  # FastAPI backend
│   ├── agents/               # AI agent implementations
│   ├── database/             # Database models and functions
│   ├── main.py               # Main API endpoints
│   ├── utils/                # Utility modules (PDF parser, etc.)
│   ├── requirements.txt      # Backend dependencies
│   └── ...
├── frontend/                 # Streamlit frontend
│   ├── app.py                # Main Streamlit application
│   └── requirements.txt      # Frontend dependencies
├── render.yaml               # Render deployment configuration
├── render-requirements.txt   # Backend requirements for Render
├── postinstall.sh            # Script for installing spaCy models
└── README.md                 # This file
```

## Backend Architecture

### AI Agents
- **ResumeAnalyzerAgent**: Analyzes resumes to extract skills, match roles, and suggest interview questions (with robust spaCy/regex fallback)
- **MockInterviewerAgent**: Evaluates interview responses and provides feedback (with spaCy and basic fallback)
- **DSAEvaluatorAgent**: Evaluates code solutions for correctness, complexity, and style
- **BehavioralCoachAgent**: Provides coaching on behavioral interview questions
- **PerformanceTrackerAgent**: Tracks user performance across sessions (with file/database fallback)

### Database
- **SQLite Database**: For persistent storage of user data, sessions, and performance metrics
- **JSON File-based Storage**: Fallback for performance tracking if DB is unavailable

### Fallback & Error Handling
- Agents and utilities use layered import and logic fallbacks for maximum reliability
- PDF parsing falls back to stub/no-op if dependencies are missing
- All endpoints and agents handle missing dependencies gracefully, never crashing the server

## API Endpoints

- `POST /analyze/resume` — Analyze resume text
- `POST /analyze/interview` — Evaluate interview answers
- `POST /analyze/code` — Evaluate code solutions
- `POST /analyze/combined` — Combined analysis of resume, interview responses, and code solutions
- `GET /performance/{user_id}` — Retrieve user performance data
- `POST /track/session` — Record session data

**Note:** Video interview endpoints and features have been removed for this release.

## Environment Variables & Secrets

**Backend:**
- `GOOGLE_API_KEY` — (Optional) For advanced NLP features
- `OPENAI_API_KEY` — (Optional) For LLM integration
- `PORT` — Port for backend server (default: 10000)
- `PYTHON_VERSION` — Python version (e.g., 3.10.0)

**Frontend:**
- `BACKEND_URL` — URL of the deployed backend API (e.g., `https://ain-backend-api.onrender.com`)
- `FALLBACK_BACKEND_URL` — (Optional) Fallback backend URL

Set these as environment variables on your deployment platform (Render, Streamlit Cloud, etc.). Do **not** hardcode secrets in your source code.

## Local Development

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Deployment Instructions

### Backend (Render)
- Configure `render.yaml` and `render-requirements.txt` as shown in this repo
- Set environment variables via the Render dashboard for secrets
- Ensure `postinstall.sh` is executable to install spaCy models

### Frontend (Streamlit Cloud or Render)
- Set `BACKEND_URL` and any other needed variables in the platform's environment settings
- Deploy the `frontend/app.py` as your main app

## Fallback Mechanisms
- All major features (resume analysis, interview, DSA, performance tracking) have robust fallbacks for missing dependencies, services, or models
- The frontend gracefully falls back to alternate backends or simulated responses if the main backend is unavailable

## Security & Best Practices
- Never commit secrets to version control
- Use environment variables for all sensitive configuration
- Restrict CORS on the backend to only allow requests from your frontend domain

## License
MIT

- `/analyze/combined`: Performs comprehensive analysis

## Frontend

The frontend is built with Streamlit and provides a user-friendly interface for interacting with the AI NinjaCoach platform. It includes:

- Multiple tabs for different features
- Form inputs for user data
- Visualizations for performance metrics
- Error handling and user feedback

## Deployment

The application is configured for deployment on Streamlit Cloud:

### Streamlit Cloud Deployment

1. **Fork or push the repository to GitHub**:
   - Make sure your repository is public or you have access to deploy from it

2. **Sign up for Streamlit Cloud**:
   - Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account

3. **Deploy the Streamlit app**:
   - Click "New app"
   - Select your repository, branch, and the `streamlit_app.py` file
   - Click "Deploy"

4. **Configure environment variables**:
   - In the Streamlit Cloud dashboard, go to your app settings
   - Add the following environment variables:
     - `BACKEND_URL`: URL of your deployed backend API
     - Any other required API keys or configuration

5. **Deploy the backend separately**:
   - Deploy the backend on a service like Render, Heroku, or other cloud platforms
   - Make sure to set the appropriate environment variables for the backend
   - Deploy the application

7. **Monitor the deployment**:
   - Check the deployment logs for any issues
   - Verify that the spaCy model is installed correctly
   - Test the API endpoints once deployment is complete

#### Frontend Connection

Connect your frontend to the backend API by setting the `BACKEND_URL` environment variable in Streamlit Cloud. The API endpoints are documented at `/docs` on your deployed backend instance.

## API Endpoints

### Analysis Endpoints

- `POST /analyze/resume` - Analyze resume and extract skills, role matches, and generate questions
- `POST /analyze/interview` - Evaluate interview responses with detailed feedback
- `POST /analyze/code` - Evaluate coding solutions for correctness, complexity, and style
- `POST /analyze/video-interview` - Analyze video interviews for verbal and non-verbal communication skills
- `POST /video-interview/questions` - Retrieve interview questions by category
- `POST /analyze/combined` - Combined analysis of resume, interview responses, code solutions, and video interviews

### Performance Tracking

- `POST /track/session` - Track a user session with metrics
- `GET /performance/{user_id}` - Get comprehensive user performance report

### API Documentation

Once deployed, full API documentation with request/response schemas is available at:
- Swagger UI: `https://your-railway-url/docs`
- ReDoc: `https://your-railway-url/redoc`

## Environment Variables

See `.env.example` for all available environment variables.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

![alt text](<Screenshot from 2025-06-01 22-39-17.png>)
