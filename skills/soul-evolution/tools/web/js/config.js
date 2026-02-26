/**
 * Project Genesis Dashboard - Configuration & Tuning (v5.7.0)
 */

async function loadClawModels() {
  try {
    const resp = await fetch('/api/openclaw/models');
    const data = await resp.json();
    const selects = document.querySelectorAll('.mac-select-main, .mac-select');
    
    selects.forEach(select => {
      const currentVal = select.value;
      select.innerHTML = '<option value="">-- Select Model --</option>';
      data.models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.textContent = m.name;
        if (currentVal === m.id) opt.selected = true;
        select.appendChild(opt);
      });
    });
    return data.models;
  } catch(e) {
    console.error("Failed to load models:", e);
  }
}

async function loadConfig() {
  try {
    await loadClawModels();
    const response = await fetch('/api/config/all');
    const config = await response.json();

    const modelResp = await fetch('/api/model/config');
    const modelCfg = await modelResp.json();
    const assignments = modelCfg.mac_assignments || {};

    if (assignments.persona) document.getElementById('config-model-persona').value = assignments.persona;
    if (assignments.limbic) document.getElementById('config-model-limbic').value = assignments.limbic;
    if (assignments.analyst) document.getElementById('config-model-analyst').value = assignments.analyst;
    if (assignments.developer) document.getElementById('config-model-developer').value = assignments.developer;

    if (modelCfg.api_key) document.getElementById('config-key-openai').value = modelCfg.api_key;
    if (modelCfg.key_anthropic) document.getElementById('config-key-anthropic').value = modelCfg.key_anthropic;
    if (modelCfg.key_gemini) document.getElementById('config-key-gemini').value = modelCfg.key_gemini;
    if (modelCfg.key_xai) document.getElementById('config-key-xai').value = modelCfg.key_xai;
    if (modelCfg.key_minimax) document.getElementById('config-key-minimax').value = modelCfg.key_minimax;
    if (modelCfg.local_url) document.getElementById('config-local-url').value = modelCfg.local_url;

    if (modelCfg.image_provider) document.getElementById('config-provider-image').value = modelCfg.image_provider;
    if (modelCfg.vision_provider) document.getElementById('config-provider-vision').value = modelCfg.vision_provider;
    if (modelCfg.key_venice) document.getElementById('config-key-venice').value = modelCfg.key_venice;
    if (modelCfg.key_fal) document.getElementById('config-key-fal').value = modelCfg.key_fal;

    if (config.character) document.getElementById('config-character-name').value = config.character.name || 'Q';

    if (config.metabolism) {
      document.getElementById('config-hunger-rate').value = config.metabolism.hunger_rate || 0.5;
      document.getElementById('config-thirst-rate').value = config.metabolism.thirst_rate || 0.5;
      document.getElementById('config-energy-rate').value = config.metabolism.energy_rate || 0.5;
      document.getElementById('config-stress-rate').value = config.metabolism.stress_accumulation || 0.3;
    }

    if (config.connectivity) {
      document.getElementById('config-vmc-enabled').checked = config.connectivity.vmc_enabled === true;
      document.getElementById('config-osc-enabled').checked = config.connectivity.osc_enabled === true;
      document.getElementById('config-vmc-ip').value = config.connectivity.vmc_ip || '127.0.0.1';
      document.getElementById('config-vmc-port').value = config.connectivity.vmc_port || 8000;
    }
  } catch (e) { console.log('Config load error:', e); }
}

async function saveAllConfig() {
  const simConfig = {
    character: { name: document.getElementById('config-character-name').value },
    metabolism: {
      hunger_rate: parseFloat(document.getElementById('config-hunger-rate').value),
      thirst_rate: parseFloat(document.getElementById('config-thirst-rate').value),
      energy_rate: parseFloat(document.getElementById('config-energy-rate').value),
      stress_accumulation: parseFloat(document.getElementById('config-stress-rate').value)
    },
    connectivity: {
      vmc_enabled: document.getElementById('config-vmc-enabled').checked,
      osc_enabled: document.getElementById('config-osc-enabled').checked,
      vmc_ip: document.getElementById('config-vmc-ip').value,
      vmc_port: parseInt(document.getElementById('config-vmc-port').value)
    }
  };

  const modelConfig = {
    mac_assignments: {
      persona: document.getElementById('config-model-persona').value,
      limbic: document.getElementById('config-model-limbic').value,
      analyst: document.getElementById('config-model-analyst').value,
      developer: document.getElementById('config-model-developer').value
    },
    api_key: document.getElementById('config-key-openai').value,
    key_anthropic: document.getElementById('config-key-anthropic').value,
    key_gemini: document.getElementById('config-key-gemini').value,
    key_xai: document.getElementById('config-key-xai').value,
    key_minimax: document.getElementById('config-key-minimax').value,
    local_url: document.getElementById('config-local-url').value,
    image_provider: document.getElementById('config-provider-image').value,
    vision_provider: document.getElementById('config-provider-vision').value,
    key_venice: document.getElementById('config-key-venice').value,
    key_fal: document.getElementById('config-key-fal').value
  };

  try {
    const statusEl = document.getElementById('config-save-status');
    if (statusEl) statusEl.textContent = 'Saving...';

    const [simResp, modelResp] = await Promise.all([
      fetch('/api/config/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(simConfig) }),
      fetch('/api/model/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(modelConfig) })
    ]);

    if (statusEl) {
      statusEl.textContent = '✓ All Settings Saved!';
      statusEl.style.color = 'var(--growth)';
      setTimeout(() => { statusEl.textContent = ''; }, 3000);
    }
  } catch (e) { console.error(e); }
}

async function loadConfigs() {
  try {
    const res = await fetch('/api/config/simulation');
    const config = await res.json();
    if (config.hunger_rate) document.getElementById('tune-hunger-rate').value = config.hunger_rate;
    // ... other tuning sliders
  } catch (e) {}
}

window.loadClawModels = loadClawModels;
window.loadConfig = loadConfig;
window.saveAllConfig = saveAllConfig;
window.loadConfigs = loadConfigs;

// Profiles & Backups
async function loadProfiles() {
  try {
    const response = await fetch('/api/profiles/list');
    const profiles = await response.json();
    const container = document.getElementById('profile-list');
    if (container && profiles) {
      container.innerHTML = profiles.map(p => `
        <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
          <span><strong>${p}</strong></span>
          <button onclick="loadProfile('${p}')" style="background:var(--growth);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Load</button>
        </div>`).join('');
    }
  } catch (e) { console.log('Could not load profiles:', e); }
}

async function loadBackups() {
  try {
    const response = await fetch('/api/backups/list');
    const backups = await response.json();
    const container = document.getElementById('backup-list');
    if (container && backups) {
      container.innerHTML = backups.map(b => `
        <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
          <span><strong>${b}</strong></span>
          <button onclick="rollbackTo('${b}')" style="background:var(--accent);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Rollback</button>
        </div>`).join('');
    }
  } catch (e) { console.log('Could not load backups:', e); }
}

// Genesis Lab
async function runGenesis() {
  const promptText = document.getElementById('genesis-prompt').value.trim();
  if (!promptText || !confirm('DANGER: This will overwrite your entire simulation. Proceed?')) return;
  try {
    const response = await fetch('/api/genesis/request', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: promptText }) });
    const result = await response.json();
    if (result.success) showToast('Bootstrap started! Reloading shortly...', 'success');
  } catch (e) { showToast(e.message, 'error'); }
}

async function loadGenesisStatus() {
  try {
    const response = await fetch('/api/genesis/status');
    const result = await response.json();
    const cb = document.getElementById('genesis-enabled');
    if (cb) cb.checked = result.enabled || false;
    loadProfiles();
    loadBackups();
  } catch (e) { console.log('Could not load genesis status:', e); }
}

window.loadProfiles = loadProfiles;
window.loadBackups = loadBackups;
window.runGenesis = runGenesis;
window.loadGenesisStatus = loadGenesisStatus;

