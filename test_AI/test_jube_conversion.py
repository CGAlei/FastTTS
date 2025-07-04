#!/usr/bin/env python3
"""
Quick test to verify 劇本 conversion fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.minimax_tts_engine import MinimaxTTSEngine

def test_jube_conversion():
    """Test that 劇本 is now converted to 剧本"""
    
    print("🧪 Testing 劇本 → 剧本 Conversion Fix")
    print("=" * 50)
    
    engine = MinimaxTTSEngine()
    
    # Test data with Traditional Chinese
    test_timings = [
        {"word": "劇本", "timestamp": 1000, "isInDB": False},
        {"word": "構築", "timestamp": 2000, "isInDB": False},
        {"word": "預設", "timestamp": 3000, "isInDB": False},
        {"word": "hello", "timestamp": 4000, "isInDB": False},  # Should not be converted
    ]
    
    print("Input timing data:")
    for timing in test_timings:
        print(f"  '{timing['word']}' at {timing['timestamp']}ms")
    
    # Apply conversion
    converted_timings = engine._convert_traditional_to_simplified(test_timings)
    
    print("\nConverted timing data:")
    conversions_found = 0
    for orig, conv in zip(test_timings, converted_timings):
        original_word = orig['word']
        converted_word = conv['word']
        
        if original_word != converted_word:
            conversions_found += 1
            print(f"  ✅ '{original_word}' → '{converted_word}' at {conv['timestamp']}ms")
        else:
            print(f"  ➡️  '{original_word}' (no change) at {conv['timestamp']}ms")
    
    # Specific test for 劇本
    jube_converted = False
    for timing in converted_timings:
        if timing['word'] == '剧本':
            jube_converted = True
            print(f"\n🎯 SUCCESS: '劇本' correctly converted to '剧本'")
            break
    
    if not jube_converted:
        print(f"\n❌ FAILED: '劇本' was not converted to '剧本'")
        return False
    
    print(f"\n📊 Summary:")
    print(f"  Total conversions: {conversions_found}/4")
    print(f"  劇本 conversion: {'✅ Working' if jube_converted else '❌ Failed'}")
    
    if jube_converted and conversions_found >= 3:
        print(f"\n🎉 SUCCESS: All Traditional Chinese conversions working!")
        return True
    else:
        print(f"\n⚠️  Some conversions may be missing")
        return False

if __name__ == "__main__":
    success = test_jube_conversion()
    exit(0 if success else 1)