"""
Doxa Ticketing System - Frontend Integration Guide

This module provides a summary of key API endpoints and JSON examples for the frontend team.

BASE URL: http://127.0.0.1:8000
SWAGGER UI: http://127.0.0.1:8000/docs
REDOC: http://127.0.0.1:8000/redoc

CORS HANDLING:
- The API is configured to accept requests from all origins ("*").
- Ensure your frontend sends the 'Content-Type: application/json' header.
- For protected endpoints, send 'Authorization: Bearer <access_token>'.
"""

API_DOCUMENTATION = {
    "auth": {
        "register": {
            "method": "POST",
            "url": "/users/",
            "description": "Register a new user.",
            "request_body": {
                "email": "user@example.com",
                "password": "securepassword",
                "full_name": "John Doe",
                "is_over_18": True,
                "receives_updates": True
            },
            "response_200": {
                "email": "user@example.com",
                "id": 1,
                "is_active": True,
                "full_name": "John Doe",
                "is_over_18": True,
                "receives_updates": True
            }
        },
        "login": {
            "method": "POST",
            "url": "/login/access_token",
            "description": "Obtain JWT access token. Note: Request body uses x-www-form-urlencoded format, not JSON.",
            "request_body_form_data": {
                "username": "user@example.com",
                "password": "securepassword"
            },
            "response_200": {
                "access_token": "eyJhbG...",
                "token_type": "bearer"
            }
        }
    },
    "tickets": {
        "create": {
            "method": "POST",
            "url": "/tickets/",
            "description": "Create a new ticket. The 'category' field is optional but recommended. Valid categories: Account, Team Management, Workflow, Notifications, Bugs, Billing, Privacy, Guidance, Other.",
            "headers": {"Authorization": "Bearer <access_token>"},
            "request_body": {
                "subject": "Login Issue",
                "description": "I cannot access my account.",
                "category": "Account"
            },
            "response_200": {
                "subject": "Login Issue",
                "description": "I cannot access my account",
                "category": "Account",
                "id": 5,
                "status": "Open",
                "ai_confidence_score": 0.0,
                "is_satisfied": None,
                "feedback_reason": None,
                "created_at": "2025-12-22T20:25:00.000000",
                "closed_at": None,
                "customer_id": 1,
                "agent_id": None
            }
        },
        "get_by_id": {
            "method": "GET",
            "url": "/tickets/{id}",
            "description": "Get ticket details by ID. This returns the AI processing status and confidence score.",
            "headers": {"Authorization": "Bearer <access_token>"},
            "response_200": {
                "subject": "Login Issue",
                "description": "I cannot access my account",
                "category": "Account",
                "id": 5,
                "status": "Resolved By AI",
                "ai_confidence_score": 0.85,
                "is_satisfied": None,
                "feedback_reason": None,
                "created_at": "2025-12-22T20:25:00.000000",
                "closed_at": None,
                "customer_id": 1,
                "agent_id": None
            }
        },
        "list": {
            "method": "GET",
            "url": "/tickets/?category=Billing",
            "description": "List tickets, optionally filtered by category.",
            "headers": {"Authorization": "Bearer <access_token>"},
            "response_200": [
                {
                    "subject": "Billing Error",
                    "category": "Billing",
                    "id": 6,
                    "status": "Open",
                    "...": "..."
                }
            ]
        }
    }
}
