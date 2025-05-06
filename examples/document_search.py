#!/usr/bin/env python3
"""
Example: Document Search

This example demonstrates how to:
1. Create an agent with a document tool
2. Upload a simple text document
3. Ask questions about the document
"""

import os
import sys
import time
import base64

# Add the parent directory to the path to import the SDK if not installed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baf_sdk import AgentBuilderClient, Agent, Chat, Tool, Resource, ToolType
from baf_sdk.exceptions import ApiError, ResourceNotReadyError, TimeoutError


# Configuration - Replace with your own values
AUTH_URL = "https://your-auth-url/oauth/token"
API_BASE_URL = "https://your-api-base-url"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"


def main():
    """Main function to demonstrate document search."""
    
    # Create a client
    print("Creating client...")
    client = AgentBuilderClient(
        auth_url=AUTH_URL,
        api_base_url=API_BASE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    # Create an agent
    print("Creating agent...")
    agent = Agent(
        name=f"Document Search Agent {time.strftime('%Y-%m-%d %H:%M:%S')}",
        expert_in="You are an expert in finding information in documents.",
        iterations=20
    )
    created_agent = client.create_agent(agent)
    print(f"Agent created with ID: {created_agent.id}")
    
    # Create a document tool
    print("Creating document tool...")
    tool = Tool(name="Document Tool", type=ToolType.DOCUMENT)
    created_tool = client.create_tool(created_agent.id, tool)
    print(f"Tool created with ID: {created_tool.id}")
    
    # Create a simple text document as a resource
    print("Creating document resource...")
    document_content = """
    # Product Catalog
    
    ## Fruits
    1. Apple - $1.99/lb
    2. Banana - $0.59/lb
    3. Orange - $1.29/lb
    4. Grapes - $2.99/lb
    5. Strawberry - $3.99/box
    
    ## Vegetables
    1. Carrot - $1.49/lb
    2. Broccoli - $2.99/head
    3. Spinach - $3.99/bag
    4. Tomato - $2.49/lb
    5. Cucumber - $0.99/each
    
    ## Bakery
    1. Bread - $2.99/loaf
    2. Bagel - $0.89/each
    3. Muffin - $1.49/each
    4. Cake - $15.99/each
    5. Cookie - $0.99/each
    """
    
    resource = Resource(
        name="Product Catalog",
        content_type="text/plain"
    )
    
    created_resource = client.create_resource(
        created_agent.id,
        created_tool.id,
        resource,
        document_content.encode('utf-8')
    )
    print(f"Resource created with ID: {created_resource.id}")
    
    try:
        # Wait for resource to be ready
        print("Waiting for resource to be ready...")
        client.wait_for_resource_ready(
            created_agent.id,
            created_tool.id,
            created_resource.id,
            max_attempts=20,
            interval=3
        )
        
        # Wait for tool to be ready
        print("Waiting for tool to be ready...")
        client.wait_for_tool_ready(
            created_agent.id,
            created_tool.id,
            max_attempts=20,
            interval=3
        )
        
        # Create a chat
        print("Creating chat...")
        chat = Chat(name=f"Product Questions {time.strftime('%Y-%m-%d %H:%M:%S')}")
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Chat created with ID: {created_chat.id}")
        
        # Ask a question
        questions = [
            "What is the price of apples?",
            "What is the most expensive fruit?",
            "List all bakery items and their prices."
        ]
        
        for question in questions:
            print(f"\nSending question: '{question}'")
            history_id = client.send_message(
                created_agent.id,
                created_chat.id,
                question,
                async_mode=True
            )
            
            print("Waiting for response...")
            response = client.wait_for_message_response(
                created_agent.id,
                created_chat.id,
                history_id
            )
            
            print("Response:")
            print("-" * 40)
            print(response.content)
            print("-" * 40)
    
    except ResourceNotReadyError as e:
        print(f"Error: Resource failed to become ready: {e}")
    except TimeoutError as e:
        print(f"Error: Operation timed out: {e}")
    except ApiError as e:
        print(f"Error: API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main() 