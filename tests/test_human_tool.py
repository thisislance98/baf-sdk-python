import asyncio
from baf_client import BAFClient, ToolType, ModelType, OutputFormat

async def test_human_tool():
    """Test the BAF human tool to allow agent to request more information"""
    # Initialize the BAF client
    client = BAFClient()
    
    # Create an agent with custom name
    agent = await client.create_agent(
        name="Human Tool Test Agent",
        initial_instructions="""
        You are a helpful assistant with the ability to ask the human user for more information
        when the query is ambiguous or lacks essential details.
        
        When you need clarification or additional information, use the human tool.
        For example:
        - If asked about scheduling but no date is provided
        - If asked for an opinion without enough context
        - If asked to calculate something with incomplete variables
        
        Always be helpful, precise, and ask for clarification only when truly needed.
        """,
        expert_in="Personalized assistance and data gathering",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O
    )
    
    # Add human tool
    await client.add_tool(
        name="human", 
        tool_type=ToolType.HUMAN
    )
    print("Added human tool")
    
    # Also add calculator tool to test combinations
    await client.add_tool(
        name="calculator", 
        tool_type=ToolType.CALCULATOR
    )
    print("Added calculator tool")
    
    # List available tools
    tools = await agent.list_tools()
    print("\nAvailable tools:")
    for tool in tools:
        print(f"- {tool.get('name')} ({tool.get('type')}): {tool.get('state')}")
    
    # Intentionally start with a vague question that should trigger the human tool
    print("\nStarting with an incomplete question that should trigger the human tool...")
    print("\nEntering interactive mode. Type 'exit' to quit.\n")
    
    # Start with a vague question that should trigger the human tool
    initial_question = "Calculate the return on investment for my portfolio"
    print(f"You: {initial_question}")
    
    response = await agent(initial_question)
    print(f"\nAgent: {response}")
    
    # Continue with interactive mode
    await agent.interactive()

if __name__ == "__main__":
    asyncio.run(test_human_tool()) 