from pydantic import BaseModel

class TaskBase(BaseModel):
    description: str
    code_snippet: str | None = None

class TaskCreate(TaskBase):
    pass

class TaskInDBBase(TaskBase):
    id: int
    project_id: int
    result: str | None = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    pass