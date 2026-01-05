# 🔍 Python Web Search Engine

這是一個基於 Python 實作的小型搜尋引擎，專為 **Information Retrieval and Generative AI** 課程的 Term Project II 所設計。

本專案實現了一個完整的搜尋引擎流程，包含從特定主題網站爬取資料、建立倒排索引 (Inverted Index)、計算 TF-IDF 權重，並透過 Flask 網頁介面提供即時的關鍵字搜尋服務。

## ✨ 核心功能 (Features)

本系統依據專案需求與 Bonus 項目開發，具備以下模組：

### 1. Web Spider (爬蟲)
* **針對性爬取**：從種子連結 (Seed URLs) 出發，抓取特定主題網頁。
* **禮貌機制 (Politeness)**：實作請求間隔 (≥ 2秒)，避免對伺服器造成負擔。
* **Robots.txt 遵循**：自動解析並遵守目標網站的 `robots.txt` 規範。
* **資料結構化**：將標題、內文、URL 與抓取時間儲存為 JSON 格式。

### 2. Indexing (索引)
* **文字前處理**：包含轉小寫 (Lowercasing)、移除標點符號與停用詞 (Stopwords Removal)。
* **倒排索引 (Inverted Index)**：建立 Term 到 Document 的映射結構，支援快速檢索。
* **TF-IDF 權重**：計算 Term Frequency 與 Inverse Document Frequency，作為排序基礎。

### 3. Search & Ranking (搜尋與排序)
* **向量空間模型**：使用 Cosine Similarity (餘弦相似度) 計算查詢與文件的相關性。
* **動態摘要 (Snippets)**：根據關鍵字在內文中的位置，動態生成預覽摘要。
* **🚀 Bonus Features**：
    * **片語搜尋 (Phrase Search)**：支援使用雙引號 ` "..." ` 進行精確匹配。
    * **效能監控**：顯示查詢執行時間 (Execution Time)。

### 4. Web Interface (網頁介面)
* 基於 **Flask** 框架開發的輕量級 Web App。
* 整合 **Bootstrap 5**，提供響應式且美觀的搜尋框與結果列表。

## 📂 專案架構 (Structure)

```text
search_engine_project/
│
├── data/                   # 資料儲存區
│   ├── crawled_data.json   # 爬蟲產出的原始數據
│   └── inverted_index.pkl  # 序列化後的索引檔案 (Search Engine Core)
│
├── src/                    # 核心原始碼
│   ├── __init__.py         # Package 初始化
│   ├── crawler.py          # 網頁爬蟲模組
│   ├── indexer.py          # 索引建置與前處理模組
│   └── search_engine.py    # 搜尋邏輯、排序演算法、Bonus 功能實作
│
├── evaluation/             # 評估模組
│   └── evaluate.py         # 計算 Precision@K 指標 (Bonus)
│
├── templates/              # Flask 網頁模板
│   ├── index.html          # 搜尋首頁
│   └── results.html        # 搜尋結果頁
│
├── app.py                  # 網頁應用程式入口 (Flask Entry Point)
├── requirements.txt        # 專案依賴套件清單
└── README.md               # 專案說明文件
```

### 🚀 快速開始 (Quick Start)
請確認您的環境已安裝 Python 3.8+。

**1. 安裝依賴 (Installation)**

```bash
# 建議建立虛擬環境 (Optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝所需套件
pip install -r requirements.txt
```


**2. 執行爬蟲 (Step 1: Crawling)**

爬蟲會根據 src/crawler.py 中設定的種子連結抓取網頁。
(預設設定為 Python 官方文件進行測試，可自行修改 seeds 變數)

```bash
python src/crawler.py
```


* 產出：data/crawled_data.json
* 注意：為遵守禮貌機制，爬取速度會受到 time.sleep(2) 限制。

**3. 建立索引 (Step 2: Indexing)**

讀取爬取的 JSON 資料，進行斷詞與權重計算。

```bash
python src/indexer.py
```


* 產出：data/inverted_index.pkl

**4. 啟動搜尋引擎 (Step 3: Web Interface)**

啟動 Flask 網頁伺服器。

```bash
python app.py
```


* 打開瀏覽器前往：http://127.0.0.1:5000
* 輸入關鍵字 (如 python, class, "web crawler") 即可開始搜尋。
---
### 📊 效能評估 (Evaluation)
本專案包含一個評估腳本，用於計算 Precision@K 指標，以衡量搜尋結果的準確度。

**如何使用評估工具：**

1. 開啟 evaluation/evaluate.py。
2. 編輯 ground_truth 字典，填入測試查詢詞與人工標記的正確 URL。
3. 執行評估腳本：

```bash
python evaluation/evaluate.py
python src/indexer.py
```
**評估指標說明**
* Precision@K：計算前 K 筆結果中，相關文件所佔的比例。
  * 公式：$Precision@K = \frac{\text{Number of relevant results in top K}}{K}$。
