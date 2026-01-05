import os
import sys
import csv
import time
import inspect

# 讓程式能找到 src 資料夾
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.query_rewrite import QueryRewriter
except ImportError:
    print("錯誤：找不到 src.query_rewrite 模組。請確認檔案結構是否正確。")
    sys.exit(1)

def main():
    print("=== Prompt Engineering Analysis (Part E) ===")
    
    # 1. 初始化 GenAI 模組
    try:
        rewriter = QueryRewriter()
    except Exception as e:
        print(f"初始化失敗: {e}")
        print("請檢查 .env 是否包含正確的 GOOGLE_API_KEY")
        return

    # [檢查] 確認 rewriter.rewrite 是否有支援 version 參數
    sig = inspect.signature(rewriter.rewrite)
    if 'version' not in sig.parameters:
        print("\n[嚴重警告] 您的 src/query_rewrite.py 尚未更新！")
        print("請先修改 rewrite 方法，使其接受 version 參數 (def rewrite(self, user_question, version='B'): ...)")
        print("分析程式無法執行，程式終止。")
        return

    # 2. 定義測試問題 (包含簡單、複雜、中文、英文)
    test_cases = [
        "Python tutorial",                                      # 簡單：基礎關鍵字
        "What Taiwanese universities are strong in AI research?", # 範例：專題說明書的例子
        "How to build a web crawler that respects robots.txt?",   # 複雜：包含技術細節
        "台北有什麼好吃的牛肉麵推薦？",                           # 中文：在地化查詢
        "Deep learning vs Machine learning differences",         # 比較：概念釐清
        "Apple stock"
    ]

    results = []
    print(f"準備測試 {len(test_cases)} 個問題...\n")

    # 3. 執行測試迴圈
    for i, question in enumerate(test_cases):
        print(f"[{i+1}/{len(test_cases)}] 測試問題: {question}")
        
        # --- 測試 Prompt A (Basic) ---
        print("  Running Prompt A (Basic)...", end="", flush=True)
        start_a = time.time()
        try:
            res_a = rewriter.rewrite(question, version='A')
        except Exception as e:
            res_a = f"Error: {e}"
        time_a = time.time() - start_a
        print(f" Done ({time_a:.2f}s)")
        time.sleep(60)
        # --- 測試 Prompt B (Advanced) ---
        print("  Running Prompt B (Advanced)...", end="", flush=True)
        start_b = time.time()
        try:
            res_b = rewriter.rewrite(question, version='B')
        except Exception as e:
            res_b = f"Error: {e}"
        time_b = time.time() - start_b
        print(f" Done ({time_b:.2f}s)")
        time.sleep(60)
        # 收集結果
        results.append({
            "Question": question,
            "Prompt_A_Output": str(res_a), # 轉字串避免 list 格式問題
            "Prompt_A_Time": round(time_a, 4),
            "Prompt_B_Output": str(res_b),
            "Prompt_B_Time": round(time_b, 4)
        })
        print("-" * 50)

    # 4. 儲存結果為 CSV
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "pe_analysis_report.csv")
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["Question", "Prompt_A_Output", "Prompt_A_Time", "Prompt_B_Output", "Prompt_B_Time"])
            writer.writeheader()
            writer.writerows(results)
        print(f"\n分析完成！結果已儲存至: {csv_file}")
        
    except Exception as e:
        print(f"儲存 CSV 失敗: {e}")

if __name__ == "__main__":
    main()