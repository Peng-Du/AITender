#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件信息读取脚本
读取指定文件的内容和元数据信息
"""

import os
import mimetypes
from pathlib import Path
import json
from datetime import datetime

def get_file_info(file_path):
    """
    获取文件的详细信息
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 包含文件信息的字典
    """
    try:
        # 获取文件路径对象
        path_obj = Path(file_path)
        
        # 检查文件是否存在
        if not path_obj.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        # 获取文件统计信息
        stat_info = path_obj.stat()
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                content = "无法读取文件内容（编码问题）"
        except Exception as e:
            content = f"读取文件内容时出错: {str(e)}"
        
        # 构建文件信息字典
        file_info = {
            "File Name": path_obj.name,
            "Directory": str(path_obj.parent),
            "File Extension": path_obj.suffix,
            "Mime Type": mime_type or "unknown",
            "File Size": f"{stat_info.st_size} B",
            "File Size (KB)": f"{stat_info.st_size / 1024:.2f} KB",
            "Created Time": datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "Modified Time": datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "Full Path": str(path_obj.absolute()),
            "Content": content,
            "Content Length": len(content),
            "Line Count": len(content.splitlines()) if isinstance(content, str) else 0
        }
        
        return file_info
        
    except Exception as e:
        return {"error": f"获取文件信息时出错: {str(e)}"}

def read_file_content(file_path):
    """
    简单读取文件内容
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        str: 文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    except Exception as e:
        return f"读取文件失败: {str(e)}"

def main():
    """
    主函数 - 演示如何使用
    """
    # 测试文件路径
    test_file = "d:/AI/AutoTenderReader/yesterday/Test1.md"
    
    print("=== 文件内容读取 ===")
    content = read_file_content(test_file)
    print(f"文件内容:\n{content}")
    print()
    
    print("=== 文件详细信息 ===")
    file_info = get_file_info(test_file)
    
    # 格式化输出文件信息
    if "error" in file_info:
        print(f"错误: {file_info['error']}")
    else:
        for key, value in file_info.items():
            if key != "Content":  # 内容单独显示
                print(f"{key}: {value}")
        
        print(f"\n文件内容:\n{file_info['Content']}")
    
    # 保存为JSON格式
    output_file = "d:/AI/AutoTenderReader/file_info_output.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(file_info, f, ensure_ascii=False, indent=2)
        print(f"\n文件信息已保存到: {output_file}")
    except Exception as e:
        print(f"保存文件信息失败: {str(e)}")

if __name__ == "__main__":
    main()