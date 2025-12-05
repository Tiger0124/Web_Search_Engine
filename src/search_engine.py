import pickle
import math
import re
import time
from collections import defaultdict, Counter
from nltk.corpus import stopwords
import nltk
from nltk.stem import PorterStemmer # [新增]

# 確保停用詞庫存在
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SearchEngine:
    def __init__(self, index_file='data/inverted_index.pkl'):
        """初始化"""
        self.index_file = index_file
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer() # [新增] 初始化 Stemmer
        self.data = self.load_index()
        
        self.inverted_index = self.data['inverted_index']
        self.documents = self.data['documents']
        self.idf = self.data['idf']

    def load_index(self):
        """讀取 Pickle 檔案"""
        print(f"Loading index from {self.index_file}...")
        with open(self.index_file, 'rb') as f:
            return pickle.load(f)

    def preprocess(self, text):
        """必須與 Indexer 的邏輯完全一致"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        
        # [修改] 加入 Stemming
        return [
            self.stemmer.stem(t) 
            for t in tokens 
            if t not in self.stop_words and len(t) > 1
        ]

    def get_query_vector(self, query_terms):
        """
        計算查詢句的向量 (Query Vector)
        Q_vector = TF(in query) * IDF(from index)
        """
        query_vector = {}
        term_counts = Counter(query_terms)
        
        for term, count in term_counts.items():
            if term in self.idf:
                # TF * IDF
                tf = count / len(query_terms)
                idf = self.idf[term]
                query_vector[term] = tf * idf
        return query_vector

    def calculate_cosine_similarity(self, query_vector, candidate_docs):
        scores = {}
        
        # 1. 計算 Dot Product (只計算 Query 有出現的詞)
        for term, q_weight in query_vector.items():
            if term in self.inverted_index:
                for doc_id, d_weight in self.inverted_index[term].items():
                    if doc_id in candidate_docs:
                        scores[doc_id] = scores.get(doc_id, 0) + (q_weight * d_weight)

        # 2. 計算 Magnitude
        q_mag = math.sqrt(sum(w**2 for w in query_vector.values()))
        
        final_scores = []
        for doc_id, dot_product in scores.items():
            # [Optimization Fix] 直接從 self.documents 讀取預算好的 magnitude
            # 如果讀不到 (例如舊資料)，預設為 1 避免報錯，但建議重跑 indexer
            d_mag = self.documents[doc_id].get('magnitude', 1.0)
            
            if q_mag == 0 or d_mag == 0:
                similarity = 0
            else:
                similarity = dot_product / (q_mag * d_mag)
            
            final_scores.append((doc_id, similarity))
            
        return sorted(final_scores, key=lambda x: x[1], reverse=True)

    def generate_snippet(self, text, query_terms, window_size=50):
        """
        [Snippet Generation]
        在原文中找到關鍵字，並擷取前後文。
        """
        text_lower = text.lower()
        # 找到第一個出現的 Query Term
        start_index = -1
        for term in query_terms:
            idx = text_lower.find(term)
            if idx != -1:
                start_index = idx
                break
        
        if start_index == -1:
            return text[:100] + "..."  # 沒找到關鍵字，回傳開頭
            
        # 擷取前後視窗
        start = max(0, start_index - window_size)
        end = min(len(text), start_index + window_size)
        snippet = text[start:end]
        
        # 修飾一下，加入 ...
        if start > 0: snippet = "..." + snippet
        if end < len(text): snippet = snippet + "..."
        
        return snippet

    def search(self, query, top_k=10):
        """
        [Main Search Function]
        包含 Bonus 功能：計時、片語搜尋
        """
        # [Bonus] 2. Query execution time
        start_time = time.time()
        
        # [Bonus] 1. Phrase Search Detection (檢查是否有引號)
        phrase_match = re.search(r'"(.*?)"', query)
        exact_phrase = None
        if phrase_match:
            exact_phrase = phrase_match.group(1).lower()
            # 移除引號內容，剩下的做一般搜尋，或直接針對片語做過濾
            # 這裡策略：先用關鍵字搜尋拿到候選名單，再用 String Matching 過濾
            clean_query = query.replace('"', '')
        else:
            clean_query = query

        # 1. 解析 Query
        query_terms = self.preprocess(clean_query)
        if not query_terms:
            return [], 0.0

        # 2. 找出包含至少一個關鍵字的候選文檔 (OR Logic)
        candidate_docs = set()
        for term in query_terms:
            if term in self.inverted_index:
                candidate_docs.update(self.inverted_index[term].keys())

        # 3. 計算向量相似度與排序
        query_vector = self.get_query_vector(query_terms)
        ranked_results = self.calculate_cosine_similarity(query_vector, candidate_docs)

        # 4. 格式化結果與 [Bonus] 片語過濾
        final_results = []
        for doc_id, score in ranked_results:
            doc = self.documents[doc_id]
            
            # [Bonus] Phrase Search Filter
            # 如果使用者搜尋 "web crawler"，我們只回傳內文真的包含該字串的文檔
            if exact_phrase and exact_phrase not in doc['text'].lower():
                continue

            snippet = self.generate_snippet(doc['text'], query_terms)
            
            final_results.append({
                "title": doc['title'],
                "url": doc['url'],
                "score": round(score, 4),
                "snippet": snippet
            })
            
            if len(final_results) >= top_k:
                break

        execution_time = time.time() - start_time
        return final_results, execution_time

if __name__ == "__main__":
    # 簡單測試
    engine = SearchEngine()
    
    # 測試查詢 (你可以換成你資料裡有的詞)
    test_query = "python"
    print(f"Searching for: {test_query}")
    
    results, time_taken = engine.search(test_query)
    
    print(f"Found {len(results)} results in {time_taken:.4f} seconds.")
    for res in results:
        print(f"[{res['score']}] {res['title']}")
        print(f"   {res['url']}")
        print(f"   {res['snippet']}")
        print("-" * 30)