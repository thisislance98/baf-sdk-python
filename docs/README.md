# BAF SDK - Python Client for the Project Agent Builder API

The BAF SDK provides a simple interface to interact with the Project Agent Builder API, allowing you to create and manage AI agents, chats, messages, tools, and resources.

## Installation

```bash
pip install baf-sdk
```

## Quick Start

```python
from baf_sdk import AgentBuilderClient, Agent, Chat, Message, Tool, Resource, ToolType

# Initialize the client
client = AgentBuilderClient(
    auth_url="https://your-auth-url/oauth/token",
    api_base_url="https://your-api-url",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Create an agent
agent = Agent(
    name="My Test Agent",
    expert_in="Python programming",
    initial_instructions="You are a helpful AI assistant specialized in Python programming."
)

created_agent = client.create_agent(agent)
print(f"Created agent with ID: {created_agent.id}")

# Create a chat
chat = Chat(name="Test Chat")
created_chat = client.create_chat(created_agent.id, chat)

# Send a message and get the response
history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message="How do I create a simple HTTP server in Python?",
    async_mode=True
)

# Wait for response
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id
)

print(f"Agent response: {response.content}")
```

## Authentication

The SDK handles authentication automatically through OAuth 2.0 client credentials flow.

```python
from baf_sdk import AgentBuilderClient

client = AgentBuilderClient(
    auth_url="https://your-auth-url/oauth/token",  # OAuth token endpoint
    api_base_url="https://your-api-url",          # Base API URL
    client_id="your-client-id",                   # Client ID
    client_secret="your-client-secret"            # Client Secret
)
```

## Core Concepts

### Agents

Agents are AI assistants with specific expertise, configuration, and tools.

```python
from baf_sdk import Agent, AgentType, ModelType, OutputFormat

# Create a basic agent
agent = Agent(
    name="Research Assistant",
    expert_in="Research and data analysis",
    initial_instructions="You are an AI research assistant specializing in data analysis."
)

# Create a more customized agent
custom_agent = Agent(
    name="Technical Support",
    type=AgentType.SMART,
    safety_check=True,
    expert_in="Technical troubleshooting",
    initial_instructions="You are a technical support agent with expertise in solving IT problems.",
    iterations=25,
    base_model=ModelType.OPENAI_GPT4O_MINI,
    advanced_model=ModelType.OPENAI_GPT4O,
    default_output_format=OutputFormat.MARKDOWN
)

# Create the agent through the client
created_agent = client.create_agent(agent)

# List all agents
agents = client.list_agents()
for agent in agents:
    print(f"Agent: {agent.name} (ID: {agent.id})")

# Get a specific agent
agent = client.get_agent("agent-id")

# Update an agent
updated_agent = client.update_agent(
    "agent-id",
    name="Updated Name",
    expert_in="New expertise"
)

# Delete an agent
client.delete_agent("agent-id")
```

### Chats

Chats represent conversation sessions with agents.

```python
from baf_sdk import Chat

# Create a new chat
chat = Chat(name="Technical Support Chat")
created_chat = client.create_chat("agent-id", chat)

# List all chats for an agent
chats = client.list_chats("agent-id")
for chat in chats:
    print(f"Chat: {chat.name} (ID: {chat.id})")

# Get a specific chat
chat = client.get_chat("agent-id", "chat-id")

# Cancel a chat
client.cancel_chat("agent-id", "chat-id")
```

### Messages

Messages are the communication units within chats.

```python
from baf_sdk import OutputFormat

# Send a message (asynchronous mode)
history_id = client.send_message(
    agent_id="agent-id",
    chat_id="chat-id",
    message="Can you explain how virtual memory works?",
    output_format=OutputFormat.MARKDOWN,
    async_mode=True
)

# Wait for a response
response = client.wait_for_message_response(
    agent_id="agent-id",
    chat_id="chat-id",
    history_id=history_id,
    max_attempts=60,
    interval=3
)
print(f"Agent response: {response.content}")

# Send a message (synchronous mode)
answer = client.send_message(
    agent_id="agent-id",
    chat_id="chat-id",
    message="What is the difference between RAM and ROM?",
    async_mode=False
)
print(f"Answer: {answer}")

# List all messages in a chat
messages = client.list_messages("agent-id", "chat-id")
for msg in messages:
    print(f"{msg.role.value}: {msg.content}")

# Get a specific message
message = client.get_message("agent-id", "chat-id", "message-id")
```

### Tools & Resources

Tools enhance agent capabilities, such as document processing, web search, or human input.

```python
from baf_sdk import Tool, ToolType, Resource

# Create a document tool
doc_tool = Tool(
    name="Knowledge Base",
    type=ToolType.DOCUMENT
)
created_tool = client.create_tool("agent-id", doc_tool)

# Wait for the tool to be ready
ready_tool = client.wait_for_tool_ready(
    agent_id="agent-id",
    tool_id=created_tool.id
)

# List all tools for an agent
tools = client.list_tools("agent-id")

# Get a specific tool
tool = client.get_tool("agent-id", "tool-id")

# Create a resource for a document tool
with open("document.pdf", "rb") as f:
    file_content = f.read()

resource = Resource(
    name="Technical Manual",
    content_type="application/pdf"
)

created_resource = client.create_resource(
    agent_id="agent-id",
    tool_id="tool-id",
    resource=resource,
    file_content=file_content
)

# Wait for resource processing
ready_resource = client.wait_for_resource_ready(
    agent_id="agent-id",
    tool_id="tool-id",
    resource_id=created_resource.id
)

# List all resources for a tool
resources = client.list_resources("agent-id", "tool-id")

# Get a specific resource
resource = client.get_resource("agent-id", "tool-id", "resource-id")
```

## Error Handling

The SDK uses custom exceptions for different error cases:

```python
from baf_sdk import ApiError, AuthenticationError, ResourceNotReadyError, TimeoutError

try:
    client.create_agent(agent)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ApiError as e:
    print(f"API error: {e}")
except ResourceNotReadyError as e:
    print(f"Resource not ready: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
```

## Advanced Features

### Continuing a Conversation with Observations

```python
# Get an initial response
history_id = client.send_message(
    agent_id="agent-id",
    chat_id="chat-id",
    message="What's the weather like?",
    async_mode=True
)

# Wait for the first response
response = client.wait_for_message_response(
    agent_id="agent-id",
    chat_id="chat-id",
    history_id=history_id
)

# Send an observation to continue the conversation
observation = "I just checked and it's sunny with a temperature of 72°F."
continuation = client.continue_message(
    agent_id="agent-id",
    chat_id="chat-id",
    history_id=response.id,
    observation=observation,
    async_mode=True
)

# Wait for the continued response
final_response = client.wait_for_message_response(
    agent_id="agent-id",
    chat_id="chat-id",
    history_id=continuation
)
print(f"Final response: {final_response.content}")
```

## API Reference

For a complete API reference, see the [API documentation](#) (link to be provided).

## License

This project is licensed under the MIT License - see the LICENSE file for details. 