const express = require('express');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth'); // 👈 importamos rutas

const app = express();

app.use((req, res, next) => {
  console.log('👉', req.method, req.url);
  next();
});

app.use(cors());
app.use(express.json());

// Rutas
app.use('/api', authRoutes); // /api/login, etc.

app.get('/', (req, res) => {
  res.send('Servidor funcionando');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});

