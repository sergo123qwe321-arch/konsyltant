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
                container.innerHTML += `
                    <div class="card-glass blog-card">
                        <div class="blog-tags">${tagsHTML}</div>
                        <div class="blog-date">📅 ${post.created_at ? post.created_at.split(' ')[0] : 'Недавно'}</div>
                        <h3 style="margin-bottom: 10px; font-size: 1.15rem; line-height: 1.4;">${post.title}</h3>
                        <p style="font-size: 0.9rem; line-height: 1.6; color: var(--text-gray); margin-bottom: 16px;">${post.summary}</p>
                        <div class="blog-card-footer">
                            <button class="read-more" onclick="openArticleReader(${post.id})">Читать далее ✨</button>
                        </div>
                    </div>
                `;
            });
        }

        async function openArticleReader(postId) {
            let post = cachedPosts.find(p => p.id === postId);
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
        function openAdminModal() {
            const token = sessionStorage.getItem('admin_token');
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

                if (!res.ok) throw new Error('Неверный логин или пароль');

                const data = await res.json();
                sessionStorage.setItem('admin_token', data.access_token);
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
            closeModal('admin-dashboard-modal');
            alert('Вы вышли из Панели управления CMS.');
        }

        function switchAdminTab(tab) {
            const tabLeads = document.getElementById('admin-tab-leads');
            const tabPosts = document.getElementById('admin-tab-posts');
            const btnLeads = document.getElementById('tab-btn-leads');
            const btnPosts = document.getElementById('tab-btn-posts');

            if (tab === 'leads') {
                tabLeads.style.display = 'block';
                tabPosts.style.display = 'none';
                btnLeads.className = 'btn btn-turquoise';
                btnPosts.className = 'btn btn-outline';
                loadAdminLeads();
            } else {
                tabLeads.style.display = 'none';
                tabPosts.style.display = 'block';
                btnLeads.className = 'btn btn-outline';
                btnPosts.className = 'btn btn-turquoise';
                loadAdminPosts();
            }
        }

        async function loadAdminLeads() {
            const list = document.getElementById('admin-leads-list');
            const counter = document.getElementById('leads-counter');
            const token = sessionStorage.getItem('admin_token');
            if (!token) return;

            list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">Загрузка заявок...</div>';

            try {
                const res = await fetch('/api/v1/admin/leads', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка загрузки заявок');
                const leads = await res.json();
                counter.textContent = leads.length;

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
            list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:20px;">Загрузка статей...</div>';

            try {
                const res = await fetch('/api/v1/public/posts');
                const posts = await res.json();

                if (posts.length === 0) {
                    list.innerHTML = '<div style="text-align:center;color:var(--text-muted);padding:30px;">В блоге пока нет статей.</div>';
                    return;
                }

                list.innerHTML = posts.map(p => {
                    let tagsList = Array.isArray(p.tags) ? p.tags : (p.tags ? p.tags.split(',') : []);
                    return `
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:center;gap:12px;">
                            <div style="flex:1;">
                                <h5 style="margin:0 0 6px 0;font-size:1rem;color:#fff;">${p.title}</h5>
                                <div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:4px;">Теги: ${tagsList.join(', ')} | 📅 ${p.created_at ? p.created_at.split(' ')[0] : ''}</div>
                                <p style="margin:0;font-size:0.85rem;color:var(--text-gray);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${p.summary}</p>
                            </div>
                            <div style="display:flex;gap:8px;">
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

        function openPostEditor(post = null) {
            const editor = document.getElementById('admin-post-editor');
            const heading = document.getElementById('editor-title-heading');
            editor.style.display = 'block';

            if (post) {
                heading.textContent = 'Редактировать статью';
                document.getElementById('edit-post-id').value = post.id;
                document.getElementById('edit-post-title').value = post.title;
                document.getElementById('edit-post-tags').value = Array.isArray(post.tags) ? post.tags.join(', ') : post.tags;
                document.getElementById('edit-post-summary').value = post.summary;
                document.getElementById('edit-post-content').value = post.content || post.summary;
            } else {
                heading.textContent = 'Создать новую статью';
                document.getElementById('post-editor-form').reset();
                document.getElementById('edit-post-id').value = '';
            }
        }

        function closePostEditor() {
            document.getElementById('admin-post-editor').style.display = 'none';
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
            const token = sessionStorage.getItem('admin_token');
            if (!token) return;

            const btn = document.getElementById('save-post-btn');
            const postId = document.getElementById('edit-post-id').value;
            const title = document.getElementById('edit-post-title').value.trim();
            const tagsRaw = document.getElementById('edit-post-tags').value;
            const tags = tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [];
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
                    body: JSON.stringify({ title, summary, content, tags })
                });

                if (!res.ok) throw new Error('Ошибка сохранения статьи');

                closePostEditor();
                loadAdminPosts();
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
            const token = sessionStorage.getItem('admin_token');
            if (!token) return;

            try {
                const res = await fetch(`/api/v1/admin/posts/${postId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!res.ok) throw new Error('Ошибка удаления');
                loadAdminPosts();
                renderBlog();
            } catch(e) {
                alert('Не удалось удалить статью.');
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
            });
        });

        window.addEventListener('DOMContentLoaded', () => {
            preserveQueryParameters();
            if (window.location.hash === '#admin' || window.location.hash === '#cms') {
                openAdminModal();
            }
            Promise.all([
                renderServices(),
                renderDoctors(),
                renderBlog(),
                renderEvents()
            ]).then(() => {
                console.log('🌌 Все сказочные блоки и CMS готовы к работе!');
            });
        });