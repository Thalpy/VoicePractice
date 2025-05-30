#!/bin/bash

echo "Setting up VoicePractice environment..."

# Step 1: Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Make sure Python 3 is installed."
    exit 1
fi
echo "Virtual environment created."

# Step 2: Activate the virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi
echo "Virtual environment activated."

# Step 3: Upgrade pip
pip install --upgrade pip

# Step 4: Install dependencies
if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found. Please run this script from the VoicePractice directory."
    exit 1
fi

pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi
echo "Dependencies installed."

# Step 5: Run the CLI pitch tester
echo "Starting CLI pitch tester..."
python test_pitch_cli.py
