// create-table.js
const pool = require('./src/config/db');

(async () => {
  try {
    const query = `
      CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
      );
    `;

    await pool.query(query);
    console.log("Tabla 'usuarios' creada exitosamente.");
  } catch (err) {
    console.error("Error creando la tabla:", err.message);
  } finally {
    pool.end();
  }
})();
