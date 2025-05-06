import asyncio
import os
from baf_client import BAFClient, ToolType, ModelType, OutputFormat

async def test_multiple_tools():
    """Test multiple BAF tools including calculator, document, and websearch"""
    # Initialize the BAF client
    client = BAFClient()
    
    # Create an agent with custom name and instructions
    agent = await client.create_agent(
        name="Multi-Tool Test Agent",
        initial_instructions="""
        You are a helpful assistant with access to multiple tools:
        1. Calculator - Use this for any mathematical calculations
        2. Document search - Use this to reference information in documents
        3. Web search - Use this for up-to-date information not in your knowledge
        
        Always use the appropriate tool when needed.
        """,
        expert_in="General assistance, calculations, and knowledge retrieval",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O,
        default_output_format=OutputFormat.MARKDOWN
    )
    
    # Add calculator tool
    await client.add_tool(
        name="calculator", 
        tool_type=ToolType.CALCULATOR
    )
    print("Added calculator tool")
    
    # Optionally add document tool with a sample document
    sample_document = """
    # Sample Financial Information
    
    Current interest rates for different investment vehicles:
    - Savings account: 0.5% APY
    - Certificate of Deposit (1 year): 2.3% APY
    - Treasury bonds (10 year): 4.1% yield
    - Corporate bonds (AA rated): 5.2% yield
    - Stock market average historical return: 7-10% annually
    
    Tax rates for 2023:
    - Income below $10,000: 10%
    - Income $10,001-$40,000: 12%
    - Income $40,001-$85,000: 22%
    - Income $85,001-$160,000: 24%
    """
    
    await agent.add_document(
        doc_name="financial_info.txt",
        content=sample_document
    )
    print("Added document tool with financial information")
    
    # Add web search tool
    try:
        await client.add_tool(
            name="websearch",
            tool_type=ToolType.WEBSEARCH
        )
        print("Added web search tool")
    except Exception as e:
        print(f"Note: Web search tool could not be added (requires additional permissions): {e}")
    
    # List all available tools
    tools = await agent.list_tools()
    print("\nAvailable tools:")
    for tool in tools:
        print(f"- {tool.get('name')} ({tool.get('type')}): {tool.get('state')}")
    
    # Test with different scenarios
    questions = [
        "What is the compound interest on $5,000 invested for 5 years at 4.1% APY?",
        "Based on the document, what's the difference between the highest and lowest interest rates listed?",
        "If I make $75,000 per year, what tax bracket am I in according to the document?"
    ]
    
    for question in questions:
        print(f"\n\nQuestion: {question}")
        response = await agent(question)
        print(f"\nResponse: {response}")
    
    # Interactive mode option
    use_interactive = input("\nDo you want to start interactive mode? (y/n): ")
    if use_interactive.lower() == 'y':
        await agent.interactive()
    
if __name__ == "__main__":
    asyncio.run(test_multiple_tools()) 