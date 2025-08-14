// static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const sendButton = document.getElementById('send-button');
    const recordButton = document.getElementById('record-button');
    const stopButton = document.getElementById('stop-button');
    const newChatButton = document.getElementById('new-chat-btn');
    const statusMessage = document.getElementById('status-message');
    const avatarContainer = document.getElementById('avatar-container');
    const mainConversationContainer = document.getElementById('conversation-container');
    const typingIndicator = document.querySelector('.typing-indicator');
    const welcomeMessage = document.querySelector('.welcome-message');

    let currentAudio = null;
    const markdownConverter = new showdown.Converter();

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
    } else {
        statusMessage.textContent = "Browser doesn't support Speech Recognition.";
        if (recordButton) recordButton.style.display = 'none';
        if (stopButton) stopButton.style.display = 'none';
    }

    function setUIState(state) {
        recordButton.disabled = false;
        stopButton.disabled = true;
        sendButton.disabled = false;
        textInput.disabled = false;
        avatarContainer.classList.remove('listening', 'speaking');
        statusMessage.textContent = 'Click the microphone or type to start a conversation';

        if (state === 'listening') {
            recordButton.disabled = true;
            stopButton.disabled = false;
            sendButton.disabled = true;
            textInput.disabled = true;
            avatarContainer.classList.add('listening');
            statusMessage.textContent = 'Listening...';
        } else if (state === 'processing' || state === 'speaking') {
            recordButton.disabled = true;
            stopButton.disabled = true;
            sendButton.disabled = true;
            textInput.disabled = true;
            statusMessage.textContent = 'Processing your request...';
            if (state === 'speaking') {
                avatarContainer.classList.add('speaking');
            }
        }
    }

    sendButton.addEventListener('click', handleTextInput);
    textInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleTextInput();
        }
    });

    if (recognition) {
        recordButton.addEventListener('click', () => {
            setUIState('listening');
            recognition.start();
        });
        stopButton.addEventListener('click', () => {
            recognition.stop();
            setUIState('idle');
        });
        recognition.onresult = (event) => {
            const transcribedText = event.results[0][0].transcript;
            setUIState('processing');
            processText(transcribedText);
        };
        recognition.onerror = (event) => {
            statusMessage.textContent = 'Error during recognition: ' + event.error;
            setUIState('idle');
        };
        recognition.onend = () => {
            if (avatarContainer.classList.contains('listening')) {
                 setUIState('idle');
            }
        };
    }
    
    newChatButton.addEventListener('click', startNewChat);

    function handleTextInput() {
        const userText = textInput.value.trim();
        if (userText) {
            setUIState('processing');
            processText(userText);
            textInput.value = '';
        }
    }
    
    function startNewChat() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        // Remove only the chat turn bubbles
        mainConversationContainer.querySelectorAll('.chat-turn').forEach(turn => turn.remove());
        
        // Show the welcome message again
        if (welcomeMessage) {
            welcomeMessage.style.display = 'block';
        }
        
        textInput.value = '';
        setUIState('idle');
        document.querySelectorAll('.history-item.active').forEach(activeItem => {
            activeItem.classList.remove('active');
        });
    }

    function processText(text) {
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }

        const userTurn = document.createElement('div');
        userTurn.className = 'chat-turn user-turn';
        userTurn.textContent = text;
        mainConversationContainer.insertBefore(userTurn, typingIndicator);
        
        typingIndicator.style.display = 'flex';
        mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;

        fetch('/process-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text_input: text })
        })
        .then(response => response.json())
        .then(data => {
            typingIndicator.style.display = 'none';
            const textHtml = markdownConverter.makeHtml(data.text_response || "");

            const aiTurn = document.createElement('div');
            aiTurn.className = 'chat-turn ai-turn';

            if (data.gif_url) {
                aiTurn.innerHTML = `<img src="${data.gif_url}" alt="${text}" style="max-width: 100%; border-radius: 8px;">`;
                if (data.text_response) {
                    aiTurn.insertAdjacentHTML('afterbegin', textHtml);
                }
            } else if (data.youtube_embed_url) {
                aiTurn.innerHTML = `${textHtml}<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-top: 1rem;"><iframe src="${data.youtube_embed_url}?autoplay=1" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>`;
            } else if (data.image_url) {
                aiTurn.innerHTML = `${textHtml}<img src="${data.image_url}" alt="${text}" style="max-width: 100%; border-radius: 8px; margin-top: 1rem;">`;
            } else {
                aiTurn.innerHTML = textHtml;
            }

            mainConversationContainer.insertBefore(aiTurn, typingIndicator);

            if (data.audio_url && !data.youtube_embed_url) {
                if(currentAudio) currentAudio.pause();
                currentAudio = new Audio(data.audio_url);
                currentAudio.play();
                setUIState('speaking');
                currentAudio.onended = () => setUIState('idle');
            } else {
                setUIState('idle');
            }
            
            mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.style.display = 'none';
            const errorTurn = document.createElement('div');
            errorTurn.className = 'chat-turn ai-turn';
            errorTurn.textContent = 'Failed to get a response from the server.';
            mainConversationContainer.insertBefore(errorTurn, typingIndicator);
            mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;
            setUIState('idle');
        });
    }

    function handleHistoryClick(event) {
        const item = event.currentTarget;
        const question = item.dataset.question;
        const answer = item.dataset.answer;

        startNewChat(); 

        if (welcomeMessage) welcomeMessage.style.display = 'none';

        const userTurn = document.createElement('div');
        userTurn.className = 'chat-turn user-turn';
        userTurn.textContent = question;
        mainConversationContainer.insertBefore(userTurn, typingIndicator);

        const aiTurn = document.createElement('div');
        aiTurn.className = 'chat-turn ai-turn';
        aiTurn.innerHTML = markdownConverter.makeHtml(answer);
        mainConversationContainer.insertBefore(aiTurn, typingIndicator);

        document.querySelectorAll('.history-item.active').forEach(activeItem => {
            activeItem.classList.remove('active');
        });
        item.classList.add('active');
        setUIState('idle');
    }

    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', handleHistoryClick);
    });
    
    setUIState('idle');
});