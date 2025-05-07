#!/usr/bin/env python3
"""
Example 3: Working with Structured JSON Output

This example shows how to get structured JSON output from an agent.
"""

import os
import json
import uuid
from pab_sdk import AgentBuilderClient, Agent, Chat, OutputFormat

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

    # Check if "Data Extractor" agent already exists
    print("Checking for existing data extraction agent...")
    agents = client.list_agents()
    existing_agent = next((agent for agent in agents if agent.name == "Data Extractor"), None)

    if existing_agent:
        print(f"Found existing agent: {existing_agent.name} (ID: {existing_agent.id})")
        created_agent = existing_agent
    else:
        # Create an agent
        print("Creating data extraction agent...")
        agent = Agent(
            name="Data Extractor",
            expert_in="Information extraction",
            initial_instructions="You are an assistant that extracts structured information.",
            default_output_format=OutputFormat.JSON
        )
        created_agent = client.create_agent(agent)
        print(f"Created new agent: {created_agent.name} (ID: {created_agent.id})")

    # Check if a chat already exists for this agent
    print("\nChecking for existing data extraction chat...")
    chats = client.list_chats(created_agent.id)
    existing_chat = next((chat for chat in chats if chat.name == "Data Extraction"), None)
    
    if existing_chat:
        print(f"Found existing chat: {existing_chat.name} (ID: {existing_chat.id})")
        created_chat = existing_chat
    else:
        # Create a new chat session with a unique name
        print("\nCreating chat for data extraction...")
        unique_chat_name = f"Data Extraction-{str(uuid.uuid4())[:8]}"
        chat = Chat(name=unique_chat_name)
        created_chat = client.create_chat(created_agent.id, chat)
        print(f"Created new chat: {created_chat.name} (ID: {created_chat.id})")

    # Define a JSON schema for product information
    json_schema = """{
      "$schema": "http://json-schema.org/draft-07/schema#",
      "type": "object",
      "properties": {
        "product_name": {
          "type": "string",
          "description": "Name of the product"
        },
        "price": {
          "type": "number",
          "description": "Price in USD"
        },
        "features": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "List of product features"
        }
      },
      "required": ["product_name", "price", "features"]
    }"""

    # Send message requesting structured JSON output
    product_text = """
    The XDR-5000 Smart Speaker features voice control, multi-room audio, 
    and high-fidelity sound. With Bluetooth 5.0 and Wi-Fi connectivity, 
    it integrates with all major smart home systems. The speaker has 
    50W output power and includes a built-in voice assistant. 
    It's available for $199.99.
    """

    print("\nSending extraction request...")
    history_id = client.send_message(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        message=f"Extract product information from this text: {product_text}",
        output_format=OutputFormat.JSON,
        output_format_options=json_schema,
        async_mode=True
    )

    # Wait for structured response
    print("Waiting for response...")
    response = client.wait_for_message_response(
        agent_id=created_agent.id,
        chat_id=created_chat.id,
        history_id=history_id
    )

    print("\nRaw JSON response:")
    print(response.content)

    # The response.content will contain structured JSON data
    try:
        product_data = json.loads(response.content)
        print("\nExtracted product information:")
        print(f"Product Name: {product_data['product_name']}")
        print(f"Price: ${product_data['price']}")
        print("Features:")
        for feature in product_data['features']:
            print(f" - {feature}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print("Raw response content:")
        print(response.content)

if __name__ == "__main__":
    main() 