"""
PAB Client - The Project Agent Builder Python SDK

This module provides a client for interacting with the Project Agent Builder API.
It allows creation and management of AI agents, tools, and conversations.
"""

import os
import json
import time
import uuid
import asyncio
import httpx
from pathlib import Path
from enum import Enum, auto
from typing import Dict, List, Union, Optional, Any, Callable, Awaitable, TextIO, TypeVar, Generic
import logging
import sys
import inspect
from inspect import iscoroutinefunction
from functools import wraps
from datetime import datetime, timedelta
import tempfile
import base64

# Default cache file location
DEFAULT_CACHE_FILE = os.path.expanduser('~/.pab_sdk_cache')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('pab_sdk')

# Define enums
class MessageRole(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"

class OutputFormat(Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"

class ToolType(Enum):
    DOCUMENT = "documentTool"
    WEB_SEARCH = "webSearchTool"
    CODE_EXECUTION = "codeExecutionTool"
    CALCULATOR = "calculatorTool"
    HUMAN = "humanTool"
    JOULE_FUNCTION = "jouleFunctionTool"
    OPENAPI = "openApiTool"
    ODATA = "odataTool"
    HANA = "hanaTool"
    CUSTOM = "customTool"

class ResourceState(Enum):
    READY = "READY"
    CREATING = "CREATING"
    FAILED = "FAILED"

class ChatState(Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class ModelType(Enum):
    OPENAI_GPT4O = "gpt-4o"
    OPENAI_GPT4O_MINI = "gpt-4o-mini"
    VERTEXAI_GEMINI_PRO = "gemini-pro"

class AgentType(Enum):
    OPENAI = "openai"
    VERTEXAI = "vertexai"

# Main client class
class PABClient:
    """
    Project Agent Builder API Client
    
    This class provides methods to interact with the Project Agent Builder API,
    allowing for the creation and management of agents, tools, and conversations.
    """
    
    _cached_credentials_path = None
    
    @classmethod
    def _get_cached_credentials_path(cls) -> Optional[str]:
        """Get the cached credentials path if available"""
        if PABClient._cached_credentials_path:
            return PABClient._cached_credentials_path
        
        # Check for cache file
        if os.path.exists(DEFAULT_CACHE_FILE):
            try:
                with open(DEFAULT_CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('credentials_path')
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    @classmethod
    def _cache_credentials_path(cls, path: str) -> None:
        """Cache the credentials path for future use"""
        PABClient._cached_credentials_path = path
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(DEFAULT_CACHE_FILE), exist_ok=True)
            
            # Write to cache file
            with open(DEFAULT_CACHE_FILE, 'w') as f:
                json.dump({'credentials_path': path}, f)
        except (IOError, OSError) as e:
            logger.warning(f"Failed to write credentials path to cache: {e}")
    
    @classmethod
    def clear_cache(cls) -> bool:
        """
        Clear the cached credentials path
        
        Returns:
            bool: True if cache was cleared, False otherwise
        """
        PABClient._cached_credentials_path = None
        if os.path.exists(DEFAULT_CACHE_FILE):
            try:
                os.remove(DEFAULT_CACHE_FILE)
                return True
            except OSError as e:
                logger.error(f"Failed to remove cache file: {e}")
                return False
        return True
    
    def __init__(self, credentials_path: str = None, name: str = "PAB Client Wrapper"):
        """
        Initialize a new PAB Client
        
        Args:
            credentials_path (str, optional): Path to credentials JSON file
            name (str, optional): Name to identify this client instance
        
        The client will attempt to load credentials in the following order:
        1. From the provided credentials_path parameter
        2. From cached credentials path (if previously saved)
        3. From environment variables (PAB_CLIENT_ID, PAB_CLIENT_SECRET, etc.)
        4. By prompting the user interactively
        """
        self.name = name
        self.loop = asyncio.get_event_loop()
        
        # Initialize required attributes
        self._client_id = None
        self._client_secret = None
        self._token_url = None
        self._api_url = None
        self._token = None
        self._token_expiry = None
        self._client = None
        self._agent_id = None
        self._cached_tools = {}
        
        # Try to get credentials path from parameter or cache
        if credentials_path:
            PABClient._cached_credentials_path = credentials_path
        else:
            credentials_path = self._get_cached_credentials_path()
        
        # Try to load credentials from various sources
        if credentials_path:
            self._load_credentials_from_file(credentials_path)
        elif self._try_load_from_env():
            logger.info("Loaded credentials from environment variables")
        else:
            # Try interactive input if all else fails
            user_path = self._interactive_credentials_input()
            if user_path:
                PABClient._cached_credentials_path = user_path
                self._load_credentials_from_file(user_path)
            else:
                raise ValueError(
                    "No credentials provided. Please provide credentials by:\n"
                    "1. Passing a path to your credentials file:\n"
                    "   PABClient('/path/to/your/credentials.json')\n"
                    "2. Setting environment variables:\n"
                    "   PAB_CLIENT_ID, PAB_CLIENT_SECRET, PAB_AUTH_URL, PAB_API_BASE_URL\n"
                    "3. Responding to the interactive prompt when asked"
                )
        
        # Initialize other attributes
        self._chat_id = None
        self._clients = {}
        self._agent_configs = {}
        self._tools = {}
        
    def _load_credentials_from_file(self, credentials_path: str):
        """Load credentials from a JSON file
        
        Args:
            credentials_path: Path to the credentials JSON file
        """
        binding_file = Path(credentials_path)
        if not binding_file.exists():
            raise ValueError(f"Credentials file not found: {credentials_path}")
        
        try:
            with open(binding_file, 'r') as f:
                binding = json.load(f)
            
            # Extract credentials from binding
            if 'uaa' in binding and 'service_urls' in binding:
                self._client_id = binding['uaa']['clientid']
                self._client_secret = binding['uaa']['clientsecret']
                self._token_url = f"{binding['uaa']['url']}/oauth/token"
                self._api_url = binding['service_urls']['agent_api_url']
                logger.info(f"Successfully loaded credentials from {credentials_path}")
            else:
                raise ValueError(f"Invalid credentials file format. Missing 'uaa' or 'service_urls' fields.")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in credentials file: {credentials_path}")
        except Exception as e:
            raise ValueError(f"Error loading credentials from {credentials_path}: {str(e)}")
            
    def _try_load_from_env(self):
        """Load credentials from environment variables
        
        Returns:
            bool: True if successful, False otherwise
        """
        self._client_id = os.environ.get("PAB_CLIENT_ID")
        self._client_secret = os.environ.get("PAB_CLIENT_SECRET")
        self._token_url = os.environ.get("PAB_AUTH_URL")
        self._api_url = os.environ.get("PAB_API_BASE_URL")
        
        # Check if all required variables are set
        if all([self._client_id, self._client_secret, self._token_url, self._api_url]):
            return True
        return False
        
    def _interactive_credentials_input(self):
        """Prompt the user for credentials interactively
        
        Returns:
            str: Path to credentials file, or None if user cancels
        """
        print("\nNo credentials found. Please provide credentials for the PAB client:")
        print("\n1. Use the instructions here to get the credentials: https://wiki.one.int.sap/wiki/display/CONAIEXP/Setting+up+Project+Agent+Builder+in+BTP")
        print("2. Save the credentials as a JSON file")
        print("3. Enter the path to your credentials file below")
        print("\nCredentials file path (or 'cancel' to exit):")
        
        try:
            user_path = input("> ").strip()
            
            if user_path.lower() == 'cancel':
                return None
            
            if not user_path:
                raise ValueError("No path provided")
            
            # Handle path with quotes
            user_path = user_path.strip("'\"")
            
            if not os.path.exists(user_path):
                raise ValueError(f"File not found: {user_path}")
            
            return user_path
        except KeyboardInterrupt:
            return None
        except Exception as e:
            raise ValueError(f"Failed to load credentials: {str(e)}")
        
    def configure(self, client_id: str = None, client_secret: str = None, token_url: str = None, api_url: str = None):
        """Configure PAB API credentials
        
        Args:
            client_id: The client ID from service key
            client_secret: The client secret from service key
            token_url: The token URL from service key
            api_url: The API URL from service key
        """
        if client_id:
            self._client_id = client_id
        if client_secret:
            self._client_secret = client_secret
        if token_url:
            self._token_url = token_url
        if api_url:
            self._api_url = api_url
        
    async def _get_token(self) -> str:
        """Get an authentication token, refreshing if necessary
        
        Returns:
            The valid access token
        """
        if not self._token or time.time() > self._token_expiry * 0.9:
            await self._refresh_token()
        return self._token
        
    async def _refresh_token(self):
        """Refresh the authentication token"""
        if not self._client_id or not self._client_secret or not self._token_url:
            raise ValueError(
                "PAB API credentials not configured. Please do one of the following:\n"
                "1. Call configure() with your credentials, or\n"
                "2. Set the following environment variables: PAB_CLIENT_ID, PAB_CLIENT_SECRET, PAB_AUTH_URL, PAB_API_BASE_URL\n\n"
                "To obtain API credentials, visit the SAP Project Agent Builder setup documentation at:\n"
                "https://wiki.one.int.sap/wiki/pages/viewpage.action?spaceKey=CONAIEXP&title=Setting+up+Project+Agent+Builder+in+BTP"
            )
            
        form_data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._token_url,
                data=form_data,
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "accept": "application/json",
                }
            )
            response.raise_for_status()
            data = response.json()
            self._token = data["access_token"]
            self._token_expiry = time.time() + data["expires_in"]
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get an HTTP client with the authentication token
        
        Returns:
            An authenticated HTTP client
        """
        token = await self._get_token()
        client = httpx.AsyncClient(
            base_url=self._api_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=300  # 5 minutes
        )
        return client
    
    async def _find_existing_agent_by_name(self, name: str) -> Optional[str]:
        """Find an existing agent by name
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent ID if found, None otherwise
        """
        client = await self._get_client()
        try:
            response = await client.get("/api/v1/Agents")
            response.raise_for_status()
            agents = response.json().get("value", [])
            
            for agent in agents:
                if agent.get("name") == name:
                    return agent.get("ID")
                    
            return None
        except Exception as e:
            logger.warning(f"Warning: Failed to find existing agent: {e}")
            return None
            
    async def _update_agent(self, agent_id: str, config: dict):
        """Update an existing agent
        
        Args:
            agent_id: The agent ID
            config: The agent configuration
        """
        client = await self._get_client()
        try:
            # Only update the fields that are allowed to be updated
            update_data = {
                k: v for k, v in config.items() 
                if k in ["expertIn", "initialInstructions", "iterations", 
                        "baseModel", "advancedModel", "defaultOutputFormat", 
                        "defaultOutputFormatOptions", "preprocessingEnabled", 
                        "postprocessingEnabled"]
            }
            
            if update_data:
                response = await client.patch(f"/api/v1/Agents({agent_id})", json=update_data)
                response.raise_for_status()
                logger.info(f"Updated existing agent with ID: {agent_id}")
            else:
                logger.info(f"No updates needed for agent with ID: {agent_id}")
                
        except Exception as e:
            logger.warning(f"Warning: Failed to update agent: {e}")
    
    async def add_tool(self, name: str, tool_type: Union[ToolType, str], **kwargs) -> str:
        """Add a tool to the agent
        
        Args:
            name: The name of the tool
            tool_type: The type of tool (e.g., ToolType.DOCUMENT, ToolType.WEBSEARCH)
            **kwargs: Additional tool configuration options
            
        Returns:
            The tool ID
        """
        if not self._agent_id:
            raise ValueError("Agent not initialized")
            
        client = await self._get_client()
        response = await client.post(
            f"/api/v1/Agents({self._agent_id})/tools",
            json={
                "name": name,
                "type": tool_type.value if isinstance(tool_type, ToolType) else tool_type,
                **kwargs
            }
        )
        response.raise_for_status()
        tool_id = response.json()["ID"]
        self._tools[name] = tool_id
        
        # Wait for the tool to be ready
        await self._wait_for_tool_ready(tool_id)
        
        return tool_id
    
    async def add_document(self, doc_name: str, content: Union[str, bytes], 
                          content_type: str = "text/plain") -> str:
        """Add a document resource to a document tool
        
        Args:
            doc_name: The name of the document
            content: The document content as string or bytes
            content_type: The content type of the document
            
        Returns:
            The resource ID
        """
        if "document" not in self._tools:
            raise ValueError(f"Document tool not found")
            
        tool_id = self._tools["document"]
        client = await self._get_client()
        
        # Convert content to base64
        if isinstance(content, str):
            content = content.encode('utf-8')
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # Add document with retries
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Sending document to API (attempt {retry_count + 1})...")
                response = await client.post(
                    f"/api/v1/Agents({self._agent_id})/tools({tool_id})/resources",
                    json={
                        "name": doc_name,
                        "contentType": content_type,
                        "data": encoded_content
                    },
                    timeout=120.0  # Longer timeout for large documents
                )
                response.raise_for_status()
                resource_id = response.json()["ID"]
                
                # Wait for the resource to be ready
                logger.info(f"Document submitted, waiting for processing...")
                await self._wait_for_resource_ready(tool_id, resource_id)
                
                return resource_id
            except httpx.HTTPStatusError as e:
                retry_count += 1
                if e.response.status_code == 503 and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Server returned 503 error. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Error adding document: {e}")
                    logger.error(f"Status code: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error adding document: {str(e)}")
                raise
                
        raise RuntimeError("Failed to add document after maximum retries")
    
    async def _wait_for_resource_ready(self, tool_id: str, resource_id: str):
        """Wait for a resource to be ready
        
        Args:
            tool_id: The tool ID
            resource_id: The resource ID
        """
        client = await self._get_client()
        ready = False
        while not ready:
            resource_response = await client.get(
                f"/api/v1/Agents({self._agent_id})/tools({tool_id})/resources({resource_id})"
            )
            resource_response.raise_for_status()
            resource_data = resource_response.json()
            
            if resource_data.get("state") == "error":
                raise RuntimeError(f"Resource failed to load: {resource_data.get('lastError')}")
                
            ready = resource_data.get("state") == "ready"
            if not ready:
                await asyncio.sleep(3)
    
    async def _wait_for_tool_ready(self, tool_id: str):
        """Wait for a tool to be ready
        
        Args:
            tool_id: The tool ID
        """
        client = await self._get_client()
        ready = False
        while not ready:
            tool_response = await client.get(
                f"/api/v1/Agents({self._agent_id})/tools({tool_id})"
            )
            tool_response.raise_for_status()
            tool_data = tool_response.json()
            
            if tool_data.get("state") == "error":
                raise RuntimeError(f"Tool failed to load: {tool_data.get('lastError')}")
                
            ready = tool_data.get("state") == "ready"
            if not ready:
                await asyncio.sleep(3)
    
    async def _create_chat(self, agent_id):
        """Create a new chat with a unique name
        
        Args:
            agent_id: The agent ID
            
        Returns:
            The chat ID
        """
        client = await self._get_client()
        
        # Always create a new chat with a unique name
        unique_name = f"Chat Session {uuid.uuid4()}"
        
        try:
            response = await client.post(
                f"/api/v1/Agents({agent_id})/chats",
                json={"name": unique_name}
            )
            response.raise_for_status()
            chat_id = response.json()["ID"]
            logger.info(f"Created new chat with ID: {chat_id}")
            return chat_id
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            # Try again with an even more unique name
            more_unique_name = f"Chat {time.time()} {uuid.uuid4()}"
            response = await client.post(
                f"/api/v1/Agents({agent_id})/chats",
                json={"name": more_unique_name}
            )
            response.raise_for_status()
            chat_id = response.json()["ID"]
            logger.info(f"Created new chat on second attempt with ID: {chat_id}")
            return chat_id
    
    async def create_agent(
        self, 
        initial_instructions: str = "",
        expert_in: str = "",
        name: str = None,
        agent_type: AgentType = AgentType.OPENAI,
        safety_check: bool = False,
        iterations: int = 20,
        base_model: ModelType = ModelType.OPENAI_GPT4O_MINI,
        advanced_model: ModelType = ModelType.OPENAI_GPT4O,
        default_output_format: OutputFormat = OutputFormat.MARKDOWN,
        default_output_format_options: str = "",
        preprocessing_enabled: bool = False,
        postprocessing_enabled: bool = False,
        orchestration_module_config: dict = None,
        chat_id: str = None
    ):
        """Create a PAB agent and return an interface
        
        Args:
            initial_instructions: Initial instructions for the agent (default: "")
            expert_in: The agent's area of expertise (maps to expertIn field)
            name: The name of the agent (defaults to self.name)
            agent_type: The type of agent (default: AgentType.OPENAI)
            safety_check: Whether to perform safety checks (default: False)
            iterations: Number of iterations for processing (default: 20)
            base_model: Base model for initial processing (default: ModelType.OPENAI_GPT4O_MINI)
            advanced_model: Advanced model for deeper processing (default: ModelType.OPENAI_GPT4O)
            default_output_format: Default output format (default: OutputFormat.MARKDOWN)
            default_output_format_options: Options for the output format (default: "")
            preprocessing_enabled: Whether preprocessing is enabled (default: False)
            postprocessing_enabled: Whether postprocessing is enabled (default: False)
            orchestration_module_config: Configuration for orchestration modules (default: None)
            chat_id: Optional chat ID to continue a previous conversation (default: None)
            
        Returns:
            AgentInterface: An interface for interacting with the agent
            
        Note:
            The agent ID is stored in the PABClient instance as self._agent_id
        """
        # Generate a unique agent name with UUID suffix to avoid conflicts
        unique_name = name or self.name
        unique_name = f"{unique_name}-{str(uuid.uuid4())[:8]}"
        
        agent_config = {
            "name": unique_name,
            "type": agent_type.value if isinstance(agent_type, AgentType) else agent_type,
            "expertIn": expert_in or "",
            "initialInstructions": initial_instructions,
            "safetyCheck": safety_check,
            "iterations": iterations,
            "baseModel": base_model.value if isinstance(base_model, ModelType) else base_model,
            "advancedModel": advanced_model.value if isinstance(advanced_model, ModelType) else advanced_model,
            "defaultOutputFormat": default_output_format.value if isinstance(default_output_format, OutputFormat) else default_output_format,
            "defaultOutputFormatOptions": default_output_format_options,
            "preprocessingEnabled": preprocessing_enabled,
            "postprocessingEnabled": postprocessing_enabled
        }
        
        if orchestration_module_config:
            agent_config["orchestrationModuleConfig"] = orchestration_module_config
        
        # Create client for this agent
        client = await self._get_client()
        
        # Check if an agent with this name already exists
        existing_agent_id = await self._find_existing_agent_by_name(unique_name)
        if existing_agent_id:
            logger.info(f"Found existing agent with name '{unique_name}' (ID: {existing_agent_id})")
            # Update the existing agent instead of deleting it
            await self._update_agent(existing_agent_id, agent_config)
            self._agent_id = existing_agent_id
        else:
            # Create a new agent
            try:
                response = await client.post("/api/v1/Agents", json=agent_config)
                response.raise_for_status()
                self._agent_id = response.json()["ID"]
                logger.info(f"Created new agent with ID: {self._agent_id}")
            except Exception as e:
                logger.error(f"Error creating agent: {e}")
                # Try one more time after a delay
                await asyncio.sleep(5)
                response = await client.post("/api/v1/Agents", json=agent_config)
                response.raise_for_status()
                self._agent_id = response.json()["ID"]
                logger.info(f"Created new agent on second attempt with ID: {self._agent_id}")
        
        # Wait for the agent to be ready
        await self._wait_for_agent_ready(self._agent_id)
        
        # Create agent interface with optional chat ID
        agent_interface = AgentInterface(self, client, chat_id)
        # Initialize the interface (creates a new chat if chat_id is None)
        await agent_interface.initialize()
        
        return agent_interface
        
    async def get_interface(self, chat_id: str = None):
        """Create a chat session and return an agent interface without requiring a context manager
        
        Args:
            chat_id: Optional chat ID to continue a previous conversation (default: None)
            
        Returns:
            AgentInterface: An interface for interacting with the agent
        """
        if not self._agent_id:
            raise ValueError("Agent not initialized. Call create_agent() first.")
            
        client = await self._get_client()
        
        # Create agent interface with optional chat ID
        agent_interface = AgentInterface(self, client, chat_id)
        # Initialize the interface (creates a new chat if chat_id is None)
        await agent_interface.initialize()
        
        return agent_interface
        
    async def run(self, chat_id: str = None):
        """Context manager for running the agent
        
        Args:
            chat_id: Optional chat ID to continue a previous conversation (default: None)
            
        Returns:
            AgentRunContext: Context manager for running the agent
        """
        client = await self._get_client()
        
        class AgentRunContext:
            def __init__(self, pab_client, client, chat_id=None):
                self.pab_client = pab_client
                self.client = client
                self.chat_id = chat_id
                
            async def __aenter__(self):
                # Create and initialize interface with optional chat ID
                agent_interface = AgentInterface(self.pab_client, self.client, self.chat_id)
                await agent_interface.initialize()
                return agent_interface
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.client.aclose()
                
        return AgentRunContext(self, client, chat_id)

    async def get_agent(self, agent_id: str, chat_id: str = None):
        """Get an interface for an existing agent by ID
        
        Args:
            agent_id: The ID of an existing agent
            chat_id: Optional chat ID to continue a previous conversation (default: None)
            
        Returns:
            AgentInterface: An interface for interacting with the agent
        """
        if not agent_id:
            raise ValueError("Agent ID cannot be empty")
            
        # Set up the agent
        self._agent_id = agent_id
        
        # Get a client
        client = await self._get_client()
        
        # Verify the agent exists
        try:
            agent_response = await client.get(f"/api/v1/Agents({agent_id})")
            agent_response.raise_for_status()
            agent_data = agent_response.json()
            logger.info(f"Found existing agent: {agent_data.get('name', 'Unnamed')}")
            
            # Check if the agent is ready
            if agent_data.get("state") == "error":
                raise RuntimeError(f"Agent is in error state: {agent_data.get('lastError')}")
                
            if agent_data.get("state") != "ready" and "state" in agent_data:
                logger.info("Agent is not in ready state. Waiting...")
                await self._wait_for_agent_ready(agent_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Agent with ID {agent_id} not found")
            else:
                raise
        
        # Create agent interface with optional chat ID
        agent_interface = AgentInterface(self, client, chat_id)
        # Initialize the interface (creates a new chat if chat_id is None)
        await agent_interface.initialize()
        
        return agent_interface
        
    async def _wait_for_agent_ready(self, agent_id: str):
        """Wait for an agent to be in ready state
        
        Args:
            agent_id: The agent ID to check
        """
        client = await self._get_client()
        ready = False
        
        while not ready:
            agent_response = await client.get(f"/api/v1/Agents({agent_id})")
            agent_response.raise_for_status()
            agent_data = agent_response.json()
            
            if agent_data.get("state") == "error":
                raise RuntimeError(f"Agent failed to initialize: {agent_data.get('lastError')}")
                
            ready = agent_data.get("state") == "ready" or "state" not in agent_data
            if not ready:
                await asyncio.sleep(3)
                
        logger.info("Agent is now ready")


class AgentInterface:
    """Interface for interacting with a PAB Agent"""
    
    def __init__(self, pab_client: PABClient, client: httpx.AsyncClient, chat_id: str = None):
        """Initialize the agent interface
        
        Args:
            pab_client: The parent PAB Client
            client: The HTTP client
            chat_id: Optional chat ID to continue a previous conversation. If None, a new chat will be created.
        """
        self.pab_client = pab_client
        self.client = client
        self.chat_id = chat_id
        
    async def initialize(self):
        """Initialize the interface by setting up the chat
        
        If a chat_id was provided at construction, it will be used.
        Otherwise, a new chat will be created.
        
        Returns:
            self: The initialized interface
        """
        # If no chat ID was provided, create a new chat
        if not self.chat_id:
            self.pab_client._chat_id = await self.pab_client._create_chat(self.pab_client._agent_id)
        else:
            # Use the provided chat ID
            self.pab_client._chat_id = self.chat_id
            # Verify that the chat exists
            try:
                chat_response = await self.client.get(
                    f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.chat_id})"
                )
                chat_response.raise_for_status()
                logger.info(f"Using existing chat with ID: {self.chat_id}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    logger.info(f"Chat with ID {self.chat_id} not found. Creating a new chat.")
                    self.pab_client._chat_id = await self.pab_client._create_chat(self.pab_client._agent_id)
                else:
                    raise
        return self
        
    async def send_message(self, message: str, output_format: OutputFormat = OutputFormat.MARKDOWN, 
                     output_format_options: str = None) -> str:
        """Send a message to the agent (same functionality as __call__)
        
        Args:
            message: The message to send
            output_format: The output format (OutputFormat.MARKDOWN, OutputFormat.TEXT, or OutputFormat.JSON)
            output_format_options: Additional format options
            
        Returns:
            The agent's response
        """
        return await self(message, output_format, output_format_options)
            
    async def __call__(self, message: str, output_format: OutputFormat = OutputFormat.MARKDOWN, 
                     output_format_options: str = None) -> str:
        """Send a message to the agent
        
        Args:
            message: The message to send
            output_format: The output format (OutputFormat.MARKDOWN, OutputFormat.TEXT, or OutputFormat.JSON)
            output_format_options: Additional format options
            
        Returns:
            The agent's response
        """
        if not self.pab_client._agent_id or not self.pab_client._chat_id:
            raise ValueError("Agent or chat not initialized")
            
        # Send the message
        response = await self.client.post(
            f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})/UnifiedAiAgentService.sendMessage",
            json={
                "msg": message,
                "outputFormat": output_format.value if isinstance(output_format, OutputFormat) else output_format,
                "outputFormatOptions": output_format_options,
                "async": True
            }
        )
        response.raise_for_status()
        history_id = response.json()["historyId"]
        
        # Poll for the response
        while True:
            answers_response = await self.client.get(
                f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})/history?$filter=previous/ID eq {history_id}"
            )
            answers_response.raise_for_status()
            answers = answers_response.json().get("value", [])
            
            # No answer yet
            if not answers:
                # Check if chat is in error state
                chat_response = await self.client.get(
                    f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})?$select=state"
                )
                chat_response.raise_for_status()
                chat_data = chat_response.json()
                
                if chat_data.get("state") == "failed":
                    raise RuntimeError("Chat failed")
                    
                await asyncio.sleep(1)
                continue
                
            # Got an answer
            return answers[0]["content"]
            
    async def interactive(self):
        """Start an interactive chat session with the agent"""
        logger.info(f"Starting interactive chat with {self.pab_client.name}. Type 'exit' to quit.")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ("exit", "quit"):
                break
                
            try:
                response = await self(user_input)
                logger.info(f"\nAgent: {response}")
            except Exception as e:
                logger.error(f"\nError: {e}")
                
    async def continue_message(self, history_id: str, observation: str) -> str:
        """Continue a message that was interrupted by a tool
        
        Args:
            history_id: The history ID of the interrupted message
            observation: The observation to continue with
            
        Returns:
            The agent's response
        """
        if not self.pab_client._agent_id or not self.pab_client._chat_id:
            raise ValueError("Agent or chat not initialized")
            
        # Send the continuation
        response = await self.client.post(
            f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})/UnifiedAiAgentService.continueMessage",
            json={
                "observation": observation,
                "historyId": history_id,
                "async": True
            }
        )
        response.raise_for_status()
        
        # Poll for the response
        while True:
            answers_response = await self.client.get(
                f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})/history?$filter=previous/ID eq {history_id}"
            )
            answers_response.raise_for_status()
            answers = answers_response.json().get("value", [])
            
            # No answer yet
            if not answers:
                # Check if chat is in error state
                chat_response = await self.client.get(
                    f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})?$select=state"
                )
                chat_response.raise_for_status()
                chat_data = chat_response.json()
                
                if chat_data.get("state") == "failed":
                    raise RuntimeError("Chat failed")
                    
                await asyncio.sleep(1)
                continue
                
            # Got an answer
            return answers[0]["content"]
            
    async def cancel(self):
        """Cancel the current chat"""
        if not self.pab_client._agent_id or not self.pab_client._chat_id:
            raise ValueError("Agent or chat not initialized")
            
        response = await self.client.post(
            f"/api/v1/Agents({self.pab_client._agent_id})/chats({self.pab_client._chat_id})/UnifiedAiAgentService.cancel",
            json={}
        )
        response.raise_for_status()
        
    async def remove_document(self, doc_name: str) -> bool:
        """Remove a document from the agent by name
        
        Args:
            doc_name: The name of the document to remove
            
        Returns:
            True if document was removed, False if it wasn't found
        """
        tool_name = "document"
        if tool_name not in self.pab_client._tools:
            logger.info(f"Document tool not found.")
            return False
            
        tool_id = self.pab_client._tools[tool_name]
        
        # List all resources to find the document by name
        client = self.client
        response = await client.get(
            f"/api/v1/Agents({self.pab_client._agent_id})/tools({tool_id})/resources"
        )
        response.raise_for_status()
        resources = response.json().get("value", [])
        
        # Find the resource with matching name
        resource_id = None
        for resource in resources:
            if resource.get("name") == doc_name:
                resource_id = resource.get("ID")
                break
                
        if not resource_id:
            logger.info(f"Document '{doc_name}' not found.")
            return False
            
        # Delete the document
        delete_response = await client.delete(
            f"/api/v1/Agents({self.pab_client._agent_id})/tools({tool_id})/resources({resource_id})"
        )
        delete_response.raise_for_status()
        logger.info(f"Removed document '{doc_name}' (ID: {resource_id}).")
        return True
        
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the document tool
        
        Returns:
            List of documents with their details
        """
        tool_name = "document"
        if tool_name not in self.pab_client._tools:
            logger.info(f"Document tool not found.")
            return []
            
        tool_id = self.pab_client._tools[tool_name]
        
        # List all resources
        client = self.client
        response = await client.get(
            f"/api/v1/Agents({self.pab_client._agent_id})/tools({tool_id})/resources"
        )
        response.raise_for_status()
        resources = response.json().get("value", [])
        
        return resources
        
    async def get_document_content(self, doc_name: str) -> Optional[str]:
        """Get the content of a document by name
        
        Args:
            doc_name: The name of the document
            
        Returns:
            The document content as a string, or None if not found
        """
        tool_name = "document"
        if tool_name not in self.pab_client._tools:
            logger.info(f"Document tool not found.")
            return None
            
        tool_id = self.pab_client._tools[tool_name]
        
        # List all resources to find the document by name
        client = self.client
        try:
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    response = await client.get(
                        f"/api/v1/Agents({self.pab_client._agent_id})/tools({tool_id})/resources",
                        timeout=30.0  # Increase timeout
                    )
                    response.raise_for_status()
                    break  # Success - exit the retry loop
                except httpx.HTTPStatusError as e:
                    retry_count += 1
                    if e.response.status_code == 503 and retry_count < max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        logger.info(f"Server returned 503 error. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise  # Re-raise if max retries or different error
            
            resources = response.json().get("value", [])
            
            # Find the resource with matching name
            resource_id = None
            for resource in resources:
                if resource.get("name") == doc_name:
                    resource_id = resource.get("ID")
                    break
                    
            if not resource_id:
                logger.info(f"Document '{doc_name}' not found.")
                return None
                
            # Get the document content with retry
            retry_count = 0
            while retry_count < max_retries:
                try:
                    logger.info(f"Fetching document content (attempt {retry_count + 1})...")
                    # Use standard endpoint instead of $value
                    content_response = await client.get(
                        f"/api/v1/Agents({self.pab_client._agent_id})/tools({tool_id})/resources({resource_id})",
                        timeout=60.0  # Longer timeout for content
                    )
                    content_response.raise_for_status()
                    
                    # Parse the JSON response and extract the data field
                    resource_data = content_response.json()
                    data = resource_data.get("data")
                    
                    if not data:
                        logger.info(f"No data field found in resource response.")
                        return None
                    
                    # Decode base64 data
                    try:
                        decoded_content = base64.b64decode(data).decode('utf-8')
                        return decoded_content
                    except Exception as e:
                        logger.error(f"Error decoding document content: {str(e)}")
                        return None
                except httpx.HTTPStatusError as e:
                    retry_count += 1
                    if e.response.status_code == 503 and retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        logger.info(f"Server returned 503 error. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Error fetching document content: {e}")
                        logger.error(f"Status code: {e.response.status_code}")
                        logger.error(f"Response body: {e.response.text}")
                        raise
        except Exception as e:
            logger.error(f"Error accessing document: {str(e)}")
            raise
            
        return None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools associated with the agent
        
        Returns:
            List of tools with their details (ID, name, state, type, etc.)
        """
        if not self.pab_client._agent_id:
            raise ValueError("Agent not initialized")
            
        # Get a client
        client = self.client
        
        try:
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    response = await client.get(
                        f"/api/v1/Agents({self.pab_client._agent_id})/tools",
                        timeout=30.0  # Reasonable timeout
                    )
                    response.raise_for_status()
                    break  # Success - exit the retry loop
                except httpx.HTTPStatusError as e:
                    retry_count += 1
                    if e.response.status_code == 503 and retry_count < max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        logger.info(f"Server returned 503 error. Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise  # Re-raise if max retries or different error
                        
            # Parse response and return tools list
            tools = response.json().get("value", [])
            
            # Update internal tools dictionary with IDs for later use
            for tool in tools:
                if "name" in tool and "ID" in tool:
                    self.pab_client._tools[tool["name"]] = tool["ID"]
                    
            return tools
        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}")
            raise

    async def get_tool_names(self) -> List[str]:
        """Get just the names of all tools associated with the agent
        
        Returns:
            List of tool names as strings
        """
        tools = await self.list_tools()
        return [tool.get("name") for tool in tools if "name" in tool]

    async def add_document(self, doc_name: str, content: Union[str, bytes], 
                        content_type: str = "text/plain") -> str:
        """Add a document to the agent
        
        If the agent doesn't already have a document tool,
        one will be created automatically.
        
        Args:
            doc_name: The name of the document
            content: The document content as string or bytes
            content_type: The content type of the document (default: "text/plain")
            
        Returns:
            The resource ID of the added document
        """
        max_retries = 3
        retry_count = 0
        
        # Check if the agent has the document tool
        if "document" not in self.pab_client._tools:
            # Create the document tool
            logger.info(f"Document tool not found. Creating it...")
            while retry_count < max_retries:
                try:
                    tool_id = await self.pab_client.add_tool(
                        name="document",
                        tool_type=ToolType.DOCUMENT
                    )
                    logger.info(f"Created document tool with ID: {tool_id}")
                    break
                except httpx.HTTPStatusError as e:
                    retry_count += 1
                    if e.response.status_code == 503 and retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        logger.info(f"Server returned 503 error. Retrying tool creation in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
        
        # Reset retry counter for document addition
        retry_count = 0
        
        # Add the document with retries
        while retry_count < max_retries:
            try:
                logger.info(f"Adding document (attempt {retry_count + 1})...")
                doc_id = await self.pab_client.add_document(
                    doc_name=doc_name,
                    content=content,
                    content_type=content_type
                )
                logger.info(f"Document added successfully with ID: {doc_id}")
                return doc_id
            except httpx.HTTPStatusError as e:
                retry_count += 1
                if e.response.status_code == 503 and retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Server returned 503 error. Retrying document addition in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Error adding document: {e}")
                    logger.error(f"Status code: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error adding document: {str(e)}")
                raise
        
        raise RuntimeError("Failed to add document after maximum retries") 