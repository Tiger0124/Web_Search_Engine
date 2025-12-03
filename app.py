from flask import Flask, render_template, request
from src.search_engine import SearchEngine
import time

app = Flask(__name__)

# [Initialization]
# 在應用程式啟動時載入搜尋引擎 (只載入一次，提升效能)
print("Initializing Search Engine...")
# 確保你的 index 檔案路徑正確，如果按照 Day 2 執行，應該在 data/inverted_index.pkl
search_engine = SearchEngine()
print("Search Engine ready!")

@app.route('/')
def index():
    """首頁：顯示搜尋框"""
    return render_template('index.html')

@app.route('/search')
def search():
    """搜尋結果頁"""
    # 從 URL 參數獲取查詢詞 (e.g., /search?q=python)
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('index.html')
    
    # 呼叫我們在 Day 3 寫好的核心邏輯
    # 這裡會回傳 results (list) 和 execution_time (float)
    results, time_taken = search_engine.search(query, top_k=10)
    
    return render_template(
        'results.html', 
        query=query, 
        results=results, 
        time_taken=time_taken,
        count=len(results)
    )

if __name__ == '__main__':
    # 啟動 Flask Server，debug=True 方便開發時除錯
    app.run(debug=True, port=5000)