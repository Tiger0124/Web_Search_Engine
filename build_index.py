import json
import os
import sys

# 讓程式找得到 src 資料夾
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.indexer import Indexer

def main():
    # 1. 設定路徑
    data_path = os.path.join('data', 'crawled_data.json')
    index_path = os.path.join('data', 'inverted_index.pkl')
    
    # 2. 檢查是否有爬蟲資料
    if not os.path.exists(data_path):
        print("錯誤：找不到 crawled_data.json，請先確認爬蟲是否有跑完。")
        return

    # 3. 讀取 JSON
    print("正在讀取資料...")
    with open(data_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)

    # 4. 真正開始建立索引 (這才是重點！)
    print(f"正在為 {len(documents)} 筆文件建立索引...")
    indexer = Indexer()
    indexer.build_index(documents)
    
    # 5. 存檔
    indexer.save_index(index_path)
    print(f"完成！索引已儲存至 {index_path}")

if __name__ == "__main__":
    main()