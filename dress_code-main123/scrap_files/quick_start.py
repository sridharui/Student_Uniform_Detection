"""
Quick Start Guide for YOLOv12 Uniform Detection
Run this to understand the complete workflow
"""

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_step(num, title, description, command):
    print(f"\n📍 STEP {num}: {title}")
    print(f"   Description: {description}")
    print(f"   Command: {command}")

def main():
    print_header("YOLOv12 COMPLETE UNIFORM DETECTION - QUICK START")
    
    print("""
This guide will help you set up and run the complete uniform detection system.
The system can detect if a student is wearing a complete uniform (Output: 1) or not (Output: 0).

WHAT IS A COMPLETE UNIFORM?

📚 FOR BOYS:
   ✓ Identity Card (Lanyard/Badge)
   ✓ Shirt (White or Gray color)
   ✓ Pant (Black/Navy Blue color)
   ✓ Shoes (Any color)
   → If all present = COMPLETE UNIFORM (Output: 1)
   → If any missing = INCOMPLETE UNIFORM (Output: 0)

👧 FOR GIRLS:
   ✓ Identity Card (Lanyard/Badge)
   ✓ Top (White or Gray color)
   ✓ Pant (Black/Navy Blue color)
   ✓ Shoes (Any color)
   → If all present = COMPLETE UNIFORM (Output: 1)
   → If any missing = INCOMPLETE UNIFORM (Output: 0)

YOUR DATASETS:
   📁 Complete_Uniform.v3i.yolov12/ - Students WITH complete uniforms (train/valid/test splits)
   📁 No_Uniform.v1i.yolov12/       - Students WITHOUT complete uniforms (validation)
    """)
    
    print_header("WORKFLOW OVERVIEW")
    
    print("""
┌─────────────────────────────────────────────────────────────┐
│  1. VERIFY SETUP                                            │
│     Check datasets, dependencies, and directories           │
│                                                             │
│  2. TRAIN MODEL                                             │
│     Train YOLOv12 on Complete_Uniform dataset              │
│     Test on Complete_Uniform test set                      │
│     Validate on No_Uniform dataset                         │
│                                                             │
│  3. RUN DETECTIONS (Choose any or all):                     │
│     A. Laptop Webcam - Real-time detection                 │
│     B. Mobile Remote - Web server for mobile apps          │
│     C. Web Application - Upload images for testing         │
│                                                             │
│  4. GET RESULTS                                             │
│     Terminal: Prints 1 (Complete) or 0 (Incomplete)        │
│     Web/Mobile: JSON response with status                  │
└─────────────────────────────────────────────────────────────┘
    """)
    
    print_header("DETAILED STEPS")
    
    print_step(
        1,
        "VERIFY YOUR SETUP",
        "Check if all datasets, dependencies, and scripts are in place",
        "python verify_setup.py"
    )
    
    print("""
    This will check:
    ✓ Python version (3.8+)
    ✓ Required packages installed
    ✓ Dataset structure (Complete_Uniform and No_Uniform)
    ✓ Output directories exist
    ✓ All scripts present
    
    Expected Output:
    ✅ All checks passed! Ready to train the model.
    """)
    
    print_step(
        2,
        "TRAIN THE MODEL",
        "Train YOLOv12 on your uniform dataset (this takes 30-60 minutes on GPU)",
        "python train_yolov12_uniform.py"
    )
    
    print("""
    This will:
    ✅ Train YOLOv12 on Complete_Uniform dataset
    ✅ Validate on Complete_Uniform test set
    ✅ Test on No_Uniform validation set
    ✅ Save best model to: runs/train/uniform_detector_yolov12/weights/best.pt
    
    Expected Output:
    ============================================================================
    YOLOv12 UNIFORM DETECTION TRAINING
    ============================================================================
    ✅ Complete Uniform dataset found
    ✅ No Uniform dataset found
    
    ============================================================================
    STEP 1: Training on COMPLETE_UNIFORM Dataset
    ============================================================================
    [Training progress with epoch information...]
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
    
    ⏱️  Time: ~30-60 minutes on GPU, ~2-3 hours on CPU
    """)
    
    print_step(
        3,
        "RUN DETECTIONS - OPTION A: LAPTOP WEBCAM",
        "Real-time uniform detection from your laptop camera",
        "python uniform_detector_system.py"
    )
    
    print("""
    This will:
    ✓ Open your webcam
    ✓ Detect uniform components in real-time
    ✓ Show COMPLETE UNIFORM or INCOMPLETE UNIFORM
    ✓ Print status (1 = Complete, 0 = Incomplete) to terminal
    
    Controls:
    📷 Live detection shows on screen
    🖨️  Results printed to terminal
    q = Quit
    c = Capture screenshot
    
    Expected Terminal Output (Complete Uniform):
    ✓ Detected: Identity Card (confidence: 0.92)
    ✓ Detected: Shirt (confidence: 0.88)
    ✓ Detected: pant (confidence: 0.85)
    ✓ Detected: shoes (confidence: 0.91)
    
    ✅ COMPLETE UNIFORM (BOYS) - Student is properly dressed
    Status: 1
    
    Expected Terminal Output (Incomplete Uniform):
    ✓ Detected: Shirt (confidence: 0.85)
    ✓ Detected: pant (confidence: 0.82)
    
    ❌ INCOMPLETE UNIFORM (BOYS) - Missing: Identity Card, shoes
    Status: 0
    """)
    
    print_step(
        3,
        "RUN DETECTIONS - OPTION B: MOBILE WEBCAM",
        "Deploy a web server for remote detection from mobile devices",
        "python mobile_webcam_detector_v2.py"
    )
    
    print("""
    This will:
    ✓ Start web server on http://localhost:5000
    ✓ Provide REST API for image uploads
    ✓ Return uniform detection status (1 or 0) as JSON
    
    Usage:
    1. Start server: python mobile_webcam_detector_v2.py
    2. Access from mobile: http://<your-computer-ip>:5000
    3. Upload image or take photo
    4. Get instant result: {"uniform_status": 1 or 0}
    
    Expected Output:
    ================================================================================
    MOBILE UNIFORM DETECTION SERVER
    ================================================================================
    Model: runs/train/uniform_detector_yolov12/weights/best.pt
    Server: http://localhost:5000
    API: http://localhost:5000/api/detect
    ================================================================================
    
    API Response (Complete Uniform):
    {
      "status": "success",
      "uniform_status": 1,
      "message": "✅ COMPLETE UNIFORM",
      "uniform_type": "BOYS",
      "detected_items": ["Identity Card", "Shirt", "pant", "shoes"]
    }
    
    API Response (Incomplete Uniform):
    {
      "status": "success",
      "uniform_status": 0,
      "message": "❌ INCOMPLETE UNIFORM",
      "uniform_type": "INCOMPLETE",
      "detected_items": ["Shirt", "pant"]
    }
    """)
    
    print_step(
        3,
        "RUN DETECTIONS - OPTION C: WEB APPLICATION",
        "Upload images to test detection via web interface",
        "python web_uniform_detector.py"
    )
    
    print("""
    This will:
    ✓ Start web server on http://localhost:8080
    ✓ Provide web interface for image uploads
    ✓ Display processed images with detection boxes
    ✓ Show uniform status (1 or 0)
    
    Usage:
    1. Start: python web_uniform_detector.py
    2. Open: http://localhost:8080
    3. Click "Choose File" and select an image
    4. View results on processed image
    5. Terminal shows detailed detection info
    
    Expected Output:
    ============================================================
      WEB UNIFORM DETECTION SYSTEM
    ============================================================
    
    📸 Test with images before going live
    🎯 Upload uniform/non-uniform images
    🚀 Run live detection after testing
    
    Server starting at: http://localhost:8080
    Press Ctrl+C to stop
    
    ============================================================
    
     * Running on http://127.0.0.1:8080
    
    Web Response (Complete Uniform):
    {
      "complete_uniform": true,
      "result": 1,
      "detections": [
        {"class": "id_card", "conf": 0.92, "color": "white"},
        {"class": "shirt", "conf": 0.88, "color": "white"},
        {"class": "pant", "conf": 0.85, "color": "black"},
        {"class": "shoes", "conf": 0.91, "color": "black"}
      ],
      "status": {
        "shirt": {"ok": true, "color": "white"},
        "pant": {"ok": true, "color": "black"},
        "shoes": {"ok": true, "color": "black"},
        "id_card": {"ok": true, "color": "white"}
      }
    }
    """)
    
    print_step(
        4,
        "INTERPRET RESULTS",
        "Understanding the output format",
        "Check your output carefully"
    )
    
    print("""
    TERMINAL OUTPUT FORMAT:
    
    ✅ COMPLETE UNIFORM (BOYS) or (GIRLS)
    Status: 1
    → Means: Student has all required uniform components
    
    ❌ INCOMPLETE UNIFORM (BOYS) or (GIRLS)
    Missing: Identity Card, shoes
    Status: 0
    → Means: Student is missing some uniform components
    
    WEB/API OUTPUT FORMAT:
    
    {"uniform_status": 1}  → Complete
    {"uniform_status": 0}  → Incomplete
    {"uniform_status": -1} → Error
    
    DETECTION REQUIREMENTS:
    
    Boys must have:    Identity Card + Shirt + Pant + Shoes
    Girls must have:   Identity Card + Top + Pant + Shoes
    
    Color Requirements:
    Shirt/Top:  White or Gray only
    Pant:       Black, Navy Blue, or Dark Blue only
    Shoes:      Any color
    ID Card:    Any color
    """)
    
    print_header("TROUBLESHOOTING")
    
    print("""
    Problem: "Model not found"
    Solution: Run training first: python train_yolov12_uniform.py
    
    Problem: "ImportError: No module named 'ultralytics'"
    Solution: Install dependencies: pip install -r requirements.txt
    
    Problem: "Poor detection quality"
    Solution 1: Ensure Complete_Uniform dataset has enough images
    Solution 2: Increase training epochs (epochs=150 in train script)
    Solution 3: Use lower confidence threshold (CONF_THRESHOLD = 0.3)
    
    Problem: "GPU out of memory"
    Solution: Reduce batch size or use CPU: device='cpu' in train script
    
    Problem: "Cannot open camera"
    Solution: Check if webcam is being used by another app
    """)
    
    print_header("FILE LOCATIONS")
    
    print("""
    Training script:          train_yolov12_uniform.py
    Laptop detection:         uniform_detector_system.py
    Mobile/Remote server:     mobile_webcam_detector_v2.py
    Web application:          web_uniform_detector.py
    Setup verification:       verify_setup.py
    This guide:               quick_start.py
    
    Training dataset:         Complete_Uniform.v3i.yolov12/
    Validation dataset:       No_Uniform.v1i.yolov12/
    
    Trained model:            runs/train/uniform_detector_yolov12/weights/best.pt
    Web uploads:              uploads/
    Mobile uploads:           mobile_uploads/
    Web results:              static/
    
    Documentation:            YOLOV12_SETUP_GUIDE.md
    """)
    
    print_header("NEXT STEPS")
    
    print("""
    1️⃣  Start here: python verify_setup.py
        Check if everything is ready
    
    2️⃣  Train the model: python train_yolov12_uniform.py
        Takes 30-60 minutes on GPU
    
    3️⃣  Test your setup (choose one or all):
        - python uniform_detector_system.py        (Laptop webcam)
        - python mobile_webcam_detector_v2.py      (Mobile server)
        - python web_uniform_detector.py           (Web app)
    
    4️⃣  Check detailed guide: YOLOV12_SETUP_GUIDE.md
        Complete documentation with examples
    """)
    
    print_header("KEY FEATURES")
    
    print("""
    ✅ Detects Complete Uniform: Output 1
    ❌ Detects Incomplete Uniform: Output 0
    
    ✓ Supports Boys and Girls uniforms
    ✓ Real-time detection from webcam
    ✓ Mobile app integration via REST API
    ✓ Web application for testing
    ✓ Color validation (shirt/top, pant)
    ✓ Multiple detection sources (laptop, mobile, web)
    ✓ Detailed component detection
    ✓ High accuracy with YOLOv12
    
    📊 Expected Performance:
       - Training time: 30-60 min (GPU) / 2-3 hours (CPU)
       - Inference speed: ~50ms per image (GPU)
       - Accuracy: >85% mAP50
    """)
    
    print("\n" + "=" * 80)
    print("Good luck! 🚀")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
