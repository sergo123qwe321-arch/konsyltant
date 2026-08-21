/* ==========================================================================
           1. ДЕМОНСТРАЦИОННАЯ СИСТЕМА ДАННЫХ (Фоллбэк при отсутствии API бэкенда)
           ========================================================================== */
        const MOCK_DATA = {
            services: [
                {
                    id: 1,
                    title: "Игровая Нейропсихология",
                    description: "Комплексное тестирование высших психических функций и бережная сенсомоторная интеграция в забавных игровых формах.",
                    category: "Диагностика",
                    icon: "🧠"
                },
                {
                    id: 2,
                    title: "Волшебная Логопедия",
                    description: "Занятия по коррекции звукопроизношения, запуску и развитию речи с использованием интерактивных симуляторов.",
                    category: "Развитие речи",
                    icon: "🗣️"
                },
                {
                    id: 3,
                    title: "Сказкотерапия и Эмоции",
                    description: "Мягкое прорабатывание детских страхов, капризов и тревожности через увлекательные развивающие сказки.",
                    category: "Эмоции и поведение",
                    icon: "🧸"
                }
            ],
            doctors: [
                {
                    id: 1,
                    full_name: "Иванова Анна Сергеевна",
                    specialization: "Детский нейропсихолог",
                    experience_years: 10,
                    avatar: "👩‍⚕️"
                },
                {
                    id: 2,
                    full_name: "Петров Дмитрий Игоревич",
                    specialization: "Логопед-игротерапевт",
                    experience_years: 8,
                    avatar: "👨‍⚕️"
                },
                {
                    id: 3,
                    full_name: "Смирнова Елена Викторовна",
                    specialization: "Детский психотерапевт",
                    experience_years: 12,
                    avatar: "👩‍⚕️"
                }
            ],
            posts: [
                {
                    id: 1,
                    title: "Как мягко подтолкнуть речь: 5 речевых игр от нейропсихолога без принуждения и слез",
                    summary: "Простые и бережные практики для домашних занятий: дыхательные упражнения со свечками, мыльными пузырями и ритмические игры на звукоподражание («Би-би», «Тик-так», «Кап-кап»).",
                    tags: "Развитие речи,Игры",
                    created_at: "2026-08-14",
                    content: `Речевое развитие ребенка — это не механическое повторение слогов за взрослым, а сложный нейродинамический процесс, неразрывно связанный с крупной моторикой, дыханием и эмоциональным контактом.

5 проверенных упражнений от ведущих нейропсихологов центра:

1. «Задуй свечу / Буря в стакане»
Формирование правильного речевого выдоха — основа четкой дикции. Дуем на бумажные кораблики в ванне, через трубочку в воду или на свечу с разного расстояния.

2. «Эхо в горах (Звукоподражание)»
Используем эмоциональные короткие звуки в контексте игры: машинка едет («Би-би!»), часики тикают («Тик-так»), дождик капает («Кап-кап»). Важно смотреть ребенку в глаза на уровне его роста.

3. «Ритмический оркестр»
Стучим деревянными ложками или ладошками по коленям под простые стишки. Ритм напрямую стимулирует речевые центры Брока и Вернике.

4. «Полоса препятствий с озвучкой»
Перешагиваем через подушки со звуками «Топ-топ», прыгаем «Прыг-скок». Связка движения и звука ускоряет запуск речи.

5. «Угадай, кто в домике»
Прячем игрушечных животных под платочек и просим угадать по звукам: «Му-у», «Гав-гав», «Ква-ква».`
                },
                {
                    id: 2,
                    title: "Энергия в мирное русло: нейроигры для сброса гиперактивности и развития самоконтроля",
                    summary: "Игры «Замри-отомри», «Канатоходец» и «Ритмические хлопки», которые помогают ребенку научиться торможению нервной системы, осознанию тела и снятию эмоционального перегруза.",
                    tags: "Эмоции и поведение,Игры",
                    created_at: "2026-08-12",
                    content: `Гиперактивность и импульсивность — это не «вредность» ребенка, а особенность созревания лобных долей головного мозга, отвечающих за функцию самоконтроля и торможения.

Нейроигры для тренировки функции торможения:

1. «Замри — Отомри (Стоп-игра)»
Под веселую музыку ребенок активно танцует или бегает, но по хлопку или слову «Замри!» мгновенно застывает в любой позе. Это напрямую тренирует тормозные механизмы коры.

2. «Канатоходец»
Наклеиваем на полу малярный скотч (или выкладываем веревочку). Задача — пройти точно по линии, удерживая равновесие и неся в руках стаканчик с водой или мячик.

3. «Ритмические хлопки и шифры»
Один хлопок — ребенок топает, два хлопка — прыгает, три — садится на корточки. Развивает произвольное внимание и слуховой контроль.

4. «Тяжелое одеяло и объятия-кокон»
Глубокое проприоцептивное давление перед сном помогает нервной системе переключиться из режима возбуждения в режим восстановления.`
                },
                {
                    id: 3,
                    title: "Быстро устает и отвлекается в школе? Понимаем нейродинамические особенности ребенка и помогаем мозгу без крика",
                    summary: "Кинезиологическая гимнастика «Кулак-ребро-ладонь», нейропеременки и режим сенсорной разгрузки для поддержки первого энергетического блока мозга.",
                    tags: "Нейродинамика,Игры",
                    created_at: "2026-08-10",
                    content: `Когда ребенок через 15 минут выполнения уроков начинает крутиться, ложиться на стол или допускать глупые ошибки — чаще всего речь идет о дефиците нейродинамики (первый энергетический блок мозга по А.Р. Лурия).

Как помочь мозгу включиться:

1. Кинезиологическое упражнение «Кулак — Ребро — Ладонь»
Ребенок последовательно меняет положение ладони на столе: сжатый кулак, ладонь ребром, раскрытая ладонь. Повторяем сначала ведущей рукой, затем другой, затем двумя руками одновременно.

2. Двуручное зеркальное рисование
Рисуем в воздухе или на листе бумаги симметричные фигуры (сердечки, круги, домики) обеими руками одновременно. Это активизирует межполушарные связи (мозолистое тело).

3. Нейропеременки каждые 20 минут
3-минутная физическая пауза: потягивания, перекрестные шаги (локоть к противоположному колену), стакан чистой воды.

4. Правильное сенсорное окружение
Уберите визуальный шум с рабочего стола: оставьте только один учебник и одну тетрадь, чтобы не перегружать поле внимания.`
                }
            ],
            events: [
                {
                    id: 1,
                    title: "Мастер-класс: Игры, развивающие мозг",
                    description: "Интерактивная встреча с нейропсихологом для увлеченных родителей.",
                    event_date: "2026-08-20 18:00",
                    location: "Игровая гостиная"
                },
                {
                    id: 2,
                    title: "Встреча Клуба: Пойми меня без слов",
                    description: "Разбор детской тревожности и кризисов возраста.",
                    event_date: "2026-08-25 15:30",
                    location: "Уютный зал"
                }
            ]
        };

        /* База данных персонажей Pixar */
        const CHARACTERS = {
            a: {
                name: "Звук «А» — Гитарист Алик",
                desc: "Весёлый гитарист, который помогает ребятам открыто выражать свои эмоции, развивает общую моторику, смелость и координацию движений.",
                img: "/static/images/char_a.jpg",
                glow: "radial-gradient(circle, rgba(239, 68, 68, 0.35) 0%, rgba(124, 58, 237, 0.05) 60%, transparent 100%)"
            },
            o: {
                name: "Звук «О» — Скрипачка Оля",
                desc: "Нежная скрипачка, которая мягко успокаивает нервную систему ребёнка, снимает мышечные зажимы, улучшает сон и развивает богатое творческое воображение.",
                img: "/static/images/char_o.jpg",
                glow: "radial-gradient(circle, rgba(251, 191, 36, 0.35) 0%, rgba(124, 58, 237, 0.05) 60%, transparent 100%)"
            },
            u: {
                name: "Звук «У» — Саксофонистка Уля",
                desc: "Жизнерадостная саксофонистка, которая учит речевому дыханию, помогает запустить речь, развивает артикуляционный аппарат и дикцию.",
                img: "/static/images/char_u.jpg",
                glow: "radial-gradient(circle, rgba(16, 185, 129, 0.35) 0%, rgba(6, 182, 212, 0.05) 60%, transparent 100%)"
            },
            i: {
                name: "Звук «И» — Флейтист Игорь",
                desc: "Внимательный флейтист. Тренирует тонкий фонематический слух, концентрацию внимания, слуховую память и аккуратность.",
                img: "/static/images/char_i.jpg",
                glow: "radial-gradient(circle, rgba(59, 130, 246, 0.35) 0%, rgba(6, 182, 212, 0.05) 60%, transparent 100%)"
            },
            y: {
                name: "Звук «Ы» — Кларнетист Ырыс",
                desc: "Мудрый кларнетист, развивающий логику, усидчивость, понимание схем, пространственное ориентирование и навыки решения головоломок.",
                img: "/static/images/char_y.jpg",
                glow: "radial-gradient(circle, rgba(139, 92, 246, 0.35) 0%, rgba(124, 58, 237, 0.05) 60%, transparent 100%)"
            },
            e: {
                name: "Звук «Э» — Тромбонист Эрик",
                desc: "Общительный тромбонист, обучающий мелкой моторике, социальным адаптивным навыкам, помогающий легко заводить друзей и привыкать к садику.",
                img: "/static/images/char_e.jpg",
                glow: "radial-gradient(circle, rgba(249, 115, 22, 0.35) 0%, rgba(124, 58, 237, 0.05) 60%, transparent 100%)"
            }
        };

        const BASE_API_URL = "/api/v1/public";
        let cachedPosts = [];

        
/* ==========================================================================
           3. API INTEGRATION & FALLBACKS
           ========================================================================== */
        let activeDemoMode = false;

        function showDemoBadge() {
            if (!activeDemoMode) {
                activeDemoMode = true;
                const badge = document.getElementById('app-demo-badge');
                if (badge) {
                    badge.innerHTML = "✨ Демонстрационный режим (Offline-ready)";
                    badge.style.background = "rgba(6, 182, 212, 0.25)";
                    badge.style.borderColor = "var(--accent-turquoise)";
                }
            }
        }

        async function loadData(endpoint) {
            try {
                const res = await fetch(`${BASE_API_URL}${endpoint}`);
                if (!res.ok) throw new Error('API Error');
                return await res.json();
            } catch (err) {
                console.warn(`[API] Ошибка при загрузке ${endpoint}, переключаемся на локальные демо-данные.`);
                showDemoBadge();
                const key = endpoint.replace('/', '').split('?')[0];
                return MOCK_DATA[key] || [];
            }
        }

        async function renderServices() {
            const container = document.getElementById('services-container');
            const data = await loadData('/services');
            container.innerHTML = '';
            
            data.forEach(srv => {
                let icon = '🧸';
                if (srv.icon_name === 'stethoscope') icon = '🩺';
                if (srv.icon_name === 'brain') icon = '🧠';
                if (srv.icon_name === 'heart') icon = '💖';
                if (srv.icon_name === 'smile') icon = '🗣️';

                container.innerHTML += `
                    <div class="card-glass service-card">
                        <div class="service-icon-wrapper">${icon}</div>
                        <h3>${srv.title}</h3>
                        <p>${srv.description}</p>
                        <a href="#contacts" class="service-link">Записаться к волшебнику →</a>
                    </div>
                `;
            });
        }

        async function renderDoctors() {
            const container = document.getElementById('doctors-container');
            const data = await loadData('/doctors');
            container.innerHTML = '';
            
            data.forEach(doc => {
                container.innerHTML += `
                    <div class="card-glass doctor-card">
                        <div class="doctor-avatar">
                            ${doc.avatar_url ? `<img src="${doc.avatar_url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">` : (doc.avatar || '👩‍⚕️')}
                        </div>
                        <h3>${doc.full_name}</h3>
                        <div class="doctor-spec">${doc.specialization}</div>
                        <div class="doctor-exp">Опыт бережной работы: ${doc.experience_years} лет</div>
                    </div>
                `;
            });
        }

        async function renderLatestPosts() {
            const container = document.getElementById('latest-posts-container');
            if (!container) return;
            const data = await loadData('/posts');
            cachedPosts = data;
            container.innerHTML = '';

            if (!data || data.length === 0) {
                container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">🦄 Новых публикаций пока нет.</div>`;
                return;
            }

            // Рендерим свежие статьи (до 6 постов)
            data.slice(0, 6).forEach(post => {
                let tagsList = [];
                if (Array.isArray(post.tags)) {
                    tagsList = post.tags;
                } else if (typeof post.tags === 'string') {
                    tagsList = post.tags.split(',').map(t => t.trim().replace(/[\[\]"]/g, ''));
                }
                if (tagsList.length === 0) tagsList = ['Экспертное'];

                const tagsHTML = tagsList.map(t => `<span class="blog-tag">${t}</span>`).join('');
                const hasCover = Boolean(post.cover_image_url);
                const hasVideo = Boolean(post.video_url);

                const coverHTML = hasCover
                    ? `<div style="height: 160px; border-radius: 12px 12px 0 0; background: url('${post.cover_image_url}') center/cover no-repeat; margin: -20px -20px 14px -20px; position: relative;">
                         ${hasVideo ? '<span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.75); color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight:600;">🎬 Видео</span>' : ''}
                       </div>`
                    : (hasVideo ? `<div style="margin-bottom: 8px;"><span style="background: rgba(239,68,68,0.2); color: #F87171; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">🎬 С видеоматериалом</span></div>` : '');

                container.innerHTML += `
                    <div class="card-glass blog-card" style="display: flex; flex-direction: column;">
                        ${coverHTML}
                        <div class="blog-tags">${tagsHTML}</div>
                        <div class="blog-date">📅 ${post.created_at ? post.created_at.split(' ')[0] : 'Недавно'}</div>
                        <h3 style="margin-bottom: 10px; font-size: 1.15rem; line-height: 1.4;">${post.title}</h3>
                        <p style="font-size: 0.9rem; line-height: 1.6; color: var(--text-gray); margin-bottom: 16px; display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">${post.summary}</p>
                        <div class="blog-card-footer" style="margin-top:auto;">
                            <button class="read-more" onclick="openArticleReader(${post.id})">Читать статью ✨</button>
                        </div>
                    </div>
                `;
            });
        }

        async function renderBlog(tag = null) {
            const endpoint = tag ? `/posts?tag=${encodeURIComponent(tag)}` : '/posts';
            const data = await loadData(endpoint);
            cachedPosts = data;
            const container = document.getElementById('blog-container');
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">🦄 Статей в этой категории пока нет.</div>`;
                return;
            }

            data.forEach(post => {
                let tagsList = [];
                if (Array.isArray(post.tags)) {
                    tagsList = post.tags;
                } else if (typeof post.tags === 'string') {
                    tagsList = post.tags.split(',').map(t => t.trim().replace(/[\[\]"]/g, ''));
                }
                if (tagsList.length === 0) tagsList = ['Полезное'];

                const tagsHTML = tagsList.map(t => `<span class="blog-tag">${t}</span>`).join('');
                const hasCover = Boolean(post.cover_image_url);
                const hasVideo = Boolean(post.video_url);

                const coverHTML = hasCover
                    ? `<div style="height: 160px; border-radius: 12px 12px 0 0; background: url('${post.cover_image_url}') center/cover no-repeat; margin: -20px -20px 14px -20px; position: relative;">
                         ${hasVideo ? '<span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.75); color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight:600;">🎬 Видео</span>' : ''}
                       </div>`
                    : (hasVideo ? `<div style="margin-bottom: 8px;"><span style="background: rgba(239,68,68,0.2); color: #F87171; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">🎬 С видеоматериалом</span></div>` : '');

                container.innerHTML += `
                    <div class="card-glass blog-card" style="display: flex; flex-direction: column;">
                        ${coverHTML}
                        <div class="blog-tags">${tagsHTML}</div>
                        <div class="blog-date">📅 ${post.created_at ? post.created_at.split(' ')[0] : 'Недавно'}</div>
                        <h3 style="margin-bottom: 10px; font-size: 1.15rem; line-height: 1.4;">${post.title}</h3>
                        <p style="font-size: 0.9rem; line-height: 1.6; color: var(--text-gray); margin-bottom: 16px;">${post.summary}</p>
                        <div class="blog-card-footer" style="margin-top:auto;">
                            <button class="read-more" onclick="openArticleReader(${post.id})">Читать далее ✨</button>
                        </div>
                    </div>
                `;
            });
        }

        async function openArticleReader(postId) {
            let post = (cachedPosts || []).find(p => p.id === postId);
            if (!post || !post.content) {
                try {
                    const res = await fetch(`/api/v1/public/posts/${postId}`);
                    if (res.ok) post = await res.json();
                } catch(e) {}
            }
            if (!post) {
                post = MOCK_DATA.posts.find(p => p.id === postId);
            }
            if (!post) {
                alert('Статья временно недоступна.');
                return;
            }

            document.getElementById('article-modal-title').textContent = post.title;
            document.getElementById('article-modal-date').textContent = `📅 Дата публикации: ${post.created_at ? post.created_at.split(' ')[0] : 'Недавно'}`;
            
            let tagsList = [];
            if (Array.isArray(post.tags)) tagsList = post.tags;
            else if (typeof post.tags === 'string') tagsList = post.tags.split(',').map(t => t.trim().replace(/[\[\]"]/g, ''));
            
            document.getElementById('article-modal-tags').innerHTML = tagsList.map(t => `<span class="blog-tag" style="margin-right: 6px;">${t}</span>`).join('');
            
            const mediaContainer = document.getElementById('article-modal-media');
            if (mediaContainer) {
                let mediaHTML = '';
                if (post.video_url) {
                    if (post.video_url.endsWith('.mp4') || post.video_url.endsWith('.webm')) {
                        mediaHTML += `<video controls style="width: 100%; max-height: 320px; border-radius: 10px; background: #000;" src="${post.video_url}"></video>`;
                    } else {
                        mediaHTML += `
                            <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 12px; display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px;">
                                <span style="font-size: 0.9rem; color: #fff;">🎬 Видеоматериал к статье</span>
                                <a href="${post.video_url}" target="_blank" class="btn btn-purple" style="padding: 6px 12px; font-size: 0.8rem; text-decoration: none;">Смотреть видео ↗️</a>
                            </div>
                        `;
                    }
                } else if (post.cover_image_url) {
                    mediaHTML += `<img src="${post.cover_image_url}" style="width: 100%; max-height: 280px; object-fit: cover; border-radius: 10px;" alt="Обложка"/>`;
                }
                if (mediaHTML) {
                    mediaContainer.innerHTML = mediaHTML;
                    mediaContainer.style.display = 'block';
                } else {
                    mediaContainer.innerHTML = '';
                    mediaContainer.style.display = 'none';
                }
            }

            document.getElementById('article-modal-body').textContent = post.content || post.summary;
            openModal('article-modal');
        }

        async function renderEvents() {
            const container = document.getElementById('events-container');
            const data = await loadData('/events');
            container.innerHTML = '';
            
            data.forEach(evt => {
                let day = '20', month = 'Авг';
                try {
                    const dateParts = evt.event_date.split(' ')[0].split('-');
                    day = dateParts[2] || '20';
                    const months = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];
                    month = months[parseInt(dateParts[1]) - 1] || 'Авг';
                } catch(e){}

                container.innerHTML += `
                    <div class="event-item">
                        <div class="event-date-box">
                            <span>${day}</span>
                            <small>${month}</small>
                        </div>
                        <div class="event-item-info">
                            <h4>${evt.title}</h4>
                            <div class="event-meta">
                                <span>🕒 ${evt.event_date.split(' ')[1] || '18:00'}</span>
                                <span>📍 ${evt.location}</span>
                            </div>
                        </div>
                        <button class="btn btn-outline" style="padding:8px 14px;font-size:0.8rem;" onclick="document.getElementById('user-msg').value='Запись на событие: ${evt.title}'; window.location.hash='#contacts';">Записаться 🎟️</button>
                    </div>
                `;
            });
        }


        /* ==========================================================================
           4. ОБРАБОТКА ЗАЯВОК С ЛЕНДИНГА
           ========================================================================== */
        async function handleLeadSubmit(e) {
            e.preventDefault();
            const submitBtn = document.getElementById('lead-submit-btn');
            const statusBox = document.getElementById('lead-form-status');
            const name = document.getElementById('user-name').value.trim();
            const phone = document.getElementById('user-phone').value.trim();
            const service = document.getElementById('select-service').value;
            const msg = document.getElementById('user-msg').value.trim();

            submitBtn.disabled = true;
            submitBtn.textContent = 'Отправка... ⏳';

            try {
                const res = await fetch('/api/v1/public/leads', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        phone: phone,
                        child_age: service,
                        message: msg
                    })
                });

                if (res.ok) {
                    statusBox.style.display = 'block';
                    statusBox.style.background = 'rgba(16, 185, 129, 0.2)';
                    statusBox.style.border = '1px solid #10B981';
                    statusBox.style.color = '#A7F3D0';
                    statusBox.innerHTML = `🎉 Спасибо, <strong>${name}</strong>! Заявка успешно отправлена. Наш заботливый администратор свяжется с вами по номеру <strong>${phone}</strong> в течение 15 минут! ✨`;
                    document.getElementById('contact-form').reset();
                } else {
                    throw new Error('Ошибка сервера');
                }
            } catch (err) {
                statusBox.style.display = 'block';
                statusBox.style.background = 'rgba(239, 68, 68, 0.2)';
                statusBox.style.border = '1px solid #EF4444';
                statusBox.style.color = '#FCA5A5';
                statusBox.innerHTML = `⚠️ Заявка сохранена локально. Мы обязательно свяжемся с вами по номеру <strong>${phone}</strong>!`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 Отправить волшебную заявку';
            }
        }

        /* ==========================================================================
           5. ПАНЕЛЬ АДМИНИСТРАТОРА (CMS)
           ========================================================================== */
        function getAdminToken() {
            return sessionStorage.getItem('admin_token') || localStorage.getItem('admin_token') || '';
        }

        function openAdminModal() {
            const token = getAdminToken();
            if (token) {
                openModal('admin-dashboard-modal');
                loadAdminLeads();
            } else {
                openModal('admin-login-modal');
            }
        }

        async function handleAdminLogin(e) {
            e.preventDefault();
            const btn = document.getElementById('admin-login-btn');
            const errBox = document.getElementById('admin-login-error');
            const user = document.getElementById('admin-user').value.trim();
            const pass = document.getElementById('admin-pass').value.trim();

            btn.disabled = true;
            btn.textContent = 'Проверка... ⏳';
            errBox.style.display = 'none';

            try {
                const res = await fetch('/api/v1/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: user, password: pass })
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Неверный логин или пароль');
                }

                const data = await res.json();
                sessionStorage.setItem('admin_token', data.access_token);
                localStorage.setItem('admin_token', data.access_token);
                closeModal('admin-login-modal');
                document.getElementById('admin-login-form').reset();
                openModal('admin-dashboard-modal');
                loadAdminLeads();
            } catch (err) {
                errBox.style.display = 'block';
                errBox.textContent = err.message || 'Ошибка входа в CMS';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Войти в CMS 🚀';
            }
        }

        function logoutAdmin() {
            sessionStorage.removeItem('admin_token');
            localStorage.removeItem('admin_token');
            closeModal('admin-dashboard-modal');
            alert('Вы вышли из Панели управления CMS.');
        }

        function switchAdminTab(tab) {
            const tabLeads = document.getElementById('admin-tab-leads');
            const tabPosts = document.getElementById('admin-tab-posts');
            const tabOps = document.getElementById('admin-tab-ops');
            const btnLeads = document.getElementById('tab-btn-leads');
            const btnPosts = document.getElementById('tab-btn-posts');
            const btnOps = document.getElementById('tab-btn-ops');

            if (tab === 'leads') {
                if (tabLeads) tabLeads.style.display = 'block';
                if (tabPosts) tabPosts.style.display = 'none';
                if (tabOps) tabOps.style.display = 'none';
                if (btnLeads) btnLeads.className = 'btn btn-turquoise';
                if (btnPosts) btnPosts.className = 'btn btn-outline';
                if (btnOps) btnOps.className = 'btn btn-outline';
                loadAdminLeads();
            } else if (tab === 'posts') {
                if (tabLeads) tabLeads.style.display = 'none';
                if (tabPosts) tabPosts.style.display = 'block';
                if (tabOps) tabOps.style.display = 'none';
                if (btnLeads) btnLeads.className = 'btn btn-outline';
                if (btnPosts) btnPosts.className = 'btn btn-turquoise';
                if (btnOps) btnOps.className = 'btn btn-outline';
                loadAdminPosts();
            } else if (tab === 'ops') {
                if (tabLeads) tabLeads.style.display = 'none';
                if (tabPosts) tabPosts.style.display = 'none';
                if (tabOps) tabOps.style.display = 'block';
                if (btnLeads) btnLeads.className = 'btn btn-outline';
                if (btnPosts) btnPosts.className = 'btn btn-outline';
                if (btnOps) btnOps.className = 'btn btn-turquoise';
                loadAdminOperations();
            }
        }

        async function loadAdminOperations() {
            const container = document.getElementById('admin-ops-content');
            const token = getAdminToken();
            if (!container) return;
            if (!token) {
                container.innerHTML = '<div style="color:#EF4444;text-align:center;padding:20px;">Требуется повторный вход в CMS.</div>';
                return;
            }

            container.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:30px;">Загрузка операционных метрик и баланса... ⏳</div>';

            try {
                const headers = { 'Authorization': `Bearer ${token}` };
                const [resEtl, resLlm, resDisk] = await Promise.all([
                    fetch('/api/v1/admin/etl/metrics', { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
                    fetch('/api/v1/admin/llm/usage', { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
                    fetch('/api/v1/admin/health/yandex-disk', { headers }).then(r => r.ok ? r.json() : null).catch(() => null)
                ]);

                let html = '';

                // 1. КАРТОЧКА: ЗДОРОВЬЕ ЯНДЕКС.ДИСКА
                if (resDisk && (resDisk.status === 'OK' || resDisk.status === 'healthy' || resDisk.yandex_disk)) {
                    const yd = resDisk.yandex_disk || resDisk;
                    const totalGb = yd.total_space_bytes ? (yd.total_space_bytes / (1024 ** 3)).toFixed(1) : '-';
                    const usedGb = yd.used_space_bytes ? (yd.used_space_bytes / (1024 ** 3)).toFixed(1) : '-';
                    const freeGb = (yd.total_space_bytes && yd.used_space_bytes) ? ((yd.total_space_bytes - yd.used_space_bytes) / (1024 ** 3)).toFixed(1) : '-';
                    const isHealthy = yd.status === 'available' || resDisk.status === 'OK' || resDisk.status === 'healthy';

                    html += `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(6,182,212,0.3);border-radius:12px;padding:16px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                                <h5 style="margin:0;font-size:1.05rem;color:var(--accent-turquoise);">☁️ Яндекс.Диск (Суверенное РФ Хранилище)</h5>
                                <span style="background:${isHealthy ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'};color:${isHealthy ? '#34D399' : '#F87171'};padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">
                                    ${isHealthy ? '✅ Подключен и доступен' : '❌ Ошибка подключения'}
                                </span>
                            </div>
                            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(160px, 1fr));gap:10px;">
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Общий объем</div>
                                    <strong style="font-size:1.1rem;color:#fff;">${totalGb} ГБ</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Занято</div>
                                    <strong style="font-size:1.1rem;color:#FBBF24;">${usedGb} ГБ</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Свободно</div>
                                    <strong style="font-size:1.1rem;color:#34D399;">${freeGb} ГБ</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Токен хранилища</div>
                                    <strong style="font-size:0.9rem;color:var(--accent-turquoise);word-break:break-all;">${yd.token || 'Авторизован (OAuth)'}</strong>
                                </div>
                            </div>
                        </div>
                    `;
                }

                // 2. КАРТОЧКА: ПРОИЗВОДИТЕЛЬНОСТЬ ETL
                if (resEtl && resEtl.aggregates) {
                    const agg = resEtl.aggregates;
                    const hist = resEtl.history || [];
                    html += `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:16px;">
                            <h5 style="margin:0 0 12px 0;font-size:1.05rem;color:var(--accent-purple);">⚡ ETL Конвейер (OCR и Векторизация документов)</h5>
                            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(160px, 1fr));gap:10px;margin-bottom:14px;">
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Обработано папок</div>
                                    <strong style="font-size:1.1rem;color:#fff;">${agg.total_folders_processed}</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Ср. время на папку</div>
                                    <strong style="font-size:1.1rem;color:var(--accent-turquoise);">${agg.avg_folder_duration_seconds ? agg.avg_folder_duration_seconds.toFixed(1) + ' с' : '-'}</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Ср. скорость на файл</div>
                                    <strong style="font-size:1.1rem;color:#34D399;">${agg.avg_time_per_file_seconds ? agg.avg_time_per_file_seconds.toFixed(2) + ' с/файл' : '-'}</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Всего файлов / чанков</div>
                                    <strong style="font-size:1.1rem;color:#FBBF24;">${agg.total_files_processed} / ${agg.total_chunks_created}</strong>
                                </div>
                            </div>
                            ${hist.length > 0 ? `
                                <div style="font-size:0.85rem;font-weight:600;color:var(--text-gray);margin-bottom:6px;">Последние запуски:</div>
                                <div style="display:flex;flex-direction:column;gap:6px;max-height:160px;overflow-y:auto;">
                                    ${hist.slice(0, 5).map(h => `
                                        <div style="background:rgba(0,0,0,0.2);padding:6px 10px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;">
                                            <span style="color:#fff;font-family:monospace;">📁 ${h.folder_name.replace('disk:/', '')}</span>
                                            <span style="color:var(--text-muted);">${h.file_count} файлов • ⏱️ ${h.duration_seconds.toFixed(1)} с (${h.avg_time_per_file_seconds.toFixed(2)} с/ф)</span>
                                            <span style="color:var(--accent-turquoise);">${h.created_at ? h.created_at.split(' ')[0] : ''}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : '<div style="font-size:0.85rem;color:var(--text-muted);">История запусков пока пуста.</div>'}
                        </div>
                    `;
                }

                // 3. КАРТОЧКА: РАСХОД ТОКЕНОВ GIGACHAT И ОФИЦИАЛЬНЫЙ БАЛАНС
                if (resLlm) {
                    const usage = resLlm.usage_summary || {};
                    const bal = resLlm.balance_info || {};
                    const todayTokens = usage.today ? usage.today.total_tokens : 0;
                    const weekTokens = usage.last_7_days ? usage.last_7_days.total_tokens : 0;
                    const allTokens = usage.all_time ? usage.all_time.total_tokens : 0;
                    const balances = (bal.balance && bal.balance.balance) ? bal.balance.balance : [];

                    html += `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(251,191,36,0.3);border-radius:12px;padding:16px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                                <h5 style="margin:0;font-size:1.05rem;color:#FBBF24;">🤖 Потребление токенов & Баланс GigaChat</h5>
                                <span style="background:rgba(251,191,36,0.15);color:#FBBF24;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">
                                    ${bal.status === 'available' ? '💰 Пакет активен' : '💳 Pay-As-You-Go'}
                                </span>
                            </div>

                            <!-- Расход токенов -->
                            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(160px, 1fr));gap:10px;margin-bottom:14px;">
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Расход за сегодня</div>
                                    <strong style="font-size:1.1rem;color:#fff;">${todayTokens.toLocaleString('ru-RU')} токенов</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">За последние 7 дней</div>
                                    <strong style="font-size:1.1rem;color:var(--accent-turquoise);">${weekTokens.toLocaleString('ru-RU')} токенов</strong>
                                </div>
                                <div style="background:rgba(0,0,0,0.25);padding:10px;border-radius:8px;">
                                    <div style="font-size:0.75rem;color:var(--text-muted);">За всё время</div>
                                    <strong style="font-size:1.1rem;color:#34D399;">${allTokens.toLocaleString('ru-RU')} токенов</strong>
                                </div>
                            </div>

                            <!-- Остатки баланса Сбера -->
                            ${balances.length > 0 ? `
                                <div style="font-size:0.85rem;font-weight:600;color:var(--text-gray);margin-bottom:6px;">Остатки официального баланса Сбера:</div>
                                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:8px;margin-bottom:10px;">
                                    ${balances.map(b => `
                                        <div style="background:rgba(0,0,0,0.2);padding:8px 10px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;">
                                            <span style="color:#fff;font-weight:500;">${b.usage}</span>
                                            <span style="color:#34D399;font-weight:600;">${Number(b.value).toLocaleString('ru-RU')} ток.</span>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : `
                                <div style="background:rgba(0,0,0,0.2);padding:8px 12px;border-radius:6px;font-size:0.85rem;color:var(--text-muted);">
                                    ${bal.message || 'Официальный баланс получен.'}
                                </div>
                            `}
                        </div>
                    `;
                }

                container.innerHTML = html || '<div style="color:var(--text-muted);padding:20px;text-align:center;">Не удалось загрузить данные мониторинга.</div>';
            } catch (err) {
                container.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка загрузки метрик: ${err.message}</div>`;
            }
        }

        async function loadAdminLeads() {
            const list = document.getElementById('admin-leads-list');
            const counter = document.getElementById('leads-counter');
            const token = getAdminToken();
            if (!token) return;

            list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">Загрузка заявок...</div>';

            try {
                const res = await fetch('/api/v1/admin/leads', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка загрузки заявок');
                const leads = await res.json();
                if (counter) counter.textContent = leads.length;

                if (leads.length === 0) {
                    list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:30px;">Пока нет новых заявок.</div>';
                    return;
                }

                list.innerHTML = leads.map(l => `
                    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                                <strong style="color:#fff;font-size:1rem;">${l.name}</strong>
                                <span style="background:rgba(6,182,212,0.15);color:var(--accent-turquoise);padding:2px 8px;border-radius:4px;font-size:0.75rem;">${l.child_age || 'Общий вопрос'}</span>
                                <small style="color:var(--text-muted);font-size:0.8rem;">📅 ${l.created_at ? l.created_at.split('.')[0] : ''}</small>
                            </div>
                            <div style="color:var(--accent-purple);font-weight:600;font-size:0.9rem;margin-bottom:4px;">📞 ${l.phone}</div>
                            ${l.message ? `<div style="color:var(--text-gray);font-size:0.85rem;background:rgba(0,0,0,0.2);padding:8px;border-radius:6px;margin-top:6px;">${l.message}</div>` : ''}
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                list.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка: ${err.message}</div>`;
            }
        }

        async function loadAdminPosts() {
            const list = document.getElementById('admin-posts-list');
            if (!list) return;
            list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">Загрузка статей...</div>';

            try {
                const res = await fetch('/api/v1/public/posts');
                const posts = await res.json();

                if (!posts || posts.length === 0) {
                    list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:30px;">В блоге пока нет статей.</div>';
                    return;
                }

                list.innerHTML = posts.map(p => {
                    let tagsList = Array.isArray(p.tags) ? p.tags : (p.tags ? p.tags.split(',') : []);
                    const hasCover = Boolean(p.cover_image_url);
                    const hasVideo = Boolean(p.video_url);
                    return `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
                            ${hasCover ? `<img src="${p.cover_image_url}" style="width:60px;height:60px;border-radius:8px;object-fit:cover;flex-shrink:0;" alt="Обложка"/>` : ''}
                            <div style="flex:1;">
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <h5 style="margin:0;font-size:1rem;color:#fff;">${p.title}</h5>
                                    ${hasVideo ? '<span style="background:rgba(239,68,68,0.2);color:#F87171;padding:2px 6px;border-radius:4px;font-size:0.7rem;">🎬 Видео</span>' : ''}
                                </div>
                                <div style="font-size:0.8rem;color:var(--text-muted);margin:4px 0;">Теги: ${tagsList.join(', ')} | 📅 ${p.created_at ? p.created_at.split(' ')[0] : ''}</div>
                                <p style="margin:0;font-size:0.85rem;color:var(--text-gray);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${p.summary}</p>
                            </div>
                            <div style="display:flex;gap:8px;flex-shrink:0;">
                                <button class="btn btn-outline" style="padding:6px 12px;font-size:0.8rem;" onclick="editPost(${p.id})">✏️</button>
                                <button class="btn btn-outline" style="padding:6px 12px;font-size:0.8rem;color:#EF4444;border-color:rgba(239,68,68,0.4);" onclick="deletePost(${p.id})">🗑️</button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (err) {
                list.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка: ${err.message}</div>`;
            }
        }

        function updateCoverPreview() {
            const input = document.getElementById('edit-post-cover');
            const previewBox = document.getElementById('edit-post-cover-preview');
            const img = document.getElementById('cover-preview-img');
            if (!input || !previewBox || !img) return;
            const url = input.value.trim();
            if (url) {
                img.src = url;
                previewBox.style.display = 'block';
            } else {
                previewBox.style.display = 'none';
            }
        }

        async function handleAdminFileUpload(event, targetInputId) {
            const file = event.target.files && event.target.files[0];
            if (!file) return;
            const token = getAdminToken();
            if (!token) {
                alert('Сессия администратора не активна. Войдите в CMS.');
                return;
            }
            const formData = new FormData();
            formData.append('file', file);
            
            const targetInput = document.getElementById(targetInputId);
            if (targetInput) targetInput.placeholder = 'Загрузка на Яндекс.Диск... ⏳';

            try {
                const res = await fetch('/api/v1/admin/upload', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Ошибка загрузки файла');
                }
                const data = await res.json();
                if (targetInput) {
                    targetInput.value = data.url || data.local_url;
                    updateCoverPreview();
                }
                alert('Файл успешно загружен на Яндекс.Диск! ☁️✨');
            } catch (err) {
                alert(`Ошибка загрузки: ${err.message}`);
                if (targetInput) targetInput.placeholder = 'https://... или выберите файл';
            }
        }

        function openPostEditor(post = null) {
            const editor = document.getElementById('admin-post-editor');
            const heading = document.getElementById('editor-title-heading');
            if (!editor) return;
            editor.style.display = 'block';

            if (post) {
                if (heading) heading.textContent = 'Редактировать статью';
                document.getElementById('edit-post-id').value = post.id || '';
                document.getElementById('edit-post-title').value = post.title || '';
                document.getElementById('edit-post-tags').value = Array.isArray(post.tags) ? post.tags.join(', ') : (post.tags || '');
                const coverInp = document.getElementById('edit-post-cover');
                if (coverInp) coverInp.value = post.cover_image_url || '';
                const videoInp = document.getElementById('edit-post-video');
                if (videoInp) videoInp.value = post.video_url || '';
                document.getElementById('edit-post-summary').value = post.summary || '';
                document.getElementById('edit-post-content').value = post.content || post.summary || '';
            } else {
                if (heading) heading.textContent = 'Создать новую статью';
                document.getElementById('post-editor-form').reset();
                document.getElementById('edit-post-id').value = '';
                const coverInp = document.getElementById('edit-post-cover');
                if (coverInp) coverInp.value = '';
                const videoInp = document.getElementById('edit-post-video');
                if (videoInp) videoInp.value = '';
            }
            updateCoverPreview();
        }

        function closePostEditor() {
            const editor = document.getElementById('admin-post-editor');
            if (editor) editor.style.display = 'none';
        }

        async function editPost(postId) {
            try {
                const res = await fetch(`/api/v1/public/posts/${postId}`);
                if (res.ok) {
                    const post = await res.json();
                    openPostEditor(post);
                }
            } catch(e) {
                alert('Не удалось загрузить данные статьи.');
            }
        }

        async function handleSavePost(e) {
            e.preventDefault();
            const token = getAdminToken();
            if (!token) {
                alert('Сессия администратора истекла. Пожалуйста, войдите в систему.');
                openModal('admin-login-modal');
                return;
            }

            const btn = document.getElementById('save-post-btn');
            const postId = document.getElementById('edit-post-id').value;
            const title = document.getElementById('edit-post-title').value.trim();
            const tagsRaw = document.getElementById('edit-post-tags').value;
            const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [];
            const coverInput = document.getElementById('edit-post-cover');
            const videoInput = document.getElementById('edit-post-video');
            const cover_image_url = coverInput ? coverInput.value.trim() : '';
            const video_url = videoInput ? videoInput.value.trim() : '';
            const summary = document.getElementById('edit-post-summary').value.trim();
            const content = document.getElementById('edit-post-content').value.trim();

            btn.disabled = true;
            btn.textContent = 'Сохранение... 💾';

            try {
                const url = postId ? `/api/v1/admin/posts/${postId}` : '/api/v1/admin/posts';
                const method = postId ? 'PUT' : 'POST';

                const res = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        title,
                        summary,
                        content,
                        tags,
                        cover_image_url,
                        video_url
                    })
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Ошибка сохранения статьи');
                }

                closePostEditor();
                loadAdminPosts();
                renderLatestPosts();
                renderBlog();
                alert(postId ? 'Статья успешно обновлена! ✨' : 'Статья успешно опубликована! 🚀');
            } catch (err) {
                alert(`Ошибка: ${err.message}`);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Сохранить статью 💾';
            }
        }

        async function deletePost(postId) {
            if (!confirm('Вы уверены, что хотите удалить эту статью?')) return;
            const token = getAdminToken();
            if (!token) {
                alert('Сессия администратора не активна.');
                return;
            }

            try {
                const res = await fetch(`/api/v1/admin/posts/${postId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Ошибка удаления');
                }
                loadAdminPosts();
                renderLatestPosts();
                renderBlog();
                alert('Статья успешно удалена.');
            } catch(e) {
                alert(`Не удалось удалить статью: ${e.message}`);
            }
        }

        /* ==========================================================================
           5.1. ЛИЧНЫЙ КАБИНЕТ ВРАЧА И ШЕРИНГ КАРТЫ (DOCTOR DASHBOARD)
           ========================================================================== */
        function openDoctorModal() {
            const docToken = localStorage.getItem('doctor_token');
            if (docToken) {
                openDoctorDashboard();
            } else {
                openModal('doctor-modal');
                const docError = document.getElementById('doctor-login-error');
                if (docError) docError.style.display = 'none';
            }
        }

        async function handleDoctorLogin(e) {
            e.preventDefault();
            const login = document.getElementById('doc-login').value.trim();
            const password = document.getElementById('doc-pass').value;
            const errorDiv = document.getElementById('doctor-login-error');
            const submitBtn = document.getElementById('doctor-login-btn');

            errorDiv.style.display = 'none';
            submitBtn.disabled = true;
            submitBtn.textContent = 'Проверка доступа... 🩺';

            try {
                const res = await fetch('/api/v1/doctor/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ login, password })
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Неверный логин или пароль врача');
                }

                const data = await res.json();
                localStorage.setItem('doctor_token', data.access_token);
                localStorage.setItem('doctor_id', data.doctor_id);
                localStorage.setItem('doctor_name', data.full_name);
                localStorage.setItem('doctor_specialty', data.specialty);

                closeModal('doctor-modal');
                openDoctorDashboard();

                // Проверяем отложенный токен шеринга из URL
                const pendingToken = sessionStorage.getItem('pending_share_token');
                if (pendingToken) {
                    sessionStorage.removeItem('pending_share_token');
                    const tokenInput = document.getElementById('doc-share-token-input');
                    if (tokenInput) tokenInput.value = pendingToken;
                    loadDoctorPatientRecord(pendingToken);
                }
            } catch (err) {
                errorDiv.textContent = err.message;
                errorDiv.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🩺 Войти в кабинет врача';
            }
        }

        function openDoctorDashboard() {
            const docName = localStorage.getItem('doctor_name') || 'Доктор Центра';
            const docSpec = localStorage.getItem('doctor_specialty') || 'Специалист';

            const nameEl = document.getElementById('doc-profile-name');
            const specEl = document.getElementById('doc-profile-specialty');
            if (nameEl) nameEl.textContent = docName;
            if (specEl) specEl.textContent = docSpec;

            openModal('doctor-dashboard-modal');
        }

        function logoutDoctor() {
            localStorage.removeItem('doctor_token');
            localStorage.removeItem('doctor_id');
            localStorage.removeItem('doctor_name');
            localStorage.removeItem('doctor_specialty');
            closeModal('doctor-dashboard-modal');
            
            // Сброс полей
            const tokenInput = document.getElementById('doc-share-token-input');
            if (tokenInput) tokenInput.value = '';
            const recordView = document.getElementById('doc-record-view');
            if (recordView) recordView.style.display = 'none';
            const recordEmpty = document.getElementById('doc-record-empty');
            if (recordEmpty) recordEmpty.style.display = 'block';
            const errorDiv = document.getElementById('doc-search-error');
            if (errorDiv) errorDiv.style.display = 'none';
        }

        async function handleDoctorSearchRecord() {
            let token = document.getElementById('doc-share-token-input').value.trim();
            if (!token) {
                const errEl = document.getElementById('doc-search-error');
                if (errEl) {
                    errEl.textContent = 'Пожалуйста, введите токен или вставьте ссылку доступа.';
                    errEl.style.display = 'block';
                }
                return;
            }

            // Извлечение чистого токена, если вставили полную ссылку
            if (token.includes('share_token=')) {
                const parts = token.split('share_token=');
                token = parts[1].split('&')[0];
                document.getElementById('doc-share-token-input').value = token;
            }

            await loadDoctorPatientRecord(token);
        }

        async function loadDoctorPatientRecord(shareToken) {
            const docToken = localStorage.getItem('doctor_token');
            const errorDiv = document.getElementById('doc-search-error');
            const recordView = document.getElementById('doc-record-view');
            const recordEmpty = document.getElementById('doc-record-empty');
            const searchBtn = document.getElementById('doc-search-btn');

            if (!docToken) {
                sessionStorage.setItem('pending_share_token', shareToken);
                closeModal('doctor-dashboard-modal');
                openDoctorModal();
                const loginErr = document.getElementById('doctor-login-error');
                if (loginErr) {
                    loginErr.textContent = 'Для просмотра карты пациента по ссылке выполните вход в систему.';
                    loginErr.style.display = 'block';
                }
                return;
            }

            if (errorDiv) errorDiv.style.display = 'none';
            if (searchBtn) {
                searchBtn.disabled = true;
                searchBtn.textContent = 'Загрузка...';
            }

            try {
                const res = await fetch(`/api/v1/doctor/patient-records/${encodeURIComponent(shareToken)}`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });

                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    if (res.status === 403 || res.status === 410) {
                        throw new Error(errData.detail || 'Срок действия ссылки истек или доступ был отозван.');
                    }
                    if (res.status === 401) {
                        logoutDoctor();
                        throw new Error('Сессия врача истекла. Пожалуйста, войдите снова.');
                    }
                    throw new Error(errData.detail || 'Медицинская карта не найдена.');
                }

                const data = await res.json();
                
                // Заполняем данные карты
                document.getElementById('doc-view-patient-id').textContent = data.patient_folder_id || 'ID: Confidential';
                document.getElementById('doc-view-expiry').textContent = `⏱️ Доступ активен до: ${data.expires_at}`;

                const grid = document.getElementById('doc-files-grid');
                grid.innerHTML = '';

                const docs = data.documents || [];
                if (docs.length === 0) {
                    grid.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem;">В папке пациента пока нет загруженных файлов.</div>';
                } else {
                    docs.forEach(doc => {
                        const card = document.createElement('div');
                        card.style.cssText = 'background: rgba(30,30,46,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 14px; display: flex; flex-direction: column; justify-content: space-between; gap: 10px; transition: transform 0.2s ease;';
                        card.onmouseenter = () => card.style.transform = 'translateY(-2px)';
                        card.onmouseleave = () => card.style.transform = 'translateY(0)';

                        const icon = (doc.name && doc.name.endsWith('.pdf')) ? '📕' : ((doc.name && doc.name.endsWith('.docx')) ? '📘' : '📋');
                        const size = doc.size ? `(${doc.size})` : '';

                        card.innerHTML = `
                            <div style="display: flex; align-items: flex-start; gap: 10px;">
                                <span style="font-size: 1.4rem; line-height: 1;">${icon}</span>
                                <div style="flex: 1; min-width: 0;">
                                    <div style="font-size: 0.9rem; font-weight: 600; color: #fff; word-break: break-word;" title="${doc.name}">${doc.name}</div>
                                    <div style="font-size: 0.75rem; color: var(--accent-turquoise); margin-top: 4px;">Диагностический документ ${size}</div>
                                </div>
                            </div>
                            <div style="display: flex; gap: 8px; margin-top: 6px;">
                                <button class="btn btn-outline" style="flex: 1; padding: 6px 10px; font-size: 0.8rem;" onclick="alert('Документ: ${doc.name}\\nФайл расшифрован и готов к клиническому анализу.')">👁️ Просмотр</button>
                                <button class="btn btn-turquoise" style="padding: 6px 12px; font-size: 0.8rem;" onclick="alert('Скачивание зашифрованного файла ${doc.name}...')">💾</button>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                }

                if (recordEmpty) recordEmpty.style.display = 'none';
                if (recordView) recordView.style.display = 'block';
            } catch (err) {
                if (recordView) recordView.style.display = 'none';
                if (recordEmpty) recordEmpty.style.display = 'block';
                if (errorDiv) {
                    errorDiv.textContent = '❌ ' + err.message;
                    errorDiv.style.display = 'block';
                }
            } finally {
                if (searchBtn) {
                    searchBtn.disabled = false;
                    searchBtn.textContent = '🔍 Открыть карту';
                }
            }
        }

        /* ==========================================================================
           6. КЛИЕНТСКИЙ ИНТЕРФЕЙС И НАВИГАЦИЯ
           ========================================================================== */
        function preserveQueryParameters() {
            const urlParams = window.location.search;
            if (urlParams) {
                const parentBtn = document.getElementById('parent-login');
                if (parentBtn) parentBtn.setAttribute('href', `/app/${urlParams}`);
                const heroAiChat = document.getElementById('hero-ai-chat');
                if (heroAiChat) heroAiChat.setAttribute('href', `/app/${urlParams}`);
            }
        }

        const header = document.getElementById('main-header');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) header.classList.add('scrolled');
            else header.classList.remove('scrolled');
        });

        const burger = document.getElementById('burger');
        const navMenu = document.getElementById('nav-menu');
        burger.addEventListener('click', () => {
            burger.classList.toggle('open');
            navMenu.classList.toggle('active');
        });

        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                burger.classList.remove('open');
                navMenu.classList.remove('active');
            });
        });

        function openModal(id) {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add('open');
                document.body.style.overflow = 'hidden';
            }
        }

        function closeModal(id) {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('open');
                document.body.style.overflow = '';
            }
        }

        document.querySelectorAll('.modal').forEach(m => {
            m.addEventListener('click', (e) => {
                if (e.target === m) closeModal(m.id);
            });
        });

        document.getElementById('blog-tags-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('chip')) {
                document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                renderBlog(e.target.getAttribute('data-tag'));
            }
        });

        /* Шоукейс персонажей Pixar */
        const showcaseImg = document.getElementById('showcase-img');
        const showcaseName = document.getElementById('showcase-name');
        const showcaseDesc = document.getElementById('showcase-desc');
        const showcaseGlow = document.getElementById('showcase-glow');
        const selectorThumbs = document.querySelectorAll('.selector-thumb');

        function playCharSound(charId) {
            try {
                let audio = new Audio(`/static/audio/sound_${charId}.mp3`);
                audio.volume = 0.5;
                let playPromise = audio.play();
                if (playPromise !== undefined) {
                    playPromise.catch(e => console.log('Android audio autoplay check:', e));
                }
            } catch (err) {
                console.log('Android audio init check:', err);
            }
        }

        selectorThumbs.forEach(thumb => {
            thumb.addEventListener('mouseenter', () => {
                const charId = thumb.getAttribute('data-char');
                if (charId) playCharSound(charId);
            });

            thumb.addEventListener('click', () => {
                const charId = thumb.getAttribute('data-char');
                const charData = CHARACTERS[charId];
                if (!charData) return;

                // Гарантированное воспроизведение звука при тапе на мобильном
                playCharSound(charId);

                selectorThumbs.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');

                const heroAlikWrapper = document.getElementById('hero-alik-wrapper');

                if (charId === 'a') {
                    // Алик — отображаем выделенный слой прозрачного Алика
                    if (heroAlikWrapper) {
                        heroAlikWrapper.style.display = 'flex';
                        heroAlikWrapper.style.opacity = '1';
                    }
                    showcaseImg.style.display = 'none';
                    document.getElementById('showcase-ph').style.display = 'none';
                    showcaseName.textContent = charData.name;
                    showcaseDesc.textContent = charData.desc;
                    showcaseGlow.style.background = charData.glow;
                } else {
                    // Другие персонажи звуков
                    if (heroAlikWrapper) {
                        heroAlikWrapper.style.display = 'none';
                    }
                    showcaseImg.classList.add('switching');
                    
                    setTimeout(() => {
                        showcaseImg.setAttribute('src', charData.img);
                        showcaseImg.onerror = function() {
                            if (this.src.endsWith('.jpg')) {
                                this.src = this.src.replace('.jpg', '.png');
                            } else {
                                this.style.display = 'none';
                                document.getElementById('showcase-ph').style.display = 'flex';
                            }
                        };
                        showcaseImg.style.display = 'block';
                        document.getElementById('showcase-ph').style.display = 'none';

                        showcaseName.textContent = charData.name;
                        showcaseDesc.textContent = charData.desc;
                        showcaseGlow.style.background = charData.glow;
                        
                        showcaseImg.classList.remove('switching');
                    }, 250);
                }
            });
        });

        /* ==========================================================================
           4. ЛОГИКА И АНИМАЦИЯ ПЛАВАЮЩЕГО ПЕРСОНАЖА «АЛИК» (FLIP & OBSERVER)
           ========================================================================== */
        function initFloatingAlik() {
            const heroAlikWrapper = document.getElementById('hero-alik-wrapper');
            const heroAlikImg = document.getElementById('hero-alik-img');
            const heroShowcase = document.querySelector('.character-showcase') || document.querySelector('.hero');
            const floatingWidget = document.getElementById('floating-alik-widget');
            const floatingAlikInner = document.getElementById('alik-avatar-inner');
            const floatingAlikImg = document.getElementById('floating-alik-img');
            const avatarContainer = document.getElementById('alik-avatar-container');
            const speechBubble = document.getElementById('alik-speech-bubble');
            const bubbleText = document.getElementById('alik-bubble-text');
            const bubbleClose = document.getElementById('alik-bubble-close');
            const widgetToggle = document.getElementById('alik-widget-toggle');
            const toggleIcon = document.getElementById('alik-toggle-icon');

            if (!floatingWidget || !floatingAlikImg) return;

            let isFloating = false;
            let isTransitioning = false;
            let isBubbleHiddenManually = false;
            let isMinimized = false;
            let currentComment = "Привет! Я Алик — весёлый музыкант и твой проводник по Маленькой Стране! 🎸";
            const defaultHeroComment = "Привет! Я Алик — весёлый музыкант и твой проводник по Маленькой Стране! 🎸";

            // Показ реплики в зеленом облачке
            function showBubble(text) {
                if (!speechBubble || !bubbleText || isBubbleHiddenManually || isMinimized) return;
                const cleanText = (text || currentComment || defaultHeroComment).trim();
                if (bubbleText.textContent === cleanText && speechBubble.classList.contains('visible')) {
                    return;
                }

                if (speechBubble.classList.contains('visible')) {
                    speechBubble.classList.add('updating');
                    setTimeout(() => {
                        bubbleText.textContent = cleanText;
                        speechBubble.classList.remove('updating');
                    }, 160);
                } else {
                    bubbleText.textContent = cleanText;
                    speechBubble.classList.add('visible');
                }
            }

            // Скрытие реплики
            function hideBubble() {
                if (speechBubble) {
                    speechBubble.classList.remove('visible');
                }
            }

            // FLIP: Переход из Hero в фиксированный виджет
            function transitionToFloating() {
                if (isFloating || isTransitioning) return;
                isTransitioning = true;

                const heroRect = heroAlikImg ? heroAlikImg.getBoundingClientRect() : null;
                
                // 1. Активируем контейнер виджета
                floatingWidget.classList.add('floating-active');
                floatingWidget.style.opacity = '1';
                floatingWidget.style.pointerEvents = 'auto';

                // 2. Вычисляем FLIP First -> Last
                if (heroRect && heroRect.width > 0 && heroRect.bottom > 0) {
                    const floatRect = floatingAlikImg.getBoundingClientRect();
                    const dx = (heroRect.left + heroRect.width / 2) - (floatRect.left + floatRect.width / 2);
                    const dy = (heroRect.top + heroRect.height / 2) - (floatRect.top + floatRect.height / 2);
                    const scale = heroRect.width / (floatRect.width || 1);

                    // Invert
                    floatingAlikInner.style.transition = 'none';
                    floatingAlikInner.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
                    if (heroAlikWrapper) heroAlikWrapper.style.opacity = '0';

                    // Play
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            floatingAlikInner.style.transition = 'transform 0.65s cubic-bezier(0.2, 0.9, 0.3, 1.15), opacity 0.4s ease';
                            floatingAlikInner.style.transform = 'translate(0, 0) scale(1)';
                        });
                    });
                } else {
                    if (heroAlikWrapper) heroAlikWrapper.style.opacity = '0';
                }

                setTimeout(() => {
                    isFloating = true;
                    isTransitioning = false;
                    floatingAlikInner.style.transition = '';
                    floatingAlikInner.style.transform = '';
                    showBubble(currentComment);
                }, 680);
            }

            // FLIP: Возврат из фиксированного виджета в Hero
            function transitionToHero() {
                if (!isFloating || isTransitioning) return;
                isTransitioning = true;
                hideBubble();

                const heroRect = heroAlikImg ? heroAlikImg.getBoundingClientRect() : null;
                if (heroRect && heroRect.width > 0 && heroRect.top > -200) {
                    const floatRect = floatingAlikImg.getBoundingClientRect();
                    const dx = (heroRect.left + heroRect.width / 2) - (floatRect.left + floatRect.width / 2);
                    const dy = (heroRect.top + heroRect.height / 2) - (floatRect.top + floatRect.height / 2);
                    const scale = heroRect.width / (floatRect.width || 1);

                    floatingAlikInner.style.transition = 'transform 0.55s cubic-bezier(0.25, 1, 0.5, 1)';
                    floatingAlikInner.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;

                    setTimeout(() => {
                        floatingWidget.classList.remove('floating-active');
                        floatingWidget.style.opacity = '0';
                        floatingWidget.style.pointerEvents = 'none';
                        floatingAlikInner.style.transition = '';
                        floatingAlikInner.style.transform = '';
                        if (heroAlikWrapper) heroAlikWrapper.style.opacity = '1';
                        isFloating = false;
                        isTransitioning = false;
                    }, 560);
                } else {
                    floatingWidget.classList.remove('floating-active');
                    floatingWidget.style.opacity = '0';
                    floatingWidget.style.pointerEvents = 'none';
                    if (heroAlikWrapper) heroAlikWrapper.style.opacity = '1';
                    isFloating = false;
                    isTransitioning = false;
                }
            }

            // Отслеживание положения Hero блока
            if ('IntersectionObserver' in window && heroShowcase) {
                const heroObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        const scrollY = window.scrollY || document.documentElement.scrollTop;
                        if (!entry.isIntersecting || entry.intersectionRatio < 0.3) {
                            if (scrollY > 160 && !isFloating && !isTransitioning) {
                                transitionToFloating();
                            }
                        } else {
                            if (scrollY < 220 && isFloating && !isTransitioning) {
                                transitionToHero();
                            }
                        }
                    });
                }, {
                    threshold: [0, 0.25, 0.5, 0.75, 1]
                });
                heroObserver.observe(heroShowcase);
            }

            // Резервный скролл-триггер
            window.addEventListener('scroll', () => {
                const scrollY = window.scrollY || document.documentElement.scrollTop;
                if (scrollY > 280 && !isFloating && !isTransitioning) {
                    transitionToFloating();
                } else if (scrollY <= 70 && isFloating && !isTransitioning) {
                    transitionToHero();
                }
            }, { passive: true });

            // Отслеживание смысловых секций страницы для смены реплик
            if ('IntersectionObserver' in window) {
                const sectionObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const comment = entry.target.getAttribute('data-alik-comment');
                            if (comment) {
                                currentComment = comment;
                                if (isFloating && !isTransitioning) {
                                    showBubble(comment);
                                }
                            }
                        }
                    });
                }, {
                    rootMargin: '-20% 0px -35% 0px',
                    threshold: 0.15
                });

                document.querySelectorAll('[data-alik-comment]').forEach(sec => {
                    sectionObserver.observe(sec);
                });
            }

            // Клик по аватару Алика — переключение диалогового облачка
            if (avatarContainer) {
                avatarContainer.addEventListener('click', (e) => {
                    if (e.target.closest('#alik-widget-toggle')) return;

                    if (isMinimized) {
                        isMinimized = false;
                        floatingWidget.classList.remove('minimized');
                        if (toggleIcon) toggleIcon.textContent = '−';
                        showBubble(currentComment);
                        return;
                    }

                    if (speechBubble && speechBubble.classList.contains('visible')) {
                        isBubbleHiddenManually = true;
                        hideBubble();
                    } else {
                        isBubbleHiddenManually = false;
                        showBubble(currentComment);
                    }
                });
            }

            // Закрытие диалогового облачка
            if (bubbleClose) {
                bubbleClose.addEventListener('click', (e) => {
                    e.stopPropagation();
                    isBubbleHiddenManually = true;
                    hideBubble();
                });
            }

            // Сворачивание / разворачивание виджета
            if (widgetToggle) {
                widgetToggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    isMinimized = !isMinimized;
                    floatingWidget.classList.toggle('minimized', isMinimized);
                    if (toggleIcon) {
                        toggleIcon.textContent = isMinimized ? '+' : '−';
                    }
                    if (isMinimized) {
                        hideBubble();
                    } else {
                        isBubbleHiddenManually = false;
                        showBubble(currentComment);
                    }
                });
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            preserveQueryParameters();
            initFloatingAlik();

            // Проверка URL параметров для глубоких ссылок (Deep-linking)
            const urlParams = new URLSearchParams(window.location.search);
            const shareToken = urlParams.get('share_token');
            const hash = window.location.hash;

            if (shareToken) {
                const docInput = document.getElementById('doc-share-token-input');
                if (docInput) docInput.value = shareToken;
                
                const docToken = localStorage.getItem('doctor_token');
                if (docToken) {
                    openDoctorDashboard();
                    loadDoctorPatientRecord(shareToken);
                } else {
                    sessionStorage.setItem('pending_share_token', shareToken);
                    openDoctorModal();
                }
            } else if (hash === '#doctor' || hash === '#doc') {
                openDoctorModal();
            } else if (hash === '#admin' || hash === '#cms') {
                openAdminModal();
            }

            Promise.all([
                renderLatestPosts(),
                renderServices(),
                renderDoctors(),
                renderBlog(),
                renderEvents()
            ]).then(() => {
                console.log('🌌 Все сказочные блоки, CMS, Докторский портал и помощник Алик готовы к работе!');
            });
        });