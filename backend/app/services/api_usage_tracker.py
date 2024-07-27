from datetime import datetime
from sqlalchemy.orm import Session
from app.models.api_usage import APIUsage

class APIUsageTracker:
    @staticmethod
    def log_usage(db: Session, model: str, tokens_used: int, cost: float):
        usage = APIUsage(
            model=model,
            timestamp=datetime.utcnow(),
            tokens_used=tokens_used,
            cost=cost
        )
        db.add(usage)
        db.commit()

    @staticmethod
    def get_usage_summary(db: Session, start_date: datetime, end_date: datetime):
        usage = db.query(APIUsage).filter(
            APIUsage.timestamp.between(start_date, end_date)
        ).all()

        summary = {}
        for entry in usage:
            if entry.model not in summary:
                summary[entry.model] = {"total_tokens": 0, "total_cost": 0}
            summary[entry.model]["total_tokens"] += entry.tokens_used
            summary[entry.model]["total_cost"] += entry.cost

        return summary

api_usage_tracker = APIUsageTracker()

# Add this to the _call_model method in TaskDistributor
response = await call_api_with_retry(session, model_info["api_url"], headers, data, model_info["name"])
tokens_used = response["usage"]["total_tokens"]
cost = calculate_cost(model, tokens_used)  # You'll need to implement this function
api_usage_tracker.log_usage(db, model, tokens_used, cost)
return response["choices"][0]["message"]["content"]