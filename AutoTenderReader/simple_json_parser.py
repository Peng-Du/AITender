#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简单的JSON解析器
专门处理用户提供的output格式
"""

import json
import re
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import glob

def markdown_to_html(markdown_text: str) -> str:
    """
    将Markdown文本转换为HTML
    """
    if not markdown_text:
        return ""
    
    html = markdown_text
    
    # 转换标题
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 转换粗体和斜体
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # 转换代码块
    html = re.sub(r'```([\s\S]*?)```', r'<pre><code>\1</code></pre>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 转换链接
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # 转换表格
    lines = html.split('\n')
    in_table = False
    result_lines = []
    
    for i, line in enumerate(lines):
        if '|' in line and line.strip():
            if not in_table:
                result_lines.append('<table class="table table-striped">')
                in_table = True
            
            # 检查是否是分隔行
            if re.match(r'^\s*\|[\s\-\|:]+\|\s*$', line):
                continue
            
            # 处理表格行
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if i == 0 or (i > 0 and '|' not in lines[i-1]):
                # 表头
                row = '<tr>' + ''.join(f'<th>{cell}</th>' for cell in cells) + '</tr>'
            else:
                # 普通行
                row = '<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>'
            result_lines.append(row)
        else:
            if in_table:
                result_lines.append('</table>')
                in_table = False
            result_lines.append(line)
    
    if in_table:
        result_lines.append('</table>')
    
    html = '\n'.join(result_lines)
    
    # 转换列表
    html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    html = re.sub(r'</ul>\s*<ul>', '', html)
    
    # 转换段落
    paragraphs = html.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<') and not p.endswith('>'):
            html_paragraphs.append(f'<p>{p}</p>')
        else:
            html_paragraphs.append(p)
    
    return '\n'.join(html_paragraphs)

def process_json_to_html(json_data: List[Dict[str, Any]], target_date_str: str, language: str = 'Chinese') -> str:
    """
    将JSON数据转换为HTML格式
    """
    if not json_data:
        return ""
    
    # Language-specific strings
    if language == 'English':
        title_text = "Tender Document Summary Report"
        header_text = "[Report] Tender Document Summary Report"
        generated_at_text = f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        stats_header_text = "[Statistics]"
        total_files_text = "Total Files:"
        report_time_text = "Report Generation Time:"
        tender_date_text = "Tender Publication Date:"
        file_header_prefix = "[File]"
        summary_placeholder = "No summary content"
        file_placeholder = "File"
    else:  # Default to Chinese
        title_text = "招标文件摘要报告"
        header_text = "[报告] 招标文件摘要报告"
        generated_at_text = f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"
        stats_header_text = "[统计信息]"
        total_files_text = "文件总数:"
        report_time_text = "报告生成时间:"
        tender_date_text = "标书发布日期:"
        file_header_prefix = "[文件]"
        summary_placeholder = "无摘要内容"
        file_placeholder = "文件"

    # 生成HTML头部
    html_content = f"""
<!DOCTYPE html>
<html lang="{'en' if language == 'English' else 'zh-CN'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_text}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .stats {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .stats h2 {{
            color: #667eea;
            margin-top: 0;
        }}
        .file-summary {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .file-header {{
            background: #667eea;
            color: white;
            padding: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .file-content {{
            padding: 30px;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .table th, .table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .table-striped tbody tr:nth-child(odd) {{
            background-color: #f8f9fa;
        }}
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{header_text}</h1>
        <p>{generated_at_text}</p>
    </div>
    
    <div class="stats">
        <h2>{stats_header_text}</h2>
        <p><strong>{total_files_text}</strong> {len(json_data)}{' files' if language == 'English' else ' 个'}</p>
        <p><strong>{report_time_text}</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>{tender_date_text}</strong> {target_date_str}</p>
    </div>
"""
    
    # 为每个文件生成HTML内容
    for i, item in enumerate(json_data, 1):
        file_name = item.get('fileName', f'{file_placeholder}{i}')
        summary = item.get('stringSummary', summary_placeholder)
        
        # 将Markdown转换为HTML
        summary_html = markdown_to_html(summary)
        
        html_content += f"""
    <div class="file-summary">
        <div class="file-header">
            {file_header_prefix} {file_name}
        </div>
        <div class="file-content">
            {summary_html}
        </div>
    </div>
"""
    
    # 添加HTML尾部
    html_content += """
</body>
</html>
"""
    
    return html_content

def extract_json_from_output(input_data):
    """
    从包含'output'字段的数据中提取JSON内容
    
    Args:
        input_data: 包含'output'字段的字典、字符串或列表
    
    Returns:
        解析后的JSON数据，如果解析失败则返回None
    """
    try:
        # 如果输入是字符串，先尝试解析为JSON
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError as e:
                print(f"[信息] JSON直接解析失败: {e}。尝试修复内容...")
                
                output_marker = '"output": "'
                start_index = input_data.find(output_marker)
                if start_index == -1:
                    print("[错误] 修复失败：未找到 'output' 标记。")
                    raise e

                start_of_value = start_index + len(output_marker)

                end_index = -1
                possible_endings = ['"}\n]', '"}]', '"}\n', '"}']
                end_marker_pos = -1
                for ending in possible_endings:
                    end_marker_pos = input_data.rfind(ending)
                    if end_marker_pos != -1 and end_marker_pos > start_of_value:
                        end_index = end_marker_pos
                        break
                
                if end_index == -1:
                    print("[错误] 修复失败：未找到有效的结束标记。")
                    raise e

                value_to_fix = input_data[start_of_value:end_index]
                
                fixed_value = value_to_fix.replace('"', '\\"')
                
                fixed_content = input_data[:start_of_value] + fixed_value + input_data[end_index:]
                
                print(f"[预览] 修复后的文件内容预览: {fixed_content[:200]}...")
                input_data = json.loads(fixed_content)
        
        # 如果是列表，处理每个元素
        if isinstance(input_data, list):
            all_results = []
            for i, item in enumerate(input_data):
                print(f"处理第 {i+1} 个元素...")
                if isinstance(item, dict) and 'output' in item:
                    result = extract_single_output(item['output'])
                    if result:
                        all_results.extend(result if isinstance(result, list) else [result])
            return all_results if all_results else None
        
        # 如果是字典，直接处理
        elif isinstance(input_data, dict) and 'output' in input_data:
            return extract_single_output(input_data['output'])
        
        else:
            print("[错误] 输入数据格式不正确")
            return None
            
    except json.JSONDecodeError as e:
        print(f"[错误] JSON解析错误: {e}")
        return None
    except Exception as e:
        print(f"[错误] 处理过程中出错: {e}")
        return None

def extract_single_output(output_text):
    """
    从单个output字段中提取JSON内容
    """
    try:
        # 首先尝试查找```json```标记后的内容
        pattern = r'```json\s*\n(.*?)```'
        match = re.search(pattern, output_text, re.DOTALL)
        
        if match:
            json_str = match.group(1).strip()
            
            max_retries = 20
            current_json = json_str
            last_exception = None
            
            for i in range(max_retries):
                try:
                    return json.loads(current_json)
                except json.JSONDecodeError as e:
                    last_exception = e
                    print(f"[信息] JSON解析失败 (第 {i+1} 次): {e}.")
                    
                    pos = e.pos
                    
                    # Find the first unescaped quote at or before the error position and escape it.
                    # We search backwards from the error position.
                    bad_quote_pos = -1
                    search_pos = pos
                    while search_pos >= 0:
                        if current_json[search_pos] == '"':
                            num_backslashes = 0
                            p = search_pos - 1
                            while p >= 0 and current_json[p] == '\\':
                                num_backslashes += 1
                                p -= 1
                            if num_backslashes % 2 == 0:
                                bad_quote_pos = search_pos
                                break
                        search_pos -= 1
                    
                    if bad_quote_pos != -1:
                        print(f"尝试修复在位置 {bad_quote_pos} 的引号...")
                        current_json = current_json[:bad_quote_pos] + '\\' + current_json[bad_quote_pos:]
                        print(f"[预览] 修复后的JSON内容预览: {current_json[:400]}...")
                    else:
                        # If we can't find an unescaped quote to fix, we can't proceed.
                        print("[错误] 找不到要修复的未转义引号。")
                        raise e
            
            print(f"[错误] 超过最大重试次数 ({max_retries})")
            # If we exit the loop, it means we failed. Raise the last error.
            if last_exception:
                raise last_exception
            else:
                # Should not happen if loop ran at least once
                return None

        else:
            # 如果没有找到```json```标记，尝试直接解析整个output_text作为JSON
            print("[警告] 未找到json标记，尝试直接解析JSON")
            try:
                result = json.loads(output_text.strip())
                print("[成功] 直接JSON解析成功")
                return result
            except json.JSONDecodeError:
                print("[错误] 直接JSON解析也失败")
                return None
    except Exception as e:
        print(f"[错误] 解析单个output时出错: {e}")
        return None

def find_summary_files(directory):
    """
    查找目录下所有以summary开头的json文件
    """
    pattern = os.path.join(directory, 'summary*.json')
    files = glob.glob(pattern)
    return files

def merge_summary_files(file_paths):
    """
    合并多个summary文件的内容
    """
    all_data = []
    
    for file_path in file_paths:
        try:
            print(f"[处理] 正在处理文件: {os.path.basename(file_path)}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示文件内容的前200个字符用于调试
            print(f"[预览] 文件内容预览: {content[:200]}...")
            
            json_result = extract_json_from_output(content)
            
            if json_result:
                if isinstance(json_result, list):
                    print(f"[成功] 成功处理文件: {os.path.basename(file_path)} - 包含 {len(json_result)} 个条目")
                    # 显示每个条目的fileName
                    for i, item in enumerate(json_result):
                        if isinstance(item, dict) and 'fileName' in item:
                            print(f"   条目 {i+1}: {item['fileName']}")
                    all_data.extend(json_result)
                else:
                    print(f"[成功] 成功处理文件: {os.path.basename(file_path)} - 包含 1 个条目")
                    if isinstance(json_result, dict) and 'fileName' in json_result:
                        print(f"   条目: {json_result['fileName']}")
                    all_data.append(json_result)
            else:
                print(f"[警告] 文件解析失败: {os.path.basename(file_path)}")
                print(f"   原始内容长度: {len(content)} 字符")
                
        except Exception as e:
            print(f"[错误] 处理文件 {os.path.basename(file_path)} 时出错: {e}")
    
    print(f"\n[统计] 合并统计: 总共处理了 {len(file_paths)} 个文件，合并得到 {len(all_data)} 个条目")
    return all_data

import argparse

def main():
    """
    主函数 - 处理用户提供的具体数据
    """
    parser = argparse.ArgumentParser(description='Parse summary JSON files for a specific date.')
    parser.add_argument('--date', help='The date to process in YYYY-MM-DD format. Defaults to today.')
    parser.add_argument('--language', type=str, default='Chinese', choices=['Chinese', 'English'], help='Language for the report (Chinese or English).')
    args = parser.parse_args()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
            target_date_str = args.date
        except ValueError:
            print(f"Error: Invalid date format for '{{args.date}}'. Please use YYYY-MM-DD.")
            return
    else:
        target_date = datetime.now()
        target_date_str = target_date.strftime('%Y-%m-%d')

    print(f"[信息] Processing data for date: {target_date_str}")

    base_dir = r"..\TenderBase"
    source_dir = os.path.join(base_dir, target_date_str)

    if not os.path.isdir(source_dir):
        print(f"[错误] Directory for date {target_date_str} not found at {source_dir}")
        return

    # 查找所有以summary开头的json文件
    summary_files = find_summary_files(source_dir)

    if not summary_files:
        print(f"[错误] 在目录 {source_dir} 中未找到任何以summary开头的json文件")
        return

    print(f"[信息] 找到 {len(summary_files)} 个summary文件:")
    for file in summary_files:
        print(f"  - {os.path.basename(file)}")

    # 合并所有summary文件
    print("\n[处理] 开始合并文件...")
    merged_data = merge_summary_files(summary_files)

    if not merged_data:
        print("[错误] 合并后没有有效数据")
        return

    print(f"\n[成功] 成功合并 {len(merged_data)} 个文件信息")

    # 将合并后的JSON和HTML报告保存在新的parsed_data目录中
    output_parsed_data_dir = os.path.join(base_dir, "parsed_data")
    output_summary_dir = os.path.join(base_dir, "summary")
    os.makedirs(output_parsed_data_dir, exist_ok=True)
    os.makedirs(output_summary_dir, exist_ok=True)

    output_json_path = os.path.join(output_parsed_data_dir, f"parsed_data_{target_date_str}.json")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    print(f"[保存] 合并数据已保存到: {output_json_path}")

    # 生成HTML报告并保存到日期目录
    html_content = process_json_to_html(merged_data, target_date_str, args.language)
    output_html_path = os.path.join(output_summary_dir, f"Summary_{target_date_str}.html")

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[生成] HTML报告已生成: {output_html_path}")
    print(f"\n[完成] 处理完成! 合并版本包含 {len(merged_data)} 个文件的信息")
    
    # 显示每个文件的fileName用于验证
    print("\n[列表] 合并后的文件列表:")
    for i, item in enumerate(merged_data, 1):
        if isinstance(item, dict) and 'fileName' in item:
            print(f"  {i}. {item['fileName']}")
    
    return merged_data

# 通用函数 - 处理任意格式的输入
def process_any_input(data):
    """
    处理任意格式的输入数据
    """
    return extract_json_from_output(data)

if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n" + "=" * 50)
        print("[完成] 解析完成! 可以使用以下方式访问数据:")
        print("- result[0]['fileName'] - 获取文件名")
        print("- result[0]['stringSummary'] - 获取摘要内容")