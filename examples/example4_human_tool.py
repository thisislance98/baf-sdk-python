#!/usr/bin/env python3
"""
Example 4: Using a Human Tool

This example demonstrates how to use a human-in-the-loop approach with the Human tool.
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

    # Check if "Human Assisted Agent" already exists
    print("Checking for existing human-assisted agent...")
    agents = client.list_agents()
    existing_agent = next((agent for agent in agents if agent.name == "Human Assisted Agent"), None)

    if existing_agent:
        print(f"Found existing agent: {existing_agent.name} (ID: {existing_agent.id})")
        created_agent = existing_agent
    else:
        # Create an agent with a human tool
        print("Creating human-assisted agent...")
        agent = Agent(
            name="Human Assisted Agent",
            expert_in="Problem solving with human assistance",
            initial_instructions="You are an assistant that can ask humans for help when needed."
        )
        created_agent = client.create_agent(agent)
        print(f"Created new agent: {created_agent.name} (ID: {created_agent.id})")

    # Check if the human tool already exists
    print("\nChecking for existing human tool...")
    tools = client.list_tools(created_agent.id)
    existing_tool = next((tool for tool in tools if tool.name == "Human Expert"), None)

    if existing_tool:
        print(f"Found existing tool: {existing_tool.name} (ID: {existing_tool.id})")
        created_tool = existing_tool
    else:
        # Create a human tool
        print("\nCreating human tool...")
        human_tool = Tool(
            name="Human Expert",
            type=ToolType.HUMAN
        )
        created_tool = client.create_tool(created_agent.id, human_tool)
        print(f"Created new tool: {created_tool.name} (ID: {created_tool.id})")

    # Check if a chat already exists for this agent
    print("\nChecking for existing human assistance chat...")
    chats = client.list_chats(created_agent.id)
    existing_chat = next((chat for chat in chats if chat.name == "Human Assistance Chat"), None)
    
    if existing_chat:
        print(f"Found existing chat: {existing_chat.name} (ID: {existing_chat.id})")
        created_chat = existing_chat
    else:
        # Create a new chat session with a unique name
        print("\nCreating chat for human assistance...")
        unique_chat_name = f"Human Assistance Chat-{str(uuid.uuid4())[:8]}"
        chat = Chat(name=unique_chat_name)
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Created new chat: {created_chat.name} (ID: {created_chat.id})")

    # Send a complex request
    complex_question = """
    I need help troubleshooting my custom hardware setup. 
    I have a Raspberry Pi connected to a temperature sensor, 
    but I'm not getting any readings. I've checked the wiring 
    and it seems correct. What should I try next?
    """

    print("\nSending complex question...")
    history_id = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=complex_question,
        async_mode=True
    )

    # Wait for the initial response (which may be a question for the human)
    print("Waiting for initial response (may include a question for human)...")
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
    
    print("\nHuman provides additional information:")
    print(human_answer)

    # Continue the conversation with the human's answer
    print("\nContinuing conversation with human's answer...")
    continuation_id = client.continue_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        history_id=response.id,
        observation=human_answer,
        async_mode=True
    )

    # Get the final response
    print("Waiting for final response...")
    final_response = client.wait_for_message_response(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        history_id=continuation_id
    )
    print(f"Final response: {final_response.content}")

if __name__ == "__main__":
    main() 