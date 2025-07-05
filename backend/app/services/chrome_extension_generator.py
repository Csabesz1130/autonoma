"""
Chrome Extension Generator Service
Handles AI-powered Chrome extension creation with specialized agents
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import zipfile
import os
import tempfile
from pathlib import Path

from app.services.ai_orchestrator import AIOrchestrator
from app.services.code_generation_service import CodeGenerationService

logger = logging.getLogger(__name__)

@dataclass
class ChromeExtensionConfig:
    name: str
    version: str
    description: str
    extension_type: str  # 'popup', 'content_script', 'background', 'devtools', 'options'
    permissions: List[str]
    host_permissions: List[str]
    content_scripts: List[Dict[str, Any]]
    background_script: Optional[str]
    popup_html: Optional[str]
    options_page: Optional[str]
    devtools_page: Optional[str]
    icons: Dict[str, str]
    manifest_version: int = 3

@dataclass
class ChromeExtensionComponent:
    file_path: str
    content: str
    file_type: str  # 'manifest', 'html', 'css', 'javascript', 'icon'
    description: str

@dataclass
class GeneratedChromeExtension:
    id: str
    name: str
    description: str
    config: ChromeExtensionConfig
    components: List[ChromeExtensionComponent]
    created_at: datetime
    build_ready: bool = False
    zip_path: Optional[str] = None

class ChromeExtensionGenerator:
    def __init__(self):
        self.ai_orchestrator = AIOrchestrator()
        self.code_generation_service = CodeGenerationService()
        
        # Extension type templates
        self.extension_types = {
            'popup': {
                'name': 'Popup Extension',
                'description': 'Extension with popup interface',
                'required_files': ['manifest.json', 'popup.html', 'popup.js', 'popup.css'],
                'permissions': ['storage'],
                'manifest_keys': ['action']
            },
            'content_script': {
                'name': 'Content Script Extension',
                'description': 'Extension that modifies web pages',
                'required_files': ['manifest.json', 'content.js', 'content.css'],
                'permissions': ['activeTab'],
                'manifest_keys': ['content_scripts']
            },
            'background': {
                'name': 'Background Extension',
                'description': 'Extension with background processing',
                'required_files': ['manifest.json', 'background.js'],
                'permissions': ['background'],
                'manifest_keys': ['background']
            },
            'devtools': {
                'name': 'DevTools Extension',
                'description': 'Extension for developer tools',
                'required_files': ['manifest.json', 'devtools.html', 'devtools.js', 'panel.html', 'panel.js'],
                'permissions': ['devtools'],
                'manifest_keys': ['devtools_page']
            },
            'options': {
                'name': 'Options Extension',
                'description': 'Extension with options page',
                'required_files': ['manifest.json', 'options.html', 'options.js', 'options.css'],
                'permissions': ['storage'],
                'manifest_keys': ['options_page']
            }
        }
        
        # Common extension patterns
        self.extension_patterns = {
            'productivity': {
                'name': 'Productivity Tools',
                'examples': ['Task Manager', 'Note Taker', 'Timer', 'Calendar'],
                'permissions': ['storage', 'activeTab', 'notifications']
            },
            'social': {
                'name': 'Social Media Tools',
                'examples': ['Social Media Manager', 'Share Helper', 'Comment Analyzer'],
                'permissions': ['activeTab', 'storage', 'tabs']
            },
            'development': {
                'name': 'Developer Tools',
                'examples': ['Code Formatter', 'API Tester', 'CSS Inspector'],
                'permissions': ['activeTab', 'devtools', 'storage']
            },
            'accessibility': {
                'name': 'Accessibility Tools',
                'examples': ['Screen Reader Helper', 'Font Resizer', 'Color Adjuster'],
                'permissions': ['activeTab', 'storage', 'tabs']
            },
            'ecommerce': {
                'name': 'E-commerce Tools',
                'examples': ['Price Tracker', 'Coupon Finder', 'Product Comparer'],
                'permissions': ['activeTab', 'storage', 'webRequest']
            }
        }

    async def generate_chrome_extension(
        self,
        prompt: str,
        extension_type: str = "popup",
        user_id: str = "default"
    ) -> GeneratedChromeExtension:
        """Generate a complete Chrome extension based on user prompt"""
        
        logger.info(f"Starting Chrome extension generation for prompt: {prompt}")
        
        try:
            # 1. Analyze requirements
            requirements = await self._analyze_extension_requirements(prompt, extension_type)
            
            # 2. Generate extension configuration
            config = await self._generate_extension_config(requirements, extension_type)
            
            # 3. Generate all components
            components = await self._generate_extension_components(config, requirements)
            
            # 4. Create extension instance
            extension = GeneratedChromeExtension(
                id=f"ext_{int(datetime.now().timestamp())}",
                name=config.name,
                description=config.description,
                config=config,
                components=components,
                created_at=datetime.now()
            )
            
            # 5. Build extension package
            await self._build_extension_package(extension)
            
            logger.info(f"Chrome extension generation completed: {extension.id}")
            return extension
            
        except Exception as e:
            logger.error(f"Chrome extension generation failed: {e}")
            raise

    async def _analyze_extension_requirements(
        self, 
        prompt: str, 
        extension_type: str
    ) -> Dict[str, Any]:
        """Analyze user requirements for Chrome extension"""
        
        analysis_prompt = f"""
        Analyze this Chrome extension requirement and extract detailed information:
        
        User Request: {prompt}
        Extension Type: {extension_type}
        
        Extract and determine:
        1. Core functionality and features
        2. Required Chrome permissions
        3. Target websites/domains (if applicable)
        4. User interface requirements
        5. Data storage needs
        6. Background processing requirements
        7. Content script interactions
        8. API integrations needed
        9. Security considerations
        10. Performance requirements
        
        Return detailed JSON analysis with specific Chrome extension requirements.
        """
        
        try:
            response = await self.ai_orchestrator.call_ai_agent(
                agent_type="requirements_analyst",
                prompt=analysis_prompt,
                model="gpt-4-turbo-preview"
            )
            
            return json.loads(response["content"])
            
        except Exception as e:
            logger.error(f"Requirements analysis failed: {e}")
            # Return basic requirements as fallback
            return {
                "core_functionality": [prompt],
                "permissions": ["storage", "activeTab"],
                "target_websites": ["<all_urls>"],
                "ui_requirements": ["popup interface"],
                "storage_needs": ["basic settings"],
                "background_processing": False,
                "content_scripts": False,
                "api_integrations": [],
                "security_level": "basic",
                "performance_requirements": "standard"
            }

    async def _generate_extension_config(
        self,
        requirements: Dict[str, Any],
        extension_type: str
    ) -> ChromeExtensionConfig:
        """Generate Chrome extension configuration"""
        
        # Determine permissions based on requirements
        permissions = set(requirements.get("permissions", []))
        
        # Add permissions based on extension type
        if extension_type == "content_script":
            permissions.update(["activeTab", "scripting"])
        elif extension_type == "background":
            permissions.update(["background"])
        elif extension_type == "devtools":
            permissions.update(["devtools"])
        
        # Determine host permissions
        host_permissions = []
        if requirements.get("target_websites"):
            host_permissions = requirements["target_websites"]
        elif requirements.get("content_scripts"):
            host_permissions = ["<all_urls>"]
        
        # Generate extension name
        name = requirements.get("name", "Generated Extension")
        if not name.startswith("Generated"):
            name = f"AI Generated {name}"
        
        # Create configuration
        config = ChromeExtensionConfig(
            name=name,
            version="1.0.0",
            description=requirements.get("description", "AI-generated Chrome extension"),
            extension_type=extension_type,
            permissions=list(permissions),
            host_permissions=host_permissions,
            content_scripts=[],
            background_script=None,
            popup_html=None,
            options_page=None,
            devtools_page=None,
            icons={
                "16": "icons/icon16.png",
                "32": "icons/icon32.png",
                "48": "icons/icon48.png",
                "128": "icons/icon128.png"
            },
            manifest_version=3
        )
        
        # Configure based on extension type
        if extension_type == "popup":
            config.popup_html = "popup.html"
        elif extension_type == "content_script":
            config.content_scripts = [{
                "matches": host_permissions or ["<all_urls>"],
                "js": ["content.js"],
                "css": ["content.css"]
            }]
        elif extension_type == "background":
            config.background_script = "background.js"
        elif extension_type == "devtools":
            config.devtools_page = "devtools.html"
        elif extension_type == "options":
            config.options_page = "options.html"
        
        return config

    async def _generate_extension_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate all Chrome extension components"""
        
        components = []
        
        # Generate manifest.json
        manifest_component = await self._generate_manifest_json(config)
        components.append(manifest_component)
        
        # Generate components based on extension type
        if config.extension_type == "popup":
            components.extend(await self._generate_popup_components(config, requirements))
        elif config.extension_type == "content_script":
            components.extend(await self._generate_content_script_components(config, requirements))
        elif config.extension_type == "background":
            components.extend(await self._generate_background_components(config, requirements))
        elif config.extension_type == "devtools":
            components.extend(await self._generate_devtools_components(config, requirements))
        elif config.extension_type == "options":
            components.extend(await self._generate_options_components(config, requirements))
        
        # Generate common components
        components.extend(await self._generate_common_components(config, requirements))
        
        return components

    async def _generate_manifest_json(self, config: ChromeExtensionConfig) -> ChromeExtensionComponent:
        """Generate manifest.json file"""
        
        manifest = {
            "manifest_version": config.manifest_version,
            "name": config.name,
            "version": config.version,
            "description": config.description,
            "permissions": config.permissions,
            "icons": config.icons
        }
        
        # Add host permissions for Manifest V3
        if config.host_permissions:
            manifest["host_permissions"] = config.host_permissions
        
        # Add extension-specific configurations
        if config.popup_html:
            manifest["action"] = {
                "default_popup": config.popup_html,
                "default_title": config.name
            }
        
        if config.content_scripts:
            manifest["content_scripts"] = config.content_scripts
        
        if config.background_script:
            manifest["background"] = {
                "service_worker": config.background_script
            }
        
        if config.options_page:
            manifest["options_page"] = config.options_page
        
        if config.devtools_page:
            manifest["devtools_page"] = config.devtools_page
        
        return ChromeExtensionComponent(
            file_path="manifest.json",
            content=json.dumps(manifest, indent=2),
            file_type="manifest",
            description="Chrome extension manifest file"
        )

    async def _generate_popup_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate popup extension components"""
        
        components = []
        
        # Generate popup HTML
        popup_html_prompt = f"""
        Generate a modern HTML file for a Chrome extension popup with these requirements:
        
        Extension Name: {config.name}
        Description: {config.description}
        Features: {requirements.get('core_functionality', [])}
        
        Create a responsive popup interface (300px wide max) with:
        - Modern CSS styling
        - Interactive elements for the main features
        - Proper form handling
        - Accessibility features
        - Chrome extension best practices
        
        Return only the HTML content.
        """
        
        popup_html = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=popup_html_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="popup.html",
            content=popup_html["content"],
            file_type="html",
            description="Extension popup HTML interface"
        ))
        
        # Generate popup JavaScript
        popup_js_prompt = f"""
        Generate JavaScript code for a Chrome extension popup with these requirements:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        Permissions: {config.permissions}
        
        Create popup.js that handles:
        - DOM manipulation and event listeners
        - Chrome extension APIs (storage, tabs, etc.)
        - User interactions and form handling
        - Error handling and validation
        - Modern JavaScript (ES6+)
        - Chrome extension security policies
        
        Return only the JavaScript code.
        """
        
        popup_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=popup_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="popup.js",
            content=popup_js["content"],
            file_type="javascript",
            description="Extension popup JavaScript logic"
        ))
        
        # Generate popup CSS
        popup_css_prompt = f"""
        Generate modern CSS styles for a Chrome extension popup:
        
        Requirements:
        - Responsive design (max 300px width)
        - Modern, clean interface
        - Consistent with Chrome's design language
        - Accessibility features
        - Dark/light mode support
        - Smooth animations
        
        Return only the CSS code.
        """
        
        popup_css = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=popup_css_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="popup.css",
            content=popup_css["content"],
            file_type="css",
            description="Extension popup styles"
        ))
        
        return components

    async def _generate_content_script_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate content script extension components"""
        
        components = []
        
        # Generate content script JavaScript
        content_js_prompt = f"""
        Generate a content script for a Chrome extension with these requirements:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        Target Sites: {requirements.get('target_websites', ['<all_urls>'])}
        
        Create content.js that:
        - Safely modifies web page content
        - Handles DOM manipulation
        - Communicates with extension background/popup
        - Follows Chrome extension security policies
        - Avoids conflicts with existing page scripts
        - Includes error handling and cleanup
        
        Return only the JavaScript code.
        """
        
        content_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=content_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="content.js",
            content=content_js["content"],
            file_type="javascript",
            description="Content script for web page interaction"
        ))
        
        # Generate content script CSS
        content_css_prompt = f"""
        Generate CSS styles for a Chrome extension content script:
        
        Requirements:
        - Styles that integrate well with existing websites
        - High specificity to avoid conflicts
        - Modern, unobtrusive design
        - Responsive design
        - Accessibility features
        
        Return only the CSS code.
        """
        
        content_css = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=content_css_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="content.css",
            content=content_css["content"],
            file_type="css",
            description="Content script styles"
        ))
        
        return components

    async def _generate_background_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate background script extension components"""
        
        # Generate background service worker
        background_js_prompt = f"""
        Generate a background service worker (Manifest V3) for a Chrome extension:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        Permissions: {config.permissions}
        
        Create background.js that handles:
        - Extension lifecycle events
        - Message passing between components
        - Background processing and tasks
        - Chrome API interactions
        - Event listeners and handlers
        - Storage management
        - Error handling
        
        Return only the JavaScript code.
        """
        
        background_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="backend_generator",
            prompt=background_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        return [ChromeExtensionComponent(
            file_path="background.js",
            content=background_js["content"],
            file_type="javascript",
            description="Background service worker"
        )]

    async def _generate_devtools_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate DevTools extension components"""
        
        components = []
        
        # Generate devtools.html
        devtools_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DevTools Extension</title>
</head>
<body>
    <script src="devtools.js"></script>
</body>
</html>"""
        
        components.append(ChromeExtensionComponent(
            file_path="devtools.html",
            content=devtools_html,
            file_type="html",
            description="DevTools page entry point"
        ))
        
        # Generate devtools.js
        devtools_js_prompt = f"""
        Generate DevTools JavaScript for a Chrome extension:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        
        Create devtools.js that:
        - Creates DevTools panels
        - Handles DevTools API interactions
        - Manages panel lifecycle
        - Communicates with content scripts
        
        Return only the JavaScript code.
        """
        
        devtools_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=devtools_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="devtools.js",
            content=devtools_js["content"],
            file_type="javascript",
            description="DevTools panel creation and management"
        ))
        
        # Generate panel.html
        panel_html_prompt = f"""
        Generate a panel HTML for a Chrome DevTools extension:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        
        Create a DevTools panel interface with:
        - Modern UI design
        - Data visualization components
        - Interactive controls
        - Debugging information display
        
        Return only the HTML content.
        """
        
        panel_html = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=panel_html_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="panel.html",
            content=panel_html["content"],
            file_type="html",
            description="DevTools panel interface"
        ))
        
        # Generate panel.js
        panel_js_prompt = f"""
        Generate JavaScript for a Chrome DevTools panel:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        
        Create panel.js that:
        - Handles panel interactions
        - Communicates with inspected page
        - Manages panel data and state
        - Provides debugging functionality
        
        Return only the JavaScript code.
        """
        
        panel_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=panel_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="panel.js",
            content=panel_js["content"],
            file_type="javascript",
            description="DevTools panel JavaScript logic"
        ))
        
        return components

    async def _generate_options_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate options page extension components"""
        
        components = []
        
        # Generate options HTML
        options_html_prompt = f"""
        Generate an options page HTML for a Chrome extension:
        
        Extension: {config.name}
        Features: {requirements.get('core_functionality', [])}
        
        Create a modern options page with:
        - Settings and configuration options
        - Form validation and saving
        - Modern UI design
        - Accessibility features
        
        Return only the HTML content.
        """
        
        options_html = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=options_html_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="options.html",
            content=options_html["content"],
            file_type="html",
            description="Extension options page"
        ))
        
        # Generate options JavaScript and CSS
        options_js_prompt = f"""
        Generate JavaScript for Chrome extension options page:
        
        Features: {requirements.get('core_functionality', [])}
        
        Handle:
        - Settings storage and retrieval
        - Form validation and submission
        - Chrome storage API usage
        - User feedback and notifications
        
        Return only the JavaScript code.
        """
        
        options_js = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=options_js_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="options.js",
            content=options_js["content"],
            file_type="javascript",
            description="Options page JavaScript"
        ))
        
        # Generate options CSS
        options_css_prompt = f"""
        Generate CSS styles for a Chrome extension options page:
        
        Requirements:
        - Modern, clean design
        - Responsive layout
        - Form styling and validation states
        - Consistent with Chrome's design language
        - Accessibility features
        - Professional appearance
        
        Return only the CSS code.
        """
        
        options_css = await self.ai_orchestrator.call_ai_agent(
            agent_type="frontend_generator",
            prompt=options_css_prompt,
            model="gpt-4-turbo-preview"
        )
        
        components.append(ChromeExtensionComponent(
            file_path="options.css",
            content=options_css["content"],
            file_type="css",
            description="Options page styles"
        ))
        
        return components

    async def _generate_common_components(
        self,
        config: ChromeExtensionConfig,
        requirements: Dict[str, Any]
    ) -> List[ChromeExtensionComponent]:
        """Generate common extension components (icons, README, etc.)"""
        
        components = []
        
        # Generate README
        readme_content = f"""# {config.name}

{config.description}

## Features

{chr(10).join(f"- {feature}" for feature in requirements.get('core_functionality', []))}

## Installation

1. Download the extension files
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked" and select the extension folder

## Usage

{requirements.get('usage_instructions', 'Use the extension from the Chrome toolbar.')}

## Permissions

This extension requires the following permissions:
{chr(10).join(f"- {perm}" for perm in config.permissions)}

## Version

Version {config.version}

Generated by Autonoma AI Webapp Creator
"""
        
        components.append(ChromeExtensionComponent(
            file_path="README.md",
            content=readme_content,
            file_type="markdown",
            description="Extension documentation"
        ))
        
        return components

    async def _build_extension_package(self, extension: GeneratedChromeExtension) -> None:
        """Build the extension into a zip package"""
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                extension_dir = Path(temp_dir) / extension.name.replace(" ", "_")
                extension_dir.mkdir()
                
                # Create icons directory
                icons_dir = extension_dir / "icons"
                icons_dir.mkdir()
                
                # Write all components to files
                for component in extension.components:
                    file_path = extension_dir / component.file_path
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(component.content)
                
                # Generate placeholder icons (you can replace with actual icon generation)
                await self._generate_placeholder_icons(icons_dir)
                
                # Create zip package
                zip_path = f"generated_projects/{extension.id}.zip"
                os.makedirs(os.path.dirname(zip_path), exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(extension_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(extension_dir)
                            zipf.write(file_path, arcname)
                
                extension.zip_path = zip_path
                extension.build_ready = True
                
                logger.info(f"Extension package built: {zip_path}")
                
        except Exception as e:
            logger.error(f"Failed to build extension package: {e}")
            raise

    async def _generate_placeholder_icons(self, icons_dir: Path) -> None:
        """Generate placeholder icons for the extension"""
        
        try:
            # Try to generate simple colored squares as PNG placeholders
            # In production, you'd use PIL or an AI image generator
            from PIL import Image, ImageDraw, ImageFont
            
            icon_sizes = [16, 32, 48, 128]
            
            for size in icon_sizes:
                # Create a simple colored square with "AI" text
                img = Image.new('RGBA', (size, size), (66, 133, 244, 255))  # Chrome blue
                draw = ImageDraw.Draw(img)
                
                # Try to add text
                try:
                    font_size = max(8, size // 4)
                    draw.text((size//2, size//2), "AI", fill=(255, 255, 255, 255), 
                             anchor="mm", font_size=font_size)
                except:
                    # Fallback without font
                    pass
                
                icon_path = icons_dir / f"icon{size}.png"
                img.save(icon_path, 'PNG')
                
        except ImportError:
            # Fallback: create simple SVG files if PIL not available
            svg_template = """<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" fill="#4285f4"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-family="Arial" font-size="{font_size}">AI</text>
</svg>"""
            
            icon_sizes = [16, 32, 48, 128]
            
            for size in icon_sizes:
                font_size = size // 3
                svg_content = svg_template.format(size=size, font_size=font_size)
                
                # Save as SVG with PNG extension (browser will still display it)
                icon_path = icons_dir / f"icon{size}.png"
                with open(icon_path, 'w') as f:
                    f.write(svg_content)

    async def get_extension_templates(self) -> Dict[str, Any]:
        """Get available Chrome extension templates"""
        from app.services.template_service import template_service
        
        # Get static templates
        static_templates = template_service.get_all_templates()
        
        # Convert to popular extensions format
        popular_extensions = []
        for template_id, template_data in static_templates.items():
            popular_extensions.append({
                "id": template_id,
                "name": template_data.get("name", template_id),
                "description": template_data.get("description", ""),
                "type": template_data.get("type", "popup"),
                "permissions": template_data.get("permissions", []),
                "complexity": template_data.get("complexity", "Medium"),
                "estimated_time": template_data.get("estimated_time", "15-30 min"),
                "features": template_data.get("features", [])
            })
        
        return {
            "extension_types": self.extension_types,
            "extension_patterns": self.extension_patterns,
            "popular_extensions": popular_extensions,
            "static_templates": static_templates
        }

    async def analyze_extension_requirements(self, prompt: str) -> Dict[str, Any]:
        """Analyze and suggest optimal extension configuration"""
        
        analysis = await self._analyze_extension_requirements(prompt, "popup")
        
        # Add suggestions for extension type
        suggestions = []
        
        if "modify" in prompt.lower() or "change" in prompt.lower():
            suggestions.append({
                "type": "content_script",
                "reason": "Prompt suggests modifying web page content"
            })
        
        if "background" in prompt.lower() or "monitor" in prompt.lower():
            suggestions.append({
                "type": "background",
                "reason": "Prompt suggests background processing"
            })
        
        if "developer" in prompt.lower() or "debug" in prompt.lower():
            suggestions.append({
                "type": "devtools",
                "reason": "Prompt suggests developer tools functionality"
            })
        
        analysis["type_suggestions"] = suggestions
        return analysis

# Singleton instance
chrome_extension_generator = ChromeExtensionGenerator()