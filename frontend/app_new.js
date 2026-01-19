// ClarityCareers Frontend JavaScript - Enhanced with PDF Upload & Analysis
const API_BASE = 'http://localhost:8000';

// ── Toast Notification Helper ──
function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) { console.warn(message); return; }
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity .3s'; setTimeout(() => toast.remove(), 350); }, duration);
}
let currentUser = null;
let authToken = null;
let currentJobId = null;
let uploadedFile = null;
let analysisData = null;
let baselineMatchPercentage = null; // Store initial match percentage for accurate simulator calculations
let allJobs = []; // Store all jobs for searching

function setBackgroundMode(isAuthMode) {
    document.body.classList.toggle('app-mode', !isAuthMode);
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setBackgroundMode(true);
    checkAuth();
    
    // Setup job search listener
    const searchInput = document.getElementById('job-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterJobs(e.target.value);
        });
    }
});

// Authentication Functions
async function login(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken);
            await fetchCurrentUser();
            showDashboard();
        } else {
            showToast('Invalid credentials. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Is the backend running?', 'error');
    }
}

async function register(event) {
    event.preventDefault();
    const userData = {
        email: document.getElementById('register-email').value,
        username: document.getElementById('register-username').value,
        full_name: document.getElementById('register-fullname').value,
        password: document.getElementById('register-password').value,
        user_type: document.getElementById('register-usertype').value
    };

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            showToast('Account created! Please sign in.', 'success');
            showLogin();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed. Please try again.', 'error');
    }
}

function logout() {
    localStorage.removeItem('token');
    authToken = null;
    currentUser = null;
    location.reload();
}

async function fetchCurrentUser() {
    const response = await fetch(`${API_BASE}/auth/me`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
    currentUser = await response.json();
}

function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        authToken = token;
        fetchCurrentUser().then(showDashboard);
    }
}

// UI Switching Functions
function showLogin() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

async function showDashboard() {
    setBackgroundMode(false);
    const authEl = document.getElementById('auth-section');
    authEl.classList.add('hidden');
    authEl.style.display = 'none';
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('nav-user').classList.remove('hidden');
    document.getElementById('user-name').textContent = currentUser.full_name || currentUser.username;
    document.getElementById('user-type').textContent = currentUser.user_type === 'job_seeker' ? 'Job Seeker' : 'Recruiter';

    if (currentUser.user_type === 'job_seeker') {
        document.getElementById('job-seeker-dashboard').classList.remove('hidden');
        loadJobs();
        checkForNewMessages();  // Check for messages from recruiters
    } else {
        document.getElementById('recruiter-dashboard').classList.remove('hidden');
        loadRecruiterJobs();
    }
}

// Job Functions
async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const jobs = await response.json();
        allJobs = jobs; // Store all jobs for search
        displayJobs(jobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-list');
    if (!jobs.length) {
        container.innerHTML = `
            <div class="col-span-3 text-center py-20">
                <div style="width:64px;height:64px;border-radius:50%;background:rgba(200,150,90,.1);border:1px solid rgba(200,150,90,.2);display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;">
                    <svg width="28" height="28" fill="none" stroke="var(--coral)" stroke-width="1.5" viewBox="0 0 24 24"><path d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                </div>
                <p style="color:rgba(232,224,212,.35);font-size:.9rem;">No opportunities available yet</p>
            </div>`;
        return;
    }
    container.innerHTML = jobs.map((job, i) => `
        <div class="job-card-premium" style="animation:fadeUp .45s ${i * 0.07}s cubic-bezier(.4,0,.2,1) both">
            <div class="gold-top-bar"></div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;">
                <div style="flex:1;margin-right:14px;">
                    <h3 style="font-family:'Cormorant Garamond',serif;font-size:1.38rem;font-weight:600;color:#f0e8dc;margin-bottom:5px;line-height:1.25;">${job.title}</h3>
                    <p style="font-size:.78rem;font-weight:700;color:var(--coral);letter-spacing:.06em;text-transform:uppercase;">${job.company}</p>
                </div>
                <span style="display:inline-flex;align-items:center;padding:4px 12px;border-radius:99px;background:rgba(212,168,64,.1);border:1px solid rgba(212,168,64,.28);color:var(--gold);font-size:.72rem;font-weight:700;white-space:nowrap;letter-spacing:.03em;flex-shrink:0;">${job.salary_range || 'Competitive'}</span>
            </div>
            <p style="color:rgba(232,224,212,.48);font-size:.82rem;line-height:1.7;margin-bottom:22px;">${job.description.substring(0, 130)}…</p>
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
                <div style="display:flex;align-items:center;gap:7px;flex-wrap:wrap;">
                    <span style="display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:99px;background:rgba(200,150,90,.07);border:1px solid rgba(200,150,90,.16);color:rgba(232,224,212,.5);font-size:.72rem;">
                        <svg width="11" height="11" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                        ${job.location || 'Remote'}
                    </span>
                    <span style="display:inline-flex;padding:4px 10px;border-radius:99px;background:rgba(29,196,154,.06);border:1px solid rgba(29,196,154,.2);color:rgba(29,196,154,.85);font-size:.72rem;font-weight:600;">${job.job_type || 'Full-time'}</span>
                </div>
                <div style="display:flex;gap:8px;">
                    <button onclick="viewJobDetails(${job.id})" style="padding:8px 16px;border-radius:10px;border:1px solid rgba(200,169,110,.25);background:transparent;color:#d8c7a2;font-size:.75rem;font-weight:600;cursor:pointer;transition:background .2s,border-color .2s;" onmouseover="this.style.background='rgba(200,169,110,.08)';this.style.borderColor='rgba(200,169,110,.42)'" onmouseout="this.style.background='transparent';this.style.borderColor='rgba(200,169,110,.25)'">Details</button>
                    <button onclick="openApplyModal(${job.id})" style="padding:8px 18px;border-radius:10px;background:rgba(200,169,110,.14);color:#efe8da;font-size:.75rem;font-weight:700;border:1px solid rgba(200,169,110,.34);cursor:pointer;transition:background .2s,border-color .2s;letter-spacing:.03em;" onmouseover="this.style.background='rgba(200,169,110,.24)';this.style.borderColor='rgba(200,169,110,.5)'" onmouseout="this.style.background='rgba(200,169,110,.14)';this.style.borderColor='rgba(200,169,110,.34)'">Apply Now</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function loadRecruiterJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs/my-jobs`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const jobs = await response.json();
        displayRecruiterJobs(jobs);
    } catch (error) {
        console.error('Error loading recruiter jobs:', error);
    }
}

function displayRecruiterJobs(jobs) {
    const container = document.getElementById('recruiter-jobs-list');
    if (!jobs.length) {
        container.innerHTML = `
            <div class="col-span-2 text-center py-20">
                <div style="width:64px;height:64px;border-radius:50%;background:rgba(200,150,90,.1);border:1px solid rgba(200,150,90,.2);display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;">
                    <svg width="28" height="28" fill="none" stroke="var(--coral)" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                </div>
                <p style="color:rgba(232,224,212,.35);font-size:.9rem;">No jobs posted yet — create your first listing</p>
            </div>`;
        return;
    }
    container.innerHTML = jobs.map((job, i) => `
        <div class="job-card-premium" style="animation:fadeUp .45s ${i * 0.07}s cubic-bezier(.4,0,.2,1) both;border-left:2px solid rgba(200,150,90,.32);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                <div style="flex:1;margin-right:12px;">
                    <h3 style="font-family:'Cormorant Garamond',serif;font-size:1.38rem;font-weight:600;color:#f0e8dc;margin-bottom:5px;line-height:1.25;">${job.title}</h3>
                    <p style="font-size:.78rem;font-weight:700;color:var(--coral);letter-spacing:.06em;text-transform:uppercase;">${job.company}</p>
                </div>
                <span style="display:inline-flex;align-items:center;padding:4px 12px;border-radius:99px;font-size:.72rem;font-weight:700;flex-shrink:0;${job.is_active ? 'background:rgba(29,196,154,.1);border:1px solid rgba(29,196,154,.28);color:#1dc49a;' : 'background:rgba(196,112,144,.1);border:1px solid rgba(196,112,144,.28);color:#C47090;'}">
                    ${job.is_active ? '● Active' : '○ Inactive'}
                </span>
            </div>
            <p style="color:rgba(232,224,212,.48);font-size:.82rem;line-height:1.7;margin-bottom:22px;">${job.description.substring(0, 130)}…</p>
            <div style="display:flex;gap:10px;">
                <button onclick="viewApplications(${job.id})" style="flex:1;padding:10px 16px;border-radius:12px;background:rgba(200,169,110,.14);border:1px solid rgba(200,169,110,.34);color:#f0e8dc;font-size:.78rem;font-weight:700;cursor:pointer;letter-spacing:.03em;transition:background .2s,border-color .2s;" onmouseover="this.style.background='rgba(200,169,110,.24)';this.style.borderColor='rgba(200,169,110,.5)'" onmouseout="this.style.background='rgba(200,169,110,.14)';this.style.borderColor='rgba(200,169,110,.34)'">View Applications</button>
                <button onclick="deleteJob(${job.id})" style="padding:10px 18px;border-radius:12px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2);color:rgba(239,68,68,.7);font-size:.78rem;font-weight:600;cursor:pointer;transition:background .2s,border-color .2s;" onmouseover="this.style.background='rgba(239,68,68,.16)';this.style.borderColor='rgba(239,68,68,.38)'" onmouseout="this.style.background='rgba(239,68,68,.07)';this.style.borderColor='rgba(239,68,68,.2)'">Delete</button>
            </div>
        </div>
    `).join('');
}

// Create Job Functions
function showCreateJobModal() {
    document.getElementById('create-job-modal').classList.remove('hidden');
}

function closeCreateJobModal() {
    document.getElementById('create-job-modal').classList.add('hidden');
}

async function createJob(event) {
    event.preventDefault();
    const jobData = {
        title: document.getElementById('job-title').value,
        company: document.getElementById('job-company').value,
        description: document.getElementById('job-description').value,
        requirements: document.getElementById('job-requirements').value,
        location: document.getElementById('job-location').value,
        salary_range: document.getElementById('job-salary').value,
        job_type: 'full-time'
    };

    try {
        const response = await fetch(`${API_BASE}/jobs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(jobData)
        });

        if (response.ok) {
            closeCreateJobModal();
            loadRecruiterJobs();
            event.target.reset();
        }
    } catch (error) {
        console.error('Error creating job:', error);
    }
}

async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job?')) return;

    try {
        await fetch(`${API_BASE}/jobs/${jobId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        loadRecruiterJobs();
    } catch (error) {
        console.error('Error deleting job:', error);
    }
}

// ============================================
// NEW: PDF UPLOAD & ANALYSIS FUNCTIONS
// ============================================

function openApplyModal(jobId) {
    currentJobId = jobId;
    document.getElementById('apply-modal').classList.remove('hidden');
    
    // Fetch job details
    fetch(`${API_BASE}/jobs/${jobId}`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(res => res.json())
    .then(job => {
        document.getElementById('apply-job-title').textContent = job.title;
        document.getElementById('apply-job-company').textContent = job.company;
    });

    // Reset to upload step - clear ALL previous state
    resetApplyModal();
    simulatorSkills = [];
    simulationResult = null;
    analysisData = null;
    baselineMatchPercentage = null;
}

function closeApplyModal() {
    document.getElementById('apply-modal').classList.add('hidden');
    resetApplyModal();
}

function resetApplyModal() {
    document.getElementById('upload-step').classList.remove('hidden');
    document.getElementById('analysis-step').classList.add('hidden');
    document.getElementById('success-step').classList.add('hidden');
    clearFile();
    
    // Reset simulator state for new job
    simulatorSkills = [];
    analysisData = null;
    baselineMatchPercentage = null;
}

// File Upload Handlers
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('file-upload-area').classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('file-upload-area').classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('file-upload-area').classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate file
    if (file.type !== 'application/pdf') {
        showToast('Please upload a PDF file.', 'warning');
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5 MB.', 'warning');
        return;
    }
    
    uploadedFile = file;
    
    // Display file info
    document.getElementById('selected-file').classList.remove('hidden');
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('analyze-btn').disabled = false;
}

function clearFile() {
    uploadedFile = null;
    document.getElementById('cv-file-input').value = '';
    document.getElementById('selected-file').classList.add('hidden');
    document.getElementById('analyze-btn').disabled = true;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Analyze CV Function
async function analyzeCV() {
    if (!uploadedFile) return;
    
    console.log('Starting CV analysis...');
    console.log('Job ID:', currentJobId);
    console.log('File:', uploadedFile.name, uploadedFile.size, 'bytes');
    
    // Show analysis step
    document.getElementById('upload-step').classList.add('hidden');
    document.getElementById('analysis-step').classList.remove('hidden');
    document.getElementById('analysis-loading').classList.remove('hidden');
    document.getElementById('analysis-results').classList.add('hidden');
    
    try {
        // Create form data with file
        const formData = new FormData();
        formData.append('cv_file', uploadedFile);
        
        console.log('Sending request to:', `${API_BASE}/applications/analyze-cv?job_id=${currentJobId}`);
        
        // Read pro model toggle
        const useProModel = document.getElementById('pro-model-toggle')?.checked || false;

        // Call analysis API
        const response = await fetch(`${API_BASE}/applications/analyze-cv?job_id=${currentJobId}&use_pro_model=${useProModel}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Analysis failed:', errorData);
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        analysisData = await response.json();
        
        // Hide loading, show results
        setTimeout(() => {
            document.getElementById('analysis-loading').classList.add('hidden');
            document.getElementById('analysis-results').classList.remove('hidden');
            displayAnalysisResults();
        }, 1500); // Small delay for better UX
        
    } catch (error) {
        console.error('Analysis error:', error);
        showToast(`Analysis failed: ${error.message}. Please ensure your PDF contains readable text.`, 'error');
        backToUpload();
    }
}

function displayAnalysisResults() {
    // Store the baseline match percentage for simulator calculations
    baselineMatchPercentage = analysisData.match_percentage;
    
    // Display match score
    document.getElementById('match-score').textContent = analysisData.match_percentage.toFixed(1) + '%';
    document.getElementById('match-prediction').textContent = analysisData.prediction;

    // Show which model was used
    const isProModel = document.getElementById('pro-model-toggle')?.checked || false;
    const modelBadge = isProModel
        ? '<span style="display:inline-block;padding:2px 10px;border-radius:20px;background:rgba(147,51,234,.25);border:1px solid rgba(147,51,234,.5);font-size:11px;font-weight:600;color:#c084fc;margin-left:8px;">🧠 Pro Model</span>'
        : '<span style="display:inline-block;padding:2px 10px;border-radius:20px;background:rgba(6,182,212,.15);border:1px solid rgba(6,182,212,.3);font-size:11px;font-weight:600;color:#67e8f9;margin-left:8px;">⚡ Standard Model</span>';
    document.getElementById('match-confidence').innerHTML = `Confidence: ${analysisData.confidence} ${modelBadge}`;
    
    // Display percentile if available
    if (analysisData.percentile_estimate !== null) {
        const percentile = analysisData.percentile_estimate.toFixed(1);
        let message = '';
        if (percentile >= 90) message = '🌟 Outstanding! Top 10% of applicants';
        else if (percentile >= 75) message = '🎯 Excellent! Above 75th percentile';
        else if (percentile >= 50) message = '✅ Good! Above average';
        else message = '📈 Room for improvement';
        
        document.getElementById('percentile-info').innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="text-sm text-gray-300 mb-1">Your Ranking</p>
                    <p class="text-2xl font-bold neon-purp">${percentile}th Percentile</p>
                </div>
                <div class="text-right">
                    <p class="text-lg font-semibold">${message}</p>
                    <p class="text-sm text-gray-300">${analysisData.total_existing_applicants} applicants so far</p>
                </div>
            </div>
        `;
    } else {
        document.getElementById('percentile-info').innerHTML = `
            <p class="text-center text-gray-200">You're the first to apply! 🎉</p>
        `;
    }
    
    // Show strengths tab by default
    showAnalysisTab('strengths');
}

function showAnalysisTab(tab, event) {
    // Update tab buttons
    if (event) {
        document.querySelectorAll('.analysis-tab').forEach(btn => {
            btn.classList.remove('active', 'text-gold', 'border-b-2', 'border-gold');
            btn.classList.add('text-gray-300');
        });
        event.target.classList.add('active', 'text-gold', 'border-b-2', 'border-gold');
        event.target.classList.remove('text-gray-300');
    }
    
    const container = document.getElementById('analysis-tab-content');
    
    if (tab === 'strengths') {
        const positive = analysisData.shap_explanations?.top_positive_features || [];
        
        // Filter out junk words and single letters/short irrelevant terms
        const junkWords = ['login', 'system', 'developed', 'control', 'standards', 'training', 'skills', 'experience', 'work', 'project', 'data', 'level', 'a', 'b', 'c', 'o', 'and', 'the', 'or', 'for', 'of', 'in', 'to', 'is', 'a', 'by', 'on', 'at', 'i'];
        const educationTerms = ['gce', 'o/l', 'a/l', 'diploma', 'certificate', 'degree', 'level'];
        
        const isJunk = (word) => {
            const lower = word.toLowerCase().trim();
            // Remove if it's a junk word
            if (junkWords.includes(lower)) return true;
            // Remove if it contains educational qualification abbreviations
            if (educationTerms.some(term => lower.includes(term))) return true;
            // Remove if it's very short (less than 3 characters) and not a known tech acronym
            if (lower.length < 3 && !['aws', 'gcp', 'api', 'git', 'sql', 'nlp', 'ml', 'ai', 'ui', 'ux'].includes(lower)) return true;
            // Remove if it looks like an acronym of educational qualification (all caps with dots or slashes)
            if (/^[A-Z]+\.?\s*[\/]?\s*[A-Z]+\.?$/.test(word)) return true;
            return false;
        };
        
        const filteredPositive = positive.filter(feature => !isJunk(feature.token));
        
        // Categorize skills
        const skillIcons = {
            'python': '🐍', 'java': '☕', 'javascript': '📜', 'typescript': '📘', 'c++': '⚙️',
            'react': '⚛️', 'angular': '🅰️', 'vue': '💚', 'django': '🎯', 'flask': '🌶️',
            'node.js': '📦', 'express': 'E', 'spring': '🍃', 'fastapi': '⚡',
            'sql': '📊', 'mongodb': '🍃', 'postgresql': '🐘', 'redis': '❤️', 'dynamodb': '⚙️',
            'aws': '☁️', 'azure': '🔷', 'gcp': '☁️', 'docker': '🐋', 'kubernetes': '⚓',
            'machine learning': '🧠', 'ai': '🤖', 'nlp': '📖', 'data science': '📈',
            'api': '🔌', 'rest': '🔌', 'graphql': '📊', 'microservices': '🏗️',
            'testing': '✓', 'agile': '⚡', 'git': '🔗', 'ci/cd': '🚀',
            'project management': '📋', 'leadership': '👥', 'communication': '💬'
        };
        
        const getIcon = (skill) => {
            const lower = skill.toLowerCase();
            for (const [key, icon] of Object.entries(skillIcons)) {
                if (lower.includes(key)) return icon;
            }
            return '⭐';
        };
        
        const getColors = (skill) => {
            const lower = skill.toLowerCase();
            if (lower.includes('python') || lower.includes('backend')) return { bg: 'rgba(88,166,255,.08)', border: 'rgba(88,166,255,.25)', text: '#58a6ff', accent: '#4ade80' };
            if (lower.includes('javascript') || lower.includes('typescript') || lower.includes('node')) return { bg: 'rgba(255,205,86,.08)', border: 'rgba(255,205,86,.25)', text: '#ffcd56', accent: '#1dc49a' };
            if (lower.includes('mongodb') || lower.includes('database') || lower.includes('sql')) return { bg: 'rgba(76,175,80,.08)', border: 'rgba(76,175,80,.25)', text: '#4caf50', accent: '#4ade80' };
            if (lower.includes('aws') || lower.includes('cloud') || lower.includes('docker') || lower.includes('kubernetes')) return { bg: 'rgba(255,152,0,.08)', border: 'rgba(255,152,0,.25)', text: '#ff9800', accent: '#ffa500' };
            if (lower.includes('react') || lower.includes('frontend')) return { bg: 'rgba(29,196,154,.08)', border: 'rgba(29,196,154,.25)', text: '#1dc49a', accent: '#4ade80' };
            if (lower.includes('management') || lower.includes('leadership') || lower.includes('project')) return { bg: 'rgba(200,150,90,.08)', border: 'rgba(200,150,90,.25)', text: '#d4a840', accent: '#9a6030' };
            return { bg: 'rgba(150,126,255,.08)', border: 'rgba(150,126,255,.25)', text: '#967eff', accent: '#c084fc' };
        };
        
        container.innerHTML = `
            <div style="display:flex;flex-direction:column;gap:14px;">
                ${filteredPositive.length > 0 ? filteredPositive.map((feature, idx) => {
                    const colors = getColors(feature.token);
                    const icon = getIcon(feature.token);
                    return `
                    <div class="glass-dark rounded-xl p-5" style="
                        animation: fadeUp .35s ${idx * 0.05}s both;
                        border: 2px solid ${colors.border};
                        background: linear-gradient(135deg, ${colors.bg}, rgba(15,23,42,.4));
                        transition: all .3s ease;
                        cursor: default;
                    " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 24px ${colors.bg}'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='none'">
                        <div style="display:flex;align-items:flex-start;gap:14px;">
                            <div style="
                                width:48px;
                                height:48px;
                                border-radius:12px;
                                background: linear-gradient(135deg, ${colors.text}22, ${colors.accent}22);
                                border: 1.5px solid ${colors.border};
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                font-size:1.8rem;
                                flex-shrink:0;
                                box-shadow: 0 4px 12px ${colors.bg};
                            ">
                                ${icon}
                            </div>
                            <div style="flex:1;">
                                <h3 style="
                                    font-weight:700;
                                    color:#f0e8dc;
                                    font-size:1rem;
                                    margin:0 0 4px 0;
                                    text-transform:capitalize;
                                ">${feature.token}</h3>
                                <p style="
                                    font-size:.75rem;
                                    color:${colors.text};
                                    font-weight:600;
                                    margin:0;
                                    letter-spacing:.04em;
                                    text-transform:uppercase;
                                ">✓ Strong Match</p>
                            </div>
                            <div style="
                                padding:4px 10px;
                                border-radius:99px;
                                background:${colors.text}15;
                                border:1px solid ${colors.border};
                                color:${colors.text};
                                font-size:.7rem;
                                font-weight:700;
                                white-space:nowrap;
                                text-transform:uppercase;
                                letter-spacing:.04em;
                            ">+${(idx + 1).toString().padStart(2, '0')}</div>
                        </div>
                    </div>
                    `;
                }).join('') : `
                    <div style="text-align:center;padding:80px 20px;">
                        <p style="font-size:4rem;margin-bottom:16px;animation:fadeUp .5s ease;">✨</p>
                        <p style="color:#f0e8dc;font-weight:600;font-size:1rem;margin-bottom:8px;">No Strengths Identified</p>
                        <p style="color:rgba(232,224,212,.4);font-size:.85rem;line-height:1.6;">Upload a resume to extract your key skills and strengths.</p>
                    </div>`}
            </div>`;
        // Optional: add hover effects
        requestAnimationFrame(() => {
            const cards = container.querySelectorAll('.glass-dark');
            cards.forEach(card => {
                card.style.cursor = 'default';
            });
        });

    } else if (tab === 'gaps') {
        const gaps = analysisData.skill_gap_analysis?.missing_skills || [];
        
        // Categorize gaps
        const gapIcons = {
            'react': '⚛️', 'javascript': '📜', 'typescript': '📘', 'tailwind': '🎨', 'frontend': '🖥️',
            'node': '📦', 'express': 'E', 'java': '☕', 'python': '🐍', 'backend': '⚙️',
            'mongodb': '🍃', 'mysql': '🗄️', 'database': '📊', 'mongoose': '🍃',
            'openai': '🤖', 'gpt': '🧠', 'machine learning': '📈', 'ml': '📈', 'ai': '🤖',
            'git': '🔗', 'github': '🐙', 'docker': '🐋', 'kubernetes': '⚓', 'devops': '🚀',
            'aws': '☁️', 'azure': '🔷', 'cloud': '☁️', 'api': '🔌', 'wordpress': '🧱'
        };
        
        const getGapIcon = (gap) => {
            const lower = gap.toLowerCase();
            for (const [key, icon] of Object.entries(gapIcons)) {
                if (lower.includes(key)) return icon;
            }
            return '•';
        };
        
        const getCategoryColor = (gap) => {
            const lower = gap.toLowerCase();
            if (lower.includes('react') || lower.includes('javascript') || lower.includes('typescript') || lower.includes('tailwind')) {
                return { bg: 'rgba(255,205,86,.08)', border: 'rgba(255,205,86,.25)', text: '#ffcd56' };
            }
            if (lower.includes('node') || lower.includes('express') || lower.includes('java') || lower.includes('python') || lower.includes('backend')) {
                return { bg: 'rgba(88,166,255,.08)', border: 'rgba(88,166,255,.25)', text: '#58a6ff' };
            }
            if (lower.includes('mongodb') || lower.includes('mysql') || lower.includes('database')) {
                return { bg: 'rgba(76,175,80,.08)', border: 'rgba(76,175,80,.25)', text: '#4caf50' };
            }
            if (lower.includes('openai') || lower.includes('gpt') || lower.includes('machine learning') || lower.includes('ai')) {
                return { bg: 'rgba(156,39,176,.08)', border: 'rgba(156,39,176,.25)', text: '#c084fc' };
            }
            if (lower.includes('git') || lower.includes('docker') || lower.includes('devops') || lower.includes('cloud')) {
                return { bg: 'rgba(255,152,0,.08)', border: 'rgba(255,152,0,.25)', text: '#ff9800' };
            }
            return { bg: 'rgba(212,168,64,.08)', border: 'rgba(212,168,64,.25)', text: '#d4a840' };
        };
        
        // Filter out invalid entries
        const validGaps = gaps.filter(gap => typeof gap === 'string' && gap.trim().length > 0);
        
        container.innerHTML = `
            <div style="display:flex;flex-direction:column;gap:12px;">
                ${validGaps.length > 0 ? validGaps.map((gap, idx) => {
                    const colors = getCategoryColor(gap);
                    const icon = getGapIcon(gap);
                    return `
                    <div class="glass-dark rounded-xl p-4" style="
                        animation: fadeUp .3s ${idx * 0.05}s both;
                        border: 1.5px solid ${colors.border};
                        background: linear-gradient(135deg, ${colors.bg}, rgba(15,23,42,.3));
                        transition: all .2s ease;
                        display: flex;
                        align-items: center;
                        gap: 12px;
                    " onmouseover="this.style.transform='translateX(4px)'" onmouseout="this.style.transform='translateX(0)'">
                        <div style="
                            width: 36px;
                            height: 36px;
                            border-radius: 9px;
                            background: ${colors.text}15;
                            border: 1px solid ${colors.border};
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 1.2rem;
                            flex-shrink: 0;
                        ">${icon}</div>
                        <div style="flex: 1;">
                            <p style="font-weight: 600; color: #f0e8dc; font-size: .88rem; margin: 0 0 2px 0;">${gap}</p>
                            <p style="font-size: .7rem; color: ${ colors.text }99; margin: 0;">Required for this role</p>
                        </div>
                        <span style="
                            padding: 4px 10px;
                            border-radius: 99px;
                            background: ${colors.text}15;
                            border: 1px solid ${colors.border};
                            color: ${colors.text};
                            font-size: .65rem;
                            font-weight: 700;
                            text-transform: uppercase;
                            letter-spacing: .04em;
                            white-space: nowrap;
                            flex-shrink: 0;
                        ">Gap</span>
                    </div>
                    `;
                }).join('') : `
                    <div style="text-align:center;padding:56px 20px;">
                        <p style="font-size:3rem;margin-bottom:12px;">🎉</p>
                        <p style="color:#1dc49a;font-weight:600;font-size:.92rem;margin-bottom:6px;">No skill gaps detected!</p>
                        <p style="color:rgba(232,224,212,.35);font-size:.82rem;">You have all the required skills for this role</p>
                    </div>`}
            </div>`;

    } else if (tab === 'recommendations') {
        const recs = analysisData.recommendations || [];
        
        // Categorize skill types
        const recIcons = {
            'react': '⚛️', 'javascript': '📜', 'typescript': '📘', 'tailwind': '🎨', 'frontend': '🖥️',
            'node': '📦', 'express': 'E', 'java': '☕', 'python': '🐍', 'backend': '⚙️',
            'mongodb': '🍃', 'mysql': '🗄️', 'mongoose': '🍃', 'database': '📊',
            'openai': '🤖', 'gpt': '🧠', 'machine learning': '📈', 'ai': '🤖',
            'git': '🔗', 'github': '🐙', 'docker': '🐋', 'kubernetes': '⚓', 'devops': '🚀'
        };
        
        const getRecIcon = (skill) => {
            const lower = skill.toLowerCase();
            for (const [key, icon] of Object.entries(recIcons)) {
                if (lower.includes(key)) return icon;
            }
            return '⭐';
        };
        
        container.innerHTML = `
            <div style="display:flex;flex-direction:column;gap:14px;">
                ${recs.length > 0 ? recs.map((rec, index) => `
                    <div class="glass-dark rounded-xl p-5" style="
                        animation: fadeUp .35s ${index * 0.07}s both;
                        border: 1.5px solid rgba(200,150,90,.15);
                        background: linear-gradient(135deg, rgba(200,150,90,.05), rgba(15,23,42,.3));
                        transition: all .2s ease;
                    " onmouseover="this.style.boxShadow='0 6px 20px rgba(212,168,64,.2)'" onmouseout="this.style.boxShadow='none'">
                        <div style="display:flex;align-items:flex-start;gap:14px;">
                            <div style="
                                width: 48px;
                                height: 48px;
                                border-radius: 12px;
                                background: rgba(212,168,64,.08);
                                border: 1px solid rgba(212,168,64,.25);
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 1.6rem;
                                flex-shrink: 0;
                            ">${getRecIcon(rec.skill)}</div>
                            <div style="flex: 1;">
                                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
                                    <h4 style="font-weight:700;color:#f0e8dc;font-size:.96rem;margin:0;">${rec.skill}</h4>
                                    <span style="
                                        padding: 4px 11px;
                                        border-radius: 99px;
                                        font-size: .66rem;
                                        font-weight: 700;
                                        text-transform: uppercase;
                                        letter-spacing: .04em;
                                        white-space: nowrap;
                                        ${rec.priority === 'High' ? 'background:rgba(196,112,144,.1);border:1px solid rgba(196,112,144,.28);color:#C47090;' :'background:rgba(212,168,64,.08);border:1px solid rgba(212,168,64,.24);color:var(--gold);'}
                                    ">${rec.priority}</span>
                                </div>
                                <p style="color:rgba(232,224,212,.55);font-size:.82rem;line-height:1.65;margin:0;">${rec.suggestion}</p>
                            </div>
                        </div>
                    </div>
                `).join('') : `
                    <div style="text-align:center;padding:56px 20px;">
                        <p style="font-size:3rem;margin-bottom:12px;">✨</p>
                        <p style="color:#f0e8dc;font-weight:600;font-size:.92rem;margin-bottom:6px;">No Recommendations</p>
                        <p style="color:rgba(232,224,212,.35);font-size:.82rem;">You're well-prepared for this role!</p>
                    </div>`}
            </div>`;

    } else if (tab === 'simulator') {
        displaySkillSimulator(container);
    }
}

function backToUpload() {
    document.getElementById('upload-step').classList.remove('hidden');
    document.getElementById('analysis-step').classList.add('hidden');
    analysisData = null;
}

// Submit Application
async function submitApplication() {
    if (!analysisData || !uploadedFile) return;
    
    try {
        // Read file as text for submission
        const reader = new FileReader();
        reader.onload = async (e) => {
            const applicationData = {
                job_id: currentJobId,
                resume_text: analysisData.extracted_text,
                analysis_report: analysisData,
                pdf_file_path: analysisData.pdf_file_path || null  // Include PDF file path
            };
            
            const response = await fetch(`${API_BASE}/applications/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(applicationData)
            });
            
            if (response.ok) {
                document.getElementById('analysis-step').classList.add('hidden');
                document.getElementById('success-step').classList.remove('hidden');
                showToast('Application submitted successfully!', 'success');
            } else {
                const error = await response.json();
                showToast(error.detail || 'Submission failed', 'error');
            }
        };
        reader.readAsText(uploadedFile);
        
    } catch (error) {
        console.error('Submission error:', error);
        showToast('Failed to submit application. Please try again.', 'error');
    }
}

// ============================================
// ADVANCED SKILL SIMULATOR
// ============================================

let simulatorSkills = [];
let simulationResult = null;

function displaySkillSimulator(container) {
    const missingSkills = analysisData.skill_gap_analysis?.missing_skills || [];
    const currentSkills = analysisData.skill_gap_analysis?.matched_skills || [];
    const suggestions = analysisData.simulator_suggestions || missingSkills.slice(0, 5);
    
    container.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:16px;">

            <!-- Current / Simulated Score Card -->
            <div class="glass-dark rounded-xl p-5" style="border:1px solid rgba(200,150,90,.12);">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;">
                    <div>
                        <p style="font-size:.73rem;color:rgba(232,224,212,.38);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;">Current Match Score</p>
                        <p style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:700;background:linear-gradient(135deg,#9A6030,#D4A840);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1;">
                            ${analysisData.match_percentage.toFixed(1)}%
                        </p>
                    </div>
                    ${simulationResult ? `
                        <div style="text-align:right;">
                            <p style="font-size:.73rem;color:rgba(232,224,212,.38);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;">Simulated Score</p>
                            <p style="font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:700;line-height:1;color:${simulationResult.improvement > 0 ? '#1dc49a' : 'var(--gold)'};">
                                ${(simulationResult.new_match_percentage || 0).toFixed(1)}%
                            </p>
                            <p style="font-size:.85rem;font-weight:600;margin-top:4px;color:${simulationResult.improvement > 0 ? '#1dc49a' : 'var(--gold)'};">
                                ${simulationResult.improvement > 0 ? '↑' : '↓'} ${Math.abs(simulationResult.improvement || 0).toFixed(1)} pts
                            </p>
                        </div>
                    ` : '<div style="text-align:right;"><p style="font-size:.75rem;color:rgba(232,224,212,.25);">Add skills to simulate</p></div>'}
                </div>
            </div>

            <!-- Skill Input Section -->
            <div class="glass-dark rounded-xl p-5" style="border:1px solid rgba(200,150,90,.1);">
                <h4 style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;color:#f0e8dc;margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                    <span style="color:var(--gold);">✦</span> Add Skills to Test
                </h4>
                <div style="display:flex;gap:8px;margin-bottom:12px;">
                    <input 
                        type="text" 
                        id="simulator-skill-input" 
                        placeholder="e.g. Python, Docker, AWS…" 
                        class="cc-input flex-1 px-4 py-3 rounded-lg"
                        onkeypress="if(event.key === 'Enter') addSimulatorSkill()"
                    >
                    <button 
                        onclick="addSimulatorSkill()" 
                        style="padding:10px 20px;border-radius:10px;background:linear-gradient(135deg,#9A6030,#D4A840);color:#030712;font-weight:700;font-size:.8rem;border:none;cursor:pointer;transition:transform .2s,box-shadow .2s;white-space:nowrap;" onmouseover="this.style.transform='scale(1.04)';this.style.boxShadow='0 6px 18px rgba(212,168,64,.35)'" onmouseout="this.style.transform='scale(1)';this.style.boxShadow='none'">
                        Add
                    </button>
                </div>
                
                <!-- Added Skills List -->
                <div id="simulator-skills-list" style="display:flex;flex-wrap:wrap;gap:8px;min-height:32px;margin-bottom:14px;">
                    ${simulatorSkills.length === 0 ? '<p style="font-size:.78rem;color:rgba(232,224,212,.28);">No skills added yet — add skills to see their impact</p>' : ''}
                </div>
                
                <!-- Action Buttons -->
                <div style="display:flex;gap:10px;">
                    <button 
                        onclick="runSimulation()" 
                        ${simulatorSkills.length === 0 ? 'disabled' : ''}
                        style="flex:1;padding:11px 16px;border-radius:12px;background:linear-gradient(135deg,rgba(154,96,48,.5),rgba(212,168,64,.4));border:1px solid rgba(212,168,64,.24);color:#f0e8dc;font-weight:700;font-size:.82rem;cursor:pointer;letter-spacing:.03em;transition:box-shadow .2s,opacity .2s;opacity:${simulatorSkills.length === 0 ? '.45' : '1'};" onmouseover="if(!this.disabled){this.style.boxShadow='0 6px 20px rgba(212,168,64,.22)'}" onmouseout="this.style.boxShadow='none'">
                        🚀 Run Simulation
                    </button>
                    <button 
                        onclick="clearSimulation()" 
                        style="padding:11px 20px;border-radius:12px;background:transparent;border:1px solid rgba(200,150,90,.2);color:rgba(232,224,212,.55);font-size:.82rem;font-weight:600;cursor:pointer;transition:background .2s;" onmouseover="this.style.background='rgba(200,150,90,.07)'" onmouseout="this.style.background='transparent'">
                        Clear
                    </button>
                </div>
            </div>

            <!-- Quick Add Suggestions -->
            ${suggestions.length > 0 ? `
                <div class="glass-dark rounded-xl p-5" style="border:1px solid rgba(200,150,90,.1);">
                    <h4 style="font-size:.75rem;font-weight:700;color:rgba(232,224,212,.45);text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px;">Suggested Skills — Quick Add</h4>
                    <div style="display:flex;flex-wrap:wrap;gap:8px;">
                        ${suggestions.map(skill => `
                            <button 
                                onclick="quickAddSkill('${skill}')" 
                                style="padding:6px 14px;border-radius:99px;background:rgba(212,168,64,.07);border:1px solid rgba(212,168,64,.28);color:var(--gold);font-size:.77rem;font-weight:600;cursor:pointer;transition:background .2s,transform .2s;" onmouseover="this.style.background='rgba(212,168,64,.15)';this.style.transform='scale(1.04)'" onmouseout="this.style.background='rgba(212,168,64,.07)';this.style.transform='scale(1)'">
                                + ${skill}
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <!-- Simulation Results -->
            ${simulationResult ? `
                <div class="glass-dark rounded-xl p-5" style="border:1px solid ${simulationResult.improvement > 0 ? 'rgba(29,196,154,.28)' : 'rgba(212,168,64,.28)'};">
                    <h4 style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;color:#f0e8dc;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
                        <span>📊</span> Simulation Results
                    </h4>
                    
                    <!-- Score comparison bars -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                        <div class="glass rounded-xl p-4" style="text-align:center;">
                            <p style="font-size:.72rem;color:rgba(232,224,212,.38);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;">Original Score</p>
                            <div style="height:6px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden;margin-bottom:8px;">
                                <div style="height:100%;border-radius:99px;background:linear-gradient(90deg,var(--coral),var(--gold));width:${Math.min(simulationResult.original_match_percentage, 100)}%;transition:width 1s ease;"></div>
                            </div>
                            <p style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:700;color:var(--gold);">${(simulationResult.original_match_percentage || 0).toFixed(1)}%</p>
                        </div>
                        <div class="glass rounded-xl p-4" style="text-align:center;">
                            <p style="font-size:.72rem;color:rgba(232,224,212,.38);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;">Simulated Score</p>
                            <div style="height:6px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden;margin-bottom:8px;">
                                <div style="height:100%;border-radius:99px;background:${simulationResult.improvement > 0 ? 'linear-gradient(90deg,#1dc49a,#4ade80)' : 'linear-gradient(90deg,var(--gold),var(--rose))'};width:${Math.min(simulationResult.new_match_percentage, 100)}%;transition:width 1s ease;"></div>
                            </div>
                            <p style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:700;color:${simulationResult.improvement > 0 ? '#1dc49a' : 'var(--gold)'};">${(simulationResult.new_match_percentage || 0).toFixed(1)}%</p>
                        </div>
                    </div>
                    
                    <!-- Added Skills Summary -->
                    <div>
                        <p style="font-size:.73rem;font-weight:700;color:rgba(232,224,212,.42);text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">Skills Added</p>
                        <div style="display:flex;flex-wrap:wrap;gap:8px;">
                            ${(simulationResult.added_skills || []).map(skill => `
                                <span style="display:inline-flex;align-items:center;padding:6px 12px;border-radius:99px;background:rgba(29,196,154,.06);border:1px solid rgba(29,196,154,.24);color:#1dc49a;font-size:.78rem;font-weight:600;">
                                    ✓ ${skill}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Impact Summary -->
                    <div style="margin-top:14px;padding:14px 16px;border-radius:12px;background:rgba(${simulationResult.improvement > 0 ? '29,196,154' : '212,168,64'},.06);border:1px solid rgba(${simulationResult.improvement > 0 ? '29,196,154' : '212,168,64'},.16);">
                        <p style="font-size:.8rem;color:rgba(232,224,212,.62);line-height:1.6;">
                            <strong style="color:${simulationResult.improvement > 0 ? '#1dc49a' : 'var(--gold)'};font-weight:700;">Impact — </strong>
                            ${simulationResult.improvement > 0 
                                ? `Adding these skills would improve your match score by <strong>+${simulationResult.improvement.toFixed(1)} points</strong>. You would reach <strong>${(simulationResult.new_match_percentage || 0).toFixed(1)}%</strong> match.`
                                : `These skills don't significantly impact your match for this role. Consider focusing on the required skills listed above.`
                            }
                        </p>
                    </div>
                </div>
            ` : ''}

            <!-- Info Box -->
            <div class="glass-dark rounded-xl p-4" style="border-left:2px solid var(--coral);">
                <p style="font-size:.78rem;color:rgba(232,224,212,.45);line-height:1.65;">
                    <strong style="color:var(--coral);">How it works —</strong> The simulator uses our AI model to predict how adding skills to your CV would affect your match score. The improvement shown is based on semantic matching to the job description.
                </p>
            </div>
        </div>
    `;
    
    updateSimulatorSkillsList();
}

function addSimulatorSkill() {
    const input = document.getElementById('simulator-skill-input');
    const skill = input.value.trim();
    
    if (!skill) {
        showToast('Please enter a skill name.', 'warning');
        return;
    }
    
    if (simulatorSkills.includes(skill)) {
        showToast('That skill is already added.', 'info');
        return;
    }
    
    simulatorSkills.push(skill);
    input.value = '';
    
    // Clear previous simulation result when adding new skill
    simulationResult = null;
    
    // Re-render the entire simulator to update button state
    const container = document.getElementById('analysis-tab-content');
    if (container) {
        displaySkillSimulator(container);
    }
}

function quickAddSkill(skill) {
    if (!simulatorSkills.includes(skill)) {
        simulatorSkills.push(skill);
        
        // Clear previous simulation result when adding new skill
        simulationResult = null;
        
        // Re-render the entire simulator to update button state
        const container = document.getElementById('analysis-tab-content');
        if (container) {
            displaySkillSimulator(container);
        }
    }
}

function removeSimulatorSkill(skill) {
    simulatorSkills = simulatorSkills.filter(s => s !== skill);
    
    // Clear previous simulation result when modifying skills
    simulationResult = null;
    
    // Re-render the entire simulator to update button state
    const container = document.getElementById('analysis-tab-content');
    if (container) {
        displaySkillSimulator(container);
    }
}

function updateSimulatorSkillsList() {
    const container = document.getElementById('simulator-skills-list');
    if (!container) return;
    
    if (simulatorSkills.length === 0) {
        container.innerHTML = '<p style="font-size:.78rem;color:rgba(232,224,212,.28);">No skills added yet — add skills to see their impact</p>';
        return;
    }
    
    container.innerHTML = simulatorSkills.map(skill => `
        <span class="sim-skill-tag">
            ${skill}
            <button onclick="removeSimulatorSkill('${skill}')" style="margin-left:8px;background:none;border:none;cursor:pointer;color:rgba(200,150,90,.6);font-size:1rem;line-height:1;padding:0;transition:color .15s;" onmouseover="this.style.color='var(--coral)'" onmouseout="this.style.color='rgba(200,150,90,.6)'">×</button>
        </span>
    `).join('');
}

async function runSimulation() {
    if (simulatorSkills.length === 0) {
        showToast('Add at least one skill to run the simulation.', 'warning');
        return;
    }
    
    try {
        console.log('Running simulation with:', {
            job_id: currentJobId,
            skills: simulatorSkills,
            resume_length: analysisData?.extracted_text?.length
        });
        
        const response = await fetch(`${API_BASE}/applications/simulate-skills`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                job_id: currentJobId,
                resume_text: analysisData.extracted_text,
                added_skills: simulatorSkills,
                original_match_percentage: baselineMatchPercentage,
                use_pro_model: document.getElementById('pro-model-toggle')?.checked || false
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Simulation error response:', errorData);
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }
        
        simulationResult = await response.json();
        console.log('Simulation result:', simulationResult);
        
        // Refresh the simulator display
        const container = document.getElementById('analysis-tab-content');
        displaySkillSimulator(container);
        
    } catch (error) {
        console.error('Simulation error:', error);
        showToast(`Simulation failed: ${error.message || 'Please try again'}`, 'error');
    }
}

function clearSimulation() {
    simulatorSkills = [];
    simulationResult = null;
    const container = document.getElementById('analysis-tab-content');
    if (container) {
        displaySkillSimulator(container);
    }
}

// ============================================
// RECRUITER: VIEW APPLICATIONS
// ============================================

async function viewApplications(jobId) {
    try {
        const response = await fetch(`${API_BASE}/applications/job/${jobId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const applications = await response.json();
        
        document.getElementById('view-applications-modal').classList.remove('hidden');
        document.getElementById('applications-count').textContent = `${applications.length} Applications`;
        
        displayApplications(applications);
    } catch (error) {
        console.error('Error loading applications:', error);
    }
}

function closeApplicationsModal() {
    document.getElementById('view-applications-modal').classList.add('hidden');
}

function displayApplications(applications) {
    const container = document.getElementById('applications-list');
    
    if (applications.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:64px 0;">
                <div style="width:60px;height:60px;border-radius:50%;background:rgba(200,150,90,.1);border:1px solid rgba(200,150,90,.2);display:flex;align-items:center;justify-content:center;margin:0 auto 1rem;">
                    <svg width="26" height="26" fill="none" stroke="var(--coral)" stroke-width="1.5" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                </div>
                <p style="color:rgba(232,224,212,.35);font-size:.9rem;">No applications yet</p>
            </div>`;
        return;
    }
    
    // Sort by match percentage
    applications.sort((a, b) => (b.match_percentage || 0) - (a.match_percentage || 0));
    
    container.innerHTML = applications.map((app, index) => {
        const score = app.match_percentage || 0;
        const scoreColor = score >= 70 ? '#1dc49a' : score >= 50 ? 'var(--gold)' : '#C47090';
        const circumference = 2 * Math.PI * 20;
        const offset = circumference - (score / 100) * circumference;
        
        return `
        <div class="glass-dark rounded-2xl p-6" style="animation:fadeUp .4s ${index * 0.06}s both;border:1px solid rgba(200,150,90,.12);">
            <!-- Header row -->
            <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px;gap:12px;flex-wrap:wrap;">
                <div style="display:flex;align-items:flex-start;gap:14px;">
                    <div class="rank-badge">${index + 1}</div>
                    <div>
                        <p style="font-weight:700;color:#f0e8dc;font-size:.94rem;">Applicant ${app.applicant_id}</p>
                        <p style="font-size:.72rem;color:rgba(232,224,212,.35);margin-top:3px;">${new Date(app.applied_at).toLocaleDateString('en-US', {month:'short', day:'numeric', year:'numeric'})}</p>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    <!-- Score ring -->
                    <svg width="52" height="52" viewBox="0 0 52 52" style="flex-shrink:0;">
                        <circle cx="26" cy="26" r="20" fill="none" stroke="rgba(255,255,255,.05)" stroke-width="5"/>
                        <circle cx="26" cy="26" r="20" fill="none" stroke="${scoreColor}" stroke-width="5" stroke-linecap="round"
                            stroke-dasharray="${circumference.toFixed(2)}" stroke-dashoffset="${offset.toFixed(2)}"
                            transform="rotate(-90 26 26)" style="transition:stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)"/>
                        <text x="26" y="30" text-anchor="middle" font-size="9.5" font-weight="700" fill="${scoreColor}" font-family="'Cormorant Garamond',serif">${score.toFixed(0)}%</text>
                    </svg>
                    <div style="text-align:right;">
                        <p style="font-family:'Cormorant Garamond',serif;font-size:1.65rem;font-weight:700;line-height:1;color:${scoreColor};">${score.toFixed(1)}%</p>
                        <p style="font-size:.7rem;color:rgba(232,224,212,.38);margin-top:3px;">${app.prediction || ''}</p>
                    </div>
                </div>
            </div>
            
            ${app.analysis_report ? `
                <!-- Stat row -->
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px;">
                    <div class="glass rounded-xl p-3" style="text-align:center;">
                        <p style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:700;color:#1dc49a;line-height:1;">
                            ${(() => {
                                const junkWords = ['login', 'system', 'developed', 'control', 'standards', 'training', 'skills', 'experience', 'work', 'project', 'data', 'level', 'a', 'b', 'c', 'o', 'and', 'the', 'or', 'for', 'of', 'in', 'to', 'is', 'a', 'by', 'on', 'at', 'i'];
                                const educationTerms = ['gce', 'o/l', 'a/l', 'diploma', 'certificate', 'degree'];
                                const isJunk = (word) => {
                                    const lower = word.toLowerCase().trim();
                                    if (junkWords.includes(lower)) return true;
                                    if (educationTerms.some(term => lower.includes(term))) return true;
                                    if (lower.length < 3 && !['aws', 'gcp', 'api', 'git', 'sql', 'nlp', 'ml', 'ai', 'ui', 'ux'].includes(lower)) return true;
                                    if (/^[A-Z]+\.?\s*[\/]?\s*[A-Z]+\.?$/.test(word)) return true;
                                    return false;
                                };
                                return (app.analysis_report.shap_explanations?.top_positive_features || []).filter(f => !isJunk(f.token)).length;
                            })()}
                        </p>
                        <p style="font-size:.68rem;color:rgba(232,224,212,.38);margin-top:3px;">Strengths</p>
                    </div>
                    <div class="glass rounded-xl p-3" style="text-align:center;">
                        <p style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:700;color:var(--gold);line-height:1;">${app.analysis_report.skill_gap_analysis?.missing_skills?.length || 0}</p>
                        <p style="font-size:.68rem;color:rgba(232,224,212,.38);margin-top:3px;">Skill Gaps</p>
                    </div>
                    <div class="glass rounded-xl p-3" style="text-align:center;">
                        <p style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:700;color:var(--coral);line-height:1;">${app.analysis_report.percentile_estimate?.toFixed(0) || '—'}</p>
                        <p style="font-size:.68rem;color:rgba(232,224,212,.38);margin-top:3px;">Percentile</p>
                    </div>
                </div>
                
                <!-- Expand analysis -->
                <details style="border:1px solid rgba(200,150,90,.12);border-radius:12px;overflow:hidden;margin-bottom:14px;">
                    <summary class="app-detail-summary">
                        <svg class="chevron-arrow" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>
                        View Complete Analysis
                    </summary>
                    <div style="padding:16px 18px;background:rgba(0,0,0,.18);">
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                            <div>
                                <h5 style="font-size:.72rem;font-weight:700;color:var(--coral);letter-spacing:.06em;text-transform:uppercase;margin-bottom:9px;">Top Strengths</h5>
                                <ul style="list-style:none;padding:0;margin:0;">
                                    ${(() => {
                                        const junkWords = ['login', 'system', 'developed', 'control', 'standards', 'training', 'skills', 'experience', 'work', 'project', 'data', 'level', 'a', 'b', 'c', 'o', 'and', 'the', 'or', 'for', 'of', 'in', 'to', 'is', 'a', 'by', 'on', 'at', 'i'];
                                        const educationTerms = ['gce', 'o/l', 'a/l', 'diploma', 'certificate', 'degree', 'level'];
                                        const isJunk = (word) => {
                                            const lower = word.toLowerCase().trim();
                                            if (junkWords.includes(lower)) return true;
                                            if (educationTerms.some(term => lower.includes(term))) return true;
                                            if (lower.length < 3 && !['aws', 'gcp', 'api', 'git', 'sql', 'nlp', 'ml', 'ai', 'ui', 'ux'].includes(lower)) return true;
                                            if (/^[A-Z]+\.?\s*[\/]?\s*[A-Z]+\.?$/.test(word)) return true;
                                            return false;
                                        };
                                        const features = (app.analysis_report.shap_explanations?.top_positive_features || []).filter(f => !isJunk(f.token));
                                        return features.map(f =>
                                            `<li style="display:flex;justify-content:space-between;font-size:.74rem;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);color:rgba(232,224,212,.65);">
                                                <span>${f.token}</span>
                                                <span style="color:#1dc49a;font-weight:600;">+${(f.impact * 100).toFixed(1)}%</span>
                                            </li>`
                                        ).join('') || '<li style="font-size:.74rem;color:rgba(232,224,212,.28);">No data</li>';
                                    })()}
                                </ul>
                            </div>
                            <div>
                                <h5 style="font-size:.72rem;font-weight:700;color:var(--gold);letter-spacing:.06em;text-transform:uppercase;margin-bottom:9px;">Missing Skills</h5>
                                <ul style="list-style:none;padding:0;margin:0;">
                                    ${app.analysis_report.skill_gap_analysis?.missing_skills?.map(skill =>
                                        `<li style="font-size:.74rem;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);color:rgba(232,224,212,.65);">${skill}</li>`
                                    ).join('') || '<li style="font-size:.74rem;color:rgba(232,224,212,.28);">None detected</li>'}
                                </ul>
                            </div>
                        </div>
                    </div>
                </details>
            ` : '<p style="font-size:.74rem;color:rgba(232,224,212,.28);font-style:italic;margin-bottom:14px;">No detailed analysis available</p>'}
            
            <div style="display:flex;gap:10px;">
                <button onclick="showContactModal(${app.id})" style="flex:1;padding:9px 16px;border-radius:10px;background:linear-gradient(135deg,rgba(154,96,48,.45),rgba(212,168,64,.35));border:1px solid rgba(212,168,64,.22);color:#f0e8dc;font-size:.76rem;font-weight:700;cursor:pointer;letter-spacing:.03em;transition:box-shadow .2s;" onmouseover="this.style.boxShadow='0 6px 18px rgba(212,168,64,.2)'" onmouseout="this.style.boxShadow='none'">Contact Candidate</button>
                <button onclick="showFullResume(${app.id})" style="padding:9px 18px;border-radius:10px;background:transparent;border:1px solid rgba(200,150,90,.22);color:var(--coral);font-size:.76rem;font-weight:600;cursor:pointer;transition:background .2s;" onmouseover="this.style.background='rgba(200,150,90,.08)'" onmouseout="this.style.background='transparent'">Full Resume</button>
            </div>
        </div>
    `}).join('');
}

// ── Job Search Functions ──
function filterJobs(searchTerm) {
    const term = searchTerm.toLowerCase().trim();
    
    if (!term) {
        // Show all jobs if search is empty
        displayJobs(allJobs);
        return;
    }
    
    const filtered = allJobs.filter(job => {
        const title = (job.title || '').toLowerCase();
        const company = (job.company || '').toLowerCase();
        const description = (job.description || '').toLowerCase();
        const location = (job.location || '').toLowerCase();
        const requirements = (job.requirements || '').toLowerCase();
        
        return title.includes(term) || 
               company.includes(term) || 
               description.includes(term) || 
               location.includes(term) ||
               requirements.includes(term);
    });
    
    displayJobs(filtered);
}

function clearJobSearch() {
    const searchInput = document.getElementById('job-search-input');
    if (searchInput) {
        searchInput.value = '';
        filterJobs('');
    }
}

// View Job Details
async function viewJobDetails(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const job = await response.json();
        
        document.getElementById('job-details-modal').classList.remove('hidden');
        document.getElementById('detail-job-title').textContent = job.title;
        document.getElementById('detail-job-company').textContent = job.company;
        document.getElementById('detail-job-location').textContent = job.location || 'Remote';
        document.getElementById('detail-job-type').textContent = job.job_type || 'Full-time';
        document.getElementById('detail-job-salary').textContent = job.salary_range || 'Competitive';
        document.getElementById('detail-job-description').textContent = job.description;
        document.getElementById('detail-job-requirements').textContent = job.requirements || 'Not specified';
        
        // Store job ID for apply button
        document.getElementById('apply-from-details-btn').onclick = () => {
            closeJobDetailsModal();
            openApplyModal(jobId);
        };
    } catch (error) {
        console.error('Error loading job details:', error);
        showToast('Failed to load job details.', 'error');
    }
}

function closeJobDetailsModal() {
    document.getElementById('job-details-modal').classList.add('hidden');
}

// ============================================
// RECRUITER: VIEW FULL RESUME
// ============================================

async function showFullResume(applicationId) {
    try {
        // Download PDF directly
        const downloadUrl = `${API_BASE}/applications/${applicationId}/resume-pdf`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `resume-${applicationId}.pdf`;
        
        // Set authorization header by fetching first
        const response = await fetch(downloadUrl, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            link.href = blobUrl;
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(blobUrl);
            document.body.removeChild(link);
            showToast('Resume download started', 'success');
        } else {
            showToast('Failed to download resume', 'error');
        }
    } catch (error) {
        console.error('Error downloading resume:', error);
        showToast('Failed to download resume. Please try again.', 'error');
    }
}

// ============================================
// RECRUITER: CONTACT CANDIDATE
// ============================================

let currentApplicationIdForMessage = null;

function showContactModal(applicationId) {
    currentApplicationIdForMessage = applicationId;
    document.getElementById('contact-modal').classList.remove('hidden');
    document.getElementById('message-subject').value = '';
    document.getElementById('message-content').value = '';
}

function closeContactModal() {
    document.getElementById('contact-modal').classList.add('hidden');
    currentApplicationIdForMessage = null;
}

async function sendMessage() {
    const subject = document.getElementById('message-subject').value.trim();
    const content = document.getElementById('message-content').value.trim();
    
    if (!subject) {
        showToast('Please enter a subject', 'warning');
        return;
    }
    
    if (!content) {
        showToast('Please enter a message', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/applications/${currentApplicationIdForMessage}/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject: subject,
                content: content
            })
        });
        
        if (response.ok) {
            showToast('Message sent successfully!', 'success');
            closeContactModal();
        } else {
            const errorData = await response.json();
            showToast(errorData.detail || 'Failed to send message', 'error');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Failed to send message. Please try again.', 'error');
    }
}

// ============================================
// APPLICANT: VIEW MESSAGES
// ============================================

async function openApplicantMessages() {
    try {
        // Get all applications for current user
        const applicationsResponse = await fetch(`${API_BASE}/applications/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!applicationsResponse.ok) {
            showToast('Failed to load messages', 'error');
            return;
        }
        
        const data = await applicationsResponse.json();
        const applications = data.applications || [];
        
        // Fetch messages for all applications
        let allMessages = [];
        for (const app of applications) {
            try {
                const messagesResponse = await fetch(`${API_BASE}/applications/${app.id}/messages`, {
                    headers: { 'Authorization': `Bearer ${authToken}` }
                });
                
                if (messagesResponse.ok) {
                    const msgData = await messagesResponse.json();
                    allMessages = allMessages.concat((msgData.messages || []).map(msg => ({
                        ...msg,
                        application_id: app.id,
                        job_title: app.job_title || 'Job Application'
                    })));
                }
            } catch (error) {
                console.error('Error fetching messages for app', app.id, error);
            }
        }
        
        // Display messages modal
        displayApplicantMessages(allMessages);
        document.getElementById('applicant-messages-modal').classList.remove('hidden');
        
        // Update badge
        updateMessageBadge(allMessages);
    } catch (error) {
        console.error('Error opening messages:', error);
        showToast('Failed to load messages', 'error');
    }
}

function displayApplicantMessages(messages) {
    const container = document.getElementById('all-messages-content');
    
    if (!messages || messages.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:40px 20px;">
                <p style="color:rgba(232,224,212,.4);font-size:.95rem;">📭 No messages yet</p>
            </div>
        `;
        return;
    }
    
    // Sort by date, newest first
    messages.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    container.innerHTML = messages.map(msg => {
        const date = new Date(msg.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div style="margin-bottom:16px;padding:16px;background:rgba(0,0,0,.2);border:1px solid rgba(212,168,64,.2);border-radius:12px;overflow:hidden;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                    <h4 style="color:#f0e8dc;font-weight:700;font-size:.95rem;margin:0;">${msg.subject || 'Message from Recruiter'}</h4>
                    <span style="font-size:.75rem;color:rgba(232,224,212,.4);">${date}</span>
                </div>
                <p style="color:rgba(232,224,212,.75);margin:0;white-space:pre-wrap;word-wrap:break-word;line-height:1.6;">
                    ${msg.content}
                </p>
            </div>
        `;
    }).join('');
}

function updateMessageBadge(messages) {
    const unreadCount = messages.filter(msg => !msg.is_read).length;
    const badge = document.getElementById('message-badge');
    
    if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function closeApplicantMessages() {
    document.getElementById('applicant-messages-modal').classList.add('hidden');
}

// Check for new messages when dashboard loads
async function checkForNewMessages() {
    if (currentUser && currentUser.user_type === 'job_seeker') {
        try {
            const response = await fetch(`${API_BASE}/applications/`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                const applications = data.applications || [];
                let totalMessages = 0;
                
                for (const app of applications) {
                    try {
                        const messagesResponse = await fetch(`${API_BASE}/applications/${app.id}/messages`, {
                            headers: { 'Authorization': `Bearer ${authToken}` }
                        });
                        
                        if (messagesResponse.ok) {
                            const msgData = await messagesResponse.json();
                            totalMessages += (msgData.messages || []).length;
                        }
                    } catch (error) {
                        console.error('Error fetching message count', error);
                    }
                }
                
                // Update badge without showing notification
                const badge = document.getElementById('message-badge');
                if (totalMessages > 0) {
                    badge.textContent = totalMessages;
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }
            }
        } catch (error) {
            console.error('Error checking messages:', error);
        }
    }
}
