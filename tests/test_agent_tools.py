#!/usr/bin/env python3
"""
Test creating a PAB agent with tools and using them with different queries
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

# Import from parent directory
from pab_client import PABClient, ModelType, AgentType, OutputFormat, ToolType

async def test_agent_with_tools():
    """Test creating an agent with tools and using them"""
    try:
        print("Starting agent with tools test...")
        
        # Get the path to the credentials file in the parent directory
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        credentials_path = parent_dir / "agent-binding.json"

        pab = PABClient(str(credentials_path), "Agent with Tools Test")
        
        print("Authenticating...")
        await pab._get_token()
        
        print("Creating agent...")
        agent = await pab.create_agent(
            initial_instructions="You are a helpful assistant that can use tools to provide better answers.",
            expert_in="Answering questions using available tools when appropriate",
            agent_type=AgentType.SMART,
            base_model=ModelType.OPENAI_GPT4O_MINI,
            advanced_model=ModelType.OPENAI_GPT4O
        )
        
        print("Agent created successfully!")
        
        # Add document tool with exception handling
        try:
            print("\nAdding document tool...")
            # Note: Tool must be named "document" for the SDK to work with it
            doc_tool_id = await pab.add_tool(
                name="document",  # This is the standard name expected by the SDK
                tool_type=ToolType.DOCUMENT
            )
            print(f"Document tool created with ID: {doc_tool_id}")
            
            # Add a sample document about a made-up company
            sample_text = """
            # TechNova Solutions
            
            TechNova Solutions is an innovative technology company specializing in four core technology domains:
            
            1. Cloud Infrastructure and Services
            2. Advanced Analytics and Machine Learning
            3. Cybersecurity Systems
            4. Digital Experience Platforms
            
            These technology domains enable our clients to implement cutting-edge business strategies, including 
            digital workforce transformation, secure cloud migration, data-driven decision making, and enhanced 
            customer engagement.
            
            ## Key Features of Our Products
            
            - Seamless Integration: Our solutions integrate with both legacy and modern systems
            - Customizable Modules: Modular architecture allows for personalized implementations
            - Enterprise-grade Security: Advanced protection for sensitive business data
            - AI-powered Automation: Intelligent workflows that reduce manual processes
            
            ## Client Success Stories
            
            TechNova has helped over 500 enterprises across financial services, healthcare, manufacturing, and 
            retail sectors to modernize their technology infrastructure and achieve significant ROI. Our flagship 
            platform, NovaSphere, has won multiple industry awards for innovation and user experience.
            """
            
            print("\nAdding document to the tool...")
            doc_id = await pab.add_document(
                doc_name="TechNova Company Overview",
                content=sample_text
            )
            print(f"Document added with ID: {doc_id}")
        except Exception as e:
            print(f"Could not add document tool: {str(e)}")
            print("Continuing with existing tools...")
        
        # Test with document query
        print("\nTesting document query...")
        doc_response = await agent.send_message(
            "What are the four core technology domains of TechNova Solutions?",
            output_format=OutputFormat.MARKDOWN
        )
        print(f"Document query response: {doc_response}")
        
        # Test with a follow-up question
        print("\nTesting follow-up question...")
        followup_response = await agent.send_message(
            "What are the key features of TechNova's products?",
            output_format=OutputFormat.MARKDOWN
        )
        print(f"Follow-up response: {followup_response}")
        
        # Test different output formats
        print("\nTesting JSON output format...")
        json_response = await agent.send_message(
            "List the four core technology domains of TechNova Solutions in JSON format.", 
            output_format=OutputFormat.JSON
        )
        print(f"JSON response: {json_response}")
        
        print("\nTesting text output format...")
        text_response = await agent.send_message(
            "Explain what TechNova Solutions is in plain text.", 
            output_format=OutputFormat.TEXT
        )
        print(f"Text response: {text_response}")
        
        # Ask about client success
        print("\nAsking about client success...")
        success_response = await agent.send_message(
            "What sectors has TechNova helped and what is their flagship platform?",
            output_format=OutputFormat.MARKDOWN
        )
        print(f"Success response: {success_response}")
        
        print("\nAll tests completed!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False

if __name__ == "__main__":
    asyncio.run(test_agent_with_tools()) 