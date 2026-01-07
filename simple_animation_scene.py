from manim import *
import os
import ast

# ===== 共用字型與顏色設定 =====
DEFAULT_LATIN_FONT = "Consolas"

# 一些常見顏色（子類別可自由使用或覆寫）
DEFAULT_COLOR = BLUE_E
COMPARE_COLOR = YELLOW
SWAP_COLOR = GREEN
PIVOT_COLOR = RED
SORTED_COLOR = GRAY_B

# 統一控制每個步驟的停頓時間（秒）
STEP_WAIT = 2.0   # 一般步驟暫停時間
SHORT_WAIT = 0.75  # 短暫停頓


class SimpleAnimationScene(Scene):
    """
    SimpleAnimationScene
    -------------------
    純動畫模式的基礎類別，提供全螢幕動畫空間。
    
    與 BaseAlgorithmScene 不同，此類別：
      - 沒有 pseudocode、animation、info 三面板配置
      - 全螢幕可用於動畫
      - 更簡單的介面，只需實作 run_algorithm_visual()
      - 仍支援視覺隱喻設計規格
    
    子類別必須實作：
      - run_algorithm_visual(self) -> None
    
    子類別可選擇實作（hook）：
      - get_input_data(self)
      - setup_animation(self)
    
    子類別可直接使用：
      - self.input_data
    """

    # 預設索引指標樣式（子類別可覆寫）
    POINTER_COLOR = MAROON_B
    POINTER_FONT_SIZE = 24

    def construct(self):
        # 1) 取得輸入資料（預設為空 list，子類別可 override）
        self.input_data = self.get_input_data()

        # 2) 讓子類別進行初始設定（若需要）
        self.setup_animation()

        # 3) 執行演算法動畫（子類別必須實作）
        self.run_algorithm_visual()

    # ========= 子類別需 / 可 override 的介面 =========

    def run_algorithm_visual(self):
        """子類別必須在此實作演算法動畫邏輯。"""
        raise NotImplementedError("Subclasses must implement run_algorithm_visual().")

    def get_input_data(self):
        """
        預設從環境變數讀取使用者輸入資料。
        子類別可 override 以自訂解析邏輯。
        """
        input_str = os.environ.get("ALGO_USER_INPUT_DATA", "[]")
        try:
            return ast.literal_eval(input_str)
        except (ValueError, SyntaxError):
            print(f"警告：無法解析輸入資料 '{input_str}'，使用空列表。")
            return []

    def setup_animation(self):
        """
        給子類別的 hook：可在此進行初始設定。
        預設不做任何事。
        """
        pass

    # ===================== 共用索引指標 helper =====================
    def _create_index_pointer(self, label_text: str, position: str = "bottom") -> VGroup:
        """
        統一建立索引指標（例如 i, j, left, right）。

        參數
        ------
        label_text
            顯示在指標上的標籤文字（例如 "i", "j", "left"）。
        position
            - "bottom": 指標放在陣列下方，三角形朝上指向陣列
            - "top"   : 指標放在陣列上方，三角形朝下指向陣列

        使用說明
        --------
        - 建立後請搭配 `next_to` 將整個 VGroup 擺到對應元素附近，
          不要自行旋轉 Triangle，以避免方向錯亂。
        """
        pointer = Triangle(
            color=self.POINTER_COLOR,
            fill_opacity=1.0,
        ).scale(0.2)

        label = Text(
            label_text,
            font_size=self.POINTER_FONT_SIZE,
            color=self.POINTER_COLOR,
        )

        if position == "bottom":
            # 預設 Triangle 朝上 → 放在陣列下方即可指向陣列
            label.next_to(pointer, UP, buff=0.1)
        elif position == "top":
            # 在陣列上方時，三角形需朝下指向陣列
            pointer.rotate(PI)
            label.next_to(pointer, DOWN, buff=0.1)
        else:
            raise ValueError("position must be 'top' or 'bottom'")

        pointer_group = VGroup(pointer, label)
        pointer_group.pointer_triangle = pointer
        pointer_group.pointer_position = position
        return pointer_group

    def _pointer_target_point(self, pointer: VGroup, target: Mobject, buff: float = 0.2) -> np.ndarray:
        """
        取得將指標尖端對準 target 後，整個指標 VGroup 應該移動到的中心座標。

        - pointer: 由 `_create_index_pointer` 建立的 VGroup
        - target : 要指向的 Mobject（例如陣列中的某個方塊）
        - buff   : 指標尖端與 target 之間的額外距離
        """
        position = getattr(pointer, "pointer_position", "bottom")
        triangle = getattr(pointer, "pointer_triangle", pointer.submobjects[0] if pointer.submobjects else pointer)

        if position == "bottom":
            anchor_point = target.get_bottom()
            pointer_tip = triangle.get_top()
            direction = DOWN
        else:
            anchor_point = target.get_top()
            pointer_tip = triangle.get_bottom()
            direction = UP

        # pointer 的中心與尖端之間的向量，移動時需加回來
        offset = pointer.get_center() - pointer_tip
        return anchor_point + direction * buff + offset

    def _move_pointer_to(self, pointer: VGroup, target: Mobject, buff: float = 0.2):
        """
        立即把指標移到 target 旁，尖端保持指向 target。
        （若要動畫移動，請使用 `pointer.animate.move_to(self._pointer_target_point(...))`）
        """
        pointer.move_to(self._pointer_target_point(pointer, target, buff=buff))
