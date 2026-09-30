"""About dialog — app info, author, tech stack."""
import webbrowser

import flet as ft

from core.about_info import (
    APP_NAME,
    APP_TAGLINE_FA,
    APP_VERSION,
    AUTHOR_EMAIL,
    AUTHOR_LINKEDIN_URL,
    AUTHOR_NAME_EN,
    AUTHOR_NAME_FA,
    AUTHOR_WEBSITE,
    AUTHOR_WEBSITE_URL,
    COPYRIGHT_HOLDER,
    COPYRIGHT_YEAR,
    GITHUB_URL,
    LICENSE_NAME,
    LOGO_PATH,
    TECH_STACK,
    get_build_date,
)
from ui.theme import OLIVE_PRIMARY


def _open_url(page: ft.Page, url: str) -> None:
    """Open URL in default browser."""
    if not url:
        page.open(ft.SnackBar(ft.Text("⚠️ آدرس تنظیم نشده است")))
        page.update()
        return
    try:
        webbrowser.open(url)
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()


def _copy_to_clipboard(page: ft.Page, text: str, label: str = "متن") -> None:
    """Copy text to clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        page.open(ft.SnackBar(ft.Text(f"✅ {label} کپی شد")))
    except ImportError:
        page.open(ft.SnackBar(ft.Text("⚠️ pyperclip نصب نیست")))
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()


def show_about_dialog(page: ft.Page) -> None:
    """Build and show the About dialog."""

    # --- Logo ---
    logo_control: ft.Control
    if LOGO_PATH.exists():
        logo_control = ft.Container(
            content=ft.Image(
                src=str(LOGO_PATH),
                width=96,
                height=96,
                fit=ft.ImageFit.CONTAIN,
            ),
            width=96,
            height=96,
            alignment=ft.alignment.center,
        )
    else:
        logo_control = ft.Container(
            content=ft.Icon(ft.Icons.MENU_BOOK, size=64, color=OLIVE_PRIMARY),
            width=96,
            height=96,
            alignment=ft.alignment.center,
        )

    # --- Header ---
    header = ft.Column(
        [
            logo_control,
            ft.Container(height=4),
            ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"نسخه {APP_VERSION}", size=13, color=ft.Colors.OUTLINE),
            ft.Container(height=4),
            ft.Text(APP_TAGLINE_FA, size=13, italic=True, color=ft.Colors.ON_SURFACE_VARIANT),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=2,
    )

    # --- Author section ---
    def _author_button(icon, label, on_click) -> ft.Control:
        return ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(icon, size=16, color=OLIVE_PRIMARY),
                    ft.Text(label, size=12),
                ],
                spacing=6,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=on_click,
        )

    author_row_buttons = ft.Row(
        [
            _author_button(
                ft.Icons.EMAIL,
                "ایمیل",
                lambda e: _copy_to_clipboard(page, AUTHOR_EMAIL, "ایمیل"),
            ),
            _author_button(
                ft.Icons.LINK,
                "LinkedIn",
                lambda e: _open_url(page, AUTHOR_LINKEDIN_URL),
            ),
            _author_button(
                ft.Icons.LANGUAGE,
                AUTHOR_WEBSITE,
                lambda e: _open_url(page, AUTHOR_WEBSITE_URL),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=4,
    )

    author_block = ft.Container(
        content=ft.Column(
            [
                ft.Text("طراحی و توسعه", size=11, color=ft.Colors.OUTLINE),
                ft.Text(AUTHOR_NAME_FA, size=14, weight=ft.FontWeight.BOLD),
                ft.Text(AUTHOR_NAME_EN, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=4),
                author_row_buttons,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        padding=10,
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
        border_radius=8,
    )

    # --- Tech stack table ---
    tech_rows = []
    for label, value in TECH_STACK:
        tech_rows.append(
            ft.Row(
                [
                    ft.Text(
                        f"{label}:",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        width=120,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    ft.Text(
                        value,
                        size=11,
                        selectable=True,
                        expand=True,
                        text_align=ft.TextAlign.LEFT,
                    ),
                ],
                rtl=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    # Build date
    build_date = get_build_date()
    tech_rows.append(
        ft.Row(
            [
                ft.Text(
                    "تاریخ ساخت:",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    width=120,
                    text_align=ft.TextAlign.RIGHT,
                ),
                ft.Text(
                    build_date,
                    size=11,
                    selectable=True,
                    expand=True,
                    color=ft.Colors.OUTLINE,
                    text_align=ft.TextAlign.LEFT,
                ),
            ],
            rtl=True,
        )
    )

    tech_block = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.BUILD, size=14, color=OLIVE_PRIMARY),
                        ft.Text("اطلاعات فنی", size=12, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=1),
                *tech_rows,
            ],
            spacing=6,
        ),
        padding=10,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.PRIMARY),
        border_radius=8,
    )

    # --- License / footer ---
    footer_parts = [
        ft.Text(
            f"© {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}",
            size=10,
            color=ft.Colors.OUTLINE,
        ),
        ft.Text(
            f"مجوز: {LICENSE_NAME}",
            size=10,
            color=ft.Colors.OUTLINE,
        ),
    ]

    if GITHUB_URL:
        footer_parts.append(
            ft.TextButton(
                "مخزن GitHub",
                icon=ft.Icons.CODE,
                on_click=lambda e: _open_url(page, GITHUB_URL),
            )
        )

    footer = ft.Column(
        footer_parts,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # --- Content ---
    content = ft.Column(
        [
            header,
            ft.Divider(height=1),
            author_block,
            tech_block,
            ft.Divider(height=1),
            footer,
        ],
        spacing=10,
        tight=True,
        width=380,
        scroll=ft.ScrollMode.AUTO,
    )

    # --- Dialog ---
    dlg = ft.AlertDialog(
        modal=True,
        content=content,
        actions=[
            ft.TextButton(
                "بستن",
                on_click=lambda e: _close(dlg, page),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()


def _close(dlg: ft.AlertDialog, page: ft.Page) -> None:
    dlg.open = False
    page.update()