from flask import Flask, render_template, Response, jsonify, request, send_file
import cv2
import numpy as np
from tensorflow.keras.models import model_from_json
import base64
import io
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

# Load the emotion detection model
json_file = open('models/emotion_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
emotion_model = model_from_json(loaded_model_json)
emotion_model.load_weights("models/emotion_model.weights.h5")

# Load face detection cascade
face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

# Emotion dictionary
emotion_dict = {
    0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy",
    4: "Neutral", 5: "Sad", 6: "Surprised"
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_frame(frame_data):
    """Process a frame and detect emotions"""
    # Decode base64 image
    image_data = base64.b64decode(frame_data.split(',')[1])
    image = Image.open(io.BytesIO(image_data))
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    return process_image(frame)

def process_image(frame):
    """Process image and detect emotions"""
    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
    
    results = []
    for (x, y, w, h) in faces:
        # Extract and preprocess face region
        roi_gray = gray_frame[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
        
        # Predict emotion
        prediction = emotion_model.predict(cropped_img)
        emotion_index = int(np.argmax(prediction))
        emotion_label = emotion_dict[emotion_index]
        confidence = float(prediction[0][emotion_index])
        
        results.append({
            'bbox': [int(x), int(y), int(w), int(h)],
            'emotion': emotion_label,
            'confidence': confidence
        })
    
    return results

def process_video(video_path):
    """Process video file and return processed video path"""
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create output video file
    output_path = video_path.rsplit('.', 1)[0] + '_processed.' + video_path.rsplit('.', 1)[1]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        results = process_image(frame)
        
        # Draw results on frame
        for result in results:
            x, y, w, h = result['bbox']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 
                       f"{result['emotion']} ({result['confidence']:.1%})", 
                       (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.9, 
                       (0, 255, 0), 
                       2)
        
        # Write frame to output video
        out.write(frame)
    
    # Release everything
    cap.release()
    out.release()
    
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame_route():
    frame_data = request.json['frame']
    results = process_frame(frame_data)
    return jsonify(results)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process video
        try:
            processed_path = process_video(filepath)
            processed_filename = os.path.basename(processed_path)
            return jsonify({
                'message': 'Video processed successfully',
                'processed_video': processed_filename
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/video/<filename>')
def processed_video(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)