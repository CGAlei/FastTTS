#!/usr/bin/env python3
"""
Simple test to check if MFA is actually working after installing dependencies
"""

import asyncio
import sys
import os

# Add the FastTTS directory to Python path
sys.path.insert(0, '/mnt/d/FastTTS')

async def test_mfa_basic():
    """Test basic MFA functionality"""
    print("🧪 Testing MFA Basic Functionality")
    print("=" * 40)
    
    # Test 1: Check if MFA aligner can be imported and initialized
    try:
        from alignment import MFAAligner
        aligner = MFAAligner()
        print(f"✅ MFA Aligner imported successfully")
        print(f"   Available: {aligner.is_available}")
        
        if aligner.is_available:
            print("✅ MFA is available!")
            
            # Check models
            models_status = aligner._check_models_available()
            print(f"   Models status: {models_status}")
            
        else:
            print("❌ MFA is not available")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import MFA aligner: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking MFA: {e}")
        return False
    
    # Test 2: Check if MiniMax TTS can detect MFA properly
    try:
        from tts.minimax_tts_engine import MinimaxTTSEngine
        engine = MinimaxTTSEngine()
        
        if not engine.is_configured():
            print("⚠️ MiniMax not configured, testing MFA detection only")
        
        # Test text
        test_text = "今天天气很好"
        
        print(f"\n🎯 Testing with text: '{test_text}'")
        
        # Try MFA extraction method directly
        try:
            # Generate a dummy audio bytes and sentence timing for testing
            dummy_audio = b"dummy_audio_data"
            dummy_timing = [{"text": test_text, "start_time": 0, "end_time": 2000, "duration": 2000}]
            
            # Test the MFA extraction
            result = await engine._extract_word_timings(dummy_audio, test_text, dummy_timing)
            
            if result:
                first_word = result[0]
                source = first_word.get("source", "unknown")
                is_mfa = first_word.get("is_mfa", False)
                confidence = first_word.get("confidence", 0.0)
                
                print(f"   Result: {len(result)} words")
                print(f"   Source: {source}")
                print(f"   Is MFA: {is_mfa}")
                print(f"   Confidence: {confidence}")
                
                if is_mfa and "mfa" in source:
                    print("✅ Real MFA alignment working!")
                    return True
                else:
                    print("📝 Using jieba estimation (MFA failed)")
                    return False
            else:
                print("❌ No timing results")
                return False
                
        except Exception as e:
            print(f"❌ MFA test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error testing MiniMax engine: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mfa_basic())