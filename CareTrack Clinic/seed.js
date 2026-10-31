require('dotenv').config();
const mysql  = require('mysql');
const bcrypt = require('bcryptjs');

const DB_NAME = process.env.DB_NAME || 'caretrack_db';

const conn = mysql.createConnection({
  host:     process.env.DB_HOST     || 'localhost',
  port:     process.env.DB_PORT     || 3306,
  user:     process.env.DB_USER     || 'root',
  password: process.env.DB_PASSWORD || process.env.DB_PASS || '',
  multipleStatements: true,
});

function q(sql, params) {
  return new Promise((resolve, reject) => {
    conn.query(sql, params || [], (err, results) => {
      if (err) return reject(err);
      resolve(results);
    });
  });
}

async function seed() {
  await q(`CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`);
  await q(`USE \`${DB_NAME}\``);

  await q(`SET FOREIGN_KEY_CHECKS = 0`);
  await q(`DROP TABLE IF EXISTS diagnoses`);
  await q(`DROP TABLE IF EXISTS users`);
  await q(`DROP TABLE IF EXISTS patients`);
  await q(`DROP TABLE IF EXISTS doctors`);
  await q(`SET FOREIGN_KEY_CHECKS = 1`);

  await q(`
    CREATE TABLE doctors (
      id         INT AUTO_INCREMENT PRIMARY KEY,
      full_name  VARCHAR(100) NOT NULL,
      specialty  VARCHAR(100),
      department VARCHAR(100),
      phone      VARCHAR(20),
      email      VARCHAR(100),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await q(`
    CREATE TABLE patients (
      id            INT AUTO_INCREMENT PRIMARY KEY,
      full_name     VARCHAR(150) NOT NULL,
      date_of_birth DATE,
      gender        ENUM('Male','Female','Other'),
      address       TEXT,
      phone         VARCHAR(20),
      doctor_id     INT,
      created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await q(`
    CREATE TABLE users (
      id            INT AUTO_INCREMENT PRIMARY KEY,
      username      VARCHAR(100) UNIQUE NOT NULL,
      password_hash VARCHAR(255) NOT NULL,
      role          ENUM('admin','clinician','patient') NOT NULL,
      patient_id    INT NULL,
      created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await q(`
    CREATE TABLE diagnoses (
      id           INT AUTO_INCREMENT PRIMARY KEY,
      icd_code     VARCHAR(20),
      title        VARCHAR(200),
      description  TEXT,
      severity     ENUM('mild','moderate','severe') NOT NULL,
      patient_id   INT NOT NULL,
      doctor_id    INT,
      diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);

  const doctors = [
    ['Rustam Aliyev',     'Kardiolog',    "Yurak-qon tomir bo'limi",   '+998901234567', 'r.aliyev@caretrack.uz'],
    ['Dilnoza Karimova',  'Pediatr',      "Bolalar bo'limi",            '+998912345678', 'd.karimova@caretrack.uz'],
    ['Sherzod Yusupov',   'Nevrolog',     "Nevrologiya bo'limi",        '+998933456789', 's.yusupov@caretrack.uz'],
    ['Madina Norova',     'Endokrinolog', "Endokrinologiya bo'limi",    '+998974567890', 'm.norova@caretrack.uz'],
    ['Otabek Mahmudov',   'Jarroh',       "Jarrohlik bo'limi",          '+998995678901', 'o.mahmudov@caretrack.uz'],
    ['Nargiza Salimova',  'Ginekolog',    "Ginekologiya bo'limi",       '+998906789012', 'n.salimova@caretrack.uz'],
    ['Sardor Ergashev',   'Terapevt',     "Umumiy terapiya bo'limi",    '+998917890123', 's.ergashev@caretrack.uz'],
    ['Ozoda Hamidova',    'Oftalmolog',   "Ko'z kasalliklari bo'limi",  '+998938901234', 'o.hamidova@caretrack.uz'],
    ['Jahongir Qodirov',  'Urolog',       "Urologiya bo'limi",          '+998999012345', 'j.qodirov@caretrack.uz'],
    ['Feruza Toshmatova', 'Dermatolog',   "Teri kasalliklari bo'limi",  '+998900123456', 'f.toshmatova@caretrack.uz'],
  ];
  for (const d of doctors) {
    await q(`INSERT INTO doctors (full_name, specialty, department, phone, email) VALUES (?,?,?,?,?)`, d);
  }

  const patients = [
    ['Akmal Tursunov',      '1985-04-12', 'Male',   'Toshkent, Chilonzor',     '+998901112233', 1],
    ['Zulfiya Rahimova',    '1992-09-23', 'Female', 'Toshkent, Mirzo Ulugbek', '+998912223344', 1],
    ['Bekzod Saidov',       '1978-01-30', 'Male',   'Samarqand, Registon',     '+998933334455', 2],
    ['Gulchehra Mirzayeva', '2001-07-08', 'Female', 'Toshkent, Yunusobod',     '+998974445566', 2],
    ['Javohir Xoliqov',     '1965-11-15', 'Male',   "Andijon, Bobur ko'chasi", '+998995556677', 3],
    ['Sevara Yuldosheva',   '1996-03-04', 'Female', 'Toshkent, Sergeli',       '+998906667788', 3],
    ['Sanjar Ergashev',     '1988-12-19', 'Male',   'Buxoro, Mustaqillik',     '+998917778899', 4],
    ['Oydin Hamidova',      '1972-06-26', 'Female', 'Toshkent, Olmazor',       '+998938889900', 5],
    ['Nodir Karimov',       '1990-08-14', 'Male',   "Namangan, Navro'z",       '+998999990011', 6],
    ['Shahnoza Umarova',    '1983-02-19', 'Female', 'Toshkent, Yakkasaroy',    '+998900001122', 7],
  ];
  for (const p of patients) {
    await q(`INSERT INTO patients (full_name, date_of_birth, gender, address, phone, doctor_id) VALUES (?,?,?,?,?,?)`, p);
  }

  const hashAdmin     = await bcrypt.hash('admin123',    10);
  const hashClinician = await bcrypt.hash('shifokor123', 10);
  const hashPatient   = await bcrypt.hash('bemor123',    10);

  await q(`INSERT INTO users (username, password_hash, role, patient_id) VALUES (?,?,?,?)`, ['admin',    hashAdmin,     'admin',     null]);
  await q(`INSERT INTO users (username, password_hash, role, patient_id) VALUES (?,?,?,?)`, ['shifokor', hashClinician, 'clinician', null]);
  await q(`INSERT INTO users (username, password_hash, role, patient_id) VALUES (?,?,?,?)`, ['bemor1',   hashPatient,   'patient',   1]);

  const diagnoses = [
    ['I10',   'Birlamchi gipertenziya',           'Bosim 150/95. Antigipertenziv tayinlandi.',           'moderate', 1,  1],
    ['I25.1', 'Yurakning ishemik kasalligi',      "EKG o'zgarishlari. Stress-test rejalashtirildi.",     'severe',   2,  1],
    ['G43.9', 'Migren',                           'MRT tavsiya etildi. Nevroprotektorlar tayinlandi.',    'moderate', 3,  3],
    ['E10.9', '1-toifa qandli diabet',            'Insulin terapiyasi boshlandi.',                        'severe',   4,  4],
    ['K35.8', "O'tkir appenditsit",               "Laparoskopik operatsiya o'tkazildi.",                  'mild',     5,  5],
    ['N94.6', 'Dismenoreya',                      'NSAID va spazmolitiklar tayinlandi.',                  'mild',     6,  6],
    ['M54.5', "Bel og'rig'i",                     'Fizioterapiya kursi tavsiya etildi.',                  'mild',     7,  7],
    ['H52.1', "Miop (qisqa ko'rlik)",             "Ko'zoynak tavsiya etildi.",                            'moderate', 8,  8],
    ['N20.0', 'Buyrak toshi',                     'Ultratovush bilan parchalash rejalashtirildi.',         'severe',   9,  9],
    ['L30.9', 'Ekzema',                           'Kortikosteroid kremlari tayinlandi.',                  'mild',     10, 10],
  ];
  for (const d of diagnoses) {
    await q(`INSERT INTO diagnoses (icd_code, title, description, severity, patient_id, doctor_id) VALUES (?,?,?,?,?,?)`, d);
  }

  console.log("Ma'lumotlar muvaffaqiyatli kiritildi!");
  conn.end();
}

conn.connect(err => {
  if (err) {
    console.error('MySQL ulanish xatosi:', err.message);
    process.exit(1);
  }
  seed().catch(e => {
    console.error('Seed xatosi:', e.message);
    conn.end();
    process.exit(1);
  });
});
