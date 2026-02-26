/**
 * Identity-Journal Plugin UI Module (v1.0.0)
 */

async function initIdentityJournal() {
  const root = document.getElementById('plugin-root-identity_journal');
  if (!root) return;

  root.innerHTML = `
    <div class="plugin-tabs">
      <button class="p-tab active" onclick="window.IdentityJournalPlugin.switchTab('skills')">📜 Skills</button>
      <button class="p-tab" onclick="window.IdentityJournalPlugin.switchTab('interests')">🎨 Interests</button>
      <button class="p-tab" onclick="window.IdentityJournalPlugin.switchTab('dreams')">💭 Dreams</button>
    </div>
    <div id="identity-journal-content" class="plugin-content">
      Loading...
    </div>
  `;

  window.IdentityJournalPlugin.switchTab('skills');
}

window.IdentityJournalPlugin = {
  init: initIdentityJournal,
  switchTab: (tab) => {
    document.querySelectorAll('#plugin-root-identity_journal .p-tab').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('identity-journal-content');
    
    if (tab === 'skills') renderSkills(container);
    if (tab === 'interests') renderInterests(container);
    if (tab === 'dreams') renderDreams(container);
  }
};

async function renderSkills(container) {
  const resp = await fetch('/api/plugins/identity_journal/skills');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>Entity Skills</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    </div>
  `;
}

async function renderInterests(container) {
  const resp = await fetch('/api/plugins/identity_journal/interests');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>Interests & Hobbies</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    </div>
  `;
}

async function renderDreams(container) {
  const resp = await fetch('/api/plugins/identity_journal/dreams');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>Recent Dreams</h3>
      <div id="dreams-list">
        ${(data.dreams || []).map(d => `<div class="list-item"><strong>${d.type}:</strong> ${d.content}</div>`).join('') || 'No dreams recorded.'}
      </div>
    </div>
  `;
}

if (document.getElementById('tab-identity_journal')) initIdentityJournal();
