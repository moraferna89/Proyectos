/* ──────────────────────────────────────────
   Drag frameless window
────────────────────────────────────────── */
let dragState  = null;
let rafPending = false;
let pendingX = 0, pendingY = 0;

document.addEventListener('mousedown', async (e) => {
  if (e.button !== 0 || !window.pywebview) return;
  const dragEl = e.target.closest('.drag-region');
  if (!dragEl || e.target.closest('.no-drag')) return;
  const pos = await window.pywebview.api.get_pos();
  dragState = {
    startMouseX: e.screenX, startMouseY: e.screenY,
    startWinX:   pos.x,     startWinY:   pos.y,
  };
});
document.addEventListener('mousemove', (e) => {
  if (!dragState || !window.pywebview) return;
  pendingX = dragState.startWinX + (e.screenX - dragState.startMouseX);
  pendingY = dragState.startWinY + (e.screenY - dragState.startMouseY);
  if (!rafPending) {
    rafPending = true;
    requestAnimationFrame(() => {
      window.pywebview.api.move_window(pendingX, pendingY);
      rafPending = false;
    });
  }
});
document.addEventListener('mouseup',    () => { dragState = null; });
document.addEventListener('mouseleave', () => { dragState = null; });

/* ──────────────────────────────────────────
   Window controls
────────────────────────────────────────── */
function closeWindow()    { window.pywebview ? window.pywebview.api.close_window()    : window.close(); }
function minimizeWindow() { window.pywebview && window.pywebview.api.minimize_window(); }

/* ──────────────────────────────────────────
   Telegram scheduler toggle
────────────────────────────────────────── */
async function refreshSchedulerStatus() {
  if (!window.pywebview) return;
  const running = await window.pywebview.api.scheduler_status();
  const btn   = document.getElementById('btn-telegram');
  const label = document.getElementById('tg-label');
  if (running) {
    btn.classList.add('active');
    label.textContent = 'Señales ON';
  } else {
    btn.classList.remove('active');
    label.textContent = 'Señales OFF';
  }
}

async function toggleScheduler() {
  if (!window.pywebview) return;
  const btn = document.getElementById('btn-telegram');
  btn.disabled = true;
  const running = await window.pywebview.api.scheduler_status();
  if (running) await window.pywebview.api.scheduler_stop();
  else         await window.pywebview.api.scheduler_start();
  await refreshSchedulerStatus();
  btn.disabled = false;
}

/* ──────────────────────────────────────────
   Splash → App
────────────────────────────────────────── */
async function launchApp() {
  const btn = document.getElementById('btn-inicio');
  btn.disabled = true;
  btn.textContent = '...';
  if (window.pywebview) window.pywebview.api.launch();
  document.getElementById('splash').classList.add('fade-out');
  setTimeout(() => {
    document.getElementById('splash').style.display = 'none';
    const app = document.getElementById('app');
    app.classList.remove('app-hidden');
    app.classList.add('app-entering');
    document.body.classList.add('app-open');
    app.addEventListener('animationend', () => app.classList.remove('app-entering'), { once: true });
    refreshSchedulerStatus();
    runAnalysis();
  }, 480);
}

/* ──────────────────────────────────────────
   Count-up animation
────────────────────────────────────────── */
function countUp(el, target, duration = 900) {
  const start = performance.now();
  const from  = parseInt(el.textContent) || 0;
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const ease     = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (target - from) * ease);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ──────────────────────────────────────────
   Pipeline de análisis
────────────────────────────────────────── */
async function runAnalysis() {
  const btn     = document.getElementById('btn-analyze');
  const status  = document.getElementById('status-msg');
  const stats   = document.getElementById('stats');
  const results = document.getElementById('results');

  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⏳</span> Analizando...';
  status.className = 'status-loading';
  status.textContent = 'Recopilando mercados y consultando IA...';
  stats.style.display = 'none';
  results.innerHTML = '';

  try {
    const res = await fetch('/api/analyze');
    if (!res.ok) throw new Error((await res.json()).detail || 'Error desconocido');
    renderResults(await res.json());
  } catch (e) {
    status.className = 'status-error';
    status.textContent = e.message;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">▶</span> Analizar ahora';
  }
}

function renderResults(data) {
  const status  = document.getElementById('status-msg');
  const stats   = document.getElementById('stats');
  const results = document.getElementById('results');

  stats.style.display = 'grid';
  countUp(document.getElementById('stat-found'),    data.total_bets_found);
  countUp(document.getElementById('stat-filtered'), data.bets_in_range,           700);
  countUp(document.getElementById('stat-combos'),   data.combinations_generated, 1100);

  if (!data.top_combinations?.length) {
    status.className = 'status-idle';
    status.innerHTML = '<span class="idle-icon">⚽</span>No se encontraron combinaciones en rango 1.4–1.85.';
    return;
  }

  status.className  = '';
  status.textContent = '';

  data.top_combinations.forEach((item, i) => {
    const card = buildCard(item, i + 1);
    card.style.animationDelay = `${i * 0.05}s`;
    card.querySelector('.score-col').style.animationDelay = `${i * 0.05 + 0.15}s`;
    results.appendChild(card);
  });
}

/* ──────────────────────────────────────────
   Card builder — BetCombo
────────────────────────────────────────── */
function buildCard(item, rank) {
  const { combination, score, recommendation } = item;
  const { bet_a, bet_b, combined_odds } = combination;
  const level    = score >= 7 ? 'high' : score >= 5 ? 'med' : 'low';
  const recLabel = score >= 7 ? 'ALTA' : score >= 5 ? 'MEDIA' : 'BAJA';
  const timeA = fmtTime(bet_a.commence_time);
  const timeB = fmtTime(bet_b.commence_time);

  const card = document.createElement('div');
  card.className = 'combo-card';
  card.innerHTML = `
    <div class="combo-header">
      <span class="combo-rank"># ${rank}<span class="rank-sep">•</span>COMBINADA</span>
    </div>
    <div class="card-body">

      <div class="card-left">
        <div class="match-block">
          <div class="match-league-row">
            <span class="match-league">${bet_a.league}</span>
            <span class="market-badge">${bet_a.market_label}</span>
          </div>
          <span class="match-teams">${bet_a.home_team} vs ${bet_a.away_team}</span>
          <span class="bet-outcome">${bet_a.outcome}</span>
        </div>
        <div class="match-separator"></div>
        <div class="match-block">
          <div class="match-league-row">
            <span class="match-league">${bet_b.league}</span>
            <span class="market-badge">${bet_b.market_label}</span>
          </div>
          <span class="match-teams">${bet_b.home_team} vs ${bet_b.away_team}</span>
          <span class="bet-outcome">${bet_b.outcome}</span>
        </div>
      </div>

      <div class="card-center">
        <img src="/static/assets/logo_cartas.png" class="card-logo" alt="" />
      </div>

      <div class="card-right">
        <div class="match-right-top">
          <div class="match-odds-info">
            <span class="odds-label">Cuota</span>
            <span class="odds-value">${bet_a.odds}</span>
            <span class="match-time">${timeA}</span>
          </div>
          <div class="score-col">
            <div class="score-circle ${level}">${score}</div>
            <div class="rec-badge ${level}">${recLabel}</div>
          </div>
        </div>
        <div class="match-right-bottom">
          <span class="odds-value">${bet_b.odds}</span>
          <span class="match-time">${timeB}</span>
        </div>
      </div>

    </div>
    <div class="combo-footer">
      <span class="footer-label">CUOTA COMBINADA TOTAL:</span>
      <span class="footer-odds">${combined_odds}</span>
    </div>`;
  return card;
}

function fmtTime(iso) {
  return new Date(iso).toLocaleString('es-ES', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  });
}
