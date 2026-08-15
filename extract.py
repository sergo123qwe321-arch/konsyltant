import os
from bs4 import BeautifulSoup

with open('index.html.лендинг', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 1. CSS
style_tag = soup.find('style')
if style_tag:
    os.makedirs('static/css', exist_ok=True)
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(style_tag.string.strip())
    new_link = soup.new_tag('link', rel='stylesheet', href='/static/css/style.css')
    style_tag.replace_with(new_link)

# 2. JS
script_tag = soup.find('script')
if script_tag and not script_tag.has_attr('src'):
    os.makedirs('static/js', exist_ok=True)
    with open('temp_script.js', 'w', encoding='utf-8') as f:
        f.write(script_tag.string.strip())
    
    # Replace with two scripts
    script1 = soup.new_tag('script', src='/static/js/bubbles.js')
    script2 = soup.new_tag('script', src='/static/js/app.js')
    script_tag.replace_with(script1)
    script1.insert_after(script2)

os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))
