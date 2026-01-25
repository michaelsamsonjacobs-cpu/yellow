"""
Topic Skew Analysis Service

Calculates the 'Bias Vairance' of an outlet across different topic categories.
This implements the "UN Resolution" factor: detecting when an outlet is neutral
on most topics but significantly biased on specific ones.
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from statistics import stdev, mean

from app.db.models import Article, Outlet
from app.scraper.taxonomy import TOPIC_CATEGORIES

class SkewCalculator:
    def __init__(self, db: Session):
        self.db = db

    def calculate_outlet_skew(self, outlet_id: str) -> Dict[str, Any]:
        """
        Calculate skew metrics for an outlet.
        Returns:
            - global_score: Average integrity score
            - category_scores: Dict of {category: score}
            - skew_penalty: Calculated penalty based on variance
            - high_skew_categories: List of categories with > 15pt deviation
        """
        # Get all articles with a category tag
        articles = (
            self.db.query(Article)
            .filter(
                Article.outlet_id == outlet_id,
                Article.category_tag.isnot(None),
                Article.score.isnot(None)
            )
            .all()
        )

        if not articles:
            return {
                "global_score": 0,
                "category_scores": {},
                "skew_penalty": 0,
                "high_skew_categories": []
            }

        # Calculate Global Average
        global_scores = [a.score for a in articles]
        global_avg = mean(global_scores)
        
        # Group by Category
        category_map = {}
        for a in articles:
            if a.category_tag not in category_map:
                category_map[a.category_tag] = []
            category_map[a.category_tag].append(a.score)
            
        # Calculate Category Averages
        category_stats = {}
        deviations = []
        high_skew_cats = []
        
        for cat, scores in category_map.items():
            # Only count categories with enough data (e.g., 3+ articles)
            if len(scores) < 3:
                continue
                
            cat_avg = mean(scores)
            deviation = abs(cat_avg - global_avg)
            
            category_stats[cat] = {
                "score": round(cat_avg, 1),
                "count": len(scores),
                "deviation": round(deviation, 1)
            }
            
            deviations.append(deviation)
            
            # Flag significant deviation (e.g. > 15 points)
            if deviation > 15:
                high_skew_cats.append({
                    "category": cat,
                    "deviation": round(deviation, 1),
                    "score": round(cat_avg, 1)
                })

        # Calculate Skew Penalty
        # If we have deviations, the penalty is a factor of the max deviation
        skew_penalty = 0
        if deviations:
            max_dev = max(deviations)
            # Penalty formula: 20% of the max deviation, capped at 15 points
            skew_penalty = min(round(max_dev * 0.4), 15)

        return {
            "global_score": round(global_avg, 1),
            "category_scores": category_stats,
            "skew_penalty": skew_penalty,
            "high_skew_categories": high_skew_cats
        }
