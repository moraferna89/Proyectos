/* ──────────────────────────────────────────
   Drag frameless window
────────────────────────────────────────── */
let _currentCombos = [];
let _currentSort   = 'score';

function setSort(criteria) {
  _currentSort = criteria;
  document.getElementById('sort-score').classList.toggle('active', criteria === 'score');
  document.getElementById('sort-date').classList.toggle('active',  criteria === 'date');
  _renderCombos();
}

function _sortedCombos() {
  const copy = [..._currentCombos];
  if (_currentSort === 'date') {
    copy.sort((a, b) => {
      const tA = Math.min(new Date(a.combination.match_a.commence_time), new Date(a.combination.match_b.commence_time));
      const tB = Math.min(new Date(b.combination.match_a.commence_time), new Date(b.combination.match_b.commence_time));
      return tA - tB;
    });
  } else {
    copy.sort((a, b) => b.score - a.score);
  }
  return copy;
}

function _renderCombos() {
  const results = document.getElementById('results');
  results.innerHTML = '';
  _sortedCombos().forEach((item, i) => {
    const card = buildCard(item, i + 1);
    card.style.animationDelay = `${i * 0.07}s`;
    card.querySelector('.score-col').style.animationDelay = `${i * 0.07 + 0.2}s`;
    results.appendChild(card);
  });
}

let dragState   = null;
let rafPending  = false;
let pendingX = 0, pendingY = 0;

document.addEventListener('mousedown', async (e) => {
  if (e.button !== 0 || !window.pywebview) return;
  const dragEl = e.target.closest('.drag-region');
  if (!dragEl || e.target.closest('.no-drag')) return;

  const pos = await window.pywebview.api.get_pos();
  dragState = {
    startMouseX: e.screenX, startMouseY: e.screenY,
    startWinX: pos.x,       startWinY: pos.y,
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
  if (running) {
    await window.pywebview.api.scheduler_stop();
  } else {
    await window.pywebview.api.scheduler_start();
  }
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

  // Lanzar animación de expansión de ventana (Python) y fade del splash en paralelo
  if (window.pywebview) window.pywebview.api.launch();   // no await → corre en paralelo

  document.getElementById('splash').classList.add('fade-out');

  // Esperar ~480ms (duración de la animación de ventana) antes de mostrar el app
  setTimeout(() => {
    const splash = document.getElementById('splash');
    const app    = document.getElementById('app');
    splash.style.display = 'none';
    app.classList.remove('app-hidden');
    app.classList.add('app-entering');
    document.body.classList.add('app-open');
    app.addEventListener('animationend', () => app.classList.remove('app-entering'), { once: true });
    refreshSchedulerStatus();
    loadSaved();
  }, 480);
}

/* ──────────────────────────────────────────
   Count-up animation
────────────────────────────────────────── */
function countUp(el, target, duration = 900) {
  const start = performance.now();
  const from = parseInt(el.textContent) || 0;

  function step(now) {
    const elapsed  = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease     = 1 - Math.pow(1 - progress, 3);   // ease-out cubic
    el.textContent = Math.round(from + (target - from) * ease);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ──────────────────────────────────────────
   Carga rápida desde BD al abrir el dashboard
────────────────────────────────────────── */
async function loadSaved() {
  const status  = document.getElementById('status-msg');
  const stats   = document.getElementById('stats');
  const results = document.getElementById('results');

  try {
    const res  = await fetch('/api/saved');
    if (!res.ok) return;
    const data = await res.json();

    if (data.top_combinations?.length) {
      stats.style.display = 'grid';
      document.getElementById('stat-found').textContent    = '—';
      document.getElementById('stat-filtered').textContent = '—';
      countUp(document.getElementById('stat-combos'), data.combinations_generated);
      status.style.display = 'none';
      document.getElementById('sort-bar').style.display = 'flex';
      _currentCombos = data.top_combinations;
      _renderCombos();
    } else {
      status.style.display = '';
      status.className  = 'status-idle';
      status.innerHTML  = '<span class="idle-icon">⚽</span>No hay combinaciones guardadas. Pulsa Analizar.';
    }
  } catch (_) {
    // Si falla, el usuario puede pulsar Analizar manualmente
  }
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
  status.style.display = '';
  status.className = 'status-loading';
  status.textContent = 'Recopilando partidos y consultando IA...';
  stats.style.display = 'none';
  document.getElementById('sort-bar').style.display = 'none';
  results.innerHTML = '';
  _currentCombos = [];
  _currentSort   = 'score';
  document.getElementById('sort-score').classList.add('active');
  document.getElementById('sort-date').classList.remove('active');

  try {
    const res = await fetch('/api/analyze');
    if (!res.ok) throw new Error((await res.json()).detail || 'Error desconocido');
    renderResults(await res.json());
  } catch (e) {
    status.className = 'status-error';
    status.textContent = `${e.message}`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">▶</span> Analizar ahora';
  }
}

function renderResults(data) {
  const status  = document.getElementById('status-msg');
  const stats   = document.getElementById('stats');
  const sortBar = document.getElementById('sort-bar');

  stats.style.display = 'grid';
  countUp(document.getElementById('stat-found'),    data.total_matches_found);
  countUp(document.getElementById('stat-filtered'), data.matches_filtered,    700);
  countUp(document.getElementById('stat-combos'),   data.combinations_generated, 1100);

  if (!data.top_combinations?.length) {
    status.style.display = '';
    status.className = 'status-idle';
    status.innerHTML = '<span class="idle-icon">⚽</span>No se encontraron combinaciones en el rango 1.4–1.8.';
    sortBar.style.display = 'none';
    return;
  }

  status.style.display = 'none';
  sortBar.style.display = 'flex';

  _currentCombos = data.top_combinations;
  _renderCombos();
}

function buildCard(item, rank) {
  const { combination, score, recommendation } = item;
  const { match_a, match_b, combined_odds } = combination;
  const level = score >= 7 ? 'high' : score >= 5 ? 'med' : 'low';

  const timeA = fmtTime(match_a.commence_time);
  const timeB = fmtTime(match_b.commence_time);

  const card = document.createElement('div');
  card.className = 'combo-card';
  card.innerHTML = `
    <div class="combo-header">
      <span class="combo-rank"># ${rank}<span class="rank-sep">•</span>COMBINADA</span>
    </div>
    <div class="card-body">

      <div class="card-left">
        <div class="match-block">
          <span class="match-league">${match_a.league}</span>
          <span class="match-teams">${match_a.home_team} vs ${match_a.away_team}</span>
        </div>
        <div class="match-separator"></div>
        <div class="match-block">
          <span class="match-league">${match_b.league}</span>
          <span class="match-teams">${match_b.home_team} vs ${match_b.away_team}</span>
        </div>
      </div>

      <div class="card-center">
        <img src="/static/assets/logo_cartas.png" class="card-logo" alt="GolSignal" />
      </div>

      <div class="card-right">
        <div class="match-right-top">
          <div class="match-odds-info">
            <span class="odds-label">Cuota</span>
            <span class="odds-value">Local: ${match_a.odds.home}</span>
            <span class="match-time">${timeA}</span>
          </div>
          <div class="score-col">
            <div class="score-circle ${level}">${score}</div>
            <div class="rec-badge ${level}">${recommendation}</div>
          </div>
        </div>
        <div class="match-right-bottom">
          <span class="odds-value">Cuota Local: ${match_b.odds.home}</span>
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
    timeZone: 'UTC',
  }) + ' UTC';
}
