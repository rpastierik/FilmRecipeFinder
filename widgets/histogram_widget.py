# ──────────────────────────────────────────────
# HISTOGRAM WIDGET  (pure Qt – no matplotlib)
# ──────────────────────────────────────────────
from PIL import Image
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget

PAD_L, PAD_R, PAD_T, PAD_B = 6, 6, 6, 0

# Clipping threshold – % of total pixels to trigger indicator
CLIP_THRESHOLD = 0.001


# ── Background worker ──────────────────────────────────────────────────────

class HistogramWorker(QThread):
    """Computes histogram buckets + clipping info in a background thread."""
    finished = pyqtSignal(list, dict)  # channels, clipping

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
            total = len(arr) // 3
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
            # clipping: any channel clipped counts
            shadows_r    = (r[0]   + g[0]   + b[0])   / (total * 3)
            highlights_r = (r[255] + g[255] + b[255]) / (total * 3)
            clipping = {
                "shadows":    shadows_r,
                "highlights": highlights_r,
                "shadow_col":    self._r_col,
                "highlight_col": self._b_col,
            }
        else:
            arr = self._img.convert("L").tobytes()
            total = len(arr)
            luma = [0] * 256
            for v in arr:
                luma[v] += 1
            channels = [(luma, self._fg_col, "L")]
            clipping = {
                "shadows":    luma[0]   / total,
                "highlights": luma[255] / total,
            }

        self.finished.emit(channels, clipping)


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
        self._clipping = {}
        self._loading  = True
        self._rgb      = rgb

        if bg is None:
            bg = "#1d2021" if dark else "#dce0e8"
        if fg is None:
            fg = "#ebdbb2" if dark else "#4c4f69"

        self._bg        = QColor(bg)
        self._fg        = QColor(fg)
        self._filled    = (hist_type == "bar")
        self._show_grid = show_grid

        bg_color = QColor(bg)
        is_dark  = (bg_color.red() + bg_color.green() + bg_color.blue()) < 384

        if is_dark:
            self._r_col = QColor(255, 70,  70)   
            self._g_col = QColor(80,  230, 100)  
            self._b_col = QColor(60,  160, 255)  
        else:
            self._r_col = QColor(210, 40,  40)   
            self._g_col = QColor(30,  160, 50)   
            self._b_col = QColor(30,  90,  210)  

        self._thumb = img.copy()
        self._thumb.thumbnail((256, 256), Image.LANCZOS)

        self._log_scale = False   # toggled by right-click
        self._worker = None
        self._start_worker()
        self.setFixedSize(*size)

    # ── worker ─────────────────────────────────────────────────────────────

    def _start_worker(self):
        self._loading  = True
        self._channels = []
        self._clipping = {}
        self.update()
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

    def _on_ready(self, channels, clipping):
        self._channels = channels
        self._clipping = clipping
        self._loading  = False
        self.update()

    # ── mouse ──────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._rgb = not self._rgb
            self._start_worker()
        elif event.button() == Qt.MouseButton.RightButton:
            self._log_scale = not self._log_scale
            self.update()

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
        import math
        log_max = math.log1p(global_max)

        if self._show_grid:
            self._draw_grid(p, plot_w, plot_h)

        for buckets, color, _label in self._channels:
            if self._filled:
                self._draw_filled(p, buckets, color, PAD_L, PAD_T, plot_w, plot_h, global_max, log_max)
            else:
                self._draw_step(p, buckets, color, PAD_L, PAD_T, plot_w, plot_h, global_max, log_max)

        self._draw_clipping_indicators(p, w, h)
        self._draw_mode_label(p, w, h)

        if self._hover_x is not None:
            self._draw_crosshair(p, plot_w, plot_h, global_max, log_max)

        p.end()

    # ── clipping indicators ────────────────────────────────────────────────

    def _draw_clipping_indicators(self, p, w, h):
        """Triangles in top-left (shadows) and top-right (highlights)."""
        SIZE = 14

        shadows_pct    = self._clipping.get("shadows",    0.0)
        highlights_pct = self._clipping.get("highlights", 0.0)

        self._draw_triangle(
            p,
            x=PAD_L + 2, y=PAD_T + 2,
            size=SIZE,
            tip="top-left",
            active=shadows_pct > CLIP_THRESHOLD,
            pct=shadows_pct,
            active_color=QColor(80, 140, 255),   # blue = shadows clipped
        )

        self._draw_triangle(
            p,
            x=w - PAD_R - 2, y=PAD_T + 2,
            size=SIZE,
            tip="top-right",
            active=highlights_pct > CLIP_THRESHOLD,
            pct=highlights_pct,
            active_color=QColor(240, 80, 80),    # red = highlights clipped
        )

        # tooltip on hover near triangles – shown beside the triangle at top
        if self._hover_x is not None:
            mx = self._hover_x
            # left triangle area
            if mx < PAD_L + SIZE + 6:
                self._draw_clipping_tooltip(
                    p, PAD_L + SIZE + 4, PAD_T + 2,
                    f"Shadows clipped: {shadows_pct * 100:.2f}%",
                    shadows_pct > CLIP_THRESHOLD,
                    QColor(80, 140, 255)
                )
            # right triangle area
            elif mx > w - PAD_R - SIZE - 6:
                self._draw_clipping_tooltip(
                    p, w - PAD_R - SIZE - 4, PAD_T + 2,
                    f"Highlights clipped: {highlights_pct * 100:.2f}%",
                    highlights_pct > CLIP_THRESHOLD,
                    QColor(240, 80, 80),
                    align_right=True
                )

    def _draw_triangle(self, p, x, y, size, tip, active, pct, active_color):
        """
        Draw a right-angle triangle anchored at top corner.
        tip="top-left"  → anchor top-left
        tip="top-right" → anchor top-right
        """
        path = QPainterPath()
        if tip == "top-left":
            path.moveTo(x, y)
            path.lineTo(x + size, y)
            path.lineTo(x, y + size)
        else:
            path.moveTo(x, y)
            path.lineTo(x - size, y)
            path.lineTo(x, y + size)
        path.closeSubpath()

        if active:
            intensity = min(pct / 0.05, 1.0)
            c = QColor(active_color)
            c.setAlpha(int(140 + 115 * intensity))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(c)
        else:
            dim = QColor(self._fg)
            dim.setAlpha(30)
            p.setPen(QPen(dim))
            p.setBrush(Qt.BrushStyle.NoBrush)

        p.drawPath(path)

    def _draw_clipping_tooltip(self, p, x, y, text, active, color, align_right=False):
        """Small tooltip next to clipping triangle."""
        font = QFont("Segoe UI", 8)
        p.setFont(font)
        fm   = p.fontMetrics()
        tw   = fm.horizontalAdvance(text) + 12
        th   = fm.height() + 6

        bx = x - tw if align_right else x
        by = y

        # box background
        box_bg = QColor(self._bg)
        box_bg.setAlpha(210)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(box_bg)
        p.drawRoundedRect(bx, by, tw, th, 3, 3)

        # box border in indicator color
        border = QColor(color)
        border.setAlpha(80 if active else 30)
        p.setPen(QPen(border))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(bx, by, tw, th, 3, 3)

        # text
        tc = QColor(color if active else self._fg)
        tc.setAlpha(200 if active else 80)
        p.setPen(tc)
        p.drawText(bx + 6, by + fm.ascent() + 3, text)

    # ── grid ──────────────────────────────────────────────────────────────

    def _draw_grid(self, p, plot_w, plot_h):
        grid_col = QColor(self._fg)
        grid_col.setAlpha(18)
        pen = QPen(grid_col)
        pen.setWidth(1)
        p.setPen(pen)

        for frac in (0.25, 0.50, 0.75):
            y = int(PAD_T + plot_h * (1.0 - frac))
            p.drawLine(PAD_L, y, PAD_L + plot_w, y)

        for val in (64, 128, 192):
            x = int(PAD_L + val * plot_w / 256)
            p.drawLine(x, PAD_T, x, PAD_T + plot_h)

        label_col = QColor(self._fg)
        label_col.setAlpha(35)
        p.setPen(label_col)
        p.setFont(QFont("Segoe UI", 7))
        fm = p.fontMetrics()
        for frac, label in ((0.25, "25%"), (0.50, "50%"), (0.75, "75%")):
            y = int(PAD_T + plot_h * (1.0 - frac))
            p.drawText(PAD_L + 3, y - 2, label)

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
        mode  = "RGB" if self._rgb else "LUM"
        scale = "LOG" if self._log_scale else "LIN"
        label = f"{mode}  {scale}"
        font = QFont("Segoe UI", 8)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        lw = fm.horizontalAdvance(label) + 10
        lh = fm.height() + 4
        bx = w - lw - 6
        by = h - lh - 4

        box_bg = QColor(self._bg)
        box_bg.setAlpha(180)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(box_bg)
        p.drawRoundedRect(bx, by, lw, lh, 3, 3)

        # draw RGB/LUM part
        c = QColor(self._fg)
        c.setAlpha(140)
        p.setPen(c)
        p.drawText(bx + 5, by + fm.ascent() + 2, mode)

        # draw LOG/LIN part in accent color when active
        sep_x = bx + 5 + fm.horizontalAdvance(mode) + 2
        log_col = QColor(200, 160, 80) if self._log_scale else QColor(self._fg)
        log_col.setAlpha(200 if self._log_scale else 80)
        p.setPen(log_col)
        p.drawText(sep_x + 2, by + fm.ascent() + 2, scale)

    # ── crosshair + tooltip ────────────────────────────────────────────────

    def _draw_crosshair(self, p, plot_w, plot_h, global_max, log_max):
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
        by = PAD_T + 28  # below clipping triangle

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

    def _scale_val(self, val, max_val, log_max):
        """Normalise val to [0,1] using linear or log scale."""
        import math
        if self._log_scale:
            return math.log1p(val) / log_max if log_max else 0.0
        return val / max_val if max_val else 0.0

    # ── histogram draw modes ───────────────────────────────────────────────

    def _draw_step(self, p, buckets, color, ox, oy, pw, ph, max_val, log_max):
        grad = QLinearGradient(0, oy, 0, oy + ph)
        c_top = QColor(color)
        c_top.setAlpha(220)
        c_bot = QColor(color)
        c_bot.setAlpha(60)
        grad.setColorAt(0.0, c_top)
        grad.setColorAt(1.0, c_bot)

        pen = QPen(QBrush(grad), 1.5)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        path = QPainterPath()
        path.moveTo(ox, oy + ph)
        for i, val in enumerate(buckets):
            x = ox + i * pw / 256
            y = oy + ph - self._scale_val(val, max_val, log_max) * ph
            path.lineTo(x, y)
            path.lineTo(x + pw / 256, y)
        path.lineTo(ox + pw, oy + ph)
        path.lineTo(ox, oy + ph)
        p.drawPath(path)

    def _draw_filled(self, p, buckets, color, ox, oy, pw, ph, max_val, log_max):
        grad = QLinearGradient(0, oy, 0, oy + ph)
        c_top = QColor(color)
        c_top.setAlpha(200)
        c_bot = QColor(color)
        c_bot.setAlpha(30)
        grad.setColorAt(0.0, c_top)
        grad.setColorAt(1.0, c_bot)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))

        path = QPainterPath()
        path.moveTo(ox, oy + ph)
        for i, val in enumerate(buckets):
            x = ox + i * pw / 256
            y = oy + ph - self._scale_val(val, max_val, log_max) * ph
            path.lineTo(x, y)
            path.lineTo(x + pw / 256, y)
        path.lineTo(ox + pw, oy + ph)
        path.closeSubpath()
        p.drawPath(path)