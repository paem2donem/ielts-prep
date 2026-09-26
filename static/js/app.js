/* ===================================================================
   ForenSync Academy: IELTS & Cyber Prep - Frontend Engine (ES6)
   Full Interactive Modules: Listening, Reading, Writing, Speaking, Mentor
   =================================================================== */

// Global State
const state = {
  currentMode: 'cyber', // 'cyber' or 'academic'
  currentModule: 'writing',
  examData: null,
  
  // Timers
  timers: {
    writing: { remaining: 3600, interval: null, running: false },
    reading: { remaining: 3600, interval: null, running: false },
    speakingPrep: { remaining: 60, interval: null, running: false },
    speakingRecord: { remaining: 120, interval: null, running: false }
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
  initNavigation();
  initModeSwitcher();
  initTimers();
  initWritingModule();
  initSpeakingRecorder();
  
  // Initial load of exam data
  await switchMode('cyber');
  loadAnalytics();
});

/* ================= Navigation Handler ================= */
function initNavigation() {
  const navButtons = document.querySelectorAll('[data-module-target]');
  
  navButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = btn.getAttribute('data-module-target');
      switchModule(target);
    });
  });
}

function switchModule(moduleName) {
  state.currentModule = moduleName;

  // Update UI Panels
  document.querySelectorAll('.panel-view').forEach(panel => {
    panel.classList.remove('active');
  });
  const targetPanel = document.getElementById(`panel-${moduleName}`);
  if (targetPanel) targetPanel.classList.add('active');

  // Update Nav Buttons
  document.querySelectorAll('[data-module-target]').forEach(btn => {
    if (btn.getAttribute('data-module-target') === moduleName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (moduleName === 'mentor') {
    loadAnalytics();
  }
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

  // Toggle active button
  document.getElementById('btn-mode-cyber').classList.toggle('active', mode === 'cyber');
  document.getElementById('btn-mode-academic').classList.toggle('active', mode === 'academic');

  // Fetch Exam Data
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

/* ================= Listening Module ================= */
let currentListeningSection = 'section_1';

function renderListeningModule() {
  const listeningData = state.examData.listening;
  if (!listeningData) return;

  const section = listeningData[currentListeningSection] || listeningData['section_1'];
  
  document.getElementById('listening-section-title').textContent = section.title;
  document.getElementById('listening-section-intro').textContent = section.intro;

  // Render Questions
  const qContainer = document.getElementById('listening-questions-container');
  qContainer.innerHTML = '';

  section.questions.forEach((q, idx) => {
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

  // Prepare Audio
  loadListeningAudio(state.currentMode, currentListeningSection);
}

async function loadListeningAudio(mode, sectionId) {
  const playBtn = document.getElementById('btn-play-listening');
  const trackTitle = document.getElementById('track-title');
  trackTitle.textContent = 'Audio loading...';

  try {
    const res = await fetch(`/api/audio/listening/${mode}/${sectionId}`);
    const data = await res.json();

    if (data.has_audio && data.audio_url) {
      state.audioElement.src = data.audio_url;
      trackTitle.textContent = 'Ready to play (Authentic Gemini Audio)';
    } else {
      trackTitle.textContent = 'Audio script ready (Native Audio Engine)';
      state.audioElement.src = '';
    }
  } catch (e) {
    trackTitle.textContent = 'Audio stream ready';
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
      // Speech synthesis fallback
      const section = state.examData.listening[currentListeningSection];
      if (window.speechSynthesis && section) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(section.audio_script);
        utterance.lang = 'en-GB';
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
        alert('Playing audio via speech synthesis engine...');
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
          answers: answers
        })
      });

      const data = await res.json();
      displayGradingResult('listening-feedback-area', data, 'Listening');
    } catch (e) {
      alert('Grading error: ' + e.message);
    } finally {
      submitListeningBtn.disabled = false;
      submitListeningBtn.innerHTML = '📝 Submit & Grade Listening';
    }
  });
}

/* ================= Reading Module ================= */
function renderReadingModule() {
  const readingData = state.examData.reading;
  if (!readingData) return;

  const passage = readingData.passage_1;
  document.getElementById('reading-passage-title').textContent = passage.title;
  document.getElementById('reading-passage-text').innerHTML = passage.text.split('\n\n').map(p => `<p>${p}</p>`).join('');

  const qContainer = document.getElementById('reading-questions-container');
  qContainer.innerHTML = '';

  passage.questions.forEach((q, idx) => {
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

// Mobile Reading View Toggle (Passage vs Questions)
const tabPassage = document.getElementById('mobile-toggle-passage');
const tabQuestions = document.getElementById('mobile-toggle-questions');
const passageBox = document.getElementById('reading-passage-column');
const questionsBox = document.getElementById('reading-questions-column');

if (tabPassage && tabQuestions) {
  tabPassage.addEventListener('click', () => {
    tabPassage.classList.add('active');
    tabQuestions.classList.remove('active');
    passageBox.style.display = 'block';
    questionsBox.style.display = 'none';
  });

  tabQuestions.addEventListener('click', () => {
    tabQuestions.classList.add('active');
    tabPassage.classList.remove('active');
    passageBox.style.display = 'none';
    questionsBox.style.display = 'block';
  });
}

// Grade Reading
const submitReadingBtn = document.getElementById('btn-submit-reading');
if (submitReadingBtn) {
  submitReadingBtn.addEventListener('click', async () => {
    const passage = state.examData.reading.passage_1;
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
          answers: answers
        })
      });

      const data = await res.json();
      displayGradingResult('reading-feedback-area', data, 'Reading');
    } catch (e) {
      alert('Grading error: ' + e.message);
    } finally {
      submitReadingBtn.disabled = false;
      submitReadingBtn.innerHTML = '📝 Submit & Grade Reading';
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

  // Word count tracker
  essayInput.addEventListener('input', () => {
    const text = essayInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const minWords = currentWritingTask === 'Task 1' ? 150 : 250;

    const countElem = document.getElementById('writing-word-count');
    countElem.textContent = `${words} / ${minWords} words`;

    if (words >= minWords) {
      countElem.style.color = 'var(--accent-emerald)';
    } else {
      countElem.style.color = 'var(--text-muted)';
    }
  });

  // Submit Writing
  const submitWritingBtn = document.getElementById('btn-submit-writing');
  submitWritingBtn.addEventListener('click', async () => {
    const essayText = essayInput.value;
    const promptCtx = document.getElementById('writing-prompt-text').textContent;

    submitWritingBtn.disabled = true;
    submitWritingBtn.innerHTML = '<span class="spinner"></span> AI Examiner Analyzing...';

    const feedbackArea = document.getElementById('writing-feedback-area');
    feedbackArea.innerHTML = '<div style="text-align:center; padding: 20px;"><span class="spinner"></span> Cambridge & Jean Monnet Examiner evaluating your essay...</div>';

    try {
      const res = await fetch('/api/evaluate/writing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          essay_text: essayText,
          task_type: currentWritingTask,
          mode: state.currentMode,
          prompt_context: promptCtx
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
      // Start Recording
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

        // Start timer
        let sec = 0;
        timerDisplay.textContent = '00:00';
        state.recordInterval = setInterval(() => {
          sec++;
          const m = String(Math.floor(sec / 60)).padStart(2, '0');
          const s = String(sec % 60).padStart(2, '0');
          timerDisplay.textContent = `${m}:${s}`;
        }, 1000);

      } catch (err) {
        alert('Microphone access denied or not available: ' + err.message);
      }
    } else {
      // Stop Recording
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

/* ================= Timer System ================= */
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

/* ================= Analytics & AI Mentor ================= */
async function loadAnalytics() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();

    document.getElementById('stat-total-tests').textContent = data.total_tests;
    document.getElementById('stat-overall-avg').textContent = data.overall_average ? data.overall_average.toFixed(1) : '0.0';
    document.getElementById('stat-writing-avg').textContent = data.module_averages.Writing ? data.module_averages.Writing.toFixed(1) : '-';
    document.getElementById('stat-speaking-avg').textContent = data.module_averages.Speaking ? data.module_averages.Speaking.toFixed(1) : '-';

    // Draw Radar / Bar chart on canvas
    drawScoreChart(data.module_averages);

    // History Table
    const tableBody = document.getElementById('history-table-body');
    if (tableBody) {
      if (!data.history || data.history.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 20px;">No test submissions yet.</td></tr>';
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

    // Background bar
    ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.fillRect(x, 20, barWidth, h - 55);

    // Score bar
    ctx.fillStyle = colors[idx];
    ctx.beginPath();
    ctx.roundRect(x, y, barWidth, barHeight, [6, 6, 0, 0]);
    ctx.fill();

    // Score label on top
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(score > 0 ? score.toFixed(1) : '0.0', x + barWidth / 2, y - 6);

    // Module name below
    ctx.fillStyle = '#94a3b8';
    ctx.font = '11px Inter, sans-serif';
    ctx.fillText(mod, x + barWidth / 2, h - 14);
  });
}

// AI Mentor Plan Generator
const mentorBtn = document.getElementById('btn-generate-mentor');
if (mentorBtn) {
  mentorBtn.addEventListener('click', async () => {
    mentorBtn.disabled = true;
    mentorBtn.innerHTML = '<span class="spinner"></span> AI Coach Analyzing Your History...';

    const reportArea = document.getElementById('mentor-report-area');
    reportArea.innerHTML = '<div style="text-align: center; padding: 25px;"><span class="spinner"></span> Compiling Cambridge & Europol study plan tailored to your weak points...</div>';

    try {
      const res = await fetch('/api/mentor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: state.currentMode })
      });
      const data = await res.json();
      reportArea.innerHTML = `
        <div class="feedback-container">
          <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px; font-size: 1.15rem;">
            🛡️ Daily Action Plan & Strategy Report
          </div>
          ${formatMarkdown(data.report)}
        </div>
      `;
    } catch (e) {
      reportArea.innerHTML = `<div class="card" style="color: var(--accent-rose);">Mentor error: ${e.message}</div>`;
    } finally {
      mentorBtn.disabled = false;
      mentorBtn.innerHTML = '🔄 Update Today\'s AI Action Plan';
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
        Your answer: <strong>${item.user_answer}</strong> | Correct: <strong style="color: var(--accent-emerald);">${item.correct_answer}</strong>
        ${item.is_correct ? '✅' : '❌'}
      </div>
      ${item.explanation ? `<div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 4px;"><em>${item.explanation}</em></div>` : ''}
    </div>
  `).join('');

  container.innerHTML = `
    <div class="feedback-container">
      <div class="score-hero">
        <div>
          <div style="text-transform: uppercase; font-size: 0.8rem; color: var(--text-dim);">${moduleName} Band Score</div>
          <div class="score-val">Band ${data.band_score}</div>
        </div>
        <div class="badge ${data.correct_count >= 3 ? 'badge-emerald' : 'badge-amber'}">${data.correct_count} / ${data.total} Correct</div>
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
