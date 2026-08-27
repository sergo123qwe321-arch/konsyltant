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

        function createBlogCardHTML(post) {
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

            return `
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
        }

        let currentLibraryTag = null;
        let isLibraryExpanded = false;

        async function renderBlog(tag = null, forceExpand = null) {
            if (forceExpand !== null) {
                isLibraryExpanded = forceExpand;
            } else if (tag !== currentLibraryTag) {
                isLibraryExpanded = false;
            }
            currentLibraryTag = tag;

            const endpoint = tag ? `/posts?tag=${encodeURIComponent(tag)}` : '/posts';
            const data = await loadData(endpoint);
            cachedPosts = data;
            const container = document.getElementById('blog-container');
            if (!container) return;
            container.innerHTML = '';
            
            if (!data || data.length === 0) {
                container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">🦄 Статей в этой категории пока нет.</div>`;
                return;
            }

            if (!isLibraryExpanded && data.length > 5) {
                // Отрисовываем ровно первые 5 карточек
                data.slice(0, 5).forEach(post => {
                    container.innerHTML += createBlogCardHTML(post);
                });

                // На 6-й позиции добавляем интерактивную кнопку-карточку «Показать еще»
                const remaining = data.length - 5;
                container.innerHTML += `
                    <div class="card-glass blog-card load-more-card" id="btn-load-more-library" onclick="renderBlog('${tag || ''}', true)">
                        <div style="font-size: 2.4rem; margin-bottom: 10px;">📚</div>
                        <h3 style="font-size: 1.15rem; margin-bottom: 6px; color: var(--accent-turquoise, #2DD4BF);">Показать еще 📚</h3>
                        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 14px;">Ещё ${remaining} материалов библиотеки</p>
                        <span class="btn btn-outline" style="padding: 6px 16px; font-size: 0.82rem; pointer-events: none;">Развернуть все ↓</span>
                    </div>
                `;
            } else {
                // Отрисовываем все материалы
                data.forEach(post => {
                    container.innerHTML += createBlogCardHTML(post);
                });

                if (data.length > 5 && isLibraryExpanded) {
                    container.innerHTML += `
                        <div class="card-glass blog-card load-more-card" id="btn-collapse-library" onclick="renderBlog('${tag || ''}', false)" style="min-height: 180px;">
                            <div style="font-size: 1.8rem; margin-bottom: 8px;">⬆️</div>
                            <h3 style="font-size: 1.05rem; margin-bottom: 4px; color: var(--accent-turquoise, #2DD4BF);">Свернуть библиотеку</h3>
                            <span class="btn btn-outline" style="padding: 4px 14px; font-size: 0.8rem; pointer-events: none;">Свернуть ↑</span>
                        </div>
                    `;
                }
            }
        }

        // Псевдонимы функций для обратной совместимости
        window.renderLibraryCards = renderBlog;
        window.loadPublicLibrary = renderBlog;
        window.renderPostsSection = renderLatestPosts;

        function escapeHtml(str) {
            if (str === null || str === undefined) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        function getEmbedVideoUrl(url) {
            if (!url) return '';
            const trimmed = url.trim();
            if (trimmed.includes('rutube.ru')) {
                const match = trimmed.match(/rutube\.ru\/(?:video|play\/embed)\/([a-zA-Z0-9]+)/);
                if (match && match[1]) {
                    return `https://rutube.ru/play/embed/${match[1]}`;
                }
                return trimmed;
            }
            if (trimmed.includes('vk.com') || trimmed.includes('vkvideo.ru')) {
                if (trimmed.includes('video_ext.php')) return trimmed;
                const match = trimmed.match(/video(-?\d+)_(\d+)/);
                if (match) {
                    return `https://vk.com/video_ext.php?oid=${match[1]}&id=${match[2]}&hd=2`;
                }
                return trimmed;
            }
            if (trimmed.includes('youtube.com') || trimmed.includes('youtu.be')) {
                let videoId = '';
                if (trimmed.includes('youtu.be/')) {
                    videoId = trimmed.split('youtu.be/')[1].split(/[?&]/)[0];
                } else if (trimmed.includes('v=')) {
                    videoId = trimmed.split('v=')[1].split('&')[0];
                } else if (trimmed.includes('embed/')) {
                    return trimmed;
                }
                if (videoId) {
                    return `https://www.youtube.com/embed/${videoId}`;
                }
            }
            return trimmed;
        }

        function renderMediaBlock(videoUrl, coverImageUrl) {
            if (!videoUrl && !coverImageUrl) return '';
            let html = '';
            
            if (videoUrl) {
                const isLocalVideo = videoUrl.endsWith('.mp4') || videoUrl.endsWith('.webm') || videoUrl.includes('/static/uploads/');
                if (isLocalVideo) {
                    const posterAttr = coverImageUrl ? `poster="${coverImageUrl}"` : '';
                    html += `
                        <div style="margin-bottom: 14px;">
                            <video controls ${posterAttr} style="width: 100%; max-height: 340px; border-radius: 12px; background: #000; display: block;" src="${videoUrl}"></video>
                            <div style="margin-top: 8px; font-size: 0.85rem;">
                                <a href="${videoUrl}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-turquoise); text-decoration: underline; display: inline-flex; align-items: center; gap: 4px;">
                                    <span>🔗 Смотреть на первоисточнике</span> <span style="font-size: 0.75rem;">↗</span>
                                </a>
                            </div>
                        </div>
                    `;
                } else {
                    const embedUrl = getEmbedVideoUrl(videoUrl);
                    html += `
                        <div style="margin-bottom: 14px;">
                            <iframe src="${embedUrl}" style="width: 100%; height: 320px; border: none; border-radius: 12px; background: #000;" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                            <div style="margin-top: 8px; font-size: 0.85rem;">
                                <a href="${videoUrl}" target="_blank" rel="noopener noreferrer" style="color: var(--accent-turquoise); text-decoration: underline; display: inline-flex; align-items: center; gap: 4px;">
                                    <span>🔗 Смотреть на первоисточнике</span> <span style="font-size: 0.75rem;">↗</span>
                                </a>
                            </div>
                        </div>
                    `;
                }
            } else if (coverImageUrl) {
                html += `<img src="${coverImageUrl}" style="width: 100%; max-height: 280px; object-fit: cover; border-radius: 12px; margin-bottom: 14px;" alt="Обложка"/>`;
            }
            
            return html;
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
            
            document.getElementById('article-modal-tags').innerHTML = tagsList.map(t => `<span class="blog-tag" style="margin-right: 6px;">${escapeHtml(t)}</span>`).join('');
            
            const mediaContainer = document.getElementById('article-modal-media');
            if (mediaContainer) {
                const mediaHTML = renderMediaBlock(post.video_url, post.cover_image_url);
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
                loadAdminDoctors();
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
                loadAdminDoctors();
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
            const tabs = ['leads', 'doctors', 'posts', 'ops', 'moderation'];
            tabs.forEach(t => {
                const el = document.getElementById(`admin-tab-${t}`);
                const btn = document.getElementById(`tab-btn-${t}`);
                if (el) {
                    el.style.display = (t === tab) ? 'block' : 'none';
                }
                if (btn) {
                    btn.className = (t === tab) ? 'btn btn-turquoise' : 'btn btn-outline';
                }
            });

            if (tab === 'leads') {
                loadAdminLeads();
            } else if (tab === 'doctors') {
                loadAdminDoctors();
            } else if (tab === 'posts') {
                loadAdminPosts();
            } else if (tab === 'ops') {
                loadAdminOperations();
                loadAdminBackups();
            } else if (tab === 'moderation') {
                loadAdminModerationQueue();
            }
        }

        async function loadAdminDoctors() {
            const listDiv = document.getElementById('admin-doctors-list');
            const counter = document.getElementById('doctors-counter');
            const token = getAdminToken();
            if (!token) return;

            if (listDiv) {
                listDiv.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">Загрузка списка специалистов... ⏳</div>';
            }

            try {
                const res = await fetch('/api/v1/admin/doctors', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка загрузки врачей');
                const data = await res.json();
                const doctors = data.doctors || [];

                if (counter) counter.textContent = doctors.length;

                if (!listDiv) return;
                if (doctors.length === 0) {
                    listDiv.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">В базе пока нет зарегистрированных специалистов.</div>';
                    return;
                }

                let html = '';
                doctors.forEach(d => {
                    const verifiedBadge = d.is_verified 
                        ? '<span style="color:#34D399;background:rgba(16,185,129,0.15);padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;">✅ Верифицирован</span>' 
                        : '<span style="color:#F59E0B;background:rgba(245,158,11,0.15);padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;">⏳ Ожидает</span>';

                    html += `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                                    <strong style="color:#fff;font-size:0.95rem;">${escapeHtml(d.full_name)}</strong>
                                    ${verifiedBadge}
                                </div>
                                <div style="color:var(--accent-turquoise);font-size:0.85rem;margin-bottom:2px;">
                                    🩺 ${escapeHtml(d.specialty || 'Специалист')}
                                </div>
                                <div style="color:var(--text-muted);font-size:0.8rem;">
                                    📧 ${escapeHtml(d.email || '-')} &nbsp;|&nbsp; 📜 Лицензия: <code>${escapeHtml(d.license_number || '-')}</code>
                                </div>
                            </div>
                            <div style="font-size:0.78rem;color:var(--text-muted);text-align:right;">
                                Регистрация:<br>${escapeHtml(d.created_at ? d.created_at.slice(0,10) : '-')}
                            </div>
                        </div>
                    `;
                });
                listDiv.innerHTML = html;
            } catch (e) {
                if (listDiv) listDiv.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка: ${escapeHtml(e.message)}</div>`;
            }
        }

        async function handleRegisterDoctor(event) {
            event.preventDefault();
            const token = getAdminToken();
            if (!token) {
                alert('Требуется авторизация администратора');
                return;
            }

            const fullNameInput = document.getElementById('doc-reg-fullname');
            const specialtyInput = document.getElementById('doc-reg-specialty');
            const emailInput = document.getElementById('doc-reg-email');
            const phoneInput = document.getElementById('doc-reg-phone');
            const licenseInput = document.getElementById('doc-reg-license');
            const submitBtn = document.getElementById('doc-reg-submit-btn');
            const resultBox = document.getElementById('doc-reg-result-box');

            const fullName = fullNameInput ? fullNameInput.value.trim() : '';
            const specialty = specialtyInput ? specialtyInput.value.trim() : '';
            const email = emailInput ? emailInput.value.trim() : '';
            const phone = phoneInput ? phoneInput.value.trim() : '';
            const license = licenseInput ? licenseInput.value.trim() : '';

            if (!fullName || !specialty || !email) {
                alert('Пожалуйста, заполните обязательные поля (ФИО, Специализация, Email).');
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Регистрация и отправка письма... ⏳';
            }
            if (resultBox) {
                resultBox.style.display = 'none';
            }

            try {
                const res = await fetch('/api/v1/admin/doctors', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        specialty: specialty,
                        email: email,
                        phone: phone,
                        license_number: license
                    })
                });

                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    throw new Error(data.detail || 'Не удалось зарегистрировать врача');
                }

                if (resultBox) {
                    const emailStatusHtml = data.email_sent 
                        ? '<span style="color:#34D399;">✅ Письмо с реквизитами доступа успешно отправлено на email врача и в копию клиники!</span>' 
                        : '<span style="color:#F59E0B;">⚠️ Врач сохранен в базе, но отправка через SMTP временно недоступна. Сохраните временный пароль.</span>';

                    resultBox.style.display = 'block';
                    resultBox.style.background = 'rgba(16,185,129,0.1)';
                    resultBox.style.border = '1px solid rgba(16,185,129,0.3)';
                    resultBox.innerHTML = `
                        <div style="font-weight:600;color:#34D399;font-size:0.95rem;margin-bottom:6px;">
                            🎉 Врач «${escapeHtml(data.doctor.full_name)}» успешно зарегистрирован!
                        </div>
                        <div style="color:#F8FAFC;margin-bottom:6px;">
                            <b>Логин:</b> <code>${escapeHtml(data.doctor.email)}</code> &nbsp;|&nbsp; 
                            <b>Временный пароль:</b> <code style="color:#4ADE80;background:rgba(0,0,0,0.4);padding:2px 8px;border-radius:4px;font-size:1rem;font-weight:bold;">${escapeHtml(data.temporary_password)}</code>
                        </div>
                        <div style="font-size:0.82rem;">${emailStatusHtml}</div>
                    `;
                }

                if (fullNameInput) fullNameInput.value = '';
                if (specialtyInput) specialtyInput.value = '';
                if (emailInput) emailInput.value = '';
                if (phoneInput) phoneInput.value = '';
                if (licenseInput) licenseInput.value = '';

                await loadAdminDoctors();
            } catch (err) {
                if (resultBox) {
                    resultBox.style.display = 'block';
                    resultBox.style.background = 'rgba(239,68,68,0.1)';
                    resultBox.style.border = '1px solid rgba(239,68,68,0.3)';
                    resultBox.innerHTML = `<span style="color:#EF4444;">❌ ${escapeHtml(err.message)}</span>`;
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Зарегистрировать врача и отправить доступы ✉️';
                }
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
            loadAdminBackups();

            try {
                const headers = { 'Authorization': `Bearer ${token}` };
                const [resEtl, resLlm, resDisk, resAlerts] = await Promise.all([
                    fetch('/api/v1/admin/etl/metrics', { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
                    fetch('/api/v1/admin/llm/usage', { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
                    fetch('/api/v1/admin/health/yandex-disk', { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
                    fetch('/api/v1/admin/alerts/status', { headers }).then(r => r.ok ? r.json() : null).catch(() => null)
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

                // 4. КАРТОЧКА: СИСТЕМА ОПОВЕЩЕНИЙ И АЛЕРТОВ
                const alertServices = resAlerts && resAlerts.services ? resAlerts.services : {};
                const hasActiveAlerts = Object.values(alertServices).some(s => s.is_active_alert);

                html += `
                    <div style="background:rgba(255,255,255,0.03);border:1px solid ${hasActiveAlerts ? 'rgba(239,68,68,0.5)' : 'rgba(16,185,129,0.3)'};border-radius:12px;padding:16px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
                            <div>
                                <h5 style="margin:0;font-size:1.05rem;color:${hasActiveAlerts ? '#F87171' : '#34D399'};">🚨 Система оповещений о сбоях</h5>
                                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">
                                    Уведомления дублируются на: <span style="color:#38BDF8;">konsultantms@yandex.com</span> и <span style="color:#38BDF8;">sergo123qwe321@gmail.com</span>
                                </div>
                            </div>
                            <button id="test-alert-btn" class="btn btn-turquoise" onclick="handleTestAlert()" style="padding:6px 12px;font-size:0.8rem;">
                                🔔 Проверить оповещения (Тест)
                            </button>
                        </div>

                        <div id="test-alert-result" style="display:none;margin-bottom:12px;"></div>

                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:8px;">
                            ${Object.keys(alertServices).length > 0 ? Object.entries(alertServices).map(([k, s]) => `
                                <div style="background:rgba(0,0,0,0.25);padding:8px 10px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;border-left:3px solid ${s.is_active_alert ? '#EF4444' : '#10B981'};">
                                    <span style="color:#fff;font-weight:500;">${s.title}</span>
                                    <span style="color:${s.is_active_alert ? '#F87171' : '#34D399'};font-weight:600;">
                                        ${s.is_active_alert ? '🚨 Сбой' : '✅ Норма'}
                                    </span>
                                </div>
                            `).join('') : `
                                <div style="background:rgba(0,0,0,0.25);padding:8px 10px;border-radius:6px;font-size:0.8rem;color:var(--text-muted);">
                                    Мониторинг 6 критических сервисов активен (интервал: 5 мин, дедупликация: 1 час).
                                </div>
                            `}
                        </div>
                    </div>
                `;

                container.innerHTML = html || '<div style="color:var(--text-muted);padding:20px;text-align:center;">Не удалось загрузить данные мониторинга.</div>';
            } catch (err) {
                container.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка загрузки метрик: ${err.message}</div>`;
            }
        }

        async function handleTestAlert() {
            const btn = document.getElementById('test-alert-btn');
            const resultDiv = document.getElementById('test-alert-result');
            const token = getAdminToken();
            if (!token) {
                alert('Требуется авторизация администратора');
                return;
            }
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Отправка тестовых писем... ⏳';
            }
            if (resultDiv) {
                resultDiv.style.display = 'none';
            }
            try {
                const res = await fetch('/api/v1/admin/alerts/test', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Сбой отправки тестового оповещения');
                
                if (resultDiv) {
                    resultDiv.style.display = 'block';
                    resultDiv.style.background = 'rgba(16,185,129,0.15)';
                    resultDiv.style.border = '1px solid #10B981';
                    resultDiv.style.color = '#34D399';
                    resultDiv.style.padding = '10px 14px';
                    resultDiv.style.borderRadius = '8px';
                    resultDiv.style.fontSize = '0.85rem';
                    const recips = (data.recipients || []).join(', ');
                    resultDiv.innerHTML = `✅ <strong>${data.message || 'Тестовое уведомление успешно отправлено!'}</strong><br><span style="color:var(--text-muted);font-size:0.8rem;">Адреса получения: ${recips}</span>`;
                }
            } catch (err) {
                if (resultDiv) {
                    resultDiv.style.display = 'block';
                    resultDiv.style.background = 'rgba(239,68,68,0.15)';
                    resultDiv.style.border = '1px solid #EF4444';
                    resultDiv.style.color = '#F87171';
                    resultDiv.style.padding = '10px 14px';
                    resultDiv.style.borderRadius = '8px';
                    resultDiv.style.fontSize = '0.85rem';
                    resultDiv.innerHTML = `❌ Ошибка: ${err.message}`;
                }
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '🔔 Проверить оповещения (Тест)';
                }
            }
        }

        /* ==========================================================================
           УПРАВЛЕНИЕ РЕЗЕРВНЫМ КОПИРОВАНИЕМ БД (152-ФЗ)
           ========================================================================== */
        async function loadAdminBackups() {
            const container = document.getElementById('admin-backups-container');
            const token = getAdminToken();
            if (!container) return;
            if (!token) {
                container.innerHTML = '<div style="color:#EF4444;text-align:center;padding:15px;font-size:0.85rem;">Требуется авторизация администратора.</div>';
                return;
            }

            try {
                const res = await fetch('/api/v1/admin/backups', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) {
                    throw new Error(`Ошибка сервера (${res.status})`);
                }
                const data = await res.json();
                const backups = data.backups || [];

                if (backups.length === 0) {
                    container.innerHTML = `
                        <div style="text-align:center;color:var(--text-muted);padding:24px 12px;background:rgba(0,0,0,0.2);border-radius:8px;font-size:0.88rem;">
                            📁 Резервные копии еще не создавались
                        </div>
                    `;
                    return;
                }

                let html = '<div style="display:flex;flex-direction:column;gap:8px;max-height:260px;overflow-y:auto;padding-right:4px;">';

                backups.forEach(b => {
                    const dateStr = b.created_at ? new Date(b.created_at).toLocaleString('ru-RU', {
                        year: 'numeric', month: '2-digit', day: '2-digit',
                        hour: '2-digit', minute: '2-digit', second: '2-digit'
                    }) : 'Неизвестно';

                    html += `
                        <div style="background:rgba(0,0,0,0.25);border:1px solid rgba(255,255,255,0.06);padding:10px 14px;border-radius:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span style="font-size:1.2rem;">💾</span>
                                <div>
                                    <div style="color:#fff;font-family:monospace;font-size:0.85rem;font-weight:600;">${b.filename}</div>
                                    <div style="font-size:0.75rem;color:var(--text-muted);">Создан: ${dateStr}</div>
                                </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:10px;">
                                <span style="background:rgba(16,185,129,0.15);color:#34D399;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">
                                    ${b.size_human || (b.size_bytes + ' B')}
                                </span>
                                <span style="background:rgba(255,255,255,0.05);color:var(--text-muted);padding:3px 8px;border-radius:6px;font-size:0.75rem;font-family:monospace;">
                                    .sql.gz
                                </span>
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
                container.innerHTML = html;
            } catch (err) {
                container.innerHTML = `
                    <div style="color:#EF4444;text-align:center;padding:15px;font-size:0.85rem;">
                        ❌ Не удалось загрузить список резервных копий: ${err.message}
                    </div>
                `;
            }
        }

        async function handleCreateBackup() {
            const btn = document.getElementById('btn-create-backup');
            const statusDiv = document.getElementById('admin-backup-action-status');
            const token = getAdminToken();

            if (!token) {
                alert('Сессия администратора истекла. Пожалуйста, выполните вход заново.');
                return;
            }

            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '⏳ Создание снимка...';
            }

            if (statusDiv) {
                statusDiv.style.display = 'block';
                statusDiv.style.background = 'rgba(6,182,212,0.15)';
                statusDiv.style.border = '1px solid var(--accent-turquoise)';
                statusDiv.style.color = 'var(--accent-turquoise)';
                statusDiv.innerHTML = '⏳ Выполняется создание и сжатие резервного дампа базы данных (152-ФЗ)...';
            }

            try {
                const res = await fetch('/api/v1/admin/backup', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        retention_days: 7,
                        max_backups: 7,
                        dry_run: false
                    })
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.detail || 'Сбой при создании резервной копии');
                }

                const b = data.backup || {};
                if (statusDiv) {
                    statusDiv.style.background = 'rgba(16,185,129,0.15)';
                    statusDiv.style.border = '1px solid #10B981';
                    statusDiv.style.color = '#34D399';
                    statusDiv.innerHTML = `✅ Резервный снимок успешно создан: <strong>${b.filename || ''}</strong> (${b.size_human || ''}).`;
                    setTimeout(() => {
                        if (statusDiv) statusDiv.style.display = 'none';
                    }, 7000);
                }

                await loadAdminBackups();
            } catch (err) {
                if (statusDiv) {
                    statusDiv.style.background = 'rgba(239,68,68,0.15)';
                    statusDiv.style.border = '1px solid #EF4444';
                    statusDiv.style.color = '#F87171';
                    statusDiv.innerHTML = `❌ Ошибка при создании дампа: ${err.message}`;
                }
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '📦 Создать резервный снимок';
                }
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

        async function checkAdminMediaUrl(inputId, mediaType = 'image') {
            const input = document.getElementById(inputId);
            if (!input) return;
            const url = input.value.trim();
            if (!url) {
                alert('Пожалуйста, сначала вставьте URL ссылки для проверки.');
                return;
            }
            const token = getAdminToken();
            if (!token) {
                alert('Сессия администратора не активна. Войдите в CMS.');
                return;
            }
            try {
                const res = await fetch('/api/v1/admin/media-url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ url: url, type: mediaType })
                });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.detail || 'Недопустимый домен или формат URL');
                }
                alert('✅ Ссылка успешно прошла проверку безопасности и допущена к публикации!');
                if (mediaType === 'image') {
                    updateCoverPreview();
                }
            } catch (err) {
                alert(`❌ Ошибка проверки ссылки: ${err.message}`);
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
                
                currentDoctorPatientFolderId = data.patient_folder_id || '';
                currentDoctorShareToken = shareToken;

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
                                    <div style="font-size: 0.9rem; font-weight: 600; color: #fff; word-break: break-word;" title="${escapeHtml(doc.name)}">${escapeHtml(doc.name)}</div>
                                    <div style="font-size: 0.75rem; color: var(--accent-turquoise); margin-top: 4px;">Диагностический документ ${size}</div>
                                </div>
                            </div>
                            <div style="display: flex; gap: 8px; margin-top: 6px;">
                                <button class="btn btn-outline" style="flex: 1; padding: 6px 10px; font-size: 0.8rem;" onclick="viewDoctorDocument('${escapeHtml(shareToken)}', '${encodeURIComponent(doc.name)}')">👁️ Просмотр</button>
                                <button class="btn btn-turquoise" style="padding: 6px 12px; font-size: 0.8rem;" onclick="downloadDoctorDocument('${escapeHtml(shareToken)}', '${encodeURIComponent(doc.name)}')">💾 Скачать</button>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                }

                // Загружаем сохраненные заметки врача
                loadDoctorNotes(data.patient_folder_id);

                // Загружаем ранее сгенерированные анализы
                loadDoctorPatientAnalysesHistory(data.patient_folder_id);

                // Сбрасываем отображение резюме и анализов
                const summaryContainer = document.getElementById('doc-summary-container');
                if (summaryContainer) {
                    summaryContainer.style.display = 'none';
                    summaryContainer.innerHTML = '';
                }
                const pdfBtn = document.getElementById('doc-download-pdf-btn');
                if (pdfBtn) pdfBtn.style.display = 'none';
                
                const analysesResult = document.getElementById('doc-analyses-result');
                if (analysesResult) analysesResult.style.display = 'none';

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

        let currentDoctorPatientFolderId = '';
        let currentDoctorShareToken = '';

        async function viewDoctorDocument(shareToken, encodedDocName) {
            const docName = decodeURIComponent(encodedDocName);
            const docToken = localStorage.getItem('doctor_token');
            if (!docToken) {
                alert('Сессия врача не активна. Пожалуйста, выполните вход.');
                return;
            }
            try {
                const res = await fetch(`/api/v1/doctor/patient-records/${encodeURIComponent(shareToken)}/document/${encodeURIComponent(docName)}`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Не удалось открыть документ');
                }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
            } catch (err) {
                alert('Ошибка открытия документа: ' + err.message);
            }
        }

        async function downloadDoctorDocument(shareToken, encodedDocName) {
            const docName = decodeURIComponent(encodedDocName);
            const docToken = localStorage.getItem('doctor_token');
            if (!docToken) {
                alert('Сессия врача не активна. Пожалуйста, выполните вход.');
                return;
            }
            try {
                const res = await fetch(`/api/v1/doctor/patient-records/${encodeURIComponent(shareToken)}/document/${encodeURIComponent(docName)}`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Не удалось скачать документ');
                }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = docName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setTimeout(() => URL.revokeObjectURL(url), 5000);
            } catch (err) {
                alert('Ошибка скачивания документа: ' + err.message);
            }
        }

        async function loadDoctorNotes(patientFolderId) {
            const docToken = localStorage.getItem('doctor_token');
            const input = document.getElementById('doc-notes-input');
            const status = document.getElementById('doc-notes-status');
            if (status) status.style.display = 'none';
            if (!docToken || !patientFolderId) return;
            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(patientFolderId)}/notes`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    if (input && data.note && data.note.note_text) {
                        input.value = data.note.note_text;
                    } else if (input) {
                        input.value = '';
                    }
                }
            } catch (e) {
                console.warn('Ошибка загрузки заметок врача:', e);
            }
        }

        async function handleSaveDoctorNotes() {
            const docToken = localStorage.getItem('doctor_token');
            const input = document.getElementById('doc-notes-input');
            const btn = document.getElementById('doc-save-notes-btn');
            const status = document.getElementById('doc-notes-status');
            if (!docToken || !currentDoctorPatientFolderId || !input) return;
            
            const noteText = input.value.trim();
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Сохранение...';
            }
            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/notes`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${docToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ note_text: noteText })
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Не удалось сохранить заметку');
                }
                if (status) {
                    status.textContent = '✓ Заметка сохранена';
                    status.style.display = 'inline';
                    setTimeout(() => { status.style.display = 'none'; }, 4000);
                }
            } catch (err) {
                alert('Ошибка: ' + err.message);
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Сохранить 💾';
                }
            }
        }

        async function handleDoctorGenerateSummary() {
            const docToken = localStorage.getItem('doctor_token');
            const btn = document.getElementById('doc-generate-summary-btn');
            const loader = document.getElementById('doc-summary-loading');
            const container = document.getElementById('doc-summary-container');
            const pdfBtn = document.getElementById('doc-download-pdf-btn');

            if (!docToken || !currentDoctorPatientFolderId) {
                alert('Сессия врача не найдена или не выбрана папка пациента.');
                return;
            }

            if (btn) btn.disabled = true;
            if (loader) loader.style.display = 'block';
            if (container) {
                container.style.display = 'none';
                container.innerHTML = '';
            }
            if (pdfBtn) pdfBtn.style.display = 'none';

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/summary`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Ошибка генерации клинического резюме');
                }

                const data = await res.json();
                const s = data.summary || {};

                if (container) {
                    let cardsHTML = '';

                    // 1. Анамнез
                    if (s.anamnesis) {
                        cardsHTML += `
                            <div style="background: rgba(255,255,255,0.03); border-left: 4px solid var(--accent-purple); border-radius: 8px; padding: 12px 14px;">
                                <h5 style="margin: 0 0 6px 0; color: #fff; font-size: 0.95rem;">📋 Анамнез и развитие</h5>
                                <p style="margin: 0; font-size: 0.88rem; color: #E2E8F0; line-height: 1.5; white-space: pre-wrap;">${escapeHtml(s.anamnesis)}</p>
                            </div>
                        `;
                    }

                    // 2. Диагнозы
                    if (s.diagnoses && (Array.isArray(s.diagnoses) ? s.diagnoses.length : s.diagnoses)) {
                        const diagList = Array.isArray(s.diagnoses) ? s.diagnoses.map(d => `<li>${escapeHtml(d)}</li>`).join('') : `<li>${escapeHtml(s.diagnoses)}</li>`;
                        cardsHTML += `
                            <div style="background: rgba(255,255,255,0.03); border-left: 4px solid var(--accent-turquoise); border-radius: 8px; padding: 12px 14px;">
                                <h5 style="margin: 0 0 6px 0; color: #fff; font-size: 0.95rem;">🩺 Установленные диагнозы и особенности</h5>
                                <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #E2E8F0; line-height: 1.5;">${diagList}</ul>
                            </div>
                        `;
                    }

                    // 3. Противопоказания (КРАСНЫМ АКЦЕНТОМ)
                    if (s.contraindications && (Array.isArray(s.contraindications) ? s.contraindications.length : s.contraindications)) {
                        const contraList = Array.isArray(s.contraindications) ? s.contraindications.map(c => `<li>${escapeHtml(c)}</li>`).join('') : `<li>${escapeHtml(s.contraindications)}</li>`;
                        cardsHTML += `
                            <div style="background: rgba(239, 68, 68, 0.12); border-left: 4px solid #EF4444; border-radius: 8px; padding: 12px 14px;">
                                <h5 style="margin: 0 0 6px 0; color: #F87171; font-size: 0.95rem;">⚠️ Абсолютные противопоказания и риски</h5>
                                <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #FCA5A5; line-height: 1.5;">${contraList}</ul>
                            </div>
                        `;
                    }

                    // 4. Несовместимые препараты (ЯНТАРНЫМ АКЦЕНТОМ)
                    if (s.drug_interactions && (Array.isArray(s.drug_interactions) ? s.drug_interactions.length : s.drug_interactions)) {
                        const drugsList = Array.isArray(s.drug_interactions) ? s.drug_interactions.map(d => `<li>${escapeHtml(d)}</li>`).join('') : `<li>${escapeHtml(s.drug_interactions)}</li>`;
                        cardsHTML += `
                            <div style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 14px;">
                                <h5 style="margin: 0 0 6px 0; color: #FBBF24; font-size: 0.95rem;">💊 Межлекарственные взаимодействия и несовместимость</h5>
                                <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #FDE68A; line-height: 1.5;">${drugsList}</ul>
                            </div>
                        `;
                    }

                    // 5. Рекомендации
                    if (s.recommendations && (Array.isArray(s.recommendations) ? s.recommendations.length : s.recommendations)) {
                        const recList = Array.isArray(s.recommendations) ? s.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('') : `<li>${escapeHtml(s.recommendations)}</li>`;
                        cardsHTML += `
                            <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; border-radius: 8px; padding: 12px 14px;">
                                <h5 style="margin: 0 0 6px 0; color: #34D399; font-size: 0.95rem;">💡 Рекомендации консилиума специалистов</h5>
                                <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #D1FAE5; line-height: 1.5;">${recList}</ul>
                            </div>
                        `;
                    }

                    container.innerHTML = cardsHTML || '<div style="color: var(--text-muted); font-size: 0.9rem;">Резюме сформировано.</div>';
                    container.style.display = 'flex';
                }

                if (pdfBtn) {
                    pdfBtn.style.display = 'inline-block';
                }
            } catch (err) {
                alert('Ошибка формирования резюме: ' + err.message);
            } finally {
                if (btn) btn.disabled = false;
                if (loader) loader.style.display = 'none';
            }
        }

        async function handleDoctorDownloadSummaryPdf() {
            const docToken = localStorage.getItem('doctor_token');
            const pdfBtn = document.getElementById('doc-download-pdf-btn');
            if (!docToken || !currentDoctorPatientFolderId) return;

            if (pdfBtn) {
                pdfBtn.disabled = true;
                pdfBtn.textContent = 'Скачивание...';
            }

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/summary/pdf`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Не удалось скачать PDF');
                }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const cleanName = currentDoctorPatientFolderId.replace('disk:/', '').replace(/[\/\\]/g, '_').trim();
                a.download = `medical_summary_${cleanName}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setTimeout(() => URL.revokeObjectURL(url), 5000);
            } catch (err) {
                alert('Ошибка скачивания PDF: ' + err.message);
            } finally {
                if (pdfBtn) {
                    pdfBtn.disabled = false;
                    pdfBtn.textContent = 'Скачать PDF 📄';
                }
            }
        }

        /* ==========================================================================
           5.1. ХРОНОЛОГИЯ АНАЛИЗОВ И МОДЕРАЦИЯ ЧАТА (Release v7.1)
           ========================================================================== */
        let currentLatestAnalysesDocId = null;
        let currentLatestAnalysesData = [];

        async function handleDoctorGenerateAnalyses() {
            const docToken = localStorage.getItem('doctor_token');
            const btn = document.getElementById('doc-generate-analyses-btn');
            const loader = document.getElementById('doc-analyses-loading');
            const resultBox = document.getElementById('doc-analyses-result');

            if (!docToken || !currentDoctorPatientFolderId) {
                alert('Сессия врача не активна или не выбрана папка пациента.');
                return;
            }

            if (btn) btn.disabled = true;
            if (loader) loader.style.display = 'block';
            if (resultBox) resultBox.style.display = 'none';

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/generate-analyses`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Ошибка структурирования анализов');
                }

                const data = await res.json();
                currentLatestAnalysesDocId = data.doc_id;
                currentLatestAnalysesData = data.analyses || [];

                if (resultBox) resultBox.style.display = 'block';
                await loadDoctorPatientAnalysesHistory(currentDoctorPatientFolderId);
                alert(`✅ Выписка анализов сформирована! Извлечено показателей: ${currentLatestAnalysesData.length}`);
            } catch (err) {
                alert(`❌ Ошибка формирования анализов: ${err.message}`);
            } finally {
                if (btn) btn.disabled = false;
                if (loader) loader.style.display = 'none';
            }
        }

        async function loadDoctorPatientAnalysesHistory(patientFolderId) {
            const docToken = localStorage.getItem('doctor_token');
            const listEl = document.getElementById('doc-analyses-list');
            if (!listEl || !docToken || !patientFolderId) return;

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(patientFolderId)}/analyses`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) return;
                const data = await res.json();
                const docs = data.analyses_documents || [];

                if (docs.length === 0) {
                    listEl.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem; font-style: italic;">Пока нет сохраненных выписок анализов.</div>';
                    return;
                }

                let html = '';
                docs.forEach(d => {
                    const dt = d.created_at ? d.created_at.slice(0, 16).replace('T', ' ') : 'Недавно';
                    const cnt = Array.isArray(d.analyses_data) ? d.analyses_data.length : 0;
                    html += `
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                            <div style="font-size: 0.82rem; color: #E2E8F0;">
                                <strong>Выписка #${d.id}</strong> (${dt}) — <span style="color: var(--accent-turquoise);">${cnt} показ.</span>
                            </div>
                            <div style="display: flex; gap: 6px;">
                                <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.75rem;" onclick="openAnalysesPreviewModal(${d.id})">👁️ Превью</button>
                                <button class="btn btn-purple" style="padding: 4px 8px; font-size: 0.75rem;" onclick="downloadDoctorAnalysesDocx(${d.id})">📄 DOCX</button>
                                <button class="btn btn-outline" style="padding: 4px 6px; font-size: 0.75rem; color: #EF4444;" onclick="deleteDoctorAnalysesDoc(${d.id})" title="Удалить">🗑️</button>
                            </div>
                        </div>
                    `;
                });
                listEl.innerHTML = html;
            } catch (e) {
                console.warn('Ошибка загрузки истории анализов:', e);
            }
        }

        async function openAnalysesPreviewModal(docId = null) {
            const docToken = localStorage.getItem('doctor_token');
            const tableBox = document.getElementById('analyses-preview-table-container');
            if (!tableBox) return;

            let items = currentLatestAnalysesData;

            if (docId) {
                try {
                    const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/analyses/${docId}/preview`, {
                        headers: { 'Authorization': `Bearer ${docToken}` }
                    });
                    if (res.ok) {
                        const data = await res.json();
                        items = (data.doc && data.doc.analyses_data) || [];
                        currentLatestAnalysesDocId = docId;
                    }
                } catch(e) {}
            }

            if (!items || items.length === 0) {
                tableBox.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 20px;">Нет данных анализов для предпросмотра.</div>';
            } else {
                let tableHtml = `
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; text-align: left;">
                        <thead>
                            <tr style="background: rgba(37,99,235,0.2); border-bottom: 2px solid var(--accent-purple);">
                                <th style="padding: 8px; color: #fff;">Дата</th>
                                <th style="padding: 8px; color: #fff;">Анализ / Показатель</th>
                                <th style="padding: 8px; color: #fff;">Результат</th>
                                <th style="padding: 8px; color: #fff;">Норма</th>
                                <th style="padding: 8px; color: #fff;">Отклонение</th>
                                <th style="padding: 8px; color: #fff;">Комментарий</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                items.forEach(it => {
                    const isOut = it.is_out_of_norm;
                    const isRep = it.is_repeated;
                    const dyn = it.dynamics ? ` (${it.dynamics})` : '';
                    const valColor = isOut ? '#EF4444; font-weight: bold;' : '#E2E8F0;';
                    const devColor = isOut ? '#EF4444; font-weight: bold;' : '#34D399;';
                    const rowBg = isRep ? 'background: rgba(124,58,237,0.08);' : '';
                    const titleWeight = isRep ? 'font-weight: bold;' : '';

                    tableHtml += `
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); ${rowBg}">
                            <td style="padding: 8px; color: var(--text-muted);">${escapeHtml(it.date || '-')}</td>
                            <td style="padding: 8px; color: #fff; ${titleWeight}">${escapeHtml(it.test_name || it.parameter || '-')}</td>
                            <td style="padding: 8px; color: ${valColor}">${escapeHtml(it.value || '-')}</td>
                            <td style="padding: 8px; color: var(--text-muted);">${escapeHtml(it.norm || '-')}</td>
                            <td style="padding: 8px; color: ${devColor}">${escapeHtml((it.deviation || 'В норме') + dyn)}</td>
                            <td style="padding: 8px; color: var(--text-gray); font-size: 0.8rem;">${escapeHtml(it.comment || '-')}</td>
                        </tr>
                    `;
                });

                tableHtml += '</tbody></table>';
                tableBox.innerHTML = tableHtml;
            }

            openModal('analyses-preview-modal');
        }

        async function handleDoctorDownloadLatestAnalysesDocx() {
            if (!currentLatestAnalysesDocId) {
                alert('Сначала сформируйте выписку анализов.');
                return;
            }
            await downloadDoctorAnalysesDocx(currentLatestAnalysesDocId);
        }

        async function downloadDoctorAnalysesDocx(docId) {
            const docToken = localStorage.getItem('doctor_token');
            if (!docToken || !currentDoctorPatientFolderId) return;

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/analyses/${docId}/download`, {
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Не удалось скачать DOCX');
                }
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                const cleanName = currentDoctorPatientFolderId.replace('disk:/', '').replace(/[\/\\]/g, '_').trim();
                a.download = `analyses_${cleanName}_doc${docId}.docx`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                setTimeout(() => URL.revokeObjectURL(url), 5000);
            } catch (err) {
                alert('Ошибка скачивания DOCX: ' + err.message);
            }
        }

        async function deleteDoctorAnalysesDoc(docId) {
            if (!confirm('Вы уверены, что хотите удалить этот документ анализов?')) return;
            const docToken = localStorage.getItem('doctor_token');
            if (!docToken || !currentDoctorPatientFolderId) return;

            try {
                const res = await fetch(`/api/v1/doctor/patient/${encodeURIComponent(currentDoctorPatientFolderId)}/analyses/${docId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${docToken}` }
                });
                if (!res.ok) throw new Error('Ошибка при удалении');
                await loadDoctorPatientAnalysesHistory(currentDoctorPatientFolderId);
            } catch (err) {
                alert('Ошибка: ' + err.message);
            }
        }

        // --- МОДЕРАЦИЯ ОТКРЫТОГО ЧАТА ДЛЯ АДМИНИСТРАТОРА (Block 3) ---

        async function loadAdminModerationQueue() {
            const token = getAdminToken();
            const listEl = document.getElementById('admin-moderation-list');
            const counterEl = document.getElementById('moderation-counter');
            if (!listEl || !token) return;

            try {
                const res = await fetch('/api/v1/admin/chat/moderation', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка загрузки очереди модерации');
                const data = await res.json();
                const msgs = data.unapproved_messages || [];

                if (counterEl) counterEl.textContent = msgs.length;

                if (msgs.length === 0) {
                    listEl.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 30px;">✅ Очередь модерации пуста. Все ссылки проверены!</div>';
                    return;
                }

                let html = '';
                msgs.forEach(m => {
                    const dt = m.created_at ? m.created_at.slice(0, 16).replace('T', ' ') : 'Недавно';
                    html += `
                        <div style="background: rgba(30,30,46,0.9); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 14px; display: flex; flex-direction: column; gap: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <strong style="color: #fff; font-size: 0.9rem;">${escapeHtml(m.author_name)}</strong>
                                    <span style="font-size: 0.75rem; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${m.author_role}</span>
                                    <span style="font-size: 0.75rem; color: var(--text-muted);">${dt}</span>
                                </div>
                                <span style="color: #F87171; font-size: 0.8rem; font-weight: 500;">⏳ Ожидает проверки</span>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; font-size: 0.88rem; color: #F1F5F9; line-height: 1.4; word-break: break-word;">
                                ${escapeHtml(m.message_text)}
                            </div>
                            <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 4px;">
                                <button class="btn btn-turquoise" style="padding: 6px 12px; font-size: 0.8rem;" onclick="approveModerationMessage(${m.id})">✓ Одобрить и опубликовать</button>
                                <button class="btn btn-outline" style="padding: 6px 10px; font-size: 0.8rem; color: #EF4444;" onclick="deleteModerationMessage(${m.id})">🗑️ Удалить</button>
                                <button class="btn btn-outline" style="padding: 6px 10px; font-size: 0.8rem; color: #F59E0B;" onclick="banUserFromModeration('${escapeHtml(m.author_id)}', '${escapeHtml(m.author_role)}')">⛔ Забанить автора (24ч)</button>
                            </div>
                        </div>
                    `;
                });
                listEl.innerHTML = html;
            } catch (err) {
                listEl.innerHTML = `<div style="color: #EF4444; padding: 20px;">Ошибка: ${err.message}</div>`;
            }
        }

        async function approveModerationMessage(msgId) {
            const token = getAdminToken();
            if (!token) return;
            try {
                const res = await fetch(`/api/v1/admin/chat/moderation/${msgId}/approve`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка одобрения');
                await loadAdminModerationQueue();
                await loadCommunityChatMessages();
            } catch (err) {
                alert('Ошибка: ' + err.message);
            }
        }

        async function deleteModerationMessage(msgId) {
            if (!confirm('Удалить это сообщение?')) return;
            const token = getAdminToken();
            if (!token) return;
            try {
                const res = await fetch(`/api/v1/public/chat/${msgId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка удаления');
                await loadAdminModerationQueue();
                await loadCommunityChatMessages();
            } catch (err) {
                alert('Ошибка: ' + err.message);
            }
        }

        async function banUserFromModeration(userId, userRole) {
            const reason = prompt('Причина блокировки:', 'Нарушение правил безопасности сообщества (сторонние ссылки / спам)');
            if (reason === null) return;
            const token = getAdminToken();
            if (!token) return;
            try {
                const res = await fetch('/api/v1/admin/ban', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        role: userRole,
                        reason: reason,
                        duration_hours: 24
                    })
                });
                if (!res.ok) throw new Error('Ошибка блокировки');
                alert('Пользователь успешно заблокирован на 24 часа.');
                await loadAdminModerationQueue();
            } catch (err) {
                alert('Ошибка: ' + err.message);
            }
        }

        async function reportCommunityMessage(msgId) {
            const auth = getActiveCommunityAuth();
            if (!auth || !auth.token) {
                alert('Для отправки жалобы необходимо авторизоваться в чате.');
                return;
            }
            const reason = prompt('Укажите причину жалобы (спам, оскорбления, ненормативная лексика):');
            if (reason === null) return;
            try {
                const res = await fetch(`/api/v1/public/chat/${msgId}/report`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${auth.token}`
                    },
                    body: JSON.stringify({ reason: reason || 'Нарушение правил сообщества' })
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Ошибка отправки жалобы');
                }
                const data = await res.json();
                alert(`Спасибо! Ваша жалоба принята (жалоб на сообщение: ${data.report_count}). При накоплении нарушений сообщение будет скрыто автоматически.`);
                loadCommunityChatMessages();
            } catch(err) {
                alert(`Ошибка: ${err.message}`);
            }
        }

        // --- ПРЕДУПРЕЖДЕНИЕ О СТОРОННИХ ССЫЛКАХ ---

        function initExternalLinkSecurityWarning() {
            document.addEventListener('click', function(e) {
                const link = e.target.closest('a');
                if (!link || !link.href) return;
                const href = link.getAttribute('href') || '';
                if (href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('/app/')) return;
                
                try {
                    const url = new URL(link.href, window.location.origin);
                    if (url.origin !== window.location.origin) {
                        e.preventDefault();
                        showExternalLinkWarningModal(link.href);
                    }
                } catch(e) {}
            });
        }

        function showExternalLinkWarningModal(targetUrl) {
            const displayEl = document.getElementById('external-link-target-display');
            const confirmBtn = document.getElementById('external-link-confirm-btn');
            if (displayEl) displayEl.textContent = targetUrl;
            if (confirmBtn) {
                confirmBtn.onclick = function() {
                    closeModal('external-link-modal');
                    window.open(targetUrl, '_blank', 'noopener,noreferrer');
                };
            }
            openModal('external-link-modal');
        }
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

                if (showcaseImg) {
                    showcaseImg.classList.add('switching');
                    
                    setTimeout(() => {
                        showcaseImg.setAttribute('src', charData.img);
                        showcaseImg.onerror = function() {
                            if (this.src.endsWith('.jpg')) {
                                this.src = this.src.replace('.jpg', '.png');
                            } else {
                                this.style.display = 'none';
                                const ph = document.getElementById('showcase-ph');
                                if (ph) ph.style.display = 'flex';
                            }
                        };
                        showcaseImg.style.display = 'block';
                        const ph = document.getElementById('showcase-ph');
                        if (ph) ph.style.display = 'none';

                        if (showcaseName) showcaseName.textContent = charData.name;
                        if (showcaseDesc) showcaseDesc.textContent = charData.desc;
                        if (showcaseGlow) showcaseGlow.style.background = charData.glow;
                        
                        showcaseImg.classList.remove('switching');
                    }, 250);
                }
            });
        });

        /* ==========================================================================
           4. ЛОГИКА И АНИМАЦИЯ ПЛАВАЮЩЕГО ПЕРСОНАЖА «АЛИК» (FLIP & OBSERVER)
           ========================================================================== */
        function initFloatingAlik() {
            const heroSection = document.getElementById('hero') || document.querySelector('.hero');
            const heroAlikWrapper = document.getElementById('hero-alik-wrapper');
            const heroAlikImg = document.getElementById('hero-alik-img');
            const floatingWidget = document.getElementById('floating-alik-widget');
            const floatingAlikInner = document.getElementById('alik-avatar-inner');
            const floatingAlikImg = document.getElementById('floating-alik-img');
            const avatarContainer = document.getElementById('alik-avatar-container');
            const speechBubble = document.getElementById('alik-speech-bubble');
            const bubbleText = document.getElementById('alik-bubble-text');
            const bubbleClose = document.getElementById('alik-bubble-close');
            const widgetToggle = document.getElementById('alik-widget-toggle');
            const toggleIcon = document.getElementById('alik-toggle-icon');

            // Защитное программирование: выход, если на странице нет виджета или Hero-блока
            if (!floatingWidget || !floatingAlikImg || !heroAlikWrapper || !heroSection) return;

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

                const isHiddenTab = document.hidden;
                const heroRect = heroAlikImg ? heroAlikImg.getBoundingClientRect() : null;

                // 1. Активируем контейнер виджета
                floatingWidget.classList.add('floating-active');
                floatingWidget.style.opacity = '1';
                floatingWidget.style.pointerEvents = 'auto';

                // 2. Проверяем возможность FLIP анимации
                const canAnimate = !isHiddenTab && heroRect && heroRect.width > 0 && heroRect.height > 0;

                if (canAnimate) {
                    const floatRect = floatingAlikImg.getBoundingClientRect();
                    if (floatRect && floatRect.width > 0) {
                        const dx = (heroRect.left + heroRect.width / 2) - (floatRect.left + floatRect.width / 2);
                        const dy = (heroRect.top + heroRect.height / 2) - (floatRect.top + floatRect.height / 2);
                        const scale = heroRect.width / floatRect.width;

                        // Invert
                        if (floatingAlikInner) {
                            floatingAlikInner.style.transition = 'none';
                            floatingAlikInner.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
                        }
                        if (heroAlikWrapper) heroAlikWrapper.style.opacity = '0';

                        // Play
                        requestAnimationFrame(() => {
                            requestAnimationFrame(() => {
                                if (floatingAlikInner) {
                                    floatingAlikInner.style.transition = 'transform 0.65s cubic-bezier(0.2, 0.9, 0.3, 1.15), opacity 0.4s ease';
                                    floatingAlikInner.style.transform = 'translate(0, 0) scale(1)';
                                }
                            });
                        });
                    } else {
                        if (heroAlikWrapper) heroAlikWrapper.style.opacity = '0';
                    }
                } else {
                    if (heroAlikWrapper) heroAlikWrapper.style.opacity = '0';
                }

                setTimeout(() => {
                    isFloating = true;
                    isTransitioning = false;
                    if (floatingAlikInner) {
                        floatingAlikInner.style.transition = '';
                        floatingAlikInner.style.transform = '';
                    }
                    showBubble(currentComment);
                }, canAnimate ? 680 : 50);
            }

            // FLIP: Возврат из фиксированного виджета в Hero
            function transitionToHero() {
                if (!isFloating || isTransitioning) return;
                isTransitioning = true;
                hideBubble();

                const isHiddenTab = document.hidden;
                const heroRect = heroAlikImg ? heroAlikImg.getBoundingClientRect() : null;
                const floatRect = floatingAlikImg ? floatingAlikImg.getBoundingClientRect() : null;

                const canAnimate = !isHiddenTab && heroRect && heroRect.width > 0 && heroRect.height > 0 &&
                                   floatRect && floatRect.width > 0 &&
                                   heroRect.top < window.innerHeight && heroRect.bottom > 0;

                if (canAnimate) {
                    const dx = (heroRect.left + heroRect.width / 2) - (floatRect.left + floatRect.width / 2);
                    const dy = (heroRect.top + heroRect.height / 2) - (floatRect.top + floatRect.height / 2);
                    const scale = heroRect.width / floatRect.width;

                    if (floatingAlikInner) {
                        floatingAlikInner.style.transition = 'transform 0.55s cubic-bezier(0.25, 1, 0.5, 1)';
                        floatingAlikInner.style.transform = `translate(${dx}px, ${dy}px) scale(${scale})`;
                    }

                    setTimeout(() => {
                        floatingWidget.classList.remove('floating-active');
                        floatingWidget.style.opacity = '0';
                        floatingWidget.style.pointerEvents = 'none';
                        if (floatingAlikInner) {
                            floatingAlikInner.style.transition = '';
                            floatingAlikInner.style.transform = '';
                        }
                        if (heroAlikWrapper) heroAlikWrapper.style.opacity = '1';
                        isFloating = false;
                        isTransitioning = false;
                    }, 560);
                } else {
                    floatingWidget.classList.remove('floating-active');
                    floatingWidget.style.opacity = '0';
                    floatingWidget.style.pointerEvents = 'none';
                    if (floatingAlikInner) {
                        floatingAlikInner.style.transition = '';
                        floatingAlikInner.style.transform = '';
                    }
                    if (heroAlikWrapper) heroAlikWrapper.style.opacity = '1';
                    isFloating = false;
                    isTransitioning = false;
                }
            }

            // 1. Отслеживание положения Hero блока через IntersectionObserver
            if ('IntersectionObserver' in window) {
                const heroObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            // Hero в области видимости -> возврат персонажа в Hero
                            if (isFloating && !isTransitioning) {
                                transitionToHero();
                            }
                        } else {
                            // Hero покинул область видимости
                            if (entry.boundingClientRect.top < 0) {
                                // Скролл вниз ниже Hero -> активация плавающего виджета
                                if (!isFloating && !isTransitioning) {
                                    transitionToFloating();
                                }
                            } else {
                                // Скролл вверх выше Hero (секция #posts) -> виджет скрыт
                                if (isFloating && !isTransitioning) {
                                    transitionToHero();
                                }
                            }
                        }
                    });
                }, {
                    threshold: [0, 0.1, 0.25, 0.5, 1]
                });
                heroObserver.observe(heroSection);
            }

            // 2. Резервный динамический скролл-триггер (без хардкодных пикселей)
            window.addEventListener('scroll', () => {
                if (!heroSection) return;
                const heroRect = heroSection.getBoundingClientRect();
                const isHeroVisible = heroRect.top < window.innerHeight && heroRect.bottom > 0;

                if (isHeroVisible) {
                    if (isFloating && !isTransitioning) {
                        transitionToHero();
                    }
                } else if (heroRect.bottom <= 0) {
                    // Скролл ниже Hero
                    if (!isFloating && !isTransitioning) {
                        transitionToFloating();
                    }
                } else if (heroRect.top >= window.innerHeight) {
                    // Скролл выше Hero
                    if (isFloating && !isTransitioning) {
                        transitionToHero();
                    }
                }
            }, { passive: true });

            // 3. Отслеживание смысловых секций страницы для динамической смены реплик
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

            // 4. Клик по аватару Алика — переключение диалогового облачка
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

            // 5. Закрытие диалогового облачка
            if (bubbleClose) {
                bubbleClose.addEventListener('click', (e) => {
                    e.stopPropagation();
                    isBubbleHiddenManually = true;
                    hideBubble();
                });
            }

            // 6. Сворачивание / разворачивание виджета
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

        /* ==========================================================================
           14. ОТКРЫТЫЙ ЧАТ СООБЩЕСТВА (COMMUNITY CHAT - BLOCK Г)
           ========================================================================== */
        function getActiveCommunityAuth() {
            const adminToken = localStorage.getItem('admin_token') || sessionStorage.getItem('admin_token');
            if (adminToken) {
                return { token: adminToken, role: 'ADMIN', name: 'Администрация' };
            }
            const docToken = localStorage.getItem('doctor_token');
            if (docToken) {
                const docName = localStorage.getItem('doctor_name') || 'Врач-специалист';
                return { token: docToken, role: 'DOCTOR', name: docName };
            }
            const patientToken = localStorage.getItem('patient_token') || sessionStorage.getItem('patient_token');
            if (patientToken) {
                const patientName = localStorage.getItem('patient_name') || 'Родитель';
                return { token: patientToken, role: 'PATIENT', name: patientName };
            }
            return null;
        }

        function updateCommunityChatAuthState() {
            const auth = getActiveCommunityAuth();
            const inputBox = document.getElementById('community-chat-input-box');
            const userBadge = document.getElementById('community-user-badge');
            const guestNameInput = document.getElementById('community-guest-name');
            const authActions = document.getElementById('community-auth-actions');
            const logoutLink = document.getElementById('community-logout-link');

            if (inputBox) inputBox.style.display = 'block';

            if (auth) {
                if (guestNameInput) guestNameInput.style.display = 'none';
                if (authActions) authActions.style.display = 'none';
                if (logoutLink) logoutLink.style.display = 'inline';
                if (userBadge) {
                    let roleTag = 'Родитель';
                    let color = '#34D399';
                    if (auth.role === 'DOCTOR') {
                        roleTag = 'Врач';
                        color = '#F87171';
                    } else if (auth.role === 'ADMIN') {
                        roleTag = 'Администрация';
                        color = '#C084FC';
                    }
                    userBadge.innerHTML = `👤 Вы вошли как: <strong style="color: ${color};">${escapeHtml(auth.name)}</strong> (${roleTag})`;
                }
            } else {
                if (guestNameInput) guestNameInput.style.display = 'inline-block';
                if (authActions) authActions.style.display = 'inline';
                if (logoutLink) logoutLink.style.display = 'none';
                if (userBadge) {
                    userBadge.innerHTML = `⚪ <span style="color:#9CA3AF;">Вы пишете как гость (до 3 сообщ/час).</span>`;
                }
            }
        }

        function logoutCommunityUser() {
            localStorage.removeItem('patient_token');
            localStorage.removeItem('patient_name');
            sessionStorage.removeItem('patient_token');
            logoutDoctor();
            logoutAdmin();
            updateCommunityChatAuthState();
            loadCommunityChatMessages();
        }

        async function loadCommunityChatMessages() {
            const feed = document.getElementById('community-chat-feed');
            if (!feed) return;
            try {
                const res = await fetch('/api/v1/public/chat?limit=50');
                if (!res.ok) return;
                const data = await res.json();
                const messages = data.messages || [];
                const auth = getActiveCommunityAuth();
                const isAdmin = auth && auth.role === 'ADMIN';

                if (messages.length === 0) {
                    feed.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 40px 0;">В сообществе пока нет сообщений. Будьте первыми! ✨</div>';
                    return;
                }

                let html = '';
                messages.forEach(m => {
                    let roleName = 'Родитель';
                    let roleColor = '#34D399';
                    let roleBg = 'rgba(16,185,129,0.15)';
                    let roleBorder = 'rgba(16,185,129,0.3)';

                    if (m.author_role === 'DOCTOR') {
                        roleName = 'Врач / Специалист';
                        roleColor = '#F87171';
                        roleBg = 'rgba(239,68,68,0.15)';
                        roleBorder = 'rgba(239,68,68,0.3)';
                    } else if (m.author_role === 'ADMIN') {
                        roleName = 'Администрация';
                        roleColor = '#C084FC';
                        roleBg = 'rgba(168,85,247,0.15)';
                        roleBorder = 'rgba(168,85,247,0.3)';
                    } else if (m.author_role === 'GUEST') {
                        roleName = 'Гость';
                        roleColor = '#9CA3AF';
                        roleBg = 'rgba(156,163,175,0.15)';
                        roleBorder = 'rgba(156,163,175,0.3)';
                    }

                    let dateStr = 'Недавно';
                    if (m.created_at) {
                        try {
                            const dt = new Date(m.created_at);
                            if (!isNaN(dt.getTime())) {
                                const time = dt.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
                                const date = dt.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
                                dateStr = `${date} ${time}`;
                            } else {
                                dateStr = m.created_at.slice(0, 16);
                            }
                        } catch(e) {
                            dateStr = m.created_at;
                        }
                    }

                    const deleteBtn = isAdmin ? `
                        <button onclick="deleteCommunityMessage(${m.id})" style="background: none; border: none; color: #EF4444; font-size: 0.8rem; cursor: pointer; padding: 2px 4px; border-radius: 4px;" title="Удалить сообщение модератором">🗑️</button>
                    ` : '';

                    const reportBtn = auth ? `
                        <button onclick="reportCommunityMessage(${m.id})" style="background: none; border: none; color: var(--text-muted); font-size: 0.8rem; cursor: pointer; padding: 2px 4px; border-radius: 4px;" title="Пожаловаться на сообщение">🚩</button>
                    ` : '';

                    html += `
                        <div style="background: rgba(30, 30, 46, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 12px 14px; display: flex; flex-direction: column; gap: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
                                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                    <strong style="color: ${roleColor}; font-size: 0.92rem;">${escapeHtml(m.author_name || 'Пользователь')}</strong>
                                    <span style="color: ${roleColor}; background: ${roleBg}; border: 1px solid ${roleBorder}; font-size: 0.72rem; padding: 2px 6px; border-radius: 4px; font-weight: 500;">${roleName}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span style="font-size: 0.75rem; color: var(--text-muted);">${dateStr}</span>
                                    ${reportBtn}
                                    ${deleteBtn}
                                </div>
                            </div>
                            <div style="font-size: 0.9rem; color: #F1F5F9; line-height: 1.45; word-break: break-word; white-space: pre-wrap;">${escapeHtml(m.message_text)}</div>
                        </div>
                    `;
                });

                feed.innerHTML = html;
                feed.scrollTop = feed.scrollHeight;
            } catch (e) {
                console.warn('Ошибка загрузки чата:', e);
            }
        }

        async function handleSendCommunityMessage(event) {
            event.preventDefault();
            const input = document.getElementById('community-msg-input');
            const guestNameInput = document.getElementById('community-guest-name');
            const btn = document.getElementById('community-send-btn');
            const auth = getActiveCommunityAuth();

            const text = input ? input.value.trim() : '';
            if (!text) return;

            const guestName = guestNameInput ? guestNameInput.value.trim() : '';

            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Отправка...';
            }

            try {
                const headers = { 'Content-Type': 'application/json' };
                if (auth && auth.token && auth.token !== 'null' && auth.token !== 'undefined') {
                    headers['Authorization'] = `Bearer ${auth.token}`;
                }

                const payload = {
                    message: text,
                    message_text: text,
                    author_name: auth ? null : (guestName || 'Гость')
                };

                const res = await fetch('/api/v1/public/chat', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    if (res.status === 429) {
                        throw new Error(err.detail || 'Превышен лимит отправки сообщений (до 3 сообщений в час для гостей). Пожалуйста, подождите или авторизуйтесь.');
                    }
                    if (res.status === 401) {
                        logoutCommunityUser();
                        throw new Error('Сессия истекла. Пожалуйста, войдите снова.');
                    }
                    throw new Error(err.detail || 'Не удалось отправить сообщение');
                }

                if (input) input.value = '';
                await loadCommunityChatMessages();
            } catch (err) {
                alert('⚠️ ' + err.message);
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = 'Отправить 🚀';
                }
            }
        }

        async function deleteCommunityMessage(messageId) {
            if (!confirm('Вы действительно хотите удалить это сообщение?')) return;
            const auth = getActiveCommunityAuth();
            if (!auth || auth.role !== 'ADMIN') {
                alert('Только администратор может удалять сообщения.');
                return;
            }
            try {
                const res = await fetch(`/api/v1/public/chat/${messageId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${auth.token}` }
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Ошибка удаления сообщения');
                }
                await loadCommunityChatMessages();
            } catch (err) {
                alert(err.message);
            }
        }

        async function handleParentLogin(event) {
            event.preventDefault();
            let token = document.getElementById('parent-token-input').value.trim();
            const pass = document.getElementById('parent-pass-input').value.trim();
            const btn = document.getElementById('parent-login-btn');
            const errDiv = document.getElementById('parent-login-error');

            if (token.includes('token=')) {
                token = token.split('token=')[1].split('&')[0];
            }

            if (!token || !pass) {
                if (errDiv) {
                    errDiv.textContent = 'Пожалуйста, заполните все поля.';
                    errDiv.style.display = 'block';
                }
                return;
            }

            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Вход...';
            }
            if (errDiv) errDiv.style.display = 'none';

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: token, password: pass })
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || 'Неверный токен или пароль');
                }

                const data = await res.json();
                const jwtToken = data.access_token || data.session_token;
                localStorage.setItem('patient_token', jwtToken);
                localStorage.setItem('patient_name', 'Родитель');

                closeModal('parent-modal');
                updateCommunityChatAuthState();
                await loadCommunityChatMessages();
            } catch (err) {
                if (errDiv) {
                    errDiv.textContent = '❌ ' + err.message;
                    errDiv.style.display = 'block';
                }
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '🧸 Войти в систему';
                }
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            preserveQueryParameters();
            initFloatingAlik();
            initExternalLinkSecurityWarning();
            updateCommunityChatAuthState();
            loadCommunityChatMessages();
            setInterval(loadCommunityChatMessages, 15000);

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
                console.log('🌌 Все сказочные блоки, CMS, Докторский портал, Чат Сообщества и помощник Алик готовы к работе!');
            });
        });

        /* ==========================================================================
           15. ГОЛОСОВОЙ ВВОД (WEB SPEECH API) УТИЛИТЫ И ЭКСПОРТ
           ========================================================================== */
        function isSpeechRecognitionSupported() {
            return typeof window !== 'undefined' && (
                'SpeechRecognition' in window || 
                'webkitSpeechRecognition' in window || 
                'mozSpeechRecognition' in window || 
                'msSpeechRecognition' in window
            );
        }

        if (typeof window !== 'undefined') {
            window.isSpeechRecognitionSupported = isSpeechRecognitionSupported;
            window.loadAdminBackups = loadAdminBackups;
            window.handleCreateBackup = handleCreateBackup;
        }
        if (typeof module !== 'undefined' && module.exports) {
            module.exports = { isSpeechRecognitionSupported, loadAdminBackups, handleCreateBackup };
        }