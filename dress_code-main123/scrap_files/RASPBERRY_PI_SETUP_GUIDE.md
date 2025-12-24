# Raspberry Pi 4 Model B - Uniform Detection System Setup Guide

## Part 1: Raspberry Pi 4 Specifications & Pinout

### 1.1 Raspberry Pi 4 Model B Specifications
- **Processor**: Broadcom BCM2711 Quad-core 1.5 GHz
- **RAM Options**: 2GB, 4GB, or 8GB LPDDR4
- **GPIO Pins**: 40 pins (28 GPIO + 12 power/ground)
- **Camera Port**: CSI (Camera Serial Interface) - for Pi Camera Module
- **USB Ports**: 4x USB 3.0 (2x) + USB 2.0 (2x)
- **Power**: USB-C (5V 3A minimum recommended)
- **Video Out**: Micro HDMI (dual display support)

### 1.2 GPIO Pinout Diagram (Top View)

```
     [3.3V] [5V]
     GPIO2  GPIO3
     GPIO4  [GND]
     GPIO17 GPIO27
     GPIO22 GPIO10
     GPIO9  GPIO11
     GPIO5  GPIO6
     GPIO13 GPIO19
     GPIO26 GPIO14
     GPIO20 GPIO21
     GPIO25 GPIO8
     GPIO24 GPIO7
     GPIO23 GPIO18
     GPIO15 GPIO14 (marked)
     GPIO11 GPIO17
     [GND] [GND]
```

### 1.3 Important Pin Functions for This Project

| Pin # | GPIO | Function | Purpose |
|-------|------|----------|---------|
| 1,17  | - | 3.3V Power | Power supply for sensors |
| 2,4   | - | 5V Power | Power supply for high-draw devices |
| 6,9,14,20,25,30,34,39 | - | GND (Ground) | Reference ground |
| 3     | GPIO2 | SDA (I2C) | Data line for I2C devices |
| 5     | GPIO3 | SCL (I2C) | Clock line for I2C devices |
| 7     | GPIO4 | General I/O | GPIO usage |
| 8     | GPIO14 | UART TX | Serial transmission |
| 10    | GPIO15 | UART RX | Serial reception |

**Camera Connection**: CSI Port (ribbon cable, not GPIO)
**USB Camera Alternative**: Any UVC-compatible USB webcam

---

## Part 2: Hardware Setup

### 2.1 What You'll Need

**Essential:**
- Raspberry Pi 4 Model B (4GB or 8GB recommended)
- Power supply (USB-C, 5V 3A+)
- MicroSD Card (32GB+ recommended, Class 10 or higher)
- USB card reader for microSD
- HDMI cable + monitor/TV (for initial setup)
- USB keyboard and mouse (for initial setup)
- Ethernet cable OR WiFi (built-in)

**For Camera:**
- **Option A**: Raspberry Pi Camera Module v2 (8MP)
- **Option B**: USB Webcam (UVC compatible)

**Optional (for performance monitoring):**
- Small cooling case with heatsinks
- Cooling fan (if doing heavy inference)

### 2.2 Physical Assembly

1. **Insert MicroSD Card**:
   - Open the microSD card slot (bottom of board, near USB ports)
   - Insert card into slot until it clicks
   - Card should be flush with the board

2. **Connect Camera (if using Pi Camera)**:
   - Locate the CSI camera port (between USB and HDMI ports)
   - Lift the black latch gently
   - Insert ribbon cable with contacts facing away from USB ports
   - Push latch down to secure

3. **Connect Power**:
   - Use USB-C power connector (near USB ports)
   - Don't power on yet

4. **Connect Display & Peripherals**:
   - HDMI to monitor
   - USB keyboard and mouse to USB ports
   - Ethernet cable (optional, WiFi also available)

---

## Part 3: Operating System Installation

### 3.1 Download Raspberry Pi OS

1. Go to [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)
2. Download **Raspberry Pi Imager**
3. Install it on your Windows PC

### 3.2 Flash MicroSD Card

1. Insert microSD card into card reader on your Windows PC
2. Open Raspberry Pi Imager
3. Click **"Choose Device"** → Select **"Raspberry Pi 4"**
4. Click **"Choose OS"** → Select **"Raspberry Pi OS (64-bit)"** (Bookworm is latest)
5. Click **"Choose Storage"** → Select your microSD card
6. Click **"Next"**
7. When prompted for customization:
   - ✓ Set hostname: `rpi4-uniform-detector`
   - ✓ Enable SSH (important for remote access)
   - ✓ Set username/password (default: `pi` / `raspberry`)
   - ✓ Configure WiFi with your network
   - ✓ Set timezone
8. Click **"Save"** and confirm
9. Wait for flashing to complete (~5 minutes)
10. Eject microSD card safely

---

## Part 4: Initial Raspberry Pi Setup

### 4.1 First Boot

1. Insert flashed microSD card into Raspberry Pi
2. Connect HDMI, keyboard, mouse, power
3. Power on by plugging in USB-C
4. Wait 2-3 minutes for first boot (system configurations)
5. You'll see desktop environment

### 4.2 Update System

Open Terminal and run:
```bash
sudo apt-get update
sudo apt-get upgrade -y
```
This takes 5-10 minutes. **Let it complete fully.**

### 4.3 Enable Camera Interface (if using Pi Camera)

1. Open Terminal
2. Run: `sudo raspi-config`
3. Navigate: **3 Interface Options** → **I1 Legacy Camera** → **Yes** → **Finish**
4. Reboot: `sudo reboot`

---

## Part 5: Install Python Dependencies

### 5.1 Install Python Development Tools

```bash
sudo apt-get install -y python3-pip python3-dev python3-venv
sudo apt-get install -y git wget nano
```

### 5.2 Install OpenCV & YOLO Dependencies

```bash
sudo apt-get install -y libatlas-base-dev
sudo apt-get install -y libjasper-dev
sudo apt-get install -y libtiff-dev libjasper-dev libharfp-dev
sudo apt-get install -y libwebp6 libtiff5 libjasper1 libharfp0c2
sudo apt-get install -y libcamera0 libcamera-dev
```

### 5.3 Create Python Virtual Environment

```bash
cd ~
python3 -m venv yolo_env
source yolo_env/bin/activate
```

### 5.4 Install Python Packages

```bash
pip install --upgrade pip
pip install numpy
pip install opencv-python
pip install ultralytics
pip install flask
pip install requests
```

**For Raspberry Pi 4 ARM64, this takes 20-30 minutes.**

---

## Part 6: Deploy Your Code

### 6.1 Transfer Your Code to Raspberry Pi

**Option A: Via SSH (recommended)**

On your Windows PC, open PowerShell:
```powershell
# Copy your project folder
scp -r "d:\DCM VSCode\dress_code-main123\SDRS" pi@rpi4-uniform-detector.local:~/uniform_detection
```

**Option B: Via Git**

On Raspberry Pi Terminal:
```bash
cd ~
git clone [your-repo-url]
cd dress_code-main123/SDRS
```

### 6.2 Verify Transfer

```bash
ls ~/uniform_detection/
```

Should show: `uniform_detector_system.py`, `web_uniform_detector.py`, etc.

### 6.3 Test Installation

```bash
cd ~/uniform_detection
source ~/yolo_env/bin/activate

# Test import
python3 -c "import cv2; import ultralytics; print('All imports successful')"
```

---

## Part 7: Configure for Raspberry Pi Hardware

### 7.1 Create Pi-Specific Configuration File

Create `pi_config.py`:

```python
# Pi-specific configurations
import os
import platform

# Detect if running on Raspberry Pi
IS_RASPBERRY_PI = os.path.exists('/proc/device-tree/model')

# Hardware configurations
CONFIGS = {
    'camera_type': 'pi_camera',  # or 'usb_camera'
    'model_size': 'nano',  # 'nano' for Pi (lighter weight)
    'inference_device': 'cpu',  # Pi4 CPU is sufficient for nano model
    'max_fps': 15,  # Reduced for Pi
    'frame_size': (320, 240),  # Lower resolution for speed
    'confidence_threshold': 0.5,
}

if IS_RASPBERRY_PI:
    print("Running on Raspberry Pi 4")
    # Pi-specific optimizations
    os.environ['OPENBLAS_CORETYPE'] = 'NEON'
else:
    print("Running on Desktop")
```

### 7.2 Modify Your Detection Script for Pi

Update `uniform_detector_system.py`:

```python
# Add at top
import platform
IS_PI = platform.machine().startswith('arm')

# In your model initialization
if IS_PI:
    model = YOLO('yolov11n.pt')  # Use nano model on Pi
else:
    model = YOLO('yolov11m.pt')  # Use medium model on desktop

# Reduce frame size on Pi
if IS_PI:
    frame_width = 320
    frame_height = 240
else:
    frame_width = 640
    frame_height = 480
```

---

## Part 8: Run Your Detection System

### 8.1 Test with Pi Camera

```bash
cd ~/uniform_detection
source ~/yolo_env/bin/activate

python3 -c "
from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

frame = picam2.capture_array()
print(f'Camera working! Frame shape: {frame.shape}')
picam2.close()
"
```

### 8.2 Run Uniform Detection

```bash
cd ~/uniform_detection
source ~/yolo_env/bin/activate

python3 mobile_webcam_detector.py
```

Or for web interface:
```bash
python3 web_uniform_detector.py --host 0.0.0.0 --port 5000
```

Access from your PC: `http://rpi4-uniform-detector.local:5000`

---

## Part 9: GPIO Control (Optional - for LED indicators)

### 9.1 GPIO Pin Usage Example

```python
import RPi.GPIO as GPIO

# Setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setup(17, GPIO.OUT)  # GPIO17 as output (Pin 11)
GPIO.setup(27, GPIO.IN)   # GPIO27 as input (Pin 13)

# Control LED (connected to GPIO17)
GPIO.output(17, GPIO.HIGH)   # Turn ON
GPIO.output(17, GPIO.LOW)    # Turn OFF

# Read button (connected to GPIO27)
if GPIO.input(27):
    print("Button pressed")

# Cleanup
GPIO.cleanup()
```

### 9.2 GPIO Wiring Example (LED Indicator)

```
LED Circuit:
3.3V (Pin 1) 
  ↓
LED (any color)
  ↓
330Ω Resistor
  ↓
GPIO17 (Pin 11)
  ↓
GND (Pin 6/9/14/20/25/30/34/39)

Connections:
- 3.3V → LED positive leg
- LED negative leg → 330Ω Resistor → GPIO17
- GND pin → LED circuit ground
```

---

## Part 10: Performance Optimization

### 10.1 Reduce Memory Usage

```bash
# Disable GUI (if not needed)
sudo raspi-config
# 1 System Options → S5 Boot → B1 Console (Text)

# Reduce swap file size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 (reduce from default)
sudo dphys-swapfile setup
sudo reboot
```

### 10.2 Enable Hardware Acceleration

```bash
# Already included in Pi OS Bookworm
# OpenGL/OpenCV will use GPU acceleration automatically
```

### 10.3 Monitor Performance

```bash
# Check CPU/RAM usage
top

# Check temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled
```

---

## Part 11: Run on Startup (Optional)

### 11.1 Create Systemd Service

```bash
sudo nano /etc/systemd/system/uniform-detector.service
```

Add:
```ini
[Unit]
Description=Uniform Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/uniform_detection
Environment="PATH=/home/pi/yolo_env/bin"
ExecStart=/home/pi/yolo_env/bin/python3 web_uniform_detector.py --host 0.0.0.0 --port 5000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable uniform-detector.service
sudo systemctl start uniform-detector.service
```

Check status:
```bash
sudo systemctl status uniform-detector.service
```

---

## Part 12: Troubleshooting

### Camera Issues
```bash
# Test camera
libcamera-hello -t 5

# List cameras
libcamera-hello --list-cameras
```

### SSH Connection
```bash
# From Windows PowerShell
ssh pi@rpi4-uniform-detector.local
# Default password: raspberry

# Or use IP address
ping rpi4-uniform-detector.local  # Find IP
ssh pi@192.168.x.x
```

### Slow Performance
- Use smaller model: `yolov11n.pt` (nano)
- Reduce frame resolution to 320x240
- Check CPU temperature: `vcgencmd measure_temp`
- If >80°C, add cooling

### Import Errors
```bash
# Reinstall specific package
pip uninstall ultralytics
pip install ultralytics --no-cache-dir
```

---

## Quick Reference Commands

```bash
# Activate virtual environment
source ~/yolo_env/bin/activate

# Deactivate
deactivate

# Check Python version
python3 --version

# Check installed packages
pip list

# Connect via SSH
ssh pi@rpi4-uniform-detector.local

# Copy files from Windows PC
scp -r "local/path" pi@rpi4-uniform-detector.local:~/remote/path

# Reboot Raspberry Pi
sudo reboot

# Shutdown safely
sudo shutdown -h now
```

---

## Next Steps

1. **Flash OS and boot** → Basic setup takes ~30 minutes
2. **Install dependencies** → Takes ~30-40 minutes
3. **Transfer code** → Takes ~5 minutes
4. **Test detection** → First run ~2-3 minutes (model loads)
5. **Deploy web interface** → Access via browser
6. **Add GPIO controls** (optional) → 10 minutes

**Total setup time: ~2-3 hours for complete deployment**

