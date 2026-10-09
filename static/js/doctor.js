/* ==========================================================================
   КАБИНЕТ СПЕЦИАЛИСТА (DOCTOR PORTAL) — автономный модуль /doctor
   Этап 1, шаг 2.1.3: логика вынесена из static/js/app.js (строки 1565–2262,
   3142–3160) и адаптирована под отдельную страницу /doctor (view-переключения
   вместо модалок лендинга). Лендинг (index.html / app.js) не изменяется.
   ========================================================================== */

/* ==========================================================================
   1. СОСТОЯНИЕ И ПЕРЕМЕННЫЕ
   ========================================================================== */
let currentDoctorPatientFolderId = '';
let currentDoctorShareToken = '';
let currentLatestAnalysesDocId = null;
let currentLatestAnalysesData = [];

const DOCTOR_TOKEN_KEY = 'doctor_token';

function getDoctorToken() {
    return localStorage.getItem(DOCTOR_TOKEN_KEY);
}

/* ==========================================================================
   2. УТИЛИТЫ
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

/* ==========================================================================
   3. ПЕРЕКЛЮЧЕНИЕ ЭКРАНОВ (AUTH <-> DASHBOARD)
   ========================================================================== */
function showDoctorAuthView() {
    const authView = document.getElementById('doctor-auth-view');
    const dashView = document.getElementById('doctor-dashboard-view');
    const userBar = document.getElementById('doctor-user-bar');
    const guestBar = document.getElementById('doctor-guest-bar');

    if (authView) {
        authView.style.display = '';
        authView.classList.add('active');
    }
    if (dashView) {
        dashView.style.display = 'none';
        dashView.classList.remove('active');
    }
    if (userBar) userBar.style.display = 'none';
    if (guestBar) guestBar.style.display = '';
}

function showDoctorDashboard() {
    const docName = localStorage.getItem('doctor_name') || 'Доктор Центра';
    const docSpec = localStorage.getItem('doctor_specialty') || 'Специалист';

    const nameEl = document.getElementById('doc-profile-name');
    const specEl = document.getElementById('doc-profile-specialty');
    if (nameEl) nameEl.textContent = docName;
    if (specEl) specEl.textContent = docSpec;

    const authView = document.getElementById('doctor-auth-view');
    const dashView = document.getElementById('doctor-dashboard-view');
    const userBar = document.getElementById('doctor-user-bar');
    const guestBar = document.getElementById('doctor-guest-bar');

    if (authView) {
        authView.style.display = 'none';
        authView.classList.remove('active');
    }
    if (dashView) {
        dashView.style.display = '';
        dashView.classList.add('active');
    }
    if (userBar) userBar.style.display = '';
    if (guestBar) guestBar.style.display = 'none';
}

/* ==========================================================================
   4. МОДАЛЬНОЕ ОКНО ПРЕДПРОСМОТРА АНАЛИЗОВ
   ========================================================================== */
function openAnalysesPreviewModalBox() {
    const modal = document.getElementById('analyses-preview-modal');
    if (modal) modal.style.display = 'flex';
}

function closeAnalysesPreviewModal() {
    const modal = document.getElementById('analyses-preview-modal');
    if (modal) modal.style.display = 'none';
}

/* ==========================================================================
   5. АВТОРИЗАЦИЯ И СЕССИЯ ВРАЧА
   ========================================================================== */
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

        showDoctorDashboard();

        // Проверяем отложенный токен шеринга из URL (deep-linking)
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

function logoutDoctor() {
    localStorage.removeItem('doctor_token');
    localStorage.removeItem('doctor_id');
    localStorage.removeItem('doctor_name');
    localStorage.removeItem('doctor_specialty');

    // Сброс полей карты
    const tokenInput = document.getElementById('doc-share-token-input');
    if (tokenInput) tokenInput.value = '';
    const recordView = document.getElementById('doc-record-view');
    if (recordView) recordView.style.display = 'none';
    const recordEmpty = document.getElementById('doc-record-empty');
    if (recordEmpty) recordEmpty.style.display = 'block';
    const errorDiv = document.getElementById('doc-search-error');
    if (errorDiv) errorDiv.style.display = 'none';
    const notesInput = document.getElementById('doc-notes-input');
    if (notesInput) notesInput.value = '';

    currentDoctorPatientFolderId = '';
    currentDoctorShareToken = '';
    currentLatestAnalysesDocId = null;
    currentLatestAnalysesData = [];

    showDoctorAuthView();
}

/* ==========================================================================
   6. РАБОТА С МЕДКАРТОЙ ПАЦИЕНТА
   ========================================================================== */
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
    const docToken = getDoctorToken();
    const errorDiv = document.getElementById('doc-search-error');
    const recordView = document.getElementById('doc-record-view');
    const recordEmpty = document.getElementById('doc-record-empty');
    const searchBtn = document.getElementById('doc-search-btn');

    if (!docToken) {
        // Не авторизован: запоминаем токен и показываем форму входа
        sessionStorage.setItem('pending_share_token', shareToken);
        showDoctorAuthView();
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

async function viewDoctorDocument(shareToken, encodedDocName) {
    const docName = decodeURIComponent(encodedDocName);
    const docToken = getDoctorToken();
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
    const docToken = getDoctorToken();
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

/* ==========================================================================
   7. КЛИНИЧЕСКИЕ ЗАМЕТКИ ВРАЧА
   ========================================================================== */
async function loadDoctorNotes(patientFolderId) {
    const docToken = getDoctorToken();
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
    const docToken = getDoctorToken();
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
            btn.textContent = 'Сохранить заметку 💾';
        }
    }
}

/* ==========================================================================
   8. RAG-КОНСИЛИУМ (GIGACHAT): РЕЗЮМЕ И PDF
   ========================================================================== */
async function handleDoctorGenerateSummary() {
    const docToken = getDoctorToken();
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

            if (s.anamnesis) {
                cardsHTML += `
                    <div style="background: rgba(255,255,255,0.03); border-left: 4px solid var(--accent-purple); border-radius: 8px; padding: 12px 14px;">
                        <h5 style="margin: 0 0 6px 0; color: #fff; font-size: 0.95rem;">📋 Анамнез и развитие</h5>
                        <p style="margin: 0; font-size: 0.88rem; color: #E2E8F0; line-height: 1.5; white-space: pre-wrap;">${escapeHtml(s.anamnesis)}</p>
                    </div>
                `;
            }

            if (s.diagnoses && (Array.isArray(s.diagnoses) ? s.diagnoses.length : s.diagnoses)) {
                const diagList = Array.isArray(s.diagnoses) ? s.diagnoses.map(d => `<li>${escapeHtml(d)}</li>`).join('') : `<li>${escapeHtml(s.diagnoses)}</li>`;
                cardsHTML += `
                    <div style="background: rgba(255,255,255,0.03); border-left: 4px solid var(--accent-turquoise); border-radius: 8px; padding: 12px 14px;">
                        <h5 style="margin: 0 0 6px 0; color: #fff; font-size: 0.95rem;">🩺 Установленные диагнозы и особенности</h5>
                        <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #E2E8F0; line-height: 1.5;">${diagList}</ul>
                    </div>
                `;
            }

            if (s.contraindications && (Array.isArray(s.contraindications) ? s.contraindications.length : s.contraindications)) {
                const contraList = Array.isArray(s.contraindications) ? s.contraindications.map(c => `<li>${escapeHtml(c)}</li>`).join('') : `<li>${escapeHtml(s.contraindications)}</li>`;
                cardsHTML += `
                    <div style="background: rgba(239, 68, 68, 0.12); border-left: 4px solid #EF4444; border-radius: 8px; padding: 12px 14px;">
                        <h5 style="margin: 0 0 6px 0; color: #F87171; font-size: 0.95rem;">⚠️ Абсолютные противопоказания и риски</h5>
                        <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #FCA5A5; line-height: 1.5;">${contraList}</ul>
                    </div>
                `;
            }

            if (s.drug_interactions && (Array.isArray(s.drug_interactions) ? s.drug_interactions.length : s.drug_interactions)) {
                const drugsList = Array.isArray(s.drug_interactions) ? s.drug_interactions.map(d => `<li>${escapeHtml(d)}</li>`).join('') : `<li>${escapeHtml(s.drug_interactions)}</li>`;
                cardsHTML += `
                    <div style="background: rgba(245, 158, 11, 0.12); border-left: 4px solid #F59E0B; border-radius: 8px; padding: 12px 14px;">
                        <h5 style="margin: 0 0 6px 0; color: #FBBF24; font-size: 0.95rem;">💊 Межлекарственные взаимодействия и несовместимость</h5>
                        <ul style="margin: 0; padding-left: 20px; font-size: 0.88rem; color: #FDE68A; line-height: 1.5;">${drugsList}</ul>
                    </div>
                `;
            }

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
    const docToken = getDoctorToken();
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
   9. ХРОНОЛОГИЯ АНАЛИЗОВ: ГЕНЕРАЦИЯ, ПРЕДПРОСМОТР, DOCX
   ========================================================================== */
async function handleDoctorGenerateAnalyses() {
    const docToken = getDoctorToken();
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
    const docToken = getDoctorToken();
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
    const docToken = getDoctorToken();
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
        } catch (e) { /* используем текущие данные */ }
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

    openAnalysesPreviewModalBox();
}

async function handleDoctorDownloadLatestAnalysesDocx() {
    if (!currentLatestAnalysesDocId) {
        alert('Сначала сформируйте выписку анализов.');
        return;
    }
    await downloadDoctorAnalysesDocx(currentLatestAnalysesDocId);
}

async function downloadDoctorAnalysesDocx(docId) {
    const docToken = getDoctorToken();
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
    const docToken = getDoctorToken();
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

/* ==========================================================================
   10. ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Восстанавливаем состояние сессии врача
    const docToken = getDoctorToken();
    if (docToken) {
        showDoctorDashboard();
    } else {
        showDoctorAuthView();
        const docError = document.getElementById('doctor-login-error');
        if (docError) docError.style.display = 'none';
    }

    // 2. Deep-linking: /doctor/?share_token=XYZ
    const urlParams = new URLSearchParams(window.location.search);
    const shareToken = urlParams.get('share_token');
    if (shareToken) {
        const docInput = document.getElementById('doc-share-token-input');
        if (docInput) docInput.value = shareToken;

        if (docToken) {
            loadDoctorPatientRecord(shareToken);
        } else {
            // Не авторизован: запоминаем токен, после логина карта откроется автоматически
            sessionStorage.setItem('pending_share_token', shareToken);
            const loginErr = document.getElementById('doctor-login-error');
            if (loginErr) {
                loginErr.textContent = 'Для просмотра карты пациента по ссылке выполните вход в систему.';
                loginErr.style.display = 'block';
            }
        }
    }
});
