// create-user.js
require('dotenv').config();
const bcrypt = require('bcrypt');
const pool = require('./src/config/db');

const email = 'prueba2@correo.com';
const password = '123456';

(async () => {
  try {
    const hash = await bcrypt.hash(password, 10);

    const result = await pool.query(
      'INSERT INTO usuarios (email, password_hash) VALUES ($1, $2) RETURNING id',
      [email, hash]
    );

    console.log('Usuario creado con id:', result.rows[0].id);
  } catch (err) {
    console.error('Error creando usuario:', err.message);
  } finally {
    pool.end();
  }
})();

