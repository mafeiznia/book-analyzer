"""Book Analyzer — main entry point."""
from pathlib import Path

import flet as ft
from dotenv import load_dotenv

from storage.db import init_db
from providers.manager import provider_manager
from ui.theme import build_theme, register_fonts, OLIVE_PRIMARY
from ui.pages.projects_list import projects_list_view
from ui.pages.project_view import project_view
from ui.pages.settings import settings_view
from services.log_bus import log_bus
from core.settings import get_theme, set_theme

load_dotenv()


def main(page: ft.Page):
    # --- Page setup ---
    page.title = "Book Analyzer"
    page.rtl = True
    current_theme = get_theme()
    theme_mode = ft.ThemeMode.DARK if current_theme == "dark" else ft.ThemeMode.LIGHT
    page.theme_mode = theme_mode
    page.theme = build_theme(theme_mode)
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window.width = 1100
    page.window.height = 750
    page.window.min_width = 800
    page.window.min_height = 600

    register_fonts(page)

    # --- State ---
    state = {"route": "list", "project_id": None}

    # --- Handlers ---
    def go_list():
        state["route"] = "list"
        state["project_id"] = None
        log_bus.set_project(None)
        render()

    def open_project(pid: int | None):
        state["route"] = "project"
        state["project_id"] = pid
        log_bus.set_project(pid)
        render()

    def go_settings():
        state["route"] = "settings"
        render()
        
    def toggle_theme():
        new_theme = "dark" if get_theme() == "light" else "light"
        set_theme(new_theme)
        new_mode = ft.ThemeMode.DARK if new_theme == "dark" else ft.ThemeMode.LIGHT
        page.theme_mode = new_mode
        page.theme = build_theme(new_mode)
        render()
        log_bus.emit("simple", f"🎨 تم تغییر کرد: {'تاریک' if new_theme == 'dark' else 'روشن'}")        

    def _on_project_saved(new_id: int):
        """After a new project is saved, stay on its page."""
        state["project_id"] = new_id
        log_bus.set_project(new_id)
        render()

    # --- Router ---
    def render():
        page.controls.clear()

        if state["route"] == "list":
            page.add(
                projects_list_view(
                    page,
                    on_open_project=lambda pid: open_project(pid),
                    on_new_project=lambda: open_project(None),
                    on_settings=go_settings,
                    on_toggle_theme=toggle_theme,
                )
            )
        elif state["route"] == "project":
            page.add(
                project_view(
                    page,
                    state["project_id"],
                    on_back=go_list,
                    on_saved=_on_project_saved,
                    on_toggle_theme=toggle_theme,
                )
            )
        elif state["route"] == "settings":
            page.add(
                settings_view(
                    page,
                    on_back=go_list,
                    on_toggle_theme=toggle_theme,
                )
            )

        page.update()

    # --- Init ---
    init_db()
    provider_manager.load()
    log_bus.emit("simple", "✅ برنامه راه‌اندازی شد")
    render()


if __name__ == "__main__":
    ft.app(target=main)