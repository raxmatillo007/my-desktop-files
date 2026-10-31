document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  if (getRole() === 'patient') {
    window.location.href = '/my-profile.html';
    return;
  }

  document.getElementById('navbar').innerHTML = renderNav('dashboard');

  try {
    const res = await apiFetch('/api/dashboard/stats');
    if (!res) return;
    const data = await res.json();

    if (!res.ok) {
      console.error('Stats xatosi:', data.error);
      return;
    }

    document.getElementById('statDoctors').textContent   = data.total_doctors   ?? 0;
    document.getElementById('statPatients').textContent  = data.total_patients  ?? 0;
    document.getElementById('statDiagnoses').textContent = data.total_diagnoses ?? 0;

    const sb = data.severity_breakdown || {};
    const gb = data.gender_breakdown   || {};
    const pd = data.patients_per_doctor || [];

    new Chart(document.getElementById('severityChart'), {
      type: 'doughnut',
      data: {
        labels: ['Yengil', "O'rta", "Og'ir"],
        datasets: [{
          data: [sb.mild || 0, sb.moderate || 0, sb.severe || 0],
          backgroundColor: ['#16a34a', '#ca8a04', '#dc2626'],
          borderWidth: 2,
          borderColor: '#fff',
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', labels: { font: { size: 12 } } } },
        cutout: '60%',
      },
    });

    new Chart(document.getElementById('genderChart'), {
      type: 'doughnut',
      data: {
        labels: ['Erkak', 'Ayol', 'Boshqa'],
        datasets: [{
          data: [gb.Male || 0, gb.Female || 0, gb.Other || 0],
          backgroundColor: ['#2563eb', '#ec4899', '#64748b'],
          borderWidth: 2,
          borderColor: '#fff',
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom', labels: { font: { size: 12 } } } },
        cutout: '60%',
      },
    });

    new Chart(document.getElementById('doctorChart'), {
      type: 'bar',
      data: {
        labels: pd.map(d => d.full_name),
        datasets: [{
          label: 'Bemorlar soni',
          data: pd.map(d => d.cnt),
          backgroundColor: '#2563eb',
          borderRadius: 4,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } },
          y: { ticks: { font: { size: 11 } } },
        },
      },
    });

  } catch (err) {
    console.error(err);
  }
});
