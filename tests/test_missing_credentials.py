#!/usr/bin/env python
"""
Test BAFClient behavior when no credentials are available
"""

import asyncio
import os
import sys
from pathlib import Path
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

async def test_no_credentials():
    """Test BAFClient behavior when no credentials are available"""
    print("\n=== TESTING BEHAVIOR WITH NO CREDENTIALS ===")
    
    # Clear the cache
    clear_cache()
    
    # Temporarily rename any .env file to prevent loading from environment variables
    env_file = ".env"
    renamed_env = ".env.bak"
    env_renamed = False
    
    if os.path.exists(env_file):
        try:
            os.rename(env_file, renamed_env)
            env_renamed = True
            print(f"Temporarily renamed {env_file} to {renamed_env}")
        except Exception as e:
            print(f"Could not rename .env file: {e}")
    
    # Save original environment variables
    saved_env = {}
    env_vars = ["BAF_CLIENT_ID", "BAF_CLIENT_SECRET", "BAF_AUTH_URL", "BAF_API_BASE_URL"]
    for var in env_vars:
        saved_env[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
            print(f"Temporarily removed environment variable: {var}")
    
    try:
        print("\nAttempting to initialize BAFClient without credentials...")
        try:
            # This should raise a ValueError with instructions
            client = BAFClient(name="Missing Credentials Test")
            print("ERROR: BAFClient initialized without credentials (unexpected)")
        except ValueError as e:
            print("\nExpected ValueError raised:")
            print(str(e))
            
            # Check if the error message contains the expected instructions
            expected_phrases = [
                "Please provide the path",
                "credentials JSON file",
                "wiki.one.int.sap/wiki/display/CONAIEXP/Setting+up+Project+Agent+Builder",
                "BAFClient('/path/to/your/credentials.json')"
            ]
            
            all_found = True
            for phrase in expected_phrases:
                if phrase not in str(e):
                    print(f"ERROR: Expected phrase not found in error message: '{phrase}'")
                    all_found = False
            
            if all_found:
                print("\nSUCCESS: Error message contains all expected instructions")
            
        # Now test with providing credentials
        print("\nNow initializing with credentials...")
        current_dir = Path.cwd()
        credentials_path = current_dir / "agent-binding.json"
        
        if credentials_path.exists():
            client = BAFClient(str(credentials_path), "Missing Credentials Test")
            print("SUCCESS: BAFClient initialized with provided credentials")
            
            # Verify the cache was created
            if os.path.exists(DEFAULT_CACHE_FILE):
                print(f"Cache file created at: {DEFAULT_CACHE_FILE}")
            else:
                print("ERROR: Cache file was not created")
                
            # Verify we can create another instance using cached credentials
            print("\nVerifying we can create a new instance with cached credentials...")
            client2 = BAFClient(name="Cached Credentials Test")
            print("SUCCESS: Second BAFClient instance created using cached credentials")
        else:
            print(f"Credentials file not found at: {credentials_path}")
            
    finally:
        # Restore .env file if it was renamed
        if env_renamed:
            try:
                os.rename(renamed_env, env_file)
                print(f"Restored {renamed_env} to {env_file}")
            except Exception as e:
                print(f"Error restoring .env file: {e}")
                
        # Restore environment variables
        for var, value in saved_env.items():
            if value is not None:
                os.environ[var] = value
                print(f"Restored environment variable: {var}")

if __name__ == "__main__":
    asyncio.run(test_no_credentials()) 