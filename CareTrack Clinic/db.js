const mysql = require('mysql');

const pool = mysql.createPool({
  host:     process.env.DB_HOST     || 'localhost',
  port:     process.env.DB_PORT     || 3306,
  user:     process.env.DB_USER     || 'root',
  password: process.env.DB_PASSWORD || process.env.DB_PASS || '',
  database: process.env.DB_NAME     || 'caretrack',
  multipleStatements: true
});

function query(sql, params = []) {
  return new Promise((resolve, reject) => {
    pool.query(sql, params, (err, results) => {
      if (err) return reject(err);
      if (Array.isArray(results)) {
        resolve([results]);
      } else {
        resolve([{ insertId: results.insertId, affectedRows: results.affectedRows }]);
      }
    });
  });
}

module.exports = { pool, query };
