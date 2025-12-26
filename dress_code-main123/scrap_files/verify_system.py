#!/usr/bin/env python3
"""
Verification Script - Ensure Boys & Girls Detection System Works
Run this to verify everything is set up correctly
"""

import os
import sys
from pathlib import Path

def print_banner():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "UNIFORM DETECTOR - SYSTEM VERIFICATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"  ✅ {description}: {filepath}")
        return True
    else:
        print(f"  ❌ {description}: {filepath} (NOT FOUND)")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"  ✅ {description} (installed)")
        return True
    except ImportError:
        print(f"  ❌ {description} (NOT installed)")
        return False

def verify_core_system():
    """Verify core detection system"""
    print("\n" + "-" * 80)
    print("1. CORE SYSTEM FILES")
    print("-" * 80)
    
    checks = [
        ("uniform_detector_system.py", "Main detection system"),
        ("quick_start_boys_girls.py", "Quick start interface"),
        ("improve_gender_detection.py", "Dataset analysis tool"),
        ("test_boys_girls_detection.py", "Testing framework"),
    ]
    
    all_ok = True
    for filepath, desc in checks:
        if not check_file_exists(filepath, desc):
            all_ok = False
    
    return all_ok

def verify_documentation():
    """Verify documentation files"""
    print("\n" + "-" * 80)
    print("2. DOCUMENTATION FILES")
    print("-" * 80)
    
    checks = [
        ("BOYS_GIRLS_DETECTION_GUIDE.md", "Complete guide"),
        ("IMPLEMENTATION_SUMMARY.md", "Technical summary"),
        ("QUICK_REFERENCE.md", "Quick reference"),
        ("IMPLEMENTATION_COMPLETE.md", "Implementation overview"),
    ]
    
    all_ok = True
    for filepath, desc in checks:
        if not check_file_exists(filepath, desc):
            all_ok = False
    
    return all_ok

def verify_dependencies():
    """Verify required Python packages"""
    print("\n" + "-" * 80)
    print("3. PYTHON DEPENDENCIES")
    print("-" * 80)
    
    dependencies = [
        ("cv2", "OpenCV (opencv-python)"),
        ("ultralytics", "YOLO (ultralytics)"),
        ("numpy", "NumPy"),
        ("torch", "PyTorch"),
    ]
    
    all_ok = True
    for module, desc in dependencies:
        if not check_import(module, desc):
            all_ok = False
    
    return all_ok

def verify_model_availability():
    """Check if model weights are available"""
    print("\n" + "-" * 80)
    print("4. MODEL WEIGHTS")
    print("-" * 80)
    
    model_paths = [
        "runs/train/uniform_detector_yolov11_cpu/weights/best.pt",
        "runs/train/uniform_detector_yolov12_cpu/weights/best.pt",
        "yolo11n.pt",
        "yolov8m.pt",
    ]
    
    found_model = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"  ✅ Model found: {model_path}")
            found_model = True
        else:
            print(f"  ℹ️  Not found: {model_path}")
    
    if not found_model:
        print("\n  ⚠️  WARNING: No pre-trained model found!")
        print("  The system will try to use a generic YOLO model if available.")
    
    return found_model

def verify_dataset():
    """Check if training dataset is available"""
    print("\n" + "-" * 80)
    print("5. TRAINING DATASET")
    print("-" * 80)
    
    dataset_path = "scrap_files/Complete_Uniform.v3i.yolov12"
    
    if os.path.exists(dataset_path):
        print(f"  ✅ Dataset found: {dataset_path}")
        
        # Check splits
        for split in ["train", "valid", "test"]:
            split_path = os.path.join(dataset_path, split)
            if os.path.exists(split_path):
                print(f"     ✅ {split} split exists")
            else:
                print(f"     ❌ {split} split missing")
        
        return True
    else:
        print(f"  ❌ Dataset not found: {dataset_path}")
        return False

def verify_system_structure():
    """Verify the enhanced system structure"""
    print("\n" + "-" * 80)
    print("6. SYSTEM ENHANCEMENTS")
    print("-" * 80)
    
    # Check if main system has been updated
    try:
        with open("uniform_detector_system.py", "r") as f:
            content = f.read()
            
            checks = [
                ("_detect_gender" in content, "Gender detection method"),
                ("CONF_THRESHOLDS" in content, "Class-specific thresholds"),
                ("detected_gender" in content, "Gender output field"),
                ("detection_details" in content, "Detection details/confidence"),
            ]
            
            all_ok = True
            for check, description in checks:
                if check:
                    print(f"  ✅ {description}")
                else:
                    print(f"  ❌ {description}")
                    all_ok = False
            
            return all_ok
    except Exception as e:
        print(f"  ❌ Error checking system: {e}")
        return False

def verify_configuration():
    """Verify system is properly configured"""
    print("\n" + "-" * 80)
    print("7. CONFIGURATION")
    print("-" * 80)
    
    try:
        from uniform_detector_system import UniformDetector
        
        # Create detector instance
        detector = UniformDetector()
        
        # Check configuration
        checks = [
            (hasattr(detector, 'REQUIRED_BOYS'), "Boys uniform requirements"),
            (hasattr(detector, 'REQUIRED_GIRLS'), "Girls uniform requirements"),
            (hasattr(detector, 'CONF_THRESHOLDS'), "Confidence thresholds"),
            (hasattr(detector, '_detect_gender'), "Gender detection method"),
            (hasattr(detector, '_check_complete_uniform_v2'), "Enhanced uniform check"),
        ]
        
        all_ok = True
        for check, description in checks:
            if check:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_ok = False
        
        # Check requirements
        print(f"\n  Boys requirements: {detector.REQUIRED_BOYS}")
        print(f"  Girls requirements: {detector.REQUIRED_GIRLS}")
        
        return all_ok
    
    except Exception as e:
        print(f"  ❌ Error loading system: {e}")
        return False

def run_basic_test():
    """Run a basic functionality test"""
    print("\n" + "-" * 80)
    print("8. BASIC FUNCTIONALITY TEST")
    print("-" * 80)
    
    try:
        from uniform_detector_system import UniformDetector
        import numpy as np
        
        print("  Creating detector instance...")
        detector = UniformDetector()
        
        if detector.model is None:
            print("  ⚠️  Model not loaded (may need to download)")
            return False
        
        print("  Creating test image...")
        # Create a dummy image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        print("  Running detection on test image...")
        result = detector.detect_uniform(test_image)
        
        print("  ✅ Detection completed successfully")
        print(f"     Status: {result['uniform_status']}")
        print(f"     Gender: {result.get('detected_gender', 'N/A')}")
        print(f"     Items: {result.get('detected_items', [])}")
        
        return True
    
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def print_summary(results):
    """Print verification summary"""
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n✅ ALL CHECKS PASSED - System is ready to use!\n")
        print("Next steps:")
        print("  1. Run: python quick_start_boys_girls.py")
        print("  2. Select option 1 for webcam detection")
        print("  3. Test with boys and girls uniforms")
    else:
        print("\n⚠️  SOME CHECKS FAILED - Please fix issues before using\n")
        print("Failed checks:")
        for check, result in results.items():
            if not result:
                print(f"  • {check}")
        
        print("\nTo fix:")
        print("  1. Review the errors above")
        print("  2. Install missing dependencies: pip install -r requirements.txt")
        print("  3. Check model files are in correct location")
        print("  4. Re-run this verification script")

def main():
    print_banner()
    
    results = {
        "Core System Files": verify_core_system(),
        "Documentation": verify_documentation(),
        "Python Dependencies": verify_dependencies(),
        "Model Availability": verify_model_availability(),
        "Training Dataset": verify_dataset(),
        "System Enhancements": verify_system_structure(),
        "Configuration": verify_configuration(),
        "Basic Functionality": run_basic_test(),
    }
    
    print_summary(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
