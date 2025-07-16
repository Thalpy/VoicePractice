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
        timestamp = datetime.now().isoformat()
        
        # Store the enhanced data (in a real app, you'd use a database)
        if 'pitch' in data:
            voice_data['pitch_history'].append({
                'timestamp': timestamp,
                'value': data['pitch']
            })
        
        if 'volume' in data:
            voice_data['volume_history'].append({
                'timestamp': timestamp,
                'value': data['volume']
            })
        
        # Store new data types
        if 'resonance' in data:
            if 'resonance_history' not in voice_data:
                voice_data['resonance_history'] = []
            voice_data['resonance_history'].append({
                'timestamp': timestamp,
                'value': data['resonance']
            })
        
        if 'intonation' in data:
            if 'intonation_history' not in voice_data:
                voice_data['intonation_history'] = []
            voice_data['intonation_history'].append({
                'timestamp': timestamp,
                'value': data['intonation']
            })
        
        if 'phoneme' in data and data['phoneme']:
            if 'phoneme_history' not in voice_data:
                voice_data['phoneme_history'] = []
            voice_data['phoneme_history'].append({
                'timestamp': timestamp,
                'phoneme': data['phoneme']['phoneme'],
                'confidence': data['phoneme']['confidence'],
                'pitch': data['pitch'],
                'resonance': data['resonance']
            })
        
        # Keep only last 100 entries for all data types
        for key in ['pitch_history', 'volume_history', 'resonance_history', 'intonation_history']:
            if key in voice_data:
                voice_data[key] = voice_data[key][-100:]
        
        # Keep last 50 phonemes (they're less frequent)
        if 'phoneme_history' in voice_data:
            voice_data['phoneme_history'] = voice_data['phoneme_history'][-50:]
        
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
        
        stats = {
            'avg_pitch': np.mean(pitch_values) if pitch_values else 0,
            'pitch_range': (np.max(pitch_values) - np.min(pitch_values)) if pitch_values else 0,
            'min_pitch': np.min(pitch_values) if pitch_values else 0,
            'max_pitch': np.max(pitch_values) if pitch_values else 0,
            'total_samples': len(pitch_values),
            'session_duration': (datetime.now() - datetime.fromisoformat(voice_data['session_start'])).total_seconds()
        }
        
        # Add resonance statistics
        if 'resonance_history' in voice_data:
            resonance_values = [entry['value'] for entry in voice_data['resonance_history'] if entry['value'] > 0]
            if resonance_values:
                stats.update({
                    'avg_resonance': np.mean(resonance_values),
                    'resonance_range': np.max(resonance_values) - np.min(resonance_values),
                    'min_resonance': np.min(resonance_values),
                    'max_resonance': np.max(resonance_values)
                })
        
        # Add intonation statistics
        if 'intonation_history' in voice_data:
            intonation_values = [entry['value'] for entry in voice_data['intonation_history'] if entry['value'] > 0]
            if intonation_values:
                stats.update({
                    'avg_intonation': np.mean(intonation_values),
                    'intonation_range': np.max(intonation_values) - np.min(intonation_values)
                })
        
        # Add phoneme statistics
        if 'phoneme_history' in voice_data:
            phoneme_counts = {}
            for entry in voice_data['phoneme_history']:
                phoneme = entry['phoneme']
                phoneme_counts[phoneme] = phoneme_counts.get(phoneme, 0) + 1
            
            stats.update({
                'total_phonemes': len(voice_data['phoneme_history']),
                'unique_phonemes': len(phoneme_counts),
                'most_common_phoneme': max(phoneme_counts.items(), key=lambda x: x[1])[0] if phoneme_counts else None
            })
        
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