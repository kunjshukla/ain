# agents/performance_tracker.py
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import os
import statistics
from collections import defaultdict

class PerformanceTrackerAgent:
    def __init__(self, storage_file: str = "data/performance.json"):
        self.storage_file = storage_file
        self.data = self._load_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load performance data from JSON file or initialize new data structure with robust error handling."""
        # Default data structure
        default_data = {
            "users": {},
            "sessions": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # If file doesn't exist, return default data
        if not os.path.exists(self.storage_file):
            print(f"Performance data file not found at {self.storage_file}. Creating new data structure.")
            return default_data
            
        # Try to load existing data
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                print(f"Successfully loaded performance data with {len(data.get('sessions', []))} sessions")
                return data
        except json.JSONDecodeError as e:
            print(f"Warning: Performance data file is corrupted: {e}. Creating backup and starting fresh.")
            # Create a backup of the corrupted file
            try:
                backup_file = f"{self.storage_file}.backup.{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                os.rename(self.storage_file, backup_file)
                print(f"Created backup of corrupted file at {backup_file}")
            except OSError as e:
                print(f"Could not create backup of corrupted file: {e}")
        except Exception as e:
            print(f"Unexpected error loading performance data: {e}")
            
        return default_data
        
    def _save_data(self):
        """Save performance data to JSON file with error handling."""
        try:
            self.data["last_updated"] = datetime.utcnow().isoformat()
            # Ensure directory exists
            try:
                os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory for performance data: {e}")
                # Use a fallback location in the current directory if needed
                self.storage_file = "performance_data.json"
                
            # Write the data
            with open(self.storage_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving performance data: {e}")
            # Continue execution even if saving fails
            
    def track_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Track a new session and update user performance metrics."""
        session_id = session_data.get("session_id", str(len(self.data["sessions"]) + 1))
        timestamp = datetime.utcnow().isoformat()
        
        # Initialize user data if not exists
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "first_seen": timestamp,
                "last_seen": timestamp,
                "sessions": [],
                "metrics": self._init_metrics()
            }
        
        # Update user's last seen time
        self.data["users"][user_id]["last_seen"] = timestamp
        
        # Process session data
        session_entry = {
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "metrics": self._extract_metrics(session_data)
        }
        
        # Store session
        self.data["sessions"].append(session_entry)
        self.data["users"][user_id]["sessions"].append(session_id)
        
        # Update user metrics
        self._update_user_metrics(user_id, session_entry["metrics"])
        
        # Save changes
        self._save_data()
        return session_id
        
    def _init_metrics(self) -> Dict[str, Any]:
        """Initialize metrics structure for a new user."""
        return {
            "interview": {
                "total_sessions": 0,
                "average_score": 0.0,
                "strengths": [],
                "weaknesses": [],
                "progress": []
            },
            "dsa": {
                "problems_attempted": 0,
                "problems_solved": 0,
                "average_complexity": 0.0,
                "common_patterns": [],
                "progress": []
            },
            "resume": {
                "skills": [],
                "last_updated": None,
                "strengths": [],
                "weaknesses": []
            }
        }
        
    def _extract_metrics(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metrics from session data."""
        metrics = {
            "interview": {},
            "dsa": {},
            "resume": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Extract interview metrics
        if "interview_results" in session_data:
            interview = session_data["interview_results"]
            metrics["interview"] = {
                "score": interview.get("average_score", 0),
                "feedback": interview.get("overall_feedback", ""),
                "improvement_areas": interview.get("improvement_areas", [])
            }
        
        # Extract DSA metrics
        if "dsa_results" in session_data:
            dsa = session_data["dsa_results"]
            metrics["dsa"] = {
                "correctness": dsa.get("correctness", 0),
                "time_complexity": dsa.get("time_complexity", "N/A"),
                "style": dsa.get("style", 0),
                "suggestions": dsa.get("suggestions", [])
            }
        
        # Extract resume metrics
        if "resume_analysis" in session_data:
            resume = session_data["resume_analysis"]
            metrics["resume"] = {
                "skills": resume.get("skills", {}).get("technical", []),
                "strengths": resume.get("strengths", []),
                "weaknesses": resume.get("weaknesses", [])
            }
            
        return metrics
        
    def _update_user_metrics(self, user_id: str, session_metrics: Dict[str, Any]):
        """Update user's metrics with new session data."""
        user = self.data["users"][user_id]
        metrics = user["metrics"]
        
        # Update interview metrics
        if "interview" in session_metrics:
            interview = session_metrics["interview"]
            old_avg = metrics["interview"]["average_score"]
            old_count = metrics["interview"]["total_sessions"]
            
            metrics["interview"]["total_sessions"] += 1
            metrics["interview"]["average_score"] = (
                (old_avg * old_count + interview.get("score", 0)) / 
                (old_count + 1)
            )
            
            # Track progress
            metrics["interview"]["progress"].append({
                "timestamp": session_metrics["timestamp"],
                "score": interview.get("score", 0)
            })
            
            # Update strengths/weaknesses (simplified)
            if interview.get("score", 0) >= 0.7:  # If score is good
                metrics["interview"]["strengths"].extend(
                    [s for s in interview.get("improvement_areas", []) 
                     if s not in metrics["interview"]["strengths"]]
                )
            else:
                metrics["interview"]["weaknesses"].extend(
                    [w for w in interview.get("improvement_areas", []) 
                     if w not in metrics["interview"]["weaknesses"]]
                )
        
        # Update DSA metrics
        if "dsa" in session_metrics:
            dsa = session_metrics["dsa"]
            metrics["dsa"]["problems_attempted"] += 1
            if dsa.get("correctness", 0) >= 0.8:  # Considered solved
                metrics["dsa"]["problems_solved"] += 1
                
            # Track progress
            metrics["dsa"]["progress"].append({
                "timestamp": session_metrics["timestamp"],
                "correctness": dsa.get("correctness", 0),
                "complexity": dsa.get("time_complexity", "N/A")
            })
            
            # Update complexity average
            if dsa.get("time_complexity") and dsa["time_complexity"] != "N/A":
                # Convert complexity to numerical value for averaging
                complexity_map = {"O(1)": 1, "O(log n)": 2, "O(n)": 3, 
                                 "O(n log n)": 4, "O(n²)": 5, "O(2^n)": 6}
                complexity = complexity_map.get(dsa["time_complexity"], 0)
                old_avg = metrics["dsa"]["average_complexity"]
                old_count = metrics["dsa"]["problems_attempted"] - 1
                metrics["dsa"]["average_complexity"] = (
                    (old_avg * old_count + complexity) / 
                    (old_count + 1)
                )
        
        # Update resume metrics
        if "resume" in session_metrics:
            resume = session_metrics["resume"]
            metrics["resume"]["skills"] = list(set(
                metrics["resume"]["skills"] + resume.get("skills", [])
            ))
            metrics["resume"]["strengths"] = list(set(
                metrics["resume"]["strengths"] + resume.get("strengths", [])
            ))
            metrics["resume"]["weaknesses"] = list(set(
                metrics["resume"]["weaknesses"] + resume.get("weaknesses", [])
            ))
            metrics["resume"]["last_updated"] = session_metrics["timestamp"]
    
    def get_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance report for a user."""
        if user_id not in self.data["users"]:
            return {
            "user_id": user_id,
            "sessions": [],
            "summary": "No performance data yet."
        }
            
        user = self.data["users"][user_id]
        sessions = [s for s in self.data["sessions"] 
                   if s["user_id"] == user_id]
        
        # Calculate time-based metrics
        first_seen = parse(user["first_seen"])
        last_seen = parse(user["last_seen"])
        days_active = (last_seen - first_seen).days or 1
        
        # Generate performance insights
        insights = self._generate_insights(user_id, sessions)
        
        return {
            "user_id": user_id,
            "activity": {
                "first_seen": user["first_seen"],
                "last_seen": user["last_seen"],
                "total_sessions": len(user["sessions"]),
                "sessions_per_week": len(user["sessions"]) / (days_active / 7),
                "recent_sessions": sessions[-5:]  # Last 5 sessions
            },
            "metrics": user["metrics"],
            "insights": insights,
            "recommendations": self._generate_recommendations(user["metrics"])
        }
        
    def _generate_insights(self, user_id: str, sessions: List[Dict]) -> Dict[str, Any]:
        """Generate performance insights from user sessions."""
        if not sessions:
            return {}
            
        # Calculate trend for interview scores
        interview_scores = [
            (parse(s["timestamp"]), s["metrics"]["interview"].get("score", 0))
            for s in sessions if "interview" in s["metrics"]
        ]
        
        # Calculate trend for DSA correctness
        dsa_scores = [
            (parse(s["timestamp"]), s["metrics"]["dsa"].get("correctness", 0))
            for s in sessions if "dsa" in s["metrics"]
        ]
        
        # Calculate skill distribution
        skill_dist = defaultdict(int)
        for s in sessions:
            if "resume" in s["metrics"]:
                for skill in s["metrics"]["resume"].get("skills", []):
                    skill_dist[skill] += 1
        
        return {
            "interview_trend": self._calculate_trend(interview_scores),
            "dsa_trend": self._calculate_trend(dsa_scores),
            "top_skills": sorted(
                skill_dist.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]  # Top 5 skills
        }
        
    def _calculate_trend(self, data: List[Tuple[datetime, float]]) -> float:
        """Calculate trend slope using linear regression (simplified)."""
        if len(data) < 2:
            return 0.0
            
        # Simple trend calculation: (last - first) / days
        data.sort()  # Sort by timestamp
        days = (data[-1][0] - data[0][0]).days or 1
        return (data[-1][1] - data[0][1]) / days
        
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on metrics."""
        recs = []
        
        # Interview recommendations
        if metrics["interview"]["total_sessions"] > 0:
            if metrics["interview"]["average_score"] < 0.6:
                recs.append("Focus on improving your interview performance. Consider practicing more mock interviews.")
            if metrics["interview"]["weaknesses"]:
                recs.append(f"Work on: {', '.join(metrics['interview']['weaknesses'][:3])}")
        
        # DSA recommendations
        if metrics["dsa"]["problems_attempted"] > 0:
            success_rate = (metrics["dsa"]["problems_solved"] / 
                          metrics["dsa"]["problems_attempted"])
            if success_rate < 0.7:
                recs.append("Practice more DSA problems to improve your problem-solving skills.")
            if metrics["dsa"]["average_complexity"] < 3:  # Below O(n)
                recs.append("Challenge yourself with more complex algorithms and data structures.")
        
        # Resume recommendations
        if len(metrics["resume"]["skills"]) < 5:
            recs.append("Consider adding more technical skills to your resume.")
        if metrics["resume"]["weaknesses"]:
            recs.append(f"Address resume weaknesses: {', '.join(metrics['resume']['weaknesses'][:2])}")
            
        return recs or ["Keep up the good work! Your performance metrics look solid."]
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieve a specific session by ID."""
        for session in self.data["sessions"]:
            if session["session_id"] == session_id:
                return session
        raise ValueError(f"Session {session_id} not found")
    
    def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions for a user."""
        if user_id not in self.data["users"]:
            return []
            
        user_sessions = [s for s in self.data["sessions"] 
                        if s["user_id"] == user_id]
        return sorted(
            user_sessions,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]