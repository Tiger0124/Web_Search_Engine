import sys
import os
import json

# [Setup] 將專案根目錄加入 Python 路徑，確保能 import src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.search_engine import SearchEngine

def calculate_precision_at_k(retrieved_urls, relevant_urls, k=5):
    top_k_retrieved = retrieved_urls[:k]
    tp = 0
    
    for ret_url in top_k_retrieved:
        # 邏輯：只要這個搜尋結果的 URL 包含任何一個正確答案 URL 的前綴，就算對
        # 例如 retrieved: .../3/using/index.html 包含 relevant: .../3/
        is_relevant = False
        for true_url in relevant_urls:
            # 移除結尾斜線以避免誤判
            clean_true = true_url.rstrip('/')
            if clean_true in ret_url:
                is_relevant = True
                break
        
        if is_relevant:
            tp += 1
            
    return tp / k

def run_evaluation():
    print("--- Starting Evaluation ---")
    
    # 1. 載入搜尋引擎
    engine = SearchEngine(index_file=os.path.join(project_root, 'data/inverted_index.pkl'))
    
    # 2. 定義 Ground Truth (人工標註的標準答案) [cite: 63, 439]
    # 這是評估最耗時的部分，你需要根據你的爬蟲資料，手動填寫幾個查詢的正確 URL。
    # 格式: "查詢詞": ["正確連結1", "正確連結2", ...]
    ground_truth = {
        "python": [
            "https://docs.python.org/3/",
            "https://www.python.org/about/gettingstarted/",
            "https://docs.python.org/3.15/",
            ""
        ],
        "w3schools": [
            "https://www.w3schools.com",
            "https://www.w3schools.com/academy/index.php",
            "https://www.w3schools.com/spaces/index.php",
            "https://www.w3schools.com/html/default.asp",
            # 請根據你的 crawled_data.json 實際內容填寫
        ],
        "tensorflow": [
            "https://www.tensorflow.org/",
            "https://www.tensorflow.org/learn",
            "https://www.tensorflow.org/tutorials",
            "https://www.tensorflow.org/guide",
            "https://www.tensorflow.org/resources/learn-ml",
        ],
    }
    
    if not ground_truth:
        print("[Warning] Ground truth is empty. Please edit evaluate.py to add relevant URLs.")
        return

    total_precision = 0
    k = 5
    
    print(f"\nEvaluating Precision@{k} for {len(ground_truth)} queries...\n")
    
    # 3. 執行評估迴圈
    for query, relevant_urls in ground_truth.items():
        print(f"Query: '{query}'")
        
        # 執行搜尋
        results, _ = engine.search(query, top_k=k)
        retrieved_urls = [res['url'] for res in results]

        # --- [DEBUG 開始] ---
        print(f"  [Debug] Ground Truth: {relevant_urls[:2]} ...") # 只印前兩個示意
        print(f"  [Debug] Retrieved:    {retrieved_urls}")
        # --- [DEBUG 結束] ---
        
        # 計算分數
        score = calculate_precision_at_k(retrieved_urls, relevant_urls, k)
        total_precision += score
        
        # 顯示詳細結果
        print(f"  - Retrieved: {len(retrieved_urls)}")
        print(f"  - Relevant (Ground Truth): {len(relevant_urls)}")
        print(f"  - Precision@{k}: {score:.2f}")
        print("-" * 30)

    # 4. 計算平均分數 (Mean Precision)
    map_score = total_precision / len(ground_truth)
    print(f"Average Precision@{k}: {map_score:.2f}")
    print("\nEvaluation Complete.")

if __name__ == "__main__":
    run_evaluation()