#!/usr/bin/env python3
"""
Complete test to verify the word container fix works end-to-end
Tests all components: Character sync + Traditional→Simplified conversion + Punctuation filtering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.minimax_tts_engine import MinimaxTTSEngine
from text_processor import preprocess_text_for_tts

def test_complete_word_container_fix():
    """Test the complete word container fix pipeline"""
    
    print("🧪 Complete Word Container Fix Test")
    print("=" * 50)
    
    # Test with problematic text that contains mixed Traditional/Simplified and punctuation
    test_text = "我深信，生命本身并未预设任何固有的、先验的意义。宇宙的物理法则构筑了一个没有剧本的舞台，星辰循轨运转。"
    
    print(f"Input text: '{test_text}'")
    print(f"Length: {len(test_text)} characters")
    
    # Step 1: Text preprocessing (what UI displays)
    print(f"\n🔄 Step 1: Text Preprocessing")
    ui_text = preprocess_text_for_tts(test_text)
    print(f"UI text: '{ui_text}'")
    print(f"UI length: {len(ui_text)} characters")
    
    # Step 2: Simulate MFA returning Traditional Chinese (the problem)
    print(f"\n🔄 Step 2: Simulating MFA Traditional Chinese Output")
    
    # Create mock timing data with Traditional Chinese (what was causing the problem)
    simulated_mfa_traditional_timings = [
        {"word": "我", "start_time": 0, "end_time": 250, "source": "mfa"},
        {"word": "深信", "start_time": 250, "end_time": 630, "source": "mfa"},
        {"word": "，", "start_time": 630, "end_time": 680, "source": "mfa"},  # Punctuation
        {"word": "生命", "start_time": 680, "end_time": 1080, "source": "mfa"},
        {"word": "本身", "start_time": 1080, "end_time": 1480, "source": "mfa"},
        {"word": "並", "start_time": 1480, "end_time": 1650, "source": "mfa"},  # Traditional → 并
        {"word": "未", "start_time": 1650, "end_time": 1820, "source": "mfa"},
        {"word": "預設", "start_time": 1820, "end_time": 2220, "source": "mfa"},  # Traditional → 预设
        {"word": "任何", "start_time": 2220, "end_time": 2620, "source": "mfa"},
        {"word": "固有", "start_time": 2620, "end_time": 3020, "source": "mfa"},
        {"word": "的", "start_time": 3020, "end_time": 3120, "source": "mfa"},
        {"word": "、", "start_time": 3120, "end_time": 3170, "source": "mfa"},  # Punctuation
        {"word": "先驗", "start_time": 3170, "end_time": 3570, "source": "mfa"},  # Traditional → 先验
        {"word": "的", "start_time": 3570, "end_time": 3670, "source": "mfa"},
        {"word": "意義", "start_time": 3670, "end_time": 4070, "source": "mfa"},  # Traditional → 意义
        {"word": "。", "start_time": 4070, "end_time": 4120, "source": "mfa"},  # Punctuation
    ]
    
    print(f"Simulated MFA timing data ({len(simulated_mfa_traditional_timings)} entries):")
    print("  Traditional Chinese words with punctuation:")
    traditional_examples = []
    punctuation_examples = []
    
    for timing in simulated_mfa_traditional_timings:
        word = timing["word"]
        if word in '，。、？！：；（）':
            punctuation_examples.append(word)
        elif word in ['並', '預設', '先驗', '意義']:
            traditional_examples.append(word)
    
    print(f"    Traditional chars: {traditional_examples}")
    print(f"    Punctuation marks: {punctuation_examples}")
    
    # Step 3: Apply our fixes
    print(f"\n🔄 Step 3: Applying Complete Fix Pipeline")
    engine = MinimaxTTSEngine()
    
    # Sub-step 3a: Traditional→Simplified conversion
    print(f"  3a. Traditional→Simplified conversion...")
    converted_timings = engine._convert_traditional_to_simplified(simulated_mfa_traditional_timings)
    
    conversion_count = 0
    for orig, conv in zip(simulated_mfa_traditional_timings, converted_timings):
        if orig["word"] != conv["word"]:
            conversion_count += 1
            print(f"      '{orig['word']}' → '{conv['word']}'")
    
    print(f"  Converted: {conversion_count} Traditional characters")
    
    # Sub-step 3b: Punctuation filtering
    print(f"  3b. Punctuation filtering...")
    filtered_timings = engine._filter_punctuation_timings(converted_timings)
    
    punctuation_count = len(converted_timings) - len(filtered_timings)
    print(f"  Filtered: {punctuation_count} punctuation marks")
    
    # Step 4: Validate results
    print(f"\n📊 Step 4: Validation Results")
    
    # Check that Traditional characters are now Simplified
    remaining_traditional = []
    for timing in filtered_timings:
        word = timing["word"]
        if word in ['並', '預設', '先驗', '意義', '構築', '對', '發生']:  # Known Traditional chars
            remaining_traditional.append(word)
    
    if not remaining_traditional:
        print(f"  ✅ All Traditional characters converted to Simplified")
    else:
        print(f"  ❌ Remaining Traditional characters: {remaining_traditional}")
    
    # Check that punctuation is removed
    remaining_punctuation = []
    for timing in filtered_timings:
        word = timing["word"]
        if word in '，。、？！：；（）':
            remaining_punctuation.append(word)
    
    if not remaining_punctuation:
        print(f"  ✅ All punctuation marks filtered out")
    else:
        print(f"  ❌ Remaining punctuation: {remaining_punctuation}")
    
    # Check that Simplified words match UI text
    ui_word_matches = 0
    ui_word_total = 0
    
    for timing in filtered_timings:
        word = timing["word"]
        if len(word) > 1:  # Multi-character words
            ui_word_total += 1
            if word in ui_text:
                ui_word_matches += 1
    
    ui_match_rate = ui_word_matches / ui_word_total if ui_word_total > 0 else 0
    print(f"  📍 UI word matching: {ui_word_matches}/{ui_word_total} ({ui_match_rate*100:.1f}%)")
    
    # Step 5: Character position simulation
    print(f"\n🔍 Step 5: Character Position Simulation")
    
    # Simulate looking for specific words in UI text
    test_word_positions = [
        ("预设", "Should find at position of '预设' in UI"),
        ("先验", "Should find at position of '先验' in UI"),
        ("意义", "Should find at position of '意义' in UI"),
    ]
    
    position_matches = 0
    for word, description in test_word_positions:
        ui_position = ui_text.find(word)
        
        # Find this word in our filtered timing data
        timing_found = False
        for timing in filtered_timings:
            if timing["word"] == word:
                timing_found = True
                break
        
        if ui_position >= 0 and timing_found:
            print(f"  ✅ '{word}': Found in UI at position {ui_position}, timing data available")
            position_matches += 1
        elif ui_position >= 0:
            print(f"  ⚠️ '{word}': Found in UI at position {ui_position}, but no timing data")
        elif timing_found:
            print(f"  ⚠️ '{word}': Timing data available, but not found in UI")
        else:
            print(f"  ❌ '{word}': Neither in UI nor timing data")
    
    # Step 6: Overall assessment
    print(f"\n🏆 Step 6: Overall Assessment")
    
    success_criteria = [
        (conversion_count > 0, "Traditional→Simplified conversion working"),
        (punctuation_count > 0, "Punctuation filtering working"),
        (len(remaining_traditional) == 0, "No Traditional characters remain"),
        (len(remaining_punctuation) == 0, "No punctuation marks remain"),
        (ui_match_rate > 0.5, "Good UI word matching rate"),
        (position_matches > 0, "Character position alignment working"),
    ]
    
    passed_criteria = sum(1 for passed, _ in success_criteria if passed)
    total_criteria = len(success_criteria)
    
    print(f"Success criteria: {passed_criteria}/{total_criteria}")
    for passed, description in success_criteria:
        status = "✅" if passed else "❌"
        print(f"  {status} {description}")
    
    if passed_criteria == total_criteria:
        print(f"\n🎉 COMPLETE SUCCESS: Word container fix is working perfectly!")
        print(f"✅ Traditional Chinese converted to Simplified Chinese")
        print(f"✅ Punctuation marks filtered from timing data")
        print(f"✅ Character positions should align correctly")
        print(f"✅ Word containers should display properly in UI")
        return True
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: {passed_criteria}/{total_criteria} criteria passed")
        print(f"Word container alignment may still have issues")
        return False

if __name__ == "__main__":
    success = test_complete_word_container_fix()
    exit(0 if success else 1)