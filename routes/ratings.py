"""
Rating routes for FastTTS star rating system
Handles HTMX endpoints for rating updates and retrieval
"""

from fasthtml.common import *
import logging
import json
from typing import Optional
from urllib.parse import unquote

from utils.rating_helpers import (
    get_word_rating, 
    update_word_rating, 
    get_all_word_ratings,
    get_rating_statistics,
    initialize_ratings_system
)
from components.star_rating import render_star_rating, render_compact_star_rating

logger = logging.getLogger(__name__)


def register_rating_routes(app):
    """
    Register all rating-related routes with the FastHTML app
    
    Args:
        app: FastHTML application instance
    """
    
    @app.post("/update-rating/{chinese_word}")
    async def update_rating_endpoint(chinese_word: str, request):
        """
        Update the rating for a specific Chinese word
        
        Args:
            chinese_word (str): The Chinese word to rate
            request: FastHTML request object containing form data
            
        Returns:
            JSON response indicating success/failure
        """
        try:
            # URL decode the Chinese word
            chinese_word = unquote(chinese_word)
            
            # Get form data
            form_data = await request.form()
            
            # Extract rating value
            rating_value = None
            for key, value in form_data.items():
                if 'rating' in key.lower() or key == 'value':
                    rating_value = value
                    break
            
            # If not found in form data, try to get from range input
            if rating_value is None:
                # Look for range input value in form
                for key, value in form_data.items():
                    try:
                        float_val = float(value)
                        if 0.5 <= float_val <= 5.0:
                            rating_value = value
                            break
                    except (ValueError, TypeError):
                        continue
            
            if rating_value is None:
                logger.error(f"No rating value found in request for word: {chinese_word}")
                return JSONResponse(
                    {"success": False, "error": "No rating value provided"},
                    status_code=400
                )
            
            try:
                rating = float(rating_value)
            except (ValueError, TypeError):
                return JSONResponse(
                    {"success": False, "error": f"Invalid rating value: {rating_value}"},
                    status_code=400
                )
            
            # Validate rating range
            if not (0.5 <= rating <= 5.0):
                return JSONResponse(
                    {"success": False, "error": f"Rating must be between 0.5 and 5.0, got: {rating}"},
                    status_code=400
                )
            
            # Update the rating in database
            success = update_word_rating(chinese_word, rating)
            
            if success:
                logger.info(f"Successfully updated rating for '{chinese_word}' to {rating}")
                return JSONResponse({
                    "success": True,
                    "chinese_word": chinese_word,
                    "rating": rating,
                    "message": f"Rating updated to {rating} stars"
                })
            else:
                logger.error(f"Failed to update rating for '{chinese_word}'")
                return JSONResponse(
                    {"success": False, "error": "Failed to update rating in database"},
                    status_code=500
                )
                
        except Exception as e:
            logger.error(f"Error in update_rating_endpoint: {e}")
            return JSONResponse(
                {"success": False, "error": f"Server error: {str(e)}"},
                status_code=500
            )
    
    
    @app.get("/get-rating/{chinese_word}")
    async def get_rating_endpoint(chinese_word: str):
        """
        Get the current rating for a specific Chinese word
        
        Args:
            chinese_word (str): The Chinese word to get rating for
            
        Returns:
            JSON response with rating data
        """
        try:
            # URL decode the Chinese word
            chinese_word = unquote(chinese_word)
            
            # Get rating from database
            rating = get_word_rating(chinese_word)
            
            return JSONResponse({
                "success": True,
                "chinese_word": chinese_word,
                "rating": rating,
                "has_rating": rating is not None
            })
            
        except Exception as e:
            logger.error(f"Error in get_rating_endpoint: {e}")
            return JSONResponse(
                {"success": False, "error": f"Server error: {str(e)}"},
                status_code=500
            )
    
    
    @app.get("/rating-component/{chinese_word}")
    async def get_rating_component(chinese_word: str, compact: bool = False):
        """
        Get a star rating component for a specific word
        
        Args:
            chinese_word (str): The Chinese word
            compact (bool): Whether to return compact version
            
        Returns:
            HTML star rating component
        """
        try:
            # URL decode the Chinese word
            chinese_word = unquote(chinese_word)
            
            # Get current rating
            current_rating = get_word_rating(chinese_word)
            
            # Return appropriate component
            if compact:
                return render_compact_star_rating(chinese_word, current_rating)
            else:
                return render_star_rating(chinese_word, current_rating)
                
        except Exception as e:
            logger.error(f"Error in get_rating_component: {e}")
            return Div(
                P(f"Error loading rating component: {str(e)}", cls="text-red-500 text-sm"),
                cls="rating-error"
            )
    
    
    @app.get("/all-ratings")
    async def get_all_ratings_endpoint():
        """
        Get all word ratings
        
        Returns:
            JSON response with all ratings
        """
        try:
            ratings = get_all_word_ratings()
            
            return JSONResponse({
                "success": True,
                "ratings": ratings,
                "count": len(ratings)
            })
            
        except Exception as e:
            logger.error(f"Error in get_all_ratings_endpoint: {e}")
            return JSONResponse(
                {"success": False, "error": f"Server error: {str(e)}"},
                status_code=500
            )
    
    
    @app.get("/rating-statistics")
    async def get_rating_statistics_endpoint():
        """
        Get rating statistics
        
        Returns:
            JSON response with rating statistics
        """
        try:
            stats = get_rating_statistics()
            
            return JSONResponse({
                "success": True,
                "statistics": stats
            })
            
        except Exception as e:
            logger.error(f"Error in get_rating_statistics_endpoint: {e}")
            return JSONResponse(
                {"success": False, "error": f"Server error: {str(e)}"},
                status_code=500
            )
    
    
    @app.post("/initialize-ratings")
    async def initialize_ratings_endpoint():
        """
        Initialize the ratings system (create tables if needed)
        
        Returns:
            JSON response indicating success/failure
        """
        try:
            success = initialize_ratings_system()
            
            if success:
                return JSONResponse({
                    "success": True,
                    "message": "Ratings system initialized successfully"
                })
            else:
                return JSONResponse(
                    {"success": False, "error": "Failed to initialize ratings system"},
                    status_code=500
                )
                
        except Exception as e:
            logger.error(f"Error in initialize_ratings_endpoint: {e}")
            return JSONResponse(
                {"success": False, "error": f"Server error: {str(e)}"},
                status_code=500
            )
    
    
    logger.info("Rating routes registered successfully")