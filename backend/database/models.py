import sqlite3
import os
from sqlite3 import Error
import json

def get_db_path():
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'db.sqlite3')

def init_db():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                resume TEXT,
                user_answers TEXT,
                code_solution TEXT,
                resume_feedback TEXT,
                interview_results TEXT,
                dsa_results TEXT,
                behavioral_results TEXT,
                final_report TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")

def save_session(session_data):
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (
                session_id, resume, user_answers, code_solution, 
                resume_feedback, interview_results, dsa_results, 
                behavioral_results, final_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get("session_id"),
            session_data.get("resume"),
            json.dumps(session_data.get("user_answers", [])),
            session_data.get("code_solution", ""),
            json.dumps(session_data.get("resume_feedback", {})),
            json.dumps(session_data.get("interview_results", {})),
            json.dumps(session_data.get("dsa_results", {})),
            json.dumps(session_data.get("behavioral_results", {})),
            json.dumps(session_data.get("final_report", {}))
        ))
        conn.commit()
        conn.close()
        return True
    except Error as e:
        print(f"Error saving session: {e}")
        return False

def get_session(session_id):
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return {
            "session_id": row[0],
            "resume": row[1],
            "user_answers": json.loads(row[2]) if row[2] else [],
            "code_solution": row[3],
            "resume_feedback": json.loads(row[4]) if row[4] else {},
            "interview_results": json.loads(row[5]) if row[5] else {},
            "dsa_results": json.loads(row[6]) if row[6] else {},
            "behavioral_results": json.loads(row[7]) if row[7] else {},
            "final_report": json.loads(row[8]) if row[8] else {}
        }
    except Error as e:
        print(f"Error retrieving session: {e}")
        return None