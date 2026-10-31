let allDiagnoses = [];
let editingId    = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  const role = getRole();
  document.getElementById('navbar').innerHTML = renderNav('diagnoses');

  if (role === 'patient') {
    document.querySelector('.page-header button').style.display = 'none';
    document.querySelector('.filter-bar').style.display = 'none';
    document.querySelector('.page-title').textContent = 'Mening tashxislarim';
    document.querySelector('thead tr').innerHTML = `
      <th>#</th><th>ICD Kod</th><th>Sarlavha</th><th>Og'irlik</th><th>Shifokor</th><th>Sana</th>
    `;
    document.getElementById('dxTbody').innerHTML =
      '<tr><td colspan="6" class="empty">Yuklanmoqda...</td></tr>';
    await loadPatientDiagnoses();
    return;
  }

  await Promise.all([loadDiagnoses(), loadSelects()]);
  document.getElementById('searchQ').addEventListener('input', renderTable);
  document.getElementById('filterSeverity').addEventListener('change', renderTable);
});

async function loadPatientDiagnoses() {
  try {
    const res = await apiFetch('/api/diagnoses/my');
    if (!res) return;
    if (!res.ok) {
      document.getElementById('dxTbody').innerHTML =
        '<tr><td colspan="6" class="empty">Tashxislar yuklanmadi</td></tr>';
      return;
    }
    const list = await res.json();
    const tbody = document.getElementById('dxTbody');
    const data = Array.isArray(list) ? list : [];
    if (!data.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty">Tashxislar tarixi yo\'q</td></tr>';
      return;
    }
    tbody.innerHTML = data.map((dx, i) => `
      <tr class="row-${dx.severity}">
        <td>${i + 1}</td>
        <td>${esc(dx.icd_code || '—')}</td>
        <td>${esc(dx.title    || '—')}</td>
        <td>${severityBadge(dx.severity)}</td>
        <td>${esc(dx.doctor_name || '—')}</td>
        <td>${formatDate(dx.diagnosed_at)}</td>
      </tr>
    `).join('');
  } catch (e) {
    document.getElementById('dxTbody').innerHTML =
      '<tr><td colspan="6" class="empty">Xato yuz berdi</td></tr>';
    console.error(e);
  }
}

async function loadDiagnoses() {
  try {
    const res = await apiFetch('/api/diagnoses');
    if (!res) return;
    allDiagnoses = await res.json();
    renderTable();
  } catch (e) {
    console.error(e);
  }
}

async function loadSelects() {
  try {
    const [resP, resD] = await Promise.all([
      apiFetch('/api/patients'),
      apiFetch('/api/doctors'),
    ]);
    if (resP) {
      const patients = await resP.json();
      const selP = document.getElementById('fPatient');
      patients.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = p.full_name;
        selP.appendChild(opt);
      });
    }
    if (resD) {
      const doctors = await resD.json();
      const selD = document.getElementById('fDoctor');
      doctors.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.id;
        opt.textContent = `${d.full_name}${d.specialty ? ' — ' + d.specialty : ''}`;
        selD.appendChild(opt);
      });
    }
  } catch (e) {
    console.error(e);
  }
}

function renderTable() {
  const q        = document.getElementById('searchQ').value.trim().toLowerCase();
  const severity = document.getElementById('filterSeverity').value;
  const role     = getRole();

  let filtered = allDiagnoses;
  if (q)        filtered = filtered.filter(dx =>
    (dx.patient_name || '').toLowerCase().includes(q) ||
    (dx.icd_code     || '').toLowerCase().includes(q)
  );
  if (severity) filtered = filtered.filter(dx => dx.severity === severity);

  const tbody = document.getElementById('dxTbody');
  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty">Tashxislar topilmadi</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((dx, i) => `
    <tr class="row-${dx.severity}">
      <td>${i + 1}</td>
      <td>${esc(dx.icd_code || '—')}</td>
      <td>${esc(dx.title    || '—')}</td>
      <td>${severityBadge(dx.severity)}</td>
      <td>${esc(dx.patient_name || '—')}</td>
      <td>${esc(dx.doctor_name  || '—')}</td>
      <td>${formatDate(dx.diagnosed_at)}</td>
      <td class="actions">
        <button class="btn btn-sm btn-secondary" onclick="openEdit(${dx.id})">Tahrirlash</button>
        ${role === 'admin' ? `<button class="btn btn-sm btn-danger" onclick="deleteDx(${dx.id})">O'chirish</button>` : ''}
      </td>
    </tr>
  `).join('');
}

function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function openAdd() {
  editingId = null;
  document.getElementById('modalTitle').textContent = "Tashxis qo'shish";
  clearForm();
  openModal();
}

function openEdit(id) {
  editingId = id;
  document.getElementById('modalTitle').textContent = 'Tashxisni tahrirlash';
  const dx = allDiagnoses.find(x => x.id === id);
  if (!dx) return;
  document.getElementById('fIcd').value      = dx.icd_code    || '';
  document.getElementById('fTitle').value    = dx.title       || '';
  document.getElementById('fDesc').value     = dx.description || '';
  document.getElementById('fSeverity').value = dx.severity    || '';
  document.getElementById('fPatient').value  = dx.patient_id  || '';
  document.getElementById('fDoctor').value   = dx.doctor_id   || '';
  openModal();
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
  const errEl = document.getElementById('formError');
  errEl.style.display = 'none';

  const body = {
    icd_code:    document.getElementById('fIcd').value.trim()      || null,
    title:       document.getElementById('fTitle').value.trim()    || null,
    description: document.getElementById('fDesc').value.trim()     || null,
    severity:    document.getElementById('fSeverity').value,
    patient_id:  document.getElementById('fPatient').value         || null,
    doctor_id:   document.getElementById('fDoctor').value          || null,
  };

  if (!body.severity) {
    errEl.textContent = "Og'irlik darajasi majburiy";
    errEl.style.display = 'block';
    return;
  }
  if (!body.patient_id) {
    errEl.textContent = 'Bemor tanlanishi shart';
    errEl.style.display = 'block';
    return;
  }

  try {
    const url    = editingId ? `/api/diagnoses/${editingId}` : '/api/diagnoses';
    const method = editingId ? 'PUT' : 'POST';
    const res = await apiFetch(url, { method, body });
    if (!res) return;
    const data = await res.json();
    if (!res.ok) {
      errEl.textContent = data.error || 'Xato';
      errEl.style.display = 'block';
      return;
    }
    closeModal();
    await loadDiagnoses();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
});

function clearForm() {
  ['fIcd','fTitle','fDesc','fSeverity','fPatient','fDoctor'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('formError').style.display = 'none';
}

function openModal()  { document.getElementById('modal').classList.add('open'); }
function closeModal() { document.getElementById('modal').classList.remove('open'); }

document.getElementById('modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});
