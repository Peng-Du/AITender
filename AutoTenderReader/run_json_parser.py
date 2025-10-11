import argparse
import datetime
from daily_tasks import json_parser

def main():
    parser = argparse.ArgumentParser(description='Run JSON parser for a specific date.')
    parser.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format. Defaults to yesterday.')
    parser.add_argument('--language', type=str, default='Chinese', choices=['Chinese', 'English'], help='Language for the report (Chinese or English).')
    args = parser.parse_args()

    target_date_str = args.date
    if target_date_str:
        try:
            datetime.datetime.strptime(target_date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format for '{{target_date_str}}'. Please use YYYY-MM-DD.")
            return

    json_parser(target_date_str=target_date_str, language=args.language)

if __name__ == "__main__":
    main()