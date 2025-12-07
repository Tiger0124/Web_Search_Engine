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
    
    # --- Precision 分子：有多少個結果是相關的？ ---
    tp_precision = 0
    for ret_url in top_k_retrieved:
        is_relevant = False
        for true_url in relevant_urls:
            clean_true = true_url.rstrip('/')
            if clean_true in ret_url:
                is_relevant = True
                break
        if is_relevant:
            tp_precision += 1
            
    # --- Recall 分子：有多少個 GT 被找到了？ ---
    tp_recall = 0
    for true_url in relevant_urls:
        clean_true = true_url.rstrip('/')
        matched = False
        for ret_url in top_k_retrieved:
            if clean_true in ret_url:
                matched = True
                break
        if matched:
            tp_recall += 1

    # --- 計算指標 ---
    precision = tp_precision / k
    
    total_relevant = len(relevant_urls)
    recall = tp_recall / total_relevant if total_relevant > 0 else 0
    
    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0
        
    # 多回傳 tp_precision 和 tp_recall 讓顯示更正確
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