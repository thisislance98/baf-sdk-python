import asyncio
import json
import os
from pab_client import PABClient, OutputFormat

# Create the application
pab = PABClient("Product Analyzer")

# Define a JSON schema for product analysis
PRODUCT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Product analysis result",
    "type": "object",
    "properties": {
        "productName": {
            "type": "string",
            "description": "The name of the product"
        },
        "estimatedPrice": {
            "type": "number",
            "description": "The estimated price in USD"
        },
        "features": {
            "type": "array",
            "description": "List of key product features",
            "items": {
                "type": "string"
            }
        },
        "targetAudience": {
            "type": "string",
            "description": "The primary target audience for this product"
        },
        "rating": {
            "type": "number",
            "description": "Rating from 1-10",
            "minimum": 1,
            "maximum": 10
        }
    },
    "required": [
        "productName",
        "estimatedPrice",
        "features",
        "rating"
    ]
}

async def main():
    # Create the agent
    agent = await pab.create_agent(
        initial_instructions="You are a product analyst expert. Analyze products and provide structured information.",
        default_output_format=OutputFormat.JSON,
        default_output_format_options=json.dumps(PRODUCT_SCHEMA)
    )
    
    # Example of getting a structured JSON response
    product_info = await agent("Analyze Apple iPhone 14")
    
    # Parse the result
    try:
        result = json.loads(product_info)
        print("Product Analysis Result:")
        print(f"Name: {result['productName']}")
        print(f"Price: ${result['estimatedPrice']}")
        print(f"Rating: {result['rating']}/10")
        print("Features:")
        for feature in result['features']:
            print(f"- {feature}")
        print(f"Target Audience: {result.get('targetAudience', 'Not specified')}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response:")
        print(product_info)
        
    # Continue with interactive mode
    print("\nYou can now analyze other products interactively.")
    await agent.interactive()

if __name__ == "__main__":
    # Set up PAB API credentials from environment variables
    pab.configure(
        client_id=os.environ.get("PAB_CLIENT_ID"),
        client_secret=os.environ.get("PAB_CLIENT_SECRET"),
        token_url=os.environ.get("PAB_AUTH_URL"),
        api_url=os.environ.get("PAB_API_BASE_URL")
    )
    
    asyncio.run(main()) 