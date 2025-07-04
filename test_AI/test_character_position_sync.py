#!/usr/bin/env python3
"""
Test script to verify character position synchronization between MFA and UI
Tests the _prepare_text_for_mfa method to ensure character positions align
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alignment.mfa_aligner import MFAAligner
from text_processor import preprocess_text_for_tts

def test_character_position_sync():
    """Test character position synchronization with problematic texts"""
    
    print("🧪 Testing Character Position Synchronization")
    print("=" * 60)
    
    # Create MFA aligner instance
    aligner = MFAAligner()
    
    # Test cases that were failing
    test_cases = [
        {
            "name": "Philosophy Text (Problematic)",
            "text": "我深信，生命本身并未预设任何固有的、先验的意义。宇宙的物理法则构筑了一个没有剧本的舞台，星辰循轨运转，对地球上发生的一切悲欢离合无动于衷。"
        },
        {
            "name": "Political Text (Compound Words)",
            "text": "政治结构上的差别，也催生了社会管理方式的不同。中国古代社会强调高度集权，实行严格的县制和户籍制度，形成了书同文，车同轨的统一标准。"
        },
        {
            "name": "Attachment Text (Long)",
            "text": "执着于某人，本质上是将自我存在的重量寄托于另一个人的存在之上。这种依附如同在风中紧抓落叶，你攥得越紧，叶片碎裂得越快。"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        original_text = test_case['text']
        print(f"Original text: '{original_text}'")
        print(f"Length: {len(original_text)} characters")
        
        # Step 1: UI text processing (what user sees)
        ui_text = preprocess_text_for_tts(original_text)
        print(f"\nUI text (preprocess_text_for_tts): '{ui_text}'")
        print(f"UI length: {len(ui_text)} characters")
        
        # Step 2: MFA text processing (what MFA aligns)
        mfa_text = aligner._prepare_text_for_mfa(ui_text)
        print(f"\nMFA text (_prepare_text_for_mfa): '{mfa_text}'")
        print(f"MFA length: {len(mfa_text)} characters")
        
        # Step 3: Character position analysis
        print(f"\n📊 Position Analysis:")
        print(f"  UI text length:  {len(ui_text)}")
        print(f"  MFA text length: {len(mfa_text)}")
        print(f"  Difference:      {abs(len(ui_text) - len(mfa_text))} characters")
        
        if len(ui_text) == len(mfa_text):
            print(f"  ✅ PERFECT SYNC: Character positions align exactly")
            alignment_score = 100
        else:
            alignment_score = (1 - abs(len(ui_text) - len(mfa_text)) / len(ui_text)) * 100
            print(f"  ⚠️  PARTIAL SYNC: {alignment_score:.1f}% character alignment")
        
        # Step 4: Character-by-character comparison (first 50 chars)
        print(f"\n🔍 Character-by-character comparison (first 50 chars):")
        comparison_length = min(50, len(ui_text), len(mfa_text))
        
        mismatches = 0
        for j in range(comparison_length):
            ui_char = ui_text[j] if j < len(ui_text) else '∅'
            mfa_char = mfa_text[j] if j < len(mfa_text) else '∅'
            
            if ui_char != mfa_char:
                mismatches += 1
                if mismatches <= 5:  # Show first 5 mismatches
                    print(f"    Position {j:2d}: UI='{ui_char}' vs MFA='{mfa_char}' ❌")
            elif j < 10:  # Show first 10 matches for verification
                print(f"    Position {j:2d}: UI='{ui_char}' vs MFA='{mfa_char}' ✅")
        
        if mismatches == 0:
            print(f"  ✅ Perfect character alignment in first {comparison_length} positions")
        else:
            print(f"  ⚠️  {mismatches} character mismatches in first {comparison_length} positions")
        
        # Step 5: Punctuation preservation analysis
        ui_punctuation = set(char for char in ui_text if char in '，。、？！：；（）""''')
        mfa_punctuation = set(char for char in mfa_text if char in '，。、？！：；（）""''')
        
        print(f"\n🔤 Punctuation Analysis:")
        print(f"  UI punctuation:  {ui_punctuation if ui_punctuation else 'None'}")
        print(f"  MFA punctuation: {mfa_punctuation if mfa_punctuation else 'None'}")
        
        if ui_punctuation == mfa_punctuation:
            print(f"  ✅ Punctuation perfectly preserved")
        else:
            missing = ui_punctuation - mfa_punctuation
            added = mfa_punctuation - ui_punctuation
            if missing:
                print(f"  ❌ Missing punctuation: {missing}")
            if added:
                print(f"  ❌ Added punctuation: {added}")
    
    print(f"\n📊 Overall Assessment:")
    print(f"Character position synchronization is critical for word container alignment.")
    print(f"Ideal result: UI length = MFA length with identical character positions.")
    print(f"This ensures MFA timing data maps correctly to UI containers.")

if __name__ == "__main__":
    test_character_position_sync()