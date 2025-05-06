#!/usr/bin/env python3
"""
Run a single PAB agent test with more detailed error reporting
"""

import asyncio
import traceback
import json
from pab_client import PABClient, AgentType, ModelType

async def test_create_simple_agent():
    """Test creating a simple agent with verbose error output"""
    try:
        print("Creating PAB Client...")
        pab = PABClient("Simple Test Agent")
        
        # Let's first check authentication is working
        print("Testing authentication...")
        await pab._get_token()
        print("Authentication successful!")
        
        # Configure client with extra debugging
        client = await pab._get_client()
        
        print("Creating simple agent with minimal configuration...")
        agent_config = {
            "name": "Simple Test Agent",
            "type": AgentType.OPENAI.value,
            "expertIn": "Testing",
            "initialInstructions": "You are a test agent."
        }
        
        print(f"Agent config: {json.dumps(agent_config, indent=2)}")
        
        try:
            response = await client.post("/api/v1/Agents", json=agent_config)
            response.raise_for_status()
            agent_id = response.json()["ID"]
            print(f"Created agent with ID: {agent_id}")
        except Exception as e:
            print(f"Error creating agent: {str(e)}")
            print(f"Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            print(f"Response body: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
            
    except Exception as e:
        print(f"Error in test: {str(e)}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_create_simple_agent()) 