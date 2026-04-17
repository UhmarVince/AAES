/**
 * AAES Standalone Chat Widget - JavaScript Logic
 * Direct connection to Gemini-powered AI Representative.
 */

const AAES_CONFIG = {
    backendUrl: 'https://uhmarvince.pythonanywhere.com/chat',
    botName: 'AAES Representative',
    botAvatar: 'logo.png', // Reusing site logo
    initialGreeting: 'Hello! I am your AAES Representative. How can I help you with your structural engineering needs today?'
};

class AAESChatbot {
    constructor() {
        this.isOpen = false;
        this.sessionId = this.getOrCreateSessionId();
        this.init();
    }

    getOrCreateSessionId() {
        let sid = localStorage.getItem('aaes_chat_sid');
        if (!sid) {
            sid = 'web_' + Math.random().toString(36).substring(2, 15);
            localStorage.setItem('aaes_chat_sid', sid);
        }
        return sid;
    }

    init() {
        this.renderWidget();
        this.setupEventListeners();
        this.loadHistory();
    }

    renderWidget() {
        const widgetHtml = `
            <div id="aaes-chat-wrapper">
                <div id="aaes-chat-bubble" title="Chat with us">
                   <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
                </div>
                <div id="aaes-chat-window">
                    <div class="aaes-chat-header">
                        <img src="${AAES_CONFIG.botAvatar}" alt="AAES">
                        <div class="aaes-chat-header-info">
                            <h4>${AAES_CONFIG.botName}</h4>
                            <p><span class="aaes-chat-status-dot"></span> Structural AI Assistant</p>
                        </div>
                    </div>
                    <div class="aaes-chat-messages" id="aaes-msg-container">
                        <!-- Messages loaded here -->
                    </div>
                    <div id="aaes-typing-indicator" class="aaes-message bot" style="display:none; width: fit-content; margin-left: 20px;">
                        <span class="aaes-typing-dot"></span>
                        <span class="aaes-typing-dot"></span>
                        <span class="aaes-typing-dot"></span>
                    </div>
                    <div class="aaes-chat-input-area">
                        <input type="text" id="aaes-chat-input" placeholder="Type your message...">
                        <button class="aaes-chat-send-btn" id="aaes-chat-send">
                            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', widgetHtml);
    }

    setupEventListeners() {
        const bubble = document.getElementById('aaes-chat-bubble');
        const sendBtn = document.getElementById('aaes-chat-send');
        const input = document.getElementById('aaes-chat-input');

        bubble.addEventListener('click', () => this.toggleWindow());
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleWindow() {
        const window = document.getElementById('aaes-chat-window');
        this.isOpen = !this.isOpen;
        window.style.display = this.isOpen ? 'flex' : 'none';
        
        if (this.isOpen && document.querySelectorAll('.aaes-message').length === 0) {
            this.addMessage(AAES_CONFIG.initialGreeting, 'bot');
        }
    }

    async sendMessage() {
        const input = document.getElementById('aaes-chat-input');
        const message = input.value.trim();
        if (!message) return;

        input.value = '';
        this.addMessage(message, 'user');
        this.showTyping(true);

        try {
            const response = await fetch(AAES_CONFIG.backendUrl, {
                method: 'POST',
                mode: 'cors', // Explicitly enable CORS mode
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();
            this.showTyping(false);
            
            if (data.response) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage("I'm having trouble connecting to my engineers. Please try again or email us at admin@aa-engineers.net.", 'bot');
            }
        } catch (error) {
            console.error('AAES Chat Error DETAILED:', error);
            this.showTyping(false);
            this.addMessage("Connection error. Our team is aware—please try back in a moment!", 'bot');
        }
    }

    addMessage(text, side) {
        const container = document.getElementById('aaes-msg-container');
        const msgDiv = document.createElement('div');
        msgDiv.className = `aaes-message ${side}`;
        msgDiv.textContent = text;
        container.appendChild(msgDiv);
        container.scrollTop = container.scrollHeight;
        
        // Save to session history (simplified)
        this.saveToHistory(text, side);
    }

    showTyping(show) {
        document.getElementById('aaes-typing-indicator').style.display = show ? 'block' : 'none';
        const container = document.getElementById('aaes-msg-container');
        container.scrollTop = container.scrollHeight;
    }

    saveToHistory(text, side) {
        let history = JSON.parse(sessionStorage.getItem('aaes_chat_history') || '[]');
        history.push({ text, side });
        sessionStorage.setItem('aaes_chat_history', JSON.stringify(history));
    }

    loadHistory() {
        const history = JSON.parse(sessionStorage.getItem('aaes_chat_history') || '[]');
        history.forEach(msg => this.addMessage(msg.text, msg.side));
    }
}

// Initialize when DOM is ready
function initAAESChat() {
    if (!window.aaesChat) {
        window.aaesChat = new AAESChatbot();
        
        // Global listener for AI Consultation triggers (AI Engineering Gateway)
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-trigger="ai-consult"]');
            if (trigger && window.aaesChat) {
                const topic = trigger.getAttribute('data-topic');
                window.aaesChat.openWithTopic(topic);
            }
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAAESChat);
} else {
    initAAESChat();
}

/**
 * Extension of AAESChatbot for contextual triggers
 */
AAESChatbot.prototype.openWithTopic = function(topic) {
    const windowEl = document.getElementById('aaes-chat-window');
    
    // 1. Open the window
    if (!this.isOpen) {
        this.isOpen = true;
        windowEl.style.display = 'flex';
    }

    // 2. Determine greeting based on topic
    let greeting = "";
    switch(topic.toLowerCase()) {
        case 'structural design':
            greeting = "I see you're interested in structural design! Let's plan your structure. What type of project are we looking at (Residential, Commercial, or Industrial)?";
            break;
        case 'structural assessment':
            greeting = "Building safety is our priority. Tell me about the structure you want us to assess (location, age, or current condition).";
            break;
        case 'code compliance':
            greeting = "Engineering integrity starts with code compliance. What certifications or permits do you need help with today?";
            break;
        default:
            greeting = AAES_CONFIG.initialGreeting;
    }

    // 3. Clear existing messages if it's just the initial greeting to keep it focused
    const container = document.getElementById('aaes-msg-container');
    if (container.querySelectorAll('.aaes-message').length <= 1) {
        container.innerHTML = '';
        sessionStorage.removeItem('aaes_chat_history');
    }

    // 4. Add the contextual message
    this.addMessage(greeting, 'bot');

    // 5. Scroll to the widget for better visibility (Mobile Support)
    document.getElementById('aaes-chat-wrapper').scrollIntoView({ behavior: 'smooth', block: 'end' });
};
