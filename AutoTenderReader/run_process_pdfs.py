import sys
import datetime
from daily_tasks import process_pdfs

def main():
    target_date = None
    if len(sys.argv) > 1:
        try:
            # 验证日期格式
            datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
            target_date = sys.argv[1]
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            return

    process_pdfs(target_date)

if __name__ == "__main__":
    main()