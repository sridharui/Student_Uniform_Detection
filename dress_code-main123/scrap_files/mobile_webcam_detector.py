# mobile_webcam_detector.py
# Real-time detection using mobile IP webcam
# Connect your phone's IP webcam app to stream video to the detection system

import cv2
import numpy as np
import joblib
import sys
import time
import os
from ultralytics import YOLO
from sklearn.cluster import KMeans

# CONFIG
MODEL_PATH = "runs/train/uniform_color_trained2/weights/best.pt"
FALLBACK_MODEL_PATH = "runs/train/uniform_color_trained/weights/best.pt"
COLOR_CLF_PATH = "color_clf.joblib"
USE_COLOR_CLASSIFIER = os.path.exists(COLOR_CLF_PATH)
CONF_THRESH = 0.10
MIN_AREA = 400
IMG_SIZE = 1280

# MOBILE WEBCAM CONFIG
MOBILE_WEBCAM_URL = "https://192.168.0.15:8080/video"  # IP Webcam video stream URL
# Alternative URLs to try:
# "http://192.168.0.15:8080/video"  # HTTP version
# "rtsp://192.168.0.15:8080/h264"   # RTSP stream
# "http://192.168.0.15:8080/shot.jpg"  # MJPEG stream

# UNIFORM VALIDATION RULES
SHIRT_ALLOWED = {'gray'}
PANTS_ALLOWED = {'black'}
ID_ALLOWED = {'purple', 'yellow', 'green', 'red', 'white'}
SHOES_REQUIRED = True   # Any shoe color accepted if detected
ID_REQUIRED = True

# Helper functions
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
    if r > 170 and g > 170 and b < 120:
        return 'yellow'
    if b > r and b > g:
        return 'blue'
    if g > r and g > b:
        return 'green'
    if r > g and r > b:
        return 'red'
    return 'unknown'

def classify_color(img_bgr, clf=None):
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
    
    # Check for multiple allowed ID colors
    lower_white = np.array([0, 0, 140]);   upper_white = np.array([180, 60, 255])
    lower_purple = np.array([130, 50, 50]); upper_purple = np.array([165, 255, 255])
    lower_yellow = np.array([20, 80, 120]); upper_yellow = np.array([35, 255, 255])
    lower_green = np.array([45, 50, 50]);   upper_green = np.array([85, 255, 255])
    lower_red1 = np.array([0, 70, 50]);     upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50]);   upper_red2 = np.array([180, 255, 255])

    ratios = []
    for low, high in [
        (lower_white, upper_white),
        (lower_purple, upper_purple),
        (lower_yellow, upper_yellow),
        (lower_green, upper_green),
        (lower_red1, upper_red1),
        (lower_red2, upper_red2),
    ]:
        mask = cv2.inRange(hsv, low, high)
        ratios.append(np.sum(mask > 0) / mask.size)

    return any(r > 0.05 for r in ratios)

CLASS_NAMES = ['shirt', 'pant', 'id_card', 'shoes']

def process_frame_detection(frame, model, clf=None):
    """Process frame and return detection results"""
    frame_height, frame_width = frame.shape[:2]
    
    try:
        results = model.predict(frame, imgsz=IMG_SIZE, conf=CONF_THRESH, verbose=False)
        res = results[0]
    except Exception as e:
        print(f"Detection error: {e}")
        return None
    
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
        color = classify_color(crop, clf)
        
        detections.append({
            'class': class_name,
            'color': color,
            'conf': conf,
            'box': (x1, y1, x2, y2),
            'area': area
        })
    
    # Check uniform status
    found = {'shirt': [], 'pant': [], 'shoes': [], 'id_card': []}
    for d in detections:
        if d['class'] in found:
            found[d['class']].append(d)
    
    # Heuristic ID card detection
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
                    'box': (chest_x - 50, chest_y - 50, chest_x + 50, chest_y + 50),
                    'heuristic': True
                })
                detections.append(found['id_card'][0])
    
    # Validation
    shirt_ok = False
    shirt_color = 'none'
    if found['shirt']:
        for s in found['shirt']:
            crop = crop_from_box(frame, s['box'])
            color = classify_color(crop, clf)
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
    
    id_ok = False if ID_REQUIRED else True
    id_color = 'none'
    if found['id_card']:
        for card in found['id_card']:
            id_color = card['color']
            if id_color in ID_ALLOWED:
                id_ok = True
                break
    
    complete_uniform = shirt_ok and pant_ok and shoes_ok and id_ok
    
    return {
        'complete': complete_uniform,
        'result': 1 if complete_uniform else 0,
        'shirt': {'ok': shirt_ok, 'color': shirt_color},
        'pant': {'ok': pant_ok, 'color': pant_color},
        'shoes': {'ok': shoes_ok, 'color': shoes_color},
        'id_card': {'ok': id_ok, 'color': id_color},
        'detections': detections,
        'found': found
    }

def detect_from_mobile_webcam(mobile_url, skip_frames=2):
    """
    Real-time detection from mobile IP webcam
    
    Args:
        mobile_url: URL of mobile webcam (e.g., "http://192.168.0.9:8080/video")
        skip_frames: Skip N frames for performance
    """
    
    print("=== Mobile IP Webcam Uniform Detector ===\n")
    print(f"Connecting to: {mobile_url}\n")
    
    # Load model
    model_path = MODEL_PATH if os.path.exists(MODEL_PATH) else FALLBACK_MODEL_PATH
    try:
        model = YOLO(model_path)
        print(f"✓ Model loaded: {model_path}\n")
    except Exception as e:
        print(f"✗ Error loading model: {e}\n")
        return
    
    # Load color classifier
    clf = None
    if USE_COLOR_CLASSIFIER:
        try:
            clf = joblib.load(COLOR_CLF_PATH)
            print("✓ Color classifier loaded\n")
        except Exception as e:
            print(f"⚠ Color classifier not found: {e}\n")
    
    # Connect to mobile webcam
    print("Connecting to mobile webcam...")
    cap = cv2.VideoCapture(mobile_url)
    
    if not cap.isOpened():
        print(f"✗ Failed to connect to {mobile_url}")
        print("\nTroubleshooting:")
        print("1. Ensure your phone's IP webcam app is running")
        print("2. Check phone is on same network as computer")
        print("3. Verify IP address: 192.168.0.9")
        print("4. Try these URLs:")
        print("   - http://192.168.0.9:8080/video")
        print("   - https://192.168.0.9:8080/video")
        print("   - rtsp://192.168.0.9:8080/h264")
        print("5. Check firewall settings")
        return
    
    print("✓ Connected to mobile webcam\n")
    print("Controls:")
    print("  Press 'Q' to quit")
    print("  Press 'S' to save detection result")
    print("  Press 'SPACE' to pause/resume\n")
    
    frame_count = 0
    fps_counter = 0
    fps_start_time = time.time()
    fps = 0
    paused = False
    
    try:
        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame, retrying...")
                    time.sleep(0.5)
                    continue
                
                frame_count += 1
                fps_counter += 1
                
                # Skip frames for performance
                if frame_count % skip_frames != 0:
                    continue
                
                # Calculate FPS
                if time.time() - fps_start_time >= 1.0:
                    fps = fps_counter
                    fps_counter = 0
                    fps_start_time = time.time()
                
                # Process frame
                result = process_frame_detection(frame, model, clf)
                
                if result is None:
                    continue
                
                # Draw detections
                frame_display = frame.copy()
                
                for det in result['detections']:
                    x1, y1, x2, y2 = det['box']
                    color = (0, 255, 0)
                    cv2.rectangle(frame_display, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame_display, f"{det['class']}:{det['color']}", 
                               (x1, y1-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Status overlay
                y_offset = 30
                status_items = [
                    (f"Shirt ({result['shirt']['color']})", result['shirt']['ok']),
                    (f"Pants ({result['pant']['color']})", result['pant']['ok']),
                    (f"Shoes ({result['shoes']['color']})", result['shoes']['ok']),
                    (f"ID Card ({result['id_card']['color']})", result['id_card']['ok'])
                ]
                
                for item_name, status in status_items:
                    symbol = "✓" if status else "✗"
                    color = (0, 255, 0) if status else (0, 0, 255)
                    text = f"{symbol} {item_name}"
                    cv2.putText(frame_display, text, (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    y_offset += 35
                
                # Result
                if result['complete']:
                    result_text = "COMPLETE UNIFORM - 1"
                    result_color = (0, 255, 0)
                else:
                    result_text = "INCOMPLETE UNIFORM - 0"
                    result_color = (0, 0, 255)
                
                cv2.putText(frame_display, result_text, (10, frame_display.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, result_color, 3)
                
                # FPS
                cv2.putText(frame_display, f"FPS: {fps}", 
                           (frame_display.shape[1] - 120, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Print result
                print(f"Result: {result['result']}", end='\r')
                
                cv2.imshow('Mobile Uniform Detection - Press Q to quit', frame_display)
            
            # Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\nQuitting...")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"detection_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame_display)
                print(f"\n✓ Saved: {filename}")
            elif key == ord(' '):
                paused = not paused
                status = "PAUSED" if paused else "RESUMED"
                print(f"\n{status}")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Disconnected from mobile webcam")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Mobile IP Webcam Uniform Detector')
    parser.add_argument('--url', type=str, default=MOBILE_WEBCAM_URL,
                       help='Mobile webcam URL (default: https://192.168.0.9:8080/video)')
    parser.add_argument('--skip', type=int, default=2,
                       help='Skip N frames for performance (default: 2)')
    parser.add_argument('--http', action='store_true',
                       help='Use HTTP instead of HTTPS')
    
    args = parser.parse_args()
    
    # Modify URL if HTTP flag set
    if args.http:
        url = args.url.replace('https://', 'http://')
    else:
        url = args.url
    
    detect_from_mobile_webcam(url, skip_frames=args.skip)
