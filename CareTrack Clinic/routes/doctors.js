const express = require('express');
const { authenticateToken, authorizeRole } = require('../middleware/auth');

module.exports = function (db) {
  const router = express.Router();

  router.get('/', authenticateToken, async (req, res) => {
    try {
      const { name, specialty } = req.query;
      let sql = 'SELECT * FROM doctors WHERE 1=1';
      const params = [];
      if (name)      { sql += ' AND full_name LIKE ?'; params.push(`%${name}%`); }
      if (specialty) { sql += ' AND specialty = ?';    params.push(specialty); }
      sql += ' ORDER BY full_name';
      const [rows] = await db.query(sql, params);
      res.json(rows);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.get('/:id', authenticateToken, async (req, res) => {
    try {
      const [rows] = await db.query('SELECT * FROM doctors WHERE id = ?', [req.params.id]);
      if (!rows.length) return res.status(404).json({ error: 'Shifokor topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.post('/', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { full_name, specialty, department, phone, email } = req.body;
      if (!full_name) return res.status(400).json({ error: "To'liq ism majburiy" });
      const [result] = await db.query(
        'INSERT INTO doctors (full_name, specialty, department, phone, email) VALUES (?,?,?,?,?)',
        [full_name, specialty || null, department || null, phone || null, email || null]
      );
      const [rows] = await db.query('SELECT * FROM doctors WHERE id = ?', [result.insertId]);
      res.status(201).json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.put('/:id', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const { full_name, specialty, department, phone, email } = req.body;
      if (!full_name) return res.status(400).json({ error: "To'liq ism majburiy" });
      await db.query(
        'UPDATE doctors SET full_name=?, specialty=?, department=?, phone=?, email=? WHERE id=?',
        [full_name, specialty || null, department || null, phone || null, email || null, req.params.id]
      );
      const [rows] = await db.query('SELECT * FROM doctors WHERE id = ?', [req.params.id]);
      if (!rows.length) return res.status(404).json({ error: 'Shifokor topilmadi' });
      res.json(rows[0]);
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  router.delete('/:id', authenticateToken, authorizeRole('admin'), async (req, res) => {
    try {
      await db.query('DELETE FROM doctors WHERE id = ?', [req.params.id]);
      res.json({ ok: true });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  return router;
};
