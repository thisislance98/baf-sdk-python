"""
Data models for the BAF SDK.

This module contains the data models used by the BAF SDK to represent
agents, chats, messages, and other entities from the Project Agent Builder API.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union


class ModelType(str, Enum):
    """AI model types available in the Project Agent Builder."""
    OPENAI_GPT4O_MINI = "OpenAiGpt4oMini"
    OPENAI_GPT4O = "OpenAiGpt4o"


class AgentType(str, Enum):
    """Agent types available in the Project Agent Builder."""
    SMART = "smart"


class OutputFormat(str, Enum):
    """Output formats supported by the Project Agent Builder."""
    JSON = "JSON"
    MARKDOWN = "Markdown"
    TEXT = "Text"


class MessageRole(str, Enum):
    """Message roles in a chat."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AI = "ai"  # API sometimes returns this instead of "assistant"


class MessageType(str, Enum):
    """Message types in a chat history."""
    START = "start"
    AGENT = "agent"
    TOOL = "tool"
    TOOL_RESOURCE = "toolResource"
    ABORT = "abort"
    ERROR = "error"
    ANSWER_FOR_USER = "answerForUser"
    QUESTION_FOR_USER = "questionForUser"
    QUESTION_FOR_TOOL = "questionForTool"
    QUESTION_FOR_AGENT = "questionForAgent"
    EVENT = "event"


class ResourceState(str, Enum):
    """States of a resource."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class ToolType(str, Enum):
    """Tool types available in the Project Agent Builder."""
    DOCUMENT = "document"
    WEBSEARCH = "websearch"
    HUMAN = "human"
    CUSTOM = "custom"


class ChatState(str, Enum):
    """States of a chat."""
    ACTIVE = "active"
    PROCESSING = "processing"
    FAILED = "failed"
    SUCCESS = "success"
    RUNNING = "running"
    NONE = "none"


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse datetime string from API, handling various formats.
    
    Args:
        date_str: ISO format datetime string, possibly with 'Z' suffix
        
    Returns:
        Parsed datetime object or None if input is None
    """
    if not date_str:
        return None
    
    # Handle 'Z' timezone indicator by replacing with +00:00
    if date_str.endswith('Z'):
        date_str = date_str[:-1] + '+00:00'
    
    return datetime.fromisoformat(date_str)


@dataclass
class OrchestrationModuleConfig:
    """Configuration for the orchestration modules."""
    reasoning: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "userCanToggle": True,
        "defaultValue": True
    })


@dataclass
class Agent:
    """Represents an agent in the Project Agent Builder."""
    name: str
    id: Optional[str] = None
    type: AgentType = AgentType.SMART
    safety_check: bool = False
    expert_in: str = ""
    initial_instructions: str = ""
    iterations: int = 20
    base_model: ModelType = ModelType.OPENAI_GPT4O_MINI
    advanced_model: ModelType = ModelType.OPENAI_GPT4O
    default_output_format: OutputFormat = OutputFormat.MARKDOWN
    default_output_format_options: str = ""
    preprocessing_enabled: bool = True
    postprocessing_enabled: bool = True
    orchestration_module_config: Optional[OrchestrationModuleConfig] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary for API requests."""
        result = {
            "name": self.name,
            "type": self.type.value,
            "safetyCheck": self.safety_check,
            "expertIn": self.expert_in,
            "initialInstructions": self.initial_instructions,
            "iterations": self.iterations,
            "baseModel": self.base_model.value,
            "advancedModel": self.advanced_model.value,
            "defaultOutputFormat": self.default_output_format.value,
        }
        
        if self.orchestration_module_config:
            result["orchestrationModuleConfig"] = {
                "reasoning": self.orchestration_module_config.reasoning
            }
            
        if self.default_output_format_options:
            result["defaultOutputFormatOptions"] = self.default_output_format_options
            
        return result

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Create an agent from an API response dictionary."""
        orchestration_config = None
        if "orchestrationModuleConfig" in data and data["orchestrationModuleConfig"] is not None:
            orchestration_config = OrchestrationModuleConfig(
                reasoning=data["orchestrationModuleConfig"].get("reasoning", {})
            )
            
        return cls(
            id=data.get("ID"),
            name=data.get("name", ""),
            type=AgentType(data.get("type", "smart")),
            safety_check=data.get("safetyCheck", False),
            expert_in=data.get("expertIn", ""),
            initial_instructions=data.get("initialInstructions", ""),
            iterations=data.get("iterations", 20),
            base_model=ModelType(data.get("baseModel", "OpenAiGpt4oMini")),
            advanced_model=ModelType(data.get("advancedModel", "OpenAiGpt4o")),
            default_output_format=OutputFormat(data.get("defaultOutputFormat", "Markdown")),
            default_output_format_options=data.get("defaultOutputFormatOptions", ""),
            preprocessing_enabled=data.get("preprocessingEnabled", True),
            postprocessing_enabled=data.get("postprocessingEnabled", True),
            orchestration_module_config=orchestration_config,
            created_at=parse_datetime(data.get("createdAt")),
            modified_at=parse_datetime(data.get("modifiedAt")),
        )


@dataclass
class Tool:
    """Represents a tool that can be used by an agent."""
    name: str
    type: ToolType
    id: Optional[str] = None
    state: Optional[str] = None
    last_error: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert the tool to a dictionary for API requests."""
        result = {
            "name": self.name,
            "type": self.type.value,
        }
        
        if self.config:
            result["config"] = self.config
            
        return result

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Tool":
        """Create a tool from an API response dictionary."""
        return cls(
            id=data.get("ID"),
            name=data.get("name", ""),
            type=ToolType(data.get("type", "document")),
            state=data.get("state"),
            last_error=data.get("lastError"),
            config=data.get("config", {})
        )


@dataclass
class Resource:
    """Represents a resource that can be used by a tool."""
    name: str
    content_type: str
    id: Optional[str] = None
    state: Optional[ResourceState] = None
    last_error: Optional[str] = None
    data: Optional[str] = None  # Base64 encoded data

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert the resource to a dictionary for API requests."""
        result = {
            "name": self.name,
            "contentType": self.content_type,
        }
        
        if self.data:
            result["data"] = self.data
            
        return result

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Resource":
        """Create a resource from an API response dictionary."""
        resource_state = None
        if "state" in data:
            state_value = data.get("state")
            try:
                resource_state = ResourceState(state_value)
            except ValueError:
                # If we get an unknown resource state, just use None
                # This allows for forward compatibility as new states are added
                print(f"Warning: Unknown resource state '{state_value}' received from API")
                pass
        
        return cls(
            id=data.get("ID"),
            name=data.get("name", ""),
            content_type=data.get("contentType", ""),
            state=resource_state,
            last_error=data.get("lastError"),
            data=data.get("data")
        )


@dataclass
class Chat:
    """Represents a chat session with an agent."""
    name: str
    id: Optional[str] = None
    state: Optional[ChatState] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert the chat to a dictionary for API requests."""
        return {
            "name": self.name
        }

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Chat":
        """Create a chat from an API response dictionary."""
        chat_state = None
        if "state" in data:
            state_value = data.get("state")
            try:
                chat_state = ChatState(state_value)
            except ValueError:
                # If we get an unknown chat state, just use None
                # This allows for forward compatibility as new states are added
                print(f"Warning: Unknown chat state '{state_value}' received from API")
                pass
        
        return cls(
            id=data.get("ID"),
            name=data.get("name", ""),
            state=chat_state,
            created_at=parse_datetime(data.get("createdAt")),
            modified_at=parse_datetime(data.get("modifiedAt")),
        )


@dataclass
class Message:
    """Represents a message in a chat."""
    content: str
    role: MessageRole
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    previous_id: Optional[str] = None
    type: Optional[MessageType] = None

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary for API requests."""
        return {
            "role": self.role.value,
            "content": self.content
        }

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a message from an API response dictionary."""
        # Extract previous_id, which might be in 'previous' as an object or 'previous_ID' directly
        previous_id = None
        if "previous" in data and isinstance(data["previous"], dict):
            previous_id = data["previous"].get("ID")
        elif "previous_ID" in data:
            previous_id = data.get("previous_ID")
        
        # Handle message type safely
        message_type = None
        if "type" in data:
            type_value = data.get("type")
            try:
                message_type = MessageType(type_value)
            except ValueError:
                # If we get an unknown message type, just use None
                # This allows for forward compatibility as new message types are added
                print(f"Warning: Unknown message type '{type_value}' received from API")
                pass
        
        # Handle role/sender - API sometimes returns 'sender' instead of 'role'
        role_value = data.get("role", data.get("sender", "user"))
        try:
            role = MessageRole(role_value)
        except ValueError:
            # If we get an unknown role, default to "user"
            print(f"Warning: Unknown message role '{role_value}' received from API")
            role = MessageRole.USER
            
        return cls(
            id=data.get("ID"),
            content=data.get("content", ""),
            role=role,
            created_at=parse_datetime(data.get("createdAt")),
            previous_id=previous_id,
            type=message_type
        ) 