"""
Database connection pool for FastTTS to optimize vocabulary lookups
"""

import sqlite3
import threading
import time
import logging
from pathlib import Path
from config.paths import get_path_manager

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool for vocabulary database"""
    
    def __init__(self, max_connections=5, connection_timeout=300):
        self.path_manager = get_path_manager()
        self.db_path = str(self.path_manager.vocab_db_path)
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        # Thread-safe connection pool
        self._pool = []
        self._pool_lock = threading.Lock()
        self._connection_times = {}
        
        # Pre-create initial connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with initial connections"""
        try:
            for i in range(min(2, self.max_connections)):  # Start with 2 connections
                conn = self._create_connection()
                if conn:
                    self._pool.append(conn)
                    self._connection_times[id(conn)] = time.time()
            
            logger.info(f"Database connection pool initialized with {len(self._pool)} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
    
    def _create_connection(self):
        """Create a new SQLite connection with optimizations"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Allow sharing between threads
                timeout=10.0  # 10 second timeout for database lock
            )
            
            # Optimize SQLite for read performance
            conn.execute("PRAGMA synchronous = OFF")  # Faster writes (safe for read-heavy workload)
            conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
            conn.execute("PRAGMA cache_size = 10000")  # 10MB cache
            conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temporary storage
            conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
            
            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def get_connection(self):
        """Get a connection from the pool (thread-safe)"""
        with self._pool_lock:
            # Clean up expired connections
            self._cleanup_expired_connections()
            
            # Try to get existing connection
            if self._pool:
                conn = self._pool.pop()
                self._connection_times[id(conn)] = time.time()  # Update usage time
                return conn
            
            # Create new connection if pool is empty and under limit
            if len(self._connection_times) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._connection_times[id(conn)] = time.time()
                    return conn
            
            # Fallback: create temporary connection
            logger.warning("Connection pool exhausted, creating temporary connection")
            return self._create_connection()
    
    def return_connection(self, conn):
        """Return a connection to the pool (thread-safe)"""
        if not conn:
            return
        
        try:
            # Test if connection is still valid
            conn.execute("SELECT 1")
            
            with self._pool_lock:
                if len(self._pool) < self.max_connections:
                    self._pool.append(conn)
                    self._connection_times[id(conn)] = time.time()
                else:
                    # Pool is full, close the connection
                    conn.close()
                    self._connection_times.pop(id(conn), None)
        except Exception as e:
            # Connection is invalid, close it
            logger.debug(f"Closing invalid connection: {e}")
            try:
                conn.close()
            except:
                pass
            self._connection_times.pop(id(conn), None)
    
    def _cleanup_expired_connections(self):
        """Remove connections that have been idle too long"""
        current_time = time.time()
        expired_connections = []
        
        # Find expired connections in pool
        for conn in self._pool[:]:  # Copy list to avoid modification during iteration
            conn_id = id(conn)
            if conn_id in self._connection_times:
                if current_time - self._connection_times[conn_id] > self.connection_timeout:
                    expired_connections.append(conn)
                    self._pool.remove(conn)
        
        # Close expired connections
        for conn in expired_connections:
            try:
                conn.close()
                self._connection_times.pop(id(conn), None)
            except:
                pass
        
        if expired_connections:
            logger.debug(f"Cleaned up {len(expired_connections)} expired connections")
    
    def close_all(self):
        """Close all connections in the pool"""
        with self._pool_lock:
            for conn in self._pool:
                try:
                    conn.close()
                except:
                    pass
            
            self._pool.clear()
            self._connection_times.clear()
            
        logger.info("Database connection pool closed")

# Global connection pool instance
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """Get the global database connection pool (thread-safe singleton)"""
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = DatabaseConnectionPool()
    
    return _connection_pool

def get_pooled_connection():
    """Get a database connection from the pool"""
    pool = get_connection_pool()
    return pool.get_connection()

def return_pooled_connection(conn):
    """Return a database connection to the pool"""
    pool = get_connection_pool()
    return pool.return_connection(conn)

class PooledConnection:
    """Context manager for database connections from pool"""
    
    def __init__(self):
        self.conn = None
    
    def __enter__(self):
        self.conn = get_pooled_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            return_pooled_connection(self.conn)

# Cleanup function for graceful shutdown
def cleanup_connection_pool():
    """Close all connections in the pool"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.close_all()
        _connection_pool = None