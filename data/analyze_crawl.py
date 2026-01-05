import json
import os
from urllib.parse import urlparse
from collections import Counter

def analyze_crawled_data(file_path='data/crawled_data.json'):
    # 1. 檢查檔案是否存在
    if not os.path.exists(file_path):
        print(f"❌ 找不到檔案: {file_path}")
        print("請先執行爬蟲 (python -m src.crawler) 抓取資料後再來執行此分析。")
        return

    # 2. 讀取資料
    print(f"正在讀取 {file_path} ...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 讀取失敗: {e}")
        return

    # 3. 開始計算指標
    total_pages = len(data)
    if total_pages == 0:
        print("⚠️ 資料庫是空的，沒有任何頁面。")
        return

    # --- 計算網域分佈 ---
    domains = []
    for page in data:
        # 從 URL 提取網域 (例如 https://docs.python.org/3/ -> docs.python.org)
        domain = urlparse(page['url']).netloc
        domains.append(domain)
    
    domain_counts = Counter(domains)

    # --- 計算平均大小 ---
    total_size = 0
    for page in data:
        # 計算 'text' 欄位的長度 (字元數)
        text_len = len(page.get('text', ''))
        total_size += text_len
    
    avg_size = total_size / total_pages

    # 4. 顯示報告結果
    print("\n" + "="*30)
    print("📊 爬蟲成果摘要 (Crawling Summary)")
    print("="*30)
    
    print(f"1️⃣ 總頁面數量 (Total Pages):  {total_pages} 頁")
    
    print(f"2️⃣ 平均頁面大小 (Avg Size):    {avg_size:.2f} 字元/頁")
    
    print("\n3️⃣ 網域分佈 (Domain Distribution):")
    print(f"{'Domain':<30} | {'Pages':<10} | {'Percentage'}")
    print("-" * 55)
    
    for domain, count in domain_counts.most_common():
        percentage = (count / total_pages) * 100
        print(f"{domain:<30} | {count:<10} | {percentage:.1f}%")
    
    print("="*30)

if __name__ == "__main__":
    analyze_crawled_data()