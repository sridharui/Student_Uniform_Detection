# Setup & Installation Guide - Boys & Girls Uniform Detection

## Prerequisites

### System Requirements
- **Python:** 3.8 or higher
- **OS:** Windows, macOS, or Linux
- **RAM:** 4GB minimum (8GB recommended)
- **Disk:** 5GB free space
- **Camera:** Webcam (for real-time detection)

### Python Packages Required
All dependencies are listed in `requirements.txt`

---

## Installation Steps

### Step 1: Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or manually install:
pip install ultralytics>=8.0.0
pip install opencv-python>=4.8.0
pip install torch>=2.0.0
pip install torchvision>=0.15.0
pip install numpy>=1.23.0
pip install pillow>=9.5.0
pip install pyserial>=3.5
```

### Step 2: Verify Installation

```bash
# Run verification script
python verify_system.py
```

This will check:
- ✅ All required files exist
- ✅ Python dependencies installed
- ✅ System enhancements implemented
- ✅ Model files available
- ✅ Basic functionality

### Step 3: Download/Verify Models

The system will automatically use available models:

**Priority Order:**
1. `runs/train/uniform_detector_yolov11_cpu/weights/best.pt` (Custom trained)
2. `runs/train/uniform_detector_yolov12_cpu/weights/best.pt` (Custom trained)
3. `yolo11n.pt` (Generic YOLOv11)
4. `yolov8m.pt` (Generic YOLOv8)

**If you need to train a new model:**
```bash
python -m ultralytics.yolo detect train \
    model=yolov11n.pt \
    data=scrap_files/Complete_Uniform.v3i.yolov12/data.yaml \
    epochs=100
```

---

## Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
python quick_start_boys_girls.py
```

### Option 2: Webcam Detection
```bash
python uniform_detector_system.py
```

### Option 3: Test Image
```bash
python -c "
from uniform_detector_system import UniformDetector
detector = UniformDetector()
result = detector.detect_uniform('your_image.jpg')
print(f'Gender: {result[\"detected_gender\"]}')
print(f'Complete: {result[\"is_complete\"]}')
"
```

---

## Configuration

### Default Model Path
Edit `uniform_detector_system.py` to change model:
```python
detector = UniformDetector(
    model_path="runs/train/uniform_detector_yolov11_cpu/weights/best.pt"
)
```

### Confidence Thresholds
Adjust in `uniform_detector_system.py`:
```python
self.CONF_THRESHOLDS = {
    'Shirt': 0.55,          # Boys shirt
    'top': 0.55,            # Girls top
    'Identity Card': 0.50,
    'pant': 0.50,
    'shoes': 0.50,
}
```

### Serial Port (Arduino)
```bash
python uniform_detector_system.py --serial-port COM3 --baud 9600
```

---

## Troubleshooting Installation

### Issue: "ModuleNotFoundError: No module named 'ultralytics'"
**Solution:**
```bash
pip install ultralytics --upgrade
```

### Issue: "ModuleNotFoundError: No module named 'cv2'"
**Solution:**
```bash
pip install opencv-python
```

### Issue: "ModuleNotFoundError: No module named 'torch'"
**Solution:**
```bash
# For CPU
pip install torch torchvision torchaudio

# For CUDA (if you have GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Camera not found
**Solution:**
```bash
# Try different camera ID
python uniform_detector_system.py --camera 1
python uniform_detector_system.py --camera 2
```

### Issue: Model not loading
**Solution:**
1. Check model file exists in `runs/train/` directory
2. Or let system download generic YOLO model
3. Run: `python verify_system.py` to diagnose

---

## Directory Structure

```
dress_code-main123/
├── uniform_detector_system.py      # Main detection system (UPDATED)
├── quick_start_boys_girls.py       # Interactive menu (NEW)
├── improve_gender_detection.py     # Analysis tool (NEW)
├── test_boys_girls_detection.py    # Testing tool (NEW)
├── verify_system.py                # Verification script (NEW)
│
├── BOYS_GIRLS_DETECTION_GUIDE.md   # Full guide (NEW)
├── IMPLEMENTATION_SUMMARY.md       # Technical summary (NEW)
├── QUICK_REFERENCE.md              # Quick lookup (NEW)
├── IMPLEMENTATION_COMPLETE.md      # Overview (NEW)
├── SETUP_GUIDE.md                  # This file (NEW)
│
├── requirements.txt                # Python dependencies
├── yolo11n.pt                      # Generic model (if present)
├── yolov8m.pt                      # Generic model (if present)
│
├── runs/                           # Training outputs
│   └── train/
│       ├── uniform_detector_yolov11_cpu/
│       │   └── weights/best.pt
│       └── uniform_detector_yolov12_cpu/
│           └── weights/best.pt
│
├── scrap_files/
│   └── Complete_Uniform.v3i.yolov12/  # Training dataset
│       ├── train/
│       ├── valid/
│       └── test/
│
└── __pycache__/                    # Python cache
```

---

## First Time Use Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Verification passed (`python verify_system.py`)
- [ ] Can access webcam
- [ ] Model file available or can be downloaded
- [ ] Read QUICK_REFERENCE.md for basic usage

---

## Running the System

### For Real-Time Webcam Detection
```bash
python quick_start_boys_girls.py
# Then select option 1
```

### For Testing with Images
```bash
python test_boys_girls_detection.py
```

### For Dataset Analysis
```bash
python improve_gender_detection.py
```

### For Single Image Testing
```bash
python -c "
from uniform_detector_system import UniformDetector
import cv2

detector = UniformDetector()
image = cv2.imread('test_image.jpg')
result = detector.detect_uniform(image)

print('=== DETECTION RESULTS ===')
print(f'Gender: {result[\"detected_gender\"]}')
print(f'Complete: {result[\"is_complete\"]}')
print(f'Items: {result[\"detected_items\"]}')
print(f'Missing: {result[\"missing_items\"]}')
print(f'Message: {result[\"message\"]}')
"
```

---

## File Permissions

### On Linux/macOS
```bash
chmod +x quick_start_boys_girls.py
chmod +x uniform_detector_system.py
chmod +x verify_system.py
```

---

## Memory Management

### For Low-Memory Systems
1. Use smaller model: `yolov8n.pt` instead of `yolov11n.pt`
2. Reduce image size: Edit detection code to use smaller images
3. Process every N frames instead of every frame

### For High Performance
1. Use CUDA if available: `device=0` in training
2. Use larger model: `yolov12n.pt` or `yolov12s.pt`
3. Increase batch size during training

---

## GPU Support (Optional)

### Check if GPU Available
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Enable GPU in Training
```bash
python -m ultralytics.yolo detect train \
    model=yolov11n.pt \
    data=scrap_files/Complete_Uniform.v3i.yolov12/data.yaml \
    device=0
```

---

## Docker Support (Optional)

### Run in Docker
```bash
docker run --gpus all -it --rm \
    -v $(pwd):/workspace \
    -w /workspace \
    ultralytics/ultralytics:latest \
    python quick_start_boys_girls.py
```

---

## Updating the System

### Pull Latest Updates
```bash
# If using git
git pull origin main
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Retrain Model
```bash
python improve_gender_detection.py  # Check recommendations
python test_boys_girls_detection.py # Current accuracy

# Retrain if needed
python -m ultralytics.yolo detect train \
    model=yolov11n.pt \
    data=scrap_files/Complete_Uniform.v3i.yolov12/data.yaml \
    epochs=100 \
    name=uniform_detector_improved
```

---

## System Specifications

### Minimum
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Disk: 2 GB
- Processing: ~150ms per frame

### Recommended
- CPU: Quad-core 2.4 GHz+
- RAM: 8 GB
- Disk: 5 GB
- GPU: 4GB VRAM (optional but faster)
- Processing: ~30-50ms per frame with GPU

### Optimal
- CPU: 6+ cores 3.0+ GHz
- RAM: 16+ GB
- Disk: 10+ GB SSD
- GPU: NVIDIA RTX 2080+ or better
- Processing: <20ms per frame

---

## Support & Help

### Verify Installation
```bash
python verify_system.py
```

### Check Documentation
- `QUICK_REFERENCE.md` - Quick lookup
- `BOYS_GIRLS_DETECTION_GUIDE.md` - Detailed guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details

### Debug Issues
```bash
# Run with verbose output
python uniform_detector_system.py  # Shows all detections

# Test specific image
python test_boys_girls_detection.py  # Compare accuracy

# Analyze dataset
python improve_gender_detection.py  # Show recommendations
```

---

## Next Steps After Installation

1. ✅ Run verification: `python verify_system.py`
2. ✅ Try quick start: `python quick_start_boys_girls.py`
3. ✅ Test with webcam (option 1)
4. ✅ Test with image (option 2)
5. ✅ Check accuracy (option 4)
6. ✅ Review guide: `QUICK_REFERENCE.md`
7. ✅ Optimize if needed: `improve_gender_detection.py`

---

## Common Commands

```bash
# Start interactive menu
python quick_start_boys_girls.py

# Verify setup
python verify_system.py

# Test accuracy
python test_boys_girls_detection.py

# Analyze dataset
python improve_gender_detection.py

# Real-time detection
python uniform_detector_system.py

# Test single image
python -c "from uniform_detector_system import UniformDetector; detector = UniformDetector(); result = detector.detect_uniform('image.jpg'); print(result['detected_gender'], result['is_complete'])"
```

---

## Uninstallation

```bash
# Remove Python packages
pip uninstall ultralytics opencv-python torch torchvision numpy pillow pyserial -y

# Or remove virtual environment
deactivate
rm -rf venv/  # or .venv/
```

---

## Success Criteria

After installation, you should be able to:

✅ Run `python verify_system.py` with all checks passing
✅ Launch `python quick_start_boys_girls.py` without errors
✅ Select webcam detection and see real-time output
✅ See gender classification (BOYS or GIRLS)
✅ See detected items and missing items
✅ See status flag (1=complete, 0=incomplete)

---

**Congratulations!** Your uniform detection system is now set up and ready to use.

Start with: `python quick_start_boys_girls.py`

