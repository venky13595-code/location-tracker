# 📍 Advanced Location Tracker

A Flask-based web application that tracks user location and collects device information through an interactive YouTube video interface.

## 🚀 Features

- **GPS Location Tracking**: Requests accurate GPS coordinates (accurate to meters)
- **8-Hour Live Tracking**: Continuous location updates every 2 minutes
- **50+ Device Data Points**: Collects comprehensive device information
- **IP-Based Fallback**: Uses IP geolocation if GPS is denied
- **Camera Capture**: Optional photo capture
- **Network Information**: ISP, ASN, connection type, speed
- **Battery Status**: Level, charging state, time remaining
- **Device Details**: OS, browser, screen, GPU, CPU, RAM

## 📋 Requirements

- Python 3.x
- Flask 3.0.0
- pyngrok 7.0.5

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/location-tracker.git
cd location-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app_clean.py
```

## 🌐 Deployment Options

### Local with Ngrok (Quick Start)
```bash
python app_clean.py
```
The public URL will be displayed in the console.

### Production Deployment

#### Option 1: Render.com
1. Use `app_render.py` for deployment
2. Deploy via Render dashboard
3. Set environment variables if needed

#### Option 2: PythonAnywhere / Railway / Heroku
- Use appropriate configuration files
- Update requirements.txt for production server

## 📊 Data Collection

The application collects:

- **Location Data**: GPS coordinates or IP-based location
- **Device Information**: 
  - OS and version
  - Browser and version
  - Screen resolution
  - GPU information
  - CPU cores
  - Device memory
- **Network Data**:
  - Public IP address
  - ISP name and ASN
  - Connection type (WiFi/4G/5G)
  - Network speed and latency
- **Battery Information**:
  - Battery level
  - Charging status
  - Time estimates
- **Additional Data**:
  - Timezone
  - Language preferences
  - Referrer information

## 🔐 Privacy & Security

⚠️ **Important**: This application collects sensitive user data. Please ensure:

1. You have proper consent from users
2. Data is stored securely
3. Comply with GDPR, CCPA, and other privacy laws
4. Use HTTPS in production
5. Implement proper data retention policies

## 📝 API Endpoints

- `GET /` - Main application interface
- `POST /upload` - Receives initial location and photo data
- `POST /live_location` - Receives continuous location updates
- `GET /data` - View all collected data (JSON format)

## 🛠️ Configuration

Edit these variables in the Python files:

- `youtube_video_id` - YouTube video to display
- `TRACKING_DURATION` - Duration of live tracking (default: 8 hours)
- `UPDATE_INTERVAL` - Location update frequency (default: 2 minutes)

## ⚙️ Files

- `app_clean.py` - Main application with all features
- `app_local.py` - Local network version (no ngrok)
- `app_render.py` - Production deployment version
- `requirements.txt` - Python dependencies

## 📱 Usage

1. Share the public URL with users
2. Users click the video thumbnail
3. Browser requests location permission
4. Application collects data and plays video
5. View collected data at `/data` endpoint

## ⚠️ Legal Disclaimer

This tool is for educational purposes only. Ensure you:
- Obtain explicit user consent
- Comply with local privacy laws
- Use responsibly and ethically
- Do not use for unauthorized tracking

## 📜 License

MIT License - Use at your own risk

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 👤 Author

Your Name - Your GitHub Profile

---

**Note**: This application requires user permission for GPS and camera access. Browser security policies enforce these requirements and cannot be bypassed.
