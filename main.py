import os
import time
from src.crawler import Crawler

def main():
    # 1. 設定種子網址 (這裡使用技術文件，最容易成功)
    seed_urls = [
        "https://docs.python.org/3/tutorial/index.html",
    ]
    
    # 2. 初始化爬蟲
    # 作業要求 delay >= 2 秒
    # max_pages 設定為 50 頁先做測試，確認沒問題後再改成 500 或 1000
    crawler = Crawler(base_url=seed_urls[0], max_pages=50, delay=2.1)
    
    # 手動將其他種子加入待爬清單 (因為你的 Crawler class 設計主要是單一 base_url)
    # 我們這裡稍微變通一下，用迴圈跑每一個 seed
    
    all_data = []
    
    for url in seed_urls:
        print(f"開始爬取 Seed: {url} ...")
        # 為了避免每個 seed 都重置 visited_urls，我們可能需要修改一下 crawler 的邏輯
        # 但為了不改動你的原始碼，我們這裡簡單地對每個 seed 跑一個小爬蟲，然後合併資料
        
        c = Crawler(base_url=url, max_pages=30, delay=2.1) # 每個站抓 30 頁
        data = c.crawl()
        all_data.extend(data)
        print(f" -> 從 {url} 抓到了 {len(data)} 頁")
        
        time.sleep(2) # 換網站中間休息一下

    # 3. 儲存資料
    output_path = os.path.join('data', 'crawled_data.json')
    
    # 由於你的 Crawler.save_data 是存自己的 self.crawled_data
    # 我們這裡手動用一個 Crawler 實例來存合併後的資料
    final_crawler = Crawler(base_url="", max_pages=0)
    final_crawler.crawled_data = all_data
    
    # 確保 data 資料夾存在
    os.makedirs('data', exist_ok=True)
    
    final_crawler.save_data(output_path)
    print(f"\n總共爬取了 {len(all_data)} 頁。")
    print(f"資料已儲存至: {output_path}")

if __name__ == "__main__":
    main()