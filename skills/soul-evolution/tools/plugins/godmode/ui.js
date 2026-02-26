/**
 * God-Mode Plugin UI Module (v1.0.0)
 * Handles direct simulation manipulation.
 */

async function initGodMode() {
  const root = document.getElementById('plugin-root-godmode');
  if (!root) return;

  // 1. Build UI Structure
  root.innerHTML = `
    <div class="godmode-container">
      <div class="panel-card">
        <h3>🎚️ Direct Needs Control</h3>
        <div id="gm-sliders-plugin" class="sliders-grid">
          Loading Current State...
        </div>
        <button class="btn-primary" onclick="window.GodModePlugin.applyNeeds()" style="margin-top:1.5rem; width:100%;">💾 Apply Changes</button>
      </div>

      <div class="panel-card">
        <h3>🎲 Inject Life Event</h3>
        <div class="inject-form">
          <label>Type</label>
          <select id="gm-event-type-plugin">
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
            <option value="neutral">Neutral</option>
          </select>
          
          <label>Description</label>
          <input type="text" id="gm-event-desc-plugin" placeholder="Event description...">
          
          <label>Impact (1-10)</label>
          <input type="range" id="gm-event-impact-plugin" min="1" max="10" value="5">
          
          <button class="btn-primary" onclick="window.GodModePlugin.injectEvent()" style="margin-top:1rem;">🚀 Trigger Event</button>
        </div>
      </div>
    </div>
  `;

  // 2. Load and Populate Sliders
  const sliders = ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'];
  const container = document.getElementById('gm-sliders-plugin');
  
  try {
    const resp = await fetch('/api/plugins/godmode/physique');
    const data = await resp.json();
    const needs = data.needs || {};

    container.innerHTML = '';
    sliders.forEach(k => {
      const val = needs[k] || 50;
      const row = document.createElement('div');
      row.className = 'slider-row';
      row.innerHTML = `
        <label>${k}</label>
        <input type="range" id="gm-p-${k}" min="0" max="100" value="${val}" oninput="document.getElementById('gm-p-${k}-val').textContent=this.value">
        <span id="gm-p-${k}-val" class="slider-value">${val}</span>
      `;
      container.appendChild(row);
    });
  } catch(e) {
    container.innerHTML = `<div class="error">Failed to load physique state: ${e.message}</div>`;
  }
}

// Global API for the plugin
window.GodModePlugin = {
  init: initGodMode,
  applyNeeds: async () => {
    const needs = {};
    ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'].forEach(k => {
      const el = document.getElementById('gm-p-' + k);
      if (el) needs[k] = parseInt(el.value);
    });
    
    try {
      const res = await fetch('/api/plugins/godmode/override/needs', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(needs)
      });
      const result = await res.json();
      if (result.success) showToast('✅ Needs updated successfully!', 'success');
    } catch(e) { showToast('Error: ' + e.message, 'error'); }
  },
  injectEvent: async () => {
    const event = {
      type: document.getElementById('gm-event-type-plugin').value,
      event: document.getElementById('gm-event-desc-plugin').value || 'Manual Override',
      impact: parseInt(document.getElementById('gm-event-impact-plugin').value)
    };
    
    try {
      const res = await fetch('/api/plugins/godmode/inject/event', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(event)
      });
      const result = await res.json();
      if (result.success) {
        showToast('🎲 Event injected!', 'success');
        document.getElementById('gm-event-desc-plugin').value = '';
      }
    } catch(e) { showToast('Error: ' + e.message, 'error'); }
  }
};

// Start if tab is already active
if (document.getElementById('tab-godmode')) initGodMode();
