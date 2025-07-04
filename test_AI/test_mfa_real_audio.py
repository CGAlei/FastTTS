#!/usr/bin/env python3
"""
Test MFA with real audio file from existing session
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the FastTTS directory to Python path
sys.path.insert(0, '/mnt/d/FastTTS')

async def test_mfa_with_real_audio():
    """Test MFA functionality with real audio from session"""
    print("🧪 Testing MFA with Real Audio")
    print("=" * 40)
    
    # Use real audio and text from existing session
    session_dir = Path("/mnt/d/FastTTS/sessions/20250626_015036")
    audio_file = session_dir / "audio.mp3"
    
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
        
    print(f"📁 Using session: {session_dir.name}")
    print(f"🎵 Audio file: {audio_file} ({audio_file.stat().st_size} bytes)")
    
    # Read the audio file
    audio_bytes = audio_file.read_bytes()
    print(f"✅ Read {len(audio_bytes)} bytes of audio data")
    
    # Use a shorter text for testing (first sentence)
    test_text = "我们常常习惯于拿自己与别人进行比较，这是一种深深植根于我们心中的习惯。"
    print(f"📝 Test text: '{test_text}'")
    print(f"📝 Text length: {len(test_text)} characters")
    
    # Test MFA alignment
    try:
        from alignment.mfa_aligner import MFAAligner
        aligner = MFAAligner()
        
        if not aligner.is_available:
            print("❌ MFA not available")
            return False
            
        print("✅ MFA aligner initialized")
        
        # Test with a subset of the audio (first 10 seconds worth)
        # This should be enough to align the first sentence
        print("\n🎯 Running MFA alignment...")
        
        # Create dummy sentence timing for the first sentence
        sentence_timing = [{
            "text": test_text,
            "start_time": 0,
            "end_time": 10000,  # 10 seconds
            "duration": 10000
        }]
        
        result = await aligner.align_chinese_audio(
            audio_bytes=audio_bytes,
            text=test_text,
            sentence_timings=sentence_timing,
            is_chunk=False
        )
        
        if result:
            print(f"\n✅ MFA alignment successful!")
            print(f"   Generated {len(result)} word timings")
            
            # Check first few words
            for i, word_timing in enumerate(result[:5]):
                source = word_timing.get("source", "unknown")
                is_mfa = word_timing.get("is_mfa", False)
                confidence = word_timing.get("confidence", 0.0)
                word = word_timing.get("word", "")
                start_time = word_timing.get("start_time", 0)
                end_time = word_timing.get("end_time", 0)
                
                print(f"   Word {i+1}: '{word}' ({start_time:.1f}ms-{end_time:.1f}ms)")
                print(f"           Source: {source}, MFA: {is_mfa}, Confidence: {confidence}")
            
            # Check if we got real MFA results
            first_word = result[0]
            if first_word.get("is_mfa", False) and "mfa" in first_word.get("source", ""):
                print("\n🎉 SUCCESS: Real MFA alignment working!")
                return True
            else:
                print(f"\n📝 FALLBACK: Using {first_word.get('source', 'unknown')} (MFA failed)")
                return False
        else:
            print("❌ No alignment results")
            return False
            
    except Exception as e:
        print(f"❌ MFA test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mfa_with_real_audio())
    if success:
        print("\n🎉 MFA test passed - Real alignment achieved!")
        sys.exit(0)
    else:
        print("\n❌ MFA test failed - Still using fallback methods")
        sys.exit(1)