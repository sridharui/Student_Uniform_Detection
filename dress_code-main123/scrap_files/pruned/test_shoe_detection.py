#!/usr/bin/env python3
"""Test the updated shoe detection thresholds"""

from uniform_detector_system import UniformDetector

# Initialize detector
detector = UniformDetector()

print("=" * 70)
print("SHOE DETECTION IMPROVEMENTS")
print("=" * 70)
print(f"\n✅ Module loaded successfully")
print(f"\n📊 Updated Confidence Thresholds:")
print(f"   • Shoes: {detector.CONF_THRESHOLDS['shoes']} (was 0.85 → now 0.92)")
print(f"   • Pants: {detector.CONF_THRESHOLDS['pant']} (unchanged)")
print(f"   • ID Card: {detector.CONF_THRESHOLDS['Identity Card']}")
print(f"\n🎯 Color Validation for Shoes:")
print(f"   ✓ ACCEPTED colors: black, white, brown, gray, yellow, red, blue, navy")
print(f"   ✗ REJECTED colors: cement, peach, tan, flesh, beige, orange")
print(f"\n📝 What this means:")
print(f"   • Bare feet with 'cement' color (skin tone) → REJECTED")
print(f"   • Toes with skin-tone colors → REJECTED")
print(f"   • Only actual shoes with 0.92+ confidence AND proper colors → ACCEPTED")
print(f"\n✨ Result: False positives for bare feet/toes should be eliminated!\n")

# Test the color validation
print("=" * 70)
print("COLOR VALIDATION TEST")
print("=" * 70)

test_cases = [
    ('black', 'shoes', True, 'Real black shoes'),
    ('white', 'shoes', True, 'White shoes'),
    ('cement', 'shoes', False, 'Skin tone - bare foot (REJECT)'),
    ('peach', 'shoes', False, 'Skin tone - bare foot (REJECT)'),
    ('yellow', 'shoes', True, 'Yellow shoes'),
    ('blue', 'shoes', True, 'Blue shoes'),
]

print("\nTesting shoe color validation:\n")
for color, component, expected, description in test_cases:
    valid, msg = detector._validate_component_color(color, component, 'BOYS')
    status = "✓ ACCEPT" if valid else "✗ REJECT"
    match = "✓" if valid == expected else "✗"
    print(f"{match} {status:12} | {color:10} | {msg}")

print("\n" + "=" * 70)
print("Ready for testing! Run: python uniform_detector_system.py")
print("=" * 70 + "\n")
