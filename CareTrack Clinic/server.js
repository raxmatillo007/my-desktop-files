require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({ origin: '*' }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

const db = require('./db');

app.use('/api/auth', require('./routes/auth')(db));
app.use('/api/doctors', require('./routes/doctors')(db));
app.use('/api/patients', require('./routes/patients')(db));
app.use('/api/diagnoses', require('./routes/diagnoses')(db));
app.use('/api/dashboard', require('./routes/dashboard')(db));

app.get('/', (req, res) => res.redirect('/login.html'));

app.listen(PORT, () => console.log(`http://localhost:${PORT}`));
