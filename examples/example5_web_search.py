#!/usr/bin/env python3
"""
Example 5: Creating a Web Search Agent

This example shows how to create an agent that can search the web for information.
"""

import os
import uuid
from baf_sdk import AgentBuilderClient, Agent, Chat, Tool, ToolType

# Get authentication details from environment variables
# Remember to set these in your environment or .env file
AUTH_URL = os.environ.get("BAF_AUTH_URL")
API_BASE_URL = os.environ.get("BAF_API_BASE_URL")
CLIENT_ID = os.environ.get("BAF_CLIENT_ID")
CLIENT_SECRET = os.environ.get("BAF_CLIENT_SECRET")

def main():
    # Create a client with authentication details
    client = AgentBuilderClient(
        auth_url=AUTH_URL,
        api_base_url=API_BASE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    # Check if "Research Assistant" agent already exists
    print("Checking for existing research assistant agent...")
    agents = client.list_agents()
    existing_agent = next((agent for agent in agents if agent.name == "Research Assistant"), None)

    if existing_agent:
        print(f"Found existing agent: {existing_agent.name} (ID: {existing_agent.id})")
        created_agent = existing_agent
    else:
        # Create an agent with web search capability
        print("Creating research assistant agent...")
        agent = Agent(
            name="Research Assistant",
            expert_in="Online research",
            initial_instructions="You are a research assistant that can search the web for current information."
        )
        created_agent = client.create_agent(agent)
        print(f"Created new agent: {created_agent.name} (ID: {created_agent.id})")

    # Check if the web search tool already exists
    print("\nChecking for existing web search tool...")
    tools = client.list_tools(created_agent.id)
    existing_tool = next((tool for tool in tools if tool.name == "Web Search"), None)

    if existing_tool:
        print(f"Found existing tool: {existing_tool.name} (ID: {existing_tool.id})")
        created_tool = existing_tool
    else:
        # Create a web search tool
        print("\nCreating web search tool...")
        web_tool = Tool(
            name="Web Search",
            type=ToolType.WEBSEARCH
        )
        created_tool = client.create_tool(created_agent.id, web_tool)
        print(f"Created new tool: {created_tool.name} (ID: {created_tool.id})")

    # Check if a chat already exists for this agent
    print("\nChecking for existing research chat...")
    chats = client.list_chats(created_agent.id)
    existing_chat = next((chat for chat in chats if chat.name == "Research Chat"), None)
    
    if existing_chat:
        print(f"Found existing chat: {existing_chat.name} (ID: {existing_chat.id})")
        created_chat = existing_chat
    else:
        # Create a new chat session with a unique name
        print("\nCreating research chat...")
        unique_chat_name = f"Research Chat-{str(uuid.uuid4())[:8]}"
        chat = Chat(name=unique_chat_name)
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Created new chat: {created_chat.name} (ID: {created_chat.id})")

    # Ask a question that might require current information
    query = "What are the latest developments in quantum computing?"
    print(f"\nSending research question: {query}")
    history_id = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=query,
        async_mode=True
    )

    # Wait for response
    print("Waiting for response (this may take longer for web searches)...")
    response = client.wait_for_message_response(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        history_id=history_id,
        max_attempts=90,  # Web searches can take longer
        interval=5
    )
    print(f"Research results: {response.content}")

if __name__ == "__main__":
    main() 