# mobile_client_example.py
# Example client for mobile apps to use the uniform detection API
# Can be adapted for Flutter, React Native, or any mobile platform

import requests
import base64
import json
from PIL import Image
import io

class UniformDetectorClient:
    """Client library for Uniform Detection API"""
    
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if API is running"""
        try:
            response = self.session.get(f"{self.api_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": False}
    
    def detect_from_file(self, image_path, annotated=False):
        """
        Detect uniform from image file
        
        Args:
            image_path: Path to image file
            annotated: Return annotated image in response
        
        Returns:
            dict with detection results
        """
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                params = {'annotated': 'true' if annotated else 'false'}
                response = self.session.post(
                    f"{self.api_url}/detect-image",
                    files=files,
                    params=params,
                    timeout=30
                )
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": False}
    
    def detect_from_base64(self, base64_string, annotated=False):
        """
        Detect uniform from base64 encoded image
        
        Args:
            base64_string: Base64 encoded image data
            annotated: Return annotated image in response
        
        Returns:
            dict with detection results
        """
        try:
            payload = {
                "image": base64_string,
                "annotated": annotated
            }
            response = self.session.post(
                f"{self.api_url}/detect-base64",
                json=payload,
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": False}
    
    def detect_from_pil_image(self, pil_image, annotated=False):
        """
        Detect uniform from PIL Image object
        
        Args:
            pil_image: PIL Image object
            annotated: Return annotated image in response
        
        Returns:
            dict with detection results
        """
        try:
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            pil_image.save(buffered, format="JPEG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            return self.detect_from_base64(img_b64, annotated=annotated)
        except Exception as e:
            return {"error": str(e), "status": False}
    
    def get_config(self):
        """Get current API configuration"""
        try:
            response = self.session.get(f"{self.api_url}/config")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_config(self, config_dict):
        """Update API configuration"""
        try:
            response = self.session.post(
                f"{self.api_url}/config",
                json=config_dict
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_info(self):
        """Get API information"""
        try:
            response = self.session.get(f"{self.api_url}/info")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    print("=== Mobile Uniform Detector API - Client Example ===\n")
    
    # Initialize client
    client = UniformDetectorClient("http://localhost:5000")
    
    # 1. Health check
    print("1. Health Check:")
    health = client.health_check()
    print(f"   Status: {health}\n")
    
    # 2. Get API info
    print("2. API Information:")
    info = client.get_info()
    print(f"   {json.dumps(info, indent=2)}\n")
    
    # 3. Get current config
    print("3. Current Configuration:")
    config = client.get_config()
    print(f"   {json.dumps(config, indent=2)}\n")
    
    # 4. Example detection from image
    print("4. Detect from Image File:")
    print("   Usage: client.detect_from_file('path/to/image.jpg', annotated=True)")
    print("   Returns: Detection results with component status\n")
    
    # 5. Example detection from base64
    print("5. Detect from Base64:")
    print("   Usage: client.detect_from_base64(base64_string, annotated=True)")
    print("   Returns: Detection results with optional annotated image\n")
    
    # 6. Update configuration
    print("6. Update Configuration:")
    print("   Usage: client.update_config({'confidence_threshold': 0.15})")
    print("   Available params: confidence_threshold, min_area, image_size\n")
    
    print("\n=== Mobile Integration Guide ===")
    print("""
For Flutter/React Native apps:

1. Install HTTP client: 
   - Flutter: http or dio package
   - React Native: fetch API or axios

2. Basic detection code:

   // Capture image from camera
   var file = await ImagePicker().pickImage(source: ImageSource.camera);
   
   // Convert to base64
   var bytes = await file.readAsBytes();
   var base64 = base64Encode(bytes);
   
   // Send to API
   var response = await http.post(
     Uri.parse('http://YOUR_SERVER:5000/detect-base64'),
     headers: {'Content-Type': 'application/json'},
     body: jsonEncode({'image': base64, 'annotated': true})
   );
   
   // Parse response
   var result = jsonDecode(response.body);
   print(result['complete_uniform']); // true/false
   print(result['result']); // 1 or 0
   print(result['components']); // Detailed component info

3. Response structure:
   {
     "complete_uniform": true,
     "result": 1,
     "components": {
       "shirt": {"detected": true, "color": "gray", "valid": true},
       "pants": {"detected": true, "color": "navy blue", "valid": true},
       "shoes": {"detected": true, "color": "black", "valid": true},
       "id_card": {"detected": true, "color": "white", "valid": true}
     },
     "detections": [...],
     "timestamp": "2025-12-05T..."
   }

4. Error handling:
   - Check "status" field in response
   - Handle network timeouts (recommend 30s timeout)
   - Retry on failure with exponential backoff
   - Cache results for offline capability
    """)
