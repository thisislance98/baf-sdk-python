#!/usr/bin/env python
"""
Test the interactive credentials input functionality of BAFClient
"""

import asyncio
import os
import sys
import io
from pathlib import Path
from unittest.mock import patch
from baf_client import BAFClient, DEFAULT_CACHE_FILE

def clear_cache():
    """Clear the credentials cache file"""
    try:
        result = BAFClient.clear_cache()
        if result:
            print("Successfully cleared credentials cache")
        else:
            print("Failed to clear credentials cache")
    except Exception as e:
        print(f"Error clearing cache: {e}")

async def test_with_valid_input():
    """Test BAFClient with simulated valid user input"""
    print("\n=== TESTING INTERACTIVE CREDENTIALS INPUT (VALID PATH) ===")
    
    # Clear the cache
    clear_cache()
    
    # Save original environment variables
    saved_env = {}
    env_vars = ["BAF_CLIENT_ID", "BAF_CLIENT_SECRET", "BAF_AUTH_URL", "BAF_API_BASE_URL"]
    for var in env_vars:
        saved_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
            print(f"Temporarily removed environment variable: {var}")
    
    # Get the actual valid path to credentials file
    current_dir = Path.cwd()
    credentials_path = current_dir / "agent-binding.json"
    
    if not credentials_path.exists():
        print(f"ERROR: Credentials file not found at {credentials_path}")
        print("This test needs a valid credentials file to work.")
        return False
    
    try:
        # Patch the input function to return our credentials path
        with patch('builtins.input', return_value=str(credentials_path)):
            print(f"\nSimulating user input: {credentials_path}")
            
            # This should prompt for credentials and accept our simulated input
            client = BAFClient(name="Interactive Test")
            
            print("\nSUCCESS: BAFClient initialized with interactive input")
            
            # Verify the cache was created
            if os.path.exists(DEFAULT_CACHE_FILE):
                print(f"Cache file created at: {DEFAULT_CACHE_FILE}")
            else:
                print("ERROR: Cache file was not created")
            
            # Test that we can authenticate
            print("\nTesting authentication...")
            await client._get_token()
            print("Authentication successful!")
            
            return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    finally:
        # Restore environment variables
        for var, value in saved_env.items():
            if value is not None:
                os.environ[var] = value
                print(f"Restored environment variable: {var}")

async def test_with_cancel():
    """Test BAFClient with simulated cancel input"""
    print("\n=== TESTING INTERACTIVE CREDENTIALS INPUT (CANCEL) ===")
    
    # Clear the cache
    clear_cache()
    
    # Save original environment variables
    saved_env = {}
    env_vars = ["BAF_CLIENT_ID", "BAF_CLIENT_SECRET", "BAF_AUTH_URL", "BAF_API_BASE_URL"]
    for var in env_vars:
        saved_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        # Patch the input function to return 'cancel'
        with patch('builtins.input', return_value='cancel'):
            print("\nSimulating user input: 'cancel'")
            
            try:
                # This should prompt for credentials and receive cancel
                client = BAFClient(name="Interactive Cancel Test")
                print("ERROR: BAFClient initialized despite cancellation")
                return False
            except ValueError as e:
                if "cancelled by user" in str(e):
                    print("\nSUCCESS: BAFClient initialization was correctly cancelled")
                    return True
                else:
                    print(f"ERROR: Unexpected error: {str(e)}")
                    return False
    finally:
        # Restore environment variables
        for var, value in saved_env.items():
            if value is not None:
                os.environ[var] = value

async def test_with_invalid_path():
    """Test BAFClient with simulated invalid path input"""
    print("\n=== TESTING INTERACTIVE CREDENTIALS INPUT (INVALID PATH) ===")
    
    # Clear the cache
    clear_cache()
    
    # Save original environment variables
    saved_env = {}
    env_vars = ["BAF_CLIENT_ID", "BAF_CLIENT_SECRET", "BAF_AUTH_URL", "BAF_API_BASE_URL"]
    for var in env_vars:
        saved_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    try:
        # Use a path that definitely doesn't exist
        invalid_path = "/path/that/definitely/does/not/exist.json"
        
        # Patch the input function to return invalid path
        with patch('builtins.input', return_value=invalid_path):
            print(f"\nSimulating user input: '{invalid_path}'")
            
            try:
                # This should prompt for credentials and receive invalid path
                client = BAFClient(name="Interactive Invalid Path Test")
                print("ERROR: BAFClient initialized despite invalid path")
                return False
            except ValueError as e:
                if "File not found" in str(e):
                    print("\nSUCCESS: BAFClient correctly reported invalid file path")
                    return True
                else:
                    print(f"ERROR: Unexpected error: {str(e)}")
                    return False
    finally:
        # Restore environment variables
        for var, value in saved_env.items():
            if value is not None:
                os.environ[var] = value

async def run_all_tests():
    """Run all tests for interactive credentials input"""
    results = []
    
    # Test with valid input
    results.append(await test_with_valid_input())
    
    # Test with cancel
    results.append(await test_with_cancel())
    
    # Test with invalid path
    results.append(await test_with_invalid_path())
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    print(f"Valid input test: {'PASSED' if results[0] else 'FAILED'}")
    print(f"Cancel test: {'PASSED' if results[1] else 'FAILED'}")
    print(f"Invalid path test: {'PASSED' if results[2] else 'FAILED'}")
    
    # Overall result
    if all(results):
        print("\nAll tests PASSED!")
        return True
    else:
        print("\nSome tests FAILED!")
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 