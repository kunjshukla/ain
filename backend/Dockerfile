FROM python:3.10-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Create a clean version of requirements without any problematic dependencies
RUN grep -v "crewai" requirements.txt > clean_requirements.txt

# Install dependencies from clean requirements
RUN pip install --no-cache-dir -r clean_requirements.txt

# Install spaCy models (small model for fallback)
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Fix line endings and make executable
RUN chmod +x start.sh

# Run directly without shell interpretation
CMD ["./start.sh"]