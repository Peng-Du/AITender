const bcrypt = require('bcrypt');
const { db } = require('../config/database');
const { config } = require('../config/config');

const username = process.env.ADMIN_USERNAME || 'admin';
const password = process.env.ADMIN_PASSWORD || 'admin123';
const full_name = process.env.ADMIN_FULL_NAME || '管理员';

async function ensureAdmin() {
  await new Promise((resolve, reject) => {
    db.get('SELECT * FROM users WHERE username = ?', [username], (err, row) => {
      if (err) return reject(err);
      if (row) {
        console.log(`管理员已存在: ${username}`);
        return resolve();
      }
      resolve();
    });
  });

  const password_hash = await bcrypt.hash(password, 10);
  await new Promise((resolve, reject) => {
    db.run(
      'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
      [username, password_hash, full_name, 'admin'],
      function (err) {
        if (err) return reject(err);
        console.log(`管理员创建成功: ${username}`);
        resolve();
      }
    );
  });
}

ensureAdmin()
  .then(() => process.exit(0))
  .catch(err => {
    console.error(err);
    process.exit(1);
  });