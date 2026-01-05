import os
from google import genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class AIExplainer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("找不到 GOOGLE_API_KEY，請檢查 .env 檔案")
            
        self.client = genai.Client(api_key=api_key)
        
        # [使用您確認可行的模型清單]
        self.candidate_models = [
            "gemini-3-flash-preview",
            "gemini-2.5-flash"
        ]

    def explain(self, user_question, search_results):
        """
        根據搜尋結果的 snippet 解釋問題
        """
        if not search_results:
            return "找不到相關資料，無法進行總結。"

        # 組合 Context (將搜尋到的標題與摘要串接)
        context = ""
        for i, res in enumerate(search_results[:5]): # 只取前 5 筆
            snippet = res.get('snippet', 'No snippet')
            context += f"[{i+1}] 標題: {res['title']}\n摘要: {snippet}\n\n"

        # 建立 Prompt
        prompt = f"""
        你是一個負責解釋搜尋結果的助手。
        
        使用者問題："{user_question}"
        
        請嚴格根據以下提供的搜尋結果摘要來回答問題：
        === 搜尋結果開始 ===
        {context}
        === 搜尋結果結束 ===
        
        指令：
        1. **只能**根據上述提供的摘要內容回答，**絕對不要**使用你自己的外部知識或編造事實 (No Hallucination)。
        2. 如果提供的摘要資訊不足以回答問題，請明確說明「根據搜尋結果，資訊不足以回答此問題」。
        3. 請用 3-5 句繁體中文進行重點總結，解釋為什麼這些頁面跟使用者的問題相關。
        """

        # 自動輪詢所有模型
        for model_name in self.candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                # print(f"模型 {model_name} 失敗: {e}") # 需要除錯時可打開
                continue
                
        return "解釋生成失敗 (所有 AI 模型皆無回應)"

# 簡單測試區塊
if __name__ == "__main__":
    explainer = AIExplainer()
    fake_results = [
        {"title": "測試標題", "snippet": "這是一個測試摘要，說明 AI 的功能。"}
    ]
    print("Testing AIExplainer...")
    # 測試是否能正常呼叫
    print(explainer.explain("這是什麼測試？", fake_results))