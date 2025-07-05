"""
Chrome Extension Generation API Endpoints
Handles AI-powered Chrome extension creation requests
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import asyncio
import logging
from datetime import datetime
import tempfile
import os
import uuid

from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.services.chrome_extension_generator import chrome_extension_generator
from app.schemas.user import User
from app.models.chrome_extension import (
    ChromeExtension, 
    ChromeExtensionComponent, 
    ExtensionGeneration
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for Chrome Extension API"""
    try:
        # Check if the chrome extension generator is available
        generator_status = chrome_extension_generator is not None
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "chrome-extension-api",
            "version": "1.0.0",
            "generator_available": generator_status,
            "endpoints": {
                "generate": "/api/chrome-extension/generate",
                "analyze": "/api/chrome-extension/analyze",
                "list": "/api/chrome-extension/list",
                "templates": "/api/chrome-extension/templates",
                "types": "/api/chrome-extension/types",
                "permissions": "/api/chrome-extension/permissions",
                "download": "/api/chrome-extension/download/{extension_id}",
                "preview": "/api/chrome-extension/preview/{extension_id}",
                "publish": "/api/chrome-extension/publish/{extension_id}"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "chrome-extension-api",
            "error": str(e)
        }

# Pydantic Models
class ChromeExtensionRequest(BaseModel):
    prompt: str = Field(..., description="Description of the Chrome extension to generate")
    extension_type: str = Field(default="popup", description="Type of extension (popup, content_script, background, devtools, options)")
    target_websites: Optional[List[str]] = Field(default=None, description="Target websites for content scripts")
    permissions: Optional[List[str]] = Field(default=None, description="Additional permissions required")
    include_options: bool = Field(default=False, description="Include options page")
    include_background: bool = Field(default=False, description="Include background script")

class ChromeExtensionResponse(BaseModel):
    extension_id: str
    name: str
    description: str
    extension_type: str
    status: str
    download_url: Optional[str] = None
    install_instructions: List[str]

class ExtensionAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="Extension description for analysis")

class ExtensionTemplateResponse(BaseModel):
    extension_types: Dict[str, Any]
    extension_patterns: Dict[str, Any]
    popular_extensions: List[Dict[str, Any]]

@router.post("/generate", response_model=ChromeExtensionResponse)
async def generate_chrome_extension(
    request: ChromeExtensionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a complete Chrome extension based on user prompt
    Uses AI agents specialized for browser extension development
    """
    try:
        logger.info(f"Starting Chrome extension generation for user {current_user.id}")
        
        # Create extension record in database
        extension_id = str(uuid.uuid4())
        
        # Create generation record for tracking
        generation = ExtensionGeneration(
            id=str(uuid.uuid4()),
            user_id=str(current_user.id),
            prompt=request.prompt,
            extension_type=request.extension_type,
            status="processing"
        )
        db.add(generation)
        db.commit()
        
        # Generate extension using AI agents
        extension = await chrome_extension_generator.generate_chrome_extension(
            prompt=request.prompt,
            extension_type=request.extension_type,
            user_id=str(current_user.id)
        )
        
        # Save extension to database
        db_extension = ChromeExtension(
            id=extension.id,
            name=extension.name,
            description=extension.description,
            extension_type=extension.config.extension_type,
            prompt=request.prompt,
            permissions=extension.config.permissions,
            host_permissions=extension.config.host_permissions,
            manifest_data=extension.config.__dict__,
            user_id=str(current_user.id),
            status="completed" if extension.build_ready else "generating",
            build_ready=extension.build_ready,
            zip_path=extension.zip_path
        )
        db.add(db_extension)
        
        # Save components to database
        for component in extension.components:
            db_component = ChromeExtensionComponent(
                extension_id=extension.id,
                file_path=component.file_path,
                content=component.content,
                file_type=component.file_type,
                description=component.description
            )
            db.add(db_component)
        
        # Update generation record
        generation.status = "completed"
        generation.extension_id = extension.id
        generation.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Prepare install instructions
        install_instructions = [
            "1. Download the extension ZIP file",
            "2. Extract the ZIP file to a folder",
            "3. Open Chrome and navigate to chrome://extensions/",
            "4. Enable 'Developer mode' in the top right",
            "5. Click 'Load unpacked' and select the extracted folder",
            "6. The extension will be installed and ready to use!"
        ]
        
        # Add specific instructions based on extension type
        if request.extension_type == "popup":
            install_instructions.append("7. Click the extension icon in the toolbar to use it")
        elif request.extension_type == "content_script":
            install_instructions.append("7. Visit any website to see the extension in action")
        elif request.extension_type == "devtools":
            install_instructions.append("7. Open DevTools (F12) to access the extension panel")
        
        return ChromeExtensionResponse(
            extension_id=extension.id,
            name=extension.name,
            description=extension.description,
            extension_type=extension.config.extension_type,
            status="completed" if extension.build_ready else "building",
            download_url=f"/api/chrome-extension/download/{extension.id}" if extension.build_ready else None,
            install_instructions=install_instructions
        )
        
    except Exception as e:
        logger.error(f"Chrome extension generation failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_extension_requirements(
    request: ExtensionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze extension requirements and suggest optimal configuration"""
    try:
        # Create generation record for tracking analysis
        generation = ExtensionGeneration(
            id=str(uuid.uuid4()),
            user_id=str(current_user.id),
            prompt=request.prompt,
            status="analyzing"
        )
        db.add(generation)
        db.commit()
        
        analysis = await chrome_extension_generator.analyze_extension_requirements(request.prompt)
        
        # Update generation record with analysis
        generation.analysis_data = analysis
        generation.status = "analyzed"
        generation.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "analysis": analysis,
            "recommendations": {
                "suggested_type": analysis.get("type_suggestions", []),
                "required_permissions": analysis.get("permissions", []),
                "complexity_score": _calculate_complexity_score(analysis),
                "estimated_development_time": _estimate_development_time(analysis)
            }
        }
        
    except Exception as e:
        logger.error(f"Extension analysis failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_user_extensions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all extensions created by the current user"""
    try:
        extensions = db.query(ChromeExtension).filter(
            ChromeExtension.user_id == str(current_user.id)
        ).offset(skip).limit(limit).all()
        
        return {
            "extensions": [ext.to_dict() for ext in extensions],
            "total": db.query(ChromeExtension).filter(
                ChromeExtension.user_id == str(current_user.id)
            ).count()
        }
        
    except Exception as e:
        logger.error(f"Failed to list extensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=ExtensionTemplateResponse)
async def get_extension_templates(
    current_user: User = Depends(get_current_user)
):
    """Get available Chrome extension templates and examples"""
    try:
        templates = await chrome_extension_generator.get_extension_templates()
        return ExtensionTemplateResponse(**templates)
        
    except Exception as e:
        logger.error(f"Failed to get extension templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_extension_types(
    current_user: User = Depends(get_current_user)
):
    """Get supported Chrome extension types with descriptions"""
    return {
        "popup": {
            "name": "Popup Extension",
            "description": "Extension with a popup interface accessible from the browser toolbar",
            "use_cases": ["Quick actions", "Settings", "Mini-apps", "Status displays"],
            "complexity": "Simple",
            "examples": ["Password generator", "Unit converter", "Quick notes"]
        },
        "content_script": {
            "name": "Content Script Extension",
            "description": "Extension that modifies or enhances web pages",
            "use_cases": ["Page modification", "Data extraction", "UI enhancement", "Automation"],
            "complexity": "Medium",
            "examples": ["Ad blocker", "Page translator", "Social media enhancer"]
        },
        "background": {
            "name": "Background Extension",
            "description": "Extension with background processing capabilities",
            "use_cases": ["Monitoring", "Background tasks", "Event handling", "Data sync"],
            "complexity": "Advanced",
            "examples": ["System monitor", "Auto-backup", "Notification manager"]
        },
        "devtools": {
            "name": "DevTools Extension",
            "description": "Extension that adds panels to Chrome Developer Tools",
            "use_cases": ["Developer utilities", "Debugging tools", "Performance analysis"],
            "complexity": "Advanced",
            "examples": ["React DevTools", "Performance profiler", "API inspector"]
        },
        "options": {
            "name": "Options Extension",
            "description": "Extension with a dedicated options/settings page",
            "use_cases": ["Configuration", "Preferences", "Advanced settings"],
            "complexity": "Simple",
            "examples": ["Theme customizer", "Privacy settings", "Feature toggles"]
        }
    }

@router.get("/permissions")
async def get_chrome_permissions(
    current_user: User = Depends(get_current_user)
):
    """Get available Chrome extension permissions with descriptions"""
    return {
        "storage": {
            "description": "Store and retrieve data using Chrome's storage API",
            "required_for": ["Settings", "User data", "Preferences"]
        },
        "activeTab": {
            "description": "Access the currently active tab",
            "required_for": ["Current page modification", "Tab information"]
        },
        "tabs": {
            "description": "Access information about all tabs",
            "required_for": ["Tab management", "Multi-tab operations"]
        },
        "scripting": {
            "description": "Inject scripts into web pages",
            "required_for": ["Content script injection", "Page modification"]
        },
        "notifications": {
            "description": "Display system notifications",
            "required_for": ["User alerts", "Status updates"]
        },
        "alarms": {
            "description": "Schedule code to run at specific times",
            "required_for": ["Timers", "Scheduled tasks", "Reminders"]
        },
        "webRequest": {
            "description": "Monitor and modify network requests",
            "required_for": ["Request blocking", "Request modification"]
        },
        "cookies": {
            "description": "Access and modify cookies",
            "required_for": ["Cookie management", "Session handling"]
        },
        "history": {
            "description": "Access browsing history",
            "required_for": ["History analysis", "Visited sites"]
        },
        "bookmarks": {
            "description": "Access and modify bookmarks",
            "required_for": ["Bookmark management", "Quick access"]
        }
    }

@router.get("/download/{extension_id}")
async def download_extension(
    extension_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the generated Chrome extension as a ZIP file"""
    try:
        # Get extension from database
        extension = db.query(ChromeExtension).filter(
            ChromeExtension.id == extension_id,
            ChromeExtension.user_id == str(current_user.id)
        ).first()
        
        if not extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        if not extension.build_ready or not extension.zip_path:
            raise HTTPException(status_code=400, detail="Extension not ready for download")
        
        if not os.path.exists(extension.zip_path):
            raise HTTPException(status_code=404, detail="Extension file not found")
        
        return FileResponse(
            extension.zip_path,
            media_type="application/zip",
            filename=f"chrome_extension_{extension.name.replace(' ', '_')}.zip"
        )
        
    except Exception as e:
        logger.error(f"Extension download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{extension_id}")
async def preview_extension_code(
    extension_id: str,
    file_path: str = "manifest.json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview the code of a specific file in the generated extension"""
    try:
        # Get extension from database
        extension = db.query(ChromeExtension).filter(
            ChromeExtension.id == extension_id,
            ChromeExtension.user_id == str(current_user.id)
        ).first()
        
        if not extension:
            raise HTTPException(status_code=404, detail="Extension not found")
        
        # Get specific component
        component = db.query(ChromeExtensionComponent).filter(
            ChromeExtensionComponent.extension_id == extension_id,
            ChromeExtensionComponent.file_path == file_path
        ).first()
        
        if not component:
            raise HTTPException(status_code=404, detail=f"File {file_path} not found in extension")
        
        return {
            "file_path": component.file_path,
            "content": component.content,
            "file_type": component.file_type,
            "description": component.description,
            "extension_id": extension_id,
            "extension_name": extension.name
        }
        
    except Exception as e:
        logger.error(f"Extension preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish/{extension_id}")
async def publish_to_chrome_store(
    extension_id: str,
    current_user: User = Depends(get_current_user)
):
    """Help user publish extension to Chrome Web Store (guidance only)"""
    return {
        "message": "Publishing guidance provided",
        "steps": [
            {
                "step": 1,
                "title": "Prepare for Publishing",
                "description": "Ensure your extension follows Chrome Web Store policies",
                "actions": [
                    "Test extension thoroughly",
                    "Prepare high-quality screenshots",
                    "Write clear description",
                    "Create promotional images"
                ]
            },
            {
                "step": 2,
                "title": "Chrome Web Store Developer Account",
                "description": "Set up your developer account",
                "actions": [
                    "Visit Chrome Web Store Developer Dashboard",
                    "Pay one-time $5 registration fee",
                    "Verify your identity"
                ]
            },
            {
                "step": 3,
                "title": "Upload Extension",
                "description": "Upload your extension package",
                "actions": [
                    "Create ZIP file with your extension",
                    "Upload to Developer Dashboard",
                    "Fill out store listing details",
                    "Submit for review"
                ]
            },
            {
                "step": 4,
                "title": "Review Process",
                "description": "Wait for Chrome Web Store review",
                "actions": [
                    "Review typically takes 1-3 business days",
                    "Address any review feedback",
                    "Extension goes live after approval"
                ]
            }
        ],
        "resources": [
            {
                "title": "Chrome Web Store Developer Dashboard",
                "url": "https://chrome.google.com/webstore/devconsole"
            },
            {
                "title": "Chrome Web Store Policy",
                "url": "https://developer.chrome.com/docs/webstore/program-policies"
            },
            {
                "title": "Extension Publishing Guide",
                "url": "https://developer.chrome.com/docs/webstore/publish"
            }
        ]
    }

# Helper functions
def _calculate_complexity_score(analysis: Dict[str, Any]) -> str:
    """Calculate complexity score based on requirements"""
    features = len(analysis.get("core_functionality", []))
    permissions = len(analysis.get("permissions", []))
    api_integrations = len(analysis.get("api_integrations", []))
    
    score = features + permissions + api_integrations
    
    if score <= 3:
        return "Simple"
    elif score <= 6:
        return "Medium"
    else:
        return "Complex"

def _estimate_development_time(analysis: Dict[str, Any]) -> str:
    """Estimate development time based on complexity"""
    complexity = _calculate_complexity_score(analysis)
    
    if complexity == "Simple":
        return "5-15 minutes"
    elif complexity == "Medium":
        return "15-30 minutes"
    else:
        return "30-60 minutes"

def _get_file_type(file_path: str) -> str:
    """Get file type based on extension"""
    if file_path.endswith('.json'):
        return 'json'
    elif file_path.endswith('.js'):
        return 'javascript'
    elif file_path.endswith('.html'):
        return 'html'
    elif file_path.endswith('.css'):
        return 'css'
    elif file_path.endswith('.md'):
        return 'markdown'
    else:
        return 'text'