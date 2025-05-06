# BAF SDK - Python Wrapper for Project Agent Builder

A Python SDK wrapper for the Project Agent Builder (BAF) API that provides an easy-to-use interface for creating and managing AI agents.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install httpx python-dotenv
```

## Setup

You can set up your BAF credentials in three ways:

### Option 1: Using a JSON Credentials File

The SDK can automatically load credentials from a JSON file (recommended approach):

```python
import asyncio
from baf_client import BAFClient

# Create BAF client with credentials file path
baf = BAFClient("path/to/agent-binding.json", "My Agent")

async def main():
    # Create and use the agent
    agent = await baf.create_agent(
        initial_instructions="You are a helpful assistant.",
        expert_in="Providing information"
    )
    
    response = await agent("What is the capital of France?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

The SDK will automatically cache the credentials path after the first use, so you can omit the path in future runs:

```python
# After the first run with a valid credentials path
baf = BAFClient(name="My Agent")  # Uses cached credentials
```

### Option 2: Using Environment Variables

Set up your BAF credentials as environment variables:

```bash
export BAF_CLIENT_ID="your-client-id"
export BAF_CLIENT_SECRET="your-client-secret"
export BAF_AUTH_URL="your-auth-url"
export BAF_API_BASE_URL="your-api-base-url"
```

Then in your code:

```python
from baf_client import BAFClient

# Creates a client using environment variables
baf = BAFClient(name="My Agent")
```

### Option 3: Interactive Setup

If no credentials are provided or found in the cache, the SDK will interactively prompt you for the path to your credentials file:

```python
# Will prompt for credentials if none are found
baf = BAFClient(name="My Agent")
```

## Usage Examples

### Simple Agent

Create a simple agent that responds to messages:

```python
import asyncio
from baf_client import BAFClient, OutputFormat, ModelType

async def main():
    # Create the BAF client - will use cached credentials or prompt for them
    baf = BAFClient(name="Simple Test Agent")
    
    # Create an agent
    agent = await baf.create_agent(
        initial_instructions="You are a helpful assistant that provides concise answers.",
        expert_in="Providing factual information",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O
    )
    
    # Get a response in default Markdown format
    md_response = await agent("What is the capital of France?")
    print(f"Markdown response: {md_response}")
    
    # Get a response in Text format
    text_response = await agent("List three planets in our solar system.", 
                              output_format=OutputFormat.TEXT)
    print(f"Text response: {text_response}")
    
    # Get a response in JSON format
    json_response = await agent("Give me the population of the 3 most populous countries.", 
                             output_format=OutputFormat.JSON)
    print(f"JSON response: {json_response}")
    
    # Interactive chat mode
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

### Document Assistant

Create an agent that can answer questions about documents:

```python
import asyncio
from baf_client import BAFClient, ToolType

async def main():
    # Create the BAF client
    baf = BAFClient(name="Document Assistant")
    
    # Create an agent
    agent = await baf.create_agent(
        initial_instructions="You are an assistant that helps answer questions about documents.",
        expert_in="Document analysis"
    )
    
    # Add a document tool
    tool_id = await baf.add_tool(
        name="Document Tool",
        tool_type=ToolType.DOCUMENT
    )
    
    # Add a sample document
    sample_content = """
    # Project Overview
    
    This document provides information about our company's Q3 financial results.
    
    ## Revenue
    
    Total revenue: $5.2 million
    Growth from Q2: 15%
    
    ## Expenses
    
    Total expenses: $3.8 million
    """
    
    await baf.add_document(
        doc_name="Q3 Financial Report",
        content=sample_content,
        content_type="text/markdown"
    )
    
    print("Document added successfully. You can now ask questions about it.")
    
    # List available documents
    documents = await agent.list_documents()
    print(f"Available documents: {documents}")
    
    # Ask questions about the document
    response = await agent("What was the total revenue in Q3?")
    print(f"Agent response: {response}")
    
    # Interactive chat
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

### Web Search Tool

Create an agent that can search the web for information:

```python
import asyncio
from baf_client import BAFClient, ToolType

async def main():
    # Create the BAF client
    baf = BAFClient(name="Research Assistant")
    
    # Create an agent
    agent = await baf.create_agent(
        initial_instructions="You are a research assistant that can search the web for information.",
        expert_in="Internet research"
    )
    
    # Add a web search tool
    tool_id = await baf.add_tool(
        name="Web Search",
        tool_type=ToolType.WEBSEARCH
    )
    
    # Wait for tool to be ready
    await baf._wait_for_tool_ready(tool_id)
    
    # Ask questions that require web search
    response = await agent("What is the current population of Tokyo?")
    print(f"Agent response: {response}")
    
    # Interactive chat
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

### Human Tool for Interactive Assistance

Create an agent that can ask a human for help:

```python
import asyncio
from baf_client import BAFClient, ToolType

async def main():
    # Create the BAF client
    baf = BAFClient(name="Interactive Assistant")
    
    # Create an agent
    agent = await baf.create_agent(
        initial_instructions="""You are an assistant that can ask a human for help. 
        If you don't know something, ask the human.""",
        expert_in="Interactive problem solving"
    )
    
    # Add a human tool
    tool_id = await baf.add_tool(
        name="Ask Human",
        tool_type=ToolType.HUMAN
    )
    
    print("Human tool added successfully. The agent can now ask for human help.")
    
    # Start interactive session
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### BAFClient Class

```python
BAFClient(credentials_path: str = None, name: str = "BAF Client Wrapper")
```

The main class for creating and managing BAF clients.

#### Methods

- `configure(client_id: str, client_secret: str, token_url: str, api_url: str)`: Configure BAF API credentials programmatically
- `add_tool(name: str, tool_type: Union[ToolType, str], **kwargs) -> str`: Add a tool to the agent
- `add_document(doc_name: str, content: Union[str, bytes], content_type: str = "text/plain") -> str`: Add a document resource
- `create_agent(...)`: Create a BAF agent with various configuration options
- `get_interface(chat_id: str = None)`: Get an interface for an existing agent
- `run(chat_id: str = None)`: Context manager for running the agent

### AgentInterface Class

Interface for interacting with a BAF Agent.

#### Methods

- `__call__(message: str, output_format: OutputFormat = OutputFormat.MARKDOWN, output_format_options: str = None) -> str`: Send a message to the agent
- `send_message(...)`: Same as `__call__` but with a different name
- `interactive()`: Start an interactive chat session with the agent
- `continue_message(history_id: str, observation: str) -> str`: Continue a message that was interrupted by a tool
- `cancel()`: Cancel the current chat
- `list_documents()`: List all documents added to the agent
- `get_document_content(doc_name: str)`: Get the content of a document
- `remove_document(doc_name: str)`: Remove a document from the agent
- `list_tools()`: List all tools added to the agent
- `get_tool_names()`: Get the names of all tools added to the agent

## Setting Up BAF API Credentials

To use this wrapper, you need to obtain BAF API credentials:

1. Create a Project Agent Builder service instance in your BTP subaccount
2. Create a service key for the service instance
3. Download the service key JSON file (agent-binding.json)
4. Use the file path when creating a BAFClient instance

See the SAP documentation for more details: https://wiki.one.int.sap/wiki/pages/viewpage.action?spaceKey=CONAIEXP&title=Setting+up+Project+Agent+Builder+in+BTP 