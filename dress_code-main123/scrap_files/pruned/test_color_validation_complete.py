"""
Comprehensive Color Validation Test
Tests all updated color rules for uniform detection
"""

import sys
sys.path.insert(0, 'D:\\Student\\dress_code-main123')

from uniform_detector_system import UniformDetector

def test_all_color_validations():
    """Test all component color validations"""
    detector = UniformDetector()
    
    print("=" * 80)
    print("COMPREHENSIVE COLOR VALIDATION TEST")
    print("=" * 80)
    
    # Test Shirt colors
    print("\n✓ SHIRT COLOR VALIDATION:")
    print("  Accepted: white, gray, cement")
    shirt_tests = [
        ('white', True),
        ('gray', True),
        ('cement', True),
        ('black', False),
        ('blue', False),
        ('red', False),
    ]
    for color, should_accept in shirt_tests:
        is_valid, msg = detector._validate_component_color(color, 'Shirt', 'boys')
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        result = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        print(f"  {status}: {color:10} → {result:6} (expected: {expected:6})")
    
    # Test ID Card colors
    print("\n✓ ID CARD COLOR VALIDATION:")
    print("  Accepted: white, violet, green, red, yellow")
    idcard_tests = [
        ('white', True),
        ('violet', True),
        ('green', True),
        ('red', True),
        ('yellow', True),
        ('blue', False),
        ('black', False),
        ('gray', False),
    ]
    for color, should_accept in idcard_tests:
        is_valid, msg = detector._validate_component_color(color, 'Identity Card', 'boys')
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        result = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        print(f"  {status}: {color:10} → {result:6} (expected: {expected:6})")
    
    # Test Top colors
    print("\n✓ TOP COLOR VALIDATION:")
    print("  Accepted: white, gray, cement")
    top_tests = [
        ('white', True),
        ('gray', True),
        ('cement', True),
        ('black', False),
        ('blue', False),
        ('violet', False),
    ]
    for color, should_accept in top_tests:
        is_valid, msg = detector._validate_component_color(color, 'top', 'girls')
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        result = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        print(f"  {status}: {color:10} → {result:6} (expected: {expected:6})")
    
    # Test Pant colors
    print("\n✓ PANT COLOR VALIDATION:")
    print("  Accepted: black, navy, blue (dark blue)")
    pant_tests = [
        ('black', True),
        ('navy', True),
        ('blue', True),
        ('gray', False),
        ('white', False),
        ('green', False),
    ]
    for color, should_accept in pant_tests:
        is_valid, msg = detector._validate_component_color(color, 'pant', 'boys')
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        result = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        print(f"  {status}: {color:10} → {result:6} (expected: {expected:6})")
    
    # Test Shoes colors
    print("\n✓ SHOE COLOR VALIDATION:")
    print("  Accepted: ANY color except skin tones")
    print("  Rejected: cement, peach, tan, flesh, beige, orange, yellow (bare feet)")
    shoe_tests = [
        ('black', True),
        ('white', True),
        ('brown', True),
        ('blue', True),
        ('red', True),
        ('green', True),
        ('violet', True),
        ('cement', False),  # Skin tone
        ('peach', False),   # Skin tone
        ('tan', False),     # Skin tone
        ('flesh', False),   # Skin tone
        ('beige', False),   # Skin tone
        ('orange', False),  # Skin tone
        ('yellow', False),  # Skin tone
    ]
    for color, should_accept in shoe_tests:
        is_valid, msg = detector._validate_component_color(color, 'shoes', 'boys')
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        result = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        print(f"  {status}: {color:10} → {result:6} (expected: {expected:6})")
    
    print("\n" + "=" * 80)
    print("✅ SUMMARY OF ACCEPTED COLORS")
    print("=" * 80)
    print("\n📋 Complete Color Rules:")
    print("  • Shirt (Boys):    white, gray, cement")
    print("  • ID Card:         white, violet, green, red, yellow")
    print("  • Top (Girls):     white, gray, cement")
    print("  • Pant:            black, navy, blue (dark blue)")
    print("  • Shoes:           ANY color except skin tones")
    print("                     (Reject: cement, peach, tan, flesh, beige, orange, yellow)")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_all_color_validations()
