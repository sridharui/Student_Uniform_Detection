# Uniform Detection System

## Quick Start

To run the uniform detector:

### Option 1: Direct Python
```bash
python uniform_detector_system.py
```

### Option 2: Using Run Scripts
```bash
# Windows Batch
run_uniform.bat

# PowerShell
.\run_uniform.ps1
```

## Project Structure

### Main Files (Essential for Detection)
- **uniform_detector_system.py** - Main detection system
- **requirements.txt** - Python dependencies
- **yolo11n.pt** - YOLO 11 pretrained model (fallback)
- **yolov8m.pt** - YOLO 8 pretrained model (fallback)
- **runs/** - Trained models directory
  - `runs/train/uniform_detector_yolov11_cpu/weights/best.pt` - Primary model
- **run_uniform.bat** - Windows batch script to run detector
- **run_uniform.ps1** - PowerShell script to run detector

### Folders
- **scrap_files/** - Archive of old/experimental files
- **.venv/** - Python virtual environment

## How It Works

The system detects if a student is wearing complete uniform:

### For Boys:
- ✅ Identity Card
- ✅ Shirt
- ✅ Pant
- ✅ Shoes

### For Girls:
- ✅ Identity Card
- ✅ Top
- ✅ Pant
- ✅ Shoes

### Output
- **1** = Complete uniform detected
- **0** = Incomplete uniform (missing items shown in terminal)

### Controls
- Press **Q** to quit the detection window
- Press **S** to save current frame

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

## Model Information

The system uses trained YOLO models with a confidence threshold of 0.5 for detection.
