"""
Test script for multi-student uniform detection
Run this to test detecting multiple students in one frame
"""
from uniform_detector_system import UniformDetector
import cv2
import os

# Initialize detector
print("Initializing detector...")
detector = UniformDetector()

print("\n" + "="*80)
print("MULTI-STUDENT UNIFORM DETECTION TEST")
print("="*80)

# Test with webcam - MULTI-STUDENT MODE
print("\n📷 Starting webcam detection in MULTI-STUDENT mode...")
print("This will detect multiple students in one frame and show individual status")
print("Press 'q' to quit, 'c' to capture...\n")

detector.detect_from_webcam(camera_id=0, display=True, multi_student=True)
