#!/usr/bin/env python3
"""
Test using send_message method of AgentInterface
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import from parent directory
from baf_client import BAFClient, ModelType, AgentType, OutputFormat

async def test_send_message():
    """Test sending messages to an agent with different output formats"""
    try:
        print("Starting send message test...")
        
        # Get the path to the credentials file in the parent directory
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        credentials_path = parent_dir / "agent-binding.json"
        
        print(f"Creating BAF Agent wrapper with credentials from {credentials_path}...")
        baf = BAFClient(str(credentials_path), "Send Message Test")
        
        print("Creating agent...")
        agent = await baf.create_agent(
            initial_instructions="You are a helpful assistant that responds to questions.",
            expert_in="Answering questions about different topics",
            agent_type=AgentType.SMART,
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        print("Agent created successfully!")
        
        # Test using __call__ method (traditional way)
        print("\nTesting with __call__ method...")
        call_response = await agent("What is the capital of France?")
        print(f"Response using __call__: {call_response}")
        
        # Test using send_message method (explicit method)
        print("\nTesting with send_message method...")
        message_response = await agent.send_message("What is the capital of Germany?")
        print(f"Response using send_message: {message_response}")
        
        # Test different output formats with send_message
        print("\nTesting send_message with TEXT format...")
        text_response = await agent.send_message(
            "List three planets in our solar system.", 
            output_format=OutputFormat.TEXT
        )
        print(f"Text response: {text_response}")
        
        print("\nTesting send_message with JSON format...")
        json_response = await agent.send_message(
            "Give me the population of 3 European capitals.", 
            output_format=OutputFormat.JSON
        )
        print(f"JSON response: {json_response}")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_send_message()) 