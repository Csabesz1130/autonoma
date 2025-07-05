"""
Webapp Generation API Endpoints
Handles AI-powered webapp creation requests and integrates with MCP servers
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import asyncio
import logging
from datetime import datetime

from app.core.deps import get_current_user
from app.mcp_servers.webapp_creator_server import webapp_creator_server
from app.services.ai_orchestrator import AIOrchestrator
from app.services.code_generation_service import CodeGenerationService
from app.services.deployment_service import DeploymentService
from app.schemas.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class WebappGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Description of the webapp to generate")
    tech_stack: Optional[List[str]] = Field(default=None, description="Preferred technology stack")
    project_type: str = Field(default="fullstack", description="Type of project to generate")
    deployment_platform: Optional[str] = Field(default="vercel", description="Preferred deployment platform")
    include_auth: bool = Field(default=True, description="Include authentication system")
    include_database: bool = Field(default=True, description="Include database integration")
    include_tests: bool = Field(default=True, description="Include test files")

class TechStackAnalysisRequest(BaseModel):
    prompt: str = Field(..., description="Project description for tech stack analysis")

class ComponentGenerationRequest(BaseModel):
    component_type: str = Field(..., description="Type of component to generate")
    requirements: str = Field(..., description="Component requirements")
    tech_stack: List[str] = Field(..., description="Technology stack to use")

class WebappGenerationResponse(BaseModel):
    request_id: str
    status: str
    message: str
    estimated_completion_time: Optional[int] = None

class GenerationStatusResponse(BaseModel):
    request_id: str
    status: str
    progress: int
    current_step: str
    components_generated: int
    total_components: int
    estimated_time_remaining: Optional[int] = None

class TechStackRecommendation(BaseModel):
    frontend: Dict[str, Any]
    backend: Dict[str, Any] 
    database: Dict[str, Any]
    deployment: Dict[str, Any]
    additional_services: List[Dict[str, Any]]
    reasoning: str

# AI Orchestrator for coordinating multiple AI agents
ai_orchestrator = AIOrchestrator()
code_generation_service = CodeGenerationService()
deployment_service = DeploymentService()

@router.post("/generate", response_model=WebappGenerationResponse)
async def generate_webapp(
    request: WebappGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a complete webapp based on user prompt
    Uses multiple AI agents to create a production-ready application
    """
    try:
        # Start MCP-based generation
        mcp_response = await webapp_creator_server.call_tool(
            "generate_webapp",
            {
                "prompt": request.prompt,
                "tech_stack": request.tech_stack,
                "project_type": request.project_type
            }
        )
        
        if mcp_response.get("status") == "error":
            raise HTTPException(status_code=500, detail=mcp_response.get("message"))
        
        request_id = mcp_response["request_id"]
        
        # Add background task for enhanced generation
        background_tasks.add_task(
            enhance_generation_with_ai_agents,
            request_id,
            request,
            current_user.id
        )
        
        return WebappGenerationResponse(
            request_id=request_id,
            status="started",
            message="Webapp generation started with AI agents",
            estimated_completion_time=300  # 5 minutes
        )
        
    except Exception as e:
        logger.error(f"Webapp generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{request_id}", response_model=GenerationStatusResponse)
async def get_generation_status(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the current status of a webapp generation request"""
    try:
        # Get status from MCP server
        mcp_status = await webapp_creator_server.call_tool(
            "get_generation_status",
            {"request_id": request_id}
        )
        
        if "error" in mcp_status:
            raise HTTPException(status_code=404, detail="Generation request not found")
        
        # Enhance with additional progress information
        enhanced_status = await ai_orchestrator.get_detailed_status(request_id)
        
        return GenerationStatusResponse(
            request_id=request_id,
            status=mcp_status["status"],
            progress=enhanced_status.get("progress", 0),
            current_step=enhanced_status.get("current_step", "Initializing"),
            components_generated=enhanced_status.get("components_generated", 0),
            total_components=enhanced_status.get("total_components", 0),
            estimated_time_remaining=enhanced_status.get("estimated_time_remaining")
        )
        
    except Exception as e:
        logger.error(f"Failed to get generation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{request_id}")
async def stream_generation_progress(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stream real-time generation progress using Server-Sent Events"""
    
    async def generate_progress_stream():
        """Generate SSE stream for real-time updates"""
        try:
            while True:
                status = await ai_orchestrator.get_detailed_status(request_id)
                
                if not status:
                    yield f"data: {json.dumps({'error': 'Request not found'})}\n\n"
                    break
                
                yield f"data: {json.dumps(status)}\n\n"
                
                if status.get("status") in ["completed", "failed"]:
                    break
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.post("/analyze-tech-stack", response_model=TechStackRecommendation)
async def analyze_tech_stack(
    request: TechStackAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze project requirements and recommend optimal tech stack"""
    try:
        # Use MCP server for analysis
        analysis = await webapp_creator_server.call_tool(
            "analyze_tech_requirements",
            {"prompt": request.prompt}
        )
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return TechStackRecommendation(**analysis)
        
    except Exception as e:
        logger.error(f"Tech stack analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-component")
async def generate_component(
    request: ComponentGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a specific component (frontend, backend, etc.)"""
    try:
        component = await webapp_creator_server.call_tool(
            "generate_component",
            {
                "component_type": request.component_type,
                "requirements": request.requirements,
                "tech_stack": request.tech_stack
            }
        )
        
        if "error" in component:
            raise HTTPException(status_code=500, detail=component["error"])
        
        return component
        
    except Exception as e:
        logger.error(f"Component generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_project_templates(
    query: str = "",
    current_user: User = Depends(get_current_user)
):
    """Get available project templates and code examples"""
    try:
        templates = await webapp_creator_server.call_resource(
            "code_templates",
            {"query": query}
        )
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deploy/{request_id}")
async def deploy_generated_webapp(
    request_id: str,
    platform: str = "vercel",
    current_user: User = Depends(get_current_user)
):
    """Deploy a generated webapp to the specified platform"""
    try:
        deployment_result = await deployment_service.deploy_webapp(
            request_id, 
            platform, 
            current_user.id
        )
        
        return deployment_result
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{request_id}")
async def download_generated_code(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download the generated webapp code as a ZIP file"""
    try:
        zip_file = await code_generation_service.create_download_package(
            request_id, 
            current_user.id
        )
        
        return StreamingResponse(
            zip_file,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=webapp-{request_id}.zip"}
        )
        
    except Exception as e:
        logger.error(f"Code download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def enhance_generation_with_ai_agents(
    request_id: str,
    request: WebappGenerationRequest,
    user_id: str
):
    """
    Background task to enhance webapp generation with additional AI agents
    Adds advanced features like testing, optimization, security analysis
    """
    try:
        # Initialize AI orchestrator for this request
        await ai_orchestrator.initialize_request(request_id, request, user_id)
        
        # Run parallel AI agent tasks
        tasks = [
            ai_orchestrator.enhance_with_security_agent(request_id),
            ai_orchestrator.enhance_with_performance_agent(request_id),
            ai_orchestrator.enhance_with_testing_agent(request_id),
            ai_orchestrator.enhance_with_ui_ux_agent(request_id)
        ]
        
        await asyncio.gather(*tasks)
        
        # Finalize generation
        await ai_orchestrator.finalize_generation(request_id)
        
    except Exception as e:
        logger.error(f"Enhanced generation failed for request {request_id}: {e}")
        await ai_orchestrator.mark_failed(request_id, str(e))