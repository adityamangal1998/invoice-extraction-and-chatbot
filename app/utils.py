import os
import json
import base64
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}) -> bool:
    """
    Check if file has allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Boolean indicating if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder: str) -> str:
    """
    Save uploaded file to the uploads folder.
    
    Args:
        file: Flask file object
        upload_folder: Path to upload folder
        
    Returns:
        Path to saved file
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)
    filename = f"{name}_{timestamp}{ext}"
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    logger.info(f"Saved uploaded file to: {file_path}")
    return file_path

def format_json_for_display(data: dict) -> str:
    """
    Format JSON data for better display in HTML.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted JSON string
    """
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.error(f"Error formatting JSON: {str(e)}")
        return str(data)

def load_prompt_template(prompt_file: str) -> str:
    """
    Load prompt template from file.
    
    Args:
        prompt_file: Path to prompt file
        
    Returns:
        Prompt template string
    """
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {prompt_file}")
        return get_default_prompt()
    except Exception as e:
        logger.error(f"Error loading prompt file: {str(e)}")
        return get_default_prompt()

def get_default_prompt() -> str:
    """
    Get default invoice extraction prompt.
    
    Returns:
        Default prompt string
    """
    return """
Please analyze this invoice image and extract all relevant information in a structured JSON format.

Include the following information if available:
- Invoice number
- Date
- Due date
- Vendor/Supplier information (name, address, contact details)
- Bill to/Customer information (name, address)
- Line items (description, quantity, unit price, total)
- Subtotal
- Tax information
- Total amount
- Payment terms
- Any additional notes or special instructions

Structure the response as a valid JSON object with clear field names. If any information is not clearly visible or available, indicate it as null or "Not specified".

Example structure:
{
  "invoice_number": "INV-001",
  "date": "2023-12-01",
  "vendor": {
    "name": "Company Name",
    "address": "123 Main St, City, State"
  },
  "total_amount": 1000.00,
  "line_items": [
    {
      "description": "Product/Service",
      "quantity": 1,
      "unit_price": 1000.00,
      "total": 1000.00
    }
  ]
}
"""

def clean_filename(filename: str) -> str:
    """
    Clean filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    return secure_filename(filename)

def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def validate_invoice_data(data: dict) -> bool:
    """
    Basic validation of extracted invoice data.
    
    Args:
        data: Extracted invoice data
        
    Returns:
        Boolean indicating if data is valid
    """
    if not isinstance(data, dict):
        return False
    
    # Check if we have at least some key fields
    required_fields = ['invoice_number', 'vendor', 'total_amount', 'date']
    has_required = any(field in data for field in required_fields)
    
    return has_required or len(data) > 2  # At least some meaningful data
