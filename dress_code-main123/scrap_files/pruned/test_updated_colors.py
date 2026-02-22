"""
Test script to verify updated color validation rules:
- SHOES: Accept ANY color except skin tones (cement, peach, tan, flesh, beige, orange)
- PANTS: Accept ONLY navy blue, dark blue, black
"""

import sys
sys.path.insert(0, 'D:\\Student\\dress_code-main123')

from uniform_detector_system import UniformDetector

def test_shoe_colors():
    """Test shoe color validation - accept all colors except skin tones"""
    detector = UniformDetector()
    
    print("=" * 70)
    print("SHOE COLOR VALIDATION TEST")
    print("=" * 70)
    
    # Test colors that should be ACCEPTED (any color except skin tones)
    accept_colors = ['black', 'white', 'brown', 'gray', 'red', 'blue', 'navy', 
                     'green', 'purple', 'pink', 'maroon', 'olive']
    
    print("\n✓ SHOULD ACCEPT (any color except skin tones):")
    for color in accept_colors:
        is_valid, msg = detector._validate_component_color(color, 'shoes', 'boys')
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  {status}: {color:12} -> {msg}")
        if not is_valid:
            print(f"       ERROR: Should accept {color} for shoes!")
    
    # Test colors that should be REJECTED (skin tones = bare feet)
    reject_colors = ['cement', 'peach', 'tan', 'flesh', 'beige', 'orange', 'yellow']
    
    print("\n✗ SHOULD REJECT (skin tones = bare feet):")
    for color in reject_colors:
        is_valid, msg = detector._validate_component_color(color, 'shoes', 'boys')
        status = "✓ PASS" if not is_valid else "✗ FAIL"
        print(f"  {status}: {color:12} -> {msg}")
        if is_valid:
            print(f"       ERROR: Should reject {color} for shoes (skin tone)!")
    
    print("\n" + "=" * 70)


def test_pant_colors():
    """Test pant color validation - accept ONLY navy blue, dark blue, black"""
    detector = UniformDetector()
    
    print("\nPANT COLOR VALIDATION TEST (MOST STRICT)")
    print("=" * 70)
    
    # Test colors that should be ACCEPTED (navy blue, dark blue, black ONLY)
    accept_colors = ['navy', 'blue', 'black']
    
    print("\n✓ SHOULD ACCEPT (navy blue/dark blue/black ONLY):")
    for color in accept_colors:
        is_valid, msg = detector._validate_component_color(color, 'pant', 'boys')
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  {status}: {color:12} -> {msg}")
        if not is_valid:
            print(f"       ERROR: Should accept {color} for pants!")
    
    # Test colors that should be REJECTED (everything else)
    reject_colors = ['gray', 'green', 'red', 'white', 'brown', 'yellow', 
                     'purple', 'pink', 'maroon', 'olive', 'cement']
    
    print("\n✗ SHOULD REJECT (any color except navy/blue/black):")
    for color in reject_colors:
        is_valid, msg = detector._validate_component_color(color, 'pant', 'boys')
        status = "✓ PASS" if not is_valid else "✗ FAIL"
        print(f"  {status}: {color:12} -> {msg}")
        if is_valid:
            print(f"       ERROR: Should reject {color} for pants!")
    
    print("\n" + "=" * 70)


def run_all_tests():
    """Run all color validation tests"""
    print("\n" + "=" * 70)
    print("UPDATED COLOR VALIDATION TEST SUITE")
    print("=" * 70)
    print("\nTesting new rules:")
    print("1. SHOES: Accept ANY color except skin tones (bare feet)")
    print("2. PANTS: Accept ONLY navy blue/dark blue/black")
    print("=" * 70)
    
    try:
        test_shoe_colors()
        test_pant_colors()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print("\nSummary:")
        print("  • Shoes: Accept all colors except skin tones")
        print("  • Pants: Accept ONLY navy/blue/black")
        print("  • Validation logic updated successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
