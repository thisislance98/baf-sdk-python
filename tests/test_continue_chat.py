#!/usr/bin/env python3
"""
Test continuing a conversation with an existing chat ID
"""

import asyncio
from baf_client import BAFAgent, OutputFormat, ModelType, AgentType

async def test_continue_chat():
    """Test creating an agent, having a conversation, then continuing it with a new interface"""
    try:
        credentials_path = "agent-binding.json"
        print(f"Creating BAF Agent wrapper with credentials from {credentials_path}...")
        baf = BAFAgent(credentials_path, "Continue Chat Test")
        
        print("Creating agent for first conversation...")
        agent = await baf.create_agent(
            initial_instructions="You are a helpful assistant that remembers our conversation.",
            expert_in="Remembering context and previous information",
            agent_type=AgentType.SMART,
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )

        # Save the agent and chat IDs for later
        agent_id = baf._agent_id
        chat_id = baf._chat_id
        
        print(f"Agent created with ID: {agent_id}")
        print(f"Chat created with ID: {chat_id}")
        
        # First part of the conversation
        print("\nStarting first part of conversation...")
        response1 = await agent("Hello, I'd like to discuss Python programming. Remember that my name is Alice.")
        print(f"Agent: {response1}")
        
        response2 = await agent("What are three key features of Python?")
        print(f"Agent: {response2}")
        
        # Create a new agent interface using the same agent_id and chat_id
        print("\nSimulating a new session with the same chat...")
        print("Creating new BAF wrapper...")
        new_baf = BAFAgent(credentials_path, "Continue Chat Test (New Session)")
        
        print(f"Getting existing agent with ID: {agent_id}")
        # Continue with the existing chat ID
        continued_agent = await new_baf.get_agent(agent_id, chat_id)
        
        # Continue the conversation
        print("\nContinuing conversation...")
        response3 = await continued_agent("Can you remind me of my name? And what were we discussing?")
        print(f"Agent: {response3}")
        
        # Test that context is maintained
        print("\nVerifying that context is maintained...")
        response4 = await continued_agent("What programming language were we discussing?")
        print(f"Agent: {response4}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_continue_chat()) 