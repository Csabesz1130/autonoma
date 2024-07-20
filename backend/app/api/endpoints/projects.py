from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.schemas.task import TaskCreate
from app.services.project_service import project_service
from app.services.feedback_service import feedback_service
from app.core.security import oauth2_scheme

router = APIRouter()

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await project_service.create_project(db=db, project=project, user_id=current_user.id)

@router.get("/", response_model=List[Project])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = project_service.get_projects(db, skip=skip, limit=limit)
    return [project for project in projects if project.owner_id == current_user.id]

@router.get("/{project_id}", response_model=Project)
async def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project_service.update_project(db, project_id=project_id, project_update=project)

@router.delete("/{project_id}", response_model=bool)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_service.delete_project(db, project_id=project_id)

@router.post("/{project_id}/tasks/", response_model=dict)
async def process_task(
    project_id: int,
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Process task in the background
    background_tasks.add_task(project_service.process_task, db, project_id, task)
    
    return {"message": "Task processing started"}

@router.post("/{project_id}/feedback/", response_model=dict)
async def create_feedback(
    project_id: int,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None or db_project.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await feedback_service.process_feedback(db, feedback, current_user.id)
    return {"message": "Feedback received and processed"}