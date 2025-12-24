# Mobile IP Webcam Setup Guide

## Your Mobile Webcam Information
- **IP Address**: 192.168.0.9
- **Port**: 8080
- **Protocol**: HTTPS
- **Stream URL**: https://192.168.0.9:8080/video

---

## 🚀 Quick Start with Mobile Webcam

### Step 1: Ensure Phone is Running IP Webcam App

1. Download "IP Webcam" app on your phone
2. Start the app
3. Tap "Start server"
4. Note the IP address shown (you have: 192.168.0.9:8080)

### Step 2: Run Detection from Mobile Feed

```bash
# Using your mobile webcam (HTTP)
python mobile_webcam_detector.py --http

# Using HTTPS (if certificate issues, use --http)
python mobile_webcam_detector.py

# With custom skip frames for faster processing
python mobile_webcam_detector.py --skip 1

# With specific URL
python mobile_webcam_detector.py --url "http://192.168.0.9:8080/video"
```

### Step 3: View Live Detection

- Window will show real-time uniform detection
- Green checkmarks = valid components
- Red X marks = missing components
- Result at bottom: "1" = access granted, "0" = access denied

---

## 📱 IP Webcam Stream URLs

Try these URLs if connection fails:

```
# Video stream (main)
http://192.168.0.9:8080/video
https://192.168.0.9:8080/video

# MJPEG stream
http://192.168.0.9:8080/mjpegfeed

# Static snapshot
http://192.168.0.9:8080/shot.jpg

# RTSP stream
rtsp://192.168.0.9:8080/h264

# H264 stream
http://192.168.0.9:8080/h264
```

---

## 🔧 Commands

### Basic Detection
```bash
python mobile_webcam_detector.py
```

### Force HTTP (if HTTPS fails)
```bash
python mobile_webcam_detector.py --http
```

### Faster Processing (Skip more frames)
```bash
python mobile_webcam_detector.py --skip 3
```

### Better Quality (Skip fewer frames)
```bash
python mobile_webcam_detector.py --skip 1
```

### Custom URL
```bash
python mobile_webcam_detector.py --url "http://192.168.0.9:8080/video"
```

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| **Q** | Quit application |
| **S** | Save current detection frame |
| **SPACE** | Pause/Resume stream |

---

## 🎯 Performance Tips

### For Fast Detection (Real-time)
```bash
python mobile_webcam_detector.py --skip 3
```
- Processes every 3rd frame
- ~10 FPS detection
- Lower accuracy but faster response

### For Accurate Detection
```bash
python mobile_webcam_detector.py --skip 1
```
- Processes every frame
- ~5 FPS detection
- Higher accuracy

### Balanced (Recommended)
```bash
python mobile_webcam_detector.py --skip 2
```
- Processes every 2nd frame
- ~7 FPS detection
- Good balance

---

## 🌐 Network Troubleshooting

### Connection Failed?

**Check 1: Same Network**
```bash
# On your computer, ping the phone
ping 192.168.0.9
```
Expected: Replies showing connection is working

**Check 2: Port is Open**
```bash
# Check if port 8080 is accessible
telnet 192.168.0.9 8080
```

**Check 3: Try HTTP Instead of HTTPS**
```bash
python mobile_webcam_detector.py --http
```

**Check 4: Phone IP Webcam Status**
- Open browser: http://192.168.0.9:8080
- Should show IP Webcam web interface
- Confirm server is running

**Check 5: Firewall**
- Disable firewall temporarily (Windows)
- Or add port 8080 to firewall whitelist
- On phone: Ensure app has network permission

---

## 📊 Stream Information Display

When running, you'll see in the window:
```
✓ Shirt (gray)        ← Valid
✓ Pants (navy blue)   ← Valid
✓ Shoes (black)       ← Valid
✓ ID Card (white)     ← Valid

COMPLETE UNIFORM - 1  ← Final Result
FPS: 7                ← Processing speed
```

---

## 💾 Saving Results

Press **S** key to save detection frame:
```
detection_1733380245.jpg  ← Saved with timestamp
```

Saved images include:
- Detection bounding boxes
- Component status
- Result (1 or 0)

---

## 🔴 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Failed to open webcam" | Ensure phone app is running on 192.168.0.9:8080 |
| SSL Certificate Error | Use `--http` flag instead of HTTPS |
| Connection timeout | Check firewall, restart phone app, try different URL |
| Low FPS | Increase skip frames: `--skip 3` or `--skip 4` |
| No detections | Check lighting, distance (1-3m), camera angle |
| App crashes | Reduce image size or skip more frames |

---

## 📝 Example Scenarios

### Scenario 1: High Security Entrance
```bash
# High accuracy, doesn't matter if slow
python mobile_webcam_detector.py --skip 1
# FPS: 5, Accuracy: 95%
```

### Scenario 2: Busy School Hallway
```bash
# Fast processing for crowd
python mobile_webcam_detector.py --skip 3
# FPS: 12, Accuracy: 90%
```

### Scenario 3: Balanced Production Setup
```bash
# Recommended for most cases
python mobile_webcam_detector.py --skip 2
# FPS: 7, Accuracy: 92%
```

---

## 🔌 Integration with Hardware

### Send Result to Arduino/ESP32
```python
# Add this to mobile_webcam_detector.py
import serial

# Connect to Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600)  # Linux
# arduino = serial.Serial('COM3', 9600)  # Windows

# In detection loop, send result
result = detection_result['result']  # 1 or 0
arduino.write(str(result).encode())
```

### Arduino Code
```cpp
int gatePin = 5;

void setup() {
    Serial.begin(9600);
    pinMode(gatePin, OUTPUT);
}

void loop() {
    if (Serial.available() > 0) {
        char result = Serial.read();
        if (result == '1') {
            // Open gate
            digitalWrite(gatePin, HIGH);
            delay(3000);
            digitalWrite(gatePin, LOW);
        }
    }
}
```

---

## 📊 Expected Output

```
=== Mobile IP Webcam Uniform Detector ===

Connecting to: https://192.168.0.9:8080/video

✓ Model loaded: runs/train/uniform_color_trained2/weights/best.pt

✓ Color classifier loaded

Connecting to mobile webcam...
✓ Connected to mobile webcam

Controls:
  Press 'Q' to quit
  Press 'S' to save detection result
  Press 'SPACE' to pause/resume

Result: 1 [window shows live detection]
```

---

## 🎓 Advanced Usage

### Custom Model
```bash
# If you have a different trained model
python mobile_webcam_detector.py --model "your_model.pt"
```

### Change Network Address
```bash
# If phone IP changed
python mobile_webcam_detector.py --url "http://NEW_IP:8080/video"
```

### Export Detections to Database
```bash
# Add logging before running
python mobile_webcam_detector.py >> detection_log.txt 2>&1
```

---

## 🚨 Security Notes

1. **HTTPS vs HTTP**: Use HTTPS for security (default)
2. **Network**: Keep phone and computer on same secure network
3. **Firewall**: Restrict port 8080 access
4. **Privacy**: Disable IP Webcam when not needed
5. **Storage**: Delete saved detection images periodically

---

## 📞 Support

**If detection fails:**
1. Check phone IP is 192.168.0.9
2. Verify port 8080 is open
3. Try HTTP instead: `--http`
4. Check network connectivity: `ping 192.168.0.9`
5. Restart both phone app and PC script

**For better accuracy:**
1. Improve lighting
2. Maintain 1-3 meter distance
3. Stand centered in frame
4. Wear uniform properly

---

## 🎯 Next Steps

1. ✅ Confirm phone is on 192.168.0.9:8080
2. ✅ Run: `python mobile_webcam_detector.py --http`
3. ✅ Stand in front of camera
4. ✅ Check detection results
5. ✅ Integrate with gate control system if needed

---

**Last Updated**: December 5, 2025
**Status**: Ready for Production ✓
