const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'caretrack_jwt_2026';

module.exports = function (db) {
  const router = express.Router();

  router.post('/login', async (req, res) => {
    try {
      const { username, password } = req.body;
      if (!username || !password) {
        return res.status(400).json({ error: 'Username va parol kiritilishi shart' });
      }

      const [rows] = await db.query(
        'SELECT id, username, password_hash, role, patient_id FROM users WHERE username = ?',
        [username]
      );

      if (!rows || rows.length === 0) {
        return res.status(401).json({ error: "Username yoki parol noto'g'ri" });
      }

      const user = rows[0];
      const match = await bcrypt.compare(password, user.password_hash);
      if (!match) {
        return res.status(401).json({ error: "Username yoki parol noto'g'ri" });
      }

      const payload = {
        id:         user.id,
        username:   user.username,
        role:       user.role,
        patient_id: user.patient_id,
      };

      const token = jwt.sign(payload, JWT_SECRET, { expiresIn: '24h' });

      res.json({
        token,
        role:       user.role,
        username:   user.username,
        patient_id: user.patient_id,
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Server xatosi' });
    }
  });

  return router;
};
