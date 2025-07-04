#!/usr/bin/env python3
"""
Text Processing Module for FastTTS
Handles text sanitization and number conversion for optimal TTS experience
"""

import re
import logging

logger = logging.getLogger(__name__)

def convert_numbers_to_chinese(text):
    """
    Convert Arabic numerals to Chinese numbers for proper TTS pronunciation
    
    Examples:
    - 180 → 一百八十
    - 2024 → 二千零二十四
    - 18世纪 → 一十八世纪
    - 360度 → 三百六十度
    """
    if not text:
        return ""
    
    # Chinese number mappings
    digit_map = {
        '0': '零', '1': '一', '2': '二', '3': '三', '4': '四',
        '5': '五', '6': '六', '7': '七', '8': '八', '9': '九'
    }
    
    def number_to_chinese(num_str):
        """Convert a number string to Chinese representation"""
        num = int(num_str)
        
        if num == 0:
            return '零'
        
        # Handle numbers up to 9999 (most common in Chinese text)
        if num < 10:
            return digit_map[str(num)]
        elif num < 100:
            tens = num // 10
            ones = num % 10
            if tens == 1:
                if ones == 0:
                    return '十'
                else:
                    return '十' + digit_map[str(ones)]
            else:
                if ones == 0:
                    return digit_map[str(tens)] + '十'
                else:
                    return digit_map[str(tens)] + '十' + digit_map[str(ones)]
        elif num < 1000:
            hundreds = num // 100
            remainder = num % 100
            result = digit_map[str(hundreds)] + '百'
            if remainder == 0:
                return result
            elif remainder < 10:
                return result + '零' + digit_map[str(remainder)]
            else:
                return result + number_to_chinese(str(remainder))
        elif num < 10000:
            thousands = num // 1000
            remainder = num % 1000
            result = digit_map[str(thousands)] + '千'
            if remainder == 0:
                return result
            elif remainder < 100:
                return result + '零' + number_to_chinese(str(remainder))
            else:
                return result + number_to_chinese(str(remainder))
        else:
            # For numbers >= 10000, use simplified conversion
            # This handles edge cases but most Chinese text uses smaller numbers
            return ''.join(digit_map.get(d, d) for d in str(num))
    
    # Find all standalone numbers (not part of other text)
    # Pattern: numbers surrounded by non-digits or string boundaries
    def replace_number(match):
        number_str = match.group(0)
        try:
            chinese_number = number_to_chinese(number_str)
            logger.debug(f"Converting number: {number_str} → {chinese_number}")
            return chinese_number
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to convert number {number_str}: {e}")
            return number_str
    
    # Replace standalone numbers (1-4 digits)
    # Pattern: (start/non-digit) + digits + (end/non-digit)
    # Use positive lookbehind and lookahead to not include the surrounding characters
    result = re.sub(r'(?<!\d)\d{1,4}(?!\d)', replace_number, text)
    
    return result

def sanitize_text_for_karaoke(text):
    """
    Master text sanitization function for smooth karaoke experience
    Removes ALL symbols that create individual containers or disrupt TTS
    Used consistently across all TTS engines and processing stages
    """
    if not text:
        return ""
    
    # Remove ALL bracket types that create empty containers
    text = re.sub(r'[【】\[\]{}「」『』〈〉《》（）()〔〕［］｛｝＜＞]', '', text)
    
    # Remove ALL quote types including the specific Unicode quotes found in logs (U+201C, U+201D)
    text = re.sub(r'[\'\"''""‛‟„‚‹›«»""\u201C\u201D]', '', text)
    
    # Remove dashes and hyphens that create individual containers
    text = re.sub(r'[—–―\-]', '', text)
    
    # Remove other symbols that create containers
    text = re.sub(r'[～@#$%^&*_+=|\\<>/]', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_text_for_tts(text):
    """
    Master text preprocessing function for TTS generation
    Combines number conversion and sanitization for optimal TTS experience
    
    Args:
        text (str): Raw input text
        
    Returns:
        str: Processed text ready for TTS generation
    """
    if not text:
        return ""
    
    logger.info(f"Preprocessing text for TTS: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    # Step 1: Convert numbers to Chinese for proper pronunciation
    text_with_chinese_numbers = convert_numbers_to_chinese(text)
    logger.debug(f"After number conversion: '{text_with_chinese_numbers}'")
    
    # Step 2: Sanitize text to remove problematic symbols
    final_text = sanitize_text_for_karaoke(text_with_chinese_numbers)
    logger.debug(f"After sanitization: '{final_text}'")
    
    logger.info(f"Text preprocessing complete: '{text}' → '{final_text}'")
    
    return final_text

# Legacy function names for backward compatibility
def clean_chinese_text(text):
    """Legacy function - use preprocess_text_for_tts instead"""
    logger.warning("clean_chinese_text() is deprecated, use preprocess_text_for_tts() instead")
    return preprocess_text_for_tts(text)

# Test function for development and debugging
def test_number_conversion():
    """Test number conversion with common examples"""
    test_cases = [
        "绕180度",
        "18世纪的时候",
        "2024年1月1日", 
        "他转了360度",
        "在第5章节",
        "总共有1500个",
        "距离2公里",
        "等待10分钟",
        "一共50个人",
        "价格是99元"
    ]
    
    print("=== Number Conversion Test ===")
    for text in test_cases:
        converted = convert_numbers_to_chinese(text)
        print(f"'{text}' → '{converted}'")

if __name__ == "__main__":
    # Run tests when module is executed directly
    test_number_conversion()