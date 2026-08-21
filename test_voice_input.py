import os
import unittest
import re

class TestVoiceInputIntegration(unittest.TestCase):
    """
    Тестовый набор для клиентской подсистемы голосового ввода Web Speech API (Phase 4).
    """

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.static_index_path = os.path.join(self.base_dir, 'static', 'index.html')
        self.landing_template_path = os.path.join(self.base_dir, 'templates', 'index.html')
        self.voice_js_path = os.path.join(self.base_dir, 'static', 'js', 'voiceInput.js')
        self.patient_app_js_path = os.path.join(self.base_dir, 'static', 'app.js')
        self.landing_app_js_path = os.path.join(self.base_dir, 'static', 'js', 'app.js')
        self.style_css_path = os.path.join(self.base_dir, 'static', 'style.css')

    def test_voice_button_present_in_patient_chat_dom(self):
        """1. Тест наличия кнопки микрофона и статус-контейнеров в DOM приватного чата пациента (/app/)."""
        self.assertTrue(os.path.exists(self.static_index_path), 'Файл static/index.html должен существовать')
        with open(self.static_index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('id="voice-input-btn"', html, 'Кнопка микрофона #voice-input-btn должна присутствовать в DOM')
        self.assertIn('class="btn-voice', html, 'Кнопка микрофона должна иметь базовый CSS класс btn-voice')
        self.assertIn('id="voice-status-container"', html, 'Контейнер статуса #voice-status-container должен присутствовать')
        self.assertIn('id="voice-status-text"', html, 'Текстовый индикатор #voice-status-text должен присутствовать')
        self.assertIn('id="voice-fallback-hint"', html, 'Фоллбэк-подсказка #voice-fallback-hint должна присутствовать')
        self.assertIn('/static/js/voiceInput.js', html, 'Скрипт voiceInput.js должен подключаться в static/index.html')

    def test_voice_fallback_hint_message(self):
        """2. Тест корректности формулировки фоллбэк-подсказки для неподдерживаемых браузеров."""
        with open(self.static_index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        self.assertIn('Голосовой ввод доступен в Chrome, Яндекс.Браузере, Edge и Safari', html)

    def test_rbac_voice_button_not_on_anonymous_landing(self):
        """3. Тест RBAC: кнопка микрофона чата пациента изолирована в /app/ и не рендерится на публичном лендинге."""
        self.assertTrue(os.path.exists(self.landing_template_path), 'Шаблон templates/index.html должен существовать')
        with open(self.landing_template_path, 'r', encoding='utf-8') as f:
            landing_html = f.read()

        # На публичном лендинге нет кнопки голосового ввода приватного чата
        self.assertNotIn('id="voice-input-btn"', landing_html, 'Кнопка #voice-input-btn не должна присутствовать на публичном лендинге')

    def test_voice_input_js_logic_and_parameters(self):
        """4. Тест логики и параметров SpeechRecognition в voiceInput.js."""
        self.assertTrue(os.path.exists(self.voice_js_path), 'Файл static/js/voiceInput.js должен существовать')
        with open(self.voice_js_path, 'r', encoding='utf-8') as f:
            js = f.read()

        # Проверка функции детекции браузера
        self.assertIn('function isSpeechRecognitionSupported()', js)
        self.assertIn('webkitSpeechRecognition', js)
        
        # Проверка параметров
        self.assertIn("lang = options.lang || 'ru-RU'", js, 'Язык по умолчанию должен быть ru-RU')
        self.assertIn('continuous = true', js, 'Запись должна быть непрерывной (continuous=true)')
        self.assertIn('interimResults = true', js, 'Промежуточные результаты должны выводиться в реальном времени')
        self.assertIn('60000', js, 'Таймаут тишины должен составлять 60 секунд (60000 мс)')

        # Проверка обработчиков ошибок
        self.assertIn('not-allowed', js, 'Обработка отказа в доступе к микрофону')
        self.assertIn('Для голосового ввода разрешите доступ к микрофону в настройках браузера', js)
        self.assertIn('network', js, 'Обработка ошибки сети')
        self.assertIn('Проверьте подключение к интернету', js)
        self.assertIn('no-speech', js, 'Обработка таймаута тишины')
        self.assertIn('aborted', js, 'Обработка прерывания записи')

        # Проверка автоостановки при ручном вводе
        self.assertIn('keydown', js, 'Остановка записи при наборе текста с клавиатуры')
        self.assertIn('recording-focus', js, 'Пульсирующий фокус поля ввода')

    def test_patient_app_js_integration(self):
        """5. Тест инициализации VoiceInputController в static/app.js при открытии чата."""
        with open(self.patient_app_js_path, 'r', encoding='utf-8') as f:
            app_js = f.read()

        self.assertIn('initPatientVoiceInput', app_js)
        self.assertIn('VoiceInputController', app_js)

    def test_voice_css_styles_and_animations(self):
        """6. Тест CSS стилей кнопки, пульсации, ошибок и фокуса в static/style.css."""
        with open(self.style_css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        self.assertIn('.btn-voice', css)
        self.assertIn('.btn-voice.recording', css)
        self.assertIn('pulseMic', css)
        self.assertIn('.btn-voice.error', css)
        self.assertIn('.recording-focus', css)
        self.assertIn('.voice-status-bar', css)
        self.assertIn('.voice-pulse-dot', css)

if __name__ == '__main__':
    unittest.main()
