"""Test the full search flow"""
import asyncio
from tools.search_tools import HybridSearchTool

async def test():
    tool = HybridSearchTool()
    result = await tool.search("wound dressing", "Home")
    
    print(f"Success: {result.get('success')}")
    print(f"Has procedures: {'procedures' in result}")
    
    if 'procedures' in result:
        procedures = result['procedures']
        print(f"Procedures type: {type(procedures)}")
        print(f"Procedures keys: {list(procedures.keys()) if isinstance(procedures, dict) else 'not dict'}")
        
        if isinstance(procedures, dict):
            detailed = procedures.get('detailed_procedure')
            print(f"Has detailed_procedure: {bool(detailed)}")
            if detailed:
                print(f"Detailed procedure type: {type(detailed)}")
                print(f"Length: {len(str(detailed))}")
                print(f"\nFirst 300 chars:\n{str(detailed)[:300]}")

if __name__ == "__main__":
    asyncio.run(test())

