/**
 * Project Genesis Dashboard - Core Logic (v6.0.0)
 * Handles navigation, modals, and the main dashboard view.
 */

const SECTION_COLORS = {
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
};

// --- NAVIGATION & UI CORE ---

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  
  const target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');
  
  // Update buttons (handling both core and dynamic ones)
  document.querySelectorAll('.tab-btn').forEach(btn => {
    if (btn.getAttribute('onclick')?.includes(`'${tabId}'`)) btn.classList.add('active');
  });

  if (tabId === 'dashboard') initDashboard();
  if (tabId === 'diagnostics') loadDiagnostics();
}

function esc(str) {
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container') || document.body;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

// --- MAIN DASHBOARD RENDERERS ---

function initDashboard() {
  renderAgentName();
  renderStats();
  renderSoulTree();
  renderFeed();
  renderVitals();
  renderMentalActivity();
}

function renderAgentName() {
  const idText = DATA.identity_raw || '';
  const nameMatch = idText.match(/Name:\s*(.+)/i);
  if (nameMatch) {
    const name = nameMatch[1].replace(/\[|\]/g, '').trim();
    const el = document.getElementById('agent-name');
    if (el) el.textContent = name;
  }
}

function renderStats() {
  const bar = document.getElementById('stats-bar');
  if (!bar) return;
  const stats = [
    { num: DATA.experiences?.length || 0, label: 'Experiences' },
    { num: DATA.reflections?.length || 0, label: 'Reflections' },
    { num: DATA.soul_tree?.length || 0, label: 'Sections' }
  ];
  bar.innerHTML = stats.map(s => `<div class="stat"><div class="num">${s.num}</div><div class="label">${s.label}</div></div>`).join('');
}

function renderSoulTree() {
  const container = document.getElementById('soul-tree');
  if (!container) return;
  container.innerHTML = (DATA.soul_tree || []).map(sec => `
    <div class="section-block">
      <div class="section-header">${esc(sec.text)}</div>
      <div class="section-body">
        ${(sec.children || []).map(c => `
          <div class="bullet">${esc(c.text)}</div>
        `).join('')}
      </div>
    </div>
  `).join('');
}

function renderFeed() {
  const container = document.getElementById('exp-feed');
  if (!container) return;
  container.innerHTML = (DATA.experiences || []).slice(-10).reverse().map(e => `
    <div class="exp-entry">
      <small>${esc(e.source)}</small>
      <p>${esc(e.content)}</p>
    </div>
  `).join('') || 'No experiences yet.';
}

function renderVitals() {
  const grid = document.getElementById('vitals-grid');
  if (!grid || !DATA.physique?.needs) return;
  grid.innerHTML = Object.entries(DATA.physique.needs).map(([k, v]) => `
    <div class="vital-row">
      <span>${k}</span>
      <div class="vital-bar-bg"><div class="vital-bar" style="width:${v}%"></div></div>
      <span>${v}</span>
    </div>
  `).join('');
}

function renderMentalActivity() {
  const container = document.getElementById('mental-activity-list');
  if (!container) return;
  container.innerHTML = '<div class="mental-card">System Synchronized</div>';
}

// --- DIAGNOSTICS ---

async function loadDiagnostics() {
  const container = document.getElementById('log-stream');
  if (!container) return;
  container.innerHTML = 'Loading system logs...';
  try {
    const resp = await fetch('/api/logs/recent');
    const logs = await resp.json();
    container.innerHTML = logs.map(l => `<div>[${l.level}] ${l.module}: ${l.message}</div>`).join('');
  } catch(e) { container.innerHTML = 'Error loading logs.'; }
}

// Global Exports
window.switchTab = switchTab;
window.initDashboard = initDashboard;
window.showToast = showToast;
window.esc = esc;
