"""
視覺隱喻設計器 (Visual Metaphor Designer)

此模組負責將抽象的演算法概念轉換為具體的視覺設計決策。
"""

import os
import json
import re
from dataclasses import dataclass, asdict
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
VISUAL_METAPHOR_PROMPT_PATH = "visual_metaphor_prompt.txt"


@dataclass
class VisualMetaphor:
    """視覺隱喻資料結構"""
    algorithm_name: str
    shapes: dict[str, str]
    colors: dict[str, str]
    camera_movements: list[str]
    layout_strategy: str
    animation_style: str
    metaphor_explanation: str

    def to_json(self, indent: int = 2) -> str:
        """轉換為格式化的 JSON 字串"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "VisualMetaphor":
        """從字典建立 VisualMetaphor 物件"""
        return cls(
            algorithm_name=data.get("algorithm_name", ""),
            shapes=data.get("shapes", {}),
            colors=data.get("colors", {}),
            camera_movements=data.get("camera_movements", []),
            layout_strategy=data.get("layout_strategy", ""),
            animation_style=data.get("animation_style", ""),
            metaphor_explanation=data.get("metaphor_explanation", "")
        )


def _extract_json_from_response(text: str) -> Optional[dict]:
    """
    從 LLM 回應中提取 JSON 物件。
    支援 ```json 標記或直接的 JSON 文字。
    """
    if not text:
        return None

    # 嘗試提取 ```json 程式碼區塊
    json_pattern = r"```json\s*\n([\s\S]*?)\n```"
    match = re.search(json_pattern, text, flags=re.MULTILINE)
    
    if match:
        json_str = match.group(1).strip()
    else:
        # 嘗試提取 ``` 程式碼區塊
        code_pattern = r"```\s*\n([\s\S]*?)\n```"
        match = re.search(code_pattern, text, flags=re.MULTILINE)
        if match:
            json_str = match.group(1).strip()
        else:
            # 假設整段文字就是 JSON
            json_str = text.strip()

    # 嘗試解析 JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗: {e}")
        print(f"嘗試解析的內容:\n{json_str[:500]}...")
        return None


def _load_prompt_template() -> Optional[str]:
    """載入視覺隱喻提示詞模板"""
    try:
        with open(VISUAL_METAPHOR_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"錯誤：找不到視覺隱喻提示詞模板：{VISUAL_METAPHOR_PROMPT_PATH}")
        return None
    except OSError as e:
        print(f"錯誤：讀取提示詞模板時發生問題：{e}")
        return None


def _build_visual_metaphor_prompt(algorithm_name: str, input_data: str) -> Optional[str]:
    """建立完整的視覺隱喻生成提示詞"""
    template = _load_prompt_template()
    if template is None:
        return None

    return (
        template
        .replace("{{algorithm_name}}", algorithm_name)
        .replace("{{input_data}}", input_data)
    )


def generate_visual_metaphor(
    algorithm_name: str,
    input_data: str,
    model_name: str = "gemini-3-pro-preview"
) -> Optional[VisualMetaphor]:
    """
    使用 LLM 生成視覺隱喻設計。

    參數:
        algorithm_name: 演算法名稱
        input_data: 輸入資料
        model_name: LLM 模型名稱

    回傳:
        VisualMetaphor 物件，若失敗則回傳 None
    """
    if not API_KEY:
        print("錯誤：找不到 GOOGLE_API_KEY。")
        print("請在專案根目錄建立 .env 檔案並設定 GOOGLE_API_KEY=你的金鑰。")
        return None

    # 建立提示詞
    prompt = _build_visual_metaphor_prompt(algorithm_name, input_data)
    if prompt is None:
        return None

    try:
        # 呼叫 LLM API
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)
        
        print(f"正在使用 {model_name} 生成視覺隱喻設計...")
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}  # 稍微提高創意性
        )

        # 提取回應文字
        content_text = getattr(response, "text", None) or ""
        
        # 解析 JSON
        json_data = _extract_json_from_response(content_text)
        if json_data is None:
            print("錯誤：無法從 LLM 回應中提取有效的 JSON。")
            return None

        # 驗證必要欄位
        required_fields = [
            "algorithm_name", "shapes", "colors", 
            "camera_movements", "layout_strategy", 
            "animation_style", "metaphor_explanation"
        ]
        missing_fields = [f for f in required_fields if f not in json_data]
        if missing_fields:
            print(f"錯誤：JSON 缺少必要欄位：{', '.join(missing_fields)}")
            return None

        # 建立 VisualMetaphor 物件
        visual_metaphor = VisualMetaphor.from_dict(json_data)
        return visual_metaphor

    except Exception as e:
        print(f"生成視覺隱喻時發生錯誤：{e}")
        return None


def main():
    """測試用主程式"""
    print("=== 視覺隱喻設計器測試 ===\n")
    
    algorithm_name = input("請輸入演算法名稱 (例如: Bubble Sort): ").strip()
    input_data = input("請輸入要處理的資料 (例如: [8, 2, 6, 4]): ").strip()

    if not algorithm_name or not input_data:
        print("錯誤：演算法名稱和輸入資料不能為空。")
        return

    print("\n" + "=" * 50)
    visual_metaphor = generate_visual_metaphor(algorithm_name, input_data)
    print("=" * 50 + "\n")

    if visual_metaphor is None:
        print("❌ 視覺隱喻生成失敗。")
        return

    print("✅ 視覺隱喻生成成功！\n")
    print("=" * 50)
    print("生成的設計規格 (JSON):")
    print("=" * 50)
    print(visual_metaphor.to_json())
    print("=" * 50)


if __name__ == "__main__":
    main()
