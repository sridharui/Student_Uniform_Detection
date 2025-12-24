"""
Resume YOLOv11 training on No_Uniform from epoch 42
"""
from ultralytics import YOLO  # noqa
import os  # noqa

def main():
    print("="*60)
    print("  YOLOv11 Resume Training - No Uniform Dataset")
    print("="*60)
    
    # Resume from last checkpoint
    model = YOLO('runs/train/no_uniform_detector_yolov11_cpu/weights/last.pt')
    print("✅ Resuming from last checkpoint")
    
    print("\n📋 Resume Configuration:")
    print(f"   Resuming epochs: 42-50")
    print(f"   Dataset: No_Uniform.v1i.yolov12/data.yaml")
    print(f"   Image size: 640")
    print(f"   Batch size: 16")
    print(f"   Device: cpu")
    print("="*60 + "\n")
    
    # Resume training from epoch 42 to 50
    print("🚀 Resuming training...")
    results = model.train(
        data='No_Uniform.v1i.yolov12/data.yaml',
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,
        device='cpu',
        workers=0,
        project='runs/train',
        name='no_uniform_detector_yolov11_cpu',
        exist_ok=True,
        resume=True,
        verbose=True
    )
    
    print("\n✅ Training completed!")
    print(f"📁 Results saved to: runs/train/no_uniform_detector_yolov11_cpu/")
    
    # Load trained model for validation
    print("\n🔍 Running validation on No_Uniform dataset...")
    trained_model = YOLO('runs/train/no_uniform_detector_yolov11_cpu/weights/best.pt')
    no_uniform_val = trained_model.val(data='No_Uniform.v1i.yolov12/data.yaml')
    print(f"✅ Validation metrics (No_Uniform): mAP50={no_uniform_val.box.map50:.4f}")
    
    print("\n" + "="*60)
    print("  ✅ No_Uniform Training Finished")
    print("="*60)

if __name__ == "__main__":
    main()
