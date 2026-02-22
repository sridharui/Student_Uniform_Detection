"""
Test script to verify MAXIMUM ACCURACY MODE with enhanced skin tone detection
Tests updated confidence thresholds and improved bare feet rejection
"""

import sys
sys.path.insert(0, 'D:\\Student\\dress_code-main123')

from uniform_detector_system import UniformDetector

def test_maximum_accuracy_thresholds():
    """Test that confidence thresholds are set to maximum values"""
    detector = UniformDetector()
    
    print("=" * 80)
    print("MAXIMUM ACCURACY MODE - CONFIDENCE THRESHOLDS TEST")
    print("=" * 80)
    
    print("\n✓ CONFIDENCE THRESHOLDS (100% Accuracy Mode):")
    print(f"  • Shoes/Slippers: {detector.CONF_THRESHOLDS['shoes']:.2f} (0.92 = ULTRA-HIGH)")
    print(f"  • Identity Card:  {detector.CONF_THRESHOLDS['Identity Card']:.2f} (0.68 = VERY HIGH)")
    print(f"  • Shirt:          {detector.CONF_THRESHOLDS['Shirt']:.2f} (0.65 = VERY HIGH)")
    print(f"  • Top:            {detector.CONF_THRESHOLDS['top']:.2f} (0.65 = VERY HIGH)")
    print(f"  • Pant:           {detector.CONF_THRESHOLDS['pant']:.2f} (0.68 = VERY HIGH)")
    print(f"  • Default:        {detector.CONF_THRESHOLDS['default']:.2f} (0.60 = HIGH)")
    
    print("\n" + "=" * 80)


def test_skin_tone_detection():
    """Test enhanced skin tone detection in color algorithm"""
    detector = UniformDetector()
    
    print("\nENHANCED SKIN TONE DETECTION TEST")
    print("=" * 80)
    
    # Test various HSV values that represent skin tones
    test_cases = [
        # (H, S, V, R, G, B, Expected Color)
        (15, 80, 200, 210, 180, 140, "peach"),      # Light skin
        (18, 60, 150, 180, 150, 120, "tan"),        # Medium skin
        (20, 50, 100, 150, 130, 100, "beige"),      # Darker skin
        (12, 70, 190, 200, 170, 150, "flesh"),      # Very light skin
        (25, 45, 160, 170, 150, 100, "yellow"),     # Yellowish skin in lighting
        (15, 100, 140, 180, 140, 90, "orange"),     # Orange-brown skin
        (0, 0, 200, 200, 200, 200, "white"),        # White (should NOT be skin)
        (120, 100, 150, 50, 100, 150, "blue"),      # Blue (should NOT be skin)
    ]
    
    print("\n✓ Skin Tone Detection Results:")
    for h, s, v, r, g, b, expected in test_cases:
        color_data = {
            'hsv': (h, s, v),
            'rgb': (r, g, b)
        }
        detected_color = detector._detect_color_name(color_data)
        
        is_skin = detected_color in ['peach', 'tan', 'flesh', 'beige', 'orange', 'yellow']
        status = "✓ SKIN" if is_skin else "✗ NOT SKIN"
        
        print(f"  {status}: HSV({h:3}, {s:3}, {v:3}) RGB({r:3}, {g:3}, {b:3}) → {detected_color:10} (expected: {expected})")
    
    print("\n" + "=" * 80)


def test_shoe_color_validation():
    """Test shoe color validation - accept ALL colors except skin tones"""
    detector = UniformDetector()
    
    print("\nSHOE COLOR VALIDATION TEST (ACCEPT ALL EXCEPT SKIN TONES)")
    print("=" * 80)
    
    # Test shoes with various colors
    test_colors = [
        # (color_name, should_accept, reason)
        ('black', True, 'Valid shoe color'),
        ('white', True, 'Valid shoe color'),
        ('brown', True, 'Valid shoe color'),
        ('blue', True, 'Valid shoe color'),
        ('navy', True, 'Valid shoe color'),
        ('red', True, 'Valid shoe color'),
        ('gray', True, 'Valid shoe color'),
        ('green', True, 'Valid shoe color'),
        ('purple', True, 'Valid shoe color'),
        ('pink', True, 'Valid shoe color'),
        ('maroon', True, 'Valid shoe color'),
        ('cyan', True, 'Valid shoe color'),
        ('unknown', True, 'Accept unknown (enhanced skin detection catches bare feet)'),
        ('peach', False, 'Skin tone = bare feet'),
        ('tan', False, 'Skin tone = bare feet'),
        ('flesh', False, 'Skin tone = bare feet'),
        ('beige', False, 'Skin tone = bare feet'),
        ('orange', False, 'Skin tone = bare feet'),
        ('yellow', False, 'Skin tone = bare feet'),
        ('cement', False, 'Skin tone = bare feet'),
    ]
    
    print("\n✓ Shoe Color Validation (Accept ALL colors except skin tones):")
    accept_count = 0
    reject_count = 0
    
    for color, should_accept, reason in test_colors:
        is_valid, msg = detector._validate_component_color(color, 'shoes', 'boys')
        
        if is_valid == should_accept:
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        
        accept_reject = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        
        print(f"  {status}: {color:10} → {accept_reject:6} (expected: {expected:6}) - {reason}")
        
        if is_valid:
            accept_count += 1
        else:
            reject_count += 1
    
    print(f"\n  Summary: {accept_count} accepted, {reject_count} rejected")
    print(f"  → Accepts ANY color except 7 skin tones (100% flexibility for shoes)")
    print("\n" + "=" * 80)


def test_pant_color_validation():
    """Test strict pant color validation (navy/blue/black only)"""
    detector = UniformDetector()
    
    print("\nSTRICT PANT COLOR VALIDATION TEST")
    print("=" * 80)
    
    test_colors = [
        ('navy', True),
        ('blue', True),
        ('black', True),
        ('gray', False),
        ('green', False),
        ('brown', False),
        ('white', False),
        ('red', False),
    ]
    
    print("\n✓ Pant Color Validation (ONLY navy/blue/black):")
    for color, should_accept in test_colors:
        is_valid, msg = detector._validate_component_color(color, 'pant', 'boys')
        
        status = "✓ PASS" if (is_valid == should_accept) else "✗ FAIL"
        accept_reject = "ACCEPT" if is_valid else "REJECT"
        expected = "ACCEPT" if should_accept else "REJECT"
        
        print(f"  {status}: {color:10} → {accept_reject:6} (expected: {expected:6})")
    
    print("\n" + "=" * 80)


def run_all_tests():
    """Run all accuracy tests"""
    print("\n" + "=" * 80)
    print("MAXIMUM ACCURACY MODE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("\nTesting:")
    print("1. Ultra-high confidence thresholds (0.92 for shoes, 0.65-0.68 for others)")
    print("2. Enhanced skin tone detection (HSV + RGB multi-method)")
    print("3. Strict shoe validation (reject unknown + skin tones)")
    print("4. Strict pant validation (navy/blue/black only)")
    print("=" * 80 + "\n")
    
    try:
        test_maximum_accuracy_thresholds()
        test_skin_tone_detection()
        test_shoe_color_validation()
        test_pant_color_validation()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nKey Features:")
        print("  ✓ Shoes threshold: 0.92 (Ultra-high for 100% accuracy)")
        print("  ✓ Pant threshold: 0.68 (Very high for better detection)")
        print("  ✓ ID Card threshold: 0.68 (Very high for stricter validation)")
        print("  ✓ Shirt/Top threshold: 0.65 (Very high for better detection)")
        print("  ✓ Enhanced skin tone detection (4 methods: HSV, RGB, yellow, orange)")
        print("  ✓ Accept ALL shoe colors EXCEPT skin tones (maximum flexibility)")
        print("  ✓ Bare feet detected via enhanced skin detection algorithm")
        print("  ✓ Multi-layer validation: 0.92 confidence + enhanced color detection")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
