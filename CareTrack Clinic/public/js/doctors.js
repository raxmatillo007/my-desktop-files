let allDoctors = [];
let editingId  = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  document.getElementById('navbar').innerHTML = renderNav('doctors');

  const role = getRole();

  if (role === 'patient') {
    document.getElementById('btnAdd').style.display = 'none';
  }

  await loadDoctors();

  document.getElementById('searchName').addEventListener('input', renderTable);
  document.getElementById('filterSpecialty').addEventListener('change', renderTable);
});

async function loadDoctors() {
  try {
    const res = await apiFetch('/api/doctors');
    if (!res) return;
    allDoctors = await res.json();
    buildSpecialtyFilter();
    renderTable();
  } catch (e) {
    console.error(e);
  }
}

function buildSpecialtyFilter() {
  const sel = document.getElementById('filterSpecialty');
  const current = sel.value;
  // Keep first default option
  while (sel.options.length > 1) sel.remove(1);

  const specialties = [...new Set(allDoctors.map(d => d.specialty).filter(Boolean))].sort();
  specialties.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s;
    opt.textContent = s;
    sel.appendChild(opt);
  });
  sel.value = current;
}

function renderTable() {
  const name      = document.getElementById('searchName').value.trim().toLowerCase();
  const specialty = document.getElementById('filterSpecialty').value;
  const role      = getRole();

  let filtered = allDoctors;
  if (name)      filtered = filtered.filter(d => d.full_name.toLowerCase().includes(name));
  if (specialty) filtered = filtered.filter(d => d.specialty === specialty);

  const tbody = document.getElementById('doctorsTbody');
  if (!filtered.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Shifokorlar topilmadi</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map((d, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${esc(d.full_name)}</td>
      <td>${esc(d.specialty || '—')}</td>
      <td>${esc(d.department || '—')}</td>
      <td>${esc(d.phone || '—')}</td>
      <td>${esc(d.email || '—')}</td>
      <td class="actions">
        <button class="btn btn-sm btn-view" onclick="openView(${d.id})">Ko'rish</button>
        ${role !== 'patient' ? `<button class="btn btn-sm btn-secondary" onclick="openEdit(${d.id})">Tahrirlash</button>` : ''}
        ${role === 'admin'   ? `<button class="btn btn-sm btn-danger"    onclick="deleteDr(${d.id})">O'chirish</button>` : ''}
      </td>
    </tr>
  `).join('');
}

function esc(str) {
  return String(str ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function openView(id) {
  const d = allDoctors.find(x => x.id === id);
  if (!d) return;
  document.getElementById('viewContent').innerHTML = `
    <div class="info-row"><span class="info-label">To'liq ism</span><span class="info-value">${esc(d.full_name)}</span></div>
    <div class="info-row"><span class="info-label">Mutaxassislik</span><span class="info-value">${esc(d.specialty||'—')}</span></div>
    <div class="info-row"><span class="info-label">Bo'lim</span><span class="info-value">${esc(d.department||'—')}</span></div>
    <div class="info-row"><span class="info-label">Telefon</span><span class="info-value">${esc(d.phone||'—')}</span></div>
    <div class="info-row"><span class="info-label">Email</span><span class="info-value">${esc(d.email||'—')}</span></div>
  `;
  document.getElementById('viewModal').classList.add('open');
}
function closeViewModal() { document.getElementById('viewModal').classList.remove('open'); }

function openAdd() {
  editingId = null;
  document.getElementById('modalTitle').textContent = "Shifokor qo'shish";
  clearForm();
  openModal();
}

async function openEdit(id) {
  editingId = id;
  document.getElementById('modalTitle').textContent = 'Shifokorni tahrirlash';
  const doc = allDoctors.find(d => d.id === id);
  if (!doc) return;
  document.getElementById('fName').value       = doc.full_name   || '';
  document.getElementById('fSpecialty').value  = doc.specialty   || '';
  document.getElementById('fDepartment').value = doc.department  || '';
  document.getElementById('fPhone').value      = doc.phone       || '';
  document.getElementById('fEmail').value      = doc.email       || '';
  openModal();
}

async function deleteDr(id) {
  if (!confirm("Shifokorni o'chirishni tasdiqlaysizmi?")) return;
  try {
    const res = await apiFetch(`/api/doctors/${id}`, { method: 'DELETE' });
    if (!res) return;
    if (res.ok) {
      await loadDoctors();
    } else {
      const d = await res.json();
      alert(d.error || "O'chirishda xato");
    }
  } catch (e) {
    alert(e.message);
  }
}

document.getElementById('doctorForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('formError');
  errEl.style.display = 'none';

  const body = {
    full_name:  document.getElementById('fName').value.trim(),
    specialty:  document.getElementById('fSpecialty').value.trim(),
    department: document.getElementById('fDepartment').value.trim(),
    phone:      document.getElementById('fPhone').value.trim(),
    email:      document.getElementById('fEmail').value.trim(),
  };

  if (!body.full_name) {
    errEl.textContent = "To'liq ism majburiy";
    errEl.style.display = 'block';
    return;
  }

  try {
    const url    = editingId ? `/api/doctors/${editingId}` : '/api/doctors';
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
    await loadDoctors();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
});

function clearForm() {
  ['fName','fSpecialty','fDepartment','fPhone','fEmail'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('formError').style.display = 'none';
}

function openModal()  { document.getElementById('modal').classList.add('open'); }
function closeModal() { document.getElementById('modal').classList.remove('open'); }

document.getElementById('modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});
