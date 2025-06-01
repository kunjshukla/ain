import sqlite3
import os
import json
from sqlite3 import Error
from datetime import datetime
from .models import get_db_path

def init_user_db():
    """Initialize the user database tables"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at TEXT,
                last_active TEXT
            )
        """)
        
        # Create user_sessions table to track all sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                session_type TEXT,
                timestamp TEXT,
                metrics TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Create user_skills table to track skills from resume
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                skill TEXT,
                skill_type TEXT,
                confidence REAL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Error initializing user database: {e}")
        return False

def register_user(user_id, name="", email=""):
    """Register a new user or update existing user"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing_user:
            # Update last active
            cursor.execute("""
                UPDATE users SET last_active = ? WHERE user_id = ?
            """, (now, user_id))
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (user_id, name, email, created_at, last_active)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, email, now, now))
        
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Error registering user: {e}")
        return False

def track_user_session(user_id, session_id, session_type, metrics):
    """Track a user session with metrics"""
    try:
        # Register user if not exists
        register_user(user_id)
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Insert session
        cursor.execute("""
            INSERT INTO user_sessions (user_id, session_id, session_type, timestamp, metrics)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            session_id,
            session_type,
            datetime.now().isoformat(),
            json.dumps(metrics)
        ))
        
        # If resume skills are in metrics, update user skills
        if session_type == "resume" and "resume_skills" in metrics:
            skills = metrics.get("resume_skills", [])
            for skill in skills:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_skills (user_id, skill, skill_type, confidence)
                    VALUES (?, ?, ?, ?)
                """, (user_id, skill, "technical", 0.8))
        
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Error tracking user session: {e}")
        return False

def get_user_performance(user_id):
    """Get comprehensive user performance data"""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return {"error": "User not found"}
        
        # Get all user sessions
        cursor.execute("""
            SELECT * FROM user_sessions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
        """, (user_id,))
        sessions = [dict(row) for row in cursor.fetchall()]
        
        # Process sessions to extract metrics
        processed_sessions = []
        interview_scores = []
        dsa_scores = []
        
        for session in sessions:
            session_data = dict(session)
            metrics = json.loads(session_data.get("metrics", "{}"))
            
            # Add metrics to session data
            session_data.update(metrics)
            
            # Track scores for averages
            if "interview_score" in metrics:
                interview_scores.append(float(metrics["interview_score"]))
            if "code_correctness" in metrics:
                dsa_scores.append(float(metrics["code_correctness"]))
                
            # Remove raw metrics JSON
            del session_data["metrics"]
            processed_sessions.append(session_data)
        
        # Get user skills
        cursor.execute("SELECT skill FROM user_skills WHERE user_id = ?", (user_id,))
        skills = [row[0] for row in cursor.fetchall()]
        
        # Calculate averages
        avg_interview = sum(interview_scores) / len(interview_scores) if interview_scores else 0
        avg_dsa = sum(dsa_scores) / len(dsa_scores) if dsa_scores else 0
        
        # Compile final report
        report = {
            "user_id": user_id,
            "total_sessions": len(processed_sessions),
            "average_interview_score": avg_interview,
            "average_dsa_score": avg_dsa,
            "sessions": processed_sessions,
            "skills": skills
        }
        
        conn.close()
        return report
    except Error as e:
        print(f"Error getting user performance: {e}")
        return {"error": f"Database error: {str(e)}"}
