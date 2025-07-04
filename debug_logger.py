#!/usr/bin/env python3
"""
Comprehensive debug logger for FastTTS
Logs all console outputs, MFA calls, and conversion operations
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

class DebugLogger:
    """Centralized debug logger for FastTTS operations"""
    
    def __init__(self, log_file_path=None):
        if log_file_path is None:
            # Use project root directory for debug.log
            project_root = Path(__file__).parent.resolve()
            log_file_path = project_root / "debug.log"
        self.log_file = Path(log_file_path)
        self.session_start = datetime.now()
        
        # Create or clear log file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"FastTTS Debug Log - Session Started: {self.session_start}\n")
            f.write("=" * 80 + "\n\n")
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('FastTTS_Debug')
        self.mfa_call_count = 0
        self.conversion_count = 0
        
        self.logger.info("🚀 DEBUG LOGGER INITIALIZED")
        self.logger.info(f"📁 Log file: {self.log_file}")
    
    def log_mfa_call(self, text_length, is_chunk=False, chunk_info=None):
        """Log MFA alignment call"""
        self.mfa_call_count += 1
        call_type = "CHUNK" if is_chunk else "FULL"
        
        self.logger.critical(f"🎯 MFA CALL #{self.mfa_call_count} - TYPE: {call_type}")
        self.logger.critical(f"   Text length: {text_length} chars")
        if chunk_info:
            self.logger.critical(f"   Chunk info: {chunk_info}")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"MFA CALL #{self.mfa_call_count} - {call_type}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Text length: {text_length}\n")
            if chunk_info:
                f.write(f"Chunk info: {chunk_info}\n")
            f.write(f"{'='*50}\n\n")
    
    def log_conversion(self, original_count, converted_count, examples=None):
        """Log Traditional→Simplified conversion"""
        self.conversion_count += 1
        
        self.logger.warning(f"🔄 CONVERSION #{self.conversion_count}")
        self.logger.warning(f"   {converted_count}/{original_count} words converted")
        if examples:
            self.logger.warning(f"   Examples: {examples[:5]}")  # First 5 examples
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nCONVERSION #{self.conversion_count}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Words: {converted_count}/{original_count} converted\n")
            if examples:
                f.write(f"Examples: {examples}\n")
            f.write("-" * 30 + "\n")
    
    def log_error(self, operation, error_msg):
        """Log errors with full context"""
        self.logger.error(f"❌ ERROR in {operation}: {error_msg}")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nERROR in {operation}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Message: {error_msg}\n")
            f.write("-" * 30 + "\n")
    
    def log_session_data(self, session_id, word_count, traditional_found, simplified_found):
        """Log session creation data"""
        self.logger.info(f"💾 SESSION SAVED: {session_id}")
        self.logger.info(f"   Total words: {word_count}")
        self.logger.info(f"   Traditional chars: {traditional_found}")
        self.logger.info(f"   Simplified chars: {simplified_found}")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nSESSION SAVED: {session_id}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Words: {word_count}\n")
            f.write(f"Traditional: {traditional_found}\n")
            f.write(f"Simplified: {simplified_found}\n")
            f.write("-" * 40 + "\n")
    
    def get_summary(self):
        """Get debug session summary"""
        duration = datetime.now() - self.session_start
        
        summary = f"""
DEBUG SESSION SUMMARY
{'='*50}
Duration: {duration}
Total MFA calls: {self.mfa_call_count}
Total conversions: {self.conversion_count}
Log file: {self.log_file}
"""
        
        self.logger.info(summary)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{summary}\n")
        
        return summary

# Global debug logger instance
debug_logger = DebugLogger()

def log_mfa_call(text_length, is_chunk=False, chunk_info=None):
    """Global function to log MFA calls"""
    debug_logger.log_mfa_call(text_length, is_chunk, chunk_info)

def log_conversion(original_count, converted_count, examples=None):
    """Global function to log conversions"""
    debug_logger.log_conversion(original_count, converted_count, examples)

def log_error(operation, error_msg):
    """Global function to log errors"""
    debug_logger.log_error(operation, error_msg)

def log_session_data(session_id, word_count, traditional_found, simplified_found):
    """Global function to log session data"""
    debug_logger.log_session_data(session_id, word_count, traditional_found, simplified_found)

def get_debug_summary():
    """Global function to get debug summary"""
    return debug_logger.get_summary()