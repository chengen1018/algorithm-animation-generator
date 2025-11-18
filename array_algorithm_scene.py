from manim import *

from base_algorithm_scene import (
    BaseAlgorithmScene,
    DEFAULT_LATIN_FONT,
    DEFAULT_COLOR,
    COMPARE_COLOR,
    SWAP_COLOR,
    SORTED_COLOR,
)


class ArrayAlgorithmScene(BaseAlgorithmScene):
    """
    預留用的一維陣列演算法 Base：

    目前僅作為設計草稿與 TODO，尚未在專案中實際使用。
    未來若多個演算法（Bubble Sort、Insertion Sort、Quick Sort、Heap Sort⋯）
    都需要類似的「一維陣列方塊 + swap + 高亮」邏輯，可以把共用部分抽到這個類別。

    預計會提供：
      - self.array_data: list[int] 或其他元素
      - self.array_mobjects: list[VGroup]，每個元素是一個方塊 + 文字
      - _create_array_mobjects(arr)
      - _get_swap_animation(i, j)
      - _swap_elements_state(i, j)
      - _highlight_compare(j, on=True)
      - _highlight_swap_pair(i, j, on=True)
      - _mark_sorted(idx)

    層級關係（未來規劃）：
      BaseAlgorithmScene
          ↑
    ArrayAlgorithmScene
          ↑
     QuickSortScene / BubbleSortScene / HeapSortScene / ...
    """

    # TODO: 從 quick_sort_scene.QuickSortScene 中抽取下列共用邏輯：
    #   - BOX_SIZE / BOX_GAP / BOX_FONT_SIZE 等視覺參數（視需求調整為屬性或常數）
    #   - _create_array_mobjects
    #   - _get_swap_animation
    #   - _swap_elements_state
    #   - _highlight_compare
    #   - _highlight_swap_pair
    #   - _mark_sorted
    #
    # 並在 before_algorithm_visual() 中呼叫某個 setup_array(self.input_data)
    # 讓所有一維陣列演算法子類別可以直接繼承與使用。

    pass


