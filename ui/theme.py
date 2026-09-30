"""Theme: dark by default, olive green primary, RTL."""
import flet as ft
from pathlib import Path
import sys

# --- Colors ---
OLIVE_PRIMARY = "#9CAF3F"      # سبز زیتونی روشن (برای تم تاریک)
OLIVE_DARK    = "#6B7A2A"
OLIVE_LIGHT   = "#C3D36E"

BG_DARK       = "#121212"
SURFACE_DARK  = "#1E1E1E"
SURFACE_2     = "#262626"

BG_LIGHT      = "#FAFAF5"
SURFACE_LIGHT = "#FFFFFF"

TEXT_DARK     = "#EAEAEA"
TEXT_LIGHT    = "#1A1A1A"

def _get_font_dir() -> Path:
    """Return the fonts directory.

    - In frozen mode: <_MEIPASS>/assets/fonts
    - In dev mode: <project_root>/assets/fonts
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / "fonts"
    return Path(__file__).parent.parent / "assets" / "fonts"


FONT_DIR = _get_font_dir()


def build_theme(mode: ft.ThemeMode = ft.ThemeMode.DARK) -> ft.Theme:
    """Build the app theme."""
    return ft.Theme(
        color_scheme_seed=OLIVE_PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=OLIVE_PRIMARY,
            secondary=OLIVE_DARK,
            surface=SURFACE_DARK if mode == ft.ThemeMode.DARK else SURFACE_LIGHT,
            on_surface=TEXT_DARK if mode == ft.ThemeMode.DARK else TEXT_LIGHT,
        ),
        font_family="Vazirmatn",
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def register_fonts(page: ft.Page) -> None:
    """Register Vazirmatn font if available."""
    regular = FONT_DIR / "Vazirmatn-Regular.ttf"
    bold = FONT_DIR / "Vazirmatn-Bold.ttf"
    if regular.exists() and bold.exists():
        page.fonts = {
            "Vazirmatn": str(regular),
            "Vazirmatn-Bold": str(bold),
        }