# Текущий план задач (Harness Backlog)

- [ ] **Task 1: Стабилизация позиционирования и FLIP-докинга маскота «Алик»**
  - [ ] Проанализировать актуальный порядок секций в `templates/index.html` и логику `initFloatingAlik`, `dockToSoundShowcase`, `undockToFloating` в `static/js/app.js`.
  - [ ] Устранить выпадение маскота за пределы рамки/окна при скролле и скорректировать триггеры с учетом нового положения блоков.
  - [ ] Запустить целевые тесты: `python -m unittest test_alik_animation.py`.
  - [ ] Прогнать общий сьют: `python -m unittest discover -s . -p "test_*.py"`.
  - [ ] Проверить отсутствие запрещенных логов: `python scripts/lint_no_txt_logs.py`.
  - [ ] Зафиксировать отчет в `process.md` и сделать атомарный Git-коммит.
