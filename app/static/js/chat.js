// Chat functionality for Invoice Chatbot
class InvoiceChatbot {
    constructor() {
        console.log('=== INITIALIZING CHATBOT ===');
        
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.sendBtn = document.getElementById('sendBtn');
        this.statusText = document.getElementById('statusText');
        this.statusCard = document.getElementById('statusCard');
        
        console.log('DOM elements found:', {
            chatMessages: !!this.chatMessages,
            messageInput: !!this.messageInput,
            chatForm: !!this.chatForm,
            sendBtn: !!this.sendBtn,
            statusText: !!this.statusText,
            statusCard: !!this.statusCard
        });
        
        this.init();
    }
    
    init() {
        console.log('=== INITIALIZING CHAT FUNCTIONALITY ===');
        
        // Bind event listeners
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
            console.log('Form submit listener added');
        } else {
            console.error('Chat form not found!');
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => this.handleKeyPress(e));
            // Focus on input
            this.messageInput.focus();
            console.log('Input listeners added and focused');
        } else {
            console.error('Message input not found!');
        }
        
        // Load chat history from session storage
        this.loadChatHistory();
        
        console.log('Chat initialization complete');
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        console.log('=== CHAT MESSAGE SUBMIT ===');
        
        const message = this.messageInput.value.trim();
        console.log('User message:', message);
        
        if (!message) {
            console.log('Empty message, returning');
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable form
        this.messageInput.value = '';
        this.setFormState(false);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Add loading message
        const loadingId = this.addLoadingMessage();
        
        try {
            console.log('Sending request to /chat/message...');
            
            // Send message to backend
            const response = await fetch('/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            const result = await response.json();
            console.log('Response data:', result);
            
            // Remove loading message
            this.removeLoadingMessage(loadingId);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (result.success) {
                console.log('Chat response successful');
                // Add bot response
                this.addMessage(result.response, 'bot');
            } else {
                console.error('Chat response error:', result.error);
                // Add error message
                this.addMessage(`Error: ${result.error}`, 'bot', true);
            }
            
        } catch (error) {
            console.error('Network error:', error);
            
            // Remove loading message
            this.removeLoadingMessage(loadingId);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add network error message
            this.addMessage(`Network error: ${error.message}`, 'bot', true);
        } finally {
            console.log('Chat request completed');
            // Re-enable form
            this.setFormState(true);
            this.messageInput.focus();
        }
    }
    
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.chatForm.dispatchEvent(new Event('submit'));
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.id = messageId;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="d-flex align-items-start justify-content-end">
                        <div class="me-3">
                            <strong>You</strong>
                            <p class="mb-0 mt-1">${this.escapeHtml(content)}</p>
                        </div>
                        <div class="avatar bg-secondary text-white rounded-circle">
                            <i class="fas fa-user"></i>
                        </div>
                    </div>
                </div>
            `;
        } else {
            const iconClass = isError ? 'fas fa-exclamation-triangle' : 'fas fa-robot';
            const bgClass = isError ? 'bg-warning' : 'bg-primary';
            
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="d-flex align-items-start">
                        <div class="avatar ${bgClass} text-white rounded-circle me-3">
                            <i class="${iconClass}"></i>
                        </div>
                        <div>
                            <strong>${isError ? 'System' : 'AI Assistant'}</strong>
                            <p class="mb-0 mt-1">${this.formatBotMessage(content)}</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        this.saveChatHistory();
        
        return messageId;
    }
    
    addLoadingMessage() {
        const loadingId = 'loading_' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message';
        loadingDiv.id = loadingId;
        
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="d-flex align-items-start">
                    <div class="avatar bg-primary text-white rounded-circle me-3">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div>
                        <strong>AI Assistant</strong>
                        <p class="mb-0 mt-1">
                            <span class="loading-dots">Thinking</span>
                        </p>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(loadingDiv);
        this.scrollToBottom();
        
        return loadingId;
    }
    
    removeLoadingMessage(loadingId) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }
    
    setFormState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendBtn.disabled = !enabled;
        
        if (enabled) {
            this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        } else {
            this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    }
    
    formatBotMessage(content) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(content);
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Code blocks
        formatted = formatted.replace(/`(.*?)`/g, '<code class="bg-light px-2 py-1 rounded">$1</code>');
        
        return formatted;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    saveChatHistory() {
        const messages = Array.from(this.chatMessages.children).map(msg => ({
            id: msg.id,
            html: msg.innerHTML,
            className: msg.className
        }));
        
        sessionStorage.setItem('chatHistory', JSON.stringify(messages));
    }
    
    loadChatHistory() {
        const history = sessionStorage.getItem('chatHistory');
        if (history) {
            try {
                const messages = JSON.parse(history);
                // Only load non-system messages
                messages.forEach(msg => {
                    if (!msg.id.startsWith('msg_') || msg.className.includes('bot-message')) {
                        return; // Skip initial bot message and system messages
                    }
                    
                    const messageDiv = document.createElement('div');
                    messageDiv.id = msg.id;
                    messageDiv.className = msg.className;
                    messageDiv.innerHTML = msg.html;
                    
                    this.chatMessages.appendChild(messageDiv);
                });
                
                this.scrollToBottom();
            } catch (error) {
                console.warn('Could not load chat history:', error);
            }
        }
    }
    
    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.classList.remove('d-none');
        }
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.classList.add('d-none');
        }
    }
    
    clearChatHistory() {
        // Keep only the initial bot message
        const messages = this.chatMessages.children;
        const firstMessage = messages[0]; // The welcome message
        
        // Remove all messages except the first one
        while (messages.length > 1) {
            messages[1].remove();
        }
        
        // Clear session storage
        sessionStorage.removeItem('chatHistory');
        
        this.scrollToBottom();
    }
}

// Global functions
async function checkStatus() {
    try {
        const response = await fetch('/status');
        const result = await response.json();
        
        const statusText = document.getElementById('statusText');
        const statusCard = document.getElementById('statusCard');
        const clearChatBtn = document.getElementById('clearChatBtn');
        const suggestionsCard = document.getElementById('suggestionsCard');
        
        if (result.success) {
            // Update invoice image
            updateInvoiceImage(result);
            
            if (result.has_invoice) {
                statusText.innerHTML = `
                    <i class="fas fa-check-circle text-success me-2"></i>
                    Invoice data loaded: <strong>${result.invoice_file}</strong>
                `;
                statusCard.className = 'card mb-4 border-success';
                clearChatBtn.disabled = false;
                suggestionsCard.style.display = 'block';
            } else {
                statusText.innerHTML = `
                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                    No invoice data found. <a href="/" class="text-decoration-none">Upload an invoice first</a>
                `;
                statusCard.className = 'card mb-4 border-warning';
                clearChatBtn.disabled = true;
                suggestionsCard.style.display = 'none';
            }
        } else {
            statusText.innerHTML = `
                <i class="fas fa-times-circle text-danger me-2"></i>
                Error checking status: ${result.error}
            `;
            statusCard.className = 'card mb-4 border-danger';
            clearChatBtn.disabled = true;
            suggestionsCard.style.display = 'none';
        }
    } catch (error) {
        const statusText = document.getElementById('statusText');
        const statusCard = document.getElementById('statusCard');
        
        statusText.innerHTML = `
            <i class="fas fa-times-circle text-danger me-2"></i>
            Connection error: ${error.message}
        `;
        statusCard.className = 'card mb-4 border-danger';
    }
}

function askQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Add visual feedback
    messageInput.value = question;
    messageInput.focus();
    
    // Add a small pulse effect to the send button
    sendBtn.classList.add('pulse');
    setTimeout(() => sendBtn.classList.remove('pulse'), 1000);
    
    // Auto-submit the question after a brief delay for better UX
    setTimeout(() => {
        document.getElementById('chatForm').dispatchEvent(new Event('submit'));
    }, 300);
}

async function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        if (window.chatbot) {
            window.chatbot.clearChatHistory();
        }
        
        // Also clear session on server
        try {
            await fetch('/clear_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        } catch (error) {
            console.warn('Could not clear server session:', error);
        }
        
        // Refresh status
        checkStatus();
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chatbot
    window.chatbot = new InvoiceChatbot();
    
    // Check status periodically
    setInterval(checkStatus, 30000); // Check every 30 seconds
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        checkStatus(); // Check status when page becomes visible
    }
});

// Update invoice image display
function updateInvoiceImage(statusData) {
    const invoiceImage = document.getElementById('invoiceImage');
    const noInvoiceMessage = document.getElementById('noInvoiceMessage');
    const invoiceInfo = document.getElementById('invoiceInfo');
    const invoiceFileName = document.getElementById('invoiceFileName');
    const chatZoomControls = document.getElementById('chatZoomControls');
    
    console.log('Updating invoice image...', statusData);
    
    if (statusData.has_invoice && statusData.image_url) {
        // Show image
        if (invoiceImage) {
            invoiceImage.src = statusData.image_url;
            invoiceImage.classList.remove('d-none');
        }
        
        // Hide no invoice message
        if (noInvoiceMessage) {
            noInvoiceMessage.classList.add('d-none');
        }
        
        // Show invoice info
        if (invoiceInfo && invoiceFileName) {
            invoiceFileName.textContent = statusData.invoice_file || 'invoice.jpg';
            invoiceInfo.classList.remove('d-none');
        }
        
        // Show zoom controls
        if (chatZoomControls) {
            chatZoomControls.classList.remove('d-none');
        }
        
        console.log('✅ Invoice image loaded:', statusData.image_url);
    } else {
        // Hide image
        if (invoiceImage) {
            invoiceImage.classList.add('d-none');
        }
        
        // Show no invoice message
        if (noInvoiceMessage) {
            noInvoiceMessage.classList.remove('d-none');
        }
        
        // Hide invoice info
        if (invoiceInfo) {
            invoiceInfo.classList.add('d-none');
        }
        
        // Hide zoom controls
        if (chatZoomControls) {
            chatZoomControls.classList.add('d-none');
        }
        
        console.log('ℹ️ No invoice image to display');
    }
}
