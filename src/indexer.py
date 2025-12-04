import json
import re
import math
import pickle
import os
import nltk
from nltk.corpus import stopwords
from collections import defaultdict, Counter

# 確保 NLTK 資源已下載
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class Indexer:
    def __init__(self, data_file='data/crawled_data.json', index_file='data/inverted_index.pkl'):
        self.data_file = data_file
        self.index_file = index_file
        self.documents = {}  # 儲存 doc_id -> {url, title, text} 以便檢索時顯示
        self.inverted_index = defaultdict(dict)  # term -> {doc_id: weight, ...}
        self.idf = {}
        # 載入英文停用詞
        self.stop_words = set(stopwords.words('english'))

    def load_data(self):
        """讀取爬蟲抓下來的 JSON 資料"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file {self.data_file} not found. Run crawler first.")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 將 List 轉為 Dict，並分配 doc_id (使用 URL 當作 ID 也可以，但整數 ID 較省空間)
        for idx, entry in enumerate(data):
            self.documents[idx] = entry

    def preprocess(self, text):
        """
        文字前處理：
        1. 轉小寫
        2. 移除標點符號 (Regex)
        3. Tokenization (簡單依空白切割)
        4. 移除 Stopwords
        """
        # 1. Lowercasing
        text = text.lower()
        
        # 2. Remove punctuation (保留英數字與空白)
        text = re.sub(r'[^\w\s]', '', text)
        
        # 3. Tokenize
        tokens = text.split()
        
        # 4. Remove stopwords
        clean_tokens = [t for t in tokens if t not in self.stop_words and len(t) > 1]
        
        return clean_tokens

    def build_index(self):
        """建立倒排索引並計算 TF-IDF"""
        print("Building index...")
        
        # 總文件數 N
        N = len(self.documents)
        doc_term_freqs = {} # 暫存每份文件的詞頻
        df_counts = Counter() # Document Frequency
        
        # --- Step 1: 計算 TF (Term Frequency) 與 DF (Document Frequency) ---
        # (這是之前可能被不小心刪除的部分)
        for doc_id, doc_data in self.documents.items():
            # 結合標題與內文
            content = f"{doc_data['title']} {doc_data['text']}"
            tokens = self.preprocess(content)
            
            # 計算該文件內的詞頻 (TF)
            term_counts = Counter(tokens)
            total_terms = len(tokens) if len(tokens) > 0 else 1
            
            doc_term_freqs[doc_id] = {
                term: count / total_terms 
                for term, count in term_counts.items()
            }
            
            # 更新 DF
            for term in term_counts.keys():
                df_counts[term] += 1
                
        # --- Step 2: 計算 IDF (Inverse Document Frequency) ---
        for term, df in df_counts.items():
            self.idf[term] = math.log10(N / df)
            
        # --- Step 3: 計算最終 TF-IDF 並存入 Inverted Index ---
        # (這是我們優化的部分：同時計算 Document Magnitude)
        for doc_id, tf_dict in doc_term_freqs.items():
            magnitude_sq = 0  # 累加平方和
            
            for term, tf in tf_dict.items():
                idf = self.idf[term]
                weight = tf * idf
                self.inverted_index[term][doc_id] = weight
                
                # 累加權重平方
                magnitude_sq += weight ** 2
            
            # 將算好的長度存入 documents 結構中
            self.documents[doc_id]['magnitude'] = math.sqrt(magnitude_sq)
                
        print(f"Index built! Total terms: {len(self.inverted_index)}")

    # save_index 不需要大改，因為它已經會儲存 self.documents

    def save_index(self):
        """儲存索引與文件對應表 (使用 pickle 序列化)"""
        # 確保目錄存在
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        
        data_to_save = {
            "inverted_index": self.inverted_index,
            "documents": self.documents, # 搜尋時需要顯示標題與連結
            "idf": self.idf # 搜尋 query 時需要用到 IDF
        }
        
        with open(self.index_file, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"Index saved to {self.index_file}")

if __name__ == "__main__":
    indexer = Indexer()
    indexer.load_data()
    indexer.build_index()
    indexer.save_index()