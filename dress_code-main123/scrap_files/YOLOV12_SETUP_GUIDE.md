# Complete Uniform Detection System - YOLOv12

A comprehensive system for detecting if students are wearing complete uniforms using YOLOv12 object detection. The system supports:
- **Laptop Webcam Detection** - Real-time detection via laptop camera
- **Mobile Webcam Detection** - Remote detection from mobile devices
- **Web Application** - Upload images for testing and analysis

## Dataset Structure

### Complete_Uniform.v3i.yolov12
Images of students wearing complete uniforms with component annotations:
- **Boys**: ID Card + Shirt + Pant + Shoes ✅
- **Girls**: ID Card + Top + Pant + Shoes ✅
- **Classes**: Identity Card, Shirt, identity card, pant, shoes, slippers, top
- **Splits**: train/, valid/, test/

### No_Uniform.v1i.yolov12
Images of students without complete uniforms for validation

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Required packages
pip install ultralytics opencv-python flask flask-cors numpy pillow
```

## Quick Start Guide

### Step 1: Train the Model

```bash
python train_yolov12_uniform.py
```

This will:
1. ✅ Train YOLOv12 on Complete_Uniform dataset (train/valid/test splits)
2. ✅ Validate on Complete_Uniform test set
3. ✅ Test on No_Uniform dataset
4. ✅ Save best model to: `runs/train/uniform_detector_yolov12/weights/best.pt`

**Expected Output:**
```
============================================================================
YOLOv12 UNIFORM DETECTION TRAINING
============================================================================
✅ Complete Uniform dataset found: Complete_Uniform.v3i.yolov12/data.yaml
✅ No Uniform dataset found: No_Uniform.v1i.yolov12/data.yaml

============================================================================
STEP 1: Training on COMPLETE_UNIFORM Dataset
============================================================================
[Training progress...]
✅ Complete Uniform training completed!

============================================================================
STEP 2: Testing on COMPLETE_UNIFORM Test Set
============================================================================
✅ Complete Uniform validation completed!

============================================================================
STEP 3: Validating on NO_UNIFORM Dataset
============================================================================
✅ No Uniform validation completed!

============================================================================
TRAINING COMPLETE!
============================================================================
✅ Model saved at: runs/train/uniform_detector_yolov12/weights/best.pt
✅ Ready for inference on webcams and web application
```

### Step 2: Run Detections

#### Option A: Laptop Webcam Detection

```bash
python uniform_detector_system.py
```

**Features:**
- Real-time detection from webcam
- Shows detection status (Complete/Incomplete) on video feed
- Press 'q' to quit, 'c' to capture images
- Prints detection results to terminal

**Expected Output:**
```
================================================================================
UNIFORM DETECTION SYSTEM
================================================================================
📷 Webcam detection started. Press 'q' to quit, 'c' to capture...

Frame 5:   ✓ Detected: Identity Card (confidence: 0.92)
  ✓ Detected: Shirt (confidence: 0.88)
  ✓ Detected: pant (confidence: 0.85)
  ✓ Detected: shoes (confidence: 0.91)

✅ COMPLETE UNIFORM (BOYS) - Student is properly dressed

Frame 10: [similar detection results]
```

#### Option B: Mobile Webcam Detection

```bash
python mobile_webcam_detector_v2.py
```

**Features:**
- Web server on `http://localhost:5000`
- API endpoint: `POST /api/detect`
- Mobile-friendly interface
- Remote detection from any device on network

**Usage:**
1. Start the server
2. Access from mobile: `http://<your-computer-ip>:5000`
3. Take photo or upload image
4. Get instant uniform status (1 = Complete, 0 = Incomplete)

#### Option C: Web Application

```bash
python web_uniform_detector.py
```

**Features:**
- Web interface on `http://localhost:8080`
- Upload images for testing
- See processed image with detection boxes
- Terminal output with detailed results:

**Expected Output:**
```
============================================================
  WEB UNIFORM DETECTION SYSTEM
============================================================

📸 Test with images before going live
🎯 Upload uniform/non-uniform images to build training dataset
🚀 Run live detection after testing

Server starting at: http://localhost:8080
Press Ctrl+C to stop

============================================================

 * Running on http://127.0.0.1:8080
```

**Upload and Detection:**
- Go to `http://localhost:8080`
- Upload an image
- View results:
  ```
  {
    "complete_uniform": true,
    "result": 1,
    "status": {
      "shirt": {"ok": true, "color": "white"},
      "pant": {"ok": true, "color": "black"},
      "shoes": {"ok": true, "color": "black"},
      "id_card": {"ok": true, "color": "white"}
    },
    "detections": [...]
  }
  ```

## Output Interpretation

### Terminal Output

**Complete Uniform (Output: 1)**
```
✓ Detected: Identity Card (confidence: 0.92)
✓ Detected: Shirt (confidence: 0.88)
✓ Detected: pant (confidence: 0.85)
✓ Detected: shoes (confidence: 0.91)

✅ COMPLETE UNIFORM (BOYS) - Student is properly dressed
Status: 1
```

**Incomplete Uniform (Output: 0)**
```
✓ Detected: Shirt (confidence: 0.85)
✓ Detected: pant (confidence: 0.82)

❌ INCOMPLETE UNIFORM (BOYS) - Missing: Identity Card, shoes
Status: 0
```

### Web Application Display

**On Processed Image:**
- ✓ Shirt (white) - Green checkmark if valid
- ✓ Pant (black) - Green checkmark if valid
- ✓ Shoes (black) - Green checkmark if valid
- ✓ ID Card (white) - Green checkmark if detected

- ❌ Missing Item - Red X if not detected
- **COMPLETE UNIFORM - 1** (Green text, large)
- **INCOMPLETE UNIFORM - 0** (Red text, large)

## Detection Logic

### For Boys ✓
All of these must be detected:
1. **Identity Card** - Lanyard/ID badge
2. **Shirt** - Must be white or gray color
3. **Pant** - Must be black, navy blue, or dark blue
4. **Shoes** - Any color

Output: **1** (Complete) or **0** (Incomplete)

### For Girls ✓
All of these must be detected:
1. **Identity Card** - Lanyard/ID badge
2. **Top** - Must be white or gray color
3. **Pant** - Must be black, navy blue, or dark blue
4. **Shoes** - Any color

Output: **1** (Complete) or **0** (Incomplete)

## File Structure

```
dress_code-main/
├── train_yolov12_uniform.py          # Training script
├── uniform_detector_system.py        # Laptop webcam detection
├── mobile_webcam_detector_v2.py      # Mobile/remote detection
├── web_uniform_detector.py           # Web application
│
├── Complete_Uniform.v3i.yolov12/     # Training dataset (boys & girls)
│   ├── data.yaml
│   ├── train/
│   ├── valid/
│   └── test/
│
├── No_Uniform.v1i.yolov12/           # Validation dataset
│   ├── data.yaml
│   └── train/
│
├── runs/train/
│   └── uniform_detector_yolov12/     # Trained model (after training)
│       └── weights/
│           ├── best.pt
│           └── last.pt
│
├── uploads/                          # Web app uploads
├── mobile_uploads/                   # Mobile app uploads
└── static/                           # Web app results
```

## Configuration

### Training Parameters (in `train_yolov12_uniform.py`)

```python
epochs=100              # Number of training epochs
imgsz=640              # Image size for training
batch=16               # Batch size
patience=20            # Early stopping patience
device=0               # GPU device ID
conf=0.5               # Confidence threshold
```

### Detection Parameters (in `uniform_detector_system.py`)

```python
CONF_THRESHOLD = 0.5   # Confidence threshold for detections
```

### Web App Configuration (in `web_uniform_detector.py`)

```python
CONF_THRESH = 0.10     # Low threshold to catch ID cards
MIN_AREA = 400         # Minimum detection area
IMG_SIZE = 640         # Input image size
USE_SPATIAL_FILTERING = True  # Validate detection locations
SHIRT_ALLOWED = {'gray', 'white'}
PANTS_ALLOWED = {'black', 'navy blue', 'blue', 'dark blue'}
```

## Troubleshooting

### Model Not Found
```
⚠️ Model not found at runs/train/uniform_detector_yolov12/weights/best.pt
Please run training first: python train_yolov12_uniform.py
```
**Solution**: Run the training script first

### Poor Detection Quality
1. Check dataset completeness:
   ```bash
   # Count training images
   ls -la Complete_Uniform.v3i.yolov12/train/images/ | wc -l
   ls -la Complete_Uniform.v3i.yolov12/valid/images/ | wc -l
   ls -la Complete_Uniform.v3i.yolov12/test/images/ | wc -l
   ```

2. Increase training epochs:
   ```python
   epochs=150  # in train_yolov12_uniform.py
   ```

3. Use lower confidence threshold:
   ```python
   CONF_THRESHOLD = 0.3  # in uniform_detector_system.py
   ```

### GPU Issues
If CUDA not available:
```python
device='cpu'  # in train_yolov12_uniform.py, line with device=0
```

## Performance Metrics

Expected after training on Complete_Uniform.v3i.yolov12:
- **mAP50**: > 85%
- **Precision**: > 80%
- **Recall**: > 85%
- **Inference Speed**: ~50ms per image (GPU)

## Next Steps

1. ✅ **Train** the model: `python train_yolov12_uniform.py`
2. ✅ **Test** with laptop: `python uniform_detector_system.py`
3. ✅ **Deploy** mobile server: `python mobile_webcam_detector_v2.py`
4. ✅ **Use** web app: `python web_uniform_detector.py`

## Support

For detailed logs:
```bash
python train_yolov12_uniform.py 2>&1 | tee training.log
```

## Version History

- **v1.0** (Dec 2024): YOLOv12 Complete Uniform Detection System
  - Multi-source detection (webcam, mobile, web)
  - 1/0 output format
  - Support for boys and girls uniforms
