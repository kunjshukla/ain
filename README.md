# AI NinjaCoach

AI NinjaCoach is a comprehensive interview preparation platform powered by multiple AI agents to help users prepare for technical interviews through resume analysis, mock interviews, DSA evaluations, and performance tracking.

## Deployed URLs

- **Frontend**: [https://frontend-production-cae7.up.railway.app](https://frontend-production-cae7.up.railway.app)
- **Backend**: [https://ain-v2-production.up.railway.app](https://ain-v2-production.up.railway.app)

## Features

- **Resume Analysis**: Upload or paste your resume to get insights on skills, role matches, and suggested interview questions
- **Mock Interview**: Practice answering behavioral interview questions and receive AI-powered feedback
- **DSA Challenges**: Solve coding problems and get evaluations on correctness, complexity, and style
- **Video Interview**: Record or upload video responses to interview questions and receive feedback on verbal and non-verbal communication
- **Performance Dashboard**: Track your progress over time with detailed metrics and visualizations
- **Combined Analysis**: Get comprehensive feedback by analyzing your resume, interview answers, code solutions, and video interviews together

## Project Structure

```
/ain
├── backend/                # FastAPI backend
│   ├── agents/            # AI agent implementations
│   ├── database/          # Database models and functions
│   ├── Dockerfile         # Docker configuration for backend
│   ├── main.py            # Main API endpoints
│   ├── requirements.txt   # Python dependencies
│   └── start.sh           # Startup script for Railway
└── frontend/              # Streamlit frontend
    ├── app.py             # Main Streamlit application
    ├── Dockerfile         # Docker configuration for frontend
    ├── railway.json       # Railway deployment configuration
    ├── requirements.txt   # Python dependencies
    └── start.sh           # Startup script for Railway
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

Both the frontend and backend are deployed on Railway:

### Backend Deployment

```bash
cd /path/to/ain/backend
railway login
railway link
railway up
```

### Frontend Deployment

```bash
cd /path/to/ain/frontend
railway login
railway init
railway up
```

## Local Development

### Backend

```bash
cd /path/to/ain/backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
```

### Frontend

```bash
cd /path/to/ain/frontend
pip install -r requirements.txt
streamlit run app.py
```

## Testing

### API Testing

```bash
# Test resume analysis
curl -X POST https://ain-v2-production.up.railway.app/analyze/resume \
  -H "Content-Type: application/json" \
  -d '{"text": "Software Engineer with 5 years of experience in Python, JavaScript, and React. Skilled in machine learning and data analysis."}'

# Test interview evaluation
curl -X POST https://ain-v2-production.up.railway.app/analyze/interview \
  -H "Content-Type: application/json" \
  -d '{"responses": ["I am a software engineer with 5 years of experience in Python and JavaScript."], "question_set": "default"}'

# Test code evaluation
curl -X POST https://ain-v2-production.up.railway.app/analyze/code \
  -H "Content-Type: application/json" \
  -d '{"code": "def reverse_string(s):\n    return s[::-1]", "problem": "reverse_string"}'

# Test video interview questions
curl -X POST https://ain-v2-production.up.railway.app/video-interview/questions \
  -H "Content-Type: application/json" \
  -d '{"category": "behavioral", "count": 5}'

# Test video interview analysis (note: actual base64 video data would be much longer)
curl -X POST https://ain-v2-production.up.railway.app/analyze/video-interview \
  -H "Content-Type: application/json" \
  -d '{"video_data": "base64_encoded_video_data", "question": "Tell me about a time you faced a challenge at work", "user_id": "user123"}'
```

## Fallback Mechanisms

The platform includes robust fallback mechanisms:

1. **ResumeAnalyzerAgent**: Fallback from en_core_web_lg to en_core_web_sm, with final fallback to regex-based skill matching
2. **MockInterviewerAgent**: SpaCy model fallback with basic text analysis when no models are available
3. **PerformanceTrackerAgent**: Error handling for file operations with backup creation
4. **BehavioralCoachAgent**: Fallback mechanisms for missing Google API key

## Future Enhancements

1. **User Authentication**: Add user authentication for secure access
2. **PDF Resume Parsing**: Implement PDF resume parsing for better user experience
3. **More DSA Problems**: Expand the library of coding problems
4. **Advanced Visualizations**: Enhance data visualization for performance metrics
5. **Mobile Optimization**: Improve mobile responsiveness

## Contributors

- Kunj Shukla

## License

MIT

A comprehensive AI-powered interview preparation platform that helps candidates prepare for technical and behavioral interviews.

## Features

- **Resume Analysis**: Get detailed feedback on your resume
- **Mock Interviews**: Practice with AI-powered mock interviews
- **DSA Evaluation**: Solve coding problems with automated evaluation
- **Behavioral Coaching**: Get feedback on your behavioral responses
- **Performance Tracking**: Track your progress over time

## Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **AI/ML**: LangChain, Google Generative AI
- **Database**: SQLite (file-based)
- **Frontend**: (To be implemented)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Google Cloud API key with Generative AI enabled

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aininjacoach.git
   cd aininjacoach/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install spaCy models (at least one is required):
   ```bash
   # Install the small English model (recommended)
   python -m spacy download en_core_web_sm
   
   # Optionally install the large model for better performance (if you have sufficient resources)
   python -m spacy download en_core_web_lg
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

### Running the Application

1. Start the backend server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. The API will be available at `http://localhost:8000`
3. API documentation will be available at `http://localhost:8000/docs`

### Fallback Mechanisms

The application includes several fallback mechanisms to ensure robustness:

1. **spaCy Model Fallbacks**:
   - The system will first try to load the large English model (`en_core_web_lg`)
   - If unavailable, it falls back to the small English model (`en_core_web_sm`)
   - If no spaCy models are available, it uses basic text processing techniques

2. **API Key Fallbacks**:
   - If Google API keys are missing, the system will use simplified evaluation logic

3. **Data Storage Fallbacks**:
   - If the performance data directory cannot be created, data will be stored in the current directory
   - Corrupted data files are automatically backed up and recreated

### Deployment

#### Railway Deployment

1. **Install Railway CLI** (if deploying locally):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize a new Railway project** (if not connecting to an existing one):
   ```bash
   cd backend
   railway init
   ```

4. **Set up environment variables**:
   ```bash
   railway variables set GOOGLE_API_KEY=your_google_api_key_here
   ```
   - `GOOGLE_API_KEY` (optional): Your Google API key for enhanced behavioral analysis
   - `OPENAI_API_KEY` (optional): Your OpenAI API key for enhanced language processing

5. **Deploy the application**:
   ```bash
   railway up
   ```

6. **Alternative: Deploy via Railway Dashboard**:
   - Create a new project in Railway dashboard
   - Connect your GitHub repository
   - Railway will automatically detect the Dockerfile and deploy using it
   - Add environment variables in the project settings
   - Deploy the application

7. **Monitor the deployment**:
   - Check the deployment logs for any issues
   - Verify that the spaCy model is installed correctly
   - Test the API endpoints once deployment is complete

#### Frontend Connection

Connect your frontend to the backend API using the Railway-provided URL. The API endpoints are documented at `/docs` on your deployed instance.

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