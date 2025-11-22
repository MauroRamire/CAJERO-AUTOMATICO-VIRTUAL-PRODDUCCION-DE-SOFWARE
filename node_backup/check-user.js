// check-user.js
const pool = require('./src/config/db');

(async () => {
  try {
    const res = await pool.query('SELECT id, email, password_hash FROM usuarios');
    console.log(res.rows);
  } catch (err) {
    console.error('Error leyendo usuarios:', err.message);
  } finally {
    pool.end();
  }
})();
