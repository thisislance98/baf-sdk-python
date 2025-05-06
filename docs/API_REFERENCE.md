# BAF SDK API Reference

This document provides detailed reference information for the BAF SDK classes, methods, and objects.

## Table of Contents

- [AgentBuilderClient](#agentbuilderclient)
- [Data Models](#data-models)
  - [Agent](#agent)
  - [Chat](#chat)
  - [Message](#message)
  - [Tool](#tool)
  - [Resource](#resource)
- [Enumerations](#enumerations)
- [Exceptions](#exceptions)

## AgentBuilderClient

The main client class for interacting with the Project Agent Builder API.

### Constructor

```python
AgentBuilderClient(
    auth_url: str,
    api_base_url: str,
    client_id: str,
    client_secret: str,
    timeout: int = 60
)
```

- **auth_url**: The OAuth token endpoint URL
- **api_base_url**: The base URL for the Project Agent Builder API
- **client_id**: The client ID for authentication
- **client_secret**: The client secret for authentication
- **timeout**: Default timeout for API requests (in seconds)

### Agent Methods

#### `list_agents()`

Get a list of all agents.

**Returns**: List of [Agent](#agent) objects

#### `get_agent(agent_id: str)`

Get an agent by ID.

**Parameters**:
- **agent_id**: The ID of the agent

**Returns**: [Agent](#agent) object

**Raises**: [ApiError](#exceptions) if the agent is not found

#### `create_agent(agent: Agent)`

Create a new agent.

**Parameters**:
- **agent**: [Agent](#agent) object with configuration

**Returns**: Created [Agent](#agent) object with ID

**Raises**: [ApiError](#exceptions) if creation fails

#### `update_agent(agent_id: str, **kwargs)`

Update an agent's configuration.

**Parameters**:
- **agent_id**: The ID of the agent to update
- **kwargs**: Agent properties to update (any properties of the Agent object)

**Returns**: Updated [Agent](#agent) object

**Raises**: [ApiError](#exceptions) if update fails

#### `delete_agent(agent_id: str)`

Delete an agent.

**Parameters**:
- **agent_id**: The ID of the agent to delete

**Returns**: None

**Raises**: [ApiError](#exceptions) if deletion fails

### Tool Methods

#### `list_tools(agent_id: str)`

List all tools for an agent.

**Parameters**:
- **agent_id**: The ID of the agent

**Returns**: List of [Tool](#tool) objects

**Raises**: [ApiError](#exceptions) if the request fails

#### `get_tool(agent_id: str, tool_id: str)`

Get a specific tool.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool

**Returns**: [Tool](#tool) object

**Raises**: [ApiError](#exceptions) if the tool is not found

#### `create_tool(agent_id: str, tool: Tool)`

Create a new tool for an agent.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool**: [Tool](#tool) object with configuration

**Returns**: Created [Tool](#tool) object with ID

**Raises**: [ApiError](#exceptions) if creation fails

#### `wait_for_tool_ready(agent_id: str, tool_id: str, max_attempts: int = 30, interval: int = 3)`

Wait for a tool to become ready.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool
- **max_attempts**: Maximum number of attempts to check status
- **interval**: Time between attempts in seconds

**Returns**: Ready [Tool](#tool) object

**Raises**:
- [ResourceNotReadyError](#exceptions) if the tool fails to become ready
- [TimeoutError](#exceptions) if max_attempts is reached

### Resource Methods

#### `list_resources(agent_id: str, tool_id: str)`

List all resources for a tool.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool

**Returns**: List of [Resource](#resource) objects

**Raises**: [ApiError](#exceptions) if the request fails

#### `get_resource(agent_id: str, tool_id: str, resource_id: str)`

Get a specific resource.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool
- **resource_id**: The ID of the resource

**Returns**: [Resource](#resource) object

**Raises**: [ApiError](#exceptions) if the resource is not found

#### `create_resource(agent_id: str, tool_id: str, resource: Resource, file_content: Optional[bytes] = None)`

Create a new resource for a tool.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool
- **resource**: [Resource](#resource) object with configuration
- **file_content**: Binary content of the file to upload

**Returns**: Created [Resource](#resource) object with ID

**Raises**: [ApiError](#exceptions) if creation fails

#### `wait_for_resource_ready(agent_id: str, tool_id: str, resource_id: str, max_attempts: int = 30, interval: int = 3)`

Wait for a resource to become ready.

**Parameters**:
- **agent_id**: The ID of the agent
- **tool_id**: The ID of the tool
- **resource_id**: The ID of the resource
- **max_attempts**: Maximum number of attempts to check status
- **interval**: Time between attempts in seconds

**Returns**: Ready [Resource](#resource) object

**Raises**:
- [ResourceNotReadyError](#exceptions) if the resource fails to become ready
- [TimeoutError](#exceptions) if max_attempts is reached

### Chat Methods

#### `list_chats(agent_id: str)`

List all chats for an agent.

**Parameters**:
- **agent_id**: The ID of the agent

**Returns**: List of [Chat](#chat) objects

**Raises**: [ApiError](#exceptions) if the request fails

#### `get_chat(agent_id: str, chat_id: str)`

Get a specific chat.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat

**Returns**: [Chat](#chat) object

**Raises**: [ApiError](#exceptions) if the chat is not found

#### `create_chat(agent_id: str, chat: Chat)`

Create a new chat for an agent.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat**: [Chat](#chat) object with configuration

**Returns**: Created [Chat](#chat) object with ID

**Raises**: [ApiError](#exceptions) if creation fails

#### `cancel_chat(agent_id: str, chat_id: str)`

Cancel an active chat.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat

**Returns**: None

**Raises**: [ApiError](#exceptions) if cancellation fails

### Message Methods

#### `list_messages(agent_id: str, chat_id: str)`

List all messages in a chat.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat

**Returns**: List of [Message](#message) objects

**Raises**: [ApiError](#exceptions) if the request fails

#### `get_message(agent_id: str, chat_id: str, message_id: str)`

Get a specific message.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat
- **message_id**: The ID of the message

**Returns**: [Message](#message) object

**Raises**: [ApiError](#exceptions) if the message is not found

#### `send_message(agent_id: str, chat_id: str, message: str, output_format: OutputFormat = OutputFormat.MARKDOWN, output_format_options: str = "", async_mode: bool = True, return_trace: bool = False, destination: Optional[str] = None)`

Send a message to a chat.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat
- **message**: The message content
- **output_format**: The desired output format (JSON, MARKDOWN, TEXT)
- **output_format_options**: Options for the output format (e.g., JSON schema)
- **async_mode**: If True, returns history_id; if False, waits for response
- **return_trace**: If True, returns trace information about message processing
- **destination**: Optional destination hint

**Returns**:
- If async_mode is True: history_id (str)
- If async_mode is False: answer (str)
- If return_trace is True: Dictionary with trace information

**Raises**: [ApiError](#exceptions) if the request fails

#### `wait_for_message_response(agent_id: str, chat_id: str, history_id: str, max_attempts: int = 60, interval: int = 3)`

Wait for a response to an asynchronous message.

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat
- **history_id**: The history ID from send_message
- **max_attempts**: Maximum number of attempts to check for response
- **interval**: Time between attempts in seconds

**Returns**: [Message](#message) object containing the response

**Raises**:
- [TimeoutError](#exceptions) if max_attempts is reached
- [ApiError](#exceptions) if the request fails

#### `continue_message(agent_id: str, chat_id: str, history_id: str, observation: str, async_mode: bool = True, return_trace: bool = False, destination: Optional[str] = None)`

Continue a conversation with an observation (e.g., after a tool response).

**Parameters**:
- **agent_id**: The ID of the agent
- **chat_id**: The ID of the chat
- **history_id**: The history ID of the message to continue
- **observation**: The observation/response to provide
- **async_mode**: If True, returns history_id; if False, waits for response
- **return_trace**: If True, returns trace information
- **destination**: Optional destination hint

**Returns**:
- If async_mode is True: history_id (str)
- If async_mode is False: answer (str)
- If return_trace is True: Dictionary with trace information

**Raises**: [ApiError](#exceptions) if the request fails

## Data Models

### Agent

Represents an agent in the Project Agent Builder.

#### Properties

- **name**: str - The name of the agent
- **id**: Optional[str] - The ID of the agent (read-only, set by API)
- **type**: AgentType - The type of agent (default: SMART)
- **safety_check**: bool - Whether to perform safety checks (default: False)
- **expert_in**: str - The agent's area of expertise (default: "")
- **initial_instructions**: str - Initial instructions for the agent (default: "")
- **iterations**: int - Number of iterations for processing (default: 20)
- **base_model**: ModelType - Base model for initial processing (default: OPENAI_GPT4O_MINI)
- **advanced_model**: ModelType - Advanced model for deeper processing (default: OPENAI_GPT4O)
- **default_output_format**: OutputFormat - Default output format (default: MARKDOWN)
- **default_output_format_options**: str - Options for the output format (default: "")
- **preprocessing_enabled**: bool - Whether preprocessing is enabled (default: True)
- **postprocessing_enabled**: bool - Whether postprocessing is enabled (default: True)
- **orchestration_module_config**: Optional[OrchestrationModuleConfig] - Configuration for orchestration modules
- **created_at**: Optional[datetime] - Creation timestamp (read-only)
- **modified_at**: Optional[datetime] - Last modification timestamp (read-only)

#### Methods

- **to_api_dict()**: Convert the agent to a dictionary for API requests
- **from_api_dict(data)**: (classmethod) Create an agent from an API response dictionary

### Chat

Represents a chat session with an agent.

#### Properties

- **name**: str - The name of the chat
- **id**: Optional[str] - The ID of the chat (read-only, set by API)
- **state**: Optional[ChatState] - The state of the chat (read-only)
- **created_at**: Optional[datetime] - Creation timestamp (read-only)
- **modified_at**: Optional[datetime] - Last modification timestamp (read-only)

#### Methods

- **to_api_dict()**: Convert the chat to a dictionary for API requests
- **from_api_dict(data)**: (classmethod) Create a chat from an API response dictionary

### Message

Represents a message in a chat.

#### Properties

- **content**: str - The content of the message
- **role**: MessageRole - The role of the message sender (USER, ASSISTANT, SYSTEM)
- **id**: Optional[str] - The ID of the message (read-only, set by API)
- **created_at**: Optional[datetime] - Creation timestamp (read-only)
- **previous_id**: Optional[str] - ID of the previous message (read-only)
- **type**: Optional[MessageType] - The type of the message (read-only)

#### Methods

- **to_api_dict()**: Convert the message to a dictionary for API requests
- **from_api_dict(data)**: (classmethod) Create a message from an API response dictionary

### Tool

Represents a tool that can be used by an agent.

#### Properties

- **name**: str - The name of the tool
- **type**: ToolType - The type of the tool
- **id**: Optional[str] - The ID of the tool (read-only, set by API)
- **state**: Optional[str] - The state of the tool (read-only)
- **last_error**: Optional[str] - The last error message, if any (read-only)
- **config**: Dict[str, Any] - Configuration options for the tool

#### Methods

- **to_api_dict()**: Convert the tool to a dictionary for API requests
- **from_api_dict(data)**: (classmethod) Create a tool from an API response dictionary

### Resource

Represents a resource that can be used by a tool.

#### Properties

- **name**: str - The name of the resource
- **content_type**: str - The MIME type of the resource
- **id**: Optional[str] - The ID of the resource (read-only, set by API)
- **state**: Optional[ResourceState] - The state of the resource (read-only)
- **last_error**: Optional[str] - The last error message, if any (read-only)
- **data**: Optional[str] - Base64 encoded data for small resources

#### Methods

- **to_api_dict()**: Convert the resource to a dictionary for API requests
- **from_api_dict(data)**: (classmethod) Create a resource from an API response dictionary

## Enumerations

### AgentType

- **SMART**: "smart" - Smart agent type

### ModelType

- **OPENAI_GPT4O_MINI**: "OpenAiGpt4oMini" - OpenAI GPT-4o Mini model
- **OPENAI_GPT4O**: "OpenAiGpt4o" - OpenAI GPT-4o model

### OutputFormat

- **JSON**: "JSON" - JSON output format
- **MARKDOWN**: "Markdown" - Markdown output format
- **TEXT**: "Text" - Plain text output format

### MessageRole

- **USER**: "user" - User message
- **ASSISTANT**: "assistant" - Assistant message
- **SYSTEM**: "system" - System message
- **AI**: "ai" - AI message (sometimes returned by API instead of "assistant")

### MessageType

- **START**: "start" - Start of conversation
- **AGENT**: "agent" - Agent message
- **TOOL**: "tool" - Tool message
- **TOOL_RESOURCE**: "toolResource" - Tool resource message
- **ABORT**: "abort" - Aborted message
- **ERROR**: "error" - Error message
- **ANSWER_FOR_USER**: "answerForUser" - Answer for user
- **QUESTION_FOR_USER**: "questionForUser" - Question for user
- **QUESTION_FOR_TOOL**: "questionForTool" - Question for tool
- **QUESTION_FOR_AGENT**: "questionForAgent" - Question for agent
- **EVENT**: "event" - Event message

### ResourceState

- **UPLOADING**: "uploading" - Resource is being uploaded
- **PROCESSING**: "processing" - Resource is being processed
- **READY**: "ready" - Resource is ready to use
- **ERROR**: "error" - Resource encountered an error

### ToolType

- **DOCUMENT**: "document" - Document tool for processing documents
- **WEBSEARCH**: "websearch" - Web search tool
- **HUMAN**: "human" - Human interaction tool
- **CUSTOM**: "custom" - Custom tool

### ChatState

- **ACTIVE**: "active" - Chat is active
- **PROCESSING**: "processing" - Chat is processing a message
- **FAILED**: "failed" - Chat has failed
- **NONE**: "none" - Chat has no specific state

## Exceptions

### ApiError

Exception raised for errors in API responses.

### AuthenticationError

Exception raised for authentication failures.

### ResourceNotReadyError

Exception raised when a resource fails to become ready.

### TimeoutError

Exception raised when an operation times out. 