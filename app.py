from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from tensorflow.keras.models import model_from_json
import base64
import io
from PIL import Image

app = Flask(__name__)

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

def process_frame(frame_data):
    """Process a frame and detect emotions"""
    # Decode base64 image
    image_data = base64.b64decode(frame_data.split(',')[1])
    image = Image.open(io.BytesIO(image_data))
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame_route():
    from flask import request
    frame_data = request.json['frame']
    results = process_frame(frame_data)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)