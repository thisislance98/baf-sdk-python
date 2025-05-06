#!/usr/bin/env python3
"""
Example: JSON Output Format

This example demonstrates how to:
1. Create an agent with a websearch tool
2. Request responses in JSON format using a schema
3. Process structured data from the agent
"""

import os
import sys
import time
import json

# Add the parent directory to the path to import the SDK if not installed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baf_sdk import AgentBuilderClient, Agent, Chat, Tool, ToolType, OutputFormat
from baf_sdk.exceptions import ApiError, ResourceNotReadyError, TimeoutError


# Configuration - Replace with your own values
AUTH_URL = "https://your-auth-url/oauth/token"
API_BASE_URL = "https://your-api-base-url"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"


def main():
    """Main function to demonstrate JSON output format."""
    
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
        name=f"JSON Output Agent {time.strftime('%Y-%m-%d %H:%M:%S')}",
        expert_in="You are an expert in providing structured data about various topics.",
        iterations=20
    )
    created_agent = client.create_agent(agent)
    print(f"Agent created with ID: {created_agent.id}")
    
    # Create a websearch tool (optional)
    print("Creating websearch tool...")
    tool = Tool(name="Web Search", type=ToolType.WEBSEARCH)
    created_tool = client.create_tool(created_agent.id, tool)
    print(f"Tool created with ID: {created_tool.id}")
    
    # Wait for tool to be ready
    print("Waiting for tool to be ready...")
    try:
        client.wait_for_tool_ready(
            created_agent.id,
            created_tool.id,
            max_attempts=20,
            interval=3
        )
        
        # Create a chat
        print("Creating chat...")
        chat = Chat(name=f"JSON Output Chat {time.strftime('%Y-%m-%d %H:%M:%S')}")
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Chat created with ID: {created_chat.id}")
        
        # Define a JSON schema for country information
        country_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "The name of the country"
                },
                "capital": {
                    "type": "string",
                    "description": "The capital city of the country"
                },
                "population": {
                    "type": "number",
                    "description": "The population of the country in millions"
                },
                "languages": {
                    "type": "array",
                    "description": "Official languages spoken in the country",
                    "items": {
                        "type": "string"
                    }
                },
                "currency": {
                    "type": "string",
                    "description": "The official currency of the country"
                }
            },
            "required": ["country", "capital"]
        }
        
        # Convert schema to string
        schema_str = json.dumps(country_schema)
        
        # List of countries to query
        countries = ["France", "Japan", "Brazil"]
        
        for country in countries:
            print(f"\nQuerying information about: {country}")
            query = f"Provide information about {country}"
            
            # Send the message with JSON output format
            history_id = client.send_message(
                created_agent.id,
                created_chat.id,
                query,
                output_format=OutputFormat.JSON,
                output_format_options=schema_str,
                async_mode=True
            )
            
            print("Waiting for response...")
            response = client.wait_for_message_response(
                created_agent.id,
                created_chat.id,
                history_id
            )
            
            # Parse the JSON response
            try:
                data = json.loads(response.content)
                
                print(f"Information about {country}:")
                print("-" * 40)
                print(f"Capital: {data.get('capital', 'N/A')}")
                print(f"Population: {data.get('population', 'N/A')} million")
                
                languages = data.get('languages', [])
                if languages:
                    print(f"Languages: {', '.join(languages)}")
                    
                print(f"Currency: {data.get('currency', 'N/A')}")
                print("-" * 40)
                
                # Raw JSON for reference
                print("Raw JSON response:")
                print(json.dumps(data, indent=2))
                print()
                
            except json.JSONDecodeError:
                print("Error: Could not decode JSON response")
                print("Raw response:")
                print(response.content)
    
    except ResourceNotReadyError as e:
        print(f"Error: Tool failed to become ready: {e}")
    except TimeoutError as e:
        print(f"Error: Operation timed out: {e}")
    except ApiError as e:
        print(f"Error: API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main() 