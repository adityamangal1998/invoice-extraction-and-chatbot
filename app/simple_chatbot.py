"""
Simplified chatbot without RAG for testing
"""
import logging

logger = logging.getLogger(__name__)

class SimpleChatbot:
    def __init__(self):
        """Initialize simple chatbot without heavy ML models"""
        self.invoice_data = None
        logger.info("SimpleChatbot initialized")
    
    def update_invoice_data(self, data):
        """Store invoice data"""
        self.invoice_data = data
        logger.info(f"Invoice data updated with {len(str(data))} characters")
    
    def get_context_for_question(self, question):
        """Return simple context from invoice data"""
        if not self.invoice_data:
            return "No invoice data available"
        
        # Simple string conversion of invoice data
        context = str(self.invoice_data)
        logger.info(f"Generated simple context with {len(context)} characters")
        return context
