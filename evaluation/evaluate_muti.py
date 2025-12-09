import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.search_engine import SearchEngine

def calculate_metrics(retrieved_urls, relevant_urls, k=5):
    """
    計算 Precision, Recall, F1
    回傳: (precision, recall, f1, tp_precision, tp_recall)
    """
    top_k_retrieved = retrieved_urls[:k]
    
    tp_precision = 0
    found_relevant_urls = set() # [Recall 關鍵] 用集合紀錄「哪些標準答案被找到了」
    
    # --- 核心修改：統一從「搜尋結果」出發，去對答案 ---
    for ret_url in top_k_retrieved:
        is_valid_result = False
        
        # 拿這個搜尋結果，去跟每一個標準答案 (GT) 比對
        for true_url in relevant_urls:
            clean_true = true_url.rstrip('/')
            
            # 判斷邏輯：標準答案 (GT) 是否包含在 搜尋結果 (Result) 中？
            # 例如 GT: "python.org", Result: "python.org/doc" -> True
            if clean_true in ret_url:
                is_valid_result = True
                found_relevant_urls.add(true_url) # 記錄：這個 GT 被抓到了！
                # 這裡不 break，因為一個結果可能同時滿足多個 GT (視您的 GT 定義而定)
                # 用 set 也不怕重複加
        
        # 如果這個結果有對應到任何一個 GT，Precision 分子 +1
        if is_valid_result:
            tp_precision += 1
            
    # --- 統計 Recall 分子 ---
    # 看 set 裡面收集到了幾個不重複的 GT
    tp_recall = len(found_relevant_urls)

    # --- 計算指標 (保持不變) ---
    precision = tp_precision / k
    
    total_relevant = len(relevant_urls)
    recall = tp_recall / total_relevant if total_relevant > 0 else 0
    
    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0
        
    return precision, recall, f1, tp_precision, tp_recall

def run_evaluation():
    print("--- Starting Evaluation ---")
    
    # 1. 載入搜尋引擎
    index_path = os.path.join(project_root, 'data/inverted_index.pkl')
    # 相容性檢查：如果上一層找不到，找當前目錄
    if not os.path.exists(index_path):
         index_path = os.path.join(current_dir, 'data/inverted_index.pkl')
         
    engine = SearchEngine(index_file=index_path)
    
    # 2. 讀取 Ground Truth
    json_path = os.path.join(current_dir, 'ground_truth.json')
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)

    total_precision = 0
    total_recall = 0
    total_f1 = 0
    k = 5
    
    print(f"\nEvaluating metrics@{k} for {len(ground_truth)} queries...\n")
    
    for query, relevant_urls in ground_truth.items():
        print(f"Query: '{query}'")
        
        results, _ = engine.search(query, top_k=k)
        retrieved_urls = [res['url'] for res in results]

        # --- [DEBUG 開始] ---
        print(f"  [Debug] Ground Truth: {relevant_urls} ...") # 只印前兩個示意
        print(f"  [Debug] Retrieved:    {retrieved_urls}")
        # --- [DEBUG 結束] ---

        # 接收 5 個回傳值
        p, r, f1, tp_p, tp_r = calculate_metrics(retrieved_urls, relevant_urls, k)
        
        total_precision += p
        total_recall += r
        total_f1 += f1
        
        # --- 修正後的顯示邏輯 ---
        print(f"  - Precision@{k}: {p:.2f} (Found {tp_p}/{k} valid docs)")
        print(f"  - Recall@{k}:    {r:.2f} (Found {tp_r}/{len(relevant_urls)} GT items)")
        print(f"  - F1 Score:     {f1:.2f}")
        print("-" * 30)

    num = len(ground_truth)
    if num > 0:
        print("=== Overall Results ===")
        print(f"Mean Precision@{k}: {total_precision/num:.4f}")
        print(f"Mean Recall@{k}:    {total_recall/num:.4f}")
        print(f"Mean F1 Score:      {total_f1/num:.4f}")
        print("=======================")

if __name__ == "__main__":
    run_evaluation()