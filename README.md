# 🎬 Advanced Location Tracker with YouTube Integration

This is an advanced web application that requests location and camera permissions before playing a YouTube video.

## Features

✨ **Key Features:**
- 📍 Location tracking with GPS coordinates
- 📷 Camera access and photo capture
- 🎥 YouTube video integration
- 💾 Data storage (location, timestamp, photos)
- 🌐 Public URL sharing via ngrok
- 📱 Mobile-friendly responsive design
- 🎨 Modern UI with animations

## How It Works

1. User opens the shared link
2. App requests location permission
3. App requests camera permission
4. Takes a photo automatically
5. Sends all data to server
6. Plays YouTube video after permissions granted

## Installation

1. Install Python packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app_advanced.py
```

3. Share the ngrok URL with anyone

## Configuration

To change the YouTube video, edit line 40 in `app_advanced.py`:
```python
youtube_video_id = "YOUR_VIDEO_ID"  # Change this
```

## Data Storage

- Photos: `photos/` folder
- User data: `data/user_data.json`
- View all data: Visit `/data` endpoint

## Security Note

⚠️ This app collects sensitive information (location, photos). Use responsibly and ensure users are aware of data collection.

## Requirements

- Python 3.7+
- Flask
- pyngrok
- Internet connection (for ngrok)

## License

Use at your own risk. For educational purposes only.
