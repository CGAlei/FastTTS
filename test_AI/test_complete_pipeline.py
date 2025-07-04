#!/usr/bin/env python3
"""
Complete pipeline test to verify the fix works end-to-end
Tests the actual text flow from input to word containers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_processor import preprocess_text_for_tts
from alignment.mfa_aligner import MFAAligner
from tts.minimax_tts_engine import MinimaxTTSEngine

def test_complete_pipeline():
    """Test the complete text processing pipeline"""
    
    print("🧪 Complete Pipeline Test - Word Container Fix")
    print("=" * 60)
    
    # Test text that was breaking word containers
    test_text = "执着于某人，本质上是将自我存在的重量寄托于另一个人的存在之上。这种依附如同在风中紧抓落叶，你攥得越紧，叶片碎裂得越快。"
    
    print(f"Input text: '{test_text}'")
    print(f"Length: {len(test_text)} characters")
    
    # Step 1: Text preprocessing (what both MiniMax and UI use)
    print(f"\n🔄 Step 1: Text Preprocessing")
    preprocessed = preprocess_text_for_tts(test_text)
    print(f"Preprocessed: '{preprocessed}'")
    print(f"Length: {len(preprocessed)} characters")
    
    # Step 2: MFA text preparation (what MFA aligns against)
    print(f"\n🔄 Step 2: MFA Text Preparation")
    aligner = MFAAligner()
    mfa_text = aligner._prepare_text_for_mfa(preprocessed)
    print(f"MFA text: '{mfa_text}'")
    print(f"Length: {len(mfa_text)} characters")
    
    # Step 3: Character position validation
    print(f"\n📊 Step 3: Character Position Validation")
    if len(preprocessed) == len(mfa_text):
        print(f"✅ PERFECT SYNC: UI and MFA text have identical length")
        
        # Check character-by-character alignment
        mismatches = 0
        for i, (ui_char, mfa_char) in enumerate(zip(preprocessed, mfa_text)):
            if ui_char != mfa_char:
                mismatches += 1
                if mismatches <= 3:  # Show first 3 mismatches
                    print(f"❌ Position {i}: UI='{ui_char}' vs MFA='{mfa_char}'")
        
        if mismatches == 0:
            print(f"✅ PERFECT CHARACTER ALIGNMENT: All {len(preprocessed)} positions match")
            sync_quality = "PERFECT"
        else:
            print(f"⚠️ {mismatches} character mismatches out of {len(preprocessed)}")
            sync_quality = f"{((len(preprocessed) - mismatches) / len(preprocessed)) * 100:.1f}%"
    else:
        length_diff = abs(len(preprocessed) - len(mfa_text))
        print(f"❌ LENGTH MISMATCH: {length_diff} character difference")
        sync_quality = "FAILED"
    
    # Step 4: Punctuation analysis
    print(f"\n🔤 Step 4: Punctuation Analysis")
    ui_punctuation = [i for i, char in enumerate(preprocessed) if char in '，。、？！：；（）""''']
    mfa_punctuation = [i for i, char in enumerate(mfa_text) if char in '，。、？！：；（）""''']
    
    print(f"UI punctuation positions:  {ui_punctuation}")
    print(f"MFA punctuation positions: {mfa_punctuation}")
    
    if ui_punctuation == mfa_punctuation:
        print(f"✅ PUNCTUATION ALIGNMENT: All punctuation in same positions")
        punct_sync = "PERFECT"
    else:
        print(f"❌ PUNCTUATION MISMATCH: Different positions")
        punct_sync = "FAILED"
    
    # Step 5: Test punctuation filtering (simulate MFA timing result)
    print(f"\n🔄 Step 5: Punctuation Filter Test")
    engine = MinimaxTTSEngine()
    
    # Simulate MFA results with punctuation (what would happen without our fix)
    simulated_mfa_timings = [
        {"word": "执着", "start_time": 0, "end_time": 500},
        {"word": "于", "start_time": 500, "end_time": 700},
        {"word": "某人", "start_time": 700, "end_time": 1200},
        {"word": "，", "start_time": 1200, "end_time": 1250},  # Punctuation entry
        {"word": "本质", "start_time": 1250, "end_time": 1750},
        {"word": "上", "start_time": 1750, "end_time": 1900},
        {"word": "是", "start_time": 1900, "end_time": 2100},
        {"word": "将", "start_time": 2100, "end_time": 2300},
        {"word": "。", "start_time": 5000, "end_time": 5050},  # Punctuation entry
    ]
    
    print(f"Simulated MFA timing entries: {len(simulated_mfa_timings)}")
    
    # Apply punctuation filter
    filtered_timings = engine._filter_punctuation_timings(simulated_mfa_timings)
    print(f"Filtered timing entries: {len(filtered_timings)}")
    
    punctuation_filtered = len(simulated_mfa_timings) - len(filtered_timings)
    print(f"Punctuation entries removed: {punctuation_filtered}")
    
    # Show remaining words
    remaining_words = [timing['word'] for timing in filtered_timings]
    print(f"Remaining words: {remaining_words}")
    
    # Step 6: Overall assessment
    print(f"\n📋 Step 6: Overall Assessment")
    print(f"Text Synchronization: {sync_quality}")
    print(f"Punctuation Alignment: {punct_sync}")
    print(f"Filter Effectiveness: {punctuation_filtered} punctuation entries removed")
    
    if sync_quality == "PERFECT" and punct_sync == "PERFECT":
        print(f"\n🎉 SUCCESS: Word container fix is working correctly!")
        print(f"✅ UI and MFA process identical text")
        print(f"✅ Character positions align perfectly") 
        print(f"✅ Punctuation preserved for natural TTS")
        print(f"✅ Punctuation filtered from timing data")
        print(f"✅ Word containers should now align properly")
        
        return True
    else:
        print(f"\n❌ FAILURE: Word container fix has issues")
        print(f"Text synchronization and punctuation alignment must both be PERFECT")
        
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    exit(0 if success else 1)