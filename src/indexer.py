import json
import re
import math
import pickle
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer  # [新增] 引入詞幹提取器
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
        self.documents = {}
        self.inverted_index = defaultdict(dict)
        self.idf = {}
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()  # [新增] 初始化 Stemmer

    def load_data(self):
        """讀取爬蟲抓下來的 JSON 資料"""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file {self.data_file} not found. Run crawler first.")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for idx, entry in enumerate(data):
            self.documents[idx] = entry

    def preprocess(self, text):
        """
        文字前處理：轉小寫 -> 移除標點 -> Tokenize -> 移除 Stopwords -> Stemming
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text) # 將標點符號換成空白，避免黏字
        tokens = text.split()
        
        # [修改] 加入 Stemming (還原詞幹)
        # 例如: "schools" -> "school", "running" -> "run"
        clean_tokens = [
            self.stemmer.stem(t) 
            for t in tokens 
            if t not in self.stop_words and len(t) > 1
        ]
        return clean_tokens

    def build_index(self):
        """建立倒排索引 (包含 SEO 權重優化)"""
        print("Building index with SEO optimization...")
        
        N = len(self.documents)
        doc_term_freqs = {}
        df_counts = Counter()
        
        # --- Step 1: 計算 TF & DF ---
        for doc_id, doc_data in self.documents.items():
            # [SEO 核心優化]：欄位加權 (Field Weighting)
            # 1. 處理 URL：把網址中的符號去掉，當作關鍵字來源
            #    例如 "python.org" -> "python org"
            clean_url = re.sub(r'[^\w\s]', ' ', doc_data['url'])
            
            # 2. 組合內容並給予權重
            #    - Title 重複 5 次 (權重最高)
            #    - URL 重複 3 次 (權重次之)
            #    - Text 重複 1 次 (一般內容)
            #    原理：首頁字數少，標題重複 5 次後，關鍵字密度(Density)會變得超高！
            content = (doc_data['title'] + " ") * 5 + \
                      (clean_url + " ") * 3 + \
                      doc_data['text']
            
            tokens = self.preprocess(content)
            
            # 計算 TF (Term Frequency)
            term_counts = Counter(tokens)
            total_terms = len(tokens) if len(tokens) > 0 else 1
            
            doc_term_freqs[doc_id] = {
                term: count / total_terms 
                for term, count in term_counts.items()
            }
            
            # 更新 DF
            for term in term_counts.keys():
                df_counts[term] += 1
                
        # --- Step 2: 計算 IDF ---
        for term, df in df_counts.items():
            self.idf[term] = math.log10(N / df)
            
        # --- Step 3: 計算最終 TF-IDF 與 Document Magnitude ---
        for doc_id, tf_dict in doc_term_freqs.items():
            magnitude_sq = 0
            for term, tf in tf_dict.items():
                idf = self.idf[term]
                weight = tf * idf
                self.inverted_index[term][doc_id] = weight
                magnitude_sq += weight ** 2
            
            self.documents[doc_id]['magnitude'] = math.sqrt(magnitude_sq)
                
        print(f"Index built! Total terms: {len(self.inverted_index)}")

    def save_index(self):
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        data_to_save = {
            "inverted_index": self.inverted_index,
            "documents": self.documents,
            "idf": self.idf
        }
        with open(self.index_file, 'wb') as f:
            pickle.dump(data_to_save, f)
        print(f"Index saved to {self.index_file}")

if __name__ == "__main__":
    indexer = Indexer()
    indexer.load_data()
    indexer.build_index()
    indexer.save_index()