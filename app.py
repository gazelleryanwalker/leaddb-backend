#!/usr/bin/env python3
"""
Entry point for the LeadDB Flask application.
This file serves as the main entry point for Railway deployment.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from src/main.py
from src.main import app

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
