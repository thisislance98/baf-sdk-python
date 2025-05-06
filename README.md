# BAF SDK - Python Wrapper for Project Agent Builder

A Python SDK wrapper for the Project Agent Builder (BAF) API that provides an easy-to-use interface for creating and managing AI agents.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install httpx
```

## Setup

You need to set up your BAF credentials as environment variables:

```bash
export BAF_CLIENT_ID="your-client-id"
export BAF_CLIENT_SECRET="your-client-secret"
export BAF_AUTH_URL="your-auth-url"
export BAF_API_BASE_URL="your-api-base-url"
```

These values can be found in your BAF service key. Note that the variable names have changed from older versions:
- Use `BAF_AUTH_URL` instead of `BAF_TOKEN_URL`
- Use `BAF_API_BASE_URL` instead of `BAF_API_URL`

For detailed instructions on how to obtain these credentials, see:
https://wiki.one.int.sap/wiki/pages/viewpage.action?spaceKey=CONAIEXP&title=Setting+up+Project+Agent+Builder+in+BTP

## Usage Examples

### Simple Agent

Create a simple agent that responds to messages:

```python
import asyncio
import os
from baf_agent import BAFAgent

# Create the application
baf = BAFAgent("Size Estimator")

@baf.agent(instruction="Given an object, respond only with an estimate of its size.")
async def main(agent_ctx):
    async with agent_ctx as agent:
        # Example of single message
        moon_size = await agent("the moon")
        print(f"Moon size: {moon_size}")
        
        # Interactive chat
        await agent.interactive()

if __name__ == "__main__":
    # Set up BAF API credentials from environment variables
    baf.configure(
        client_id=os.environ.get("BAF_CLIENT_ID"),
        client_secret=os.environ.get("BAF_CLIENT_SECRET"),
        token_url=os.environ.get("BAF_AUTH_URL"),
        api_url=os.environ.get("BAF_API_BASE_URL")
    )
    
    asyncio.run(main())
```

### Document Assistant

Create an agent that can answer questions about documents:

```python
import asyncio
import os
from baf_agent import BAFAgent

# Create the application
baf = BAFAgent("Document Assistant")

@baf.agent(instruction="You are an assistant that helps answer questions about documents.")
async def main(agent_ctx):
    # Create the agent
    async with agent_ctx as agent:
        # Add a document tool
        doc_tool_id = await baf.add_tool(
            name="Document Tool",
            tool_type="document"
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
        
        resource_id = await baf.add_document(
            tool_name="Document Tool",
            doc_name="Q3 Financial Report",
            content=sample_content,
            content_type="text/markdown"
        )
        
        print("Document added successfully. You can now ask questions about it.")
        
        # Interactive chat
        await agent.interactive()

if __name__ == "__main__":
    # Configure BAF credentials
    baf.configure(
        client_id=os.environ.get("BAF_CLIENT_ID"),
        client_secret=os.environ.get("BAF_CLIENT_SECRET"),
        token_url=os.environ.get("BAF_AUTH_URL"),
        api_url=os.environ.get("BAF_API_BASE_URL")
    )
    
    asyncio.run(main())
```

### JSON Output

Create an agent that returns structured JSON data:

```python
import asyncio
import json
import os
from baf_agent import BAFAgent

# Create the application
baf = BAFAgent("Product Analyzer")

# Define a JSON schema for product analysis
PRODUCT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Product analysis result",
    "type": "object",
    "properties": {
        "productName": {
            "type": "string",
            "description": "The name of the product"
        },
        "estimatedPrice": {
            "type": "number",
            "description": "The estimated price in USD"
        },
        "features": {
            "type": "array",
            "description": "List of key product features",
            "items": {
                "type": "string"
            }
        },
        "rating": {
            "type": "number",
            "description": "Rating from 1-10",
            "minimum": 1,
            "maximum": 10
        }
    },
    "required": [
        "productName",
        "estimatedPrice",
        "features",
        "rating"
    ]
}

@baf.agent(
    instruction="You are a product analyst expert. Analyze products and provide structured information.",
    defaultOutputFormat="JSON", 
    defaultOutputFormatOptions=json.dumps(PRODUCT_SCHEMA)
)
async def main(agent_ctx):
    async with agent_ctx as agent:
        # Example of getting a structured JSON response
        product_info = await agent("Analyze Apple iPhone 14")
        
        # Parse the result
        result = json.loads(product_info)
        print(f"Name: {result['productName']}")
        print(f"Price: ${result['estimatedPrice']}")
        
        # Interactive mode
        await agent.interactive()

if __name__ == "__main__":
    # Configure BAF
    baf.configure(
        client_id=os.environ.get("BAF_CLIENT_ID"),
        client_secret=os.environ.get("BAF_CLIENT_SECRET"),
        token_url=os.environ.get("BAF_AUTH_URL"),
        api_url=os.environ.get("BAF_API_BASE_URL")
    )
    
    asyncio.run(main())
```

## API Reference

### BAFAgent Class

```python
BAFAgent(name: str = "BAF Agent Wrapper")
```

The main class for creating and managing BAF agents.

#### Methods

- `configure(client_id: str, client_secret: str, token_url: str, api_url: str)`: Configure BAF API credentials
- `add_tool(name: str, tool_type: str, **kwargs) -> str`: Add a tool to the agent
- `add_document(tool_name: str, doc_name: str, content: Union[str, bytes], content_type: str = "text/plain") -> str`: Add a document resource to a document tool
- `agent(instruction: str = None, **kwargs)`: Decorator to create a BAF agent
- `run()`: Context manager for running the agent

### AgentInterface Class

```python
AgentInterface(baf_agent: BAFAgent, client: httpx.AsyncClient)
```

Interface for interacting with a BAF Agent, returned by the context manager.

#### Methods

- `__call__(message: str, output_format: str = "Markdown", output_format_options: str = None) -> str`: Send a message to the agent
- `interactive()`: Start an interactive chat session with the agent
- `continue_message(history_id: str, observation: str) -> str`: Continue a message that was interrupted by a tool
- `cancel()`: Cancel the current chat

## Setting Up BAF API Credentials

To use this wrapper, you need to obtain BAF API credentials:

1. Create a Project Agent Builder service instance in your BTP subaccount
2. Create a service key for the service instance
3. Extract the required credentials from the service key

For more information, see the [Project Agent Builder API documentation](https://your-documentation-url.com).

## Limitations

- This wrapper is designed for simple agent usage. For more advanced use cases, you may need to use the BAF API directly.
- Error handling is minimal and should be expanded for production use.
- The wrapper doesn't support all BAF API features, such as custom models or bring-your-own tools.

## License

MIT 