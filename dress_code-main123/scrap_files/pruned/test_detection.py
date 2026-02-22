"""Test uniform detection on sample images"""
from uniform_detector_system import UniformDetector
import cv2
import os

# Initialize detector
detector = UniformDetector()

# Test images
test_images = [
    "scrap_files/uploads/20251215_064743_20251203_191212_Complete_Uniform7.jpeg",
    "scrap_files/uploads/20251215_060325_20251203_191315_No_Uniform8.jpeg",
]

print("\n" + "="*80)
print("TESTING UNIFORM DETECTION ON SAMPLE IMAGES")
print("="*80)

for img_path in test_images:
    if not os.path.exists(img_path):
        print(f"\n❌ Image not found: {img_path}")
        continue
    
    print(f"\n📸 Testing: {os.path.basename(img_path)}")
    print("-" * 80)
    
    # Run detection
    result = detector.detect_uniform(img_path)
    
    # Display results
    print(f"Status: {result['uniform_status']}")
    print(f"Message: {result['message']}")
    print(f"Type: {result['uniform_type']}")
    print(f"Detected Items: {result['detected_items']}")
    if result['missing_items']:
        print(f"Missing Items: {result['missing_items']}")
    
    # Save result image
    output_path = f"test_result_{os.path.basename(img_path)}"
    cv2.imwrite(output_path, result['image'])
    print(f"✅ Saved result to: {output_path}")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
