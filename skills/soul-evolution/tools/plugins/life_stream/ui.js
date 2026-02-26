/**
 * Life-Stream Plugin UI Module (v1.0.0)
 */

async function initLifeStream() {
  const root = document.getElementById('plugin-root-life_stream');
  if (!root) return;

  root.innerHTML = `
    <div class="stream-layout">
      <div class="stream-left">
        <div class="panel-card" id="presence-card">
          <h3>Präsenz & Mood</h3>
          <div id="presence-info">Loading...</div>
        </div>
        <div class="panel-card" style="margin-top:1rem;">
          <h3>Social Feed</h3>
          <div id="social-feed-plugin" class="feed-list">Loading...</div>
        </div>
      </div>
      <div class="stream-right">
        <div class="panel-card">
          <h3>Memory Photos</h3>
          <div id="photo-grid-plugin" class="photo-grid">Loading...</div>
        </div>
      </div>
    </div>
  `;

  loadPresence();
  loadPhotos();
  setInterval(loadPresence, 10000);
}

async function loadPresence() {
  const resp = await fetch('/api/plugins/life_stream/state');
  const state = await resp.json();
  const info = document.getElementById('presence-info');
  const feed = document.getElementById('social-feed-plugin');
  
  if (info) {
    info.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="color:${state.isActive ? 'var(--growth)' : 'var(--text-dim)'}">● ${state.isActive ? 'Active' : 'Idle'}</span>
        <span class="tag">${state.currentMood || 'neutral'}</span>
      </div>
    `;
  }

  if (feed && state.feed) {
    feed.innerHTML = state.feed.slice(0, 10).map(post => `
      <div class="feed-item">
        <small>${new Date(post.timestamp).toLocaleTimeString()}</small>
        <p>${post.content}</p>
      </div>
    `).join('') || 'No feed activity.';
  }
}

async function loadPhotos() {
  const resp = await fetch('/api/plugins/life_stream/photos');
  const data = await resp.json();
  const grid = document.getElementById('photo-grid-plugin');
  if (grid) {
    grid.innerHTML = (data.photos || []).map(p => `
      <div class="photo-item">
        <img src="/media/photos/${p}" onclick="window.LifeStreamPlugin.openPhoto('${p}')">
      </div>
    `).join('') || 'No photos captured.';
  }
}

window.LifeStreamPlugin = {
  init: initLifeStream,
  openPhoto: (p) => {
    if (typeof openLightbox === 'function') openLightbox('/media/photos/' + p);
  },
  deletePhoto: async (path) => {
    if (!confirm("Löschen?")) return;
    const resp = await fetch('/api/plugins/life_stream/delete', {
      method: 'POST',
      body: JSON.stringify({ path })
    });
    const res = await resp.json();
    if (res.success) { 
      if (typeof closeLightbox === 'function') closeLightbox();
      loadPhotos();
    }
  }
};

if (document.getElementById('tab-life_stream')) initLifeStream();
