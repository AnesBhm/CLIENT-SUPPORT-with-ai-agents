import httpx
import asyncio

URL = "http://127.0.0.1:8005/tickets/"

async def test_create_ticket():
    # Login first to get token
    async with httpx.AsyncClient() as client:
        # Assuming admin user exists from previous steps
        login_data = {"username": "admin@doxa.com", "password": "Admin123!"}
        print("Logging in...")
        try:
            resp = await client.post("http://127.0.0.1:8005/login/access_token", data=login_data)
            if resp.status_code != 200:
                print(f"Login failed: {resp.status_code} {resp.text}")
                return
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            payload = {
                "subject": "Test Ticket via HTTP",
                "description": "Testing internal server error via HTTP script",
                "category": "Bugs",
                "ai_confidence_score": 0.0
            }
            
            print("Creating ticket...")
            resp = await client.post(URL, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_create_ticket())
