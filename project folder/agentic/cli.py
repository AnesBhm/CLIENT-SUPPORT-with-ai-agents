"""
Command-line interface for testing the agentic AI system
This replaces the old test.py with proper architecture
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.services.classification_service import classification_service
from src.services.enhanced_rag_service import enhanced_rag_service


def main():
    """
    Main function to run classification and RAG pipeline in terminal.
    """
    print("=" * 60)
    print("DOXA RAG SYSTEM - Terminal Interface")
    print("=" * 60)
    
    # Get user query
    user_query = input("\nEnter your question: ").strip()
    
    if not user_query:
        print("Error: No query provided.")
        return
    
    print(f"\n📝 Processing query: '{user_query}'")
    print("-" * 60)
    
    # STEP 1: Classification
    print("\n🔍 Step 1: Classifying query...")
    classification = classification_service.classify_query(user_query)
    
    print(f"✅ Classification: {classification}")
    print("-" * 60)
    
    # STEP 2: Handle based on classification
    if classification == "doxa_related":
        print("\n🤖 Step 2: Running Enhanced RAG Pipeline with Feedback Loop...")
        rag_result = enhanced_rag_service.query_with_feedback_loop(user_query, max_retries=3)
        
        print(f"\n   📊 RAG Status: {rag_result['status']}")
        print(f"   🔄 Attempts: {rag_result.get('attempts', 1)}")
        
        # Show feedback history if escalated
        if rag_result['status'].startswith('escalated_') and 'feedback_history' in rag_result:
            print(f"\n   📝 Retry History:")
            for feedback in rag_result['feedback_history']:
                print(f"      • {feedback}")
        
        # Show success message if resolved after retries
        if 'success_message' in rag_result and rag_result['success_message']:
            print(f"\n   ✅ {rag_result['success_message']}")
        
        print("\n📋 RAG Response:")
        print("=" * 60)
        print(rag_result['response'])
        print("=" * 60)
        
        # Additional info based on evaluation
        if rag_result['status'] == "multiple_answers":
            print("\nℹ️ Note: Multiple valid options were found in the documentation.")
        elif rag_result['status'].startswith('escalated_'):
            print(f"\n🚨 ESCALATION: Query forwarded to human support after {rag_result.get('attempts', 3)} attempts.")
    
    elif classification == "spam":
        print("\n⚠️ Response: This appears to be spam or nonsense. Please provide a valid query.")
    
    elif classification == "aggressive":
        print("\n⚠️ Response: Your message contains aggressive language. Please rephrase politely.")
    
    elif classification == "sensitive":
        print("\n⚠️ Response: Your query contains sensitive personal information. Please avoid sharing private data.")
    
    elif classification == "out_of_scope":
        print("\n⚠️ Response: This question is outside the scope of Doxa platform support.")
        print("I can only help with questions about Doxa project management platform.")
    
    elif classification == "ambiguous":
        print("\n⚠️ Response: Your question is too vague. Please provide more specific details.")
        print("Example: Instead of 'I need help', try 'How do I create a project in Doxa?'")
    
    else:
        print(f"\n⚠️ Unknown classification: {classification}")


if __name__ == "__main__":
    main()
