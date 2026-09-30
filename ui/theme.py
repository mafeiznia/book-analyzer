"""Theme: light by default, olive green primary, RTL."""
import flet as ft
from pathlib import Path

# --- Colors ---
OLIVE_PRIMARY = "#9CAF3F"      # سبز زیتونی روشن
OLIVE_DARK    = "#6B7A2A"
OLIVE_LIGHT   = "#C3D36E"

# --- Dark theme (softer) ---
BG_DARK       = "#1A1D18"       # پس‌زمینه نرم‌تر
SURFACE_DARK  = "#232820"       # کارت‌ها
SURFACE_2     = "#2A2F26"

TEXT_DARK     = "#E8EAE4"

# --- Light theme ---
BG_LIGHT      = "#F7F8F3"       # کرم ملایم
SURFACE_LIGHT = "#FFFFFF"
TEXT_LIGHT    = "#1A1D18"

FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"


def build_theme(mode: ft.ThemeMode = ft.ThemeMode.LIGHT) -> ft.Theme:
    """Build the app theme based on mode."""
    if mode == ft.ThemeMode.DARK:
        surface = SURFACE_DARK
        on_surface = TEXT_DARK
    else:
        surface = SURFACE_LIGHT
        on_surface = TEXT_LIGHT

    return ft.Theme(
        color_scheme_seed=OLIVE_PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=OLIVE_PRIMARY,
            secondary=OLIVE_DARK,
            surface=surface,
            on_surface=on_surface,
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