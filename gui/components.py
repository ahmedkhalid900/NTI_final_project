"""
Small reusable UI building blocks so every page looks like it belongs
to the same app instead of being styled one-off.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect

from qfluentwidgets import (
    CardWidget, BodyLabel, CaptionLabel, StrongBodyLabel, TitleLabel,
    IconWidget, FluentIcon, isDarkTheme, ProgressBar, MessageBoxBase,
    SubtitleLabel, LineEdit,
)

from . import theme


def apply_soft_shadow(widget: QWidget, blur=24, y_offset=6, alpha=45):
    """A soft drop shadow is most of what makes cards feel 'raised'
    instead of flat rectangles - used on every card in the app."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


class SectionHeader(QWidget):
    """A title + optional subtitle used at the top of every page, so
    the visual rhythm (spacing, font weight) never has to be guessed
    again per page."""

    def __init__(self, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = TitleLabel(title, self)
        layout.addWidget(title_label)

        if subtitle:
            sub = CaptionLabel(subtitle, self)
            sub.setTextColor(QColor("#8A8A93"), QColor("#9A9AA3"))
            layout.addWidget(sub)


class IconBadge(QWidget):
    """A small rounded, tinted square with an icon inside - used as the
    leading visual on cards (budget cards, insight cards) instead of a
    plain icon floating with no anchor."""

    def __init__(self, icon: FluentIcon, color: str, size: int = 40, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(size, size)
        icon_widget = IconWidget(icon, self)
        pad = size // 4
        icon_widget.setGeometry(pad, pad, size - 2 * pad, size - 2 * pad)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(self._color)
        color.setAlpha(38 if not isDarkTheme() else 55)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), theme.RADIUS_SM, theme.RADIUS_SM)
        painter.drawPath(path)
        super().paintEvent(event)


class StatCard(CardWidget):
    """A compact metric card: big value, small caption, optional icon
    badge and accent color bar - the workhorse of the Dashboard."""

    def __init__(self, title: str, value: str, icon: FluentIcon = None,
                 accent: str = theme.COLOR_INFO, parent=None):
        super().__init__(parent)
        self.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(self, blur=20, y_offset=4, alpha=28)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(14)

        if icon is not None:
            outer.addWidget(IconBadge(icon, accent, 44))

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self.value_label = StrongBodyLabel(value, self)
        self.value_label.setStyleSheet("font-size: 22px; font-weight: 700;")
        caption = CaptionLabel(title, self)
        caption.setTextColor(QColor("#8A8A93"), QColor("#9A9AA3"))
        text_col.addWidget(self.value_label)
        text_col.addWidget(caption)
        outer.addLayout(text_col, 1)

    def set_value(self, value: str):
        self.value_label.setText(value)


class EmptyState(QWidget):
    """Shown instead of a blank list/table when there's no data yet -
    turns 'nothing here' into a friendly nudge instead of looking
    broken."""

    def __init__(self, icon: FluentIcon, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        icon_widget = IconWidget(icon, self)
        icon_widget.setFixedSize(56, 56)
        layout.addWidget(icon_widget, 0, Qt.AlignCenter)

        title_label = StrongBodyLabel(title, self)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        sub_label = CaptionLabel(subtitle, self)
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setTextColor(QColor("#8A8A93"), QColor("#9A9AA3"))
        sub_label.setWordWrap(True)
        layout.addWidget(sub_label)

        self.setMinimumHeight(220)


class CategoryDot(QWidget):
    """A tiny colored circle used next to a category name in tables /
    lists, so categories are recognizable by color at a glance."""

    def __init__(self, category: str, size: int = 10, parent=None):
        super().__init__(parent)
        self._color = QColor(theme.color_for_category(category))
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())


class BudgetProgressCard(CardWidget):
    """One budget shown as: icon, name, spent/total, and a color-coded
    progress bar (green -> amber -> red as it approaches/exceeds the
    limit) - the single most important visual on the Dashboard."""

    def __init__(self, name: str, spent: float, total: float, currency: str = "$", parent=None):
        super().__init__(parent)
        self.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(self, blur=18, y_offset=4, alpha=26)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        color = theme.color_for_category(name)
        top_row.addWidget(IconBadge(FluentIcon.PIE_SINGLE, color, 36))

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        name_col.addWidget(StrongBodyLabel(name, self))
        ratio = (spent / total) if total else 0
        status_text = "Over budget" if ratio > 1 else ("Almost there" if ratio > 0.85 else "On track")
        status_color = theme.COLOR_DANGER if ratio > 1 else (theme.COLOR_WARNING if ratio > 0.85 else theme.COLOR_SUCCESS)
        status = CaptionLabel(status_text, self)
        status.setStyleSheet(f"color: {status_color}; font-weight: 600;")
        name_col.addWidget(status)
        top_row.addLayout(name_col, 1)

        amount_label = BodyLabel(f"{currency}{spent:,.2f} / {currency}{total:,.2f}", self)
        top_row.addWidget(amount_label, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addLayout(top_row)

        bar = ProgressBar(self)
        bar.setRange(0, 100)
        bar.setValue(min(100, int(ratio * 100)))
        bar.setFixedHeight(6)
        bar.setCustomBarColor(QColor(status_color), QColor(status_color))
        layout.addWidget(bar)


class EditDialog(MessageBoxBase):
    """A small reusable 'edit' popup: pass a title and a list of
    (field_key, label, current_value) tuples, get back a dict of
    field_key -> new text once the user confirms. Used by both the
    Expenses and Budgets pages so editing an existing row doesn't
    require deleting it and adding it again from scratch."""

    def __init__(self, title: str, fields, parent=None):
        super().__init__(parent)
        self._field_keys = []
        self._inputs = {}

        self.titleLabel = SubtitleLabel(title, self)
        self.viewLayout.addWidget(self.titleLabel)

        for key, label, current_value in fields:
            self._field_keys.append(key)
            row = QVBoxLayout()
            row.setSpacing(4)
            caption = CaptionLabel(label, self)
            caption.setTextColor(QColor("#8A8A93"), QColor("#9A9AA3"))
            row.addWidget(caption)

            line_edit = LineEdit(self)
            line_edit.setText("" if current_value is None else str(current_value))
            row.addWidget(line_edit)

            self._inputs[key] = line_edit
            self.viewLayout.addLayout(row)

        self.widget.setMinimumWidth(360)
        self.yesButton.setText("Save")
        self.cancelButton.setText("Cancel")

    def values(self) -> dict:
        """Call after exec() returns True (user clicked Save)."""
        return {key: widget.text().strip() for key, widget in self._inputs.items()}
