from flask import Flask, render_template, request
from src.search_engine import SearchEngine
from src.query_rewrite import QueryRewriter
from src.ai_explain import AIExplainer
import time

app = Flask(__name__)

# [Initialization]
# 在應用程式啟動時載入搜尋引擎 (只載入一次，提升效能)
print("Initializing Search Engine...")
# 確保你的 index 檔案路徑正確，如果按照 Day 2 執行，應該在 data/inverted_index.pkl
search_engine = SearchEngine()
print("Search Engine ready!")
# 初始化 AI
# 請確保您有設定環境變數 OPENAI_API_KEY，或直接在這邊傳入 api_key="sk-..."
rewriter = QueryRewriter()
explainer = AIExplainer()
print("System ready!")

@app.route('/')
def index():
    """首頁：顯示搜尋框"""
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('index.html')
    
    start_time = time.time()

    # --- 階段 1: GenAI 改寫查詢 (Part C) ---
    # 不再直接搜尋 query，而是先問 AI
    # generated_queries = rewriter.rewrite(query)
    generated_queries = rewriter.rewrite(query, version='A') # 爛prompt
    # generated_queries = rewriter.rewrite(query, version='B') # 好prompt
    print(f"Original: {query} -> Generated: {generated_queries}")
    
    # --- 階段 2: 執行搜尋 (Part B) ---
    # 策略：搜尋所有生成的關鍵字，然後合併結果 (或是只搜第一個)
    # 這裡示範簡單版：只搜尋 AI 產生的第一個關鍵字，或者把原本的 query 也加入搜尋
    
    final_results = []
    seen_urls = set()
    
    # 搜尋 AI 建議的關鍵字
    for q in generated_queries:
        results, _ = search_engine.search(q, top_k=5)
        for res in results:
            if res['url'] not in seen_urls:
                final_results.append(res)
                seen_urls.add(res['url'])
    
    # 截斷結果只取前 10 筆
    final_results = final_results[:10]
    
    # --- 階段 3: GenAI 解釋結果 (Part D) ---
    ai_response = explainer.explain(query, final_results)
    
    total_time = time.time() - start_time
    
    # 回傳給前端 (記得修改 results.html 來顯示 generated_queries 和 ai_response)
    return render_template(
        'results.html', 
        query=query, 
        generated_queries=generated_queries, # [新增] 讓前端顯示 AI 產生了什麼關鍵字
        results=final_results, 
        ai_response=ai_response,             # [新增] 讓前端顯示 AI 的總結
        time_taken=total_time,
        count=len(final_results)
    )

@app.route('/about')
def about():
    """關於頁面：顯示系統統計資訊"""
    # 從 search_engine 物件中讀取已索引的文件總數
    # search_engine.documents 是一個字典，key 是 doc_id
    doc_count = len(search_engine.documents) if hasattr(search_engine, 'documents') else 0
    
    # 也可以順便顯示有多少個關鍵字 (Bonus)
    term_count = len(search_engine.inverted_index) if hasattr(search_engine, 'inverted_index') else 0
    
    return render_template('about.html', doc_count=doc_count, term_count=term_count)

if __name__ == '__main__':
    # 啟動 Flask Server，debug=True 方便開發時除錯
    app.run(debug=True, port=5000)