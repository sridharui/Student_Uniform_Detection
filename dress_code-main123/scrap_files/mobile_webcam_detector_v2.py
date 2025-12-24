"""
Mobile Webcam Uniform Detection
Real-time uniform detection from mobile phone camera (via network)
"""
import cv2
import numpy as np
from ultralytics import YOLO
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import base64
import io
from PIL import Image
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'mobile_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model
MODEL_PATH = "runs/train/uniform_detector_yolov12_cpu/weights/best.pt"
FALLBACK_MODEL_PATH = "runs/train/uniform_detector_yolov12/weights/best.pt"
model = None

if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print(f"✅ Model loaded: {MODEL_PATH}")
elif os.path.exists(FALLBACK_MODEL_PATH):
    model = YOLO(FALLBACK_MODEL_PATH)
    print(f"✅ Fallback model loaded: {FALLBACK_MODEL_PATH}")
else:
    print(f"⚠️  Model not found at {MODEL_PATH} or fallback path")


class MobileUniformDetector:
    """Mobile uniform detector"""
    
    def __init__(self, model):
        self.model = model
        
        self.REQUIRED_BOYS = {
            'Identity Card', 'Shirt', 'pant', 'shoes'
        }
        
        self.REQUIRED_GIRLS = {
            'Identity Card', 'top', 'pant', 'shoes'
        }
    
    def detect(self, image_bytes):
        """Detect uniform from image bytes"""
        if self.model is None:
            return {
                'status': 'error',
                'message': 'Model not loaded',
                'uniform_status': -1
            }
        
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Run inference
            results = self.model(image, conf=0.5, verbose=False)
            
            # Extract detections
            detected = set()
            
            if results and len(results) > 0:
                result = results[0]
                if result.boxes is not None:
                    for cls_id in result.boxes.cls:
                        class_name = result.names[int(cls_id)]
                        detected.add(class_name)
            
            # Normalize and check
            normalized = self._normalize(detected)
            boys_ok = self.REQUIRED_BOYS.issubset(normalized)
            girls_ok = self.REQUIRED_GIRLS.issubset(normalized)
            
            if boys_ok or girls_ok:
                uniform_status = 1
                message = "✅ COMPLETE UNIFORM"
                uniform_type = "BOYS" if boys_ok else "GIRLS"
            else:
                uniform_status = 0
                message = "❌ INCOMPLETE UNIFORM"
                uniform_type = "INCOMPLETE"
            
            return {
                'status': 'success',
                'uniform_status': uniform_status,
                'message': message,
                'uniform_type': uniform_type,
                'detected_items': list(detected),
                'normalized_items': list(normalized)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'uniform_status': -1
            }
    
    def _normalize(self, detections):
        """Normalize class names"""
        normalized = set()
        for cls in detections:
            cls_lower = cls.lower()
            if 'identity' in cls_lower or 'card' in cls_lower or 'id' in cls_lower:
                normalized.add('Identity Card')
            elif cls_lower == 'shirt':
                normalized.add('Shirt')
            elif cls_lower == 'top':
                normalized.add('top')
            elif cls_lower == 'pant':
                normalized.add('pant')
            elif cls_lower == 'shoes':
                normalized.add('shoes')
        return normalized


detector = MobileUniformDetector(model)


@app.route('/')
def index():
    """Mobile interface"""
    return render_template('mobile_uniform_detector.html')


@app.route('/api/detect', methods=['POST'])
def api_detect():
    """API endpoint for uniform detection"""
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        image_bytes = file.read()
        result = detector.detect(image_bytes)
        
        # Save uploaded image
        if result['status'] == 'success':
            filename = secure_filename(f"mobile_{len(os.listdir(app.config['UPLOAD_FOLDER']))}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e), 'uniform_status': -1}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok' if model else 'model_not_loaded',
        'model': MODEL_PATH
    })


def main():
    """Run mobile server"""
    print("=" * 80)
    print("MOBILE UNIFORM DETECTION SERVER")
    print("=" * 80)
    print(f"Model: {MODEL_PATH}")
    print(f"Server: http://localhost:5000")
    print(f"API: http://localhost:5000/api/detect")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()
