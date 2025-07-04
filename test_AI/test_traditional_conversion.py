#!/usr/bin/env python3
"""
Test script to verify Traditional to Simplified Chinese conversion
Tests the conversion using actual data from timestamps.json
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.minimax_tts_engine import MinimaxTTSEngine

def test_traditional_conversion():
    """Test Traditional to Simplified conversion with real timestamp data"""
    
    print("🧪 Testing Traditional→Simplified Chinese Conversion")
    print("=" * 60)
    
    # Create engine instance
    engine = MinimaxTTSEngine()
    
    # Sample Traditional Chinese words from the actual timestamps.json
    test_traditional_timings = [
        {"word": "並", "timestamp": 2280, "isInDB": False},        # line 23 → 并
        {"word": "預設", "timestamp": 2660, "isInDB": False},      # line 33 → 预设
        {"word": "先驗", "timestamp": 4150, "isInDB": False},      # line 53 → 先验
        {"word": "意義", "timestamp": 4790, "isInDB": False},      # line 63 → 意义
        {"word": "則", "timestamp": 6500, "isInDB": False},        # line 83 → 则
        {"word": "構築", "timestamp": 6760, "isInDB": False},      # line 88 → 构筑
        {"word": "瞭", "timestamp": 7050, "isInDB": False},        # line 93 → 了
        {"word": "運轉", "timestamp": 11050, "isInDB": False},     # line 138 → 运转
        {"word": "對", "timestamp": 11840, "isInDB": False},       # line 143 → 对
        {"word": "發生", "timestamp": 12350, "isInDB": False},     # line 158 → 发生
        {"word": "悲歡離閤", "timestamp": 13410, "isInDB": False}, # line 173 → 悲欢离合
        {"word": "無動於衷", "timestamp": 14420, "isInDB": False}, # line 178 → 无动于衷
        {"word": "導嚮", "timestamp": 17470, "isInDB": False},     # line 213 → 导向
        {"word": "認為", "timestamp": 23650, "isInDB": False},     # line 293 → 认为
        {"word": "纔", "timestamp": 31980, "isInDB": False},       # line 397 → 才
        {"word": "個", "timestamp": 37380, "isInDB": False},       # line 473 → 个
        {"word": "講述者", "timestamp": 38440, "isInDB": False},   # line 493 → 讲述者
        {"word": "聆聽者", "timestamp": 39330, "isInDB": False},   # line 503 → 聆听者
        {"word": "類", "timestamp": 41980, "isInDB": False},       # line 518 → 类 (人類→人类)
        {"word": "與", "timestamp": 22580, "isInDB": False},       # line 278 → 与
    ]
    
    print(f"\n📋 Testing {len(test_traditional_timings)} Traditional Chinese words from timestamps.json")
    print("-" * 60)
    
    # Show original Traditional words
    print("Original Traditional Chinese timing data:")
    for i, timing in enumerate(test_traditional_timings[:10], 1):  # Show first 10
        print(f"  {i:2d}. '{timing['word']}' at {timing['timestamp']}ms")
    if len(test_traditional_timings) > 10:
        print(f"  ... and {len(test_traditional_timings) - 10} more")
    
    # Apply conversion
    print(f"\n🔄 Applying Traditional→Simplified conversion...")
    converted_timings = engine._convert_traditional_to_simplified(test_traditional_timings)
    
    print(f"\nConverted Simplified Chinese timing data:")
    conversion_examples = []
    
    for original, converted in zip(test_traditional_timings, converted_timings):
        original_word = original["word"]
        converted_word = converted["word"]
        
        if original_word != converted_word:
            conversion_examples.append((original_word, converted_word))
            print(f"  ✅ '{original_word}' → '{converted_word}' at {converted['timestamp']}ms")
        else:
            print(f"  ➡️  '{original_word}' (no conversion needed) at {converted['timestamp']}ms")
    
    # Validation
    print(f"\n📊 Conversion Results:")
    print(f"  Total words tested: {len(test_traditional_timings)}")
    print(f"  Words converted: {len(conversion_examples)}")
    print(f"  Conversion rate: {len(conversion_examples)/len(test_traditional_timings)*100:.1f}%")
    
    # Show key conversions
    print(f"\n🔤 Key Traditional→Simplified Conversions:")
    for trad, simp in conversion_examples[:15]:  # Show first 15
        print(f"    {trad} → {simp}")
    
    # Test character position implications
    print(f"\n📍 Character Position Analysis:")
    position_tests = [
        ("預設", "预设"),  # Different character count implications
        ("並", "并"),      # Single character conversion
        ("悲歡離閤", "悲欢离合"),  # Multi-character compound
        ("無動於衷", "无动于衷"),  # Another compound
    ]
    
    for trad, expected_simp in position_tests:
        # Find if this conversion exists in our results
        found_conversion = None
        for orig_trad, converted_simp in conversion_examples:
            if orig_trad == trad:
                found_conversion = converted_simp
                break
        
        if found_conversion:
            if found_conversion == expected_simp:
                print(f"  ✅ '{trad}' → '{found_conversion}' (correct)")
            else:
                print(f"  ❌ '{trad}' → '{found_conversion}' (expected '{expected_simp}')")
        else:
            print(f"  ❓ '{trad}' not found in test data")
    
    # Test with UI text comparison simulation
    print(f"\n🖥️  UI Compatibility Test:")
    print("Simulating how converted words would match UI Simplified Chinese text...")
    
    # Common UI text patterns (Simplified Chinese)
    ui_simplified_text = "我深信，生命本身并未预设任何固有的、先验的意义。宇宙的物理法则构筑了一个没有剧本的舞台"
    
    # Check if converted words would be found in UI text
    ui_matches = 0
    ui_total = 0
    
    for timing in converted_timings:
        word = timing["word"]
        if len(word) > 1:  # Only check multi-character words
            ui_total += 1
            if word in ui_simplified_text:
                ui_matches += 1
                print(f"  ✅ '{word}' found in UI text")
            else:
                print(f"  ❌ '{word}' NOT found in UI text")
    
    print(f"\n📈 UI Compatibility: {ui_matches}/{ui_total} words would match UI text ({ui_matches/ui_total*100:.1f}%)")
    
    # Overall assessment
    if len(conversion_examples) > len(test_traditional_timings) * 0.8:
        print(f"\n🎉 SUCCESS: High conversion rate indicates good Traditional→Simplified mapping")
        print(f"✅ Word containers should now align correctly with UI text")
        return True
    else:
        print(f"\n⚠️  WARNING: Low conversion rate - may need more character mappings")
        return False

if __name__ == "__main__":
    success = test_traditional_conversion()
    exit(0 if success else 1)