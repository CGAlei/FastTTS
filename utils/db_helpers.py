"""
Database helper functions for FastTTS
"""

import sqlite3
import logging
import os

# Get logger
logger = logging.getLogger(__name__)

# Import path manager
from config.paths import get_path_manager

# Initialize path manager
path_manager = get_path_manager()


def get_database_connection(db_path=None):
    """
    Get a database connection with proper error handling
    
    Args:
        db_path (str, optional): Path to database file. Defaults to dynamic vocab_db_path.
    
    Returns:
        sqlite3.Connection or None: Database connection if successful
    """
    try:
        if db_path is None:
            db_path = str(path_manager.vocab_db_path)
            
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database {db_path}: {e}")
        return None


def close_database_connection(conn):
    """
    Safely close a database connection
    
    Args:
        conn (sqlite3.Connection): Database connection to close
    """
    try:
        if conn:
            conn.close()
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with proper error handling
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch_one (bool): Whether to fetch one result
        fetch_all (bool): Whether to fetch all results
        commit (bool): Whether to commit the transaction
    
    Returns:
        Query result or None if error
    """
    conn = None
    try:
        conn = get_database_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
            
        if commit:
            conn.commit()
            
        return result
        
    except Exception as e:
        logger.error(f"Database query error: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        return None
    finally:
        close_database_connection(conn)