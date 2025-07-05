"""
Template Service for Chrome Extensions
Manages extension templates from JSON files and database
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models.chrome_extension import ExtensionTemplate

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "chrome_extensions"
        self._cached_templates = {}
    
    def load_static_templates(self) -> Dict[str, Any]:
        """Load templates from static JSON files"""
        templates = {}
        
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return templates
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_id = template_file.stem
                    templates[template_id] = template_data
                    logger.info(f"Loaded template: {template_id}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        if not self._cached_templates:
            self._cached_templates = self.load_static_templates()
        
        return self._cached_templates.get(template_id)
    
    def get_all_templates(self) -> Dict[str, Any]:
        """Get all available templates"""
        if not self._cached_templates:
            self._cached_templates = self.load_static_templates()
        
        return self._cached_templates
    
    def get_templates_by_type(self, extension_type: str) -> Dict[str, Any]:
        """Get templates filtered by extension type"""
        all_templates = self.get_all_templates()
        filtered = {}
        
        for template_id, template_data in all_templates.items():
            if template_data.get("type") == extension_type:
                filtered[template_id] = template_data
        
        return filtered
    
    def save_template_to_db(
        self, 
        db: Session, 
        template_data: Dict[str, Any],
        created_by: str
    ) -> ExtensionTemplate:
        """Save a template to the database"""
        template = ExtensionTemplate(
            id=template_data.get("id") or template_data["name"].lower().replace(" ", "_"),
            name=template_data["name"],
            description=template_data.get("description", ""),
            extension_type=template_data["type"],
            complexity=template_data.get("complexity", "Medium"),
            estimated_time=template_data.get("estimated_time", "15-30 minutes"),
            permissions=template_data.get("permissions", []),
            manifest_template=template_data.get("manifest", {}),
            files_template=template_data.get("files", {}),
            features=template_data.get("features", []),
            use_cases=template_data.get("use_cases", []),
            examples=template_data.get("examples", []),
            install_instructions=template_data.get("install_instructions", []),
            created_by=created_by
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return template
    
    def migrate_static_templates_to_db(self, db: Session, created_by: str = "system"):
        """Migrate static JSON templates to database"""
        static_templates = self.load_static_templates()
        
        for template_id, template_data in static_templates.items():
            # Check if template already exists
            existing = db.query(ExtensionTemplate).filter(
                ExtensionTemplate.id == template_id
            ).first()
            
            if not existing:
                try:
                    template_data["id"] = template_id
                    self.save_template_to_db(db, template_data, created_by)
                    logger.info(f"Migrated template to database: {template_id}")
                except Exception as e:
                    logger.error(f"Failed to migrate template {template_id}: {e}")
    
    def get_db_templates(
        self, 
        db: Session, 
        extension_type: Optional[str] = None,
        is_public: Optional[bool] = True
    ) -> List[ExtensionTemplate]:
        """Get templates from database"""
        query = db.query(ExtensionTemplate)
        
        if extension_type:
            query = query.filter(ExtensionTemplate.extension_type == extension_type)
        
        if is_public is not None:
            query = query.filter(ExtensionTemplate.is_public == is_public)
        
        return query.all()

# Singleton instance
template_service = TemplateService()