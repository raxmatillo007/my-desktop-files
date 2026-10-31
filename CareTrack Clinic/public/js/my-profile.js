document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  if (getRole() !== 'patient') {
    window.location.href = '/dashboard.html';
    return;
  }

  document.getElementById('navbar').innerHTML = renderNav('profile');

  await Promise.all([loadProfile(), loadMyDiagnoses()]);
});

async function loadProfile() {
  try {
    const res = await apiFetch('/api/patients/my');
    if (!res) return;
    const p = await res.json();
    if (!res.ok) {
      const msg = esc(p.error || 'Profil yuklanmadi');
      document.getElementById('profileInfo').innerHTML = `<div class="empty">${msg}</div>`;
      document.getElementById('doctorInfo').innerHTML  = `<div class="empty">—</div>`;
      return;
    }
    const bannerEl = document.getElementById('bannerName');
    if (bannerEl) bannerEl.textContent = p.full_name || getUsername() || 'Bemor';
    renderProfile(p);
    renderDoctor(p);
  } catch (e) {
    document.getElementById('profileInfo').innerHTML = `<div class="empty">Xato yuz berdi</div>`;
    document.getElementById('doctorInfo').innerHTML  = `<div class="empty">—</div>`;
    console.error(e);
  }
}

function renderProfile(p) {
  document.getElementById('profileInfo').innerHTML = `
    <div class="info-row"><span class="info-label">To'liq ism:</span>     <span class="info-value">${esc(p.full_name)}</span></div>
    <div class="info-row"><span class="info-label">Tug'ilgan sana:</span>  <span class="info-value">${formatDate(p.date_of_birth)}</span></div>
    <div class="info-row"><span class="info-label">Jinsi:</span>           <span class="info-value">${genderLabel(p.gender)}</span></div>
    <div class="info-row"><span class="info-label">Telefon:</span>         <span class="info-value">${esc(p.phone || '—')}</span></div>
    <div class="info-row"><span class="info-label">Manzil:</span>          <span class="info-value">${esc(p.address || '—')}</span></div>
  `;
}

function renderDoctor(p) {
  if (!p.doctor_name) {
    document.getElementById('doctorInfo').innerHTML = '<div class="empty">Shifokor biriktirilmagan</div>';
    return;
  }
  document.getElementById('doctorInfo').innerHTML = `
    <div class="info-row"><span class="info-label">Ism:</span>          <span class="info-value">${esc(p.doctor_name)}</span></div>
    <div class="info-row"><span class="info-label">Mutaxassislik:</span> <span class="info-value">${esc(p.doctor_specialty || '—')}</span></div>
    <div class="info-row"><span class="info-label">Bo'lim:</span>        <span class="info-value">${esc(p.doctor_department || '—')}</span></div>
    <div class="info-row"><span class="info-label">Telefon:</span>       <span class="info-value">${esc(p.doctor_phone || '—')}</span></div>
  `;
}

async function loadMyDiagnoses() {
  try {
    const res = await apiFetch('/api/diagnoses/my');
    if (!res) return;
    if (!res.ok) {
      document.getElementById('dxTbody').innerHTML =
        '<tr><td colspan="5" class="empty">Tashxislar yuklanmadi</td></tr>';
      return;
    }
    const list = await res.json();
    renderDxTable(Array.isArray(list) ? list : []);
  } catch (e) {
    document.getElementById('dxTbody').innerHTML =
      '<tr><td colspan="5" class="empty">Xato yuz berdi</td></tr>';
    console.error(e);
  }
}

function renderDxTable(list) {
  const tbody = document.getElementById('dxTbody');
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">Tashxislar tarixi yo\'q</td></tr>';
    return;
  }
  tbody.innerHTML = list.map(dx => `
    <tr class="row-${dx.severity}">
      <td>${esc(dx.icd_code || '—')}</td>
      <td>${esc(dx.title    || '—')}</td>
      <td>${severityBadge(dx.severity)}</td>
      <td>${esc(dx.doctor_name || '—')}</td>
      <td>${formatDate(dx.diagnosed_at)}</td>
    </tr>
  `).join('');
}

function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
