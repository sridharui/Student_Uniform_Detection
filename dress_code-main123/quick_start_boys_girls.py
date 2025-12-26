"""
Quick Start Script - Test Boys and Girls Uniform Detection
Run this to see immediate results and understand the system
"""

import os
import cv2
from uniform_detector_system import UniformDetector

def print_header():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "UNIFORM DETECTOR - QUICK START (BOYS & GIRLS)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")

def print_instructions():
    print("=" * 80)
    print("HOW TO USE THIS SYSTEM")
    print("=" * 80)
    print("""
This system detects if students are wearing complete uniform for both boys and girls.

BOYS UNIFORM = ID Card + Shirt + Pant + Shoes
GIRLS UNIFORM = ID Card + Top + Pant + Shoes

Options:
1. Test with Webcam (real-time detection)
2. Test with Image File (single image)
3. Analyze Dataset (recommendations for improvement)
4. Run Detailed Tests (accuracy comparison)
5. Exit
""")

def run_webcam():
    print("\n" + "=" * 80)
    print("STARTING WEBCAM DETECTION")
    print("=" * 80)
    print("""
Instructions:
- Position yourself in front of the camera
- The system will automatically detect your gender based on clothing
- You'll see real-time feedback on detection accuracy
- Press 'Q' to quit
- Press 'C' to capture a frame
""")
    
    detector = UniformDetector()
    if detector.model is None:
        print("❌ Model not loaded. Please check your setup.")
        return
    
    detector.detect_from_webcam(camera_id=0, display=True)

def test_image():
    print("\n" + "=" * 80)
    print("TEST WITH IMAGE FILE")
    print("=" * 80)
    
    image_path = input("\nEnter image path: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return
    
    detector = UniformDetector()
    if detector.model is None:
        print("❌ Model not loaded.")
        return
    
    print("\nAnalyzing image...")
    result = detector.detect_uniform(image_path)
    
    print("\n" + "-" * 80)
    print("DETECTION RESULTS")
    print("-" * 80)
    print(f"\n✓ Gender Detected: {result.get('detected_gender', 'UNKNOWN')}")
    print(f"✓ Status: {'COMPLETE' if result['is_complete'] else 'INCOMPLETE'}")
    print(f"✓ Type: {result['uniform_type']}")
    print(f"\nDetected Items:")
    for item in result.get('detected_items', []):
        print(f"  ✓ {item}")
    
    if result.get('missing_items'):
        print(f"\nMissing Items:")
        for item in result.get('missing_items', []):
            print(f"  ✗ {item}")
    
    print(f"\nMessage: {result['message']}")
    
    if result.get('detection_details'):
        print(f"\nConfidence Scores:")
        for detail in result['detection_details']:
            print(f"  • {detail['class']}: {detail['confidence']:.2%}")

def analyze_dataset():
    print("\n" + "=" * 80)
    print("ANALYZING DATASET FOR IMPROVEMENT RECOMMENDATIONS")
    print("=" * 80)
    
    try:
        from improve_gender_detection import (
            analyze_dataset as analyze_fn,
            test_model_accuracy,
            suggest_training_command
        )
        
        analyze_fn()
        test_model_accuracy()
        suggest_training_command()
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        print("Make sure improve_gender_detection.py is in the same directory")

def run_detailed_tests():
    print("\n" + "=" * 80)
    print("RUNNING DETAILED BOYS VS GIRLS ACCURACY TESTS")
    print("=" * 80)
    
    try:
        from test_boys_girls_detection import (
            analyze_validation_set
        )
        
        print("\nInitializing detector...")
        detector = UniformDetector()
        
        if detector.model is None:
            print("❌ Model not loaded.")
            return
        
        analyze_validation_set(detector)
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        print("Make sure test_boys_girls_detection.py is in the same directory")

def main():
    print_header()
    
    while True:
        print_instructions()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            run_webcam()
        elif choice == '2':
            test_image()
        elif choice == '3':
            analyze_dataset()
        elif choice == '4':
            run_detailed_tests()
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
