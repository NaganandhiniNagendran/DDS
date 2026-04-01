# Driver Drowsiness Detection System

A comprehensive full-stack web application that uses computer vision to detect driver fatigue and prevent accidents caused by drowsy driving.

## Features

- **Real-time Detection**: Uses webcam to monitor eye closure and yawning patterns
- **Alert System**: Visual and audio alerts when drowsiness is detected
- **Modern Dashboard**: Clean, responsive UI with dark theme
- **Session Tracking**: Monitor driving sessions with detailed metrics
- **History Management**: View and export historical session data

## Technology Stack

### Backend
- **Flask**: Python web framework
- **OpenCV**: Computer vision library for video processing
- **Dlib**: Facial landmark detection
- **NumPy**: Numerical computations
- **Scipy**: Scientific computing

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with dark theme
- **JavaScript**: Interactive functionality
- **Font Awesome**: Icon library

## Installation

### Prerequisites
- Python 3.8 or higher
- Webcam access
- Modern web browser

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd driver-drowsiness-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Dlib Facial Landmark Model**
   
   Download the 68-point facial landmark predictor model:
   ```bash
   # Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   # Extract and place in the project root directory
   ```

5. **Add Alarm Sound**
   
   Place an alarm sound file named `alarm.wav` in the `static/` directory. You can download free alarm sounds from:
   - https://www.soundjay.com/beep-sounds-1.html
   - https://www.zapsplat.com/sound-effect-category/alarm-sounds/

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   
   Open your web browser and navigate to: `http://localhost:5000`

## Usage

### Starting Detection
1. Navigate to the **Detection** page
2. Click **"Start Detection"** to begin monitoring
3. Allow webcam access when prompted
4. The system will monitor your eye state and alert you if drowsiness is detected

### Viewing Dashboard
- Visit the **Dashboard** page to see:
  - Total driving time
  - Number of alerts
  - Fatigue level indicators
  - Safety score

### Managing History
- Access the **History** page to:
  - View past driving sessions
  - Filter sessions by date and alert count
  - Export session data as CSV

## Algorithm Details

### Eye Aspect Ratio (EAR)
The system uses the Eye Aspect Ratio algorithm to detect eye closure:

```
EAR = (|p2-p6| + |p3-p5|) / (2|p1-p4|)
```

Where p1-p6 are the six eye landmarks.

### Detection Logic
1. **Face Detection**: Uses Dlib's face detector
2. **Landmark Detection**: Identifies 68 facial landmarks
3. **EAR Calculation**: Computes eye aspect ratio for both eyes
4. **Threshold Analysis**: Triggers alert if EAR < 0.25 for 20 consecutive frames

## Project Structure

```
driver-drowsiness-system/
│
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   ├── js/
│   │   └── main.js           # JavaScript functionality
│   ├── images/               # Image assets
│   └── alarm.wav            # Alarm sound file
│
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   ├── detection.html       # Live detection page
│   ├── dashboard.html       # Dashboard page
│   └── history.html         # History page
│
├── app.py                   # Flask application
├── drowsiness_detection.py  # Detection algorithm
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Detection Parameters
You can adjust detection sensitivity in `drowsiness_detection.py`:

```python
# Eye aspect ratio threshold
self.EAR_THRESHOLD = 0.25

# Consecutive frames for alert
self.EAR_CONSEC_FRAMES = 20
```

### Customization
- **Theme**: Modify CSS variables in `static/css/style.css`
- **Alert Sound**: Replace `static/alarm.wav` with custom sound
- **Detection Sensitivity**: Adjust EAR threshold values

## Troubleshooting

### Common Issues

1. **Webcam not detected**
   - Ensure webcam is connected and not used by other applications
   - Check browser permissions for camera access

2. **Dlib model not found**
   - Download `shape_predictor_68_face_landmarks.dat` and place in project root
   - Ensure the file path is correct in `drowsiness_detection.py`

3. **Audio alerts not working**
   - Check browser audio permissions
   - Ensure `alarm.wav` file exists in static directory

4. **Application won't start**
   - Verify all dependencies are installed
   - Check Python version compatibility
   - Ensure virtual environment is activated

### Performance Optimization
- Use good lighting conditions for better detection accuracy
- Maintain appropriate distance from webcam (2-3 feet recommended)
- Ensure stable internet connection for web application performance

## Browser Compatibility

This application works best with modern browsers:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Security Considerations

- Webcam access is required only during detection sessions
- No data is stored on external servers
- All processing happens locally on your machine
- Session data is stored in local memory only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dlib library for facial landmark detection
- OpenCV for computer vision operations
- Font Awesome for icons
- Flask web framework

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information

---

**⚠️ Disclaimer**: This system is designed as a safety aid and should not replace responsible driving practices. Always drive safely and take regular breaks when needed.
