# Quick Reference - Mobile Detection API

## 🚀 Start API Server
```bash
python mobile_detector_api.py
```
Server runs on `http://localhost:5000`

## 📱 Test Detection

### Using Python Client
```bash
python mobile_client_example.py
```

### Using cURL
```bash
# Image file upload
curl -X POST -F "image=@photo.jpg" http://localhost:5000/detect-image

# Base64 image
curl -X POST -H "Content-Type: application/json" \
  -d '{"image":"base64_string","annotated":true}' \
  http://localhost:5000/detect-base64

# Health check
curl http://localhost:5000/health

# Get config
curl http://localhost:5000/config

# API info
curl http://localhost:5000/info
```

## 🔄 Response Examples

### Complete Uniform
```json
{
  "status": true,
  "complete_uniform": true,
  "result": 1,
  "components": {
    "shirt": {"detected": true, "color": "gray", "valid": true},
    "pants": {"detected": true, "color": "navy blue", "valid": true},
    "shoes": {"detected": true, "color": "black", "valid": true},
    "id_card": {"detected": true, "color": "white", "valid": true}
  }
}
```

### Incomplete Uniform
```json
{
  "status": true,
  "complete_uniform": false,
  "result": 0,
  "components": {
    "shirt": {"detected": true, "color": "gray", "valid": true},
    "pants": {"detected": false, "color": "none", "valid": false},
    "shoes": {"detected": false, "color": "none", "valid": false},
    "id_card": {"detected": false, "color": "none", "valid": false}
  }
}
```

## 🛠️ API Configuration

### Get Current Config
```bash
curl http://localhost:5000/config
```

### Update Config
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"confidence_threshold":0.15,"image_size":640}' \
  http://localhost:5000/config
```

### Configurable Parameters
- `confidence_threshold`: Detection confidence (0.0-1.0)
- `min_area`: Minimum detection area in pixels
- `image_size`: Input image size (640, 1280, etc.)

## 📱 Mobile Client Examples

### Flutter
```dart
final detector = UniformDetector('http://192.168.1.100:5000');
final result = await detector.detectFromCamera();
if (result['complete_uniform']) {
  print('Access Granted');
}
```

### React Native
```javascript
const response = await axios.post(
  'http://192.168.1.100:5000/detect-base64',
  { image: base64String, annotated: true }
);
if (response.data.result === 1) {
  alert('Access Granted');
}
```

### Android (Kotlin)
```kotlin
val detector = UniformDetectorClient("http://192.168.1.100:5000")
detector.detectFromBitmap(bitmap) { result ->
  val complete = result?.get("complete_uniform") as? Boolean
  if (complete == true) showGranted() else showDenied()
}
```

### iOS (Swift)
```swift
let detector = UniformDetectorClient(apiUrl: "http://192.168.1.100:5000")
detector.detectFromImage(image) { result in
  if result?.complete_uniform == true {
    print("Access Granted")
  }
}
```

## 🌐 Network Configuration

### Find Server IP
- **Windows**: `ipconfig` (look for IPv4 Address)
- **Mac/Linux**: `ifconfig` or `ip addr`

### Firewall Rules
- Allow port 5000 for internal network
- For internet: Use VPN or cloud deployment
- Test with: `telnet 192.168.1.100 5000`

## 📊 Expected Outputs

| Input | Output | Meaning |
|-------|--------|---------|
| `"result": 1` | Access Granted | Complete uniform detected |
| `"result": 0` | Access Denied | Incomplete uniform |
| `"status": false` | Error | Detection failed |

## ⚡ Performance Tips

1. **Fast Detection**: Reduce `image_size` to 640
2. **Better Accuracy**: Increase `image_size` to 1280
3. **Lighting**: Ensure good lighting in camera feed
4. **Distance**: Optimal distance 1-3 meters
5. **Timeout**: Set client timeout to 30 seconds

## 🔐 Security Notes

- API runs on localhost by default
- For production: Add authentication (API keys)
- Use HTTPS if exposed to internet
- Validate image size (max 50MB)
- Rate limit requests if needed
- Log all detections for audit

## 📝 Database Integration

### Store Detection Results
```python
import sqlite3
from datetime import datetime

db = sqlite3.connect('detections.db')
db.execute("""
CREATE TABLE IF NOT EXISTS detections (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  result INTEGER,
  shirt_color TEXT,
  pants_color TEXT,
  shoes_detected INTEGER,
  id_card_detected INTEGER
)
""")

# Insert detection
db.execute(
  "INSERT INTO detections VALUES (?, ?, ?, ?, ?, ?, ?)",
  (None, datetime.now(), result, shirt_color, pants_color, shoes_ok, id_ok)
)
db.commit()
```

## 🔧 Troubleshooting

### API Not Responding
```bash
# Test if running
curl http://localhost:5000/health

# Check if port is in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Mac/Linux
```

### Image Detection Issues
- Check image size: should be < 50MB
- Verify base64 encoding is valid
- Ensure image is JPEG/PNG format
- Try with annotated=true for debugging

### Mobile App Connection Issues
```
1. Verify both devices on same network
2. Disable VPN if connected
3. Check firewall allows port 5000
4. Use actual IP, not localhost
5. Ensure camera permission granted
```

## 📚 Documentation Files

- `detect_and_classify_improved.py` - Main detection engine
- `mobile_detector_api.py` - REST API server
- `mobile_client_example.py` - Python client library
- `AndroidUniformDetector.kt` - Android implementation
- `MOBILE_INTEGRATION_GUIDE.md` - Full integration guide
- `QUICK_REFERENCE.md` - This file

## 🎯 Next Steps

1. ✅ Run API server
2. ✅ Test with Python client
3. ✅ Choose mobile platform (Flutter/React/Android/iOS)
4. ✅ Implement camera integration
5. ✅ Add UI for results display
6. ✅ Deploy to production

---

**Last Updated**: December 5, 2025
**Status**: Production Ready ✓
