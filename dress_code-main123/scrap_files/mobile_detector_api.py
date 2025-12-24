# mobile_detector_api.py
# Mobile-compatible REST API for uniform detection
# Supports both image upload and real-time video streaming

from flask import Flask, request, jsonify, send_file
import cv2
import numpy as np
import os
import joblib
from ultralytics import YOLO
from sklearn.cluster import KMeans
import io
import base64
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# CONFIG
MODEL_PATH = "runs/train/uniform_color_trained2/weights/best.pt"
FALLBACK_MODEL_PATH = "runs/train/uniform_color_trained/weights/best.pt"
COLOR_CLF_PATH = "color_clf.joblib"
USE_COLOR_CLASSIFIER = os.path.exists(COLOR_CLF_PATH)
CONF_THRESH = 0.10
MIN_AREA = 400
IMG_SIZE = 1280

# UNIFORM VALIDATION RULES
SHIRT_ALLOWED = {'gray', 'white'}
PANTS_ALLOWED = {'black', 'navy blue', 'blue', 'dark blue'}
SHOES_REQUIRED = True
ID_REQUIRED = True

# Load model
model = None
clf = None

def initialize_models():
    """Initialize AI models on startup"""
    global model, clf
    
    try:
        model_path = MODEL_PATH if os.path.exists(MODEL_PATH) else FALLBACK_MODEL_PATH
        model = YOLO(model_path)
        logger.info(f"✓ Model loaded: {model_path}")
    except Exception as e:
        logger.error(f"✗ Error loading model: {e}")
        return False
    
    if USE_COLOR_CLASSIFIER:
        try:
            clf = joblib.load(COLOR_CLF_PATH)
            logger.info("✓ Color classifier loaded")
        except Exception as e:
            logger.error(f"⚠ Could not load color classifier: {e}")
    
    return True

# Helper functions (from detect_and_classify_improved.py)
def crop_from_box(img, xyxy):
    x1, y1, x2, y2 = xyxy
    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
    h, w = img.shape[:2]
    x1, x2 = max(0, min(x1, w-1)), max(0, min(x2, w-1))
    y1, y2 = max(0, min(y1, h-1)), max(0, min(y2, h-1))
    return img[y1:y2, x1:x2]

def kmeans_dominant_rgb(img_bgr, k=3):
    pixels = img_bgr.reshape(-1, 3)
    if len(pixels) < 10:
        return np.array([0, 0, 0])
    pixels = pixels.astype(np.float32)
    km = KMeans(n_clusters=k, random_state=0, n_init=10).fit(pixels[:, ::-1])
    counts = np.bincount(km.labels_)
    dom = km.cluster_centers_[np.argmax(counts)]
    return dom

def hsv_gray_ratio(img_bgr, sat_thresh=60, v_min=30):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = (sat <= sat_thresh) & (val >= v_min)
    return float(np.sum(mask)) / mask.size

def rgb_to_color_name(rgb):
    r, g, b = map(int, rgb)
    if r < 60 and g < 60 and b < 60:
        return 'black'
    if abs(r-g) < 20 and abs(g-b) < 20 and r > 120:
        return 'white'
    if abs(r-g) < 30 and abs(g-b) < 30 and r < 160 and g < 160 and b < 160:
        return 'gray'
    if b > r and b > g:
        return 'blue'
    if r > g and r > b:
        return 'red'
    if g > r and g > b:
        return 'green'
    return 'unknown'

def classify_color(img_bgr):
    if clf is not None:
        dom_rgb = kmeans_dominant_rgb(img_bgr, k=3)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        h_mean, s_mean, v_mean = hsv[:, :, 0].mean(), hsv[:, :, 1].mean(), hsv[:, :, 2].mean()
        low_sat_ratio = float(np.mean(hsv[:, :, 1] < 60))
        feat = np.concatenate([dom_rgb, [h_mean, s_mean, v_mean, low_sat_ratio]])
        pred = clf.predict([feat])[0]
        return pred
    dom_rgb = kmeans_dominant_rgb(img_bgr, k=3)
    if hsv_gray_ratio(img_bgr, sat_thresh=60) > 0.4:
        return 'gray'
    return rgb_to_color_name(dom_rgb)

def detect_id_card_heuristic(img, shirt_box):
    """Fallback heuristic to detect ID card"""
    x1, y1, x2, y2 = shirt_box
    shirt_width = x2 - x1
    shirt_height = y2 - y1
    
    chest_x1 = x1 + int(shirt_width * 0.35)
    chest_x2 = x1 + int(shirt_width * 0.65)
    chest_y1 = y1 + int(shirt_height * 0.1)
    chest_y2 = y1 + int(shirt_height * 0.5)
    
    h, w = img.shape[:2]
    chest_x1 = max(0, min(chest_x1, w-1))
    chest_x2 = max(0, min(chest_x2, w-1))
    chest_y1 = max(0, min(chest_y1, h-1))
    chest_y2 = max(0, min(chest_y2, h-1))
    
    if chest_x2 <= chest_x1 or chest_y2 <= chest_y1:
        return False
    
    chest_crop = img[chest_y1:chest_y2, chest_x1:chest_x2]
    if chest_crop.size == 0:
        return False
    
    hsv = cv2.cvtColor(chest_crop, cv2.COLOR_BGR2HSV)
    
    lower_white = np.array([0, 0, 140])
    upper_white = np.array([180, 60, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    white_ratio = np.sum(white_mask > 0) / white_mask.size
    
    lower_purple = np.array([130, 50, 50])
    upper_purple = np.array([160, 255, 255])
    purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    purple_ratio = np.sum(purple_mask > 0) / purple_mask.size
    
    return white_ratio > 0.08 or purple_ratio > 0.05

CLASS_NAMES = ['shirt', 'pant', 'id_card', 'shoes']

def process_frame(frame, return_annotated=False):
    """
    Process a frame and return detection results
    
    Args:
        frame: numpy array (BGR image)
        return_annotated: if True, return annotated frame as well
    
    Returns:
        dict with detection results
    """
    if model is None:
        return {"error": "Model not loaded", "status": False}
    
    frame_height, frame_width = frame.shape[:2]
    
    try:
        results = model.predict(frame, imgsz=IMG_SIZE, conf=CONF_THRESH, verbose=False)
        res = results[0]
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return {"error": str(e), "status": False}
    
    detections = []
    
    for b in res.boxes:
        conf = float(b.conf[0])
        cls = int(b.cls[0])
        x1, y1, x2, y2 = map(int, b.xyxy[0])
        area = (x2 - x1) * (y2 - y1)
        
        if area < MIN_AREA:
            continue
        
        class_name = CLASS_NAMES[cls] if cls < len(CLASS_NAMES) else str(cls)
        
        crop = crop_from_box(frame, (x1, y1, x2, y2))
        color = classify_color(crop)
        
        detections.append({
            'class': class_name,
            'color': color,
            'conf': conf,
            'box': [x1, y1, x2, y2],
            'area': area
        })
    
    # Check for ID card using heuristic if not detected
    found = {'shirt': [], 'pant': [], 'shoes': [], 'id_card': []}
    for d in detections:
        if d['class'] in found:
            found[d['class']].append(d)
    
    if not found['id_card'] and found['shirt']:
        main_shirt = None
        for shirt in found['shirt']:
            box = shirt['box']
            center_y = (box[1] + box[3]) / 2
            if center_y < frame_height * 0.6:
                area = (box[2] - box[0]) * (box[3] - box[1])
                if main_shirt is None or area > main_shirt[1]:
                    main_shirt = (shirt['box'], area)
        
        if main_shirt is not None:
            shirt_box = main_shirt[0]
            if detect_id_card_heuristic(frame, shirt_box):
                x1, y1, x2, y2 = shirt_box
                chest_x = x1 + int((x2 - x1) * 0.5)
                chest_y = y1 + int((y2 - y1) * 0.3)
                found['id_card'].append({
                    'class': 'id_card',
                    'color': 'white',
                    'conf': 0.90,
                    'box': [chest_x - 50, chest_y - 50, chest_x + 50, chest_y + 50],
                    'heuristic': True
                })
                detections.append(found['id_card'][0])
    
    # Validation
    shirt_ok = False
    shirt_color = 'none'
    if found['shirt']:
        for s in found['shirt']:
            crop = crop_from_box(frame, s['box'])
            color = classify_color(crop)
            shirt_color = color
            if color in SHIRT_ALLOWED or hsv_gray_ratio(crop, sat_thresh=60) > 0.35:
                shirt_ok = True
                break
    
    pant_ok = False
    pant_color = 'none'
    if found['pant']:
        for p in found['pant']:
            pant_color = p['color']
            if p['color'] in PANTS_ALLOWED:
                pant_ok = True
                break
    
    shoes_ok = len(found['shoes']) > 0 if SHOES_REQUIRED else True
    shoes_color = found['shoes'][0]['color'] if found['shoes'] else 'none'
    
    id_ok = len(found['id_card']) > 0 if ID_REQUIRED else True
    id_color = found['id_card'][0]['color'] if found['id_card'] else 'none'
    
    complete_uniform = shirt_ok and pant_ok and shoes_ok and id_ok
    
    result = {
        "status": True,
        "complete_uniform": complete_uniform,
        "result": 1 if complete_uniform else 0,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "shirt": {
                "detected": shirt_ok,
                "color": shirt_color,
                "valid": shirt_ok
            },
            "pants": {
                "detected": pant_ok,
                "color": pant_color,
                "valid": pant_ok
            },
            "shoes": {
                "detected": shoes_ok,
                "color": shoes_color,
                "valid": shoes_ok
            },
            "id_card": {
                "detected": id_ok,
                "color": id_color,
                "valid": id_ok
            }
        },
        "detections": detections,
        "frame_size": [frame_width, frame_height]
    }
    
    if return_annotated:
        # Create annotated frame
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['box']
            color = (0, 255, 0) if det['class'] in found else (0, 0, 255)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, f"{det['class']}:{det['color']}", (x1, y1-8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add status overlay
        y_offset = 30
        status_items = [
            (f'Shirt ({shirt_color})', shirt_ok),
            (f'Pants ({pant_color})', pant_ok),
            (f'Shoes ({shoes_color})', shoes_ok),
            (f'ID Card ({id_color})', id_ok)
        ]
        
        for item_name, status in status_items:
            symbol = "✓" if status else "✗"
            color = (0, 255, 0) if status else (0, 0, 255)
            text = f"{symbol} {item_name}"
            cv2.putText(annotated_frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 35
        
        if complete_uniform:
            result_text = "COMPLETE UNIFORM - 1"
            result_color = (0, 255, 0)
        else:
            result_text = "INCOMPLETE UNIFORM - 0"
            result_color = (0, 0, 255)
        
        cv2.putText(annotated_frame, result_text, (10, annotated_frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, result_color, 3)
        
        # Encode to base64
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        result['annotated_image'] = base64.b64encode(buffer).decode()
    
    return result

# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/detect-image', methods=['POST'])
def detect_image():
    """
    Detect uniform in uploaded image
    
    Request: multipart/form-data with 'image' file
    Response: JSON with detection results
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided", "status": False}), 400
        
        file = request.files['image']
        file_bytes = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image format", "status": False}), 400
        
        # Get annotated parameter from query
        return_annotated = request.args.get('annotated', 'false').lower() == 'true'
        
        result = process_frame(frame, return_annotated=return_annotated)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in /detect-image: {e}")
        return jsonify({"error": str(e), "status": False}), 500

@app.route('/detect-base64', methods=['POST'])
def detect_base64():
    """
    Detect uniform in base64 encoded image
    
    Request: JSON with 'image' as base64 string
    Response: JSON with detection results
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided", "status": False}), 400
        
        image_b64 = data['image']
        image_bytes = base64.b64decode(image_b64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid image format", "status": False}), 400
        
        return_annotated = data.get('annotated', False)
        
        result = process_frame(frame, return_annotated=return_annotated)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in /detect-base64: {e}")
        return jsonify({"error": str(e), "status": False}), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "confidence_threshold": CONF_THRESH,
        "min_area": MIN_AREA,
        "image_size": IMG_SIZE,
        "shirt_allowed": list(SHIRT_ALLOWED),
        "pants_allowed": list(PANTS_ALLOWED),
        "shoes_required": SHOES_REQUIRED,
        "id_required": ID_REQUIRED,
        "model_path": MODEL_PATH,
        "color_classifier_loaded": USE_COLOR_CLASSIFIER
    })

@app.route('/config', methods=['POST'])
def update_config():
    """Update configuration"""
    global CONF_THRESH, MIN_AREA, IMG_SIZE
    
    try:
        data = request.get_json()
        
        if 'confidence_threshold' in data:
            CONF_THRESH = data['confidence_threshold']
        if 'min_area' in data:
            MIN_AREA = data['min_area']
        if 'image_size' in data:
            IMG_SIZE = data['image_size']
        
        return jsonify({
            "status": "success",
            "message": "Configuration updated",
            "confidence_threshold": CONF_THRESH,
            "min_area": MIN_AREA,
            "image_size": IMG_SIZE
        })
    
    except Exception as e:
        return jsonify({"error": str(e), "status": False}), 500

@app.route('/info', methods=['GET'])
def get_info():
    """Get API information"""
    return jsonify({
        "api_name": "Mobile Uniform Detector API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /detect-image": "Detect from image upload",
            "POST /detect-base64": "Detect from base64 image",
            "GET /config": "Get current config",
            "POST /config": "Update config",
            "GET /info": "API information"
        },
        "output_format": {
            "complete_uniform": "Boolean - whether uniform is complete",
            "result": "Binary - 1 for complete, 0 for incomplete",
            "components": {
                "shirt": {"detected": "bool", "color": "string", "valid": "bool"},
                "pants": {"detected": "bool", "color": "string", "valid": "bool"},
                "shoes": {"detected": "bool", "color": "string", "valid": "bool"},
                "id_card": {"detected": "bool", "color": "string", "valid": "bool"}
            }
        }
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large"""
    return jsonify({
        "error": "File too large. Maximum size: 50MB",
        "status": False
    }), 413

if __name__ == '__main__':
    logger.info("Initializing Mobile Detector API...")
    
    if not initialize_models():
        logger.error("Failed to initialize models. Exiting.")
        exit(1)
    
    logger.info("Starting Flask API server...")
    logger.info("API available at: http://localhost:5000")
    logger.info("Health check: http://localhost:5000/health")
    logger.info("API info: http://localhost:5000/info")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
