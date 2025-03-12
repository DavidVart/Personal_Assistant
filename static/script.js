document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const exampleLinks = document.querySelectorAll('.example-link');
    
    // Generate a unique session ID for this browser session
    const sessionId = 'session_' + Math.random().toString(36).substring(2, 15);
    console.log('Session ID:', sessionId);
    
    // Function to add a message to the chat
    function addMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Replace newlines with <br> tags
        content = content.replace(/\n/g, '<br>');
        
        messageContent.innerHTML = content;
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to send a message to the assistant
    async function sendMessage(message) {
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input field
        userInput.value = '';
        
        try {
            // Show loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            const loadingContent = document.createElement('div');
            loadingContent.className = 'message-content';
            loadingContent.textContent = 'Thinking...';
            loadingDiv.appendChild(loadingContent);
            chatMessages.appendChild(loadingDiv);
            
            // Send request to server with session ID
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: sessionId
                })
            });
            
            // Remove loading indicator
            chatMessages.removeChild(loadingDiv);
            
            if (response.ok) {
                const data = await response.json();
                // Add assistant response to chat
                addMessage(data.response, false);
            } else {
                // Add error message
                addMessage('Sorry, I encountered an error. Please try again.', false);
            }
        } catch (error) {
            console.error('Error:', error);
            // Add error message
            addMessage('Sorry, I encountered an error. Please try again.', false);
        }
    }
    
    // Handle form submission
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    });
    
    // Handle example link clicks
    exampleLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.textContent;
            userInput.value = message;
            sendMessage(message);
        });
    });
    
    // Focus on input field when page loads
    userInput.focus();
});
    