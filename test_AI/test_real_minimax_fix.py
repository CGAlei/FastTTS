#!/usr/bin/env python3
"""
Real MiniMax TTS test with actual API calls and JSON verification
Tests both efficiency fixes and Traditional→Simplified conversion
"""

import sys
import os
import json
import asyncio
from pathlib import Path
import tempfile
import shutil

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts.minimax_tts_engine import MinimaxTTSEngine
from text_processor import preprocess_text_for_tts

async def test_real_minimax_fix():
    """Test real MiniMax TTS with efficiency fixes and JSON verification"""
    
    print("🧪 Real MiniMax TTS Test with JSON Verification")
    print("=" * 70)
    
    # Test credentials first
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID")
    
    if not api_key or not group_id:
        print("❌ MiniMax credentials not found in .env file")
        print("   Required: MINIMAX_API_KEY and MINIMAX_GROUP_ID")
        return False
    
    print(f"✅ Credentials loaded:")
    print(f"   API Key: {api_key[:20]}...")
    print(f"   Group ID: {group_id}")
    
    # Test with problematic Traditional Chinese text
    test_text = "我深信生命本身並未預設任何固有的先驗意義。宇宙構築了一個沒有劇本的舞台。"
    
    print(f"\n📝 Test Text (with Traditional Chinese):")
    print(f"   Input: '{test_text}'")
    print(f"   Length: {len(test_text)} characters")
    
    # Check for Traditional characters
    traditional_chars = ['並', '預設', '先驗', '構築', '劇本']
    found_traditional = [char for char in traditional_chars if char in test_text]
    print(f"   Traditional chars found: {found_traditional}")
    
    # Step 1: Test single chunk (no chunking)
    print(f"\n🔄 Step 1: Single Chunk Test (Baseline)")
    
    engine = MinimaxTTSEngine()
    
    # Ensure single chunk by setting large chunk size
    engine.chunk_size_words = 1000
    
    try:
        # Generate TTS
        print("   Generating TTS...")
        audio_data, word_timings = await engine.generate_speech(
            text=test_text,
            voice="moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430",  # Aria
            speed=1.0,
            volume=0.8
        )
        
        print(f"   ✅ Audio generated: {len(audio_data)} bytes")
        print(f"   ✅ Word timings: {len(word_timings)} words")
        
        # Save and analyze timing data
        single_chunk_file = Path("/tmp/single_chunk_timings.json")
        with open(single_chunk_file, 'w', encoding='utf-8') as f:
            json.dump(word_timings, f, ensure_ascii=False, indent=2)
        
        print(f"   📄 Timings saved to: {single_chunk_file}")
        
        # Analyze the JSON results
        print(f"\n📊 Single Chunk JSON Analysis:")
        
        # Check for Traditional Chinese in results
        traditional_in_json = []
        simplified_in_json = []
        
        expected_simplified = {
            '並': '并',
            '預設': '预设', 
            '先驗': '先验',
            '構築': '构筑',
            '劇本': '剧本'
        }
        
        for timing in word_timings[:10]:  # Check first 10 words
            word = timing.get('word', '')
            if any(trad in word for trad in expected_simplified.keys()):
                traditional_in_json.append(word)
            if any(simp in word for simp in expected_simplified.values()):
                simplified_in_json.append(word)
        
        print(f"   Traditional chars in JSON: {traditional_in_json}")
        print(f"   Simplified chars in JSON: {simplified_in_json}")
        
        # Show first few timings
        print(f"   First 5 word timings:")
        for i, timing in enumerate(word_timings[:5], 1):
            word = timing.get('word', 'N/A')
            timestamp = timing.get('timestamp', 0)
            is_in_db = timing.get('isInDB', False)
            print(f"     {i}. '{word}' at {timestamp}ms (inDB: {is_in_db})")
        
    except Exception as e:
        print(f"   ❌ Single chunk test failed: {e}")
        return False
    
    # Step 2: Test chunked processing (efficiency test)
    print(f"\n🔄 Step 2: Chunked Processing Test (Efficiency Fix)")
    
    # Force chunking with smaller chunk size
    engine.chunk_size_words = 15  # Force multiple chunks
    
    longer_text = test_text + "星辰循軌運轉，對地球上發生的一切悲歡離閤無動於衷。這似乎會導嚮一種虛無。然而，經過長期的探索與反思，我認為這恰恰是賦予生命以獨特價值的自由之源。"
    
    print(f"   Extended text: {len(longer_text)} chars")
    
    try:
        # Generate TTS with chunking
        print("   Generating chunked TTS...")
        start_time = asyncio.get_event_loop().time()
        
        chunked_audio, chunked_timings = await engine.generate_speech(
            text=longer_text,
            voice="moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430",
            speed=1.0,
            volume=0.8
        )
        
        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time
        
        print(f"   ✅ Chunked audio generated: {len(chunked_audio)} bytes")
        print(f"   ✅ Chunked timings: {len(chunked_timings)} words")
        print(f"   ⏱️  Processing time: {processing_time:.1f} seconds")
        
        # Save chunked timing data
        chunked_file = Path("/tmp/chunked_timings.json")
        with open(chunked_file, 'w', encoding='utf-8') as f:
            json.dump(chunked_timings, f, ensure_ascii=False, indent=2)
        
        print(f"   📄 Chunked timings saved to: {chunked_file}")
        
        # Analyze chunked JSON results
        print(f"\n📊 Chunked Processing JSON Analysis:")
        
        # Check conversion effectiveness
        traditional_in_chunked = []
        simplified_in_chunked = []
        
        for timing in chunked_timings:
            word = timing.get('word', '')
            if any(trad in word for trad in expected_simplified.keys()):
                traditional_in_chunked.append(word)
            if any(simp in word for simp in expected_simplified.values()):
                simplified_in_chunked.append(word)
        
        print(f"   Traditional chars in chunked JSON: {traditional_in_chunked}")
        print(f"   Simplified chars in chunked JSON: {simplified_in_chunked}")
        
        # Check for specific problematic words
        target_words = ['剧本', '预设', '先验', '构筑']
        found_targets = []
        
        for timing in chunked_timings:
            word = timing.get('word', '')
            if word in target_words:
                found_targets.append(word)
        
        print(f"   Target simplified words found: {found_targets}")
        
        # Show timing source information
        mfa_timings = 0
        jieba_timings = 0
        
        for timing in chunked_timings:
            source = timing.get('source', 'unknown')
            if 'mfa' in source.lower():
                mfa_timings += 1
            elif 'jieba' in source.lower():
                jieba_timings += 1
        
        print(f"   MFA timings: {mfa_timings}")
        print(f"   Jieba timings: {jieba_timings}")
        print(f"   Total timings: {len(chunked_timings)}")
        
        # Show sample timings with source info
        print(f"   Sample timings with source:")
        for i, timing in enumerate(chunked_timings[:8], 1):
            word = timing.get('word', 'N/A')
            timestamp = timing.get('timestamp', 0)
            source = timing.get('source', 'unknown')
            print(f"     {i}. '{word}' at {timestamp}ms ({source})")
        
    except Exception as e:
        print(f"   ❌ Chunked test failed: {e}")
        return False
    
    # Step 3: Validation and Results
    print(f"\n📋 Step 3: Validation Results")
    
    validation_passed = 0
    total_validations = 6
    
    # Validation 1: No Traditional Chinese in final JSON
    traditional_found = len(traditional_in_chunked) == 0
    if traditional_found:
        validation_passed += 1
        print(f"   ✅ No Traditional Chinese in final JSON")
    else:
        print(f"   ❌ Traditional Chinese still present: {traditional_in_chunked}")
    
    # Validation 2: Simplified Chinese present
    simplified_found = len(simplified_in_chunked) > 0
    if simplified_found:
        validation_passed += 1
        print(f"   ✅ Simplified Chinese properly converted")
    else:
        print(f"   ❌ No Simplified Chinese found")
    
    # Validation 3: Target words present
    targets_found = len(found_targets) > 0
    if targets_found:
        validation_passed += 1
        print(f"   ✅ Target simplified words found: {found_targets}")
    else:
        print(f"   ❌ Target simplified words missing")
    
    # Validation 4: Audio generated successfully
    audio_valid = len(chunked_audio) > 1000  # At least 1KB
    if audio_valid:
        validation_passed += 1
        print(f"   ✅ Valid audio generated ({len(chunked_audio)} bytes)")
    else:
        print(f"   ❌ Audio too small or invalid")
    
    # Validation 5: Reasonable timing count
    timing_valid = len(chunked_timings) >= 10
    if timing_valid:
        validation_passed += 1
        print(f"   ✅ Reasonable timing count ({len(chunked_timings)} words)")
    else:
        print(f"   ❌ Too few timings generated")
    
    # Validation 6: Processing completed reasonably fast
    speed_valid = processing_time < 60  # Should complete within 1 minute
    if speed_valid:
        validation_passed += 1
        print(f"   ✅ Processing completed quickly ({processing_time:.1f}s)")
    else:
        print(f"   ❌ Processing too slow ({processing_time:.1f}s)")
    
    # Final Summary
    print(f"\n🎯 Final Results: {validation_passed}/{total_validations} validations passed")
    
    if validation_passed == total_validations:
        print(f"\n🎉 SUCCESS: All fixes working perfectly!")
        print(f"✅ Traditional→Simplified conversion working")
        print(f"✅ Chunked processing with efficiency fixes")
        print(f"✅ JSON results contain proper Simplified Chinese")
        print(f"✅ Audio generation successful")
        print(f"✅ Performance optimized")
        
        # Show file locations for inspection
        print(f"\n📁 Output Files for Inspection:")
        print(f"   Single chunk: {single_chunk_file}")
        print(f"   Chunked: {chunked_file}")
        
        return True
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {validation_passed}/{total_validations} validations passed")
        print(f"Some issues remain - check the output files for details")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_minimax_fix())
    exit(0 if success else 1)