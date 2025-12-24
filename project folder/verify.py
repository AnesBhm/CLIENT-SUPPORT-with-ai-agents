import asyncio
import httpx
import sys
import random

async def main():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=10.0) as client:
        try:
            # 1. Health check
            print("Checking Root...")
            r = await client.get("/")
            print(f"Root: {r.status_code}")

            # 2. Create User
            print("Creating User...")
            rnd = random.randint(1000,9999)
            email = f"exp_verify_{rnd}@doxa.com"
            user_data = {"email": email, "password": "password123", "role": "Client"}
            r = await client.post("/users/", json=user_data)
            if r.status_code != 200:
                 print(f"User creation failed: {r.status_code} {r.text}")
                 return
            
            user_id = r.json()["id"]
            print(f"User Created: {email}")
                
            # 3. Create Ticket (Trigger AI)
            print("Creating Ticket...")
            ticket_data = {
                "subject": "Expansion Test", 
                "description": "Testing me and stats", 
                "customer_id": user_id
            }
            r = await client.post("/tickets/", json=ticket_data)
            if r.status_code != 200:
                print(f"Ticket creation failed: {r.status_code} {r.text}")
                return
            
            ticket_id = r.json()["id"]
            print(f"Ticket Created: ID {ticket_id}")

            print("Waiting for AI processing (3.5 seconds)...")
            await asyncio.sleep(3.5)

            # 4. Check /tickets/me
            print("Checking /tickets/me...")
            r = await client.get("/tickets/me", headers={"X-User-Email": email})
            if r.status_code == 200:
                print(f"My Tickets: {len(r.json())}")
            else:
                print(f"Failed /tickets/me: {r.status_code} {r.text}")

            # 5. Check /tickets/escalated
            print("Checking /tickets/escalated...")
            r = await client.get("/tickets/escalated")
            print(f"Escalated Tickets: {len(r.json())}")

            # 6. Submit Feedback
            print("Submitting Feedback...")
            r = await client.post(f"/tickets/{ticket_id}/feedback", json={"satisfaction_score": 5})
            if r.status_code == 200:
                print("Feedback submitted.")
            else:
                print(f"Feedback failed: {r.status_code} {r.text}")

            # 7. Check Admin Stats
            print("Checking /admin/stats...")
            r = await client.get("/admin/stats")
            print(f"Stats (no slash): {r.status_code}")
            if r.status_code == 200:
                print(f"Stats: {r.json()}")
            
            r = await client.get("/admin/stats/")
            print(f"Stats (slash): {r.status_code}")
            if r.status_code == 200:
                print(f"Stats: {r.json()}")


        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
