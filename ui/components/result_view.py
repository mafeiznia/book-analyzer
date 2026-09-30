"""Beautiful display of analysis result (bilingual-aware)."""
import flet as ft

from core.bilingual import pick, pick_list
from ui.theme import OLIVE_PRIMARY


def _section_header(icon: str, title: str) -> ft.Control:
    return ft.Row(
        [
            ft.Text(icon, size=18),
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=OLIVE_PRIMARY),
        ],
        spacing=6,
    )


def build_result_view(
    analysis: dict,
    translation_prompt: str,
    sources_used: list[str],
    provider: str,
    model: str,
    version: int,
    analyzed_at: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    on_copy_prompt=None,
    on_open_folder=None,
    output_folder_path=None,
) -> ft.Control:
    """Return a Control displaying the analysis result (Persian)."""

    LANG = "fa"  # UI is always Persian

    genre = analysis.get("genre", {}) or {}
    tone = analysis.get("tone", {}) or {}
    style = analysis.get("style", {}) or {}
    notes = analysis.get("translation_notes", []) or []
    confidence = analysis.get("confidence", "Unknown")

    blocks: list[ft.Control] = []

    # --- Meta bar ---
    confidence_color = {
        "Confirmed": ft.colors.GREEN_300,
        "Probable": ft.colors.AMBER,
        "Unknown": ft.colors.OUTLINE,
    }.get(confidence, ft.colors.OUTLINE)

    meta_row = ft.Row(
        [
            ft.Container(
                content=ft.Text(f"نسخه {version}", size=11, color=ft.colors.WHITE),
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                bgcolor=OLIVE_PRIMARY,
                border_radius=6,
            ),
            ft.Container(
                content=ft.Text(f"اطمینان: {confidence}", size=11, color=confidence_color),
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                bgcolor=ft.colors.with_opacity(0.15, confidence_color),
                border_radius=6,
            ),
            ft.Text(f"🤖 {provider}/{model}", size=11, color=ft.colors.OUTLINE),
            ft.Text(f"🕒 {analyzed_at}", size=11, color=ft.colors.OUTLINE),
            ft.Text(f"📊 {tokens_in}+{tokens_out} توکن", size=11, color=ft.colors.OUTLINE),
        ],
        spacing=8,
        wrap=True,
    )
    blocks.append(meta_row)
    blocks.append(ft.Divider(height=1))

    # --- Genre ---
    blocks.append(_section_header("📖", "ژانر"))
    primary = pick(genre.get("primary"), LANG)
    secondary = pick(genre.get("secondary"), LANG)
    if primary:
        genre_txt = f"**{primary}**"
        if secondary:
            genre_txt += f"  |  {secondary}"
        blocks.append(ft.Markdown(genre_txt, selectable=True))
    notes_genre = pick(genre.get("notes"), LANG)
    if notes_genre:
        blocks.append(ft.Text(notes_genre, size=13, selectable=True))
    blocks.append(ft.Container(height=6))

    # --- Tone ---
    blocks.append(_section_header("🎭", "لحن"))
    tone_desc = pick(tone.get("description"), LANG)
    if tone_desc:
        blocks.append(ft.Text(tone_desc, size=13, selectable=True))
    examples = pick_list(tone.get("examples"), LANG)
    if examples:
        blocks.append(ft.Container(height=4))
        for ex in examples:
            blocks.append(
                ft.Container(
                    content=ft.Text(
                        f"« {ex} »",
                        size=12,
                        italic=True,
                        selectable=True,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border=ft.border.only(left=ft.BorderSide(3, OLIVE_PRIMARY)),
                    bgcolor=ft.colors.with_opacity(0.04, OLIVE_PRIMARY),
                )
            )
    blocks.append(ft.Container(height=6))

    # --- Style ---
    blocks.append(_section_header("✍️", "سبک نویسنده"))
    style_items = []
    sl = pick(style.get("sentence_length"), LANG)
    nv = pick(style.get("narrative_voice"), LANG)
    vc = pick(style.get("vocabulary"), LANG)
    if sl:
        style_items.append(("طول جمله‌ها", sl))
    if nv:
        style_items.append(("راوی", nv))
    if vc:
        style_items.append(("واژگان", vc))

    for k, v in style_items:
        blocks.append(
            ft.Row(
                [
                    ft.Text(f"{k}:", size=12, weight=ft.FontWeight.BOLD, width=100),
                    ft.Text(v, size=12, selectable=True, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    features = pick_list(style.get("notable_features"), LANG)
    if features:
        blocks.append(ft.Container(height=4))
        blocks.append(ft.Text("ویژگی‌های قابل توجه:", size=12, weight=ft.FontWeight.BOLD))
        for f in features:
            blocks.append(
                ft.Row(
                    [
                        ft.Text("•", size=13, color=OLIVE_PRIMARY),
                        ft.Text(f, size=12, selectable=True, expand=True),
                    ],
                    spacing=6,
                )
            )
    blocks.append(ft.Container(height=6))

    # --- Translation Notes ---
    blocks.append(_section_header("🌐", "نکات ترجمه"))
    if notes:
        for i, n in enumerate(notes, 1):
            blocks.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"{i}. {pick(n.get('topic'), LANG)}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"چالش: {pick(n.get('issue'), LANG)}",
                                size=12,
                                selectable=True,
                            ),
                            ft.Text(
                                f"راهبرد: {pick(n.get('suggestion'), LANG)}",
                                size=12,
                                selectable=True,
                                color=ft.colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                    border_radius=6,
                )
            )
    else:
        blocks.append(ft.Text("(نکته‌ای ثبت نشده)", italic=True, color=ft.colors.OUTLINE))
    blocks.append(ft.Container(height=6))

    # --- Sources ---
    if sources_used:
        blocks.append(_section_header("🔗", "منابع استفاده‌شده"))
        for url in sources_used:
            blocks.append(
                ft.Text(url, size=11, color=ft.colors.ON_SURFACE_VARIANT, selectable=True)
            )
        blocks.append(ft.Container(height=6))

    # --- Translation Prompt ---
    blocks.append(_section_header("📝", "پرامپت ترجمه"))

    prompt_field = ft.TextField(
        value=translation_prompt or "",
        multiline=True,
        min_lines=7,
        max_lines=18,
        read_only=True,
        text_size=11,
        border_radius=6,
    )

    prompt_actions = ft.Row(
        [
            ft.ElevatedButton(
                "کپی پرامپت",
                icon=ft.icons.COPY,
                on_click=lambda e: _copy_prompt(e, translation_prompt, on_copy_prompt),
            ),
        ],
        spacing=8,
    )

    blocks.append(
        ft.Row(
            [
                ft.Container(content=prompt_field, expand=9),
                ft.Container(expand=1),
            ],
        )
    )
    blocks.append(prompt_actions)

    # --- Output folder ---
    if on_open_folder and output_folder_path:
        blocks.append(ft.Container(height=10))
        blocks.append(ft.Divider(height=1))
        blocks.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(ft.icons.FOLDER_SPECIAL, size=16, color=OLIVE_PRIMARY),
                                ft.Text(
                                    "خروجی‌ها ذخیره شده‌اند در:",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=6,
                        ),
                        ft.Text(
                            str(output_folder_path),
                            size=11,
                            selectable=True,
                            color=ft.colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Container(height=4),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "📂 باز کردن پوشه خروجی",
                                    icon=ft.icons.FOLDER_OPEN,
                                    style=ft.ButtonStyle(
                                        bgcolor=OLIVE_PRIMARY, color=ft.colors.BLACK
                                    ),
                                    on_click=lambda e: on_open_folder(),
                                ),
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=6,
                ),
                padding=12,
                bgcolor=ft.colors.with_opacity(0.04, ft.colors.ON_SURFACE),
                border_radius=6,
            )
        )

    return ft.Column(blocks, spacing=8)


def _copy_prompt(e, prompt_text: str, on_copy=None):
    if on_copy:
        on_copy(prompt_text)