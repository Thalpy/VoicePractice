#!/usr/bin/env python3
"""
Simple web-based voice analysis tool
Alternative to the complex desktop application
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Simple in-memory storage for demo
voice_data = {
    'pitch_history': [],
    'volume_history': [],
    'session_start': datetime.now().isoformat()
}

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/config')
def get_config():
    """Get application configuration"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice-data', methods=['POST'])
def receive_voice_data():
    """Receive voice analysis data from client"""
    try:
        data = request.json
        
        # Store the data (in a real app, you'd use a database)
        if 'pitch' in data:
            voice_data['pitch_history'].append({
                'timestamp': datetime.now().isoformat(),
                'value': data['pitch']
            })
        
        if 'volume' in data:
            voice_data['volume_history'].append({
                'timestamp': datetime.now().isoformat(),
                'value': data['volume']
            })
        
        # Keep only last 100 entries
        voice_data['pitch_history'] = voice_data['pitch_history'][-100:]
        voice_data['volume_history'] = voice_data['volume_history'][-100:]
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice-data', methods=['GET'])
def get_voice_data():
    """Get current voice analysis data"""
    return jsonify(voice_data)

@app.route('/api/stats')
def get_stats():
    """Get voice analysis statistics"""
    try:
        pitch_values = [entry['value'] for entry in voice_data['pitch_history'] if entry['value'] > 0]
        
        if not pitch_values:
            return jsonify({
                'avg_pitch': 0,
                'pitch_range': 0,
                'total_samples': 0
            })
        
        stats = {
            'avg_pitch': np.mean(pitch_values),
            'pitch_range': np.max(pitch_values) - np.min(pitch_values),
            'min_pitch': np.min(pitch_values),
            'max_pitch': np.max(pitch_values),
            'total_samples': len(pitch_values),
            'session_duration': (datetime.now() - datetime.fromisoformat(voice_data['session_start'])).total_seconds()
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("Starting Voice Practice Web App...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)