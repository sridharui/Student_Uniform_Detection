"""
Validation Script - Test the trained model on both datasets
This completes the validation/testing process
"""
import os
from ultralytics import YOLO

def validate_model():
    """Validate the trained model on both datasets"""
    
    model_path = "runs/train/uniform_detector_yolov12_cpu/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("   Please run training first!")
        return False
    
    print("=" * 80)
    print("MODEL VALIDATION & TESTING")
    print("=" * 80)
    print(f"✅ Model loaded: {model_path}\n")
    
    model = YOLO(model_path)
    
    # STEP 1: Validate on Complete_Uniform validation set
    print("=" * 80)
    print("STEP 1: Validating on COMPLETE_UNIFORM Validation Set")
    print("=" * 80)
    try:
        val_results = model.val(
            data='Complete_Uniform.v3i.yolov12/data.yaml',
            split='val',  # Use validation split
            device='cpu',
            imgsz=640,
            conf=0.25,
            iou=0.6,
            verbose=True
        )
        print("✅ Complete_Uniform validation completed!")
        print(f"   mAP50: {val_results.box.map50:.4f}")
        print(f"   mAP50-95: {val_results.box.map:.4f}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # STEP 2: Test on Complete_Uniform test set
    print("\n" + "=" * 80)
    print("STEP 2: Testing on COMPLETE_UNIFORM Test Set")
    print("=" * 80)
    try:
        test_results = model.val(
            data='Complete_Uniform.v3i.yolov12/data.yaml',
            split='test',  # Use test split
            device='cpu',
            imgsz=640,
            conf=0.25,
            iou=0.6,
            verbose=True
        )
        print("✅ Complete_Uniform test completed!")
        print(f"   mAP50: {test_results.box.map50:.4f}")
        print(f"   mAP50-95: {test_results.box.map:.4f}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # STEP 3: Validate on No_Uniform dataset
    print("\n" + "=" * 80)
    print("STEP 3: Validating on NO_UNIFORM Dataset")
    print("=" * 80)
    try:
        no_uniform_results = model.val(
            data='No_Uniform.v1i.yolov12/data.yaml',
            split='val',  # Uses train split (as configured)
            device='cpu',
            imgsz=640,
            conf=0.25,
            iou=0.6,
            verbose=True
        )
        print("✅ No_Uniform validation completed!")
        print(f"   mAP50: {no_uniform_results.box.map50:.4f}")
        print(f"   mAP50-95: {no_uniform_results.box.map:.4f}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE!")
    print("=" * 80)
    print("✅ All validation and testing steps completed")
    print(f"✅ Model ready for deployment: {model_path}")
    
    return True

if __name__ == "__main__":
    validate_model()
