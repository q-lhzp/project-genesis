/**
 * Project Genesis Dashboard - Economy & The Vault Logic (v5.7.0)
 */

async function loadVaultData() {
  try {
    const res = await fetch('/api/vault/status');
    const result = await res.json();
    
    // Update balance
    const balanceEl = document.getElementById('vault-balance');
    if (balanceEl && result.balances) {
      balanceEl.textContent = '$' + (result.balances.USD || 0).toLocaleString();
    }

    // Render portfolio
    const portfolioDiv = document.getElementById('vault-portfolio');
    if (portfolioDiv && result.positions) {
      const positions = Object.entries(result.positions);
      if (positions.length === 0) {
        portfolioDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No active positions.</p>';
      } else {
        portfolioDiv.innerHTML = positions.map(([symbol, qty]) => `
          <div style="display:flex;justify-content:space-between;padding:0.5rem;background:var(--bg);border-radius:4px;margin-bottom:0.4rem;">
            <span><strong>${symbol}</strong></span>
            <span>${qty} units</span>
          </div>
        `).join('');
      }
    }
  } catch (e) { console.error('Vault load error:', e); }
}

function startEconomyPolling() {
  if (window._economyPolling) clearInterval(window._economyPolling);
  loadVaultData();
  window._economyPolling = setInterval(loadVaultData, 10000);
}

window.loadVaultData = loadVaultData;
window.startEconomyPolling = startEconomyPolling;
