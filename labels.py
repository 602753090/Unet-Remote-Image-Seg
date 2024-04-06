import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def create_color_legend(colors, class_names):
    """
    Create and save a color legend.

    Args:
    - colors (list): List of colors, where each color is a tuple (R, G, B).
    - class_names (list): List of class names as strings.

    This function does not return anything.
    """

    assert len(colors) == len(class_names), "Colors and class names lists must have the same length"

    fig, ax = plt.subplots(figsize=(6, 1))
    fig.subplots_adjust(left=0.05, right=0.95, top=0.5, bottom=0.25)

    legend_patches = [mpatches.Patch(color=[c/255 for c in color], label=class_name) for color, class_name in zip(colors, class_names)]

    ax.legend(handles=legend_patches, loc='center', frameon=False, ncol=len(class_names))

    ax.axis('off')

    # plt.savefig('color_legend.png', dpi=300)  # 保存图例为PNG
    plt.show()  # 显示图例

# 定义你的颜色和类名
colors = [
    (0, 0, 0),       # 背景
    (255, 128, 255),     # background
    (128, 128, 128),     # building
    (255, 255, 0),     # road
    (0, 0, 255),   # water
    (255, 0, 0),   # barren
    (0, 128, 0),   # forest
    (0, 255, 0)  # agriculture
]
class_names = ['NONE', 'background', 'building', 'road', 'water', 'barren', 'forest', 'agriculture']

create_color_legend(colors, class_names)
