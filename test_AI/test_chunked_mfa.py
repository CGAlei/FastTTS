#!/usr/bin/env python3
"""
Test MFA with chunked MiniMax TTS processing for longer texts
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

async def test_chunked_mfa():
    """Test MFA with chunked processing for longer text"""
    print("🧪 Testing Chunked MFA Processing")
    print("=" * 50)
    
    # Use longer text that will trigger chunking (>120 words)
    long_text = """
    中国是一个历史悠久的国家，拥有五千年的灿烂文明。从古代的商周文明到秦汉帝国，从唐宋盛世到明清王朝，中华民族创造了无数辉煌的成就。
    古代中国在科学技术方面取得了许多重要发明。四大发明造纸术、火药、指南针和印刷术对世界文明产生了深远影响。中医药学、天文历法、数学等领域也都有重要贡献。
    在文学艺术方面，中国古代诗词、书法、绘画、音乐、戏曲等艺术形式丰富多彩。唐诗宋词、元曲明小说等文学作品至今仍被广泛传诵。孔子、老子、庄子等思想家的哲学思想影响深远。
    现代中国正在快速发展。改革开放以来，中国经济取得了举世瞩目的成就。高铁、移动支付、共享经济等新技术新模式不断涌现。中国正在努力建设创新型国家。
    """.strip().replace('\n', '').replace('    ', '')
    
    print(f"📝 Test text: '{long_text[:100]}...'")
    print(f"📝 Text length: {len(long_text)} characters")
    
    # Test MiniMax TTS engine with chunking
    try:
        from tts.minimax_tts_engine import MinimaxTTSEngine
        engine = MinimaxTTSEngine()
        
        print(f"\n🔧 Engine configuration:")
        print(f"   Is configured: {engine.is_configured()}")
        print(f"   Chunk size: {engine.chunk_size_words} words")
        
        if not engine.is_configured():
            print("❌ MiniMax engine not configured")
            return False
            
        print(f"\n🎯 Generating chunked TTS audio...")
        
        # Generate speech with chunking and MFA
        audio_bytes, word_timings = await engine.generate_speech(
            text=long_text,
            voice=os.getenv("MINIMAX_CUSTOM_VOICE_ID"),
            speed=1.0,
            volume=0.8
        )
        
        print(f"✅ Chunked TTS generation completed!")
        print(f"   Total audio size: {len(audio_bytes)} bytes")
        print(f"   Total word timings: {len(word_timings)} words")
        
        if not word_timings:
            print("❌ No word timings generated")
            return False
            
        # Analyze the results by chunk
        print(f"\n📊 Chunked Timing Analysis:")
        
        # Group by source and chunk
        sources = {}
        chunk_sources = {}
        mfa_count = 0
        jieba_count = 0
        
        for timing in word_timings:
            source = timing.get("source", "unknown")
            is_mfa = timing.get("is_mfa", False)
            chunk_id = timing.get("chunk_id", "unknown")
            
            sources[source] = sources.get(source, 0) + 1
            
            if chunk_id != "unknown":
                if chunk_id not in chunk_sources:
                    chunk_sources[chunk_id] = {"mfa": 0, "jieba": 0}
                if is_mfa:
                    chunk_sources[chunk_id]["mfa"] += 1
                else:
                    chunk_sources[chunk_id]["jieba"] += 1
            
            if is_mfa:
                mfa_count += 1
            else:
                jieba_count += 1
        
        print(f"   Overall sources: {sources}")
        print(f"   MFA words: {mfa_count}")
        print(f"   Jieba words: {jieba_count}")
        
        if chunk_sources:
            print(f"   Per-chunk breakdown:")
            for chunk_id, counts in chunk_sources.items():
                total = counts["mfa"] + counts["jieba"]
                mfa_pct = (counts["mfa"] / total * 100) if total > 0 else 0
                print(f"     Chunk {chunk_id}: {counts['mfa']} MFA, {counts['jieba']} jieba ({mfa_pct:.1f}% MFA)")
        
        # Show sample timings from different chunks
        print(f"\n📝 Sample timings by chunk:")
        current_chunk = None
        shown_chunks = set()
        for i, timing in enumerate(word_timings):
            chunk_id = timing.get("chunk_id", None)
            if chunk_id is not None and chunk_id != current_chunk and chunk_id not in shown_chunks:
                current_chunk = chunk_id
                shown_chunks.add(chunk_id)
                
                word = timing.get("word", "")
                start_time = timing.get("start_time", 0)
                end_time = timing.get("end_time", 0)
                source = timing.get("source", "unknown")
                is_mfa = timing.get("is_mfa", False)
                confidence = timing.get("confidence", 0.0)
                
                print(f"   Chunk {chunk_id}: '{word}' ({start_time:.1f}ms-{end_time:.1f}ms)")
                print(f"               Source: {source}, MFA: {is_mfa}, Confidence: {confidence}")
                
                if len(shown_chunks) >= 3:  # Show only first 3 chunks
                    break
        
        # Check timing continuity
        print(f"\n⏱️ Timing Continuity Check:")
        timing_gaps = []
        for i in range(1, len(word_timings)):
            prev_end = word_timings[i-1].get("end_time", 0)
            curr_start = word_timings[i].get("start_time", 0)
            gap = curr_start - prev_end
            if abs(gap) > 50:  # Gap > 50ms might indicate issues
                timing_gaps.append((i, gap))
        
        if timing_gaps:
            print(f"   Found {len(timing_gaps)} timing gaps > 50ms:")
            for word_idx, gap in timing_gaps[:5]:  # Show first 5 gaps
                word = word_timings[word_idx].get("word", "")
                print(f"     Word {word_idx} ('{word}'): {gap:.1f}ms gap")
        else:
            print(f"   ✅ No significant timing gaps detected")
        
        # Success criteria
        success_rate = (mfa_count / len(word_timings) * 100) if word_timings else 0
        
        if success_rate > 80:
            print(f"\n🎉 SUCCESS: Chunked MFA working well!")
            print(f"   {success_rate:.1f}% of words from MFA alignment")
            return True
        elif success_rate > 50:
            print(f"\n⚠️ PARTIAL SUCCESS: Mixed MFA/jieba results")
            print(f"   {success_rate:.1f}% of words from MFA alignment")
            return True
        else:
            print(f"\n📝 MOSTLY JIEBA: MFA not working in chunked mode")
            print(f"   Only {success_rate:.1f}% of words from MFA alignment")
            return False
            
    except Exception as e:
        print(f"❌ Chunked test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_chunked_mfa())
    if success:
        print("\n🎉 Chunked MFA test passed!")
        sys.exit(0)
    else:
        print("\n❌ Chunked MFA test failed")
        sys.exit(1)