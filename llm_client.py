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


def generate_manim_code(prompt: str, model_name: str = "gemini-2.5-pro") -> Optional[str]:
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
    prompt: str, draft_code: str, model_name: str = "gemini-2.5-pro"
) -> Optional[str]:
    """使用 Reflection 階段檢查並修正初稿，回傳完整程式碼。"""

    if not API_KEY:
        print("錯誤：找不到 GOOGLE_API_KEY。請在專案根目錄建立 .env 並設定 GOOGLE_API_KEY=你的金鑰。")
        return None

    checklist = """
[SYSTEM]
You are a strict code reviewer for a specific Manim project. 
Your goal is to fix errors in the draft code based on the `BaseAlgorithmScene` contract.

[BaseAlgorithmScene Contract]
The abstract class `BaseAlgorithmScene` defines the control flow in its `construct()` method.
Subclasses MUST follow this structure:
1. `get_input_data(self)`: Returns the input data (e.g., list[int]).
2. `get_pseudocode_lines(self)`: Returns a list of strings for the code display.
3. `setup_animation_panel(self)`: Initializes Mobjects (squares, arrows) in `self.anim_panel`.
4. `run_algorithm_visual(self)`: Contains the main animation logic (comparisons, swaps).

[CHECKLIST - CRITICAL]
1. **Mandatory Implementation**:
   - The class **MUST** implement `get_pseudocode_lines(self) -> list[str]`.
   - The class **MUST** implement `run_algorithm_visual(self)`.
   - The class **MUST NOT** implement `construct(self)` (it is inherited).
   - The class **MUST NOT** implement `algorithm(self)` or `setup_scene(self)` (these are invalid names).

2. **Data Handling**:
   - Ensure `get_input_data(self)` is used to parse input. 
   - Do NOT access `self.input_str` or `self.user_input` directly; they do not exist.
   - Use `self.input_data` (populated by Base) in `setup_animation_panel` and `run_algorithm_visual`.

3. **Visual Helper Usage**:
   - Use `self._pc_highlight(line_index)` for code highlighting.
   - Use `self._info_push(text)` for status updates.
   - Use `self._create_index_pointer(text)` for creating pointers (e.g., i, j).
   - Use `self.play(...)` followed by state updates (Play-Then-Update pattern).

4. **Formatting**:
   - Ensure strictly ONE Python code block ` ```python ... ``` `.
   - Keep imports: `from manim import *` and `from base_algorithm_scene import BaseAlgorithmScene`.

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


