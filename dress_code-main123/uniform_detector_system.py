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
        # Based on Complete_Uniform.v3i.yolov12 classes
        self.REQUIRED_BOYS = {
            'Identity Card',  # or 'identity card'
            'Shirt',
            'pant',
            'shoes'
        }
        
        self.REQUIRED_GIRLS = {
            'Identity Card',  # or 'identity card'
            'top',
            'pant',
            'shoes'
        }
        
        # All possible class names from the dataset (expanded with common aliases)
        self.VALID_CLASSES = {
            'Identity Card', 'identity card', 'id card', 'idcard',
            'Shirt', 'shirt', 'tshirt', 't-shirt', 'top',
            'pant', 'pants', 'trouser', 'trousers',
            'shoes', 'shoe', 'slippers', 'sandal', 'sandals'
        }
        
        # Per-item confidence thresholds (very aggressive for shoes/ID to catch at full-body distance)
        self.CONF_THRESHOLDS = {
            'shoes': 0.18,         # Very low to catch shoes even at distance
            'Identity Card': 0.20, # Very low to catch visible ID cards/lanyards
            'Shirt': 0.34,         # Balanced for shirts
            'top': 0.34,           # Balanced for tops
            'pant': 0.28,          # Lower to recover pants
            'slippers': 0.18,      # Match shoes
            'default': 0.30        # Balanced default
        }

        self.CONF_THRESHOLD = 0.20  # Base threshold for initial model filtering
        
        # Color validation enabled flag
        self.ENABLE_COLOR_VALIDATION = True
        
        # Multi-student detection settings
        self.ENABLE_MULTI_STUDENT_DETECTION = True
        self.PERSON_CONF_THRESHOLD = 0.20  # Very low to ensure person association
        self.MAX_DISTANCE_TO_PERSON = 200  # Max pixel distance to associate item with person
        
        # Allowed colors for uniform components
        self.ALLOWED_COLORS = {
            'id_card_tag': ['yellow', 'pink', 'green', 'red'],
            'id_card': ['white'],  # White with letters
            'shirt': ['gray', 'cement'],  # Gray/cement color
            'top': ['gray'],  # Gray (can have dupatta)
            'dupatta': ['navy', 'black'],  # Navy blue or black dupatta
            'pant': ['navy', 'black'],  # Navy blue or black
            'shoes': []  # Any color allowed
        }

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
    
    def _is_full_body_visible(self, detections_data, image_height, image_width):
        """
        Check if full person is visible in frame (head to toe)
        Returns True only if person fully fits in frame
        
        Args:
            detections_data: List of (box, class_name, confidence) tuples
            image_height: Height of the frame
            image_width: Width of the frame
        
        Returns:
            bool: True if full body is visible, False otherwise
        """
        if not detections_data:
            return False
        
        # Collect all bounding boxes
        all_boxes = [box for box, _, _ in detections_data]
        
        if len(all_boxes) < 3:  # Need at least 3 components for full body
            return False
        
        # Calculate overall person bounding box (union of all detections)
        min_y = min(box[1] for box in all_boxes)  # Top
        max_y = max(box[3] for box in all_boxes)  # Bottom
        min_x = min(box[0] for box in all_boxes)  # Left
        max_x = max(box[2] for box in all_boxes)  # Right
        
        person_height = max_y - min_y
        person_width = max_x - min_x
        
        # Check if person fits well in frame (not cut off at edges)
        # Person should be at least 60% of frame height for full body
        # Person should not touch the top/bottom edges (margins required)
        
        TOP_MARGIN = 0.05 * image_height      # 5% margin from top
        BOTTOM_MARGIN = 0.05 * image_height   # 5% margin from bottom
        MIN_HEIGHT_RATIO = 0.60               # Person should be at least 60% of frame height
        
        # Check if person is fully visible (not cut off)
        is_top_visible = min_y > TOP_MARGIN              # Not cut at top
        is_bottom_visible = max_y < (image_height - BOTTOM_MARGIN)  # Not cut at bottom
        is_tall_enough = person_height > (MIN_HEIGHT_RATIO * image_height)  # Tall enough
        
        full_body_visible = is_top_visible and is_bottom_visible and is_tall_enough
        
        if not full_body_visible:
            if not is_top_visible:
                print(f"  ⏸️  Person cut at top (min_y: {min_y:.0f}, required: >{TOP_MARGIN:.0f})")
            if not is_bottom_visible:
                print(f"  ⏸️  Person cut at bottom (max_y: {max_y:.0f}, required: <{image_height - BOTTOM_MARGIN:.0f})")
            if not is_tall_enough:
                print(f"  ⏸️  Person too small (height: {person_height:.0f}/{image_height:.0f} = {person_height/image_height:.0%}, required: >{MIN_HEIGHT_RATIO:.0%})")
        
        return full_body_visible
    
    def detect_uniform(self, image_source, require_full_body=False):
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
        
        # Run inference with base threshold
        results = self.model(image, conf=self.CONF_THRESHOLD, verbose=False)
        
        # Get image dimensions for full-body check
        image_height, image_width = image.shape[:2]
        
        # Collect all detections first (for full-body check)
        all_detections_data = []
        
        # Extract detections with per-item confidence filtering and color validation
        detections = defaultdict(int)
        detected_classes = []
        color_validation_results = {}
        
        if results and len(results) > 0:
            result = results[0]
            
            if result.boxes is not None:
                # First pass: collect all detections above threshold
                for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    class_name = result.names[int(cls_id)]
                    confidence = float(conf)
                    item_threshold = self._get_confidence_threshold(class_name)
                    
                    if confidence >= item_threshold:
                        all_detections_data.append((box.cpu().numpy(), class_name, confidence))
                
                # Check if full body is visible (only if required)
                if require_full_body:
                    if not self._is_full_body_visible(all_detections_data, image_height, image_width):
                        return {
                            'uniform_status': -2,  # Waiting for full body
                            'is_complete': False,
                            'uniform_type': 'WAITING',
                            'detected_items': [],
                            'missing_items': [],
                            'raw_detections': {},
                            'color_validation': {},
                            'message': '⏸️  WAITING - Person not fully visible in frame',
                            'image': image,
                            'full_body_visible': False
                        }
                
                # Second pass: process detections with color validation
                for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    class_name = result.names[int(cls_id)]
                    confidence = float(conf)
                    
                    # Get specific threshold for this item
                    item_threshold = self._get_confidence_threshold(class_name)
                    
                    # Only accept detection if it meets the item-specific threshold
                    if confidence >= item_threshold:
                        # Extract bounding box region for color analysis
                        x1, y1, x2, y2 = map(int, box)
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
                        
                        region = image[y1:y2, x1:x2]
                        
                        # Perform color detection
                        color_data = self._extract_dominant_color_hsv(region)
                        color_name = self._detect_color_name(color_data)
                        
                        # Validate color for this component
                        normalized_class = self._normalize_class_name(class_name)
                        color_valid, color_msg = self._validate_component_color(color_name, normalized_class, 'UNKNOWN')
                        
                        if color_valid:
                            detected_classes.append(class_name)
                            detections[class_name] += 1
                            color_validation_results[class_name] = {
                                'color': color_name,
                                'valid': True,
                                'message': color_msg
                            }
                            print(f"  ✓ Detected: {class_name} (conf: {confidence:.2f}) [color: {color_name}] ✓")
                        else:
                            color_validation_results[class_name] = {
                                'color': color_name,
                                'valid': False,
                                'message': color_msg
                            }
                            print(f"  ✗ Color Invalid: {class_name} (conf: {confidence:.2f}) - {color_msg}")
                    else:
                        print(f"  ✗ Rejected: {class_name} (confidence: {confidence:.2f}) [below threshold: {item_threshold:.2f}]")
        
        # Normalize class names (handle variations) and keep counts
        normalized_detections, normalized_counts = self._normalize_detections(detected_classes, detections)

        # Check for complete uniform (prefer 'top' -> girls, 'Shirt' -> boys)
        is_complete, missing_items, uniform_type = self._check_complete_uniform(normalized_detections, normalized_counts)
        
        return {
            'uniform_status': 1 if is_complete else 0,
            'is_complete': is_complete,
            'uniform_type': uniform_type,
            'detected_items': list(normalized_detections),
            'missing_items': missing_items,
            'raw_detections': dict(detections),
            'color_validation': color_validation_results,
            'message': self._generate_message(is_complete, missing_items, uniform_type),
            'image': image
        }
    
    def detect_uniform_multi_student(self, image_source, require_full_body=False, verbose=True):
        """
        Detect uniforms for MULTIPLE students in a single frame
        
        Args:
            image_source: Path to image or numpy array
        
        Returns:
            dict with detection results for each student
        """
        if self.model is None:
            return {
                'status': -1,
                'message': 'Model not loaded',
                'students': []
            }
        
        # Load image
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                return {
                    'status': -1,
                    'message': f'Failed to load image: {image_source}',
                    'students': []
                }
        else:
            image = image_source

        if verbose:
            print("\n" + "="*80)
            print("MULTI-STUDENT UNIFORM DETECTION")
            print("="*80)
        
        # Detect persons in frame
        persons = self._detect_persons(image)
        if verbose:
            print(f"\n👥 Persons detected: {len(persons)}")
        
        if len(persons) == 0:
            if verbose:
                print("⚠️ No persons detected in frame")
            return {
                'status': 0,
                'message': 'No persons detected',
                'students': [],
                'image': image
            }
        
        # Run full YOLO inference to get all detections
        results = self.model(image, conf=self.CONF_THRESHOLD, verbose=False)
        
        # Collect all items with their bounding boxes
        items_with_boxes = []
        
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    class_name = result.names[int(cls_id)]
                    confidence = float(conf)
                    
                    # Skip person detections, only get uniform items
                    if 'person' not in class_name.lower() and int(cls_id) != 0:
                        items_with_boxes.append({
                            'class_name': class_name,
                            'confidence': confidence,
                            'box': box
                        })
        
            if verbose:
                print(f"📦 Total items detected: {len(items_with_boxes)}")
        
        # Assign items to persons
        persons = self._assign_items_to_persons(items_with_boxes, persons)
        
        # Analyze uniform for each person
        student_results = []
        total_complete = 0
        
        for idx, person in enumerate(persons, 1):
            if verbose:
                print(f"\n--- Student {idx} Analysis ---")
                print(f"Items assigned: {len(person['uniform_items'])}")

            result = self._analyze_person_uniform(person['uniform_items'], idx, image, verbose)
            student_results.append(result)
            
            # Print result
            if verbose:
                status_text = "✅" if result['is_complete'] else "❌"
                print(f"{status_text} {result['message']}")
                print(f"Terminal Output: {result['uniform_status']}")
            
            if result['is_complete']:
                total_complete += 1
            
            # Send flag to Arduino
            self._send_flag(result['uniform_status'])
        
        if verbose:
            print("\n" + "="*80)
            print(f"SUMMARY: {total_complete}/{len(persons)} students have complete uniforms")
            print("="*80)
        
        return {
            'status': 1 if total_complete == len(persons) else 0,
            'message': f'{total_complete}/{len(persons)} complete',
            'students': student_results,
            'image': image
        }
    
    def _get_confidence_threshold(self, class_name):
        """Get the confidence threshold for a specific item class (200% ACCURACY MODE)"""
        ln = class_name.lower().strip()
        
        # Check for shoes/footwear (Balanced: High accuracy + good detection)
        if ln in ('shoes', 'shoe', 'slippers', 'sandal', 'sandals'):
            return self.CONF_THRESHOLDS.get('shoes', 0.88)
        
        # Check for ID card (Balanced: High threshold)
        if ('identity' in ln) or ('card' in ln) or (ln == 'id'):
            return self.CONF_THRESHOLDS.get('Identity Card', 0.65)
        
        # Check for upper garments (Balanced)
        if ln in ('shirt', 'tshirt', 't-shirt'):
            return self.CONF_THRESHOLDS.get('Shirt', 0.62)
        if ln == 'top':
            return self.CONF_THRESHOLDS.get('top', 0.62)
        
        # Check for lower garments (OPTIMIZED: Lower threshold for better pant detection)
        if ln in ('pant', 'pants', 'trouser', 'trousers'):
            return self.CONF_THRESHOLDS.get('pant', 0.60)
        
        return self.CONF_THRESHOLDS.get('default', 0.58)
    
    def _extract_dominant_color_hsv(self, image_region):
        """Extract dominant color from image region using HSV analysis"""
        if image_region is None or image_region.size == 0:
            return None
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image_region, cv2.COLOR_BGR2HSV)
        
        # Calculate mean HSV values
        h_mean = np.mean(hsv[:, :, 0])
        s_mean = np.mean(hsv[:, :, 1])
        v_mean = np.mean(hsv[:, :, 2])
        
        # Also get BGR for RGB analysis
        b_mean = np.mean(image_region[:, :, 0])
        g_mean = np.mean(image_region[:, :, 1])
        r_mean = np.mean(image_region[:, :, 2])
        
        return {
            'hsv': (h_mean, s_mean, v_mean),
            'rgb': (r_mean, g_mean, b_mean),
            'bgr': (b_mean, g_mean, r_mean)
        }
    
    def _detect_color_name(self, color_data):
        """Detect color name from HSV/RGB data with enhanced skin tone detection"""
        if color_data is None:
            return 'unknown'
        
        h, s, v = color_data['hsv']
        r, g, b = color_data['rgb']
        
        # ============ SKIN TONE DETECTION (PRIORITY CHECK) ============
        # Detect various skin tones that indicate bare feet
        # Skin tones typically have: hue 0-25, saturation 20-80, value 60-255
        
        # Method 1: HSV-based skin detection (yellow-orange-red range)
        if (0 <= h <= 25 or h >= 165) and (15 <= s <= 170) and (60 <= v <= 255):
            # Check if RGB values match skin pattern (R > G > B)
            if r > g and g >= b and (r - b) > 15:
                # Light skin tones (peach, beige, flesh)
                if v > 140:
                    return 'peach'
                # Medium skin tones (tan, beige)
                elif v > 100:
                    return 'tan'
                # Darker skin tones (brown, bronze)
                else:
                    return 'beige'
        
        # Method 2: RGB-based skin detection
        # Typical skin: R > 95, G > 40, B > 20, R > G > B, |R-G| > 15
        if r > 95 and g > 40 and b > 20:
            if r > g > b and (r - g) > 15:
                if v > 180:  # Very light skin
                    return 'flesh'
                elif v > 120:  # Light to medium skin
                    return 'peach'
                else:  # Medium to dark skin
                    return 'tan'
        
        # Method 3: Yellowish tones that appear in certain lighting (bare feet)
        if 20 <= h <= 40 and 20 <= s <= 100 and 100 <= v <= 220:
            if r > 150 and g > 120:  # Yellowish skin appearance
                return 'yellow'
        
        # Method 4: Orange/brown tones (darker skin or certain lighting)
        if 5 <= h <= 25 and 40 <= s <= 150 and 60 <= v <= 180:
            return 'orange'
        
        # ============ STANDARD COLOR DETECTION ============
        
        # White detection (high value, low saturation)
        if v > 150 and s < 50:
            return 'white'
        
        # Black detection (very low value)
        if v < 60:
            return 'black'
        
        # Gray detection (low saturation, medium value)
        if s < 50 and 60 <= v <= 150:
            return 'gray'
        
        # Cement color (light gray with slight warmth)
        if s < 70 and 100 <= v <= 180 and abs(r - g) < 30 and abs(g - b) < 30:
            return 'cement'
        
        # Color detection based on hue (for saturated colors)
        if s > 50:  # Only for saturated colors
            # Red: 0-10 or 160-180
            if (h < 10) or (h > 160):
                return 'red'
            # Yellow: 20-40 (excluding skin tones already detected)
            elif 20 <= h < 40:
                return 'yellow'
            # Green: 40-80
            elif 40 <= h < 80:
                return 'green'
            # Cyan: 80-100
            elif 80 <= h < 100:
                return 'cyan'
            # Blue: 100-130
            elif 100 <= h < 130:
                if v < 100:  # Dark blue = navy
                    return 'navy'
                return 'blue'
            # Violet/Purple: 130-160
            elif 130 <= h < 160:
                return 'violet'
        
        # Navy blue special detection (dark blue)
        if 100 <= h < 130 and v < 100 and s > 30:
            return 'navy'
        
        # Brown detection (for shoes)
        if 10 <= h <= 30 and 30 <= s <= 120 and 30 <= v <= 120:
            return 'brown'
        
        return 'unknown'
    
    def _validate_component_color(self, color_name, component_type, uniform_type):
        """Validate if detected color matches allowed colors for component"""
        if not self.ENABLE_COLOR_VALIDATION:
            return True, "Color validation disabled"
        
        # Shoes validation - Accept ANY color EXCEPT bare feet (skin tones)
        # With enhanced 4-method skin detection, we can safely accept all non-skin colors
        if component_type in ['shoes', 'slippers']:
            # Skin tone colors that indicate bare feet (detected by enhanced algorithm)
            skin_tone_colors = ['cement', 'peach', 'tan', 'flesh', 'beige', 'orange', 'yellow']
            
            # REJECT ONLY skin tone colors that indicate bare feet
            if color_name in skin_tone_colors:
                return False, f"Rejected shoe with skin-tone color ({color_name}) - likely bare foot"
            
            # ACCEPT ALL other colors (including unknown, since enhanced skin detection should catch bare feet)
            return True, f"Valid shoe color ({color_name})"
        
        # ID Card validation - Accept white, violet, green, red, yellow, gray
        if component_type == 'Identity Card':
            allowed_idcard_colors = ['white', 'violet', 'green', 'red', 'yellow', 'gray']
            if color_name in allowed_idcard_colors:
                return True, f"Valid ID card color ({color_name})"
            else:
                return False, f"Invalid ID card color ({color_name}), expected: white/violet/green/red/yellow/gray"
        
        # Shirt validation (Boys) - Accept pure white, white, gray, cement, green, cyan
        if component_type == 'Shirt':
            allowed_shirt_colors = ['white', 'gray', 'cement', 'green', 'cyan']
            if color_name in allowed_shirt_colors:
                return True, f"Valid shirt color ({color_name})"
            else:
                return False, f"Invalid shirt color ({color_name}), expected: white/gray/cement/green/cyan"
        
        # Top validation (Girls) - Accept pure white, white, gray, cement, green, cyan
        if component_type == 'top':
            allowed_top_colors = ['white', 'gray', 'cement', 'green', 'cyan']
            if color_name in allowed_top_colors:
                return True, f"Valid top color ({color_name})"
            else:
                return False, f"Invalid top color ({color_name}), expected: white/gray/cement/green/cyan"
        
        # Pant validation (Both) - Accept black, navy blue, dark blue
        if component_type == 'pant':
            allowed_pant_colors = ['black', 'navy', 'blue']  # black, navy blue, dark blue
            # Accept black, navy blue, dark blue
            if color_name in allowed_pant_colors:
                return True, f"Valid pant color ({color_name})"
            else:
                # REJECT ALL other colors
                return False, f"Invalid pant color ({color_name}), expected: black/navy blue/dark blue ONLY"
        
        return True, f"Color check skipped ({color_name})"
    
    def _detect_persons(self, image):
        """Detect all persons/people in the image using YOLO"""
        if self.model is None:
            return []
        
        results = self.model(image, conf=self.PERSON_CONF_THRESHOLD, verbose=False)
        persons = []
        
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    class_name = result.names[int(cls_id)]
                    # Check if this is a person/human detection
                    # In YOLO, person class is typically class 0 or has 'person' in name
                    if 'person' in class_name.lower() or int(cls_id) == 0:
                        x1, y1, x2, y2 = map(float, box)
                        persons.append({
                            'box': (x1, y1, x2, y2),
                            'center': ((x1 + x2) / 2, (y1 + y2) / 2),
                            'confidence': float(conf),
                            'uniform_items': []
                        })
        
        return persons
    
    def _get_item_center(self, box):
        """Get center point of detected item bounding box"""
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _distance_between_points(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def _assign_items_to_persons(self, items_with_boxes, persons):
        """Assign detected uniform items to nearest person"""
        if not persons or not items_with_boxes:
            return persons
        
        for item_data in items_with_boxes:
            item_center = self._get_item_center(item_data['box'])
            
            # Find closest person
            closest_person_idx = 0
            min_distance = float('inf')
            
            for idx, person in enumerate(persons):
                distance = self._distance_between_points(item_center, person['center'])
                if distance < min_distance:
                    min_distance = distance
                    closest_person_idx = idx
            
            # Assign item to closest person if within max distance
            if min_distance <= self.MAX_DISTANCE_TO_PERSON:
                persons[closest_person_idx]['uniform_items'].append(item_data)
        
        return persons
    
    def _analyze_person_uniform(self, items, person_id, image, verbose=True):
        """Analyze uniform for a single person"""
        detections = defaultdict(int)
        detected_classes = []
        color_validation_results = {}
        
        # Process items assigned to this person
        for item in items:
            class_name = item['class_name']
            confidence = item['confidence']
            box = item['box']
            
            # Get specific threshold for this item
            item_threshold = self._get_confidence_threshold(class_name)
            
            if confidence >= item_threshold:
                # Extract region for color analysis
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
                
                region = image[y1:y2, x1:x2]
                
                # Perform color detection
                color_data = self._extract_dominant_color_hsv(region)
                color_name = self._detect_color_name(color_data)
                
                # Validate color
                normalized_class = self._normalize_class_name(class_name)
                color_valid, color_msg = self._validate_component_color(color_name, normalized_class, 'UNKNOWN')
                
                if color_valid:
                    detected_classes.append(class_name)
                    detections[class_name] += 1
                    color_validation_results[class_name] = {
                        'color': color_name,
                        'valid': True,
                        'message': color_msg
                    }
                    if verbose:
                        print(f"    Student {person_id}: ✓ {class_name} (conf: {confidence:.2f}) [color: {color_name}]")
                else:
                    color_validation_results[class_name] = {
                        'color': color_name,
                        'valid': False,
                        'message': color_msg
                    }
                    if verbose:
                        print(f"    Student {person_id}: ✗ {class_name} - Invalid color ({color_name})")
        
        # Normalize detections
        normalized_detections, normalized_counts = self._normalize_detections(detected_classes, dict(detections))
        
        # Check for complete uniform
        is_complete, missing_items, uniform_type = self._check_complete_uniform(normalized_detections, normalized_counts)
        
        return {
            'person_id': person_id,
            'uniform_status': 1 if is_complete else 0,
            'is_complete': is_complete,
            'uniform_type': uniform_type,
            'detected_items': list(normalized_detections),
            'missing_items': missing_items,
            'color_validation': color_validation_results,
            'message': self._generate_message(is_complete, missing_items, uniform_type)
        }

    def _normalize_class_name(self, class_name):
        """Normalize a single class name to standard format."""
        ln = class_name.lower().strip()

        if ('identity' in ln) or ('card' in ln) or (ln == 'id') or (ln == 'id card') or (ln == 'idcard'):
            return 'Identity Card'
        if ln in ('shirt', 'tshirt', 't-shirt'):
            return 'Shirt'
        if ln == 'top':
            return 'top'
        if ln in ('pant', 'pants', 'trouser', 'trousers'):
            return 'pant'
        if ln in ('shoes', 'shoe'):
            return 'shoes'
        if ln in ('slippers', 'sandal', 'sandals'):
            return 'slippers'

        return class_name
    
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
            ln = raw_name.lower().strip()

            # Normalize identity card variations
            if ('identity' in ln) or ('card' in ln) or (ln == 'id') or (ln == 'id card') or (ln == 'idcard'):
                normalized.add('Identity Card')
                counts['Identity Card'] += cnt
                continue

            # Normalize upper-body garments (treat common forms)
            if ln in ('shirt', 'tshirt', 't-shirt'):
                normalized.add('Shirt')
                counts['Shirt'] += cnt
                continue
            if ln == 'top':
                normalized.add('top')
                counts['top'] += cnt
                continue

            # Normalize lower-body garments
            if ln in ('pant', 'pants', 'trouser', 'trousers'):
                normalized.add('pant')
                counts['pant'] += cnt
                continue

            # Normalize footwear
            if ln in ('shoes', 'shoe'):
                normalized.add('shoes')
                counts['shoes'] += cnt
                continue
            if ln in ('slippers', 'sandal', 'sandals'):
                normalized.add('slippers')
                counts['slippers'] += cnt
                continue

        return normalized, counts
    
    def _check_complete_uniform(self, detections, counts=None):
        """
        Check if detected items form a complete uniform
        Returns: (is_complete, missing_items, uniform_type)
        """
        # Decide likely uniform type first
        top_present = 'top' in detections
        shirt_present = 'Shirt' in detections
        upper_present = top_present or shirt_present

        if top_present and not shirt_present:
            likely_type = 'GIRLS'
        elif shirt_present and not top_present:
            likely_type = 'BOYS'
        else:
            # Use counts to break ties when both or none are present
            if counts is not None:
                top_count = int(counts.get('top', 0))
                shirt_count = int(counts.get('Shirt', 0))
                if top_count > shirt_count:
                    likely_type = 'GIRLS'
                elif shirt_count > top_count:
                    likely_type = 'BOYS'
                else:
                    likely_type = 'BOYS'  # default
            else:
                likely_type = 'BOYS'  # default

        # Check completeness using interchangeable upper garment rule
        base_required = {'Identity Card', 'pant', 'shoes'}
        base_missing = list(base_required - detections)

        is_complete = (len(base_missing) == 0) and upper_present

        # Build missing list reflecting chosen type
        missing_items = base_missing.copy()
        if not upper_present:
            missing_items.append('top' if likely_type == 'GIRLS' else 'Shirt')

        return (True, missing_items, likely_type) if is_complete else (False, missing_items, f"{likely_type} (incomplete)")
    
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
        print("⏱️  Processing 1 frame every 3 seconds...\n")
        
        # Get FPS to calculate frames for 3 seconds
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30  # Default to 30 FPS if unable to detect
        
        frames_per_detection = int(fps * 3)  # Process 1 frame every 3 seconds
        
        frame_count = 0  # Actual frame counter
        detection_count = 0  # Sequential detection frame counter
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                frame_count += 1
                
                # Run detection every 3 seconds (based on FPS)
                if frame_count % frames_per_detection == 0:
                    detection_count += 1  # Increment sequential frame number
                    # Detect WITHOUT full-body requirement (detect always)
                    result = self.detect_uniform(frame, require_full_body=False)
                    
                    # Display result on frame
                    status = result['uniform_status']
                    message = result['message']
                    
                    # Color based on status
                    color = (0, 255, 0) if status == 1 else (0, 0, 255) if status == 0 else (0, 165, 255)
                    
                    # Add text to frame
                    cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, color, 2)
                    cv2.putText(frame, f"Status: {status}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                               1, color, 2)
                    
                    # Print to console
                    print(f"\nFrame {detection_count}: {message}")
                    print(f"Detected: {result['detected_items']}")
                    # Terminal Output flag: 1 for complete, 0 otherwise
                    flag = 1 if status == 1 else 0
                    print(f"Terminal Output: {flag}")
                    # Send flag to Arduino
                    self._send_flag(status)
                
                if display:
                    cv2.imshow('Uniform Detection', frame)
                    
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
        
        frame_count = 0  # Actual frame counter
        detection_count = 0  # Sequential detection frame counter
        frames_per_detection = int(fps * 3)  # Process 1 frame every 3 seconds
        
        print(f"📹 Processing video: {video_path}")
        print(f"⏱️  Processing 1 frame every 3 seconds (FPS: {fps})...\n")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Detect every 3 seconds
            if frame_count % frames_per_detection == 0:
                detection_count += 1  # Increment sequential frame number
                result = self.detect_uniform(frame)
                status = result['uniform_status']
                message = result['message']
                color = (0, 255, 0) if status == 1 else (0, 0, 255)
                
                cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, color, 2)
                
                print(f"\nFrame {detection_count}: {message}")
                print(f"Detected: {result['detected_items']}")
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
    parser.add_argument("--single-student", action="store_true", help="Use single-student detection mode (default: multi-student)")
    args = parser.parse_args()

    detector = UniformDetector(model_path=args.model, serial_port=args.serial_port, baud=args.baud, enable_serial=(not args.no_serial))
    
    print("\n" + "=" * 80)
    print("UNIFORM DETECTION SYSTEM (Laptop Webcam)")
    print("=" * 80)
    print(f"Model: {args.model}")
    print(f"Camera ID: {args.camera}")
    print(f"Mode: {'SINGLE STUDENT' if args.single_student else 'MULTI-STUDENT (Multiple students per frame)'}")
    
    # Webcam detection
    detector.detect_from_webcam(camera_id=args.camera, multi_student=(not args.single_student))
    
    # Optional: quick test with an image if present
    test_image = "test_uniform.jpg"
    if os.path.exists(test_image):
        result = detector.detect_uniform(test_image)
        print(f"\nImage Result -> Status: {result['uniform_status']} | {result['message']}")


if __name__ == "__main__":
    main()
