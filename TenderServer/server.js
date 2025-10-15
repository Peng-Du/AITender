const express = require('express');
const path = require('path');
const session = require('express-session');

const { config } = require('./config/config');
const { db } = require('./config/database');
const authRoutes = require('./routes/auth');
const tenderRoutes = require('./routes/tenders');

const app = express();
const PORT = config.PORT;

// 中间件
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
  secret: config.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: Number(config.SESSION_MAX_AGE) || 24 * 60 * 60 * 1000 }
}));

// 路由
app.use('/api/auth', authRoutes);
app.use('/api/tenders', tenderRoutes);
// 不需要上传逻辑，移除上传路由

// 健康检查
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// 启动服务器
app.listen(PORT, config.HOST, () => {
  const hostLabel = config.HOST === '0.0.0.0' ? 'localhost' : config.HOST;
  console.log(`标书系统运行在 http://${hostLabel}:${PORT}`);
  console.log(`工作目录: ${__dirname}`);
});