# PAB SDK - Python Wrapper for Project Agent Builder

A Python SDK wrapper for the Project Agent Builder (PAB) API that provides an easy-to-use interface for creating and managing AI agents.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pab-sdk.git
   cd pab-sdk
   ```

2. Install the required dependencies using the requirements.txt file:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

You can set up your PAB credentials in three ways:

### Option 1: Using a JSON Credentials File

The SDK can automatically load credentials from a JSON file (recommended approach):

```python
import asyncio
from pab_client import PABClient

# Create PAB client with credentials file path
pab = PABClient("path/to/agent-binding.json", "My Agent")

async def main():
    # Create and use the agent
    agent = await pab.create_agent(
        initial_instructions="You are a helpful assistant.",
        expert_in="Providing information"
    )
    
    response = await agent.send_message(
        "What is the capital of France?",
        output_format=OutputFormat.MARKDOWN
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

The SDK will automatically cache the credentials path after the first use, so you can omit the path in future runs:

```python
# After the first run with a valid credentials path
pab = PABClient(name="My Agent")  # Uses cached credentials
```

### Option 2: Using Environment Variables

Set up your PAB credentials as environment variables:

```bash
export PAB_CLIENT_ID="your-client-id"
export PAB_CLIENT_SECRET="your-client-secret"
export PAB_AUTH_URL="your-auth-url"
export PAB_API_BASE_URL="your-api-base-url"
```

Then in your code:

```python
from pab_client import PABClient

# Creates a client using environment variables
pab = PABClient(name="My Agent")
```

### Option 3: Interactive Setup

If no credentials are provided or found in the cache, the SDK will interactively prompt you for the path to your credentials file:

```python
# Will prompt for credentials if none are found
pab = PABClient(name="My Agent")
```

## Usage Examples

### Simple Agent

Create a simple agent that responds to messages:

```python
import asyncio
from pab_client import PABClient, OutputFormat, ModelType

async def main():
    # Create the PAB client - will use cached credentials or prompt for them
    pab = PABClient(name="Simple Test Agent")
    
    # Create an agent
    agent = await pab.create_agent(
        initial_instructions="You are a helpful assistant that provides concise answers.",
        expert_in="Providing factual information",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O
    )
    
    # Get a response in default Markdown format
    md_response = await agent.send_message(
        "What is the capital of France?",
        output_format=OutputFormat.MARKDOWN
    )
    print(f"Markdown response: {md_response}")
    
    # Get a response in Text format
    text_response = await agent.send_message(
        "List three planets in our solar system.", 
        output_format=OutputFormat.TEXT
    )
    print(f"Text response: {text_response}")
    
    # Get a response in JSON format
    json_response = await agent.send_message(
        "Give me the population of the 3 most populous countries.", 
        output_format=OutputFormat.JSON
    )
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
from pab_client import PABClient, ToolType, OutputFormat

async def main():
    # Create the PAB client
    pab = PABClient(name="Document Assistant")
    
    # Create an agent
    agent = await pab.create_agent(
        initial_instructions="You are an assistant that helps answer questions about documents.",
        expert_in="Document analysis"
    )
    
    # Add a document tool
    tool_id = await pab.add_tool(
        name="document",  # Important: Must be named "document" 
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
    
    await pab.add_document(
        doc_name="Q3 Financial Report",
        content=sample_content,
        content_type="text/markdown"
    )
    
    print("Document added successfully. You can now ask questions about it.")
    
    # List available documents
    documents = await agent.list_documents()
    print(f"Available documents: {documents}")
    
    # Ask questions about the document
    response = await agent.send_message(
        "What was the total revenue in Q3?",
        output_format=OutputFormat.MARKDOWN
    )
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
from pab_client import PABClient, ToolType, OutputFormat

async def main():
    # Create the PAB client
    pab = PABClient(name="Interactive Assistant")
    
    # Create an agent
    agent = await pab.create_agent(
        initial_instructions="""You are an assistant that can ask a human for help. 
        If you don't know something, ask the human.""",
        expert_in="Interactive problem solving"
    )
    
    # Add a human tool
    tool_id = await pab.add_tool(
        name="human",  # Important: Must use standard name
        tool_type=ToolType.HUMAN
    )
    
    print("Human tool added successfully. The agent can now ask for human help.")
    
    # Start interactive session
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### PABClient Class

```python
PABClient(credentials_path: str = None, name: str = "PAB Client Wrapper")
```

The main class for creating and managing PAB clients.

#### Methods

- `configure(client_id: str, client_secret: str, token_url: str, api_url: str)`: Configure PAB API credentials programmatically
- `add_tool(name: str, tool_type: Union[ToolType, str], **kwargs) -> str`: Add a tool to the agent
- `add_document(doc_name: str, content: Union[str, bytes], content_type: str = "text/plain") -> str`: Add a document resource
- `create_agent(...)`: Create a PAB agent with various configuration options
- `get_interface(chat_id: str = None)`: Get an interface for an existing agent
- `run(chat_id: str = None)`: Context manager for running the agent

### AgentInterface Class

Interface for interacting with a PAB Agent.

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

## Setting Up PAB API Credentials

To use this wrapper, you need to obtain PAB API credentials:

1. Create a Project Agent Builder service instance in your BTP subaccount
2. Create a service key for the service instance
3. Download the service key JSON file (agent-binding.json)
4. Use the file path when creating a PABClient instance

See the SAP documentation for more details: https://wiki.one.int.sap/wiki/pages/viewpage.action?spaceKey=CONAIEXP&title=Setting+up+Project+Agent+Builder+in+BTP 