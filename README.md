# AI NinjaCoach

AI NinjaCoach is a comprehensive interview preparation platform powered by multiple AI agents to help users prepare for technical interviews through resume analysis, mock interviews, DSA evaluations, and performance tracking.

## Deployment

This application is configured for deployment on Streamlit Cloud:

- **Streamlit App**: [https://ai-ninjacoach.streamlit.app](https://ai-ninjacoach.streamlit.app)
- **Backend API**: Deploy separately on a service like Render, Heroku, or other cloud platforms

## Features

- **Resume Analysis**: Upload or paste your resume to get insights on skills, role matches, and suggested interview questions
- **Mock Interview**: Practice answering behavioral interview questions and receive AI-powered feedback
- **DSA Challenges**: Solve coding problems and get evaluations on correctness, complexity, and style
- **Performance Dashboard**: Track your progress over time with detailed metrics and visualizations
- **Combined Analysis**: Get comprehensive feedback by analyzing your resume, interview answers, and code solutions together

## Project Structure

```
/ain
├── backend/                # FastAPI backend
│   ├── agents/            # AI agent implementations
│   ├── database/          # Database models and functions
│   ├── Dockerfile         # Docker configuration for backend
│   ├── main.py            # Main API endpoints
│   └── requirements.txt   # Frontend dependencies
└── frontend/              # Streamlit frontend
    ├── app.py             # Main Streamlit application
    ├── Dockerfile         # Docker configuration for frontend
    └── requirements.txt   # Backend dependencies
```

## Backend Architecture

### AI Agents

1. **ResumeAnalyzerAgent**: Analyzes resumes to extract skills, match roles, and suggest interview questions
2. **MockInterviewerAgent**: Evaluates interview responses and provides feedback
3. **DSAEvaluatorAgent**: Evaluates code solutions for correctness, complexity, and style
4. **BehavioralCoachAgent**: Provides coaching on behavioral interview questions
5. **VideoInterviewAgent**: Analyzes video interviews for verbal and non-verbal communication skills
6. **PerformanceTrackerAgent**: Tracks user performance across sessions

### Database

The platform uses a dual storage system:
- **SQLite Database**: For persistent storage of user data, sessions, and performance metrics
- **JSON File-based Storage**: Legacy system for performance tracking with fallback mechanism

### API Endpoints

- `/analyze/resume`: Analyzes resume text
- `/analyze/interview`: Evaluates interview answers
- `/analyze/code`: Analyzes code solutions
- `/analyze/video-interview`: Analyzes video interview recordings
- `/video-interview/questions`: Retrieves interview questions by category
- `/performance/{user_id}`: Retrieves user performance data
- `/track/session`: Records session data
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