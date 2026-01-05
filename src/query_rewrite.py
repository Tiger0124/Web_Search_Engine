import os
import json
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
        
        self.candidate_models = [
            "gemini-3-flash-preview",
            "gemini-2.5-flash"
        ]

    def rewrite(self, user_question):
        prompt = f"""
        你是一個搜尋引擎輔助助手。
        任務：將使用者的自然語言問題轉換為 2-3 個適合搜尋引擎的關鍵字查詢。
        
        使用者問題："{user_question}"
        
        輸出格式要求 (JSON)：
        {{
            "queries": ["關鍵字1", "關鍵字2"]
        }}
        
        限制：
        1. 只要回傳 JSON，不要有其他廢話。
        2. 關鍵字必須適合用於 TF-IDF 關鍵字搜尋。
        """

        # 自動嘗試所有候選模型
        for model_name in self.candidate_models:
            try:
                # print(f"Trying model: {model_name}...") # 除錯用
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                
                result = json.loads(response.text)
                final_queries = result.get("queries", [user_question])
                # print(f"Success with {model_name}!")
                return final_queries
            
            except Exception as e:
                # 如果是 404 或其他 API 錯誤，就試下一個模型
                # print(f"Model {model_name} failed: {e}")
                continue

        # 如果全部失敗，回傳原始問題
        print("All GenAI models failed. Returning original query.")
        return [user_question]

if __name__ == "__main__":
    rewriter = QueryRewriter()
    print("Testing QueryRewriter...")
    print(rewriter.rewrite("台灣哪裡有 AI 相關的大學系所？"))