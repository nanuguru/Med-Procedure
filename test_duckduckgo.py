"""Test DuckDuckGo search"""
import asyncio
from tools.search_tools import DuckDuckGoSearchTool

async def test():
    tool = DuckDuckGoSearchTool()
    result = await tool.search("wound dressing nursing procedure", setting="Home")
    print(f"Success: {result.get('success')}")
    print(f"Results: {len(result.get('results', []))}")
    if result.get('results'):
        print(f"\nFirst result:")
        print(result['results'][0])

if __name__ == "__main__":
    asyncio.run(test())

