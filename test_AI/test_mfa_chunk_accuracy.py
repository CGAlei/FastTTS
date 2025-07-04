#!/usr/bin/env python3
"""
Test script to validate MFA chunk-based timing accuracy improvements
Compares timing accuracy between jieba estimation and MFA chunk alignment
"""

import asyncio
import time
import json
import logging
from typing import List, Dict, Any
from tts.minimax_tts_engine import MinimaxTTSEngine
from tts.tts_factory import TTSFactory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mfa_chunk_test')

# Test texts of varying lengths to validate chunk processing
TEST_TEXTS = {
    "short": "今天天气很好，我们去公园散步。",
    "medium": "常常听人说，所有的道路终将通向真理。但这条路上有太多岔路，太多诱惑，太多让人迷失方向的风景。有时候我们走着走着就忘记了最初的目标，被路边的花香吸引，被远山的美景迷惑。",
    "long": "在这个快速发展的时代，人工智能技术正在深刻地改变着我们的生活。从简单的语音识别到复杂的自然语言处理，从基础的图像识别到高级的计算机视觉，AI技术的应用范围越来越广泛。特别是在教育领域，智能学习系统能够根据每个学生的特点提供个性化的学习方案，大大提高了学习效率。同时，在医疗健康方面，AI辅助诊断系统可以帮助医生更准确地识别疾病，为患者提供更好的治疗方案。"
}

# MiniMax voices to test with different speaking characteristics
TEST_VOICES = [
    "moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430",  # Aria (Female)
    "moss_audio_afeaf743-22e7-11f0-b934-42db1b8d9b3b",  # Kevin (Male)
]

class ChunkMFAAccuracyTester:
    """Test suite for MFA chunk timing accuracy"""
    
    def __init__(self):
        self.results = {}
        self.minimax_engine = None
        
    async def setup(self):
        """Initialize test environment"""
        logger.info("🔧 Setting up MFA chunk accuracy test...")
        
        # Create MiniMax TTS engine
        try:
            self.minimax_engine = TTSFactory.create_engine("minimax")
            if not self.minimax_engine.is_configured():
                logger.error("❌ MiniMax TTS engine not configured")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to initialize MiniMax engine: {e}")
            return False
        
        # Check MFA availability
        try:
            from alignment import MFAAligner
            aligner = MFAAligner()
            if not aligner.is_available:
                logger.warning("⚠️ MFA not available - will test jieba estimation only")
            else:
                logger.info("✅ MFA aligner available for testing")
        except ImportError:
            logger.warning("⚠️ MFA aligner not installed - testing jieba estimation only")
        
        return True
    
    async def test_timing_accuracy(self, text_key: str, text: str, voice: str) -> Dict[str, Any]:
        """Test timing accuracy for a specific text and voice combination"""
        logger.info(f"🎯 Testing timing accuracy: {text_key} text with {voice}")
        
        test_result = {
            "text_key": text_key,
            "text": text,
            "voice": voice,
            "text_length": len(text),
            "chunk_count": 0,
            "processing_time": 0,
            "mfa_chunks_successful": 0,
            "total_words": 0,
            "timing_source": [],
            "confidence_scores": [],
            "timing_precision": None,
            "success": False,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            # Generate TTS with chunk-based MFA alignment
            audio_bytes, word_timings = await self.minimax_engine.generate_speech(
                text=text,
                voice=voice,
                speed=1.0,
                volume=0.8
            )
            
            processing_time = time.time() - start_time
            
            # Analyze timing results
            test_result.update({
                "processing_time": processing_time,
                "total_words": len(word_timings),
                "success": True
            })
            
            # Count chunks (estimate based on text length and chunk size)
            estimated_chunks = max(1, len(text) // (self.minimax_engine.chunk_size_words * 2))
            test_result["chunk_count"] = estimated_chunks
            
            # Analyze timing data quality
            if word_timings:
                # Check timing sources and confidence scores
                mfa_count = 0
                confidence_scores = []
                timing_sources = []
                
                for timing in word_timings:
                    source = timing.get("source", "jieba_estimation")
                    timing_sources.append(source)
                    
                    if "mfa" in source:
                        mfa_count += 1
                    
                    confidence = timing.get("confidence", 0.0)
                    if confidence > 0:
                        confidence_scores.append(confidence)
                
                test_result.update({
                    "mfa_chunks_successful": mfa_count,
                    "timing_source": timing_sources,
                    "confidence_scores": confidence_scores,
                    "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                    "mfa_coverage": mfa_count / len(word_timings) if word_timings else 0.0
                })
                
                # Calculate timing precision metrics
                timing_precision = self._calculate_timing_precision(word_timings)
                test_result["timing_precision"] = timing_precision
                
                logger.info(f"✅ Test completed: {len(word_timings)} words, {mfa_count} MFA-aligned, avg confidence: {test_result['avg_confidence']:.2f}")
            else:
                logger.warning(f"⚠️ No word timings generated for {text_key}")
                
        except Exception as e:
            logger.error(f"❌ Test failed for {text_key}: {e}")
            test_result.update({
                "success": False,
                "error": str(e)
            })
        
        return test_result
    
    def _calculate_timing_precision(self, word_timings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate timing precision metrics"""
        if not word_timings:
            return {}
        
        # Calculate basic timing metrics
        total_duration = word_timings[-1]["end_time"] if word_timings else 0
        avg_word_duration = total_duration / len(word_timings) if word_timings else 0
        
        # Calculate timing gap consistency
        gaps = []
        for i in range(len(word_timings) - 1):
            gap = word_timings[i + 1]["start_time"] - word_timings[i]["end_time"]
            gaps.append(gap)
        
        gap_variance = sum((g - sum(gaps) / len(gaps))**2 for g in gaps) / len(gaps) if gaps else 0
        
        # Calculate word duration variance (consistency metric)
        durations = [timing["duration"] for timing in word_timings]
        avg_duration = sum(durations) / len(durations)
        duration_variance = sum((d - avg_duration)**2 for d in durations) / len(durations)
        
        return {
            "total_duration_ms": total_duration,
            "avg_word_duration_ms": avg_word_duration,
            "word_count": len(word_timings),
            "gap_variance": gap_variance,
            "duration_variance": duration_variance,
            "timing_consistency": 1.0 / (1.0 + duration_variance / 1000),  # Normalized consistency score
        }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive timing accuracy test across all text lengths and voices"""
        logger.info("🚀 Starting comprehensive MFA chunk timing accuracy test...")
        
        if not await self.setup():
            return {"success": False, "error": "Setup failed"}
        
        test_results = {
            "test_timestamp": time.time(),
            "test_summary": {},
            "detailed_results": [],
            "performance_metrics": {},
            "recommendations": []
        }
        
        total_tests = len(TEST_TEXTS) * len(TEST_VOICES)
        completed_tests = 0
        successful_tests = 0
        
        # Run tests for each combination
        for text_key, text in TEST_TEXTS.items():
            for voice in TEST_VOICES:
                logger.info(f"📋 Running test {completed_tests + 1}/{total_tests}: {text_key} + {voice}")
                
                result = await self.test_timing_accuracy(text_key, text, voice)
                test_results["detailed_results"].append(result)
                
                completed_tests += 1
                if result["success"]:
                    successful_tests += 1
                
                # Add delay between tests to respect rate limits
                await asyncio.sleep(2)
        
        # Calculate summary metrics
        test_results["test_summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests,
            "average_mfa_coverage": sum(r.get("mfa_coverage", 0) for r in test_results["detailed_results"]) / len(test_results["detailed_results"]),
            "average_confidence": sum(r.get("avg_confidence", 0) for r in test_results["detailed_results"]) / len(test_results["detailed_results"])
        }
        
        # Generate performance analysis
        self._analyze_performance(test_results)
        
        # Generate recommendations
        self._generate_recommendations(test_results)
        
        logger.info(f"✅ Comprehensive test completed: {successful_tests}/{total_tests} successful")
        logger.info(f"📊 Average MFA coverage: {test_results['test_summary']['average_mfa_coverage']:.1%}")
        logger.info(f"📊 Average confidence: {test_results['test_summary']['average_confidence']:.2f}")
        
        return test_results
    
    def _analyze_performance(self, test_results: Dict[str, Any]):
        """Analyze performance metrics from test results"""
        detailed_results = test_results["detailed_results"]
        
        # Group results by text length
        by_length = {}
        for result in detailed_results:
            length = result["text_key"]
            if length not in by_length:
                by_length[length] = []
            by_length[length].append(result)
        
        # Calculate performance by text length
        performance_by_length = {}
        for length, results in by_length.items():
            successful = [r for r in results if r["success"]]
            if successful:
                performance_by_length[length] = {
                    "avg_processing_time": sum(r["processing_time"] for r in successful) / len(successful),
                    "avg_mfa_coverage": sum(r.get("mfa_coverage", 0) for r in successful) / len(successful),
                    "avg_confidence": sum(r.get("avg_confidence", 0) for r in successful) / len(successful),
                    "avg_words": sum(r["total_words"] for r in successful) / len(successful)
                }
        
        test_results["performance_metrics"] = {
            "by_text_length": performance_by_length,
            "overall_metrics": {
                "chunk_processing_effective": test_results["test_summary"]["average_mfa_coverage"] > 0.5,
                "timing_quality_improved": test_results["test_summary"]["average_confidence"] > 0.8,
                "rate_limit_respected": all(r.get("processing_time", 0) > 1.0 for r in detailed_results)
            }
        }
    
    def _generate_recommendations(self, test_results: Dict[str, Any]):
        """Generate recommendations based on test results"""
        recommendations = []
        
        avg_mfa_coverage = test_results["test_summary"]["average_mfa_coverage"]
        avg_confidence = test_results["test_summary"]["average_confidence"]
        
        if avg_mfa_coverage < 0.3:
            recommendations.append("LOW_MFA_COVERAGE: Consider checking MFA installation and model availability")
        elif avg_mfa_coverage < 0.7:
            recommendations.append("MODERATE_MFA_COVERAGE: Some chunks falling back to jieba estimation - consider optimizing chunk size")
        else:
            recommendations.append("HIGH_MFA_COVERAGE: MFA chunk processing working effectively")
        
        if avg_confidence < 0.8:
            recommendations.append("LOW_CONFIDENCE: Consider adjusting MFA parameters for better alignment accuracy")
        else:
            recommendations.append("HIGH_CONFIDENCE: MFA alignment producing high-quality timing data")
        
        # Check performance by text length
        perf_metrics = test_results.get("performance_metrics", {})
        by_length = perf_metrics.get("by_text_length", {})
        
        if "long" in by_length:
            long_coverage = by_length["long"].get("avg_mfa_coverage", 0)
            if long_coverage < 0.5:
                recommendations.append("LONG_TEXT_ISSUE: MFA coverage decreases for longer texts - consider smaller chunk sizes")
        
        test_results["recommendations"] = recommendations

async def main():
    """Main test execution"""
    tester = ChunkMFAAccuracyTester()
    
    print("🧪 MFA Chunk Timing Accuracy Test")
    print("=" * 50)
    
    # Run comprehensive test
    results = await tester.run_comprehensive_test()
    
    # Save results to file
    output_file = f"mfa_chunk_test_results_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Test Results Summary:")
    print(f"Success Rate: {results.get('test_summary', {}).get('success_rate', 0):.1%}")
    print(f"MFA Coverage: {results.get('test_summary', {}).get('average_mfa_coverage', 0):.1%}")
    print(f"Average Confidence: {results.get('test_summary', {}).get('average_confidence', 0):.2f}")
    
    print(f"\n📝 Recommendations:")
    for rec in results.get("recommendations", []):
        print(f"  • {rec}")
    
    print(f"\n💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())