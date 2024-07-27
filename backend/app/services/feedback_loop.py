from typing import Dict
from app.models.feedback import Feedback
from sqlalchemy.orm import Session
from sqlalchemy import func

class FeedbackLoop:
    def __init__(self):
        self.model_weights = {
            "claude": 1.0,
            "gpt4": 1.0,
            "codex": 1.0
        }

    def update_weights(self, db: Session):
        # Calculate average rating for each model
        model_ratings = db.query(
            Feedback.model,
            func.avg(Feedback.rating).label('avg_rating')
        ).group_by(Feedback.model).all()

        # Update weights based on average ratings
        total_rating = sum(rating for _, rating in model_ratings)
        for model, avg_rating in model_ratings:
            self.model_weights[model] = avg_rating / total_rating

    def get_model_weight(self, model: str) -> float:
        return self.model_weights.get(model, 1.0)

feedback_loop = FeedbackLoop()

# Add this method to the TaskDistributor class
def update_model_weights(self, db: Session):
    feedback_loop.update_weights(db)

# Modify the _select_models method in TaskDistributor to use these weights
def _select_models(self, preprocessed_input: List[str]) -> List[str]:
    model_scores = {model: 0 for model in self.models.keys()}
    for word in preprocessed_input:
        for model, info in self.models.items():
            if word in info["strengths"]:
                model_scores[model] += 1 * feedback_loop.get_model_weight(model)
    
    selected_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    return [model for model, _ in selected_models[:2]]