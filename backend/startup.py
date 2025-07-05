#!/usr/bin/env python3
"""
Startup script for the backend application
Initializes database and runs setup tasks
"""

import asyncio
import logging
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.template_service import template_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def startup():
    """Run startup tasks"""
    logger.info("Starting application setup...")
    
    # Initialize database tables
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return
    
    # Migrate static templates to database
    logger.info("Migrating templates to database...")
    try:
        db = SessionLocal()
        template_service.migrate_static_templates_to_db(db, created_by="system")
        db.close()
        logger.info("Templates migrated successfully")
    except Exception as e:
        logger.error(f"Template migration failed: {e}")
    
    logger.info("Application setup completed!")

if __name__ == "__main__":
    startup()