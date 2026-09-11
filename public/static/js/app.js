/**
 * AI Resume Analyzer - Shared JavaScript utilities
 */

const API = {
  base: '/api',

  async request(endpoint, options = {}) {
    const url = `${this.base}${endpoint}`;
    const config = {
      headers: { 'Content-Type': 'application/json', ...options.headers },
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
    return fetch(`${this.base}${endpoint}`, {
      method: 'POST',
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

  // Highlight active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav a').forEach((link) => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
});
