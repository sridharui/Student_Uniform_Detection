from uniform_detector_system import UniformDetector
import numpy as np

# Create detector without serial
det = UniformDetector(model_path="runs/train/uniform_detector_yolov11_cpu/weights/best.pt", enable_serial=False)

# Create a blank image (height 480, width 640)
img = np.zeros((480, 640, 3), dtype=np.uint8)

result = det.detect_uniform(img)
print("Message:", result.get('message'))
print("Status:", result.get('uniform_status'))
print("Detected items:", result.get('detected_items'))
print("Raw detections:", result.get('raw_detections'))
