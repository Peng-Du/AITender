import json
import re
from collections import Counter

def check_duplicate_ids(file_path):
    """检查JSON文件中的fileName字段是否有重复的id号"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取所有的id号
        ids = []
        for item in data:
            if 'fileName' in item:
                # 使用正则表达式提取id号
                match = re.search(r'id_(\d+)', item['fileName'])
                if match:
                    ids.append(match.group(1))
        
        # 统计id号出现次数
        id_counts = Counter(ids)
        
        print(f"总共找到 {len(ids)} 个id号")
        print(f"唯一id号数量: {len(id_counts)}")
        
        # 检查重复
        duplicates = {id_num: count for id_num, count in id_counts.items() if count > 1}
        
        if duplicates:
            print("\n发现重复的id号:")
            for id_num, count in duplicates.items():
                print(f"  id_{id_num}: 出现 {count} 次")
            return False
        else:
            print("\n✅ 没有发现重复的id号")
            return True
            
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    file_path = "d:\\AI\\AutoTenderReader\\yesterday\\parsed_data_2025-07-05.json"
    check_duplicate_ids(file_path)