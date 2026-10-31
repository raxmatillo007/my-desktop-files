const express = require('express');
const { authenticateToken, authorizeRole } = require('../middleware/auth');

module.exports = function (db) {
  const router = express.Router();

  router.get('/my', authenticateToken, authorizeRole('patient'), async (req, res) => {
    try {
      const patientId = req.user.patient_id;
      if (!patientId) return res.status(404).json({ error: 'Bemor profili topilmadi' });
      const [rows] = await db.query(
        `SELECT p.*,
                d.full_name  AS doctor_name,
                d.specialty  AS doctor_specialty,
                d.department AS doctor_department,
                d.phone      AS doctor_phone
         FROM patients p
         LEFT JOIN doctors d ON p.doctor_id = d.id
         WHERE p.id = ?`,
        [patientId]
      );
      if (!rows.length) return res.status(404).json({ error: 'Bemor topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.get('/', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { name } = req.query;
      let sql = `SELECT p.*, d.full_name AS doctor_name
                 FROM patients p
                 LEFT JOIN doctors d ON p.doctor_id = d.id
                 WHERE 1=1`;
      const params = [];
      if (name) { sql += ' AND p.full_name LIKE ?'; params.push(`%${name}%`); }
      sql += ' ORDER BY p.full_name';
      const [rows] = await db.query(sql, params);
      res.json(rows);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.get('/:id', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const [rows] = await db.query(
        `SELECT p.*,
                d.full_name  AS doctor_name,
                d.specialty  AS doctor_specialty,
                d.department AS doctor_department,
                d.phone      AS doctor_phone
         FROM patients p
         LEFT JOIN doctors d ON p.doctor_id = d.id
         WHERE p.id = ?`,
        [req.params.id]
      );
      if (!rows.length) return res.status(404).json({ error: 'Bemor topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.post('/', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { full_name, date_of_birth, gender, address, phone, doctor_id } = req.body;
      if (!full_name) return res.status(400).json({ error: "To'liq ism majburiy" });
      const [result] = await db.query(
        'INSERT INTO patients (full_name, date_of_birth, gender, address, phone, doctor_id) VALUES (?,?,?,?,?,?)',
        [full_name, date_of_birth || null, gender || null, address || null, phone || null, doctor_id || null]
      );
      const [rows] = await db.query('SELECT * FROM patients WHERE id = ?', [result.insertId]);
      res.status(201).json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.put('/:id', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { full_name, date_of_birth, gender, address, phone, doctor_id } = req.body;
      if (!full_name) return res.status(400).json({ error: "To'liq ism majburiy" });
      await db.query(
        'UPDATE patients SET full_name=?, date_of_birth=?, gender=?, address=?, phone=?, doctor_id=? WHERE id=?',
        [full_name, date_of_birth || null, gender || null, address || null, phone || null, doctor_id || null, req.params.id]
      );
      const [rows] = await db.query('SELECT * FROM patients WHERE id = ?', [req.params.id]);
      if (!rows.length) return res.status(404).json({ error: 'Bemor topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.delete('/:id', authenticateToken, authorizeRole('admin'), async (req, res) => {
    try {
      await db.query('DELETE FROM patients WHERE id = ?', [req.params.id]);
      res.json({ ok: true });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  return router;
};
