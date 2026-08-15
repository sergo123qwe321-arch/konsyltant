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
                    title: "Как помочь малышу заговорить через игру",
                    summary: "Простые и весёлые игровые техники для дома, которые запустят речь естественным образом.",
                    tags: "Развитие речи,Игры",
                    created_at: "2026-08-11"
                },
                {
                    id: 2,
                    title: "Сон ребёнка: мягкие ритуалы засыпания",
                    summary: "Как успокоить нервную систему перед сном и забыть про вечерние капризы.",
                    tags: "Сон и режим,Эмоции и поведение",
                    created_at: "2026-08-10"
                },
                {
                    id: 3,
                    title: "Игры для гиперактивных детей: разгрузка",
                    summary: "Подборка терапевтических игр для расслабления и концентрации внимания у детей.",
                    tags: "Игры,Эмоции и поведение",
                    created_at: "2026-08-08"
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

        
/* ==========================================================================
           3. API INTEGRATION & FALLBACKS
           ========================================================================== */
        let activeDemoMode = false;

        function showDemoBadge() {
            if (!activeDemoMode) {
                activeDemoMode = true;
                const badge = document.getElementById('app-demo-badge');
                if (badge) {
                    badge.innerHTML = "✨ Демонстрационный режим (данные загружены локально)";
                    badge.style.background = "linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(244, 63, 94, 0.2))";
                    badge.style.borderColor = "var(--accent-purple)";
                }
            }
        }

        async function loadData(endpoint) {
            try {
                const response = await fetch(`${BASE_API_URL}${endpoint}`);
                if (!response.ok) throw new Error(`Ошибка: ${response.status}`);
                return await response.json();
            } catch (err) {
                console.warn(`[API FETCH FAILED] Используем локальные данные для ${endpoint}`);
                showDemoBadge();
                if (endpoint.startsWith('/services')) return MOCK_DATA.services;
                if (endpoint.startsWith('/doctors')) return MOCK_DATA.doctors;
                if (endpoint.startsWith('/posts')) {
                    const url = new URL(`http://localhost${endpoint}`);
                    const tag = url.searchParams.get('tag');
                    if (tag && tag !== 'Все') {
                        return MOCK_DATA.posts.filter(p => p.tags.split(',').includes(tag));
                    }
                    return MOCK_DATA.posts;
                }
                if (endpoint.startsWith('/events')) return MOCK_DATA.events;
                return [];
            }
        }

        async function renderServices() {
            const container = document.getElementById('services-container');
            const data = await loadData('/services');
            container.innerHTML = '';
            
            data.forEach(service => {
                const icon = service.icon_name === 'brain' ? '🧠' : (service.icon || '🧚');
                container.innerHTML += `
                    <div class="card-glass service-card">
                        <div class="sticker-icon">
                            <span style="font-size: 2rem;">${icon}</span>
                        </div>
                        <h3>${service.title}</h3>
                        <p>${service.description}</p>
                        <a href="#contacts" class="read-more" onclick="document.getElementById('select-service').value='${service.title.includes('Лого') ? 'Логопедия' : (service.title.includes('Нейро') ? 'Нейропсихология' : 'Диагностика')}'">Записаться 🌸</a>
                    </div>
                `;
            });
        }

        async function renderDoctors() {
            const container = document.getElementById('doctors-container');
            const data = await loadData('/doctors');
            container.innerHTML = '';
            
            data.forEach(doc => {
                const avatar = doc.avatar_url ? `<img class="doctor-avatar" src="${doc.avatar_url}" alt="${doc.full_name}" onerror="this.outerHTML='<span style=\\'font-size:4rem;\\'>${doc.avatar || '👩‍⚕️'}</span>'">` : `<span style="font-size: 4rem;">${doc.avatar || '👩‍⚕️'}</span>`;
                container.innerHTML += `
                    <div class="card-glass doctor-card">
                        <div class="doctor-avatar-wrapper">
                            ${avatar}
                        </div>
                        <h4 class="doctor-name">${doc.full_name}</h4>
                        <div class="doctor-spec">${doc.specialization}</div>
                        <div class="doctor-exp">Стаж работы: ${doc.experience_years} лет</div>
                        <button class="btn btn-outline" style="padding: 8px 16px; font-size: 0.85rem;" onclick="document.getElementById('select-service').value='${doc.specialization.includes('Лого') ? 'Логопедия' : 'Нейропсихология'}'; document.getElementById('user-msg').value='Запись к врачу: ${doc.full_name}'; window.location.hash='#contacts';">
                            📅 Записаться к врачу
                        </button>
                    </div>
                `;
            });
        }

        async function renderBlog(tag = 'Все') {
            const container = document.getElementById('blog-container');
            container.innerHTML = `
                <div class="card-glass blog-card skeleton-card"><div class="skeleton skeleton-img"></div><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
                <div class="card-glass blog-card skeleton-card"><div class="skeleton skeleton-img"></div><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text"></div></div>
            `;
            
            const endpoint = tag === 'Все' ? '/posts' : `/posts?tag=${encodeURIComponent(tag)}`;
            const data = await loadData(endpoint);
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">🦄 Статей пока нет, они скоро появятся!</div>`;
                return;
            }

            data.forEach(post => {
                const tagsList = post.tags ? post.tags.split(',') : ['Полезное'];
                const tagsHTML = tagsList.map(t => `<span class="blog-tag">${t}</span>`).join('');
                container.innerHTML += `
                    <div class="card-glass blog-card">
                        <div class="blog-card-img"></div>
                        <div class="blog-tags">${tagsHTML}</div>
                        <div class="blog-date">📅 ${post.created_at || 'Недавно'}</div>
                        <h3>${post.title}</h3>
                        <p>${post.summary}</p>
                        <div class="blog-card-footer">
                            <button class="read-more" onclick="alert('Полный текст статьи появится в личном кабинете родителя!')">Читать далее ✨</button>
                        </div>
                    </div>
                `;
            });
        }

        async function renderEvents() {
            const container = document.getElementById('events-container');
            const data = await loadData('/events');
            container.innerHTML = '';
            
            data.forEach(evt => {
                let day = '20', month = 'Авг';
                try {
                    const dateParts = evt.event_date.split(' ').split('-');
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
           4. ПЕРЕДАЧА QUERY ПАРАМЕТРОВ
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


        /* ==========================================================================
           5. КЛИЕНТСКИЙ ИНТЕРФЕЙС, МОБИЛЬНОЕ МЕНЮ И МОДАЛКИ
           ========================================================================== */
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
            document.getElementById(id).classList.add('open');
            document.body.style.overflow = 'hidden';
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('open');
            document.body.style.overflow = '';
        }

        document.querySelectorAll('.modal').forEach(m => {
            m.addEventListener('click', (e) => {
                if (e.target === m) closeModal(m.id);
            });
        });

        function handleFormSubmit(e) {
            e.preventDefault();
            const name = document.getElementById('user-name').value;
            const phone = document.getElementById('user-phone').value;
            const service = document.getElementById('select-service').value;
            alert(`🎉 Ура, ${name}! Ваша волшебная заявка на направление "${service}" отправлена. Мы свяжемся с вами по телефону ${phone} в течение 15 минут! ✨`);
            document.getElementById('consultation-form').reset();
        }

        document.getElementById('blog-tags-container').addEventListener('click', (e) => {
            if (e.target.classList.contains('chip')) {
                document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                renderBlog(e.target.getAttribute('data-tag'));
            }
        });

        /* Логика шоукейса персонажей Pixar */
        const showcaseImg = document.getElementById('showcase-img');
        const showcaseName = document.getElementById('showcase-name');
        const showcaseDesc = document.getElementById('showcase-desc');
        const showcaseGlow = document.getElementById('showcase-glow');
        const selectorThumbs = document.querySelectorAll('.selector-thumb');

        selectorThumbs.forEach(thumb => {
            thumb.addEventListener('mouseenter', () => {
                const charId = thumb.getAttribute('data-char');
                const charData = CHARACTERS[charId];
                if (!charData) return;

                // Play sound on hover
                let audio = new Audio(`/static/audio/sound_${charId}.mp3`);
                audio.volume = 0.5;
                audio.play().catch(e => console.log('Audio autoplay prevented'));
            });

            thumb.addEventListener('click', () => {
                const charId = thumb.getAttribute('data-char');
                const charData = CHARACTERS[charId];
                if (!charData) return;

                selectorThumbs.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');

                // Плавная анимация переключения (Pixar bounce)
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
            Promise.all([
                renderServices(),
                renderDoctors(),
                renderBlog(),
                renderEvents()
            ]).then(() => {
                console.log('🌌 Все сказочные блоки успешно загружены!');
            });
        });