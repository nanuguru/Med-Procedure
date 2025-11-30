"""
Test script to debug procedure retrieval
"""
import asyncio
import sys
from config import settings
from tools.search_tools import GroqSearchTool

async def test_groq():
    """Test Groq search directly"""
    print("Testing Groq Search Tool...")
    print(f"API Key configured: {'Yes' if settings.groq_api_key else 'No'}")
    
    if not settings.groq_api_key:
        print("ERROR: Groq API key not configured!")
        print("Get your free API key at: https://console.groq.com/keys")
        return
    
    tool = GroqSearchTool()
    result = await tool.search_procedures("wound dressing", "Home")
    
    print(f"\nSuccess: {result.get('success')}")
    if result.get('success'):
        print(f"Has procedures: {'procedures' in result}")
        if 'procedures' in result:
            procedures = result['procedures']
            print(f"Procedure type: {type(procedures)}")
            print(f"Procedure length: {len(str(procedures)) if procedures else 0}")
            if procedures:
                print(f"\nFirst 500 chars:\n{str(procedures)[:500]}")
    else:
        print(f"Error: {result.get('error', result.get('message'))}")

if __name__ == "__main__":
    asyncio.run(test_groq())

