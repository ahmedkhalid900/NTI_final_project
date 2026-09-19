from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from qfluentwidgets import (
    CardWidget, StrongBodyLabel, CaptionLabel, SegmentedWidget, ComboBox,
    InfoBar, InfoBarPosition,
)

from . import theme
from .components import SectionHeader, apply_soft_shadow

ACCENT_CHOICES = [
    "#4C9BE8", "#3FB950", "#F0A020", "#B57BEE",
    "#F0618A", "#3AC7C0", "#E5484D", "#8C7BEE",
]


class AccentSwatch(QWidget):
    clicked_color = Signal(str)

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._selected = False
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()

    def mousePressEvent(self, event):
        self.clicked_color.emit(self._color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(3, 3, -3, -3)
        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)
        if self._selected:
            pen_color = QColor("#FFFFFF")
            painter.setPen(pen_color)
            painter.setBrush(Qt.NoBrush)
            outer = self.rect().adjusted(0, 0, -1, -1)
            painter.drawEllipse(outer)


class SettingsPage(QWidget):
    currency_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = theme.load_settings()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(theme.SPACE_LG)

        layout.addWidget(SectionHeader("Settings", "Make it feel like yours"))

        # --- Appearance card ---
        appearance_card = CardWidget()
        appearance_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(appearance_card, blur=18, y_offset=4, alpha=26)
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(22, 20, 22, 20)
        appearance_layout.setSpacing(16)

        appearance_layout.addWidget(StrongBodyLabel("Appearance"))

        theme_row = QHBoxLayout()
        theme_row.addWidget(CaptionLabel("Theme"))
        theme_row.addStretch(1)
        self.theme_segment = SegmentedWidget()
        current_mode = self.settings.get("theme_mode", "Auto")
        for mode in ("Light", "Dark", "Auto"):
            self.theme_segment.addItem(
                routeKey=mode,
                text=mode,
                onClick=lambda checked=False, m=mode: self._on_theme_changed(m),
            )
        self.theme_segment.setCurrentItem(current_mode)
        theme_row.addWidget(self.theme_segment)
        appearance_layout.addLayout(theme_row)

        accent_row = QHBoxLayout()
        accent_row.addWidget(CaptionLabel("Accent color"))
        accent_row.addStretch(1)
        self._swatches = []
        for color in ACCENT_CHOICES:
            swatch = AccentSwatch(color)
            swatch.set_selected(color.lower() == self.settings.get("accent", "").lower())
            swatch.clicked_color.connect(self._on_accent_clicked)
            self._swatches.append(swatch)
            accent_row.addWidget(swatch)
        appearance_layout.addLayout(accent_row)

        layout.addWidget(appearance_card)

        # --- Preferences card ---
        prefs_card = CardWidget()
        prefs_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(prefs_card, blur=18, y_offset=4, alpha=26)
        prefs_layout = QVBoxLayout(prefs_card)
        prefs_layout.setContentsMargins(22, 20, 22, 20)
        prefs_layout.setSpacing(16)

        prefs_layout.addWidget(StrongBodyLabel("Preferences"))

        currency_row = QHBoxLayout()
        currency_row.addWidget(CaptionLabel("Currency symbol"))
        currency_row.addStretch(1)
        self.currency_combo = ComboBox()
        self.currency_combo.addItems(["$", "€", "£", "E£", "﷼", "¥"])
        current_currency = self.settings.get("currency", "$")
        idx = self.currency_combo.findText(current_currency)
        self.currency_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.currency_combo.setFixedWidth(100)
        self.currency_combo.currentTextChanged.connect(self._on_currency_changed)
        currency_row.addWidget(self.currency_combo)
        prefs_layout.addLayout(currency_row)

        layout.addWidget(prefs_card)

        # --- About card ---
        about_card = CardWidget()
        about_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(about_card, blur=18, y_offset=4, alpha=26)
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(22, 20, 22, 20)
        about_layout.setSpacing(4)
        about_layout.addWidget(StrongBodyLabel("About"))
        about_layout.addWidget(CaptionLabel("Expense Tracker · Fluent design · built on your original backend"))
        layout.addWidget(about_card)

        layout.addStretch(1)

    def _persist(self):
        theme.save_settings(self.settings)

    def _notify_restart(self):
        InfoBar.success(
            "Saved",
            "Your changes are saved and will show up next time you open the app.",
            position=InfoBarPosition.TOP, duration=2500, parent=self,
        )

    def _on_theme_changed(self, mode):
        self.settings["theme_mode"] = mode
        self._persist()
        self._notify_restart()

    def _on_accent_clicked(self, color):
        self.settings["accent"] = color
        self._persist()
        for swatch in self._swatches:
            swatch.set_selected(swatch._color.lower() == color.lower())
        self._notify_restart()

    def _on_currency_changed(self, symbol):
        self.settings["currency"] = symbol
        self._persist()
        self.currency_changed.emit(symbol)
        self._notify_restart()
