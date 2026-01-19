// ClarityCareers Frontend JavaScript
const API_URL = 'http://localhost:8000';
let currentUser = null;
let authToken = null;
let currentApplicationId = null;
let simSkills = [];
let allJobs = []; // Store all jobs for searching

// â”€â”€ Toast notification system â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function showToast(message, type = 'info', duration = 4000) {
    const icons = { success: 'âœ“', error: 'âœ•', info: 'â„¹' };
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    }, duration);
}

// â”€â”€ Initialize â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        loadCurrentUser();
    }    
    // Setup job search listener
    const searchInput = document.getElementById('job-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            filterJobs(e.target.value);
        });
    }});

// â”€â”€ API Helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });
    if (response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }
    return response;
}

// â”€â”€ Auth Functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function showLogin() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
}

async function register(event) {
    event.preventDefault();
    const data = {
        email: document.getElementById('reg-email').value,
        username: document.getElementById('reg-username').value,
        password: document.getElementById('reg-password').value,
        full_name: document.getElementById('reg-fullname').value,
        user_type: document.getElementById('reg-usertype').value
    };
    try {
        const response = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (response.ok) {
            showToast('Account created! Please sign in.', 'success');
            showLogin();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration error: ' + error.message, 'error');
    }
}

async function login(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);
    try {
        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = data.user;
            showDashboard();
        } else {
            showToast('Login failed. Check your credentials.', 'error');
        }
    } catch (error) {
        showToast('Login error: ' + error.message, 'error');
    }
}

async function loadCurrentUser() {
    try {
        const response = await apiCall('/auth/me');
        if (response.ok) {
            currentUser = await response.json();
            showDashboard();
        }
    } catch (error) {
        console.error('Error loading user:', error);
        logout();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
    const navUser = document.getElementById('nav-user');
    navUser.classList.add('hidden');
    navUser.style.display = 'none';
}

function showDashboard() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-section').classList.remove('hidden');
    const navUser = document.getElementById('nav-user');
    navUser.classList.remove('hidden');
    navUser.style.display = 'flex';
    document.getElementById('user-name').textContent = `${currentUser.full_name || currentUser.username}`;

    if (currentUser.user_type === 'job_seeker') {
        document.getElementById('job-seeker-dashboard').classList.remove('hidden');
        document.getElementById('recruiter-dashboard').classList.add('hidden');
        loadJobs();
        loadMyApplications();
    } else {
        document.getElementById('job-seeker-dashboard').classList.add('hidden');
        document.getElementById('recruiter-dashboard').classList.remove('hidden');
        loadMyJobs();
    }
}

// â”€â”€ Job Functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async function loadJobs() {
    try {
        const response = await apiCall('/jobs/');
        if (response.ok) {
            const jobs = await response.json();
            allJobs = jobs; // Store all jobs for search
            displayJobs(jobs);
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-list');
    container.innerHTML = '';

    if (jobs.length === 0) {
        container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px 20px;color:rgba(226,232,240,0.35);">
            <div style="font-size:3rem;margin-bottom:12px;">ðŸ”</div>
            <p style="font-size:1rem;">No jobs available right now. Check back soon!</p>
        </div>`;
        return;
    }

    jobs.forEach((job, i) => {
        const card = document.createElement('div');
        card.className = 'glass glass-hover slide-up';
        card.style.cssText = `padding:24px;animation-delay:${i * 0.06}s;`;
        card.onclick = () => showJobDetails(job);

        const typeColor = job.job_type === 'Full-time' ? '#39ff14' : job.job_type === 'Contract' ? '#ffd700' : '#00f5ff';

        card.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                <span style="padding:3px 10px;background:rgba(0,245,255,0.08);border:1px solid rgba(0,245,255,0.2);border-radius:6px;font-size:0.72rem;font-weight:700;letter-spacing:0.07em;color:${typeColor};">${job.job_type || 'Full-time'}</span>
                <span style="font-size:0.78rem;color:rgba(226,232,240,0.35);">${job.application_count || 0} applicants</span>
            </div>
            <h3 style="font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:6px;line-height:1.3;">${job.title}</h3>
            <p style="color:var(--neon-cyan);font-weight:600;font-size:0.9rem;margin-bottom:4px;">${job.company}</p>
            <p style="color:rgba(226,232,240,0.45);font-size:0.83rem;margin-bottom:14px;">ðŸ“ ${job.location || 'Remote'}</p>
            <p style="color:rgba(226,232,240,0.6);font-size:0.85rem;line-height:1.6;margin-bottom:16px;">${job.description.substring(0, 130)}â€¦</p>
            <div style="display:flex;justify-content:space-between;align-items:center;padding-top:14px;border-top:1px solid rgba(255,255,255,0.07);">
                ${job.salary_range ? `<span style="color:#ffd700;font-weight:600;font-size:0.85rem;">${job.salary_range}</span>` : '<span></span>'}
                <span style="color:var(--neon-cyan);font-size:0.82rem;font-weight:600;">View & Apply â†’</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function showJobDetails(job) {
    document.getElementById('modal-job-title').textContent = job.title;
    document.getElementById('apply-job-id').value = job.id;

    document.getElementById('modal-job-details').innerHTML = `
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;">
            <span style="padding:6px 14px;background:rgba(0,245,255,0.08);border:1px solid rgba(0,245,255,0.2);border-radius:8px;font-size:0.83rem;color:var(--neon-cyan);">ðŸ¢ ${job.company}</span>
            <span style="padding:6px 14px;background:rgba(0,245,255,0.08);border:1px solid rgba(0,245,255,0.2);border-radius:8px;font-size:0.83rem;color:rgba(226,232,240,0.7);">ðŸ“ ${job.location || 'Remote'}</span>
            <span style="padding:6px 14px;background:rgba(0,245,255,0.08);border:1px solid rgba(0,245,255,0.2);border-radius:8px;font-size:0.83rem;color:rgba(226,232,240,0.7);">â± ${job.job_type}</span>
            ${job.salary_range ? `<span style="padding:6px 14px;background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.25);border-radius:8px;font-size:0.83rem;color:#ffd700;">ðŸ’° ${job.salary_range}</span>` : ''}
        </div>
        <div style="margin-bottom:20px;">
            <h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:rgba(0,245,255,0.6);font-weight:700;margin-bottom:10px;">Description</h4>
            <p style="color:rgba(226,232,240,0.75);line-height:1.8;white-space:pre-wrap;font-size:0.92rem;">${job.description}</p>
        </div>
        ${job.requirements ? `
        <div>
            <h4 style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:rgba(0,245,255,0.6);font-weight:700;margin-bottom:10px;">Requirements</h4>
            <p style="color:rgba(226,232,240,0.75);line-height:1.8;white-space:pre-wrap;font-size:0.92rem;">${job.requirements}</p>
        </div>` : ''}
    `;

    document.getElementById('job-modal').classList.remove('hidden');
}

// â"€â"€ Job Search Functions â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€
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

async function applyToJob(event) {
    event.preventDefault();
    const jobId = document.getElementById('apply-job-id').value;
    const resumeText = document.getElementById('apply-resume').value;

    if (!resumeText.trim()) {
        showToast('Please paste your resume text', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/applications/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                job_id: parseInt(jobId),
                resume_text: resumeText
            })
        });

        if (response.ok) {
            const application = await response.json();
            showToast('Application submitted! Loading your AI matchâ€¦', 'success');
            closeModal('job-modal');
            document.getElementById('apply-resume').value = '';
            loadMyApplications();
            setTimeout(() => showMatchResults(application.id), 800);
        } else {
            const error = await response.json();
            showToast(error.detail || 'Application failed', 'error');
        }
    } catch (error) {
        console.error('Application error:', error);
        showToast('Error submitting application: ' + error.message, 'error');
    }
}

// â”€â”€ Application Functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async function loadMyApplications() {
    try {
        const response = await apiCall('/applications/my-applications');
        if (response.ok) {
            const applications = await response.json();
            displayApplications(applications);
        }
    } catch (error) {
        console.error('Error loading applications:', error);
    }
}

async function deleteApplication(applicationId) {
    if (!confirm('Delete this application? This cannot be undone.')) return;

    try {
        const response = await apiCall(`/applications/${applicationId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            showToast('Application deleted.', 'info');
            loadMyApplications();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to delete application', 'error');
        }
    } catch (error) {
        console.error('Error deleting application:', error);
        showToast('Error deleting application: ' + error.message, 'error');
    }
}

function displayApplications(applications) {
    const container = document.getElementById('applications-list');
    container.innerHTML = '';

    if (applications.length === 0) {
        container.innerHTML = `<div style="text-align:center;padding:60px 20px;color:rgba(226,232,240,0.35);">
            <div style="font-size:3rem;margin-bottom:12px;">ðŸ“‹</div>
            <p>No applications yet. Browse jobs and apply!</p>
        </div>`;
        return;
    }

    applications.forEach((app, i) => {
        const card = document.createElement('div');
        card.className = 'glass slide-up';
        card.style.cssText = `padding:24px;animation-delay:${i * 0.07}s;`;

        const pct = app.match_percentage || 0;
        const scoreClass = pct >= 70 ? 'score-high' : pct >= 50 ? 'score-mid' : 'score-low';
        const barWidth = Math.min(100, pct).toFixed(1);
        const barColor = pct >= 70 ? '#39ff14' : pct >= 50 ? '#ffd700' : '#ff3cac';

        card.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="font-size:1rem;font-weight:700;color:#fff;">Application #${app.id}</span>
                        <span class="badge-status">${app.status}</span>
                    </div>
                    <p style="color:rgba(226,232,240,0.4);font-size:0.82rem;">Applied ${new Date(app.applied_at).toLocaleDateString('en-US',{year:'numeric',month:'short',day:'numeric'})}</p>
                </div>
                <div style="text-align:right;">
                    <p class="${scoreClass}" style="font-size:2rem;font-weight:800;line-height:1;">${pct.toFixed(1)}%</p>
                    <p style="color:rgba(226,232,240,0.45);font-size:0.8rem;margin-top:2px;">${app.prediction || ''} Â· ${app.confidence || ''}</p>
                </div>
            </div>
            <div style="margin:16px 0 6px;">
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width:${barWidth}%;background:linear-gradient(90deg,${barColor},${barColor}cc);"></div>
                </div>
            </div>
            <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap;">
                <button onclick="showMatchResults(${app.id})" class="btn-neon" style="padding:9px 20px;font-size:0.85rem;">View AI Analysis</button>
                <button onclick="deleteApplication(${app.id})" class="btn-danger" style="padding:9px 18px;font-size:0.85rem;">Delete</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function showMatchResults(applicationId) {
    currentApplicationId = applicationId;

    try {
        const matchResponse = await apiCall(`/applications/${applicationId}/match`);
        if (!matchResponse.ok) throw new Error(`Match API failed: ${matchResponse.status}`);
        const matchData = await matchResponse.json();

        const explainResponse = await apiCall(`/applications/${applicationId}/explain`);
        if (!explainResponse.ok) throw new Error(`Explain API failed: ${explainResponse.status}`);
        const explainData = await explainResponse.json();

        const rankResponse = await apiCall(`/applications/${applicationId}/rank`);
        if (!rankResponse.ok) throw new Error(`Rank API failed: ${rankResponse.status}`);
        const rankData = await rankResponse.json();

        displayMatchScore(matchData);
        displayExplanation(explainData);
        displayRanking(rankData);
        document.getElementById('match-modal').classList.remove('hidden');

    } catch (error) {
        console.error('Error loading match results:', error);
        showToast('Error loading match results: ' + error.message, 'error');
    }
}

function displayMatchScore(data) {
    const percentage = data.match_percentage;
    const circle = document.getElementById('match-circle');
    const circumference = 502.65; // r=80
    const offset = circumference - (percentage / 100) * circumference;

    circle.style.strokeDashoffset = offset;
    document.getElementById('match-percentage').textContent = `${percentage.toFixed(1)}%`;
    document.getElementById('match-prediction').textContent = data.prediction;
    document.getElementById('match-confidence').textContent = `${data.confidence} Confidence`;
}

function displayExplanation(data) {
    const container = document.getElementById('positive-features');
    container.innerHTML = '';

    data.top_positive_features.forEach(feature => {
        const width = Math.min(100, Math.abs(feature.impact) * 100);
        const row = document.createElement('div');
        row.style.cssText = 'display:flex;align-items:center;gap:12px;';
        row.innerHTML = `
            <span style="width:120px;font-size:0.82rem;font-weight:600;color:rgba(226,232,240,0.8);text-align:right;flex-shrink:0;">${feature.token}</span>
            <div class="progress-bar-track" style="flex:1;">
                <div class="progress-bar-fill" style="width:${width}%;"></div>
            </div>
            <span style="font-size:0.8rem;color:#39ff14;font-weight:700;width:48px;text-align:right;flex-shrink:0;">+${(feature.impact * 100).toFixed(1)}%</span>
        `;
        container.appendChild(row);
    });

    // Missing skills
    const skillsContainer = document.getElementById('missing-skills');
    skillsContainer.innerHTML = '';
    data.missing_skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'tag-missing';
        tag.textContent = skill;
        skillsContainer.appendChild(tag);
    });

    // Recommendations
    const recsContainer = document.getElementById('recommendations-list');
    recsContainer.innerHTML = '';
    data.recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'rec-card';
        item.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;gap:8px;">
                <span style="font-weight:700;color:#fff;font-size:0.95rem;">${rec.skill}</span>
                <span style="padding:3px 10px;background:rgba(191,95,255,0.12);border:1px solid rgba(191,95,255,0.3);color:var(--neon-purple);border-radius:6px;font-size:0.72rem;font-weight:700;letter-spacing:0.05em;white-space:nowrap;">${rec.priority}</span>
            </div>
            <p style="color:rgba(226,232,240,0.65);font-size:0.86rem;line-height:1.6;margin-bottom:6px;">${rec.suggestion}</p>
            <p style="color:#39ff14;font-size:0.83rem;font-weight:600;">â†‘ ${rec.impact_if_added}</p>
        `;
        recsContainer.appendChild(item);
    });
}

function displayRanking(data) {
    document.getElementById('ranking-message').innerHTML = `
        <span style="font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#00f5ff,#bf5fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${data.percentile.toFixed(1)}th Percentile</span><br>
        <span style="color:rgba(226,232,240,0.75);">Rank ${data.rank_position} of ${data.total_applicants} applicants</span><br>
        <span style="color:rgba(226,232,240,0.45);font-style:italic;font-size:0.88rem;">${data.message}</span>
    `;
}

// â”€â”€ Impact Simulator â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function addSimSkill() {
    const skill = document.getElementById('sim-skill').value.trim();
    if (skill && !simSkills.includes(skill)) {
        simSkills.push(skill);
        updateSimSkillsList();
        document.getElementById('sim-skill').value = '';
    }
}

function updateSimSkillsList() {
    const container = document.getElementById('sim-skills-list');
    container.innerHTML = '';
    simSkills.forEach((skill, index) => {
        const tag = document.createElement('span');
        tag.className = 'tag-sim';
        tag.innerHTML = `${skill}<button onclick="removeSimSkill(${index})">Ã—</button>`;
        container.appendChild(tag);
    });
}

function removeSimSkill(index) {
    simSkills.splice(index, 1);
    updateSimSkillsList();
}

async function runSimulation() {
    if (simSkills.length === 0) {
        showToast('Add at least one skill to simulate', 'info');
        return;
    }
    try {
        const response = await apiCall('/applications/simulate', {
            method: 'POST',
            body: JSON.stringify({
                application_id: currentApplicationId,
                added_skills: simSkills
            })
        });
        if (response.ok) {
            const data = await response.json();
            displaySimResult(data);
        }
    } catch (error) {
        showToast('Simulation error: ' + error.message, 'error');
    }
}

function displaySimResult(data) {
    const container = document.getElementById('sim-result');
    container.classList.remove('hidden');
    const improvement = data.improvement;
    const positive = improvement > 0;
    const color = positive ? '#39ff14' : '#ff3cac';
    container.innerHTML = `
        <h5 style="font-weight:700;margin-bottom:14px;font-size:0.8rem;letter-spacing:0.08em;text-transform:uppercase;color:rgba(226,232,240,0.5);">Simulation Result</h5>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:14px;">
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:14px;text-align:center;">
                <p style="font-size:0.78rem;color:rgba(226,232,240,0.4);margin-bottom:4px;">Current Score</p>
                <p style="font-size:2rem;font-weight:800;color:#fff;">${data.original_percentage.toFixed(1)}%</p>
            </div>
            <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:14px;text-align:center;">
                <p style="font-size:0.78rem;color:rgba(226,232,240,0.4);margin-bottom:4px;">Simulated Score</p>
                <p style="font-size:2rem;font-weight:800;color:${color};">${data.simulated_percentage.toFixed(1)}%</p>
            </div>
        </div>
        <p style="font-size:1.1rem;font-weight:700;color:${color};">${positive ? 'â†‘' : 'â†“'} ${Math.abs(improvement).toFixed(1)}% change</p>
        <p style="color:rgba(226,232,240,0.6);font-size:0.86rem;margin-top:8px;">${data.recommendation}</p>
    `;
}

// â”€â”€ Recruiter Functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async function loadMyJobs() {
    try {
        const response = await apiCall('/jobs/my-jobs');
        if (response.ok) {
            const jobs = await response.json();
            displayRecruiterJobs(jobs);
        }
    } catch (error) {
        console.error('Error loading jobs:', error);
    }
}

function displayRecruiterJobs(jobs) {
    const container = document.getElementById('recruiter-jobs-list');
    container.innerHTML = '';

    if (jobs.length === 0) {
        container.innerHTML = `<div style="text-align:center;padding:60px 20px;color:rgba(226,232,240,0.35);">
            <div style="font-size:3rem;margin-bottom:12px;">ðŸ“</div>
            <p>No jobs posted yet. Click <strong style="color:var(--neon-cyan);">Post New Job</strong> to get started!</p>
        </div>`;
        return;
    }

    jobs.forEach((job, i) => {
        const card = document.createElement('div');
        card.className = 'glass slide-up';
        card.style.cssText = `padding:24px;animation-delay:${i * 0.07}s;`;

        card.innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div style="flex:1;min-width:200px;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <h3 style="font-size:1.15rem;font-weight:700;color:#fff;">${job.title}</h3>
                        <span class="${job.is_active ? 'badge-active' : 'badge-inactive'}">${job.is_active ? 'ACTIVE' : 'INACTIVE'}</span>
                    </div>
                    <p style="color:rgba(226,232,240,0.5);font-size:0.85rem;">ðŸ¢ ${job.company} &nbsp;Â·&nbsp; ðŸ“ ${job.location || 'Remote'}</p>
                </div>
                <div style="text-align:right;">
                    <p style="font-size:1.8rem;font-weight:800;color:var(--neon-cyan);line-height:1;">${job.application_count || 0}</p>
                    <p style="color:rgba(226,232,240,0.4);font-size:0.78rem;margin-top:2px;">Applications</p>
                </div>
            </div>
            <p style="color:rgba(226,232,240,0.55);font-size:0.86rem;line-height:1.7;margin:14px 0;">${job.description.substring(0, 200)}â€¦</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;padding-top:14px;border-top:1px solid rgba(255,255,255,0.07);">
                <button onclick="viewJobApplications(${job.id}, '${job.title.replace(/'/g,"\\'")}' )" class="btn-neon" style="padding:9px 20px;font-size:0.85rem;">View Applicants</button>
            </div>
        `;
        container.appendChild(card);
    });
}

function showPostJobModal() {
    document.getElementById('post-job-modal').classList.remove('hidden');
}

async function postJob(event) {
    event.preventDefault();
    const data = {
        title: document.getElementById('job-title').value,
        company: document.getElementById('job-company').value,
        location: document.getElementById('job-location').value,
        description: document.getElementById('job-description').value,
        requirements: document.getElementById('job-requirements').value,
        job_type: document.getElementById('job-type').value,
        salary_range: document.getElementById('job-salary').value
    };
    try {
        const response = await apiCall('/jobs/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        if (response.ok) {
            showToast('Job posted successfully!', 'success');
            closeModal('post-job-modal');
            event.target.reset();
            loadMyJobs();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to post job', 'error');
        }
    } catch (error) {
        showToast('Error posting job: ' + error.message, 'error');
    }
}

async function viewJobApplications(jobId, jobTitle) {
    try {
        const response = await apiCall(`/applications/job/${jobId}`);
        if (response.ok) {
            const applications = await response.json();
            applications.sort((a, b) => (b.match_percentage || 0) - (a.match_percentage || 0));

            document.getElementById('applicants-modal-title').textContent = `${jobTitle} â€” ${applications.length} Applicant${applications.length !== 1 ? 's' : ''}`;
            const listEl = document.getElementById('applicants-list');
            listEl.innerHTML = '';

            if (applications.length === 0) {
                listEl.innerHTML = `<p style="text-align:center;color:rgba(226,232,240,0.35);padding:40px 0;">No applicants yet.</p>`;
            } else {
                applications.forEach((app, i) => {
                    const pct = app.match_percentage || 0;
                    const scoreClass = pct >= 70 ? 'score-high' : pct >= 50 ? 'score-mid' : 'score-low';
                    const row = document.createElement('div');
                    row.style.cssText = `background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;transition:all 0.2s ease;animation:slideUp 0.3s ease ${i*0.05}s both;`;
                    row.innerHTML = `
                        <div>
                            <p style="font-weight:600;color:#fff;font-size:0.93rem;">Applicant #${app.applicant_id}</p>
                            <p style="color:rgba(226,232,240,0.4);font-size:0.78rem;margin-top:2px;">${app.prediction || ''} Â· ${app.confidence || ''} confidence</p>
                        </div>
                        <div style="display:flex;align-items:center;gap:16px;">
                            <span class="${scoreClass}" style="font-size:1.4rem;font-weight:800;">${pct.toFixed(1)}%</span>
                            <span style="font-size:0.78rem;color:rgba(226,232,240,0.35);">Rank #${i + 1}</span>
                        </div>
                    `;
                    listEl.appendChild(row);
                });
            }
            document.getElementById('applicants-modal').classList.remove('hidden');
        }
    } catch (error) {
        showToast('Error loading applications: ' + error.message, 'error');
    }
}

// â”€â”€ UI Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function showTab(tabId) {
    document.getElementById('jobs-tab').classList.add('hidden');
    document.getElementById('applications-tab').classList.add('hidden');
    document.getElementById(tabId).classList.remove('hidden');

    // Update tab button active states
    document.getElementById('tab-btn-jobs').classList.toggle('active', tabId === 'jobs-tab');
    document.getElementById('tab-btn-apps').classList.toggle('active', tabId === 'applications-tab');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
    if (modalId === 'match-modal') {
        simSkills = [];
        updateSimSkillsList();
        document.getElementById('sim-result').classList.add('hidden');
    }
}

// Close modal on background click
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', e => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    });
});
