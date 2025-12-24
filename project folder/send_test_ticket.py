import httpx
import json
import asyncio
import os

# Backend API Endpoint
URL = "http://localhost:8000/tickets/"
LOG_FILE = "ai_log.txt"

# ------------------------------------------------------------------
# 📝 EDIT YOUR TICKET DATA HERE
# ------------------------------------------------------------------
ticket_payload = {
    "subject": "creer un compte?", 
    "description": "subscription billing pro sur doxa",
    "customer_id": 1  # Required by backend
}
# ------------------------------------------------------------------

async def check_logs_for_completion(ticket_id: int, max_retries: int = 30):
    """
    Asynchronously poll the log file for ticket completion.
    """
    print(f"\n⏳ Waiting for AI Agent to process Ticket {ticket_id} (Async)...")
    
    for i in range(max_retries):
        if os.path.exists(LOG_FILE):
            try:
                # File I/O is still sync but fast enough for this test tool
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for completion marker
                finish_marker = f"Finished ticket {ticket_id}"
                if finish_marker in content:
                    print("✅ AI Processing Complete!\n")
                    
                    # Extract response
                    start_marker = f"Processing ticket {ticket_id}"
                    if start_marker in content:
                        segment = content.split(start_marker)[-1]
                        
                        print("-" * 40)
                        print(f"AI AGENT RESPONSE (Ticket {ticket_id}):")
                        print(segment.strip())
                        print("-" * 40)
                    return True
            except Exception as e:
                print(f"⚠️ Error reading logs: {e}")
        
        # Async sleep - non-blocking wait
        await asyncio.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   ... waiting ({i}s)")
            
    print(f"\n❌ Timed out waiting for AI response after {max_retries} seconds.")
    return False

async def send_ticket():
    print(f"🚀 Sending ticket to: {URL}")
    print(f"📦 Payload:\n{json.dumps(ticket_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Send POST request asynchronously
            response = await client.post(URL, json=ticket_payload)
            
            print(f"\n✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                ticket_id = data.get('id')
                print("📄 Response Data:")
                print(json.dumps(data, indent=2))
                print(f"\nLogged Ticket ID: {ticket_id}")
                
                # Await the log checking loop
                await check_logs_for_completion(ticket_id)
                
            else:
                print("⚠️ Request failed:")
                print(response.text)
                
        except httpx.RequestError as exc:
            print(f"\n❌ Connection Error: {exc}")
            print("Tip: Make sure the backend is running on port 8000")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(send_ticket())
