import os
import re
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 以取得 GOOGLE_API_KEY
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


def _extract_code_block(text: str) -> str:
    """從回覆文字中擷取第一個 Python 程式碼區塊；若找不到則回傳原文去除首尾空白。
    支援 ```python / ```py / ``` 三種標記。
    """
    if not text:
        return ""

    patterns = [
        r"```python\n([\s\S]*?)\n```",
        r"```py\n([\s\S]*?)\n```",
        r"```\n([\s\S]*?)\n```",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return match.group(1).strip()
    return text.strip()


def generate_manim_code(prompt: str, model_name: str = "gemini-3-pro-preview") -> Optional[str]:
    """
    使用 Google Gemini 產生 Manim 程式碼。

    :param prompt: 已經填充好的完整提示詞
    :param model_name: 預設使用 gemini-3-pro-preview，可依環境調整
    :return: 程式碼字串；若發生錯誤回傳 None
    """
    if not API_KEY:
        print("錯誤：找不到 GOOGLE_API_KEY。請在專案根目錄建立 .env 並設定 GOOGLE_API_KEY=你的金鑰。")
        return None

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, generation_config={"temperature": 0.2})

        # 可能回傳物件的介面會隨版本不同，這裡以 .text 取整段文字
        content_text = getattr(response, "text", None) or ""
        code = _extract_code_block(content_text)
        return code
    except Exception as e:
        print(f"呼叫 LLM API 時發生錯誤: {e}")
        return None


# ... (保留原本的 imports 和 generate_manim_code)

def fix_manim_code(broken_code: str, error_log: str, model_name: str = "gemini-3-pro-preview") -> Optional[str]:
    """
    將錯誤訊息回傳給 LLM 進行自我修復。
    """
    if not API_KEY:
        print("錯誤：找不到 GOOGLE_API_KEY。")
        return None

    # 建構修復用的 Prompt
    prompt = f"""
    [SYSTEM]
    You are a Manim expert. The Python code you generated previously failed to execute.
    Your task is to analyze the error message and FIX the code.

    ---
    
    ### BROKEN CODE:
    ```python
    {broken_code}
    ```

    ### EXECUTION ERROR (stderr):
    {error_log}

    ---

    ### INSTRUCTIONS:
    1. Identify the cause of the error (e.g., AttributeError, TypeError, SyntaxError).
    2. Fix the code logic or syntax. 
    3. **DO NOT** change the overall structure (must inherit from BaseAlgorithmScene).
    4. Return the **COMPLETE** fixed Python code block (wrapped in ```python).
    """

    try:
        # 使用與原本相同的配置，建議使用較聰明的模型來進行 Debug
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)
        
        print(f"正在請求 AI 修復程式碼 (Model: {model_name})...")
        response = model.generate_content(prompt, generation_config={"temperature": 0.2})

        content_text = getattr(response, "text", None) or ""
        fixed_code = _extract_code_block(content_text)
        return fixed_code
    except Exception as e:
        print(f"呼叫 LLM Fix API 時發生錯誤: {e}")
        return None