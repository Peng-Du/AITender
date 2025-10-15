const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const User = require('../models/User');

// 登录
router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: '用户名和密码必填' });
  try {
    const user = await User.findByUsername(username);
    if (!user) return res.status(401).json({ error: '用户不存在' });
    const ok = await bcrypt.compare(password, user.password_hash);
    if (!ok) return res.status(401).json({ error: '密码错误' });
    req.session.user = { id: user.id, username: user.username, full_name: user.full_name, role: user.role };
    res.json({ success: true, user: req.session.user });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 退出登录
router.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

// 当前用户
router.get('/me', (req, res) => {
  if (req.session && req.session.user) return res.json(req.session.user);
  res.status(401).json({ error: '未登录' });
});

module.exports = router;