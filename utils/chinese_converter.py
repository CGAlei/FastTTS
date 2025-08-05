"""
Robust Traditional to Simplified Chinese Converter
Provides multiple fallback layers to ensure conversion never fails
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import OpenCC
try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
except ImportError:
    OpenCC = None
    OPENCC_AVAILABLE = False


class ChineseConverter:
    """
    Robust Traditional to Simplified Chinese converter with multiple fallback layers
    
    Conversion Priority:
    1. OpenCC (tw2s) - Primary conversion method
    2. UI Compatibility Mapping - Manual overrides for OpenCC gaps
    3. Comprehensive Character Mapping - Emergency fallback
    
    Never fails - always returns some form of conversion
    """
    
    def __init__(self):
        self.cc = None
        self.conversion_stats = {
            'opencc_conversions': 0,
            'ui_mapping_conversions': 0,
            'manual_mapping_conversions': 0,
            'total_processed': 0
        }
        
        # Initialize OpenCC if available
        self._init_opencc()
        
        # UI compatibility mapping for edge cases OpenCC doesn't handle well
        self.ui_compatibility_mapping = {
            '那幺': '那么', '那麽': '那么',
            '要幺': '要么', '要麽': '要么', 
            '什幺': '什么', '什麽': '什么',
            '瞭': '了', '麽': '么', '幺': '么',
            '於': '于', '爲': '为', '與': '与',
            '過': '过', '來': '来', '時': '时',
            '個': '个', '們': '们', '這': '这',
            '種': '种', '應': '应', '會': '会',
            '說': '说', '還': '还', '沒': '没',
            # Special case: OpenCC converts 顯著→显著 but standard is 显着
            '顯著': '显着', '著名': '著名'  # 著名 keeps 著 in Simplified
        }
        
        # Comprehensive Traditional→Simplified character mapping (emergency fallback)
        self.manual_char_mapping = {
            # Basic frequent characters
            '國': '国', '學': '学', '東': '东', '經': '经', '發': '发',
            '長': '长', '開': '开', '關': '关', '門': '门', '問': '问',
            '間': '间', '業': '业', '產': '产', '務': '务', '員': '员',
            '際': '际', '點': '点', '線': '线', '義': '义', '議': '议',
            '認': '认', '識': '识', '實': '实', '際': '际', '現': '现',
            '機': '机', '構': '构', '準': '准', '標': '标', '確': '确',
            '總': '总', '統': '统', '條': '条', '團': '团', '達': '达',
            '運': '运', '進': '进', '選': '选', '連': '连', '導': '导',
            '創': '创', '響': '响', '聲': '声', '題': '题', '類': '类',
            '質': '质', '級': '级', '極': '极', '決': '决', '層': '层',
            '異': '异', '護': '护', '視': '视', '覺': '觉', '觀': '观',
            '聽': '听', '讀': '读', '寫': '写', '語': '语', '話': '话',
            '詞': '词', '譯': '译', '記': '记', '錄': '录', '報': '报',
            '紙': '纸', '書': '书', '筆': '笔', '畫': '画', '圖': '图',
            '場': '场', '處': '处', '辦': '办', '務': '务', '費': '费',
            '價': '价', '買': '买', '賣': '卖', '貨': '货', '財': '财',
            '錢': '钱', '銀': '银', '鐵': '铁', '鋼': '钢', '銅': '铜',
            '車': '车', '飛': '飞', '船': '船', '電': '电', '網': '网',
            '計': '计', '設': '设', '備': '备', '器': '器', '術': '术',
            '醫': '医', '藥': '药', '療': '疗', '病': '病', '院': '院',
            '養': '养', '護': '护', '康': '康', '健': '健', '檢': '检',
            '測': '测', '試': '试', '驗': '验', '檢': '检', '查': '查',
            '調': '调', '節': '节', '制': '制', '控': '控', '管': '管',
            '理': '理', '規': '规', '範': '范', '準': '准', '則': '则',
            '律': '律', '法': '法', '權': '权', '利': '利', '義': '义',
            
            # Missing characters found in tests - CRITICAL ADDITIONS
            '濟': '济', '習': '习', '對': '对', '絡': '络', '會': '会',
            '為': '为', '這': '这', '個': '个', '們': '们', '來': '来',
            '時': '时', '種': '种', '應': '应', '說': '说', '還': '还',
            '沒': '没', '過': '过', '與': '与', '於': '于', '爲': '为',
            '儘': '尽', '盡': '尽', '從': '从', '衆': '众', '眾': '众',
            '體': '体', '態': '态', '變': '变', '遷': '迁', '轉': '转',
            '傳': '传', '統': '统', '漢': '汉', '當': '当', '黨': '党',
            
            # CRITICAL: Missing characters from real session data (20250802_234941)
            '兩': '两', '鄰': '邻', '傢': '家', '雖': '虽', '然': '然',
            '後': '后', '卻': '却', '結': '结', '构': '构', '著': '着',
            '顯': '显', '麼': '么', '麽': '么', '後': '后', '來': '来', 
            '大': '大', '傢': '家', '體': '体', '製': '制', '內': '内',
            '在': '在', '性': '性', '分': '分', '水': '水', '嶺': '岭',
            '嗎': '吗', '閤': '合', '法': '法', '喪': '丧', '失': '失',
            '頻': '频', '繁': '繁', '湯': '汤', '武': '武', '幾': '几',
            '乎': '乎', '終': '终', '生': '生', '象': '象', '徵': '征',
            '輕': '轻', '易': '易', '永': '永', '遠': '远', '讓': '让',
            '那': '那', '樣': '样', '這': '这', '樣': '样', '難': '难',
            '道': '道', '分': '分', '道': '道', '揚': '扬', '鑣': '镳',
            # Additional critical mappings from session
            '近': '近', '雖': '虽', '然': '然', '構': '构', '顯': '显',
            '著': '着', '結': '结', '構': '构', '頻': '频', '繁': '繁',
            
            # Political and geographical
            '臺': '台', '灣': '湾', '島': '岛', '省': '省', '縣': '县',
            '區': '区', '鎮': '镇', '鄉': '乡', '村': '村', '街': '街',
            '號': '号', '樓': '楼', '層': '层', '室': '室', '戶': '户',
            # Time and numbers
            '時': '时', '間': '间', '鐘': '钟', '分': '分', '秒': '秒',
            '週': '周', '歲': '岁', '齡': '龄', '歷': '历', '曆': '历',
            '億': '亿', '萬': '万', '千': '千', '百': '百', '拾': '十',
            # Body and nature  
            '頭': '头', '臉': '脸', '眼': '眼', '鼻': '鼻', '嘴': '嘴',
            '耳': '耳', '手': '手', '腳': '脚', '腿': '腿', '身': '身',
            '體': '体', '心': '心', '腦': '脑', '血': '血', '骨': '骨',
            '樹': '树', '花': '花', '草': '草', '葉': '叶', '果': '果',
            '鳥': '鸟', '魚': '鱼', '蟲': '虫', '獸': '兽', '龍': '龙',
        }
    
    def _init_opencc(self):
        """Initialize OpenCC converter with error handling"""
        if not OPENCC_AVAILABLE:
            logger.warning("🚫 OpenCC not available - using fallback conversion only")
            return
            
        try:
            self.cc = OpenCC('tw2s')
            logger.info("✅ OpenCC converter initialized (tw2s)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenCC converter: {e}")
            self.cc = None
    
    def convert_word(self, word: str) -> str:
        """
        Convert a single word from Traditional to Simplified Chinese
        Uses multiple fallback methods to ensure conversion never fails
        """
        if not word:
            return word
            
        original_word = word
        self.conversion_stats['total_processed'] += 1
        
        # Method 1: UI compatibility mapping (highest priority for known edge cases)
        if word in self.ui_compatibility_mapping:
            converted = self.ui_compatibility_mapping[word]
            self.conversion_stats['ui_mapping_conversions'] += 1
            logger.debug(f"✅ UI mapping: '{original_word}' → '{converted}'")
            return converted
        
        # Method 2: OpenCC conversion (if available)
        if self.cc:
            try:
                converted = self.cc.convert(word)
                if converted != original_word:
                    self.conversion_stats['opencc_conversions'] += 1
                    logger.debug(f"✅ OpenCC: '{original_word}' → '{converted}'")
                    return converted
            except Exception as e:
                logger.warning(f"❌ OpenCC conversion failed for '{word}': {e}")
        
        # Method 3: Character-by-character manual mapping (emergency fallback)
        converted_chars = []
        conversion_made = False
        unconverted_traditional = []
        
        for char in word:
            if char in self.manual_char_mapping:
                converted_chars.append(self.manual_char_mapping[char])
                conversion_made = True
                logger.debug(f"✅ Manual char: '{char}' → '{self.manual_char_mapping[char]}'")
            else:
                converted_chars.append(char)
                # Check if this is a Traditional character we're missing
                if '\u4e00' <= char <= '\u9fff':  # Chinese character range
                    # Common Traditional characters we should catch
                    known_traditional = set(self.manual_char_mapping.keys()) | set(self.ui_compatibility_mapping.keys())
                    if char not in known_traditional:
                        # Check if it looks Traditional by testing some patterns
                        traditional_indicators = ['龍', '國', '學', '過', '來', '時', '個', '們', '這', '對', '會', '說', '還', '沒', '後', '長', '開', '關', '門', '問', '間', '業', '產', '務', '員', '際', '點', '線', '義', '議', '認', '識', '實', '現', '機', '構', '準', '標', '確', '總', '統', '條', '團', '達', '運', '進', '選', '連', '導', '創', '響', '聲', '題', '類', '質', '級', '極', '決', '層', '異', '護', '視', '覺', '觀', '聽', '讀', '寫', '語', '話', '詞', '譯', '記', '錄', '報', '紙', '書', '筆', '畫', '圖', '場', '處', '辦', '費', '價', '買', '賣', '貨', '財', '錢', '銀', '鐵', '鋼', '銅', '車', '飛', '電', '網', '計', '設', '備', '術', '醫', '藥', '療', '檢', '測', '試', '驗', '查', '調', '節', '控', '管', '規', '範', '則', '權', '濟', '習', '絡', '為', '種', '應', '與', '於', '儘', '盡', '從', '衆', '眾', '體', '態', '變', '遷', '轉', '傳', '漢', '當', '黨', '臺', '灣', '島', '縣', '區', '鎮', '鄉', '號', '樓', '戶', '鐘', '週', '歲', '齡', '歷', '曆', '億', '萬', '拾', '頭', '臉', '腳', '腦', '樹', '葉', '鳥', '魚', '蟲', '獸', '兩', '鄰', '傢', '雖', '然', '卻', '結', '著', '顯', '麼', '麽', '內', '嶺', '嗎', '閤', '喪', '頻', '繁', '湯', '幾', '終', '象', '徵', '輕', '永', '遠', '讓', '樣', '難', '揚', '鑣', '構', '近']
                        # This is a very rough heuristic but helps identify missed Traditional chars
                        unconverted_traditional.append(char)
        
        if conversion_made:
            converted = ''.join(converted_chars)
            self.conversion_stats['manual_mapping_conversions'] += 1
            logger.debug(f"✅ Manual mapping: '{original_word}' → '{converted}'")
            
            # Log any unconverted Traditional characters for future mapping
            if unconverted_traditional:
                logger.warning(f"⚠️ POTENTIAL TRADITIONAL CHARS NOT CONVERTED in '{original_word}': {unconverted_traditional}")
            
            return converted
        
        # Check if entire word contains potential Traditional characters
        potential_traditional = []
        for char in word:
            if '\u4e00' <= char <= '\u9fff':  # Chinese character
                known_chars = set(self.manual_char_mapping.values()) | {'的', '了', '在', '是', '我', '有', '和', '人', '这', '中', '大', '为', '上', '个', '国', '我', '以', '要', '他', '时', '来', '用', '们', '生', '到', '作', '地', '于', '出', '就', '分', '对', '成', '会', '可', '主', '发', '年', '动', '同', '工', '也', '能', '下', '过', '子', '说', '产', '种', '面', '而', '方', '后', '多', '定', '行', '学', '法', '所', '民', '得', '经', '十', '三', '之', '进', '着', '等', '部', '度', '家', '电', '力', '里', '如', '水', '化', '高', '自', '二', '理', '起', '小', '物', '现', '实', '加', '量', '都', '两', '体', '制', '机', '当', '使', '点', '从', '业', '本', '去', '把', '性', '好', '应', '开', '它', '合', '还', '因', '由', '其', '些', '然', '前', '外', '天', '政', '四', '日', '那', '社', '义', '事', '平', '形', '相', '全', '表', '间', '样', '与', '关', '各', '重', '新', '线', '内', '数', '正', '心', '反', '你', '明', '看', '原', '又', '么', '利', '比', '或', '但', '质', '气', '第', '向', '道', '命', '此', '变', '条', '只', '没', '结', '解', '问', '意', '建', '月', '公', '无', '系', '军', '很', '情', '者', '最', '立', '代', '想', '已', '通', '并', '提', '直', '题', '党', '程', '展', '五', '果', '料', '象', '员', '革', '位', '入', 
                                '继', '总', '即', '车', '重', '便', '斗', '白', '调', '满', '县', '局', '照', '参', '红', '细', '引', '听', '该', '铁', '价', '严', '龙', '土', '快', '过', '非', '转', '今', '识', '干', '办', '标', '据', '求', '统', '次', '处', '团', '决', '品', '声', '争', '思', '八', '完', '般', '受', '计', '除', '却', '组', '号', '列', '温', '什', '必', '院', '易', '早', '论', '吃', '再', '任', '掌', '精', '九', '你', '做', '每', '集', '半', '确', '候', '际', '千', '指', '深', '李', '整', '走', '究', '观', '取', '节', '历', '称', '单', '马', '难', '价', '奋', '许', '快', '城', '回', '选', '包', '围', '专', '更', '击', '复', '六', '少', '华', '阶', '清', '风', '拉', '住', '写', '农', '八', '型', '石', '接', '近', '备', '费', '世', '门', '特', '则', '常', '领', '五', '备', '装', '报', '毛', '究', '算', '周', '维', '断', '极', '管', '运', '件', '率', '保', '先', '息', '希', '态', '步', '离', '测', '试', '段', '按', '语', '快', '除', '周', '容', '共', '兵', '位', '别', '够', '商', '似', '阳', '区', '七', '食', '连', '请', '海', '强', '给', '何', '色', '长', '路', '即', '织', '拿', '交', '消', '克', '且', '住', '科', '训', '火', '边', '光', '验', '收', '记', '住', '书', '房', '任', '王', '存', '太', '文', '友', '若', '种', '存', '花', '谈', '万', '制', '确', '传', '加', '安', '配', '空', '级', '布', '终', '走', '随', '呢', '习', '夜', '具', '按', '增', '基', '流', '消', '况', '答', '治', '男', '担', '千', '术', '纸', '余', '群', '往', '顺', '首', '故', '古', '门', '图', '喜', '女', '材', '视', '志', '坚', '供', '范', '苦', '伍', '杀', '止', '练', '敌', '靠', '算', '盾', '响', '云', '差', '百', '木', '众', '板', '右', '妇', '左', '头', '尔', '创', '牛', '述', '若', '谁', '春', '养', '息', '乡', '希', '影', '岁', '房', '造', '达', '案', '录', '派', '病', '装', '限', '南', '热', '江', '切', '投', '格', '失', '京', '片', '角', '缺', '钱', '技', '越', '远', '洋', '波', '黄', '典', '欢', '师', '底', '纪', '注', '课', '镇', '防', '土', '富', '厂', '支', '妈', '负', '田', '独', '序', '亚', '录', '买', '告', '细', '六', '血', '西', '守', '推', '职', '亲', '永', '剩', '初', '校', '树', '简', '千', '校', '资', '倒', '验', '服', '推', '活', '夏', '护', '牙', '买', '项', '待', '客', '户', '福', '岛', '木', '预', '降', '板', '七', '斯', '房', '港', '良', '落', '例', '停', '春', '阶', '油', '准', '留', '讲', '死', '费', '临', '弟', '示', '层', '执', '李', '养', '乔', '编', '卫', '败', '助', '约', '担', '坐', '草', '聚', '罗', '亿', '午', '拿', '判', '伤', '尾', '较', '网', '低', '愈', '愿', '宝', '层', '弱', '洲', '赶', '居', '船', '双', '飞', '积', '呀', '块', '顾', '早', '班', '暖', '景', '虽', '皮', '季', '阿', '谷', '纷', '默', '钢', '移', '篇', '画', '诉', '雨', '仍', '米', '夫', '板', '杀', '败', '乱', '扫', '挥', '免', '紧', '留', '建', '毁', '盖', '岸', '黑', '犯', '微', '鲜', '采', '亮', '嗯', '凡', '范', '宁', '仁', '卡', '获', '版', '抗', '硬', '仍', '承', '另', '呢', '硬', '罪', '曹', '苏', '村', '贵', '操', '监', '洋', '胜', '固', '父', '句', '透'}
                
                # If it's not in common simplified characters, it might be traditional
                if char not in known_chars and char not in self.manual_char_mapping and char not in self.ui_compatibility_mapping:
                    potential_traditional.append(char)
        
        if potential_traditional:
            logger.warning(f"🚨 UNCONVERTED POTENTIAL TRADITIONAL CHARACTERS in '{original_word}': {potential_traditional}")
            logger.warning(f"   Add these to manual_char_mapping: {dict(zip(potential_traditional, ['?' for _ in potential_traditional]))}")
        
        # No conversion needed or possible - return original
        return original_word
    
    def convert_word_timings(self, word_timings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert word timings from Traditional to Simplified Chinese
        NEVER fails - always returns converted or original data
        """
        if not word_timings:
            return word_timings
        
        converted_timings = []
        conversions_made = 0
        
        for timing in word_timings:
            original_word = timing.get("word", "")
            if not original_word:
                converted_timings.append(timing)
                continue
            
            converted_word = self.convert_word(original_word)
            
            # Create new timing object with converted word
            new_timing = timing.copy()
            new_timing["word"] = converted_word
            converted_timings.append(new_timing)
            
            if converted_word != original_word:
                conversions_made += 1
        
        # Log conversion summary
        if conversions_made > 0:
            logger.info(f"🔄 Traditional→Simplified conversion: {conversions_made}/{len(word_timings)} words converted")
            self._log_conversion_stats()
        else:
            logger.debug(f"✅ No Traditional characters detected in {len(word_timings)} words")
        
        return converted_timings
    
    def convert_text(self, text: str) -> str:
        """
        Convert entire text from Traditional to Simplified Chinese
        """
        if not text:
            return text
            
        # Use OpenCC for full text conversion if available
        if self.cc:
            try:
                converted = self.cc.convert(text)
                if converted != text:
                    logger.info(f"📝 Text converted: {len(text)} chars → {len(converted)} chars")
                return converted
            except Exception as e:
                logger.warning(f"OpenCC text conversion failed: {e}")
        
        # Fallback: character-by-character conversion
        converted_chars = []
        for char in text:
            if char in self.manual_char_mapping:
                converted_chars.append(self.manual_char_mapping[char])
            elif char in self.ui_compatibility_mapping:
                converted_chars.append(self.ui_compatibility_mapping[char])
            else:
                converted_chars.append(char)
        
        return ''.join(converted_chars)
    
    def _log_conversion_stats(self):
        """Log detailed conversion statistics"""
        stats = self.conversion_stats
        total_conversions = (stats['opencc_conversions'] + 
                           stats['ui_mapping_conversions'] + 
                           stats['manual_mapping_conversions'])
        
        if total_conversions > 0:
            details = []
            if stats['opencc_conversions'] > 0:
                details.append(f"{stats['opencc_conversions']} OpenCC")
            if stats['ui_mapping_conversions'] > 0:
                details.append(f"{stats['ui_mapping_conversions']} UI-mapping")
            if stats['manual_mapping_conversions'] > 0:
                details.append(f"{stats['manual_mapping_conversions']} manual")
            
            logger.info(f"📊 Conversion breakdown: {', '.join(details)}")
    
    def is_opencc_available(self) -> bool:
        """Check if OpenCC is available and working"""
        return self.cc is not None
    
    def get_conversion_stats(self) -> Dict[str, int]:
        """Get conversion statistics"""
        return self.conversion_stats.copy()
    
    def reset_stats(self):
        """Reset conversion statistics"""
        self.conversion_stats = {
            'opencc_conversions': 0,
            'ui_mapping_conversions': 0,
            'manual_mapping_conversions': 0,
            'total_processed': 0
        }
    
    def validate_simplified_chinese(self, word_timings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that all words in word_timings are in Simplified Chinese
        
        Returns:
            Dict with validation results and any Traditional characters found
        """
        traditional_chars_found = set()
        traditional_words = []
        
        # Only flag characters that are EXCLUSIVELY Traditional (not used in Simplified)
        # These are characters that should NEVER appear in Simplified Chinese text
        exclusively_traditional_chars = {
            '國', '學', '東', '經', '發', '長', '開', '關', '門', '問', '間', '業', '產', '務', '員',
            '際', '點', '線', '義', '議', '認', '識', '實', '現', '機', '構', '準', '標', '確',
            '總', '統', '條', '團', '達', '運', '進', '選', '連', '導', '創', '響', '聲', '題',
            '類', '質', '級', '極', '決', '層', '異', '護', '視', '覺', '觀', '聽', '讀', '寫',
            '語', '話', '詞', '譯', '記', '錄', '報', '紙', '書', '筆', '畫', '圖', '場', '處',
            '辦', '費', '價', '買', '賣', '貨', '財', '錢', '銀', '鐵', '鋼', '銅', '車', '飛',
            '電', '網', '計', '設', '備', '術', '醫', '藥', '療', '檢', '測', '試', '驗', '查',
            '調', '節', '控', '管', '規', '範', '則', '權', '濟', '習', '絡', '為', '種', '應',
            '與', '於', '儘', '盡', '從', '衆', '眾', '體', '態', '變', '遷', '轉', '傳', '漢',
            '當', '黨', '臺', '灣', '島', '縣', '區', '鎮', '鄉', '號', '樓', '戶', '鐘', '週',
            '歲', '齡', '歷', '曆', '億', '萬', '拾', '頭', '臉', '腳', '腦', '樹', '葉', '鳥',
            '魚', '蟲', '獸', '兩', '鄰', '傢', '雖', '後', '卻', '結', '顯', '麼', '麽',
            '內', '嶺', '嗎', '閤', '喪', '頻', '繁', '湯', '幾', '終', '象', '徵', '輕', '永',
            '遠', '讓', '樣', '難', '揚', '鑣', '製', '齣'
            # Note: Removed '著' as it has valid uses in Simplified Chinese (著名, 著作, etc.)
        }
        
        for timing in word_timings:
            word = timing.get("word", "")
            word_has_traditional = False
            traditional_chars_in_word = []
            
            for char in word:
                if char in exclusively_traditional_chars:
                    traditional_chars_found.add(char)
                    traditional_chars_in_word.append(char)
                    word_has_traditional = True
            
            if word_has_traditional:
                traditional_words.append({
                    'word': word,
                    'traditional_chars': traditional_chars_in_word,
                    'timestamp': timing.get('timestamp', 0)
                })
        
        validation_result = {
            'is_valid': len(traditional_chars_found) == 0,
            'traditional_chars_found': list(traditional_chars_found),
            'traditional_words': traditional_words,
            'total_words_checked': len(word_timings)
        }
        
        if not validation_result['is_valid']:
            logger.warning(f"🚨 TRUE Traditional characters detected in final output: {traditional_chars_found}")
            logger.warning(f"🔍 Affected words: {[w['word'] for w in traditional_words]}")
        else:
            logger.info(f"✅ Validation passed: All {len(word_timings)} words are properly Simplified Chinese")
        
        return validation_result


# Global instance
_chinese_converter = None

def get_chinese_converter() -> ChineseConverter:
    """Get the global Chinese converter instance"""
    global _chinese_converter
    if _chinese_converter is None:
        _chinese_converter = ChineseConverter()
    return _chinese_converter