import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.services.enhanced_rag_service import enhanced_rag_service

print("Testing RAG Service...")
try:
    result = enhanced_rag_service.query_with_feedback_loop("How do I create a project?")
    print("RAG Result:", result)
except Exception as e:
    print("RAG FAILED with error:")
    print(e)
    import traceback
    traceback.print_exc()
