from pydantic import BaseModel
from typing import List

class ProjectBase(BaseModel):
    name: str
    description: str | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass

class ProjectWithTasks(ProjectInDBBase):
    tasks: List["Task"] = []