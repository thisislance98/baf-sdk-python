#!/usr/bin/env python3
"""
Run PAB agent tests one at a time.
This allows for easier debugging and clearer output.
"""

import asyncio
import sys
from test_pab_agent import (
    test_create_openai_agent_with_gpt4o,
    test_create_basic_agent,
    test_create_vertexai_agent,
    test_agent_with_different_output_formats,
    test_agent_with_context_manager
)

async def run_test(test_func, name):
    """Run a single test with clear separation"""
    print("\n" + "="*80)
    print(f"RUNNING TEST: {name}")
    print("="*80)
    
    try:
        await test_func()
        print(f"\n✅ TEST PASSED: {name}\n")
        return True
    except Exception as e:
        print(f"\n❌ TEST FAILED: {name}")
        print(f"Error: {str(e)}")
        return False

async def main():
    """Run all tests sequentially"""
    tests = [
        (test_create_openai_agent_with_gpt4o, "OpenAI Agent with GPT-4o"),
        (test_create_basic_agent, "Basic Agent"),
        (test_create_vertexai_agent, "VertexAI Agent"),
        (test_agent_with_different_output_formats, "Agent with Different Output Formats"),
        (test_agent_with_context_manager, "Agent with Context Manager")
    ]
    
    # Get test name from command line if provided
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        filtered_tests = [(func, name) for func, name in tests if test_name in name.lower()]
        if filtered_tests:
            tests = filtered_tests
        else:
            print(f"No tests match '{test_name}'. Running all tests.")
    
    results = []
    for test_func, name in tests:
        result = await run_test(test_func, name)
        results.append((name, result))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{status}: {name}")
    
    # Return non-zero exit code if any test failed
    if not all(result for _, result in results):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 