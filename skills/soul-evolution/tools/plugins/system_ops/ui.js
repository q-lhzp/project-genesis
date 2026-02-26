/**
 * System-Ops Plugin UI Module (v1.0.0)
 */

async function initSystemOps() {
  const root = document.getElementById('plugin-root-system_ops');
  if (!root) return;

  root.innerHTML = `
    <div class="plugin-tabs">
      <button class="p-tab active" onclick="window.SystemOpsPlugin.switchTab('logs')">📋 Logs</button>
      <button class="p-tab" onclick="window.SystemOpsPlugin.switchTab('cycle')">🌙 Cycle</button>
      <button class="p-tab" onclick="window.SystemOpsPlugin.switchTab('health')">🛠️ Health</button>
    </div>
    <div id="system-ops-content" class="plugin-content">
      Loading...
    </div>
  `;

  window.SystemOpsPlugin.switchTab('logs');
}

window.SystemOpsPlugin = {
  init: initSystemOps,
  switchTab: (tab) => {
    document.querySelectorAll('#plugin-root-system_ops .p-tab').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    const container = document.getElementById('system-ops-content');
    
    if (tab === 'logs') renderLogs(container);
    if (tab === 'cycle') renderCycle(container);
    if (tab === 'health') renderHealth(container);
  }
};

async function renderLogs(container) {
  const resp = await fetch('/api/plugins/system_ops/logs');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card" style="height:500px; overflow-y:auto; font-family:monospace; font-size:0.8rem;">
      ${(data.logs || []).map(l => `<div>[${l.level}] ${l.module}: ${l.message}</div>`).join('') || 'No logs found.'}
    </div>
  `;
}

async function renderCycle(container) {
  const resp = await fetch('/api/plugins/system_ops/cycle');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>Current Cycle</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    </div>
  `;
}

async function renderHealth(container) {
  const resp = await fetch('/api/plugins/system_ops/health');
  const data = await resp.json();
  container.innerHTML = `
    <div class="panel-card">
      <h3>System Integrity</h3>
      <div>Status: <span style="color:var(--growth);">${data.status}</span></div>
      <div style="margin-top:1rem;">Uptime: ${data.uptime}</div>
    </div>
  `;
}

if (document.getElementById('tab-system_ops')) initSystemOps();
