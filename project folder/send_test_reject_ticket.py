import asyncio
import httpx

async def create_spam_ticket():
    # URL for creating a ticket (adjust if your port is different)
    url = "http://localhost:8000/api/v1/tickets/"
    
    # Payload designed to trigger "spam" classification
    # This depends on your Agentic Service's classification logic. 
    # Usually "Earn money fast" or aggressive nonsense triggers it.
    payload = {
        "subject": "URGENT $$$ Make Money Fast!!!",
        "description": "Click this link to win a prize! Verify your account immediately or it will be deleted. SPAM SPAM SPAM.",
        "category": "Other"
    }

    # You might need authentication headers depending on your setup.
    # Assuming public or simple auth for this test script, or simulate a logged-in user.
    # If your endpoint requires auth, you'll need to login first. 
    # For now, let's assume we can hit the endpoint or use a known user token.
    
    # NOTE: Since /tickets/ endpoint usually requires a user, we need a valid token.
    # This script assumes you can manually provide a token or it uses a hardcoded one.
    # Let's try to login as the admin/user first to get a token.
    
    login_url = "http://localhost:8000/api/v1/login/access-token"
    # Use the credentials created in create_admin.py or known ones
    login_data = {"username": "admin@doxa.com", "password": "Admin123!"} 
    
    async with httpx.AsyncClient() as client:
        # 1. Login
        try:
            auth_resp = await client.post(login_url, data=login_data)
            auth_resp.raise_for_status()
            token = auth_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful.")
        except Exception as e:
            print(f"Login failed: {e}")
            return

        # 2. Create Ticket
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            print(f"Ticket created: ID={data['id']} Subject='{data['subject']}'")
            print("Waiting for AI processing...")
            
            # 3. Poll for status
            ticket_id = data['id']
            for _ in range(10): # Poll for 30 seconds
                await asyncio.sleep(3)
                status_resp = await client.get(f"http://localhost:8000/api/v1/tickets/{ticket_id}/status", headers=headers)
                status_data = status_resp.json()
                status = status_data['status']
                print(f"Current Status: {status}")
                if status in ["Rejected", "Escalated", "Resolved By AI"]:
                    print(f"Final Status: {status}")
                    print(f"AI Response: {status_data.get('ai_response_body')}")
                    break
        except Exception as e:
            print(f"Error creating/polling ticket: {e}")

if __name__ == "__main__":
    asyncio.run(create_spam_ticket())
