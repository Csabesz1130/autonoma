"""
Chrome Extension Database Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.db.base_class import Base

class ChromeExtension(Base):
    """Database model for generated Chrome extensions"""
    
    __tablename__ = "chrome_extensions"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    extension_type = Column(String(50), nullable=False)  # popup, content_script, background, etc.
    prompt = Column(Text, nullable=False)  # Original user prompt
    
    # Extension configuration
    permissions = Column(JSON)  # List of permissions
    host_permissions = Column(JSON)  # List of host permissions
    manifest_data = Column(JSON)  # Complete manifest.json data
    
    # Generation metadata
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default='generating')  # generating, completed, failed
    build_ready = Column(Boolean, default=False)
    zip_path = Column(String(500))  # Path to generated ZIP file
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="chrome_extensions")
    components = relationship("ChromeExtensionComponent", back_populates="extension", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "extension_type": self.extension_type,
            "status": self.status,
            "build_ready": self.build_ready,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class ChromeExtensionComponent(Base):
    """Database model for individual extension component files"""
    
    __tablename__ = "chrome_extension_components"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    extension_id = Column(String, ForeignKey('chrome_extensions.id'), nullable=False)
    file_path = Column(String(255), nullable=False)  # e.g., "popup.html", "manifest.json"
    content = Column(Text, nullable=False)  # File content
    file_type = Column(String(50), nullable=False)  # html, css, javascript, json, etc.
    description = Column(String(255))  # Human readable description
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    extension = relationship("ChromeExtension", back_populates="components")

class ExtensionTemplate(Base):
    """Database model for extension templates"""
    
    __tablename__ = "extension_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    extension_type = Column(String(50), nullable=False)
    complexity = Column(String(20))  # Simple, Medium, Advanced
    estimated_time = Column(String(50))  # e.g., "10-15 minutes"
    
    # Template configuration
    permissions = Column(JSON)  # Default permissions
    manifest_template = Column(JSON)  # Manifest template
    files_template = Column(JSON)  # File templates and structure
    
    # Features and metadata
    features = Column(JSON)  # List of features
    use_cases = Column(JSON)  # List of use cases
    examples = Column(JSON)  # List of example extensions
    install_instructions = Column(JSON)  # Installation steps
    
    # Publishing metadata
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)  # Average rating 1-5
    
    # Author information
    created_by = Column(String, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "extension_type": self.extension_type,
            "complexity": self.complexity,
            "estimated_time": self.estimated_time,
            "features": self.features,
            "use_cases": self.use_cases,
            "is_featured": self.is_featured,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class ExtensionGeneration(Base):
    """Database model for tracking extension generation requests"""
    
    __tablename__ = "extension_generations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    prompt = Column(Text, nullable=False)
    extension_type = Column(String(50))
    
    # Request metadata
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # AI analysis results
    analysis_data = Column(JSON)  # AI analysis of requirements
    recommendations = Column(JSON)  # AI recommendations
    
    # Result
    extension_id = Column(String, ForeignKey('chrome_extensions.id'))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    extension = relationship("ChromeExtension", foreign_keys=[extension_id])