"""
Example usage of NurseSOP Live API
"""
import asyncio
import httpx
import time


async def example_request():
    """Example of making a request to the API"""
    
    base_url = "http://localhost:8000"
    
    # Example 1: Request procedure for Hospital setting
    print("Example 1: Requesting wound dressing procedure in Hospital setting")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Make request
        response = await client.post(
            f"{base_url}/api/v1/procedures",
            json={
                "user_text": "wound dressing",
                "setting": "Hospital"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        session_id = result.get("session_id")
        
        if session_id:
            # Poll for results
            print(f"\nPolling session {session_id} for results...")
            max_attempts = 30
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                
                status_response = await client.get(
                    f"{base_url}/api/v1/sessions/{session_id}"
                )
                status_data = status_response.json()
                
                print(f"Attempt {attempt + 1}: Status = {status_data.get('status')}")
                
                if status_data.get("status") == "completed":
                    print("\n✅ Procedure retrieved successfully!")
                    print(f"Result: {status_data.get('result')}")
                    break
                elif status_data.get("status") == "error":
                    print(f"\n❌ Error: {status_data.get('result')}")
                    break
    
    # Example 2: Request procedure for Home setting
    print("\n\nExample 2: Requesting blood pressure measurement in Home setting")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/api/v1/procedures",
            json={
                "user_text": "blood pressure measurement",
                "setting": "Home"
            }
        )
        
        result = response.json()
        session_id = result.get("session_id")
        print(f"Session ID: {session_id}")
        print("Check status using: GET /api/v1/sessions/{session_id}")


if __name__ == "__main__":
    print("NurseSOP Live API Example Usage")
    print("=" * 50)
    print("Make sure the server is running on http://localhost:8000")
    print("=" * 50)
    asyncio.run(example_request())

