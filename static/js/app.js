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
           4. ЛОГИКА И АНИМАЦИЯ ПЛАВАЮЩЕГО ПЕРСОНАЖА «АЛИК» (FLIP & SOUND SHOWCASE DOCKING)
           ========================================================================== */
        function initFloatingAlik() {
            const charactersSection = document.getElementById('characters') || document.querySelector('.characters-section');
            const dockPlaceholder = document.getElementById('alik-dock-placeholder') || document.querySelector('.alik-dock-slot');
            const dockImg = document.getElementById('alik-dock-img') || (dockPlaceholder ? dockPlaceholder.querySelector('img') : null);
            const floatingWidget = document.getElementById('floating-alik-widget');
            const floatingAlikInner = document.getElementById('alik-avatar-inner');
            const floatingAlikImg = document.getElementById('floating-alik-img');
            const avatarContainer = document.getElementById('alik-avatar-container');
            const speechBubble = document.getElementById('alik-speech-bubble');
            const bubbleText = document.getElementById('alik-bubble-text');
            const bubbleClose = document.getElementById('alik-bubble-close');
            const widgetToggle = document.getElementById('alik-widget-toggle');
            const toggleIcon = document.getElementById('alik-toggle-icon');
            const widgetClose = document.getElementById('alik-widget-close');

            // Защитное программирование: выход, если на странице нет виджета
            if (!floatingWidget || !floatingAlikImg) return;

            let isDocked = false;
            let isTransitioning = false;
            let isBubbleHiddenManually = false;
            let isMinimized = false;
            const defaultHeroComment = "Привет! Я Алик — твой проводник по Маленькой Стране! 🎸";
            let currentComment = defaultHeroComment;

            // Показ реплики в зеленом облачке
            function showBubble(text) {
                if (!speechBubble || !bubbleText || isBubbleHiddenManually || isMinimized || isDocked) return;
                if (sessionStorage.getItem('alik_closed') === '1') return;

                const cleanText = (text || currentComment || defaultHeroComment).trim();
                if (bubbleText.textContent === cleanText && speechBubble.classList.contains('visible') && !speechBubble.classList.contains('bubble-hidden')) {
                    return;
                }

                if (speechBubble.classList.contains('visible') && !speechBubble.classList.contains('bubble-hidden')) {
                    speechBubble.classList.add('updating');
                    setTimeout(() => {
                        bubbleText.textContent = cleanText;
                        speechBubble.classList.remove('updating');
                    }, 160);
                } else {
                    bubbleText.textContent = cleanText;
                    speechBubble.classList.remove('bubble-hidden');
                    speechBubble.classList.add('visible');
                }
            }

            // Скрытие реплики
            function hideBubble() {
                if (speechBubble) {
                    speechBubble.classList.remove('visible');
                    speechBubble.classList.add('bubble-hidden');
                }
            }

            // Переход в слот витрины звуков (Docking)
            function dockToSoundShowcase() {
                if (isDocked && floatingWidget.classList.contains('docked-hidden')) return;
                isTransitioning = true;
                hideBubble();

                // Скрываем плавающий виджет и убираем кликабельность
                floatingWidget.classList.remove('floating-active');
                floatingWidget.classList.add('docked-hidden');
                floatingWidget.style.opacity = '0';
                floatingWidget.style.pointerEvents = 'none';

                if (floatingAlikInner) {
                    floatingAlikInner.style.transition = '';
                    floatingAlikInner.style.transform = '';
                }

                // Активируем маскота внутри витрины звуков
                if (dockPlaceholder) {
                    dockPlaceholder.classList.add('docked');
                }

                isDocked = true;
                isTransitioning = false;
            }

            // Возврат из витрины звуков в плавающий виджет-компаньон (Undocking)
            function undockToFloating() {
                if (sessionStorage.getItem('alik_closed') === '1') {
                    if (dockPlaceholder) dockPlaceholder.classList.add('docked');
                    return;
                }

                if (!isDocked && floatingWidget.classList.contains('floating-active') && !floatingWidget.classList.contains('docked-hidden')) return;
                isTransitioning = true;

                // Освобождаем слот в витрине
                if (dockPlaceholder) {
                    dockPlaceholder.classList.remove('docked');
                }

                if (floatingAlikInner) {
                    floatingAlikInner.style.transition = '';
                    floatingAlikInner.style.transform = '';
                }

                // Активируем плавающий виджет в правом нижнем углу
                floatingWidget.classList.remove('docked-hidden');
                floatingWidget.classList.add('floating-active');
                floatingWidget.style.opacity = '1';
                floatingWidget.style.pointerEvents = 'auto';

                isDocked = false;
                isTransitioning = false;

                // Отображаем актуальный комментарий текущего блока
                showBubble(currentComment);
            }

            // Проверка закрытия виджета пользователем в текущей сессии
            if (sessionStorage.getItem('alik_closed') === '1') {
                floatingWidget.classList.add('docked-hidden');
                floatingWidget.style.display = 'none';
                floatingWidget.style.opacity = '0';
                floatingWidget.style.pointerEvents = 'none';
                if (dockPlaceholder) dockPlaceholder.classList.add('docked');
                isDocked = true;
            } else {
                // Определение начального состояния при загрузке страницы
                let initiallyInCharacters = false;
                if (charactersSection) {
                    const charRect = charactersSection.getBoundingClientRect();
                    initiallyInCharacters = charRect.top < window.innerHeight && charRect.bottom > 0;
                }

                if (initiallyInCharacters) {
                    dockToSoundShowcase();
                } else {
                    undockToFloating();
                }
            }

            // 1. Отслеживание контейнера витрины #characters через IntersectionObserver
            if ('IntersectionObserver' in window && charactersSection) {
                const charObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            dockToSoundShowcase();
                        } else {
                            undockToFloating();
                        }
                    });
                }, {
                    threshold: [0, 0.15, 0.5]
                });
                charObserver.observe(charactersSection);
            }

            // 2. Резервный динамический скролл-триггер для абсолютной надежности
            window.addEventListener('scroll', () => {
                if (!charactersSection) return;
                if (sessionStorage.getItem('alik_closed') === '1') return;

                const charRect = charactersSection.getBoundingClientRect();
                const isCharVisible = charRect.top < window.innerHeight && charRect.bottom > 0;

                if (isCharVisible) {
                    if (!isDocked && !isTransitioning) {
                        dockToSoundShowcase();
                    }
                } else {
                    if (isDocked && !isTransitioning) {
                        undockToFloating();
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
                                if (!isDocked && !isTransitioning) {
                                    showBubble(comment);
                                }
                            }
                        }
                    });
                }, {
                    rootMargin: '-15% 0px -30% 0px',
                    threshold: 0.1
                });

                document.querySelectorAll('[data-alik-comment]').forEach(sec => {
                    sectionObserver.observe(sec);
                });
            }

            // 4. Клик по аватару Алика — переключение диалогового облачка
            if (avatarContainer) {
                avatarContainer.addEventListener('click', (e) => {
                    if (e.target.closest('#alik-widget-toggle') || e.target.closest('#alik-widget-close')) return;

                    if (isMinimized) {
                        isMinimized = false;
                        floatingWidget.classList.remove('minimized');
                        if (toggleIcon) toggleIcon.textContent = '−';
                        showBubble(currentComment);
                        return;
                    }

                    if (speechBubble && speechBubble.classList.contains('visible') && !speechBubble.classList.contains('bubble-hidden')) {
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

            // 7. Полное закрытие плавающего виджета на всю сессию (sessionStorage)
            if (widgetClose) {
                widgetClose.addEventListener('click', (e) => {
                    e.stopPropagation();
                    sessionStorage.setItem('alik_closed', '1');
                    hideBubble();
                    floatingWidget.classList.remove('floating-active');
                    floatingWidget.classList.add('docked-hidden');
                    floatingWidget.style.display = 'none';
                    floatingWidget.style.opacity = '0';
                    floatingWidget.style.pointerEvents = 'none';
                    if (dockPlaceholder) {
                        dockPlaceholder.classList.add('docked');
                    }
                    isDocked = true;
                });
            }

            // 8. Интерактивный клик по слоту в витрине звуков при докинге
            if (dockPlaceholder) {
                dockPlaceholder.addEventListener('click', () => {
                    playCharSound('a');
                    dockPlaceholder.classList.add('pulse-active');
                    setTimeout(() => dockPlaceholder.classList.remove('pulse-active'), 400);
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
            localStorage.removeItem('doctor_token');
            localStorage.removeItem('doctor_id');
            localStorage.removeItem('doctor_name');
            localStorage.removeItem('doctor_specialty');
            localStorage.removeItem('admin_token');
            sessionStorage.removeItem('admin_token');
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

            // Хеши #admin / #cms больше не обрабатываются: панель CMS вынесена
            // на автономный маршрут /admin (см. templates/admin.html, static/js/admin.js).
            // share_token и кабинет врача (/doctor) обслуживаются редиректом main.py и doctor.js.

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
        }
        if (typeof module !== 'undefined' && module.exports) {
            module.exports = { isSpeechRecognitionSupported };
        }
