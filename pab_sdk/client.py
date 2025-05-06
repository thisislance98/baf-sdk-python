"""
Main client module for the BAF SDK.

This module contains the main client class that provides access to the
Project Agent Builder API.
"""

import json
import logging
import os
import time
from typing import List, Dict, Any, Optional, Union, Tuple
import base64

import requests
from dotenv import load_dotenv

from .auth import TokenManager, AuthenticationError
from .models import (
    Agent, Chat, Message, Tool, Resource,
    MessageRole, OutputFormat, ToolType, ResourceState, ChatState
)
from .exceptions import ApiError, ResourceNotReadyError, TimeoutError


logger = logging.getLogger(__name__)


class AgentBuilderClient:
    """
    Main client for the Project Agent Builder API.
    
    This class handles communication with the API and provides methods
    for creating and managing agents, chats, and messages.
    """
    
    def __init__(
        self,
        auth_url: Optional[str] = None,
        api_base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 60,
        dotenv_path: Optional[str] = None
    ):
        """
        Initialize the API client.
        
        If parameters are not provided, they will be loaded from environment variables:
        - BAF_AUTH_URL: The OAuth token endpoint URL
        - BAF_API_BASE_URL: The base URL for the Project Agent Builder API
        - BAF_CLIENT_ID: The client ID for authentication
        - BAF_CLIENT_SECRET: The client secret for authentication
        
        Args:
            auth_url: The OAuth token endpoint URL
            api_base_url: The base URL for the Project Agent Builder API
            client_id: The client ID for authentication
            client_secret: The client secret for authentication
            timeout: Default timeout for API requests (in seconds)
            dotenv_path: Optional path to .env file
        """
        # Load environment variables from .env file
        load_dotenv(dotenv_path=dotenv_path)
        
        # Use provided values or fall back to environment variables
        self.api_base_url = (api_base_url or os.getenv("BAF_API_BASE_URL")).rstrip("/")
        auth_url = auth_url or os.getenv("BAF_AUTH_URL")
        client_id = client_id or os.getenv("BAF_CLIENT_ID")
        client_secret = client_secret or os.getenv("BAF_CLIENT_SECRET")
        
        # Validate required parameters
        if not self.api_base_url:
            raise ValueError("API base URL is required, either provide it or set BAF_API_BASE_URL environment variable")
        if not auth_url:
            raise ValueError("Auth URL is required, either provide it or set BAF_AUTH_URL environment variable")
        if not client_id:
            raise ValueError("Client ID is required, either provide it or set BAF_CLIENT_ID environment variable")
        if not client_secret:
            raise ValueError("Client secret is required, either provide it or set BAF_CLIENT_SECRET environment variable")
        
        self.token_manager = TokenManager(auth_url, client_id, client_secret)
        self.timeout = timeout
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers with authorization token for API requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        token = self.token_manager.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (relative to base URL)
            data: Request data (for POST, PATCH)
            params: Query parameters
            
        Returns:
            Response data as a dictionary
            
        Raises:
            ApiError: If the API returns an error
        """
        url = f"{self.api_base_url}{endpoint}"
        headers = self._get_headers()
        
        logger.debug(f"Making API request: {method} {url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Params: {params}")
        logger.debug(f"Data: {data}")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, params=params, timeout=self.timeout)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data, params=params, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.debug(f"API Response Status Code: {response.status_code}")
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                logger.debug("API Response: No content (204)")
                return {}
                
            response_json = response.json()
            logger.debug(f"API Response JSON: {response_json}")
            return response_json
            
        except requests.RequestException as e:
            error_msg = str(e)
            error_details = ""
            
            if hasattr(e, 'response') and e.response:
                logger.error(f"API Error Status Code: {e.response.status_code}")
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        error_details = f"{error_data.get('error')}: {error_data.get('message', '')}"
                    elif isinstance(error_data, dict):
                        # If error is not structured as expected, just dump the whole error data
                        error_details = json.dumps(error_data)
                    logger.error(f"API Error Response JSON: {error_data}")
                except Exception:
                    # If we can't parse as JSON, use text content
                    error_details = e.response.text
                    logger.error(f"API Error Response Text: {error_details}")
            
            full_error = error_msg
            if error_details:
                full_error = f"{error_msg} - {error_details}"
                
            logger.error(f"API request failed: {full_error}")
            raise ApiError(f"API request failed: {full_error}") from e
    
    # Agent methods
    
    def list_agents(self) -> List[Agent]:
        """
        Get a list of all agents.
        
        Returns:
            List of Agent objects
        """
        response = self._make_request("GET", "/api/v1/Agents")
        agents = []
        
        for agent_data in response.get("value", []):
            agents.append(Agent.from_api_dict(agent_data))
            
        return agents
    
    def get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Agent object
            
        Raises:
            ApiError: If the agent is not found
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})")
        return Agent.from_api_dict(response)
    
    def create_agent(self, agent: Agent) -> Agent:
        """
        Create a new agent or update an existing one with the same name.
        
        Args:
            agent: Agent object with configuration
            
        Returns:
            Created or updated Agent object with ID
        """
        # Check if an agent with the same name already exists
        existing_agents = self.list_agents()
        existing_agent = next((a for a in existing_agents if a.name == agent.name), None)
        
        if existing_agent:
            logger.info(f"Agent with name '{agent.name}' already exists (ID: {existing_agent.id}). Updating instead.")
            # Update the existing agent with the new configuration
            update_data = agent.to_api_dict()
            # Remove ID from update data if present
            update_data.pop("ID", None)
            
            self._make_request("PATCH", f"/api/v1/Agents({existing_agent.id})", data=update_data)
            return self.get_agent(existing_agent.id)
        
        # Create a new agent if none exists with that name
        response = self._make_request("POST", "/api/v1/Agents", data=agent.to_api_dict())
        agent_id = response.get("ID")
        
        # Get the full agent object
        return self.get_agent(agent_id)
    
    def update_agent(self, agent_id: str, **kwargs) -> Agent:
        """
        Update an agent's configuration.
        
        Args:
            agent_id: The ID of the agent to update
            **kwargs: Agent properties to update
            
        Returns:
            Updated Agent object
        """
        # Convert snake_case keys to camelCase for API
        data = {}
        for key, value in kwargs.items():
            # Convert snake_case to camelCase
            parts = key.split('_')
            camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
            data[camel_key] = value
        
        self._make_request("PATCH", f"/api/v1/Agents({agent_id})", data=data)
        return self.get_agent(agent_id)
    
    def delete_agent(self, agent_id: str) -> None:
        """
        Delete an agent.
        
        Args:
            agent_id: The ID of the agent to delete
        """
        self._make_request("DELETE", f"/api/v1/Agents({agent_id})")
    
    # Tool methods
    
    def list_tools(self, agent_id: str) -> List[Tool]:
        """
        Get a list of all tools for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            List of Tool objects
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/tools")
        tools = []
        
        for tool_data in response.get("value", []):
            tools.append(Tool.from_api_dict(tool_data))
            
        return tools
    
    def get_tool(self, agent_id: str, tool_id: str) -> Tool:
        """
        Get a tool by ID.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            
        Returns:
            Tool object
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/tools({tool_id})")
        return Tool.from_api_dict(response)
    
    def create_tool(self, agent_id: str, tool: Tool) -> Tool:
        """
        Create a new tool for an agent.
        
        Args:
            agent_id: The ID of the agent
            tool: Tool object with configuration
            
        Returns:
            Created Tool object with ID
        """
        response = self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/tools",
            data=tool.to_api_dict()
        )
        tool_id = response.get("ID")
        
        # Get the full tool object
        return self.get_tool(agent_id, tool_id)
    
    def wait_for_tool_ready(
        self,
        agent_id: str,
        tool_id: str,
        max_attempts: int = 30,
        interval: int = 3
    ) -> Tool:
        """
        Wait until a tool is in the ready state.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            max_attempts: Maximum number of polling attempts
            interval: Polling interval in seconds
            
        Returns:
            Tool object in ready state
            
        Raises:
            ResourceNotReadyError: If the tool fails to become ready
            TimeoutError: If max_attempts is reached
        """
        for attempt in range(max_attempts):
            tool = self.get_tool(agent_id, tool_id)
            
            if tool.state == "ready":
                return tool
            elif tool.state == "error":
                raise ResourceNotReadyError(f"Tool failed to become ready: {tool.last_error}")
            
            logger.debug(f"Tool not ready yet, waiting... (state: {tool.state})")
            time.sleep(interval)
        
        raise TimeoutError(f"Tool did not become ready after {max_attempts} attempts")
    
    # Resource methods
    
    def list_resources(self, agent_id: str, tool_id: str) -> List[Resource]:
        """
        Get a list of all resources for a tool.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            
        Returns:
            List of Resource objects
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/tools({tool_id})/resources")
        resources = []
        
        for resource_data in response.get("value", []):
            resources.append(Resource.from_api_dict(resource_data))
            
        return resources
    
    def get_resource(self, agent_id: str, tool_id: str, resource_id: str) -> Resource:
        """
        Get a resource by ID.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            resource_id: The ID of the resource
            
        Returns:
            Resource object
        """
        response = self._make_request(
            "GET",
            f"/api/v1/Agents({agent_id})/tools({tool_id})/resources({resource_id})"
        )
        return Resource.from_api_dict(response)
    
    def create_resource(
        self,
        agent_id: str,
        tool_id: str,
        resource: Resource,
        file_content: Optional[bytes] = None
    ) -> Resource:
        """
        Create a new resource for a tool.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            resource: Resource object with configuration
            file_content: Optional binary content to upload
            
        Returns:
            Created Resource object with ID
        """
        if file_content:
            # Base64 encode the file content
            resource.data = base64.b64encode(file_content).decode('utf-8')
        
        response = self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/tools({tool_id})/resources",
            data=resource.to_api_dict()
        )
        resource_id = response.get("ID")
        
        # Get the full resource object
        return self.get_resource(agent_id, tool_id, resource_id)
    
    def wait_for_resource_ready(
        self,
        agent_id: str,
        tool_id: str,
        resource_id: str,
        max_attempts: int = 30,
        interval: int = 3
    ) -> Resource:
        """
        Wait until a resource is in the ready state.
        
        Args:
            agent_id: The ID of the agent
            tool_id: The ID of the tool
            resource_id: The ID of the resource
            max_attempts: Maximum number of polling attempts
            interval: Polling interval in seconds
            
        Returns:
            Resource object in ready state
            
        Raises:
            ResourceNotReadyError: If the resource fails to become ready
            TimeoutError: If max_attempts is reached
        """
        for attempt in range(max_attempts):
            resource = self.get_resource(agent_id, tool_id, resource_id)
            
            if resource.state == ResourceState.READY:
                return resource
            elif resource.state == ResourceState.ERROR:
                raise ResourceNotReadyError(f"Resource failed to become ready: {resource.last_error}")
            
            logger.debug(f"Resource not ready yet, waiting... (state: {resource.state})")
            time.sleep(interval)
        
        raise TimeoutError(f"Resource did not become ready after {max_attempts} attempts")
    
    # Chat methods
    
    def list_chats(self, agent_id: str) -> List[Chat]:
        """
        Get a list of all chats for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            List of Chat objects
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/chats")
        chats = []
        
        for chat_data in response.get("value", []):
            chats.append(Chat.from_api_dict(chat_data))
            
        return chats
    
    def get_chat(self, agent_id: str, chat_id: str) -> Chat:
        """
        Get a chat by ID.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            
        Returns:
            Chat object
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/chats({chat_id})")
        return Chat.from_api_dict(response)
    
    def create_chat(self, agent_id: str, chat: Chat) -> Chat:
        """
        Create a new chat for an agent or return an existing one with the same name.
        
        Args:
            agent_id: The ID of the agent
            chat: Chat object with name
            
        Returns:
            Created Chat object with ID or existing chat with the same name
        """
        # Check if a chat with the same name already exists for this agent
        existing_chats = self.list_chats(agent_id)
        existing_chat = next((c for c in existing_chats if c.name == chat.name), None)
        
        if existing_chat:
            logger.info(f"Chat with name '{chat.name}' already exists for agent {agent_id} (Chat ID: {existing_chat.id}). Returning existing chat.")
            return existing_chat
        
        # Create a new chat if none exists with that name
        response = self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/chats",
            data=chat.to_api_dict()
        )
        chat_id = response.get("ID")
        
        # Get the full chat object
        return self.get_chat(agent_id, chat_id)
    
    # Message methods
    
    def list_messages(self, agent_id: str, chat_id: str) -> List[Message]:
        """
        Get a list of all messages in a chat.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            
        Returns:
            List of Message objects
        """
        response = self._make_request("GET", f"/api/v1/Agents({agent_id})/chats({chat_id})/history")
        messages = []
        
        for message_data in response.get("value", []):
            messages.append(Message.from_api_dict(message_data))
            
        return messages
    
    def get_message(self, agent_id: str, chat_id: str, message_id: str) -> Message:
        """
        Get a message by ID.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            message_id: The ID of the message
            
        Returns:
            Message object
        """
        response = self._make_request(
            "GET",
            f"/api/v1/Agents({agent_id})/chats({chat_id})/history({message_id})"
        )
        return Message.from_api_dict(response)
    
    def send_message(
        self,
        agent_id: str,
        chat_id: str,
        message: str,
        output_format: OutputFormat = OutputFormat.MARKDOWN,
        output_format_options: str = "",
        async_mode: bool = True,
        return_trace: bool = False,
        destination: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Send a message to an agent.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            message: The message text
            output_format: Desired output format
            output_format_options: Additional format options
            async_mode: Whether to process the message asynchronously
            return_trace: Whether to return the trace
            destination: Optional SAP BTP destination for callbacks
            
        Returns:
            If async_mode is True, returns the history ID
            If async_mode is False, returns the agent's response
        """
        logger.info(f"Sending message to agent {agent_id}, chat {chat_id}, async={async_mode}")
        logger.debug(f"Message content: {message}")
        data = {
            "msg": message,
            "outputFormat": output_format.value,
            "async": async_mode,
            "returnTrace": return_trace
        }
        
        if output_format_options:
            data["outputFormatOptions"] = output_format_options
            logger.debug(f"Output format options: {output_format_options}")
            
        if destination:
            data["destination"] = destination
            logger.debug(f"Destination: {destination}")
        
        logger.debug(f"Calling send_message endpoint with data: {data}")
        response = self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/chats({chat_id})/UnifiedAiAgentService.sendMessage",
            data=data
        )
        logger.debug(f"Send message response: {response}")
        
        if async_mode:
            result = response.get("historyId")
            logger.info(f"Message sent asynchronously. History ID: {result}")
            return result
        else:
            result = response.get("answer", "")
            logger.info(f"Message sent synchronously. Received answer.")
            logger.debug(f"Answer content: {result}")
            return result
    
    def wait_for_message_response(
        self,
        agent_id: str,
        chat_id: str,
        history_id: str,
        max_attempts: int = 60,
        interval: int = 3
    ) -> Message:
        """
        Wait for a response to an asynchronous message.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            history_id: The history ID of the sent message
            max_attempts: Maximum number of polling attempts
            interval: Polling interval in seconds
            
        Returns:
            Message object containing the agent's response
            
        Raises:
            ApiError: If the chat fails
            TimeoutError: If max_attempts is reached
        """
        for attempt in range(max_attempts):
            logger.debug(f"Polling for response to history ID {history_id} (Attempt {attempt+1}/{max_attempts})")
            # Get all messages in the chat
            all_messages = self.list_messages(agent_id, chat_id)

            # Find the message that is a response to our sent message
            for message in all_messages:
                if message.previous_id == history_id:
                    logger.info(f"Found response message {message.id} for history ID {history_id}")
                    return message

            # Check if the chat is in a failed state (optional but good practice)
            chat = self.get_chat(agent_id, chat_id)
            if chat.state == ChatState.FAILED:
                logger.error(f"Chat {chat_id} entered FAILED state while waiting for response.")
                raise ApiError("Chat processing failed")

            logger.debug(f"No response yet for {history_id}, waiting {interval}s...")
            time.sleep(interval)

        logger.error(f"No response received for history ID {history_id} after {max_attempts} attempts")
        raise TimeoutError(f"No response received after {max_attempts} attempts")
    
    def continue_message(
        self,
        agent_id: str,
        chat_id: str,
        history_id: str,
        observation: str,
        async_mode: bool = True,
        return_trace: bool = False,
        destination: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Continue a message that was interrupted by a tool.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
            history_id: The history ID of the interrupted message
            observation: The observation to continue with
            async_mode: Whether to process the message asynchronously
            return_trace: Whether to return the trace
            destination: Optional SAP BTP destination for callbacks
            
        Returns:
            If async_mode is True, returns the history ID
            If async_mode is False, returns the agent's response
        """
        data = {
            "historyId": history_id,
            "observation": observation,
            "async": async_mode,
            "returnTrace": return_trace
        }
        
        if destination:
            data["destination"] = destination
        
        response = self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/chats({chat_id})/UnifiedAiAgentService.continueMessage",
            data=data
        )
        
        if async_mode:
            return response.get("historyId")
        else:
            return response.get("answer", "")
    
    def cancel_chat(self, agent_id: str, chat_id: str) -> None:
        """
        Cancel the agent loop.
        
        Args:
            agent_id: The ID of the agent
            chat_id: The ID of the chat
        """
        self._make_request(
            "POST",
            f"/api/v1/Agents({agent_id})/chats({chat_id})/UnifiedAiAgentService.cancel",
            data={}
        ) 