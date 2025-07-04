#!/usr/bin/env python3
"""
Test script to verify MiniMax punctuation filter works correctly
Tests the _filter_punctuation_timings method with various punctuation combinations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.minimax_tts_engine import MinimaxTTSEngine

def test_punctuation_filter():
    """Test the punctuation filter with various input scenarios"""
    
    print("🧪 Testing MiniMax Punctuation Filter")
    print("=" * 50)
    
    # Create engine instance
    engine = MinimaxTTSEngine()
    
    # Test case 1: Mixed Chinese and Western punctuation
    test_case_1 = [
        {"word": "政治", "start_time": 0, "end_time": 500},
        {"word": "结构", "start_time": 500, "end_time": 1000},
        {"word": "，", "start_time": 1000, "end_time": 1100},  # Chinese comma - should be filtered
        {"word": "也", "start_time": 1100, "end_time": 1300},
        {"word": ",", "start_time": 1300, "end_time": 1400},   # Western comma - should be filtered
        {"word": "催生", "start_time": 1400, "end_time": 1800},
        {"word": "了", "start_time": 1800, "end_time": 2000},
        {"word": "。", "start_time": 2000, "end_time": 2100},  # Chinese period - should be filtered
    ]
    
    print("\n📋 Test Case 1: Mixed Chinese/Western Punctuation")
    print("Input timing entries:")
    for i, timing in enumerate(test_case_1):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    filtered_1 = engine._filter_punctuation_timings(test_case_1)
    print(f"\nFiltered results ({len(filtered_1)} entries):")
    for i, timing in enumerate(filtered_1):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    # Test case 2: Brackets and container symbols
    test_case_2 = [
        {"word": "我", "start_time": 0, "end_time": 200},
        {"word": "深信", "start_time": 200, "end_time": 600},
        {"word": "【", "start_time": 600, "end_time": 650},    # Chinese bracket - should be filtered
        {"word": "生命", "start_time": 650, "end_time": 1050},
        {"word": "】", "start_time": 1050, "end_time": 1100},  # Chinese bracket - should be filtered
        {"word": "(", "start_time": 1100, "end_time": 1150},   # Western bracket - should be filtered
        {"word": "本身", "start_time": 1150, "end_time": 1550},
        {"word": ")", "start_time": 1550, "end_time": 1600},   # Western bracket - should be filtered
    ]
    
    print("\n📋 Test Case 2: Brackets and Container Symbols")
    print("Input timing entries:")
    for i, timing in enumerate(test_case_2):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    filtered_2 = engine._filter_punctuation_timings(test_case_2)
    print(f"\nFiltered results ({len(filtered_2)} entries):")
    for i, timing in enumerate(filtered_2):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    # Test case 3: Compound words and enumeration marks
    test_case_3 = [
        {"word": "书同文", "start_time": 0, "end_time": 800},
        {"word": "、", "start_time": 800, "end_time": 850},     # Enumeration comma - should be filtered
        {"word": "车同轨", "start_time": 850, "end_time": 1650},
        {"word": "的", "start_time": 1650, "end_time": 1800},
        {"word": "统一", "start_time": 1800, "end_time": 2200},
        {"word": "标准", "start_time": 2200, "end_time": 2600},
    ]
    
    print("\n📋 Test Case 3: Compound Words and Enumeration")
    print("Input timing entries:")
    for i, timing in enumerate(test_case_3):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    filtered_3 = engine._filter_punctuation_timings(test_case_3)
    print(f"\nFiltered results ({len(filtered_3)} entries):")
    for i, timing in enumerate(filtered_3):
        print(f"  {i+1}. '{timing['word']}' ({timing['start_time']}ms - {timing['end_time']}ms)")
    
    # Validation
    print("\n✅ Validation Results:")
    
    # Check that all punctuation was filtered
    punctuation_chars = {'，', '。', '、', '？', '！', '：', '；', '（', '）', '"', '"', ''', ''',
                        ',', '.', '!', '?', ':', ';', '(', ')', '"', "'",
                        '{', '}', '[', ']', '【', '】', '〈', '〉', '《', '》'}
    
    all_filtered = filtered_1 + filtered_2 + filtered_3
    remaining_punctuation = [timing['word'] for timing in all_filtered if timing['word'] in punctuation_chars]
    
    if not remaining_punctuation:
        print("  ✅ All punctuation successfully filtered")
    else:
        print(f"  ❌ Punctuation still present: {remaining_punctuation}")
    
    # Check that Chinese words were preserved
    chinese_words = [timing['word'] for timing in all_filtered]
    expected_words = ['政治', '结构', '也', '催生', '了', '我', '深信', '生命', '本身', '书同文', '车同轨', '的', '统一', '标准']
    
    if all(word in chinese_words for word in expected_words):
        print("  ✅ All Chinese words preserved")
    else:
        missing = [word for word in expected_words if word not in chinese_words]
        print(f"  ❌ Missing Chinese words: {missing}")
    
    print(f"\n📊 Summary:")
    print(f"  Total input entries: {len(test_case_1) + len(test_case_2) + len(test_case_3)}")
    print(f"  Total filtered entries: {len(all_filtered)}")
    print(f"  Punctuation removed: {len(test_case_1) + len(test_case_2) + len(test_case_3) - len(all_filtered)}")
    print(f"  Filter efficiency: {((len(test_case_1) + len(test_case_2) + len(test_case_3) - len(all_filtered)) / (len(test_case_1) + len(test_case_2) + len(test_case_3))) * 100:.1f}%")

if __name__ == "__main__":
    test_punctuation_filter()