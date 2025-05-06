import asyncio
import os
from dotenv import load_dotenv
from pab_client import PABClient

# Load environment variables from .env file
load_dotenv()

# Create the application
pab = PABClient("PAB Example with dotenv")

async def main():
    # Create the agent
    agent = await pab.create_agent(
        initial_instructions="You are a helpful assistant."
    )
    
    print("Agent created successfully!")
    await agent.interactive()

if __name__ == "__main__":
    # Configure PAB with credentials from .env file
    pab.configure(
        client_id=os.environ.get("PAB_CLIENT_ID"),
        client_secret=os.environ.get("PAB_CLIENT_SECRET"),
        token_url=os.environ.get("PAB_AUTH_URL"),
        api_url=os.environ.get("PAB_API_BASE_URL")
    )
    
    asyncio.run(main()) 