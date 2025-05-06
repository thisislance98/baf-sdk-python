#!/usr/bin/env python3
"""
A minimal test for the PAB SDK.

This example shows the most basic usage: creating an agent and sending a message.
"""

import os
import json
import time
import asyncio
import uuid
from pathlib import Path

try:
    import httpx
except ImportError:
    print("httpx not found. Install it with: pip install httpx")
    exit(1)

from pab_client import PABClient, ModelType, AgentType, OutputFormat

# Get the path to the credentials file
credentials_path = os.environ.get("AGENT_CREDENTIALS_PATH", "agent-binding.json")
if not os.path.exists(credentials_path):
    credentials_path = "agent-binding.json"

async def test_agent():
    # Create the PAB client
    pab = PABClient(credentials_path, "Minimal Test Agent")
    
    print("Creating agent...")
    agent = await pab.create_agent(
        initial_instructions="You are a helpful assistant who gives short responses.",
        expert_in="Providing concise answers",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O,
        safety_check=False,
        agent_type=AgentType.OPENAI  # Use OpenAI model
    )
    
    # Send a message and get a response
    print("Sending a simple message...")
    response = await agent("Write a haiku about coding")
    print(f"Agent response:\n{response}")
    
    # Try different output formats
    print("\nTesting different output formats...")
    
    # Markdown (default)
    response = await agent("Tell me about Python in one sentence.")
    print(f"\nMarkdown response:\n{response}")
    
    # Plain text
    text_response = await agent("Tell me about Java in one sentence.", 
                              output_format=OutputFormat.TEXT)
    print(f"\nText response:\n{text_response}")
    
    # JSON
    json_response = await agent("List three programming languages as a JSON array.", 
                             output_format=OutputFormat.JSON)
    print(f"\nJSON response:\n{json_response}")
    
    print("\nMinimal test completed successfully!")

if __name__ == "__main__":
    print("Starting minimal PAB SDK test...")
    asyncio.run(test_agent()) 