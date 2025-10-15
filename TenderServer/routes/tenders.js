const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const fsp = fs.promises;
const { config } = require('../config/config');

// 工具：安全解析并确保在根目录内
function safeResolveUnderRoot(root, relPath) {
  const resolved = path.resolve(root, relPath);
  const normalizedRoot = path.resolve(root);
  if (!resolved.startsWith(normalizedRoot)) {
    return null;
  }
  return resolved;
}

// 工具：生成稳定ID（Base64相对路径）
function encodeId(relPath) {
  return Buffer.from(relPath).toString('base64');
}
function decodeId(id) {
  try {
    return Buffer.from(id, 'base64').toString();
  } catch {
    return null;
  }
}

// 递归遍历目录，收集文件
async function walkFiles(dir) {
  const out = [];
  const entries = await fsp.readdir(dir, { withFileTypes: true });
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      const sub = await walkFiles(full);
      out.push(...sub);
    } else if (ent.isFile()) {
      out.push(full);
    }
  }
  return out;
}

// 搜索：从 TenderBase 目录检索文件名包含关键词
router.get('/search', async (req, res) => {
  try {
    const root = config.UPLOAD_DIR; // 已配置为 ../TenderBase 的绝对路径
    const { q } = req.query;
    const term = (q || '').trim().toLowerCase();

    // 仅遍历以 Download 开头的目录
    const rootEntries = await fsp.readdir(root, { withFileTypes: true });
    const downloadDirs = rootEntries
      .filter((ent) => ent.isDirectory() && ent.name.toLowerCase().startsWith('download'))
      .map((ent) => path.join(root, ent.name));

    const files = [];
    for (const dir of downloadDirs) {
      const subFiles = await walkFiles(dir);
      files.push(...subFiles);
    }

    // 构造结果（默认最多返回200条，按修改时间倒序）
    const stats = await Promise.all(
      files.map(async (full) => ({
        full,
        stat: await fsp.stat(full)
      }))
    );
    stats.sort((a, b) => b.stat.mtimeMs - a.stat.mtimeMs);

    const results = [];
    for (const { full, stat } of stats) {
      const relUnderUpload = path.relative(root, full);
      const fileName = path.basename(full);
      if (term && !fileName.toLowerCase().includes(term) && !relUnderUpload.toLowerCase().includes(term)) {
        continue;
      }
      results.push({
        id: encodeId(relUnderUpload),
        title: fileName,
        description: relUnderUpload,
        file_path: relUnderUpload,
        file_name: fileName,
        file_size: stat.size,
        uploader_name: null,
        download_count: 0,
        updated_at: stat.mtime
      });
      if (results.length >= 200) break;
    }

    res.json(results);
  } catch (error) {
    console.error('Search tenders (fs) error:', error);
    res.status(500).json({ error: '服务器错误' });
  }
});

// 下载：通过Base64编码的相对路径进行下载（限定在根目录）
router.get('/:id/download', async (req, res) => {
  try {
    const root = config.UPLOAD_DIR;
    const decoded = decodeId(req.params.id);
    if (!decoded) {
      return res.status(400).json({ error: '下载参数不合法' });
    }
    const safeFull = safeResolveUnderRoot(root, decoded);
    if (!safeFull) {
      return res.status(400).json({ error: '非法路径' });
    }
    if (!fs.existsSync(safeFull)) {
      return res.status(404).json({ error: '文件不存在' });
    }
    res.download(safeFull, path.basename(safeFull));
  } catch (error) {
    console.error('Download tender (fs) error:', error);
    res.status(500).json({ error: '服务器错误' });
  }
});

module.exports = router;