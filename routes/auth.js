const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// In-memory fake DB for now (replace with Mongo or Postgres later)
const users = [];

router.post('/register', async (req, res) => {
  const { email, password } = req.body;

  if (!email.endsWith('@mail.utoronto.ca')) {
    return res.status(400).json({ error: 'Email must be @mail.utoronto.ca' });
  }

  const existingUser = users.find(user => user.email === email);
  if (existingUser) return res.status(400).json({ error: 'User already exists' });

  const hashedPassword = await bcrypt.hash(password, 10);
  const newUser = { email, password: hashedPassword };
  users.push(newUser);

  const token = jwt.sign({ email }, process.env.JWT_SECRET, { expiresIn: '1h' });

  res.status(201).json({ message: 'User registered', token });
});

module.exports = router;
