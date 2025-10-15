# 简化版标书下载系统

单机部署，适用于 10 人左右办公室使用。

## 运行步骤（Windows）

1. 安装 Node.js 18+
2. 进入目录 `D:\AITender\TenderServer`
3. 安装依赖：`npm install`
4. 初始化数据库：`npm run init-db`
5. 启动服务：`npm start`

默认地址：`http://localhost:3000`

## 目录结构

见 `简化版标书下载系统设计文档.md`，本项目已按该文档实现。

## 环境变量（.env）

```
PORT=3000
HOST=0.0.0.0
DB_PATH=./database/tender.db
SESSION_SECRET=your-secret-key-change-this-in-production
SESSION_MAX_AGE=86400000
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=.pdf,.doc,.docx,.zip
```

## 账号初始化

首次使用请在数据库中插入一个管理员用户：

```sql
INSERT INTO users (username, password_hash, full_name, role)
VALUES ('admin', '$2b$10$HcUuVYdS4N3T1z8YQqFQge0mVdHqkqvKJY1S9jz5s3i4Yl2VtK0cK', '管理员', 'admin');
```

> 上述 `password_hash` 为密码 `admin123` 的示例哈希，请在生产环境中替换。

## 备份

使用 `backup.bat` 进行数据库与上传文件备份。