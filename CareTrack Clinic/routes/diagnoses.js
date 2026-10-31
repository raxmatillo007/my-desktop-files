const express = require('express');
const { authenticateToken, authorizeRole } = require('../middleware/auth');

module.exports = function (db) {
  const router = express.Router();

  router.get('/my', authenticateToken, authorizeRole('patient'), async (req, res) => {
    try {
      const patientId = req.user.patient_id;
      if (!patientId) return res.status(404).json({ error: 'Bemor profili topilmadi' });
      const [rows] = await db.query(
        `SELECT dx.*, d.full_name AS doctor_name, d.specialty AS doctor_specialty
         FROM diagnoses dx
         LEFT JOIN doctors d ON dx.doctor_id = d.id
         WHERE dx.patient_id = ?
         ORDER BY dx.diagnosed_at DESC`,
        [patientId]
      );
      res.json(rows);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.get('/patient/:patient_id', authenticateToken, async (req, res) => {
    try {
      const [rows] = await db.query(
        `SELECT dx.*, d.full_name AS doctor_name, d.specialty AS doctor_specialty
         FROM diagnoses dx
         LEFT JOIN doctors d ON dx.doctor_id = d.id
         WHERE dx.patient_id = ?
         ORDER BY dx.diagnosed_at DESC`,
        [req.params.patient_id]
      );
      res.json(rows);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.get('/', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { severity, q } = req.query;
      let sql = `SELECT dx.*,
                        p.full_name AS patient_name,
                        d.full_name AS doctor_name
                 FROM diagnoses dx
                 LEFT JOIN patients p ON dx.patient_id = p.id
                 LEFT JOIN doctors  d ON dx.doctor_id  = d.id
                 WHERE 1=1`;
      const params = [];
      if (severity) { sql += ' AND dx.severity = ?'; params.push(severity); }
      if (q)        { sql += ' AND (p.full_name LIKE ? OR dx.icd_code LIKE ?)'; params.push(`%${q}%`, `%${q}%`); }
      sql += ' ORDER BY dx.diagnosed_at DESC, dx.id DESC';
      const [rows] = await db.query(sql, params);
      res.json(rows);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.post('/', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { icd_code, title, description, severity, patient_id, doctor_id } = req.body;
      if (!patient_id) return res.status(400).json({ error: 'Bemor tanlanishi shart' });
      if (!severity)   return res.status(400).json({ error: "Og'irlik darajasi majburiy" });
      const [result] = await db.query(
        'INSERT INTO diagnoses (icd_code, title, description, severity, patient_id, doctor_id) VALUES (?,?,?,?,?,?)',
        [icd_code || null, title || null, description || null, severity, patient_id, doctor_id || null]
      );
      const [rows] = await db.query(
        `SELECT dx.*, p.full_name AS patient_name, d.full_name AS doctor_name
         FROM diagnoses dx
         LEFT JOIN patients p ON dx.patient_id = p.id
         LEFT JOIN doctors  d ON dx.doctor_id  = d.id
         WHERE dx.id = ?`,
        [result.insertId]
      );
      res.status(201).json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.put('/:id', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { icd_code, title, description, severity, patient_id, doctor_id } = req.body;
      if (!severity) return res.status(400).json({ error: "Og'irlik darajasi majburiy" });
      await db.query(
        'UPDATE diagnoses SET icd_code=?, title=?, description=?, severity=?, patient_id=?, doctor_id=? WHERE id=?',
        [icd_code || null, title || null, description || null, severity, patient_id || null, doctor_id || null, req.params.id]
      );
      const [rows] = await db.query(
        `SELECT dx.*, p.full_name AS patient_name, d.full_name AS doctor_name
         FROM diagnoses dx
         LEFT JOIN patients p ON dx.patient_id = p.id
         LEFT JOIN doctors  d ON dx.doctor_id  = d.id
         WHERE dx.id = ?`,
        [req.params.id]
      );
      if (!rows.length) return res.status(404).json({ error: 'Tashxis topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.delete('/:id', authenticateToken, authorizeRole('admin'), async (req, res) => {
    try {
      await db.query('DELETE FROM diagnoses WHERE id = ?', [req.params.id]);
      res.json({ ok: true });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  return router;
};
