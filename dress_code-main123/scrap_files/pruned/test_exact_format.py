#!/usr/bin/env python3
"""
FINAL TEST SCRIPT - EXACT OUTPUT FORMAT VERIFICATION

Run this to test the exact output format you requested
"""

from uniform_detector_system import UniformDetector
import cv2
import time

def main():
    print("\n" + "="*80)
    print("MULTI-STUDENT DETECTION - EXACT OUTPUT FORMAT")
    print("="*80)
    print("\nThis script shows output in the exact format you requested:")
    print("\nFrame X:")
    print("Student 1= [status]")
    print("Detected: [items]")
    print("Terminal Output: [0/1]")
    print("\nStudent 2= [status]")
    print("Detected: [items]")
    print("Terminal Output: [0/1]")
    print("\n(and so on for each student...)\n")
    
    print("="*80)
    print("Initializing detector...")
    
    detector = UniformDetector()
    
    if detector.model is None:
        print("❌ Model failed to load")
        return
    
    print("✅ Model loaded successfully!\n")
    print("="*80)
    print("Starting webcam detection...")
    print("Place 2-4 students in front of camera")
    print("Press 'q' to quit\n")
    print("="*80 + "\n")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    frame_num = 0
    detection_num = 0
    last_print_time = time.time()  # Track when last print happened
    print_interval = 3  # Print every 3 seconds
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_num += 1
            
            # Run detection on every frame (quiet), but only print every 3s
            result = detector.detect_uniform_multi_student(frame, verbose=False)
            
            # Print results only every 3 seconds
            current_time = time.time()
            if current_time - last_print_time >= print_interval:
                last_print_time = current_time
                detection_num += 1
                
                print(f"Frame {detection_num}:")
                print("-" * 80)
                
                # Print in exact format: Student X= [status]
                if result['students']:
                    for student in result['students']:
                        emoji = "✅" if student['is_complete'] else "❌"
                        student_num = student['person_id']
                        message = student['message']
                        
                        # Exact format as requested
                        print(f"\nStudent {student_num}= {emoji} {message}")
                        
                        # Detected items
                        detected = student.get('detected_items', [])
                        print(f"Detected: {detected if detected else '[]'}")
                        
                        # Terminal output
                        print(f"Terminal Output: {student['uniform_status']}")
                else:
                    print("No students detected")
                
                print("-" * 80 + "\n")
            
            # Show on screen; keep UI responsive (no forced delay)
            cv2.imshow('Multi-Student Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Detection stopped")

if __name__ == "__main__":
    main()
