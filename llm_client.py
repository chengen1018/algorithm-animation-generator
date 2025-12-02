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
    :param model_name: 預設使用 gemini-2.5-pro，可依環境調整
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


def review_manim_code(
    prompt: str, draft_code: str, model_name: str = "gemini-3-pro-preview"
) -> Optional[str]:
    """使用 Reflection 階段檢查並修正初稿，回傳完整程式碼。"""

    if not API_KEY:
        print("錯誤：找不到 GOOGLE_API_KEY。請在專案根目錄建立 .env 並設定 GOOGLE_API_KEY=你的金鑰。")
        return None

    checklist = """
[SYSTEM]
You are a precise Manim code reviewer. Perform static analysis and fix issues in the draft.

Hard requirements:
- Keep the class name `AlgorithmAnimation` and ensure it inherits `BaseAlgorithmScene`.
- Only use Python standard library and Manim Community Edition APIs (0.18+).
- Include necessary imports: `from manim import *` and `from base_algorithm_scene import BaseAlgorithmScene`; add `import ast` when parsing input.
- Forbidden (to keep execution deterministic and secure in an offline sandbox): network requests, file I/O, randomness, dynamic imports, or accessing local/remote resources.
- Output exactly one Python code block containing the full script; no extra text.

[CHECKLIST]
- Repair missing or incorrect imports.
- Ensure only one scene class named `AlgorithmAnimation(BaseAlgorithmScene)` exists.
- Verify hooks follow BaseAlgorithmScene expectations (no construct override).
- Remove forbidden operations and keep animations deterministic.
- Maintain compatibility with the provided task prompt and user input.

[TASK CONTEXT]
User prompt:
{prompt}

Draft code:
```python
{draft_code}
```
"""

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(checklist, generation_config={"temperature": 0})
        content_text = getattr(response, "text", None) or ""
        reviewed_code = _extract_code_block(content_text)
        return reviewed_code
    except Exception as e:
        print(f"Reflection 階段呼叫 LLM API 時發生錯誤: {e}")
        return None


