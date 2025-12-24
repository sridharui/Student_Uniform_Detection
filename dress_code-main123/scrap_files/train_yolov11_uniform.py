"""
Train YOLOv11 on Complete_Uniform dataset
"""
from ultralytics import YOLO  # noqa
import os  # noqa

def main():
    print("="*60)
    print("  YOLOv11 Training - Complete Uniform Dataset")
    print("="*60)
    
    # Dataset paths
    uniform_data = "Complete_Uniform.v3i.yolov12/data.yaml"
    no_uniform_data = "No_Uniform.v1i.yolov12/data.yaml"
    
    if not os.path.exists(uniform_data):
        print(f"❌ Dataset not found: {uniform_data}")
        return
    
    # Load YOLOv11 model
    try:
        model = YOLO('yolo11n.pt')  # YOLOv11 nano model
        print("✅ YOLOv11 model loaded successfully")
    except Exception as e:
        print(f"⚠️  Failed to load yolo11n.pt: {e}")
        print("📥 Downloading YOLOv11 model...")
        model = YOLO('yolo11n.pt')
    
    # Training configuration
    print("\n📋 Training Configuration:")
    print(f"   Model: YOLOv11n")
    print(f"   Dataset: {uniform_data}")
    print(f"   Epochs: 50")
    print(f"   Image size: 640")
    print(f"   Batch size: 16")
    print(f"   Device: cpu")
    print(f"   Patience: 10 (early stopping)")
    print("="*60 + "\n")
    
    # Train the model
    print("🚀 Starting training on Complete_Uniform dataset...")
    results = model.train(
        data=uniform_data,
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        device='cpu',
        workers=0,
        project='runs/train',
        name='uniform_detector_yolov11_cpu',
        exist_ok=True,
        verbose=True
    )
    
    print("\n✅ Training completed!")
    print(f"📁 Results saved to: runs/train/uniform_detector_yolov11_cpu/")
    
    # Load trained model for validation
    print("\n🔍 Running validation on Complete_Uniform dataset...")
    trained_model = YOLO('runs/train/uniform_detector_yolov11_cpu/weights/best.pt')
    uniform_val = trained_model.val(data=uniform_data)
    print(f"✅ Validation metrics (Complete_Uniform): mAP50={uniform_val.box.map50:.4f}")
    
    # Validate on No_Uniform dataset
    if os.path.exists(no_uniform_data):
        print("\n🔍 Running validation on No_Uniform dataset...")
        no_uniform_val = trained_model.val(data=no_uniform_data)
        print(f"✅ Validation metrics (No_Uniform): mAP50={no_uniform_val.box.map50:.4f}")
    
    print("\n" + "="*60)
    print("  ✅ Complete_Uniform Training Finished")
    print("="*60)

if __name__ == "__main__":
    main()
