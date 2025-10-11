20250902
解决双引号"转义问题

20250812
改为相对路径

20250704
01:00am：（Python）下载pdf，将当前D:\AI\DownloadTender\Download改名为\Download+前天日期，创建新的Download目录，用于下载昨天的pdf
01:30am：（Python）转化md，执行daily_tasks.py，从D:\AI\DownloadTender\Download读取文档，转化为md，放在:D:\AI\AutoTenderReader\yesterday下面
02:00am：（n8n）执行n8n工作流，读取D:\AI\AutoTenderReader\yesterday，分析原始id.md，生成多个summary_id.md
04:00am：（Python）将多个summary_id.md汇总，生成summary.html和parsed_data.json
自动：（n8n）自动检查summary目录，提取最新生成的summary.html通过邮件发送

需要打开：
1. npx n8n
2. python daily_tasks

20250715
1. 此版本支持指定日期分析

20250723
2. 此版本支持语言选择
（1）英语：AI Agent使用英文版系统提示词，JSON Parser节点选择--language English；
（2）中文：AI Agent使用中文版系统提示词，JSON Parser节点选择--language Chinese；

20251006
1. 把md文件，Summary文件，Parsed_data和html都放到TenderBase中