"""Settings page: manage providers (add / edit / test / activate / delete)."""
import flet as ft

from providers.manager import provider_manager
from services.log_bus import log_bus
from ui.theme import OLIVE_PRIMARY
from ui.components.about_dialog import show_about_dialog


def settings_view(page: ft.Page, on_back, on_toggle_theme=None) -> ft.Control:
    # --- Refresh ---
    def refresh():
        rows = provider_manager.list_providers()
        cards.controls.clear()
        for row in rows:
            cards.controls.append(_provider_card(row))
        page.update()

    # --- Test handler ---
    async def _do_test(name: str, status_text: ft.Text, test_btn: ft.ElevatedButton):
        test_btn.disabled = True
        status_text.value = "⏳ در حال تست چند مدل..."
        status_text.color = ft.Colors.AMBER
        page.update()

        provider = provider_manager.get(name)
        if provider is None:
            status_text.value = "❌ Provider یافت نشد"
            status_text.color = ft.Colors.RED
            test_btn.disabled = False
            page.update()
            return

        result = await provider.test_connection()
        if result.ok:
            status_text.value = f"✅ {result.message}"
            status_text.color = ft.Colors.GREEN
            log_bus.emit("simple", f"✅ تست {name} موفق")
        else:
            status_text.value = f"❌ {result.message}"
            status_text.color = ft.Colors.RED
            log_bus.emit("simple", f"❌ تست {name} ناموفق")
        test_btn.disabled = False
        page.update()

    # --- Activate handler ---
    def _do_activate(name: str):
        provider_manager.set_active(name)
        log_bus.emit("simple", f"⚙️ Provider فعال: {name}")
        refresh()

    # --- Remove handler ---
    def _do_remove(name: str):
        provider_manager.remove_custom(name)
        log_bus.emit("simple", f"🗑️ Provider حذف شد: {name}")
        refresh()

    # --- Edit dialog ---
    def open_edit_dialog(row: dict):
        name = row["name"]
        is_builtin = bool(row["is_builtin"])
        raw = provider_manager.get_raw(name) or {}

        name_field = ft.TextField(
            label="نام (غیرقابل ویرایش)",
            value=name,
            width=340,
            read_only=True,
            disabled=True,
        )
        url_field = ft.TextField(
            label="Base URL" + (" (غیرقابل ویرایش)" if is_builtin else ""),
            value=row.get("base_url") or "",
            width=340,
            read_only=is_builtin,
            disabled=is_builtin,
        )
        env_field = ft.TextField(
            label="نام کلید در .env" + (" (غیرقابل ویرایش)" if is_builtin else ""),
            value=row.get("env_key") or "",
            width=340,
            read_only=is_builtin,
            disabled=is_builtin,
            hint_text="مثلاً OPENROUTER_API_KEY",
        )

        # API key field with show/hide
        key_value = (raw.get("api_key") or "").strip()
        api_key_field = ft.TextField(
            label="کلید API",
            value=key_value,
            password=True,
            can_reveal_password=True,
            width=340,
            hint_text="اگر خالی بماند، از .env خوانده می‌شود",
        )

        # Current source indicator
        src = row.get("key_source", "none")
        src_label = {
            "db": "🔒 منبع فعلی: پایگاه داده (این فرم)",
            "env": "📄 منبع فعلی: فایل .env",
            "none": "⚠️ هیچ کلیدی تنظیم نشده",
        }.get(src, "")

        src_text = ft.Text(src_label, size=11, color=ft.Colors.OUTLINE)

        models_field = ft.TextField(
            label="مدل‌ها (با کاما جدا کنید)",
            value=", ".join(row.get("models_list") or []),
            width=340,
            multiline=True,
            min_lines=3,
            max_lines=6,
        )

        error = ft.Text("", color=ft.Colors.RED_300, size=12)

        def _submit(ev):
            new_key = api_key_field.value.strip()
            new_models = [
                m.strip() for m in (models_field.value or "").split(",") if m.strip()
            ]

            try:
                provider_manager.update_provider(
                    name=name,
                    api_key=new_key,
                    models=new_models,
                    env_key=env_field.value if not is_builtin else None,
                    base_url=url_field.value if not is_builtin else None,
                )
                log_bus.emit("simple", f"✏️ Provider ویرایش شد: {name}")
                dlg.open = False
                refresh()
            except Exception as ex:
                error.value = f"خطا: {ex}"
                page.update()

        def _clear_key(ev):
            api_key_field.value = ""
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"ویرایش Provider: {name}"),
            content=ft.Column(
                [
                    name_field,
                    url_field,
                    env_field,
                    ft.Divider(height=1),
                    api_key_field,
                    src_text,
                    ft.TextButton(
                        "پاک کردن کلید (بازگشت به .env)",
                        icon=ft.Icons.CLEAR,
                        on_click=_clear_key,
                    ),
                    ft.Divider(height=1),
                    models_field,
                    error,
                ],
                tight=True,
                spacing=10,
                width=360,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("انصراف", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton(
                    "ذخیره",
                    style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.Colors.BLACK),
                    on_click=_submit,
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # --- Add custom dialog ---
    def open_add_dialog(e):
        name_field = ft.TextField(
            label="نام (یکتا، انگلیسی، بدون فاصله)",
            width=340,
        )
        url_field = ft.TextField(
            label="Base URL",
            width=340,
            hint_text="https://api.example.com/v1",
        )
        env_field = ft.TextField(
            label="نام کلید در .env (اختیاری)",
            width=340,
            hint_text="CUSTOM_EXAMPLE_API_KEY",
        )
        api_key_field = ft.TextField(
            label="کلید API (اختیاری)",
            width=340,
            password=True,
            can_reveal_password=True,
            hint_text="اگر اینجا وارد کنید، در DB ذخیره می‌شود",
        )
        models_field = ft.TextField(
            label="مدل‌ها (با کاما جدا کنید)",
            width=340,
            multiline=True,
            min_lines=2,
            max_lines=5,
        )
        error = ft.Text("", color=ft.Colors.RED_300, size=12)

        def _submit(ev):
            name = name_field.value.strip()
            url = url_field.value.strip()
            env = env_field.value.strip()
            key = api_key_field.value.strip()
            models = [m.strip() for m in (models_field.value or "").split(",") if m.strip()]

            if not name or not url:
                error.value = "پر کردن نام و URL الزامی است."
                page.update()
                return

            if not models:
                error.value = "حداقل یک مدل وارد کنید."
                page.update()
                return

            try:
                provider_manager.add_custom(name, url, env, models, api_key=key)
                log_bus.emit("simple", f"➕ Provider افزوده شد: {name}")
                dlg.open = False
                refresh()
            except Exception as ex:
                error.value = f"خطا: {ex}"
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("افزودن Provider سفارشی"),
            content=ft.Column(
                [name_field, url_field, env_field, api_key_field, models_field, error],
                tight=True,
                spacing=10,
                width=360,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("انصراف", on_click=lambda e: _close(dlg)),
                ft.ElevatedButton(
                    "افزودن",
                    style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.Colors.BLACK),
                    on_click=_submit,
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def _close(dlg):
        dlg.open = False
        page.update()

    # --- Card builder ---
    def _provider_card(row: dict) -> ft.Control:
        name = row["name"]
        is_active = bool(row["is_active"])
        has_key = row["has_key"]
        is_builtin = bool(row["is_builtin"])
        models_count = len(row["models_list"])
        src = row.get("key_source", "none")

        status_text = ft.Text("", size=12, selectable=True)

        # Key source badge
        if src == "db":
            key_label = "کلید: 💾 پایگاه داده"
            key_color = ft.Colors.GREEN
        elif src == "env":
            key_label = "کلید: 📄 .env"
            key_color = ft.Colors.BLUE_300
        else:
            key_label = "کلید: ⚠️ تنظیم نشده"
            key_color = ft.Colors.AMBER

        key_badge = ft.Container(
            content=ft.Text(key_label, size=11, color=key_color),
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            bgcolor=ft.Colors.with_opacity(0.15, key_color),
            border_radius=4,
        )

        title_row = ft.Row(
            [
                ft.Icon(
                    ft.Icons.RADIO_BUTTON_CHECKED if is_active else ft.Icons.RADIO_BUTTON_UNCHECKED,
                    color=ft.Colors.PRIMARY if is_active else ft.Colors.OUTLINE,
                    size=20,
                ),
                ft.Text(row["name"], size=15, weight=ft.FontWeight.BOLD),
                ft.Text(f"({row['base_url']})", size=11, color=ft.Colors.OUTLINE),
                ft.Container(expand=True),
                key_badge,
            ],
            spacing=8,
        )

        type_badge = ft.Container(
            content=ft.Text(
                "builtin" if is_builtin else "custom",
                size=10,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=4,
        )

        info_row = ft.Row(
            [
                type_badge,
                ft.Text(f"{models_count} مدل", size=11, color=ft.Colors.OUTLINE),
            ],
            spacing=8,
        )

        test_btn = ft.ElevatedButton(
            "تست اتصال",
            icon=ft.Icons.WIFI_TETHERING,
            on_click=lambda e: page.run_task(_do_test, name, status_text, test_btn),
        )
        edit_btn = ft.OutlinedButton(
            "ویرایش",
            icon=ft.Icons.EDIT,
            on_click=lambda e: open_edit_dialog(row),
        )

        buttons = [test_btn, edit_btn]

        if not is_active:
            buttons.append(
                ft.OutlinedButton(
                    "فعال‌سازی",
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    on_click=lambda e: _do_activate(name),
                )
            )
        else:
            buttons.append(
                ft.Container(
                    content=ft.Text("فعال ✓", size=12, color=ft.Colors.PRIMARY),
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                )
            )

        if not is_builtin:
            buttons.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_300,
                    tooltip="حذف",
                    on_click=lambda e: _do_remove(name),
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        info_row,
                        ft.Row(buttons, spacing=8, wrap=True),
                        status_text,
                    ],
                    spacing=8,
                ),
                padding=14,
            ),
        )

    # --- Build page ---
    cards = ft.Column(spacing=10)

    theme_icon = ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE

    header = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                tooltip="بازگشت",
                on_click=lambda e: on_back(),
            ),
            ft.Text("تنظیمات Providerها", size=22, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=theme_icon,
                tooltip="تغییر تم روشن/تاریک",
                on_click=lambda e: on_toggle_theme() if on_toggle_theme else None,
            ),
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                tooltip="درباره برنامه",
                on_click=lambda e: show_about_dialog(page),
            ),
            ft.ElevatedButton(
                "افزودن Provider سفارشی",
                icon=ft.Icons.ADD,
                style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.Colors.BLACK),
                on_click=open_add_dialog,
            ),
        ]
    )

    note = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "🔐 کلیدهای API به دو روش قابل تنظیم هستند:",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "۱. وارد کردن مستقیم در فرم ویرایش هر Provider (ذخیره در پایگاه داده)\n"
                    "۲. تنظیم متغیر مربوطه در فایل .env (روش سنتی)\n"
                    "اگر کلید در پایگاه داده وارد شده باشد، به فایل .env اولویت دارد.",
                    size=11,
                    color=ft.Colors.OUTLINE,
                ),
            ],
            spacing=4,
        ),
        padding=10,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        border_radius=6,
    )

    refresh()

    return ft.Column(
        [
            header,
            ft.Divider(),
            note,
            ft.Container(height=6),
            ft.ListView([cards], expand=True, spacing=8),
        ],
        expand=True,
        spacing=10,
    )