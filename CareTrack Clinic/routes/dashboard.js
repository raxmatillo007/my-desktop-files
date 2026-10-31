const express = require('express');
const { authenticateToken, authorizeRole } = require('../middleware/auth');

module.exports = function (db) {
  const router = express.Router();

  router.get('/stats', authenticateToken, authorizeRole('admin', 'clinician'), async (req, res) => {
    try {
      const [[doctorRow]]    = await db.query('SELECT COUNT(*) AS cnt FROM doctors');
      const [[patientRow]]   = await db.query('SELECT COUNT(*) AS cnt FROM patients');
      const [[diagnosisRow]] = await db.query('SELECT COUNT(*) AS cnt FROM diagnoses');

      const [[sevRow]] = await db.query(`
        SELECT
          SUM(CASE WHEN severity = 'mild'     THEN 1 ELSE 0 END) AS mild,
          SUM(CASE WHEN severity = 'moderate' THEN 1 ELSE 0 END) AS moderate,
          SUM(CASE WHEN severity = 'severe'   THEN 1 ELSE 0 END) AS severe
        FROM diagnoses
      `);

      const [[genderRow]] = await db.query(`
        SELECT
          SUM(CASE WHEN gender = 'Male'   THEN 1 ELSE 0 END) AS Male,
          SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS Female,
          SUM(CASE WHEN gender = 'Other'  THEN 1 ELSE 0 END) AS \`Other\`
        FROM patients
      `);

      const [perDoctor] = await db.query(`
        SELECT d.full_name, COUNT(p.id) AS cnt
        FROM doctors d
        LEFT JOIN patients p ON p.doctor_id = d.id
        GROUP BY d.id, d.full_name
        ORDER BY cnt DESC
        LIMIT 10
      `);

      res.json({
        total_doctors:   doctorRow.cnt,
        total_patients:  patientRow.cnt,
        total_diagnoses: diagnosisRow.cnt,
        severity_breakdown: {
          mild:     Number(sevRow.mild)     || 0,
          moderate: Number(sevRow.moderate) || 0,
          severe:   Number(sevRow.severe)   || 0,
        },
        gender_breakdown: {
          Male:   Number(genderRow.Male)   || 0,
          Female: Number(genderRow.Female) || 0,
          Other:  Number(genderRow.Other)  || 0,
        },
        patients_per_doctor: perDoctor,
      });
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: e.message });
    }
  });

  return router;
};
