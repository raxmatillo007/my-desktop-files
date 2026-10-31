const API_BASE = '';

function getToken()    { return localStorage.getItem('token'); }
function getRole()     { return localStorage.getItem('role'); }
function getUsername() { return localStorage.getItem('username'); }

function checkAuth() {
  if (!getToken()) { window.location.href = '/login.html'; return false; }
  return true;
}

async function apiFetch(url, options = {}) {
  const config = {
    method: (options.method || 'GET').toUpperCase(),
    url: API_BASE + url,
    headers: { 'Authorization': 'Bearer ' + getToken() },
  };
  if (options.body) {
    config.data = options.body;
    config.headers['Content-Type'] = 'application/json';
  }
  try {
    const r = await axios(config);
    return { ok: true, status: r.status, json: () => Promise.resolve(r.data) };
  } catch (err) {
    const status = err.response?.status;
    if (status === 401) { logout(); return null; }
    if (status === 403) { alert('Kirish taqiqlandi'); throw new Error('403'); }
    return {
      ok: false,
      status: status || 500,
      json: () => Promise.resolve(err.response?.data || { error: 'Server xatosi' }),
    };
  }
}

function logout() { localStorage.clear(); window.location.href = '/login.html'; }

function renderNav(active) {
  const role     = getRole();
  const username = getUsername();
  let links = '';
  if (role === 'admin' || role === 'clinician') {
    links = `
      <a href="/dashboard.html"  class="${active === 'dashboard'  ? 'active' : ''}">Boshqaruv</a>
      <a href="/doctors.html"    class="${active === 'doctors'    ? 'active' : ''}">Shifokorlar</a>
      <a href="/patients.html"   class="${active === 'patients'   ? 'active' : ''}">Bemorlar</a>
      <a href="/diagnoses.html"  class="${active === 'diagnoses'  ? 'active' : ''}">Tashxislar</a>
    `;
  } else {
    links = `
      <a href="/my-profile.html" class="${active === 'profile'   ? 'active' : ''}">Profilim</a>
      <a href="/doctors.html"    class="${active === 'doctors'   ? 'active' : ''}">Shifokorlar</a>
      <a href="/patients.html"   class="${active === 'patients'  ? 'active' : ''}">Bemorlar</a>
      <a href="/diagnoses.html"  class="${active === 'diagnoses' ? 'active' : ''}">Tashxislarim</a>
    `;
  }
  return `<nav class="navbar">
    <div class="nav-brand">
      <svg width="26" height="26" viewBox="0 0 40 40">
        <rect width="40" height="40" rx="8" fill="#0891b2"/>
        <path d="M20 8v24M8 20h24" stroke="white" stroke-width="5" stroke-linecap="round"/>
      </svg>
      CareTrack
    </div>
    <div class="nav-links">${links}</div>
    <div class="nav-right">
      <span class="nav-user">${username || ''}</span>
      <button class="btn btn-sm btn-outline-white" onclick="logout()">Chiqish</button>
    </div>
  </nav>`;
}

function severityBadge(s) {
  const map = { mild: 'Yengil', moderate: "O'rta", severe: "Og'ir" };
  return `<span class="badge badge-${s}">${map[s] || s}</span>`;
}

function formatDate(val) {
  if (!val) return '—';
  return new Date(val).toLocaleDateString('uz-UZ', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function genderLabel(g) {
  const map = { Male: 'Erkak', Female: 'Ayol', Other: 'Boshqa' };
  return map[g] || g || '—';
}
