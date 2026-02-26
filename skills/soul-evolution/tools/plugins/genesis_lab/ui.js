/**
 * Genesis-Lab Plugin UI Module (v1.0.0)
 */

async function initGenesisLab() {
  const root = document.getElementById('plugin-root-genesis_lab');
  if (!root) return;

  root.innerHTML = `
    <div class="panel-card">
      <h3>Genesis Life Bootstrap</h3>
      <p>Enter a description for the life simulation you want to generate.</p>
      <textarea id="genesis-prompt-plugin" style="width:100%; height:100px; background:var(--bg-dim); color:var(--text); border:1px solid var(--border); border-radius:4px; padding:0.5rem;"></textarea>
      <button class="btn-primary" style="margin-top:1rem; width:100%;" onclick="window.GenesisLabPlugin.runGenesis()">🚀 Run Life Generation</button>
    </div>
  `;
}

window.GenesisLabPlugin = {
  init: initGenesisLab,
  runGenesis: async () => {
    const prompt = document.getElementById('genesis-prompt-plugin').value;
    if (!prompt) return;
    if (!confirm("This will overwrite existing state. Continue?")) return;
    
    const resp = await fetch('/api/plugins/genesis_lab/request', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    });
    const res = await resp.json();
    if (res.success) showToast("Genesis request sent!");
  }
};

if (document.getElementById('tab-genesis_lab')) initGenesisLab();
