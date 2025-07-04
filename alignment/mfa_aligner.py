"""
Montreal Forced Alignment (MFA) Integration
Provides word-level alignment for Chinese TTS audio
"""

import os
import tempfile
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class MFAAligner:
    """Montreal Forced Alignment wrapper for Chinese text-to-speech"""
    
    def __init__(self):
        self.mfa_command = "mfa"
        self.acoustic_model = "mandarin_mfa"
        self.dictionary = "mandarin_mfa"
        self.temp_dir = None
        
        # Check if MFA is installed
        self.is_available = self._check_mfa_installation()
    
    def _check_mfa_installation(self) -> bool:
        """Check if MFA is properly installed and accessible"""
        try:
            result = subprocess.run(
                [self.mfa_command, "version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_models_available(self) -> Dict[str, bool]:
        """Check if required MFA models are downloaded"""
        models_status = {
            "acoustic_model": False,
            "dictionary": False
        }
        
        if not self.is_available:
            return models_status
        
        try:
            # Check acoustic models
            result = subprocess.run(
                [self.mfa_command, "model", "list", "acoustic"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and self.acoustic_model in result.stdout:
                models_status["acoustic_model"] = True
            
            # Check dictionaries
            result = subprocess.run(
                [self.mfa_command, "model", "list", "dictionary"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and self.dictionary in result.stdout:
                models_status["dictionary"] = True
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return models_status
    
    async def download_models(self) -> Dict[str, Any]:
        """Download required MFA models if not present"""
        if not self.is_available:
            return {
                "success": False,
                "error": "MFA not installed or not accessible"
            }
        
        models_status = self._check_models_available()
        downloads = []
        
        try:
            # Download acoustic model if needed
            if not models_status["acoustic_model"]:
                print(f"📥 Downloading MFA acoustic model: {self.acoustic_model}")
                result = subprocess.run(
                    [self.mfa_command, "model", "download", "acoustic", self.acoustic_model],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                if result.returncode == 0:
                    downloads.append(f"acoustic model: {self.acoustic_model}")
                else:
                    return {
                        "success": False,
                        "error": f"Failed to download acoustic model: {result.stderr}"
                    }
            
            # Download dictionary if needed  
            if not models_status["dictionary"]:
                print(f"📥 Downloading MFA dictionary: {self.dictionary}")
                result = subprocess.run(
                    [self.mfa_command, "model", "download", "dictionary", self.dictionary],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                if result.returncode == 0:
                    downloads.append(f"dictionary: {self.dictionary}")
                else:
                    return {
                        "success": False,
                        "error": f"Failed to download dictionary: {result.stderr}"
                    }
            
            return {
                "success": True,
                "downloads": downloads,
                "message": f"Downloaded {len(downloads)} models" if downloads else "All models already available"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Model download timeout (>5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Model download error: {str(e)}"
            }
    
    async def align_chinese_audio(
        self, 
        audio_bytes: bytes, 
        text: str, 
        sentence_timings: Optional[List[Dict[str, Any]]] = None,
        is_chunk: bool = False,
        chunk_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform forced alignment on Chinese audio with full debugging
        
        Args:
            audio_bytes: Audio data in MP3 format
            text: Chinese text corresponding to the audio
            sentence_timings: Optional sentence-level timing constraints
            is_chunk: Whether this is a chunk from a larger text (affects processing)
            chunk_info: Additional info for chunk processing (chunk_id, total_chunks, etc.)
            
        Returns:
            List of word-level timing dictionaries
        """
        print(f"🎯 DEBUG: MFA alignment started")
        print(f"   Audio size: {len(audio_bytes)} bytes")
        print(f"   Text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
        print(f"   Is chunk: {is_chunk}")
        print(f"   Chunk info: {chunk_info}")
        
        if not self.is_available:
            print(f"❌ MFA not available")
            raise RuntimeError("MFA not available for alignment")
        
        models_status = self._check_models_available()
        print(f"   Models status: {models_status}")
        if not all(models_status.values()):
            missing = [k for k, v in models_status.items() if not v]
            print(f"❌ Missing MFA models: {missing}")
            raise RuntimeError(f"Missing MFA models: {', '.join(missing)}")
        
        # Create temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)
            print(f"   Temp directory: {self.temp_dir}")
            
            try:
                # Prepare input files with chunk-specific optimizations
                print(f"   Step 1: Preparing input files...")
                audio_file, text_file = self._prepare_mfa_inputs(audio_bytes, text, is_chunk)
                
                # Run MFA alignment with chunk-aware parameters
                print(f"   Step 2: Running MFA alignment...")
                alignment_output = await self._run_mfa_alignment(audio_file, text_file, is_chunk)
                
                # Parse MFA output and apply timing constraints
                print(f"   Step 3: Parsing MFA output...")
                word_timings = self._parse_mfa_output(alignment_output, sentence_timings, is_chunk)
                
                # Apply chunk-specific post-processing if needed
                if is_chunk and chunk_info:
                    print(f"   Step 4: Post-processing chunk timings...")
                    word_timings = self._post_process_chunk_timings(word_timings, chunk_info)
                
                print(f"✅ MFA alignment completed: {len(word_timings)} words")
                if word_timings:
                    first_word = word_timings[0]
                    print(f"   First word sample: {first_word}")
                
                return word_timings
                
            except Exception as e:
                print(f"❌ MFA alignment failed in pipeline: {str(e)}")
                import traceback
                traceback.print_exc()
                raise RuntimeError(f"MFA alignment failed: {str(e)}")
            finally:
                self.temp_dir = None
    
    def _prepare_mfa_inputs(self, audio_bytes: bytes, text: str, is_chunk: bool = False) -> Tuple[Path, Path]:
        """Prepare audio and text files for MFA processing"""
        # Create corpus directory structure expected by MFA
        corpus_dir = self.temp_dir / "corpus"
        corpus_dir.mkdir()
        
        # Save audio file (convert to WAV if needed)
        audio_file = corpus_dir / "audio.wav"
        self._save_audio_as_wav(audio_bytes, audio_file, is_chunk)
        
        # Save text file with MFA-compatible format
        text_file = corpus_dir / "audio.txt"
        cleaned_text = self._prepare_text_for_mfa(text, is_chunk)
        text_file.write_text(cleaned_text, encoding='utf-8')
        
        return audio_file, text_file
    
    def _save_audio_as_wav(self, audio_bytes: bytes, output_path: Path, is_chunk: bool = False):
        """Convert audio bytes to WAV format for MFA with detailed debugging"""
        import shutil
        
        print(f"🔧 DEBUG: Starting audio conversion")
        print(f"   Input audio size: {len(audio_bytes)} bytes")
        print(f"   Output path: {output_path}")
        print(f"   Is chunk: {is_chunk}")
        
        # Save as temporary MP3 first
        temp_mp3 = self.temp_dir / "temp.mp3"
        temp_mp3.write_bytes(audio_bytes)
        print(f"   Saved temp MP3: {temp_mp3} ({temp_mp3.stat().st_size} bytes)")
        
        # Also save a debug copy we can inspect later
        debug_mp3 = self.temp_dir / "debug_minimax_audio.mp3"
        shutil.copy(temp_mp3, debug_mp3)
        print(f"   Debug copy saved: {debug_mp3}")
        
        # Convert to WAV using ffmpeg (MFA requirement)
        try:
            # Use standard settings that should work with MiniMax audio
            ffmpeg_args = [
                "ffmpeg", "-i", str(temp_mp3), 
                "-ar", "16000",  # 16kHz sample rate (MFA standard)
                "-ac", "1",      # Mono
                "-f", "wav",     # Force WAV format
                "-y",            # Overwrite
                str(output_path)
            ]
            
            print(f"   Running ffmpeg: {' '.join(ffmpeg_args)}")
            result = subprocess.run(ffmpeg_args, check=True, capture_output=True, text=True)
            print(f"   ✅ ffmpeg success: {output_path} ({output_path.stat().st_size} bytes)")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ffmpeg conversion failed:")
            print(f"   Return code: {e.returncode}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            
            # Try alternative approach - use the temp MP3 directly but rename it
            print(f"   Attempting fallback: copying MP3 as WAV extension")
            try:
                shutil.copy(temp_mp3, output_path.with_suffix('.wav'))
                print(f"   Fallback saved: {output_path.with_suffix('.wav')}")
            except Exception as fallback_error:
                print(f"   Fallback failed: {fallback_error}")
                raise RuntimeError(f"Both ffmpeg and fallback failed: {e}, {fallback_error}")
        
        except FileNotFoundError:
            print(f"❌ ffmpeg not found - trying without conversion")
            # Just copy the MP3 file directly
            shutil.copy(temp_mp3, output_path.with_suffix('.mp3'))
            print(f"   Direct MP3 copy: {output_path.with_suffix('.mp3')}")
        
        except Exception as e:
            print(f"❌ Unexpected error in audio conversion: {e}")
            raise
    
    def _prepare_text_for_mfa(self, text: str, is_chunk: bool = False) -> str:
        """
        CHARACTER POSITION SYNC FIX: Keep Chinese punctuation for UI alignment
        
        The key insight: MFA text must have same character positions as UI text
        to ensure word containers align correctly with timing data.
        """
        from text_processor import sanitize_text_for_karaoke
        import re
        
        print(f"🔧 CHARACTER POSITION SYNC FIX: MFA text preprocessing")
        print(f"   Original text: '{text}' ({len(text)} chars)")
        print(f"   Is chunk: {is_chunk}")
        
        # Step 1: Basic cleaning (removes problematic symbols like brackets)
        cleaned = sanitize_text_for_karaoke(text)
        print(f"   After basic cleaning: '{cleaned}' ({len(cleaned)} chars)")
        
        # Step 2: CHARACTER POSITION SYNC FIX - Keep Chinese punctuation for alignment
        # MFA can handle Chinese punctuation and will separate it from words during alignment
        # This maintains character position synchronization with UI text
        chinese_punctuation_to_keep = '，。、？！：；（）""''‚„‹›«»'
        
        # Build pattern: Chinese chars + spaces + Chinese punctuation
        pattern = f'[^\u4e00-\u9fff\s{re.escape(chinese_punctuation_to_keep)}]'
        mfa_text = re.sub(pattern, '', cleaned)
        
        # Normalize whitespace but preserve structure
        mfa_text = re.sub(r'\s+', ' ', mfa_text).strip()
        
        print(f"   CHARACTER POSITION SYNC FIX: '{text}' → '{mfa_text}' ({len(mfa_text)} chars)")
        print(f"   Character count difference: {len(text) - len(mfa_text)} (smaller difference = better alignment)")
        
        if len(mfa_text) == 0:
            print(f"❌ WARNING: Text preprocessing resulted in empty string!")
        elif len(mfa_text) < len(text) * 0.7:  # Updated threshold - expect smaller reduction now
            print(f"⚠️ WARNING: Text significantly reduced after cleaning ({len(mfa_text)}/{len(text)} chars)")
        else:
            print(f"✅ Good character preservation: {len(mfa_text)}/{len(text)} chars retained")
        
        return mfa_text
    
    async def _run_mfa_alignment(self, audio_file: Path, text_file: Path, is_chunk: bool = False) -> Path:
        """Run MFA alignment command with detailed debugging"""
        output_dir = self.temp_dir / "aligned"
        output_dir.mkdir()
        
        print(f"🔧 DEBUG: MFA command setup")
        print(f"   Audio file: {audio_file} (exists: {audio_file.exists()})")
        print(f"   Text file: {text_file} (exists: {text_file.exists()})")
        print(f"   Output dir: {output_dir}")
        
        # Debug: read text file content
        if text_file.exists():
            try:
                text_content = text_file.read_text(encoding='utf-8')
                print(f"   Text content: '{text_content}'")
            except Exception as e:
                print(f"   Could not read text file: {e}")
        
        # Debug: check audio file size
        if audio_file.exists():
            print(f"   Audio file size: {audio_file.stat().st_size} bytes")
        else:
            # Check alternative extensions
            audio_mp3 = audio_file.with_suffix('.mp3')
            audio_wav = audio_file.with_suffix('.wav')
            print(f"   Checking alternatives: MP3={audio_mp3.exists()}, WAV={audio_wav.exists()}")
            if audio_mp3.exists():
                audio_file = audio_mp3
                print(f"   Using MP3 file: {audio_file}")
            elif audio_wav.exists():
                audio_file = audio_wav
                print(f"   Using WAV file: {audio_file}")
        
        cmd = [
            self.mfa_command, "align",
            str(audio_file.parent),  # Corpus directory
            str(self.dictionary),    # Dictionary
            str(self.acoustic_model), # Acoustic model
            str(output_dir),         # Output directory
            "--clean",               # Clean temporary files
            "--verbose",             # Always verbose for debugging
            "--quiet"                # Reduce stdout noise but keep stderr
        ]
        
        print(f"   MFA command: {' '.join(cmd)}")
        
        try:
            # Standard timeout for all operations
            timeout = 120
            
            print(f"   Running MFA (timeout: {timeout}s)...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.temp_dir)  # Run from temp directory
            )
            
            print(f"   MFA return code: {result.returncode}")
            if result.stdout:
                print(f"   MFA stdout: {result.stdout[:500]}...")
            if result.stderr:
                print(f"   MFA stderr: {result.stderr[:500]}...")
            
            if result.returncode != 0:
                raise RuntimeError(f"MFA alignment failed (code {result.returncode}): {result.stderr}")
            
            # Find output TextGrid file
            textgrid_file = output_dir / "audio.TextGrid"
            print(f"   Looking for TextGrid: {textgrid_file}")
            
            if not textgrid_file.exists():
                # List all files in output directory for debugging
                output_files = list(output_dir.glob("*"))
                print(f"   Output directory contents: {[f.name for f in output_files]}")
                raise RuntimeError("MFA did not produce expected TextGrid output")
            
            print(f"   ✅ TextGrid found: {textgrid_file} ({textgrid_file.stat().st_size} bytes)")
            return textgrid_file
            
        except subprocess.TimeoutExpired:
            print(f"❌ MFA alignment timeout after {timeout} seconds")
            raise RuntimeError(f"MFA alignment timeout (>{timeout} seconds)")
        except Exception as e:
            print(f"❌ MFA alignment error: {e}")
            raise
    
    def _parse_mfa_output(
        self, 
        textgrid_file: Path, 
        sentence_timings: Optional[List[Dict[str, Any]]] = None,
        is_chunk: bool = False
    ) -> List[Dict[str, Any]]:
        """Parse MFA TextGrid output to extract word timings"""
        try:
            # Parse TextGrid file (simplified parser)
            word_timings = []
            
            with open(textgrid_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract word intervals from TextGrid
            # This is a simplified parser - in production, use a proper TextGrid library
            import re
            
            # Find word tier intervals
            intervals = re.findall(
                r'intervals \[(\d+)\]:\s*xmin = ([\d.]+)\s*xmax = ([\d.]+)\s*text = "([^"]*)"',
                content
            )
            
            for interval_num, xmin, xmax, text in intervals:
                if text.strip() and text.strip() != "<SIL>":  # Skip silence markers
                    word_timing = {
                        "word": text.strip(),
                        "start_time": float(xmin) * 1000,  # Convert to milliseconds
                        "end_time": float(xmax) * 1000,
                        "offset": float(xmin) * 1000,
                        "duration": (float(xmax) - float(xmin)) * 1000
                    }
                    
                    # Mark as TRUE MFA results (not jieba)
                    if is_chunk:
                        word_timing["confidence"] = 0.95
                        word_timing["source"] = "mfa_chunk"
                        word_timing["is_mfa"] = True  # CRITICAL: Mark as real MFA
                    else:
                        word_timing["confidence"] = 0.85
                        word_timing["source"] = "mfa_full"
                        word_timing["is_mfa"] = True  # CRITICAL: Mark as real MFA
                    
                    word_timings.append(word_timing)
            
            # Apply sentence timing constraints if provided
            if sentence_timings:
                word_timings = self._apply_sentence_constraints(word_timings, sentence_timings, is_chunk)
            
            return word_timings
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse MFA output: {str(e)}")
    
    def _apply_sentence_constraints(
        self, 
        word_timings: List[Dict[str, Any]], 
        sentence_timings: List[Dict[str, Any]],
        is_chunk: bool = False
    ) -> List[Dict[str, Any]]:
        """Apply sentence-level timing constraints to word-level timings"""
        if not sentence_timings or not word_timings:
            return word_timings
        
        # For chunks, apply timing constraint normalization
        if is_chunk and len(sentence_timings) > 0:
            constraint = sentence_timings[0]
            expected_duration = constraint.get("duration", constraint.get("end_time", 0))
            
            if expected_duration > 0 and len(word_timings) > 0:
                # Scale word timings to match expected chunk duration
                actual_duration = word_timings[-1]["end_time"] if word_timings else 0
                
                if actual_duration > 0:
                    scale_factor = expected_duration / actual_duration
                    
                    # Apply scaling to ensure chunk timing matches expected duration
                    for word_timing in word_timings:
                        word_timing["start_time"] *= scale_factor
                        word_timing["end_time"] *= scale_factor
                        word_timing["offset"] *= scale_factor
                        word_timing["duration"] *= scale_factor
        
        return word_timings
    
    def _post_process_chunk_timings(
        self, 
        word_timings: List[Dict[str, Any]], 
        chunk_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply chunk-specific post-processing to timing data"""
        # Add chunk metadata to each word timing
        chunk_id = chunk_info.get("chunk_id", 0)
        total_chunks = chunk_info.get("total_chunks", 1)
        
        for word_timing in word_timings:
            word_timing["chunk_id"] = chunk_id
            word_timing["total_chunks"] = total_chunks
            word_timing["is_chunk_timing"] = True
        
        return word_timings
    
    def get_installation_status(self) -> Dict[str, Any]:
        """Get detailed MFA installation and model status"""
        status = {
            "mfa_installed": self.is_available,
            "models": self._check_models_available() if self.is_available else {},
            "ready": False
        }
        
        if self.is_available:
            models_status = status["models"]
            status["ready"] = all(models_status.values())
        
        return status