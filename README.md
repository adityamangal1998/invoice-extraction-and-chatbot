# 🧾 Invoice Extraction & Chatbot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![Claude 3.5](https://img.shields.io/badge/Claude-3.5%20Vision-purple.svg)](https://www.anthropic.com/claude)

*AI-Powered Invoice Data Extraction and Interactive Chatbot using Claude 3.5 Vision via AWS Bedrock*

[Demo](#demo) • [Features](#features) • [Quick Start](#quick-start) • [Usage](#usage) • [API](#api)

</div>

---

## 🌟 Overview

A sophisticated Flask web application that combines **computer vision** and **natural language processing** to extract structured data from invoice images and provide an intelligent chatbot interface for querying the extracted information.

### 🎯 Key Highlights

- **🤖 AI-Powered**: Uses Claude 3.5 Vision model via AWS Bedrock for accurate data extraction
- **💬 Interactive Chat**: Natural language queries about invoice data with RAG implementation  
- **🔍 Advanced Image Zoom**: Professional zoom functionality with modal and inline controls
- **📱 Responsive Design**: Modern Bootstrap 5 UI with mobile-first approach
- **🚀 Production Ready**: Uvicorn ASGI server with fallback to Flask development server
- **🔒 Secure**: Proper session management and CORS handling

---

## ✨ Features

### 🖼️ **Invoice Processing**
- **Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, WEBP (max 16MB)
- **Real-time Processing**: Upload and extract data in seconds
- **Structured Output**: JSON format with comprehensive invoice data
- **Image Serving**: Secure image access with session-based URLs

### 💬 **Intelligent Chatbot**
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: RAG implementation for accurate answers
- **Pre-built Suggestions**: Quick access to common queries
- **Session Persistence**: Chat history maintained across page loads

### 🔍 **Advanced Image Zoom**
- **Inline Zoom Controls**: Zoom in/out buttons on both screens
- **Modal Zoom**: Full-screen zoom with professional controls
- **Keyboard Shortcuts**: `+`, `-`, `0`, `F` for zoom operations
- **Mouse Wheel Support**: Ctrl+scroll for smooth zooming
- **Touch Gestures**: Mobile-friendly zoom interactions

### 🎨 **Modern UI/UX**
- **Bootstrap 5**: Professional, responsive design
- **FontAwesome Icons**: Beautiful iconography throughout
- **Smooth Animations**: CSS3 transitions and hover effects
- **Dark/Light Themes**: Consistent color scheme
- **Mobile Optimized**: Works seamlessly on all devices

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account with Bedrock access
- Claude 3.5 model access in AWS Bedrock

### 1️⃣ Installation

```bash
# Clone the repository
git clone https://github.com/adityamangal1998/invoice-extraction-and-chatbot.git
cd invoice-extraction-and-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ AWS Configuration

Create a `.env` file in the project root:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-2

# Optional: Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_REGION=us-east-2
```

### 3️⃣ Run the Application

```bash
# Start with Uvicorn (recommended)
python main.py

# Alternative: Flask development server
python flask_main.py

# Legacy: Original Flask server
python run.py
```

### 4️⃣ Access the Application

Open your browser and navigate to:
- **Main Application**: http://localhost:8000
- **Chat Interface**: http://localhost:8000/chat
- **API Test**: http://localhost:8000/test

---

## 📁 Project Structure

```
invoice-extraction-and-chatbot/
├── 📂 app/                          # Main application package
│   ├── 📂 templates/                # HTML templates
│   │   ├── 🏠 index.html           # Main upload page
│   │   └── 💬 chat.html            # Chatbot interface
│   ├── 📂 static/                   # Static assets
│   │   ├── 📂 css/
│   │   │   └── 🎨 style.css        # Custom styles
│   │   └── 📂 js/
│   │       └── 💬 chat.js          # Chat functionality
│   ├── 📂 prompts/                  # AI prompts
│   │   └── 📝 invoice_prompt.txt   # Claude extraction prompt
│   ├── 🔧 __init__.py              # App factory
│   ├── 🛣️ routes.py               # API endpoints
│   ├── 🤖 bedrock_client.py       # AWS Bedrock integration
│   ├── 💬 chatbot.py              # RAG chatbot logic
│   └── 🔧 utils.py                # Helper functions
├── 📂 uploads/                      # Uploaded invoice images
├── 📂 sample_images/               # Test images
├── 🚀 main.py                      # Uvicorn server entry point
├── 🐍 flask_main.py               # Flask server alternative
├── 🔧 run.py                      # Legacy entry point
├── 📋 requirements.txt             # Dependencies
├── 🔐 .env.example                # Environment template
└── 📖 README.md                   # This file
```

---

## 🎮 Usage Guide

### 📤 **Upload & Extract**

1. **Navigate** to the main page (http://localhost:8000)
2. **Upload** an invoice image using the file selector
3. **Extract** data by clicking "Extract Invoice Data"
4. **View** the structured results with image preview
5. **Use zoom controls** to examine invoice details

### 💬 **Chat Interface**

1. **Navigate** to the chat page (http://localhost:8000/chat)
2. **Ask questions** about your uploaded invoice:
   - "What is the total amount?"
   - "Who is the vendor?"
   - "When is the due date?"
   - "List all line items"
3. **Use suggestions** for quick queries
4. **View invoice** with zoom controls in the left panel

### 🔍 **Zoom Functionality**

#### **Inline Zoom Controls**
- **Location**: Below invoice images on both screens
- **Buttons**: 🔍➖ Zoom Out | **100%** Reset | 🔍➕ Zoom In
- **Range**: 50% to 200% in 20% increments

#### **Modal Zoom**
- **Trigger**: Click any invoice image
- **Controls**: Full-screen modal with advanced zoom
- **Features**: Fullscreen, download, keyboard shortcuts

#### **Keyboard Shortcuts**
- **`+` or `=`**: Zoom in
- **`-`**: Zoom out  
- **`0`**: Reset zoom to 100%
- **`F`**: Toggle fullscreen
- **`Ctrl + Scroll`**: Mouse wheel zoom

---

## 🔌 API Reference

### **Upload Invoice**
```http
POST /upload
Content-Type: multipart/form-data

Parameters:
- invoice_file: Image file (PNG, JPG, JPEG, GIF, BMP, WEBP)

Response:
{
  "success": true,
  "data": {
    "total_amount": "929.50",
    "vendor": "CLEANING SERVICES",
    "invoice_number": "INV-13456",
    "due_date": "12/06/2013",
    "line_items": [...],
    ...
  },
  "image_url": "/uploads/invoice_123.jpg"
}
```

### **Chat with Invoice**
```http
POST /chat/message
Content-Type: application/json

Body:
{
  "message": "What is the total amount?"
}

Response:
{
  "success": true,
  "response": "The total amount on this invoice is $929.50."
}
```

### **Check Status**
```http
GET /status

Response:
{
  "success": true,
  "has_invoice": true,
  "invoice_file": "invoice_123.jpg",
  "image_url": "/uploads/invoice_123.jpg"
}
```

---

## 🛠️ Technologies

### **Backend**
- **Flask 2.3+**: Web framework
- **Uvicorn**: ASGI server for production
- **AWS Bedrock**: AI model hosting
- **Boto3**: AWS SDK

### **AI/ML**
- **Claude 3.5 Vision**: Invoice data extraction
- **RAG Implementation**: Context-aware chatbot responses
- **Sentence Transformers**: Text embeddings

### **Frontend**
- **Bootstrap 5**: Responsive UI framework
- **FontAwesome 6**: Icon library
- **Vanilla JavaScript**: Client-side logic
- **CSS3**: Modern styling and animations

### **Storage & Processing**
- **Pillow**: Image processing
- **Session Management**: Server-side storage
- **File Upload**: Secure image handling

---

## 🧪 Testing

### **Run Tests**
```bash
# Test server connection
python -c "import requests; print(requests.post('http://localhost:8000/test', json={'test': 'data'}).json())"

# Test invoice upload
python test_zoom_buttons.py

# Complete functionality test
python zoom_test_complete.py
```

### **Manual Testing**
1. **Upload Test**: Use sample images from `sample_images/`
2. **Extraction Test**: Verify structured data output
3. **Chat Test**: Ask various questions about uploaded invoice
4. **Zoom Test**: Try all zoom controls and shortcuts
5. **Mobile Test**: Test responsive design on mobile devices

---

## 🔧 Configuration

### **Environment Variables**
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-2

# Bedrock Configuration (optional)
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_REGION=us-east-2

# Flask Configuration (optional)
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

### **Server Configuration**
```python
# main.py - Uvicorn configuration
uvicorn.run(
    app,
    host="127.0.0.1",
    port=8000,
    reload=False,
    workers=1
)

# flask_main.py - Flask configuration
app.run(
    host="127.0.0.1",
    port=8000,
    debug=True,
    threaded=True
)
```

---

## 🚀 Deployment

### **Local Development**
```bash
python main.py  # Uvicorn server (recommended)
```

### **Production**
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### **Docker** (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude 3.5 Vision model
- **AWS** for Bedrock platform
- **Bootstrap** for UI components
- **FontAwesome** for icons

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/adityamangal1998/invoice-extraction-and-chatbot/issues)
- **Email**: adityamangal98@gmail.com
- **Documentation**: [Wiki](https://github.com/adityamangal1998/invoice-extraction-and-chatbot/wiki)

---

<div align="center">

**Made with ❤️ by [Aditya Mangal](https://github.com/adityamangal1998)**

⭐ **Star this repo if you find it helpful!**

</div>
