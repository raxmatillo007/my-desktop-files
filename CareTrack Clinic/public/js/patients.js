let allPatients = [];
let editingId   = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  const role = getRole();
  document.getElementById('navbar').innerHTML = renderNav('patients');

  if (role === 'patient') {
    document.getElementById('btnAdd').style.display = 'none';
    document.querySelector('.filter-bar').style.display = 'none';
    document.getElementById('patientsTbody').innerHTML =
      '<tr><td colspan="7" class="empty">Yuklanmoqda...</td></tr>';
    await loadMyRecord();
    return;
  }

  await Promise.all([loadPatients(), loadDoctorsSelect()]);
  document.getElementById('searchName').addEventListener('input', renderTable);
});

async function loadMyRecord() {
  try {
    const res = await apiFetch('/api/patients/my');
    if (!res) return;
    if (!res.ok) {
      document.getElementById('patientsTbody').innerHTML =
        '<tr><td colspan="7" class="empty">Ma\'lumot topilmadi</td></tr>';
      return;
    }
    const p = await res.json();
    document.getElementById('patientsTbody').innerHTML = `
      <tr>
        <td>1</td>
        <td><a href="/my-profile.html">${esc(p.full_name)}</a></td>
        <td>${formatDate(p.date_of_birth)}</td>
        <td>${genderLabel(p.gender)}</td>
        <td>${esc(p.phone || '—')}</td>
        <td>${esc(p.doctor_name || '—')}</td>
        <td class="actions">
          <a href="/my-profile.html" class="btn btn-sm btn-view">Ko'rish</a>
        </td>
      </tr>
    `;
  } catch (e) {
    document.getElementById('patientsTbody').innerHTML =
      '<tr><td colspan="7" class="empty">Xato yuz berdi</td></tr>';
    console.error(e);
  }
}

async function loadPatients() {
  try {
    const res = await apiFetch('/api/patients');
    if (!res) return;
    allPatients = await res.json();
    renderTable();
  } catch (e) {
    console.error(e);
  }
}

async function loadDoctorsSelect() {
  try {
    const res = await apiFetch('/api/doctors');
    if (!res) return;
    const doctors = await res.json();
    const sel = document.getElementById('fDoctor');
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

function renderTable() {
  const name = document.getElementById('searchName').value.trim().toLowerCase();
  const role = getRole();

  let filtered = allPatients;
  if (name) filtered = filtered.filter(p => p.full_name.toLowerCase().includes(name));

  const tbody = document.getElementById('patientsTbody');
  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Bemorlar topilmadi</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((p, i) => `
    <tr>
      <td>${i + 1}</td>
      <td><a href="/patient-detail.html?id=${p.id}">${esc(p.full_name)}</a></td>
      <td>${formatDate(p.date_of_birth)}</td>
      <td>${genderLabel(p.gender)}</td>
      <td>${esc(p.phone || '—')}</td>
      <td>${esc(p.doctor_name || '—')}</td>
      <td class="actions">
        <a href="/patient-detail.html?id=${p.id}" class="btn btn-sm btn-view">Ko'rish</a>
        <button class="btn btn-sm btn-secondary" onclick="openEdit(${p.id})">Tahrirlash</button>
        ${role === 'admin' ? `<button class="btn btn-sm btn-danger" onclick="deletePatient(${p.id})">O'chirish</button>` : ''}
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
  document.getElementById('modalTitle').textContent = "Bemor qo'shish";
  clearForm();
  openModal();
}

function openEdit(id) {
  editingId = id;
  document.getElementById('modalTitle').textContent = 'Bemorni tahrirlash';
  const p = allPatients.find(x => x.id === id);
  if (!p) return;
  document.getElementById('fName').value    = p.full_name     || '';
  document.getElementById('fDob').value     = p.date_of_birth ? p.date_of_birth.slice(0, 10) : '';
  document.getElementById('fGender').value  = p.gender        || '';
  document.getElementById('fAddress').value = p.address       || '';
  document.getElementById('fPhone').value   = p.phone         || '';
  document.getElementById('fDoctor').value  = p.doctor_id     || '';
  openModal();
}

async function deletePatient(id) {
  if (!confirm("Bemorni o'chirishni tasdiqlaysizmi?")) return;
  try {
    const res = await apiFetch(`/api/patients/${id}`, { method: 'DELETE' });
    if (!res) return;
    if (res.ok) {
      await loadPatients();
    } else {
      const d = await res.json();
      alert(d.error || "O'chirishda xato");
    }
  } catch (e) {
    alert(e.message);
  }
}

document.getElementById('patientForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('formError');
  errEl.style.display = 'none';

  const body = {
    full_name:     document.getElementById('fName').value.trim(),
    date_of_birth: document.getElementById('fDob').value     || null,
    gender:        document.getElementById('fGender').value  || null,
    address:       document.getElementById('fAddress').value.trim() || null,
    phone:         document.getElementById('fPhone').value.trim()   || null,
    doctor_id:     document.getElementById('fDoctor').value  || null,
  };

  if (!body.full_name) {
    errEl.textContent = "To'liq ism majburiy";
    errEl.style.display = 'block';
    return;
  }

  try {
    const url    = editingId ? `/api/patients/${editingId}` : '/api/patients';
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
    await loadPatients();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
});

function clearForm() {
  ['fName','fDob','fGender','fAddress','fPhone','fDoctor'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('formError').style.display = 'none';
}

function openModal()  { document.getElementById('modal').classList.add('open'); }
function closeModal() { document.getElementById('modal').classList.remove('open'); }

document.getElementById('modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});
