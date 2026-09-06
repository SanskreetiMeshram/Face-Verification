#!/bin/bash
echo "==================================================="
echo "    Starting FaceChain Verify (Universal App)"
echo "==================================================="

# Setup virtual environment if missing
if [ ! -d "backend_venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv backend_venv
    source backend_venv/bin/activate
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
else
    source backend_venv/bin/activate
fi

python3 run_server.py
