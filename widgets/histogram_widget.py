# ──────────────────────────────────────────────
# HISTOGRAM WIDGET  (pure Qt – no matplotlib)
# ──────────────────────────────────────────────
from PIL import Image
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget

PAD_L, PAD_R, PAD_T, PAD_B = 6, 6, 6, 0


# ── Background worker ──────────────────────────────────────────────────────

class HistogramWorker(QThread):
    """Computes histogram buckets in a background thread."""
    finished = pyqtSignal(list)  # emits list of (buckets, QColor, label)

    def __init__(self, img: Image.Image, rgb: bool, r_col, g_col, b_col, fg_col):
        super().__init__()
        self._img    = img
        self._rgb    = rgb
        self._r_col  = r_col
        self._g_col  = g_col
        self._b_col  = b_col
        self._fg_col = fg_col

    def run(self):
        if self._rgb:
            arr = self._img.convert("RGB").tobytes()
            r, g, b = [0] * 256, [0] * 256, [0] * 256
            for i in range(0, len(arr), 3):
                r[arr[i]]     += 1
                g[arr[i + 1]] += 1
                b[arr[i + 2]] += 1
            channels = [
                (b, self._b_col, "B"),
                (g, self._g_col, "G"),
                (r, self._r_col, "R"),
            ]
        else:
            arr = self._img.convert("L").tobytes()
            luma = [0] * 256
            for v in arr:
                luma[v] += 1
            channels = [(luma, self._fg_col, "L")]

        self.finished.emit(channels)


# ── Widget ─────────────────────────────────────────────────────────────────

class HistogramWidget(QWidget):
    def __init__(self, img: Image.Image, rgb=True, hist_type="step",
                 dark=True, size=(390, 350), bg=None, fg=None, show_grid=True):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hover_x  = None
        self._channels = []
        self._loading  = True
        self._rgb      = rgb   # current mode – toggled on click

        if bg is None:
            bg = "#1d2021" if dark else "#dce0e8"
        if fg is None:
            fg = "#ebdbb2" if dark else "#4c4f69"

        self._bg     = QColor(bg)
        self._fg     = QColor(fg)
        self._filled = (hist_type == "bar")
        self._show_grid = show_grid

        bg_color = QColor(bg)
        is_dark  = (bg_color.red() + bg_color.green() + bg_color.blue()) < 384

        if is_dark:
            self._r_col = QColor(240, 80,  80)
            self._g_col = QColor(80,  200, 80)
            self._b_col = QColor(80,  140, 255)
        else:
            self._r_col = QColor(180, 30,  30)
            self._g_col = QColor(30,  130, 30)
            self._b_col = QColor(30,  80,  180)

        # store thumb for re-use when toggling mode
        self._thumb = img.copy()
        self._thumb.thumbnail((256, 256), Image.LANCZOS)

        self._worker = None
        self._show_grid = show_grid
        self._start_worker()
        self.setFixedSize(*size)

    # ── worker ─────────────────────────────────────────────────────────────

    def _start_worker(self):
        self._loading = True
        self._channels = []
        self.update()
        # stop previous worker if still running
        if self._worker and self._worker.isRunning():
            self._worker.finished.disconnect()
            self._worker.quit()
            self._worker.wait()
        self._worker = HistogramWorker(
            self._thumb, self._rgb,
            self._r_col, self._g_col, self._b_col, self._fg
        )
        self._worker.finished.connect(self._on_ready)
        self._worker.start()

    def _on_ready(self, channels):
        self._channels = channels
        self._loading  = False
        self.update()

    # ── mouse ──────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._rgb = not self._rgb
            self._start_worker()

    def mouseMoveEvent(self, event):
        self._hover_x = event.position().x()
        self.update()

    def leaveEvent(self, _event):
        self._hover_x = None
        self.update()

    # ── painting ───────────────────────────────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        plot_w = w - PAD_L - PAD_R
        plot_h = h - PAD_T - PAD_B

        p.fillRect(0, 0, w, h, self._bg)

        if self._loading:
            self._draw_loading(p, w, h)
            p.end()
            return

        global_max = max(max(buckets) for buckets, _, _l in self._channels) or 1

        # grid below histogram
        if self._show_grid:
            self._draw_grid(p, plot_w, plot_h)

        for buckets, color, _label in self._channels:
            if self._filled:
                self._draw_filled(p, buckets, color, PAD_L, PAD_T, plot_w, plot_h, global_max)
            else:
                self._draw_step(p, buckets, color, PAD_L, PAD_T, plot_w, plot_h, global_max)

        # mode indicator – small label in bottom-right corner
        self._draw_mode_label(p, w, h)

        if self._hover_x is not None:
            self._draw_crosshair(p, plot_w, plot_h, global_max)

        p.end()

    def _draw_grid(self, p, plot_w, plot_h):
        """Subtle horizontal and vertical grid lines."""
        grid_col = QColor(self._fg)
        grid_col.setAlpha(18)
        pen = QPen(grid_col)
        pen.setWidth(1)
        p.setPen(pen)

        # horizontal lines at 25%, 50%, 75%
        for frac in (0.25, 0.50, 0.75):
            y = int(PAD_T + plot_h * (1.0 - frac))
            p.drawLine(PAD_L, y, PAD_L + plot_w, y)

        # vertical lines at brightness 64, 128, 192
        for val in (64, 128, 192):
            x = int(PAD_L + val * plot_w / 256)
            p.drawLine(x, PAD_T, x, PAD_T + plot_h)

        # subtle percent labels on horizontal lines
        label_col = QColor(self._fg)
        label_col.setAlpha(35)
        p.setPen(label_col)
        p.setFont(QFont("Segoe UI", 7))
        fm = p.fontMetrics()
        for frac, label in ((0.25, "25%"), (0.50, "50%"), (0.75, "75%")):
            y = int(PAD_T + plot_h * (1.0 - frac))
            p.drawText(PAD_L + 3, y - 2, label)

        # subtle brightness labels on vertical lines
        for val in (64, 128, 192):
            x = int(PAD_L + val * plot_w / 256)
            label = str(val)
            lw = fm.horizontalAdvance(label)
            p.drawText(x - lw // 2, PAD_T + plot_h - 4, label)

    def _draw_loading(self, p, w, h):
        c = QColor(self._fg)
        c.setAlpha(80)
        p.setPen(c)
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "Loading…")

    def _draw_mode_label(self, p, w, h):
        """Small RGB / LUM label in bottom-right so user knows current mode."""
        label = "RGB" if self._rgb else "LUM"
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        lw = fm.horizontalAdvance(label) + 8
        lh = fm.height() + 4
        bx = w - lw - 6
        by = h - lh - 4

        box_bg = QColor(self._bg)
        box_bg.setAlpha(180)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(box_bg)
        p.drawRoundedRect(bx, by, lw, lh, 3, 3)

        c = QColor(self._fg)
        c.setAlpha(140)
        p.setPen(c)
        p.drawText(bx + 4, by + fm.ascent() + 2, label)

    # ── crosshair + tooltip ────────────────────────────────────────────────

    def _draw_crosshair(self, p, plot_w, plot_h, global_max):
        mx = self._hover_x
        if mx < PAD_L or mx > PAD_L + plot_w:
            return

        bucket = int((mx - PAD_L) / plot_w * 256)
        bucket = max(0, min(255, bucket))

        line_col = QColor(self._fg)
        line_col.setAlpha(80)
        pen = QPen(line_col)
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.drawLine(int(mx), PAD_T, int(mx), PAD_T + plot_h)

        lines  = [f"Value: {bucket}"]
        colors = [self._fg]
        for buckets, color, label in self._channels:
            lines.append(f"{label}: {buckets[bucket]:,}")
            colors.append(color)

        font = QFont("Segoe UI", 9)
        p.setFont(font)
        fm     = p.fontMetrics()
        line_h = fm.height() + 2
        box_w  = max(fm.horizontalAdvance(l) for l in lines) + 16
        box_h  = len(lines) * line_h + 10

        bx = int(mx) + 10
        if bx + box_w > self.width() - 4:
            bx = int(mx) - box_w - 10
        by = PAD_T + 8

        box_bg = QColor(self._bg)
        box_bg.setAlpha(220)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(box_bg)
        p.drawRoundedRect(bx, by, box_w, box_h, 4, 4)

        border_col = QColor(self._fg)
        border_col.setAlpha(60)
        p.setPen(QPen(border_col))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(bx, by, box_w, box_h, 4, 4)

        ty = by + 6 + fm.ascent()
        for i, (line, color) in enumerate(zip(lines, colors)):
            c = QColor(color)
            c.setAlpha(255)
            p.setPen(c)
            p.drawText(bx + 8, int(ty + i * line_h), line)

    # ── histogram draw modes ───────────────────────────────────────────────

    def _draw_step(self, p, buckets, color, ox, oy, pw, ph, max_val):
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

    def _draw_filled(self, p, buckets, color, ox, oy, pw, ph, max_val):
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