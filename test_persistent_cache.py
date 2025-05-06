#!/usr/bin/env python
"""
Test that PABClient credentials caching persists between runs
"""

import asyncio
import os
import sys
from pathlib import Path
from pab_client import PABClient, DEFAULT_CACHE_FILE

async def test_part1():
    """First part of test - set up credentials and verify they're cached"""
    print("\n=== TEST PART 1: INITIALIZING WITH CREDENTIALS PATH ===")
    
    # Get the path to the credentials file
    current_dir = Path.cwd()
    credentials_path = current_dir / "agent-binding.json"
    
    if not credentials_path.exists():
        print(f"Credentials file not found at: {credentials_path}")
        print("Please provide the correct path to your credentials file:")
        credentials_path = input("> ")
        if not Path(credentials_path).exists():
            print(f"File not found: {credentials_path}")
            return False
    
    # Check if cache file exists before initialization
    cache_exists_before = os.path.exists(DEFAULT_CACHE_FILE)
    if cache_exists_before:
        print(f"Cache file already exists at: {DEFAULT_CACHE_FILE}")
    else:
        print(f"No cache file found at: {DEFAULT_CACHE_FILE}")
    
    print(f"\nInitializing PABClient with credentials path: {credentials_path}")
    client = PABClient(str(credentials_path), "Persistent Cache Test")
    
    # Check if cache file exists after initialization
    cache_exists_after = os.path.exists(DEFAULT_CACHE_FILE)
    if cache_exists_after:
        print(f"\nCache file created/updated at: {DEFAULT_CACHE_FILE}")
        
        # Verify content of cache file
        try:
            import json
            with open(DEFAULT_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                
            if 'credentials_path' in cache_data:
                cached_path = cache_data['credentials_path']
                print(f"Cached credentials path: {cached_path}")
                
                # Check if cached path matches the provided path
                if os.path.samefile(cached_path, str(credentials_path)):
                    print("SUCCESS: Cached path matches provided path")
                else:
                    print(f"WARNING: Cached path ({cached_path}) doesn't match provided path ({credentials_path})")
            else:
                print("WARNING: 'credentials_path' not found in cache file")
        except Exception as e:
            print(f"Error reading cache file: {e}")
    else:
        print("\nWARNING: Cache file was not created")
    
    print("\nVERIFICATION: Now run 'test_part2.py' to verify cache persistence")
    return True

async def test_part2():
    """Second part of test - initialize without credentials path"""
    print("\n=== TEST PART 2: INITIALIZING WITHOUT CREDENTIALS PATH ===")
    
    # Check if cache file exists before initialization
    cache_exists = os.path.exists(DEFAULT_CACHE_FILE)
    if cache_exists:
        print(f"Cache file found at: {DEFAULT_CACHE_FILE}")
        
        # Show content of cache file
        try:
            import json
            with open(DEFAULT_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                
            if 'credentials_path' in cache_data:
                cached_path = cache_data['credentials_path']
                print(f"Cached credentials path: {cached_path}")
            else:
                print("WARNING: 'credentials_path' not found in cache file")
        except Exception as e:
            print(f"Error reading cache file: {e}")
    else:
        print(f"\nERROR: No cache file found at {DEFAULT_CACHE_FILE}")
        print("Please run test_part1() first to generate the cache file")
        return False
    
    print("\nInitializing PABClient without credentials path")
    try:
        client = PABClient(name="Persistent Cache Test")
        print("\nSUCCESS: PABClient initialized successfully using cached credentials")
        
        # Test authentication
        print("\nTesting authentication with cached credentials...")
        try:
            await client._get_token()
            print("Authentication successful!")
            
            print("\nCreating test agent...")
            agent = await client.create_agent(
                initial_instructions="You are a helpful assistant.",
                expert_in="Testing credential caching between runs"
            )
            
            print("\nSending test message to agent...")
            response = await agent("Do my cached credentials work between runs?")
            print(f"\nAgent response: {response}")
            
            print("\nPersistent cache test completed successfully!")
            return True
        except Exception as e:
            print(f"Error during authentication/test: {e}")
            return False
    except ValueError as e:
        print(f"ERROR: Failed to initialize PABClient: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "part2":
        asyncio.run(test_part2())
    else:
        asyncio.run(test_part1()) 