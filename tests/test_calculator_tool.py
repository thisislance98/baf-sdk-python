import asyncio
import json
from pab_client import PABClient, ToolType, ModelType, AgentType, OutputFormat

async def test_calculator_tool():
    """Test the PAB calculator tool"""
    # Initialize the PAB client
    # Get path to the credentials file
    credentials_path = "agent-binding.json"
    client = PABClient(credentials_path)
    
    # Create an agent with custom name
    agent = await client.create_agent(
        name="Calculator Test Agent",
        initial_instructions="You are a helpful assistant with access to a calculator tool. Use it when mathematical calculations are required.",
        expert_in="Math and numerical calculations",
        base_model=ModelType.OPENAI_GPT4O_MINI,
        advanced_model=ModelType.OPENAI_GPT4O,
        agent_type=AgentType.SMART
    )
    
    # Add calculator tool
    calculator_tool_id = await client.add_tool(
        name="calculator", 
        tool_type=ToolType.CALCULATOR
    )
    print(f"Added calculator tool with ID: {calculator_tool_id}")
    
    # Test with a simple calculation
    question = "What is the square root of 144 plus 50 divided by 2?"
    print(f"\nAsking: {question}")
    
    response = await agent.send_message(
        question,
        output_format=OutputFormat.MARKDOWN
    )
    print(f"\nResponse: {response}")
    
    # Test with a more complex calculation
    question = "If I invest $1000 with 5% annual compound interest, how much will I have after 10 years?"
    print(f"\nAsking: {question}")
    
    response = await agent.send_message(
        question,
        output_format=OutputFormat.MARKDOWN
    )
    print(f"\nResponse: {response}")
    
    # List available tools
    tools = await agent.list_tools()
    print("\nAvailable tools:")
    for tool in tools:
        print(f"- {tool.get('name')} ({tool.get('type')}): {tool.get('state')}")

if __name__ == "__main__":
    asyncio.run(test_calculator_tool()) 