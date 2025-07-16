# Voice Practice - Real-time Voice Analysis Tool

A sophisticated real-time voice analysis application designed for voice training and feminization practice. Features live pitch tracking, resonance analysis, intonation monitoring, and phoneme visualization.

## Features

- **Real-time Audio Analysis**: Live pitch, resonance, and intonation tracking
- **Visual Feedback**: Interactive plots showing voice metrics over time
- **Phoneme Analysis**: Speech-to-text with detailed phoneme breakdown
- **Spectrogram Visualization**: Real-time frequency analysis
- **Configurable Targets**: Customizable pitch and resonance ranges
- **Overlay GUI**: Draggable, always-on-top interface
- **Hotkey Support**: Toggle visibility with Ctrl+Shift+V

## Installation

### Prerequisites

- Python 3.8 or higher
- A working microphone
- Windows, macOS, or Linux

### Setup

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Optional Dependencies

For advanced phoneme analysis, you may need additional tools:
- **Montreal Forced Alignment (MFA)**: For detailed phoneme timing
- **Praat**: For formant analysis
- **CMU Pronouncing Dictionary**: For phoneme expectations

## Configuration

The application uses two configuration files:

### config.json
Main application settings including audio parameters, target ranges, and GUI settings.

### settings.json
User preferences including development mode, logging, and file paths.

## Usage

1. **Start the Application**: Run `python main.py`
2. **Adjust Microphone Sensitivity**: Use the volume slider to set the detection threshold
3. **Monitor Your Voice**: Speak and watch the real-time feedback
4. **Toggle Visibility**: Press Ctrl+Shift+V to hide/show the overlay
5. **View Spectrograms**: Check the "Show Spectrogram" option for frequency analysis

### Understanding the Metrics

- **Pitch**: Fundamental frequency in Hz (target: 165-255 Hz for feminine voice)
- **Resonance**: Spectral centroid indicating vocal tract resonance
- **Intonation**: Pitch variation indicating natural speech patterns
- **Phoneme Plot**: Scatter plot showing individual sound characteristics

## Calibration

Use the calibration module to practice with example audio:

```bash
python calibration.py
```

## Development

### Project Structure

- `main.py`: Application entry point
- `overlay_gui.py`: Main GUI interface
- `live_analysis_system.py`: Real-time audio processing
- `config_manager.py`: Configuration management
- `pitch_analysis.py`: Pitch tracking algorithms
- `resonance_analysis.py`: Spectral analysis
- `intonation_analysis.py`: Pitch variation analysis
- `library/`: Core processing modules

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **No audio input**: Check microphone permissions and default audio device
2. **High CPU usage**: Reduce buffer size or update interval in config.json
3. **Whisper errors**: Ensure torch and torchaudio are properly installed
4. **GUI not responding**: Check PyQt5 installation and display settings

### Debug Mode

Enable debug mode in settings.json:
```json
{
  "dev": true
}
```

This will show additional logging information and error details.

## License

See LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for speech recognition
- librosa for audio analysis
- PyQt5 for the GUI framework
- Montreal Forced Alignment project for phoneme timing