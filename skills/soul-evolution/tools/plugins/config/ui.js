/**
 * System Config Plugin UI Module (v1.0.0)
 * Handles System settings, MAC models and API keys.
 */

async function initConfig() {
  const root = document.getElementById('plugin-root-config');
  if (!root) return;

  // 1. Build UI Structure
  root.innerHTML = `
    <div class="config-container">
      <div class="panel-card">
        <h3>🧠 MAC Model Assignments</h3>
        <div class="config-grid">
          <label>Persona (Main Identity)</label>
          <select id="cfg-m-persona" class="mac-select"></select>
          <label>Limbic (Emotions)</label>
          <select id="cfg-m-limbic" class="mac-select"></select>
          <label>Analyst (Reasoning)</label>
          <select id="cfg-m-analyst" class="mac-select"></select>
          <label>Developer (Coding)</label>
          <select id="cfg-m-developer" class="mac-select"></select>
        </div>
      </div>

      <div class="panel-card">
        <h3>🔑 API Keys & Providers</h3>
        <div class="config-grid">
          <label>OpenAI / OpenClaw Key</label>
          <input type="password" id="cfg-k-openai" placeholder="sk-...">
          <label>Anthropic Key</label>
          <input type="password" id="cfg-k-anthropic" placeholder="sk-ant-...">
          <label>Gemini Key</label>
          <input type="password" id="cfg-k-gemini">
          <label>X.AI (Grok) Key</label>
          <input type="password" id="cfg-k-xai">
        </div>
      </div>

      <div class="panel-card full-width">
        <h3>⚡ Metabolism & Simulation</h3>
        <div class="config-grid-3">
          <div class="slider-box">
            <label>Hunger Rate: <span id="cfg-s-hunger-val">0.5</span></label>
            <input type="range" id="cfg-s-hunger" min="0" max="2" step="0.1" value="0.5">
          </div>
          <div class="slider-box">
            <label>Thirst Rate: <span id="cfg-s-thirst-val">0.5</span></label>
            <input type="range" id="cfg-s-thirst" min="0" max="2" step="0.1" value="0.5">
          </div>
          <div class="slider-box">
            <label>Energy Drain: <span id="cfg-s-energy-val">0.5</span></label>
            <input type="range" id="cfg-s-energy" min="0" max="2" step="0.1" value="0.5">
          </div>
        </div>
      </div>

      <div class="action-bar full-width">
        <div id="cfg-status"></div>
        <button class="btn-save-plugin" onclick="window.ConfigPlugin.save()">💾 Save All Settings</button>
      </div>
    </div>
  `;

  // 2. Load Data
  await loadData();
  
  // 3. Add Listeners
  root.addEventListener('input', (e) => {
    if (e.target.type === 'range') {
      const valEl = document.getElementById(e.target.id + '-val');
      if (valEl) valEl.textContent = e.target.value;
    }
  });
}

async function loadData() {
  try {
    // Load Models
    const modelsResp = await fetch('/api/plugins/config/openclaw/models');
    const modelsData = await modelsResp.json();
    const selects = document.querySelectorAll('.mac-select');
    
    selects.forEach(select => {
      select.innerHTML = '<option value="">-- Select Model --</option>';
      (modelsData.models || []).forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id; opt.textContent = m.name;
        select.appendChild(opt);
      });
    });

    // Load Config
    const configResp = await fetch('/api/plugins/config/all');
    const data = await configResp.json();
    const m = data.models || {};
    const s = data.simulation || {};

    // Apply assignments
    if (m.mac_assignments) {
      document.getElementById('cfg-m-persona').value = m.mac_assignments.persona || '';
      document.getElementById('cfg-m-limbic').value = m.mac_assignments.limbic || '';
      document.getElementById('cfg-m-analyst').value = m.mac_assignments.analyst || '';
      document.getElementById('cfg-m-developer').value = m.mac_assignments.developer || '';
    }

    // Apply keys
    document.getElementById('cfg-k-openai').value = m.api_key || '';
    document.getElementById('cfg-k-anthropic').value = m.key_anthropic || '';
    document.getElementById('cfg-k-gemini').value = m.key_gemini || '';
    document.getElementById('cfg-k-xai').value = m.key_xai || '';

    // Apply simulation
    if (s.metabolism) {
      const mb = s.metabolism;
      document.getElementById('cfg-s-hunger').value = mb.hunger_rate || 0.5;
      document.getElementById('cfg-s-thirst').value = mb.thirst_rate || 0.5;
      document.getElementById('cfg-s-energy').value = mb.energy_rate || 0.5;
      
      document.getElementById('cfg-s-hunger-val').textContent = mb.hunger_rate || 0.5;
      document.getElementById('cfg-s-thirst-val').textContent = mb.thirst_rate || 0.5;
      document.getElementById('cfg-s-energy-val').textContent = mb.energy_rate || 0.5;
    }

  } catch(e) { console.error("Config Load Error:", e); }
}

// Global API
window.ConfigPlugin = {
  init: initConfig,
  save: async () => {
    const status = document.getElementById('cfg-status');
    status.textContent = "Saving..."; status.style.color = "var(--accent)";

    const payload = {
      models: {
        mac_assignments: {
          persona: document.getElementById('cfg-m-persona').value,
          limbic: document.getElementById('cfg-m-limbic').value,
          analyst: document.getElementById('cfg-m-analyst').value,
          developer: document.getElementById('cfg-m-developer').value,
        },
        api_key: document.getElementById('cfg-k-openai').value,
        key_anthropic: document.getElementById('cfg-k-anthropic').value,
        key_gemini: document.getElementById('cfg-k-gemini').value,
        key_xai: document.getElementById('cfg-k-xai').value,
      },
      simulation: {
        metabolism: {
          hunger_rate: parseFloat(document.getElementById('cfg-s-hunger').value),
          thirst_rate: parseFloat(document.getElementById('cfg-s-thirst').value),
          energy_rate: parseFloat(document.getElementById('cfg-s-energy').value),
        }
      }
    };

    try {
      const res = await fetch('/api/plugins/config/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();
      if (result.success) {
        status.textContent = "✓ Saved Successfully!"; status.style.color = "var(--growth)";
        setTimeout(() => status.textContent = "", 3000);
      }
    } catch(e) { status.textContent = "✗ Error: " + e.message; status.style.color = "var(--danger)"; }
  }
};

if (document.getElementById('tab-config')) initConfig();
