"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Review Utilities - Pure functions for review/rating operations.
All functions are pure, deterministic, and atomic.
"""

import hashlib


def create_review(reviewer_id: str, item_id: str, rating: int, text: str, timestamp: int) -> dict:
    """Create review record."""
    return {
        "review_id": generate_review_id(reviewer_id, item_id, timestamp),
        "reviewer_id": reviewer_id,
        "item_id": item_id,
        "rating": rating,
        "text": text,
        "timestamp": timestamp,
        "helpful_count": 0,
        "verified": False
    }


def generate_review_id(reviewer_id: str, item_id: str, timestamp: int) -> str:
    """Generate unique review ID."""
    data = f"{reviewer_id}{item_id}{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def validate_rating(rating: int, min_rating: int, max_rating: int) -> bool:
    """Validate rating value."""
    return min_rating <= rating <= max_rating


def calculate_average_rating(ratings: list) -> float:
    """Calculate average rating."""
    if not ratings:
        return 0
    return round(sum(ratings) / len(ratings), 2)


def calculate_weighted_average(ratings: list, weights: list) -> float:
    """Calculate weighted average rating."""
    if not ratings or not weights:
        return 0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0
    return round(sum(r * w for r, w in zip(ratings, weights)) / total_weight, 2)


def get_rating_distribution(reviews: list, max_rating: int) -> dict:
    """Get distribution of ratings."""
    dist = {i: 0 for i in range(1, max_rating + 1)}
    for review in reviews:
        rating = review.get("rating", 0)
        if rating in dist:
            dist[rating] += 1
    return dist


def get_rating_percentages(distribution: dict) -> dict:
    """Convert distribution to percentages."""
    total = sum(distribution.values())
    if total == 0:
        return {k: 0 for k in distribution}
    return {k: round(v / total * 100, 1) for k, v in distribution.items()}


def mark_as_helpful(review: dict) -> dict:
    """Increment helpful count."""
    return {**review, "helpful_count": review.get("helpful_count", 0) + 1}


def mark_as_verified(review: dict) -> dict:
    """Mark review as verified purchase."""
    return {**review, "verified": True}


def filter_verified_reviews(reviews: list) -> list:
    """Filter to verified reviews only."""
    return [r for r in reviews if r.get("verified", False)]


def filter_by_rating(reviews: list, min_rating: int, max_rating: int) -> list:
    """Filter reviews by rating range."""
    return [r for r in reviews if min_rating <= r.get("rating", 0) <= max_rating]


def filter_with_text(reviews: list) -> list:
    """Filter reviews that have text."""
    return [r for r in reviews if r.get("text", "").strip()]


def sort_by_helpful(reviews: list) -> list:
    """Sort reviews by helpful count."""
    return sorted(reviews, key=lambda r: -r.get("helpful_count", 0))


def sort_by_recent(reviews: list) -> list:
    """Sort reviews by timestamp (newest first)."""
    return sorted(reviews, key=lambda r: -r.get("timestamp", 0))


def sort_by_rating(reviews: list, descending: bool) -> list:
    """Sort reviews by rating."""
    return sorted(reviews, key=lambda r: r.get("rating", 0), reverse=descending)


def get_review_summary(reviews: list) -> dict:
    """Get review summary statistics."""
    ratings = [r.get("rating", 0) for r in reviews]
    return {
        "total_reviews": len(reviews),
        "average_rating": calculate_average_rating(ratings),
        "verified_count": len(filter_verified_reviews(reviews)),
        "with_text_count": len(filter_with_text(reviews))
    }


def format_rating_stars(rating: float, max_rating: int) -> str:
    """Format rating as star string."""
    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0
    empty = max_rating - full - half
    return "★" * full + "☆" * half + "☆" * empty


def can_review(user_id: str, item_id: str, existing_reviews: list) -> bool:
    """Check if user can review item."""
    for review in existing_reviews:
        if review.get("reviewer_id") == user_id and review.get("item_id") == item_id:
            return False
    return True


def get_user_reviews(reviews: list, user_id: str) -> list:
    """Get all reviews by user."""
    return [r for r in reviews if r.get("reviewer_id") == user_id]


def get_item_reviews(reviews: list, item_id: str) -> list:
    """Get all reviews for item."""
    return [r for r in reviews if r.get("item_id") == item_id]


def calculate_bayesian_average(item_rating: float, item_count: int, global_avg: float, min_votes: int) -> float:
    """Calculate Bayesian average rating."""
    return (min_votes * global_avg + item_count * item_rating) / (min_votes + item_count)


def needs_moderation(review: dict, min_length: int, flagged_words: list) -> bool:
    """Check if review needs moderation."""
    text = review.get("text", "").lower()
    if len(text) < min_length:
        return True
    for word in flagged_words:
        if word.lower() in text:
            return True
    return False
