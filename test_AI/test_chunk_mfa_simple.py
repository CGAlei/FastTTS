#!/usr/bin/env python3
"""
Simple focused test for MFA chunk processing
Tests whether MFA alignment is being applied per chunk vs. overall estimation
"""

import asyncio
import json
import logging
from tts.minimax_tts_engine import MinimaxTTSEngine

# Configure logging to see MFA processing details
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_mfa_chunking():
    """Test MFA chunking with a text that will definitely be split into chunks"""
    
    # Test text long enough to trigger chunking (>120 words when segmented)
    test_text = """在这个快速发展的时代，人工智能技术正在深刻地改变着我们的生活方式和工作模式。
    从简单的语音识别技术到复杂的自然语言处理系统，从基础的图像识别算法到高级的计算机视觉应用，
    人工智能的应用范围正在不断扩大，渗透到社会的各个领域。特别是在教育行业，
    智能学习系统能够根据每个学生的学习特点和进度提供个性化的学习方案和教学内容，
    大大提高了学习效率和教学质量。同时，在医疗健康领域，人工智能辅助诊断系统
    可以帮助医生更加准确快速地识别各种疾病症状，为患者提供更加精准有效的治疗方案。
    在金融服务行业，智能风控系统通过大数据分析和机器学习算法，
    能够有效识别和防范各种金融风险，保护用户资金安全。"""
    
    print("🧪 Testing MFA Chunk Processing")
    print("=" * 50)
    print(f"📝 Test text length: {len(test_text)} characters")
    
    try:
        # Initialize MiniMax TTS engine
        engine = MinimaxTTSEngine()
        
        if not engine.is_configured():
            print("❌ MiniMax engine not configured")
            return
        
        print("✅ MiniMax engine configured")
        print(f"📊 Chunk size setting: {engine.chunk_size_words} words")
        
        # Test chunking logic first
        chunks = engine._split_text_into_chunks(test_text, engine.chunk_size_words)
        print(f"📄 Text will be split into {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"   Chunk {i}: {len(chunk)} chars - '{chunk[:50]}...'")
        
        if len(chunks) == 1:
            print("⚠️ Text not long enough to trigger chunking - extending test...")
            test_text = test_text * 2  # Double the text
            chunks = engine._split_text_into_chunks(test_text, engine.chunk_size_words)
            print(f"📄 Extended text split into {len(chunks)} chunks")
        
        # Generate TTS with chunking (this will trigger MFA per chunk if available)
        print("\n🎯 Generating TTS with MFA chunk processing...")
        
        audio_bytes, word_timings = await engine.generate_speech(
            text=test_text,
            voice="moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430",  # Aria voice
            speed=1.0,
            volume=0.8
        )
        
        print(f"✅ TTS generation completed!")
        print(f"📊 Generated audio: {len(audio_bytes)} bytes")
        print(f"📊 Word timings: {len(word_timings)} words")
        
        # Analyze timing data to see MFA usage
        mfa_words = 0
        jieba_words = 0
        chunk_info_words = 0
        confidence_scores = []
        
        print("\n🔍 Analyzing timing data sources:")
        for i, timing in enumerate(word_timings[:10]):  # Show first 10 words
            word = timing.get("word", "")
            source = timing.get("source", "unknown")
            confidence = timing.get("confidence", 0.0)
            is_chunk = timing.get("is_chunk_timing", False)
            
            print(f"   Word {i+1}: '{word}' | Source: {source} | Confidence: {confidence} | Chunk: {is_chunk}")
            
            if "mfa" in source.lower():
                mfa_words += 1
            elif "jieba" in source.lower():
                jieba_words += 1
            
            if is_chunk:
                chunk_info_words += 1
            
            if confidence > 0:
                confidence_scores.append(confidence)
        
        # Count total sources
        total_mfa = sum(1 for t in word_timings if "mfa" in t.get("source", "").lower())
        total_jieba = sum(1 for t in word_timings if "jieba" in t.get("source", "").lower() or t.get("source", "") == "")
        total_chunk_marked = sum(1 for t in word_timings if t.get("is_chunk_timing", False))
        
        print(f"\n📈 Timing Analysis Summary:")
        print(f"   Total words: {len(word_timings)}")
        print(f"   MFA-aligned words: {total_mfa} ({total_mfa/len(word_timings)*100:.1f}%)")
        print(f"   Jieba-estimated words: {total_jieba} ({total_jieba/len(word_timings)*100:.1f}%)")
        print(f"   Chunk-processed words: {total_chunk_marked} ({total_chunk_marked/len(word_timings)*100:.1f}%)")
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            print(f"   Average confidence: {avg_confidence:.3f}")
        
        # Determine if MFA chunking is working
        print(f"\n🎯 MFA Chunking Assessment:")
        if total_mfa > 0:
            print(f"   ✅ MFA alignment is working! {total_mfa} words processed with MFA")
            if total_chunk_marked > 0:
                print(f"   ✅ Chunk processing is active! {total_chunk_marked} words marked as chunk-processed")
            else:
                print(f"   ⚠️ MFA working but chunk metadata missing")
        else:
            print(f"   ❌ No MFA alignment detected - likely falling back to jieba estimation")
            print(f"   💡 This could mean:")
            print(f"      • MFA not installed or not available")
            print(f"      • MFA models missing")
            print(f"      • All chunk MFA attempts failed and fell back to jieba")
        
        # Save sample result for inspection
        sample_result = {
            "test_summary": {
                "text_length": len(test_text),
                "chunks_generated": len(chunks),
                "total_words": len(word_timings),
                "mfa_words": total_mfa,
                "jieba_words": total_jieba,
                "chunk_marked_words": total_chunk_marked,
                "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            },
            "first_10_words": word_timings[:10],
            "chunk_sizes": [len(chunk) for chunk in chunks]
        }
        
        with open("mfa_chunk_test_sample.json", "w", encoding="utf-8") as f:
            json.dump(sample_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Sample results saved to: mfa_chunk_test_sample.json")
        
        # Conclusion
        if total_mfa > len(word_timings) * 0.5:
            print(f"\n🎉 SUCCESS: MFA chunk processing is working effectively!")
        elif total_mfa > 0:
            print(f"\n⚠️ PARTIAL: MFA chunk processing partially working - some chunks falling back to jieba")
        else:
            print(f"\n❌ ISSUE: MFA chunk processing not working - all words using jieba estimation")
            print(f"   🔧 Check MFA installation and model availability")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mfa_chunking())