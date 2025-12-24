"""
Train YOLOv11 on No_Uniform dataset
"""
from ultralytics import YOLO  # noqa
import os  # noqa

def main():
    print("="*60)
    print("  YOLOv11 Training - No Uniform Dataset")
    print("="*60)
    
    # Dataset path
    no_uniform_data = "No_Uniform.v1i.yolov12/data.yaml"
    
    if not os.path.exists(no_uniform_data):
        print(f"❌ Dataset not found: {no_uniform_data}")
        return
    
    # Load YOLOv11 model
    model = YOLO('yolo11n.pt')
    print("✅ YOLOv11 model loaded successfully")
    
    # Training configuration
    print("\n📋 Training Configuration:")
    print(f"   Model: YOLOv11n")
    print(f"   Dataset: {no_uniform_data}")
    print(f"   Epochs: 50")
    print(f"   Image size: 640")
    print(f"   Batch size: 16")
    print(f"   Device: cpu")
    print(f"   Patience: 10 (early stopping)")
    print("="*60 + "\n")
    
    # Train the model
    print("🚀 Starting training on No_Uniform dataset...")
    results = model.train(
        data=no_uniform_data,
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        device='cpu',
        workers=0,
        project='runs/train',
        name='no_uniform_detector_yolov11_cpu',
        exist_ok=True,
        verbose=True
    )
    
    print("\n✅ Training completed!")
    print(f"📁 Results saved to: runs/train/no_uniform_detector_yolov11_cpu/")
    
    # Load trained model for validation
    print("\n🔍 Running validation on No_Uniform dataset...")
    trained_model = YOLO('runs/train/no_uniform_detector_yolov11_cpu/weights/best.pt')
    no_uniform_val = trained_model.val(data=no_uniform_data)
    print(f"✅ Validation metrics (No_Uniform): mAP50={no_uniform_val.box.map50:.4f}")
    
    print("\n" + "="*60)
    print("  ✅ No_Uniform Training Finished")
    print("="*60)

if __name__ == "__main__":
    main()
