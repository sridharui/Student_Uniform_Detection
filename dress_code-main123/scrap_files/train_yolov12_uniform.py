"""
YOLOv12 Uniform Detection Training Script
Train the model on Complete_Uniform and No_Uniform datasets
"""
import os
import sys
from pathlib import Path

def check_ultralytics():
    """Check if ultralytics is installed"""
    try:
        from ultralytics import YOLO
        print("✅ ultralytics installed")
        return True
    except ImportError:
        print("❌ ultralytics not installed")
        print("   Install: pip install ultralytics")
        return False

def train_uniform_detector():
    """Train YOLOv12 model on uniform detection dataset"""
    
    # Check dependencies
    if not check_ultralytics():
        return False
    
    from ultralytics import YOLO
    
    # Define dataset paths
    complete_uniform_data = "Complete_Uniform.v3i.yolov12/data.yaml"
    no_uniform_data = "No_Uniform.v1i.yolov12/data.yaml"
    
    print("=" * 80)
    print("YOLOv12 UNIFORM DETECTION TRAINING")
    print("=" * 80)
    
    # Check if datasets exist
    if not os.path.exists(complete_uniform_data):
        print(f"❌ Error: {complete_uniform_data} not found!")
        return False
    
    if not os.path.exists(no_uniform_data):
        print(f"❌ Error: {no_uniform_data} not found!")
        return False
    
    print(f"✅ Complete Uniform dataset found: {complete_uniform_data}")
    print(f"✅ No Uniform dataset found: {no_uniform_data}")
    
    # Training on Complete_Uniform dataset (has test, train, valid splits)
    print("\n" + "=" * 80)
    print("STEP 1: Training on COMPLETE_UNIFORM Dataset")
    print("=" * 80)
    
    try:
        print("\n📥 Loading YOLOv12 Medium model (downloading if needed)...")
        try:
            model = YOLO("yolov12m.pt")  # Try YOLOv12 first
            print("✅ YOLOv12 model loaded successfully!\n")
        except Exception as e:
            print(f"⚠️  YOLOv12 not available, using YOLOv8 instead...")
            model = YOLO("yolov8m.pt")  # Fallback to YOLOv8
            print("✅ YOLOv8 model loaded successfully!\n")
        
        results = model.train(
            data=complete_uniform_data,
            epochs=50,
            imgsz=640,
            batch=16,
            patience=10,
            save=True,
            device='cpu',  # Use CPU (no CUDA GPU available)
            workers=0,      # Avoid multiprocessing issues on Windows/CPU
            name="uniform_detector_yolov12_cpu",
            project="runs/train",
            exist_ok=True,
            pretrained=True,
            augment=True,
            mosaic=1.0,
            conf=0.5,
            verbose=True
        )
        
        print("✅ Complete Uniform training completed!")
        print(f"Results saved to: runs/train/uniform_detector_yolov12_cpu")
        
    except Exception as e:
        print(f"❌ Error during Complete Uniform training: {str(e)}")
        return False
    
    # Testing on Complete_Uniform test set
    print("\n" + "=" * 80)
    print("STEP 2: Testing on COMPLETE_UNIFORM Test Set")
    print("=" * 80)
    
    try:
        trained_model = YOLO("runs/train/uniform_detector_yolov12_cpu/weights/best.pt")
        
        test_results = trained_model.val(
            data=complete_uniform_data,
            device='cpu',  # Use CPU
            imgsz=640,
            conf=0.5,
            verbose=True
        )
        
        print("✅ Complete Uniform validation completed!")
        
    except Exception as e:
        print(f"❌ Error during Complete Uniform validation: {str(e)}")
        return False
    
    # Validation on No_Uniform dataset
    print("\n" + "=" * 80)
    print("STEP 3: Validating on NO_UNIFORM Dataset")
    print("=" * 80)
    
    try:
        trained_model = YOLO("runs/train/uniform_detector_yolov12_cpu/weights/best.pt")
        
        no_uniform_results = trained_model.val(
            data=no_uniform_data,
            device='cpu',  # Use CPU
            imgsz=640,
            conf=0.5,
            verbose=True
        )
        
        print("✅ No Uniform validation completed!")
        
    except Exception as e:
        print(f"❌ Error during No Uniform validation: {str(e)}")
        return False
    
    print("\n" + "=" * 80)
    print("TRAINING COMPLETE!")
    print("=" * 80)
    print(f"✅ Model saved at: runs/train/uniform_detector_yolov12_cpu/weights/best.pt")
    print(f"✅ Ready for inference on webcams and web application")
    
    return True

if __name__ == "__main__":
    success = train_uniform_detector()
    if success:
        print("\n🎉 Training pipeline completed successfully!")
    else:
        print("\n❌ Training pipeline failed!")
