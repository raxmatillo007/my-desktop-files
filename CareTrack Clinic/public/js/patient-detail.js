/**
 * public/js/patient-detail.js — Patient detail page logic.
 * Shows patient info, assigned doctor, and diagnoses for that patient.
 * Add/Edit diagnosis for admin and clinician. Delete for admin only.
 */

let patientId  = null;
let editingDxId = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  // Only admin and clinician may view detail page
  if (getRole() === 'patient') {
    window.location.href = '/my-profile.html';
    return;
  }

  document.getElementById('navbar').innerHTML = renderNav('patients');

  patientId = new URLSearchParams(location.search).get('id');
  if (!patientId) {
    document.getElementById('patientInfo').innerHTML = '<div class="empty">Bemor ID topilmadi</div>';
    return;
  }

  // Hide add-diagnosis button for clinician (still shown for admin)
  if (getRole() !== 'admin' && getRole() !== 'clinician') {
    const btn = document.getElementById('btnAddDx');
    if (btn) btn.style.display = 'none';
  }

  await Promise.all([loadPatient(), loadDiagnoses(), loadDoctorsSelect()]);
});

async function loadPatient() {
  try {
    const res = await apiFetch(`/api/patients/${patientId}`);
    if (!res) return;
    const p = await res.json();
    if (!res.ok) {
      document.getElementById('patientInfo').innerHTML = `<div class="empty">${esc(p.error)}</div>`;
      return;
    }
    renderPatientInfo(p);
    renderDoctorInfo(p);
  } catch (e) {
    console.error(e);
  }
}

function renderPatientInfo(p) {
  document.title = `${p.full_name} — CareTrack Clinic`;
  document.getElementById('patientInfo').innerHTML = `
    <div class="info-row"><span class="info-label">To'liq ism:</span>     <span class="info-value">${esc(p.full_name)}</span></div>
    <div class="info-row"><span class="info-label">Tug'ilgan sana:</span>  <span class="info-value">${formatDate(p.date_of_birth)}</span></div>
    <div class="info-row"><span class="info-label">Jinsi:</span>           <span class="info-value">${genderLabel(p.gender)}</span></div>
    <div class="info-row"><span class="info-label">Telefon:</span>         <span class="info-value">${esc(p.phone || '—')}</span></div>
    <div class="info-row"><span class="info-label">Manzil:</span>          <span class="info-value">${esc(p.address || '—')}</span></div>
  `;
}

function renderDoctorInfo(p) {
  if (!p.doctor_name) {
    document.getElementById('doctorInfo').innerHTML = '<div class="empty">Shifokor biriktirilmagan</div>';
    return;
  }
  document.getElementById('doctorInfo').innerHTML = `
    <div class="info-row"><span class="info-label">Ism:</span>         <span class="info-value">${esc(p.doctor_name)}</span></div>
    <div class="info-row"><span class="info-label">Mutaxassislik:</span><span class="info-value">${esc(p.doctor_specialty || '—')}</span></div>
    <div class="info-row"><span class="info-label">Bo'lim:</span>       <span class="info-value">${esc(p.doctor_department || '—')}</span></div>
    <div class="info-row"><span class="info-label">Telefon:</span>      <span class="info-value">${esc(p.doctor_phone || '—')}</span></div>
  `;
}

async function loadDiagnoses() {
  try {
    const res = await apiFetch(`/api/diagnoses/patient/${patientId}`);
    if (!res) return;
    const list = await res.json();
    renderDxTable(list);
  } catch (e) {
    console.error(e);
  }
}

function renderDxTable(list) {
  const role  = getRole();
  const tbody = document.getElementById('dxTbody');
  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Tashxislar yo\'q</td></tr>';
    return;
  }
  tbody.innerHTML = list.map(dx => `
    <tr class="row-${dx.severity}">
      <td>${esc(dx.icd_code || '—')}</td>
      <td>${esc(dx.title || '—')}</td>
      <td>${severityBadge(dx.severity)}</td>
      <td>${esc(dx.doctor_name || '—')}</td>
      <td>${formatDate(dx.diagnosed_at)}</td>
      <td class="actions">
        ${role !== 'patient' ? `<button class="btn btn-sm btn-secondary" onclick="openEditDx(${dx.id})">Tahrirlash</button>` : ''}
        ${role === 'admin'   ? `<button class="btn btn-sm btn-danger"    onclick="deleteDx(${dx.id})">O'chirish</button>` : ''}
      </td>
    </tr>
  `).join('');

  // Store list for edit lookups
  window._dxList = list;
}

async function loadDoctorsSelect() {
  try {
    const res = await apiFetch('/api/doctors');
    if (!res) return;
    const doctors = await res.json();
    const sel = document.getElementById('dxDoctor');
    doctors.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d.id;
      opt.textContent = `${d.full_name}${d.specialty ? ' — ' + d.specialty : ''}`;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error(e);
  }
}

function openAddDx() {
  editingDxId = null;
  document.getElementById('dxModalTitle').textContent = "Tashxis qo'shish";
  clearDxForm();
  openDxModal();
}

function openEditDx(id) {
  editingDxId = id;
  document.getElementById('dxModalTitle').textContent = 'Tashxisni tahrirlash';
  const dx = (window._dxList || []).find(x => x.id === id);
  if (!dx) return;
  document.getElementById('dxIcd').value      = dx.icd_code    || '';
  document.getElementById('dxTitle').value    = dx.title       || '';
  document.getElementById('dxDesc').value     = dx.description || '';
  document.getElementById('dxSeverity').value = dx.severity    || '';
  document.getElementById('dxDoctor').value   = dx.doctor_id   || '';
  openDxModal();
}

async function deleteDx(id) {
  if (!confirm("Tashxisni o'chirishni tasdiqlaysizmi?")) return;
  try {
    const res = await apiFetch(`/api/diagnoses/${id}`, { method: 'DELETE' });
    if (!res) return;
    if (res.ok) {
      await loadDiagnoses();
    } else {
      const d = await res.json();
      alert(d.error || "O'chirishda xato");
    }
  } catch (e) {
    alert(e.message);
  }
}

document.getElementById('dxForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('dxFormError');
  errEl.style.display = 'none';

  const body = {
    icd_code:    document.getElementById('dxIcd').value.trim()      || null,
    title:       document.getElementById('dxTitle').value.trim()    || null,
    description: document.getElementById('dxDesc').value.trim()     || null,
    severity:    document.getElementById('dxSeverity').value,
    patient_id:  Number(patientId),
    doctor_id:   document.getElementById('dxDoctor').value          || null,
  };

  if (!body.severity) {
    errEl.textContent = "Og'irlik darajasi majburiy";
    errEl.style.display = 'block';
    return;
  }

  try {
    const url    = editingDxId ? `/api/diagnoses/${editingDxId}` : '/api/diagnoses';
    const method = editingDxId ? 'PUT' : 'POST';
    const res = await apiFetch(url, { method, body });
    if (!res) return;
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.error || 'Xato';
      errEl.style.display = 'block';
      return;
    }
    closeDxModal();
    await loadDiagnoses();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
});

function clearDxForm() {
  ['dxIcd','dxTitle','dxDesc','dxSeverity','dxDoctor'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('dxFormError').style.display = 'none';
}

function openDxModal()  { document.getElementById('dxModal').classList.add('open'); }
function closeDxModal() { document.getElementById('dxModal').classList.remove('open'); }

document.getElementById('dxModal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeDxModal();
});

function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
