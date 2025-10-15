const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbDir = path.join(__dirname, '..', 'database');
const dbPath = path.join(dbDir, 'tender.db');

// 确保数据库目录存在
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
  // 用户表
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  // 标书表
  db.run(`CREATE TABLE IF NOT EXISTS tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_user_id INTEGER,
    download_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (upload_user_id) REFERENCES users(id)
  )`);

  // 下载记录表
  db.run(`CREATE TABLE IF NOT EXISTS download_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    download_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
  )`);

  // 索引
  db.run('CREATE INDEX IF NOT EXISTS idx_tenders_title ON tenders(title)');
  db.run('CREATE INDEX IF NOT EXISTS idx_tenders_description ON tenders(description)');
  db.run('CREATE INDEX IF NOT EXISTS idx_tenders_created_at ON tenders(created_at)');

  console.log('数据库初始化完成，数据库文件位于: ' + dbPath);
});

db.close();