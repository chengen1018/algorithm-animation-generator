import os
import sys
import glob
import subprocess
import shutil
import re
from datetime import datetime

from llm_client import generate_manim_code, fix_manim_code
from visual_metaphor_designer import generate_visual_metaphor

# 模板模式常數
TEMPLATE_MODE_FULL = "full"
TEMPLATE_MODE_SIMPLE = "simple"

# 模板檔案路徑
PROMPT_TEMPLATE_FULL = "prompt_template.txt"
PROMPT_TEMPLATE_SIMPLE = "prompt_template_simple.txt"

# Base Class 檔案路徑
BASE_CLASS_FULL = "base_algorithm_scene.py"
BASE_CLASS_SIMPLE = "simple_animation_scene.py"

# 生成的程式碼路徑
GENERATED_CODE_PATH = "generated_algo_scene.py"
MANIM_CLASS_NAME = "AlgorithmAnimation"

# 設定最大自動修復次數
MAX_RETRIES = 3

# 錯誤紀錄目錄
ERROR_LOG_DIR = "error_logs"


def ensure_error_log_dir() -> None:
    """確保錯誤紀錄目錄存在。"""
    os.makedirs(ERROR_LOG_DIR, exist_ok=True)


def slugify_algorithm_name(name: str) -> str:
    """
    將演算法名稱轉成適合作為檔名的 slug。
    只保留英文小寫、數字與底線，其他字元會被移除。
    """
    name = (name or "").strip().lower()
    # 先把空白轉成底線
    name = re.sub(r"\s+", "_", name)
    # 再移除非 a-z0-9_ 的字元
    name = re.sub(r"[^a-z0-9_]+", "", name)
    return name or "algorithm"


def save_error_snapshot(
    algorithm_name: str, attempt_index: int, code: str, stderr: str
) -> None:
    """
    將「當前版本的 Manim 程式碼」與「對應錯誤訊息」落盤，方便之後分析。

    會在 ERROR_LOG_DIR 底下產生兩個檔案：
      - {slug}_{timestamp}_attempt{n}.py
      - {slug}_{timestamp}_attempt{n}.log
    """
    ensure_error_log_dir()
    slug = slugify_algorithm_name(algorithm_name)
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    base_name = f"{slug}_{ts}_attempt{attempt_index}"

    code_path = os.path.join(ERROR_LOG_DIR, f"{base_name}.py")
    log_path = os.path.join(ERROR_LOG_DIR, f"{base_name}.log")

    try:
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code or "")
    except OSError as e:
        print(f"警告：儲存錯誤程式碼失敗（{code_path}）：{e}")

    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(stderr or "")
    except OSError as e:
        print(f"警告：儲存錯誤日誌失敗（{log_path}）：{e}")

def main():
    # 向使用者取得要生成的演算法名稱與輸入資料
    print("--- 歡迎使用 AI 演算法動畫生成器 ---")
    
    # 選擇模板模式
    print("\n請選擇模板模式:")
    print("1. 完整模式 (pseudocode + animation + explanation)")
    print("2. 純動畫模式 (animation only)")
    
    while True:
        mode_choice = input("選擇 (1/2): ").strip()
        if mode_choice == "1":
            template_mode = TEMPLATE_MODE_FULL
            break
        elif mode_choice == "2":
            template_mode = TEMPLATE_MODE_SIMPLE
            break
        else:
            print("無效的選擇，請輸入 1 或 2。")
    
    algorithm_name = input("\n請輸入演算法名稱 (例如: Bubble Sort): ")
    input_data = input("請輸入要處理的資料 (例如: [8, 2, 6, 4]): ")

    # 【新增】生成視覺隱喻設計
    print("\n" + "=" * 50)
    print("步驟 1: 生成視覺設計方案...")
    print("=" * 50)
    visual_metaphor = generate_visual_metaphor(algorithm_name, input_data)
    
    if visual_metaphor is None:
        print("\n視覺隱喻生成失敗，無法繼續。")
        print("請檢查您的輸入或 API 金鑰設定。")
        return
    
    print("\n視覺設計方案生成成功！")
    print(f"設計隱喻: {visual_metaphor.metaphor_explanation[:80]}...")

    # 建立給 LLM 的完整 prompt；若模板或 Base Class 檔案有問題則提前結束
    print("\n" + "=" * 50)
    print("步驟 2: 建立程式碼生成提示詞...")
    print("=" * 50)
    prompt = build_prompt(algorithm_name, input_data, visual_metaphor, template_mode)
    if prompt is None:
        # build_prompt 已顯示詳細錯誤訊息，這裡直接結束主程式即可
        return

    print("\n" + "=" * 50)
    print("步驟 3: 使用 AI 生成 Manim 程式碼...")
    print("=" * 50)
    generated_code = generate_manim_code(prompt)       # 使用 LLM 生成 Manim 程式碼

    # 檢查生成程式碼是否有效；若有效則進入「執行 → 報錯 → 修正 → 再執行」自動修復迴圈
    if generated_code and "class AlgorithmAnimation" in generated_code:
        print("\n" + "=" * 50)
        print("步驟 4: 渲染動畫...")
        print("=" * 50)
        run_with_auto_fix(algorithm_name, input_data, generated_code)
    else:
        print("\n抱歉，無法生成有效的 Manim 程式碼。請檢查您的輸入或 API 金鑰。")


def build_prompt(algorithm: str, data: str, visual_metaphor, template_mode: str) -> str | None:
    """
    根據使用者輸入、視覺隱喻、模板、Base Class 原始碼組合出給 LLM 的完整提示詞。
    若模板檔或 Base Class 檔案不存在或無法讀取，會印出友善錯誤訊息並回傳 None。
    
    參數:
        algorithm: 演算法名稱
        data: 輸入資料
        visual_metaphor: VisualMetaphor 物件（視覺設計規格）
        template_mode: 模板模式 ("full" 或 "simple")
    """
    # 根據模板模式選擇對應的檔案
    if template_mode == TEMPLATE_MODE_FULL:
        prompt_template_path = PROMPT_TEMPLATE_FULL
        base_class_path = BASE_CLASS_FULL
    else:  # TEMPLATE_MODE_SIMPLE
        prompt_template_path = PROMPT_TEMPLATE_SIMPLE
        base_class_path = BASE_CLASS_SIMPLE
    
    # 讀取提示詞模板
    try:
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"錯誤：找不到提示詞模板檔案：{prompt_template_path}。")
        print("請確認該檔案是否存在於專案根目錄，或檔名是否正確。")
        return None
    except OSError as e:
        print(f"錯誤：讀取提示詞模板檔案時發生問題：{e}")
        return None

    # 讀取 Base Class 的原始碼
    try:
        with open(base_class_path, "r", encoding="utf-8") as f:
            base_code = f.read()
    except FileNotFoundError:
        print(f"錯誤：找不到 Base Class 檔案：{base_class_path}。")
        print(f"請確認該檔案是否存在於專案根目錄，或檔名是否正確。")
        return None
    except OSError as e:
        print(f"錯誤：讀取 Base Class 檔案時發生問題：{e}")
        return None

    # 將視覺隱喻轉換為 JSON 字串
    visual_metaphor_json = visual_metaphor.to_json(indent=2)
    
    return (
        template.replace("{{algorithm_name}}", algorithm)
        .replace("{{user_input_data}}", data)
        .replace("{{base_class_code}}", base_code)
        .replace("{{visual_metaphor_json}}", visual_metaphor_json)
    )


def save_code(code: str):
    with open(GENERATED_CODE_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"AI 生成的程式碼已儲存至: {GENERATED_CODE_PATH}")


def clean_previous_outputs():
    # 刪除本場景的 partial 檔案
    partial_dir = os.path.join(
        "media",
        "videos",
        "generated_algo_scene",
        "720p30",
        "partial_movie_files",
        "AlgorithmAnimation",
    )
    shutil.rmtree(partial_dir, ignore_errors=True)

    # 如需刪除最終影片（同名場景）
    final_mp4 = os.path.join(
        "media", "videos", "generated_algo_scene", "720p30", "AlgorithmAnimation.mp4"
    )
    if os.path.isfile(final_mp4):
        os.remove(final_mp4)

    # 如需清空文字快取（會讓文字重新渲染）
    texts_dir = os.path.join("media", "texts")
    shutil.rmtree(texts_dir, ignore_errors=True)


def run_with_auto_fix(algorithm_name: str, input_data: str, initial_code: str) -> None:
    """
    建立「執行 → 報錯 → LLM 修正 → 再執行」的自動修復迴圈。

    - 會最多進行 1 + MAX_RETRIES 次嘗試（原始程式碼一次 + 最多 MAX_RETRIES 次修正版）。
    - 每次失敗都會將當前版本的程式碼與 stderr 落盤，方便事後分析。
    """
    current_code = initial_code
    attempt = 0

    while True:
        print("=" * 50)
        print(f"第 {attempt + 1} 次嘗試渲染動畫…")
        print("=" * 50)

        # 將目前版本程式碼寫入檔案，並清除舊的輸出
        save_code(current_code)
        clean_previous_outputs()

        # 單次嘗試執行 Manim
        success, stderr = _render_manim_core(input_data)

        if success:
            print(f"\nManim 渲染成功（第 {attempt + 1} 次嘗試）")
            video = _find_latest_video()
            if video:
                abs_path = os.path.abspath(video)
                print(f"動畫已生成，影片檔案位於: {abs_path}")
                try:
                    if sys.platform == "win32":
                        os.startfile(video)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", video])
                    else:
                        subprocess.run(["xdg-open", video])
                except Exception:
                    print("\n無法自動開啟影片，請手動開啟檔案。")
            else:
                print("找不到輸出影片檔案，請檢查 Manim 輸出目錄。")
            break

        # 失敗：先把這一版程式碼與錯誤訊息存起來
        print(f"\nManim 渲染失敗（第 {attempt + 1} 次嘗試）。")
        save_error_snapshot(algorithm_name, attempt, current_code, stderr or "")

        # 已達最大自動修復次數（錯誤詳細內容已寫入 error_logs，不再印出 stderr）
        if attempt >= MAX_RETRIES:
            print("已達最大自動修復次數，仍無法成功渲染。")
            print("詳細錯誤訊息與對應程式碼已儲存在 error_logs 目錄中。")
            break

        # 尚有修復次數，請 LLM 嘗試修正程式碼
        print("嘗試使用 LLM 自動修復程式碼…")
        fixed_code = fix_manim_code(current_code, stderr or "")

        if not fixed_code or "class AlgorithmAnimation" not in fixed_code:
            print("AI 無法提供可用的修正版程式碼，停止自動修復。")
            break

        current_code = fixed_code
        attempt += 1


def _run_manim(quality_flag: str, input_data: str) -> bool:
    """
    執行 manim，並透過環境變數 ALGO_USER_INPUT_DATA
    將使用者輸入字串傳遞給子程序中的 AlgorithmAnimation。
    """
    # -pqm 等同 -p -qm；若出現相容問題，改用分開旗標
    cmd = ["manim", quality_flag, GENERATED_CODE_PATH, MANIM_CLASS_NAME]
    alt_cmd = ["manim", "-p", "-qm", GENERATED_CODE_PATH, MANIM_CLASS_NAME]

    env = os.environ.copy()
    env["ALGO_USER_INPUT_DATA"] = input_data

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, env=env
        )
        # 成功時仍回傳可能存在的 stderr（通常為空字串）
        return True, (result.stderr or "")
    except subprocess.CalledProcessError as e:
        err = e.stderr or ""
        # 若不支援 -pqm，嘗試以 -p -qm
        if "no such option" in err:
            try:
                result2 = subprocess.run(
                    alt_cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env,
                )
                combined = "\n".join(
                    part for part in (err, result2.stderr or "") if part
                )
                return True, combined
            except subprocess.CalledProcessError as e2:
                combined = "\n".join(part for part in (err, e2.stderr or "") if part)
                return False, combined
        return False, err


def _find_latest_video() -> str | None:
    pattern = os.path.join("media", "videos", "generated_algo_scene", "**", f"{MANIM_CLASS_NAME}.mp4")
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def _render_manim_core(input_data: str) -> tuple[bool, str]:
    """
    單次嘗試渲染動畫的核心函式：
      - 直接使用 -pql（低畫質預覽）執行一次 manim。

    回傳：
      - success: 是否成功完成渲染
      - stderr: 這次執行過程中的 stderr 文字（方便傳給 LLM）
    """
    env = os.environ.copy()
    env["ALGO_USER_INPUT_DATA"] = input_data
    try:
        result = subprocess.run(
            ["manim", "-pql", GENERATED_CODE_PATH, MANIM_CLASS_NAME],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        return True, (result.stderr or "")
    except subprocess.CalledProcessError as e:
        return False, (e.stderr or "")


def render_animation(input_data: str):
    """
    保留給單次執行用的封裝函式。
    目前自動化流程會改用 run_with_auto_fix，
    這裡只負責一次渲染與結果顯示。
    """
    print("=" * 50)
    print("正在使用 Manim 渲染動畫…（優先 -pqm，失敗回退 -pql）")
    print("這可能需要一點時間，請耐心等候。")
    print("=" * 50)

    success, stderr = _render_manim_core(input_data)
    if not success:
        print("\nManim 渲染失敗！")
        print("AI 生成的程式碼可能存在語法或邏輯錯誤。")
        print("以下是 Manim 的錯誤訊息：")
        print("-" * 50)
        print(stderr)
        print("-" * 50)
        return

    video = _find_latest_video()
    if video:
        abs_path = os.path.abspath(video)
        print(f"\n動畫已生成，影片檔案位於: {abs_path}")
        try:
            if sys.platform == "win32":
                os.startfile(video)
            elif sys.platform == "darwin":
                subprocess.run(["open", video])
            else:
                subprocess.run(["xdg-open", video])
        except Exception:
            print("\n無法自動開啟影片，請手動開啟檔案。")
    else:
        print("找不到輸出影片檔案，請檢查 Manim 輸出目錄。")


if __name__ == "__main__":
    main()
