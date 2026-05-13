const API_BASE = "http://127.0.0.1:8000/api";

let questions = [];
let currentIndex = 0;
let score = 0;
let currentQuestion = null;
let hintsShown = 0;

// Setup Marked.js with syntax highlighting
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
    }
});

// DOM Elements
const views = {
    setup: document.getElementById('setup-view'),
    training: document.getElementById('training-view'),
    summary: document.getElementById('summary-view')
};

// Setup Form Elements
const domainSelect = document.getElementById('domain-select');
const difficultySelect = document.getElementById('difficulty-select');
const typeSelect = document.getElementById('type-select');
const countInput = document.getElementById('count-input');
const startBtn = document.getElementById('start-btn');

// Training Elements
const qDomain = document.getElementById('q-domain');
const qDifficulty = document.getElementById('q-difficulty');
const qType = document.getElementById('q-type');
const qPrompt = document.getElementById('q-prompt');
const inputArea = document.getElementById('input-area');
const submitBtn = document.getElementById('submit-btn');
const skipBtn = document.getElementById('skip-btn');
const nextBtn = document.getElementById('next-btn');

const evalResult = document.getElementById('eval-result');
const resultTitle = document.getElementById('result-title');
const resultMessage = document.getElementById('result-message');
const modelAnswerSection = document.getElementById('model-answer-section');
const modelAnswerContent = document.getElementById('model-answer-content');

const progressBarFill = document.getElementById('progress-bar-fill');
const currentQNum = document.getElementById('current-q-num');
const totalQNum = document.getElementById('total-q-num');

const hintsContainer = document.getElementById('q-hints-container');
const showHintBtn = document.getElementById('show-hint-btn');
const hintsList = document.getElementById('hints-list');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await fetchConfig();
    
    startBtn.addEventListener('click', startSession);
    submitBtn.addEventListener('click', submitAnswer);
    skipBtn.addEventListener('click', skipQuestion);
    nextBtn.addEventListener('click', nextQuestion);
    document.getElementById('restart-btn').addEventListener('click', () => switchView('setup'));
    showHintBtn.addEventListener('click', showNextHint);
});

function switchView(viewName) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    views[viewName].classList.add('active');
}

async function fetchConfig() {
    try {
        const res = await fetch(`${API_BASE}/config`);
        const data = await res.json();
        
        populateSelect(domainSelect, data.domains);
        populateSelect(difficultySelect, data.difficulties);
        populateSelect(typeSelect, data.types);
    } catch (err) {
        console.error("Failed to fetch config", err);
        domainSelect.innerHTML = '<option value="all">all</option>';
        difficultySelect.innerHTML = '<option value="all">all</option>';
        typeSelect.innerHTML = '<option value="all">all</option>';
    }
}

function populateSelect(selectEl, options) {
    selectEl.innerHTML = '';
    options.forEach(opt => {
        const el = document.createElement('option');
        el.value = opt;
        el.textContent = opt.charAt(0).toUpperCase() + opt.slice(1).replace('_', ' ');
        selectEl.appendChild(el);
    });
}

async function startSession() {
    startBtn.disabled = true;
    startBtn.innerHTML = 'Loading...';
    
    const reqData = {
        domain: domainSelect.value,
        difficulty: difficultySelect.value,
        exercise_type: typeSelect.value,
        count: parseInt(countInput.value) || 5
    };
    
    try {
        const res = await fetch(`${API_BASE}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqData)
        });
        
        const data = await res.json();
        questions = data.questions;
        
        if (questions.length === 0) {
            alert("No questions found matching criteria.");
            startBtn.disabled = false;
            startBtn.innerHTML = 'Start Training <span class="btn-icon">→</span>';
            return;
        }
        
        currentIndex = 0;
        score = 0;
        totalQNum.textContent = questions.length;
        
        renderQuestion();
        switchView('training');
    } catch (err) {
        console.error("Failed to start session", err);
        alert("Error connecting to server. Is the backend running?");
    }
    
    startBtn.disabled = false;
    startBtn.innerHTML = 'Start Training <span class="btn-icon">→</span>';
}

function renderQuestion() {
    currentQuestion = questions[currentIndex];
    hintsShown = 0;
    
    // Update Progress
    currentQNum.textContent = currentIndex + 1;
    progressBarFill.style.width = `${((currentIndex) / questions.length) * 100}%`;
    
    // Reset UI
    evalResult.classList.add('hidden');
    evalResult.classList.remove('success', 'error');
    submitBtn.classList.remove('hidden');
    skipBtn.classList.remove('hidden');
    hintsList.innerHTML = '';
    
    // Set Header
    qDomain.textContent = currentQuestion.domain.replace('_', ' ');
    qDifficulty.textContent = currentQuestion.difficulty;
    qType.textContent = currentQuestion.exercise_type.replace(/_/g, ' ');
    
    // Set Prompt
    let fullPrompt = currentQuestion.prompt;
    if (currentQuestion.schema_ddl) {
        fullPrompt += `\n\n**Schema:**\n\`\`\`sql\n${currentQuestion.schema_ddl}\n\`\`\``;
    }
    if (currentQuestion.project_spec) {
        fullPrompt += `\n\n**Project Spec:**\n${currentQuestion.project_spec}`;
    }
    
    qPrompt.innerHTML = marked.parse(fullPrompt);
    
    // Hints setup
    if (currentQuestion.hints && currentQuestion.hints.length > 0) {
        hintsContainer.classList.remove('hidden');
        showHintBtn.style.display = 'inline-flex';
    } else {
        hintsContainer.classList.add('hidden');
    }
    
    // Setup Input Area
    inputArea.innerHTML = '';
    
    switch(currentQuestion.exercise_type) {
        case 'multiple_choice':
            const mcContainer = document.createElement('div');
            mcContainer.className = 'mc-options';
            currentQuestion.choices.forEach((choice, idx) => {
                const opt = document.createElement('div');
                opt.className = 'mc-option';
                opt.innerHTML = `
                    <input type="radio" name="mc-ans" value="${idx}" id="choice-${idx}">
                    <span class="mc-label">${marked.parseInline(choice)}</span>
                `;
                opt.addEventListener('click', () => {
                    document.querySelectorAll('.mc-option').forEach(el => el.classList.remove('selected'));
                    opt.classList.add('selected');
                    document.getElementById(`choice-${idx}`).checked = true;
                });
                mcContainer.appendChild(opt);
            });
            inputArea.appendChild(mcContainer);
            break;
            
        case 'fill_in_code':
        case 'sql_challenge':
            const ta = document.createElement('textarea');
            ta.id = 'code-input';
            ta.placeholder = 'Type your solution here...';
            if (currentQuestion.code_template) {
                ta.value = currentQuestion.code_template;
            }
            inputArea.appendChild(ta);
            break;
            
        case 'explain_concept':
        case 'take_home':
            const exTa = document.createElement('textarea');
            exTa.id = 'concept-input';
            exTa.placeholder = 'Type your answer or notes here...';
            inputArea.appendChild(exTa);
            break;
    }
}

function showNextHint() {
    if (hintsShown < currentQuestion.hints.length) {
        const hintEl = document.createElement('div');
        hintEl.className = 'hint-item';
        hintEl.innerHTML = marked.parseInline(`**Hint ${hintsShown + 1}:** ${currentQuestion.hints[hintsShown]}`);
        hintsList.appendChild(hintEl);
        hintsShown++;
        
        if (hintsShown >= currentQuestion.hints.length) {
            showHintBtn.style.display = 'none';
        }
    }
}

async function submitAnswer() {
    let userAnswer = "";
    
    if (currentQuestion.exercise_type === 'multiple_choice') {
        const selected = document.querySelector('input[name="mc-ans"]:checked');
        if (!selected) {
            alert("Please select an option.");
            return;
        }
        userAnswer = selected.value;
    } else if (currentQuestion.exercise_type === 'fill_in_code' || currentQuestion.exercise_type === 'sql_challenge') {
        userAnswer = document.getElementById('code-input').value;
        if (!userAnswer.trim()) {
            alert("Please enter some code.");
            return;
        }
    } else {
        userAnswer = document.getElementById('concept-input').value;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Evaluating...';
    
    try {
        const res = await fetch(`${API_BASE}/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: currentQuestion.id,
                user_answer: userAnswer
            })
        });
        
        const data = await res.json();
        showEvaluationResult(data);
    } catch (err) {
        console.error("Evaluation failed", err);
        alert("Failed to evaluate answer.");
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Answer';
}

function skipQuestion() {
    showEvaluationResult({
        correct: false,
        message: "Question skipped.",
        model_answer: "Skipped",
        explanation: currentQuestion.explanation || "No explanation provided."
    });
}

function showEvaluationResult(data) {
    submitBtn.classList.add('hidden');
    skipBtn.classList.add('hidden');
    
    evalResult.classList.remove('hidden');
    evalResult.classList.remove('success', 'error');
    evalResult.classList.add(data.correct ? 'success' : 'error');
    
    if (data.correct) {
        score++;
        resultTitle.textContent = '✨ Correct!';
    } else {
        resultTitle.textContent = '❌ Incorrect';
    }
    
    let msgFormatted = data.message;
    if (currentQuestion.exercise_type === 'fill_in_code' || currentQuestion.exercise_type === 'sql_challenge') {
        msgFormatted = `\`\`\`text\n${data.message}\n\`\`\``;
    }
    resultMessage.innerHTML = marked.parse(msgFormatted);
    
    if (data.model_answer || data.explanation) {
        modelAnswerSection.classList.remove('hidden');
        let content = '';
        if (data.model_answer) {
            const lang = currentQuestion.domain === 'sql' ? 'sql' : 'python';
            content += `**Model Answer:**\n\`\`\`${lang}\n${data.model_answer}\n\`\`\`\n\n`;
        }
        if (data.explanation) {
            content += `**Explanation:**\n${data.explanation}`;
        }
        modelAnswerContent.innerHTML = marked.parse(content);
    } else {
        modelAnswerSection.classList.add('hidden');
    }
    
    // Run highlight js on newly injected blocks
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });
}

function nextQuestion() {
    currentIndex++;
    if (currentIndex >= questions.length) {
        showSummary();
    } else {
        renderQuestion();
    }
}

function showSummary() {
    progressBarFill.style.width = '100%';
    
    const percentage = Math.round((score / questions.length) * 100);
    document.getElementById('final-score').textContent = `${percentage}%`;
    document.getElementById('correct-count').textContent = score;
    document.getElementById('total-count').textContent = questions.length;
    
    // Update circle progress
    document.querySelector('.score-circle').style.setProperty('--percentage', `${percentage}%`);
    
    switchView('summary');
}
