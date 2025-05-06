#!/usr/bin/env python3
"""
Example 1: Creating a Simple Question-Answering Agent

This example shows how to create a basic agent and have a conversation with it.
"""

import time
import logging
from baf_sdk import AgentBuilderClient, Agent, Chat, OutputFormat
from baf_sdk.models import ChatState

def main():
    # Configure logging - setting to INFO level to reduce verbosity
    logging.basicConfig(
        level=logging.INFO,  # Changed from DEBUG to INFO to reduce verbosity
        format='%(levelname)s: %(message)s'  # Simplified format
    )
    logger = logging.getLogger("baf_sdk")
    logger.setLevel(logging.WARNING)  # Only show warnings and errors from the SDK
    
    # Print welcome message
    print("======= Basic Agent Example ========")
    print("This example creates a general assistant and asks it two questions.\n")

    # Create a client - authentication details will be loaded from environment variables
    client = AgentBuilderClient()

    # Create or update an agent
    agent = Agent(
        name="General Assistant",
        expert_in="General knowledge",
        initial_instructions="You are a helpful assistant that provides accurate and concise answers."
    )

    # The create_agent method will check if the agent already exists and update it
    created_agent = client.create_agent(agent)
    print(f"Using agent: {created_agent.name} (ID: {created_agent.id})")

    # Create or reuse an existing chat
    chat = Chat(name="General Questions")
    created_chat = client.create_chat(created_agent.id, chat)
    print(f"Using chat: {created_chat.name} (ID: {created_chat.id})\n")

    # Wait for chat to be ready before sending a message
    max_wait_attempts = 10
    wait_interval = 1  # seconds
    
    # Simple function to wait for chat to be in a usable state
    def wait_for_chat_ready(agent_id, chat_id):
        print("Waiting for chat to be ready...")
        for attempt in range(max_wait_attempts):
            current_chat_state = client.get_chat(agent_id, chat_id).state
            
            if current_chat_state in [ChatState.SUCCESS.value, ChatState.RUNNING.value, 
                                      ChatState.ACTIVE.value, ChatState.NONE.value]:
                return True
                
            if current_chat_state == ChatState.FAILED.value:
                print("ERROR: Chat failed to initialize")
                return False
                
            print(".", end="", flush=True)
            time.sleep(wait_interval)
            
        print("\nWarning: Chat didn't reach ready state")
        return False
    
    # Wait for chat to be ready
    if not wait_for_chat_ready(created_agent.id, created_chat.id):
        return

    # Send first question - Synchronous mode
    question1 = "What are the main differences between Python 2 and Python 3?"
    print("\n\n===== QUESTION 1 (Synchronous) =====")
    print(f"User: {question1}")
    
    # Get answer in synchronous mode (blocking until response is received)
    answer = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=question1,
        async_mode=False
    )
    
    print(f"\nAssistant:\n{answer}\n")

    # Wait for chat to be ready again before sending the second message
    time.sleep(2)  # Small pause for better UX
    
    if not wait_for_chat_ready(created_agent.id, created_chat.id):
        return
        
    # Send second question - Asynchronous mode
    question2 = "What are the main applications of machine learning?"
    print("\n===== QUESTION 2 (Asynchronous) =====")
    print(f"User: {question2}")
    
    # Send the message asynchronously
    history_id = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=question2,
        async_mode=True
    )
    
    # Wait for and display the response
    print("Waiting for response...", end="", flush=True)
    
    try:
        # wait_for_message_response polls until the response is available
        response_message = client.wait_for_message_response(
            agent_id=created_agent.id,
            chat_id=created_chat.id,
            history_id=history_id,
            max_attempts=30,
            interval=2
        )
        print("\n\nAssistant:\n" + response_message.content)
    except Exception as e:
        print(f"\nError getting response: {e}")
    
    print("\n======= Example Complete ========")

if __name__ == "__main__":
    main() 