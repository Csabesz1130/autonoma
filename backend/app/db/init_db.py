"""
Database initialization script
Creates all tables defined in models
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base_class import Base

# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.feedback import Feedback
from app.models.chrome_extension import (
    ChromeExtension,
    ChromeExtensionComponent,
    ExtensionTemplate,
    ExtensionGeneration
)

def init_db() -> None:
    """Initialize database by creating all tables"""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()