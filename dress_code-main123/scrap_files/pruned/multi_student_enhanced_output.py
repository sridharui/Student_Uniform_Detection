#!/usr/bin/env python3
"""
ENHANCED MULTI-STUDENT DETECTION WITH EXACT OUTPUT FORMAT
Shows Student 1=, Student 2=, etc. with complete details per frame
"""

from uniform_detector_system import UniformDetector
import cv2

def print_frame_results(frame_num, results):
    """Print results in the exact format requested"""
    print(f"\n{'='*80}")
    print(f"Frame {frame_num}:")
    print(f"{'='*80}")
    
    if not results['students']:
        print("No students detected in frame")
        return
    
    # Print each student's results
    for student in results['students']:
        person_id = student['person_id']
        status_emoji = "✅" if student['is_complete'] else "❌"
        message = student['message']
        
        # Format: Student X= [emoji] [message]
        print(f"\nStudent {person_id}= {status_emoji} {message}")
        
        # Show detected items
        if student['detected_items']:
            print(f"Detected: {student['detected_items']}")
        else:
            print(f"Detected: []")
        
        # Show confidence scores for each detected item
        if student.get('color_validation'):
            for item_name, validation_info in student['color_validation'].items():
                color_info = f" [{validation_info.get('color', 'unknown')}]" if validation_info.get('valid') else ""
                print(f"  ✓ Detected: {item_name} (confidence: varies){color_info}")
        
        # Terminal output flag
        print(f"Terminal Output: {student['uniform_status']}")
    
    # Print frame summary
    total = len(results['students'])
    complete = sum(1 for s in results['students'] if s['is_complete'])
    print(f"\n{'-'*80}")
    print(f"Frame {frame_num} Summary: {complete}/{total} students have complete uniforms")
    print(f"{'='*80}")

def main():
    print("\n" + "="*80)
    print("MULTI-STUDENT UNIFORM DETECTION - ENHANCED OUTPUT FORMAT")
    print("="*80)
    
    # Initialize detector
    detector = UniformDetector()
    
    if detector.model is None:
        print("❌ Model failed to load")
        return
    
    print("✅ Model loaded successfully")
    print("\n📷 Starting webcam detection...")
    print("   - Shows: Student 1=, Student 2=, etc. per frame")
    print("   - Press 'q' to quit\n")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera")
        return
    
    frame_count = 0
    detection_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Run detection every 5 frames
            if frame_count % 5 == 0:
                detection_count += 1
                
                # Run multi-student detection
                result = detector.detect_uniform_multi_student(frame)
                
                # Print in requested format
                print_frame_results(detection_count, result)
            
            # Display on screen
            cv2.imshow('Multi-Student Uniform Detection', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n📷 Webcam detection stopped")

if __name__ == "__main__":
    main()
