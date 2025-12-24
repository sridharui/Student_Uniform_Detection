"""
Verification Script for YOLOv12 Uniform Detection Setup
Check all requirements and datasets before training
"""
import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_dependencies():
    """Check required packages"""
    required = ['ultralytics', 'cv2', 'flask', 'numpy', 'PIL']
    
    print("\nChecking dependencies:")
    all_ok = True
    
    for pkg in required:
        try:
            if pkg == 'cv2':
                import cv2
            elif pkg == 'PIL':
                from PIL import Image
            elif pkg == 'numpy':
                import numpy
            else:
                __import__(pkg)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_datasets():
    """Check dataset structure"""
    print("\nChecking datasets:")
    
    complete_uniform = Path("Complete_Uniform.v3i.yolov12")
    no_uniform = Path("No_Uniform.v1i.yolov12")
    
    datasets_ok = True
    
    # Check Complete_Uniform dataset
    if complete_uniform.exists():
        print(f"✅ Found: {complete_uniform}")
        
        # Check subdirectories
        required_dirs = ['train', 'valid', 'test']
        for dir_name in required_dirs:
            dir_path = complete_uniform / dir_name
            if dir_path.exists():
                images_path = dir_path / 'images'
                labels_path = dir_path / 'labels'
                
                if images_path.exists() and labels_path.exists():
                    img_count = len(list(images_path.glob('*')))
                    lbl_count = len(list(labels_path.glob('*')))
                    print(f"  ✅ {dir_name}/: {img_count} images, {lbl_count} labels")
                else:
                    print(f"  ❌ {dir_name}/: missing images or labels directory")
                    datasets_ok = False
            else:
                print(f"  ❌ {dir_name}/ not found")
                datasets_ok = False
        
        # Check data.yaml
        yaml_path = complete_uniform / 'data.yaml'
        if yaml_path.exists():
            print(f"  ✅ data.yaml found")
        else:
            print(f"  ❌ data.yaml not found")
            datasets_ok = False
    else:
        print(f"❌ Not found: {complete_uniform}")
        datasets_ok = False
    
    # Check No_Uniform dataset
    if no_uniform.exists():
        print(f"✅ Found: {no_uniform}")
        
        train_dir = no_uniform / 'train'
        if train_dir.exists():
            images_path = train_dir / 'images'
            labels_path = train_dir / 'labels'
            
            if images_path.exists() and labels_path.exists():
                img_count = len(list(images_path.glob('*')))
                lbl_count = len(list(labels_path.glob('*')))
                print(f"  ✅ train/: {img_count} images, {lbl_count} labels")
            else:
                print(f"  ❌ train/: missing images or labels")
                datasets_ok = False
        else:
            print(f"  ❌ train/ not found")
            datasets_ok = False
        
        # Check data.yaml
        yaml_path = no_uniform / 'data.yaml'
        if yaml_path.exists():
            print(f"  ✅ data.yaml found")
        else:
            print(f"  ❌ data.yaml not found")
            datasets_ok = False
    else:
        print(f"❌ Not found: {no_uniform}")
        datasets_ok = False
    
    return datasets_ok

def check_directories():
    """Check and create required output directories"""
    print("\nChecking output directories:")
    
    dirs = ['uploads', 'mobile_uploads', 'static', 'training_data']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created {dir_name}/")
            except Exception as e:
                print(f"  ❌ Failed to create {dir_name}/: {e}")
                return False
    
    return True

def check_scripts():
    """Check if all required scripts exist"""
    print("\nChecking scripts:")
    
    scripts = [
        'train_yolov12_uniform.py',
        'uniform_detector_system.py',
        'mobile_webcam_detector_v2.py',
        'web_uniform_detector.py'
    ]
    
    all_ok = True
    for script in scripts:
        if os.path.exists(script):
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} - NOT FOUND")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 80)
    print("YOLOv12 UNIFORM DETECTION SETUP VERIFICATION")
    print("=" * 80)
    
    results = {}
    
    # Run checks
    results['python'] = check_python_version()
    results['dependencies'] = check_dependencies()
    results['datasets'] = check_datasets()
    results['directories'] = check_directories()
    results['scripts'] = check_scripts()
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    checks = [
        ("Python Version", results['python']),
        ("Dependencies", results['dependencies']),
        ("Datasets", results['datasets']),
        ("Directories", results['directories']),
        ("Scripts", results['scripts'])
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n🎉 All checks passed! Ready to train the model.\n")
        print("Next step: Run the training script")
        print("  python train_yolov12_uniform.py\n")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above before training.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
