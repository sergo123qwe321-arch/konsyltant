/**
 * VoiceInput Module - Client-side Web Speech API voice transcription
 * Fully autonomous in-browser speech recognition (Chrome, Yandex Browser, Edge, Safari).
 */

function isSpeechRecognitionSupported() {
    return typeof window !== 'undefined' && (
        'SpeechRecognition' in window || 
        'webkitSpeechRecognition' in window || 
        'mozSpeechRecognition' in window || 
        'msSpeechRecognition' in window
    );
}

class VoiceInputController {
    constructor(options = {}) {
        this.inputElement = options.inputElement || document.getElementById('chat-input');
        this.buttonElement = options.buttonElement || document.getElementById('voice-input-btn');
        this.statusContainer = options.statusContainer || document.getElementById('voice-status-container');
        this.statusText = options.statusText || document.getElementById('voice-status-text');
        this.fallbackHint = options.fallbackHint || document.getElementById('voice-fallback-hint');
        this.lang = options.lang || 'ru-RU';
        this.silenceTimeoutMs = options.silenceTimeoutMs || 60000;
        
        this.recognition = null;
        this.isRecording = false;
        this.silenceTimer = null;
        this.baseInputValue = '';
        
        this.init();
    }

    init() {
        if (!isSpeechRecognitionSupported()) {
            if (this.buttonElement) {
                this.buttonElement.style.display = 'none';
            }
            if (this.fallbackHint) {
                this.fallbackHint.classList.remove('hidden');
                this.fallbackHint.style.display = 'block';
            }
            console.log('[VoiceInput] Web Speech API не поддерживается текущим браузером. Показана подсказка о совместимости.');
            return;
        }

        if (this.fallbackHint) {
            this.fallbackHint.classList.add('hidden');
            this.fallbackHint.style.display = 'none';
        }

        const SpeechRecognitionClass = window.SpeechRecognition || 
                                       window.webkitSpeechRecognition || 
                                       window.mozSpeechRecognition || 
                                       window.msSpeechRecognition;
        
        if (!SpeechRecognitionClass) return;

        this.recognition = new SpeechRecognitionClass();
        this.recognition.lang = this.lang;
        this.recognition.continuous = true;
        this.recognition.interimResults = true;

        this.bindEvents();
    }

    bindEvents() {
        if (this.buttonElement) {
            this.buttonElement.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleRecording();
            });
        }

        if (this.inputElement) {
            // Если родитель начинает печатать вручную во время активной записи, запись останавливается
            this.inputElement.addEventListener('keydown', (e) => {
                if (this.isRecording && e.key !== 'Enter' && e.key !== 'Shift' && e.key !== 'Control') {
                    console.log('[VoiceInput] Ручной ввод с клавиатуры. Автоматическая остановка записи.');
                    this.stopRecording();
                }
            });
        }

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.baseInputValue = this.inputElement ? this.inputElement.value.trim() : '';
            this.setButtonState('recording');
            this.resetSilenceTimer();
            if (this.inputElement) {
                this.inputElement.focus();
                this.inputElement.classList.add('recording-focus');
            }
            if (this.statusContainer) {
                this.statusContainer.classList.remove('hidden');
                this.statusContainer.style.display = 'flex';
            }
            if (this.statusText) {
                this.statusText.textContent = 'Слушаю... Говорите';
            }
            console.log('[VoiceInput] Запись активна. Слушаю речь...');
        };

        this.recognition.onresult = (event) => {
            this.resetSilenceTimer();
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (this.inputElement) {
                const prefix = this.baseInputValue ? this.baseInputValue + ' ' : '';
                const combined = (prefix + finalTranscript + (interimTranscript ? ' ' + interimTranscript : '')).trim();
                this.inputElement.value = combined;
                if (finalTranscript) {
                    this.baseInputValue = (prefix + finalTranscript).trim();
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error('[VoiceInput Client Error]', event.error, event.message || '');
            this.clearSilenceTimer();

            if (event.error === 'not-allowed') {
                const msg = 'Для голосового ввода разрешите доступ к микрофону в настройках браузера';
                this.setButtonState('error', msg);
                if (this.statusText) this.statusText.textContent = msg;
                this.isRecording = false;
            } else if (event.error === 'network') {
                const msg = 'Проверьте подключение к интернету';
                this.setButtonState('error', msg);
                if (this.statusText) this.statusText.textContent = msg;
                this.isRecording = false;
            } else if (event.error === 'no-speech') {
                console.log('[VoiceInput] Таймаут тишины (no-speech). Завершение записи.');
                this.stopRecording();
            } else if (event.error === 'aborted') {
                console.warn('[VoiceInput] Запись прервана внешним источником (aborted).');
                if (this.isRecording) {
                    try {
                        this.recognition.start();
                    } catch (e) {
                        this.stopRecording();
                    }
                }
            } else {
                this.setButtonState('error', 'Ошибка: ' + event.error);
                this.stopRecording();
            }
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            this.clearSilenceTimer();
            if (this.buttonElement && !this.buttonElement.classList.contains('error')) {
                this.setButtonState('inactive');
            }
            if (this.inputElement) {
                this.inputElement.classList.remove('recording-focus');
                this.inputElement.focus();
            }
            if (this.statusContainer && (!this.buttonElement || !this.buttonElement.classList.contains('error'))) {
                this.statusContainer.classList.add('hidden');
                this.statusContainer.style.display = 'none';
            }
            console.log('[VoiceInput] Сессия распознавания завершена.');
        };
    }

    toggleRecording() {
        if (!this.recognition) {
            this.init();
            if (!this.recognition) return;
        }

        // При повторном клике пользователя при ошибке сбрасываем ошибку и пытаемся запустить запись заново
        if (this.buttonElement && this.buttonElement.classList.contains('error')) {
            this.setButtonState('inactive');
            if (this.statusContainer) {
                this.statusContainer.classList.add('hidden');
                this.statusContainer.style.display = 'none';
            }
            if (this.statusText) {
                this.statusText.textContent = '';
            }
            this.isRecording = false;
            this.startRecording();
            return;
        }

        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        if (!this.recognition || this.isRecording) return;
        try {
            this.setButtonState('inactive');
            this.recognition.start();
        } catch (e) {
            console.warn('[VoiceInput] Ошибка запуска recognition.start():', e);
            if (e.name === 'InvalidStateError') {
                // Если сервис уже запущен, синхронизируем внутреннее состояние
                this.isRecording = true;
                this.setButtonState('recording');
            } else {
                this.setButtonState('error', 'Не удалось запустить микрофон');
                this.isRecording = false;
            }
        }
    }

    stopRecording() {
        this.clearSilenceTimer();
        if (!this.recognition) {
            this.isRecording = false;
            return;
        }
        try {
            this.recognition.stop();
        } catch (e) {
            console.warn('[VoiceInput] Ошибка остановки recognition.stop():', e);
        } finally {
            this.isRecording = false;
            if (this.inputElement) {
                this.inputElement.classList.remove('recording-focus');
            }
            if (this.buttonElement && !this.buttonElement.classList.contains('error')) {
                this.setButtonState('inactive');
            }
            if (this.statusContainer && (!this.buttonElement || !this.buttonElement.classList.contains('error'))) {
                this.statusContainer.classList.add('hidden');
                this.statusContainer.style.display = 'none';
            }
        }
    }

    resetSilenceTimer() {
        this.clearSilenceTimer();
        this.silenceTimer = setTimeout(() => {
            console.log('[VoiceInput] 60 секунд тишины истекли. Остановка записи.');
            this.stopRecording();
        }, this.silenceTimeoutMs);
    }

    clearSilenceTimer() {
        if (this.silenceTimer) {
            clearTimeout(this.silenceTimer);
            this.silenceTimer = null;
        }
    }

    setButtonState(state, errorMessage = '') {
        if (!this.buttonElement) return;

        this.buttonElement.classList.remove('recording', 'error', 'inactive');
        if (state === 'recording') {
            this.buttonElement.classList.add('recording');
            this.buttonElement.title = 'Идёт запись... Нажмите для остановки';
            this.buttonElement.setAttribute('aria-label', 'Остановить голосовой ввод');
        } else if (state === 'error') {
            this.buttonElement.classList.add('error');
            this.buttonElement.title = errorMessage || 'Ошибка микрофона';
            this.buttonElement.setAttribute('aria-label', errorMessage || 'Ошибка микрофона');
        } else {
            this.buttonElement.classList.add('inactive');
            this.buttonElement.title = 'Голосовой ввод (нажмите для записи)';
            this.buttonElement.setAttribute('aria-label', 'Начать голосовой ввод');
        }
    }
}

if (typeof window !== 'undefined') {
    window.isSpeechRecognitionSupported = isSpeechRecognitionSupported;
    window.VoiceInputController = VoiceInputController;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { isSpeechRecognitionSupported, VoiceInputController };
}
