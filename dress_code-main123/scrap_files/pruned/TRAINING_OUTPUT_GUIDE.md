# Training Output Guide - YOLO Epochs & Metrics Explained

## Previous Training Configuration

Your previous training runs used these settings:

```yaml
Model: YOLOv11n (nano model)
Epochs: 50
Batch Size: 16
Image Size: 640x640
Device: CPU
Patience: 10 (early stopping)
Dataset: Complete_Uniform.v3i.yolov12/data.yaml
Project: runs/train/uniform_detector_yolov11_cpu
```

## Training Output Format

### 1. **Training Script Output** (Terminal Display)
When you run the training script, you'll see:

```python
model.train(
    data=uniform_data,
    epochs=50,           # Total training loops through entire dataset
    imgsz=640,          # Image size in pixels
    batch=16,           # Images processed per step
    patience=10,        # Stop if no improvement for 10 epochs
    device='cpu',       # Training device
    workers=0,          # Data loading workers
    project='runs/train',
    name='uniform_detector_yolov11_cpu',
    exist_ok=True,      # Allow overwriting existing runs
    verbose=True        # Show detailed output
)
```

### 2. **Per-Epoch Output** (During Training)

Each epoch produces metrics like:
```
Epoch 1/50: 100%|████████| 10/10 [00:30<00:00, 3.00s/it]
train/box_loss: 0.751    (Bounding box loss)
train/cls_loss: 3.150    (Classification loss)
train/dfl_loss: 1.004    (Distribution focal loss)
val/box_loss: 0.542      (Validation box loss)
val/cls_loss: 3.617      (Validation classification loss)
```

---

## Results File: `results.csv`

Located at: `runs/train/uniform_detector_yolov11_cpu/results.csv`

### Column Headers:
```csv
epoch, time, train/box_loss, train/cls_loss, train/dfl_loss, 
metrics/precision(B), metrics/recall(B), metrics/mAP50(B), metrics/mAP50-95(B),
val/box_loss, val/cls_loss, val/dfl_loss, lr/pg0, lr/pg1, lr/pg2
```

### Example Data from Your Training (Epoch 1-5):

| Epoch | Time (s) | Train Box Loss | Train Cls Loss | Precision | Recall | mAP50 | mAP50-95 | Val Box Loss |
|-------|----------|---|---|---|---|---|---|---|
| 1 | 174.886 | 0.751 | 3.150 | 0.018 | 0.523 | 0.412 | 0.378 | 0.542 |
| 2 | 338.899 | 0.627 | 1.356 | 0.923 | 0.372 | 0.763 | 0.668 | 0.599 |
| 3 | 502.425 | 0.557 | 0.859 | 0.902 | 0.674 | 0.842 | 0.768 | 0.556 |
| 4 | 664.128 | 0.528 | 0.747 | 0.719 | 0.747 | 0.821 | 0.765 | 0.481 |
| 5 | 825.188 | 0.493 | 0.697 | 0.886 | 0.898 | 0.842 | 0.778 | 0.505 |

---

## Key Metrics Explained

### **Loss Metrics** (Lower is better)
- **train/box_loss**: Bounding box coordinate accuracy
- **train/cls_loss**: Classification (object detection) accuracy
- **train/dfl_loss**: Distribution focal loss
- **val/box_loss, val/cls_loss, val/dfl_loss**: Same metrics on validation set

### **Performance Metrics** (Higher is better)
- **precision(B)**: Of detected objects, how many are correct (0-1 scale)
- **recall(B)**: Of all actual objects, how many did model find (0-1 scale)
- **mAP50(B)**: Mean Average Precision at 0.50 IoU threshold
- **mAP50-95(B)**: Mean Average Precision across 0.5-0.95 IoU thresholds

### **Learning Rate (lr)**
- **lr/pg0, lr/pg1, lr/pg2**: Learning rate per parameter group (changes during training)

### **Time**
- Cumulative time in seconds for that epoch

---

## Training Arguments File: `args.yaml`

Located at: `runs/train/uniform_detector_yolov11_cpu/args.yaml`

Stores all training configurations:
```yaml
task: detect
mode: train
model: yolo11n.pt        # Starting model
data: Complete_Uniform.v3i.yolov12/data.yaml
epochs: 50               # Total epochs planned
batch: 16                # Batch size
imgsz: 640              # Image resolution
device: cpu             # Processing device
patience: 10            # Early stopping patience
optimizer: auto         # Auto-select optimizer
seed: 0                 # Reproducibility
```

---

## Output Directories

```
runs/train/uniform_detector_yolov11_cpu/
├── weights/
│   ├── best.pt         # Best model weights
│   └── last.pt         # Last epoch weights
├── results.csv         # Metrics per epoch
├── results.png         # Training curves plot
├── args.yaml           # Training configuration
├── confusion_matrix.png    # Class confusion matrix
├── BoxPR_curve.png     # Precision-Recall curve
├── train_batch0.jpg    # Training batch samples
└── val_batch0_pred.jpg # Validation predictions
```

---

## Example Training Progress

### Early Epochs (Convergence Phase)
```
Epoch 1: High losses (3.15 cls_loss), Low metrics (0.41 mAP50)
Epoch 2: Improving (1.36 cls_loss), Better metrics (0.76 mAP50)
Epoch 5: Good improvement (0.70 cls_loss), Strong metrics (0.84 mAP50)
```

### Later Epochs (Refinement Phase)
```
Epoch 10: Stabilizing (0.54 cls_loss), Consistent (0.84 mAP50)
Epoch 19: Fine-tuning (0.46 cls_loss), Peak performance
Epoch 20+: May plateau or slightly improve
```

---

## Early Stopping Rule

Training stops automatically if:
- **No improvement in mAP50 for 10 consecutive epochs** (patience=10)

Your training reached 19 epochs before best.pt was saved around epoch 14.

---

## How to Run Training

```python
from ultralytics import YOLO

# Load model
model = YOLO('yolo11n.pt')

# Train
results = model.train(
    data='Complete_Uniform.v3i.yolov12/data.yaml',
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

# Access results
print(f"Best mAP50: {results.box.map50}")
```

---

## Viewing Training Results

### Option 1: View CSV in Excel/Spreadsheet
Open `results.csv` directly in Excel or a spreadsheet app to see all metrics.

### Option 2: View PNG Plots
- `results.png` - Training curves for all metrics
- `BoxPR_curve.png` - Precision-Recall curve
- `confusion_matrix.png` - Class prediction matrix

### Option 3: Terminal Command
```bash
python -c "import pandas as pd; df=pd.read_csv('runs/train/uniform_detector_yolov11_cpu/results.csv'); print(df)"
```

---

## Performance Summary from Your Training

- **Final Epoch**: 19 (stopped before 50 due to early stopping)
- **Best mAP50**: ~0.868 (epoch 19)
- **Final Precision**: 0.886
- **Final Recall**: 0.898
- **Training Time**: ~3,252 seconds (~54 minutes)
- **Time per Epoch**: ~171 seconds (~2.8 minutes) on CPU

---

## Next Training

To train a new model with similar settings:

```bash
# YOLOv12 training
python scrap_files/train_yolov12_uniform.py

# Or YOLOv11 training  
python scrap_files/train_yolov11_uniform.py
```

You'll get new results in `runs/train/` with the same output format.
