const path = require('path');
require('dotenv').config();

// 规范化路径：如果是相对路径，基于项目根目录（TenderServer）转换为绝对路径
function resolvePath(p) {
  return path.isAbsolute(p) ? p : path.join(__dirname, '..', p);
}

const config = {
  PORT: process.env.PORT || 3000,
  HOST: process.env.HOST || '0.0.0.0',
  DB_PATH: resolvePath(process.env.DB_PATH || path.join(__dirname, '..', 'database', 'tender.db')),
  SESSION_SECRET: process.env.SESSION_SECRET || 'your-secret-key',
  SESSION_MAX_AGE: process.env.SESSION_MAX_AGE || String(24 * 60 * 60 * 1000),
  UPLOAD_DIR: resolvePath(process.env.UPLOAD_DIR || path.join(__dirname, '..', 'uploads')),
  MAX_FILE_SIZE: process.env.MAX_FILE_SIZE || String(50 * 1024 * 1024),
  ALLOWED_FILE_TYPES: (process.env.ALLOWED_FILE_TYPES || '.pdf,.doc,.docx,.zip')
    .split(',')
    .map(s => s.trim().toLowerCase())
};

module.exports = { config };