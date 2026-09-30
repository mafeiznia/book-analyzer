"""Projects list page — with search, delete, and real DB loading."""
import flet as ft

from services.log_bus import log_bus
from storage import repositories as repo
from ui.theme import OLIVE_PRIMARY
from ui.components.about_dialog import show_about_dialog


def projects_list_view(page: ft.Page, on_open_project, on_new_project, on_settings) -> ft.Control:
    """Return the projects list view."""

    # --- State ---
    search_value = {"text": ""}

    # --- Delete confirmation ---
    def ask_delete(project_id: int, title: str):
        def _confirm(ev):
            repo.delete_project(project_id)
            log_bus.emit("simple", f"🗑️ پروژه حذف شد: {title}")
            dlg.open = False
            refresh()
            page.update()

        def _cancel(ev):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("حذف پروژه"),
            content=ft.Text(f"آیا از حذف پروژه «{title}» مطمئن هستید؟\nاین عمل قابل بازگشت نیست."),
            actions=[
                ft.TextButton("انصراف", on_click=_cancel),
                ft.ElevatedButton(
                    "حذف",
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED_400,
                    on_click=_confirm,
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # --- Card builder ---
    def _project_card(row: dict) -> ft.Control:
        # Status badge
        status_map = {
            "draft": ("پیش‌نویس", ft.colors.OUTLINE),
            "analyzing": ("در حال تحلیل", ft.colors.AMBER),
            "done": ("انجام‌شده", ft.colors.GREEN),
            "failed": ("خطا", ft.colors.RED_300),
        }
        status_label, status_color = status_map.get(row["status"], (row["status"], ft.colors.OUTLINE))

        status_badge = ft.Container(
            content=ft.Text(status_label, size=11, color=status_color),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            bgcolor=ft.colors.with_opacity(0.15, status_color),
            border_radius=6,
        )

        # URL count
        url_count = 0
        if row.get("urls"):
            try:
                import json
                url_count = len(json.loads(row["urls"]))
            except Exception:
                url_count = 0

        meta_row = ft.Row(
            [
                status_badge,
                ft.Text(f"🔗 {url_count} لینک", size=11, color=ft.colors.OUTLINE),
                ft.Text(f"🗓️ {row.get('updated_at', '')[:10]}", size=11, color=ft.colors.OUTLINE),
            ],
            spacing=12,
        )

        title_col = ft.Column(
            [
                ft.Text(row["title"] or "(بدون عنوان)", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(row["author"] or "(بدون نویسنده)", size=13, color=ft.colors.OUTLINE),
                ft.Container(height=2),
                meta_row,
            ],
            spacing=2,
            expand=True,
        )

        actions = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.OPEN_IN_NEW,
                    icon_size=18,
                    tooltip="باز کردن",
                    on_click=lambda e, pid=row["id"]: on_open_project(pid),
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_size=18,
                    icon_color=ft.colors.RED_300,
                    tooltip="حذف",
                    on_click=lambda e, pid=row["id"], t=row["title"]: ask_delete(pid, t),
                ),
            ],
            spacing=0,
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [title_col, actions],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=15,
                on_click=lambda e, pid=row["id"]: on_open_project(pid),
                ink=True,
            ),
        )

    # --- Refresh ---
    list_container = ft.Column(spacing=10)

    def refresh():
        rows = repo.list_projects(search_value["text"])
        list_container.controls.clear()

        if not rows:
            empty = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.MENU_BOOK_OUTLINED, size=64, color=ft.colors.OUTLINE),
                        ft.Text(
                            "هیچ پروژه‌ای یافت نشد" if search_value["text"] else "هنوز پروژه‌ای ندارید",
                            size=18,
                        ),
                        ft.Text(
                            "عبارت دیگری را جست‌وجو کنید." if search_value["text"] else "برای شروع روی «پروژه جدید» بزنید.",
                            size=13,
                            color=ft.colors.OUTLINE,
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "پروژه جدید",
                            icon=ft.icons.ADD,
                            on_click=lambda e: on_new_project(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
            list_container.controls.append(empty)
        else:
            for r in rows:
                list_container.controls.append(_project_card(r))

        page.update()

    # --- Search ---
    def on_search_change(e):
        search_value["text"] = e.control.value
        refresh()

    search_field = ft.TextField(
        hint_text="جست‌وجو در عنوان یا نویسنده...",
        prefix_icon=ft.icons.SEARCH,
        border_radius=8,
        on_change=on_search_change,
        dense=True,
    )

        # --- Header ---
    header = ft.Row(
        [
            ft.Text("📚 Book Analyzer", size=26, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.icons.REFRESH,
                tooltip="بروزرسانی لیست",
                on_click=lambda e: refresh(),
            ),
            ft.ElevatedButton(
                "پروژه جدید",
                icon=ft.icons.ADD,
                style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.colors.BLACK),
                on_click=lambda e: on_new_project(),
            ),
            ft.IconButton(
                icon=ft.icons.INFO_OUTLINE,
                tooltip="درباره برنامه",
                on_click=lambda e: show_about_dialog(page),
            ),
            ft.IconButton(
                icon=ft.icons.SETTINGS,
                tooltip="تنظیمات",
                on_click=lambda e: on_settings(),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    refresh()

    return ft.ListView(
        [
            header,
            search_field,
            ft.Divider(height=1),
            list_container,
        ],
        spacing=10,
        expand=True,
    )