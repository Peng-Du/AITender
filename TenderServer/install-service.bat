@echo off
cd /d "D:\AITender\TenderServer"

echo 安装PM2...
npm install -g pm2

echo 启动服务...
pm2 start server.js --name "tender-system"

echo 设置开机自启...
pm2 startup
pm2 save

echo 服务安装完成！