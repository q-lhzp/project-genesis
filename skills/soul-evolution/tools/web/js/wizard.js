/**
 * Project Genesis Dashboard - Onboarding Wizard Logic (v5.7.0)
 */

(async function() {
  let currentStep = 1;
  const totalSteps = 5;

  async function checkWizard() {
    try {
      const resp = await fetch('/api/wizard/status');
      const data = await resp.json();
      if (!data.setup_complete) {
        document.getElementById('wizardOverlay').classList.add('active');
        await loadStep(1);
      }
    } catch(e) { console.error('Wizard check failed:', e); }
  }

  async function loadStep(step) {
    currentStep = step;
    updateUI();
    if (step === 1) await loadInfrastructure();
    if (step === 2) if (typeof initMacStep === 'function') await initMacStep();
    if (step === 4) await loadAvatar();
  }

  function updateUI() {
    document.querySelectorAll('.wizard-step').forEach((el, i) => {
      el.classList.toggle('active', i + 1 === currentStep);
      el.classList.toggle('done', i + 1 < currentStep);
    });
    document.querySelectorAll('.wizard-step-view').forEach((el, i) => {
      el.classList.toggle('active', i + 1 === currentStep);
    });
    document.getElementById('wizardPrev').style.visibility = currentStep === 1 ? 'hidden' : 'visible';
    document.getElementById('wizardNext').textContent = currentStep === totalSteps ? 'Complete ✓' : 'Next →';
  }

  async function loadInfrastructure() {
    const statusEl = document.getElementById('step1Status');
    const listEl = document.getElementById('bridgeList');
    if (!statusEl || !listEl) return;
    statusEl.style.display = 'block';
    statusEl.className = 'wizard-status loading';
    statusEl.textContent = 'Checking system bridges...';
    try {
      const resp = await fetch('/api/wizard/check/health');
      const data = await resp.json();
      listEl.innerHTML = data.bridges.map(b =>
        `<div class="wizard-bridge-item">
          <span>${b.name}</span>
          <span class="${b.exists && b.executable ? 'ok' : 'fail'}">${b.exists && b.executable ? '✓ OK' : '✗ MISSING'}</span>
        </div>`
      ).join('');
      statusEl.className = 'wizard-status ' + (data.success ? 'success' : 'error');
      statusEl.textContent = data.success ? 'System verified!' : 'Some bridges missing';
    } catch(e) {
      statusEl.className = 'wizard-status error';
      statusEl.textContent = 'Check failed: ' + e.message;
    }
  }

  async function initMacStep() {
    try {
      const modelsResp = await fetch('/api/openclaw/models');
      const modelsData = await modelsResp.json();
      const configResp = await fetch('/api/model/config');
      const configData = await configResp.json();
      const assignments = configData.mac_assignments || {};
      const selects = document.querySelectorAll('.mac-select');
      selects.forEach(select => {
        const role = select.id.replace('mac-model-', '');
        select.innerHTML = '<option value="">-- Select Model --</option>';
        modelsData.models.forEach(m => {
          const opt = document.createElement('option');
          opt.value = m.id;
          opt.textContent = m.name;
          if (assignments[role] === m.id) opt.selected = true;
          select.appendChild(opt);
        });
      });
    } catch(e) { console.error(e); }
  }

  async function saveKeys() {
    const assignments = {
      persona: document.getElementById('mac-model-persona').value,
      analyst: document.getElementById('mac-model-analyst').value,
      developer: document.getElementById('mac-model-developer').value,
      limbic: document.getElementById('mac-model-limbic').value
    };
    const resp = await fetch('/api/model/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ mac_assignments: assignments }) });
    return resp.ok;
  }

  async function saveVaultKeys() {
    const alpacaKey = document.getElementById('alpacaKey').value;
    const alpacaSecret = document.getElementById('alpacaSecret').value;
    const paperMode = document.getElementById('alpacaPaper').checked;
    await fetch('/api/model/config', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ vault_api_key: alpacaKey, vault_api_secret: alpacaSecret, vault_provider: 'alpaca' }) });
    await fetch('/api/godmode/vault/simulate-trade', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ action: 'switch_mode', mode: paperMode ? 'paper' : 'live' }) });
    return true;
  }

  async function loadAvatar() {
    const path = document.getElementById('vrmPath').value || 'avatars/q_avatar.vrm';
    try {
      const resp = await fetch('/api/wizard/check/avatar?path=' + encodeURIComponent(path));
      const data = await resp.json();
      if (data.verified) {
        const statusEl = document.getElementById('step4Status');
        statusEl.style.display = 'block';
        statusEl.className = 'wizard-status success';
        statusEl.textContent = 'Standard model found. Ready to proceed.';
      }
    } catch(e) {}
  }

  // Bind Listeners
  document.getElementById('wizardNext')?.addEventListener('click', async () => {
    if (currentStep === 2) await saveKeys();
    if (currentStep === 3) await saveVaultKeys();
    if (currentStep < totalSteps) await loadStep(currentStep + 1);
    else {
      await fetch('/api/wizard/complete', {method: 'POST'});
      document.getElementById('wizardOverlay').classList.remove('active');
    }
  });

  document.getElementById('wizardPrev')?.addEventListener('click', () => { if (currentStep > 1) loadStep(currentStep - 1); });

  // Init
  checkWizard();
})();
