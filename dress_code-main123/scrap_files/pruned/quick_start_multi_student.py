#!/usr/bin/env python3
"""
QUICK START: Multi-Student Uniform Detection

This script shows how to use the new multi-student detection feature.
"""

from uniform_detector_system import UniformDetector
import cv2

def main():
    print("\n" + "="*80)
    print("MULTI-STUDENT UNIFORM DETECTION - QUICK START")
    print("="*80)
    
    # Initialize the detector
    print("\n1️⃣ Initializing detector...")
    detector = UniformDetector()
    
    if detector.model is None:
        print("❌ Model failed to load. Please check model path.")
        return
    
    print("✅ Model loaded successfully!")
    
    # Show available modes
    print("\n2️⃣ Available Modes:")
    print("   a) Real-time Webcam (Multiple Students) - Default")
    print("   b) Single Student Mode")
    print("   c) Test with Image")
    
    choice = input("\nSelect mode (a/b/c): ").strip().lower()
    
    if choice == 'a' or choice == '':
        print("\n📷 Starting MULTI-STUDENT webcam detection...")
        print("   - Press 'q' to quit")
        print("   - Press 'c' to capture frame")
        print("   - Shows per-student uniform status")
        detector.detect_from_webcam(camera_id=0, display=True, multi_student=True)
    
    elif choice == 'b':
        print("\n📷 Starting SINGLE STUDENT webcam detection...")
        print("   - Press 'q' to quit")
        print("   - Press 'c' to capture frame")
        detector.detect_from_webcam(camera_id=0, display=True, multi_student=False)
    
    elif choice == 'c':
        image_path = input("\nEnter image path: ").strip()
        if image_path:
            print(f"\n🖼️  Analyzing: {image_path}")
            result = detector.detect_uniform_multi_student(image_path)
            
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            print(f"Summary: {result['message']}")
            print(f"\nDetailed Results:")
            for student in result['students']:
                print(f"\n  Student {student['person_id']}:")
                print(f"    Type: {student['uniform_type']}")
                print(f"    Status: {'✅ COMPLETE' if student['is_complete'] else '❌ INCOMPLETE'}")
                print(f"    Output: {student['uniform_status']}")
                print(f"    Detected: {student['detected_items']}")
                if student['missing_items']:
                    print(f"    Missing: {student['missing_items']}")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
