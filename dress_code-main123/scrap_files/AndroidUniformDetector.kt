// AndroidUniformDetector.kt
// Kotlin implementation for Android mobile app

package com.example.uniformdetector

import android.content.Context
import android.graphics.Bitmap
import android.util.Base64
import android.util.Log
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okio.ByteString
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Uniform Detector API Client for Android
 * 
 * Usage:
 * val detector = UniformDetectorClient("http://192.168.x.x:5000")
 * val result = detector.detectFromBitmap(bitmap) { result ->
 *     if (result["complete_uniform"] == true) {
 *         showAccessGranted()
 *     } else {
 *         showAccessDenied()
 *     }
 * }
 */
class UniformDetectorClient(private val apiUrl: String) {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    companion object {
        private const val TAG = "UniformDetector"
    }
    
    /**
     * Detect uniform from Bitmap image
     * @param bitmap: Android Bitmap from camera
     * @param annotated: If true, returns annotated image in response
     * @param callback: Callback with detection results
     */
    fun detectFromBitmap(
        bitmap: Bitmap,
        annotated: Boolean = false,
        callback: (Map<String, Any>?) -> Unit
    ) {
        Thread {
            try {
                val base64 = bitmapToBase64(bitmap)
                detectFromBase64(base64, annotated, callback)
            } catch (e: Exception) {
                Log.e(TAG, "Error converting bitmap", e)
                callback(null)
            }
        }.start()
    }
    
    /**
     * Detect uniform from Base64 encoded image
     * @param base64String: Base64 encoded image
     * @param annotated: If true, returns annotated image
     * @param callback: Callback with detection results
     */
    fun detectFromBase64(
        base64String: String,
        annotated: Boolean = false,
        callback: (Map<String, Any>?) -> Unit
    ) {
        Thread {
            try {
                val json = JSONObject().apply {
                    put("image", base64String)
                    put("annotated", annotated)
                }
                
                val body = RequestBody.create(
                    "application/json".toMediaType(),
                    json.toString()
                )
                
                val request = Request.Builder()
                    .url("$apiUrl/detect-base64")
                    .post(body)
                    .build()
                
                client.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string() ?: return@use
                        val result = parseResponse(responseBody)
                        callback(result)
                    } else {
                        Log.e(TAG, "API Error: ${response.code}")
                        callback(null)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error in detectFromBase64", e)
                callback(null)
            }
        }.start()
    }
    
    /**
     * Health check to verify API is running
     * @param callback: Callback with health status
     */
    fun healthCheck(callback: (Boolean) -> Unit) {
        Thread {
            try {
                val request = Request.Builder()
                    .url("$apiUrl/health")
                    .get()
                    .build()
                
                client.newCall(request).execute().use { response ->
                    callback(response.isSuccessful)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Health check failed", e)
                callback(false)
            }
        }.start()
    }
    
    /**
     * Get current API configuration
     * @param callback: Callback with config data
     */
    fun getConfig(callback: (Map<String, Any>?) -> Unit) {
        Thread {
            try {
                val request = Request.Builder()
                    .url("$apiUrl/config")
                    .get()
                    .build()
                
                client.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string() ?: return@use
                        val result = parseResponse(responseBody)
                        callback(result)
                    } else {
                        callback(null)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error getting config", e)
                callback(null)
            }
        }.start()
    }
    
    /**
     * Convert Android Bitmap to Base64 string
     */
    private fun bitmapToBase64(bitmap: Bitmap): String {
        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream)
        val byteArray = outputStream.toByteArray()
        return Base64.encodeToString(byteArray, Base64.DEFAULT)
    }
    
    /**
     * Parse JSON response from API
     */
    private fun parseResponse(jsonString: String): Map<String, Any>? {
        return try {
            val json = JSONObject(jsonString)
            mapOf(
                "complete_uniform" to json.optBoolean("complete_uniform"),
                "result" to json.optInt("result"),
                "status" to json.optBoolean("status"),
                "components" to json.optJSONObject("components")?.toMap() ?: emptyMap<String, Any>(),
                "timestamp" to json.optString("timestamp"),
                "error" to json.optString("error")
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing response", e)
            null
        }
    }
    
    private fun JSONObject.toMap(): Map<String, Any> {
        val map = mutableMapOf<String, Any>()
        val keys = keys()
        while (keys.hasNext()) {
            val key = keys.next()
            map[key] = get(key)
        }
        return map
    }
}

// ==================== USAGE EXAMPLE ====================

/**
 * Example Activity for uniform detection
 */
class UniformDetectionActivity : AppCompatActivity() {
    
    private lateinit var detector: UniformDetectorClient
    private lateinit var cameraProvider: ProcessCameraProvider
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize detector (use actual server IP)
        detector = UniformDetectorClient("http://192.168.1.100:5000")
        
        // Check API connectivity
        detector.healthCheck { isHealthy ->
            if (isHealthy) {
                Log.d("UniformDetector", "API is online")
            } else {
                showError("Cannot connect to server")
            }
        }
    }
    
    /**
     * Called when camera captures an image
     */
    private fun onImageCaptured(bitmap: Bitmap) {
        // Show loading
        showLoading(true)
        
        // Send to API for detection
        detector.detectFromBitmap(bitmap, annotated = true) { result ->
            showLoading(false)
            
            if (result == null) {
                showError("Detection failed")
                return@detectFromBitmap
            }
            
            val completeUniform = result["complete_uniform"] as? Boolean ?: false
            val detectionResult = result["result"] as? Int ?: 0
            val components = result["components"] as? Map<String, Any>
            
            // Update UI
            updateDetectionUI(completeUniform, components)
            
            // Log result (for gate control)
            Log.d("UniformDetector", "Result: $detectionResult")
            
            // Could send binary result to Arduino/ESP32 via Bluetooth/Serial
            if (detectionResult == 1) {
                playAccessGrantedSound()
                // triggerGateOpen()
            } else {
                playAccessDeniedSound()
            }
        }
    }
    
    /**
     * Update UI with detection results
     */
    private fun updateDetectionUI(
        complete: Boolean,
        components: Map<String, Any>?
    ) {
        val statusColor = if (complete) Color.GREEN else Color.RED
        val statusText = if (complete) "COMPLETE UNIFORM" else "INCOMPLETE UNIFORM"
        
        // Update UI elements
        // statusView.setBackgroundColor(statusColor)
        // statusView.text = statusText
        
        // Show component details
        components?.let { comps ->
            // shirt.text = "Shirt: ${comps["shirt"]}"
            // pants.text = "Pants: ${comps["pants"]}"
            // shoes.text = "Shoes: ${comps["shoes"]}"
            // idCard.text = "ID Card: ${comps["id_card"]}"
        }
    }
    
    private fun showLoading(show: Boolean) {
        // loadingSpinner.visibility = if (show) View.VISIBLE else View.GONE
    }
    
    private fun showError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    private fun playAccessGrantedSound() {
        // Play beep sound or notification
    }
    
    private fun playAccessDeniedSound() {
        // Play error sound or notification
    }
}

// ==================== BUILD.GRADLE DEPENDENCIES ====================

/*
dependencies {
    // OkHttp for HTTP requests
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    
    // CameraX for camera integration
    implementation("androidx.camera:camera-core:1.2.0")
    implementation("androidx.camera:camera-camera2:1.2.0")
    implementation("androidx.camera:camera-lifecycle:1.2.0")
    
    // Image loading and processing
    implementation("com.github.bumptech.glide:glide:4.15.1")
    
    // JSON parsing
    implementation("com.google.code.gson:gson:2.10.1")
}
*/
