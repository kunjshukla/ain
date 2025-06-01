"""
Main entry point for Streamlit Cloud deployment
This file redirects to the frontend/app.py file
"""
import sys
import os

# Add the frontend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "frontend"))

# Import the app from the frontend directory
from app import *
