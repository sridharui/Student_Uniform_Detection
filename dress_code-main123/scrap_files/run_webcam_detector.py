#!/usr/bin/env python3
"""
Quick start script for uniform detection with laptop webcam
Run this script directly: python run_webcam_detector.py
"""
import sys
import os

# Ensure we're in the SDRS directory for relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sdrs_dir = os.path.join(script_dir, "SDRS")
os.chdir(sdrs_dir)

# Now import and run
from uniform_detector_system import UniformDetector

if __name__ == "__main__":
    # Model path - will use v12 cpu model
    model_path = "runs/train/uniform_detector_yolov12_cpu/weights/best.pt"
    
    print("\n" + "=" * 80)
    print("🎥 UNIFORM DETECTION - LAPTOP WEBCAM")
    print("=" * 80)
    print("Press 'q' to quit the camera feed")
    print("=" * 80 + "\n")
    
    # Create detector and start webcam
    detector = UniformDetector(
        model_path=model_path,
        enable_serial=False  # Disable serial output
    )
    
    # Start webcam detection
    detector.detect_from_webcam(camera_id=0)
