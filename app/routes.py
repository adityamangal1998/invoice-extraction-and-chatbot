from flask import Blueprint, render_template, request, jsonify, current_app, session, flash, redirect, url_for, send_from_directory
import os
import json
import logging
from werkzeug.utils import secure_filename

from app.bedrock_client import BedrockClient
from app.mock_bedrock import MockBedrockClient
from app.simple_chatbot import SimpleChatbot
from app.utils import allowed_file, save_uploaded_file, format_json_for_display, load_prompt_template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
main = Blueprint('main', __name__)

# Initialize global instances
# Try to use real Bedrock client, fallback to mock if AWS credentials are missing
try:
    bedrock_client = BedrockClient()
    logger.info("✅ Real AWS Bedrock client initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ AWS Bedrock client failed to initialize: {str(e)}")
    logger.info("🔄 Falling back to Mock Bedrock client for testing")
    bedrock_client = MockBedrockClient()

chatbot = None  # Initialize lazily to avoid memory issues

def get_chatbot():
    """Lazy initialization of chatbot to avoid startup memory issues."""
    global chatbot
    if chatbot is None:
        logger.info("Initializing simple chatbot (lazy loading)...")
        chatbot = SimpleChatbot()
        logger.info("Simple chatbot initialized successfully")
    return chatbot

@main.before_request
def make_session_permanent():
    """Make session permanent for better persistence."""
    session.permanent = True
    logger.info(f"Session ID: {session.get('_id', 'New session')}")
    logger.info(f"Session keys before request: {list(session.keys())}")

@main.route('/')
def index():
    """Main page for invoice upload and extraction."""
    return render_template('index.html')

@main.route('/chat')
def chat():
    """Chat interface page."""
    logger.info("=== CHAT PAGE REQUESTED ===")
    logger.info(f"Session keys: {list(session.keys())}")
    logger.info(f"Has invoice data: {'invoice_data' in session}")
    
    try:
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering chat template: {str(e)}")
        return f"Error loading chat page: {str(e)}", 500

@main.route('/chat-test')
def chat_test():
    """Simple test route for chat debugging."""
    return """
    <html>
    <head><title>Chat Test</title></head>
    <body>
        <h1>Chat Test Page</h1>
        <p>If you can see this, Flask routing is working!</p>
        <p>Session keys: """ + str(list(session.keys())) + """</p>
        <a href="/chat">Try Chat Page</a>
    </body>
    </html>
    """

@main.route('/upload', methods=['POST', 'OPTIONS'])
def upload_invoice():
    """Handle invoice file upload and extraction."""
    logger.info("=== UPLOAD ENDPOINT CALLED ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Add CORS headers for cross-origin requests
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        for key, value in response_headers.items():
            response.headers[key] = value
        return response
    
    try:
        # Check if file was uploaded
        if 'invoice_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['invoice_file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Please upload an image file (PNG, JPG, JPEG, GIF, BMP, WEBP)'
            }), 400
        
        # Save uploaded file
        file_path = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # Load prompt template
        prompt_file = os.path.join(os.path.dirname(__file__), 'prompts', 'invoice_prompt.txt')
        prompt = load_prompt_template(prompt_file)
        
        # Extract data using AWS Bedrock Claude 3.5 Vision
        logger.info(f"🔍 Extracting invoice data from: {file_path}")
        logger.info(f"📄 Using prompt template: {prompt_file}")
        logger.info(f"🤖 Using client type: {type(bedrock_client).__name__}")
        
        extracted_data = bedrock_client.extract_invoice_data(file_path, prompt)
        
        # Log extraction results
        if isinstance(extracted_data, dict):
            if extracted_data.get('extraction_successful', True):
                logger.info("✅ Invoice extraction completed successfully")
                logger.info(f"📊 Extracted fields: {list(extracted_data.keys())}")
            else:
                logger.warning(f"⚠️ Extraction had issues: {extracted_data.get('error', 'Unknown error')}")
        else:
            logger.warning("⚠️ Unexpected extraction result format")
        
        # Store in session for chatbot
        session['invoice_data'] = extracted_data
        session['invoice_file'] = os.path.basename(file_path)
        session['invoice_file_path'] = file_path  # Store full path for serving
        session['session_id'] = session.get('session_id', os.urandom(16).hex())
        
        logger.info(f"=== INVOICE DATA STORED IN SESSION ===")
        logger.info(f"Session ID: {session.get('session_id')}")
        logger.info(f"Invoice file: {session.get('invoice_file')}")
        logger.info(f"Session keys after storing: {list(session.keys())}")
        logger.info(f"Invoice data keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Not a dict'}")
        
        # Update chatbot with new data
        if extracted_data.get('extraction_successful', True):
            chatbot_instance = get_chatbot()
            chatbot_instance.update_invoice_data(extracted_data)
            logger.info("Updated chatbot with new invoice data")
        else:
            logger.warning("Invoice extraction was not successful, skipping chatbot update")
        
        # Clean up uploaded file (optional - comment out if you want to keep files)
        # os.remove(file_path)
        
        response = jsonify({
            'success': True,
            'data': extracted_data,
            'formatted_data': format_json_for_display(extracted_data),
            'image_url': f'/uploads/{os.path.basename(file_path)}',
            'invoice_file': os.path.basename(file_path)
        })
        
        # Add CORS headers to success response
        for key, value in response_headers.items():
            response.headers[key] = value
            
        return response
        
    except Exception as e:
        logger.error(f"Error processing invoice upload: {str(e)}")
        
        error_response = jsonify({
            'success': False,
            'error': f'Error processing file: {str(e)}'
        })
        
        # Add CORS headers to error response
        for key, value in response_headers.items():
            error_response.headers[key] = value
            
        return error_response, 500

@main.route('/chat/message', methods=['POST', 'OPTIONS'])
def chat_message():
    """Handle chat messages and return AI responses."""
    logger.info("=== CHAT MESSAGE ENDPOINT CALLED ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request content type: {request.content_type}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Add CORS headers for cross-origin requests
    response_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        for key, value in response_headers.items():
            response.headers[key] = value
        return response
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data or 'message' not in data:
            logger.error("No message provided in request data")
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        user_message = data['message'].strip()
        logger.info(f"User message: '{user_message}'")
        
        if not user_message:
            logger.error("Empty message received")
            return jsonify({
                'success': False,
                'error': 'Empty message'
            }), 400
        
        # Check if we have invoice data in session
        invoice_data = session.get('invoice_data')
        logger.info(f"Invoice data in session: {bool(invoice_data)}")
        logger.info(f"Session keys: {list(session.keys())}")
        
        if not invoice_data:
            logger.error("No invoice data in session")
            return jsonify({
                'success': False,
                'error': 'No invoice data available. Please upload an invoice first.'
            }), 400
        
        # Get context from chatbot (RAG)
        logger.info("Getting context from chatbot RAG system...")
        chatbot_instance = get_chatbot()
        context = chatbot_instance.get_context_for_question(user_message)
        logger.info(f"RAG context length: {len(context) if context else 0}")
        logger.info(f"RAG context preview: {context[:200] if context else 'None'}...")
        
        # Get response from Claude
        logger.info("Sending request to Claude...")
        response = bedrock_client.chat_with_claude(user_message, context)
        logger.info(f"Claude response length: {len(response) if response else 0}")
        logger.info(f"Claude response preview: {response[:200] if response else 'None'}...")
        
        logger.info("=== CHAT MESSAGE SUCCESS ===")
        response = jsonify({
            'success': True,
            'response': response,
            'invoice_file': session.get('invoice_file', 'Unknown')
        })
        
        # Add CORS headers to response
        for key, value in response_headers.items():
            response.headers[key] = value
            
        return response
        
    except Exception as e:
        logger.error(f"=== CHAT MESSAGE ERROR ===")
        logger.error(f"Error processing chat message: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        error_response = jsonify({
            'success': False,
            'error': f'Error processing message: {str(e)}'
        })
        
        # Add CORS headers to error response
        for key, value in response_headers.items():
            error_response.headers[key] = value
            
        return error_response, 500

@main.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear session data."""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Session cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error clearing session: {str(e)}'
        }), 500

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    try:
        uploads_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(uploads_dir, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return "File not found", 404

@main.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """Simple test endpoint for debugging fetch issues."""
    logger.info("=== TEST ENDPOINT CALLED ===")
    logger.info(f"Request method: {request.method}")
    
    response = jsonify({
        'success': True,
        'message': 'Test endpoint working!',
        'method': request.method
    })
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@main.route('/status')
def status():
    """Get current session status."""
    try:
        has_invoice = 'invoice_data' in session
        invoice_file = session.get('invoice_file', None)
        image_url = f'/uploads/{invoice_file}' if invoice_file else None
        
        return jsonify({
            'success': True,
            'has_invoice': has_invoice,
            'invoice_file': invoice_file,
            'image_url': image_url
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error getting status: {str(e)}'
        }), 500
