# FastTTS Database Schema & Operations Guide

## 📋 Database Overview

FastTTS uses SQLite as its primary database for vocabulary storage and session metadata management. The system is designed for efficient lookups, vocabulary expansion, and cross-session synchronization.

**Database Location**: `/db/vocab.db`  
**Current Size**: ~585KB  
**Vocabulary Count**: 1,573+ entries  
**Encoding**: UTF-8 with Chinese character support

---

## 🗄️ Vocabulary Table Schema

### **Primary Table: `vocabulary`**

```sql
CREATE TABLE vocabulary (
    ChineseWord TEXT PRIMARY KEY,           -- Chinese word (unique identifier)
    filename TEXT NOT NULL,                 -- Source filename
    length INTEGER NOT NULL,                -- Character count
    PinyinPronunciation TEXT,               -- Romanized pronunciation
    SpanishMeaning TEXT,                    -- Primary Spanish translation
    ChineseMeaning TEXT,                    -- Chinese definition/explanation
    Sinonims TEXT,                          -- Synonyms (comma-separated)
    Antonims TEXT,                          -- Antonyms (comma-separated)
    UsageExample TEXT,                      -- Example sentence in context
    AudioTTSPath TEXT,                      -- Path to audio file (optional)
    UpdatedAt TEXT,                         -- Last modification timestamp
    WordType TEXT                           -- Grammar type (名词, 动词, 形容词, etc.)
);
```

### **Field Specifications**

| Field | Type | Constraints | Purpose | Example |
|-------|------|-------------|---------|---------|
| `ChineseWord` | TEXT | PRIMARY KEY, NOT NULL | Unique Chinese word identifier | "世界" |
| `filename` | TEXT | NOT NULL | Source data file reference | "vocab.db" |
| `length` | INTEGER | NOT NULL | Character count for sorting/filtering | 2 |
| `PinyinPronunciation` | TEXT | NULL allowed | Romanized pronunciation guide | "shìjiè" |
| `SpanishMeaning` | TEXT | NULL allowed | Primary Spanish translation | "mundo" |
| `ChineseMeaning` | TEXT | NULL allowed | Chinese definition/explanation | "整个地球；全球" |
| `Sinonims` | TEXT | NULL allowed | Comma-separated synonyms | "地球, 全球" |
| `Antonims` | TEXT | NULL allowed | Comma-separated antonyms | "无" |
| `UsageExample` | TEXT | NULL allowed | Contextual usage example | "世界很大，我想去看看。" |
| `AudioTTSPath` | TEXT | NULL allowed | Audio file path (future use) | "/audio/世界.mp3" |
| `UpdatedAt` | TEXT | NULL allowed | ISO8601 timestamp | "2025-06-25T14:30:22Z" |
| `WordType` | TEXT | NULL allowed | Grammar classification | "名词" |

### **Sample Data Structure**
```sql
INSERT INTO vocabulary VALUES (
    '世界',                                  -- ChineseWord
    'vocab.db',                              -- filename
    2,                                       -- length
    'shìjiè',                               -- PinyinPronunciation
    'mundo',                                -- SpanishMeaning
    '整个地球；全球',                        -- ChineseMeaning
    '地球, 全球',                           -- Sinonims
    '无',                                   -- Antonims
    '世界很大，我想去看看。',                -- UsageExample
    NULL,                                   -- AudioTTSPath
    '2025-06-25T14:30:22Z',                -- UpdatedAt
    '名词'                                  -- WordType
);
```

---

## 🔍 Core Database Operations

### **Connection Management** (`utils/db_helpers.py`)

#### **Get Database Connection**
```python
def get_database_connection():
    """Establish SQLite connection with optimized settings"""
    db_path = get_path_manager().vocab_db_path
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Performance optimization
        conn.execute("PRAGMA cache_size=10000")  # Memory cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Temp tables in memory
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise
```

#### **Connection Cleanup**
```python
def close_database_connection(conn):
    """Safely close database connection with commit"""
    if conn:
        try:
            conn.commit()  # Ensure all changes are saved
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Error closing database: {e}")
```

### **Performance Optimizations**

#### **Database PRAGMA Settings**
```sql
-- Write-Ahead Logging for better concurrency
PRAGMA journal_mode=WAL;

-- Balanced synchronization for performance
PRAGMA synchronous=NORMAL;

-- Large cache for frequent lookups (10MB)
PRAGMA cache_size=10000;

-- Memory-based temporary storage
PRAGMA temp_store=MEMORY;

-- Foreign key enforcement
PRAGMA foreign_keys=ON;
```

#### **Indexing Strategy**
```sql
-- Primary index (automatic on PRIMARY KEY)
-- Additional indexes for common queries

-- Index for length-based filtering
CREATE INDEX IF NOT EXISTS idx_vocabulary_length 
ON vocabulary(length);

-- Index for word type filtering
CREATE INDEX IF NOT EXISTS idx_vocabulary_type 
ON vocabulary(WordType);

-- Index for pronunciation lookups
CREATE INDEX IF NOT EXISTS idx_vocabulary_pinyin 
ON vocabulary(PinyinPronunciation);

-- Composite index for complex queries
CREATE INDEX IF NOT EXISTS idx_vocabulary_compound 
ON vocabulary(WordType, length, UpdatedAt);
```

---

## 📚 Vocabulary Operations (`utils/text_helpers.py`)

### **Word Existence Check**
```python
def check_word_in_vocabulary(word: str) -> bool:
    """Fast vocabulary lookup for existence checking"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM vocabulary WHERE ChineseWord = ? LIMIT 1",
            (word,)
        )
        return cursor.fetchone() is not None
    finally:
        close_database_connection(conn)
```

**Performance**: Optimized for karaoke highlighting checks  
**Usage**: Called frequently during TTS generation  
**Index**: Uses PRIMARY KEY index for O(log n) lookups

### **Complete Vocabulary Retrieval**
```python
def get_vocabulary_info(word: str) -> dict:
    """Retrieve complete vocabulary information"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ChineseWord as word,
                   PinyinPronunciation as pinyin,
                   SpanishMeaning as spanish_meaning,
                   ChineseMeaning as chinese_meaning,
                   WordType as word_type,
                   Sinonims as synonyms,
                   Antonims as antonyms,
                   UsageExample as usage_example,
                   UpdatedAt as updated_at
            FROM vocabulary 
            WHERE ChineseWord = ?
        """, (word,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        close_database_connection(conn)
```

**Returns**: Complete vocabulary data dictionary or None  
**Usage**: Display in right sidebar, vocabulary cards  
**Format**: Standardized field names for frontend consistency

### **Vocabulary Insertion** (AI-Generated)
```python
def insert_vocabulary_word(definition_data: dict) -> bool:
    """Insert AI-generated definition into database"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Prepare data with defaults
        word_data = {
            'word': definition_data.get('word', ''),
            'pinyin': definition_data.get('pinyin', ''),
            'spanish_meaning': definition_data.get('spanish_meaning', ''),
            'chinese_meaning': definition_data.get('chinese_meaning', ''),
            'word_type': definition_data.get('word_type', ''),
            'synonyms': definition_data.get('synonyms', '无'),
            'antonyms': definition_data.get('antonyms', '无'),
            'usage_example': definition_data.get('usage_example', ''),
            'updated_at': datetime.now().isoformat(),
            'filename': 'AI_Generated',
            'length': len(definition_data.get('word', ''))
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO vocabulary (
                ChineseWord, PinyinPronunciation, SpanishMeaning,
                ChineseMeaning, WordType, Sinonims, Antonims,
                UsageExample, UpdatedAt, filename, length
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            word_data['word'], word_data['pinyin'], word_data['spanish_meaning'],
            word_data['chinese_meaning'], word_data['word_type'], 
            word_data['synonyms'], word_data['antonyms'],
            word_data['usage_example'], word_data['updated_at'],
            word_data['filename'], word_data['length']
        ))
        
        conn.commit()
        logger.info(f"Inserted vocabulary word: {word_data['word']}")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Database insertion failed: {e}")
        conn.rollback()
        return False
    finally:
        close_database_connection(conn)
```

**Features**: UPSERT operation (INSERT OR REPLACE)  
**Source Tracking**: Marks AI-generated entries with "AI_Generated" filename  
**Error Handling**: Transaction rollback on failure  
**Logging**: Detailed success/failure logging

---

## 💾 Session Metadata Storage

### **File-Based Session Storage**
FastTTS uses file-based storage for session data to enable easy backup and synchronization.

**Structure**:
```
sessions/
├── session_metadata.json           # Global UI preferences
├── 20250625_143022/                # Individual session directory
│   ├── metadata.json               # Session information
│   ├── timestamps.json             # Word timing data
│   └── audio.mp3                   # Generated TTS audio
└── 20250625_144515/
    ├── metadata.json
    ├── timestamps.json
    └── audio.mp3
```

### **Global Session Metadata** (`session_metadata.json`)
```json
{
  "20250625_143022": {
    "is_favorite": true,
    "custom_name": "Chinese Grammar Lesson 1",
    "created_at": "2025-06-25T14:30:22Z",
    "modified_at": "2025-06-25T15:45:30Z"
  },
  "20250625_144515": {
    "is_favorite": false,
    "custom_name": null,
    "created_at": "2025-06-25T14:45:15Z",
    "modified_at": "2025-06-25T14:45:15Z"
  }
}
```

### **Individual Session Metadata** (`sessions/{id}/metadata.json`)
```json
{
  "id": "20250625_143022",
  "text": "你好世界，我是FastTTS",
  "date": "2025-06-25 14:30:22",
  "word_count": 8,
  "custom_name": "Chinese Grammar Lesson 1",
  "tts_engine": "edge",
  "voice": "zh-CN-XiaoxiaoNeural",
  "speed": 1.0,
  "volume": 1.0
}
```

### **Word Timing Data** (`sessions/{id}/timestamps.json`)
```json
[
  {
    "word": "你",
    "startTime": 0.1,
    "endTime": 0.5,
    "wordId": "word_0",
    "wordIndex": 0,
    "hasVocabulary": true,
    "vocabularySource": "database"
  },
  {
    "word": "好",
    "startTime": 0.5,
    "endTime": 0.9,
    "wordId": "word_1", 
    "wordIndex": 1,
    "hasVocabulary": true,
    "vocabularySource": "ai_generated"
  }
]
```

---

## 🔄 Vocabulary State Management (`utils/vocabulary_manager.py`)

### **Database Statistics**
```python
def get_database_stats() -> dict:
    """Comprehensive database statistics for monitoring"""
    db_path = get_path_manager().vocab_db_path
    
    try:
        # File system information
        file_size = db_path.stat().st_size if db_path.exists() else 0
        last_modified = datetime.fromtimestamp(
            db_path.stat().st_mtime
        ) if db_path.exists() else None
        
        # Database content statistics
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Total word count
        cursor.execute("SELECT COUNT(*) FROM vocabulary")
        word_count = cursor.fetchone()[0]
        
        # Word type distribution
        cursor.execute("""
            SELECT WordType, COUNT(*) 
            FROM vocabulary 
            WHERE WordType IS NOT NULL 
            GROUP BY WordType 
            ORDER BY COUNT(*) DESC
        """)
        word_types = dict(cursor.fetchall())
        
        # Source distribution
        cursor.execute("""
            SELECT filename, COUNT(*) 
            FROM vocabulary 
            GROUP BY filename 
            ORDER BY COUNT(*) DESC
        """)
        sources = dict(cursor.fetchall())
        
        return {
            'filename': db_path.name,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'word_count': word_count,
            'last_modified': last_modified.isoformat() if last_modified else None,
            'last_modified_formatted': last_modified.strftime('%Y-%m-%d %H:%M') if last_modified else None,
            'word_types': word_types,
            'sources': sources
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {'error': str(e)}
    finally:
        close_database_connection(conn)
```

### **Vocabulary Refresh Operations**
```python
async def refresh_vocabulary_state(progress_callback=None) -> dict:
    """Refresh vocabulary status across all sessions"""
    start_time = time.time()
    sessions_processed = 0
    words_updated = 0
    
    try:
        # Get all sessions
        sessions_dir = get_path_manager().sessions_dir
        if not sessions_dir.exists():
            return {'success': True, 'message': 'No sessions to process'}
        
        session_dirs = [d for d in sessions_dir.iterdir() if d.is_dir()]
        total_sessions = len(session_dirs)
        
        # Process each session
        for i, session_dir in enumerate(session_dirs):
            if progress_callback:
                await progress_callback(
                    f"Processing session {i+1} of {total_sessions}...",
                    i, total_sessions
                )
            
            # Load and update timestamps
            timestamps_file = session_dir / 'timestamps.json'
            if timestamps_file.exists():
                with open(timestamps_file, 'r', encoding='utf-8') as f:
                    word_data = json.load(f)
                
                updated = False
                for word_entry in word_data:
                    word_text = word_entry.get('word', '')
                    if word_text:
                        # Check current vocabulary status
                        has_vocab = check_word_in_vocabulary(word_text)
                        if word_entry.get('hasVocabulary') != has_vocab:
                            word_entry['hasVocabulary'] = has_vocab
                            word_entry['vocabularySource'] = 'database' if has_vocab else 'unknown'
                            words_updated += 1
                            updated = True
                
                # Save updated timestamps
                if updated:
                    with open(timestamps_file, 'w', encoding='utf-8') as f:
                        json.dump(word_data, f, ensure_ascii=False, indent=2)
            
            sessions_processed += 1
        
        duration = time.time() - start_time
        
        return {
            'success': True,
            'message': f'Refresh completed successfully',
            'vocabulary_count': get_database_stats()['word_count'],
            'sessions_processed': sessions_processed,
            'words_updated': words_updated,
            'duration_seconds': round(duration, 2)
        }
        
    except Exception as e:
        logger.error(f"Vocabulary refresh failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'sessions_processed': sessions_processed,
            'words_updated': words_updated
        }
```

---

## 🔍 Query Patterns and Performance

### **Common Query Patterns**

#### **Word Lookup (Primary Use Case)**
```sql
-- Fast existence check (uses PRIMARY KEY index)
SELECT 1 FROM vocabulary WHERE ChineseWord = ? LIMIT 1;

-- Complete word information
SELECT * FROM vocabulary WHERE ChineseWord = ?;
```

#### **Filtering and Search Queries**
```sql
-- Filter by word type
SELECT ChineseWord, PinyinPronunciation, SpanishMeaning 
FROM vocabulary 
WHERE WordType = '名词' 
ORDER BY length, ChineseWord;

-- Filter by character length
SELECT ChineseWord, SpanishMeaning 
FROM vocabulary 
WHERE length = 2 
ORDER BY ChineseWord;

-- Search by Spanish meaning (full-text search)
SELECT ChineseWord, PinyinPronunciation, SpanishMeaning 
FROM vocabulary 
WHERE SpanishMeaning LIKE '%mundo%' 
ORDER BY length;

-- Recent additions (AI-generated)
SELECT ChineseWord, UpdatedAt, filename 
FROM vocabulary 
WHERE filename = 'AI_Generated' 
ORDER BY UpdatedAt DESC 
LIMIT 20;
```

#### **Statistics and Analysis Queries**
```sql
-- Word type distribution
SELECT WordType, COUNT(*) as count 
FROM vocabulary 
WHERE WordType IS NOT NULL 
GROUP BY WordType 
ORDER BY count DESC;

-- Length distribution
SELECT length, COUNT(*) as count 
FROM vocabulary 
GROUP BY length 
ORDER BY length;

-- Source file analysis
SELECT filename, COUNT(*) as word_count, 
       MIN(UpdatedAt) as first_entry,
       MAX(UpdatedAt) as last_entry
FROM vocabulary 
GROUP BY filename 
ORDER BY word_count DESC;
```

### **Performance Metrics**

| Operation | Time Complexity | Typical Response | Index Used |
|-----------|----------------|------------------|------------|
| Word existence check | O(log n) | <1ms | PRIMARY KEY |
| Complete word lookup | O(log n) | <5ms | PRIMARY KEY |
| Type filtering | O(m log n) | <20ms | idx_vocabulary_type |
| Length filtering | O(k log n) | <15ms | idx_vocabulary_length |
| Full-text search | O(n) | <100ms | None (sequential scan) |
| Insert operation | O(log n) | <10ms | PRIMARY KEY |
| Statistics query | O(n) | <50ms | Various indexes |

### **Optimization Strategies**

#### **Connection Pooling**
```python
# Connection pool for high-frequency operations
import threading
from queue import Queue

class DatabasePool:
    def __init__(self, max_connections=5):
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(max_connections):
            conn = get_database_connection()
            self.pool.put(conn)
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, conn):
        self.pool.put(conn)
```

#### **Batch Operations**
```python
def batch_vocabulary_check(words: list) -> dict:
    """Check multiple words in single database operation"""
    if not words:
        return {}
    
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(words))
        
        cursor.execute(f"""
            SELECT ChineseWord, 1 as exists 
            FROM vocabulary 
            WHERE ChineseWord IN ({placeholders})
        """, words)
        
        results = {word: False for word in words}  # Default to False
        for row in cursor.fetchall():
            results[row[0]] = True
            
        return results
    finally:
        close_database_connection(conn)
```

#### **Prepared Statements Pattern**
```python
class VocabularyQueries:
    """Pre-compiled query patterns for better performance"""
    
    WORD_EXISTS = "SELECT 1 FROM vocabulary WHERE ChineseWord = ? LIMIT 1"
    WORD_INFO = """
        SELECT ChineseWord, PinyinPronunciation, SpanishMeaning,
               ChineseMeaning, WordType, Sinonims, Antonims, UsageExample
        FROM vocabulary WHERE ChineseWord = ?
    """
    INSERT_WORD = """
        INSERT OR REPLACE INTO vocabulary 
        (ChineseWord, PinyinPronunciation, SpanishMeaning, ChineseMeaning,
         WordType, Sinonims, Antonims, UsageExample, UpdatedAt, filename, length)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
```

---

## 🛡️ Data Integrity and Backup

### **Database Integrity Checks**
```sql
-- Check for corruption
PRAGMA integrity_check;

-- Analyze database statistics
PRAGMA table_info(vocabulary);

-- Check foreign key consistency
PRAGMA foreign_key_check;

-- Verify indexes
SELECT name, sql FROM sqlite_master WHERE type='index';
```

### **Backup Strategy**
```python
def backup_database(backup_path: str) -> bool:
    """Create database backup with verification"""
    try:
        source_db = get_path_manager().vocab_db_path
        backup_db = Path(backup_path)
        
        # Create backup using SQLite backup API
        source_conn = sqlite3.connect(str(source_db))
        backup_conn = sqlite3.connect(str(backup_db))
        
        source_conn.backup(backup_conn)
        
        # Verify backup integrity
        backup_conn.execute("PRAGMA integrity_check")
        result = backup_conn.fetchone()
        
        source_conn.close()
        backup_conn.close()
        
        if result[0] == 'ok':
            logger.info(f"Database backup created: {backup_path}")
            return True
        else:
            logger.error(f"Backup integrity check failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False
```

### **Data Validation Rules**
```python
def validate_vocabulary_entry(entry: dict) -> list:
    """Validate vocabulary entry data"""
    errors = []
    
    # Required fields
    if not entry.get('word'):
        errors.append("Chinese word is required")
    
    # Length validation
    word = entry.get('word', '')
    if len(word) != entry.get('length', 0):
        errors.append(f"Length mismatch: expected {len(word)}, got {entry.get('length')}")
    
    # Character validation
    if word and not all('\u4e00' <= char <= '\u9fff' for char in word if char.isalpha()):
        errors.append("Word contains non-Chinese characters")
    
    # Pinyin validation (basic)
    pinyin = entry.get('pinyin', '')
    if pinyin and not all(char.isalpha() or char in 'āáǎàēéěèīíǐìōóǒòūúǔùüǖǘǚǜ' for char in pinyin):
        errors.append("Invalid pinyin format")
    
    return errors
```

---

## 📊 Database Monitoring and Maintenance

### **Performance Monitoring**
```python
def get_database_performance_metrics() -> dict:
    """Database performance and usage statistics"""
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        
        # Table size information
        cursor.execute("SELECT COUNT(*) FROM vocabulary")
        row_count = cursor.fetchone()[0]
        
        # Index usage statistics (SQLite specific)
        cursor.execute("PRAGMA index_list('vocabulary')")
        indexes = cursor.fetchall()
        
        # Database file size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        return {
            'row_count': row_count,
            'indexes': len(indexes),
            'database_size_bytes': page_count * page_size,
            'pages': page_count,
            'page_size': page_size
        }
    finally:
        close_database_connection(conn)
```

### **Maintenance Operations**
```sql
-- Optimize database (rebuild indexes, clean up)
VACUUM;

-- Update table statistics for query optimizer
ANALYZE;

-- Check for unused space
PRAGMA freelist_count;

-- Rebuild indexes if needed
REINDEX vocabulary;
```

---

*This guide provides comprehensive database documentation for AI coding assistants working with FastTTS. The SQLite-based system offers excellent performance for vocabulary lookups while maintaining data integrity and supporting future expansion.*