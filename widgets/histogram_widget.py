# ──────────────────────────────────────────────
# HISTOGRAM WIDGET
# ──────────────────────────────────────────────
import numpy as np
from PIL import Image
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class HistogramWidget(FigureCanvas):
    def __init__(self, img: Image.Image, rgb=True, hist_type="step", dark=True, size=(390, 350)):
        bg = "#1d2021" if dark else "#dce0e8"
        fg = "#ebdbb2" if dark else "#4c4f69"

        fig = Figure(figsize=(size[0] / 100, size[1] / 100), tight_layout=True)
        fig.patch.set_facecolor(bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(bg)
        for spine in ax.spines.values():
            spine.set_color(fg)
        ax.tick_params(colors=fg)

        if rgb:
            img_arr = np.array(img.convert("RGB"))
            for i, color in enumerate(['red', 'green', 'blue']):
                ax.hist(img_arr[:, :, i].ravel(), bins=256, range=(0, 256),
                        color=color, alpha=0.5, histtype=hist_type)
        else:
            img_arr = np.array(img.convert("L"))
            ax.hist(img_arr.ravel(), bins=256, range=(0, 256),
                    color=fg, alpha=0.8, histtype=hist_type)

        ax.set_xlim(0, 256)
        ax.set_xticks([])
        ax.set_yticks([])

        super().__init__(fig)
        self.setFixedSize(size[0], size[1])
