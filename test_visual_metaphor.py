"""
視覺隱喻設計器測試腳本

此腳本用於測試視覺隱喻生成功能，並將結果儲存到檔案。
"""

import sys
from visual_metaphor_designer import generate_visual_metaphor


def test_visual_metaphor(algorithm_name: str, input_data: str, output_file: str = None):
    """
    測試視覺隱喻生成功能
    
    參數:
        algorithm_name: 演算法名稱
        input_data: 輸入資料
        output_file: 輸出檔案路徑（可選）
    """
    print("=" * 60)
    print(f"演算法: {algorithm_name}")
    print(f"輸入資料: {input_data}")
    print("=" * 60)
    print()

    # 生成視覺隱喻
    print("🎨 正在生成視覺隱喻設計...")
    visual_metaphor = generate_visual_metaphor(algorithm_name, input_data)
    
    if visual_metaphor is None:
        print()
        print("=" * 60)
        print("❌ 視覺隱喻生成失敗")
        print("=" * 60)
        sys.exit(1)
    
    # 顯示結果
    print()
    print("=" * 60)
    print("✅ 視覺隱喻生成成功！")
    print("=" * 60)
    print()
    
    json_output = visual_metaphor.to_json()
    print(json_output)
    print()
    
    # 儲存到檔案（如果指定）
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"✅ 設計規格已儲存至: {output_file}")
        except OSError as e:
            print(f"⚠️  儲存檔案失敗: {e}")
    
    print("=" * 60)
    return visual_metaphor


def main():
    """主程式"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "視覺隱喻設計器測試工具" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 預設測試案例
    test_cases = [
        ("Bubble Sort", "[8, 2, 6, 4]"),
        ("Binary Search", "[1, 3, 5, 7, 9, 11, 13, 15]"),
        ("BFS", '{"vertices": [1,2,3,4,5], "edges": [[1,2],[1,3],[2,4],[3,5]]}'),
    ]
    
    print("請選擇測試案例：")
    for i, (algo, data) in enumerate(test_cases, 1):
        print(f"  {i}. {algo} - {data}")
    print(f"  {len(test_cases) + 1}. 自訂輸入")
    print()
    
    try:
        choice = input("請選擇 (1-{}): ".format(len(test_cases) + 1)).strip()
        choice_num = int(choice)
        
        if 1 <= choice_num <= len(test_cases):
            algorithm_name, input_data = test_cases[choice_num - 1]
        elif choice_num == len(test_cases) + 1:
            algorithm_name = input("請輸入演算法名稱: ").strip()
            input_data = input("請輸入資料: ").strip()
            
            if not algorithm_name or not input_data:
                print("❌ 演算法名稱和輸入資料不能為空")
                sys.exit(1)
        else:
            print("❌ 無效的選擇")
            sys.exit(1)
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 已取消")
        sys.exit(1)
    
    print()
    
    # 執行測試
    output_file = f"result/visual_metaphor_{algorithm_name.lower().replace(' ', '_')}.json"
    test_visual_metaphor(algorithm_name, input_data, output_file)


if __name__ == "__main__":
    main()
