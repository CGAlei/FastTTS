"""
Progress Manager for TTS Generation
Handles real-time progress tracking and SSE communication
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import uuid


class TTSProgressManager:
    """Manages progress tracking for TTS generation sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.sse_clients: Dict[str, List] = {}
        self.cleanup_task = None
        
    def create_session(self, total_chunks: int = 1) -> str:
        """
        Create a new progress tracking session
        
        Args:
            total_chunks: Total number of chunks to process
            
        Returns:
            Session ID for tracking progress
        """
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            'total_chunks': total_chunks,
            'current_chunk': 0,
            'status': 'starting',
            'message': 'Initializing TTS generation...',
            'percentage': 0,
            'start_time': time.time(),
            'last_update': time.time(),
            'error': None
        }
        
        # Initialize SSE client list for this session
        self.sse_clients[session_id] = []
        
        # Start cleanup task if not already running
        self._ensure_cleanup_task()
        
        return session_id
    
    def update_progress(self, session_id: str, current_chunk: int, message: str = None, status: str = 'processing'):
        """
        Update progress for a session
        
        Args:
            session_id: Session ID
            current_chunk: Current chunk being processed
            message: Custom progress message
            status: Current status (processing, completed, error)
        """
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        session['current_chunk'] = current_chunk
        session['status'] = status
        session['last_update'] = time.time()
        
        # Calculate percentage
        if session['total_chunks'] > 0:
            session['percentage'] = int((current_chunk / session['total_chunks']) * 100)
        
        # Generate message if not provided
        if message is None:
            if status == 'processing':
                if session['total_chunks'] > 1:
                    message = f"Processing chunk {current_chunk}/{session['total_chunks']}... ({session['percentage']}%)"
                else:
                    message = "Generating audio..."
            elif status == 'combining':
                message = "Combining audio chunks..."
            elif status == 'completed':
                message = "TTS generation completed successfully!"
            elif status == 'error':
                message = "TTS generation failed"
        
        session['message'] = message
        
        # Send SSE update to all connected clients
        self._send_sse_update(session_id, session)
    
    def set_error(self, session_id: str, error_message: str):
        """Set error status for a session"""
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        session['status'] = 'error'
        session['error'] = error_message
        session['message'] = f"Error: {error_message}"
        session['last_update'] = time.time()
        
        self._send_sse_update(session_id, session)
    
    def complete_session(self, session_id: str):
        """Mark session as completed"""
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        session['status'] = 'completed'
        session['percentage'] = 100
        session['message'] = 'TTS generation completed successfully!'
        session['last_update'] = time.time()
        
        self._send_sse_update(session_id, session)
        
        # Schedule cleanup
        asyncio.create_task(self._cleanup_session_later(session_id))
    
    def get_session_progress(self, session_id: str) -> Optional[Dict]:
        """Get current progress for a session"""
        return self.active_sessions.get(session_id)
    
    def add_sse_client(self, session_id: str, response_obj):
        """Add SSE client for a session"""
        if session_id not in self.sse_clients:
            self.sse_clients[session_id] = []
        
        self.sse_clients[session_id].append(response_obj)
    
    def remove_sse_client(self, session_id: str, response_obj):
        """Remove SSE client for a session"""
        if session_id in self.sse_clients:
            try:
                self.sse_clients[session_id].remove(response_obj)
            except ValueError:
                pass
    
    def _send_sse_update(self, session_id: str, session_data: Dict):
        """Send SSE update to all connected clients"""
        if session_id not in self.sse_clients:
            return
        
        # Prepare SSE message
        event_data = {
            'type': 'progress_update',
            'session_id': session_id,
            'current_chunk': session_data['current_chunk'],
            'total_chunks': session_data['total_chunks'],
            'percentage': session_data['percentage'],
            'status': session_data['status'],
            'message': session_data['message'],
            'timestamp': session_data['last_update']
        }
        
        if session_data.get('error'):
            event_data['error'] = session_data['error']
        
        sse_message = f"data: {json.dumps(event_data)}\n\n"
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.sse_clients[session_id]:
            try:
                # Try to write to the client
                if hasattr(client, 'write'):
                    client.write(sse_message.encode())
                elif hasattr(client, 'send'):
                    asyncio.create_task(client.send(sse_message))
            except Exception:
                # Client disconnected
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.remove_sse_client(session_id, client)
    
    async def _cleanup_session_later(self, session_id: str, delay: int = 30):
        """Clean up session after delay"""
        await asyncio.sleep(delay)
        
        # Remove session and clients
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        if session_id in self.sse_clients:
            del self.sse_clients[session_id]
    
    def get_minimax_progress(self) -> Optional[Dict]:
        """Get current MiniMax TTS progress for progress bar"""
        # Find the most recent active session
        if not self.active_sessions:
            return None
            
        # Get the most recently updated session that's still processing
        recent_session = None
        for session_id, session in self.active_sessions.items():
            if session['status'] in ['starting', 'processing', 'combining']:
                if recent_session is None or session['last_update'] > recent_session['last_update']:
                    recent_session = session
        
        return recent_session

    def cleanup_old_sessions(self, max_age_minutes: int = 10):
        """Clean up sessions older than max_age_minutes"""
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        
        expired_sessions = []
        for session_id, session in self.active_sessions.items():
            if current_time - session['last_update'] > max_age_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            if session_id in self.sse_clients:
                del self.sse_clients[session_id]
    
    def _ensure_cleanup_task(self):
        """Ensure cleanup task is running"""
        try:
            # Only start if we have an event loop and task is not running
            loop = asyncio.get_running_loop()
            if self.cleanup_task is None or self.cleanup_task.done():
                async def cleanup_loop():
                    while True:
                        try:
                            await asyncio.sleep(300)  # Clean up every 5 minutes
                            self.cleanup_old_sessions(max_age_minutes=10)
                        except Exception as e:
                            print(f"Cleanup task error: {e}")
                
                self.cleanup_task = asyncio.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running, cleanup will be handled manually
            pass


# Global progress manager instance
progress_manager = TTSProgressManager()