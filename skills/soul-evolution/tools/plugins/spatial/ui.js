/**
 * Spatial Plugin UI Module (v1.0.0)
 * Combines Interior, Inventory, and Wardrobe.
 */

async function initSpatial() {
  const root = document.getElementById('plugin-root-spatial');
  if (!root) return;

  console.log('[PLUGIN:spatial] Initializing UI');

  root.innerHTML = `
    <div class="spatial-tabs">
      <button class="s-tab active" onclick="window.SpatialPlugin.switchSubTab('interior')">🏠 Interior</button>
      <button class="s-tab" onclick="window.SpatialPlugin.switchSubTab('inventory')">🎒 Inventory</button>
      <button class="s-tab" onclick="window.SpatialPlugin.switchSubTab('wardrobe')">👔 Wardrobe</button>
    </div>
    <div id="spatial-content" class="spatial-content">
      <div id="spatial-view">Loading Spatial Data...</div>
    </div>
  `;

  window.SpatialPlugin.switchSubTab('interior');
}

window.SpatialPlugin = {
  init: initSpatial,
  switchSubTab: async (sub) => {
    // UI Update
    document.querySelectorAll('.s-tab').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    
    const container = document.getElementById('spatial-view');
    container.innerHTML = `<div class="loader">Loading ${sub}...</div>`;

    try {
      const resp = await fetch('/api/plugins/spatial/' + sub);
      const data = await resp.json();
      
      if (sub === 'interior') renderInterior(data, container);
      if (sub === 'inventory') renderInventory(data, container);
      if (sub === 'wardrobe') renderWardrobe(data, container);
      
    } catch(e) {
      container.innerHTML = `<div class="error">Error loading ${sub}: ${e.message}</div>`;
    }
  }
};

function renderInterior(data, container) {
  container.innerHTML = `<h3>Physical Environment</h3><div class="panel-card"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
}

function renderInventory(data, container) {
  container.innerHTML = `<h3>Entity Inventory</h3><div class="panel-card"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
}

function renderWardrobe(data, container) {
  container.innerHTML = `<h3>Wardrobe</h3><div class="panel-card"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
}

if (document.getElementById('tab-spatial')) initSpatial();
