import requests
from bs4 import BeautifulSoup
import time
import json
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from datetime import datetime
import os

class WebSpider:
    def __init__(self, seed_urls, max_pages=1000, output_file='data/crawled_data.json'):
        """
        初始化爬蟲
        :param seed_urls: 初始種子連結列表 (5-10 個)
        :param max_pages: 最大爬取頁數 (預設 1000)
        :param output_file: 儲存路徑
        """
        self.seed_urls = seed_urls
        self.max_pages = max_pages
        self.output_file = output_file
        self.visited_urls = set()  # 用於去重，跳過重複的 URL
        self.urls_to_visit = list(seed_urls)
        self.crawled_data = []
        self.robots_parsers = {}  # 緩存不同網域的 robots.txt 解析器
        
        # 設定 User-Agent (禮貌爬蟲的基本素養)
        self.headers = {
            'User-Agent': 'TermProjectSpider/1.0 (Student Project)'
        }

    def get_robots_parser(self, base_url):
        """獲取並緩存該網域的 robots.txt 解析器"""
        domain = urlparse(base_url).netloc
        if domain in self.robots_parsers:
            return self.robots_parsers[domain]
        
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urljoin(base_url, "/robots.txt"))
        try:
            rp.read()
            self.robots_parsers[domain] = rp
        except Exception:
            # 如果讀取失敗，記錄警告並回傳 None (視為沒有 robots.txt)
            print(f"[Warning] Could not fetch robots.txt for {domain}")
            return None
        return rp

    def can_fetch(self, url):
        """檢查 robots.txt 是否允許爬取"""
        rp = self.get_robots_parser(url)
        if rp:
            return rp.can_fetch(self.headers['User-Agent'], url)
        # 如果沒有 robots.txt，預設允許
        return True

    def fetch_page(self, url):
        """下載並解析單一頁面"""
        try:
            # 關鍵要求：每次請求前強制等待 2 秒 (Politeness policy)
            time.sleep(2)
            
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"[Fail] Status {response.status_code}: {url}")
                return None
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取標題
            title = soup.title.string if soup.title else "No Title"
            
            # 移除 script 和 style 標籤，只保留主要內文
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=' ', strip=True)
            
            # 提取當前頁面中的新連結，加入待爬取隊列 (BFS)
            base_domain = urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                new_url = urljoin(url, link['href'])
                
                # 去除 URL 中的 fragment (例如 #section1)，避免重複爬取同一頁的不同位置
                new_url = new_url.split('#')[0]

                # 簡單過濾：只爬取 http/https 且尚未訪問過
                if new_url not in self.visited_urls and new_url.startswith('http'):
                    # 限制：為了符合 "Specific Topic"，這裡限制只爬取相同網域下的連結
                    if urlparse(new_url).netloc == base_domain:
                        self.urls_to_visit.append(new_url)

            # 回傳符合專案要求的欄位格式
            return {
                "url": url,
                "title": title,
                "text": text,
                "fetch_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[Error] Failed to fetch {url}: {e}")
            return None

    def save_data(self):
        """將結果存入 JSON"""
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        # 使用 utf-8 寫入，並設定 ensure_ascii=False 以正確顯示中文
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {self.output_file}")

    def run(self):
        """執行爬蟲主流程"""
        print(f"Starting crawl with seeds: {self.seed_urls}")
        
        while self.urls_to_visit and len(self.crawled_data) < self.max_pages:
            current_url = self.urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue # 跳過重複的 URL
            
            # 檢查 robots.txt 權限
            if not self.can_fetch(current_url):
                print(f"[Blocked] Robots.txt disallows: {current_url}")
                self.visited_urls.add(current_url)
                continue
                
            print(f"[{len(self.crawled_data) + 1}/{self.max_pages}] Crawling: {current_url}")
            data = self.fetch_page(current_url)
            
            if data:
                self.crawled_data.append(data)
            
            self.visited_urls.add(current_url)
            
        self.save_data()
        print("Crawling finished.")

if __name__ == "__main__":
    # 範例種子連結：設定為 Python 官方文件 (可根據需求修改為特定主題)
    seeds = [
        "https://docs.python.org/3/",
        "https://www.python.org/about/gettingstarted/",
        "https://developer.mozilla.org/en-US/docs/Learn",
        "https://www.w3schools.com/",
        "https://scikit-learn.org/",
        "https://www.tensorflow.org/",
    ]
    
    # 建立並執行爬蟲
    # 測試階段可以先將 max_pages 設小一點 (例如 20)
    spider = WebSpider(seed_urls=seeds, max_pages=1000)
    spider.run()