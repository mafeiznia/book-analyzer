"""Project view — input form + analysis + result + output folder."""
import asyncio
import json
import os
import time
from datetime import datetime

import flet as ft
from dotenv import load_dotenv

from core.analyzer import analyze_book
from exporters.to_json import project_dir, save_json
from exporters.to_md import build_markdown, save_markdown
from exporters.to_pdf import save_pdf
from providers.manager import provider_manager
from services.log_bus import log_bus
from storage import repositories as repo
from ui.components.log_panel import LogPanel
from ui.components.result_view import build_result_view
from ui.theme import OLIVE_PRIMARY

load_dotenv()


def project_view(
    page: ft.Page,
    project_id: int | None,
    on_back,
    on_saved=None,
    on_toggle_theme=None,
) -> ft.Control:
    """Return the project view."""
    is_new = project_id is None
    project = repo.get_project(project_id) if not is_new else None

    if not is_new and project is None:
        return _not_found(on_back)

    # --- Fields ---
    title_field = ft.TextField(
        label="عنوان کتاب *",
        value=project["title"] if project else "",
        border_radius=8,
        autofocus=is_new,
    )

    author_field = ft.TextField(
        label="نام نویسنده *",
        value=project["author"] if project else "",
        border_radius=8,
    )

    initial_urls = ""
    if project:
        urls_list = repo.parse_urls(project.get("urls"))
        initial_urls = "\n".join(urls_list)

    urls_field = ft.TextField(
        label="لینک‌ها (هر خط یک لینک)",
        value=initial_urls,
        multiline=True,
        min_lines=3,
        max_lines=6,
        border_radius=8,
        hint_text="https://www.goodreads.com/...\nhttps://...",
    )

    snippet_field = ft.TextField(
        label="بخشی از متن کتاب (اختیاری، حداکثر یک فصل)",
        value=project["snippet"] if project else "",
        multiline=True,
        min_lines=6,
        max_lines=14,
        border_radius=8,
        hint_text="چند پاراگراف از کتاب را اینجا پیست کنید...",
    )

    error_text = ft.Text("", size=12, color=ft.colors.RED_300)

    # --- Model selector (from active provider) ---
    active_provider = provider_manager.get_active()
    if active_provider is None:
        available_models: list[str] = []
        active_provider_name = ""
    else:
        available_models = list(active_provider.models)
        active_provider_name = active_provider.name

    saved_model = (project["model"] if project else "") or ""

    # Build dropdown options
    model_options: list[ft.dropdown.Option] = []
    for m in available_models:
        model_options.append(ft.dropdown.Option(key=m, text=m))

    # If saved model is not in list, prepend it as a legacy option
    if saved_model and saved_model not in available_models:
        model_options.insert(
            0,
            ft.dropdown.Option(key=saved_model, text=f"{saved_model}  (قبلی)"),
        )

    # Default selection
    if saved_model:
        default_model_value = saved_model
    elif available_models:
        default_model_value = available_models[0]
    else:
        default_model_value = None

    model_dropdown = ft.Dropdown(
        label=f"مدل (Provider فعال: {active_provider_name or 'هیچ'})",
        value=default_model_value,
        options=model_options,
        border_radius=8,
        disabled=not available_models,
        hint_text="هیچ مدلی در دسترس نیست — ابتدا در تنظیمات Provider فعال کنید"
        if not available_models
        else None,
    )

    # --- Log panel ---
    log_panel = LogPanel(page)

    # --- Status ---
    status_text = ft.Text("", size=12, color=ft.colors.OUTLINE)
    elapsed_text = ft.Text("", size=12, color=ft.colors.OUTLINE)

    cancel_btn = ft.OutlinedButton(
        "لغو تحلیل",
        icon=ft.icons.CANCEL,
        style=ft.ButtonStyle(color=ft.colors.RED_300),
        visible=False,
    )

    analyze_btn = ft.ElevatedButton(
        "شروع تحلیل",
        icon=ft.icons.PLAY_ARROW,
        style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.colors.BLACK),
        disabled=is_new,
    )

    save_btn = ft.OutlinedButton(
        "ذخیره",
        icon=ft.icons.SAVE,
    )
    save_back_btn = ft.ElevatedButton(
        "ذخیره و بازگشت",
        icon=ft.icons.SAVE_ALT,
        style=ft.ButtonStyle(bgcolor=OLIVE_PRIMARY, color=ft.colors.BLACK),
    )

    # --- Task state (for cancellation) ---
    task_state = {"current_task": None, "timer_task": None}

    async def _update_elapsed(start_time: float):
        try:
            while True:
                secs = int(time.time() - start_time)
                mins = secs // 60
                rem = secs % 60
                elapsed_text.value = f"⏱ {mins:02d}:{rem:02d}"
                try:
                    page.update()
                except Exception:
                    pass
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def cancel_analysis(e):
        task = task_state.get("current_task")
        if task and not task.done():
            task.cancel()

    cancel_btn.on_click = cancel_analysis

    # --- Result section ---
    result_section = ft.Column([], spacing=10)

    # --- Validation ---
    def _validate() -> bool:
        if not title_field.value or not title_field.value.strip():
            error_text.value = "عنوان کتاب الزامی است."
            page.update()
            return False
        if not author_field.value or not author_field.value.strip():
            error_text.value = "نام نویسنده الزامی است."
            page.update()
            return False
        for line in (urls_field.value or "").splitlines():
            line = line.strip()
            if not line:
                continue
            if not (line.startswith("http://") or line.startswith("https://")):
                error_text.value = f"لینک نامعتبر: {line[:60]}\n(باید با http یا https شروع شود)"
                page.update()
                return False
        error_text.value = ""
        return True

    def _current_urls_json() -> str:
        urls = [u.strip() for u in (urls_field.value or "").splitlines() if u.strip()]
        return repo.serialize_urls(urls)

    # --- Render saved result ---
    def _render_saved_result(latest: dict) -> None:
        try:
            analysis_dict = json.loads(latest.get("result_json") or "{}")
            sources = json.loads(latest.get("sources_used") or "[]")
        except Exception:
            return

        version = latest.get("version", 1)
        base = project_dir(project["id"], project["title"]) / f"v{version}"

        result_section.controls.clear()
        result_section.controls.append(
            build_result_view(
                analysis=analysis_dict,
                translation_prompt=latest.get("translation_prompt") or "",
                sources_used=sources,
                provider=latest.get("provider") or "",
                model=latest.get("model") or "",
                version=version,
                analyzed_at=latest.get("created_at") or "",
                tokens_in=latest.get("tokens_in") or 0,
                tokens_out=latest.get("tokens_out") or 0,
                on_copy_prompt=lambda txt: _copy_clipboard(page, txt),
                on_open_folder=lambda: _open_output_folder(page, base),
                output_folder_path=base,
            )
        )

    # --- Save handlers ---
    def save_and_stay(e):
        if not _validate():
            return
        urls_json = _current_urls_json()
        selected_model = (model_dropdown.value or "").strip()
        selected_provider = active_provider_name or ""

        if is_new:
            new_id = repo.create_project(
                title=title_field.value.strip(),
                author=author_field.value.strip(),
                urls=urls_json,
                snippet=snippet_field.value or "",
                model=selected_model,
                provider=selected_provider,
            )
            log_bus.emit("simple", f"➕ پروژه ساخته شد: {title_field.value.strip()}")
            if on_saved:
                on_saved(new_id)
            else:
                on_back()
        else:
            repo.update_project(
                project["id"],
                title=title_field.value.strip(),
                author=author_field.value.strip(),
                urls=urls_json,
                snippet=snippet_field.value or "",
                model=selected_model,
                provider=selected_provider,
            )
            log_bus.emit("simple", f"💾 پروژه ذخیره شد: {title_field.value.strip()}")
            page.open(ft.SnackBar(ft.Text("✅ تغییرات ذخیره شد")))
            page.update()

    def save_and_back(e):
        if not _validate():
            return
        urls_json = _current_urls_json()
        selected_model = (model_dropdown.value or "").strip()
        selected_provider = active_provider_name or ""

        if is_new:
            repo.create_project(
                title=title_field.value.strip(),
                author=author_field.value.strip(),
                urls=urls_json,
                snippet=snippet_field.value or "",
                model=selected_model,
                provider=selected_provider,
            )
        else:
            repo.update_project(
                project["id"],
                title=title_field.value.strip(),
                author=author_field.value.strip(),
                urls=urls_json,
                snippet=snippet_field.value or "",
                model=selected_model,
                provider=selected_provider,
            )
        on_back()

    save_btn.on_click = save_and_stay
    save_back_btn.on_click = save_and_back

    # --- Analysis handler ---
    async def run_analysis(e):
        if is_new or project is None:
            return
        if not _validate():
            return

        # Persist form first
        repo.update_project(
            project["id"],
            title=title_field.value.strip(),
            author=author_field.value.strip(),
            urls=_current_urls_json(),
            snippet=snippet_field.value or "",
        )

        provider = provider_manager.get_active()
        if provider is None:
            log_bus.emit("simple", "❌ هیچ Provider فعالی وجود ندارد. ابتدا در تنظیمات فعال کنید.")
            page.open(ft.SnackBar(ft.Text("❌ هیچ Provider فعالی نیست.")))
            page.update()
            return

        # Model priority: dropdown value > .env DEFAULT_MODEL
        model = (model_dropdown.value or "").strip()
        if not model:
            model = os.getenv("DEFAULT_MODEL", "").strip()
        if not model:
            log_bus.emit("simple", "❌ هیچ مدلی انتخاب نشده و DEFAULT_MODEL در .env هم تنظیم نیست.")
            page.open(ft.SnackBar(ft.Text("❌ مدلی انتخاب نشده")))
            page.update()
            return

        # Disable UI
        analyze_btn.disabled = True
        save_btn.disabled = True
        save_back_btn.disabled = True
        cancel_btn.visible = True
        status_text.value = "⏳ در حال تحلیل..."
        status_text.color = ft.colors.AMBER
        page.update()

        log_bus.emit("simple", f"🚀 شروع تحلیل: {title_field.value.strip()}")
        log_bus.emit("simple", f"🔌 Provider: {provider.name} | Model: {model}")

        # Save current task + start timer
        start_time = time.time()
        task_state["current_task"] = asyncio.current_task()
        task_state["timer_task"] = asyncio.create_task(_update_elapsed(start_time))

        try:
            result = await analyze_book(
                title=title_field.value.strip(),
                author=author_field.value.strip(),
                urls=[u.strip() for u in (urls_field.value or "").splitlines() if u.strip()],
                snippet=snippet_field.value or "",
                provider=provider,
                model=model,
                on_log=lambda level, msg, tech=None: log_bus.emit(level, msg, tech),
            )
        except asyncio.CancelledError:
            log_bus.emit("simple", "⛔ تحلیل توسط کاربر لغو شد")
            status_text.value = "⛔ لغو شد"
            status_text.color = ft.colors.AMBER
            repo.set_status(project["id"], "draft")
            analyze_btn.disabled = False
            save_btn.disabled = False
            save_back_btn.disabled = False
            cancel_btn.visible = False
            timer = task_state.get("timer_task")
            if timer and not timer.done():
                timer.cancel()
            # Freeze elapsed time with "(لغو شد)" suffix
            if elapsed_text.value:
                elapsed_text.value = f"{elapsed_text.value} (لغو شد)"
            task_state["current_task"] = None
            task_state["timer_task"] = None
            page.update()
            return
        except Exception as ex:
            log_bus.emit("simple", f"❌ خطای غیرمنتظره: {type(ex).__name__}: {str(ex)[:200]}")
            status_text.value = "❌ خطا"
            status_text.color = ft.colors.RED_300
            analyze_btn.disabled = False
            save_btn.disabled = False
            save_back_btn.disabled = False
            cancel_btn.visible = False
            elapsed_text.value = ""
            page.update()
            return

        # Save to DB + filesystem
        if result.ok and result.analysis:
            ts = datetime.now().isoformat(timespec="seconds")
            try:
                repo.save_analysis(
                    project_id=project["id"],
                    provider=result.provider,
                    model=result.model,
                    result_json=json.dumps(result.analysis, ensure_ascii=False),
                    translation_prompt=result.translation_prompt or "",
                    sources_used=json.dumps(result.sources_used, ensure_ascii=False),
                    tokens_in=result.tokens_in,
                    tokens_out=result.tokens_out,
                )
                repo.set_status(project["id"], "done")

                latest = repo.get_latest_analysis(project["id"])
                version = latest["version"] if latest else 1

                base_dir = project_dir(project["id"], title_field.value.strip()) / f"v{version}"

                # --- Save JSON ---
                try:
                    save_json(
                        project_id=project["id"],
                        title=title_field.value.strip(),
                        author=author_field.value.strip(),
                        version=version,
                        analysis=result.analysis,
                        translation_prompt=result.translation_prompt or "",
                        sources_used=result.sources_used,
                        provider=result.provider,
                        model=result.model,
                        tokens_in=result.tokens_in,
                        tokens_out=result.tokens_out,
                        analyzed_at=ts,
                    )
                except Exception as ex:
                    log_bus.emit("simple", f"⚠️ خطا در JSON: {type(ex).__name__}: {str(ex)[:150]}")

                # --- Save MD ---
                md_text = ""
                try:
                    md_text = build_markdown(
                        project_id=project["id"],
                        title=title_field.value.strip(),
                        author=author_field.value.strip(),
                        version=version,
                        analysis=result.analysis,
                        translation_prompt=result.translation_prompt or "",
                        sources_used=result.sources_used,
                        provider=result.provider,
                        model=result.model,
                        tokens_in=result.tokens_in,
                        tokens_out=result.tokens_out,
                        analyzed_at=ts,
                    )
                    save_markdown(
                        project_id=project["id"],
                        title=title_field.value.strip(),
                        author=author_field.value.strip(),
                        version=version,
                        analysis=result.analysis,
                        translation_prompt=result.translation_prompt or "",
                        sources_used=result.sources_used,
                        provider=result.provider,
                        model=result.model,
                        tokens_in=result.tokens_in,
                        tokens_out=result.tokens_out,
                        analyzed_at=ts,
                    )
                except Exception as ex:
                    log_bus.emit("simple", f"⚠️ خطا در MD: {type(ex).__name__}: {str(ex)[:150]}")

                # --- Save PDF ---
                if md_text:
                    try:
                        save_pdf(
                            project_id=project["id"],
                            title=title_field.value.strip(),
                            version=version,
                            markdown_text=md_text,
                        )
                    except Exception as ex:
                        log_bus.emit("simple", f"⚠️ خطا در PDF: {type(ex).__name__}: {str(ex)[:150]}")

                log_bus.emit("simple", f"📁 خروجی‌ها: {base_dir}")

                # --- Render result view ---
                result_section.controls.clear()
                result_section.controls.append(
                    build_result_view(
                        analysis=result.analysis,
                        translation_prompt=result.translation_prompt or "",
                        sources_used=result.sources_used,
                        provider=result.provider,
                        model=result.model,
                        version=version,
                        analyzed_at=ts,
                        tokens_in=result.tokens_in,
                        tokens_out=result.tokens_out,
                        on_copy_prompt=lambda txt: _copy_clipboard(page, txt),
                        on_open_folder=lambda: _open_output_folder(page, base_dir),
                        output_folder_path=base_dir,
                    )
                )

                log_bus.emit("simple", "💾 تحلیل در دیتابیس ذخیره شد.")
                status_text.value = f"✅ تحلیل کامل شد ({result.elapsed_ms}ms)"
                status_text.color = ft.colors.GREEN_300
                page.open(ft.SnackBar(ft.Text("✅ تحلیل کامل شد و ذخیره شد")))

            except Exception as ex_save:
                log_bus.emit("simple", f"❌ خطا در ذخیره: {type(ex_save).__name__}: {str(ex_save)[:150]}")
                status_text.value = "⚠️ ذخیره ناموفق"
                status_text.color = ft.colors.AMBER
        else:
            repo.set_status(project["id"], "failed")
            log_bus.emit("simple", f"❌ تحلیل ناموفق: {result.error[:200]}")
            status_text.value = "❌ تحلیل ناموفق"
            status_text.color = ft.colors.RED_300

        analyze_btn.disabled = False
        save_btn.disabled = False
        save_back_btn.disabled = False
        cancel_btn.visible = False
        elapsed_text.value = ""
        timer = task_state.get("timer_task")
        if timer and not timer.done():
            timer.cancel()
        task_state["current_task"] = None
        task_state["timer_task"] = None
        page.update()

    analyze_btn.on_click = lambda e: page.run_task(run_analysis, e)

    # --- Load previous result if exists ---
    if not is_new:
        latest = repo.get_latest_analysis(project["id"])
        if latest:
            _render_saved_result(latest)

    # --- Header ---
    header_title = "پروژه جدید" if is_new else f"ویرایش پروژه #{project['id']}"
    theme_icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE

    header = ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="بازگشت",
                on_click=lambda e: on_back(),
            ),
            ft.Text(header_title, size=22, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=theme_icon,
                tooltip="تغییر تم روشن/تاریک",
                on_click=lambda e: on_toggle_theme() if on_toggle_theme else None,
            ),
            save_btn,
            save_back_btn,
        ],
    )

    # --- Form card (90% width) ---
    form_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    title_field,
                    author_field,
                    urls_field,
                    snippet_field,
                    model_dropdown,
                    error_text,
                ],
                spacing=14,
            ),
            padding=20,
        )
    )

    form_card_wrapped = ft.Row(
        [
            ft.Container(content=form_card, expand=9),
            ft.Container(expand=1),
        ],
    )

    action_row = ft.Row(
        [analyze_btn, cancel_btn, status_text, elapsed_text],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    body = ft.Column(
        [
            form_card_wrapped,
            action_row,
            result_section,
            log_panel.control,
        ],
        spacing=14,
    )

    return ft.Column([header, ft.Divider(), body], spacing=10)


# ====================================================================
# Helper functions
# ====================================================================

def _not_found(on_back) -> ft.Control:
    header = ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.ARROW_FORWARD,
                tooltip="بازگشت",
                on_click=lambda e: on_back(),
            ),
            ft.Text("پروژه یافت نشد", size=22, weight=ft.FontWeight.BOLD),
        ]
    )
    body = ft.Container(
        content=ft.Text("این پروژه وجود ندارد یا حذف شده است.", color=ft.colors.RED_300),
        alignment=ft.alignment.center,
        expand=True,
    )
    return ft.Column([header, ft.Divider(), body], spacing=10)


def _copy_clipboard(page: ft.Page, text: str) -> None:
    try:
        import pyperclip
        pyperclip.copy(text)
        page.open(ft.SnackBar(ft.Text("✅ پرامپت کپی شد")))
    except ImportError:
        page.open(ft.SnackBar(ft.Text("⚠️ pyperclip نصب نیست")))
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()


def _open_output_folder(page: ft.Page, folder_path) -> None:
    """Open the output folder in Windows Explorer."""
    try:
        from pathlib import Path

        path = Path(folder_path)
        if not path.exists():
            page.open(ft.SnackBar(ft.Text(f"❌ پوشه یافت نشد: {path}")))
            page.update()
            return

        os.startfile(str(path))
        page.open(ft.SnackBar(ft.Text("📂 پوشه در Explorer باز شد")))
    except Exception as ex:
        page.open(ft.SnackBar(ft.Text(f"❌ خطا: {ex}")))
    page.update()