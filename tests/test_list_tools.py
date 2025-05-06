#!/usr/bin/env python
"""
Test script to demonstrate how to list tools from a BAF agent.
"""

import asyncio
import os
import sys
from pprint import pprint
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_list_tools():
    """Create a BAF agent and list the available tools."""
    # Path to credentials file - update this to your actual file path
    # Or set the environment variable BAF_CREDENTIALS_PATH
    
    # Check if BAF_CREDENTIALS_PATH is set in the environment
    credentials_path = os.environ.get("BAF_CREDENTIALS_PATH")
    
    if not credentials_path:
        print("ERROR: BAF_CREDENTIALS_PATH environment variable is not set.")
        print("Please set it to the path of your credentials.json file:")
        print("  export BAF_CREDENTIALS_PATH=/path/to/your/credentials.json")
        return
        
    # Check if the file exists
    if not os.path.exists(credentials_path):
        print(f"ERROR: Credentials file not found at: {credentials_path}")
        return
    
    # Create an agent
    print(f"Initializing BAF client with credentials from: {credentials_path}")
    baf_client = BAFClient(credentials_path, name="Tool Lister Test")
    
    try:
        # Create a basic agent
        print("Creating agent...")
        agent = await baf_client.create_agent(
            initial_instructions="You are a helpful assistant with various tools.",
            expert_in="Helping users with information",
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        # Add a document tool if there are no tools
        if not baf_client._tools:
            print("Adding document tool...")
            try:
                await agent.add_document(
                    "test_document.txt", 
                    "This is a test document to ensure we have at least one tool.",
                    "text/plain"
                )
                print("Document tool added successfully")
            except Exception as e:
                print(f"Error adding document tool: {e}")
        
        # List all tools with full details
        print("\nListing all tools with full details:")
        try:
            tools = await agent.list_tools()
            print(f"Found {len(tools)} tools:")
            pprint(tools)
        except Exception as e:
            print(f"Error listing tools: {e}")
        
        # Get just the tool names
        print("\nGetting just the tool names:")
        try:
            tool_names = await agent.get_tool_names()
            print(f"Tool names: {tool_names}")
        except Exception as e:
            print(f"Error getting tool names: {e}")
        
        # Send a message to the agent asking about its tools
        print("\nAsking the agent about its tools...")
        try:
            response = await agent("What tools do you have access to?")
            print(f"Agent response:\n{response}")
        except Exception as e:
            print(f"Error sending message to agent: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if 'agent' in locals() and hasattr(agent.client, 'aclose'):
            await agent.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_list_tools()) 