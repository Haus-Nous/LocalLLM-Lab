document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');
    const modelSelect = document.getElementById('model-select');
    const tempSlider = document.getElementById('temp-slider');
    const tempVal = document.getElementById('temp-val');
    const newChatBtn = document.getElementById('new-chat-btn');
    const headerModelName = document.getElementById('header-model-name');

    let conversationHistory = [];
    let isGenerating = false;

    // Adjust textarea height automatically
    promptInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if(this.value.trim().length > 0) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Enter to submit (Shift+Enter for newline)
    promptInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if(this.value.trim().length > 0 && !isGenerating) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Temp slider display
    tempSlider.addEventListener('input', function() {
        tempVal.textContent = this.value;
    });

    // Update header dynamically
    modelSelect.addEventListener('change', function() {
        headerModelName.textContent = this.value;
    });

    // New Chat
    newChatBtn.addEventListener('click', () => {
        conversationHistory = [];
        chatMessages.innerHTML = `
            <div class="message system-msg">
                <div class="avatar"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    <p>Hello! I am your Local AI Assistant.</p>
                    <p>New conversation started.</p>
                </div>
            </div>
        `;
    });

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value.trim();
        if (!prompt || isGenerating) return;

        // Reset input
        promptInput.value = '';
        promptInput.style.height = 'auto';
        sendBtn.setAttribute('disabled', 'true');

        appendMessage('user', prompt);
        conversationHistory.push({ role: 'user', content: prompt });

        const loadingId = appendLoadingIndicator();
        isGenerating = true;
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: modelSelect.value,
                    prompt: prompt,
                    messages: conversationHistory.slice(0, -1), // Everything except the latest prompt
                    temperature: parseFloat(tempSlider.value)
                })
            });

            removeElement(loadingId);
            
            if (!response.ok) {
                const errData = await response.json();
                appendError(errData.detail || "Error generating response.");
                conversationHistory.pop(); // Remove failed user message from history
            } else {
                const data = await response.json();
                appendAIResponse(data);
                conversationHistory.push({ role: 'assistant', content: data.answer });
            }
        } catch (error) {
            removeElement(loadingId);
            appendError("Network error. Make sure FastAPI server is running.");
            conversationHistory.pop();
        } finally {
            isGenerating = false;
        }
    });

    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        // Use marked.js if available
        const parsedText = typeof marked !== 'undefined' ? marked.parse(text) : text;
        
        if (role === 'user') {
            msgDiv.innerHTML = `<div class="message-content">${parsedText}</div>`;
        }
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendAIResponse(data) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ai';
        
        const parsedAnswer = typeof marked !== 'undefined' ? marked.parse(data.answer) : data.answer;
        
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fas fa-brain"></i></div>
            <div class="message-content">
                <div class="reasoning">
                    <div class="reasoning-header">
                        <span>Reasoning</span>
                        <span>Confidence: ${(data.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div>${data.reasoning}</div>
                </div>
                <div class="answer">${parsedAnswer}</div>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendError(errorText) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message system-msg';
        msgDiv.innerHTML = `
            <div class="avatar" style="background-color: #f38ba8;"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="message-content" style="color: #f38ba8;">
                <p>${errorText}</p>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function appendLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ai';
        msgDiv.id = id;
        
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fas fa-brain"></i></div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return id;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
