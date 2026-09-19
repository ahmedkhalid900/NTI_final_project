"""
Central design system for the app.

Nothing in here touches money logic - it only decides how things LOOK:
spacing, corner radius, category colors, fonts. Every page imports from
here instead of hard-coding a color/number itself, so the whole app
stays visually consistent and a single accent-color change (see
settings_page.py) reaches every screen at once.
"""
import colorsys
import json
import os

from PySide6.QtGui import QColor


# ---------------------------------------------------------------------
# Spacing / radius scale (Fluent-ish 4px grid)
# ---------------------------------------------------------------------
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 32

RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16

# ---------------------------------------------------------------------
# Status colors (used for budget health, anomalies, etc.)
# ---------------------------------------------------------------------
COLOR_SUCCESS = "#3FB950"
COLOR_WARNING = "#F0A020"
COLOR_DANGER = "#E5484D"
COLOR_INFO = "#4C9BE8"

# A curated palette used to color categories consistently and
# pleasantly (avoids muddy/neon hashed colors).
_CATEGORY_PALETTE = [
    "#4C9BE8",  # blue
    "#3FB950",  # green
    "#F0A020",  # amber
    "#B57BEE",  # violet
    "#F0618A",  # pink
    "#3AC7C0",  # teal
    "#E5484D",  # red
    "#8C7BEE",  # indigo
    "#D4A373",  # sand
    "#5FA8D3",  # steel blue
]


def color_for_category(name: str) -> str:
    """Deterministic, pleasant color per category name.

    Same category -> always the same color across every page/session,
    without maintaining a manual name->color table (categories are
    free text the user types in).
    """
    if not name:
        return _CATEGORY_PALETTE[0]
    h = sum(ord(c) for c in name) * 2654435761 & 0xFFFFFFFF
    return _CATEGORY_PALETTE[h % len(_CATEGORY_PALETTE)]


def mix_with_theme(hex_color: str, dark: bool, amount: float = 0.15) -> str:
    """Lighten (light mode) or darken (dark mode) a hex color slightly,
    used for hover/pressed states without needing a second color per
    element."""
    c = QColor(hex_color)
    h, l, s = colorsys.rgb_to_hls(c.redF(), c.greenF(), c.blueF())
    l = max(0.0, l - amount) if dark else min(1.0, l + amount)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return QColor.fromRgbF(r, g, b).name()


# ---------------------------------------------------------------------
# Small persisted app settings (accent color / theme mode / currency).
# Lives next to expenses.json / budgets.json but is purely cosmetic -
# deleting settings.json never affects money data.
# ---------------------------------------------------------------------
SETTINGS_PATH = "settings.json"

DEFAULT_SETTINGS = {
    "theme_mode": "Auto",       # Light | Dark | Auto
    "accent": "#4C9BE8",        # hex
    "currency": "$",
}


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
