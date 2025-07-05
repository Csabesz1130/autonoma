"""
MCP Server for Webapp Creator
Handles AI agent communication and orchestration for application generation
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

from mcp_server import MCPServer, Tool, Resource
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    id: str
    prompt: str
    tech_stack: List[str]
    project_type: str
    user_id: str
    timestamp: datetime
    status: str = "pending"
    
@dataclass
class GeneratedComponent:
    name: str
    type: str  # 'frontend', 'backend', 'database', 'config'
    code: str
    dependencies: List[str]
    description: str
    file_path: str

@dataclass
class GeneratedProject:
    id: str
    name: str
    description: str
    components: List[GeneratedComponent]
    tech_stack: List[str]
    deployment_config: Dict[str, Any]
    created_at: datetime

class WebappCreatorMCPServer(MCPServer):
    def __init__(self):
        super().__init__("webapp-creator", "1.0.0")
        
        # AI Clients
        self.openai_client = AsyncOpenAI()
        self.anthropic_client = AsyncAnthropic()
        
        # Vector DB for code examples and templates
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("code_templates")
        
        # Sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # In-memory storage (replace with Redis in production)
        self.active_requests: Dict[str, GenerationRequest] = {}
        self.generated_projects: Dict[str, GeneratedProject] = {}
        
        self._register_tools()
        self._register_resources()
        
    def _register_tools(self):
        """Register MCP tools for webapp generation"""
        
        @self.tool("generate_webapp")
        async def generate_webapp(
            prompt: str,
            tech_stack: Optional[List[str]] = None,
            project_type: str = "fullstack"
        ) -> Dict[str, Any]:
            """Generate a complete webapp based on user prompt"""
            request_id = str(uuid.uuid4())
            
            # TODO: Get actual user_id from auth context when MCP supports it
            # For now, use a default user or extract from headers
            user_id = "default"  # This should be replaced with actual auth
            
            request = GenerationRequest(
                id=request_id,
                prompt=prompt,
                tech_stack=tech_stack or ["nextjs", "fastapi", "postgresql"],
                project_type=project_type,
                user_id=user_id,
                timestamp=datetime.now()
            )
            
            self.active_requests[request_id] = request
            
            try:
                # Start async generation process
                asyncio.create_task(self._generate_webapp_async(request))
                
                return {
                    "request_id": request_id,
                    "status": "started",
                    "message": "Webapp generation started"
                }
            except Exception as e:
                logger.error(f"Failed to start webapp generation: {e}")
                return {
                    "request_id": request_id,
                    "status": "error",
                    "message": str(e)
                }
        
        @self.tool("get_generation_status")
        async def get_generation_status(request_id: str) -> Dict[str, Any]:
            """Get the status of a webapp generation request"""
            if request_id not in self.active_requests:
                return {"error": "Request not found"}
                
            request = self.active_requests[request_id]
            return {
                "request_id": request_id,
                "status": request.status,
                "prompt": request.prompt,
                "tech_stack": request.tech_stack,
                "timestamp": request.timestamp.isoformat()
            }
        
        @self.tool("analyze_tech_requirements")
        async def analyze_tech_requirements(prompt: str) -> Dict[str, Any]:
            """Analyze prompt and suggest optimal tech stack"""
            
            analysis_prompt = f"""
            Analyze this webapp requirement and suggest the optimal tech stack:
            
            Requirement: {prompt}
            
            Consider:
            - Frontend framework (React/Next.js, Vue, Angular, etc.)
            - Backend framework (FastAPI, Express, Django, etc.)
            - Database (PostgreSQL, MongoDB, Redis, etc.)
            - Authentication method
            - Deployment platform
            - Additional services needed
            
            Return a JSON with recommendations and reasoning.
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"Tech analysis failed: {e}")
                return {"error": str(e)}
        
        @self.tool("generate_component")
        async def generate_component(
            component_type: str,
            requirements: str,
            tech_stack: List[str]
        ) -> Dict[str, Any]:
            """Generate a specific component (frontend, backend, chrome_extension, etc.)"""
            
            try:
                if component_type == "frontend":
                    return await self._generate_frontend_component(requirements, tech_stack)
                elif component_type == "backend":
                    return await self._generate_backend_component(requirements, tech_stack)
                elif component_type == "database":
                    return await self._generate_database_schema(requirements, tech_stack)
                elif component_type == "chrome_extension":
                    return await self._generate_chrome_extension(requirements, tech_stack)
                else:
                    return {"error": f"Unknown component type: {component_type}"}
            except Exception as e:
                logger.error(f"Component generation failed: {e}")
                return {"error": str(e)}
        
        @self.tool("generate_chrome_extension")
        async def generate_chrome_extension(
            prompt: str,
            extension_type: str = "popup",
            permissions: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Generate a complete Chrome extension based on user prompt"""
            
            try:
                # Analyze extension requirements
                analysis_prompt = f"""
                Analyze this Chrome extension requirement and generate a complete extension:
                
                User Request: {prompt}
                Extension Type: {extension_type}
                Permissions: {permissions or []}
                
                Generate:
                1. Extension manifest.json (Manifest V3)
                2. Main extension files based on type
                3. Proper Chrome API usage
                4. Modern JavaScript/HTML/CSS
                5. Security best practices
                
                Return a detailed JSON structure with all files and configurations.
                """
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
                
            except Exception as e:
                logger.error(f"Chrome extension generation failed: {e}")
                return {"error": str(e)}
        
        @self.tool("analyze_extension_idea")
        async def analyze_extension_idea(prompt: str) -> Dict[str, Any]:
            """Analyze Chrome extension idea and suggest optimal configuration"""
            
            analysis_prompt = f"""
            Analyze this Chrome extension idea and provide recommendations:
            
            Extension Idea: {prompt}
            
            Analyze:
            1. Best extension type (popup, content_script, background, devtools, options)
            2. Required Chrome permissions
            3. Technical complexity (Simple/Medium/Complex)
            4. Development time estimate
            5. Chrome Web Store policy compliance
            6. Similar existing extensions
            7. Unique value proposition
            8. Target user personas
            
            Return detailed JSON analysis with actionable recommendations.
            """
            
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                
                return json.loads(response.content[0].text)
            except Exception as e:
                logger.error(f"Extension idea analysis failed: {e}")
                return {"error": str(e)}
    
    def _register_resources(self):
        """Register MCP resources for code templates and examples"""
        
        @self.resource("code_templates")
        async def get_code_templates(query: str = "") -> List[Dict[str, Any]]:
            """Get code templates based on query"""
            
            if not query:
                return [
                    {
                        "name": "Next.js App Router Setup",
                        "type": "frontend",
                        "framework": "nextjs",
                        "description": "Modern Next.js 14 setup with App Router"
                    },
                    {
                        "name": "FastAPI CRUD API",
                        "type": "backend", 
                        "framework": "fastapi",
                        "description": "RESTful API with CRUD operations"
                    }
                ]
            
            # Search templates using vector similarity
            query_embedding = self.embedding_model.encode([query])
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=5
            )
            
            return [
                {
                    "name": metadata["name"],
                    "type": metadata["type"],
                    "code": document,
                    "similarity": 1 - distance
                }
                for document, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )
            ]
    
    async def _generate_webapp_async(self, request: GenerationRequest):
        """Async webapp generation pipeline"""
        try:
            request.status = "analyzing"
            
            # 1. Analyze requirements and suggest tech stack
            tech_analysis = await self._analyze_requirements(request.prompt)
            
            request.status = "planning"
            
            # 2. Create project structure plan
            project_plan = await self._create_project_plan(
                request.prompt, 
                request.tech_stack,
                tech_analysis
            )
            
            request.status = "generating"
            
            # 3. Generate components in parallel
            components = await self._generate_all_components(project_plan)
            
            # 4. Create deployment configuration
            deployment_config = await self._create_deployment_config(
                request.tech_stack,
                components
            )
            
            # 5. Save generated project
            project = GeneratedProject(
                id=request.id,
                name=project_plan.get("name", "Generated App"),
                description=request.prompt,
                components=components,
                tech_stack=request.tech_stack,
                deployment_config=deployment_config,
                created_at=datetime.now()
            )
            
            self.generated_projects[request.id] = project
            request.status = "completed"
            
            logger.info(f"Webapp generation completed for request {request.id}")
            
        except Exception as e:
            logger.error(f"Webapp generation failed for request {request.id}: {e}")
            request.status = "failed"
    
    async def _analyze_requirements(self, prompt: str) -> Dict[str, Any]:
        """Analyze user requirements using AI"""
        
        analysis_prompt = f"""
        Analyze this webapp requirement and extract key information:
        
        User Request: {prompt}
        
        Extract:
        1. Core functionality needed
        2. User types and roles
        3. Data models required
        4. API endpoints needed
        5. UI/UX requirements
        6. Third-party integrations
        7. Performance requirements
        8. Security considerations
        
        Return detailed JSON analysis.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _create_project_plan(
        self, 
        prompt: str, 
        tech_stack: List[str],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create detailed project structure plan"""
        
        planning_prompt = f"""
        Based on this analysis, create a detailed project structure plan:
        
        Requirements Analysis: {json.dumps(analysis, indent=2)}
        Chosen Tech Stack: {tech_stack}
        
        Create a plan with:
        1. Project name and description
        2. Folder structure
        3. Component breakdown
        4. Database schema
        5. API design
        6. Frontend pages/components
        7. Integration points
        8. Deployment strategy
        
        Return detailed JSON plan.
        """
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": planning_prompt}]
        )
        
        return json.loads(response.content[0].text)
    
    async def _generate_all_components(self, plan: Dict[str, Any]) -> List[GeneratedComponent]:
        """Generate all project components in parallel"""
        
        tasks = []
        
        # Generate frontend components
        if "frontend" in plan:
            tasks.append(self._generate_frontend_components(plan["frontend"]))
        
        # Generate backend components  
        if "backend" in plan:
            tasks.append(self._generate_backend_components(plan["backend"]))
        
        # Generate database schema
        if "database" in plan:
            tasks.append(self._generate_database_components(plan["database"]))
        
        # Generate configuration files
        if "config" in plan:
            tasks.append(self._generate_config_components(plan["config"]))
        
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        components = []
        for result in results:
            if isinstance(result, list):
                components.extend(result)
            else:
                components.append(result)
        
        return components
    
    async def _generate_frontend_components(self, frontend_plan: Dict[str, Any]) -> List[GeneratedComponent]:
        """Generate frontend components"""
        components = []
        
        # Generate main app structure
        # Generate pages
        # Generate components
        # Generate styles
        # Generate utils
        
        # TODO: Implement detailed frontend generation
        # This would use AI to generate actual code files
        
        return components
    
    async def _generate_backend_components(self, backend_plan: Dict[str, Any]) -> List[GeneratedComponent]:
        """Generate backend components"""
        components = []
        
        # Generate API routes
        # Generate models
        # Generate services
        # Generate middleware
        # Generate tests
        
        # TODO: Implement detailed backend generation
        
        return components
    
    async def _generate_database_components(self, db_plan: Dict[str, Any]) -> List[GeneratedComponent]:
        """Generate database schema and migrations"""
        components = []
        
        # Generate schema
        # Generate migrations
        # Generate seed data
        
        # TODO: Implement database generation
        
        return components
    
    async def _generate_config_components(self, config_plan: Dict[str, Any]) -> List[GeneratedComponent]:
        """Generate configuration files"""
        components = []
        
        # Generate Docker files
        # Generate CI/CD configs
        # Generate environment configs
        # Generate package.json/requirements.txt
        
        # TODO: Implement config generation
        
        return components
    
    async def _create_deployment_config(
        self, 
        tech_stack: List[str],
        components: List[GeneratedComponent]
    ) -> Dict[str, Any]:
        """Create deployment configuration"""
        
        # Generate deployment configs for different platforms
        # Vercel, Netlify, Railway, AWS, etc.
        
        return {
            "platforms": {
                "vercel": {
                    "frontend_deploy": True,
                    "serverless_functions": True
                },
                "railway": {
                    "backend_deploy": True,
                    "database_hosting": True
                }
            }
        }

# Singleton instance
webapp_creator_server = WebappCreatorMCPServer()

async def start_mcp_server():
    """Start the MCP server"""
    await webapp_creator_server.start()
    logger.info("Webapp Creator MCP Server started")

if __name__ == "__main__":
    asyncio.run(start_mcp_server())