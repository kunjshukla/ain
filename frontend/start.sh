#!/bin/bash

# Get the PORT from Railway environment or use default 8501
PORT=${PORT:-8501}

# Run Streamlit
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
