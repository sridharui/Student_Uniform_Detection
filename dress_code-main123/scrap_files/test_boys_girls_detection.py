"""
Test Script for Boys and Girls Uniform Detection
Compare detection accuracy between genders
"""

import os
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict
from uniform_detector_system import UniformDetector

def test_single_image(detector, image_path, expected_gender=None):
    """Test detection on a single image"""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\nTesting: {Path(image_path).name}")
    print("-" * 60)
    
    image = cv2.imread(image_path)
    result = detector.detect_uniform(image)
    
    print(f"Expected Gender: {expected_gender if expected_gender else 'Unknown'}")
    print(f"Detected Gender: {result.get('detected_gender', 'UNKNOWN')}")
    print(f"Status: {'✅ COMPLETE' if result['is_complete'] else '❌ INCOMPLETE'}")
    print(f"Type: {result.get('uniform_type', 'Unknown')}")
    print(f"Detected Items: {result.get('detected_items', [])}")
    print(f"Missing Items: {result.get('missing_items', [])}")
    print(f"Message: {result['message']}")
    
    detection_details = result.get('detection_details', [])
    if detection_details:
        print(f"\nDetection Details:")
        for detail in detection_details:
            print(f"  • {detail['class']}: {detail['confidence']:.2f}")
    
    return result

def compare_boys_vs_girls(detector, boys_images=None, girls_images=None):
    """Compare detection accuracy between boys and girls uniforms"""
    print("\n" + "=" * 80)
    print("BOYS vs GIRLS UNIFORM DETECTION COMPARISON")
    print("=" * 80)
    
    # Default test directories
    if boys_images is None:
        boys_images = []
        girls_images = []
    
    boys_stats = {
        'total_tested': 0,
        'correctly_identified': 0,
        'missing_shirt': 0,
        'missing_id': 0,
        'missing_pant': 0,
        'missing_shoes': 0,
    }
    
    girls_stats = {
        'total_tested': 0,
        'correctly_identified': 0,
        'missing_top': 0,
        'missing_id': 0,
        'missing_pant': 0,
        'missing_shoes': 0,
    }
    
    print("\n" + "-" * 80)
    print("BOYS UNIFORM DETECTION")
    print("-" * 80)
    
    for img_path in boys_images:
        if not os.path.exists(img_path):
            continue
        
        boys_stats['total_tested'] += 1
        result = test_single_image(detector, img_path, expected_gender="BOYS")
        
        if result:
            detected_gender = result.get('detected_gender', 'UNKNOWN')
            if detected_gender == 'BOYS':
                boys_stats['correctly_identified'] += 1
            
            missing = result.get('missing_items', [])
            if 'Shirt' in missing:
                boys_stats['missing_shirt'] += 1
            if 'Identity Card' in missing:
                boys_stats['missing_id'] += 1
            if 'pant' in missing:
                boys_stats['missing_pant'] += 1
            if 'shoes' in missing:
                boys_stats['missing_shoes'] += 1
    
    print("\n" + "-" * 80)
    print("GIRLS UNIFORM DETECTION")
    print("-" * 80)
    
    for img_path in girls_images:
        if not os.path.exists(img_path):
            continue
        
        girls_stats['total_tested'] += 1
        result = test_single_image(detector, img_path, expected_gender="GIRLS")
        
        if result:
            detected_gender = result.get('detected_gender', 'UNKNOWN')
            if detected_gender == 'GIRLS':
                girls_stats['correctly_identified'] += 1
            
            missing = result.get('missing_items', [])
            if 'top' in missing:
                girls_stats['missing_top'] += 1
            if 'Identity Card' in missing:
                girls_stats['missing_id'] += 1
            if 'pant' in missing:
                girls_stats['missing_pant'] += 1
            if 'shoes' in missing:
                girls_stats['missing_shoes'] += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("DETECTION ACCURACY SUMMARY")
    print("=" * 80)
    
    print("\nBOYS UNIFORM DETECTION RESULTS:")
    if boys_stats['total_tested'] > 0:
        accuracy = (boys_stats['correctly_identified'] / boys_stats['total_tested']) * 100
        print(f"  Total Tested: {boys_stats['total_tested']}")
        print(f"  Correctly Identified as BOYS: {boys_stats['correctly_identified']} ({accuracy:.1f}%)")
        print(f"  Missing Shirt: {boys_stats['missing_shirt']}")
        print(f"  Missing ID Card: {boys_stats['missing_id']}")
        print(f"  Missing Pant: {boys_stats['missing_pant']}")
        print(f"  Missing Shoes: {boys_stats['missing_shoes']}")
    else:
        print("  No test images provided")
    
    print("\nGIRLS UNIFORM DETECTION RESULTS:")
    if girls_stats['total_tested'] > 0:
        accuracy = (girls_stats['correctly_identified'] / girls_stats['total_tested']) * 100
        print(f"  Total Tested: {girls_stats['total_tested']}")
        print(f"  Correctly Identified as GIRLS: {girls_stats['correctly_identified']} ({accuracy:.1f}%)")
        print(f"  Missing Top: {girls_stats['missing_top']}")
        print(f"  Missing ID Card: {girls_stats['missing_id']}")
        print(f"  Missing Pant: {girls_stats['missing_pant']}")
        print(f"  Missing Shoes: {girls_stats['missing_shoes']}")
    else:
        print("  No test images provided")
    
    print("\n" + "=" * 80)

def analyze_validation_set(detector):
    """Analyze validation set performance by gender"""
    print("\n" + "=" * 80)
    print("VALIDATION SET ANALYSIS")
    print("=" * 80)
    
    val_dir = "scrap_files/Complete_Uniform.v3i.yolov12/valid/images"
    
    if not os.path.exists(val_dir):
        print(f"⚠️  Validation directory not found: {val_dir}")
        return
    
    test_images = [f for f in os.listdir(val_dir) if f.endswith(('.jpg', '.png'))]
    
    print(f"\nTesting {len(test_images)} validation images...")
    print("-" * 80)
    
    gender_stats = defaultdict(lambda: {
        'total': 0,
        'complete': 0,
        'incomplete': 0,
        'shirt_only': 0,
        'top_only': 0,
        'both_detected': 0
    })
    
    for i, img_file in enumerate(test_images[:20]):  # Test first 20
        img_path = os.path.join(val_dir, img_file)
        result = detector.detect_uniform(img_path)
        
        detected_gender = result.get('detected_gender', 'UNKNOWN')
        detected_items = result.get('detected_items', [])
        is_complete = result.get('is_complete', False)
        
        gender_stats[detected_gender]['total'] += 1
        
        if is_complete:
            gender_stats[detected_gender]['complete'] += 1
        else:
            gender_stats[detected_gender]['incomplete'] += 1
        
        if 'Shirt' in detected_items:
            gender_stats[detected_gender]['shirt_only'] += 1
        if 'top' in detected_items:
            gender_stats[detected_gender]['top_only'] += 1
        if 'Shirt' in detected_items and 'top' in detected_items:
            gender_stats[detected_gender]['both_detected'] += 1
        
        status = "✅" if is_complete else "❌"
        print(f"  {status} {img_file:30s} → {detected_gender:10s} | {', '.join(detected_items)}")
    
    print("\n" + "-" * 80)
    print("VALIDATION RESULTS BY GENDER:")
    print("-" * 80)
    
    for gender in ['BOYS', 'GIRLS', 'UNKNOWN']:
        stats = gender_stats[gender]
        if stats['total'] > 0:
            complete_pct = (stats['complete'] / stats['total']) * 100
            print(f"\n{gender}:")
            print(f"  Total Detections: {stats['total']}")
            print(f"  Complete Uniforms: {stats['complete']} ({complete_pct:.1f}%)")
            print(f"  Incomplete: {stats['incomplete']}")
            print(f"  With Shirt: {stats['shirt_only']}")
            print(f"  With Top: {stats['top_only']}")
            print(f"  Both Shirt & Top: {stats['both_detected']} ⚠️ (should be 0)")
    
    print("\n" + "=" * 80)

def main():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "UNIFORM DETECTOR - BOYS & GIRLS TEST".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    # Initialize detector
    print("Initializing detector...")
    detector = UniformDetector()
    
    if detector.model is None:
        print("❌ Failed to load model. Please check the model path.")
        return
    
    print("✅ Detector initialized successfully")
    
    # Test on validation set
    analyze_validation_set(detector)
    
    # Instructions for custom testing
    print("\n" + "=" * 80)
    print("HOW TO USE THIS TEST SCRIPT")
    print("=" * 80)
    print("""
To test specific images:

1. Place boy's uniform images in a directory
2. Place girl's uniform images in another directory
3. Modify main() to call compare_boys_vs_girls() with your image paths:
   
   boys_images = ['path/to/boy1.jpg', 'path/to/boy2.jpg', ...]
   girls_images = ['path/to/girl1.jpg', 'path/to/girl2.jpg', ...]
   compare_boys_vs_girls(detector, boys_images, girls_images)

4. Or test a single image:
   
   result = test_single_image(detector, 'path/to/image.jpg', expected_gender='BOYS')

Current Test Results Summary:
- Detection accuracy for BOYS (Shirt-based detection)
- Detection accuracy for GIRLS (Top-based detection)
- Ambiguous detections (both Shirt and Top detected)
""")
    
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
