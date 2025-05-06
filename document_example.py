import asyncio
from pab_client import PABClient, ToolType

# Create the application
pab = PABClient("Document Assistant")

async def main():
    # Create the agent
    agent = await pab.create_agent(
        initial_instructions="You are an assistant that helps answer questions about documents."
    )
    
    # Add a document tool
    await agent.list_tools()  # Make sure tools are initialized
    
    # Add a sample document
    sample_content = """
    # Project Overview
    
    This document provides information about our company's Q3 financial results.
    
    ## Revenue
    
    Total revenue: $5.2 million
    Growth from Q2: 15%
    
    ## Expenses
    
    Total expenses: $3.8 million
    Major categories:
    - Salaries: $2.1 million
    - Marketing: $0.7 million
    - Operations: $1.0 million
    
    ## Profit
    
    Net profit: $1.4 million
    Profit margin: 26.9%
    """
    
    await agent.add_document(
        doc_name="Q3 Financial Report",
        content=sample_content,
        content_type="text/markdown"
    )
    
    print("Document added successfully. You can now ask questions about it.")
    
    # Interactive chat
    await agent.interactive()

if __name__ == "__main__":
    # PABClient now loads environment variables automatically
    asyncio.run(main()) 