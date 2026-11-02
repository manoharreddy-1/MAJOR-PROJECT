/**
 * AI Resume Analyzer - Shared JavaScript utilities
 */

const API = {
  base: '/api',

  async request(endpoint, options = {}) {
    const url = `${this.base}${endpoint}`;
    let storedUser = null;
    try {
      const rawUser = localStorage.getItem('user');
      if (rawUser) storedUser = JSON.parse(rawUser);
    } catch (e) {}

    const authHeaders = {};
    if (storedUser) {
      if (storedUser.role) authHeaders['X-User-Role'] = storedUser.role;
      if (storedUser.user_id) authHeaders['X-User-Id'] = storedUser.user_id;
      if (storedUser.token) authHeaders['Authorization'] = `Bearer ${storedUser.token}`;
    }

    const config = {
      headers: { 'Content-Type': 'application/json', ...authHeaders, ...options.headers },
      ...options,
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error?.message || 'Request failed');
      }
      return data;
    } catch (error) {
      if (error.message === 'Failed to fetch') {
        throw new Error('Network error. Please check your connection.');
      }
      throw error;
    }
  },

  upload(endpoint, formData) {
    let storedUser = null;
    try {
      const rawUser = localStorage.getItem('user');
      if (rawUser) storedUser = JSON.parse(rawUser);
    } catch (e) {}

    const authHeaders = {};
    if (storedUser) {
      if (storedUser.role) authHeaders['X-User-Role'] = storedUser.role;
      if (storedUser.user_id) authHeaders['X-User-Id'] = storedUser.user_id;
      if (storedUser.token) authHeaders['Authorization'] = `Bearer ${storedUser.token}`;
    }

    return fetch(`${this.base}${endpoint}`, {
      method: 'POST',
      headers: authHeaders,
      body: formData,
    }).then(async (res) => {
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error?.message || 'Upload failed');
      }
      return data;
    });
  },
};

// Session storage helpers
const Store = {
  set(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
  },
  get(key) {
    const item = sessionStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  },
  remove(key) {
    sessionStorage.removeItem(key);
  },
};

// UI Helpers
const UI = {
  showLoading(container, message = 'Processing...') {
    container.innerHTML = `
      <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <p class="text-muted">${message}</p>
      </div>`;
  },

  showError(container, message) {
    container.innerHTML = `<div class="error-state">${message}</div>`;
  },

  showEmpty(container, icon, message) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">${icon}</div>
        <p>${message}</p>
      </div>`;
  },

  createScoreGauge(score, label = 'ATS Score') {
    const circumference = 2 * Math.PI * 70;
    const offset = circumference - (score / 100) * circumference;
    const color = score >= 80 ? '#22c55e' : score >= 65 ? '#0ea5e9' : score >= 50 ? '#f59e0b' : '#ef4444';

    return `
      <div class="score-gauge">
        <svg width="180" height="180" viewBox="0 0 180 180">
          <circle cx="90" cy="90" r="70" fill="none" stroke="#e2e8f0" stroke-width="12"/>
          <circle cx="90" cy="90" r="70" fill="none" stroke="${color}" stroke-width="12"
            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
            stroke-linecap="round"/>
        </svg>
        <div class="score-value">
          <div class="score-number">${Math.round(score)}</div>
          <div class="score-label">${label}</div>
        </div>
      </div>`;
  },

  createProgressBar(label, score, cssClass) {
    return `
      <div class="progress-item">
        <div class="progress-header">
          <span>${label}</span>
          <span><strong>${Math.round(score)}%</strong></span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill ${cssClass}" style="width: ${score}%"></div>
        </div>
      </div>`;
  },

  initTabs(container) {
    const tabs = container.querySelectorAll('.tab');
    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.tab;
        container.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
        container.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));
        tab.classList.add('active');
        container.querySelector(`#${target}`)?.classList.add('active');
      });
    });
  },

  initNavToggle() {
    const toggle = document.querySelector('.nav-toggle');
    const nav = document.querySelector('.navbar-nav');
    if (toggle && nav) {
      toggle.addEventListener('click', () => nav.classList.toggle('open'));
    }
  },

  formatDate(isoString) {
    if (!isoString) return 'N/A';
    return new Date(isoString).toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric',
    });
  },
};

// File upload handler
function initUploadZone(zoneId, inputId, onFile) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  if (!zone || !input) return;

  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      onFile(e.dataTransfer.files[0]);
    }
  });
  input.addEventListener('change', () => {
    if (input.files.length) onFile(input.files[0]);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  UI.initNavToggle();

  // Authentication Guard & Dynamic Navigation Bar
  const path = window.location.pathname;
  const isLoginPage = (path === '/' || path === '/login');

  // Check user session
  let user = null;
  try {
    const rawUser = localStorage.getItem('user');
    if (rawUser) user = JSON.parse(rawUser);
  } catch (e) {}

  // 1. If not logged in and attempting to access protected features, redirect to /login
  if (!user && !isLoginPage) {
    window.location.href = '/login';
    return;
  }

  // 2. If logged in and on the login page, redirect directly to dashboard /home
  if (user && isLoginPage) {
    window.location.href = '/home';
    return;
  }

  // 3. Dynamically configure navigation bar visibility based on auth state
  const navList = document.querySelector('.navbar-nav');
  if (navList) {
    if (!user) {
      // User NOT logged in: only show Login link, hide all feature tabs
      navList.innerHTML = `
        <li><a href="/login" class="active">Login</a></li>
      `;
    } else {
      // User IS logged in: reveal all features, analysis, courses, history, and profile
      navList.innerHTML = `
        <li><a href="/home" ${path === '/home' || path === '/dashboard' ? 'class="active"' : ''}>Home</a></li>
        <li><a href="/resume-analysis" ${path.startsWith('/resume-analysis') || path === '/analyze' ? 'class="active"' : ''}>Resume Analysis</a></li>
        <li><a href="/courses" ${path.startsWith('/course') ? 'class="active"' : ''}>AI Courses</a></li>
        <li><a href="/history" ${path === '/history' ? 'class="active"' : ''}>History</a></li>
        <li><a href="/profile" ${path === '/profile' ? 'class="active"' : ''}>Profile</a></li>
        <li><a href="javascript:void(0)" onclick="logoutUser()" style="color: #ef4444; font-weight: 600;">Sign Out</a></li>
      `;
    }
  }

  // Highlight active nav link fallback
  document.querySelectorAll('.navbar-nav a').forEach((link) => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
});

function logoutUser() {
  localStorage.removeItem('user');
  sessionStorage.clear();
  window.location.href = '/login';
}


// ========================================================
// AI Resume Optimizer State & Handlers
// ========================================================
let latestOptimization = null;

async function triggerResumeOptimization(confirmedSkills = []) {
  const btn = document.getElementById('createResumeAiBtn');
  const container = document.getElementById('aiResumeContainer');
  const loading = document.getElementById('aiResumeLoading');
  const results = document.getElementById('aiResumeResults');
  const errBox = document.getElementById('aiResumeError');

  if (!container || !loading || !results) return;

  if (errBox) {
    errBox.style.display = 'none';
    errBox.innerHTML = '';
  }

  const analysis = Store.get('analysis_data') || {};
  const resume = Store.get('resume_data') || analysis.resume_data || analysis.resume || {};
  const job = Store.get('job_data') || analysis.job_data || analysis.job || {};
  const skills = analysis.skill_analysis || {};

  const missingSkills = (skills.missing || []).map(s => typeof s === 'string' ? s : s.skill).filter(Boolean);
  const matchedSkills = (skills.matched || []).map(s => typeof s === 'string' ? s : s.skill).filter(Boolean);
  const currentScore = analysis.scores?.overall || analysis.overall_score || 50;

  // UI loading state
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span>⏳</span> Optimizing your resume…';
  }
  container.style.display = 'block';
  loading.style.display = 'block';
  results.style.display = 'none';

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const payload = {
    analysis_id: Store.get('analysis_id') || analysis.analysis_id,
    resume_id: Store.get('resume_id') || analysis.resume_id || resume.resume_id,
    job_id: Store.get('job_id') || analysis.job_description_id || job.job_id,
    resume_data: resume,
    job_data: job,
    missing_skills: missingSkills,
    matched_skills: matchedSkills,
    current_score: currentScore,
    confirmed_skills: confirmedSkills,
  };

  try {
    const res = await API.request('/optimize-resume', {
      method: 'POST',
      body: payload,
    });

    latestOptimization = res.data;
    renderOptimizationView(latestOptimization);

    loading.style.display = 'none';
    results.style.display = 'block';
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span>✨</span> Re-optimize with AI';
    }
  } catch (err) {
    loading.style.display = 'none';
    results.style.display = 'none';
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span>✨</span> Create Resume with AI';
    }
    if (errBox) {
      errBox.style.display = 'block';
      errBox.innerHTML = `
        <div class="card mb-3" style="border: 1px solid #f87171; background: #fef2f2; padding: 1.5rem; text-align: center;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
          <h4 style="color: #991b1b; font-weight: 700; margin-bottom: 0.5rem;">Could Not Optimize Resume</h4>
          <p style="color: #b91c1c; font-size: 0.875rem; margin-bottom: 1rem;">${err.message || 'Unable to optimize resume. Please check your network or try again.'}</p>
          <button class="btn btn-primary" onclick="triggerResumeOptimization()">Try Again</button>
        </div>
      `;
    }
  }
}

function renderOptimizationView(data) {
  if (!data) return;

  // 1. Scores & Banner
  const oldScoreEl = document.getElementById('optOldScore');
  const newScoreEl = document.getElementById('optNewScore');
  const deltaBadgeEl = document.getElementById('optScoreDeltaBadge');
  const summaryEl = document.getElementById('optChangesSummary');

  if (oldScoreEl) oldScoreEl.textContent = `${data.old_score || 0}%`;
  if (newScoreEl) newScoreEl.textContent = `${data.new_score || 0}%`;

  const delta = (data.score_delta !== undefined) ? data.score_delta : Math.round((data.new_score - data.old_score) * 10) / 10;
  if (deltaBadgeEl) {
    deltaBadgeEl.textContent = `${delta >= 0 ? '+' : ''}${delta}% ATS Boost`;
    deltaBadgeEl.className = `badge badge-${delta >= 0 ? 'success' : 'warning'}`;
  }
  if (summaryEl) summaryEl.textContent = data.changes_summary || 'Your resume has been systematically aligned with the target role.';

  // 2. Added Skills Pills
  const addedListEl = document.getElementById('optAddedSkillsList');
  if (addedListEl) {
    const added = data.added_skills || [];
    if (!added.length) {
      addedListEl.innerHTML = '<span class="text-muted" style="font-size: 0.8125rem;">No new skills added (resume already had high coverage).</span>';
    } else {
      addedListEl.innerHTML = added.map(a => `
        <span class="skill-pill-badge added">
          <strong>+ ${a.skill}</strong>
          <span style="font-size: 0.75rem; color: #047857; margin-left: 0.25rem;">(${a.placed_in || 'Skills'})</span>
        </span>
      `).join('');
    }
  }

  // 3. Needs Confirmation Checklist
  const confBox = document.getElementById('optConfirmationBox');
  const confList = document.getElementById('optConfirmationCheckboxes');
  const unconfirmed = data.needs_user_confirmation || [];
  if (confBox && confList) {
    if (unconfirmed.length > 0) {
      confBox.style.display = 'block';
      confList.innerHTML = unconfirmed.map((c, i) => `
        <label style="display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.875rem; cursor: pointer;">
          <input type="checkbox" value="${c.skill}" class="unconfirmed-skill-chk" style="margin-top: 0.25rem;">
          <div>
            <strong>${c.skill}</strong> &mdash;
            <span class="text-muted" style="font-size: 0.8125rem;">${c.reason || 'Confirm if you have hands-on experience.'}</span>
          </div>
        </label>
      `).join('');
    } else {
      confBox.style.display = 'none';
    }
  }

  // 4. Side-by-side Resume Preview
  const origEl = document.getElementById('originalResumePreview');
  const optEl = document.getElementById('optimizedResumePreview');
  const addedSkillNames = (data.added_skills || []).map(a => a.skill);

  if (origEl) {
    origEl.innerHTML = formatResumeHtml(data.original, []);
  }
  if (optEl) {
    optEl.innerHTML = formatResumeHtml(data.optimized, addedSkillNames);
  }
}

function formatResumeHtml(res, highlights = []) {
  if (!res) return '<p class="text-muted">No resume details provided.</p>';

  const highlightText = (txt) => {
    if (!txt || !highlights.length) return txt || '';
    let result = String(txt);
    highlights.forEach(h => {
      if (h && h.length > 1) {
        const regex = new RegExp(`\\b(${h})\\b`, 'gi');
        result = result.replace(regex, '<span class="highlight-addition">$1</span>');
      }
    });
    return result;
  };

  let html = '';

  // Header / Name
  html += `<div style="text-align: center; margin-bottom: 1rem;">
    <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--primary); margin-bottom: 0.25rem;">${res.name || 'Candidate Name'}</h3>`;
  const contact = res.contact || {};
  const cParts = [contact.email, contact.phone, contact.location, contact.linkedin, contact.github].filter(Boolean);
  if (cParts.length) {
    html += `<p class="text-muted" style="font-size: 0.8125rem;">${cParts.join(' | ')}</p>`;
  }
  html += `</div>`;

  // Summary
  if (res.summary) {
    html += `<h2>Professional Summary</h2>`;
    html += `<p style="margin-bottom: 0.75rem;">${highlightText(res.summary)}</p>`;
  }

  // Skills
  if (res.skills) {
    html += `<h2>Technical Skills</h2>`;
    if (typeof res.skills === 'object' && !Array.isArray(res.skills)) {
      html += `<ul>`;
      for (const [cat, items] of Object.entries(res.skills)) {
        const itemList = Array.isArray(items) ? items : [items];
        html += `<li><strong>${cat}:</strong> ${highlightText(itemList.join(', '))}</li>`;
      }
      html += `</ul>`;
    } else if (Array.isArray(res.skills)) {
      html += `<p>${highlightText(res.skills.join(', '))}</p>`;
    }
  }

  // Experience
  if (res.experience && res.experience.length) {
    html += `<h2>Professional Experience</h2>`;
    res.experience.forEach(exp => {
      if (typeof exp === 'object') {
        const meta = [exp.company, exp.duration].filter(Boolean).join(' | ');
        html += `<div style="margin-bottom: 0.75rem;">
          <div style="font-weight: 700; color: var(--primary);">${exp.title || 'Role'} ${meta ? `<span class="text-muted" style="font-weight: normal; font-size: 0.8125rem;">(${meta})</span>` : ''}</div>`;
        if (exp.bullets && exp.bullets.length) {
          html += `<ul>${exp.bullets.map(b => `<li>${highlightText(b)}</li>`).join('')}</ul>`;
        }
        html += `</div>`;
      } else {
        html += `<p>${highlightText(exp)}</p>`;
      }
    });
  }

  // Projects
  if (res.projects && res.projects.length) {
    html += `<h2>Technical Projects</h2>`;
    res.projects.forEach(p => {
      if (typeof p === 'object') {
        const stack = p.tech_stack ? ` <span class="text-muted" style="font-size: 0.8125rem;">[${p.tech_stack.join(', ')}]</span>` : '';
        html += `<div style="margin-bottom: 0.75rem;">
          <div style="font-weight: 700; color: var(--primary);">${p.title || 'Project'}${stack}</div>`;
        if (p.bullets && p.bullets.length) {
          html += `<ul>${p.bullets.map(b => `<li>${highlightText(b)}</li>`).join('')}</ul>`;
        }
        html += `</div>`;
      } else {
        html += `<p>${highlightText(p)}</p>`;
      }
    });
  }

  // Education
  if (res.education && res.education.length) {
    html += `<h2>Education</h2>`;
    html += `<ul>`;
    res.education.forEach(ed => {
      if (typeof ed === 'object') {
        const meta = [ed.institution, ed.year].filter(Boolean).join(' | ');
        html += `<li><strong>${ed.degree || 'Degree'}</strong> ${meta ? `&mdash; ${meta}` : ''}</li>`;
      } else {
        html += `<li>${ed}</li>`;
      }
    });
    html += `</ul>`;
  }

  return html;
}

function reoptimizeWithConfirmedSkills() {
  const checkboxes = document.querySelectorAll('.unconfirmed-skill-chk:checked');
  const confirmed = Array.from(checkboxes).map(cb => cb.value);
  if (!confirmed.length) {
    alert('Please check at least one skill to confirm.');
    return;
  }
  triggerResumeOptimization(confirmed);
}

function resetOptimizedEdits() {
  if (latestOptimization) {
    const optEl = document.getElementById('optimizedResumePreview');
    const addedSkillNames = (latestOptimization.added_skills || []).map(a => a.skill);
    if (optEl) {
      optEl.innerHTML = formatResumeHtml(latestOptimization.optimized, addedSkillNames);
    }
  }
}

async function downloadOptimizedDocx() {
  if (!latestOptimization || !latestOptimization.structured_optimized) {
    alert('Please generate the AI resume first.');
    return;
  }
  try {
    const res = await fetch('/api/optimize-resume/export/docx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ structured_optimized: latestOptimization.structured_optimized })
    });
    if (!res.ok) throw new Error('Download failed');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const rawName = latestOptimization.structured_optimized.name || 'Candidate';
    const cleanName = rawName.replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_') || 'Candidate';
    a.download = `ATS_Optimized_Resume_${cleanName}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert('Error downloading DOCX: ' + err.message);
  }
}

async function downloadOptimizedPdf() {
  if (!latestOptimization || !latestOptimization.structured_optimized) {
    alert('Please generate the AI resume first.');
    return;
  }
  try {
    const res = await fetch('/api/optimize-resume/export/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ structured_optimized: latestOptimization.structured_optimized })
    });
    if (!res.ok) throw new Error('Download failed');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const rawName = latestOptimization.structured_optimized.name || 'Candidate';
    const cleanName = rawName.replace(/[^\w\s-]/g, '').trim().replace(/\s+/g, '_') || 'Candidate';
    a.download = `ATS_Optimized_Resume_${cleanName}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert('Error downloading PDF: ' + err.message);
  }
}

function copyOptimizedText() {
  const optEl = document.getElementById('optimizedResumePreview');
  if (!optEl) return;
  const text = optEl.innerText;
  navigator.clipboard.writeText(text).then(() => {
    alert('ATS Optimized resume text copied to clipboard!');
  }).catch(() => {
    alert('Could not copy to clipboard.');
  });
}
