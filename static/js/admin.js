/* ==========================================================================
   7. АВТОНАМНАЯ ПАНЕЛЬ АДМИНИСТРАТОРА (CMS) — /admin
   Изолированная копия логики из static/js/app.js (блок «ПАНЕЛЬ
   АДМИНИСТРАТОРА»). Не зависит от лендинга: локальный escapeHtml,
   экраны вместо модалок (showAdminView), автономная инициализация.
   ========================================================================== */

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getAdminToken() {
    return sessionStorage.getItem('admin_token') || localStorage.getItem('admin_token') || '';
}

/* --- Переключение экранов: login <-> dashboard --- */
function showAdminView(name) {
    const loginView = document.getElementById('admin-login-view');
    const dashboardView = document.getElementById('admin-dashboard-view');
    const userBar = document.getElementById('admin-user-bar');
    const guestBar = document.getElementById('admin-guest-bar');

    if (loginView) {
        loginView.classList.toggle('active', name === 'login');
        loginView.style.display = '';
    }
    if (dashboardView) {
        dashboardView.classList.toggle('active', name === 'dashboard');
        dashboardView.style.display = '';
    }
    if (userBar) {
        userBar.style.display = (name === 'dashboard') ? '' : 'none';
    }
    if (guestBar) {
        guestBar.style.display = (name === 'dashboard') ? 'none' : '';
    }
}

async function handleAdminLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('admin-login-btn');
    const errBox = document.getElementById('admin-login-error');
    const user = document.getElementById('admin-username').value.trim();
    const pass = document.getElementById('admin-password').value.trim();

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
        document.getElementById('admin-login-form').reset();
        showAdminView('dashboard');
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
    showAdminView('login');
    alert('Вы вышли из Панели управления CMS.');
}

/* --- Навигация по вкладкам дашборда --- */
function switchAdminTab(tab) {
    const tabs = ['leads', 'doctors', 'posts', 'ops', 'moderation'];
    tabs.forEach(t => {
        const el = document.getElementById(`admin-tab-${t}`);
        const btn = document.getElementById(`tab-btn-${t}`);
        if (el) {
            el.classList.toggle('active', t === tab);
            el.style.display = '';
        }
        if (btn) {
            btn.className = 'btn tab-btn ' + (t === tab ? 'btn-turquoise active' : 'btn-outline');
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

/* ==========================================================================
   ВКЛАДКА: ЗАЯВКИ С САЙТА
   ========================================================================== */
async function loadAdminLeads() {
    const list = document.getElementById('admin-leads-list');
    const counter = document.getElementById('leads-counter');
    const token = getAdminToken();
    if (!token) return;
    if (!list) return;

    list.innerHTML = '<div class="list-placeholder">Загрузка заявок...</div>';

    try {
        const res = await fetch('/api/v1/admin/leads', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Ошибка загрузки заявок');
        const leads = await res.json();
        if (counter) counter.textContent = leads.length;

        if (leads.length === 0) {
            list.innerHTML = '<div class="list-placeholder">Пока нет новых заявок.</div>';
            return;
        }

        list.innerHTML = leads.map(l => `
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                <div style="flex:1;">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                        <strong style="color:#fff;font-size:1rem;">${escapeHtml(l.name)}</strong>
                        <span style="background:rgba(6,182,212,0.15);color:var(--accent-turquoise);padding:2px 8px;border-radius:4px;font-size:0.75rem;">${escapeHtml(l.child_age || 'Общий вопрос')}</span>
                        <small style="color:var(--text-muted);font-size:0.8rem;">📅 ${l.created_at ? l.created_at.split('.')[0] : ''}</small>
                    </div>
                    <div style="color:var(--accent-purple);font-weight:600;font-size:0.9rem;margin-bottom:4px;">📞 ${escapeHtml(l.phone)}</div>
                    ${l.message ? `<div style="color:var(--text-gray);font-size:0.85rem;background:rgba(0,0,0,0.2);padding:8px;border-radius:6px;margin-top:6px;">${escapeHtml(l.message)}</div>` : ''}
                </div>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка: ${escapeHtml(err.message)}</div>`;
    }
}

/* ==========================================================================
   ВКЛАДКА: СПЕЦИАЛИСТЫ И ВРАЧИ
   ========================================================================== */
async function loadAdminDoctors() {
    const listDiv = document.getElementById('admin-doctors-list');
    const counter = document.getElementById('doctors-counter');
    const token = getAdminToken();
    if (!token) return;

    if (listDiv) {
        listDiv.innerHTML = '<div class="list-placeholder">Загрузка списка специалистов... ⏳</div>';
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
            listDiv.innerHTML = '<div class="list-placeholder">В базе пока нет зарегистрированных специалистов.</div>';
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

/* ==========================================================================
   ВКЛАДКА: УПРАВЛЕНИЕ БЛОГОМ
   ========================================================================== */
async function loadAdminPosts() {
    const list = document.getElementById('admin-posts-list');
    if (!list) return;
    list.innerHTML = '<div class="list-placeholder">Загрузка статей...</div>';

    try {
        const res = await fetch('/api/v1/public/posts');
        const posts = await res.json();

        if (!posts || posts.length === 0) {
            list.innerHTML = '<div class="list-placeholder">В блоге пока нет статей.</div>';
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
                            <h5 style="margin:0;font-size:1rem;color:#fff;">${escapeHtml(p.title)}</h5>
                            ${hasVideo ? '<span style="background:rgba(239,68,68,0.2);color:#F87171;padding:2px 6px;border-radius:4px;font-size:0.7rem;">🎬 Видео</span>' : ''}
                        </div>
                        <div style="font-size:0.8rem;color:var(--text-muted);margin:4px 0;">Теги: ${escapeHtml(tagsList.join(', '))} | 📅 ${p.created_at ? p.created_at.split(' ')[0] : ''}</div>
                        <p style="margin:0;font-size:0.85rem;color:var(--text-gray);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">${escapeHtml(p.summary)}</p>
                    </div>
                    <div style="display:flex;gap:8px;flex-shrink:0;">
                        <button class="btn btn-outline" style="padding:6px 12px;font-size:0.8rem;" onclick="editPost(${p.id})">✏️</button>
                        <button class="btn btn-outline" style="padding:6px 12px;font-size:0.8rem;color:#EF4444;border-color:rgba(239,68,68,0.4);" onclick="deletePost(${p.id})">🗑️</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        list.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка: ${escapeHtml(err.message)}</div>`;
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

async function handleAdminUploadFile(fileInputId, targetInputId) {
    const fileInput = document.getElementById(fileInputId);
    const targetInput = document.getElementById(targetInputId);
    const token = getAdminToken();
    if (!fileInput || !fileInput.files || !fileInput.files[0]) return;
    if (!token) {
        alert('Сессия администратора не активна. Войдите в CMS.');
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch('/api/v1/admin/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Ошибка загрузки файла');
        }
        const data = await res.json();
        if (targetInput && data.url) {
            targetInput.value = data.url;
            if (typeof updateCoverPreview === 'function') {
                updateCoverPreview();
            }
        }
        alert('✅ Файл успешно загружен и сохранен локально: ' + data.filename);
    } catch (err) {
        alert('❌ ' + err.message);
    } finally {
        fileInput.value = '';
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
    } catch (e) {
        alert('Не удалось загрузить данные статьи.');
    }
}

async function handleSavePost(e) {
    e.preventDefault();
    const token = getAdminToken();
    if (!token) {
        alert('Сессия администратора истекла. Пожалуйста, войдите в систему.');
        showAdminView('login');
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
        alert('Статья успешно удалена.');
    } catch (e) {
        alert(`Не удалось удалить статью: ${e.message}`);
    }
}

/* ==========================================================================
   ВКЛАДКА: ОПЕРАЦИОННАЯ ПАНЕЛЬ
   ========================================================================== */
async function loadAdminOperations() {
    const container = document.getElementById('admin-ops-content');
    const token = getAdminToken();
    if (!container) return;
    if (!token) {
        container.innerHTML = '<div style="color:#EF4444;text-align:center;padding:20px;">Требуется повторный вход в CMS.</div>';
        return;
    }

    container.innerHTML = '<div class="list-placeholder">Загрузка операционных метрик и баланса... ⏳</div>';
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
                            <strong style="font-size:0.9rem;color:var(--accent-turquoise);word-break:break-all;">${escapeHtml(yd.token || 'Авторизован (OAuth)')}</strong>
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
                                    <span style="color:#fff;font-family:monospace;">📁 ${escapeHtml(h.folder_name.replace('disk:/', ''))}</span>
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

                    ${balances.length > 0 ? `
                        <div style="font-size:0.85rem;font-weight:600;color:var(--text-gray);margin-bottom:6px;">Остатки официального баланса Сбера:</div>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:8px;margin-bottom:10px;">
                            ${balances.map(b => `
                                <div style="background:rgba(0,0,0,0.2);padding:8px 10px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;">
                                    <span style="color:#fff;font-weight:500;">${escapeHtml(b.usage)}</span>
                                    <span style="color:#34D399;font-weight:600;">${Number(b.value).toLocaleString('ru-RU')} ток.</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div style="background:rgba(0,0,0,0.2);padding:8px 12px;border-radius:6px;font-size:0.85rem;color:var(--text-muted);">
                            ${escapeHtml(bal.message || 'Официальный баланс получен.')}
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
                    ${Object.keys(alertServices).length > 0 ? Object.entries(alertServices).map(([k, s]) => {
                        const isErr = s.is_active_alert || (k === 'backup_freshness' && s.status === 'critical');
                        let badgeText = isErr ? '🚨 Сбой' : '✅ Норма';
                        if (k === 'backup_freshness') {
                            if (isErr) {
                                badgeText = '🚨 Дамп устарел';
                            } else if (s.last_backup_age_hours !== undefined && s.last_backup_age_hours !== null) {
                                badgeText = `🟢 Актуален (${s.last_backup_age_hours}ч)`;
                            } else {
                                badgeText = '🟢 Актуален';
                            }
                        }
                        return `
                            <div style="background:rgba(0,0,0,0.25);padding:8px 10px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;font-size:0.8rem;border-left:3px solid ${isErr ? '#EF4444' : '#10B981'};">
                                <span style="color:#fff;font-weight:500;">${escapeHtml(s.title)}</span>
                                <span style="color:${isErr ? '#F87171' : '#34D399'};font-weight:600;">
                                    ${badgeText}
                                </span>
                            </div>
                        `;
                    }).join('') : `
                        <div style="background:rgba(0,0,0,0.25);padding:8px 10px;border-radius:6px;font-size:0.8rem;color:var(--text-muted);">
                            Мониторинг 7 критических сервисов активен (интервал: 5 мин, дедупликация: 1 час).
                        </div>
                    `}
                </div>
            </div>
        `;

        container.innerHTML = html || '<div style="color:var(--text-muted);padding:20px;text-align:center;">Не удалось загрузить данные мониторинга.</div>';
    } catch (err) {
        container.innerHTML = `<div style="color:#EF4444;text-align:center;padding:20px;">Ошибка загрузки метрик: ${escapeHtml(err.message)}</div>`;
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
            resultDiv.innerHTML = `✅ <strong>${escapeHtml(data.message || 'Тестовое уведомление успешно отправлено!')}</strong><br><span style="color:var(--text-muted);font-size:0.8rem;">Адреса получения: ${escapeHtml(recips)}</span>`;
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
            resultDiv.innerHTML = `❌ Ошибка: ${escapeHtml(err.message)}`;
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
                            <div style="color:#fff;font-family:monospace;font-size:0.85rem;font-weight:600;">${escapeHtml(b.filename)}</div>
                            <div style="font-size:0.75rem;color:var(--text-muted);">Создан: ${escapeHtml(dateStr)}</div>
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="background:rgba(16,185,129,0.15);color:#34D399;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;">
                            ${escapeHtml(b.size_human || (b.size_bytes + ' B'))}
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
                ❌ Не удалось загрузить список резервных копий: ${escapeHtml(err.message)}
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
            statusDiv.innerHTML = `✅ Резервный снимок успешно создан: <strong>${escapeHtml(b.filename || '')}</strong> (${escapeHtml(b.size_human || '')}).`;
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
            statusDiv.innerHTML = `❌ Ошибка при создании дампа: ${escapeHtml(err.message)}`;
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '📦 Создать резервный снимок';
        }
    }
}

/* ==========================================================================
   ВКЛАДКА: МОДЕРАЦИЯ ОТКРЫТОГО ЧАТА ДЛЯ АДМИНИСТРАТОРА (Block 3)
   ========================================================================== */
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
            listEl.innerHTML = '<div class="list-placeholder">✅ Очередь модерации пуста. Все ссылки проверены!</div>';
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
                            <span style="font-size: 0.75rem; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">${escapeHtml(m.author_role)}</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(dt)}</span>
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
        listEl.innerHTML = `<div style="color: #EF4444; padding: 20px;">Ошибка: ${escapeHtml(err.message)}</div>`;
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

/* ==========================================================================
   ЭКСПОРТ В ГЛОБАЛЬНУЮ ОБЛАСТЬ (inline onclick/onsubmit в admin.html)
   ========================================================================== */
window.escapeHtml = escapeHtml;
window.getAdminToken = getAdminToken;
window.showAdminView = showAdminView;
window.handleAdminLogin = handleAdminLogin;
window.logoutAdmin = logoutAdmin;
window.switchAdminTab = switchAdminTab;
window.loadAdminLeads = loadAdminLeads;
window.loadAdminDoctors = loadAdminDoctors;
window.handleRegisterDoctor = handleRegisterDoctor;
window.loadAdminPosts = loadAdminPosts;
window.updateCoverPreview = updateCoverPreview;
window.checkAdminMediaUrl = checkAdminMediaUrl;
window.handleAdminUploadFile = handleAdminUploadFile;
window.openPostEditor = openPostEditor;
window.closePostEditor = closePostEditor;
window.editPost = editPost;
window.handleSavePost = handleSavePost;
window.deletePost = deletePost;
window.loadAdminOperations = loadAdminOperations;
window.handleTestAlert = handleTestAlert;
window.loadAdminBackups = loadAdminBackups;
window.handleCreateBackup = handleCreateBackup;
window.loadAdminModerationQueue = loadAdminModerationQueue;
window.approveModerationMessage = approveModerationMessage;
window.deleteModerationMessage = deleteModerationMessage;
window.banUserFromModeration = banUserFromModeration;

/* ==========================================================================
   ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    const token = getAdminToken();
    if (token) {
        showAdminView('dashboard');
        loadAdminLeads();
        loadAdminDoctors();
    } else {
        showAdminView('login');
    }
});
