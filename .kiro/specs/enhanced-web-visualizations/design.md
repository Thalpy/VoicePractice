# Design Document

## Overview

This design document outlines the architecture for enhancing the Voice Practice web application with comprehensive visualizations matching the desktop version. The enhancement adds four new visualization components (resonance, intonation, spectrogram, phoneme scatter plot) while maintaining the existing pitch and volume charts. The design emphasizes performance, responsiveness, and user experience through collapsible interfaces and browser-optimized audio processing.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   UI Layer      │  │  Audio Engine   │  │ Chart Layer │ │
│  │                 │  │                 │  │             │ │
│  │ - Collapsible   │  │ - Web Audio API │  │ - Chart.js  │ │
│  │   Panels        │  │ - FFT Analysis  │  │ - Canvas 2D │ │
│  │ - Settings      │  │ - Pitch Detect  │  │ - WebGL     │ │
│  │ - Controls      │  │ - Spectral Calc │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Flask Backend                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   API Layer     │  │  Data Storage   │  │ Config Mgmt │ │
│  │                 │  │                 │  │             │ │
│  │ - Voice Data    │  │ - Session Data  │  │ - Settings  │ │
│  │ - Statistics    │  │ - Metrics       │  │ - Targets   │ │
│  │ - Configuration │  │ - History       │  │ - Defaults  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Audio Processing Pipeline

```
Audio Input → Web Audio API → Analysis Engine → Visualization Updates
     │              │              │                    │
     │              │              ├─ Pitch Detection   ├─ Pitch Chart
     │              │              ├─ Volume Analysis   ├─ Volume Chart  
     │              │              ├─ Spectral Centroid ├─ Resonance Chart
     │              │              ├─ Pitch Std Dev     ├─ Intonation Chart
     │              │              ├─ FFT Analysis      ├─ Spectrogram
     │              │              └─ Speech Recognition└─ Phoneme Plot
     │              │
     │              └─ Real-time Processing (100ms intervals)
     │
     └─ MediaStream API (microphone access)
```

## Components and Interfaces

### 1. Enhanced Audio Analysis Engine

**Purpose:** Extends the current basic audio processing to include all desktop-version metrics.

**Key Methods:**
```javascript
class AudioAnalysisEngine {
    // Existing methods
    calculatePitch(audioData)
    calculateVolume(audioData)
    
    // New methods
    calculateSpectralCentroid(audioData)     // For resonance
    calculatePitchStandardDeviation(pitchHistory)  // For intonation
    performFFTAnalysis(audioData)            // For spectrogram
    detectPhonemes(audioData)                // For phoneme plot (basic)
}
```

**Interface:**
```javascript
{
    pitch: number,           // Hz
    volume: number,          // 0.0-1.0
    resonance: number,       // Hz (spectral centroid)
    intonation: number,      // Hz (pitch std dev)
    spectrum: Float32Array,  // FFT data for spectrogram
    phonemes: Array<{        // Basic phoneme detection
        phoneme: string,
        pitch: number,
        resonance: number,
        timestamp: number
    }>
}
```

### 2. Collapsible Visualization Framework

**Purpose:** Provides a unified system for managing collapsible chart sections with performance optimization.

**Structure:**
```html
<div class="visualization-panel" data-chart="resonance">
    <div class="panel-header" onclick="togglePanel('resonance')">
        <h3>🎵 Resonance Analysis</h3>
        <span class="collapse-icon">▼</span>
        <span class="status-indicator">●</span>
    </div>
    <div class="panel-content" id="resonance-content">
        <canvas id="resonanceChart"></canvas>
        <div class="chart-controls">
            <!-- Chart-specific controls -->
        </div>
    </div>
</div>
```

**JavaScript Interface:**
```javascript
class VisualizationManager {
    togglePanel(chartId)
    isCollapsed(chartId)
    updateChart(chartId, data)
    pauseChart(chartId)      // Stop processing when collapsed
    resumeChart(chartId)     // Resume processing when expanded
    saveState()              // Persist collapse states
    loadState()              // Restore collapse states
}
```

### 3. Resonance Chart Component

**Purpose:** Displays spectral centroid over time with target range indicators.

**Implementation:**
- Chart.js line chart with time-series data
- Target range: 2500-3500 Hz highlighted area
- Color coding: green (in target), yellow (close), red (off target)
- Real-time updates every 100ms

**Data Processing:**
```javascript
function calculateSpectralCentroid(fftData, sampleRate) {
    let numerator = 0;
    let denominator = 0;
    
    for (let i = 0; i < fftData.length; i++) {
        const frequency = (i * sampleRate) / (2 * fftData.length);
        const magnitude = fftData[i];
        numerator += frequency * magnitude;
        denominator += magnitude;
    }
    
    return denominator > 0 ? numerator / denominator : 0;
}
```

### 4. Intonation Chart Component

**Purpose:** Shows pitch variation (standard deviation) over time to indicate speech naturalness.

**Implementation:**
- Rolling window calculation of pitch standard deviation
- Target range: 15-25 Hz std dev
- Smoothed line chart with trend indicators
- Window size: 5 seconds of pitch data

**Data Processing:**
```javascript
function calculateIntonation(pitchHistory, windowSize = 50) {
    if (pitchHistory.length < windowSize) return 0;
    
    const recentPitches = pitchHistory.slice(-windowSize);
    const validPitches = recentPitches.filter(p => p > 0);
    
    if (validPitches.length < 10) return 0;
    
    const mean = validPitches.reduce((a, b) => a + b) / validPitches.length;
    const variance = validPitches.reduce((sum, pitch) => 
        sum + Math.pow(pitch - mean, 2), 0) / validPitches.length;
    
    return Math.sqrt(variance);
}
```

### 5. Real-time Spectrogram Component

**Purpose:** Displays frequency content over time as a scrolling heatmap.

**Implementation:**
- HTML5 Canvas with ImageData manipulation
- FFT size: 2048 samples for good frequency resolution
- Update rate: 30 FPS for smooth scrolling
- Color mapping: Viridis or Inferno colormap
- Frequency range: 0-8000 Hz (focus on voice range)

**Canvas Implementation:**
```javascript
class SpectrogramCanvas {
    constructor(canvasId, width = 800, height = 400) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = width;
        this.height = height;
        this.imageData = this.ctx.createImageData(width, height);
        this.scrollBuffer = new Float32Array(width * height);
    }
    
    updateSpectrogram(fftData) {
        // Scroll existing data left
        this.scrollLeft();
        
        // Add new column from FFT data
        this.addColumn(fftData);
        
        // Convert to RGB and draw
        this.updateCanvas();
    }
}
```

### 6. Phoneme Scatter Plot Component

**Purpose:** Shows individual phonemes plotted by pitch vs resonance with clustering analysis.

**Implementation:**
- Chart.js scatter plot with custom point styling
- Basic phoneme detection using formant analysis
- Clustering visualization with average markers
- Interactive tooltips showing phoneme details

**Simplified Phoneme Detection:**
```javascript
function detectBasicPhonemes(audioData, pitch, resonance) {
    // Simplified phoneme classification based on pitch/resonance
    // This is a basic implementation - full phoneme detection requires ML
    
    const phonemeMap = {
        high_front: { pitch: '>200', resonance: '>3000', label: 'i/e' },
        high_back: { pitch: '>200', resonance: '<2500', label: 'u/o' },
        low: { pitch: '<150', resonance: '2000-3000', label: 'a' },
        consonant: { pitch: '<100', resonance: 'variable', label: 'C' }
    };
    
    // Basic classification logic
    if (pitch > 200 && resonance > 3000) return 'i/e';
    if (pitch > 200 && resonance < 2500) return 'u/o';
    if (pitch < 150) return 'a';
    return 'C';
}
```

## Data Models

### Audio Analysis Data Model
```javascript
interface AudioAnalysisData {
    timestamp: number;
    pitch: number;           // Hz, 0 if unvoiced
    volume: number;          // 0.0-1.0
    resonance: number;       // Hz, spectral centroid
    intonation: number;      // Hz, pitch standard deviation
    spectrum: Float32Array;  // FFT magnitudes
    isVoiced: boolean;       // Voice activity detection
}
```

### Phoneme Data Model
```javascript
interface PhonemeData {
    phoneme: string;         // Detected phoneme symbol
    pitch: number;           // Hz
    resonance: number;       // Hz
    timestamp: number;       // ms
    confidence: number;      // 0.0-1.0
    duration: number;        // ms
}
```

### Visualization State Model
```javascript
interface VisualizationState {
    panels: {
        [chartId: string]: {
            collapsed: boolean;
            enabled: boolean;
            lastUpdate: number;
        }
    };
    settings: {
        updateRate: number;      // ms
        maxHistory: number;      // data points
        targetRanges: {
            pitch: [number, number];
            resonance: [number, number];
            intonation: [number, number];
        };
    };
}
```

## Error Handling

### Browser Compatibility
- **Web Audio API**: Fallback to basic audio processing if unavailable
- **Canvas Support**: Graceful degradation for spectrogram on older browsers
- **Performance Issues**: Automatic quality reduction on resource-constrained devices

### Audio Processing Errors
- **Microphone Access**: Clear error messages and retry mechanisms
- **FFT Failures**: Fallback to simpler analysis methods
- **Invalid Audio Data**: Robust validation and error recovery

### Chart Rendering Errors
- **Canvas Errors**: Fallback to simpler visualization methods
- **Chart.js Issues**: Error boundaries around chart components
- **Memory Issues**: Automatic data cleanup and garbage collection

## Testing Strategy

### Unit Testing
- **Audio Analysis Functions**: Test pitch detection, spectral centroid calculation, FFT processing
- **Data Processing**: Test rolling statistics, phoneme classification, data validation
- **Utility Functions**: Test mathematical operations, data transformations

### Integration Testing
- **Audio Pipeline**: End-to-end testing of microphone → analysis → visualization
- **Chart Updates**: Test real-time data flow to all visualization components
- **State Management**: Test collapse/expand functionality and persistence

### Performance Testing
- **Real-time Processing**: Ensure consistent frame rates under various loads
- **Memory Usage**: Test for memory leaks during extended sessions
- **Browser Compatibility**: Test across Chrome, Firefox, Safari, Edge

### User Experience Testing
- **Responsive Design**: Test on various screen sizes and orientations
- **Accessibility**: Test keyboard navigation and screen reader compatibility
- **Usability**: Test collapsible interface and settings management

## Performance Considerations

### Optimization Strategies
1. **Selective Processing**: Only process data for expanded/visible charts
2. **Efficient FFT**: Use optimized FFT libraries (e.g., FFT.js)
3. **Canvas Optimization**: Use requestAnimationFrame for smooth animations
4. **Data Throttling**: Limit update rates based on device capabilities
5. **Memory Management**: Implement circular buffers for historical data

### Resource Management
- **CPU Usage**: Monitor processing load and adjust quality automatically
- **Memory Usage**: Implement data cleanup and garbage collection
- **Battery Life**: Reduce processing on mobile devices when appropriate

### Scalability
- **Multiple Charts**: Efficient rendering when all visualizations are active
- **Extended Sessions**: Maintain performance during long training sessions
- **Device Adaptation**: Automatic quality adjustment based on device capabilities