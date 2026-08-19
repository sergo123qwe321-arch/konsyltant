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
    const activeUrlToken = localStorage.getItem('active_url_token');

    // Проверка токена в URL для изоляции мультитенантности
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');

    // Если открыли ссылку с новым токеном, сбрасываем старую сессию чужого пациента
    if (urlToken && urlToken !== activeUrlToken) {
        console.log("[MULTI-TENANT SAFETY] Сброс сессии чужого пациента. Новый токен из URL:", urlToken);
        localStorage.removeItem('session_token');
        localStorage.setItem('active_url_token', urlToken);
        sessionToken = null;
    }

    if (urlToken) {
        tokenInput.value = urlToken;
    }

    // Проверяем сессию при загрузке
    if (sessionToken) {
        showScreen('chat');
    } else {
        showScreen('login');
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
            localStorage.setItem('active_url_token', token);
            
            // Очищаем историю старого чата
            chatHistory.innerHTML = `
                <div class="message bot-message">
                    <div class="msg-avatar">ИИ</div>
                    <div class="msg-content">Здравствуйте! Я ваш медицинский ИИ-Консультант. Я проанализировал документы из вашей папки и готов ответить на вопросы. Чем могу помочь?</div>
                </div>
            `;

            showScreen('chat');
        } catch (err) {
            loginError.textContent = err.message || 'Ошибка подключения к серверу.';
        } finally {
            setLoginLoading(false);
        }
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('session_token');
        localStorage.removeItem('active_url_token');
        sessionToken = null;
        chatHistory.innerHTML = `
            <div class="message bot-message">
                <div class="msg-avatar">ИИ</div>
                <div class="msg-content">Здравствуйте! Я ваш медицинский ИИ-Консультант. Чем могу помочь?</div>
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

    // ==========================================
    // ЛОГИКА ШЕРИНГА КАРТЫ С ВРАЧОМ
    // ==========================================
    const shareRecordBtn = document.getElementById('share-record-btn');
    const shareModal = document.getElementById('share-modal');
    const closeShareModalBtn = document.getElementById('close-share-modal');
    const generateShareBtn = document.getElementById('generate-share-btn');
    const shareTtlSelect = document.getElementById('share-ttl-select');
    const shareResultBlock = document.getElementById('share-result-block');
    const shareUrlInput = document.getElementById('share-url-input');
    const copyShareBtn = document.getElementById('copy-share-btn');
    const copyStatus = document.getElementById('copy-status');
    const shareExpiresText = document.getElementById('share-expires-text');
    const shareLoader = document.getElementById('share-loader');
    const shareLimitWarning = document.getElementById('share-limit-warning');
    const activeSharesList = document.getElementById('active-shares-list');
    const activeSharesBadge = document.getElementById('active-shares-count-badge');

    async function loadActiveShares() {
        if (!sessionToken || !activeSharesList) return;
        try {
            const res = await fetch('/api/v1/patient/shares', {
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            });
            if (!res.ok) return;
            const data = await res.json();
            const shares = data.shares || [];
            const count = shares.length;

            if (activeSharesBadge) {
                activeSharesBadge.textContent = `${count} / 2`;
                if (count >= 2) {
                    activeSharesBadge.style.color = '#ef4444';
                    activeSharesBadge.style.background = 'rgba(239, 68, 68, 0.15)';
                } else {
                    activeSharesBadge.style.color = '#a78bfa';
                    activeSharesBadge.style.background = 'rgba(167, 139, 250, 0.15)';
                }
            }

            if (count >= 2) {
                if (shareLimitWarning) shareLimitWarning.classList.remove('hidden');
                if (generateShareBtn) generateShareBtn.disabled = true;
            } else {
                if (shareLimitWarning) shareLimitWarning.classList.add('hidden');
                if (generateShareBtn) generateShareBtn.disabled = false;
            }

            if (shares.length === 0) {
                activeSharesList.innerHTML = '<div style="font-size: 12px; color: #94a3b8; text-align: center; padding: 8px 0;">Нет активных ссылок</div>';
                return;
            }

            activeSharesList.innerHTML = '';
            shares.forEach(s => {
                const item = document.createElement('div');
                item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); font-size: 12px;';
                
                const expires = s.expires_at ? s.expires_at.substring(0, 16).replace('T', ' ') : '24ч';
                item.innerHTML = `
                    <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 65%;">
                        <div style="color: #f1f5f9; font-weight: 500;">Доступ #${s.id}</div>
                        <div style="color: #94a3b8; font-size: 11px;">⏱️ до ${expires}</div>
                    </div>
                    <button class="btn-revoke-share" data-id="${s.id}" style="background: rgba(239,68,68,0.2); border: 1px solid #ef4444; color: #fca5a5; padding: 4px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; transition: all 0.2s;">
                        Отозвать
                    </button>
                `;
                activeSharesList.appendChild(item);
            });

            // Навешиваем слушатели на кнопки отзыва
            activeSharesList.querySelectorAll('.btn-revoke-share').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const grantId = e.currentTarget.getAttribute('data-id');
                    if (!grantId) return;
                    e.currentTarget.disabled = true;
                    e.currentTarget.textContent = '...';
                    await revokeShareGrant(grantId);
                });
            });

        } catch (e) {
            console.error('Ошибка загрузки активных ссылок:', e);
        }
    }

    async function revokeShareGrant(grantId) {
        try {
            const res = await fetch(`/api/v1/patient/share/${grantId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${sessionToken}` }
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                alert(err.detail || 'Не удалось отозвать ссылку');
                return;
            }
            if (shareResultBlock) shareResultBlock.classList.add('hidden');
            await loadActiveShares();
        } catch (e) {
            alert('Ошибка сети при отзыве ссылки: ' + e.message);
        }
    }

    if (shareRecordBtn && shareModal) {
        shareRecordBtn.addEventListener('click', () => {
            shareModal.classList.remove('hidden');
            if (copyStatus) copyStatus.classList.add('hidden');
            loadActiveShares();
        });

        if (closeShareModalBtn) {
            closeShareModalBtn.addEventListener('click', () => {
                shareModal.classList.add('hidden');
            });
        }

        // Закрытие по клику на оверлей
        shareModal.addEventListener('click', (e) => {
            if (e.target === shareModal) {
                shareModal.classList.add('hidden');
            }
        });

        if (generateShareBtn) {
            generateShareBtn.addEventListener('click', async () => {
                const ttlHours = parseInt(shareTtlSelect ? shareTtlSelect.value : "24", 10);
                if (shareLoader) shareLoader.classList.remove('hidden');
                generateShareBtn.disabled = true;

                try {
                    const res = await fetch('/api/v1/patient/share', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${sessionToken}`
                        },
                        body: JSON.stringify({ expires_in_hours: ttlHours })
                    });

                    if (res.status === 429) {
                        const errData = await res.json().catch(() => ({}));
                        const errMsg = (errData.detail && errData.detail.message) || errData.detail || 'У вас уже 2 активные ссылки. Отзовите одну из них, чтобы создать новую.';
                        if (shareLimitWarning) {
                            shareLimitWarning.innerHTML = `⚠️ <strong>Ограничение:</strong> ${errMsg}`;
                            shareLimitWarning.classList.remove('hidden');
                        }
                        await loadActiveShares();
                        return;
                    }

                    if (!res.ok) {
                        const errData = await res.json().catch(() => ({}));
                        const msg = (errData.detail && typeof errData.detail === 'object' ? errData.detail.message : errData.detail) || 'Не удалось создать ссылку доступа';
                        throw new Error(msg);
                    }

                    const data = await res.json();
                    
                    // Формируем красивую веб-ссылку на портал
                    const hostUrl = window.location.origin;
                    const directUrl = `${hostUrl}/?share_token=${data.share_token}`;

                    if (shareUrlInput) shareUrlInput.value = directUrl;
                    if (shareExpiresText) shareExpiresText.textContent = data.expires_at || '24 часа';
                    if (shareResultBlock) shareResultBlock.classList.remove('hidden');
                    
                    await loadActiveShares();
                } catch (err) {
                    alert('Ошибка: ' + err.message);
                } finally {
                    if (shareLoader) shareLoader.classList.add('hidden');
                    generateShareBtn.disabled = false;
                }
            });
        }

        if (copyShareBtn && shareUrlInput) {
            copyShareBtn.addEventListener('click', async () => {
                const textToCopy = shareUrlInput.value;
                if (!textToCopy) return;

                try {
                    if (navigator.clipboard && window.isSecureContext) {
                        await navigator.clipboard.writeText(textToCopy);
                    } else {
                        shareUrlInput.select();
                        document.execCommand('copy');
                    }

                    if (copyStatus) {
                        copyStatus.classList.remove('hidden');
                        setTimeout(() => copyStatus.classList.add('hidden'), 3000);
                    }
                } catch (err) {
                    console.error('Ошибка копирования:', err);
                }
            });
        }
    }
});

