import httpx
import time
import sys

BASE_URL = "http://localhost:8000"

def verify_integration():
    # 0. Create User & Login
    username = f"testuser_{int(time.time())}@example.com"
    password = "password123"
    
    print(f"0. Registering user {username}...")
    try:
        r = httpx.post(f"{BASE_URL}/users/", json={
            "email": username,
            "password": password,
            "full_name": "Test User", 
            "role": "client"
        })
        if r.status_code not in [200, 201]:
            print(f"Registration failed: {r.text}")
            # Try login anyway if user exists
    except Exception as e:
        print(f"Registration error: {e}")

    print("0b. Logging in...")
    access_token = None
    try:
        r = httpx.post(f"{BASE_URL}/login/access_token", data={
            "username": username,
            "password": password
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if r.status_code == 200:
            access_token = r.json()["access_token"]
            print("Login successful.")
        else:
            print(f"Login failed: {r.text}")
            return False
    except Exception as e:
        print(f"Login error: {e}")
        return False

    headers = {"Authorization": f"Bearer {access_token}"}

    print("1. Creating ticket via Backend API...")
    payload = {
        "subject": "How do I reset my password?",
        "description": "I forgot my password and cannot login. please help.",
        "category": "Technique" # inferred requirement from previous context
    }
    
    try:
        response = httpx.post(f"{BASE_URL}/tickets/", json=payload, headers=headers, timeout=10.0)
        
        if response.status_code != 200:
            print(f"FAILED to create ticket: {response.status_code} - {response.text}")
            return False
            
        ticket_data = response.json()
        ticket_id = ticket_data["id"]
        print(f"Ticket created: ID {ticket_id}")
        
    except Exception as e:
        print(f"ERROR calling backend: {e}")
        return False

    print("2. Waiting for AI processing (Background Task)...")
    time.sleep(5) # Wait for background task
    
    print("3. Checking ai_log.txt...")
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        if f"Processing ticket {ticket_id}" in content and f"Ticket {ticket_id} Result:" in content:
            print("SUCCESS: AI processing logs found!")
            print("-" * 20)
            # Find the segment for this ticket
            segment = content.split(f"Processing ticket {ticket_id}")[-1]
            print(segment[:500]) # Print first 500 chars of result
            print("-" * 20)
            return True
        else:
            print("FAILED: Logs for this ticket not found yet.")
            return False
            
    except FileNotFoundError:
        print("FAILED: ai_log.txt not found.")
        return False

if __name__ == "__main__":
    success = verify_integration()
    sys.exit(0 if success else 1)
