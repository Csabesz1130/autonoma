from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.task_distributor import task_distributor

class ProjectService:
    @staticmethod
    async def create_project(db: Session, project: ProjectCreate, user_id: int) -> Project:
        db_project = Project(
            name=project.name,
            description=project.description,
            owner_id=user_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(Project).offset(skip).limit(limit).all()

    @staticmethod
    async def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        db_project = ProjectService.get_project(db, project_id)
        if db_project:
            update_data = project_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_project, key, value)
            db.commit()
            db.refresh(db_project)
        return db_project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        db_project = ProjectService.get_project(db, project_id)
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False

    @staticmethod
    async def process_task(db: Session, project_id: int, task_create: TaskCreate) -> Dict:
        project = ProjectService.get_project(db, project_id)
        if not project:
            raise ValueError("Project not found")
        return await task_distributor.process_task(task_create, project)

project_service = ProjectService()