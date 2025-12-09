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
            
    return tp / k, tp

def run_evaluation():
    print("--- Starting Evaluation ---")
    
    # 1. 載入搜尋引擎
    engine = SearchEngine(index_file=os.path.join(project_root, 'data/inverted_index.pkl'))
    
    # 2. 讀取 Ground Truth (從 JSON 檔案)
    json_path = os.path.join(current_dir, 'ground_truth.json')
    
    if not os.path.exists(json_path):
        print(f"[Error] Ground truth file not found at: {json_path}")
        print("Please create 'ground_truth.json' first.")
        return

    print(f"Loading ground truth from: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            ground_truth = json.load(f)
    except json.JSONDecodeError:
        print(f"[Error] Failed to parse {json_path}. Please check if it is valid JSON.")
        return
    
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
        # print(f"  [Debug] Ground Truth: {relevant_urls} ...") # 只印前兩個示意
        # print(f"  [Debug] Retrieved:    {retrieved_urls}")
        # --- [DEBUG 結束] ---
        
        # 接收兩個值 (分數, 答對數)
        score, tp = calculate_precision_at_k(retrieved_urls, relevant_urls, k)
        total_precision += score
        
        # 顯示詳細結果
        print(f"  - Retrieved (Top K): {len(retrieved_urls)}")
        print(f"  - Found Relevant (TP): {tp}")
        print(f"  - Precision@{k}: {score:.2f}")
        print("-" * 30)

    # 4. 計算平均分數 (Mean Precision)
    map_score = total_precision / len(ground_truth)
    print(f"Average Precision@{k}: {map_score:.2f}")
    print("\nEvaluation Complete.")

if __name__ == "__main__":
    run_evaluation()