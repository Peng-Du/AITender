const { db } = require('../config/database');

module.exports = {
  insert({ title, description, file_path, file_name, file_size, upload_user_id }) {
    return new Promise((resolve, reject) => {
      db.run(
        'INSERT INTO tenders (title, description, file_path, file_name, file_size, upload_user_id) VALUES (?, ?, ?, ?, ?, ?)',
        [title, description, file_path, file_name, file_size, upload_user_id || null],
        function (err) {
          if (err) reject(err); else resolve({ id: this.lastID });
        }
      );
    });
  },
  search(query) {
    return new Promise((resolve, reject) => {
      const sql = `
        SELECT t.*, u.full_name as uploader_name
        FROM tenders t
        LEFT JOIN users u ON t.upload_user_id = u.id
        WHERE t.title LIKE ? OR t.description LIKE ?
        ORDER BY t.created_at DESC
      `;
      db.all(sql, [`%${query}%`, `%${query}%`], (err, rows) => {
        if (err) reject(err); else resolve(rows);
      });
    });
  },
  getById(id) {
    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM tenders WHERE id = ?', [id], (err, row) => {
        if (err) reject(err); else resolve(row);
      });
    });
  },
  incrementDownloadCount(id) {
    db.run('UPDATE tenders SET download_count = download_count + 1 WHERE id = ?', [id]);
  },
  logDownload({ tender_id, user_id, ip_address }) {
    db.run('INSERT INTO download_records (tender_id, user_id, ip_address) VALUES (?, ?, ?)', [tender_id, user_id, ip_address]);
  }
};