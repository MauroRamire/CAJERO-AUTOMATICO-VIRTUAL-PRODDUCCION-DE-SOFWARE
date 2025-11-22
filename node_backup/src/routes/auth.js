const express = require('express');
const router = express.Router();

router.post('/login', (req, res) => {
  console.log('📩 /api/login llamado. Body:', req.body);

  return res.status(200).json({
    message: 'DEBUG LOGIN OK',
    body: req.body
  });
});

module.exports = router;


