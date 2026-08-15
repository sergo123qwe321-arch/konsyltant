import os
import re

with open('temp_script.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# We know the bubble section starts at /* ==========================================================================
# 2. ИНТЕРАКТИВНАЯ HERO-АНИМАЦИЯ (Dream Bubbles на Canvas)
bubble_start = js_content.find('2. ИНТЕРАКТИВНАЯ HERO-АНИМАЦИЯ')
bubble_start = js_content.rfind('/*', 0, bubble_start)

bubble_end = js_content.find('3. API INTEGRATION & FALLBACKS')
bubble_end = js_content.rfind('/*', 0, bubble_end)

bubbles_code = js_content[bubble_start:bubble_end]
app_code = js_content[:bubble_start] + '\n' + js_content[bubble_end:]

# Add hover audio logic to app.js
audio_logic = '''
                // Audio hover logic
                let audio = new Audio(/static/audio/sound_\.mp3);
                audio.volume = 0.5;
                audio.play().catch(e => console.log('Audio autoplay prevented'));
'''
app_code = app_code.replace('const charId = thumb.getAttribute(\'data-char\');', 'const charId = thumb.getAttribute(\'data-char\');' + audio_logic)


# We already have an existing static/app.js which contains the old chat logic!
# We must preserve it or replace it? The prompt implies the new app.js handles the landing page, and maybe the chat logic is inside the modal or separate.
# Wait, the prompt says "static/js/app.js: Вынести логику работы с API, переключение персонажей Pixar".
# The old app.js was in "static/app.js", the new one is "static/js/app.js". 
# So they don't overwrite each other if we use different paths, but it's cleaner to keep them separate.
os.makedirs('static/js', exist_ok=True)
with open('static/js/bubbles.js', 'w', encoding='utf-8') as f:
    f.write(bubbles_code.strip())

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_code.strip())
