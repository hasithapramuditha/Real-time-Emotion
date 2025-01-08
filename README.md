# Real-time Emotion Detection Web Application

A Flask-based web application that performs real-time emotion detection using your webcam. The application uses a CNN model trained on the FER2013 dataset to detect faces and classify emotions in real-time.

## Features

- Real-time webcam feed processing
- Face detection using OpenCV
- Emotion classification with confidence scores
- Seven emotion categories: Angry, Disgusted, Fearful, Happy, Neutral, Sad, Surprised
- Interactive web interface with start/stop controls
- Visual feedback with bounding boxes and emotion labels

## Model Architecture

The emotion detection model uses a Convolutional Neural Network (CNN) with the following architecture:
- Input layer: 48x48x1 (grayscale images)
- Multiple convolutional layers with ReLU activation
- MaxPooling layers for spatial dimension reduction
- Dropout layers for regularization
- Dense layers for final classification
- Output: 7 classes (emotions)

Training specifications:
- Learning rate: 0.0001
- Optimizer: Adam
- Loss function: Categorical crossentropy
- Batch size: 64
- Epochs: 50

## Dataset

The model is trained on the FER2013 dataset which contains:
- 28,709 training images
- 7,178 test images
- 48x48 pixel grayscale images
- 7 emotion categories

## Prerequisites

- Python 3.7 or higher
- Webcam
- Modern web browser with JavaScript enabled
- GPU (recommended for training)

## Required Files

Before running the application, ensure you have the following files:
- `models/emotion_model.json` - Model architecture file
- `models/emotion_model.weights.h5` - Model weights file
- `models/haarcascade_frontalface_default.xml` - OpenCV face detection cascade

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hasithapramuditha/Real-time-Emotion.git
cd emotion-detection-app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
emotion-detection-app/
├── static/
│   ├── js/
│   │   └── main.js
│   └── css/
│       └── style.css
├── templates/
│   └── index.html
├── models/
│   ├── emotion_model.json
│   ├── emotion_model.weights.h5
│   └── haarcascade_frontalface_default.xml
├── train/
│   └── TrainEmotionDetection.ipynb
├── app.py
└── requirements.txt
```

## Training the Model

1. The model can be trained using the provided Jupyter notebook in `train/TrainEmotionDetection.ipynb`
2. Required libraries for training:
   ```
   tensorflow
   opencv-python
   numpy
   pandas
   kagglehub
   ```
3. The notebook includes:
   - Dataset download and preparation
   - Model architecture definition
   - Training configuration
   - Model training and saving

Training the model requires:
- GPU for reasonable training time
- Around 8GB RAM
- Storage space for dataset (~60MB)

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Click the "Start Detection" button to begin emotion detection
4. Grant permission to access your webcam when prompted
5. Click "Stop Detection" to end the session

## Performance Notes

- The application processes frames at 3 FPS by default (configurable in `static/js/main.js`)
- Performance may vary depending on your hardware and browser
- Chrome or Firefox browsers are recommended for best performance
- Model achieves approximately 60-70% accuracy on the validation set

## Troubleshooting

1. If the webcam doesn't start:
   - Ensure your browser has permission to access the webcam
   - Check if another application is using the webcam
   - Verify your webcam is properly connected and functioning

2. If emotions aren't being detected:
   - Ensure proper lighting conditions
   - Position your face clearly in the frame
   - Verify all model files are present in the `models/` directory

3. If the application fails to start:
   - Check if all dependencies are installed correctly
   - Verify Python version compatibility
   - Ensure all required files are in their correct locations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- FER2013 dataset for emotion detection
- OpenCV for face detection
- TensorFlow for the deep learning framework
- Flask for the web framework

## Contact

For questions and support, please open an issue in the GitHub repository.