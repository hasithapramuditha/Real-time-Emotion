let video;
let canvas;
let context;
let streaming = false;
const FPS = 3;  // Frames per second for processing

// Initialize the camera stream
async function startVideo() {
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    context = canvas.getContext('2d');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.play();
        streaming = true;
        document.getElementById('startButton').disabled = true;
        document.getElementById('stopButton').disabled = false;
        processVideo();
    } catch (err) {
        console.error("Error accessing webcam:", err);
        document.getElementById('status').textContent = "Error accessing webcam. Please make sure you have a webcam connected and have granted permission to use it.";
    }
}

// Stop the video stream
function stopVideo() {
    streaming = false;
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach(track => track.stop());
    document.getElementById('startButton').disabled = false;
    document.getElementById('stopButton').disabled = true;
    context.clearRect(0, 0, canvas.width, canvas.height);
}

// Process video frames
async function processVideo() {
    if (!streaming) return;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    try {
        // Convert canvas to base64
        const frame = canvas.toDataURL('image/jpeg');
        
        // Send frame to backend
        const response = await fetch('/process_frame', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ frame: frame })
        });
        
        const results = await response.json();
        
        // Clear previous drawings
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Draw detection results
        results.forEach(result => {
            const [x, y, w, h] = result.bbox;
            
            // Draw rectangle around face
            context.strokeStyle = '#00ff00';
            context.lineWidth = 2;
            context.strokeRect(x, y, w, h);
            
            // Draw emotion label
            context.fillStyle = '#00ff00';
            context.font = '16px Arial';
            context.fillText(
                `${result.emotion} (${(result.confidence * 100).toFixed(1)}%)`,
                x, y - 5
            );
        });
        
    } catch (error) {
        console.error('Error processing frame:', error);
    }
    
    // Schedule next frame processing
    setTimeout(() => {
        if (streaming) {
            processVideo();
        }
    }, 1000 / FPS);
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startButton').addEventListener('click', startVideo);
    document.getElementById('stopButton').addEventListener('click', stopVideo);
});