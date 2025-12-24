# Complete Agent Architecture - 10 Agents Explained

## Overview

The Doxa Agentic AI system now uses **10 specialized AI agents** working together in a sophisticated pipeline to process user complaints.

---

## Agent Categories

### Category 1: Classification Agents (6 agents)
**Purpose**: Initial filtering and categorization of queries

### Category 2: Processing Agents (4 agents)  
**Purpose**: Advanced query processing, enrichment, and validation

---

## Complete Agent Breakdown

### **CLASSIFICATION AGENTS** (6 Agents)

#### 1. **Spam Detector Agent**
```python
Role: Detects spam, nonsense, or gibberish queries
Examples:
  - "asdfasdf" → spam
  - "!!!!!!" → spam
  - "hello hello hello" → spam
Output: 'spam' or 'valid'
```

#### 2. **Aggression Detector Agent**
```python
Role: Identifies hostile, aggressive, or abusive language
Examples:
  - "you idiots!" → aggressive
  - "this is garbage" → aggressive  
  - "I'm frustrated but..." → polite (NOT aggressive)
Output: 'aggressive' or 'polite'
```

#### 3. **Sensitive Data Detector Agent**
```python
Role: Flags queries containing personal sensitive information
Examples:
  - "My credit card is 1234-5678..." → sensitive
  - "SSN: 123-45-6789" → sensitive
  - "reset my password" → safe (no actual data)
Output: 'sensitive' or 'safe'
```

#### 4. **Out-of-Scope Detector Agent**
```python
Role: Detects queries unrelated to Doxa platform
Examples:
  - "where is Paris?" → out_of_scope
  - "what's the weather?" → out_of_scope
  - "how to cook pasta?" → out_of_scope
  - "pricing plans" → relevant (Doxa-related)
Output: 'out_of_scope' or 'relevant'
```

#### 5. **Ambiguity Detector Agent**
```python
Role: Detects vague or unclear queries needing clarification
Examples:
  - "help" → ambiguous
  - "I need help" → ambiguous
  - "How do I create a project?" → clear
Output: 'ambiguous' or 'clear'
```

#### 6. **RAG Validation Agent**
```python
Role: Validates if query is about Doxa platform features
Examples:
  - "How to create project?" → doxa_related
  - "Pricing plans?" → doxa_related
  - "What is AI?" → not_doxa
Output: 'doxa_related' or 'not_doxa'
```

---

### **PROCESSING AGENTS** (4 Agents)

#### 7. **Query Intent Agent** ⭐ NEW
```python
Role: Determines specific intent behind the user's query
Intent Categories:
  - 'how_to': Step-by-step instructions
  - 'information': Factual information
  - 'troubleshooting': Problem solving
  - 'comparison': Compare options
  - 'pricing': Cost/plans
  - 'feature_request': Feature availability
  - 'account': Account-related

Examples:
  "How do I create a project?" → how_to
  "What are pricing plans?" → pricing
  "I can't login" → troubleshooting
  "Does Doxa support Slack?" → feature_request

Why important: Routes to appropriate processing strategy
```

#### 8. **Context Enrichment Agent** ⭐ NEW
```python
Role: Enriches query with additional context for better RAG retrieval

Enrichment Tasks:
  1. Expand abbreviations:
     "PM" → "project management"
  
  2. Add domain context:
     "project" → "Doxa project, project management, creation"
  
  3. Add synonyms:
     "create" → "make, add, new"
  
  4. Add related concepts:
     "pricing" → "subscription, plans, cost, billing"

Example:
  Input: "How to create PM in Doxa?"
  Output: "How to create project management project in Doxa 
           platform project creation new project add project"

Why important: Better document retrieval from ChromaDB
```

#### 9. **Response Validation Agent** ⭐ NEW
```python
Role: Validates if RAG response actually answers the question

Validation Checks:
  1. Relevance: Does it address the question?
  2. Completeness: Is the answer complete?
  3. Accuracy: Does it stay within provided context?
  4. Clarity: Is it clear and well-structured?

Input:
  - Original user question
  - AI-generated response
  - Source documents used

Output: 'valid', 'partial', 'irrelevant', or 'hallucination'

Example:
  Question: "How to create a project?"
  Response: "Click Projects > New Project"
  Validation: valid

  Question: "What are pricing plans?"
  Response: "Doxa offers great features."
  Validation: irrelevant (doesn't answer question)

Why important: Prevents hallucinations and irrelevant answers
```

#### 10. **Confidence Scoring Agent** ⭐ NEW
```python
Role: Calculates confidence score (0.0-1.0) for response quality

Scoring Factors:
  1. Document Relevance (40%)
     High: 0.4, Medium: 0.25, Low: 0.1
  
  2. Response Completeness (30%)
     Complete: 0.3, Partial: 0.15, Incomplete: 0.0
  
  3. Query Clarity (20%)
     Clear: 0.2, Somewhat clear: 0.1, Vague: 0.0
  
  4. Source Quality (10%)
     Official: 0.1, Community: 0.05, Unknown: 0.0

Confidence Levels:
  0.80-1.00: High → Auto-resolve ticket
  0.60-0.79: Medium → Suggest human review
  0.40-0.59: Low → Escalate to human
  0.00-0.39: Very low → Reject/Escalate

Example:
  Clear query + Complete response + 5 docs + valid → 0.87
  Vague query + Partial response + 2 docs → 0.45

Why important: Determines if human escalation needed
```

---

## Complete Processing Pipeline

```
USER QUERY: "How do I create a project in Doxa?"
│
├─ PHASE 1: CLASSIFICATION (6 agents in parallel)
│  ├─ Spam Agent → valid ✓
│  ├─ Aggressive Agent → polite ✓
│  ├─ Sensitive Agent → safe ✓
│  ├─ Out-of-Scope Agent → relevant ✓
│  ├─ Ambiguous Agent → clear ✓
│  └─ RAG Agent → doxa_related ✓
│  Result: PROCEED to processing
│
├─ PHASE 2: INTENT ANALYSIS
│  └─ Query Intent Agent → "how_to"
│     (User wants step-by-step instructions)
│
├─ PHASE 3: CONTEXT ENRICHMENT
│  └─ Context Enrichment Agent
│     Input: "How do I create a project in Doxa?"
│     Output: "How to create project in Doxa platform 
│              project creation new project add project 
│              make project project management"
│
├─ PHASE 4: RAG PIPELINE
│  ├─ BGE Model: Generate embeddings
│  ├─ ChromaDB: Retrieve 6 relevant documents
│  └─ Gemini AI: Generate response
│     Response: "To create a project in Doxa:
│                1. Click 'Projects' in sidebar
│                2. Click 'New Project' button
│                3. Fill in project details..."
│
├─ PHASE 5: RESPONSE VALIDATION
│  └─ Response Validation Agent
│     Check: Does response answer "how to create project"?
│     Result: valid ✓ (Response has step-by-step instructions)
│
└─ PHASE 6: CONFIDENCE SCORING
   └─ Confidence Scoring Agent
      Factors:
        - Document relevance: 6 docs found (0.4)
        - Response complete: Full steps (0.3)
        - Query clear: Yes (0.2)
        - Source quality: Official docs (0.1)
      Final Score: 0.87 (High Confidence)
      Recommendation: AUTO-RESOLVE

FINAL OUTPUT:
{
  "classification": "doxa_related",
  "intent": "how_to",
  "response": "To create a project in Doxa: 1. Click...",
  "confidence_score": 0.87,
  "recommendation": "auto_resolve",
  "rag_used": true,
  "validation": "valid"
}
```

---

## API Endpoints

### Standard Processing (6 agents)
```
POST /api/v1/complaints/process
```
Uses only classification agents + RAG

### Enhanced Processing (10 agents) ⭐ NEW
```
POST /api/v1/complaints/process-enhanced
```
Uses all 10 agents with full pipeline

---

## Data Folder Structure

```
data/
├── chroma_db/              # ChromaDB persistent storage
│   └── test_collection/    # Vector database
│
├── embeddings/             # Pre-computed embeddings cache
│   └── bge_embeddings.pkl
│
└── raw_docs/              # Source documents
    ├── doxa_docs/         # Doxa documentation
    ├── faqs/              # FAQ documents
    └── manuals/           # User manuals
```

---

## Agent Communication Flow

```
Backend                     Agentic Service
(Port 8000)                (Port 8001)
    │                           │
    │  HTTP POST                │
    ├──────────────────────────►│
    │  /process-enhanced        │
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 1 │
    │                      │ 6 agents│
    │                      └────┬────┘
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 2 │
    │                      │ Intent  │
    │                      └────┬────┘
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 3 │
    │                      │ Enrich  │
    │                      └────┬────┘
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 4 │
    │                      │   RAG   │
    │                      └────┬────┘
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 5 │
    │                      │Validate │
    │                      └────┬────┘
    │                           │
    │                      ┌────▼────┐
    │                      │ Phase 6 │
    │                      │ Score   │
    │                      └────┬────┘
    │                           │
    │  HTTP Response            │
    │◄──────────────────────────┤
    │                           │
    ▼                           │
Update DB                       │
```

---

## Response Flow to Backend

### 1. **Backend Sends Request**
```python
# app/services/ai_service.py
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8001/api/v1/complaints/process-enhanced",
        json={"complaint_text": "How do I create a project?"}
    )
```

### 2. **Agentic Processes (10 agents)**
```python
# agentic/src/api/complaints.py
@router.post("/process-enhanced")
async def process_complaint_enhanced(request: ComplaintRequest):
    result = enhanced_complaint_service.process_complaint(request.complaint_text)
    # Runs all 10 agents through the pipeline
    
    return ComplaintResponse(
        classification=result["classification"],
        response=result["response"],
        rag_used=result["rag_used"]
    )
```

### 3. **Backend Receives JSON Response**
```json
{
  "complaint_id": 123,
  "classification": "doxa_related",
  "response": "To create a project in Doxa:\n1. Click 'Projects'...",
  "rag_used": true
}
```

### 4. **Backend Updates Ticket**
```python
# Backend stores response in database
ticket.ai_response = ai_result["response"]
ticket.ai_classification = ai_result["classification"]
ticket.ai_confidence_score = 0.87
ticket.status = TicketStatus.RESOLVED
```

---

## Benefits of 10-Agent Architecture

✅ **Better Accuracy**: Multiple validation layers  
✅ **Fewer Hallucinations**: Response validation catches errors  
✅ **Better RAG Retrieval**: Context enrichment improves search  
✅ **Smarter Routing**: Intent analysis guides processing  
✅ **Confidence Scoring**: Knows when to escalate to humans  
✅ **Safety**: Multiple filters catch spam, abuse, PII  

---

## Usage Examples

### Example 1: Clear Technical Question
```
Input: "How do I create a project in Doxa?"

Phase 1: doxa_related ✓
Phase 2: Intent = "how_to"
Phase 3: Enriched = "create project Doxa platform..."
Phase 4: RAG finds 6 docs, generates steps
Phase 5: Validation = "valid"
Phase 6: Confidence = 0.87

Output: Step-by-step answer, AUTO-RESOLVE
```

### Example 2: Vague Question
```
Input: "help"

Phase 1: ambiguous ❌
Output: "Please provide more details. Example: 'How do I create a project?'"
Confidence: 0.50
Recommendation: REQUEST CLARIFICATION
```

### Example 3: Out of Scope
```
Input: "What's the weather today?"

Phase 1: out_of_scope ❌
Output: "This is outside Doxa platform support."
Confidence: 0.80
Recommendation: REJECT
```

---

## Summary

**Total Agents**: 10  
**Classification**: 6 agents  
**Processing**: 4 agents  
**Endpoints**: 2 (standard + enhanced)  
**Pipeline Phases**: 6  
**Response Time**: 3-7 seconds  
**Confidence-Based**: Auto-resolve or escalate  

This architecture ensures high-quality, validated responses while protecting against spam, abuse, and hallucinations.
