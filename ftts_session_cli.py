#!/usr/bin/env python3
"""
FastTTS Audio Session Creator - CLI Tool
Usage: ftts-session audio.wav [options]

Creates a FastTTS session from audio files with MFA alignment and timing data.
"""

import os
import sys
import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the CLI tool"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    return logging.getLogger(__name__)

def validate_audio_file(audio_path: Path) -> bool:
    """Validate that the audio file exists and has a supported extension"""
    if not audio_path.exists():
        return False
    
    supported_extensions = {'.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac'}
    return audio_path.suffix.lower() in supported_extensions

async def extract_audio_text(audio_path: Path, logger: logging.Logger) -> str:
    """
    Extract or prompt for text corresponding to the audio.
    For now, we'll prompt the user. In the future, this could use speech-to-text.
    """
    logger.info("Text extraction needed for MFA alignment")
    
    print(f"\n📄 Processing audio file: {audio_path.name}")
    print("🎯 For accurate word-level timing, please provide the Chinese text that corresponds to this audio.")
    print("💡 Tip: Copy the text from your source material for best alignment results.")
    print("📝 For long texts: Type 'file:' to read from a text file, or 'multi:' for multi-line input\n")
    
    while True:
        text_input = input("Enter the Chinese text (or 'quit' to exit): ").strip()
        
        if text_input.lower() in ['quit', 'exit', 'q']:
            print("❌ Operation cancelled by user")
            sys.exit(0)
        
        # Handle multi-line input
        if text_input.lower() == 'multi:':
            print("📝 Multi-line input mode. Paste your text and press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done:")
            try:
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                text = '\n'.join(lines).strip()
            except KeyboardInterrupt:
                print("\n❌ Input cancelled")
                continue
        
        # Handle file input
        elif text_input.lower().startswith('file:'):
            file_path = text_input[5:].strip()
            if not file_path:
                file_path = input("Enter text file path: ").strip()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                print(f"✅ Loaded {len(text)} characters from {file_path}")
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}")
                continue
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                continue
        
        # Handle direct input
        else:
            text = text_input
        
        if not text:
            print("⚠️ Please enter some text, use 'multi:' for multi-line input, 'file:' to read from file, or 'quit' to exit")
            continue
            
        # Basic validation - check if it contains Chinese characters
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        if chinese_chars == 0:
            print("⚠️ No Chinese characters detected. Please enter Chinese text or 'quit' to exit")
            continue
        
        # Show text length for confirmation
        if len(text) > 500:
            print(f"📊 Text length: {len(text)} characters, {chinese_chars} Chinese characters")
            print(f"📄 Preview: {text[:100]}{'...' if len(text) > 100 else ''}")
            confirm = input("Continue with this text? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '']:
                continue
            
        logger.info(f"Text provided: {len(text)} characters, {chinese_chars} Chinese characters")
        return text

def load_audio_file(audio_path: Path, logger: logging.Logger) -> bytes:
    """Load audio file as bytes"""
    logger.info(f"Loading audio file: {audio_path}")
    
    try:
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        logger.info(f"Audio loaded: {len(audio_bytes)} bytes")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"Failed to load audio file: {e}")
        raise RuntimeError(f"Could not read audio file: {e}")

async def perform_mfa_alignment(audio_bytes: bytes, text: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    """Perform MFA alignment using existing FastTTS infrastructure"""
    try:
        from alignment.mfa_aligner import MFAAligner
        
        logger.info("Initializing MFA aligner")
        aligner = MFAAligner()
        
        if not aligner.is_available:
            logger.warning("MFA not available, falling back to Jieba segmentation")
            return await fallback_timing_estimation(text, audio_bytes, logger)
        
        # Check if models are available
        models_status = aligner._check_models_available()
        if not all(models_status.values()):
            missing = [k for k, v in models_status.items() if not v]
            logger.warning(f"MFA models missing: {missing}")
            
            # Try to download models automatically
            logger.info("Attempting to download missing MFA models...")
            download_result = await aligner.download_models()
            if not download_result.get('success', False):
                logger.warning("Model download failed, falling back to Jieba")
                return await fallback_timing_estimation(text, audio_bytes, logger)
        
        # Preprocess text for MFA alignment
        from text_processor import preprocess_text_for_tts
        processed_text = preprocess_text_for_tts(text)
        logger.info(f"Text preprocessed: '{processed_text}'")
        
        # Perform MFA alignment
        logger.info("Running MFA alignment...")
        word_timings = await aligner.align_chinese_audio(
            audio_bytes=audio_bytes,
            text=processed_text,
            is_chunk=False
        )
        
        logger.info(f"MFA alignment completed: {len(word_timings)} words")
        return word_timings
        
    except Exception as e:
        logger.error(f"MFA alignment failed: {e}")
        logger.info("Falling back to Jieba segmentation")
        return await fallback_timing_estimation(text, audio_bytes, logger)

async def validate_and_fix_timings(audio_bytes: bytes, word_timings: List[Dict[str, Any]], logger: logging.Logger) -> List[Dict[str, Any]]:
    """Validate timing data against actual audio duration and fix overflows"""
    try:
        import subprocess
        import tempfile
        from pathlib import Path
        
        # Get actual audio duration
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        try:
            # Use ffprobe to get exact audio duration
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', temp_audio_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                actual_duration_seconds = float(result.stdout.strip())
                actual_duration_ms = actual_duration_seconds * 1000
                
                logger.info(f"Audio duration: {actual_duration_seconds:.1f}s ({actual_duration_ms:.0f}ms)")
                
                # Check for timing overflows
                max_timestamp = max((w.get('end_time', w.get('start_time', 0)) for w in word_timings), default=0)
                
                if max_timestamp > actual_duration_ms:
                    overflow_ms = max_timestamp - actual_duration_ms
                    logger.warning(f"Timing overflow detected: {overflow_ms:.0f}ms beyond audio end")
                    print(f"⚠️ Fixing timing sync: timestamps extended {overflow_ms/1000:.1f}s beyond audio")
                    
                    # Scale all timings to fit within audio duration with 100ms buffer
                    target_duration = actual_duration_ms - 100  # 100ms buffer
                    scale_factor = target_duration / max_timestamp if max_timestamp > 0 else 1.0
                    
                    logger.info(f"Scaling timings by factor: {scale_factor:.3f}")
                    
                    for word_timing in word_timings:
                        if 'start_time' in word_timing:
                            word_timing['start_time'] *= scale_factor
                        if 'end_time' in word_timing:
                            word_timing['end_time'] *= scale_factor
                        if 'offset' in word_timing:
                            word_timing['offset'] *= scale_factor
                        if 'duration' in word_timing:
                            word_timing['duration'] *= scale_factor
                    
                    print("✅ Timing sync corrected - karaoke highlighting should now work properly")
                else:
                    logger.info("✅ Timing validation passed - no overflow detected")
                    
        finally:
            Path(temp_audio_path).unlink(missing_ok=True)
            
    except Exception as e:
        logger.warning(f"Timing validation failed: {e}")
        print(f"⚠️ Could not validate audio timing - karaoke sync may be affected")
    
    return word_timings

async def fallback_timing_estimation(text: str, audio_bytes: bytes, logger: logging.Logger) -> List[Dict[str, Any]]:
    """Fallback timing estimation using Jieba segmentation"""
    try:
        import jieba
        from text_processor import preprocess_text_for_tts
        
        logger.info("Using Jieba for word segmentation and timing estimation")
        
        # Preprocess text
        processed_text = preprocess_text_for_tts(text)
        
        # Segment text using Jieba
        words = list(jieba.cut(processed_text))
        words = [w.strip() for w in words if w.strip()]
        
        # Estimate audio duration (this is a rough estimation)
        # In a real implementation, you'd use audio analysis libraries
        estimated_duration = len(audio_bytes) / 16000 * 1000  # Very rough estimation
        
        # Distribute timing evenly across words
        word_timings = []
        if words:
            time_per_word = estimated_duration / len(words)
            current_time = 0
            
            for word in words:
                word_timing = {
                    "word": word,
                    "start_time": current_time,
                    "end_time": current_time + time_per_word,
                    "offset": current_time,
                    "duration": time_per_word,
                    "confidence": 0.3,  # Low confidence for estimated timing
                    "source": "jieba_estimation",
                    "is_mfa": False
                }
                word_timings.append(word_timing)
                current_time += time_per_word
        
        logger.info(f"Jieba segmentation completed: {len(word_timings)} words")
        return word_timings
        
    except Exception as e:
        logger.error(f"Fallback timing estimation failed: {e}")
        return []

def create_session_folder(audio_path: Path, output_dir: Optional[Path], folder_name: Optional[str]) -> Path:
    """Create session folder and determine output path"""
    # Determine session name from audio file
    session_name = audio_path.stem
    
    if output_dir:
        # Use specified output directory
        if output_dir.is_absolute():
            session_dir = output_dir / session_name
        else:
            # Make relative to original working directory stored in environment
            original_cwd = os.environ.get('ORIGINAL_CWD', os.getcwd())
            session_dir = Path(original_cwd) / output_dir / session_name
    else:
        # Create in original working directory, not current script directory
        original_cwd = os.environ.get('ORIGINAL_CWD', os.getcwd())
        session_dir = Path(original_cwd) / session_name
    
    # Create folder if it doesn't exist
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir

def save_session_files(
    session_dir: Path, 
    audio_bytes: bytes, 
    text: str, 
    word_timings: List[Dict[str, Any]], 
    audio_path: Path,
    logger: logging.Logger
) -> None:
    """Save the three required session files"""
    logger.info(f"Saving session files to: {session_dir}")
    
    # 1. Save audio file as audio.mp3
    audio_file = session_dir / "audio.mp3"
    with open(audio_file, 'wb') as f:
        f.write(audio_bytes)
    logger.info(f"Saved audio: {audio_file}")
    
    # 2. Create and save metadata.json (matching web format exactly)
    from datetime import datetime
    metadata = {
        "id": session_dir.name,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "word_count": len(word_timings)
    }
    
    metadata_file = session_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved metadata: {metadata_file}")
    
    # 3. Convert timing data to FastTTS web format and save timestamps.json
    from utils.response_helpers import convert_timings_to_word_data
    
    # Convert MFA timing data to web-compatible format
    web_format_timings = convert_timings_to_word_data(word_timings)
    
    timestamps_file = session_dir / "timestamps.json"
    with open(timestamps_file, 'w', encoding='utf-8') as f:
        json.dump(web_format_timings, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved timestamps: {timestamps_file} ({len(web_format_timings)} words)")
    
    logger.info(f"✅ Session created successfully!")
    print(f"\n🎉 Session created: {session_dir}")
    print(f"📁 Files created:")
    print(f"   📄 {audio_file.name} ({len(audio_bytes)} bytes)")
    print(f"   📄 {metadata_file.name} ({len(word_timings)} words)")
    print(f"   📄 {timestamps_file.name} (timing data)")

async def process_audio_file(
    audio_path: Path,
    output_dir: Optional[Path] = None,
    folder_name: Optional[str] = None,
    text_file: Optional[Path] = None,
    verbose: bool = False
) -> None:
    """Main processing function"""
    logger = setup_logging(verbose)
    
    try:
        # Validate input
        if not validate_audio_file(audio_path):
            raise ValueError(f"Invalid or unsupported audio file: {audio_path}")
        
        # Load audio
        audio_bytes = load_audio_file(audio_path, logger)
        
        # Get text from file or user
        if text_file:
            logger.info(f"Loading text from file: {text_file}")
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
                if chinese_chars == 0:
                    raise ValueError("No Chinese characters found in text file")
                logger.info(f"Text loaded from file: {len(text)} characters, {chinese_chars} Chinese characters")
            except Exception as e:
                raise ValueError(f"Failed to read text file: {e}")
        else:
            text = await extract_audio_text(audio_path, logger)
        
        # Perform MFA alignment
        word_timings = await perform_mfa_alignment(audio_bytes, text, logger)
        
        if not word_timings:
            logger.warning("No timing data generated")
            print("⚠️ Warning: No word timing data was generated")
        else:
            # Validate timing data against actual audio duration
            word_timings = await validate_and_fix_timings(audio_bytes, word_timings, logger)
        
        # Create session folder
        session_dir = create_session_folder(audio_path, output_dir, folder_name)
        
        # Save session files
        save_session_files(session_dir, audio_bytes, text, word_timings, audio_path, logger)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Create FastTTS sessions from audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ftts-session audio.wav                      # Creates ./audio/ folder with session files
  ftts-session audio.wav --output /path/      # Creates session in specified directory  
  ftts-session audio.wav --text-file text.txt # Use text from file (for long texts)
  ftts-session audio.wav --verbose            # Show detailed processing information

Text Input Options:
  - Interactive: Copy/paste text when prompted (works for short texts)
  - Multi-line: Type 'multi:' then paste long text, end with Ctrl+D
  - File input: Type 'file:/path/to/text.txt' or use --text-file argument

The tool will create a folder with three files:
  - audio.mp3: The audio file
  - metadata.json: Session metadata
  - timestamps.json: Word-level timing data from MFA alignment
        """)
    
    parser.add_argument(
        "audio_file",
        type=Path,
        help="Input audio file (wav, mp3, m4a, aac, ogg, flac)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output directory (default: current directory)"
    )
    
    parser.add_argument(
        "--folder", "-f",
        type=str,
        help="Folder name for session organization (future use)"
    )
    
    parser.add_argument(
        "--text-file", "-t",
        type=Path,
        help="Text file containing Chinese text (avoids manual input)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed processing information"
    )
    
    args = parser.parse_args()
    
    # Welcome message
    print("🚀 FastTTS Audio Session Creator")
    print("=================================")
    
    # Run the main processing function
    asyncio.run(process_audio_file(
        audio_path=args.audio_file,
        output_dir=args.output,
        folder_name=args.folder,
        text_file=args.text_file,
        verbose=args.verbose
    ))

if __name__ == "__main__":
    main()