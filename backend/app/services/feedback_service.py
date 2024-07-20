from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate

class FeedbackService:
    @staticmethod
    async def create_feedback(db: Session, feedback: FeedbackCreate, user_id: int) -> Feedback:
        db_feedback = Feedback(
            task_id=feedback.task_id,
            user_id=user_id,
            rating=feedback.rating,
            comment=feedback.comment
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        return db_feedback

    @staticmethod
    def get_feedback_for_task(db: Session, task_id: int):
        return db.query(Feedback).filter(Feedback.task_id == task_id).all()

    @staticmethod
    async def process_feedback(db: Session, feedback: FeedbackCreate, user_id: int):
        db_feedback = await FeedbackService.create_feedback(db, feedback, user_id)
        # Here you can add logic to update the task distributor based on feedback
        # For example, adjusting model selection weights or updating a machine learning model
        return db_feedback

feedback_service = FeedbackService()