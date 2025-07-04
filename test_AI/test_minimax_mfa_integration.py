#!/usr/bin/env python3
"""
Test MiniMax TTS + MFA integration with proper environment loading
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the FastTTS directory to Python path
sys.path.insert(0, '/mnt/d/FastTTS')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('/mnt/d/FastTTS/.env')

async def test_minimax_mfa_integration():
    """Test complete MiniMax TTS + MFA pipeline"""
    print("🧪 Testing MiniMax TTS + MFA Integration")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv("MINIMAX_API_KEY")
    group_id = os.getenv("MINIMAX_GROUP_ID") 
    voice_id = os.getenv("MINIMAX_CUSTOM_VOICE_ID")
    
    print(f"🔑 Environment Check:")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"   Group ID: {'✅ Set' if group_id else '❌ Missing'}")
    print(f"   Voice ID: {voice_id}")
    
    if not api_key or not group_id:
        print("❌ MiniMax credentials not properly loaded")
        return False
    
    # Test with short Chinese text
    test_text = "今天天气很好，我们一起去公园散步。"
    print(f"\n📝 Test text: '{test_text}'")
    print(f"📝 Text length: {len(test_text)} characters")
    
    # Test MiniMax TTS engine
    try:
        from tts.minimax_tts_engine import MinimaxTTSEngine
        engine = MinimaxTTSEngine()
        
        print(f"\n🔧 Engine configuration:")
        print(f"   Is configured: {engine.is_configured()}")
        print(f"   Voice: {voice_id}")
        print(f"   Default voice: {engine.default_voice}")
        
        if not engine.is_configured():
            print("❌ MiniMax engine not configured properly")
            return False
            
        print(f"\n🎯 Generating TTS audio...")
        
        # Generate speech with MFA
        audio_bytes, word_timings = await engine.generate_speech(
            text=test_text,
            voice=voice_id,
            speed=1.0,
            volume=0.8
        )
        
        print(f"✅ TTS generation completed!")
        print(f"   Audio size: {len(audio_bytes)} bytes")
        print(f"   Word timings: {len(word_timings)} words")
        
        if not word_timings:
            print("❌ No word timings generated")
            return False
            
        # Analyze the results
        print(f"\n📊 Timing Analysis:")
        
        # Check source of timing data
        sources = {}
        mfa_count = 0
        jieba_count = 0
        
        for timing in word_timings:
            source = timing.get("source", "unknown")
            is_mfa = timing.get("is_mfa", False)
            
            sources[source] = sources.get(source, 0) + 1
            if is_mfa:
                mfa_count += 1
            else:
                jieba_count += 1
        
        print(f"   Sources: {sources}")
        print(f"   MFA words: {mfa_count}")
        print(f"   Jieba words: {jieba_count}")
        
        # Show first few words
        print(f"\n📝 Sample timings:")
        for i, timing in enumerate(word_timings[:5]):
            word = timing.get("word", "")
            start_time = timing.get("start_time", 0)
            end_time = timing.get("end_time", 0)
            source = timing.get("source", "unknown")
            is_mfa = timing.get("is_mfa", False)
            confidence = timing.get("confidence", 0.0)
            
            print(f"   {i+1}. '{word}' ({start_time:.1f}ms-{end_time:.1f}ms)")
            print(f"      Source: {source}, MFA: {is_mfa}, Confidence: {confidence}")
        
        # Check for real MFA results
        if mfa_count > 0:
            print(f"\n🎉 SUCCESS: Real MFA alignment achieved!")
            print(f"   {mfa_count}/{len(word_timings)} words from MFA")
            return True
        else:
            print(f"\n📝 FALLBACK: All words from jieba estimation")
            print(f"   MFA pipeline exists but did not succeed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_minimax_mfa_integration())
    if success:
        print("\n🎉 MiniMax + MFA integration working!")
        sys.exit(0)
    else:
        print("\n❌ MiniMax + MFA integration needs debugging")
        sys.exit(1)