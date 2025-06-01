# AI Ninja Coach

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

4. Set up environment variables:
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

## API Endpoints

- `POST /api/session/start` - Start a new session
- `GET /api/session/{session_id}` - Get session data
- `POST /api/analyze/resume/{session_id}` - Analyze resume

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