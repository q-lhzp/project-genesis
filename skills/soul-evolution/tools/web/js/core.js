/**
 * Project Genesis Dashboard - Core Logic (v5.7.0)
 */

// Global state
window._interiorRendered = false;
window._inventoryRendered = false;
window._wardrobeRendered = false;
window._devRendered = false;
window._cycleRendered = false;
window._worldRendered = false;
window._skillsRendered = false;
window._psychRendered = false;
window._repRendered = false;
window._streamRendered = false;
window._genesisRendered = false;
window._vaultRendered = false;

// Basic Utilities
function esc(s) {
  if (s === null || s === undefined) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function updateClock() {
  const el = document.getElementById('clock');
  if (el) {
    el.textContent = new Date().toLocaleTimeString();
  }
}

// Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML = message;
  toast.onclick = () => toast.remove();
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideIn 0.3s ease-in reverse forwards';
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// Tab Navigation
function switchTab(tabId) {
  console.log('Switching to tab:', tabId);
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  
  const el = document.getElementById('tab-' + tabId);
  if (el) el.classList.add('active');
  
  document.querySelectorAll('.tab-btn').forEach(b => {
    if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(`'${tabId}'`)) {
      b.classList.add('active');
    }
  });

  // Feature-specific initializations
  if (tabId === 'interior' && !window._interiorRendered && typeof renderInterior === 'function') { renderInterior(); window._interiorRendered = true; }
  if (tabId === 'inventory' && !window._inventoryRendered && typeof renderInventoryPanel === 'function') { renderInventoryPanel(); window._inventoryRendered = true; }
  if (tabId === 'wardrobe' && !window._wardrobeRendered && typeof renderWardrobePanel === 'function') { renderWardrobePanel(); window._wardrobeRendered = true; }
  if (tabId === 'development' && !window._devRendered && typeof renderDevPanel === 'function') { renderDevPanel(); window._devRendered = true; }
  if (tabId === 'development' && typeof loadExpansionState === 'function') { loadExpansionState(); loadProjectsList(); }
  if (tabId === 'cycle' && !window._cycleRendered && typeof renderCyclePanel === 'function') { renderCyclePanel(); window._cycleRendered = true; }
  if (tabId === 'world' && !window._worldRendered && typeof renderWorldPanel === 'function') { renderWorldPanel(); window._worldRendered = true; }
  if (tabId === 'skills' && !window._skillsRendered && typeof renderSkillsPanel === 'function') { renderSkillsPanel(); window._skillsRendered = true; }
  if (tabId === 'psychology' && !window._psychRendered && typeof renderPsychPanel === 'function') { renderPsychPanel(); window._psychRendered = true; }
  if (tabId === 'reputation' && !window._repRendered && typeof renderReputationPanel === 'function') { 
    renderReputationPanel(); 
    if (typeof loadContactCRM === 'function') loadContactCRM();
    if (typeof loadPendingSocialEvents === 'function') loadPendingSocialEvents();
    window._repRendered = true; 
  }
  if (tabId === 'reputation' && typeof loadPendingSocialEvents === 'function') { loadPendingSocialEvents(); }
  if (tabId === 'stream' && !window._streamRendered && typeof renderPhotoStream === 'function') { renderPhotoStream(); window._streamRendered = true; }
  if (tabId === 'genesis' && !window._genesisRendered) { 
    window._genesisRendered = true; 
    if (typeof loadGenesisStatus === 'function') loadGenesisStatus(); 
    if (typeof loadConfigs === 'function') loadConfigs(); 
    if (typeof loadClawModels === 'function') loadClawModels(); 
  }
  if (tabId === 'genesis' && typeof refreshSpatialState === 'function') { refreshSpatialState(); }
  if (tabId === 'config') { 
    if (typeof loadConfig === 'function') loadConfig(); 
    if (typeof loadClawModels === 'function') loadClawModels(); 
  }
  if (tabId === 'vault' && !window._vaultRendered && typeof loadVaultData === 'function') { 
    window._vaultRendered = true; 
    loadVaultData(); 
    if (typeof startEconomyPolling === 'function') startEconomyPolling();
  }
  if (tabId === 'diagnostics' && typeof loadDiagnostics === 'function') { loadDiagnostics(); }
  if (tabId === 'godmode' && typeof initGodMode === 'function') { initGodMode(); }
  
  if (tabId === 'stream' && typeof startPresencePolling === 'function') startPresencePolling();
  if (tabId === 'analytics' && typeof loadAnalyticsData === 'function') loadAnalyticsData();
}

// Modal system
let _modalResolve = null;

function openModal(title, fields) {
  return new Promise(resolve => {
    _modalResolve = resolve;
    document.getElementById('modal-title').textContent = title;
    const container = document.getElementById('modal-fields');
    container.innerHTML = fields.map(f => {
      if (f.type === 'select') {
        const opts = f.options.map(o => `<option value="${o}">${o}</option>`).join('');
        return `<div class="modal-field"><label>${f.label}</label><select id="mf-${f.key}">${opts}</select></div>`;
      }
      return `<div class="modal-field"><label>${f.label}</label><input id="mf-${f.key}" type="${f.type||'text'}" value="${f.default||''}" placeholder="${f.placeholder||''}"></div>`;
    }).join('');
    
    document.getElementById('modal-ok').onclick = () => {
      const result = {};
      fields.forEach(f => { result[f.key] = document.getElementById('mf-' + f.key).value; });
      closeModal();
      resolve(result);
    };
    
    document.getElementById('modal-overlay').classList.add('open');
    const first = container.querySelector('input, select');
    if (first) setTimeout(() => first.focus(), 100);
  });
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  if (_modalResolve) { _modalResolve(null); _modalResolve = null; }
}

// Lightbox
let _lightboxCtx = { category: '', itemId: '', images: [], currentIdx: 0 };

function openLightbox(category, itemId, images, startIdx) {
  _lightboxCtx = { category, itemId, images: images || [], currentIdx: startIdx || 0 };
  document.getElementById('lightbox').classList.add('open');
  renderLightbox();
}

function closeLightbox() {
  document.getElementById('lightbox').classList.remove('open');
}

function renderLightbox() {
  const main = document.getElementById('lightbox-main');
  const gallery = document.getElementById('lightbox-gallery');
  if (!main || !gallery) return;

  if (_lightboxCtx.images.length === 0) {
    main.src = '';
    main.alt = 'No images';
    gallery.innerHTML = '<span style="color:var(--text-dim);font-size:0.8rem;">No images yet — drop an image or click Upload</span>';
    return;
  }
  const current = _lightboxCtx.images[_lightboxCtx.currentIdx] || _lightboxCtx.images[0];
  main.src = '/' + current;
  gallery.innerHTML = _lightboxCtx.images.map((img, i) =>
    `<img src="/${img}" class="${i === _lightboxCtx.currentIdx ? 'active' : ''}" onclick="_lightboxCtx.currentIdx=${i};renderLightbox();">`
  ).join('');
}

// Event Listeners
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (document.getElementById('lightbox')?.classList.contains('open')) closeLightbox();
    else if (document.getElementById('modal-overlay')?.classList.contains('open')) closeModal();
  }
});

// Clock Interval
setInterval(updateClock, 1000);

// Export to window
window.esc = esc;
window.showToast = showToast;
window.switchTab = switchTab;
window.openModal = openModal;
window.closeModal = closeModal;
window.openLightbox = openLightbox;
window.closeLightbox = closeLightbox;
window.renderLightbox = renderLightbox;

// Initial Dashboard Render
function initDashboard() {
  if (typeof renderAgentName === 'function') renderAgentName();
  if (typeof renderStats === 'function') renderStats();
  if (typeof renderLegend === 'function') renderLegend();
  if (typeof renderSoulTree === 'function') renderSoulTree(DATA.changes.length);
  if (typeof renderTimeline === 'function') renderTimeline();
  if (typeof renderFeed === 'function') renderFeed();
  if (typeof renderVitals === 'function') renderVitals();
  if (typeof renderMentalActivity === 'function') renderMentalActivity();
  if (typeof renderProposals === 'function') renderProposals();
  if (typeof renderReflections === 'function') renderReflections();
  if (typeof renderSignificant === 'function') renderSignificant();
  if (typeof renderPipelineState === 'function') renderPipelineState();

  // Auto-refresh Dashboard every 30s
  setInterval(() => {
    const dashboardTab = document.getElementById('tab-dashboard');
    if (dashboardTab && dashboardTab.classList.contains('active')) {
      location.reload();
    }
  }, 30000);
}
window.initDashboard = initDashboard;

function doUpload(file) {
  if (!file || !file.type.startsWith('image/')) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const b64 = e.target.result.split(',')[1];
    fetch('/upload-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: _lightboxCtx.category,
        item_id: _lightboxCtx.itemId,
        filename: file.name,
        data: b64,
      })
    }).then(r => r.json()).then(res => {
      _lightboxCtx.images.push(res.path);
      _lightboxCtx.currentIdx = _lightboxCtx.images.length - 1;
      renderLightbox();
      if (typeof refreshPanel === 'function') refreshPanel(_lightboxCtx.category);
      showToast('Image uploaded', 'success');
    }).catch(err => showToast('Upload failed: ' + err, 'error'));
  };
  reader.readAsDataURL(file);
}

function uploadLightboxImage(event) {
  doUpload(event.target.files[0]);
  event.target.value = '';
}

function deleteLightboxImage() {
  if (_lightboxCtx.images.length === 0) return;
  const path = _lightboxCtx.images[_lightboxCtx.currentIdx];
  if (!confirm('Delete this image?')) return;
  fetch('/delete-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category: _lightboxCtx.category, item_id: _lightboxCtx.itemId, path: path })
  }).then(() => {
    _lightboxCtx.images.splice(_lightboxCtx.currentIdx, 1);
    if (_lightboxCtx.currentIdx >= _lightboxCtx.images.length) _lightboxCtx.currentIdx = Math.max(0, _lightboxCtx.images.length - 1);
    renderLightbox();
    if (typeof refreshPanel === 'function') refreshPanel(_lightboxCtx.category);
    showToast('Image deleted', 'success');
  }).catch(err => showToast('Delete failed: ' + err, 'error'));
}

function refreshPanel(category) {
  window['_' + category + 'Rendered'] = false;
  switch(category) {
    case 'interior': if (typeof renderInterior === 'function') renderInterior(); break;
    case 'inventory': if (typeof renderInventoryPanel === 'function') renderInventoryPanel(); break;
    case 'wardrobe': if (typeof renderWardrobePanel === 'function') renderWardrobePanel(); break;
  }
}

function deleteAllImages(category, itemId, images) {
  if (!images || images.length === 0) return Promise.resolve();
  return Promise.all(images.map(path =>
    fetch('/delete-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, item_id: itemId, path })
    }).catch(() => {})
  ));
}

window.doUpload = doUpload;
window.uploadLightboxImage = uploadLightboxImage;
window.deleteLightboxImage = deleteLightboxImage;
window.refreshPanel = refreshPanel;
window.deleteAllImages = deleteAllImages;

// Diagnostics & Logging
async function loadDiagnostics() {
  loadLogStream();
  loadSystemHealth();
  loadModelDiagnostics();
}

function loadModelDiagnostics() {
  if (typeof DATA === 'undefined' || !DATA.system_config) return;
  const cfg = DATA.system_config;
  const setStatus = (id, isConfigured) => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = isConfigured ? 'OK' : 'Missing';
      el.style.color = isConfigured ? 'var(--growth)' : 'var(--core)';
    }
  };
  setStatus('model-status-openai', cfg.openai_ok);
  setStatus('model-status-anthropic', cfg.anthropic_ok);
  setStatus('model-status-xai', cfg.xai_ok);
  setStatus('model-status-gemini', cfg.gemini_ok);
}

async function loadSystemHealth() {
  try {
    const logHealth = document.getElementById('health-logging');
    if (logHealth) logHealth.textContent = 'Active';
    const economyResponse = await fetch('/api/economy/state');
    const economy = await economyResponse.json();
    const econHealth = document.getElementById('health-economy');
    if (econHealth) econHealth.textContent = economy.isActive ? 'Active' : 'Idle';
  } catch (e) { console.log('Health check error:', e); }
}

async function loadLogStream() {
  const level = document.getElementById('log-filter-level')?.value || '';
  const count = 100;
  try {
    let url = '/api/logs/recent?count=' + count;
    if (level) url += '&level=' + level;
    const response = await fetch(url);
    const logs = await response.json();
    const logStream = document.getElementById('log-stream');
    if (logStream) {
      logStream.innerHTML = logs.length ? logs.map(entry => {
        const time = new Date(entry.timestamp).toLocaleTimeString();
        return `<div style="padding:0.25rem 0;border-bottom:1px solid var(--border-dim);">
          <span style="color:var(--text-dim);font-size:0.7rem;">${time}</span> 
          <span style="color:var(--accent);font-size:0.75rem;">[${entry.module}]</span> 
          <span style="color:var(--text);">${entry.message}</span>
        </div>`;
      }).join('') : '<div style="color:var(--text-dim);font-style:italic;">No log entries yet.</div>';
    }
  } catch (e) { console.log('Log load error:', e); }
}

window.loadDiagnostics = loadDiagnostics;
window.loadLogStream = loadLogStream;


