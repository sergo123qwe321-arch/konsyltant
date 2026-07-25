document.addEventListener('DOMContentLoaded', () => {
    const loginScreen = document.getElementById('login-screen');
    const chatScreen = document.getElementById('chat-screen');
    const loginForm = document.getElementById('login-form');
    const tokenInput = document.getElementById('token-input');
    const passwordInput = document.getElementById('password-input');
    const loginError = document.getElementById('login-error');
    const loginBtn = document.getElementById('login-btn');
    const loginLoader = document.getElementById('login-loader');
    
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    const logoutBtn = document.getElementById('logout-btn');
    const sendBtn = document.getElementById('send-btn');

    let sessionToken = localStorage.getItem('session_token');

    // Автозаполнение токена из URL
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    if (urlToken) {
        tokenInput.value = urlToken;
    }

    // Проверяем сессию при загрузке
    if (sessionToken) {
        showScreen('chat');
    }

    function showScreen(screen) {
        if (screen === 'login') {
            loginScreen.classList.add('active');
            chatScreen.classList.remove('active');
        } else {
            loginScreen.classList.remove('active');
            chatScreen.classList.add('active');
            chatInput.focus();
        }
    }

    function setLoginLoading(isLoading) {
        loginBtn.disabled = isLoading;
        if (isLoading) {
            loginLoader.classList.remove('hidden');
            loginBtn.querySelector('span').textContent = 'Вход...';
        } else {
            loginLoader.classList.add('hidden');
            loginBtn.querySelector('span').textContent = 'Войти в систему';
        }
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = tokenInput.value.trim();
        const password = passwordInput.value;
        
        loginError.textContent = '';
        setLoginLoading(true);

        try {
            // 1. Проверка токена
            const verifyRes = await fetch('/api/verify-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token })
            });

            if (!verifyRes.ok) {
                throw new Error('Указанный код доступа не найден или недействителен.');
            }

            // 2. Логин
            const loginRes = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, password })
            });

            if (!loginRes.ok) {
                throw new Error('Неверный пароль.');
            }

            const data = await loginRes.json();
            sessionToken = data.session_token;
            localStorage.setItem('session_token', sessionToken);
            
            showScreen('chat');
        } catch (err) {
            loginError.textContent = err.message || 'Ошибка подключения к серверу.';
        } finally {
            setLoginLoading(false);
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('session_token');
        sessionToken = null;
        chatHistory.innerHTML = `
            <div class="message bot-message">
                <div class="msg-avatar">ИИ</div>
                <div class="msg-content">Здравствуйте! Я ваш медицинский ИИ-Консультант. Я проанализировал ваши документы и готов ответить на вопросы. Обратите внимание, я не даю самостоятельных диагнозов, а опираюсь строго на факты из ваших файлов. Чем могу помочь?</div>
            </div>
        `;
        passwordInput.value = '';
        showScreen('login');
    });

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'msg-avatar';
        avatarDiv.textContent = sender === 'bot' ? 'ИИ' : 'ВЫ';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'msg-content';
        
        if (text === 'typing') {
            contentDiv.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            msgDiv.id = 'typing-indicator';
        } else {
            contentDiv.textContent = text;
        }

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);
        chatHistory.appendChild(msgDiv);
        
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;

        appendMessage('bot', 'typing');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionToken}`
                },
                body: JSON.stringify({ message })
            });

            removeTypingIndicator();

            if (res.status === 401) {
                logoutBtn.click();
                return;
            }

            if (!res.ok) {
                throw new Error('Ошибка сервера');
            }

            const data = await res.json();
            appendMessage('bot', data.reply);
        } catch (err) {
            removeTypingIndicator();
            appendMessage('bot', 'Произошла ошибка при обращении к серверу. Попробуйте позже.');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });
});
