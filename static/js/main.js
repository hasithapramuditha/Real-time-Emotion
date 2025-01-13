let video;
let canvas;
let context;
let streaming = false;
const FPS = 3;

// Initialize the camera stream
async function startVideo() {
  video = document.getElementById("video");
  canvas = document.getElementById("canvas");
  context = canvas.getContext("2d");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.play();
    streaming = true;
    document.getElementById("startButton").disabled = true;
    document.getElementById("stopButton").disabled = false;
    processVideo();
  } catch (err) {
    console.error("Error accessing webcam:", err);
    document.getElementById("status").textContent =
      "Error accessing webcam. Please make sure you have a webcam connected and have granted permission to use it.";
  }
}

// Stop the video stream
function stopVideo() {
  streaming = false;
  const stream = video.srcObject;
  const tracks = stream.getTracks();
  tracks.forEach((track) => track.stop());
  document.getElementById("startButton").disabled = false;
  document.getElementById("stopButton").disabled = true;
  context.clearRect(0, 0, canvas.width, canvas.height);
}

// Process video frames
async function processVideo() {
  if (!streaming) return;

  // Draw current video frame to canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  try {
    // Convert canvas to base64
    const frame = canvas.toDataURL("image/jpeg");

    // Send frame to backend
    const response = await fetch("/process_frame", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ frame: frame }),
    });

    const results = await response.json();

    // Clear previous drawings
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Draw detection results
    results.forEach((result) => {
      const [x, y, w, h] = result.bbox;

      // Draw rectangle around face
      context.strokeStyle = "#00ff00";
      context.lineWidth = 2;
      context.strokeRect(x, y, w, h);

      // Draw emotion label
      context.fillStyle = "#00ff00";
      context.font = "16px Arial";
      context.fillText(
        `${result.emotion} (${(result.confidence * 100).toFixed(1)}%)`,
        x,
        y - 5
      );
    });
  } catch (error) {
    console.error("Error processing frame:", error);
  }

  // Schedule next frame processing
  setTimeout(() => {
    if (streaming) {
      processVideo();
    }
  }, 1000 / FPS);
}

// Handle video file upload
document
  .getElementById("videoUploadForm")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData();
    const fileField = document.getElementById("videoFile");

    if (fileField.files.length === 0) {
      alert("Please select a video file first");
      return;
    }

    formData.append("video", fileField.files[0]);

    const uploadStatus = document.getElementById("uploadStatus");
    uploadStatus.textContent = "Uploading and processing video...";

    try {
      const response = await fetch("/upload_video", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        uploadStatus.textContent = "Video processed successfully!";

        // Show processed video
        const videoResult = document.querySelector(".video-result");
        videoResult.style.display = "block";

        const processedVideo = document.getElementById("processedVideo");
        processedVideo.src = `/video/${result.processed_video}`;
        processedVideo.load();
      } else {
        uploadStatus.textContent = `Error: ${result.error}`;
      }
    } catch (error) {
      uploadStatus.textContent = `Error: ${error.message}`;
    }
  });

// Set up event listeners
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("startButton").addEventListener("click", startVideo);
  document.getElementById("stopButton").addEventListener("click", stopVideo);
});
