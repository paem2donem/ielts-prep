/* ===================================================================
   IELTS: Band 7.5+ Master Prep Suite - Frontend Engine (v3.0)
   Full Interactive Modules: Dynamic AI Generator, User Profiles, 
   Question Bank, Error Notebook, Cambridge Tricks, Timers & Analytics
   =================================================================== */

// Safe Storage Helpers (protects incognito & mobile WebViews)
function safeGetStorage(key, defaultVal) {
  try {
    const val = localStorage.getItem(key);
    return val !== null ? val : defaultVal;
  } catch (e) {
    return defaultVal;
  }
}
function safeSetStorage(key, val) {
  try {
    localStorage.setItem(key, val);
  } catch (e) {}
}

// Global State
const state = {
  currentUser: {
    email: safeGetStorage('forensync_user_email', 'paem2.donem@gmail.com'),
    name: safeGetStorage('forensync_user_name', 'Aday')
  },
  currentMode: 'cyber', // 'cyber' or 'academic'
  currentModule: 'writing',
  examData: null,
  activeCustomPassage: null,
  activeCustomSection: null,
  allQuestions: [],

  // Timers
  timers: {
    writing: { remaining: 3600, interval: null, running: false },
    reading: { remaining: 3600, interval: null, running: false },
    speakingPrep: { remaining: 60, interval: null, running: false }
  },

  // Audio Recording
  mediaRecorder: null,
  recordedChunks: [],
  recordedBlob: null,
  isRecording: false,

  // Listening Audio
  audioElement: new Audio(),
  isPlaying: false
};

// Robust Application Launcher (executes regardless of DOMContentLoaded timing)
function startApp() {
  initAuthUI();
  initNavigation();
  initModeSwitcher();
  initTimers();
  initWritingModule();
  initSpeakingRecorder();
  initDynamicGenerators();
  initQuestionBankEvents();
  
  // Initial load
  switchMode('cyber');
  loadAnalytics();
  loadTricks();
  loadMistakes();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  startApp();
}

/* ================= Auth & User Profile ================= */
function initAuthUI() {
  const userPill = document.getElementById('user-profile-pill');
  const userDisplayEmail = document.getElementById('user-display-email');
  const userDisplayAvatar = document.getElementById('user-display-avatar');
  const modal = document.getElementById('modal-login');
  const closeBtn = document.getElementById('btn-close-login');
  const saveBtn = document.getElementById('btn-save-login');
  const inputEmail = document.getElementById('login-email-input');

  function updatePill() {
    userDisplayEmail.textContent = state.currentUser.email;
    userDisplayAvatar.textContent = state.currentUser.email.charAt(0).toUpperCase();
  }
  updatePill();

  if (userPill) {
    userPill.addEventListener('click', () => {
      inputEmail.value = state.currentUser.email;
      modal.classList.add('active');
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
  }

  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const email = inputEmail.value.trim().toLowerCase();
      if (!email || !email.includes('@')) {
        alert('Lütfen geçerli bir Gmail / e-posta adresi girin.');
        return;
      }

      state.currentUser.email = email;
      state.currentUser.name = email.split('@')[0].capitalize();
      localStorage.setItem('forensync_user_email', email);
      localStorage.setItem('forensync_user_name', state.currentUser.name);

      updatePill();
      modal.classList.remove('active');

      // Sync with server
      await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, name: state.currentUser.name })
      });

      loadAnalytics();
      loadMistakes();
    });
  }
}

String.prototype.capitalize = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};

/* ================= Navigation Handler ================= */
function initNavigation() {
  const navButtons = document.querySelectorAll('[data-module-target]');
  
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-module-target');
      switchModule(target);
    });
  });
}

function switchModule(moduleName) {
  state.currentModule = moduleName;

  document.querySelectorAll('.panel-view').forEach(panel => {
    panel.classList.remove('active');
  });
  const targetPanel = document.getElementById(`panel-${moduleName}`);
  if (targetPanel) targetPanel.classList.add('active');

  document.querySelectorAll('[data-module-target]').forEach(btn => {
    if (btn.getAttribute('data-module-target') === moduleName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (moduleName === 'mentor') loadAnalytics();
  if (moduleName === 'mistakes') loadMistakes();
  if (moduleName === 'tricks') loadTricks();
  if (moduleName === 'bank') loadQuestionBank();
}

/* ================= Mode Switcher ================= */
function initModeSwitcher() {
  const cyberBtn = document.getElementById('btn-mode-cyber');
  const acadBtn = document.getElementById('btn-mode-academic');

  cyberBtn.addEventListener('click', () => switchMode('cyber'));
  acadBtn.addEventListener('click', () => switchMode('academic'));
}

async function switchMode(mode) {
  state.currentMode = mode;
  state.activeCustomPassage = null; // reset dynamic passage on mode switch
  currentReadingPassage = 'passage_1';
  currentListeningSection = 'section_1';

  document.getElementById('btn-mode-cyber').classList.toggle('active', mode === 'cyber');
  document.getElementById('btn-mode-academic').classList.toggle('active', mode === 'academic');

  try {
    const res = await fetch(`/api/exam-data/${mode}`);
    state.examData = await res.json();
    renderAllModules();
  } catch (err) {
    console.error('Failed to load exam data:', err);
  }
}

function renderAllModules() {
  if (!state.examData) return;
  renderListeningModule();
  renderReadingModule();
  renderWritingModule();
  renderSpeakingModule();
}

/* ================= Dynamic AI Exam Generators ================= */
function initDynamicGenerators() {
  // Reading AI Generator
  const btnGenReading = document.getElementById('btn-generate-ai-reading');
  if (btnGenReading) {
    btnGenReading.addEventListener('click', async () => {
      btnGenReading.disabled = true;
      btnGenReading.innerHTML = '<span class="spinner"></span> AI Generating Band 8.0 Passage...';

      try {
        const res = await fetch('/api/exam/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ module: 'reading', mode: state.currentMode })
        });
        const data = await res.json();
        if (data.success) {
          state.activeCustomPassage = data.data;
          renderReadingModule();
          alert('✨ Yeni Cambridge IELTS Okuma Pasajı ve Soruları başarıyla üretildi!');
        }
      } catch (e) {
        alert('Üretim hatası: ' + e.message);
      } finally {
        btnGenReading.disabled = false;
        btnGenReading.innerHTML = '✨ Yapay Zeka ile Sınırsız Yeni Pasaj Üret';
      }
    });
  }

  // Writing AI Generator
  const btnGenWriting = document.getElementById('btn-generate-ai-writing');
  if (btnGenWriting) {
    btnGenWriting.addEventListener('click', async () => {
      btnGenWriting.disabled = true;
      btnGenWriting.innerHTML = '<span class="spinner"></span> AI Writing Prompt...';

      try {
        const res = await fetch('/api/exam/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            module: 'writing', 
            mode: state.currentMode,
            task_type: currentWritingTask
          })
        });
        const data = await res.json();
        if (data.success) {
          document.getElementById('writing-prompt-text').textContent = data.data.prompt;
          alert('✨ Yeni Kompozisyon Sorusu oluşturuldu!');
        }
      } catch (e) {
        alert('Üretim hatası: ' + e.message);
      } finally {
        btnGenWriting.disabled = false;
        btnGenWriting.innerHTML = '✨ Yeni Görev Üret';
      }
    });
  }

  // Listening AI Generator
  const btnGenListening = document.getElementById('btn-generate-ai-listening');
  if (btnGenListening) {
    btnGenListening.addEventListener('click', async () => {
      btnGenListening.disabled = true;
      btnGenListening.innerHTML = '<span class="spinner"></span> AI Dinleme Sınavı Üretiliyor...';

      try {
        const res = await fetch('/api/exam/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ module: 'listening', mode: state.currentMode })
        });
        const data = await res.json();
        if (data.success) {
          state.activeCustomSection = data.data;
          renderListeningModule();
          alert('✨ Yeni Cambridge IELTS Dinleme Sınavı (Audio Script + 4 Soru) başarıyla üretildi!');
        } else {
          alert('Üretim hatası: ' + (data.detail || 'Bilinmeyen hata'));
        }
      } catch (e) {
        alert('Üretim hatası: ' + e.message);
      } finally {
        btnGenListening.disabled = false;
        btnGenListening.innerHTML = '✨ Yapay Zeka ile Yeni Dinleme Sınavı Üret';
      }
    });
  }

  // Speaking AI Generator
  const btnGenSpeaking = document.getElementById('btn-generate-ai-speaking');
  if (btnGenSpeaking) {
    btnGenSpeaking.addEventListener('click', async () => {
      btnGenSpeaking.disabled = true;
      btnGenSpeaking.innerHTML = '<span class="spinner"></span> AI Konuşma Sınavı Üretiliyor...';

      try {
        const res = await fetch('/api/exam/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ module: 'speaking', mode: state.currentMode })
        });
        const data = await res.json();
        if (data.success) {
          if (!state.examData) state.examData = {};
          state.examData.speaking = data.data;
          renderSpeakingModule();
          alert('✨ Yeni Cambridge IELTS Konuşma Sınavı (Part 1, Cue Card ve Part 3) başarıyla oluşturuldu!');
        } else {
          alert('Üretim hatası: ' + (data.detail || 'Bilinmeyen hata'));
        }
      } catch (e) {
        alert('Üretim hatası: ' + e.message);
      } finally {
        btnGenSpeaking.disabled = false;
        btnGenSpeaking.innerHTML = '✨ Yeni Konuşma Sınavı Üret';
      }
    });
  }
}

/* ================= Reading Module ================= */
let currentReadingPassage = 'passage_1';

function renderReadingModule() {
  const readingData = state.examData ? state.examData.reading : null;
  if (!readingData && !state.activeCustomPassage) return;

  // Populate Reading Selector Dropdown
  const selector = document.getElementById('reading-test-selector');
  if (selector && readingData) {
    selector.innerHTML = '';
    Object.keys(readingData).forEach(key => {
      const opt = document.createElement('option');
      opt.value = key;
      opt.textContent = readingData[key].title;
      if (!state.activeCustomPassage && key === currentReadingPassage) {
        opt.selected = true;
      }
      selector.appendChild(opt);
    });

    if (state.activeCustomPassage) {
      const opt = document.createElement('option');
      opt.value = 'custom_ai';
      opt.textContent = `✨ [AI Üretimi] ${state.activeCustomPassage.title}`;
      opt.selected = true;
      selector.appendChild(opt);
    }

    selector.onchange = (e) => {
      const val = e.target.value;
      if (val === 'custom_ai') {
        if (state.activeCustomPassage) {
          renderCustomReadingPassage(state.activeCustomPassage);
        }
      } else {
        state.activeCustomPassage = null;
        currentReadingPassage = val;
        renderStaticReadingPassage(readingData[val]);
      }
    };
  }

  if (state.activeCustomPassage) {
    renderCustomReadingPassage(state.activeCustomPassage);
  } else if (readingData) {
    const passage = readingData[currentReadingPassage] || readingData['passage_1'];
    renderStaticReadingPassage(passage);
  }
}

function renderStaticReadingPassage(passage) {
  if (!passage) return;
  document.getElementById('reading-passage-title').textContent = passage.title;
  document.getElementById('reading-passage-text').innerHTML = passage.text.split('\n\n').map(p => `<p>${p}</p>`).join('');
  renderReadingQuestions(passage.questions);
}

function renderCustomReadingPassage(passage) {
  document.getElementById('reading-passage-title').innerHTML = `✨ [AI Canlı Sınav] ${passage.title}`;
  document.getElementById('reading-passage-text').innerHTML = passage.text.split('\n\n').map(p => `<p>${p}</p>`).join('');
  renderReadingQuestions(passage.questions);
}

function renderReadingQuestions(questions) {
  const qContainer = document.getElementById('reading-questions-container');
  qContainer.innerHTML = '';

  questions.forEach(q => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question-item';

    const optionsHtml = q.options.map(opt => `
      <label class="radio-label">
        <input type="radio" name="rq-${q.id}" value="${opt}">
        <span>${opt}</span>
      </label>
    `).join('');

    qDiv.innerHTML = `
      <div class="question-text">${q.prompt}</div>
      <div class="q-options-group">${optionsHtml}</div>
    `;

    qContainer.appendChild(qDiv);
  });
}

// Grade Reading
const submitReadingBtn = document.getElementById('btn-submit-reading');
if (submitReadingBtn) {
  submitReadingBtn.addEventListener('click', async () => {
    const readingData = state.examData ? state.examData.reading : null;
    const passage = state.activeCustomPassage || (readingData ? (readingData[currentReadingPassage] || readingData.passage_1) : null);
    if (!passage) return;

    const answers = {};
    passage.questions.forEach(q => {
      const checked = document.querySelector(`input[name="rq-${q.id}"]:checked`);
      answers[q.id] = checked ? checked.value : '';
    });

    submitReadingBtn.disabled = true;
    submitReadingBtn.innerHTML = '<span class="spinner"></span> Grading...';

    try {
      const res = await fetch('/api/grade/reading', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: state.currentMode,
          passage_id: currentReadingPassage,
          answers: answers,
          user_email: state.currentUser.email,
          custom_passage: state.activeCustomPassage
        })
      });

      const data = await res.json();
      displayGradingResult('reading-feedback-area', data, 'Reading');
      loadAnalytics();
      loadMistakes();
    } catch (e) {
      alert('Grading error: ' + e.message);
    } finally {
      submitReadingBtn.disabled = false;
      submitReadingBtn.innerHTML = '📝 Testi Puanla & Yanlışlarımı Kaydet';
    }
  });
}

/* ================= Listening Module ================= */
let currentListeningSection = 'section_1';

function renderListeningModule() {
  const listeningData = state.examData ? state.examData.listening : null;
  if (!listeningData && !state.activeCustomSection) return;

  // Populate Listening Selector Dropdown
  const selector = document.getElementById('listening-test-selector');
  if (selector && listeningData) {
    selector.innerHTML = '';
    Object.keys(listeningData).forEach(key => {
      const opt = document.createElement('option');
      opt.value = key;
      opt.textContent = listeningData[key].title;
      if (!state.activeCustomSection && key === currentListeningSection) {
        opt.selected = true;
      }
      selector.appendChild(opt);
    });

    if (state.activeCustomSection) {
      const opt = document.createElement('option');
      opt.value = 'custom_ai';
      opt.textContent = `✨ [AI Canlı Dinleme] ${state.activeCustomSection.title}`;
      opt.selected = true;
      selector.appendChild(opt);
    }

    selector.onchange = (e) => {
      const val = e.target.value;
      if (val === 'custom_ai') {
        if (state.activeCustomSection) {
          renderListeningContent(state.activeCustomSection, true);
        }
      } else {
        state.activeCustomSection = null;
        currentListeningSection = val;
        renderListeningContent(listeningData[val], false);
      }
    };
  }

  if (state.activeCustomSection) {
    renderListeningContent(state.activeCustomSection, true);
  } else if (listeningData) {
    const section = listeningData[currentListeningSection] || listeningData['section_1'];
    renderListeningContent(section, false);
  }
}

function renderListeningContent(section, isCustom = false) {
  if (!section) return;
  document.getElementById('listening-section-title').textContent = (isCustom ? '✨ [AI Canlı Sınav] ' : '') + section.title;
  document.getElementById('listening-section-intro').textContent = section.intro;

  const qContainer = document.getElementById('listening-questions-container');
  qContainer.innerHTML = '';

  section.questions.forEach(q => {
    const qDiv = document.createElement('div');
    qDiv.className = 'question-item';

    if (q.type === 'fill') {
      qDiv.innerHTML = `
        <div class="question-text">${q.prompt}</div>
        <input type="text" class="input-fill" id="lq-${q.id}" placeholder="Type your answer...">
      `;
    } else if (q.type === 'mcq') {
      const optionsHtml = q.options.map(opt => {
        const val = opt.charAt(0);
        return `
          <label class="radio-label">
            <input type="radio" name="lq-${q.id}" value="${val}">
            <span>${opt}</span>
          </label>
        `;
      }).join('');

      qDiv.innerHTML = `
        <div class="question-text">${q.prompt}</div>
        <div class="q-options-group">${optionsHtml}</div>
      `;
    }

    qContainer.appendChild(qDiv);
  });

  loadListeningAudio(state.currentMode, currentListeningSection);
}

async function loadListeningAudio(mode, sectionId) {
  const trackTitle = document.getElementById('track-title');
  if (!trackTitle) return;

  if (state.activeCustomSection) {
    trackTitle.textContent = '✨ AI Ses Metni Hazır (Oynata Basarak Dinleyin)';
    state.audioElement.src = '';
    return;
  }

  trackTitle.textContent = 'Audio loading...';

  try {
    const res = await fetch(`/api/audio/listening/${mode}/${sectionId}`);
    const data = await res.json();

    if (data.has_audio && data.audio_url) {
      state.audioElement.src = data.audio_url;
      trackTitle.textContent = 'Ready to play (Authentic Gemini Audio)';
    } else {
      trackTitle.textContent = 'Audio script ready (Native Speech Engine)';
      state.audioElement.src = '';
    }
  } catch (e) {
    trackTitle.textContent = 'Audio ready';
  }
}

// Audio Player Buttons
const playBtn = document.getElementById('btn-play-listening');
if (playBtn) {
  playBtn.addEventListener('click', () => {
    if (state.activeCustomSection) {
      if (window.speechSynthesis) {
        if (state.isPlaying) {
          window.speechSynthesis.cancel();
          playBtn.innerHTML = '▶';
          state.isPlaying = false;
        } else {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(state.activeCustomSection.audio_script);
          utterance.lang = 'en-GB';
          utterance.rate = 0.95;
          utterance.onend = () => {
            playBtn.innerHTML = '▶';
            state.isPlaying = false;
          };
          utterance.onerror = () => {
            playBtn.innerHTML = '▶';
            state.isPlaying = false;
          };
          window.speechSynthesis.speak(utterance);
          playBtn.innerHTML = '⏸';
          state.isPlaying = true;
        }
      }
      return;
    }

    if (state.audioElement.src) {
      if (state.isPlaying) {
        state.audioElement.pause();
        playBtn.innerHTML = '▶';
        state.isPlaying = false;
      } else {
        state.audioElement.play();
        playBtn.innerHTML = '⏸';
        state.isPlaying = true;
      }
    } else {
      const section = state.examData ? state.examData.listening[currentListeningSection] : null;
      if (window.speechSynthesis && section) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(section.audio_script);
        utterance.lang = 'en-GB';
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
      }
    }
  });

  state.audioElement.addEventListener('timeupdate', () => {
    const progress = (state.audioElement.currentTime / (state.audioElement.duration || 1)) * 100;
    const bar = document.getElementById('listening-progress-bar');
    if (bar) bar.style.width = `${progress}%`;
  });

  state.audioElement.addEventListener('ended', () => {
    playBtn.innerHTML = '▶';
    state.isPlaying = false;
  });
}

// Grade Listening
const submitListeningBtn = document.getElementById('btn-submit-listening');
if (submitListeningBtn) {
  submitListeningBtn.addEventListener('click', async () => {
    const section = state.activeCustomSection || (state.examData && state.examData.listening ? state.examData.listening[currentListeningSection] : null);
    if (!section) return;
    const answers = {};

    section.questions.forEach(q => {
      if (q.type === 'fill') {
        const inp = document.getElementById(`lq-${q.id}`);
        answers[q.id] = inp ? inp.value.trim() : '';
      } else if (q.type === 'mcq') {
        const checked = document.querySelector(`input[name="lq-${q.id}"]:checked`);
        answers[q.id] = checked ? checked.value : '';
      }
    });

    submitListeningBtn.disabled = true;
    submitListeningBtn.innerHTML = '<span class="spinner"></span> Sınav Notlandırılıyor...';

    try {
      const res = await fetch('/api/grade/listening', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: state.currentMode,
          section_id: state.activeCustomSection ? 'custom_ai' : currentListeningSection,
          answers: answers,
          user_email: state.currentUser.email,
          custom_section: state.activeCustomSection || null
        })
      });

      const data = await res.json();
      displayGradingResult('listening-feedback-area', data, 'Listening');
      loadAnalytics();
      loadMistakes();
    } catch (e) {
      alert('Grading error: ' + e.message);
    } finally {
      submitListeningBtn.disabled = false;
      submitListeningBtn.innerHTML = '📝 Submit & Grade Listening';
    }
  });
}

/* ================= Writing Module ================= */
let currentWritingTask = 'Task 2';

function initWritingModule() {
  const btnTask1 = document.getElementById('btn-writing-task1');
  const btnTask2 = document.getElementById('btn-writing-task2');
  const essayInput = document.getElementById('essay-input');

  btnTask1.addEventListener('click', () => {
    currentWritingTask = 'Task 1';
    btnTask1.classList.add('active');
    btnTask2.classList.remove('active');
    renderWritingModule();
  });

  btnTask2.addEventListener('click', () => {
    currentWritingTask = 'Task 2';
    btnTask2.classList.add('active');
    btnTask1.classList.remove('active');
    renderWritingModule();
  });

  essayInput.addEventListener('input', () => {
    const text = essayInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const minWords = currentWritingTask === 'Task 1' ? 150 : 250;

    const countElem = document.getElementById('writing-word-count');
    countElem.textContent = `${words} / ${minWords} words`;
    countElem.style.color = (words >= minWords) ? 'var(--accent-emerald)' : 'var(--text-muted)';
  });

  const submitWritingBtn = document.getElementById('btn-submit-writing');
  submitWritingBtn.addEventListener('click', async () => {
    const essayText = essayInput.value;
    const promptCtx = document.getElementById('writing-prompt-text').textContent;

    submitWritingBtn.disabled = true;
    submitWritingBtn.innerHTML = '<span class="spinner"></span> AI Examiner Analyzing...';

    const feedbackArea = document.getElementById('writing-feedback-area');
    feedbackArea.innerHTML = '<div style="text-align:center; padding: 20px;"><span class="spinner"></span> Cambridge & Jean Monnet Examiner evaluating essay...</div>';

    try {
      const res = await fetch('/api/evaluate/writing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          essay_text: essayText,
          task_type: currentWritingTask,
          mode: state.currentMode,
          prompt_context: promptCtx,
          user_email: state.currentUser.email
        })
      });

      const data = await res.json();
      if (data.success) {
        feedbackArea.innerHTML = `
          <div class="feedback-container">
            <div class="score-hero">
              <div>
                <div style="text-transform: uppercase; font-size: 0.8rem; color: var(--text-dim);">${currentWritingTask} Band Score</div>
                <div class="score-val">Band ${data.score}</div>
              </div>
              <div class="badge badge-cyan">${data.word_count} Words</div>
            </div>
            ${formatMarkdown(data.feedback)}
          </div>
        `;
        loadAnalytics();
      } else {
        feedbackArea.innerHTML = `<div class="card" style="border-color: var(--accent-rose); color: var(--accent-rose);">${data.error || 'Evaluation error'}</div>`;
      }
    } catch (e) {
      feedbackArea.innerHTML = `<div class="card" style="color: var(--accent-rose);">Network error: ${e.message}</div>`;
    } finally {
      submitWritingBtn.disabled = false;
      submitWritingBtn.innerHTML = '🚀 Submit to AI Examiner';
    }
  });
}

function renderWritingModule() {
  const writingData = state.examData.writing;
  if (!writingData) return;

  const taskData = (currentWritingTask === 'Task 1') ? writingData.task_1 : writingData.task_2;
  document.getElementById('writing-task-title').textContent = taskData.title;
  document.getElementById('writing-prompt-text').textContent = taskData.prompt.trim();

  const minWords = currentWritingTask === 'Task 1' ? 150 : 250;
  document.getElementById('writing-word-count').textContent = `0 / ${minWords} words`;
}

/* ================= Speaking Module ================= */
let currentSpeakingPart = 'Part 2';

function renderSpeakingModule() {
  const speakingData = state.examData ? state.examData.speaking : null;
  if (!speakingData) return;

  const cueCardElem = document.getElementById('speaking-cue-card-box');
  const partData = speakingData.part_2;
  const examTitle = speakingData.title ? `<div style="font-size: 0.85rem; color: var(--accent-purple); font-weight: 600; margin-bottom: 8px;">🎯 ${speakingData.title}</div>` : '';

  let part1Html = '';
  if (speakingData.part_1 && speakingData.part_1.questions && speakingData.part_1.questions.length > 0) {
    part1Html = `
      <details style="margin-bottom: 12px; background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 8px 12px;">
        <summary style="cursor: pointer; font-size: 0.82rem; font-weight: 600; color: var(--accent-cyan);">📋 Part 1 Isınma Sorularını İncele (${speakingData.part_1.questions.length} Soru)</summary>
        <ul style="margin: 8px 0 0 16px; font-size: 0.82rem; color: var(--text-main); line-height: 1.6;">
          ${speakingData.part_1.questions.map(q => `<li>${q}</li>`).join('')}
        </ul>
      </details>
    `;
  }

  let part3Html = '';
  if (speakingData.part_3 && speakingData.part_3.questions && speakingData.part_3.questions.length > 0) {
    part3Html = `
      <details style="margin-top: 12px; background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 8px 12px;">
        <summary style="cursor: pointer; font-size: 0.82rem; font-weight: 600; color: var(--accent-purple);">💡 Part 3 Analitik Tartışma Sorularını İncele (${speakingData.part_3.questions.length} Soru)</summary>
        <ul style="margin: 8px 0 0 16px; font-size: 0.82rem; color: var(--text-main); line-height: 1.6;">
          ${speakingData.part_3.questions.map(q => `<li>${q}</li>`).join('')}
        </ul>
      </details>
    `;
  }

  if (partData && partData.cue_card) {
    cueCardElem.innerHTML = `
      ${examTitle}
      ${part1Html}
      <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 8px;">IELTS Speaking Part 2 - Cue Card (1 dk Hazırlık, 2 dk Konuşma):</div>
      <div class="cue-card">${partData.cue_card.trim().replace(/\n/g, '<br>')}</div>
      ${part3Html}
    `;
  }
}

function initSpeakingRecorder() {
  const recordBtn = document.getElementById('btn-record-speaking');
  const audioPreview = document.getElementById('speaking-audio-preview');
  const submitBtn = document.getElementById('btn-submit-speaking');
  const timerDisplay = document.getElementById('speaking-record-time');
  const micWarning = document.getElementById('speaking-mic-warning');
  const fileInput = document.getElementById('speaking-file-input');
  const uploadBtn = document.getElementById('btn-upload-audio-file');

  // Check if getUserMedia is actually supported in the current browser and origin context
  const hasMediaDevices = Boolean(
    navigator && 
    navigator.mediaDevices && 
    typeof navigator.mediaDevices.getUserMedia === 'function'
  );

  // If HTTP / insecure context, display informative warning banner gracefully
  if (!hasMediaDevices && micWarning) {
    micWarning.style.display = 'block';
  }

  // Handle direct audio file upload (mobile voice memo / desktop recording)
  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => {
      fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      state.recordedBlob = file;
      audioPreview.src = URL.createObjectURL(file);
      audioPreview.style.display = 'block';
      submitBtn.disabled = false;
      timerDisplay.textContent = 'Yüklendi';

      const existingNotice = document.getElementById('speaking-file-info-badge');
      if (existingNotice) existingNotice.remove();

      const badge = document.createElement('div');
      badge.id = 'speaking-file-info-badge';
      badge.className = 'badge badge-green';
      badge.style.marginTop = '10px';
      badge.textContent = `✓ Ses dosyası seçildi: ${file.name} (${Math.round(file.size / 1024)} KB)`;
      audioPreview.parentNode.insertBefore(badge, audioPreview.nextSibling);
    });
  }

  recordBtn.addEventListener('click', async () => {
    // If browser doesn't have getUserMedia (e.g. plain HTTP IP), trigger file picker seamlessly without throwing
    if (!hasMediaDevices) {
      if (micWarning) micWarning.style.display = 'block';
      if (fileInput) {
        fileInput.click();
      } else {
        alert('Tarayıcınız güvensiz HTTP bağlantısında mikrofon erişimini kısıtlamıştır. Lütfen ses dosyanızı yükleyin.');
      }
      return;
    }

    if (!state.isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.mediaRecorder = new MediaRecorder(stream);
        state.recordedChunks = [];

        state.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) state.recordedChunks.push(e.data);
        };

        state.mediaRecorder.onstop = () => {
          state.recordedBlob = new Blob(state.recordedChunks, { type: 'audio/webm' });
          audioPreview.src = URL.createObjectURL(state.recordedBlob);
          audioPreview.style.display = 'block';
          submitBtn.disabled = false;
        };

        state.mediaRecorder.start();
        state.isRecording = true;
        recordBtn.classList.add('recording');
        recordBtn.innerHTML = '⏹';

        let sec = 0;
        timerDisplay.textContent = '00:00';
        state.recordInterval = setInterval(() => {
          sec++;
          const m = String(Math.floor(sec / 60)).padStart(2, '0');
          const s = String(sec % 60).padStart(2, '0');
          timerDisplay.textContent = `${m}:${s}`;
        }, 1000);

      } catch (err) {
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          alert('Mikrofon erişim izni verilmedi. Tarayıcı ayarlarından izni açabilir veya doğrudan "Ses Dosyası Seç / Yükle" butonuyla ses kaydınızı yükleyebilirsiniz.');
        } else {
          alert('Mikrofon başlatılamadı: ' + err.message + '. Alternatif olarak ses dosyanızı yükleyebilirsiniz.');
        }
        if (micWarning) micWarning.style.display = 'block';
      }
    } else {
      if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
        state.mediaRecorder.stop();
      }
      state.isRecording = false;
      recordBtn.classList.remove('recording');
      recordBtn.innerHTML = '🎙️';
      clearInterval(state.recordInterval);
    }
  });

  submitBtn.addEventListener('click', async () => {
    if (!state.recordedBlob) return;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> AI Dinliyor & Analiz Ediyor...';

    const feedbackArea = document.getElementById('speaking-feedback-area');
    feedbackArea.innerHTML = '<div style="text-align:center; padding: 20px;"><span class="spinner"></span> Çok Modlu Gemini Ses Motoru konuşmanızı dinliyor ve Cambridge kriterleriyle puanlıyor...</div>';

    const filename = (state.recordedBlob instanceof File && state.recordedBlob.name) 
      ? state.recordedBlob.name 
      : 'speech_recording.webm';

    const formData = new FormData();
    formData.append('audio', state.recordedBlob, filename);
    formData.append('part', currentSpeakingPart);
    formData.append('mode', state.currentMode);
    formData.append('prompt_context', document.getElementById('speaking-cue-card-box').textContent);
    formData.append('user_email', state.currentUser.email);

    try {
      const res = await fetch('/api/evaluate/speaking', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (data.success) {
        feedbackArea.innerHTML = `
          <div class="feedback-container">
            <div class="score-hero">
              <div>
                <div style="text-transform: uppercase; font-size: 0.8rem; color: var(--text-dim);">${currentSpeakingPart} Speaking Score</div>
                <div class="score-val">Band ${data.score}</div>
              </div>
              <div class="badge badge-purple">Audio Verified</div>
            </div>
            ${formatMarkdown(data.feedback)}
          </div>
        `;
        loadAnalytics();
      } else {
        feedbackArea.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.error || 'Evaluation error'}</div>`;
      }
    } catch (e) {
      feedbackArea.innerHTML = `<div class="card" style="color: var(--accent-rose);">Network error: ${e.message}</div>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '🎧 Submit Recording to AI Examiner';
    }
  });
}

/* ================= Mistake Notebook (Yanlış Defteri) ================= */
async function loadMistakes() {
  const container = document.getElementById('mistakes-list-container');
  if (!container) return;

  try {
    const res = await fetch(`/api/user/mistakes?email=${encodeURIComponent(state.currentUser.email)}`);
    const data = await res.json();
    const mistakes = data.mistakes || [];

    const badgeElem = document.getElementById('badge-mistakes-count');
    if (badgeElem) badgeElem.textContent = mistakes.length;

    if (mistakes.length === 0) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 40px; color: var(--text-dim);">
          🎉 Tebrikler! Henüz kaydedilmiş bir yanlışınız bulunmuyor. Test çözdükçe yapay zeka hatalarınızı buraya analiz edecektir.
        </div>
      `;
      return;
    }

    container.innerHTML = mistakes.map(m => `
      <div class="mistake-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <span class="badge badge-rose">${m.module}</span>
          <span style="font-size: 0.75rem; color: var(--text-dim);">${m.date}</span>
        </div>
        <div class="mistake-q">${m.question_prompt}</div>
        <div class="mistake-answers-row">
          <div>Sizin Cevabınız: <span class="ans-wrong">${m.user_answer}</span></div>
          <div>Doğru Cevap: <span class="ans-right">${m.correct_answer}</span></div>
        </div>
        ${m.explanation ? `<div class="mistake-expl"><strong>Çözüm & Neden:</strong> ${m.explanation}</div>` : ''}
        ${m.trick_tip ? `<div class="mistake-trick">💡 <strong>Cambridge Taktik:</strong> ${m.trick_tip}</div>` : ''}
      </div>
    `).join('');
  } catch (err) {
    console.error('Mistakes load error:', err);
  }
}

/* ================= Masterclass & Tricks ================= */
async function loadTricks() {
  const container = document.getElementById('tricks-container');
  if (!container) return;

  try {
    const res = await fetch('/api/tricks');
    const data = await res.json();

    let html = '';
    for (const [moduleKey, mod] of Object.entries(data)) {
      html += `
        <div class="card" style="margin-bottom: 24px;">
          <div class="card-title">
            <div>${mod.title}</div>
          </div>
          <div class="card-desc">${mod.description}</div>
      `;

      mod.sections.forEach(sec => {
        const rulesList = sec.rules.map(r => `<li>${r}</li>`).join('');
        const exampleHtml = sec.example ? `
          <div class="trick-example-box" style="margin-top: 10px;">
            <div style="font-weight: 700; margin-bottom: 4px;">🔎 Örnek Vaka:</div>
            <div><em>Pasaj:</em> "${sec.example.passage}"</div>
            <div style="margin-top: 4px;"><em>Soru:</em> "${sec.example.question}"</div>
            <div style="margin-top: 4px; color: var(--accent-emerald);"><strong>Cevap:</strong> ${sec.example.answer}</div>
          </div>
        ` : '';

        html += `
          <div class="trick-block">
            <div class="trick-topic">
              <span>${sec.topic}</span>
              <span class="badge badge-amber">${sec.badge}</span>
            </div>
            <ul class="trick-list">${rulesList}</ul>
            ${exampleHtml}
          </div>
        `;
      });

      html += `</div>`;
    }

    container.innerHTML = html;
  } catch (err) {
    console.error('Tricks load error:', err);
  }
}

/* ================= Timers ================= */
function initTimers() {
  const writingTimerBtn = document.getElementById('btn-timer-writing');
  if (writingTimerBtn) {
    writingTimerBtn.addEventListener('click', () => toggleExamTimer('writing', 3600, 'timer-display-writing', writingTimerBtn));
  }

  const readingTimerBtn = document.getElementById('btn-timer-reading');
  if (readingTimerBtn) {
    readingTimerBtn.addEventListener('click', () => toggleExamTimer('reading', 3600, 'timer-display-reading', readingTimerBtn));
  }

  const prepTimerBtn = document.getElementById('btn-speaking-prep-timer');
  if (prepTimerBtn) {
    prepTimerBtn.addEventListener('click', () => toggleExamTimer('speakingPrep', 60, 'speaking-prep-display', prepTimerBtn));
  }
}

function toggleExamTimer(name, defaultSec, displayId, btnElem) {
  const t = state.timers[name];
  const display = document.getElementById(displayId);

  if (t.running) {
    clearInterval(t.interval);
    t.running = false;
    btnElem.textContent = '▶ Start Timer';
  } else {
    t.running = true;
    btnElem.textContent = '⏸ Pause';
    t.interval = setInterval(() => {
      if (t.remaining > 0) {
        t.remaining--;
        const m = String(Math.floor(t.remaining / 60)).padStart(2, '0');
        const s = String(t.remaining % 60).padStart(2, '0');
        if (display) display.textContent = `${m}:${s}`;
      } else {
        clearInterval(t.interval);
        t.running = false;
        alert(`Time is up for ${name}!`);
      }
    }, 1000);
  }
}

/* ================= Analytics & Personalized Mentor ================= */
async function loadAnalytics() {
  try {
    const res = await fetch(`/api/user/analytics?email=${encodeURIComponent(state.currentUser.email)}`);
    const data = await res.json();

    document.getElementById('stat-total-tests').textContent = data.total_tests;
    document.getElementById('stat-overall-avg').textContent = data.overall_average ? data.overall_average.toFixed(1) : '0.0';
    document.getElementById('stat-writing-avg').textContent = data.module_averages.Writing ? data.module_averages.Writing.toFixed(1) : '-';
    document.getElementById('stat-speaking-avg').textContent = data.module_averages.Speaking ? data.module_averages.Speaking.toFixed(1) : '-';

    drawScoreChart(data.module_averages);

    const tableBody = document.getElementById('history-table-body');
    if (tableBody) {
      if (!data.history || data.history.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 20px;">Henüz çözülmüş test kaydınız bulunmuyor.</td></tr>';
      } else {
        tableBody.innerHTML = data.history.map(row => `
          <tr>
            <td>${row.date}</td>
            <td><span class="badge ${row.mode === 'cyber' ? 'badge-cyan' : 'badge-amber'}">${row.mode.toUpperCase()}</span></td>
            <td>${row.module}</td>
            <td>${row.task_type}</td>
            <td><strong style="color: var(--accent-cyan); font-size: 1.05rem;">${row.score.toFixed(1)}</strong></td>
          </tr>
        `).join('');
      }
    }
  } catch (err) {
    console.error('Analytics load error:', err);
  }
}

function drawScoreChart(averages) {
  const canvas = document.getElementById('analytics-chart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  const modules = ['Listening', 'Reading', 'Writing', 'Speaking'];
  const colors = ['#38bdf8', '#818cf8', '#34d399', '#fb7185'];
  const barWidth = 44;
  const spacing = (w - (barWidth * modules.length)) / (modules.length + 1);

  modules.forEach((mod, idx) => {
    const score = averages[mod] || 0;
    const maxScore = 9.0;
    const barHeight = (score / maxScore) * (h - 70);
    const x = spacing + idx * (barWidth + spacing);
    const y = h - 35 - barHeight;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.fillRect(x, 20, barWidth, h - 55);

    ctx.fillStyle = colors[idx];
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barHeight, [6, 6, 0, 0]);
    ctx.fill();

    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(score > 0 ? score.toFixed(1) : '0.0', x + barWidth / 2, y - 6);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px Inter, sans-serif';
    ctx.fillText(mod, x + barWidth / 2, h - 14);
  });
}

// AI Personalized Mentor Plan Generator
const mentorBtn = document.getElementById('btn-generate-mentor');
if (mentorBtn) {
  mentorBtn.addEventListener('click', async () => {
    mentorBtn.disabled = true;
    mentorBtn.innerHTML = '<span class="spinner"></span> Yanlışlarınız Analiz Ediliyor...';

    const reportArea = document.getElementById('mentor-report-area');
    reportArea.innerHTML = '<div style="text-align: center; padding: 25px;"><span class="spinner"></span> Yanlış Defteriniz ve sınav geçmişiniz incelenerek size özel 35 dakikalık telafi reçetesi oluşturuluyor...</div>';

    try {
      const res = await fetch('/api/mentor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mode: state.currentMode,
          user_email: state.currentUser.email
        })
      });
      const data = await res.json();
      reportArea.innerHTML = `
        <div class="feedback-container">
          <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px; font-size: 1.15rem;">
            🛡️ ${state.currentUser.name} İçin Kişiselleştirilmiş IELTS Strateji Raporu
          </div>
          ${formatMarkdown(data.report)}
        </div>
      `;
    } catch (e) {
      reportArea.innerHTML = `<div class="card" style="color: var(--accent-rose);">Mentor error: ${e.message}</div>`;
    } finally {
      mentorBtn.disabled = false;
      mentorBtn.innerHTML = '🔄 Kişisel Telafi Planımı Güncelle';
    }
  });
}

/* ================= Helpers ================= */
function displayGradingResult(containerId, data, moduleName) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const itemsHtml = data.breakdown.map(item => `
    <div style="padding: 10px; margin-bottom: 8px; border-radius: 8px; background: ${item.is_correct ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)'}; border: 1px solid ${item.is_correct ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)'};">
      <div style="font-weight: 600; font-size: 0.9rem;">${item.prompt}</div>
      <div style="font-size: 0.85rem; margin-top: 4px;">
        Cevabınız: <strong>${item.user_answer}</strong> | Doğru: <strong style="color: var(--accent-emerald);">${item.correct_answer}</strong>
        ${item.is_correct ? '✅' : '❌ (Yanlış Defterine Eklendi)'}
      </div>
      ${item.explanation ? `<div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 4px;"><em>${item.explanation}</em></div>` : ''}
    </div>
  `).join('');

  container.innerHTML = `
    <div class="feedback-container">
      <div class="score-hero">
        <div>
          <div style="text-transform: uppercase; font-size: 0.8rem; color: var(--text-dim);">${moduleName} Band Skoru</div>
          <div class="score-val">Band ${data.band_score}</div>
        </div>
        <div class="badge ${data.correct_count >= 3 ? 'badge-emerald' : 'badge-amber'}">${data.correct_count} / ${data.total} Doğru</div>
      </div>
      <div style="margin-top: 16px;">${itemsHtml}</div>
    </div>
  `;
}

function formatMarkdown(md) {
  if (!md) return '';
  return md
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/^- (.*$)/gim, '<li>$1</li>')
    .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    .replace(/\n\n/gim, '<br><br>');
}

/* ================= Database (Soru ve Sınav Veritabanı) ================= */
let bankQuestions = [];
let bankViewMode = 'grouped'; // 'grouped' (Sınav bazlı) or 'table' (Tablo)

async function loadQuestionBank() {
  const groupedContainer = document.getElementById('bank-grouped-container');
  const tbody = document.getElementById('bank-table-body');
  
  if (groupedContainer) {
    groupedContainer.innerHTML = '<div style="text-align: center; padding: 30px;"><span class="spinner"></span> Veritabanındaki sınavlar ve sorular yükleniyor...</div>';
  }
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 25px;"><span class="spinner"></span> Veritabanı yükleniyor...</td></tr>';
  }

  try {
    const res = await fetch('/api/questions');
    const data = await res.json();
    bankQuestions = data.questions || [];

    const badge = document.getElementById('bank-total-count-badge');
    if (badge) badge.textContent = `${data.total || bankQuestions.length} Soru Kayıtlı`;

    renderQuestionBank();
  } catch (err) {
    if (groupedContainer) {
      groupedContainer.innerHTML = `<div class="card" style="text-align: center; color: var(--accent-rose); padding: 20px;">Hata: ${err.message}</div>`;
    }
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--accent-rose); padding: 20px;">Hata: ${err.message}</td></tr>`;
    }
  }
}

function renderQuestionBank() {
  const searchInput = (document.getElementById('bank-search-input')?.value || '').toLowerCase().trim();
  const moduleFilter = document.getElementById('bank-filter-module')?.value || 'all';
  const modeFilter = document.getElementById('bank-filter-mode')?.value || 'all';

  const filtered = bankQuestions.filter(q => {
    if (moduleFilter !== 'all' && q.module !== moduleFilter) return false;
    if (modeFilter !== 'all' && q.mode !== modeFilter) return false;
    if (searchInput) {
      const haystack = `${q.id} ${q.source} ${q.prompt} ${q.answer} ${q.q_type} ${q.explanation}`.toLowerCase();
      if (!haystack.includes(searchInput)) return false;
    }
    return true;
  });

  const badge = document.getElementById('bank-total-count-badge');
  if (badge) {
    badge.textContent = `${filtered.length} / ${bankQuestions.length} Soru Gösteriliyor`;
  }

  renderQuestionBankGrouped(filtered);
  renderQuestionBankTable(filtered);
}

function renderQuestionBankGrouped(filtered) {
  const container = document.getElementById('bank-grouped-container');
  if (!container) return;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 35px; color: var(--text-dim);">
        🔍 Arama kriterinize uygun sınav veya soru bulunamadı.
      </div>
    `;
    return;
  }

  // Group questions by unique source / passage title
  const groupsMap = new Map();
  filtered.forEach(q => {
    const key = `${q.module}:::${q.source}`;
    if (!groupsMap.has(key)) {
      groupsMap.set(key, {
        module: q.module,
        mode: q.mode,
        source: q.source,
        passage_or_script: q.passage_or_script,
        questions: []
      });
    }
    groupsMap.get(key).questions.push(q);
  });

  const groups = Array.from(groupsMap.values());

  container.innerHTML = groups.map(grp => {
    const isReading = grp.module === 'Reading';
    const isListening = grp.module === 'Listening';
    const passageLabel = isReading ? '📖 Okuma Metnini (Passage Text) İncele' : (isListening ? '🎧 Dinleme Senaryosu (Audio Script) Metnini İncele' : '📄 Sınav / Görev Detayı');

    const questionsHtml = grp.questions.map((q, idx) => {
      let answerColor = '#10b981'; // green
      if (q.answer === 'FALSE') answerColor = '#f43f5e';
      else if (q.answer === 'NOT GIVEN') answerColor = '#f59e0b';
      else if (q.module === 'Writing' || q.module === 'Speaking') answerColor = '#38bdf8';

      return `
        <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid var(--border-glass); border-left: 3px solid ${answerColor}; padding: 12px 14px; border-radius: 6px; margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
            <div style="font-weight: 600; color: #ffffff; font-size: 0.92rem; line-height: 1.5; flex: 1;">
              <code style="color: var(--accent-cyan); font-size: 0.78rem; font-weight: 700; margin-right: 4px;">[${escapeHtml(q.id)}]</code>
              ${escapeHtml(q.prompt)}
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="badge badge-purple" style="font-size: 0.7rem;">${escapeHtml(q.q_type)}</span>
              <button class="btn btn-outline btn-view-question" data-qid="${escapeHtml(q.id)}" style="padding: 2px 8px; font-size: 0.72rem; min-height: 24px; border-color: var(--accent-cyan); color: var(--accent-cyan);">
                🔍 İncele
              </button>
            </div>
          </div>

          <!-- Prominent Answer Box -->
          <div style="display: flex; align-items: center; gap: 10px; margin-top: 8px; flex-wrap: wrap;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #10b981; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); padding: 4px 12px; border-radius: 4px; display: inline-flex; align-items: center; gap: 6px;">
              <span>✅ Doğru Cevap:</span>
              <span style="color: #ffffff; font-size: 0.92rem; font-weight: 800;">${escapeHtml(q.answer)}</span>
            </div>
            ${q.options && q.options.length ? `
              <div style="font-size: 0.76rem; color: var(--text-dim);">
                Seçenekler: ${q.options.map(o => `<code style="background: rgba(255,255,255,0.06); padding: 1px 6px; border-radius: 3px; margin: 0 2px; color: #cbd5e1;">${escapeHtml(o)}</code>`).join(' ')}
              </div>
            ` : ''}
          </div>

          ${q.explanation ? `
            <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 6px; line-height: 1.5; background: rgba(0,0,0,0.22); padding: 6px 10px; border-radius: 4px;">
              💡 <strong style="color: var(--accent-cyan);">Çözüm Açıklaması:</strong> ${escapeHtml(q.explanation)}
              ${q.trick_tip ? `<br>🎯 <strong style="color: var(--accent-amber);">Cambridge Taktiği:</strong> ${escapeHtml(q.trick_tip)}` : ''}
            </div>
          ` : ''}
        </div>
      `;
    }).join('');

    return `
      <div class="card" style="border: 1px solid var(--border-glass); background: rgba(15, 23, 42, 0.65); padding: 18px; border-radius: 8px; margin-bottom: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; border-bottom: 1px solid var(--border-glass); padding-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span class="badge ${getModuleBadge(grp.module)}">${grp.module}</span>
            <span class="badge ${grp.mode === 'academic' ? 'badge-amber' : 'badge-cyan'}">${grp.mode === 'academic' ? 'Cambridge Academic' : 'Adli Bilişim & Cyber'}</span>
            <strong style="color: #ffffff; font-size: 1.05rem;">${escapeHtml(grp.source)}</strong>
          </div>
          <span class="badge badge-emerald" style="font-size: 0.8rem; font-weight: 700;">
            ${grp.questions.length} Soru & Cevabın Tamamı
          </span>
        </div>

        ${grp.passage_or_script ? `
          <details style="margin-bottom: 14px; background: rgba(0,0,0,0.25); border: 1px solid var(--border-glass); border-radius: 6px; padding: 8px 12px;">
            <summary style="cursor: pointer; font-size: 0.82rem; color: var(--accent-cyan); font-weight: 600;">
              ${passageLabel} (Tıklayarak Aç / Kapat)
            </summary>
            <div style="margin-top: 10px; font-size: 0.85rem; line-height: 1.6; color: var(--text-muted); max-height: 240px; overflow-y: auto; white-space: pre-wrap; background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 4px;">
              ${escapeHtml(grp.passage_or_script)}
            </div>
          </details>
        ` : ''}

        <div style="display: flex; flex-direction: column;">
          ${questionsHtml}
        </div>
      </div>
    `;
  }).join('');

  // Attach modal click events for grouped cards
  container.querySelectorAll('.btn-view-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const qid = btn.getAttribute('data-qid');
      openQuestionDetailModal(qid);
    });
  });
}

function renderQuestionBankTable(filtered) {
  const tbody = document.getElementById('bank-table-body');
  if (!tbody) return;

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 25px; color: var(--text-dim);">Filtreye uygun soru bulunamadı.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(q => `
    <tr>
      <td><code style="font-size: 0.78rem; color: var(--accent-cyan); font-weight: 600;">${escapeHtml(q.id)}</code></td>
      <td><span class="badge ${getModuleBadge(q.module)}">${escapeHtml(q.module)}</span></td>
      <td><strong style="color: #ffffff; font-size: 0.86rem;">${escapeHtml(q.source)}</strong></td>
      <td><span class="badge badge-purple" style="font-size: 0.72rem;">${escapeHtml(q.q_type)}</span></td>
      <td style="max-width: 300px; font-size: 0.84rem; line-height: 1.4;">
        ${escapeHtml(q.prompt.length > 90 ? q.prompt.substring(0, 90) + '...' : q.prompt)}
      </td>
      <td>
        <span style="color: #10b981; font-weight: 800; font-size: 0.88rem; background: rgba(16, 185, 129, 0.12); padding: 3px 8px; border-radius: 4px; display: inline-block;">
          ${escapeHtml(q.answer)}
        </span>
      </td>
      <td style="text-align: center;">
        <button class="btn btn-outline btn-view-question" data-qid="${escapeHtml(q.id)}" style="padding: 4px 8px; font-size: 0.76rem; border-color: var(--accent-cyan); color: var(--accent-cyan);">
          🔍 İncele
        </button>
      </td>
    </tr>
  `).join('');

  // Attach click events for table view
  tbody.querySelectorAll('.btn-view-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const qid = btn.getAttribute('data-qid');
      openQuestionDetailModal(qid);
    });
  });
}

function openQuestionDetailModal(qid) {
  const q = bankQuestions.find(item => item.id === qid);
  if (!q) return;

  const modal = document.getElementById('modal-question-detail');
  if (!modal) return;

  // Badges
  const badgesBox = document.getElementById('qdetail-modal-badges');
  badgesBox.innerHTML = `
    <span class="badge ${getModuleBadge(q.module)}">${escapeHtml(q.module)}</span>
    <span class="badge ${q.mode === 'academic' ? 'badge-amber' : 'badge-cyan'}">${q.mode === 'academic' ? 'Cambridge Academic' : 'Adli Bilişim & Jean Monnet'}</span>
    <span class="badge badge-purple">${escapeHtml(q.q_type)}</span>
  `;

  // Source & Prompt
  document.getElementById('qdetail-modal-source').textContent = q.source;
  document.getElementById('qdetail-modal-prompt').textContent = q.prompt;

  // Options
  const optBox = document.getElementById('qdetail-modal-options-box');
  const optContainer = document.getElementById('qdetail-modal-options');
  if (q.options && Array.isArray(q.options) && q.options.length > 0) {
    optBox.style.display = 'block';
    optContainer.innerHTML = q.options.map(opt => `
      <span class="badge" style="background: rgba(30, 41, 59, 0.8); border: 1px solid var(--border-glass); color: #e2e8f0; font-size: 0.8rem; padding: 4px 10px;">
        ${escapeHtml(opt)}
      </span>
    `).join('');
  } else {
    optBox.style.display = 'none';
    optContainer.innerHTML = '';
  }

  // Answer
  document.getElementById('qdetail-modal-answer').innerHTML = `
    <span>${escapeHtml(q.answer || 'Model Değerlendirme / Serbest Yanıt')}</span>
  `;

  // Explanation & Tips
  let explanationHtml = escapeHtml(q.explanation || 'Bu soru için ek açıklama bulunmamaktadır.');
  if (q.trick_tip) {
    explanationHtml += `<br><br><strong style="color: var(--accent-amber);">💡 Cambridge Sınav Taktiği:</strong> ${escapeHtml(q.trick_tip)}`;
  }
  document.getElementById('qdetail-modal-explanation').innerHTML = explanationHtml;

  // Passage / Audio Script
  const passageEl = document.getElementById('qdetail-modal-passage');
  const togglePassageBtn = document.getElementById('btn-toggle-passage-content');
  passageEl.textContent = q.passage_or_script || 'Bağlam metni veya ses senaryosu kayıtlı değil.';
  passageEl.style.display = 'none'; // closed by default
  if (togglePassageBtn) togglePassageBtn.textContent = 'Metni Göster';

  // Companion Questions in this Exam
  const compBox = document.getElementById('qdetail-modal-companion-box');
  const compList = document.getElementById('qdetail-modal-companion-list');
  const companions = bankQuestions.filter(item => item.source === q.source && item.id !== q.id);

  if (companions.length > 0 && compBox && compList) {
    compBox.style.display = 'block';
    compList.innerHTML = companions.map(cq => `
      <div style="background: rgba(15, 23, 42, 0.55); border: 1px solid var(--border-glass); padding: 8px 12px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; gap: 8px;">
        <div style="font-size: 0.84rem; color: #ffffff; flex: 1;">
          <code style="color: var(--accent-cyan); font-weight: 700;">[${escapeHtml(cq.id)}]</code> ${escapeHtml(cq.prompt)}
        </div>
        <div style="font-weight: 800; color: #10b981; font-size: 0.85rem; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); padding: 3px 10px; border-radius: 4px; white-space: nowrap;">
          ✅ ${escapeHtml(cq.answer)}
        </div>
      </div>
    `).join('');
  } else if (compBox) {
    compBox.style.display = 'none';
  }

  modal.classList.add('active');
}

function initQuestionBankEvents() {
  const searchInput = document.getElementById('bank-search-input');
  if (searchInput) searchInput.addEventListener('input', renderQuestionBank);

  const modFilter = document.getElementById('bank-filter-module');
  if (modFilter) modFilter.addEventListener('change', renderQuestionBank);

  const modeFilter = document.getElementById('bank-filter-mode');
  if (modeFilter) modeFilter.addEventListener('change', renderQuestionBank);

  const refreshBtn = document.getElementById('btn-refresh-bank');
  if (refreshBtn) refreshBtn.addEventListener('click', loadQuestionBank);

  const gotoBankBtn = document.getElementById('btn-goto-bank');
  if (gotoBankBtn) gotoBankBtn.addEventListener('click', () => switchModule('bank'));

  // View Switcher Buttons
  const btnGrouped = document.getElementById('btn-bank-view-grouped');
  const btnTable = document.getElementById('btn-bank-view-table');
  const grpContainer = document.getElementById('bank-grouped-container');
  const tblContainer = document.getElementById('bank-table-container');

  if (btnGrouped && btnTable && grpContainer && tblContainer) {
    btnGrouped.addEventListener('click', () => {
      bankViewMode = 'grouped';
      btnGrouped.className = 'btn btn-ai-magic';
      btnTable.className = 'btn btn-outline';
      grpContainer.style.display = 'flex';
      tblContainer.style.display = 'none';
    });

    btnTable.addEventListener('click', () => {
      bankViewMode = 'table';
      btnTable.className = 'btn btn-ai-magic';
      btnGrouped.className = 'btn btn-outline';
      tblContainer.style.display = 'block';
      grpContainer.style.display = 'none';
    });
  }

  // Toggle Passage Content inside modal
  const togglePassageBtn = document.getElementById('btn-toggle-passage-content');
  const passageEl = document.getElementById('qdetail-modal-passage');
  if (togglePassageBtn && passageEl) {
    togglePassageBtn.addEventListener('click', () => {
      if (passageEl.style.display === 'none') {
        passageEl.style.display = 'block';
        togglePassageBtn.textContent = 'Metni Gizle';
      } else {
        passageEl.style.display = 'none';
        togglePassageBtn.textContent = 'Metni Göster';
      }
    });
  }

  // Close Detail Modal
  const closeBtn1 = document.getElementById('btn-close-qdetail');
  const closeBtn2 = document.getElementById('btn-close-qdetail-footer');
  const modal = document.getElementById('modal-question-detail');
  
  if (closeBtn1 && modal) closeBtn1.addEventListener('click', () => modal.classList.remove('active'));
  if (closeBtn2 && modal) closeBtn2.addEventListener('click', () => modal.classList.remove('active'));
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }
}

function getModuleBadge(mod) {
  if (mod === 'Reading') return 'badge-cyan';
  if (mod === 'Listening') return 'badge-emerald';
  if (mod === 'Writing') return 'badge-purple';
  if (mod === 'Speaking') return 'badge-amber';
  return 'badge-cyan';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
