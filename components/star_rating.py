"""
Star rating component for FastTTS vocabulary system
Based on single HTML element star rating tutorial
"""

from fasthtml.common import *
from typing import Optional


def render_star_rating(chinese_word: str, current_rating: Optional[float] = None, 
                      disabled: bool = False, size: str = "1.2rem") -> Div:
    """
    Renders a star rating component for a vocabulary word
    
    Args:
        chinese_word (str): The Chinese word this rating belongs to
        current_rating (Optional[float]): Current rating value (0.5-5.0)
        disabled (bool): Whether the rating is read-only
        size (str): CSS size value for the stars
        
    Returns:
        Div: Star rating component container
    """
    # Set default rating if none provided
    if current_rating is None:
        current_rating = 2.5
        
    # Ensure rating is within valid range and increments
    current_rating = max(0.5, min(5.0, round(current_rating * 2) / 2))
    
    # Create unique ID for this rating component
    rating_id = f"rating-{chinese_word.replace(' ', '-')}"
    
    return Div(
        # Star rating input element
        Input(
            type="range",
            min="0.5",
            max="5",
            step="0.5",
            value=str(current_rating),
            cls=f"star-rating {'star-rating-disabled' if disabled else ''}",
            id=rating_id,
            style=f"--val: {current_rating}; --size: {size}",
            disabled=disabled,
            **{
                "data-chinese-word": chinese_word,
                "data-current-rating": str(current_rating),
                "aria-label": f"Rate word {chinese_word}",
                "hx-post": f"/update-rating/{chinese_word}",
                "hx-trigger": "input",
                "hx-include": f"#{rating_id}",
                "hx-swap": "none",
                "oninput": f"this.style.setProperty('--val', this.value)"
            }
        ),
        
        # Rating display (for accessibility and visual feedback)
        Div(
            Span(
                current_rating,
                id=f"rating-display-{chinese_word.replace(' ', '-')}",
                cls="rating-display-value"
            ),
            " / 5 ⭐",
            cls="rating-display",
            **{"aria-live": "polite"}
        ),
        
        cls="star-rating-container",
        id=f"star-rating-container-{chinese_word.replace(' ', '-')}"
    )


def render_compact_star_rating(chinese_word: str, current_rating: Optional[float] = None, 
                             size: str = "1rem") -> Div:
    """
    Renders a compact star rating component (stars only, no text)
    
    Args:
        chinese_word (str): The Chinese word this rating belongs to
        current_rating (Optional[float]): Current rating value (0.5-5.0)
        size (str): CSS size value for the stars
        
    Returns:
        Div: Compact star rating component
    """
    # Set default rating if none provided
    if current_rating is None:
        current_rating = 2.5
        
    # Ensure rating is within valid range and increments
    current_rating = max(0.5, min(5.0, round(current_rating * 2) / 2))
    
    # Create unique ID for this rating component
    rating_id = f"compact-rating-{chinese_word.replace(' ', '-')}"
    
    return Div(
        Input(
            type="range",
            min="0.5",
            max="5",
            step="0.5",
            value=str(current_rating),
            cls="star-rating star-rating-compact",
            id=rating_id,
            style=f"--val: {current_rating}; --size: {size}",
            **{
                "data-chinese-word": chinese_word,
                "data-current-rating": str(current_rating),
                "aria-label": f"Rate word {chinese_word}: {current_rating} stars",
                "hx-post": f"/update-rating/{chinese_word}",
                "hx-trigger": "input",
                "hx-include": f"#{rating_id}",
                "hx-swap": "none",
                "oninput": f"this.style.setProperty('--val', this.value)"
            }
        ),
        cls="star-rating-container compact",
        id=f"compact-star-rating-container-{chinese_word.replace(' ', '-')}",
        title=f"Rating: {current_rating}/5 stars"
    )


def render_readonly_star_rating(current_rating: float, size: str = "1rem") -> Div:
    """
    Renders a read-only star rating display
    
    Args:
        current_rating (float): Rating value to display (0.5-5.0)
        size (str): CSS size value for the stars
        
    Returns:
        Div: Read-only star rating display
    """
    # Ensure rating is within valid range
    current_rating = max(0.5, min(5.0, round(current_rating * 2) / 2))
    
    return Div(
        Div(
            cls="star-rating-readonly",
            style=f"--val: {current_rating}; --size: {size}",
            **{"aria-label": f"Rating: {current_rating} out of 5 stars"}
        ),
        cls="star-rating-container readonly",
        title=f"Rating: {current_rating}/5 stars"
    )


def render_rating_summary(ratings_stats: dict) -> Div:
    """
    Renders a summary of rating statistics
    
    Args:
        ratings_stats (dict): Statistics from get_rating_statistics()
        
    Returns:
        Div: Rating summary component
    """
    total = ratings_stats.get('total_ratings', 0)
    average = ratings_stats.get('average_rating', 0)
    distribution = ratings_stats.get('distribution', {})
    
    if total == 0:
        return Div(
            P("No words have been rated yet.", cls="text-gray-500 text-sm italic"),
            cls="rating-summary empty"
        )
    
    return Div(
        Div(
            H4("Rating Summary", cls="text-sm font-semibold mb-2"),
            
            # Overall statistics
            Div(
                Div(f"Total Rated: {total}", cls="stat-item"),
                Div(f"Average: {average}⭐", cls="stat-item"),
                cls="rating-stats flex gap-4 mb-3"
            ),
            
            # Rating distribution
            Div(
                H5("Distribution:", cls="text-xs font-medium mb-1"),
                *[
                    Div(
                        Span(f"{rating}⭐", cls="rating-label"),
                        Span(f"({count})", cls="rating-count"),
                        cls="distribution-item flex justify-between text-xs"
                    )
                    for rating, count in sorted(distribution.items(), key=lambda x: float(x[0]), reverse=True)
                ],
                cls="rating-distribution"
            ),
            
            cls="rating-summary-content"
        ),
        cls="rating-summary card p-3 bg-gray-50 border rounded"
    )