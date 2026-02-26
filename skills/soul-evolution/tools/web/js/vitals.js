/**
 * Project Genesis Dashboard - Vitals & Dashboard Logic (v5.7.0)
 */

const SECTION_COLORS = {
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
};

function sectionColor(name) {
  for (const [k, v] of Object.entries(SECTION_COLORS)) {
    if (name && name.includes(k)) return v;
  }
  return '#888';
}

function renderAgentName() {
  const idText = DATA.identity_raw || '';
  const nameMatch = idText.match(/\*\*Name:\*\*\s*(.+)/i) || idText.match(/Name:\s*(.+)/i);
  if (nameMatch && nameMatch[1]) {
    const name = nameMatch[1].replace(/\[|\]/g, '').trim();
    if (name && !name.includes('Agent Name')) {
      const nameEl = document.getElementById('agent-name');
      if (nameEl) nameEl.textContent = name;
      document.title = name + ' — Project Genesis';
    }
  }
}

function renderStats() {
  const bar = document.getElementById('stats-bar');
  if (!bar) return;
  const tree = DATA.soul_tree;
  let core = 0, mutable = 0, totalBullets = 0;
  tree.forEach(sec => {
    sec.children.forEach(child => {
      if (child.type === 'bullet') {
        totalBullets++;
        if (child.tag === 'CORE') core++;
        if (child.tag === 'MUTABLE') mutable++;
      }
      if (child.children) child.children.forEach(b => {
        if (b.type === 'bullet') {
          totalBullets++;
          if (b.tag === 'CORE') core++;
          if (b.tag === 'MUTABLE') mutable++;
        }
      });
    });
  });
  const stats = [
    { num: DATA.experiences.length, label: 'Experiences' },
    { num: DATA.reflections.length, label: 'Reflections' },
    { num: (DATA.news?.browsing_history || []).length, label: 'Web Searches' },
    { num: (DATA.news?.headlines || []).length, label: 'World News' },
    { num: core, label: 'Core' },
    { num: mutable, label: 'Mutable' },
  ];
  
  bar.innerHTML = stats.map(s =>
    `<div class="stat"><div class="num">${s.num}</div><div class="label">${s.label}</div></div>`
  ).join('');
}

function renderLegend() {
  const el = document.getElementById('legend');
  if (!el) return;
  const items = [
    { color: 'var(--core)', label: 'CORE (immutable)' },
    { color: 'var(--mutable)', label: 'MUTABLE (evolvable)' },
    ...Object.entries(SECTION_COLORS).map(([k, v]) => ({ color: v, label: k })),
  ];
  el.innerHTML = items.map(i =>
    `<div class="legend-item"><div class="legend-dot" style="background:${i.color}"></div>${i.label}</div>`
  ).join('');
}

let allBulletEls = [];
let editMode = false;

function renderSoulTree(revealUpTo) {
  const container = document.getElementById('soul-tree');
  if (!container) return;
  container.innerHTML = '';
  allBulletEls = [];

  const hiddenAfter = new Set();
  if (!editMode) {
    const changes = DATA.changes;
    for (let i = changes.length - 1; i >= 0; i--) {
      if (i >= revealUpTo) {
        if (changes[i].change_type === 'add' && changes[i].after) {
          hiddenAfter.add(changes[i].after.trim());
        }
      }
    }
  }

  DATA.soul_tree.forEach((sec, si) => {
    const color = sectionColor(sec.text);
    const block = document.createElement('div');
    block.className = 'section-block';
    block.style.borderColor = color + '33';

    const header = document.createElement('div');
    header.className = 'section-header';
    header.style.background = color + '0d';
    header.innerHTML = `<div class="dot" style="background:${color}"></div>${esc(sec.text)}<span class="arrow">▼</span>`;
    header.onclick = () => block.classList.toggle('collapsed');
    block.appendChild(header);

    const body = document.createElement('div');
    body.className = 'section-body';

    sec.children.forEach((child, ci) => {
      if (child.type === 'subsection') {
        const sub = document.createElement('div');
        sub.className = 'subsection';
        sub.innerHTML = `<div class="subsection-title">${esc(child.text)}</div>`;

        (child.children || []).forEach((b, bi) => {
          const bEl = renderBullet(b, hiddenAfter, [si, ci, bi]);
          sub.appendChild(bEl);
        });

        const addBtn = document.createElement('button');
        addBtn.className = 'btn-add-bullet';
        addBtn.textContent = '+ add bullet';
        addBtn.onclick = () => addBullet(si, ci);
        sub.appendChild(addBtn);

        body.appendChild(sub);
      } else if (child.type === 'bullet') {
        body.appendChild(renderBullet(child, hiddenAfter, [si, ci, -1]));
      }
    });

    block.appendChild(body);
    container.appendChild(block);
    setTimeout(() => block.classList.add('visible'), 80 * si);
  });
}

function renderBullet(b, hiddenAfter, path) {
  const el = document.createElement('div');
  el.className = 'bullet';
  const isHidden = hiddenAfter.has(b.raw.trim());
  if (isHidden) {
    el.classList.add('is-new');
  }

  const tagClass = b.tag === 'CORE' ? 'core' : (b.tag === 'MUTABLE' ? 'mutable' : '');

  if (editMode) {
    el.classList.add('editing');
    const [si, ci, bi] = path;

    const tagEl = document.createElement('span');
    tagEl.className = `tag ${tagClass} tag-toggle`;
    tagEl.textContent = b.tag || 'TAG';
    tagEl.onclick = () => {
      const next = b.tag === 'CORE' ? 'MUTABLE' : 'CORE';
      b.tag = next;
      updateBulletRaw(b);
      renderSoulTree(currentStep);
    };
    el.appendChild(tagEl);

    const input = document.createElement('textarea');
    input.className = 'edit-text';
    input.value = b.text;
    input.rows = 1;
    input.oninput = () => {
      input.style.height = 'auto';
      input.style.height = input.scrollHeight + 'px';
      b.text = input.value;
      updateBulletRaw(b);
    };
    setTimeout(() => { input.style.height = input.scrollHeight + 'px'; }, 0);
    el.appendChild(input);

    const del = document.createElement('button');
    del.className = 'btn-delete';
    del.innerHTML = '×';
    del.onclick = () => deleteBullet(si, ci, bi);
    el.appendChild(del);
  } else {
    el.innerHTML = `
      ${tagClass ? `<span class="tag ${tagClass}">${esc(b.tag)}</span>` : ''}
      <span>${esc(b.text)}</span>
    `;
  }

  allBulletEls.push({ el, raw: b.raw, tag: b.tag });
  return el;
}

function updateBulletRaw(b) {
  b.raw = `- ${b.text} [${b.tag}]`;
}

function toggleEditMode() {
  editMode = !editMode;
  const btn = document.getElementById('btn-edit');
  const saveBtn = document.getElementById('btn-save');
  const mapEl = document.getElementById('soul-map');

  if (editMode) {
    btn.classList.add('active');
    btn.textContent = '✎ Editing';
    saveBtn.style.display = '';
    mapEl.classList.add('edit-mode');
  } else {
    btn.classList.remove('active');
    btn.textContent = '✎ Edit';
    saveBtn.style.display = 'none';
    mapEl.classList.remove('edit-mode');
  }
  renderSoulTree(currentStep);
}

function addBullet(si, ci) {
  const sub = DATA.soul_tree[si].children[ci];
  if (!sub.children) sub.children = [];
  const sec = DATA.soul_tree[si];
  const newBullet = {
    type: 'bullet',
    text: 'New belief',
    raw: '- New belief [MUTABLE]',
    tag: 'MUTABLE',
    section: sec.raw,
    subsection: sub.raw,
  };
  sub.children.push(newBullet);
  renderSoulTree(currentStep);
}

function deleteBullet(si, ci, bi) {
  if (bi >= 0) {
    DATA.soul_tree[si].children[ci].children.splice(bi, 1);
  } else {
    DATA.soul_tree[si].children.splice(ci, 1);
  }
  renderSoulTree(currentStep);
}

function reconstructSoulMd() {
  let lines = ['# SOUL.md - Who You Are', '', '> ⚠️ This file is managed by **Soul Evolution**. Bullets tagged `[CORE]` are immutable.', '> Bullets tagged `[MUTABLE]` may evolve through the structured proposal pipeline.', '> Direct edits outside the pipeline are not permitted for `[MUTABLE]` items.', '> See `soul-evolution/SKILL.md` for the full protocol.', '', '---'];

  DATA.soul_tree.forEach(sec => {
    lines.push('', `## ${sec.text}`);
    sec.children.forEach(child => {
      if (child.type === 'subsection') {
        lines.push('', `### ${child.text}`, '');
        (child.children || []).forEach(b => lines.push(`- ${b.text} [${b.tag}]`));
      } else if (child.type === 'bullet') {
        lines.push(`- ${child.text} [${child.tag}]`);
      }
    });
  });

  lines.push('', '---', '', '_This file is yours to evolve. As you learn who you are, update it._');
  return lines.join('
');
}

function saveSoul() {
  const content = reconstructSoulMd();
  fetch('/save-soul', {
    method: 'POST',
    headers: { 'Content-Type': 'text/markdown' },
    body: content
  }).then(resp => {
    if (resp.ok) showToast('✓ SOUL.md saved', 'success');
    else throw new Error('Server save failed');
  }).catch(() => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'SOUL.md';
    a.click();
    URL.revokeObjectURL(url);
    showToast('✓ SOUL.md downloaded');
  });
}

let currentStep = -1;
let playing = false;
let playInterval = null;

function renderTimeline() {
  const changes = DATA.changes;
  const slider = document.getElementById('timeline-slider');
  if (!slider) return;
  slider.max = changes.length;
  slider.value = changes.length;
  currentStep = changes.length;
  slider.oninput = () => {
    currentStep = parseInt(slider.value);
    updateTimelineView();
  };
  updateTimelineView();
}

function updateTimelineView() {
  const changes = DATA.changes;
  const label = document.getElementById('timeline-label');
  if (!label) return;

  if (currentStep === 0) {
    label.textContent = 'origin';
  } else if (currentStep <= changes.length) {
    const c = changes[currentStep - 1];
    label.textContent = (c.timestamp || '').slice(11, 16) || `#${currentStep}`;
  }

  renderSoulTree(currentStep);
  renderChangesList(currentStep);
  document.getElementById('timeline-slider').value = currentStep;
}

function renderChangesList(upTo) {
  const container = document.getElementById('changes-list');
  if (!container) return;
  const changes = DATA.changes;

  if (changes.length === 0) {
    container.innerHTML = '<div class="empty-state">No soul changes yet.</div>';
    return;
  }

  container.innerHTML = '';
  changes.slice(0, upTo).forEach((c, i) => {
    const el = document.createElement('div');
    el.className = 'change-entry';
    const time = (c.timestamp || '').slice(0, 16).replace('T', ' ');
    const section = (c.section || '').replace('## ', '') + ' › ' + (c.subsection || '').replace('### ', '');
    const cleanContent = (c.after || c.before || '').replace(/\s*\[(CORE|MUTABLE)\]\s*/g, '').replace(/^- /, '');

    el.innerHTML = `
      <div class="change-time">${esc(time)}</div>
      <span class="change-type ${esc(c.change_type)}">${esc(c.change_type)}</span>
      <div class="change-section">${esc(section)}</div>
      <div class="change-content">${esc(cleanContent)}</div>
    `;
    container.appendChild(el);
    setTimeout(() => el.classList.add('visible'), 60 * i);
  });
}

function handleTimelinePlay() {
  if (playing) {
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    return;
  }
  playing = true;
  document.getElementById('btn-play').textContent = '⏸';
  currentStep = 0;
  updateTimelineView();

  playInterval = setInterval(() => {
    currentStep++;
    if (currentStep > DATA.changes.length) {
      clearInterval(playInterval);
      playing = false;
      document.getElementById('btn-play').textContent = '▶';
      return;
    }
    updateTimelineView();
    const change = DATA.changes[currentStep - 1];
    if (change && change.after) {
      const match = allBulletEls.find(b => b.raw.trim() === change.after.trim());
      if (match) {
        match.el.classList.remove('is-new');
        match.el.classList.add('revealed', 'highlight-enter');
        match.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, 1800);
}

function handleTimelineReset() {
  if (playing) {
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
  }
  currentStep = 0;
  updateTimelineView();
}

function renderFeed() {
  const container = document.getElementById('exp-feed');
  if (!container) return;
  const exps = DATA.experiences.slice().reverse();

  if (exps.length === 0) {
    container.innerHTML = '<div class="empty-state">No experiences logged yet.</div>';
    return;
  }

  container.innerHTML = exps.map(e => {
    const t = (e.timestamp || '').slice(11, 16);
    return `
      <div class="exp-entry">
        <div class="exp-meta">
          <span class="exp-source ${esc((e.source||'').toLowerCase())}">${esc(e.source)}</span>
          <span class="exp-sig ${esc((e.significance||'').toLowerCase())}">${esc(e.significance)}</span>
          <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc(t)}</span>
        </div>
        <div class="exp-content">${esc(e.content)}</div>
      </div>
    `;
  }).join('');
}

function vitalColor(value, key) {
  if (key === 'energy') {
    if (value < 10) return '#e05050';
    if (value < 30) return '#f0a050';
    if (value < 60) return '#e0d050';
    return '#50c878';
  }
  if (value > 90) return '#e05050';
  if (value > 70) return '#f0a050';
  if (value > 40) return '#e0d050';
  return '#50c878';
}

function renderVitals() {
  const ph = DATA.physique;
  const grid = document.getElementById('vitals-grid');
  const meta = document.getElementById('vitals-meta');
  if (!grid || !meta) return;

  if (!ph || !ph.needs) {
    grid.innerHTML = '<div class="empty-state">No vitals data available.</div>';
    return;
  }

  const needKeys = ['energy', 'hunger', 'thirst', 'bladder', 'bowel', 'hygiene', 'stress', 'arousal'];
  grid.innerHTML = needKeys.map(k => {
    const v = ph.needs[k] ?? 0;
    const color = vitalColor(v, k);
    return `<div class="vital-row">
      <span class="vital-label">${k}</span>
      <div class="vital-bar-bg"><div class="vital-bar" style="width:${v}%;background:${color}"></div></div>
      <span class="vital-value">${v}</span>
    </div>`;
  }).join('');

  const metaLines = [];
  if (ph.current_location) metaLines.push(`<span>📍 ${esc(ph.current_location)}</span>`);
  if (ph.current_outfit && ph.current_outfit.length) metaLines.push(`<span>👔 ${esc(ph.current_outfit.join(', '))}</span>`);
  if (ph.last_tick) metaLines.push(`<span>⏱ ${esc(ph.last_tick.slice(0, 19).replace('T', ' '))}</span>`);
  meta.innerHTML = metaLines.join('');
}

function renderMentalActivity() {
  const container = document.getElementById('mental-activity-list');
  if (!container) return;
  const news = DATA.news || {};
  const comms = DATA.internal_comm || {};
  const refs = DATA.reflections || [];
  const social = DATA.social_events || { pending: [] };
  
  let html = '';
  const activeSocial = social.pending.find(e => !e.processed);
  if (activeSocial) {
    html += `<div class="mental-card" style="border-left-color: #f0a050;">
      <span class="mental-label">Incoming Message from ${esc(activeSocial.sender_name)}</span>
      <div class="mental-content">"${esc(activeSocial.message)}"</div>
      <span class="mental-sub">${new Date(activeSocial.timestamp).toLocaleTimeString()}</span>
    </div>`;
  }

  const latestMemo = (comms.memos || []).find(m => m.sender === 'limbic' && m.type === 'emotion');
  const latestRef = refs[refs.length - 1];
  
  if (latestMemo) {
    html += `<div class="mental-card">
      <span class="mental-label">Inner Voice (Limbic)</span>
      <div class="mental-content">"${esc(latestMemo.content)}"</div>
      <span class="mental-sub">${new Date(latestMemo.timestamp).toLocaleTimeString()}</span>
    </div>`;
  } else if (latestRef) {
    html += `<div class="mental-card">
      <span class="mental-label">Current Reflection</span>
      <div class="mental-content">${esc(latestRef.summary || latestRef.reflection_summary || '')}</div>
    </div>`;
  }

  const history = news.browsing_history || [];
  if (history.length > 0) {
    const last = history[0];
    let snapHtml = last.screenshot ? `<img src="/media/browser_snapshots/${last.screenshot.split('/').pop()}" class="browser-snap" onclick="window.open(this.src)">` : '';
    html += `<div class="mental-card" style="border-left-color: var(--growth);">
      <span class="mental-label">Web Research</span>
      <div class="mental-content">Searching for: <strong>${esc(last.query)}</strong></div>
      ${snapHtml}
      <span class="mental-sub">${new Date(last.timestamp).toLocaleTimeString()}</span>
    </div>`;
  }

  container.innerHTML = html || '<div class="empty-state">Observing cognitive processes...</div>';

  const ticker = document.getElementById('ticker-content');
  const headlines = news.headlines || [];
  if (ticker && headlines.length > 0) {
    const line = headlines.map(h => `<div class="ticker-item">[${h.category.toUpperCase()}] ${esc(h.title)}</div>`).join('');
    ticker.innerHTML = line + line;
  }

  const statusText = document.getElementById('status-text');
  if (statusText) {
    if (history.length > 0 && (new Date() - new Date(history[0].timestamp)) < 300000) {
      statusText.textContent = 'Autonomous Web Research Active';
      statusText.style.color = 'var(--growth)';
    } else if (latestMemo) {
      statusText.textContent = 'Processing Internal Narrative';
      statusText.style.color = 'var(--accent)';
    } else {
      statusText.textContent = 'Cognitive System Synchronized';
      statusText.style.color = 'var(--text-dim)';
    }
  }
}

function renderProposals() {
  const list = document.getElementById('proposals-list');
  const count = document.getElementById('proposals-count');
  if (!list || !count) return;
  const pending = DATA.proposals_pending || [];
  count.textContent = pending.length > 0 ? `(${pending.length})` : '';

  if (pending.length === 0) {
    list.innerHTML = '<div class="empty-state">No pending proposals.</div>';
    return;
  }

  list.innerHTML = pending.map((p, i) => {
    const type = (p.change_type || p.type || 'modify').toLowerCase();
    return `<div class="proposal-card" id="proposal-${i}">
      <div class="proposal-header">
        <span class="proposal-id">${esc(p.id || 'PROP-' + i)}</span>
        <span class="proposal-type ${esc(type)}">${esc(type)}</span>
      </div>
      <div class="proposal-section">${esc(p.section || '')} ${p.subsection ? '› ' + esc(p.subsection) : ''}</div>
      <div class="proposal-content">${esc(p.content || p.after || p.proposed || '')}</div>
      <div class="proposal-reason">${esc(p.reason || p.rationale || '')}</div>
      <div class="proposal-actions">
        <button class="btn-approve" onclick="resolveProposal(${i}, 'approved')">Approve</button>
        <button class="btn-reject" onclick="resolveProposal(${i}, 'rejected')">Reject</button>
      </div>
    </div>`;
  }).join('');
}

function resolveProposal(index, decision) {
  fetch('/resolve-proposal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ index, decision })
  }).then(r => {
    if (r.ok) {
      const card = document.getElementById('proposal-' + index);
      if (card) card.style.display = 'none';
      showToast('✓ Proposal ' + decision, 'success');
    } else alert('Failed to resolve proposal.');
  }).catch(() => alert('Server not reachable.'));
}

function renderReflections() {
  const list = document.getElementById('reflections-list');
  if (!list) return;
  const refs = (DATA.reflections || []).slice().reverse();

  if (refs.length === 0) {
    list.innerHTML = '<div class="empty-state">No reflections yet.</div>';
    return;
  }

  list.innerHTML = refs.slice(0, 20).map(r => {
    const insights = r.insights || r.key_insights || [];
    return `<div class="reflection-card collapsed">
      <div class="reflection-header" onclick="this.parentElement.classList.toggle('collapsed')">
        <span class="ref-type">${esc(r.type || r.reflection_type || 'batch')}</span>
        <span style="color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc((r.summary||r.reflection_summary||'').slice(0, 80))}</span>
        <span class="ref-arrow">▼</span>
      </div>
      <div class="reflection-body">
        <div>${esc(r.summary || r.reflection_summary || '')}</div>
        ${insights.length > 0 ? '<ul class="ref-insights">' + insights.map(ins => '<li>' + esc(typeof ins === 'string' ? ins : (ins.insight || JSON.stringify(ins))) + '</li>').join('') + '</ul>' : ''}
        ${r.proposal_decision || r.proposals_generated ? `<div style="margin-top:0.4rem;font-size:0.68rem;color:var(--accent)">Proposals: ${esc(String(r.proposal_decision || r.proposals_generated))}</div>` : ''}
      </div>
    </div>`;
  }).join('');
}

function renderSignificant() {
  const list = document.getElementById('significant-list');
  if (!list) return;
  const sigs = (DATA.significant || []).slice().reverse();

  if (sigs.length === 0) {
    list.innerHTML = '<div class="empty-state">No significant memories yet.</div>';
    return;
  }

  list.innerHTML = sigs.map(s => `
    <div class="sig-entry">
      <div class="exp-meta">
        <span class="sig-badge">${esc(s.significance || 'notable')}</span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc(s.id || '')}</span>
        <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc((s.timestamp || '').slice(0, 16).replace('T', ' '))}</span>
      </div>
      <div class="sig-content">${esc((s.content || s.summary || '').slice(0, 200))}</div>
      ${s.context || s.significance_reason ? '<div class="sig-context">' + esc(s.context || s.significance_reason) + '</div>' : ''}
    </div>
  `).join('');
}

function renderPipelineState() {
  const cards = document.getElementById('state-cards');
  const runs = document.getElementById('pipeline-runs');
  if (!cards || !runs) return;
  const state = DATA.state || {};
  const pipeline = DATA.pipeline || [];

  const stateEntries = Object.entries(state);
  if (stateEntries.length === 0 && pipeline.length === 0) {
    cards.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No pipeline state yet.</div>';
    return;
  }

  cards.innerHTML = stateEntries.map(([k, v]) => {
    const display = typeof v === 'object' ? JSON.stringify(v) : String(v);
    return `<div class="state-card">
      <div class="sc-value">${esc(display.length > 12 ? display.slice(0, 12) + '…' : display)}</div>
      <div class="sc-label">${esc(k.replace(/_/g, ' '))}</div>
    </div>`;
  }).join('');

  if (pipeline.length > 0) {
    runs.innerHTML = `<div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--text-dim);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.08em">Recent Runs</div>` +
      pipeline.slice(-10).reverse().map(p => {
        const ts = (p.timestamp || p.completed_at || '').slice(0, 16).replace('T', ' ');
        return `<div class="pipeline-run">${esc(ts)} — ${esc(p.status || p.result || 'done')}</div>`;
      }).join('');
  }
}

// Export to window
window.renderAgentName = renderAgentName;
window.renderStats = renderStats;
window.renderLegend = renderLegend;
window.renderSoulTree = renderSoulTree;
window.toggleEditMode = toggleEditMode;
window.saveSoul = saveSoul;
window.renderTimeline = renderTimeline;
window.handleTimelinePlay = handleTimelinePlay;
window.handleTimelineReset = handleTimelineReset;
window.renderFeed = renderFeed;
window.renderVitals = renderVitals;
window.renderMentalActivity = renderMentalActivity;
window.renderProposals = renderProposals;
window.resolveProposal = resolveProposal;
window.renderReflections = renderReflections;
window.renderSignificant = renderSignificant;
window.renderPipelineState = renderPipelineState;

// Phase 31: Interests & Dreams
async function loadInterestsTab() {
  try {
    const res = await fetch('/api/interests');
    const interests = await res.json();
    const hobbyList = document.getElementById('hobby-list');
    if (hobbyList && interests.hobbies) {
      if (interests.hobbies.length === 0) {
        hobbyList.innerHTML = '<div style="color:var(--text-dim);">No hobbies discovered yet.</div>';
      } else {
        hobbyList.innerHTML = interests.hobbies.map(h => `
          <div class="panel-card" style="padding:0.75rem;">
            <div style="font-weight:bold;">${h.topic}</div>
            <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.5rem;">
              <div style="flex:1;height:6px;background:var(--bg);border-radius:3px;overflow:hidden;">
                <div style="width:${h.sentiment * 100}%;height:100%;background:var(--accent);border-radius:3px;"></div>
              </div>
              <span style="font-size:0.8rem;color:var(--text-dim);">${Math.round(h.sentiment * 100)}%</span>
            </div>
          </div>
        `).join('');
      }
    }
    const likesList = document.getElementById('likes-list');
    if (likesList && interests.likes) {
      const likes = Object.entries(interests.likes);
      likesList.innerHTML = likes.length ? likes.map(([topic, score]) => `
        <div style="padding:0.25rem 0;border-bottom:1px solid var(--border);">
          <span>${topic}</span>
          <span style="float:right;color:var(--growth);">${Math.round(score * 100)}%</span>
        </div>
      `).join('') : '<div style="color:var(--text-dim);font-size:0.85rem;">No likes yet</div>';
    }
  } catch (e) { console.error(e); }
}

async function loadDreamsTab() {
  try {
    const res = await fetch('/api/dreams');
    const data = await res.json();
    if (document.getElementById('dream-count')) document.getElementById('dream-count').textContent = data.count || 0;
    if (document.getElementById('insight-count')) document.getElementById('insight-count').textContent = data.insights || 0;
    const dreamList = document.getElementById('dream-list');
    if (dreamList && data.dreams) {
      dreamList.innerHTML = data.dreams.length ? data.dreams.map(d => `
        <div class="panel-card" style="margin-bottom:1rem;padding:1rem;border-left:4px solid var(--dream);">
          <h4 style="color:var(--accent);">${d.date}</h4>
          <p style="margin-top:0.5rem;color:var(--text);">${d.summary}</p>
        </div>
      `).join('') : '<div style="color:var(--text-dim);font-style:italic;">No dreams yet</div>';
    }
  } catch (e) { console.error(e); }
}
window.loadInterestsTab = loadInterestsTab;
window.loadDreamsTab = loadDreamsTab;

function getCategoryIcon(cat) {
  const icons = { furniture: '🪑', electronics: '💻', decoration: '🎨', storage: '📦' };
  return icons[cat] || '📦';
}

function renderInterior() {
  const interior = DATA.interior || { rooms: [] };
  const tabsEl = document.getElementById('room-tabs');
  const gridEl = document.getElementById('interior-grid');
  const detailEl = document.getElementById('interior-detail');
  if (!tabsEl || !gridEl || !detailEl) return;

  if (interior.rooms.length === 0) {
    tabsEl.innerHTML = '';
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No rooms yet. Add one to get started.</div>';
    detailEl.innerHTML = '';
    return;
  }

  if (!window._currentRoom || !interior.rooms.find(r => r.id === window._currentRoom)) {
    window._currentRoom = interior.rooms[0].id;
  }

  tabsEl.innerHTML = interior.rooms.map(r => {
    const cnt = r.objects ? r.objects.length : 0;
    return `<button class="room-tab ${r.id === window._currentRoom ? 'active' : ''}" onclick="window._currentRoom='${esc(r.id)}';renderInterior();">${esc(r.name)} (${cnt})</button>`;
  }).join('') + `<button class="room-tab" style="color:var(--core);" onclick="removeRoom('${esc(window._currentRoom)}')">- Remove</button>`;

  const room = interior.rooms.find(r => r.id === window._currentRoom);
  if (!room) return;

  detailEl.innerHTML = `<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">${esc(room.description || '')}</div>
    <button class="btn-crud" onclick="addObject('${esc(room.id)}')">+ Object</button>`;

  const topLevel = room.objects.filter(o => !o.located_on);
  gridEl.innerHTML = topLevel.map(obj => {
    const thumb = obj.images && obj.images.length > 0
      ? `<img src="/${obj.images[0]}" alt="${esc(obj.name)}">`
      : getCategoryIcon(obj.category);
    const subs = (obj.items_on || []).map(id => room.objects.find(o => o.id === id)).filter(Boolean);
    const subHtml = subs.length > 0
      ? `<div style="font-size:0.65rem;color:var(--text-dim);margin-top:0.3rem;">Items: ${subs.map(s => esc(s.name)).join(', ')}</div>`
      : '';
    return `<div class="item-card" onclick="openLightbox('interior','${esc(obj.id)}',${JSON.stringify(obj.images||[])},0)">
      <div class="thumb">${thumb}</div>
      <div class="card-name">${esc(obj.name)}</div>
      <div class="card-meta">${esc(obj.category)}${subHtml}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;">
        <button class="btn-crud danger" onclick="event.stopPropagation();removeObject('${esc(room.id)}','${esc(obj.id)}')">Remove</button>
      </div>
    </div>`;
  }).join('');
}

async function addRoom() {
  const result = await openModal('Add Room', [
    { key: 'name', label: 'Room Name', placeholder: 'e.g. Living Room' },
    { key: 'desc', label: 'Description (optional)', placeholder: '' },
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || { rooms: [] };
  const newRoom = { id: 'room_' + Date.now().toString(36), name: result.name, description: result.desc || '', objects: [] };
  interior.rooms.push(newRoom);
  DATA.interior = interior;
  window._currentRoom = newRoom.id;
  saveInterior();
  renderInterior();
}

function removeRoom(roomId) {
  if (!confirm('Remove this room and all its objects?')) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  if (room) {
    for (const obj of room.objects) {
      if (typeof deleteAllImages === 'function') deleteAllImages('interior', obj.id, obj.images);
    }
  }
  interior.rooms = interior.rooms.filter(r => r.id !== roomId);
  DATA.interior = interior;
  window._currentRoom = null;
  saveInterior();
  renderInterior();
}

async function addObject(roomId) {
  const result = await openModal('Add Object', [
    { key: 'name', label: 'Object Name', placeholder: 'e.g. Desk' },
    { key: 'category', label: 'Category', type: 'select', options: ['furniture', 'electronics', 'decoration', 'storage', 'other'] },
    { key: 'desc', label: 'Description (optional)', placeholder: '' },
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  room.objects.push({
    id: 'obj_' + Date.now().toString(36),
    name: result.name, category: result.category || 'other', description: result.desc || '',
    images: [], added_at: new Date().toISOString()
  });
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}

function removeObject(roomId, objId) {
  if (!confirm('Remove this object?')) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  const obj = room.objects.find(o => o.id === objId);
  if (obj && typeof deleteAllImages === 'function') deleteAllImages('interior', objId, obj.images);
  room.objects = room.objects.filter(o => o.id !== objId);
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}

function saveInterior() {
  fetch('/update-interior', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(DATA.interior)
  }).then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    showToast('Interior saved', 'success');
  }).catch(err => showToast('Save failed: ' + err, 'error'));
}

window.renderInterior = renderInterior;
window.addRoom = addRoom;
window.removeRoom = removeRoom;
window.addObject = addObject;
window.removeObject = removeObject;

// Inventory logic
window._invCategoryFilter = 'all';
function renderInventoryPanel() {
  const inv = DATA.inventory || { items: [], categories: [] };
  const chipsEl = document.getElementById('inv-chips');
  if (!chipsEl) return;

  const cats = ['all', ...(inv.categories || [])];
  const countMap = {};
  (inv.items || []).forEach(i => { countMap[i.category] = (countMap[i.category] || 0) + 1; });
  const totalCount = (inv.items || []).length;

  chipsEl.innerHTML = cats.map(c => {
    const cnt = c === 'all' ? totalCount : (countMap[c] || 0);
    return `<button class="chip ${c === window._invCategoryFilter ? 'active' : ''}" onclick="window._invCategoryFilter='${c}';renderInventoryPanel();">${c} (${cnt})</button>`;
  }).join('') + `<button class="btn-crud" style="margin-left:auto;" onclick="addInventoryItem()">+ Item</button>`;

  filterInventory();
}

function filterInventory() {
  const inv = DATA.inventory || { items: [], categories: [] };
  const query = (document.getElementById('inv-search')?.value || '').toLowerCase();
  const gridEl = document.getElementById('inventory-grid');
  if (!gridEl) return;

  let items = inv.items || [];
  if (window._invCategoryFilter !== 'all') items = items.filter(i => i.category === window._invCategoryFilter);
  if (query) items = items.filter(i =>
    i.name.toLowerCase().includes(query) ||
    (i.description || '').toLowerCase().includes(query) ||
    (i.tags || []).some(t => t.toLowerCase().includes(query))
  );

  gridEl.innerHTML = items.length ? items.map(item => {
    const thumb = item.images && item.images.length > 0 ? `<img src="/${item.images[0]}" alt="${esc(item.name)}">` : '📦';
    const locBadge = item.location ? `<span style="font-size:0.6rem;background:var(--accent-glow);padding:0.1rem 0.4rem;border-radius:8px;color:var(--accent);">@ ${esc(item.location)}</span>` : '';
    const tags = (item.tags || []).map(t => `<span style="font-size:0.55rem;background:var(--bg);padding:0.1rem 0.3rem;border-radius:4px;color:var(--text-dim);">${esc(t)}</span>`).join(' ');
    return `<div class="item-card" onclick="openLightbox('inventory','${item.id}',${JSON.stringify(item.images||[])},0)">
      <div class="thumb">${thumb}</div>
      <div class="card-name">${esc(item.name)}</div>
      <div class="card-meta">x${item.quantity} [${esc(item.category)}] ${locBadge}</div>
      <div style="margin-top:0.2rem;">${tags}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;"><button class="btn-crud danger" onclick="event.stopPropagation();removeInventoryItem('${item.id}')">Remove</button></div>
    </div>`;
  }).join('') : '<div style="color:var(--text-dim);font-size:0.85rem;">No items found.</div>';
}

async function addInventoryItem() {
  const result = await openModal('Add Item', [{ key: 'name', label: 'Item Name' }, { key: 'category', label: 'Category' }, { key: 'qty', label: 'Quantity', type: 'number', default: '1' }]);
  if (!result || !result.name) return;
  const inv = DATA.inventory || { items: [], categories: [] };
  const qty = parseInt(result.qty, 10) || 1;
  const category = result.category || 'other';
  inv.items.push({ id: 'inv_'+Date.now().toString(36), name: result.name, category, quantity: qty, images: [], tags: [], added_at: new Date().toISOString() });
  if (!inv.categories.includes(category)) inv.categories.push(category);
  DATA.inventory = inv; saveInventory(); renderInventoryPanel();
}

function removeInventoryItem(itemId) {
  if (!confirm('Remove this item?')) return;
  const inv = DATA.inventory || { items: [], categories: [] };
  const item = inv.items.find(i => i.id === itemId);
  if (item && typeof deleteAllImages === 'function') deleteAllImages('inventory', itemId, item.images);
  inv.items = inv.items.filter(i => i.id !== itemId);
  DATA.inventory = inv; saveInventory(); renderInventoryPanel();
}

function saveInventory() {
  fetch('/update-inventory', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(DATA.inventory) })
  .then(r => r.ok ? showToast('Inventory saved', 'success') : null);
}

window.renderInventoryPanel = renderInventoryPanel;
window.addInventoryItem = addInventoryItem;
window.removeInventoryItem = removeInventoryItem;

// Wardrobe logic
window._wardrobeCatFilter = 'all';
function renderWardrobePanel() {
  const wd = DATA.wardrobe || { inventory: {}, outfits: {} };
  const chipsEl = document.getElementById('wardrobe-chips');
  const gridEl = document.getElementById('wardrobe-grid');
  if (!chipsEl || !gridEl) return;

  const cats = Object.keys(wd.inventory || {});
  chipsEl.innerHTML = ['all', ...cats].map(c => `<button class="chip ${c === window._wardrobeCatFilter ? 'active' : ''}" onclick="window._wardrobeCatFilter='${c}';renderWardrobePanel();">${c}</button>`).join('');

  let allItems = [];
  for (const [cat, items] of Object.entries(wd.inventory || {})) {
    if (window._wardrobeCatFilter !== 'all' && cat !== window._wardrobeCatFilter) continue;
    items.forEach(item => { if (typeof item === 'object') allItems.push({...item, _cat: cat}); });
  }

  gridEl.innerHTML = allItems.length ? allItems.map(item => {
    const thumb = item.images?.length ? `<img src="/${item.images[0]}" alt="${esc(item.name)}">` : '👕';
    return `<div class="item-card" onclick="openLightbox('wardrobe','${item.id}',${JSON.stringify(item.images||[])},0)">
      <div class="thumb">${thumb}</div>
      <div class="card-name">${esc(item.name)}</div>
      <div class="card-meta">${esc(item._cat)}</div>
    </div>`;
  }).join('') : '<div style="color:var(--text-dim);font-size:0.85rem;">No items in wardrobe.</div>';
}
window.renderWardrobePanel = renderWardrobePanel;

// Development / World / Skills / Voice (simplified)
function renderDevPanel() {
  const manifest = DATA.dev_manifest || { projects: [] };
  const gridEl = document.getElementById('dev-grid');
  if (!gridEl) return;
  gridEl.innerHTML = manifest.projects.map(p => `<div class="item-card" onclick="showDevDetail('${p.id}')"><div class="card-name">${esc(p.name)}</div></div>`).join('');
}
function renderWorldPanel() {
  const ws = DATA.world_state || {};
  const weatherIcons = { sunny: '☀️', cloudy: '☁️', rainy: '🌧️', stormy: '⛈️', snowy: '❄️' };
  const el = document.getElementById('world-weather');
  if (el) el.innerHTML = `<div style="font-size:3rem;text-align:center;">${weatherIcons[ws.weather] || '🌤️'}</div>`;
}
function renderSkillsPanel() {
  const skills = DATA.skills?.skills || [];
  const el = document.getElementById('skills-list');
  if (el) el.innerHTML = skills.map(s => `<div><strong>${s.name}</strong> Lv.${s.level}</div>`).join('');
}

window.renderDevPanel = renderDevPanel;
window.renderWorldPanel = renderWorldPanel;
window.renderSkillsPanel = renderSkillsPanel;
window.renderPhotoStream = () => {
  const container = document.getElementById('photo-stream');
  if (container) container.innerHTML = (DATA.photos || []).map(p => `<img src="/media/photos/${p}" style="width:100px;">`).join('');
};

// Presence & Hardware
async function loadPresenceState() {
  try {
    const response = await fetch('/api/presence/state');
    const state = await response.json();
    const statusEl = document.getElementById('presence-status');
    if (statusEl) {
      statusEl.textContent = state.isActive ? 'Active' : 'Inactive';
      statusEl.style.color = state.isActive ? '#10b981' : 'var(--text-dim)';
    }
    const moodEl = document.getElementById('presence-mood');
    if (moodEl) {
      const moodColors = { 'euphoric': '#10b981', 'happy': '#10b981', 'content': '#10b981', 'neutral': 'var(--core)', 'stressed': '#ef4444', 'anxious': '#f59e0b', 'tired': '#6b7280' };
      moodEl.textContent = (state.currentMood || 'neutral').charAt(0).toUpperCase() + (state.currentMood || 'neutral').slice(1);
      moodEl.style.color = moodColors[state.currentMood] || 'var(--text)';
    }
    const feedEl = document.getElementById('social-feed');
    if (feedEl && state.feed) {
      feedEl.innerHTML = state.feed.length ? state.feed.slice(0, 10).map(post => `
        <div style="padding:0.75rem;background:var(--bg-dim);border-radius:6px;margin-bottom:0.5rem;border-left:3px solid #10b981">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
            <span style="font-size:1.2rem;">${post.type==='selfie'?'📷':'🎉'}</span>
            <span style="font-size:0.75rem;color:var(--text-dim);">${new Date(post.timestamp).toLocaleTimeString()}</span>
          </div>
          <div style="font-size:0.9rem;line-height:1.4;">${post.content}</div>
        </div>
      `).join('') : '<p style="color:var(--text-dim);font-size:0.85rem;">No posts yet.</p>';
    }
  } catch (e) { console.log('Presence state error:', e); }
}

function startPresencePolling() {
  if (window._presencePolling) clearInterval(window._presencePolling);
  loadPresenceState();
  window._presencePolling = setInterval(loadPresenceState, 5000);
}

async function loadHardwareState() {
  try {
    const response = await fetch('/api/hardware/resonance');
    const state = await response.json();
    const cpuEl = document.getElementById('hardware-cpu');
    if (cpuEl) {
      cpuEl.textContent = (state.currentCpuLoad || 0).toFixed(0) + '%';
      cpuEl.style.color = state.currentCpuLoad > 80 ? '#ef4444' : 'var(--accent)';
    }
    const ramEl = document.getElementById('hardware-ram');
    if (ramEl) {
      ramEl.textContent = (state.currentMemoryUsage || 0).toFixed(0) + '%';
      ramEl.style.color = state.currentMemoryUsage > 85 ? '#ef4444' : 'var(--growth)';
    }
  } catch (e) { console.log('Hardware state error:', e); }
}

// Analytics
async function loadAnalyticsData() {
  try {
    const vitalsResponse = await fetch('/api/telemetry/vitals');
    const vitals = await vitalsResponse.json();
    const vitalsEl = document.getElementById('analytics-vitals');
    if (vitalsEl && vitals.length > 0) {
      vitalsEl.innerHTML = '<div style="display:flex;gap:2px;height:100px;align-items:flex-end;">' +
        vitals.slice(-48).map(v => `<div style="flex:1;display:flex;flex-direction:column;gap:1px;"><div style="height:${v.needs?.stress||50}%;background:var(--danger);min-height:1px;"></div><div style="height:${v.needs?.energy||50}%;background:var(--growth);min-height:1px;"></div></div>`).join('') +
        '</div>';
    }
  } catch (e) { console.log('Analytics load error:', e); }
}

window.loadPresenceState = loadPresenceState;
window.startPresencePolling = startPresencePolling;
window.loadHardwareState = loadHardwareState;
window.loadAnalyticsData = loadAnalyticsData;

async function addManualContact() {
  const name = document.getElementById('new-contact-name').value.trim();
  const circle = document.getElementById('new-contact-circle').value;
  if (!name) { showToast('Please enter a name.', 'error'); return; }
  try {
    const response = await fetch('/api/social/add-entity', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entity_name: name, circle: circle, relationship_type: 'acquaintance' }) });
    const result = await response.json();
    if (result.success) { showToast('✓ Contact added!', 'success'); document.getElementById('new-contact-name').value = ''; loadContactCRM(); }
    else showToast('Error: ' + result.error, 'error');
  } catch (e) { showToast(e.message, 'error'); }
}

async function reImagineNPC(entityId, name) {
  const promptText = prompt('Enter new visual description for ' + name + ':');
  if (!promptText || !promptText.trim()) return;
  try {
    const response = await fetch('/api/social/update-entity', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ entity_id: entityId, visual_description: promptText.trim() }) });
    const result = await response.json();
    if (result.success) { showToast('Visual description updated!', 'success'); loadContactCRM(); }
    else showToast('Error: ' + result.error, 'error');
  } catch (e) { showToast(e.message, 'error'); }
}

// God-Mode
async function initGodMode() {
  const sliders = ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'];
  const container = document.getElementById('godmode-sliders');
  if (!container) return;
  container.innerHTML = '';
  sliders.forEach(k => {
    const row = document.createElement('div');
    row.style.display = 'grid'; row.style.gridTemplateColumns = '100px 1fr 40px'; row.style.gap = '1rem'; row.style.alignItems = 'center';
    row.innerHTML = `<label style="text-transform:capitalize; color:var(--text-dim);">${k}</label>
      <input type="range" id="gm-${k}" min="0" max="100" value="50" oninput="document.getElementById('gm-${k}-val').textContent=this.value">
      <span id="gm-${k}-val" style="color:var(--accent);">50</span>`;
    container.appendChild(row);
  });
  try {
    const resp = await fetch('/api/godmode/physique');
    const data = await resp.json();
    if (data && data.needs) {
      Object.entries(data.needs).forEach(([k, v]) => {
        const el = document.getElementById('gm-' + k);
        if (el) { el.value = v; document.getElementById('gm-' + k + '-val').textContent = v; }
      });
    }
  } catch(e) {}
}

async function applyGodModeNeeds() {
  const needs = {};
  ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'].forEach(k => {
    needs[k] = parseInt(document.getElementById('gm-' + k).value);
  });
  await fetch('/api/godmode/override/needs', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(needs) });
  showToast('✅ Needs updated!', 'success');
}

async function injectGodModeEvent() {
  const event = {
    type: document.getElementById('gm-event-type').value,
    event: document.getElementById('gm-event-desc').value || 'Manual Override',
    impact: parseInt(document.getElementById('gm-event-impact').value)
  };
  await fetch('/api/godmode/inject/event', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(event) });
  showToast('🎲 Event injected!', 'success');
}

window.addManualContact = addManualContact;
window.reImagineNPC = reImagineNPC;
window.initGodMode = initGodMode;
window.applyGodModeNeeds = applyGodModeNeeds;
window.injectGodModeEvent = injectGodModeEvent;
