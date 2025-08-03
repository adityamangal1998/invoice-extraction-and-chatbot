"""
Main entry point for the Invoice Extraction and Chatbot application.
Uses Uvicorn ASGI server to run the Flask app with better performance.
"""

import os
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from app import create_app

def ensure_directories():
    """Create necessary directories if they don't exist."""
    base_dir = os.path.dirname(__file__)
    directories = [
        os.path.join(base_dir, 'uploads'),
        os.path.join(base_dir, 'app', 'static', 'uploads')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Create Flask app
flask_app = create_app()

# Convert Flask WSGI app to ASGI for Uvicorn
app = WsgiToAsgi(flask_app)

if __name__ == "__main__":
    # Ensure required directories exist
    ensure_directories()
    
    # Run with Uvicorn
    print("🚀 Starting Invoice Extraction & Chatbot with Uvicorn...")
    print("📱 Access the app at: http://localhost:8000")
    print("🔄 Hot reload enabled for development")
    
    try:
        uvicorn.run(
            app,  # Pass app directly instead of string reference
            host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for stability
            port=8000,
            reload=False,  # Disable reload to prevent executor issues
            log_level="info",
            access_log=True,
            workers=1  # Single worker to avoid threading issues
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("🔄 Trying fallback Flask development server...")
        flask_app.run(host="127.0.0.1", port=8000, debug=True)
