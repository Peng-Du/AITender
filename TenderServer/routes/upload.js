const express = require('express');
const router = express.Router();
const path = require('path');
const { upload } = require('../middleware/upload');
const { requireAuth } = require('../middleware/auth');
const Tender = require('../models/Tender');

// 上传文件并创建标书记录
router.post('/file', requireAuth, upload.single('file'), async (req, res) => {
  try {
    const { title, description } = req.body;
    const file = req.file;
    if (!file) return res.status(400).json({ error: '未上传文件' });
    if (!title) return res.status(400).json({ error: '标题必填' });

    // 存储相对路径（相对于项目根目录 TenderServer）
    const projectRoot = path.join(__dirname, '..');
    const relPath = path.relative(projectRoot, path.join(require('../config/config').config.UPLOAD_DIR, file.filename));

    const record = await Tender.insert({
      title,
      description: description || '',
      file_path: relPath,
      file_name: file.filename,
      file_size: file.size,
      upload_user_id: req.session.user.id
    });

    res.json({ success: true, id: record.id, file_name: file.filename });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;