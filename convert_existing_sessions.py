#!/usr/bin/env python3
"""
Convert Traditional Chinese to Simplified Chinese in all existing session JSON files
One-time conversion script to fix existing timestamps.json files
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def get_traditional_to_simplified_mapping():
    """Get comprehensive Traditional to Simplified Chinese character mapping"""
    return {
        # Core conversions from actual session data
        '劇本': '剧本',  # The specific issue mentioned
        '並': '并',
        '預設': '预设',
        '先驗': '先验',
        '意義': '意义',
        '則': '则',
        '構築': '构筑',
        '瞭': '了',
        '舞颱': '舞台',
        '循軌': '循轨',
        '運轉': '运转',
        '對': '对',
        '發生': '发生',
        '悲歡離閤': '悲欢离合',
        '無動於衷': '无动于衷',
        '導嚮': '导向',
        '虛無': '虚无',
        '經過': '经过',
        '長期': '长期',
        '與': '与',
        '認為': '认为',
        '賦予': '赋予',
        '獨特': '独特',
        '價值': '价值',
        '纔': '才',
        '獲得': '获得',
        '創造': '创造',
        '終極': '终极',
        '將': '将',
        '為': '为',
        '個': '个',
        '講述者': '讲述者',
        '聆聽者': '聆听者',
        '類': '类',
        '敘事': '叙事',
        '數據': '数据',
        '無論是': '无论是',
        '還是': '还是',
        '個人': '个人',
        '愛恨情仇': '爱恨情仇',
        '糾葛': '纠葛',
        '個個': '个个',
        '們': '们',
        '訓練': '训练',
        '豐富': '丰富',
        '情感': '情感',
        '驅動力': '驱动力',
        '審視': '审视',
        '結構': '结构',
        '潛在': '潜在',
        '實踐': '实践',
        '練': '练',
        '課': '课',
        '區分': '区分',
        '現實': '现实',
        '靜觀': '静观',
        '內心': '内心',
        '念頭': '念头',
        '著': '着',
        '覺知': '觉知',
        '蘊含': '蕴含',
        '奇跡': '奇迹',
        '遙遠': '遥远',
        '並非': '并非',
        '摒棄': '摒弃',
        '自覺': '自觉',
        '玩傢': '玩家',
        '幫助': '帮助',
        '參與': '参与',
        '遊戲': '游戏',
        '規則': '规则',
        '做齣': '做出',
        '選擇': '选择',
        '麵紗': '面纱',
        '輕輕': '轻轻',
        '揭開': '揭开',
        '齣來': '出来',
        '叩擊': '叩击',
        '密鑰': '密钥',
        '解脫': '解脱',
        '苦難': '苦难',
        '這種': '这种',
        '無論': '无论',
        '領域': '领域',
        '持久': '持久',
        
        # Additional common Traditional characters
        '學': '学',
        '會': '会',
        '來': '来',
        '時': '时',
        '間': '间',
        '動': '动',
        '國': '国',
        '開': '开',
        '關': '关',
        '門': '门',
        '問': '问',
        '題': '题',
        '應': '应',
        '該': '该',
        '說': '说',
        '話': '话',
        '語': '语',
        '種': '种',
        '樣': '样',
        '點': '点',
        '線': '线',
        '錢': '钱',
        '買': '买',
        '賣': '卖',
        '見': '见',
        '聽': '听',
        '說': '说',
        '讀': '读',
        '寫': '写',
        '頭': '头',
        '身': '身',
        '體': '体',
        '風': '风',
        '雨': '雨',
        '雪': '雪',
        '雲': '云',
        '電': '电',
        '視': '视',
        '網': '网',
        '際': '际',
        '務': '务',
        '業': '业',
        '場': '场',
        '處': '处',
        '備': '备',
        '記': '记',
        '錄': '录',
        '單': '单',
        '雙': '双',
        '復': '复',
        '雜': '杂',
        '簡': '简',
        '傳': '传',
        '統': '统',
        '繼': '继',
        '續': '续',
        '變': '变',
        '換': '换',
        '遷': '迁',
        '達': '达',
        '過': '过',
        '進': '进',
        '退': '退',
        '轉': '转',
        '彎': '弯',
        '圓': '圆',
        '園': '园',
        '團': '团',
        '員': '员',
        '專': '专',
        '業': '业',
        '職': '职',
        '務': '务',
        '責': '责',
        '任': '任',
        '權': '权',
        '利': '利',
        '義': '义',
        '務': '务',
        '學': '学',
        '習': '习',
        '練': '练',
        '習': '习',
    }

def convert_word(word, mapping):
    """Convert a word from Traditional to Simplified Chinese"""
    # First try exact match
    if word in mapping:
        return mapping[word], True
    
    # Then try character-by-character conversion
    converted = ""
    has_conversion = False
    
    for char in word:
        if char in mapping:
            converted += mapping[char]
            has_conversion = True
        else:
            converted += char
    
    return converted, has_conversion

def convert_timestamps_file(file_path, mapping, backup=True):
    """Convert Traditional Chinese to Simplified in a timestamps.json file"""
    try:
        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix('.json.backup')
            shutil.copy2(file_path, backup_path)
            print(f"  📋 Backup created: {backup_path.name}")
        
        # Load JSON data
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"  ❌ Invalid JSON format (not a list)")
            return False, 0
        
        # Convert Traditional characters in word fields
        conversion_count = 0
        converted_words = []
        
        for entry in data:
            if isinstance(entry, dict) and 'word' in entry:
                original_word = entry['word']
                converted_word, had_conversion = convert_word(original_word, mapping)
                
                if had_conversion:
                    entry['word'] = converted_word
                    conversion_count += 1
                    converted_words.append(f"'{original_word}' → '{converted_word}'")
        
        # Save converted data back to file
        if conversion_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ Converted {conversion_count} words:")
            for conversion in converted_words[:10]:  # Show first 10
                print(f"     {conversion}")
            if len(converted_words) > 10:
                print(f"     ... and {len(converted_words) - 10} more")
        else:
            print(f"  ➡️  No Traditional characters found")
        
        return True, conversion_count
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parsing error: {e}")
        return False, 0
    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
        return False, 0

def find_session_files(sessions_dir):
    """Find all timestamps.json files in session directories"""
    sessions_path = Path(sessions_dir)
    
    if not sessions_path.exists():
        print(f"❌ Sessions directory not found: {sessions_dir}")
        return []
    
    timestamp_files = []
    
    # Look for session directories (format: YYYYMMDD_HHMMSS)
    for item in sessions_path.iterdir():
        if item.is_dir():
            timestamp_file = item / "timestamps.json"
            if timestamp_file.exists():
                timestamp_files.append(timestamp_file)
    
    return timestamp_files

def main():
    """Main conversion process"""
    print("🔄 Converting Traditional Chinese to Simplified in Session Files")
    print("=" * 70)
    
    # Configuration
    from config.paths import get_path_manager
    sessions_dir = str(get_path_manager().sessions_dir)
    mapping = get_traditional_to_simplified_mapping()
    
    print(f"Sessions directory: {sessions_dir}")
    print(f"Character mappings loaded: {len(mapping)}")
    
    # Find all timestamp files
    print(f"\n🔍 Finding session files...")
    timestamp_files = find_session_files(sessions_dir)
    
    if not timestamp_files:
        print(f"❌ No session files found in {sessions_dir}")
        return
    
    print(f"Found {len(timestamp_files)} session files:")
    for file_path in timestamp_files:
        print(f"  📁 {file_path.parent.name}/timestamps.json")
    
    # Auto-proceed with conversion (non-interactive mode)
    print(f"\n⚠️  Modifying {len(timestamp_files)} JSON files in place.")
    print(f"⚠️  Backups will be created with .backup extension.")
    print(f"🔄 Proceeding with automatic conversion...")
    
    # Process each file
    print(f"\n🔄 Processing session files...")
    total_files = len(timestamp_files)
    successful_files = 0
    total_conversions = 0
    
    for i, file_path in enumerate(timestamp_files, 1):
        print(f"\n📝 Processing {i}/{total_files}: {file_path.parent.name}")
        
        success, conversion_count = convert_timestamps_file(file_path, mapping, backup=True)
        
        if success:
            successful_files += 1
            total_conversions += conversion_count
        
    # Summary
    print(f"\n📊 Conversion Summary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Successfully converted: {successful_files}")
    print(f"  Total word conversions: {total_conversions}")
    print(f"  Failed conversions: {total_files - successful_files}")
    
    if total_conversions > 0:
        print(f"\n🎉 SUCCESS: {total_conversions} Traditional Chinese words converted to Simplified!")
        print(f"✅ Word containers should now display correctly")
        print(f"✅ Backup files created with .backup extension")
    else:
        print(f"\n📝 No Traditional Chinese characters found in session files")
    
    print(f"\n💡 Note: New sessions will automatically use Simplified Chinese")

if __name__ == "__main__":
    main()