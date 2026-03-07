# ──────────────────────────────────────────────
# HISTOGRAM WIDGET  (pure Qt – no matplotlib)
# ──────────────────────────────────────────────
from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QWidget


def _compute_channel(img: Image.Image, channel: int) -> list[int]:
    """Return a 256-bucket histogram for one RGB channel."""
    arr = img.convert("RGB").tobytes()
    buckets = [0] * 256
    for i in range(channel, len(arr), 3):
        buckets[arr[i]] += 1
    return buckets


def _compute_luma(img: Image.Image) -> list[int]:
    """Return a 256-bucket luminance histogram."""
    arr = img.convert("L").tobytes()
    buckets = [0] * 256
    for v in arr:
        buckets[v] += 1
    return buckets


class HistogramWidget(QWidget):
    def __init__(self, img: Image.Image, rgb=True, hist_type="step",
                 dark=True, size=(390, 350), bg=None, fg=None):
        super().__init__()
        # WA_OpaquePaintEvent tells Qt we paint our own background in paintEvent
        # so the QSS theme rule "QWidget { background-color: ... }" is ignored
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)

        # colours
        if bg is None:
            bg = "#1d2021" if dark else "#dce0e8"
        if fg is None:
            fg = "#ebdbb2" if dark else "#4c4f69"

        self._bg  = QColor(bg)
        self._fg  = QColor(fg)
        self._rgb = rgb
        self._filled = (hist_type == "bar")

        # pre-compute histograms
        thumb = img.copy()
        thumb.thumbnail((256, 256), Image.LANCZOS)

        # Detect if background is dark or light to pick readable channel colors
        bg_color = QColor(bg if bg else "#1d2021")
        is_dark = (bg_color.red() + bg_color.green() + bg_color.blue()) < 384

        if is_dark:
            r_col = QColor(240, 80,  80)
            g_col = QColor(80,  200, 80)
            b_col = QColor(80,  140, 255)
        else:
            r_col = QColor(180, 30,  30)
            g_col = QColor(30,  130, 30)
            b_col = QColor(30,  80,  180)

        if rgb:
            self._channels = [
                (_compute_channel(thumb, 2), b_col),
                (_compute_channel(thumb, 1), g_col),
                (_compute_channel(thumb, 0), r_col),
            ]
        else:
            self._channels = [
                (_compute_luma(thumb), self._fg),
            ]

        self.setFixedSize(*size)

    # ── drawing ────────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 6, 6, 6, 0
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        # background
        p.fillRect(0, 0, w, h, self._bg)

        # find global max for scaling
        global_max = max(
            max(buckets) for buckets, _ in self._channels
        ) or 1

        for buckets, color in self._channels:
            if self._filled:
                self._draw_filled(p, buckets, color,
                                  pad_l, pad_t, plot_w, plot_h, global_max)
            else:
                self._draw_step(p, buckets, color,
                                pad_l, pad_t, plot_w, plot_h, global_max)

        # no border – background color blends with card

        p.end()

    def _draw_step(self, p, buckets, color,
                   ox, oy, pw, ph, max_val):
        """Outline / step histogram – no fill, just the top edge."""
        c = QColor(color)
        c.setAlpha(220)
        p.setPen(c)
        p.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        path.moveTo(ox, oy + ph)
        for i, val in enumerate(buckets):
            x = ox + i * pw / 256
            y = oy + ph - (val / max_val) * ph
            path.lineTo(x, y)
            path.lineTo(x + pw / 256, y)
        path.lineTo(ox + pw, oy + ph)
        path.lineTo(ox, oy + ph)
        p.drawPath(path)

    def _draw_filled(self, p, buckets, color,
                     ox, oy, pw, ph, max_val):
        """Filled histogram – closed polygon along top edge and bottom baseline."""
        c = QColor(color)
        c.setAlpha(160)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)

        path = QPainterPath()
        path.moveTo(ox, oy + ph)
        for i, val in enumerate(buckets):
            x = ox + i * pw / 256
            y = oy + ph - (val / max_val) * ph
            path.lineTo(x, y)
            path.lineTo(x + pw / 256, y)
        path.lineTo(ox + pw, oy + ph)
        path.closeSubpath()
        p.drawPath(path)