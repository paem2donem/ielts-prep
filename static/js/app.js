/* ===================================================================
   ForenSync Academy: IELTS & Cyber Prep - Frontend Engine (v3.0)
   Full Interactive Modules: Dynamic AI Generator, User Profiles, 
   Error Notebook, Cambridge Tricks, Timers & Analytics
   =================================================================== */

// Global State
const state = {
  currentUser: {
    email: localStorage.getItem('forensync_user_email') || 'paem2.donem@gmail.com',
    name: localStorage.getItem('forensync_user_name') || 'Aday'
  },
  currentMode: 'cyber', // 'cyber' or 'academic'
  currentModule: 'writing',
  examData: null,
  activeCustomPassage: null,

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

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', async () => {
  initAuthUI();
  initNavigation();
  initModeSwitcher();
  initTimers();
  initWritingModule();
  initSpeakingRecorder();
  initDynamicGenerators();
  
  // Initial load
  await switchMode('cyber');
  loadAnalytics();
  loadTricks();
  loadMistakes();
});

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
          renderCustomReadingPassage(data.data);
          alert('✨ Yeni Cambridge IELTS Okuma Pasajı ve Soruları başarıyla üretildi!');
        }
      } catch (e) {
        alert('Üretim hatası: ' + e.message);
      } finally {
        btnGenReading.disabled = false;
        btnGenReading.innerHTML = '✨ Yapay Zeka ile Yeni Pasaj Üret';
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
}

/* ================= Reading Module ================= */
function renderReadingModule() {
  if (state.activeCustomPassage) {
    renderCustomReadingPassage(state.activeCustomPassage);
    return;
  }
  const readingData = state.examData.reading;
  if (!readingData) return;

  const passage = readingData.passage_1;
  document.getElementById('reading-passage-title').textContent = passage.title;
  document.getElementById('reading-passage-text').innerHTML = passage.text.split('\n\n').map(p => `<p>${p}</p>`).join('');

  renderReadingQuestions(passage.questions);
}

function renderCustomReadingPassage(passage) {
  document.getElementById('reading-passage-title').innerHTML = `✨ [AI Generated] ${passage.title}`;
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
    const passage = state.activeCustomPassage || state.examData.reading.passage_1;
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
          passage_id: 'passage_1',
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
      submitReadingBtn.innerHTML = '📝 Submit & Grade Reading';
    }
  });
}

/* ================= Listening Module ================= */
let currentListeningSection = 'section_1';

function renderListeningModule() {
  const listeningData = state.examData.listening;
  if (!listeningData) return;

  const section = listeningData[currentListeningSection] || listeningData['section_1'];
  
  document.getElementById('listening-section-title').textContent = section.title;
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
      const section = state.examData.listening[currentListeningSection];
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
    const section = state.examData.listening[currentListeningSection];
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
    submitListeningBtn.innerHTML = '<span class="spinner"></span> Grading...';

    try {
      const res = await fetch('/api/grade/listening', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: state.currentMode,
          section_id: currentListeningSection,
          answers: answers,
          user_email: state.currentUser.email
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
  const speakingData = state.examData.speaking;
  if (!speakingData) return;

  const cueCardElem = document.getElementById('speaking-cue-card-box');
  const partData = speakingData.part_2;
  cueCardElem.innerHTML = `
    <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 8px;">IELTS Speaking Part 2 - Cue Card:</div>
    <div class="cue-card">${partData.cue_card.trim().replace(/\n/g, '<br>')}</div>
  `;
}

function initSpeakingRecorder() {
  const recordBtn = document.getElementById('btn-record-speaking');
  const audioPreview = document.getElementById('speaking-audio-preview');
  const submitBtn = document.getElementById('btn-submit-speaking');
  const timerDisplay = document.getElementById('speaking-record-time');

  recordBtn.addEventListener('click', async () => {
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
        alert('Microphone access denied: ' + err.message);
      }
    } else {
      state.mediaRecorder.stop();
      state.isRecording = false;
      recordBtn.classList.remove('recording');
      recordBtn.innerHTML = '🎙️';
      clearInterval(state.recordInterval);
    }
  });

  submitBtn.addEventListener('click', async () => {
    if (!state.recordedBlob) return;

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> AI Listening & Analyzing...';

    const feedbackArea = document.getElementById('speaking-feedback-area');
    feedbackArea.innerHTML = '<div style="text-align:center; padding: 20px;"><span class="spinner"></span> Multimodal Gemini Speech Engine transcribing and scoring your speech...</div>';

    const formData = new FormData();
    formData.append('audio', state.recordedBlob, 'speech_recording.webm');
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
