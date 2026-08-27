import unittest
import os
import re
from fastapi.testclient import TestClient
from main import app

class TestAlikAnimationAndLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        with open("templates/index.html", "r", encoding="utf-8") as f:
            cls.html = f.read()
        with open("static/css/style.css", "r", encoding="utf-8") as f:
            cls.css = f.read()
        with open("static/js/app.js", "r", encoding="utf-8") as f:
            cls.js = f.read()

    def test_01_no_static_mascot_in_hero(self):
        """1. В секции Hero (#hero) полностью отсутствует статичный маскот и контейнеры hero-alik-*"""
        pos_hero = self.html.find('id="hero"')
        pos_blog = self.html.find('id="blog"')
        self.assertNotEqual(pos_hero, -1, "Hero секция найдена")
        self.assertNotEqual(pos_blog, -1, "Секция Библиотека найдена")
        hero_chunk = self.html[pos_hero:pos_blog]

        self.assertNotIn("hero-alik-wrapper", hero_chunk, "В Hero не должно быть hero-alik-wrapper")
        self.assertNotIn("hero-alik-img", hero_chunk, "В Hero не должно быть hero-alik-img")
        self.assertNotIn("hero-alik-picture", hero_chunk, "В Hero не должно быть hero-alik-picture")
        self.assertNotIn("hero-visual", hero_chunk, "В Hero не должно быть hero-visual")
        self.assertIn('data-alik-comment="Привет! Я Алик — твой проводник по Маленькой Стране! 🎸"', hero_chunk)

    def test_02_floating_widget_markup(self):
        """2. Виджет-компаньон (#floating-alik-widget) присутствует в разметке со всеми элементами"""
        self.assertIn('id="floating-alik-widget"', self.html)
        self.assertIn('id="alik-speech-bubble"', self.html)
        self.assertIn('id="alik-bubble-text"', self.html)
        self.assertIn('id="alik-bubble-close"', self.html)
        self.assertIn('id="alik-avatar-container"', self.html)
        self.assertIn('id="alik-avatar-inner"', self.html)
        self.assertIn('id="floating-alik-img"', self.html)
        self.assertIn('id="alik-widget-toggle"', self.html)
        self.assertIn('id="alik-toggle-icon"', self.html)

    def test_03_sound_showcase_docking_slot_markup(self):
        """3. В секции «Герои звуков» (#characters) присутствует круговой плейсхолдер докинга"""
        pos_char = self.html.find('id="characters"')
        pos_about = self.html.find('id="about"')
        self.assertNotEqual(pos_char, -1, "Секция Герои звуков найдена")
        self.assertNotEqual(pos_about, -1, "Секция О центре найдена")
        char_chunk = self.html[pos_char:pos_about]

        self.assertIn('id="alik-dock-placeholder"', char_chunk)
        self.assertIn('class="alik-dock-slot"', char_chunk)
        self.assertIn('id="alik-dock-inner"', char_chunk)
        self.assertIn('id="alik-dock-img"', char_chunk)
        self.assertIn('class="alik-dock-ring"', char_chunk)
        self.assertIn('class="alik-dock-tag"', char_chunk)

    def test_04_css_styles_for_floating_and_docking(self):
        """4. Проверка стилей CSS: активное состояние виджета, слот докинга и отсутствие устаревших hero-alik стилей"""
        self.assertNotIn(".hero-alik-wrapper", self.css)
        self.assertNotIn(".hero-alik-img", self.css)

        self.assertIn(".floating-alik-widget", self.css)
        self.assertIn(".floating-alik-widget.floating-active", self.css)
        self.assertIn(".floating-alik-widget.docked-hidden", self.css)
        self.assertIn(".alik-speech-bubble", self.css)

        self.assertIn(".alik-dock-slot", self.css)
        self.assertIn(".alik-dock-slot.docked", self.css)
        self.assertIn(".alik-dock-img", self.css)
        self.assertIn(".alik-dock-ring", self.css)
        self.assertIn(".alik-dock-tag", self.css)

    def test_05_js_init_floating_alik_logic(self):
        """5. Проверка логики JS: dockToSoundShowcase, undockToFloating, привязка к #characters"""
        self.assertIn("function initFloatingAlik()", self.js)
        self.assertIn("dockToSoundShowcase", self.js)
        self.assertIn("undockToFloating", self.js)
        self.assertIn("alik-dock-placeholder", self.js)
        self.assertIn("charactersSection", self.js)

        self.assertNotIn("heroAlikWrapper", self.js)
        self.assertNotIn("heroAlikImg", self.js)
        self.assertNotIn("transitionToHero", self.js)

    def test_06_data_alik_comments_on_all_sections(self):
        """6. Проверка атрибутов data-alik-comment во всех ключевых секциях лендинга"""
        expected_sections = [
            'id="posts"',
            'id="hero"',
            'id="blog"',
            'id="characters"',
            'id="about"',
            'id="services"',
            'id="doctors"',
            'id="events"',
            'id="community-chat"',
            'id="special-care-section"',
            'id="contacts"',
            '<footer'
        ]
        for sec in expected_sections:
            self.assertIn(sec, self.html, f"Секция {sec} присутствует в HTML")

        comments_count = len(re.findall(r'data-alik-comment="[^"]+"', self.html))
        self.assertGreaterEqual(comments_count, 10, f"Найдено {comments_count} реплик data-alik-comment")

    def test_07_characters_sound_selector_isolation(self):
        """7. Проверка изоляции переключателей звуков (А, О, У, И, Ы, Э) и аудиосэмплов"""
        sound_chars = ['data-char="a"', 'data-char="o"', 'data-char="u"', 'data-char="i"', 'data-char="y"', 'data-char="e"']
        for char in sound_chars:
            self.assertIn(char, self.html, f"Переключатель звука {char} присутствует в HTML")

        self.assertIn("playCharSound", self.js)
        self.assertIn("sound_${charId}.mp3", self.js)


if __name__ == "__main__":
    unittest.main()
