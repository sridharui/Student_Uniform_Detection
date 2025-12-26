"""
Complete Uniform Detection System
Detects if a student is wearing complete uniform (1) or not (0)
For Boys: ID Card + Shirt + Pant + Shoes
For Girls: ID Card + Top + Pant + Shoes
"""
import cv2
import numpy as np
from ultralytics import YOLO
import os
from collections import defaultdict
try:
    import serial
    from serial.tools import list_ports
except Exception:
    serial = None
    list_ports = None

class UniformDetector:
    """Uniform detection system using YOLO (v11 weights by default)"""
    
    def __init__(self, model_path="runs/train/uniform_detector_yolov11_cpu/weights/best.pt", serial_port=None, baud=9600, enable_serial=True):
        """Initialize the detector with trained model"""
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Always resolve relative paths against the script directory so running from elsewhere still works
        resolved_model_path = model_path
        if not os.path.isabs(model_path):
            resolved_model_path = os.path.join(script_dir, model_path)
        self.model_path = resolved_model_path

        # Check for the first available weights file
        candidates = [
            resolved_model_path,
            os.path.join(script_dir, "runs/train/uniform_detector_yolov11_cpu/weights/best.pt"),
            os.path.join(script_dir, "yolo11n.pt"),
            os.path.join(script_dir, "yolov8m.pt"),
        ]

        self.model = None
        for candidate in candidates:
            if os.path.exists(candidate):
                self.model = YOLO(candidate)
                print(f"✅ Model loaded: {candidate}")
                break

        if self.model is None:
            print(f"⚠️  Model not found at {resolved_model_path}")
            print("Please run training first or provide --model path")
        
        # Serial link setup (optional)
        self.enable_serial = enable_serial and (serial is not None)
        self.ser = None
        self.baud = baud
        self.serial_port = serial_port
        self._init_serial_link()

        # Define uniform components
        # For Boys: ID Card + Shirt + Pant + Shoes
        # For Girls: ID Card + Top + Pant + Shoes
        self.REQUIRED_BOYS = {
            'Identity Card',
            'Shirt',
            'pant',
            'shoes'
        }
        
        self.REQUIRED_GIRLS = {
            'Identity Card',
            'top',
            'pant',
            'shoes'
        }
        
        # Gender-specific classes
        self.BOYS_CLASSES = {'Shirt'}
        self.GIRLS_CLASSES = {'top'}
        
        # All possible class names from the dataset
        self.VALID_CLASSES = {
            'Identity Card', 'Shirt', 'identity card', 'pant', 
            'shoes', 'slippers', 'top'
        }
        
        # Confidence thresholds per class for better accuracy
        self.CONF_THRESHOLDS = {
            'Identity Card': 0.50,
            'identity card': 0.50,
            'Shirt': 0.55,
            'top': 0.55,
            'pant': 0.50,
            'shoes': 0.50,
            'slippers': 0.50
        }
        
        self.CONF_THRESHOLD = 0.50  # Default threshold

    def _init_serial_link(self):
        """Initialize serial connection to Arduino if available"""
        if not self.enable_serial:
            print("ℹ️ Serial disabled or pyserial not installed; skipping COM link")
            return

        try:
            port = self.serial_port
            if port is None and list_ports is not None:
                # Try auto-detect Arduino-like ports
                candidates = []
                for p in list_ports.comports():
                    desc = (p.description or "").lower()
                    hwid = (p.hwid or "").lower()
                    if any(tag in desc for tag in ["arduino", "ch340", "wch", "usb serial"]):
                        candidates.append(p.device)
                port = candidates[0] if candidates else None

            if port is None:
                print("⚠️ No Arduino COM port auto-detected. Set --serial-port COMx to enable.")
                return

            self.ser = serial.Serial(port, self.baud, timeout=0.5)
            print(f"🔌 Serial link established on {port} @ {self.baud} baud")
        except Exception as e:
            print(f"⚠️ Failed to open serial port: {e}")
            self.ser = None

    def _send_flag(self, status):
        """Send 1 for complete, 0 otherwise over serial"""
        if not self.ser:
            return
        try:
            flag = 1 if status == 1 else 0
            self.ser.write(f"{flag}\n".encode("utf-8"))
        except Exception as e:
            # Non-fatal; keep detection running
            print(f"⚠️ Serial write failed: {e}")
    
    def detect_uniform(self, image_source):
        """
        Detect if person is wearing complete uniform
        
        Args:
            image_source: Path to image or numpy array
        
        Returns:
            dict with detection results
        """
        if self.model is None:
            return {
                'uniform_status': -1,  # Error
                'message': 'Model not loaded',
                'detections': []
            }
        
        # Load image
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                return {
                    'uniform_status': -1,
                    'message': f'Failed to load image: {image_source}',
                    'detections': []
                }
        else:
            image = image_source
        
        # Run inference with lower confidence to catch all potential detections
        results = self.model(image, conf=0.3, verbose=False)
        
        # Extract detections with class-specific thresholds
        detections = defaultdict(int)
        detected_classes = []
        detection_details = []  # Store confidence scores for better filtering
        
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None:
                for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    class_name = result.names[int(cls_id)]
                    confidence = float(conf)
                    
                    # Apply class-specific threshold
                    class_threshold = self.CONF_THRESHOLDS.get(class_name, self.CONF_THRESHOLD)
                    
                    if confidence >= class_threshold:
                        detected_classes.append(class_name)
                        detections[class_name] += 1
                        detection_details.append({
                            'class': class_name,
                            'confidence': confidence,
                            'box': box.cpu().numpy() if hasattr(box, 'cpu') else box
                        })
                        print(f"  ✓ Detected: {class_name} (confidence: {confidence:.2f}, threshold: {class_threshold})")
                    else:
                        print(f"  ✗ Filtered out: {class_name} (confidence: {confidence:.2f} < threshold: {class_threshold})")
        
        # Normalize class names (handle variations) and keep counts
        normalized_detections, normalized_counts = self._normalize_detections(detected_classes, detections)

        # Detect gender and check for complete uniform
        detected_gender = self._detect_gender(normalized_detections, normalized_counts)
        is_complete, missing_items, uniform_type = self._check_complete_uniform_v2(
            normalized_detections, normalized_counts, detected_gender
        )
        
        return {
            'uniform_status': 1 if is_complete else 0,
            'is_complete': is_complete,
            'uniform_type': uniform_type,
            'detected_gender': detected_gender,
            'detected_items': list(normalized_detections),
            'missing_items': missing_items,
            'detection_counts': dict(normalized_counts),
            'raw_detections': dict(detections),
            'detection_details': detection_details,
            'message': self._generate_message(is_complete, missing_items, uniform_type),
            'image': image
        }
    
    def _normalize_detections(self, detected_classes, raw_counts=None):
        """Normalize class names to standard format and return counts.

        Returns: (normalized_set, normalized_counts_dict)
        """
        normalized = set()
        counts = defaultdict(int)

        # When raw_counts is provided from YOLO boxes, rely on it to avoid double-counting
        source_counts = raw_counts if raw_counts else defaultdict(int)
        if not raw_counts:
            for class_name in detected_classes:
                source_counts[class_name] += 1

        for raw_name, cnt in source_counts.items():
            ln = raw_name.lower()

            if 'identity' in ln or 'card' in ln or 'id' in ln:
                normalized.add('Identity Card')
                counts['Identity Card'] += cnt
            elif ln == 'shirt':
                normalized.add('Shirt')
                counts['Shirt'] += cnt
            elif ln == 'top':
                normalized.add('top')
                counts['top'] += cnt
            elif ln == 'pant':
                normalized.add('pant')
                counts['pant'] += cnt
            elif ln == 'shoes':
                normalized.add('shoes')
                counts['shoes'] += cnt
            elif ln == 'slippers':
                normalized.add('slippers')
                counts['slippers'] += cnt

        return normalized, counts
    
    def _detect_gender(self, detections, counts):
        """
        Detect if the person is likely a boy or girl based on clothing
        Returns: 'BOYS', 'GIRLS', or 'UNKNOWN'
        """
        # Priority: explicit gender-specific classes
        if 'top' in detections and 'Shirt' not in detections:
            return 'GIRLS'
        elif 'Shirt' in detections and 'top' not in detections:
            return 'BOYS'
        elif 'top' in detections and 'Shirt' in detections:
            # Both detected - use confidence counts
            top_count = counts.get('top', 0)
            shirt_count = counts.get('Shirt', 0)
            if top_count > shirt_count:
                return 'GIRLS'
            elif shirt_count > top_count:
                return 'BOYS'
        
        return 'UNKNOWN'
    
    def _check_complete_uniform_v2(self, detections, counts, detected_gender):
        """
        Enhanced uniform checking with gender prioritization
        Returns: (is_complete, missing_items, uniform_type)
        """
        # If gender is clearly detected, use that requirement set
        if detected_gender == 'GIRLS':
            girls_complete = self.REQUIRED_GIRLS.issubset(detections)
            missing_girls = list(self.REQUIRED_GIRLS - detections)
            status = "GIRLS"
            return (True, missing_girls, status) if girls_complete else (False, missing_girls, f"{status} (incomplete)")
        
        elif detected_gender == 'BOYS':
            boys_complete = self.REQUIRED_BOYS.issubset(detections)
            missing_boys = list(self.REQUIRED_BOYS - detections)
            status = "BOYS"
            return (True, missing_boys, status) if boys_complete else (False, missing_boys, f"{status} (incomplete)")
        
        else:
            # Unknown gender - check both possibilities
            boys_complete = self.REQUIRED_BOYS.issubset(detections)
            girls_complete = self.REQUIRED_GIRLS.issubset(detections)

            missing_boys = self.REQUIRED_BOYS - detections
            missing_girls = self.REQUIRED_GIRLS - detections

            if boys_complete:
                return True, list(missing_boys), "BOYS"
            elif girls_complete:
                return True, list(missing_girls), "GIRLS"
            else:
                # Choose the type with fewer missing items
                if len(missing_boys) <= len(missing_girls):
                    return False, list(missing_boys), "BOYS (incomplete)"
                else:
                    return False, list(missing_girls), "GIRLS (incomplete)"
    
    def _check_complete_uniform(self, detections, counts=None):
        """
        Legacy method - kept for backward compatibility
        Check if detected items form a complete uniform
        Returns: (is_complete, missing_items, uniform_type)
        """
        # Priority rule: if 'top' detected (and 'Shirt' not), treat as GIRLS
        if 'top' in detections and 'Shirt' not in detections:
            girls_complete = self.REQUIRED_GIRLS.issubset(detections)
            missing_girls = list(self.REQUIRED_GIRLS - detections)
            return (True, missing_girls, "GIRLS") if girls_complete else (False, missing_girls, "GIRLS (incomplete)")

        # Priority rule: if 'Shirt' detected (and 'top' not), treat as BOYS
        if 'Shirt' in detections and 'top' not in detections:
            boys_complete = self.REQUIRED_BOYS.issubset(detections)
            missing_boys = list(self.REQUIRED_BOYS - detections)
            return (True, missing_boys, "BOYS") if boys_complete else (False, missing_boys, "BOYS (incomplete)")

        # Fallback: check both
        boys_complete = self.REQUIRED_BOYS.issubset(detections)
        girls_complete = self.REQUIRED_GIRLS.issubset(detections)

        missing_boys = self.REQUIRED_BOYS - detections
        missing_girls = self.REQUIRED_GIRLS - detections

        if boys_complete:
            return True, list(missing_boys), "BOYS"
        elif girls_complete:
            return True, list(missing_girls), "GIRLS"
        else:
            # If counts are available, use them to decide which gender is likelier
            if counts is not None:
                top_count = int(counts.get('top', 0))
                shirt_count = int(counts.get('Shirt', 0))
                if top_count > shirt_count:
                    return False, list(missing_girls), "GIRLS (incomplete)"
                elif shirt_count > top_count:
                    return False, list(missing_boys), "BOYS (incomplete)"

            # Default: choose the type with fewer missing items
            if len(missing_boys) <= len(missing_girls):
                return False, list(missing_boys), "BOYS (incomplete)"
            else:
                return False, list(missing_girls), "GIRLS (incomplete)"
    
    def _generate_message(self, is_complete, missing_items, uniform_type):
        """Generate human-readable message"""
        if is_complete:
            return f"✅ COMPLETE UNIFORM ({uniform_type}) - Student is properly dressed"
        else:
            missing_str = ", ".join(missing_items) if missing_items else "Unknown"
            return f"❌ INCOMPLETE UNIFORM ({uniform_type}) - Missing: {missing_str}"
    
    def detect_from_webcam(self, camera_id=0, display=True):
        """
        Real-time uniform detection from webcam
        
        Args:
            camera_id: Webcam device ID
            display: Whether to display results
        """
        if self.model is None:
            print("❌ Model not loaded")
            return
        
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {camera_id}")
            return
        
        print("📷 Webcam detection started. Press 'q' to quit, 'c' to capture...")
        print("=" * 80)
        print("DETECTION GUIDELINES:")
        print("  BOYS: ID Card + Shirt + Pant + Shoes")
        print("  GIRLS: ID Card + Top + Pant + Shoes")
        print("=" * 80)
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Run detection every 5 frames for efficiency
                if frame_count % 5 == 0:
                    result = self.detect_uniform(frame)
                    
                    # Display result on frame
                    status = result['uniform_status']
                    message = result['message']
                    detected_gender = result.get('detected_gender', 'UNKNOWN')
                    detected_items = result.get('detected_items', [])
                    missing_items = result.get('missing_items', [])
                    
                    # Color based on status
                    color = (0, 255, 0) if status == 1 else (0, 0, 255) if status == 0 else (0, 165, 255)
                    
                    # Add text to frame with enhanced info
                    cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.8, color, 2)
                    cv2.putText(frame, f"Gender: {detected_gender}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                               0.7, (255, 200, 0), 2)
                    cv2.putText(frame, f"Detected: {', '.join(detected_items)}", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 1)
                    if missing_items:
                        cv2.putText(frame, f"Missing: {', '.join(missing_items)}", (10, 150), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                    
                    # Terminal Output
                    print(f"\n[Frame {frame_count}]")
                    print(f"  Gender Detected: {detected_gender}")
                    print(f"  {message}")
                    print(f"  Detected Items: {detected_items}")
                    print(f"  Missing Items: {missing_items}")
                    print(f"  Status Flag: {1 if status == 1 else 0}")
                    
                    # Send flag to Arduino
                    self._send_flag(status)
                
                if display:
                    cv2.imshow('Uniform Detection - Press Q to quit, C to capture', frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('c'):
                        cv2.imwrite(f"uniform_detection_{frame_count}.jpg", frame)
                        print(f"✅ Captured: uniform_detection_{frame_count}.jpg")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("📷 Webcam detection stopped")
            print("=" * 80)
    
    def detect_from_video(self, video_path, output_path="uniform_detection_output.mp4"):
        """
        Detect uniform from video file
        """
        if self.model is None:
            print("❌ Model not loaded")
            return
        
        if not os.path.exists(video_path):
            print(f"❌ Video not found: {video_path}")
            return
        
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        
        frame_count = 0
        
        print(f"📹 Processing video: {video_path}")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Detect every 5 frames
            if frame_count % 5 == 0:
                result = self.detect_uniform(frame)
                status = result['uniform_status']
                message = result['message']
                color = (0, 255, 0) if status == 1 else (0, 0, 255)
                
                cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, color, 2)
                
                print(f"Frame {frame_count}: {message}")
                # Terminal Output flag for video frames
                flag = 1 if status == 1 else 0
                print(f"Terminal Output: {flag}")
                # Send flag to Arduino
                self._send_flag(status)
            
            out.write(frame)
        
        cap.release()
        out.release()
        print(f"✅ Video processing complete: {output_path}")


def main():
    """Run laptop webcam detection with optional model override"""
    import argparse
    parser = argparse.ArgumentParser(description="Uniform detection via laptop webcam")
    parser.add_argument("--model", type=str, default="runs/train/uniform_detector_yolov11_cpu/weights/best.pt",
                        help="Path to YOLO model weights (.pt)")
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index (default: 0)")
    parser.add_argument("--serial-port", type=str, default=None, help="COM port for Arduino (e.g., COM3). If omitted, auto-detect is attempted.")
    parser.add_argument("--baud", type=int, default=9600, help="Serial baud rate (default: 9600)")
    parser.add_argument("--no-serial", action="store_true", help="Disable serial output to Arduino")
    args = parser.parse_args()

    detector = UniformDetector(model_path=args.model, serial_port=args.serial_port, baud=args.baud, enable_serial=(not args.no_serial))
    
    print("\n" + "=" * 80)
    print("UNIFORM DETECTION SYSTEM (Laptop Webcam)")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Camera ID: {args.camera}")
    
    # Webcam detection
    detector.detect_from_webcam(camera_id=args.camera)
    
    # Optional: quick test with an image if present
    test_image = "test_uniform.jpg"
    if os.path.exists(test_image):
        result = detector.detect_uniform(test_image)
        print(f"\nImage Result -> Status: {result['uniform_status']} | {result['message']}")


if __name__ == "__main__":
    main()
