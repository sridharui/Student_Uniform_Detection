"""
Script to improve uniform detection accuracy for both boys and girls
Provides analysis and recommendations for better model training
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict

def analyze_dataset():
    """Analyze the training dataset for gender-specific items"""
    print("=" * 80)
    print("UNIFORM DETECTION DATASET ANALYSIS")
    print("=" * 80)
    
    dataset_base = "scrap_files/Complete_Uniform.v3i.yolov12"
    
    splits = ["train", "valid", "test"]
    stats = defaultdict(lambda: defaultdict(int))
    
    for split in splits:
        img_dir = os.path.join(dataset_base, split, "images")
        label_dir = os.path.join(dataset_base, split, "labels")
        
        if not os.path.exists(img_dir):
            print(f"⚠️  {split} split not found: {img_dir}")
            continue
        
        image_count = len([f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.png'))])
        
        # Class mapping from data.yaml
        classes = ['Identity Card', 'Shirt', 'identity card', 'pant', 'shoes', 'slippers', 'top']
        class_counts = defaultdict(int)
        
        if os.path.exists(label_dir):
            for label_file in os.listdir(label_dir):
                if label_file.endswith('.txt'):
                    with open(os.path.join(label_dir, label_file), 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                class_id = int(parts[0])
                                if class_id < len(classes):
                                    class_counts[classes[class_id]] += 1
        
        print(f"\n{split.upper()} Split:")
        print(f"  Images: {image_count}")
        print(f"  Class Distribution:")
        
        total_annotations = sum(class_counts.values())
        for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_annotations * 100) if total_annotations > 0 else 0
            print(f"    {cls:20s}: {count:4d} ({pct:5.1f}%)")
        
        stats[split] = class_counts
    
    print("\n" + "=" * 80)
    print("GENDER-SPECIFIC RECOMMENDATIONS")
    print("=" * 80)
    
    # Analyze gender balance
    boys_items = {'Shirt': 0, 'pant': 0, 'shoes': 0}
    girls_items = {'top': 0, 'pant': 0, 'shoes': 0}
    
    for split in splits:
        split_stats = stats[split]
        for item in boys_items:
            boys_items[item] += split_stats.get(item, 0)
        for item in girls_items:
            if item in split_stats:
                girls_items[item] += split_stats.get(item, 0)
    
    print("\nBOYS Uniform Components (Total across all splits):")
    for item, count in boys_items.items():
        print(f"  {item}: {count}")
    
    print("\nGIRLS Uniform Components (Total across all splits):")
    for item, count in girls_items.items():
        print(f"  {item}: {count}")
    
    # Recommendations
    print("\n" + "-" * 80)
    print("RECOMMENDATIONS FOR IMPROVED DETECTION")
    print("-" * 80)
    
    recommendations = [
        "1. BALANCE DATASET: Ensure equal number of boys and girls images",
        "2. SHIRT vs TOP: Collect more samples of 'top' for girls (currently may have fewer)",
        "3. AUGMENTATION: Apply data augmentation (rotation, scaling, lighting changes)",
        "4. CONFIDENCE TUNING: Adjust confidence thresholds per class:",
        "     - 'Shirt' should be prioritized for boys detection",
        "     - 'top' should be prioritized for girls detection",
        "5. DUPLICATE LABELS: Remove duplicate 'Identity Card'/'identity card' classes",
        "6. ANNOTATION QUALITY: Review annotations for consistency",
        "7. ANGLE DIVERSITY: Collect images from multiple angles (front, side, back)",
        "8. LIGHTING: Include various lighting conditions in training data"
    ]
    
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)

def test_model_accuracy(model_path="runs/train/uniform_detector_yolov11_cpu/weights/best.pt"):
    """Test model accuracy on boys and girls detection"""
    print("\n" + "=" * 80)
    print("TESTING MODEL ACCURACY")
    print("=" * 80)
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return
    
    model = YOLO(model_path)
    print(f"✅ Model loaded: {model_path}")
    
    # Test on validation set
    val_dir = "scrap_files/Complete_Uniform.v3i.yolov12/valid/images"
    
    if not os.path.exists(val_dir):
        print(f"⚠️  Validation directory not found: {val_dir}")
        return
    
    print(f"\nValidating on: {val_dir}")
    
    # Get list of test images
    test_images = [f for f in os.listdir(val_dir) if f.endswith(('.jpg', '.png'))][:10]  # Test on first 10
    
    boys_detected = defaultdict(int)
    girls_detected = defaultdict(int)
    detection_issues = []
    
    for img_file in test_images:
        img_path = os.path.join(val_dir, img_file)
        image = cv2.imread(img_path)
        
        # Run detection
        results = model(image, conf=0.5, verbose=False)
        
        detected_classes = set()
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for cls_id in result.boxes.cls:
                    class_name = result.names[int(cls_id)]
                    detected_classes.add(class_name)
        
        # Classify detection
        has_shirt = 'Shirt' in detected_classes
        has_top = 'top' in detected_classes
        
        if has_shirt:
            boys_detected['detected'] += 1
        if has_top:
            girls_detected['detected'] += 1
        
        if has_shirt and has_top:
            detection_issues.append(f"  ⚠️  {img_file}: Both 'Shirt' and 'top' detected (ambiguous)")
        
        print(f"  {img_file}: {detected_classes}")
    
    print(f"\nResults (from {len(test_images)} test images):")
    print(f"  Boys (Shirt detected): {boys_detected['detected']}")
    print(f"  Girls (Top detected): {girls_detected['detected']}")
    
    if detection_issues:
        print(f"\n⚠️  Ambiguous Detections (both Shirt and Top):")
        for issue in detection_issues:
            print(issue)
    
    print("\n" + "=" * 80)

def suggest_training_command():
    """Suggest the best YOLO training command for this dataset"""
    print("\n" + "=" * 80)
    print("SUGGESTED TRAINING COMMAND")
    print("=" * 80)
    
    commands = [
        "\nTo train a new YOLO model on boys/girls uniform detection:\n",
        "python -m ultralytics.yolo detect train \\",
        "    model=yolov11n.pt \\",
        "    data=scrap_files/Complete_Uniform.v3i.yolov12/data.yaml \\",
        "    epochs=100 \\",
        "    imgsz=640 \\",
        "    batch=16 \\",
        "    patience=20 \\",
        "    device=0 \\",
        "    name=uniform_detector_boys_girls_v1 \\",
        "    augment=True \\",
        "    mosaic=1.0 \\",
        "    mixup=0.1 \\",
        "    fliplr=0.5 \\",
        "    flipud=0.5 \\",
        "    degrees=15 \\",
        "    translate=0.1 \\",
        "    scale=0.9",
        "\nFor YOLOv12 (better accuracy):\n",
        "python -m ultralytics.yolo detect train \\",
        "    model=yolov12n.pt \\",
        "    data=scrap_files/Complete_Uniform.v3i.yolov12/data.yaml \\",
        "    epochs=150 \\",
        "    imgsz=640 \\",
        "    batch=16 \\",
        "    device=0 \\",
        "    name=uniform_detector_boys_girls_yolov12",
    ]
    
    for cmd in commands:
        print(cmd)
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "UNIFORM DETECTOR - BOYS & GIRLS ACCURACY IMPROVEMENT".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝\n")
    
    # Run analysis
    analyze_dataset()
    
    # Test current model if available
    test_model_accuracy()
    
    # Suggest improvements
    suggest_training_command()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nTo improve detection accuracy for boys and girls:")
    print("  1. Run the analysis above to understand your dataset")
    print("  2. Balance the dataset - ensure equal boys and girls samples")
    print("  3. Retrain model using the suggested command")
    print("  4. Use the updated model with the improved detector system")
    print("  5. Test with real-world images to validate accuracy")
    print("\nThe updated uniform_detector_system.py now supports:")
    print("  ✓ Gender-specific detection (BOYS vs GIRLS)")
    print("  ✓ Class-specific confidence thresholds")
    print("  ✓ Enhanced detection logging")
    print("  ✓ Better handling of 'Shirt' (boys) vs 'top' (girls)")
    print("=" * 80 + "\n")
