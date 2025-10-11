import sys
from datetime import datetime
from daily_tasks import clear_and_download

def main():
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，则使用第一个参数作为日期
        target_date_str = sys.argv[1]
        try:
            # 验证日期格式
            datetime.strptime(target_date_str, '%Y-%m-%d')
            print(f"Using specified date: {target_date_str}")
            clear_and_download(target_date_str)
        except ValueError:
            print("Error: Date format is not valid. Please use YYYY-MM-DD.")
            sys.exit(1)
    else:
        # 如果没有参数，则使用当前日期
        print("No date specified, using today's date.")
        clear_and_download()

if __name__ == "__main__":
    main()