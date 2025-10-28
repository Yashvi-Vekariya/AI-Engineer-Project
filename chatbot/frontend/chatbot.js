class ProfessionalChatbot {
    constructor() {
        this.messages = [];
        this.isMinimized = true;
        this.loading = false;
        this.currentModel = 'llama-3.1-8b-instant';
        this.apiUrl = 'http://localhost:3000/api/chat';
        this.conversationId = this.generateId();
        this.initialize();
    }

    initialize() {
        this.createChatWidget();
        this.attachEventListeners();
        this.loadConversationHistory();
        this.testBackendConnection();
    }

    generateId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    createChatWidget() {
        const chatHTML = `
            <div id="professional-chatbot" class="professional-chatbot">
                <!-- Floating Action Button -->
                <button id="chatbot-fab" class="chatbot-fab">
                    <i class="fas fa-comments"></i>
                    <span class="notification-badge" id="notificationBadge"></span>
                </button>

                <!-- Chat Window -->
                <div id="chatbot-window" class="chatbot-window">
                    <!-- Header -->
                    <div class="chatbot-header">
                        <div class="header-content">
                            <div class="bot-info">
                                <div class="bot-avatar">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="bot-details">
                                    <h3>AI Assistant</h3>
                                    <p class="status online">
                                        <span class="status-dot"></span>
                                        Online
                                    </p>
                                </div>
                            </div>
                            <div class="header-actions">
                                <button class="icon-btn" id="modelSelector" title="Change Model">
                                    <i class="fas fa-microchip"></i>
                                </button>
                                <button class="icon-btn" id="clearChat" title="Clear Conversation">
                                    <i class="fas fa-trash"></i>
                                </button>
                                <button class="icon-btn" id="minimizeChat" title="Minimize">
                                    <i class="fas fa-minus"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Model Selector Dropdown -->
                        <div class="model-selector-dropdown" id="modelDropdown">
                            <div class="dropdown-header">
                                <h4>Select AI Model</h4>
                                <button class="close-dropdown" id="closeModelDropdown">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            <div class="model-options">
                                <div class="model-option" data-model="llama-3.1-8b-instant">
                                    <div class="model-info">
                                        <strong>Llama 3.1 8B Instant</strong>
                                        <span class="model-desc">Fastest response time</span>
                                    </div>
                                    <div class="model-badge speed">⚡ Fast</div>
                                </div>
                                <div class="model-option" data-model="llama-3.1-70b-versatile">
                                    <div class="model-info">
                                        <strong>Llama 3.1 70B Versatile</strong>
                                        <span class="model-desc">Most capable</span>
                                    </div>
                                    <div class="model-badge quality">🎯 Smart</div>
                                </div>
                                <div class="model-option" data-model="mixtral-8x7b-32768">
                                    <div class="model-info">
                                        <strong>Mixtral 8x7B</strong>
                                        <span class="model-desc">Great for coding</span>
                                    </div>
                                    <div class="model-badge balanced">⚖️ Balanced</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Messages Container -->
                    <div class="chatbot-messages" id="chatbotMessages">
                        <div class="welcome-message">
                            <div class="welcome-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="welcome-content">
                                <h4>Hello! I'm your AI Assistant 🤖</h4>
                                <p>I can help you with questions, coding, writing, analysis, and much more. How can I assist you today?</p>
                                <div class="quick-actions">
                                    <button class="quick-action" data-prompt="Help me write a professional email">
                                        <i class="fas fa-envelope"></i>
                                        Write Email
                                    </button>
                                    <button class="quick-action" data-prompt="Explain quantum computing in simple terms">
                                        <i class="fas fa-lightbulb"></i>
                                        Explain Concept
                                    </button>
                                    <button class="quick-action" data-prompt="Help me debug this JavaScript code">
                                        <i class="fas fa-code"></i>
                                        Debug Code
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Input Area -->
                    <div class="chatbot-input-area">
                        <div class="input-container">
                            <div class="input-wrapper">
                                <textarea 
                                    id="chatbotInput" 
                                    placeholder="Type your message... (Press Shift+Enter for new line)" 
                                    rows="1"
                                    maxlength="2000"
                                ></textarea>
                                <button id="sendMessage" class="send-button" disabled>
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                            <div class="input-footer">
                                <span class="char-count">0/2000</span>
                                <span class="model-indicator">
                                    <i class="fas fa-microchip"></i>
                                    <span id="currentModelDisplay">Llama 3.1 8B Instant</span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
        this.injectStyles();
    }

    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .professional-chatbot {
                --primary-color: #667eea;
                --primary-dark: #5a6fd8;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --error-color: #ef4444;
                --bg-primary: #ffffff;
                --bg-secondary: #f8fafc;
                --bg-tertiary: #f1f5f9;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --text-tertiary: #94a3b8;
                --border-color: #e2e8f0;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                --border-radius: 12px;
                --border-radius-lg: 16px;
            }

            [data-theme="dark"] .professional-chatbot {
                --bg-primary: #1e293b;
                --bg-secondary: #334155;
                --bg-tertiary: #475569;
                --text-primary: #f1f5f9;
                --text-secondary: #cbd5e1;
                --text-tertiary: #94a3b8;
                --border-color: #475569;
            }

            .professional-chatbot * {
                box-sizing: border-box;
            }

            /* Floating Action Button */
            .chatbot-fab {
                position: fixed;
                bottom: 24px;
                right: 24px;
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background: var(--primary-color);
                border: none;
                color: white;
                cursor: pointer;
                box-shadow: var(--shadow-xl);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                z-index: 10000;
            }

            .chatbot-fab:hover {
                transform: scale(1.1);
                background: var(--primary-dark);
            }

            .notification-badge {
                position: absolute;
                top: -4px;
                right: -4px;
                background: var(--error-color);
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                font-size: 0.7rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
            }

            /* Chat Window */
            .chatbot-window {
                position: fixed;
                bottom: 100px;
                right: 24px;
                width: 420px;
                height: 600px;
                background: var(--bg-primary);
                border-radius: var(--border-radius-lg);
                box-shadow: var(--shadow-xl);
                display: none;
                flex-direction: column;
                overflow: hidden;
                z-index: 9999;
                border: 1px solid var(--border-color);
                animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .chatbot-window.open {
                display: flex;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            /* Header */
            .chatbot-header {
                background: var(--primary-color);
                color: white;
                padding: 0;
                position: relative;
            }

            .header-content {
                padding: 16px 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .bot-info {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .bot-avatar {
                width: 40px;
                height: 40px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }

            .bot-details h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
            }

            .status {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 12px;
                opacity: 0.9;
                margin: 0;
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background: var(--success-color);
                border-radius: 50%;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .header-actions {
                display: flex;
                gap: 8px;
            }

            .icon-btn {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }

            .icon-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            /* Model Selector Dropdown */
            .model-selector-dropdown {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
                box-shadow: var(--shadow-lg);
                display: none;
                z-index: 100;
            }

            .model-selector-dropdown.open {
                display: block;
            }

            .dropdown-header {
                padding: 16px 20px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .dropdown-header h4 {
                margin: 0;
                color: var(--text-primary);
                font-size: 14px;
            }

            .close-dropdown {
                background: none;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 4px;
            }

            .model-options {
                padding: 8px;
            }

            .model-option {
                padding: 12px;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background 0.2s;
            }

            .model-option:hover {
                background: var(--bg-secondary);
            }

            .model-option.active {
                background: var(--bg-tertiary);
            }

            .model-info {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }

            .model-info strong {
                font-size: 13px;
                color: var(--text-primary);
            }

            .model-desc {
                font-size: 11px;
                color: var(--text-secondary);
            }

            .model-badge {
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: 600;
            }

            .model-badge.speed {
                background: #dbeafe;
                color: #1d4ed8;
            }

            .model-badge.quality {
                background: #f0fdf4;
                color: #166534;
            }

            .model-badge.balanced {
                background: #fef3c7;
                color: #92400e;
            }

            /* Messages Container */
            .chatbot-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: var(--bg-secondary);
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            .chatbot-messages::-webkit-scrollbar {
                width: 6px;
            }

            .chatbot-messages::-webkit-scrollbar-thumb {
                background: var(--border-color);
                border-radius: 3px;
            }

            .chatbot-messages::-webkit-scrollbar-thumb:hover {
                background: var(--text-tertiary);
            }

            /* Welcome Message */
            .welcome-message {
                background: var(--bg-primary);
                border-radius: var(--border-radius);
                padding: 20px;
                box-shadow: var(--shadow-sm);
                display: flex;
                gap: 12px;
            }

            .welcome-avatar {
                width: 40px;
                height: 40px;
                background: var(--primary-color);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                flex-shrink: 0;
            }

            .welcome-content h4 {
                margin: 0 0 8px 0;
                font-size: 15px;
                color: var(--text-primary);
            }

            .welcome-content p {
                margin: 0 0 16px 0;
                font-size: 14px;
                color: var(--text-secondary);
                line-height: 1.5;
            }

            .quick-actions {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .quick-action {
                background: var(--bg-secondary);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: var(--text-primary);
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .quick-action:hover {
                background: var(--bg-tertiary);
                border-color: var(--primary-color);
            }

            /* Message Styles */
            .message {
                display: flex;
                gap: 12px;
                animation: messageSlide 0.3s ease;
            }

            @keyframes messageSlide {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .message.user {
                flex-direction: row-reverse;
            }

            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                font-size: 14px;
            }

            .message.assistant .message-avatar {
                background: var(--primary-color);
                color: white;
            }

            .message.user .message-avatar {
                background: var(--bg-tertiary);
                color: var(--text-primary);
            }

            .message-content {
                max-width: 75%;
                padding: 12px 16px;
                border-radius: 16px;
                font-size: 14px;
                line-height: 1.5;
                word-wrap: break-word;
            }

            .message.assistant .message-content {
                background: var(--bg-primary);
                color: var(--text-primary);
                border-bottom-left-radius: 4px;
                box-shadow: var(--shadow-sm);
            }

            .message.user .message-content {
                background: var(--primary-color);
                color: white;
                border-bottom-right-radius: 4px;
            }

            .message-time {
                font-size: 11px;
                color: var(--text-tertiary);
                margin-top: 4px;
                text-align: right;
            }

            .message.user .message-time {
                text-align: left;
            }

            /* Typing Indicator */
            .typing-indicator {
                display: flex;
                gap: 4px;
                padding: 16px;
                background: var(--bg-primary);
                border-radius: 16px;
                border-bottom-left-radius: 4px;
                width: fit-content;
                box-shadow: var(--shadow-sm);
                align-items: center;
            }

            .typing-dots {
                display: flex;
                gap: 4px;
            }

            .typing-dots span {
                width: 8px;
                height: 8px;
                background: var(--text-tertiary);
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }

            .typing-dots span:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-dots span:nth-child(3) {
                animation-delay: 0.4s;
            }

            .typing-text {
                font-size: 12px;
                color: var(--text-secondary);
                margin-left: 8px;
            }

            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.7;
                }
                30% {
                    transform: translateY(-10px);
                    opacity: 1;
                }
            }

            /* Input Area */
            .chatbot-input-area {
                border-top: 1px solid var(--border-color);
                background: var(--bg-primary);
                padding: 16px;
            }

            .input-container {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .input-wrapper {
                display: flex;
                gap: 8px;
                align-items: flex-end;
            }

            #chatbotInput {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid var(--border-color);
                border-radius: 20px;
                font-size: 14px;
                font-family: inherit;
                background: var(--bg-primary);
                color: var(--text-primary);
                resize: none;
                max-height: 120px;
                transition: border-color 0.2s;
            }

            #chatbotInput:focus {
                outline: none;
                border-color: var(--primary-color);
            }

            #chatbotInput::placeholder {
                color: var(--text-tertiary);
            }

            .send-button {
                width: 44px;
                height: 44px;
                background: var(--primary-color);
                border: none;
                border-radius: 50%;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s;
                flex-shrink: 0;
            }

            .send-button:hover:not(:disabled) {
                background: var(--primary-dark);
                transform: scale(1.05);
            }

            .send-button:disabled {
                background: var(--text-tertiary);
                cursor: not-allowed;
                transform: none;
            }

            .input-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
                color: var(--text-tertiary);
            }

            .char-count.warning {
                color: var(--warning-color);
            }

            .char-count.error {
                color: var(--error-color);
            }

            .model-indicator {
                display: flex;
                align-items: center;
                gap: 4px;
            }

            /* Error Message */
            .error-message {
                background: #fef2f2;
                border: 1px solid #fecaca;
                color: #dc2626;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 13px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .error-message i {
                font-size: 14px;
            }

            /* Responsive Design */
            @media (max-width: 480px) {
                .chatbot-window {
                    width: calc(100vw - 32px);
                    height: calc(100vh - 120px);
                    bottom: 16px;
                    right: 16px;
                    left: 16px;
                }

                .chatbot-fab {
                    bottom: 16px;
                    right: 16px;
                }
            }
        `;

        document.head.appendChild(style);
    }

    attachEventListeners() {
        // Toggle chat window
        document.getElementById('chatbot-fab').addEventListener('click', () => this.toggleChat());
        document.getElementById('minimizeChat').addEventListener('click', () => this.toggleChat());

        // Send message
        document.getElementById('sendMessage').addEventListener('click', () => this.sendMessage());
        
        // Input events
        const input = document.getElementById('chatbotInput');
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        input.addEventListener('input', (e) => {
            this.handleInputChange(e);
            this.autoResizeTextarea(e.target);
        });

        // Model selector
        document.getElementById('modelSelector').addEventListener('click', () => this.toggleModelDropdown());
        document.getElementById('closeModelDropdown').addEventListener('click', () => this.toggleModelDropdown());
        
        // Model options
        document.querySelectorAll('.model-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectModel(e.currentTarget.dataset.model);
            });
        });

        // Clear chat
        document.getElementById('clearChat').addEventListener('click', () => this.clearConversation());

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                document.getElementById('chatbotInput').value = prompt;
                this.sendMessage();
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.model-selector-dropdown') && !e.target.closest('#modelSelector')) {
                document.getElementById('modelDropdown').classList.remove('open');
            }
        });
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    handleInputChange(e) {
        const input = e.target;
        const sendButton = document.getElementById('sendMessage');
        const charCount = document.querySelector('.char-count');
        
        const length = input.value.length;
        charCount.textContent = `${length}/2000`;
        
        // Update character count color
        charCount.className = 'char-count';
        if (length > 1500) {
            charCount.classList.add('warning');
        }
        if (length > 1900) {
            charCount.classList.add('error');
        }
        
        // Enable/disable send button
        sendButton.disabled = length === 0 || this.loading || length > 2000;
    }

    toggleChat() {
        this.isMinimized = !this.isMinimized;
        const window = document.getElementById('chatbot-window');
        const fab = document.getElementById('chatbot-fab');
        
        if (this.isMinimized) {
            window.classList.remove('open');
            fab.style.display = 'flex';
        } else {
            window.classList.add('open');
            fab.style.display = 'none';
            document.getElementById('chatbotInput').focus();
            this.scrollToBottom();
        }
        
        // Hide notification badge when opening
        if (!this.isMinimized) {
            this.hideNotification();
        }
    }

    toggleModelDropdown() {
        const dropdown = document.getElementById('modelDropdown');
        dropdown.classList.toggle('open');
    }

    selectModel(modelId) {
        this.currentModel = modelId;
        
        // Update UI
        const modelOptions = document.querySelectorAll('.model-option');
        modelOptions.forEach(option => {
            option.classList.remove('active');
            if (option.dataset.model === modelId) {
                option.classList.add('active');
            }
        });
        
        // Update model display
        const modelDisplay = document.getElementById('currentModelDisplay');
        const selectedOption = document.querySelector(`.model-option[data-model="${modelId}"]`);
        modelDisplay.textContent = selectedOption.querySelector('strong').textContent;
        
        // Close dropdown
        this.toggleModelDropdown();
        
        // Show confirmation
        this.showTempMessage(`Model switched to ${selectedOption.querySelector('strong').textContent}`, 'success');
    }

    async sendMessage() {
        const input = document.getElementById('chatbotInput');
        const message = input.value.trim();

        if (!message || this.loading || message.length > 2000) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';
        this.handleInputChange({ target: input });
        this.autoResizeTextarea(input);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ 
                    messages: this.messages,
                    model: this.currentModel
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            // Add AI response
            this.addMessage('assistant', data.message);
            
            // Save conversation
            this.saveConversationHistory();

        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('assistant', 
                `I apologize, but I encountered an error: ${error.message}. ` +
                `Please make sure the backend server is running and your API key is configured correctly.`
            );
        } finally {
            this.hideTypingIndicator();
            this.loading = false;
            input.focus();
            
            // Show notification if minimized
            if (this.isMinimized) {
                this.showNotification();
            }
        }
    }

    addMessage(role, content) {
        const message = {
            role,
            content,
            timestamp: new Date().toISOString(),
            id: this.generateMessageId()
        };
        
        this.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
    }

    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    renderMessage(message) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        
        // Remove welcome message if it's the first user message
        if (message.role === 'user' && welcomeMessage && this.messages.filter(m => m.role === 'user').length === 1) {
            welcomeMessage.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.role}`;
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${message.role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                ${this.formatMessageContent(message.content)}
                <div class="message-time">
                    ${this.formatTime(message.timestamp)}
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
    }

    formatMessageContent(content) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
        
        // Convert line breaks to <br>
        content = content.replace(/\n/g, '<br>');
        
        // Basic code formatting
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        return content;
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showTypingIndicator() {
        this.loading = true;
        const messagesContainer = document.getElementById('chatbotMessages');
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message assistant';
        typingIndicator.id = 'typingIndicator';
        typingIndicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <div class="typing-text">AI is thinking...</div>
            </div>
        `;
        
        messagesContainer.appendChild(typingIndicator);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.loading = false;
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbotMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showNotification() {
        const badge = document.getElementById('notificationBadge');
        badge.textContent = '1';
        badge.style.display = 'flex';
    }

    hideNotification() {
        const badge = document.getElementById('notificationBadge');
        badge.style.display = 'none';
    }

    showTempMessage(message, type = 'info') {
        // Implementation for temporary toast messages
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    clearConversation() {
        this.messages = [];
        const messagesContainer = document.getElementById('chatbotMessages');
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="welcome-content">
                    <h4>Hello! I'm your AI Assistant 🤖</h4>
                    <p>I can help you with questions, coding, writing, analysis, and much more. How can I assist you today?</p>
                    <div class="quick-actions">
                        <button class="quick-action" data-prompt="Help me write a professional email">
                            <i class="fas fa-envelope"></i>
                            Write Email
                        </button>
                        <button class="quick-action" data-prompt="Explain quantum computing in simple terms">
                            <i class="fas fa-lightbulb"></i>
                            Explain Concept
                        </button>
                        <button class="quick-action" data-prompt="Help me debug this JavaScript code">
                            <i class="fas fa-code"></i>
                            Debug Code
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Re-attach quick action listeners
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                document.getElementById('chatbotInput').value = prompt;
                this.sendMessage();
            });
        });
        
        this.saveConversationHistory();
        this.showTempMessage('Conversation cleared', 'success');
    }

    saveConversationHistory() {
        const history = {
            id: this.conversationId,
            messages: this.messages,
            model: this.currentModel,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('chatbot_conversation', JSON.stringify(history));
    }

    loadConversationHistory() {
        try {
            const saved = localStorage.getItem('chatbot_conversation');
            if (saved) {
                const history = JSON.parse(saved);
                this.messages = history.messages || [];
                this.conversationId = history.id || this.generateId();
                this.currentModel = history.model || 'llama-3.1-8b-instant';
                
                // Update model display
                this.selectModel(this.currentModel);
                
                // Render messages
                if (this.messages.length > 0) {
                    const messagesContainer = document.getElementById('chatbotMessages');
                    messagesContainer.innerHTML = '';
                    this.messages.forEach(msg => this.renderMessage(msg));
                }
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
        }
    }

    async testBackendConnection() {
        try {
            const response = await fetch('http://localhost:3000/api/health');
            if (response.ok) {
                console.log('✅ Backend connection successful');
            } else {
                console.warn('⚠️ Backend health check failed');
            }
        } catch (error) {
            console.error('❌ Backend connection failed:', error);
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfessionalChatbot();
});
