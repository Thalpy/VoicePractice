# Voice Practice - Real-time Voice Analysis Tool

A sophisticated voice analysis application designed for voice training and feminization practice. Available as both a desktop application and web-based tool.

## 🚀 Quick Start

### Option 1: Web Version (Recommended for beginners)
```bash
python web_app.py
```
Then open http://localhost:5000 in your browser.

### Option 2: Desktop Application (Full features)
```bash
# First, run diagnostics and install dependencies
python diagnose_and_fix.py

# If dependencies are missing, run:
python setup_fixed.py

# Then start the application
python main.py
```

## 📋 Prerequisites

- Python 3.8 or higher
- A working microphone
- Windows, macOS, or Linux

## 🔧 Installation & Setup

### Automated Setup (Recommended)

1. **Run the diagnostic tool:**
   ```bash
   python diagnose_and_fix.py
   ```

2. **Install dependencies if needed:**
   ```bash
   python setup_fixed.py
   ```

3. **Start the application:**
   ```bash
   python main.py          # Desktop version
   # OR
   python web_app.py       # Web version
   ```

### Manual Setup

If the automated setup doesn't work:

```bash
# Install core dependencies
pip install numpy scipy

# Install audio libraries
pip install sounddevice librosa soundfile

# Install GUI libraries (for desktop version)
pip install PyQt5 pyqtgraph matplotlib

# Install ML libraries (for advanced features)
pip install torch torchaudio openai-whisper

# Install utilities
pip install keyboard flask
```

## 🎯 Features

### Desktop Application
- **Real-time Audio Analysis**: Live pitch, resonance, and intonation tracking
- **Advanced Visualizations**: Spectrograms, phoneme plots, real-time waveforms
- **Speech Recognition**: Detailed phoneme breakdown using OpenAI Whisper
- **Overlay GUI**: Always-on-top, draggable interface
- **Hotkey Support**: Toggle visibility with Ctrl+Shift+V
- **Configurable Targets**: Customizable pitch and resonance ranges

### Web Application
- **Browser-based**: No complex installation required
- **Real-time Pitch Tracking**: Live frequency analysis
- **Volume Monitoring**: Audio level detection
- **Interactive Charts**: Visual feedback with Chart.js
- **Session Statistics**: Track your progress over time
- **Mobile Friendly**: Works on tablets and phones

## 📊 Understanding the Metrics

- **Pitch**: Fundamental frequency in Hz
  - Feminine target: 165-255 Hz
  - Masculine range: 85-180 Hz
- **Volume**: Audio amplitude (0.0-1.0)
- **Resonance**: Spectral centroid indicating vocal tract characteristics
- **Intonation**: Pitch variation patterns

## 🎮 Usage

### Desktop Version
1. Start with `python main.py`
2. Adjust microphone sensitivity using the volume slider
3. Speak and monitor real-time feedback
4. Use Ctrl+Shift+V to toggle overlay visibility
5. Enable spectrogram view for detailed frequency analysis

### Web Version
1. Start with `python web_app.py`
2. Open http://localhost:5000 in your browser
3. Click "Start Analysis" and allow microphone access
4. Speak and watch the live charts update
5. View session statistics in real-time

## ⚙️ Configuration

### config.json
Main application settings:
```json
{
  "pitch": {
    "target_min": 165.0,
    "target_max": 255.0
  },
  "audio": {
    "sample_rate": 22050,
    "buffer_size": 1024
  }
}
```

### settings.json
User preferences:
```json
{
  "dev": true,
  "logs": "./logs/",
  "recordings": "./rec/"
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   python diagnose_and_fix.py
   ```

2. **No Audio Input**
   - Check microphone permissions
   - Verify default audio device
   - Test with `python -c "import sounddevice; print(sounddevice.query_devices())"`

3. **Web App Not Loading**
   - Ensure Flask is installed: `pip install flask`
   - Check if port 5000 is available
   - Try a different port: `python web_app.py --port 8080`

4. **High CPU Usage**
   - Reduce buffer size in config.json
   - Lower update frequency
   - Close other audio applications

### Debug Mode

Enable detailed logging in settings.json:
```json
{
  "dev": true
}
```

## 🏗️ Project Structure

```
VoicePractice/
├── main.py                 # Desktop app entry point
├── web_app.py             # Web app entry point
├── diagnose_and_fix.py    # Diagnostic tool
├── setup_fixed.py         # Automated setup
├── config.json            # Application configuration
├── settings.json          # User preferences
├── overlay_gui.py         # Desktop GUI
├── live_analysis_system.py # Real-time processing
├── templates/             # Web app templates
├── library/               # Core processing modules
└── logs/                  # Application logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test with both desktop and web versions
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- librosa for audio analysis
- PyQt5 for desktop GUI
- Chart.js for web visualizations
- Flask for web framework