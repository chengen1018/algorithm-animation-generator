import os
import sys
import glob
import subprocess
import shutil

from llm_client import generate_manim_code

PROMPT_TEMPLATE_PATH = "prompt_template.txt" # 提示詞模板路徑
GENERATED_CODE_PATH = "generated_scene.py" # LLM 產生的 Manim 程式碼儲存位置
MANIM_CLASS_NAME = "AlgorithmAnimation" # LLM 生成的 Manim 類別名稱


def main():
    # 向使用者取得要生成的演算法名稱與輸入資料
    print("--- 歡迎使用 AI 演算法動畫師 (終端版) ---")
    algorithm_name = input("請輸入演算法名稱 (例如: Bubble Sort): ")
    input_data = input("請輸入要處理的資料 (例如: [8, 2, 6, 4]): ")

    prompt = build_prompt(algorithm_name, input_data)  # 利用演算法名稱與輸入資料建立給 LLM 的完整 prompt
    generated_code = generate_manim_code(prompt)       # 使用 LLM 生成 Manim 程式碼

    # 檢查生成程式碼是否有效，若有效則儲存程式碼、清除之前的輸出、渲染動畫
    if generated_code and "class AlgorithmAnimation(Scene):" in generated_code:
        save_code(generated_code)        # 儲存程式碼
        clean_previous_outputs()         # 清除之前的輸出
        render_animation()               # 渲染動畫
    else:
        print("\n抱歉，無法生成有效的 Manim 程式碼。請檢查您的輸入或 API 金鑰。")


def build_prompt(algorithm: str, data: str) -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{algorithm_name}}", algorithm).replace("{{user_input_data}}", data)


def save_code(code: str):
    with open(GENERATED_CODE_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"AI 生成的程式碼已儲存至: {GENERATED_CODE_PATH}")


def clean_previous_outputs():
    # 刪除本場景的 partial 檔案
    partial_dir = os.path.join(
        "media",
        "videos",
        "generated_scene",
        "720p30",
        "partial_movie_files",
        "AlgorithmAnimation",
    )
    shutil.rmtree(partial_dir, ignore_errors=True)

    # 如需刪除最終影片（同名場景）
    final_mp4 = os.path.join(
        "media", "videos", "generated_scene", "720p30", "AlgorithmAnimation.mp4"
    )
    if os.path.isfile(final_mp4):
        os.remove(final_mp4)

    # 如需清空文字快取（會讓文字重新渲染）
    texts_dir = os.path.join("media", "texts")
    shutil.rmtree(texts_dir, ignore_errors=True)


def _run_manim(quality_flag: str) -> bool:
    # -pqm 等同 -p -qm；若出現相容問題，改用分開旗標
    cmd = ["manim", quality_flag, GENERATED_CODE_PATH, MANIM_CLASS_NAME]
    alt_cmd = ["manim", "-p", "-qm", GENERATED_CODE_PATH, MANIM_CLASS_NAME]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        # 若不支援 -pqm，嘗試以 -p -qm
        if "no such option" in (e.stderr or ""):
            try:
                subprocess.run(alt_cmd, capture_output=True, text=True, check=True)
                return True
            except subprocess.CalledProcessError as e2:
                print(e2.stderr)
                return False
        print(e.stderr)
        return False


def _find_latest_video() -> str | None:
    pattern = os.path.join("media", "videos", "generated_scene", "**", f"{MANIM_CLASS_NAME}.mp4")
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        return None
    return max(matches, key=os.path.getmtime)


def render_animation():
    print("=" * 50)
    print("正在使用 Manim 渲染動畫…（優先 -pqm，失敗回退 -pql）")
    print("這可能需要一點時間，請耐心等候。")
    print("=" * 50)

    if not _run_manim("-pqm"):
        print("改用 -pql 重新嘗試…")
        try:
            subprocess.run(["manim", "-pql", GENERATED_CODE_PATH, MANIM_CLASS_NAME], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print("\n❌ Manim 渲染失敗！ ❌")
            print("AI 生成的程式碼可能存在語法或邏輯錯誤。")
            print("以下是 Manim 的錯誤訊息：")
            print("-" * 50)
            print(e.stderr)
            print("-" * 50)
            return

    video = _find_latest_video()
    if video:
        abs_path = os.path.abspath(video)
        print(f"\n🎉 動畫已生成！影片檔案位於: {abs_path}")
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
