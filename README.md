# TC-DOXA - Client Support with AI Agents

This project is a comprehensive customer support system utilizing AI agents, consisting of three main components:
1.  **Main Backend (FastAPI)**: Handles core business logic, database, and API.
2.  **Agentic AI Service (FastAPI)**: A dedicated microservice for AI processing (RAG, Classification, Agents).
3.  **Frontend (Next.js)**: The user interface for clients and agents.

## Prerequisites

Before starting, ensure you have the following installed:
-   **Python 3.10+**
-   **Node.js** (Latest LTS version recommended)
-   **Git**

## Project Structure

-   `app/`: Main Backend application code.
-   `agentic/`: Agentic AI Service code.
-   `FRONT/`: Frontend application code.
-   `requirements.txt`: Main Backend dependencies.
-   `agentic/requirements.txt`: Agentic Service dependencies.

---

## Installation & Setup

You need to set up and run all three components for the system to function correctly.

### 1. Agentic AI Service Setup (Port 8002)

The main backend relies on this service for AI features.

1.  **Navigate to the agentic directory:**
    ```bash
    cd agentic
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    -   **Windows (PowerShell):**
        ```powershell
        .\.venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables:**
    -   Copy `.env.example` to `.env`:
        -   **Windows:** `copy .env.example .env`
        -   **Mac/Linux:** `cp .env.example .env`
    -   **Open `.env` and add your API Keys:**
        -   `GEMINI_API_KEY`: Required (Get from [Google AI Studio](https://aistudio.google.com/app/apikey))
        -   `MISTRAL_API_KEY`: Optional

6.  **Start the Agentic Service:**
    ```bash
    uvicorn src.main:app --reload --port 8002
    ```
    *Alternatively, on Windows with PowerShell:* `.\run_server.ps1`

    The service will run at `http://localhost:8002`.

---

### 2. Main Backend Setup (Port 8000)

1.  **Open a NEW terminal and navigate to the project root directory:**
    *(If you are in `agentic/`, go back up: `cd ..`)*

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    -   **Windows:** `.\.venv\Scripts\activate`
    -   **macOS/Linux:** `source .venv/bin/activate`

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Start the Backend Server:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    or
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```

    The API will be available at `http://localhost:8000`.
    API Documentation: `http://localhost:8000/docs`

---

### 3. Frontend Setup (Port 3000)

1.  **Open a NEW terminal and navigate to the `FRONT` directory:**
    ```bash
    cd FRONT
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Frontend Server:**
    ```bash
    npm run dev
    ```

    The web application will be available at `http://localhost:3000`.

---

## Usage Summary

To run the full application, you should have **three separate terminals** running:

1.  **Agentic Service**: `http://localhost:8002`
2.  **Main Backend**: `http://localhost:8000`
3.  **Frontend**: `http://localhost:3000`

## Features

-   **Smart Ticket Management**: Create, track, and resolve tickets.
-   **AI-Powered Responses**: The Agentic service analyzes requests and generates draft responses using RAG (Retrieval-Augmented Generation).
-   **Automatic Classification**: Tickets are automatically categorized (e.g., Spam, Aggressive, Support).
-   **Dashboard Analytics**: insights into ticket volume and resolution metrics.
