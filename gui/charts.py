"""
Small hand-drawn chart widgets (Qt QPainter only - no matplotlib/
pyqtgraph dependency). Kept intentionally simple: each widget takes
plain data (dicts/lists of numbers) and draws itself in paintEvent.
"""
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath
from PySide6.QtWidgets import QWidget

from . import theme


class DonutChart(QWidget):
    """Category spending breakdown as a donut, with a big number in
    the middle (total spent) - reads at a glance instead of needing a
    legend to be studied first."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # list of (label, value, color)
        self._center_text = ""
        self._center_sub = ""
        self.setMinimumSize(220, 220)

    def set_data(self, totals: dict, center_text: str = "", center_sub: str = ""):
        self._data = [
            (name, amount, theme.color_for_category(name))
            for name, amount in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
            if amount > 0
        ]
        self._center_text = center_text
        self._center_sub = center_sub
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height()) - 20
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        thickness = max(14, int(side * 0.14))
        inner_rect = rect.adjusted(thickness / 2, thickness / 2, -thickness / 2, -thickness / 2)

        total = sum(v for _, v, _ in self._data)

        # Track (background ring) so the donut still reads as a shape
        # even before any data has been drawn on top of it.
        track_pen = QPen(QColor(255, 255, 255, 18) if self._is_dark() else QColor(0, 0, 0, 12))
        track_pen.setWidth(thickness)
        track_pen.setCapStyle(Qt.FlatCap)
        painter.setPen(track_pen)
        painter.drawArc(inner_rect, 0, 360 * 16)

        if total > 0:
            start_angle = 90 * 16
            for _, value, color in self._data:
                span = int(360 * 16 * (value / total))
                pen = QPen(QColor(color))
                pen.setWidth(thickness)
                pen.setCapStyle(Qt.FlatCap)
                painter.setPen(pen)
                painter.drawArc(inner_rect, start_angle, -span)
                start_angle -= span

        # Center text
        painter.setPen(QColor("#F5F5F7") if self._is_dark() else QColor("#1A1A1E"))
        font = QFont()
        font.setPointSize(max(14, side // 11))
        font.setBold(True)
        painter.setFont(font)
        text_rect = rect.adjusted(thickness, thickness, -thickness, -thickness)
        painter.drawText(text_rect, Qt.AlignCenter | Qt.AlignBottom, self._center_text)

        if self._center_sub:
            sub_font = QFont()
            sub_font.setPointSize(max(9, side // 22))
            painter.setFont(sub_font)
            painter.setPen(QColor("#9A9AA3"))
            sub_rect = rect.adjusted(thickness, thickness, -thickness, -thickness)
            painter.drawText(sub_rect, Qt.AlignCenter | Qt.AlignTop, "\n" + self._center_sub)

    def _is_dark(self):
        from qfluentwidgets import isDarkTheme
        return isDarkTheme()


class Sparkline(QWidget):
    """A tiny filled line chart for 'spending over the last N days' -
    gives a sense of trend without the weight of a full chart with
    axes/labels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._values = []
        self._color = theme.COLOR_INFO
        self.setMinimumHeight(64)

    def set_values(self, values, color: str = theme.COLOR_INFO):
        self._values = list(values)
        self._color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if len(self._values) < 2:
            return

        w, h = self.width(), self.height()
        pad = 6
        max_v = max(self._values) or 1
        min_v = min(self._values)
        span = (max_v - min_v) or 1
        step = (w - 2 * pad) / (len(self._values) - 1)

        points = []
        for i, v in enumerate(self._values):
            x = pad + i * step
            y = h - pad - ((v - min_v) / span) * (h - 2 * pad)
            points.append(QPointF(x, y))

        # Filled area under the line
        area = QPainterPath()
        area.moveTo(points[0].x(), h - pad)
        for p in points:
            area.lineTo(p)
        area.lineTo(points[-1].x(), h - pad)
        area.closeSubpath()

        fill_color = QColor(self._color)
        fill_color.setAlpha(45)
        painter.setPen(Qt.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(area)

        # Line on top
        pen = QPen(QColor(self._color))
        pen.setWidth(2)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        path = QPainterPath()
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        painter.drawPath(path)

        # Last point marker
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(self._color))
        painter.drawEllipse(points[-1], 3.5, 3.5)
