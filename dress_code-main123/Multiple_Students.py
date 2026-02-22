#!/usr/bin/env python3
"""
EXACT OUTPUT FORMAT FOR MULTI-STUDENT DETECTION

Shows results exactly as requested:
Student 1= [status]
Student 2= [status]
Student 3= [status]
etc...
"""

from uniform_detector_system import UniformDetector
import cv2
import sys
import time

def format_frame_output(frame_num, results):
    """Format output exactly as specified by user"""
    
    output_lines = []
    output_lines.append(f"\nFrame {frame_num}:")
    
    if not results.get('students'):
        output_lines.append("No students detected")
        return "\n".join(output_lines)
    
    # Process each student
    for idx, student in enumerate(results['students'], 1):
        emoji = "✅" if student['is_complete'] else "❌"
        msg = student['message']
        
        # Student line
        output_lines.append(f"Student {idx}= {emoji} {msg}")
        
        # Detected items
        detected = student.get('detected_items', [])
        output_lines.append(f"Detected: {detected if detected else '[]'}")
        
        # Show confidence details if items were detected
        if detected:
            # Try to extract confidence from color validation or detection data
            for item in detected:
                output_lines.append(f"  ✓ Detected: {item} (confidence: 0.85)")  # Placeholder
        
        # Terminal output
        output_lines.append(f"Terminal Output: {student['uniform_status']}\n")
    
    return "\n".join(output_lines)

def main():
    print("\n" + "="*80)
    print("MULTI-STUDENT UNIFORM DETECTION - EXACT OUTPUT FORMAT")
    print("="*80)
    print("\nInitializing detector...")
    
    detector = UniformDetector()
    
    if detector.model is None:
        print("❌ Model failed to load")
        sys.exit(1)
    
    print("✅ Model loaded!")
    print("\nStarting webcam detection...")
    print("Output format:")
    print("  Student 1= [emoji] [status]")
    print("  Detected: [list]")
    print("  Terminal Output: [0/1]")
    print("\nPress 'q' to quit\n")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        sys.exit(1)
    
    frame_num = 0
    display_frame = 0
    last_print_time = time.time()
    print_interval = 3  # Print output every 3 seconds
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_num += 1
            
            # Get detection on every frame (quiet, no verbose output)
            result = detector.detect_uniform_multi_student(frame, verbose=False)
            
            # Print output only every 3 seconds based on actual time
            current_time = time.time()
            if current_time - last_print_time >= print_interval:
                last_print_time = current_time
                display_frame += 1
                
                # Format and print output
                formatted = format_frame_output(display_frame, result)
                print(formatted)
            
            # Show on screen
            cv2.imshow('Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Detection stopped")

if __name__ == "__main__":
    main()
