@echo off
set BACKUP_DIR="D:\backup\TenderServer"
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
set DATE=%DATE: =0%

echo 开始备份...
mkdir %BACKUP_DIR% 2>nul

rem 备份数据库
copy "D:\AITender\TenderServer\database\tender.db" "%BACKUP_DIR%\tender_%DATE%.db"

rem 备份上传文件
powershell "Compress-Archive -Path 'D:\AITender\TenderServer\uploads\*' -DestinationPath '%BACKUP_DIR%\uploads_%DATE%.zip'"

echo 备份完成: %BACKUP_DIR%