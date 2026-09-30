"""Live log panel with simple/technical toggle."""
import flet as ft

from services.log_bus import log_bus


LEVEL_COLORS = {
    "simple": ft.colors.ON_SURFACE,
    "technical": ft.colors.OUTLINE,
}


MAX_LINES = 200


class LogPanel:
    """Live log panel subscribed to LogBus."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.show_technical = False
        self._lines: list[dict] = []

        # --- Log content (a plain Column, no scroll — page handles scroll) ---
        self.log_column = ft.Column(controls=[], spacing=2)

        self.log_container = ft.Container(
            content=self.log_column,
            padding=10,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
            border_radius=6,
        )

        self.toggle = ft.Switch(
            label="نمایش لاگ فنی",
            value=False,
            on_change=self._on_toggle,
            label_style=ft.TextStyle(size=12),
        )

        self.clear_btn = ft.TextButton(
            "پاک کردن",
            icon=ft.icons.CLEAR_ALL,
            on_click=self._on_clear,
        )

        self.copy_btn = ft.TextButton(
            "کپی لاگ",
            icon=ft.icons.COPY_ALL,
            on_click=self._on_copy,
        )

        self.header_row = ft.Row(
            [
                ft.Icon(ft.icons.TERMINAL, size=16, color=ft.colors.PRIMARY),
                ft.Text("لاگ زنده", size=13, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                self.toggle,
                self.copy_btn,
                self.clear_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.control = ft.Container(
            content=ft.Column(
                [self.header_row, self.log_container],
                spacing=6,
            ),
            padding=10,
        )

        # Subscribe
        log_bus.subscribe(self._on_event)
        for ev in log_bus.get_history():
            self._lines.append(ev)
        self._refresh_view()

    # --- Event handling ---
    def _on_event(self, event: dict) -> None:
        self._lines.append(event)
        if len(self._lines) > MAX_LINES:
            self._lines = self._lines[-MAX_LINES:]
        self._refresh_view()

    def _refresh_view(self) -> None:
        self.log_column.controls.clear()

        for ev in self._lines:
            level = ev.get("level", "simple")
            if level == "technical" and not self.show_technical:
                continue

            ts = ev.get("time", "")
            msg = ev.get("message", "")
            color = LEVEL_COLORS.get(level, ft.colors.ON_SURFACE)
            prefix = "  " if level == "technical" else ""

            self.log_column.controls.append(
                ft.Text(
                    f"[{ts}] {prefix}{msg}",
                    size=11 if level == "technical" else 12,
                    color=color,
                    font_family="Consolas" if level == "technical" else None,
                    selectable=True,
                )
            )

        try:
            self.page.update()
        except Exception:
            pass

    def _on_toggle(self, e):
        self.show_technical = e.control.value
        self._refresh_view()

    def _on_clear(self, e):
        self._lines.clear()
        self._refresh_view()

    def _on_copy(self, e):
        """Copy visible log lines to clipboard."""
        try:
            import pyperclip
            lines = []
            for ev in self._lines:
                level = ev.get("level", "simple")
                if level == "technical" and not self.show_technical:
                    continue
                ts = ev.get("time", "")
                msg = ev.get("message", "")
                lines.append(f"[{ts}] {msg}")
            text = "\n".join(lines) if lines else "(لاگ خالی)"
            pyperclip.copy(text)
            self.page.open(ft.SnackBar(ft.Text(f"✅ {len(lines)} خط کپی شد")))
        except ImportError:
            self.page.open(ft.SnackBar(ft.Text("⚠️ pyperclip نصب نیست")))
        except Exception as ex:
            self.page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
        self.page.update()

    def dispose(self) -> None:
        log_bus.unsubscribe(self._on_event)