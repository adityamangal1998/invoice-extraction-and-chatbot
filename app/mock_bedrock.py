"""
Temporary mock Bedrock client for testing
"""
import json
import time
import logging

logger = logging.getLogger(__name__)

class MockBedrockClient:
    def __init__(self):
        """Initialize mock client"""
        logger.info("MockBedrockClient initialized (no AWS required)")
    
    def extract_invoice_data(self, image_path, prompt):
        """Return mock invoice data for testing"""
        logger.info(f"Mock processing: {image_path}")
        
        # Simulate processing time
        time.sleep(2)
        
        # Return realistic mock data
        mock_data = {
            "invoice_number": "INV-2025-001",
            "date": "2025-08-03",  
            "vendor": "Acme Corporation",
            "vendor_address": "456 Business Ave, Commerce City, ST 67890",
            "customer": "John Smith",
            "customer_address": "123 Main Street, Anytown, ST 12345",
            "total_amount": 2712.50,
            "tax_amount": 212.50,
            "subtotal": 2500.00,
            "tax_rate": "8.5%",
            "currency": "USD",
            "items": [
                {
                    "description": "Professional Services",
                    "quantity": 10,
                    "unit_price": 150.00,
                    "total": 1500.00
                },
                {
                    "description": "Consulting Hours", 
                    "quantity": 5,
                    "unit_price": 200.00,
                    "total": 1000.00
                }
            ],
            "payment_terms": "Net 30",
            "due_date": "2025-09-02",
            "extraction_successful": True,
            "extraction_method": "Mock data for testing",
            "confidence_score": 0.95
        }
        
        logger.info("Mock extraction completed successfully")
        return mock_data
    
    def chat_with_claude(self, question, context):
        """Mock chat responses"""
        logger.info(f"Mock chat: {question}")
        
        question_lower = question.lower()
        
        # Simple keyword-based responses
        if "total" in question_lower or "amount" in question_lower:
            return "The total amount on this invoice is $2,712.50."
        elif "vendor" in question_lower or "from" in question_lower:
            return "This invoice is from Acme Corporation, located at 456 Business Ave, Commerce City, ST 67890."
        elif "date" in question_lower:
            return "The invoice date is August 3, 2025, and it's due on September 2, 2025."
        elif "items" in question_lower or "services" in question_lower:
            return "The invoice includes Professional Services (10 units at $150 each) and Consulting Hours (5 units at $200 each)."
        elif "tax" in question_lower:
            return "The tax amount is $212.50, calculated at 8.5% tax rate."
        elif "customer" in question_lower or "bill" in question_lower:
            return "This invoice is billed to John Smith at 123 Main Street, Anytown, ST 12345."
        else:
            return f"I can help you with questions about this invoice. You asked: '{question}'. The invoice contains information about vendor (Acme Corporation), total amount ($2,712.50), items, dates, and more. Please ask specific questions about these details."
