#!/bin/bash
set -e
echo "Installing spaCy English model (en_core_web_sm)..."
python3 -m spacy download en_core_web_sm
