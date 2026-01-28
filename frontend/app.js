// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const newChatBtn = document.getElementById('newChatBtn');
const toggleSidebar = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const historyList = document.getElementById('historyList');
const charCount = document.getElementById('charCount');
const statusEl = document.getElementById('status');

// State
let isGenerating = false;
let currentConversationId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerHealth();
    loadConversations().then(() => {
        // Restore last active conversation
        const lastId = localStorage.getItem('lastConversationId');
        if (lastId) {
            loadConversation(lastId);
        }
    });
});

// Event Listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearDisplay);
    newChatBtn.addEventListener('click', createNewChat);
    toggleSidebar.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    messageInput.addEventListener('input', (e) => {
        updateCharCount();
        autoResize(e.target);
    });

    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// Update character count
function updateCharCount() {
    const count = messageInput.value.length;
    charCount.textContent = `${count} / 4000`;

    if (count > 3800) {
        charCount.style.color = 'var(--error)';
    } else {
        charCount.style.color = 'var(--text-secondary)';
    }
}

// Check server health
async function checkServerHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();

        if (data.status === 'healthy' && data.model_loaded) {
            setStatus('Ready', 'ready');
        } else {
            setStatus('Model loading...', 'loading');
        }
    } catch (error) {
        setStatus('Server offline', 'error');
        console.error('Health check failed:', error);
    }
}

// Load conversations
async function loadConversations() {
    try {
        const response = await fetch('/conversations');
        const conversations = await response.json();

        historyList.innerHTML = '';

        if (conversations.length === 0) {
            historyList.innerHTML = '<p class="history-empty">No conversations yet</p>';
            return;
        }

        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'history-item';
            if (conv.id === currentConversationId) item.classList.add('active');
            item.textContent = conv.title || 'New Chat';
            item.onclick = () => loadConversation(conv.id);

            // Allow deleting with right click
            item.oncontextmenu = (e) => {
                e.preventDefault();
                if (confirm('Delete this conversation?')) {
                    deleteConversation(conv.id);
                }
            };

            historyList.appendChild(item);
        });
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

// Create new chat
async function createNewChat() {
    try {
        const response = await fetch('/conversations', { method: 'POST' });
        const data = await response.json();

        // Update current ID
        currentConversationId = data.id;
        localStorage.setItem('lastConversationId', data.id); // Save state

        // Reset UI for new empty chat
        clearDisplay(false); // keep the new ID

        // Refresh sidebar list
        await loadConversations();

        setStatus('New chat created', 'ready');
    } catch (error) {
        console.error('Error creating chat:', error);
    }
}

// Load specific conversation
async function loadConversation(id) {
    if (isGenerating) return;

    try {
        const response = await fetch(`/conversations/${id}`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            // If not found, clear storage
            if (data.error === "Conversation not found") {
                localStorage.removeItem('lastConversationId');
            }
            return;
        }

        currentConversationId = id;
        localStorage.setItem('lastConversationId', id); // Save state

        clearDisplay(false); // Don't reset ID

        // Remove welcome message
        const welcomeMsg = chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();

        // Render messages
        data.history.forEach(msg => {
            addMessage(msg.content, msg.role, msg.timestamp);
        });

        // Update active state in sidebar
        loadConversations();

    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

// Delete conversation
async function deleteConversation(id) {
    try {
        await fetch(`/conversations/${id}`, { method: 'DELETE' });
        if (currentConversationId === id) {
            currentConversationId = null;
            localStorage.removeItem('lastConversationId');
            clearDisplay();
        }
        loadConversations();
    } catch (error) {
        console.error('Error deleting conversation:', error);
    }
}

// Clear display only
function clearDisplay(resetId = true) {
    if (resetId) {
        currentConversationId = null;
        localStorage.removeItem('lastConversationId');
    }

    chatContainer.innerHTML = `
        <div class="welcome-message">
            <img src="logo.jpg" alt="Vamsify Logo" class="welcome-logo">
            <h2>Welcome to Vamsify LLM Chat</h2>
           
            <p class="welcome-hint">Start a conversation below!</p>
        </div>
    `;
}

// Set status
function setStatus(text, type = 'ready') {
    statusEl.textContent = text;
    statusEl.className = `status ${type}`;
}

// Send message
async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || isGenerating) return;

    // Clear welcome message if present
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    // Create new chat if none exists
    if (!currentConversationId) {
        await createNewChat();
        // Remove welcome message again as createNewChat restores it
        const welcomeMsg = chatContainer.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
    }

    // Add user message
    addMessage(message, 'user');

    // Clear input
    messageInput.value = '';
    updateCharCount();
    messageInput.style.height = 'auto';

    // Disable input
    isGenerating = true;
    sendBtn.disabled = true;
    setStatus('Generating...', 'loading');

    // Add typing indicator
    const typingId = addTypingIndicator();

    try {
        // Use streaming endpoint
        await streamResponse(message, typingId);
        loadConversations(); // Update title
    } catch (error) {
        console.error('Error:', error);
        removeMessage(typingId);
        addMessage('Sorry, an error occurred. Please try again.', 'assistant');
        setStatus('Error', 'error');
    } finally {
        isGenerating = false;
        sendBtn.disabled = false;
        setStatus('Ready', 'ready');
    }
}

// Stream response using Server-Sent Events
async function streamResponse(message, typingId) {
    const response = await fetch('/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message,
            conversation_id: currentConversationId
        })
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    // Remove typing indicator
    removeMessage(typingId);

    // Create assistant message container
    const messageId = addMessage('', 'assistant');
    const messageContent = document.querySelector(`[data-id="${messageId}"] .message-content`);

    // Read the stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';

    while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));

                if (data.token) {
                    fullText += data.token;
                    messageContent.textContent = fullText;
                    scrollToBottom();
                } else if (data.done) {
                    // Stream complete
                    return;
                } else if (data.error) {
                    throw new Error(data.error);
                }
            }
        }
    }
}

// Add message to chat
function addMessage(text, role, timestamp = null) {
    const messageId = `msg-${Date.now()}-${Math.random()}`;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.setAttribute('data-id', messageId);

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    // Content Wrapper
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';

    // Content
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    // Timestamp
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';

    if (timestamp) {
        const date = new Date(timestamp);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        // Show date if not today
        const today = new Date();
        const isToday = date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear();

        timeSpan.textContent = isToday ? timeStr : `${date.toLocaleDateString()} ${timeStr}`;
    } else {
        // Fallback for current messages
        const now = new Date();
        timeSpan.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Assemble
    contentWrapper.appendChild(content);
    contentWrapper.appendChild(timeSpan);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentWrapper);

    chatContainer.appendChild(messageDiv);
    scrollToBottom();

    return messageId;
}

// Add typing indicator
function addTypingIndicator() {
    const messageId = `typing-${Date.now()}`;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.setAttribute('data-id', messageId);

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';

    const content = document.createElement('div');
    content.className = 'message-content typing';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    content.appendChild(indicator);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    chatContainer.appendChild(messageDiv);
    scrollToBottom();

    return messageId;
}

// Remove message
function removeMessage(messageId) {
    const message = document.querySelector(`[data-id="${messageId}"]`);
    if (message) {
        message.remove();
    }
}

// Scroll to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Clear conversation (moved to deleteConversation)
async function clearConversation() {
    // Legacy function, using clearDisplay instead
    clearDisplay();
}
