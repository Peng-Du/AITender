const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { config } = require('../config/config');

// 确保上传目录存在
if (!fs.existsSync(config.UPLOAD_DIR)) {
  fs.mkdirSync(config.UPLOAD_DIR, { recursive: true });
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, config.UPLOAD_DIR);
  },
  filename: function (req, file, cb) {
    const safeName = Date.now() + '-' + file.originalname.replace(/[^\w\.\-]/g, '_');
    cb(null, safeName);
  }
});

function uploadFilter(req, file, cb) {
  const ext = path.extname(file.originalname).toLowerCase();
  if (config.ALLOWED_FILE_TYPES.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('只允许PDF、DOC、DOCX、ZIP文件'));
  }
}

const upload = multer({
  storage,
  fileFilter: uploadFilter,
  limits: { fileSize: Number(config.MAX_FILE_SIZE) }
});

module.exports = { upload };