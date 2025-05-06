# BAF SDK Quick Start Guide

This guide provides step-by-step examples for common use cases with the BAF SDK.

## Installation

Install the BAF SDK using pip:

```bash
pip install baf-sdk
```

## Authentication Setup

Before using the SDK, you need to authenticate with the Project Agent Builder API:

```python
from baf_sdk import AgentBuilderClient

# Create a client with authentication details
client = AgentBuilderClient(
    auth_url="https://your-auth-url/oauth/token",
    api_base_url="https://your-api-url",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

## Example 1: Creating a Simple Question-Answering Agent

This example shows how to create a basic agent and have a conversation with it.

```python
from baf_sdk import Agent, Chat, OutputFormat

# Create an agent
agent = Agent(
    name="General Assistant",
    expert_in="General knowledge",
    initial_instructions="You are a helpful assistant that provides accurate and concise answers."
)

# Register the agent with the API
created_agent = client.create_agent(agent)
print(f"Created agent: {created_agent.name} (ID: {created_agent.id})")

# Create a chat session
chat = Chat(name="General Questions")
created_chat = client.create_chat(created_agent.id, chat)
print(f"Created chat: {created_chat.name} (ID: {created_chat.id})")

# Send a message and get a response
question = "What are the main differences between Python 2 and Python 3?"

# Option 1: Synchronous mode (blocking until response is received)
answer = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message=question,
    async_mode=False
)
print(f"Answer: {answer}")

# Option 2: Asynchronous mode (non-blocking)
history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message="What are the main applications of machine learning?",
    async_mode=True
)

# Wait for the response at your convenience
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id
)
print(f"Response: {response.content}")
```

## Example 2: Creating an Agent with Document Knowledge

This example demonstrates how to create an agent with access to document-based knowledge.

```python
from baf_sdk import Agent, Chat, Tool, Resource, ToolType

# Create an agent
agent = Agent(
    name="Document Assistant",
    expert_in="Technical documentation",
    initial_instructions="You are an assistant that helps users understand information in technical documents."
)
created_agent = client.create_agent(agent)

# Create a document tool for the agent
document_tool = Tool(
    name="Technical Manuals",
    type=ToolType.DOCUMENT
)
created_tool = client.create_tool(created_agent.id, document_tool)

# Upload a PDF document as a resource
with open("technical_manual.pdf", "rb") as f:
    pdf_content = f.read()

manual_resource = Resource(
    name="Product Manual",
    content_type="application/pdf"
)
created_resource = client.create_resource(
    created_agent.id,
    created_tool.id,
    manual_resource,
    pdf_content
)

# Wait for the resource to be processed
ready_resource = client.wait_for_resource_ready(
    created_agent.id, 
    created_tool.id, 
    created_resource.id,
    max_attempts=60,
    interval=5
)
print(f"Resource state: {ready_resource.state.value}")

# Wait for the tool to be ready
ready_tool = client.wait_for_tool_ready(
    created_agent.id,
    created_tool.id
)
print(f"Tool is ready: {ready_tool.state}")

# Create a chat and ask questions about the document
chat = Chat(name="Document Questions")
created_chat = client.create_chat(created_agent.id, chat)

# Ask a question about the document
history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message="What are the system requirements described in the manual?",
    async_mode=True
)

# Wait for response
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id
)
print(f"Response: {response.content}")
```

## Example 3: Working with Structured JSON Output

This example shows how to get structured JSON output from an agent.

```python
from baf_sdk import Agent, Chat, OutputFormat

# Create an agent
agent = Agent(
    name="Data Extractor",
    expert_in="Information extraction",
    initial_instructions="You are an assistant that extracts structured information.",
    default_output_format=OutputFormat.JSON
)
created_agent = client.create_agent(agent)

# Create a chat
chat = Chat(name="Data Extraction")
created_chat = client.create_chat(created_agent.id, chat)

# Define a JSON schema for product information
json_schema = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "product_name": {
      "type": "string",
      "description": "Name of the product"
    },
    "price": {
      "type": "number",
      "description": "Price in USD"
    },
    "features": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of product features"
    }
  },
  "required": ["product_name", "price", "features"]
}"""

# Send message requesting structured JSON output
product_text = """
The XDR-5000 Smart Speaker features voice control, multi-room audio, 
and high-fidelity sound. With Bluetooth 5.0 and Wi-Fi connectivity, 
it integrates with all major smart home systems. The speaker has 
50W output power and includes a built-in voice assistant. 
It's available for $199.99.
"""

history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message=f"Extract product information from this text: {product_text}",
    output_format=OutputFormat.JSON,
    output_format_options=json_schema,
    async_mode=True
)

# Wait for structured response
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id
)

# The response.content will contain structured JSON data
import json
product_data = json.loads(response.content)
print(f"Product Name: {product_data['product_name']}")
print(f"Price: ${product_data['price']}")
print("Features:")
for feature in product_data['features']:
    print(f" - {feature}")
```

## Example 4: Using a Human Tool

This example demonstrates how to use a human-in-the-loop approach with the Human tool.

```python
from baf_sdk import Agent, Chat, Tool, ToolType

# Create an agent with a human tool
agent = Agent(
    name="Human Assisted Agent",
    expert_in="Problem solving with human assistance",
    initial_instructions="You are an assistant that can ask humans for help when needed."
)
created_agent = client.create_agent(agent)

# Create a human tool
human_tool = Tool(
    name="Human Expert",
    type=ToolType.HUMAN
)
created_tool = client.create_tool(created_agent.id, human_tool)

# Create a chat
chat = Chat(name="Human Assistance Chat")
created_chat = client.create_chat(created_agent.id, chat)

# Send a complex request
complex_question = """
I need help troubleshooting my custom hardware setup. 
I have a Raspberry Pi connected to a temperature sensor, 
but I'm not getting any readings. I've checked the wiring 
and it seems correct. What should I try next?
"""

history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message=complex_question,
    async_mode=True
)

# Wait for the initial response (which may be a question for the human)
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id
)
print(f"Initial response: {response.content}")

# Simulate human providing additional information
human_answer = """
Please check if the sensor is compatible with the Raspberry Pi model you're using.
Also check if you've enabled the correct interface (I2C/SPI) in raspi-config.
Run 'sudo i2cdetect -y 1' to see if the device is detected on the I2C bus.
"""

# Continue the conversation with the human's answer
continuation_id = client.continue_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=response.id,
    observation=human_answer,
    async_mode=True
)

# Get the final response
final_response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=continuation_id
)
print(f"Final response: {final_response.content}")
```

## Example 5: Creating a Web Search Agent

This example shows how to create an agent that can search the web for information.

```python
from baf_sdk import Agent, Chat, Tool, ToolType

# Create an agent with web search capability
agent = Agent(
    name="Research Assistant",
    expert_in="Online research",
    initial_instructions="You are a research assistant that can search the web for current information."
)
created_agent = client.create_agent(agent)

# Create a web search tool
web_tool = Tool(
    name="Web Search",
    type=ToolType.WEBSEARCH
)
created_tool = client.create_tool(created_agent.id, web_tool)

# Create a chat
chat = Chat(name="Research Chat")
created_chat = client.create_chat(created_agent.id, chat)

# Ask a question that might require current information
query = "What are the latest developments in quantum computing?"
history_id = client.send_message(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    message=query,
    async_mode=True
)

# Wait for response
response = client.wait_for_message_response(
    agent_id=created_agent.id,
    chat_id=created_chat.id,
    history_id=history_id,
    max_attempts=90,  # Web searches can take longer
    interval=5
)
print(f"Research results: {response.content}")
```

## Managing Agents and Resources

### Listing and Managing Your Agents

```python
# List all agents
agents = client.list_agents()
for agent in agents:
    print(f"Agent: {agent.name} (ID: {agent.id}, Created: {agent.created_at})")

# Update an agent's configuration
if agents:
    updated_agent = client.update_agent(
        agents[0].id,
        initial_instructions="Updated instructions to be more helpful and concise.",
        iterations=25
    )
    print(f"Updated agent: {updated_agent.name}")

# Delete an agent (use with caution)
# client.delete_agent(agent_id)
```

### Working with Chat History

```python
# List all chats for an agent
agent_id = "your-agent-id"
chats = client.list_chats(agent_id)
for chat in chats:
    print(f"Chat: {chat.name} (ID: {chat.id}, State: {chat.state.value if chat.state else 'None'})")

# Get messages from a specific chat
if chats:
    chat_id = chats[0].id
    messages = client.list_messages(agent_id, chat_id)
    
    print(f"Messages in chat '{chats[0].name}':")
    for msg in messages:
        print(f"[{msg.created_at}] {msg.role.value}: {msg.content[:50]}...")
```

## Error Handling

```python
from baf_sdk import ApiError, AuthenticationError, ResourceNotReadyError, TimeoutError

# Example of proper error handling
try:
    # Attempt to get a non-existent agent
    agent = client.get_agent("non-existent-id")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle authentication failure (e.g., refresh credentials)
except ApiError as e:
    print(f"API error: {e}")
    # Handle API error (e.g., retry or report to user)
except ResourceNotReadyError as e:
    print(f"Resource not ready: {e}")
    # Handle resource not ready (e.g., notify user to try again later)
except TimeoutError as e:
    print(f"Operation timed out: {e}")
    # Handle timeout (e.g., increase timeout or try with smaller operation)
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
``` 