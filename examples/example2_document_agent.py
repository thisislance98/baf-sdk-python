#!/usr/bin/env python3
"""
Example 2: Creating an Agent with Document Knowledge

This example demonstrates how to create an agent with access to document-based knowledge.
"""

import os
import uuid
import time
import requests
import urllib.parse
from dotenv import load_dotenv
from baf_sdk import AgentBuilderClient, Agent, Chat, Tool, Resource, ToolType
from baf_sdk.models import Message, ChatState

# Load environment variables from .env file
load_dotenv()

# Get authentication details from environment variables
AUTH_URL = os.environ.get("BAF_AUTH_URL")
API_BASE_URL = os.environ.get("BAF_API_BASE_URL")
CLIENT_ID = os.environ.get("BAF_CLIENT_ID")
CLIENT_SECRET = os.environ.get("BAF_CLIENT_SECRET")

# Path to your PDF document
DOCUMENT_PATH = "data/technical_manual.pdf"  # Update this path to your document

def main():
    # Create a client with authentication details
    client = AgentBuilderClient(
        auth_url=AUTH_URL,
        api_base_url=API_BASE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    # Check if "Document Assistant" agent already exists
    print("Checking for existing document assistant agent...")
    agents = client.list_agents()
    existing_agent = next((agent for agent in agents if agent.name == "Document Assistant"), None)

    if existing_agent:
        print(f"Found existing agent: {existing_agent.name} (ID: {existing_agent.id})")
        created_agent = existing_agent
    else:
        # Create an agent
        print("Creating document assistant agent...")
        agent = Agent(
            name="Document Assistant",
            expert_in="Technical documentation",
            initial_instructions="You are an assistant that helps users understand information in technical documents."
        )
        created_agent = client.create_agent(agent)
        print(f"Created new agent: {created_agent.name} (ID: {created_agent.id})")

    # Check if the tool already exists for this agent
    print("\nChecking for existing document tool...")
    tools = client.list_tools(created_agent.id)
    existing_tool = next((tool for tool in tools if tool.name == "Technical Manuals"), None)

    if existing_tool:
        print(f"Found existing tool: {existing_tool.name} (ID: {existing_tool.id})")
        created_tool = existing_tool
    else:
        # Create a document tool for the agent
        print("\nCreating document tool...")
        document_tool = Tool(
            name="Technical Manuals",
            type=ToolType.DOCUMENT
        )
        created_tool = client.create_tool(created_agent.id, document_tool)
        print(f"Created new tool: {created_tool.name} (ID: {created_tool.id})")

        # Upload a PDF document as a resource
        print("\nUploading document...")
        with open(DOCUMENT_PATH, "rb") as f:
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
        print(f"Created resource: {created_resource.name} (ID: {created_resource.id})")

        # Wait for the resource to be processed
        print("\nWaiting for resource to be processed...")
        ready_resource = client.wait_for_resource_ready(
            created_agent.id, 
            created_tool.id, 
            created_resource.id,
            max_attempts=60,
            interval=5
        )
        print(f"Resource state: {ready_resource.state.value}")

        # Wait for the tool to be ready
        print("\nWaiting for tool to be ready...")
        ready_tool = client.wait_for_tool_ready(
            created_agent.id,
            created_tool.id
        )
        print(f"Tool is ready: {ready_tool.state}")

    # Check if a chat already exists for this agent
    print("\nChecking for existing document chat...")
    chats = client.list_chats(created_agent.id)
    existing_chat = next((chat for chat in chats if chat.name.startswith("Document Questions")), None)
    
    if existing_chat:
        print(f"Found existing chat: {existing_chat.name} (ID: {existing_chat.id})")
        created_chat = existing_chat
    else:
        # Create a new chat session with a unique name
        print("\nCreating chat for document questions...")
        unique_chat_name = f"Document Questions-{str(uuid.uuid4())[:8]}"
        chat = Chat(name=unique_chat_name)
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Created new chat: {created_chat.name} (ID: {created_chat.id})")

    # Ask a question about the document
    question = "What are the system requirements described in the manual?"
    print(f"\nSending question: {question}")
    history_id = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=question,
        async_mode=True
    )
    
    # Wait for response (custom implementation to work around SDK issue)
    print("Waiting for response...")
    max_attempts = 60
    interval = 3
    
    for attempt in range(max_attempts):
        try:
            # First, check the chat state
            chat = client.get_chat(created_agent.id, created_chat.id)
            if chat.state:
                print(f"Chat state: {chat.state}")
            
            if chat.state == ChatState.FAILED:
                print("Chat processing failed")
                break
                
            # Use direct API call to get messages
            headers = client._get_headers()
            url = f"{client.api_base_url}/api/v1/Agents({created_agent.id})/chats({created_chat.id})/history"
            
            # Get all messages in the chat
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                messages = response.json().get("value", [])
                
                # Find the response message that has our history_id as previous ID
                for msg in messages:
                    previous = msg.get("previous", {})
                    prev_id = previous.get("ID") if isinstance(previous, dict) else None
                    
                    if prev_id == history_id:
                        message = Message.from_api_dict(msg)
                        print(f"\nResponse: {message.content}")
                        return
            
            # If the chat is in SUCCESS state but we haven't found the response message yet,
            # list all messages and look for the most recent AI response
            if chat.state == ChatState.SUCCESS:
                print("\nChat completed successfully.")
                all_messages = client.list_messages(created_agent.id, created_chat.id)
                
                # First try to find direct response to our question
                for msg in all_messages:
                    if hasattr(msg, 'previous') and msg.previous and msg.previous.id == history_id:
                        print(f"\nFound response: {msg.content}")
                        return
                
                # If no direct response, get the most recent AI message
                ai_messages = [msg for msg in all_messages if msg.role == "ai" or msg.role == "assistant"]
                if ai_messages:
                    print(f"\nLatest AI response: {ai_messages[-1].content}")
                    return
                    
            if chat.state == ChatState.RUNNING or chat.state == ChatState.PROCESSING:
                print(f"Chat is still processing... (attempt {attempt+1}/{max_attempts})")
            else:
                print(f"Waiting for response... (attempt {attempt+1}/{max_attempts})")
                
            time.sleep(interval)
        except Exception as e:
            print(f"Error during polling: {str(e)}")
            time.sleep(interval)
    
    print(f"No response received after {max_attempts} attempts")

if __name__ == "__main__":
    main() 