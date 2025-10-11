import os
import schedule
import time
from datetime import datetime, timedelta
import subprocess
import shutil

def clear_and_download(target_date_str=None):
    """
    Executes the download script (main.py) in ..\TenderBase
    with a specified date.
    """
    # 如果没有提供日期，则使用今天的日期
    if not target_date_str:
        target_date_str = datetime.now().strftime('%Y-%m-%d')

    download_tender_dir = r'..\TenderBase'
    script_path = os.path.join(download_tender_dir, 'main.py')

    if os.path.exists(script_path):
        print(f'Executing download process: {script_path} for date {target_date_str}')
        
        try:
            command = ['python', 'main.py', '--date', target_date_str]
            result = subprocess.run(
                command,
                cwd=download_tender_dir,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            print(f'Download process completed successfully for date {target_date_str}')
            print(f'Output: {result.stdout}')
            if result.stderr:
                print(f'Warnings: {result.stderr}')
        except subprocess.CalledProcessError as e:
            print(f'Error executing main.py: {e}')
            print(f'Error output: {e.stderr}')
        except subprocess.TimeoutExpired:
            print(f'Timeout: main.py took too long to execute')
        except Exception as e:
            print(f'Unexpected error with main.py: {e}')
    else:
        print(f'Error: Script not found at {script_path}')

def process_pdfs(target_date_str=None):
    # 如果没有提供日期，则使用今天的日期
    if not target_date_str:
        run_date = datetime.now()
    else:
        try:
            run_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format for '{target_date_str}'. Please use YYYY-MM-DD.")
            return

    project_dir = r'..\AutoTenderReader'
    base_dir = r'..\TenderBase'
    # 使用指定日期创建目录
    date_dir = os.path.join(base_dir, run_date.strftime('%Y-%m-%d'))
    os.makedirs(date_dir, exist_ok=True)

    pdf_source_dir = os.path.join(r'..\TenderBase', f"Download{run_date.strftime('%Y-%m-%d')}")
    pdf2md_script = os.path.join(project_dir, 'pdf2md.py')

    if not os.path.isdir(pdf_source_dir):
        print(f"Error: PDF source directory '{pdf_source_dir}' not found.")
        return

    for filename in os.listdir(pdf_source_dir):
        pdf_path = os.path.join(pdf_source_dir, filename)
        if os.path.isfile(pdf_path) and filename.lower().endswith('.pdf'):
            print(f'Processing {pdf_path}...')
            try:
                md_filename = os.path.splitext(filename)[0] + '.md'
                md_output_path = os.path.join(date_dir, md_filename)
                
                command = ['python', pdf2md_script, pdf_path, md_output_path]
                subprocess.run(command, check=True)
                print(f'Successfully converted {filename} to {md_filename} in {date_dir}')
            except subprocess.CalledProcessError as e:
                print(f'Error processing {filename}: {e}')
            except FileNotFoundError:
                print(f'Error: {pdf2md_script} not found.')

def json_parser(target_date_str=None, language='Chinese'):
    """执行simple_json_parser.py脚本"""
    # 如果没有提供日期，则使用今天的日期
    if not target_date_str:
        target_date_str = datetime.now().strftime('%Y-%m-%d')

    project_dir = r'..\AutoTenderReader'
    json_parser_script = os.path.join(project_dir, 'simple_json_parser.py')
    
    if not os.path.exists(json_parser_script):
        print(f'Error: {json_parser_script} not found.')
        return
    
    print(f'Executing JSON parser: {json_parser_script} for date {target_date_str}')
    try:
        command = ['python', json_parser_script, '--date', target_date_str, '--language', language]
        result = subprocess.run(command,
                              cwd=project_dir, 
                              check=True, 
                              capture_output=True, 
                              text=True,
                              timeout=600)  # 10分钟超时
        print(f'JSON parser completed successfully')
        print(f'Output: {result.stdout}')
        if result.stderr:
            print(f'Warnings: {result.stderr}')
    except subprocess.CalledProcessError as e:
        print(f'Error executing JSON parser: {e}')
        print(f'Error output: {e.stderr}')
    except subprocess.TimeoutExpired:
        print(f'Timeout: JSON parser took too long to execute')
    except Exception as e:
        print(f'Unexpected error with JSON parser: {e}')

def main():
    # 安排任务每天凌晨1点执行清空和下载任务
    schedule.every().day.at("01:00").do(clear_and_download)
    
    # 安排任务每天凌晨2点执行PDF处理任务
    schedule.every().day.at("01:30").do(process_pdfs)
    
    # 安排任务每天凌晨1点30分执行JSON解析任务
    schedule.every().day.at("04:00").do(json_parser)

    print("Scheduler started. Waiting for scheduled times...")
    print("- 01:00: Clear download folder and execute download process")
    print("- 01:30: Process PDFs")
    print("- 04:00: Run JSON parser")
    # 初始立即运行一次用于测试
    # print("Running an initial test...")
    # clear_and_download()
    # process_pdfs()
    # json_parser()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()