// static/js/script.js

window.addEventListener('load', () => {
    // --- 1. ELEMENT SELECTORS ---
    // ... (no changes here)
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
    const imageUploadInput = document.getElementById('image-upload-input');
    const sketchButton = document.getElementById('sketch-button');
    const memeModal = document.getElementById('meme-modal');
    const memeButton = document.getElementById('meme-button');
    const closeModal = document.getElementById('close-modal');
    const generateMemeBtn = document.getElementById('generate-meme-btn');
    const memeImageInput = document.getElementById('meme-image-input');
    const memeTopText = document.getElementById('meme-top-text');
    const memeBottomText = document.getElementById('meme-bottom-text');
    const suggestTextBtn = document.getElementById('suggest-text-btn');
    const suggestionSpinner = document.getElementById('suggestion-spinner');


    // --- 2. GLOBAL VARIABLES & SESSION SETUP ---
    // ... (no changes here)
    let currentAudio = null;
    let conversationHistory = [];
    let currentDbId = null; // The database ID for the current conversation
    const markdownConverter = new showdown.Converter();
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    // Function to save the current session to sessionStorage
    const saveSession = () => {
        const sessionData = {
            history: conversationHistory,
            db_id: currentDbId
        };
        sessionStorage.setItem('genivus_session', JSON.stringify(sessionData));
    };

    // Function to load a session from sessionStorage on page load
    const loadSession = () => {
        const savedSession = sessionStorage.getItem('genivus_session');
        if (savedSession) {
            const sessionData = JSON.parse(savedSession);
            conversationHistory = sessionData.history || [];
            currentDbId = sessionData.db_id || null;

            if (conversationHistory.length > 0) {
                if (welcomeMessage) welcomeMessage.style.display = 'none';
                mainConversationContainer.innerHTML = ''; // Clear container before rendering
                conversationHistory.forEach(turn => {
                    renderTurn(turn.role, turn.parts[0].text);
                });
                mainConversationContainer.appendChild(typingIndicator); // Re-add typing indicator
            }
        }
    };

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
    } else {
        if (recordButton) recordButton.style.display = 'none';
        if (stopButton) stopButton.style.display = 'none';
    }
    setUIState('idle');
    loadSession(); // Load any active session when the page loads


    // --- 3. EVENT LISTENERS ---
    // ... (no changes here)
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
            processText(event.results[0][0].transcript);
        };

        recognition.onerror = (event) => {
            statusMessage.textContent = 'Error: ' + event.error;
            setUIState('idle');
        };
        recognition.onend = () => {
            if (avatarContainer.classList.contains('listening')) setUIState('idle');
        };
    }

    newChatButton.addEventListener('click', startNewChat);

    // Add event listeners for the delete buttons
    document.querySelectorAll('.delete-history-btn').forEach(button => {
        button.addEventListener('click', handleDeleteHistory);
    });

    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', handleHistoryClick);
    });
    
    // ... (All other event listeners for sketch, meme, etc. remain unchanged) ...
    sketchButton.addEventListener('click', () => {
        imageUploadInput.click();
    });
    imageUploadInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) uploadAndProcessImage(file);
        imageUploadInput.value = '';
    });

    memeButton.addEventListener('click', () => {
        memeModal.style.display = 'block';
    });
    closeModal.addEventListener('click', () => {
        memeModal.style.display = 'none';
    });
    window.addEventListener('click', (event) => {
        if (event.target == memeModal) memeModal.style.display = 'none';
    });
    generateMemeBtn.addEventListener('click', () => {
        const file = memeImageInput.files[0];
        if (!file) {
            alert('Please upload an image first!');
            return;
        }
        memeModal.style.display = 'none';
        uploadAndGenerateMeme(file, memeTopText.value, memeBottomText.value);
    });

    suggestTextBtn.addEventListener('click', () => {
        const file = memeImageInput.files[0];
        if (!file) {
            alert('Please upload an image before asking for a suggestion!');
            return;
        }
        suggestionSpinner.style.display = 'block';
        suggestTextBtn.disabled = true;
        const formData = new FormData();
        formData.append('image', file);
        fetch('/suggest-meme-text', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                memeTopText.value = data.top_text || '';
                memeBottomText.value = data.bottom_text || '';
            })
            .catch(error => {
                alert('Sorry, the AI could not come up with a suggestion.');
            })
            .finally(() => {
                suggestionSpinner.style.display = 'none';
                suggestTextBtn.disabled = false;
            });
    });

    // --- 4. CORE FUNCTIONS ---

    function setUIState(state) {
        // ... (no changes in this function)
        const isProcessing = state === 'listening' || state === 'processing';
        recordButton.disabled = isProcessing;
        stopButton.disabled = state !== 'listening';
        sendButton.disabled = isProcessing;
        textInput.disabled = isProcessing;
        avatarContainer.classList.toggle('listening', state === 'listening');
        avatarContainer.classList.toggle('speaking', state === 'speaking');
        statusMessage.textContent = state === 'listening' ? 'Listening...' : (state === 'processing' ? 'Processing...' : 'Click the mic or type to start');

    }

    function handleTextInput() {
        // ... (no changes in this function)
        const userText = textInput.value.trim();
        if (userText) {
            processText(userText);
            textInput.value = '';
        }
    }
    
    function renderTurn(role, text) {
        // ... (no changes in this function)
        const turnDiv = document.createElement('div');
        if (role === 'user') {
            turnDiv.className = 'chat-turn user-turn';
            turnDiv.textContent = text;
        } else { // 'model'
            turnDiv.className = 'chat-turn ai-turn';
            turnDiv.innerHTML = markdownConverter.makeHtml(text);
        }
        mainConversationContainer.insertBefore(turnDiv, typingIndicator);

    }

    function startNewChat() {
        // ... (no changes in this function)
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        conversationHistory = [];
        currentDbId = null;
        sessionStorage.removeItem('genivus_session'); // Clear session storage
        mainConversationContainer.querySelectorAll('.chat-turn').forEach(turn => turn.remove());
        if (welcomeMessage) welcomeMessage.style.display = 'block';
        textInput.value = '';
        setUIState('idle');

    }

    function processText(text) {
        // ... (no changes in this function)
        if (welcomeMessage) welcomeMessage.style.display = 'none';
        setUIState('processing');
        renderTurn('user', text); // Render the user's message immediately
        typingIndicator.style.display = 'flex';
        mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;

        fetch('/process-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text_input: text,
                history: conversationHistory, // Send the history *before* the new message
                db_id: currentDbId
            })
        })
        .then(response => response.json())
        .then(data => {
            typingIndicator.style.display = 'none';
            renderTurn('model', data.text_response); // Render AI response

            // Update history and save session
            conversationHistory.push({ role: 'user', parts: [{ text: text }] });
            conversationHistory.push({ role: 'model', parts: [{ text: data.text_response }] });
            if (data.db_id) {
                currentDbId = data.db_id;
            }
            saveSession();

            // Handle audio playback
            if (data.audio_url && !data.youtube_embed_url) {
                if (currentAudio) currentAudio.pause();
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
            typingIndicator.style.display = 'none';
            renderTurn('model', 'Sorry, I encountered an error.');
            setUIState('idle');
        });
    }

    // --- THIS IS THE CORRECTED FUNCTION ---
    function handleHistoryClick(event) {
        if (event.target.classList.contains('delete-history-btn')) {
            return; // Don't do anything if the delete button was clicked
        }

        const item = event.currentTarget;
        const answerString = item.dataset.answer;
        const dbId = item.dataset.dbId;

        startNewChat(); // Always clear the current session first
        if (welcomeMessage) welcomeMessage.style.display = 'none';

        // Check if the data is in the new JSON format (a string starting with '[')
        if (answerString && answerString.trim().startsWith('[')) {
            try {
                const historyLog = JSON.parse(answerString);

                // Load the full conversation into the active session
                conversationHistory = historyLog;
                currentDbId = dbId;
                saveSession(); // Make this the active session in sessionStorage

                // Render the entire chat log
                historyLog.forEach(turn => {
                    renderTurn(turn.role, turn.parts[0].text);
                });
            } catch (e) {
                console.error("Failed to parse history log:", e);
                // Fallback for malformed JSON
                renderTurn('user', item.dataset.question);
                renderTurn('model', "Sorry, this conversation couldn't be loaded.");
            }
        } else {
            // It's an old, plain-text answer. Just display it as a single Q&A.
            const question = item.dataset.question;
            renderTurn('user', question);
            renderTurn('model', answerString);
            // The session remains "new", so any follow-up message will start a new chat log.
        }
        mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;
    }


    function handleDeleteHistory(event) {
        // ... (no changes in this function)
        event.stopPropagation(); // Stop the click from triggering the parent's click event
        const button = event.currentTarget;
        const historyId = button.dataset.id;
        const historyItemElement = button.closest('.history-item');

        if (confirm('Are you sure you want to delete this conversation?')) {
            fetch(`/delete-history/${historyId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    historyItemElement.remove(); // Remove from the sidebar
                    // If the deleted history was the one currently active, start a new chat
                    if (currentDbId == historyId) {
                        startNewChat();
                    }
                } else {
                    alert('Failed to delete conversation: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting history:', error);
                alert('An error occurred while deleting the conversation.');
            });
        }

    }
    
    // ... (uploadAndProcessImage and uploadAndGenerateMeme are unchanged) ...
    function uploadAndProcessImage(file) {
        if (welcomeMessage) welcomeMessage.style.display = 'none';
        setUIState('processing');
        const formData = new FormData();
        formData.append('image', file);
        const userTurn = document.createElement('div');
        userTurn.className = 'chat-turn user-turn';
        userTurn.textContent = `Generate a sketch for: ${file.name}`;
        mainConversationContainer.insertBefore(userTurn, typingIndicator);
        typingIndicator.style.display = 'flex';
        fetch('/upload-image', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                typingIndicator.style.display = 'none';
                if (data.sketch_url) {
                    const aiTurn = document.createElement('div');
                    aiTurn.className = 'chat-turn ai-turn';
                    aiTurn.innerHTML = `<p>Here is the sketch I generated:</p><img src="${data.sketch_url}" alt="Sketch" style="max-width:100%;border-radius:8px;margin-top:1rem;">`;
                    mainConversationContainer.insertBefore(aiTurn, typingIndicator);
                } else {
                    throw new Error(data.error || 'Failed to get response.');
                }
                mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;
                setUIState('idle');
})
            .catch(error => {
                typingIndicator.style.display = 'none';
                const errorTurn = document.createElement('div');
                errorTurn.className = 'chat-turn ai-turn';
                errorTurn.textContent = `Sorry, I couldn't create a sketch.`;
                mainConversationContainer.insertBefore(errorTurn, typingIndicator);
                setUIState('idle');
            });
    }

    function uploadAndGenerateMeme(file, topText, bottomText) {
        if (welcomeMessage) welcomeMessage.style.display = 'none';
        setUIState('processing');
        const formData = new FormData();
        formData.append('image', file);
        formData.append('top_text', topText);
        formData.append('bottom_text', bottomText);
        const userTurn = document.createElement('div');
        userTurn.className = 'chat-turn user-turn';
        userTurn.textContent = `Generate a meme from: ${file.name}`;
        mainConversationContainer.insertBefore(userTurn, typingIndicator);
        typingIndicator.style.display = 'flex';
        fetch('/generate-meme', { method: 'POST', body: formData })
            .then(response => response.json())
            .then(data => {
                typingIndicator.style.display = 'none';
                if (data.meme_url) {
                    const aiTurn = document.createElement('div');
                    aiTurn.className = 'chat-turn ai-turn';
                    aiTurn.innerHTML = `<p>Here's the meme you asked for:</p><img src="${data.meme_url}" alt="Meme" style="max-width:100%;border-radius:8px;margin-top:1rem;">`;
                    mainConversationContainer.insertBefore(aiTurn, typingIndicator);
                } else {
                    throw new Error(data.error || 'Failed to get response.');
                }
                mainConversationContainer.scrollTop = mainConversationContainer.scrollHeight;
                setUIState('idle');
            })
            .catch(error => {
                typingIndicator.style.display = 'none';
                const errorTurn = document.createElement('div');
                errorTurn.className = 'chat-turn ai-turn';
                errorTurn.textContent = `Sorry, I couldn't create that meme.`;
                mainConversationContainer.insertBefore(errorTurn, typingIndicator);
                setUIState('idle');
            });
    }


});