const { db } = require('../config/database');

module.exports = {
  findByUsername(username) {
    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM users WHERE username = ?', [username], (err, row) => {
        if (err) reject(err); else resolve(row);
      });
    });
  },
  create({ username, password_hash, full_name, role = 'user' }) {
    return new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)',
        [username, password_hash, full_name, role],
        function (err) {
          if (err) reject(err); else resolve({ id: this.lastID });
        }
      );
    });
  }
};