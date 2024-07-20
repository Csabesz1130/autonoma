from pydantic import BaseModel, Field

class FeedbackBase(BaseModel):
    rating: float = Field(..., ge=0, le=5)
    comment: str | None = None

class FeedbackCreate(FeedbackBase):
    task_id: int

class FeedbackInDBBase(FeedbackBase):
    id: int
    user_id: int
    task_id: int

    class Config:
        from_attributes = True

class Feedback(FeedbackInDBBase):
    pass