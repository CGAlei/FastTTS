"""
Rating helper functions for FastTTS star rating system
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from utils.db_helpers import get_database_connection, close_database_connection

logger = logging.getLogger(__name__)


def create_ratings_table():
    """
    Create the word_ratings table if it doesn't exist
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_database_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Create word_ratings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chinese_word TEXT NOT NULL,
                rating REAL NOT NULL DEFAULT 2.5,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (chinese_word) REFERENCES vocabulary (ChineseWord),
                UNIQUE(chinese_word)
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_word_ratings_chinese_word 
            ON word_ratings (chinese_word)
        """)
        
        conn.commit()
        logger.info("Word ratings table created/verified successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating word_ratings table: {e}")
        return False
    finally:
        close_database_connection(conn)


def get_word_rating(chinese_word: str) -> Optional[float]:
    """
    Get the rating for a specific Chinese word
    
    Args:
        chinese_word (str): The Chinese word to get rating for
        
    Returns:
        Optional[float]: Rating value (0.5-5.0) or None if not found
    """
    try:
        conn = get_database_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating FROM word_ratings WHERE chinese_word = ?",
            (chinese_word,)
        )
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Error getting rating for word '{chinese_word}': {e}")
        return None
    finally:
        close_database_connection(conn)


def update_word_rating(chinese_word: str, rating: float) -> bool:
    """
    Update or insert the rating for a Chinese word
    
    Args:
        chinese_word (str): The Chinese word to rate
        rating (float): Rating value (0.5-5.0)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate rating range
        if not (0.5 <= rating <= 5.0):
            logger.error(f"Invalid rating value: {rating}. Must be between 0.5 and 5.0")
            return False
            
        # Validate rating increment (must be multiple of 0.5)
        if (rating * 2) % 1 != 0:
            logger.error(f"Invalid rating value: {rating}. Must be in 0.5 increments")
            return False
            
        conn = get_database_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        
        # Use INSERT OR REPLACE to handle both insert and update
        cursor.execute("""
            INSERT OR REPLACE INTO word_ratings (chinese_word, rating, updated_at)
            VALUES (?, ?, ?)
        """, (chinese_word, rating, current_time))
        
        conn.commit()
        logger.info(f"Updated rating for '{chinese_word}' to {rating}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating rating for word '{chinese_word}': {e}")
        return False
    finally:
        close_database_connection(conn)


def get_all_word_ratings() -> Dict[str, float]:
    """
    Get all word ratings as a dictionary
    
    Returns:
        Dict[str, float]: Dictionary mapping Chinese words to their ratings
    """
    try:
        conn = get_database_connection()
        if not conn:
            return {}
            
        cursor = conn.cursor()
        cursor.execute("SELECT chinese_word, rating FROM word_ratings")
        
        results = cursor.fetchall()
        return {row[0]: row[1] for row in results}
        
    except Exception as e:
        logger.error(f"Error getting all word ratings: {e}")
        return {}
    finally:
        close_database_connection(conn)


def get_words_by_rating(min_rating: float = 0.5, max_rating: float = 5.0) -> List[Tuple[str, float]]:
    """
    Get words filtered by rating range
    
    Args:
        min_rating (float): Minimum rating to include
        max_rating (float): Maximum rating to include
        
    Returns:
        List[Tuple[str, float]]: List of (chinese_word, rating) tuples
    """
    try:
        conn = get_database_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        cursor.execute("""
            SELECT chinese_word, rating 
            FROM word_ratings 
            WHERE rating >= ? AND rating <= ?
            ORDER BY rating DESC, chinese_word ASC
        """, (min_rating, max_rating))
        
        return cursor.fetchall()
        
    except Exception as e:
        logger.error(f"Error getting words by rating ({min_rating}-{max_rating}): {e}")
        return []
    finally:
        close_database_connection(conn)


def delete_word_rating(chinese_word: str) -> bool:
    """
    Delete the rating for a specific Chinese word
    
    Args:
        chinese_word (str): The Chinese word to delete rating for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_database_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute("DELETE FROM word_ratings WHERE chinese_word = ?", (chinese_word,))
        
        conn.commit()
        rows_affected = cursor.rowcount
        
        if rows_affected > 0:
            logger.info(f"Deleted rating for '{chinese_word}'")
        else:
            logger.warning(f"No rating found to delete for '{chinese_word}'")
            
        return True
        
    except Exception as e:
        logger.error(f"Error deleting rating for word '{chinese_word}': {e}")
        return False
    finally:
        close_database_connection(conn)


def get_rating_statistics() -> Dict:
    """
    Get statistics about word ratings
    
    Returns:
        Dict: Statistics including count, average, distribution
    """
    try:
        conn = get_database_connection()
        if not conn:
            return {}
            
        cursor = conn.cursor()
        
        # Get basic statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ratings,
                AVG(rating) as average_rating,
                MIN(rating) as min_rating,
                MAX(rating) as max_rating
            FROM word_ratings
        """)
        
        stats = cursor.fetchone()
        result = {
            'total_ratings': stats[0] if stats else 0,
            'average_rating': round(stats[1], 2) if stats and stats[1] else 0,
            'min_rating': stats[2] if stats else 0,
            'max_rating': stats[3] if stats else 0,
        }
        
        # Get rating distribution
        cursor.execute("""
            SELECT rating, COUNT(*) as count
            FROM word_ratings
            GROUP BY rating
            ORDER BY rating
        """)
        
        distribution = cursor.fetchall()
        result['distribution'] = {str(row[0]): row[1] for row in distribution}
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting rating statistics: {e}")
        return {}
    finally:
        close_database_connection(conn)


def initialize_ratings_system() -> bool:
    """
    Initialize the ratings system by creating necessary tables
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        success = create_ratings_table()
        if success:
            logger.info("Ratings system initialized successfully")
        else:
            logger.error("Failed to initialize ratings system")
        return success
        
    except Exception as e:
        logger.error(f"Error initializing ratings system: {e}")
        return False