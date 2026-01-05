import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class QueryRewriter:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("找不到 GOOGLE_API_KEY，請檢查 .env 檔案")
        
        self.client = genai.Client(api_key=api_key)
        
        self.model_name = "gemini-2.0-flash-exp" 

    def rewrite(self, user_question, version='B'):
        """
        將使用者問題轉換為關鍵字
        :param user_question: 使用者輸入的問題
        :param version: 'A' (Basic) 或 'B' (Advanced)
        """
        
        if version == 'A':
            # === Prompt A: Basic Version (基礎版) ===
            # 指令模糊，容易產生多餘文字或格式錯誤
            prompt = f"""
            請幫我把這個問題變成搜尋關鍵字：
            {user_question}
            給我 JSON 格式。
            """
        else:
            # === Prompt B: Advanced Version (進階版) ===
            # 包含：角色設定、明確任務、格式限制、範例 (Few-Shot)、防呆機制
            prompt = f"""
            你是一個專業的搜尋引擎優化 (SEO) 專家。
            
            [任務]
            將使用者的「自然語言問題」轉換為 2-3 組適合用於「關鍵字搜尋引擎 (TF-IDF)」的查詢字串。
            
            [使用者問題]
            "{user_question}"
            
            [限制與規則]
            1. 輸出必須是純 JSON 格式，不要包含 Markdown 標記 (如 ```json ... ```)。
            2. 這一份 JSON 必須包含一個鍵值 "queries"，對應一個字串列表。
            3. 關鍵字必須去除虛詞 (如 "the", "is", "what")，只保留實詞。
            4. 如果問題包含專有名詞 (如 "Python", "Taiwan")，必須保留。
            5. 請提供不同切入點的關鍵字組合 (例如同義詞)。
            
            [輸出範例]
            User: "What Taiwanese universities are strong in AI research?"
            Output: {{ "queries": ["Taiwan university AI research", "Artificial Intelligence research center Taiwan", "top CS universities Taiwan"] }}
            
            [你的回答]
            """

        try:
            # 呼叫 GenAI
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" # 強制 JSON 輸出 (Gemini 強項)
                )
            )
            
            # 解析 JSON
            result = json.loads(response.text)
            
            # 容錯處理：如果 AI 回傳的 JSON 結構不對，嘗試修復或回傳預設值
            if "queries" in result:
                return result["queries"]
            else:
                # 萬一 AI 回傳了 list 或是其他 key
                return list(result.values())[0] if result else [user_question]

        except Exception as e:
            print(f"[GenAI Error] {e}")
            # 發生錯誤時的 Fallback：直接回傳原始問題切開的字
            return [user_question]

if __name__ == "__main__":
    # 測試區塊
    rewriter = QueryRewriter()
    q = "台灣有哪些大學有在做深度偽造 (Deepfake) 的研究？"
    
    print(f"原始問題: {q}")
    print("-" * 30)
    
    print("測試 Prompt A (Basic):")
    res_a = rewriter.rewrite(q, version='A')
    print(res_a)
    
    print("-" * 30)
    
    print("測試 Prompt B (Advanced):")
    res_b = rewriter.rewrite(q, version='B')
    print(res_b)