"""
MiniMax Hailuo TTS Engine (Refactored for Clarity and Maintainability)
Handles text-to-speech using MiniMax API with sentence-level timing
Requires Montreal Forced Alignment for word-level timing extraction
"""

# Standard Library Imports

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

# Third-Party Imports
import requests
import jieba

# Optional imports with error handling
try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None

try:
    from mutagen.mp3 import MP3
except ImportError:
    MP3 = None

# Project-Specific Imports
from .base_tts import BaseTTSEngine
from debug_logger import log_mfa_call, log_conversion, log_error, log_session_data

# Configure logging for MiniMax TTS
logging.basicConfig(level=logging.INFO)
minimax_logger = logging.getLogger('minimax_tts')

# Check for debug mode environment variable
DEBUG_MODE = os.environ.get('FASTTTS_DEBUG_MODE', '').lower() in ('1', 'true', 'yes', 'on')
minimax_logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)


class MinimaxTTSEngine(BaseTTSEngine):
    """MiniMax Hailuo TTS implementation with forced alignment"""
    
    def __init__(self):
        super().__init__("MiniMax Hailuo")
        self.default_voice = "moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430"  # Aria (Custom Female)
        self.base_url = "https://api.minimax.io/v1/t2a_v2"
        
        self._load_credentials()
        
        self.chunk_size_words = int(os.getenv("MINIMAX_CHUNK_SIZE", "120"))
        self.max_requests_per_minute = 58  # Optimized for 60 RPM limit
        
        # MiniMax voice options (including custom voices)
        self.supported_voices = [
            # Custom MiniMax voices
            {"id": "moss_audio_96a80421-22ea-11f0-92db-0e8893cbb430", "name": "Aria (Custom Female)", "language": "zh-CN", "type": "custom"},
            {"id": "moss_audio_afeaf743-22e7-11f0-b934-42db1b8d9b3b", "name": "Kevin (Custom Male)", "language": "zh-CN", "type": "custom"},
            {"id": "moss_audio_2d7de658-22bd-11f0-92db-0e8893cbb430", "name": "Nelson (Custom Male)", "language": "zh-CN", "type": "custom"},
            {"id": "moss_audio_943faac0-1fbf-11f0-97b0-d62ca20b6c41", "name": "Vera (Custom Female)", "language": "zh-CN", "type": "custom"},
            {"id": "Chinese (Mandarin)_Lyrical_Voice", "name": "Liyue (Lyrical Voice)", "language": "zh-CN", "type": "custom"},
            {"id": "Chinese (Mandarin)_Gentleman", "name": "Willi (Gentleman)", "language": "zh-CN", "type": "custom"},
            {"id": "Chinese (Mandarin)_Reliable_Executive", "name": "Exe (Reliable Executive)", "language": "zh-CN", "type": "custom"}
        ]
        
        # Available MiniMax models
        self.supported_models = [
            {"id": "speech-02-turbo", "name": "Speech-02 Turbo (Fast & Efficient)", "description": "Enhanced multilingual with low latency"},
            {"id": "speech-02-hd", "name": "Speech-02 HD (High Quality)", "description": "Superior rhythm and stability with outstanding quality"},
            {"id": "speech-01-turbo", "name": "Speech-01 Turbo (Legacy)", "description": "Excellent performance and low latency"},
            {"id": "speech-01-hd", "name": "Speech-01 HD (Legacy)", "description": "Rich voices, expressive emotions"}
        ]
        
        # Chinese converter is now handled by shared utility
        minimax_logger.info("🔤 Chinese Traditional→Simplified conversion handled by shared converter")
    
    def _load_credentials(self):
        """Load credentials and settings from environment variables."""
        self.api_key = os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")
        self.custom_voice_id = os.getenv("MINIMAX_CUSTOM_VOICE_ID", "")
        self.preferred_model = os.getenv("MINIMAX_MODEL", "speech-02-turbo")
        minimax_logger.info("🔑 MiniMax credentials loaded.")
    
    def is_configured(self) -> bool:
        """Check if MiniMax API credentials are configured."""
        self._load_credentials()
        is_ready = bool(self.api_key and self.group_id)
        minimax_logger.info(f"🔧 MiniMax configuration status: {'✅ Ready' if is_ready else '❌ Not configured'}")
        return is_ready
    
    def get_supported_models(self) -> List[Dict[str, str]]:
        return self.supported_models.copy()
    
    def get_current_model(self) -> str:
        self._load_credentials()
        return self.preferred_model
    
    async def generate_speech(
        self, text: str, voice: str = None, speed: float = 1.0, volume: float = 0.8, **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Main entry point for generating speech."""
        minimax_logger.info(f"🎯 MiniMax TTS generation started for text: '{text[:50]}...'")
        
        if not self.is_configured():
            raise RuntimeError("MiniMax API credentials not configured.")
        
        voice = voice or self.default_voice
        if not self.validate_voice(voice):
            raise ValueError(f"Unsupported voice: {voice}")
        
        from text_processor import preprocess_text_for_tts
        preprocessed_text = preprocess_text_for_tts(text)
        if not preprocessed_text:
            raise ValueError("No valid text after preprocessing.")
        
        try:
            chunks = self._split_text_into_chunks(preprocessed_text, max_words=self.chunk_size_words)
            if len(chunks) == 1:
                return await self._generate_single_chunk(preprocessed_text, voice, speed, volume, **kwargs)
            else:
                from progress_manager import progress_manager
                progress_session_id = progress_manager.create_session(total_chunks=len(chunks))
                return await self._generate_chunked_speech(chunks, voice, speed, volume, progress_session_id, **kwargs)
        except Exception as e:
            minimax_logger.error(f"❌ MiniMax TTS generation failed: {str(e)}")
            raise
    
    async def _call_minimax_api(
        self, text: str, voice: str, speed: float, volume: float
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Calls the MiniMax API and returns audio bytes and sentence timings."""
        url = f"{self.base_url}?GroupId={self.group_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        actual_voice = self.custom_voice_id if self.custom_voice_id and voice in ["custom", self.custom_voice_id] else voice
        
        payload = {
            "model": self.preferred_model, "text": text, "stream": False,
            "voice_setting": {"voice_id": actual_voice, "speed": speed, "vol": volume, "pitch": 0},
            "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "mp3", "channel": 1},
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get("base_resp", {}).get("status_code") != 0:
                raise RuntimeError(f"MiniMax API error: {result.get('base_resp', {}).get('status_msg', 'Unknown')}")
            
            audio_hex = result.get("data", {}).get("audio")
            if not audio_hex:
                raise RuntimeError("No audio data in API response.")
            
            audio_bytes = bytes.fromhex(audio_hex)
            audio_length_ms = result.get("extra_info", {}).get("audio_length", 0)
            sentence_timings = [{"text": text, "start_time": 0, "end_time": audio_length_ms}] if audio_length_ms > 0 else []
            
            return audio_bytes, sentence_timings
        except requests.RequestException as e:
            raise RuntimeError(f"MiniMax API request failed: {e}") from e
    
    
    async def _extract_word_timings(
        self, audio_bytes: bytes, text: str, sentence_timings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extracts word timings using MFA, with a fallback to estimation."""
        try:
            from alignment import MFAAligner
            aligner = MFAAligner()
            if not aligner.is_available:
                minimax_logger.warning("⚠️ MFA not available, falling back to estimation.")
                return self._estimate_word_timings(text, sentence_timings)
            return await aligner.align_chinese_audio(audio_bytes, text, sentence_timings)
        except Exception as e:
            minimax_logger.warning(f"MFA alignment failed: {e}. Falling back to estimation.")
            return self._estimate_word_timings(text, sentence_timings)
    
    
    
    
    def _estimate_word_timings(
        self, text: str, sentence_timings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Estimates word timings using Jieba and duration ratio."""
        words = [word.strip() for word in jieba.cut(text, cut_all=False) if word.strip()]
        if not words: return []

        total_duration = sentence_timings[0].get("end_time", len(words) * 400) if sentence_timings else len(words) * 400
        total_chars = sum(len(w) for w in words)
        if total_duration <= 0 or total_chars == 0: return []

        timings, current_time = [], 0.0
        for word in words:
            duration = max(total_duration * (len(word) / total_chars), 100)
            end_time = current_time + duration
            timings.append({
                "word": word, "start_time": current_time, "end_time": end_time, "duration": duration,
                "source": "jieba_estimation", "confidence": 0.0, "is_mfa": False
            })
            current_time = end_time
        return timings

    def _finalize_timings(self, word_timings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies final conversion, filtering, and validation to word timings."""
        converted = self._convert_traditional_to_simplified(word_timings)
        filtered = self._filter_punctuation_timings(converted)
        
        # Validate that all characters are Simplified Chinese
        from utils.chinese_converter import get_chinese_converter
        converter = get_chinese_converter()
        validation_result = converter.validate_simplified_chinese(filtered)
        
        if not validation_result['is_valid']:
            minimax_logger.error(f"🚨 CRITICAL: Traditional characters found in final output!")
            minimax_logger.error(f"🔍 Traditional chars: {validation_result['traditional_chars_found']}")
            minimax_logger.error(f"📝 Affected words: {[w['word'] for w in validation_result['traditional_words']]}")
        
        return filtered
    
    def get_supported_voices(self) -> List[Dict[str, str]]:
        """Get list of supported MiniMax voices"""
        return self.supported_voices.copy()
    
    def validate_voice(self, voice_id: str) -> bool:
        return any(voice["id"] == voice_id for voice in self.supported_voices)

    async def _handle_rate_limit(self, chunk_index: int, total_chunks: int, chunk_start_time: float):
        """Calculates and applies a delay to respect API rate limits."""
        if chunk_index == 0: return

        if total_chunks <= 3:
            delay = 0.1  # Burst mode for small jobs
            minimax_logger.info("🚀 Burst mode active (minimal delay).")
        else:
            elapsed = time.time() - chunk_start_time
            required_delay = 60.0 / self.max_requests_per_minute
            delay = max(0, required_delay - elapsed)
            if delay > 0: minimax_logger.info(f"⏳ Smart rate-limiting delay: {delay:.1f}s")
        
        if delay > 0:
            await asyncio.sleep(delay)
    
    def _find_best_break_point(self, words: List[str], target_length: int) -> int:
        """Finds a natural punctuation break point near the target length."""
        sentence_endings = {'。', '！', '？', '!', '?', '.'}
        clause_breaks = {'，', '、', ',', ';', '；'}
        
        search_range = max(5, int(target_length * 0.2))
        min_pos, max_pos = max(target_length - search_range, 1), min(target_length + search_range, len(words))
        
        best_pos, best_priority = target_length, -1
        for i in range(min_pos, max_pos):
            word = words[i]
            priority = 2 if any(p in word for p in sentence_endings) else 1 if any(p in word for p in clause_breaks) else -1
            if priority > best_priority or (priority == best_priority and abs(i - target_length) < abs(best_pos - target_length)):
                best_pos, best_priority = i, priority
        return best_pos

    def _split_text_into_chunks(self, text: str, max_words: int = 120) -> List[str]:
        """Splits text into naturally-breaking chunks."""
        words = [word.strip() for word in jieba.cut(text, cut_all=False) if word.strip()]
        if not words: return [text]
        
        chunks, current_start = [], 0
        while current_start < len(words):
            target_end = current_start + max_words
            if target_end >= len(words):
                chunks.append(''.join(words[current_start:]))
                break
            
            break_point = self._find_best_break_point(words[current_start:], min(max_words, len(words) - current_start))
            chunk_end = current_start + break_point
            chunks.append(''.join(words[current_start:chunk_end]))
            current_start = chunk_end
        
        return chunks
    
    async def _generate_single_chunk(
        self, text: str, voice: str, speed: float, volume: float, **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Generates audio and timings for a single chunk of text."""
        audio_bytes, sentence_timings = await self._call_minimax_api(text, voice, speed, volume)
        word_timings = await self._extract_word_timings(audio_bytes, text, sentence_timings)
        final_timings = self._finalize_timings(word_timings)
        return audio_bytes, final_timings
    
    def _convert_traditional_to_simplified(self, word_timings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert Traditional Chinese characters to Simplified for Simplified Chinese UI compatibility.
        
        Uses OpenCC (tw2s) for standard conversions plus UI compatibility mapping for characters
        that OpenCC considers linguistically ambiguous but need conversion for UI consistency.
        
        MFA mandarin_mfa model returns Traditional Chinese characters, but this Simplified Chinese
        UI requires all characters to be in Simplified form for proper word container recognition.
        
        Args:
            word_timings: List of timing dictionaries with Traditional Chinese words
            
        Returns:
            List with Traditional Chinese converted to Simplified Chinese for UI compatibility
        """
        # Use robust Chinese converter that NEVER fails
        from utils.chinese_converter import get_chinese_converter
        
        converter = get_chinese_converter()
        return converter.convert_word_timings(word_timings)

    def _filter_punctuation_timings(self, word_timings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove ALL punctuation entries to match Edge TTS behavior
        
        Edge TTS naturally returns only word boundaries, excluding punctuation.
        This filter ensures MiniMax behaves identically by removing punctuation
        timing entries from MFA results.
        
        Args:
            word_timings: List of timing dictionaries from MFA
            
        Returns:
            Filtered list containing only Chinese word timings
        """
        all_punctuation = {
            # Chinese punctuation
            '，', '。', '、', '？', '！', '：', '；', '（', '）', '"', '"', ''', ''',
            # Western punctuation  
            ',', '.', '!', '?', ':', ';', '(', ')', '"', "'",
            # Brackets/containers (NEVER in UI - user requirement)
            '{', '}', '[', ']', '【', '】', '〈', '〉', '《', '》', '〔', '〕', '［', '］', 
            '｛', '｝', '＜', '＞', '〖', '〗', '〘', '〙', '〚', '〛',
            # Additional symbols that create containers
            '—', '–', '…', '·', '@', '#', '$', '%', '^', '&', '*', '_', '=', '+', 
            '|', '\\', '<', '>', '/', '~', '`'
        }
        
        filtered = []
        total_words = len(word_timings)
        
        for timing in word_timings:
            word = timing.get("word", "").strip()
            
            # Keep only if: not empty, not pure punctuation, contains Chinese characters
            if (word and 
                word not in all_punctuation and 
                not word.isspace() and
                any('\u4e00' <= char <= '\u9fff' for char in word)):
                filtered.append(timing)
        
        minimax_logger.info(f"🧹 Punctuation filter: {total_words} → {len(filtered)} entries (removed {total_words - len(filtered)} punctuation)")
        
        return filtered
    
    async def _generate_chunked_speech(
        self, chunks: List[str], voice: str, speed: float, volume: float, progress_session_id: str, **kwargs
    ) -> Tuple[bytes, List[Dict[str, Any]]]:
        """Processes multiple chunks, combines them, and runs a final MFA pass."""
        all_audio_bytes, temporary_timings = [], []
        chunk_start_time, cumulative_time = 0.0, 0.0

        for i, chunk in enumerate(chunks):
            from progress_manager import progress_manager
            progress_manager.update_progress(progress_session_id, i + 1, f"Processing chunk {i+1}/{len(chunks)}...")
            await self._handle_rate_limit(i, len(chunks), chunk_start_time)
            chunk_start_time = time.time()
            
            try:
                audio, timings = await self._call_minimax_api(chunk, voice, speed, volume)
                estimated_timings = self._estimate_word_timings(chunk, timings)
                all_audio_bytes.append(audio)
                temporary_timings.extend(self._adjust_timing_offsets(estimated_timings, cumulative_time))
                cumulative_time += self._get_actual_audio_duration(audio)
            except Exception as e:
                if "429" in str(e):
                    await asyncio.sleep(20)
                    audio, timings = await self._call_minimax_api(chunk, voice, speed, volume)
                    estimated_timings = self._estimate_word_timings(chunk, timings)
                    all_audio_bytes.append(audio)
                    temporary_timings.extend(self._adjust_timing_offsets(estimated_timings, cumulative_time))
                    cumulative_time += self._get_actual_audio_duration(audio)
                else:
                    progress_manager.set_error(progress_session_id, f"Chunk {i+1} failed: {e}")
                    raise

        combined_audio = b''.join(all_audio_bytes)
        
        progress_manager.update_progress(progress_session_id, len(chunks), "Running final alignment...")
        perfect_timings = await self._run_final_mfa_pass(combined_audio, chunks)

        final_word_timings = perfect_timings if any(t.get("is_mfa") for t in perfect_timings) else temporary_timings
        
        final_timings = self._finalize_timings(final_word_timings)
        progress_manager.complete_session(progress_session_id)
        
        return combined_audio, final_timings
    
    async def _run_final_mfa_pass(self, audio_bytes: bytes, text_chunks: List[str]) -> List[Dict[str, Any]]:
        """Runs a single MFA pass on the combined audio for optimal timing accuracy."""
        if not audio_bytes: return []
        full_text = ''.join(text_chunks)
        try:
            from alignment import MFAAligner
            aligner = MFAAligner()
            if not aligner.is_available:
                minimax_logger.warning("⚠️ Final MFA pass skipped: aligner not available.")
                return []
            
            duration = self._get_actual_audio_duration(audio_bytes)
            sentence_timing = [{"text": full_text, "start_time": 0, "end_time": duration}]
            
            minimax_logger.info("🎯 Running final, combined MFA pass for perfect timing...")
            return await aligner.align_chinese_audio(audio_bytes, full_text, sentence_timing)
        except Exception as e:
            minimax_logger.warning(f"⚠️ Final MFA pass failed: {e}. Fallback timings will be used.")
            return []
    
    def _adjust_timing_offsets(self, timings: List[Dict], offset: float) -> List[Dict]:
        """Adjusts word timing offsets for chunked audio."""
        return [{
            **t, 
            'start_time': t['start_time'] + offset, 
            'end_time': t['end_time'] + offset,
            'offset': t.get('offset', t['start_time']) + offset
        } for t in timings]

    def _get_actual_audio_duration(self, audio_bytes: bytes) -> float:
        """Gets precise audio duration using available tools."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_f:
            temp_f.write(audio_bytes)
            temp_path = temp_f.name
        
        duration_ms = 0
        try:
            if MP3:
                audio = MP3(temp_path)
                duration_ms = audio.info.length * 1000
        except Exception:
            try:
                result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', temp_path],
                                        capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    duration_ms = float(json.loads(result.stdout)['format']['duration']) * 1000
            except Exception:
                bytes_per_second = 128000 / 8
                duration_ms = (len(audio_bytes) / bytes_per_second) * 1000
        finally:
            os.unlink(temp_path)
        return max(duration_ms, 100)
    
    
