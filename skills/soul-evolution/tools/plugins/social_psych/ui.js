/**
 * Social & Psych Plugin UI Module (v1.0.0)
 */

async function initSocialPsych() {
  const root = document.getElementById('plugin-root-social_psych');
  if (!root) return;

  root.innerHTML = `
    <div class="plugin-tabs">
      <button class="p-tab active" onclick="window.SocialPsychPlugin.switchTab('psych')">🧠 Psychology</button>
      <button class="p-tab" onclick="window.SocialPsychPlugin.switchTab('rep')">🤝 Reputation</button>
      <button class="p-tab" onclick="window.SocialPsychPlugin.switchTab('crm')">👤 NPC CRM</button>
    </div>
    <div id="social-psych-content" class="plugin-content">
      Loading...
    </div>
  `;

  window.SocialPsychPlugin.switchTab('psych');
}

window.SocialPsychPlugin = {
  init: initSocialPsych,
  switchTab: async (tab) => {
    document.querySelectorAll('#plugin-root-social_psych .p-tab').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('social-psych-content');
    
    if (tab === 'psych') renderPsych(container);
    if (tab === 'rep') renderRep(container);
    if (tab === 'crm') renderCRM(container);
  },
  addContact: async () => {
    const name = prompt("NPC Name:");
    if (!name) return;
    const resp = await fetch('/api/plugins/social_psych/add-entity', {
      method: 'POST',
      body: JSON.stringify({ name, circle: 'Acquaintances', relationship_type: 'friend' })
    });
    const res = await resp.json();
    if (res.success) { showToast("Contact added!"); window.SocialPsychPlugin.switchTab('crm'); }
  }
};

async function renderPsych(container) {
  const resp = await fetch('/api/plugins/social_psych/psychology');
  const data = await resp.json();
  const res = data.resilience || 0;
  container.innerHTML = `
    <div class="panel-card">
      <h3>Mental Resilience</h3>
      <div class="progress-bar-container">
        <div class="progress-bar" style="width: ${res}%"></div>
      </div>
      <p style="text-align:center;">${res}/100</p>
    </div>
    <div class="panel-card" style="margin-top:1rem;">
      <h3>Active Traumas</h3>
      <div id="trauma-list">${(data.traumas || []).map(t => `<div class="list-item">${t.description} (${t.severity})</div>`).join('') || 'None'}</div>
    </div>
  `;
}

async function renderRep(container) {
  const resp = await fetch('/api/plugins/social_psych/reputation');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>Global Standing: ${data.global_score || 0}</h3>
      <div id="circles-list">
        ${(data.circles || []).map(c => `
          <div style="display:flex; justify-content:space-between; padding:0.5rem; border-bottom:1px solid var(--border);">
            <span>${c.name}</span>
            <span style="color:${c.score >= 0 ? 'var(--growth)' : 'var(--danger)'}">${c.score}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

async function renderCRM(container) {
  const resp = await fetch('/api/plugins/social_psych/entities');
  const data = await resp.json();
  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
      <h3>Contact Management</h3>
      <button class="btn-crud" onclick="window.SocialPsychPlugin.addContact()">+ Add Contact</button>
    </div>
    <div class="npc-grid">
      ${(data.entities || []).map(e => `
        <div class="panel-card npc-card">
          <div style="font-size:1.5rem;">👤</div>
          <strong>${e.name}</strong>
          <div style="font-size:0.75rem; color:var(--text-dim);">${e.relationship_type} · ${e.circle}</div>
          <div style="margin-top:0.5rem; font-size:0.8rem;">Bond: ${e.bond}</div>
        </div>
      `).join('')}
    </div>
  `;
}

if (document.getElementById('tab-social_psych')) initSocialPsych();
