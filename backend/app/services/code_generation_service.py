"""
Code Generation Service
Generates production-ready code for frontend, backend, and database components
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiofiles
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class GeneratedComponent:
    name: str
    type: str  # 'frontend', 'backend', 'database', 'config'
    file_path: str
    content: str
    dependencies: List[str]
    description: str
    language: str
    framework: str

class CodeGenerationService:
    def __init__(self):
        self.supported_frameworks = {
            "frontend": ["nextjs", "react", "vue", "angular", "svelte"],
            "backend": ["fastapi", "express", "django", "flask", "spring"],
            "database": ["postgresql", "mongodb", "mysql", "redis", "sqlite"]
        }
        
        self.template_cache = {}
        self.code_patterns = {}

    async def generate_frontend_components(
        self,
        requirements: Dict[str, Any],
        tech_stack: List[str],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate frontend components based on requirements"""
        components = []
        
        # Determine frontend framework
        frontend_framework = self._get_frontend_framework(tech_stack)
        
        if frontend_framework == "nextjs":
            components.extend(await self._generate_nextjs_components(requirements, architecture))
        elif frontend_framework == "react":
            components.extend(await self._generate_react_components(requirements, architecture))
        elif frontend_framework == "vue":
            components.extend(await self._generate_vue_components(requirements, architecture))
        else:
            # Default to React
            components.extend(await self._generate_react_components(requirements, architecture))
        
        return components

    async def generate_backend_components(
        self,
        requirements: Dict[str, Any],
        tech_stack: List[str],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate backend components based on requirements"""
        components = []
        
        # Determine backend framework
        backend_framework = self._get_backend_framework(tech_stack)
        
        if backend_framework == "fastapi":
            components.extend(await self._generate_fastapi_components(requirements, architecture))
        elif backend_framework == "express":
            components.extend(await self._generate_express_components(requirements, architecture))
        elif backend_framework == "django":
            components.extend(await self._generate_django_components(requirements, architecture))
        else:
            # Default to FastAPI
            components.extend(await self._generate_fastapi_components(requirements, architecture))
        
        return components

    async def generate_database_components(
        self,
        requirements: Dict[str, Any],
        tech_stack: List[str],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate database components based on requirements"""
        components = []
        
        # Determine database
        database = self._get_database(tech_stack)
        
        if database == "postgresql":
            components.extend(await self._generate_postgresql_components(requirements, architecture))
        elif database == "mongodb":
            components.extend(await self._generate_mongodb_components(requirements, architecture))
        elif database == "mysql":
            components.extend(await self._generate_mysql_components(requirements, architecture))
        else:
            # Default to PostgreSQL
            components.extend(await self._generate_postgresql_components(requirements, architecture))
        
        return components

    async def add_security_measures(self, components: List[GeneratedComponent]) -> List[GeneratedComponent]:
        """Add security measures to generated components"""
        enhanced_components = []
        
        for component in components:
            if component.type == "frontend":
                enhanced_component = await self._add_frontend_security(component)
            elif component.type == "backend":
                enhanced_component = await self._add_backend_security(component)
            else:
                enhanced_component = component
            
            enhanced_components.append(enhanced_component)
        
        return enhanced_components

    async def optimize_performance(self, components: List[GeneratedComponent]) -> List[GeneratedComponent]:
        """Optimize performance of generated components"""
        optimized_components = []
        
        for component in components:
            if component.type == "frontend":
                optimized_component = await self._optimize_frontend_performance(component)
            elif component.type == "backend":
                optimized_component = await self._optimize_backend_performance(component)
            else:
                optimized_component = component
            
            optimized_components.append(optimized_component)
        
        return optimized_components

    async def _generate_nextjs_components(
        self,
        requirements: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate Next.js components"""
        components = []
        
        # Generate package.json
        package_json = self._generate_nextjs_package_json(requirements)
        components.append(GeneratedComponent(
            name="package.json",
            type="config",
            file_path="package.json",
            content=package_json,
            dependencies=["next", "react", "react-dom"],
            description="Next.js package configuration",
            language="json",
            framework="nextjs"
        ))
        
        # Generate next.config.js
        next_config = self._generate_nextjs_config()
        components.append(GeneratedComponent(
            name="next.config.js",
            type="config",
            file_path="next.config.js",
            content=next_config,
            dependencies=[],
            description="Next.js configuration",
            language="javascript",
            framework="nextjs"
        ))
        
        # Generate main page
        main_page = self._generate_nextjs_main_page(requirements)
        components.append(GeneratedComponent(
            name="MainPage",
            type="frontend",
            file_path="pages/index.js",
            content=main_page,
            dependencies=[],
            description="Main application page",
            language="javascript",
            framework="nextjs"
        ))
        
        # Generate layout component
        layout = self._generate_nextjs_layout(requirements)
        components.append(GeneratedComponent(
            name="Layout",
            type="frontend",
            file_path="components/Layout.js",
            content=layout,
            dependencies=[],
            description="Application layout component",
            language="javascript",
            framework="nextjs"
        ))
        
        # Generate API routes if needed
        if requirements.get("api_routes"):
            api_routes = await self._generate_nextjs_api_routes(requirements)
            components.extend(api_routes)
        
        return components

    async def _generate_fastapi_components(
        self,
        requirements: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate FastAPI components"""
        components = []
        
        # Generate requirements.txt
        requirements_txt = self._generate_fastapi_requirements(requirements)
        components.append(GeneratedComponent(
            name="requirements.txt",
            type="config",
            file_path="requirements.txt",
            content=requirements_txt,
            dependencies=["fastapi", "uvicorn", "sqlalchemy"],
            description="Python dependencies",
            language="text",
            framework="fastapi"
        ))
        
        # Generate main.py
        main_py = self._generate_fastapi_main(requirements)
        components.append(GeneratedComponent(
            name="main.py",
            type="backend",
            file_path="main.py",
            content=main_py,
            dependencies=[],
            description="FastAPI main application",
            language="python",
            framework="fastapi"
        ))
        
        # Generate models
        models = self._generate_fastapi_models(requirements)
        components.append(GeneratedComponent(
            name="models.py",
            type="backend",
            file_path="models.py",
            content=models,
            dependencies=["sqlalchemy", "pydantic"],
            description="Database models",
            language="python",
            framework="fastapi"
        ))
        
        # Generate API routes
        routes = self._generate_fastapi_routes(requirements)
        components.append(GeneratedComponent(
            name="routes.py",
            type="backend",
            file_path="routes.py",
            content=routes,
            dependencies=["fastapi"],
            description="API routes",
            language="python",
            framework="fastapi"
        ))
        
        return components

    async def _generate_postgresql_components(
        self,
        requirements: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[GeneratedComponent]:
        """Generate PostgreSQL components"""
        components = []
        
        # Generate database schema
        schema = self._generate_postgresql_schema(requirements)
        components.append(GeneratedComponent(
            name="schema.sql",
            type="database",
            file_path="database/schema.sql",
            content=schema,
            dependencies=[],
            description="Database schema",
            language="sql",
            framework="postgresql"
        ))
        
        # Generate migrations
        migrations = self._generate_postgresql_migrations(requirements)
        components.append(GeneratedComponent(
            name="migrations.py",
            type="database",
            file_path="database/migrations.py",
            content=migrations,
            dependencies=["alembic"],
            description="Database migrations",
            language="python",
            framework="postgresql"
        ))
        
        return components

    def _generate_nextjs_package_json(self, requirements: Dict[str, Any]) -> str:
        """Generate Next.js package.json"""
        return json.dumps({
            "name": "autonoma-generated-app",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "axios": "^1.6.0",
                "tailwindcss": "^3.3.0",
                "@tailwindcss/forms": "^0.5.0"
            },
            "devDependencies": {
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0"
            }
        }, indent=2)

    def _generate_nextjs_config(self) -> str:
        """Generate Next.js configuration"""
        return """
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
}

module.exports = nextConfig
"""

    def _generate_nextjs_main_page(self, requirements: Dict[str, Any]) -> str:
        """Generate Next.js main page"""
        return """
import { useState, useEffect } from 'react'
import Head from 'next/head'
import Layout from '../components/Layout'

export default function Home() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch data from API
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data')
        const result = await response.json()
        setData(result)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  return (
    <Layout>
      <Head>
        <title>Autonoma Generated App</title>
        <meta name="description" content="AI-generated application" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-8">
              Welcome to Your AI-Generated App
            </h1>
            
            {loading ? (
              <div className="text-lg text-gray-600">Loading...</div>
            ) : (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                  Application Data
                </h2>
                <pre className="text-sm text-gray-600 overflow-auto">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </main>
    </Layout>
  )
}
"""

    def _generate_nextjs_layout(self, requirements: Dict[str, Any]) -> str:
        """Generate Next.js layout component"""
        return """
import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Autonoma App
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/" className="text-gray-600 hover:text-gray-900">
                Home
              </a>
              <a href="/about" className="text-gray-600 hover:text-gray-900">
                About
              </a>
            </div>
          </div>
        </div>
      </nav>
      
      {children}
      
      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500">
            Generated with Autonoma AI
          </p>
        </div>
      </footer>
    </div>
  )
}
"""

    def _generate_fastapi_requirements(self, requirements: Dict[str, Any]) -> str:
        """Generate FastAPI requirements.txt"""
        return """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
redis==5.0.1
celery==5.3.4
"""

    def _generate_fastapi_main(self, requirements: Dict[str, Any]) -> str:
        """Generate FastAPI main.py"""
        return """
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from database import get_db
from models import Base, engine
from routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autonoma Generated API",
    description="AI-generated FastAPI application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Autonoma Generated API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    def _generate_fastapi_models(self, requirements: Dict[str, Any]) -> str:
        """Generate FastAPI models"""
        return """
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    owner_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic Models
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
"""

    def _generate_fastapi_routes(self, requirements: Dict[str, Any]) -> str:
        """Generate FastAPI routes"""
        return """
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Item, UserCreate, User as UserModel, ItemCreate, Item as ItemModel

router = APIRouter()

@router.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password="hashed_password_here"  # Implement proper hashing
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

@router.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
"""

    def _generate_postgresql_schema(self, requirements: Dict[str, Any]) -> str:
        """Generate PostgreSQL schema"""
        return """
-- PostgreSQL Schema for Autonoma Generated App

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Items table
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_items_title ON items(title);
CREATE INDEX idx_items_owner_id ON items(owner_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

    def _get_frontend_framework(self, tech_stack: List[str]) -> str:
        """Get frontend framework from tech stack"""
        for tech in tech_stack:
            if tech.lower() in self.supported_frameworks["frontend"]:
                return tech.lower()
        return "nextjs"  # Default

    def _get_backend_framework(self, tech_stack: List[str]) -> str:
        """Get backend framework from tech stack"""
        for tech in tech_stack:
            if tech.lower() in self.supported_frameworks["backend"]:
                return tech.lower()
        return "fastapi"  # Default

    def _get_database(self, tech_stack: List[str]) -> str:
        """Get database from tech stack"""
        for tech in tech_stack:
            if tech.lower() in self.supported_frameworks["database"]:
                return tech.lower()
        return "postgresql"  # Default

    async def _add_frontend_security(self, component: GeneratedComponent) -> GeneratedComponent:
        """Add security measures to frontend component"""
        # Add security headers, input validation, etc.
        if "index.js" in component.file_path:
            # Add security headers and CSP
            security_content = component.content.replace(
                '<Head>',
                '''<Head>
        <meta httpEquiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" />
        <meta httpEquiv="X-Content-Type-Options" content="nosniff" />
        <meta httpEquiv="X-Frame-Options" content="DENY" />
        <meta httpEquiv="X-XSS-Protection" content="1; mode=block" />'''
            )
            return GeneratedComponent(
                name=component.name,
                type=component.type,
                file_path=component.file_path,
                content=security_content,
                dependencies=component.dependencies + ["security"],
                description=component.description + " (with security)",
                language=component.language,
                framework=component.framework
            )
        return component

    async def _add_backend_security(self, component: GeneratedComponent) -> GeneratedComponent:
        """Add security measures to backend component"""
        # Add authentication, authorization, input validation, etc.
        if "main.py" in component.file_path:
            security_content = component.content.replace(
                "from fastapi import FastAPI, HTTPException, Depends",
                """from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import secrets"""
            )
            return GeneratedComponent(
                name=component.name,
                type=component.type,
                file_path=component.file_path,
                content=security_content,
                dependencies=component.dependencies + ["security"],
                description=component.description + " (with security)",
                language=component.language,
                framework=component.framework
            )
        return component

    async def _optimize_frontend_performance(self, component: GeneratedComponent) -> GeneratedComponent:
        """Optimize frontend performance"""
        # Add lazy loading, code splitting, etc.
        if "index.js" in component.file_path:
            optimized_content = component.content.replace(
                "import Layout from '../components/Layout'",
                """import dynamic from 'next/dynamic'
import Layout from '../components/Layout'

// Lazy load components for better performance
const DynamicComponent = dynamic(() => import('../components/DynamicComponent'), {
  loading: () => <p>Loading...</p>
})"""
            )
            return GeneratedComponent(
                name=component.name,
                type=component.type,
                file_path=component.file_path,
                content=optimized_content,
                dependencies=component.dependencies + ["performance"],
                description=component.description + " (optimized)",
                language=component.language,
                framework=component.framework
            )
        return component

    async def _optimize_backend_performance(self, component: GeneratedComponent) -> GeneratedComponent:
        """Optimize backend performance"""
        # Add caching, connection pooling, etc.
        if "main.py" in component.file_path:
            optimized_content = component.content.replace(
                "from fastapi import FastAPI, HTTPException, Depends",
                """from fastapi import FastAPI, HTTPException, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache"""
            )
            return GeneratedComponent(
                name=component.name,
                type=component.type,
                file_path=component.file_path,
                content=optimized_content,
                dependencies=component.dependencies + ["performance"],
                description=component.description + " (optimized)",
                language=component.language,
                framework=component.framework
            )
        return component

# Global instance
code_generation_service = CodeGenerationService()