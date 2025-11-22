const pool = require('./src/config/db');

(async () => {
  try {
    const result = await pool.query('SELECT NOW()');
    console.log('Conexión exitosa! Hora en el servidor PostgreSQL:', result.rows[0]);
  } catch (err) {
    console.error('Error conectando a la BD:', err.message);
  } finally {
    pool.end();
  }
})();
