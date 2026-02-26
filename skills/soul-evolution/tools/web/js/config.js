/**
 * Project Genesis Dashboard - Configuration & Tuning (v5.7.1)
 * Audit-Fixed: Null-safe DOM access & Event listeners
 */

// Helper for safe DOM updates
const setVal = (id, val) => {
  const el = document.getElementById(id);
  if (el) {
    if (el.type === 'checkbox') el.checked = !!val;
    else el.value = val || '';
  }
};

const getVal = (id) => {
  const el = document.getElementById(id);
  if (!el) return null;
  return el.type === 'checkbox' ? el.checked : el.value;
};

const setText = (id, txt) => {
  const el = document.getElementById(id);
  if (el) el.textContent = txt;
};

async function loadClawModels() {
  try {
    const resp = await fetch('/api/openclaw/models');
    const data = await resp.json();
    const selects = document.querySelectorAll('.mac-select-main, .mac-select');
    
    selects.forEach(select => {
      const currentVal = select.value;
      select.innerHTML = '<option value="">-- Select Model --</option>';
      (data.models || []).forEach(m => {
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

    // Apply Assignments
    setVal('config-model-persona', assignments.persona);
    setVal('config-model-limbic', assignments.limbic);
    setVal('config-model-analyst', assignments.analyst);
    setVal('config-model-developer', assignments.developer);

    // Apply Keys
    setVal('config-key-openai', modelCfg.api_key);
    setVal('config-key-anthropic', modelCfg.key_anthropic);
    setVal('config-key-gemini', modelCfg.key_gemini);
    setVal('config-key-xai', modelCfg.key_xai);
    setVal('config-key-minimax', modelCfg.key_minimax);
    setVal('config-local-url', modelCfg.local_url);

    // Providers
    setVal('config-provider-image', modelCfg.image_provider);
    setVal('config-provider-vision', modelCfg.vision_provider);
    setVal('config-key-venice', modelCfg.key_venice);
    setVal('config-key-fal', modelCfg.key_fal);

    if (config.character) setVal('config-character-name', config.character.name);

    if (config.metabolism) {
      setVal('config-hunger-rate', config.metabolism.hunger_rate);
      setVal('config-thirst-rate', config.metabolism.thirst_rate);
      setVal('config-energy-rate', config.metabolism.energy_rate);
      setVal('config-stress-rate', config.metabolism.stress_accumulation);
      
      // Update display labels
      ['hunger-rate', 'thirst-rate', 'energy-rate', 'stress-rate'].forEach(k => {
        setText('config-' + k + '-val', config.metabolism[k.replace('-', '_')] || 0.5);
      });
    }

    if (config.connectivity) {
      setVal('config-vmc-enabled', config.connectivity.vmc_enabled);
      setVal('config-osc-enabled', config.connectivity.osc_enabled);
      setVal('config-vmc-ip', config.connectivity.vmc_ip);
      setVal('config-vmc-port', config.connectivity.vmc_port);
    }
  } catch (e) { console.log('Config load error:', e); }
}

async function saveAllConfig() {
  const simConfig = {
    character: { name: getVal('config-character-name') },
    metabolism: {
      hunger_rate: parseFloat(getVal('config-hunger-rate')),
      thirst_rate: parseFloat(getVal('config-thirst-rate')),
      energy_rate: parseFloat(getVal('config-energy-rate')),
      stress_accumulation: parseFloat(getVal('config-stress-rate'))
    },
    connectivity: {
      vmc_enabled: getVal('config-vmc-enabled'),
      osc_enabled: getVal('config-osc-enabled'),
      vmc_ip: getVal('config-vmc-ip'),
      vmc_port: parseInt(getVal('config-vmc-port'))
    }
  };

  const modelConfig = {
    mac_assignments: {
      persona: getVal('config-model-persona'),
      limbic: getVal('config-model-limbic'),
      analyst: getVal('config-model-analyst'),
      developer: getVal('config-model-developer')
    },
    api_key: getVal('config-key-openai'),
    key_anthropic: getVal('config-key-anthropic'),
    key_gemini: getVal('config-key-gemini'),
    key_xai: getVal('config-key-xai'),
    key_minimax: getVal('config-key-minimax'),
    local_url: getVal('config-local-url'),
    image_provider: getVal('config-provider-image'),
    vision_provider: getVal('config-provider-vision'),
    key_venice: getVal('config-key-venice'),
    key_fal: getVal('config-key-fal')
  };

  try {
    const statusEl = document.getElementById('config-save-status');
    if (statusEl) {
      statusEl.textContent = 'Saving...';
      statusEl.style.color = 'var(--accent)';
    }

    const [simResp, modelResp] = await Promise.all([
      fetch('/api/config/save', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(simConfig) }),
      fetch('/api/model/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(modelConfig) })
    ]);

    if (statusEl) {
      statusEl.textContent = '✓ All Settings Saved!';
      statusEl.style.color = 'var(--growth)';
      setTimeout(() => { statusEl.textContent = ''; }, 3000);
    }
  } catch (e) { 
    console.error(e);
    setText('config-save-status', '✗ Save failed');
  }
}

// Add listeners for sliders
document.addEventListener('input', (e) => {
  if (e.target.id && e.target.id.startsWith('config-') && e.target.type === 'range') {
    const valEl = document.getElementById(e.target.id + '-val');
    if (valEl) valEl.textContent = e.target.value;
  }
});

async function loadConfigs() {
  // Backwards compatibility for other tabs calling this
  await loadConfig();
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
      container.innerHTML = profiles.length ? profiles.map(p => `
        <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
          <span><strong>${p}</strong></span>
          <button onclick="loadProfile('${p}')" style="background:var(--growth);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Load</button>
        </div>`).join('') : '<p style="color:var(--text-dim);font-size:0.8rem;">No profiles found.</p>';
    }
  } catch (e) { console.log('Could not load profiles:', e); }
}

async function loadBackups() {
  try {
    const response = await fetch('/api/backups/list');
    const backups = await response.json();
    const container = document.getElementById('backup-list');
    if (container && backups) {
      container.innerHTML = backups.length ? backups.map(b => `
        <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
          <span><strong>${b}</strong></span>
          <button onclick="rollbackTo('${b}')" style="background:var(--accent);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Rollback</button>
        </div>`).join('') : '<p style="color:var(--text-dim);font-size:0.8rem;">No backups found.</p>';
    }
  } catch (e) { console.log('Could not load backups:', e); }
}

// Genesis Lab
async function runGenesis() {
  const promptText = getVal('genesis-prompt');
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
