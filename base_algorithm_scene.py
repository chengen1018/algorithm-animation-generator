from manim import *

# ===== 共用字型與顏色設定（與具體演算法邏輯解耦） =====
DEFAULT_LATIN_FONT = "Consolas"  # 預設等寬字型，方便顯示 pseudocode
INFO_FONT = DEFAULT_LATIN_FONT

# 一些常見顏色（子類別可自由使用或覆寫）
DEFAULT_COLOR = BLUE_E
COMPARE_COLOR = YELLOW
SWAP_COLOR = GREEN
PIVOT_COLOR = RED
SORTED_COLOR = GRAY_B

PANEL_STROKE = GRAY_C
PSEUDO_FONT_SIZE = 28
INFO_FONT_SIZE = 28

# 統一控制每個步驟的停頓時間（秒）
STEP_WAIT = 2.0   # 一般步驟暫停時間
SHORT_WAIT = 0.75  # 短暫停頓


class BaseAlgorithmScene(Scene):
    """
    BaseAlgorithmScene (三面板模式)
    -------------------
    統一版面配置：
      - 左側：演算法 pseudocode
      - 右上：動畫區（子類別負責在此建立與操作物件）
      - 右下：info panel（當前步驟文字說明）
    
    此類別適用於完整模式，包含 pseudocode、動畫和解釋。
    若只需要純動畫，請使用 SimpleAnimationScene。

    子類別必須實作：
      - get_pseudocode_lines(self) -> list[str]
      - run_algorithm_visual(self) -> None

    子類別可選擇實作（hook）：
      - get_input_data(self)
      - setup_animation_panel(self)
      - before_algorithm_visual(self)
      - after_algorithm_visual(self)

    子類別可直接使用：
      - self._pc_highlight(line_index)
      - self._pc_clear_highlight()
      - self._info_push(message)
      - self._fit_into_panel(mobject, panel, pad)
      - self.pseudo_panel / self.anim_panel / self.info_panel
      - self.pseudocode_group  (Paragraph)
    """

    # 預設索引指標樣式（子類別可覆寫）
    POINTER_COLOR = MAROON_B
    POINTER_FONT_SIZE = 24

    def construct(self):
        # 1) 取得輸入資料（預設為空 list，子類別可 override）
        self.input_data = self.get_input_data()

        # 2) 建立三大 panel 版面
        self._create_layout()

        # 3) 建立左側 pseudocode
        code_lines = self.get_pseudocode_lines()
        self._build_pseudocode(code_lines)

        # 4) 讓子類別在動畫 panel 放初始物件（若需要）
        self.setup_animation_panel()

        # 5) 建立 info panel（右下）
        self._init_info_panel()

        # 6) 前置 hook
        self.before_algorithm_visual()

        # 7) 執行演算法動畫（子類別必須實作）
        self.run_algorithm_visual()

        # 8) 後置 hook
        self.after_algorithm_visual()

    # ========= 子類別需 / 可 override 的介面 =========

    def get_pseudocode_lines(self) -> list[str]:
        """子類別必須回傳 pseudocode 行文字列表。"""
        raise NotImplementedError("Subclasses must implement get_pseudocode_lines().")

    def run_algorithm_visual(self):
        """子類別必須在此實作演算法動畫邏輯。"""
        raise NotImplementedError("Subclasses must implement run_algorithm_visual().")

    def get_input_data(self):
        """預設沒有特別的輸入資料，子類別可 override。"""
        return []

    def setup_animation_panel(self):
        """
        給子類別的 hook：可在此於 self.anim_panel 內建立初始 Mobjects。
        預設不做任何事。
        """
        pass

    def before_algorithm_visual(self):
        """在演算法動畫開始前的 hook（例如顯示說明文字）。"""
        pass

    def after_algorithm_visual(self):
        """在演算法動畫結束後的 hook（例如顯示結語）。"""
        pass

    # ===================== layout / panels =====================
    def _create_layout(self):
        """
        Left: pseudocode panel
        Right: animation panel (top) + info panel (bottom)
        """
        pseudo_width, pseudo_height = 5.8, 6.6
        anim_width, anim_height = 8.2, 5.2
        info_width, info_height = anim_width, 1.9
        GAP_COL = 0.6
        GAP_ROW_RIGHT = 0.4
        PANEL_PAD = 0.28

        self.pseudo_panel = RoundedRectangle(
            corner_radius=0.5,
            width=pseudo_width,
            height=pseudo_height,
            color=PANEL_STROKE,
        )
        self.anim_panel = Rectangle(
            width=anim_width, height=anim_height, color=PANEL_STROKE
        )
        self.info_panel = RoundedRectangle(
            corner_radius=0.35,
            width=info_width,
            height=info_height,
            color=PANEL_STROKE,
        )

        right_column = VGroup(self.anim_panel, self.info_panel).arrange(
            DOWN, buff=GAP_ROW_RIGHT, aligned_edge=LEFT
        )
        full_layout = VGroup(self.pseudo_panel, right_column).arrange(
            RIGHT, buff=GAP_COL
        )

        # 置中，若過寬則縮放
        full_layout.move_to(ORIGIN)
        max_width = config.frame_width - 0.6
        if full_layout.width > max_width:
            full_layout.scale(max_width / full_layout.width)

        self.add(full_layout)
        self._panel_pad = PANEL_PAD

    # ===================== left: pseudocode =====================
    def _build_pseudocode(self, code_lines: list[str]):
        """
        根據給定的 code_lines 建立 Paragraph，放入左側 pseudocode panel。
        """
        para = Paragraph(
            *code_lines,
            line_spacing=0.5,
            alignment="left",
            font=DEFAULT_LATIN_FONT,
            font_size=PSEUDO_FONT_SIZE,
        )
        para.next_to(self.pseudo_panel.get_top(), DOWN, buff=self._panel_pad)
        para.align_to(self.pseudo_panel, LEFT).shift(RIGHT * self._panel_pad)
        self._fit_into_panel(para, self.pseudo_panel, pad=self._panel_pad)

        self.pseudocode_group = para
        self.add(self.pseudocode_group)
        self._init_pseudocode_highlighter()

    # ===================== right-bottom: single info panel =====================
    def _init_info_panel(self):
        """建立 info_text 物件，往後只更新內容。"""
        self.info_lines = []  # 累積目前要顯示的多行文字
        # 使用非空字元作為 placeholder 避免 Manim 0.19 空字串崩潰
        self.info_text = Text(
            ".",
            font=INFO_FONT,
            font_size=INFO_FONT_SIZE,
            line_spacing=0.5,
        )
        self.info_text.set_opacity(0)  # 先隱藏
        self._layout_info_text(initial=True)

    def _layout_info_text(self, initial: bool = False):
        """將 info_text 放入 info_panel 並做 shrink-to-fit。"""
        raw = "\n".join(self.info_lines) if self.info_lines else ""
        is_empty = raw.strip() == ""
        content = raw if not is_empty else "."

        new_obj = Text(
            content,
            font=INFO_FONT,
            font_size=INFO_FONT_SIZE,
            line_spacing=0.5,
        )
        if is_empty:
            new_obj.set_opacity(0)

        # shrink-to-fit within the panel inner box（只縮小不放大）
        max_w = self.info_panel.width - 2 * self._panel_pad
        max_h = self.info_panel.height - 2 * self._panel_pad
        scale = 1.0
        scale = min(scale, max_w / new_obj.width, max_h / new_obj.height)
        new_obj.scale(scale)

        # 放在 info panel 內的左上角
        new_obj.next_to(self.info_panel.get_top(), DOWN, buff=self._panel_pad)
        new_obj.align_to(self.info_panel, LEFT).shift(RIGHT * self._panel_pad)

        if initial:
            self.info_text = new_obj
            self.add(self.info_text)
        else:
            self.play(ReplacementTransform(self.info_text, new_obj), run_time=0.25)
            self.info_text = new_obj

    def _info_push(self, message: str):
        """
        顯示目前步驟的說明：
          - message: 描述「現在」演算法在做什麼
        """
        self.info_lines = [message]
        self._layout_info_text()

    # ===================== fit into a panel (shrink only, then center) =====================
    def _fit_into_panel(self, mob: Mobject, panel: Mobject, pad: float = 0.25):
        max_w = panel.width - 2 * pad
        max_h = panel.height - 2 * pad
        scale_factor = 1.0
        if mob.width > max_w:
            scale_factor = min(scale_factor, max_w / mob.width)
        if mob.height > max_h:
            scale_factor = min(scale_factor, max_h / mob.height)
        if scale_factor < 1.0:
            mob.scale(scale_factor)
        # 將物件預設置中到目標 panel（子類別如需特殊位置，可在呼叫後再自行 move_to）
        mob.move_to(panel.get_center())

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

    # ===================== pseudocode highlighter =====================
    def _init_pseudocode_highlighter(self):
        """建立一個可重用的矩形，用來高亮目前 pseudocode 行。"""
        # 找第一個非空行作為初始 anchor
        initial_idx = 0
        for idx, line in enumerate(self.pseudocode_group.submobjects):
            if line.width > 0.01:
                initial_idx = idx
                break
        target = self.pseudocode_group[initial_idx]
        self.pseudo_highlight = SurroundingRectangle(
            target,
            buff=0.08,
            color=YELLOW,
            fill_opacity=0.18,
            stroke_width=2,
        )
        self.pseudo_highlight.set_opacity(0)  # 先隱藏
        self.add(self.pseudo_highlight)
        self._current_pc_idx = None

    def _pc_highlight(self, line_index: int, run_time: float = 0.4):
        """將高亮框動畫移動到指定 pseudocode 行。"""
        if (
            line_index < 0
            or self.pseudocode_group is None
            or line_index >= len(self.pseudocode_group.submobjects)
        ):
            return

        target = self.pseudocode_group[line_index]
        new_rect = SurroundingRectangle(
            target,
            buff=0.08,
            color=YELLOW,
            fill_opacity=0.18,
            stroke_width=2,
        )
        if self._current_pc_idx is None:
            # 第一次顯示
            self.pseudo_highlight.become(new_rect)
            # 只恢復描邊與半透明填色，避免把文字整個蓋住
            self.pseudo_highlight.set_fill(opacity=0.18)
            self.pseudo_highlight.set_stroke(opacity=1)
        else:
            self.play(Transform(self.pseudo_highlight, new_rect), run_time=run_time)
        self._current_pc_idx = line_index

    def _pc_clear_highlight(self):
        """將 pseudocode 高亮框淡出。"""
        if self._current_pc_idx is not None:
            self.play(FadeOut(self.pseudo_highlight, run_time=0.2))
            self._current_pc_idx = None


