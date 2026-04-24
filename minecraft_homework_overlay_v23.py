from __future__ import annotations

import ctypes
import json
import os
import queue
import random
import re
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from minecraft_homework_overlay_v21 import (
    ACCENT,
    ACCENT_2,
    APP_TITLE,
    BAD,
    BG,
    BORDER,
    CARD,
    CARD_2,
    CENTER,
    GOOD,
    MUTED,
    PANEL,
    TEXT,
    normalize_input,
    t,
)

from minecraft_coach.lan_admin import LanAdminServer
from minecraft_coach.local_db import LocalDB
from minecraft_coach.module_installer import (
    ModuleImportError,
    create_module_from_template,
    export_module_template,
    import_module_source,
    list_installed_modules,
    save_module_json,
)
from minecraft_coach.remote_sync import push_remote_snapshot


def _runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _bundle_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return Path(__file__).resolve().parent


def _first_existing_path(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


RUNTIME_DIR = _runtime_root()
BUNDLE_DIR = _bundle_root()
BASE_DIR = RUNTIME_DIR
DATA_DIR = RUNTIME_DIR / "coach_data"
DB_FILE = DATA_DIR / "coach.db"
SEED_DB = _first_existing_path(
    RUNTIME_DIR / "coach_seed_v22.db",
    BUNDLE_DIR / "coach_seed_v22.db",
    RUNTIME_DIR.parent / "coach_seed_v22.db",
)
ELECTRYK_DIR = _first_existing_path(
    RUNTIME_DIR / "Electryk",
    BUNDLE_DIR / "Electryk",
    RUNTIME_DIR.parent / "Electryk",
)
MODULES_DIR = _first_existing_path(
    RUNTIME_DIR / "modules",
    BUNDLE_DIR / "modules",
    RUNTIME_DIR.parent / "modules",
)
MODULE_TEMPLATES_DIR = _first_existing_path(
    RUNTIME_DIR / "module_templates",
    BUNDLE_DIR / "module_templates",
    RUNTIME_DIR.parent / "module_templates",
)
MODULE_TEMPLATE_DIR = _first_existing_path(
    MODULE_TEMPLATES_DIR / "basic_module",
    BUNDLE_DIR / "module_templates" / "basic_module",
)
MODULE_BACKUPS_DIR = RUNTIME_DIR / "module_backups"


def localized_value(item: dict, base: str, lang: str) -> str:
    for code in (lang, "ru", "pl", "en"):
        value = item.get(f"{base}_{code}")
        if value:
            return str(value)
    return str(item.get(base, ""))


def safe_int(value, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def try_pause_minecraft_window() -> None:
    if os.name != "nt":
        return
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return
            self.feedback.config(
                text={
                    "ru": "Тема изучена. Можно переходить к заданиям.",
                    "pl": "Temat przeczytany. Mozna przejsc do zadan.",
                    "en": "Lesson reviewed. You can continue to the tasks.",
                }.get(self.lang, "Lesson reviewed. You can continue to the tasks."),
                fg=GOOD,
            )
            self.feedback.config(
                text={
                    "ru": "Тема изучена. Можно переходить к заданиям.",
                    "pl": "Temat przeczytany. Mozna przejsc do zadan.",
                    "en": "Lesson reviewed. You can continue to the tasks.",
                }.get(self.lang, "Lesson reviewed. You can continue to the tasks."),
                fg=GOOD,
            )
            return
        title_buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, title_buffer, 512)
        title = title_buffer.value.lower()
        if "minecraft" not in title:
            return
        user32.keybd_event(0x1B, 0, 0, 0)
        user32.keybd_event(0x1B, 0, 0x0002, 0)
    except Exception:
        return
class ParentPanelV23(tk.Toplevel):
    def __init__(self, app: "MinecraftCoachV23") -> None:
        super().__init__(app.root)
        self.app = app
        self.lang = app.lang
        self.current_tab = ""
        self.selected_topic_id: str | None = None
        self.selected_task_id: str | None = None
        self.settings_loaded = False
        self.title(self.tt("settings"))
        self.geometry("1140x780")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.transient(app.root)
        self.app.suspend_window_lock(True)
        self.protocol("WM_DELETE_WINDOW", self.close_panel)
        self.grab_set()
        self.build()
        self.position_near_parent()
        self.after(80, self.bring_to_front)
        self.show("overview")

    def tt(self, key: str) -> str:
        return t(self.lang, key)

    def ui_text(self, ru: str, pl: str, en: str) -> str:
        return {"ru": ru, "pl": pl, "en": en}.get(self.lang, en)

    def position_near_parent(self) -> None:
        self.update_idletasks()
        x = max(20, self.app.root.winfo_rootx() + 40)
        y = max(20, self.app.root.winfo_rooty() + 36)
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{x}+{y}")
        self.bring_to_front()

    def bring_to_front(self) -> None:
        if not self.winfo_exists():
            return
        try:
            self.attributes("-topmost", True)
        except Exception:
            pass
        self.lift()
        self.focus_force()

    def build(self) -> None:
        header = tk.Frame(self, bg=PANEL, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text=self.tt("settings"),
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 22, "bold"),
        ).pack(side="left", padx=18, pady=12)
        tk.Button(
            header,
            text=self.tt("close"),
            command=self.close_panel,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        ).pack(side="right", padx=14, pady=12)

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        self.sidebar = tk.Frame(wrap, bg=CARD, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.body = tk.Frame(wrap, bg=BG)
        self.body.pack(side="left", fill="both", expand=True, padx=(14, 0))

        self.nav_buttons: dict[str, tk.Button] = {}
        for key, label in (
            ("overview", self.tt("overview")),
            ("topics", "Topics / Lessons"),
            ("modules", "Modules / module.json"),
            ("tasks", self.tt("tasks")),
            ("settings", self.tt("settings")),
        ):
            btn = tk.Button(
                self.sidebar,
                text=label,
                command=lambda current=key: self.show(current),
                bg=CARD_2,
                fg=TEXT,
                relief="flat",
                anchor="w",
                padx=18,
                pady=14,
                font=("Segoe UI", 12, "bold"),
            )
            btn.pack(fill="x", padx=10, pady=(10 if key == "overview" else 0, 8))
            self.nav_buttons[key] = btn

        self.frames = {name: tk.Frame(self.body, bg=BG) for name in self.nav_buttons}
        self.build_overview()
        self.build_topics()
        self.build_modules()
        self.build_tasks()
        self.build_settings()

    def show(self, tab: str) -> None:
        if self.current_tab == "settings" and tab != "settings":
            self.save_settings(show_message=False, close_panel=False, auto_save=True)
        if self.current_tab:
            self.frames[self.current_tab].pack_forget()
            self.nav_buttons[self.current_tab].configure(bg=CARD_2)
        self.current_tab = tab
        self.frames[tab].pack(fill="both", expand=True)
        self.nav_buttons[tab].configure(bg=ACCENT_2)
        if tab == "overview":
            self.refresh_overview()
        elif tab == "topics":
            self.refresh_topics()
        elif tab == "modules":
            self.refresh_module_editor()
        elif tab == "tasks":
            self.refresh_tasks()
        elif tab == "settings":
            self.refresh_settings()

    def pane_title(self, parent: tk.Frame, title: str) -> None:
        tk.Label(parent, text=title, bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 12))

    def build_overview(self) -> None:
        frame = self.frames["overview"]
        self.pane_title(frame, self.tt("overview"))
        self.overview_text = tk.Text(frame, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Consolas", 12))
        self.overview_text.pack(fill="both", expand=True)
        self.overview_text.configure(state="disabled")

    def refresh_overview(self) -> None:
        self.app.reload_from_db()
        dashboard = self.app.db.get_dashboard_snapshot()
        stats = self.app.stats
        lines = [
            f"{self.tt('program_id')}: {self.app.settings['program_id']}",
            f"LAN URL: {self.app.lan_url or 'disabled'}",
            f"{self.tt('coins')}: {stats['coins']}",
            f"{self.tt('correct_answers')}: {stats['correct']}",
            f"{self.tt('wrong_answers')}: {stats['wrong']}",
            f"{self.tt('completed_breaks')}: {stats['completed_breaks']}",
            f"{self.tt('child_stats')}: {stats['child_completed']}",
            f"{self.tt('adult_stats')}: {stats['adult_completed']}",
            f"{self.tt('memory_stats')}: {stats['memory_completed']}",
            f"Modules: {dashboard['counts']['modules']}",
            f"Topics: {dashboard['counts']['topics']}",
            f"Tasks: {dashboard['counts']['tasks']}",
            f"Assets: {dashboard['counts']['assets']}",
            f"Server API: {self.app.settings.get('server_base_url') or 'not configured'}",
            f"Last mode: {stats['last_mode']}",
            f"Last activity: {stats['last_activity']}",
        ]
        self.overview_text.configure(state="normal")
        self.overview_text.delete("1.0", "end")
        self.overview_text.insert("1.0", "\n".join(lines))
        self.overview_text.configure(state="disabled")

    def build_topics(self) -> None:
        frame = self.frames["topics"]
        self.pane_title(frame, "Topics / Lessons")
        top = tk.Frame(frame, bg=BG)
        top.pack(fill="both", expand=True)

        left = tk.Frame(top, bg=BG, width=330)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(top, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.topic_list = tk.Listbox(left, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 10))
        self.topic_list.pack(fill="both", expand=True)
        self.topic_list.bind("<<ListboxSelect>>", self.load_selected_topic)

        form = tk.Frame(right, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="both", expand=True)
        self.topic_widgets: dict[str, tk.Widget] = {}
        fields = [
            ("title_ru", "Title RU"),
            ("title_pl", "Title PL"),
            ("title_en", "Title EN"),
            ("description_ru", "Description RU"),
            ("description_pl", "Description PL"),
            ("description_en", "Description EN"),
            ("lesson_ru", "Lesson RU"),
            ("lesson_pl", "Lesson PL"),
            ("lesson_en", "Lesson EN"),
        ]
        for row_index, (key, label) in enumerate(fields):
            tk.Label(form, text=label, bg=CARD, fg=MUTED).grid(row=row_index, column=0, sticky="nw", padx=12, pady=6)
            widget = tk.Text(form, height=3, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
            widget.grid(row=row_index, column=1, sticky="nsew", padx=12, pady=6)
            self.topic_widgets[key] = widget
        form.grid_columnconfigure(1, weight=1)
        tk.Button(
            form,
            text=self.tt("save"),
            command=self.save_topic,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        ).grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=12, pady=12)

    def refresh_topics(self) -> None:
        self.app.reload_from_db()
        self.topic_rows = self.app.db.list_topics()
        self.topic_list.delete(0, "end")
        for topic in self.topic_rows:
            title = localized_value(topic, "title", self.lang)
            label = f"{topic['mode']} | {title}"
            self.topic_list.insert("end", label)
        if self.topic_rows:
            self.topic_list.selection_set(0)
            self.load_selected_topic()

    def load_selected_topic(self, event=None) -> None:
        selection = self.topic_list.curselection()
        if not selection:
            return
        topic = self.topic_rows[selection[0]]
        lesson = self.app.db.lesson_blocks_for_topic(topic["id"])
        lesson = lesson[0] if lesson else {}
        self.selected_topic_id = topic["id"]
        payload = {
            "title_ru": topic.get("title_ru", ""),
            "title_pl": topic.get("title_pl", ""),
            "title_en": topic.get("title_en", ""),
            "description_ru": topic.get("description_ru", ""),
            "description_pl": topic.get("description_pl", ""),
            "description_en": topic.get("description_en", ""),
            "lesson_ru": lesson.get("content_ru", ""),
            "lesson_pl": lesson.get("content_pl", ""),
            "lesson_en": lesson.get("content_en", ""),
        }
        for key, widget in self.topic_widgets.items():
            widget.delete("1.0", "end")
            widget.insert("1.0", str(payload.get(key, "")))

    def save_topic(self) -> None:
        if not self.selected_topic_id:
            return
        payload = {
            key: widget.get("1.0", "end").strip()
            for key, widget in self.topic_widgets.items()
        }
        self.app.db.update_topic(self.selected_topic_id, payload)
        self.app.reload_from_db()
        self.refresh_topics()

    def build_modules(self) -> None:
        frame = self.frames["modules"]
        self.pane_title(frame, "Modules / module.json")
        top = tk.Frame(frame, bg=BG)
        top.pack(fill="both", expand=True)

        left = tk.Frame(top, bg=BG, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(top, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        toolbar = tk.Frame(left, bg=BG)
        toolbar.pack(fill="x")
        tk.Button(
            toolbar,
            text=self.ui_text("Новый модуль", "Nowy modul", "New module"),
            command=self.create_new_module_in_editor,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left")
        tk.Button(
            toolbar,
            text=self.ui_text("Обновить список", "Odswiez liste", "Refresh list"),
            command=self.refresh_module_editor,
            bg=ACCENT_2,
            fg="white",
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left", padx=(8, 0))

        self.module_list = tk.Listbox(
            left,
            bg=CARD,
            fg=TEXT,
            selectbackground=ACCENT_2,
            selectforeground="white",
            relief="flat",
            font=("Consolas", 10),
        )
        self.module_list.pack(fill="both", expand=True, pady=(10, 0))
        self.module_list.bind("<<ListboxSelect>>", self.load_selected_module_manifest)

        info = tk.Frame(right, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        info.pack(fill="both", expand=True)
        self.module_editor_path_var = tk.StringVar(value="")
        self.module_editor_status_var = tk.StringVar(value="")
        self.module_editor_note_var = tk.StringVar(value="")

        tk.Label(
            info,
            textvariable=self.module_editor_path_var,
            bg=CARD,
            fg=TEXT,
            anchor="w",
            justify="left",
            wraplength=760,
            font=("Segoe UI", 11, "bold"),
        ).pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(
            info,
            textvariable=self.module_editor_status_var,
            bg=CARD,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=760,
        ).pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(
            info,
            textvariable=self.module_editor_note_var,
            bg=CARD,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=760,
        ).pack(fill="x", padx=12, pady=(0, 10))

        button_row = tk.Frame(info, bg=CARD)
        button_row.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(
            button_row,
            text=self.ui_text("Перезагрузить JSON", "Wczytaj JSON ponownie", "Reload JSON"),
            command=self.reload_selected_module_manifest,
            bg=CARD_2,
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left")
        tk.Button(
            button_row,
            text=self.ui_text("Сохранить module.json", "Zapisz module.json", "Save module.json"),
            command=self.save_selected_module_manifest,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left", padx=(8, 0))

        mode_row = tk.Frame(info, bg=CARD)
        mode_row.pack(fill="x", padx=12, pady=(0, 10))
        self.module_editor_mode = tk.StringVar(value="visual")
        self.module_mode_buttons: dict[str, tk.Button] = {}
        for key, label in (
            ("visual", self.ui_text("Визуальный конструктор", "Konstruktor wizualny", "Visual builder")),
            ("json", self.ui_text("Raw JSON", "Raw JSON", "Raw JSON")),
        ):
            btn = tk.Button(
                mode_row,
                text=label,
                command=lambda current=key: self.select_module_editor_mode(current),
                bg=CARD_2,
                fg=TEXT,
                relief="flat",
                padx=12,
                pady=8,
            )
            btn.pack(side="left", padx=(0 if key == "visual" else 8, 0))
            self.module_mode_buttons[key] = btn

        self.module_editor_content = tk.Frame(info, bg=CARD)
        self.module_editor_content.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.module_visual_frame = tk.Frame(self.module_editor_content, bg=CARD)
        self.module_json_frame = tk.Frame(self.module_editor_content, bg=CARD)
        self.build_module_visual_editor(self.module_visual_frame)

        editor_wrap = tk.Frame(self.module_json_frame, bg=CARD)
        editor_wrap.pack(fill="both", expand=True)
        self.module_json_text = tk.Text(
            editor_wrap,
            bg=CENTER,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Consolas", 10),
            wrap="none",
            undo=True,
        )
        y_scroll = tk.Scrollbar(editor_wrap, orient="vertical", command=self.module_json_text.yview)
        x_scroll = tk.Scrollbar(editor_wrap, orient="horizontal", command=self.module_json_text.xview)
        self.module_json_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.module_json_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        editor_wrap.grid_rowconfigure(0, weight=1)
        editor_wrap.grid_columnconfigure(0, weight=1)

        self.module_rows: list[dict] = []
        self.selected_module_folder: Path | None = None
        self.selected_module_manifest: Path | None = None
        self.module_builder_payload: dict | None = None
        self.selected_module_level_index: int | None = None
        self.selected_module_topic_index: int | None = None
        self.selected_module_lesson_index: int | None = None
        self.selected_module_task_index: int | None = None
        self.select_module_editor_mode("visual")

    def refresh_module_editor(self, *, select_path: Path | None = None) -> None:
        previous = select_path or self.selected_module_folder
        self.module_rows = list_installed_modules(self.app.db.modules_dir)
        self.module_list.delete(0, "end")
        for row in self.module_rows:
            title = localized_value(row, "title", self.lang)
            kind = str(row.get("manifest_type") or "?").upper()
            suffix = " !ERR" if row.get("error") else ""
            self.module_list.insert("end", f"[{kind}] {title}{suffix}")

        if not self.module_rows:
            self.selected_module_folder = None
            self.selected_module_manifest = None
            self.module_builder_payload = None
            self._set_module_editor_text("")
            self.refresh_module_visual_builder()
            self.module_editor_path_var.set(self.ui_text("Модулей пока нет.", "Brak modulow.", "No modules found."))
            self.module_editor_status_var.set(
                self.ui_text(
                    "Создай новый модуль из шаблона или импортируй существующий.",
                    "Utworz nowy modul z szablonu albo zaimportuj istniejacy.",
                    "Create a new module from a template or import an existing one.",
                )
            )
            self.module_editor_note_var.set("")
            return

        target_index = 0
        if previous:
            previous_str = str(previous)
            for index, row in enumerate(self.module_rows):
                if str(row["folder"]) == previous_str:
                    target_index = index
                    break
        self.module_list.selection_clear(0, "end")
        self.module_list.selection_set(target_index)
        self.module_list.activate(target_index)
        self.load_selected_module_manifest()

    def _set_module_editor_text(self, value: str) -> None:
        self.module_json_text.delete("1.0", "end")
        self.module_json_text.insert("1.0", value)

    def select_module_editor_mode(self, mode: str) -> None:
        self.module_editor_mode.set(mode)
        for frame in (self.module_visual_frame, self.module_json_frame):
            frame.pack_forget()
        active = self.module_visual_frame if mode == "visual" else self.module_json_frame
        active.pack(fill="both", expand=True)
        for key, button in self.module_mode_buttons.items():
            button.configure(bg=ACCENT_2 if key == mode else CARD_2)

    def build_module_visual_editor(self, parent: tk.Frame) -> None:
        def build_fields(container: tk.Frame, fields: list[tuple], store: dict[str, object]) -> None:
            for row_index, spec in enumerate(fields):
                key, label, kind = spec[:3]
                options = list(spec[3]) if len(spec) > 3 else []
                tk.Label(container, text=label, bg=CARD_2, fg=MUTED).grid(
                    row=row_index,
                    column=0,
                    sticky="nw",
                    padx=8,
                    pady=4,
                )
                if kind == "text":
                    widget: tk.Widget = tk.Text(
                        container,
                        height=3,
                        bg=CENTER,
                        fg=TEXT,
                        insertbackground=TEXT,
                        relief="flat",
                    )
                    store[key] = widget
                elif kind == "choice":
                    variable = tk.StringVar(value=options[0] if options else "")
                    widget = tk.OptionMenu(container, variable, *(options or [""]))
                    widget.configure(
                        bg=CENTER,
                        fg=TEXT,
                        activebackground=ACCENT_2,
                        activeforeground="white",
                        relief="flat",
                        highlightthickness=0,
                        borderwidth=0,
                    )
                    widget["menu"].configure(
                        bg=CENTER,
                        fg=TEXT,
                        activebackground=ACCENT_2,
                        activeforeground="white",
                    )
                    store[key] = {"widget": widget, "variable": variable, "kind": kind, "options": options}
                elif kind == "readonly":
                    variable = tk.StringVar(value="")
                    widget = tk.Entry(
                        container,
                        textvariable=variable,
                        state="readonly",
                        readonlybackground=CENTER,
                        fg=TEXT,
                        relief="flat",
                    )
                    store[key] = {"widget": widget, "variable": variable, "kind": kind}
                else:
                    widget = tk.Entry(
                        container,
                        bg=CENTER,
                        fg=TEXT,
                        insertbackground=TEXT,
                        relief="flat",
                    )
                    store[key] = widget
                widget.grid(row=row_index, column=1, sticky="nsew", padx=8, pady=4)
            container.grid_columnconfigure(1, weight=1)

        topic_mode_options = ["adult", "child", "memory"]
        lesson_kind_options = ["intro", "theory", "example", "summary", "practice"]
        task_type_options = ["input", "choice", "reading", "memory"]
        task_hint_options = ["concept", "rule", "word", "math", "example", "memory", "reading"]

        module_card = tk.Frame(parent, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        module_card.pack(fill="x", pady=(0, 12))
        tk.Label(
            module_card,
            text=self.ui_text("Модуль", "Modul", "Module"),
            bg=CARD_2,
            fg=TEXT,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.module_form_widgets: dict[str, object] = {}
        module_form = tk.Frame(module_card, bg=CARD_2)
        module_form.pack(fill="x", padx=8, pady=(0, 6))
        build_fields(
            module_form,
            [
                ("id", "Module ID (auto)", "readonly"),
                ("slug", "Slug", "entry"),
                ("sort_order", "Sort order", "entry"),
                ("title_ru", "Title RU", "entry"),
                ("title_pl", "Title PL", "entry"),
                ("title_en", "Title EN", "entry"),
                ("description_ru", "Description RU", "text"),
                ("description_pl", "Description PL", "text"),
                ("description_en", "Description EN", "text"),
            ],
            self.module_form_widgets,
        )
        module_buttons = tk.Frame(module_card, bg=CARD_2)
        module_buttons.pack(fill="x", padx=12, pady=(0, 10))
        tk.Button(
            module_buttons,
            text=self.ui_text("Применить модуль", "Zastosuj modul", "Apply module"),
            command=self.apply_module_form,
            bg=CARD,
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left")
        tk.Button(
            module_buttons,
            text=self.ui_text("Сохранить визуально", "Zapisz wizualnie", "Save visual"),
            command=self.save_visual_module_manifest,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            padx=12,
            pady=8,
        ).pack(side="left", padx=(8, 0))

        body = tk.Frame(parent, bg=CARD)
        body.pack(fill="both", expand=True)

        lists_col = tk.Frame(body, bg=CARD, width=340)
        lists_col.pack(side="left", fill="y")
        lists_col.pack_propagate(False)

        detail_col = tk.Frame(body, bg=CARD)
        detail_col.pack(side="left", fill="both", expand=True, padx=(12, 0))

        levels_card = tk.Frame(lists_col, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        levels_card.pack(fill="both", expand=True, pady=(0, 6))
        tk.Label(levels_card, text="Levels", bg=CARD_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        levels_buttons = tk.Frame(levels_card, bg=CARD_2)
        levels_buttons.pack(fill="x", padx=10, pady=(0, 6))
        tk.Button(levels_buttons, text="+ Level", command=self.add_module_level, bg=ACCENT, fg="#111", relief="flat", padx=10, pady=6).pack(side="left")
        tk.Button(levels_buttons, text="- Level", command=self.delete_module_level, bg=BAD, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        self.module_level_list = tk.Listbox(levels_card, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 9), height=6)
        self.module_level_list.pack(fill="x", padx=10, pady=(0, 8))
        self.module_level_list.bind("<<ListboxSelect>>", self.select_module_level)
        self.module_level_widgets: dict[str, object] = {}
        level_form = tk.Frame(levels_card, bg=CARD_2)
        level_form.pack(fill="x", padx=6, pady=(0, 6))
        build_fields(
            level_form,
            [
                ("id", "ID (auto)", "readonly"),
                ("code", "Code", "entry"),
                ("sort_order", "Sort", "entry"),
                ("title_ru", "Title RU", "entry"),
                ("title_pl", "Title PL", "entry"),
                ("title_en", "Title EN", "entry"),
            ],
            self.module_level_widgets,
        )
        tk.Button(levels_card, text=self.ui_text("Применить уровень", "Zastosuj poziom", "Apply level"), command=self.apply_selected_module_level, bg=CARD, fg=TEXT, relief="flat", padx=10, pady=6).pack(anchor="w", padx=10, pady=(0, 10))

        topics_card = tk.Frame(lists_col, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        topics_card.pack(fill="both", expand=True, pady=(6, 0))
        tk.Label(topics_card, text=self.ui_text("Темы", "Tematy", "Topics"), bg=CARD_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        topics_buttons = tk.Frame(topics_card, bg=CARD_2)
        topics_buttons.pack(fill="x", padx=10, pady=(0, 6))
        tk.Button(topics_buttons, text="+ Topic", command=self.add_module_topic, bg=ACCENT, fg="#111", relief="flat", padx=10, pady=6).pack(side="left")
        tk.Button(topics_buttons, text="Duplicate", command=self.duplicate_module_topic, bg=ACCENT_2, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        tk.Button(topics_buttons, text="- Topic", command=self.delete_module_topic, bg=BAD, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        self.module_topic_list = tk.Listbox(topics_card, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 9), height=8)
        self.module_topic_list.pack(fill="x", padx=10, pady=(0, 8))
        self.module_topic_list.bind("<<ListboxSelect>>", self.select_module_topic)
        self.module_topic_widgets: dict[str, object] = {}
        topic_form = tk.Frame(topics_card, bg=CARD_2)
        topic_form.pack(fill="x", padx=6, pady=(0, 6))
        build_fields(
            topic_form,
            [
                ("id", "ID (auto)", "readonly"),
                ("level_id", "Level ID", "entry"),
                ("slug", "Slug", "entry"),
                ("mode", "Mode", "choice", topic_mode_options),
                ("grade", "Grade", "entry"),
                ("theme", "Theme", "entry"),
                ("sort_order", "Sort", "entry"),
                ("title_ru", "Title RU", "entry"),
                ("title_pl", "Title PL", "entry"),
                ("title_en", "Title EN", "entry"),
                ("description_ru", "Description RU", "text"),
                ("description_pl", "Description PL", "text"),
                ("description_en", "Description EN", "text"),
            ],
            self.module_topic_widgets,
        )
        tk.Button(topics_card, text=self.ui_text("Применить тему", "Zastosuj temat", "Apply topic"), command=self.apply_selected_module_topic, bg=CARD, fg=TEXT, relief="flat", padx=10, pady=6).pack(anchor="w", padx=10, pady=(0, 10))

        self.module_builder_hint_var = tk.StringVar(value="")
        tk.Label(
            detail_col,
            textvariable=self.module_builder_hint_var,
            bg=CARD,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=720,
        ).pack(fill="x", pady=(0, 8))

        lessons_card = tk.Frame(detail_col, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        lessons_card.pack(fill="both", expand=True, pady=(0, 6))
        tk.Label(lessons_card, text=self.ui_text("Уроки", "Lekcje", "Lessons"), bg=CARD_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        lessons_buttons = tk.Frame(lessons_card, bg=CARD_2)
        lessons_buttons.pack(fill="x", padx=10, pady=(0, 6))
        tk.Button(lessons_buttons, text="+ Lesson", command=self.add_module_lesson, bg=ACCENT, fg="#111", relief="flat", padx=10, pady=6).pack(side="left")
        tk.Button(lessons_buttons, text="- Lesson", command=self.delete_module_lesson, bg=BAD, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        self.module_lesson_list = tk.Listbox(lessons_card, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 9), height=5)
        self.module_lesson_list.pack(fill="x", padx=10, pady=(0, 8))
        self.module_lesson_list.bind("<<ListboxSelect>>", self.select_module_lesson)
        self.module_lesson_widgets: dict[str, object] = {}
        lesson_form = tk.Frame(lessons_card, bg=CARD_2)
        lesson_form.pack(fill="x", padx=6, pady=(0, 6))
        build_fields(
            lesson_form,
            [
                ("id", "ID (auto)", "readonly"),
                ("sort_order", "Sort", "entry"),
                ("kind", "Kind", "choice", lesson_kind_options),
                ("title_ru", "Title RU", "entry"),
                ("title_pl", "Title PL", "entry"),
                ("title_en", "Title EN", "entry"),
                ("content_ru", "Content RU", "text"),
                ("content_pl", "Content PL", "text"),
                ("content_en", "Content EN", "text"),
            ],
            self.module_lesson_widgets,
        )
        tk.Button(lessons_card, text=self.ui_text("Применить урок", "Zastosuj lekcje", "Apply lesson"), command=self.apply_selected_module_lesson, bg=CARD, fg=TEXT, relief="flat", padx=10, pady=6).pack(anchor="w", padx=10, pady=(0, 10))

        tasks_card = tk.Frame(detail_col, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        tasks_card.pack(fill="both", expand=True, pady=(6, 0))
        tk.Label(tasks_card, text=self.ui_text("Задания", "Zadania", "Tasks"), bg=CARD_2, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        tasks_buttons = tk.Frame(tasks_card, bg=CARD_2)
        tasks_buttons.pack(fill="x", padx=10, pady=(0, 6))
        tk.Button(tasks_buttons, text="+ Task", command=self.add_module_task, bg=ACCENT, fg="#111", relief="flat", padx=10, pady=6).pack(side="left")
        tk.Button(tasks_buttons, text="Duplicate", command=self.duplicate_module_task, bg=ACCENT_2, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        tk.Button(tasks_buttons, text="- Task", command=self.delete_module_task, bg=BAD, fg="white", relief="flat", padx=10, pady=6).pack(side="left", padx=(6, 0))
        self.module_task_list = tk.Listbox(tasks_card, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 9), height=6)
        self.module_task_list.pack(fill="x", padx=10, pady=(0, 8))
        self.module_task_list.bind("<<ListboxSelect>>", self.select_module_task)
        self.module_task_widgets: dict[str, object] = {}
        task_form = tk.Frame(tasks_card, bg=CARD_2)
        task_form.pack(fill="x", padx=6, pady=(0, 6))
        build_fields(
            task_form,
            [
                ("id", "ID (auto)", "readonly"),
                ("type", "Type", "choice", task_type_options),
                ("mode", "Mode", "choice", topic_mode_options),
                ("grade", "Grade", "entry"),
                ("theme", "Theme", "entry"),
                ("sort_order", "Sort", "entry"),
                ("hint_type", "Hint", "choice", task_hint_options),
                ("title_ru", "Title RU", "entry"),
                ("title_pl", "Title PL", "entry"),
                ("title_en", "Title EN", "entry"),
                ("prompt_ru", "Prompt RU", "text"),
                ("prompt_pl", "Prompt PL", "text"),
                ("prompt_en", "Prompt EN", "text"),
                ("answer_text", "Answers (;)", "entry"),
                ("options_text", "Options (;)", "entry"),
            ],
            self.module_task_widgets,
        )
        tk.Button(tasks_card, text=self.ui_text("Применить задание", "Zastosuj zadanie", "Apply task"), command=self.apply_selected_module_task, bg=CARD, fg=TEXT, relief="flat", padx=10, pady=6).pack(anchor="w", padx=10, pady=(0, 10))

    def _clone_module_payload(self, payload: dict | None) -> dict:
        return json.loads(json.dumps(payload or {}, ensure_ascii=False))

    def _normalize_module_builder_payload(self, payload: dict | None) -> dict:
        normalized = self._clone_module_payload(payload)
        normalized.setdefault("id", "")
        normalized.setdefault("slug", "")
        normalized.setdefault("sort_order", 100)
        normalized.setdefault("title_ru", "")
        normalized.setdefault("title_pl", "")
        normalized.setdefault("title_en", "")
        normalized.setdefault("description_ru", "")
        normalized.setdefault("description_pl", "")
        normalized.setdefault("description_en", "")
        normalized["levels"] = [dict(item) for item in (normalized.get("levels") or [])]
        normalized["topics"] = [dict(item) for item in (normalized.get("topics") or [])]
        for topic in normalized["topics"]:
            topic.setdefault("lessons", [])
            topic.setdefault("tasks", [])
            topic["lessons"] = [dict(item) for item in (topic.get("lessons") or [])]
            topic["tasks"] = [dict(item) for item in (topic.get("tasks") or [])]
        return normalized

    def _module_levels(self) -> list[dict]:
        if not self.module_builder_payload:
            return []
        return self.module_builder_payload.setdefault("levels", [])

    def _module_topics(self) -> list[dict]:
        if not self.module_builder_payload:
            return []
        return self.module_builder_payload.setdefault("topics", [])

    def _selected_module_topic(self) -> dict | None:
        topics = self._module_topics()
        if self.selected_module_topic_index is None or self.selected_module_topic_index >= len(topics):
            return None
        return topics[self.selected_module_topic_index]

    def _selected_module_lessons(self) -> list[dict]:
        topic = self._selected_module_topic()
        if not topic:
            return []
        return topic.setdefault("lessons", [])

    def _selected_module_tasks(self) -> list[dict]:
        topic = self._selected_module_topic()
        if not topic:
            return []
        return topic.setdefault("tasks", [])

    def _clear_form_widgets(self, store: dict[str, object]) -> None:
        for widget in store.values():
            self._set_widget_value(widget, "")

    def _refresh_module_json_from_builder(self) -> None:
        if self.module_builder_payload is None:
            self._set_module_editor_text("")
            return
        self._set_module_editor_text(json.dumps(self.module_builder_payload, ensure_ascii=False, indent=2))

    def load_module_payload_into_visual_builder(self, payload: dict | None) -> None:
        self.module_builder_payload = self._normalize_module_builder_payload(payload)
        self._normalize_all_module_entities()
        self.selected_module_level_index = 0 if self._module_levels() else None
        self.selected_module_topic_index = 0 if self._module_topics() else None
        self.selected_module_lesson_index = 0 if self._selected_module_lessons() else None
        self.selected_module_task_index = 0 if self._selected_module_tasks() else None
        self.refresh_module_visual_builder()

    def refresh_module_visual_builder(self) -> None:
        if self.module_builder_payload is None:
            self._clear_form_widgets(self.module_form_widgets)
            self._clear_form_widgets(self.module_level_widgets)
            self._clear_form_widgets(self.module_topic_widgets)
            self._clear_form_widgets(self.module_lesson_widgets)
            self._clear_form_widgets(self.module_task_widgets)
            self.module_level_list.delete(0, "end")
            self.module_topic_list.delete(0, "end")
            self.module_lesson_list.delete(0, "end")
            self.module_task_list.delete(0, "end")
            self.module_builder_hint_var.set(
                self.ui_text(
                    "Выбери модуль слева или создай новый модуль.",
                    "Wybierz modul po lewej albo utworz nowy.",
                    "Select a module on the left or create a new one.",
                )
            )
            return

        self.populate_module_form()
        self.refresh_module_level_list()
        self.refresh_module_topic_list()
        self.refresh_module_lesson_list()
        self.refresh_module_task_list()
        self.module_builder_hint_var.set(
            self.ui_text(
                "Меняй форму, затем нажимай «Применить» у нужного блока. «Сохранить визуально» сразу запишет module.json.",
                "Edytuj formularze i klikaj „Zastosuj” przy odpowiednim bloku. „Zapisz wizualnie” od razu zapisze module.json.",
                "Edit the forms and click Apply on the block you changed. Save visual writes module.json right away.",
            )
        )
        self._refresh_module_json_from_builder()

    def populate_module_form(self) -> None:
        payload = self.module_builder_payload or {}
        for key, widget in self.module_form_widgets.items():
            self._set_widget_value(widget, str(payload.get(key, "")))

    def refresh_module_level_list(self) -> None:
        levels = self._module_levels()
        self.module_level_list.delete(0, "end")
        for level in levels:
            title = level.get("title_ru") or level.get("code") or level.get("id") or "-"
            token = level.get("code") or "-"
            self.module_level_list.insert("end", f"{token} | {title}")
        if not levels:
            self.selected_module_level_index = None
            self._clear_form_widgets(self.module_level_widgets)
            return
        if self.selected_module_level_index is None or self.selected_module_level_index >= len(levels):
            self.selected_module_level_index = 0
        self.module_level_list.selection_clear(0, "end")
        self.module_level_list.selection_set(self.selected_module_level_index)
        self.module_level_list.activate(self.selected_module_level_index)
        self.show_selected_module_level()

    def refresh_module_topic_list(self) -> None:
        topics = self._module_topics()
        self.module_topic_list.delete(0, "end")
        for topic in topics:
            title = topic.get("title_ru") or topic.get("slug") or topic.get("id") or "-"
            mode = topic.get("mode") or "-"
            self.module_topic_list.insert("end", f"{mode} | {title}")
        if not topics:
            self.selected_module_topic_index = None
            self.selected_module_lesson_index = None
            self.selected_module_task_index = None
            self._clear_form_widgets(self.module_topic_widgets)
            self.refresh_module_lesson_list()
            self.refresh_module_task_list()
            return
        if self.selected_module_topic_index is None or self.selected_module_topic_index >= len(topics):
            self.selected_module_topic_index = 0
        self.module_topic_list.selection_clear(0, "end")
        self.module_topic_list.selection_set(self.selected_module_topic_index)
        self.module_topic_list.activate(self.selected_module_topic_index)
        self.show_selected_module_topic()

    def refresh_module_lesson_list(self) -> None:
        lessons = self._selected_module_lessons()
        self.module_lesson_list.delete(0, "end")
        for lesson in lessons:
            title = lesson.get("title_ru") or lesson.get("kind") or lesson.get("id") or "-"
            self.module_lesson_list.insert("end", str(title))
        if not lessons:
            self.selected_module_lesson_index = None
            self._clear_form_widgets(self.module_lesson_widgets)
            return
        if self.selected_module_lesson_index is None or self.selected_module_lesson_index >= len(lessons):
            self.selected_module_lesson_index = 0
        self.module_lesson_list.selection_clear(0, "end")
        self.module_lesson_list.selection_set(self.selected_module_lesson_index)
        self.module_lesson_list.activate(self.selected_module_lesson_index)
        self.show_selected_module_lesson()

    def refresh_module_task_list(self) -> None:
        tasks = self._selected_module_tasks()
        self.module_task_list.delete(0, "end")
        for task in tasks:
            title = task.get("title_ru") or task.get("type") or task.get("id") or "-"
            token = task.get("type") or "-"
            self.module_task_list.insert("end", f"{token} | {title}")
        if not tasks:
            self.selected_module_task_index = None
            self._clear_form_widgets(self.module_task_widgets)
            return
        if self.selected_module_task_index is None or self.selected_module_task_index >= len(tasks):
            self.selected_module_task_index = 0
        self.module_task_list.selection_clear(0, "end")
        self.module_task_list.selection_set(self.selected_module_task_index)
        self.module_task_list.activate(self.selected_module_task_index)
        self.show_selected_module_task()

    def show_selected_module_level(self) -> None:
        levels = self._module_levels()
        if self.selected_module_level_index is None or self.selected_module_level_index >= len(levels):
            self._clear_form_widgets(self.module_level_widgets)
            return
        level = levels[self.selected_module_level_index]
        for key, widget in self.module_level_widgets.items():
            self._set_widget_value(widget, str(level.get(key, "")))

    def show_selected_module_topic(self) -> None:
        topic = self._selected_module_topic()
        if not topic:
            self._clear_form_widgets(self.module_topic_widgets)
            self.refresh_module_lesson_list()
            self.refresh_module_task_list()
            return
        for key, widget in self.module_topic_widgets.items():
            value = topic.get(key, "")
            self._set_widget_value(widget, "" if value is None else str(value))
        self.selected_module_lesson_index = 0 if self._selected_module_lessons() else None
        self.selected_module_task_index = 0 if self._selected_module_tasks() else None
        self.refresh_module_lesson_list()
        self.refresh_module_task_list()

    def show_selected_module_lesson(self) -> None:
        lessons = self._selected_module_lessons()
        if self.selected_module_lesson_index is None or self.selected_module_lesson_index >= len(lessons):
            self._clear_form_widgets(self.module_lesson_widgets)
            return
        lesson = lessons[self.selected_module_lesson_index]
        for key, widget in self.module_lesson_widgets.items():
            self._set_widget_value(widget, str(lesson.get(key, "")))

    def show_selected_module_task(self) -> None:
        tasks = self._selected_module_tasks()
        if self.selected_module_task_index is None or self.selected_module_task_index >= len(tasks):
            self._clear_form_widgets(self.module_task_widgets)
            return
        task = tasks[self.selected_module_task_index]
        for key, widget in self.module_task_widgets.items():
            if key == "answer_text":
                answer = task.get("answer", "")
                value = "; ".join(str(item) for item in answer) if isinstance(answer, list) else str(answer or "")
            elif key == "options_text":
                value = "; ".join(str(item) for item in (task.get("options") or []))
            else:
                raw = task.get(key, "")
                value = "" if raw is None else str(raw)
            self._set_widget_value(widget, value)

    def _builder_token(self) -> str:
        payload = self.module_builder_payload or {}
        raw = str(payload.get("slug") or payload.get("id") or "module").strip().lower()
        token = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
        return token or "module"

    def _unique_module_builder_id(self, prefix: str, existing: set[str]) -> str:
        index = 1
        candidate = f"{prefix}-{index}"
        while candidate in existing:
            index += 1
            candidate = f"{prefix}-{index}"
        return candidate

    def _builder_slug_source(self, *values: object, fallback: str = "item") -> str:
        for raw_value in values:
            normalized = normalize_input(str(raw_value or "")).strip().lower()
            token = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
            if token:
                return token
        return fallback

    def _unique_builder_token(self, base: str, existing: set[str], fallback: str = "item") -> str:
        candidate = self._builder_slug_source(base, fallback=fallback)
        index = 2
        while candidate in existing:
            candidate = f"{self._builder_slug_source(base, fallback=fallback)}-{index}"
            index += 1
        return candidate

    def _append_copy_suffix(self, value: object, suffix: str) -> str:
        text = str(value or "").strip()
        if not text:
            return suffix
        return f"{text} ({suffix})"

    def _mark_copy_titles(self, payload: dict) -> None:
        payload["title_ru"] = self._append_copy_suffix(payload.get("title_ru"), "Копия")
        payload["title_pl"] = self._append_copy_suffix(payload.get("title_pl"), "Kopia")
        payload["title_en"] = self._append_copy_suffix(payload.get("title_en"), "Copy")

    def _ensure_module_identity(self) -> None:
        if self.module_builder_payload is None:
            return
        payload = self.module_builder_payload
        payload["slug"] = self._builder_slug_source(
            payload.get("slug"),
            payload.get("title_en"),
            payload.get("title_pl"),
            payload.get("title_ru"),
            fallback="module",
        )
        payload["id"] = str(payload.get("id") or "").strip() or f"module-{payload['slug']}"

    def _ensure_level_identity(self, level: dict, index: int) -> None:
        levels = self._module_levels()
        existing_ids = {
            str(item.get("id") or "")
            for item_index, item in enumerate(levels)
            if item_index != index and str(item.get("id") or "")
        }
        level["code"] = str(level.get("code") or index + 1).strip() or str(index + 1)
        base_id = f"level-{self._builder_token()}-{self._builder_slug_source(level.get('code'), level.get('title_en'), level.get('title_pl'), level.get('title_ru'), fallback=str(index + 1))}"
        current_id = str(level.get("id") or "").strip()
        if not current_id or current_id in existing_ids:
            level["id"] = self._unique_builder_token(base_id, existing_ids, fallback=f"level-{index + 1}")

    def _ensure_topic_identity(self, topic: dict, index: int) -> None:
        topics = self._module_topics()
        existing_ids = {
            str(item.get("id") or "")
            for item_index, item in enumerate(topics)
            if item_index != index and str(item.get("id") or "")
        }
        existing_slugs = {
            str(item.get("slug") or "")
            for item_index, item in enumerate(topics)
            if item_index != index and str(item.get("slug") or "")
        }
        topic["slug"] = self._unique_builder_token(
            self._builder_slug_source(
                topic.get("slug"),
                topic.get("title_en"),
                topic.get("title_pl"),
                topic.get("title_ru"),
                topic.get("theme"),
                fallback=f"topic-{index + 1}",
            ),
            existing_slugs,
            fallback=f"topic-{index + 1}",
        )
        base_id = f"topic-{self._builder_token()}-{topic['slug']}"
        current_id = str(topic.get("id") or "").strip()
        if not current_id or current_id in existing_ids:
            topic["id"] = self._unique_builder_token(base_id, existing_ids, fallback=f"topic-{index + 1}")

    def _topic_builder_token(self, topic: dict | None, fallback_index: int = 1) -> str:
        topic = topic or {}
        return self._builder_slug_source(
            topic.get("slug"),
            topic.get("title_en"),
            topic.get("title_pl"),
            topic.get("title_ru"),
            topic.get("theme"),
            fallback=f"topic-{fallback_index}",
        )

    def _ensure_lesson_identity(self, lesson: dict, index: int, lessons: list[dict], topic: dict | None = None) -> None:
        existing_ids = {
            str(item.get("id") or "")
            for item_index, item in enumerate(lessons)
            if item_index != index and str(item.get("id") or "")
        }
        topic_token = self._topic_builder_token(topic, (self.selected_module_topic_index or 0) + 1)
        base_id = f"lesson-{topic_token}-{self._builder_slug_source(lesson.get('kind'), lesson.get('title_en'), lesson.get('title_pl'), lesson.get('title_ru'), fallback=str(index + 1))}"
        current_id = str(lesson.get("id") or "").strip()
        if not current_id or current_id in existing_ids:
            lesson["id"] = self._unique_builder_token(base_id, existing_ids, fallback=f"lesson-{index + 1}")

    def _ensure_task_identity(self, task: dict, index: int, tasks: list[dict], topic: dict | None = None) -> None:
        existing_ids = {
            str(item.get("id") or "")
            for item_index, item in enumerate(tasks)
            if item_index != index and str(item.get("id") or "")
        }
        topic_token = self._topic_builder_token(topic, (self.selected_module_topic_index or 0) + 1)
        base_id = f"task-{topic_token}-{self._builder_slug_source(task.get('type'), task.get('title_en'), task.get('title_pl'), task.get('title_ru'), fallback=str(index + 1))}"
        current_id = str(task.get("id") or "").strip()
        if not current_id or current_id in existing_ids:
            task["id"] = self._unique_builder_token(base_id, existing_ids, fallback=f"task-{index + 1}")

    def _normalize_all_module_entities(self) -> None:
        if self.module_builder_payload is None:
            return
        self._ensure_module_identity()
        for level_index, level in enumerate(self._module_levels()):
            self._ensure_level_identity(level, level_index)
        for topic_index, topic in enumerate(self._module_topics()):
            self._ensure_topic_identity(topic, topic_index)
            lessons = topic.setdefault("lessons", [])
            tasks = topic.setdefault("tasks", [])
            for lesson_index, lesson in enumerate(lessons):
                self._ensure_lesson_identity(lesson, lesson_index, lessons, topic)
            for task_index, task in enumerate(tasks):
                self._ensure_task_identity(task, task_index, tasks, topic)

    def sync_module_form_to_payload(self) -> None:
        if self.module_builder_payload is None:
            return
        for key, widget in self.module_form_widgets.items():
            value = self._get_widget_value(widget)
            if key == "sort_order":
                self.module_builder_payload[key] = safe_int(value, safe_int(self.module_builder_payload.get(key), 100))
            else:
                self.module_builder_payload[key] = value
        self._ensure_module_identity()

    def sync_selected_module_level(self) -> None:
        levels = self._module_levels()
        if self.selected_module_level_index is None or self.selected_module_level_index >= len(levels):
            return
        level = levels[self.selected_module_level_index]
        for key, widget in self.module_level_widgets.items():
            value = self._get_widget_value(widget)
            if key == "sort_order":
                level[key] = safe_int(value, safe_int(level.get(key), self.selected_module_level_index + 1))
            else:
                level[key] = value
        self._ensure_level_identity(level, self.selected_module_level_index)

    def sync_selected_module_topic(self) -> None:
        topic = self._selected_module_topic()
        if not topic:
            return
        for key, widget in self.module_topic_widgets.items():
            value = self._get_widget_value(widget)
            if key == "sort_order":
                topic[key] = safe_int(value, safe_int(topic.get(key), (self.selected_module_topic_index or 0) + 1))
            elif key == "grade":
                topic[key] = safe_int(value, 0) or None
            elif key == "level_id":
                topic[key] = value or None
            elif key == "theme":
                topic[key] = value or None
            elif key == "mode":
                topic[key] = value or "adult"
            else:
                topic[key] = value
        self._ensure_topic_identity(topic, self.selected_module_topic_index or 0)

    def sync_selected_module_lesson(self) -> None:
        lessons = self._selected_module_lessons()
        if self.selected_module_lesson_index is None or self.selected_module_lesson_index >= len(lessons):
            return
        lesson = lessons[self.selected_module_lesson_index]
        for key, widget in self.module_lesson_widgets.items():
            value = self._get_widget_value(widget)
            if key == "sort_order":
                lesson[key] = safe_int(value, safe_int(lesson.get(key), (self.selected_module_lesson_index or 0) + 1))
            elif key == "kind":
                lesson[key] = value or "intro"
            else:
                lesson[key] = value
        self._ensure_lesson_identity(
            lesson,
            self.selected_module_lesson_index,
            lessons,
            self._selected_module_topic(),
        )

    def sync_selected_module_task(self) -> None:
        tasks = self._selected_module_tasks()
        if self.selected_module_task_index is None or self.selected_module_task_index >= len(tasks):
            return
        task = tasks[self.selected_module_task_index]
        for key, widget in self.module_task_widgets.items():
            value = self._get_widget_value(widget)
            if key == "sort_order":
                task[key] = safe_int(value, safe_int(task.get(key), (self.selected_module_task_index or 0) + 1))
            elif key == "grade":
                task[key] = safe_int(value, 0) or None
            elif key == "theme":
                task[key] = value or None
            elif key == "type":
                task[key] = value or "input"
            elif key == "mode":
                task[key] = value or str(task.get("mode") or "adult")
            elif key == "hint_type":
                task[key] = value or "concept"
            elif key == "answer_text":
                answers = [item.strip() for item in value.split(";") if item.strip()]
                task_type = str(task.get("type") or "").strip().lower()
                if task_type == "reading":
                    task["answer"] = answers if len(answers) > 1 else (answers[0] if answers else "__read__")
                elif task_type == "memory":
                    task["answer"] = answers if len(answers) > 1 else (answers[0] if answers else "__memory__")
                else:
                    task["answer"] = answers if len(answers) > 1 else (answers[0] if answers else "")
            elif key == "options_text":
                task["options"] = [item.strip() for item in value.split(";") if item.strip()]
            else:
                task[key] = value
        self._ensure_task_identity(
            task,
            self.selected_module_task_index,
            tasks,
            self._selected_module_topic(),
        )

    def apply_module_form(self) -> None:
        self.sync_module_form_to_payload()
        self.refresh_module_visual_builder()

    def apply_selected_module_level(self) -> None:
        self.sync_selected_module_level()
        self.refresh_module_level_list()
        self._refresh_module_json_from_builder()

    def apply_selected_module_topic(self) -> None:
        self.sync_selected_module_topic()
        self.refresh_module_topic_list()
        self._refresh_module_json_from_builder()

    def apply_selected_module_lesson(self) -> None:
        self.sync_selected_module_lesson()
        self.refresh_module_lesson_list()
        self._refresh_module_json_from_builder()

    def apply_selected_module_task(self) -> None:
        self.sync_selected_module_task()
        self.refresh_module_task_list()
        self._refresh_module_json_from_builder()

    def add_module_level(self) -> None:
        if self.module_builder_payload is None:
            return
        self.sync_module_form_to_payload()
        self.sync_selected_module_level()
        self.sync_selected_module_topic()
        self.sync_selected_module_lesson()
        self.sync_selected_module_task()
        levels = self._module_levels()
        levels.append(
            {
                "id": "",
                "code": str(len(levels) + 1),
                "sort_order": len(levels) + 1,
                "title_ru": f"Уровень {len(levels) + 1}",
                "title_pl": f"Poziom {len(levels) + 1}",
                "title_en": f"Level {len(levels) + 1}",
            }
        )
        self.selected_module_level_index = len(levels) - 1
        self._ensure_level_identity(levels[self.selected_module_level_index], self.selected_module_level_index)
        self.refresh_module_level_list()
        self._refresh_module_json_from_builder()

    def delete_module_level(self) -> None:
        levels = self._module_levels()
        if self.selected_module_level_index is None or self.selected_module_level_index >= len(levels):
            return
        removed = levels.pop(self.selected_module_level_index)
        removed_id = str(removed.get("id") or "")
        for topic in self._module_topics():
            if str(topic.get("level_id") or "") == removed_id:
                topic["level_id"] = None
        if not levels:
            self.selected_module_level_index = None
        else:
            self.selected_module_level_index = min(self.selected_module_level_index, len(levels) - 1)
        self.refresh_module_level_list()
        self.refresh_module_topic_list()
        self._refresh_module_json_from_builder()

    def add_module_topic(self) -> None:
        if self.module_builder_payload is None:
            return
        self.sync_module_form_to_payload()
        self.sync_selected_module_level()
        self.sync_selected_module_topic()
        self.sync_selected_module_lesson()
        self.sync_selected_module_task()
        topics = self._module_topics()
        levels = self._module_levels()
        default_level_id = levels[self.selected_module_level_index]["id"] if levels and self.selected_module_level_index is not None else None
        topics.append(
            {
                "id": "",
                "level_id": default_level_id,
                "slug": "",
                "mode": "adult",
                "grade": None,
                "theme": None,
                "sort_order": len(topics) + 1,
                "title_ru": f"Новая тема {len(topics) + 1}",
                "title_pl": f"Nowy temat {len(topics) + 1}",
                "title_en": f"New topic {len(topics) + 1}",
                "description_ru": "",
                "description_pl": "",
                "description_en": "",
                "lessons": [],
                "tasks": [],
            }
        )
        self.selected_module_topic_index = len(topics) - 1
        self.selected_module_lesson_index = None
        self.selected_module_task_index = None
        self._ensure_topic_identity(topics[self.selected_module_topic_index], self.selected_module_topic_index)
        self.refresh_module_topic_list()
        self._refresh_module_json_from_builder()

    def duplicate_module_topic(self) -> None:
        topics = self._module_topics()
        if self.selected_module_topic_index is None or self.selected_module_topic_index >= len(topics):
            return
        self.sync_module_form_to_payload()
        self.sync_selected_module_level()
        self.sync_selected_module_topic()
        self.sync_selected_module_lesson()
        self.sync_selected_module_task()
        source = self._clone_module_payload(topics[self.selected_module_topic_index])
        self._mark_copy_titles(source)
        source["id"] = ""
        source["slug"] = ""
        source["sort_order"] = len(topics) + 1
        source["lessons"] = [dict(item) for item in (source.get("lessons") or [])]
        source["tasks"] = [dict(item) for item in (source.get("tasks") or [])]
        topics.append(source)
        self.selected_module_topic_index = len(topics) - 1
        self.selected_module_lesson_index = 0 if source.get("lessons") else None
        self.selected_module_task_index = 0 if source.get("tasks") else None
        self._ensure_topic_identity(source, self.selected_module_topic_index)
        for lesson_index, lesson in enumerate(source.get("lessons") or []):
            lesson["id"] = ""
            self._ensure_lesson_identity(lesson, lesson_index, source["lessons"], source)
        for task_index, task in enumerate(source.get("tasks") or []):
            task["id"] = ""
            self._ensure_task_identity(task, task_index, source["tasks"], source)
        self.refresh_module_topic_list()
        self._refresh_module_json_from_builder()

    def delete_module_topic(self) -> None:
        topics = self._module_topics()
        if self.selected_module_topic_index is None or self.selected_module_topic_index >= len(topics):
            return
        topics.pop(self.selected_module_topic_index)
        if not topics:
            self.selected_module_topic_index = None
            self.selected_module_lesson_index = None
            self.selected_module_task_index = None
        else:
            self.selected_module_topic_index = min(self.selected_module_topic_index, len(topics) - 1)
            self.selected_module_lesson_index = 0 if topics[self.selected_module_topic_index].get("lessons") else None
            self.selected_module_task_index = 0 if topics[self.selected_module_topic_index].get("tasks") else None
        self.refresh_module_topic_list()
        self._refresh_module_json_from_builder()

    def add_module_lesson(self) -> None:
        self.sync_selected_module_topic()
        topic = self._selected_module_topic()
        if not topic:
            messagebox.showinfo(APP_TITLE, self.ui_text("Сначала выбери тему.", "Najpierw wybierz temat.", "Select a topic first."), parent=self)
            return
        self.sync_selected_module_lesson()
        lessons = topic.setdefault("lessons", [])
        lessons.append(
            {
                "id": "",
                "sort_order": len(lessons) + 1,
                "kind": "intro",
                "title_ru": f"Урок {len(lessons) + 1}",
                "title_pl": f"Lekcja {len(lessons) + 1}",
                "title_en": f"Lesson {len(lessons) + 1}",
                "content_ru": "",
                "content_pl": "",
                "content_en": "",
            }
        )
        self.selected_module_lesson_index = len(lessons) - 1
        self._ensure_lesson_identity(lessons[self.selected_module_lesson_index], self.selected_module_lesson_index, lessons, topic)
        self.refresh_module_lesson_list()
        self._refresh_module_json_from_builder()

    def delete_module_lesson(self) -> None:
        lessons = self._selected_module_lessons()
        if self.selected_module_lesson_index is None or self.selected_module_lesson_index >= len(lessons):
            return
        lessons.pop(self.selected_module_lesson_index)
        self.selected_module_lesson_index = min(self.selected_module_lesson_index, len(lessons) - 1) if lessons else None
        self.refresh_module_lesson_list()
        self._refresh_module_json_from_builder()

    def add_module_task(self) -> None:
        self.sync_selected_module_topic()
        topic = self._selected_module_topic()
        if not topic:
            messagebox.showinfo(APP_TITLE, self.ui_text("Сначала выбери тему.", "Najpierw wybierz temat.", "Select a topic first."), parent=self)
            return
        self.sync_selected_module_task()
        tasks = topic.setdefault("tasks", [])
        tasks.append(
            {
                "id": "",
                "type": "input",
                "mode": str(topic.get("mode") or "adult"),
                "grade": topic.get("grade"),
                "theme": topic.get("theme"),
                "sort_order": len(tasks) + 1,
                "hint_type": "concept",
                "title_ru": f"Задание {len(tasks) + 1}",
                "title_pl": f"Zadanie {len(tasks) + 1}",
                "title_en": f"Task {len(tasks) + 1}",
                "prompt_ru": "",
                "prompt_pl": "",
                "prompt_en": "",
                "answer": "",
                "options": [],
            }
        )
        self.selected_module_task_index = len(tasks) - 1
        self._ensure_task_identity(tasks[self.selected_module_task_index], self.selected_module_task_index, tasks, topic)
        self.refresh_module_task_list()
        self._refresh_module_json_from_builder()

    def duplicate_module_task(self) -> None:
        tasks = self._selected_module_tasks()
        topic = self._selected_module_topic()
        if (
            not topic
            or self.selected_module_task_index is None
            or self.selected_module_task_index >= len(tasks)
        ):
            return
        self.sync_selected_module_topic()
        self.sync_selected_module_task()
        copy_task = self._clone_module_payload(tasks[self.selected_module_task_index])
        self._mark_copy_titles(copy_task)
        copy_task["id"] = ""
        copy_task["sort_order"] = len(tasks) + 1
        tasks.append(copy_task)
        self.selected_module_task_index = len(tasks) - 1
        self._ensure_task_identity(copy_task, self.selected_module_task_index, tasks, topic)
        self.refresh_module_task_list()
        self._refresh_module_json_from_builder()

    def delete_module_task(self) -> None:
        tasks = self._selected_module_tasks()
        if self.selected_module_task_index is None or self.selected_module_task_index >= len(tasks):
            return
        tasks.pop(self.selected_module_task_index)
        self.selected_module_task_index = min(self.selected_module_task_index, len(tasks) - 1) if tasks else None
        self.refresh_module_task_list()
        self._refresh_module_json_from_builder()

    def select_module_level(self, event=None) -> None:
        self.sync_selected_module_level()
        selection = self.module_level_list.curselection()
        if not selection:
            return
        self.selected_module_level_index = selection[0]
        self.show_selected_module_level()
        self._refresh_module_json_from_builder()

    def select_module_topic(self, event=None) -> None:
        self.sync_selected_module_topic()
        self.sync_selected_module_lesson()
        self.sync_selected_module_task()
        selection = self.module_topic_list.curselection()
        if not selection:
            return
        self.selected_module_topic_index = selection[0]
        self.selected_module_lesson_index = 0 if self._selected_module_lessons() else None
        self.selected_module_task_index = 0 if self._selected_module_tasks() else None
        self.show_selected_module_topic()
        self._refresh_module_json_from_builder()

    def select_module_lesson(self, event=None) -> None:
        self.sync_selected_module_lesson()
        selection = self.module_lesson_list.curselection()
        if not selection:
            return
        self.selected_module_lesson_index = selection[0]
        self.show_selected_module_lesson()
        self._refresh_module_json_from_builder()

    def select_module_task(self, event=None) -> None:
        self.sync_selected_module_task()
        selection = self.module_task_list.curselection()
        if not selection:
            return
        self.selected_module_task_index = selection[0]
        self.show_selected_module_task()
        self._refresh_module_json_from_builder()

    def save_visual_module_manifest(self) -> None:
        if not self.selected_module_folder or self.module_builder_payload is None:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text("Сначала выбери модуль слева.", "Najpierw wybierz modul po lewej.", "Select a module on the left first."),
                parent=self,
            )
            return
        try:
            self.sync_module_form_to_payload()
            self.sync_selected_module_level()
            self.sync_selected_module_topic()
            self.sync_selected_module_lesson()
            self.sync_selected_module_task()
            self._normalize_all_module_entities()
            manifest_path = save_module_json(self.selected_module_folder, self.module_builder_payload)
        except ModuleImportError as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self)
            return

        modules = self.app.sync_modules_from_disk(refresh_start_screen=self.app.current_topic is None)
        self.refresh_overview()
        self.refresh_settings()
        self.refresh_topics()
        self.refresh_tasks()
        self.refresh_module_editor(select_path=self.selected_module_folder)
        messagebox.showinfo(
            APP_TITLE,
            "\n".join(
                [
                    self.ui_text("Модуль сохранён визуальным конструктором.", "Modul zapisano w konstruktorze wizualnym.", "Module saved from the visual builder."),
                    f"{self.ui_text('Файл', 'Plik', 'File')}: {manifest_path}",
                    f"{self.ui_text('Модулей в приложении', 'Moduly w aplikacji', 'Modules in app')}: {len(modules)}",
                ]
            ),
            parent=self,
        )

    def load_selected_module_manifest(self, event=None) -> None:
        selection = self.module_list.curselection()
        if not selection or not self.module_rows:
            return
        row = self.module_rows[selection[0]]
        self.selected_module_folder = Path(row["folder"])
        self.selected_module_manifest = Path(row["manifest_path"])
        self.module_editor_path_var.set(
            f"{self.ui_text('Папка', 'Folder', 'Folder')}: {row['folder']}\n"
            f"{self.ui_text('Манифест', 'Manifest', 'Manifest')}: {row['manifest_path']}"
        )
        manifest_type = str(row.get("manifest_type") or "").upper()
        if row.get("error"):
            self.module_builder_payload = None
            self.module_editor_status_var.set(
                self.ui_text(
                    f"Ошибка загрузки модуля. Тип: {manifest_type}",
                    f"Blad ladowania modulu. Typ: {manifest_type}",
                    f"Module load error. Type: {manifest_type}",
                )
            )
            self.module_editor_note_var.set(str(row["error"]))
            self._set_module_editor_text(str(row.get("raw_text") or ""))
            self.refresh_module_visual_builder()
            self.select_module_editor_mode("json")
            return

        payload = row.get("payload") or {}
        self._set_module_editor_text(json.dumps(payload, ensure_ascii=False, indent=2))
        self.load_module_payload_into_visual_builder(payload)
        self.module_editor_status_var.set(
            self.ui_text(
                f"Редактируемый источник: {manifest_type}",
                f"Edytowalne zrodlo: {manifest_type}",
                f"Editable source: {manifest_type}",
            )
        )
        if manifest_type == "PY":
            self.module_editor_note_var.set(
                self.ui_text(
                    "Если сохранить изменения, рядом будет создан module.json, и именно он станет приоритетным для этого модуля.",
                    "Po zapisaniu zmian obok zostanie utworzony module.json i to on stanie sie priorytetowy dla tego modulu.",
                    "When you save, a module.json file will be created next to the Python manifest and will become the preferred source.",
                )
            )
        else:
            self.module_editor_note_var.set(
                self.ui_text(
                    "Измени JSON и нажми сохранить. После сохранения модуль сразу пересинхронизируется в приложении.",
                    "Edytuj JSON i kliknij zapisz. Po zapisie modul od razu zsynchronizuje sie w aplikacji.",
                    "Edit the JSON and click save. The module will be synchronized in the app right away.",
                )
            )
        self.select_module_editor_mode("visual")

    def reload_selected_module_manifest(self) -> None:
        if not self.selected_module_folder:
            self.refresh_module_editor()
            return
        self.refresh_module_editor(select_path=self.selected_module_folder)

    def create_new_module_in_editor(self) -> None:
        try:
            target_dir = create_module_from_template(MODULE_TEMPLATE_DIR, self.app.db.modules_dir)
            manifest = target_dir / "module.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            folder_name = target_dir.name
            payload["id"] = f"module-{folder_name}"
            payload["slug"] = folder_name
            payload["title_ru"] = "Новый модуль"
            payload["title_pl"] = "Nowy modul"
            payload["title_en"] = "New module"
            payload["description_ru"] = "Отредактируй этот модуль в редакторе справа и сохрани изменения."
            payload["description_pl"] = "Edytuj ten modul w edytorze po prawej stronie i zapisz zmiany."
            payload["description_en"] = "Edit this module in the editor on the right and save your changes."
            for topic_index, topic in enumerate(payload.get("topics") or [], start=1):
                topic["id"] = f"topic-{folder_name}-{topic_index}"
                topic["slug"] = topic.get("slug") or f"topic-{topic_index}"
                for lesson_index, lesson in enumerate(topic.get("lessons") or [], start=1):
                    lesson["id"] = f"lesson-{folder_name}-{topic_index}-{lesson_index}"
                for task_index, task in enumerate(topic.get("tasks") or [], start=1):
                    task["id"] = f"task-{folder_name}-{topic_index}-{task_index}"
            save_module_json(target_dir, payload)
        except (ModuleImportError, json.JSONDecodeError) as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self)
            return

        self.app.sync_modules_from_disk(refresh_start_screen=self.app.current_topic is None)
        self.refresh_overview()
        self.refresh_settings()
        self.refresh_module_editor(select_path=target_dir)
        self.select_module_editor_mode("visual")
        messagebox.showinfo(
            APP_TITLE,
            self.ui_text(
                f"Создан новый модуль: {target_dir}",
                f"Utworzono nowy modul: {target_dir}",
                f"New module created: {target_dir}",
            ),
            parent=self,
        )

    def save_selected_module_manifest(self) -> None:
        if not self.selected_module_folder:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text("Сначала выбери модуль слева.", "Najpierw wybierz modul po lewej.", "Select a module on the left first."),
                parent=self,
            )
            return
        raw = self.module_json_text.get("1.0", "end").strip()
        if not raw:
            messagebox.showerror(
                APP_TITLE,
                self.ui_text("JSON не может быть пустым.", "JSON nie moze byc pusty.", "JSON cannot be empty."),
                parent=self,
            )
            return
        try:
            payload = json.loads(raw)
            manifest_path = save_module_json(self.selected_module_folder, payload)
        except (ModuleImportError, json.JSONDecodeError) as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self)
            return

        modules = self.app.sync_modules_from_disk(refresh_start_screen=self.app.current_topic is None)
        self.refresh_overview()
        self.refresh_settings()
        self.refresh_topics()
        self.refresh_tasks()
        self.refresh_module_editor(select_path=self.selected_module_folder)
        self.select_module_editor_mode("json")
        messagebox.showinfo(
            APP_TITLE,
            "\n".join(
                [
                    self.ui_text("Модуль сохранён.", "Modul zapisany.", "Module saved."),
                    f"{self.ui_text('Файл', 'Plik', 'File')}: {manifest_path}",
                    f"{self.ui_text('Модулей в приложении', 'Moduly w aplikacji', 'Modules in app')}: {len(modules)}",
                ]
            ),
            parent=self,
        )

    def build_tasks(self) -> None:
        frame = self.frames["tasks"]
        self.pane_title(frame, self.tt("tasks"))
        top = tk.Frame(frame, bg=BG)
        top.pack(fill="both", expand=True)

        left = tk.Frame(top, bg=BG, width=360)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(top, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        filter_row = tk.Frame(left, bg=BG)
        filter_row.pack(fill="x")
        tk.Label(filter_row, text="Mode", bg=BG, fg=MUTED).pack(side="left")
        self.task_mode_var = tk.StringVar(value="all")
        tk.OptionMenu(filter_row, self.task_mode_var, "all", "child", "adult", "memory").pack(side="left", padx=8)
        tk.Button(filter_row, text=self.tt("save"), command=self.refresh_tasks, bg=ACCENT_2, fg="white", relief="flat").pack(side="left", padx=8)

        self.task_list = tk.Listbox(left, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 10))
        self.task_list.pack(fill="both", expand=True, pady=(10, 0))
        self.task_list.bind("<<ListboxSelect>>", self.load_selected_task)

        form = tk.Frame(right, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="both", expand=True)
        self.task_widgets: dict[str, tk.Widget] = {}
        fields = [
            ("topic_id", "Topic ID"),
            ("mode", "Mode"),
            ("grade", "Grade"),
            ("theme", "Theme"),
            ("type", "Type"),
            ("hint_type", "Hint"),
            ("title_ru", "Title RU"),
            ("title_pl", "Title PL"),
            ("title_en", "Title EN"),
            ("prompt_ru", "Prompt RU"),
            ("prompt_pl", "Prompt PL"),
            ("prompt_en", "Prompt EN"),
            ("accepted_answers", "Accepted answers (; separated)"),
            ("options", "Options (; separated)"),
        ]
        for row_index, (key, label) in enumerate(fields):
            tk.Label(form, text=label, bg=CARD, fg=MUTED).grid(row=row_index, column=0, sticky="nw", padx=12, pady=6)
            if key in {"prompt_ru", "prompt_pl", "prompt_en"}:
                widget = tk.Text(form, height=3, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
            else:
                widget = tk.Entry(form, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
            widget.grid(row=row_index, column=1, sticky="nsew", padx=12, pady=6)
            self.task_widgets[key] = widget
        form.grid_columnconfigure(1, weight=1)
        button_row = tk.Frame(form, bg=CARD)
        button_row.grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=12, pady=12)
        tk.Button(button_row, text=self.tt("save"), command=self.save_task, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(side="left")
        tk.Button(button_row, text="Delete", command=self.delete_task, bg=BAD, fg="white", relief="flat", padx=14, pady=8).pack(side="left", padx=(8, 0))

    def refresh_tasks(self) -> None:
        self.app.reload_from_db()
        mode = self.task_mode_var.get()
        rows = self.app.tasks
        if mode != "all":
            rows = [task for task in rows if task["mode"] == mode]
        self.task_rows = rows
        self.task_list.delete(0, "end")
        for task in rows:
            title = localized_value(task, "title", self.lang)
            token = task.get("grade") or task.get("theme") or task.get("topic_slug") or "-"
            self.task_list.insert("end", f"{task['mode']} | {token} | {title}")
        if self.task_rows:
            self.task_list.selection_set(0)
            self.load_selected_task()

    def _set_widget_value(self, widget: object, value: str) -> None:
        if isinstance(widget, dict):
            variable = widget.get("variable")
            if isinstance(variable, tk.StringVar):
                variable.set(value)
                return
            widget = widget.get("widget")
        if isinstance(widget, tk.Text):
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
            return
        if isinstance(widget, tk.Entry):
            state = str(widget.cget("state"))
            if state in {"readonly", "disabled"}:
                widget.configure(state="normal")
                widget.delete(0, "end")
                widget.insert(0, value)
                widget.configure(state=state)
                return
        widget.delete(0, "end")
        widget.insert(0, value)

    def _get_widget_value(self, widget: object) -> str:
        if isinstance(widget, dict):
            variable = widget.get("variable")
            if isinstance(variable, tk.StringVar):
                return variable.get().strip()
            widget = widget.get("widget")
        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def load_selected_task(self, event=None) -> None:
        selection = self.task_list.curselection()
        if not selection:
            return
        task = self.task_rows[selection[0]]
        self.selected_task_id = task["id"]
        payload = {
            "topic_id": task.get("topic_id", ""),
            "mode": task.get("mode", ""),
            "grade": str(task.get("grade") or ""),
            "theme": str(task.get("theme") or ""),
            "type": task.get("type", ""),
            "hint_type": task.get("hint_type", ""),
            "title_ru": task.get("title_ru", ""),
            "title_pl": task.get("title_pl", ""),
            "title_en": task.get("title_en", ""),
            "prompt_ru": task.get("prompt_ru", ""),
            "prompt_pl": task.get("prompt_pl", ""),
            "prompt_en": task.get("prompt_en", ""),
            "accepted_answers": "; ".join(task.get("accepted_answers") or []),
            "options": "; ".join(task.get("options") or []),
        }
        for key, widget in self.task_widgets.items():
            self._set_widget_value(widget, payload.get(key, ""))

    def save_task(self) -> None:
        if not self.selected_task_id:
            return
        payload = {key: self._get_widget_value(widget) for key, widget in self.task_widgets.items()}
        answers = [item.strip() for item in payload.pop("accepted_answers", "").split(";") if item.strip()]
        options = [item.strip() for item in payload.pop("options", "").split(";") if item.strip()]
        payload["grade"] = safe_int(payload.get("grade"), 0) or None
        payload["accepted_answers"] = answers
        payload["options"] = options
        payload["answer"] = answers if len(answers) != 1 else (answers[0] if answers else "")
        self.app.db.update_task(self.selected_task_id, payload)
        self.app.reload_from_db()
        self.refresh_tasks()

    def delete_task(self) -> None:
        if not self.selected_task_id:
            return
        self.app.db.delete_task(self.selected_task_id)
        self.app.reload_from_db()
        self.refresh_tasks()

    def build_settings(self) -> None:
        frame = self.frames["settings"]
        self.pane_title(frame, self.tt("settings"))
        card = tk.Frame(frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")
        self.settings_widgets: dict[str, tk.Widget] = {}
        self.modules_path_var = tk.StringVar(value="")
        self.module_template_var = tk.StringVar(value="")
        self.module_status_var = tk.StringVar(value="")
        self.pause_settings_info_var = tk.StringVar(value="")
        fields = [
            ("break_seconds", self.tt("break_seconds")),
            ("tasks_per_break", "Tasks per break"),
            ("lesson_seconds", "Lesson seconds"),
            ("manual_pause_uses", self.ui_text("Паузы для ученика (1-2)", "Pauzy ucznia (1-2)", "Student pauses (1-2)")),
            ("manual_pause_minutes", self.ui_text("Длительность паузы (мин)", "Dlugosc pauzy (min)", "Pause length (min)")),
            ("lan_admin_port", "LAN port"),
            ("server_base_url", "Server API URL"),
        ]
        for row_index, (key, label) in enumerate(fields):
            tk.Label(card, text=label, bg=CARD, fg=MUTED).grid(row=row_index, column=0, sticky="w", padx=12, pady=12)
            entry = tk.Entry(card, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
            entry.grid(row=row_index, column=1, sticky="ew", padx=12, pady=12)
            self.settings_widgets[key] = entry

        lang_row = len(fields)
        tk.Label(card, text=self.tt("language"), bg=CARD, fg=MUTED).grid(row=lang_row, column=0, sticky="w", padx=12, pady=12)
        self.parent_lang_var = tk.StringVar(value=self.app.lang)
        tk.OptionMenu(card, self.parent_lang_var, "ru", "pl", "en").grid(row=lang_row, column=1, sticky="w", padx=12, pady=12)

        program_row = lang_row + 1
        tk.Label(card, text=self.tt("program_id"), bg=CARD, fg=MUTED).grid(row=program_row, column=0, sticky="w", padx=12, pady=12)
        self.program_id_label = tk.Label(card, text="", bg=CARD, fg=TEXT, font=("Consolas", 12, "bold"))
        self.program_id_label.grid(row=program_row, column=1, sticky="w", padx=12, pady=12)

        password_row = program_row + 1
        tk.Label(card, text="New password", bg=CARD, fg=MUTED).grid(row=password_row, column=0, sticky="w", padx=12, pady=12)
        self.password_entry = tk.Entry(card, show="*", bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.password_entry.grid(row=password_row, column=1, sticky="ew", padx=12, pady=12)

        confirm_row = password_row + 1
        tk.Label(card, text="Repeat password", bg=CARD, fg=MUTED).grid(row=confirm_row, column=0, sticky="w", padx=12, pady=12)
        self.password_confirm_entry = tk.Entry(card, show="*", bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.password_confirm_entry.grid(row=confirm_row, column=1, sticky="ew", padx=12, pady=12)

        button_row = confirm_row + 1
        tk.Button(
            card,
            text=self.tt("save"),
            command=self.save_settings,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        ).grid(row=button_row, column=0, columnspan=2, sticky="w", padx=12, pady=12)

        modules_row = button_row + 1
        tk.Label(card, text=self.ui_text("Модули", "Moduly", "Modules"), bg=CARD, fg=MUTED).grid(row=modules_row, column=0, sticky="nw", padx=12, pady=12)
        modules_box = tk.Frame(card, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        modules_box.grid(row=modules_row, column=1, sticky="ew", padx=12, pady=12)
        tk.Label(
            modules_box,
            textvariable=self.modules_path_var,
            bg=CARD_2,
            fg=TEXT,
            justify="left",
            anchor="w",
            wraplength=640,
        ).pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(
            modules_box,
            textvariable=self.module_template_var,
            bg=CARD_2,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=640,
        ).pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(
            modules_box,
            textvariable=self.module_status_var,
            bg=CARD_2,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=640,
        ).pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(
            modules_box,
            textvariable=self.pause_settings_info_var,
            bg=CARD_2,
            fg=TEXT,
            justify="left",
            anchor="w",
            wraplength=640,
        ).pack(fill="x", padx=12, pady=(0, 10))

        top_buttons = tk.Frame(modules_box, bg=CARD_2)
        top_buttons.pack(anchor="w", padx=12, pady=(0, 8))
        tk.Button(
            top_buttons,
            text=self.ui_text("Открыть папку модулей", "Otworz folder modulow", "Open modules folder"),
            command=self.open_modules_folder,
            bg=ACCENT_2,
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            top_buttons,
            text=self.ui_text("Обновить модули", "Odswiez moduly", "Refresh modules"),
            command=lambda: self.refresh_modules(announce=True),
            bg=CARD,
            fg=TEXT,
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left")

        bottom_buttons = tk.Frame(modules_box, bg=CARD_2)
        bottom_buttons.pack(anchor="w", padx=12, pady=(0, 12))
        tk.Button(
            bottom_buttons,
            text=self.ui_text("Импорт папки...", "Import folderu...", "Import folder..."),
            command=self.import_module_folder_dialog,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            bottom_buttons,
            text=self.ui_text("Импорт zip/json...", "Import zip/json...", "Import zip/json..."),
            command=self.import_module_file_dialog,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            bottom_buttons,
            text=self.ui_text("Создать шаблон...", "Utworz szablon...", "Create template..."),
            command=self.export_template_dialog,
            bg=CARD,
            fg=TEXT,
            relief="flat",
            padx=14,
            pady=8,
        ).pack(side="left")
        card.grid_columnconfigure(1, weight=1)

    def refresh_settings(self) -> None:
        self.app.reload_from_db()
        self.lang = self.app.lang
        self.settings_loaded = True
        self.program_id_label.configure(text=self.app.settings["program_id"])
        for key, widget in self.settings_widgets.items():
            widget.delete(0, "end")
            widget.insert(0, str(self.app.settings.get(key, "")))
        self.parent_lang_var.set(self.app.lang)
        self.password_entry.delete(0, "end")
        self.password_confirm_entry.delete(0, "end")
        module_count = len(self.app.db.list_modules())
        pause_min, pause_max = self.app.pause_duration_bounds()
        extra_tokens = safe_int(self.app.settings.get("shop_extra_pause_tokens"), 0)
        upgrade_level = safe_int(self.app.settings.get("pause_upgrade_level"), 0)
        self.modules_path_var.set(f"{self.ui_text('Папка модулей', 'Folder modulow', 'Modules folder')}: {self.app.db.modules_dir}")
        self.module_template_var.set(f"{self.ui_text('Шаблон модуля', 'Szablon modulu', 'Module template')}: {MODULE_TEMPLATE_DIR}")
        self.module_status_var.set(
            self.ui_text(
                f"Загружено модулей: {module_count}. Можно импортировать архив, JSON или просто открыть папку модулей и положить туда новую папку.",
                f"Zaladowane moduly: {module_count}. Mozesz zaimportowac archiwum, JSON albo po prostu otworzyc folder modulow i wkleic tam nowy katalog.",
                f"Loaded modules: {module_count}. You can import a zip/JSON file or just open the modules folder and drop a new module folder there.",
            )
        )
        self.pause_settings_info_var.set(
            self.ui_text(
                f"Уровень улучшения паузы: {upgrade_level}/4. Сейчас можно поставить {pause_min}-{pause_max} мин. Доп. паузы в запасе: {extra_tokens}.",
                f"Poziom ulepszenia pauzy: {upgrade_level}/4. Teraz mozna ustawic {pause_min}-{pause_max} min. Dodatkowe pauzy w zapasie: {extra_tokens}.",
                f"Pause upgrade level: {upgrade_level}/4. You can currently set {pause_min}-{pause_max} min. Extra pauses in reserve: {extra_tokens}.",
            )
        )

    def save_settings(self, *, show_message: bool = True, close_panel: bool = True, auto_save: bool = False) -> bool:
        if auto_save and not self.settings_loaded:
            return True
        updates = {}
        for key, widget in self.settings_widgets.items():
            raw = widget.get().strip()
            if key in {"break_seconds", "tasks_per_break", "lesson_seconds", "lan_admin_port"}:
                updates[key] = max(1, safe_int(raw, safe_int(self.app.settings.get(key), 1)))
            elif key == "manual_pause_uses":
                updates[key] = min(2, max(1, safe_int(raw, safe_int(self.app.settings.get(key), 1))))
            elif key == "manual_pause_minutes":
                pause_min, pause_max = self.app.pause_duration_bounds()
                current_value = safe_int(raw, safe_int(self.app.settings.get(key), pause_min))
                updates[key] = min(pause_max, max(pause_min, current_value))
            else:
                updates[key] = raw
        updates["window_language"] = self.parent_lang_var.get()
        password = self.password_entry.get().strip()
        confirm = self.password_confirm_entry.get().strip()
        if password or confirm:
            if password != confirm:
                if auto_save:
                    password = ""
                    confirm = ""
                else:
                    messagebox.showerror(APP_TITLE, "Passwords do not match", parent=self)
                    return False
            if len(password) < 4:
                if auto_save:
                    password = ""
                else:
                    messagebox.showerror(APP_TITLE, "Password must contain at least 4 characters", parent=self)
                    return False
            if password and password == confirm:
                self.app.db.update_parent_password(password)
        self.app.db.update_settings(updates)
        self.app.reload_from_db()
        self.app.start_lan_server_if_needed()
        self.app.refresh_language()
        self.app.queue_remote_sync(250)
        if show_message:
            messagebox.showinfo(APP_TITLE, self.tt("save"), parent=self)
        if close_panel:
            self.destroy()
        return True

    def close_panel(self) -> None:
        self.save_settings(show_message=False, close_panel=False, auto_save=True)
        try:
            self.grab_release()
        except Exception:
            pass
        if getattr(self.app, "parent_panel_window", None) is self:
            self.app.parent_panel_window = None
        self.destroy()
        self.app.root.after(20, lambda: self.app.suspend_window_lock(False))

    def open_modules_folder(self) -> None:
        self.app.db.modules_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(self.app.db.modules_dir)  # type: ignore[attr-defined]
        except Exception:
            messagebox.showinfo(APP_TITLE, str(self.app.db.modules_dir), parent=self)

    def refresh_modules(self, *, announce: bool = False) -> None:
        modules = self.app.sync_modules_from_disk(refresh_start_screen=self.app.current_topic is None)
        self.refresh_settings()
        self.refresh_overview()
        if self.current_tab == "topics":
            self.refresh_topics()
        elif self.current_tab == "modules":
            self.refresh_module_editor()
        elif self.current_tab == "tasks":
            self.refresh_tasks()
        if announce:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text(
                    f"Модули обновлены. Сейчас доступно: {len(modules)}.",
                    f"Moduly zostaly odswiezone. Teraz dostepne: {len(modules)}.",
                    f"Modules refreshed. Available now: {len(modules)}.",
                ),
                parent=self,
            )

    def import_module_folder_dialog(self) -> None:
        selected = filedialog.askdirectory(
            parent=self,
            title=self.ui_text("Выберите папку модуля", "Wybierz folder modulu", "Choose a module folder"),
            mustexist=True,
        )
        if not selected:
            return
        self.import_module(Path(selected))

    def import_module_file_dialog(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title=self.ui_text("Выберите файл модуля", "Wybierz plik modulu", "Choose a module file"),
            filetypes=[
                ("Module packages", "*.zip *.json *.py"),
                ("ZIP archives", "*.zip"),
                ("JSON modules", "*.json"),
                ("Python modules", "*.py"),
                ("All files", "*.*"),
            ],
        )
        if not selected:
            return
        self.import_module(Path(selected))

    def export_template_dialog(self) -> None:
        destination = filedialog.askdirectory(
            parent=self,
            title=self.ui_text("Куда сохранить шаблон модуля", "Gdzie zapisac szablon modulu", "Where to save the module template"),
            mustexist=True,
        )
        if not destination:
            return
        try:
            created = export_module_template(MODULE_TEMPLATE_DIR, Path(destination))
        except ModuleImportError as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self)
            return
        messagebox.showinfo(
            APP_TITLE,
            self.ui_text(
                f"Шаблон создан: {created}",
                f"Szablon zostal utworzony: {created}",
                f"Template created: {created}",
            ),
            parent=self,
        )

    def import_module(self, source: Path) -> None:
        try:
            result = import_module_source(
                source,
                self.app.db.modules_dir,
                backups_dir=MODULE_BACKUPS_DIR,
            )
        except ModuleImportError as exc:
            messagebox.showerror(APP_TITLE, str(exc), parent=self)
            return

        modules = self.app.sync_modules_from_disk(refresh_start_screen=self.app.current_topic is None)
        self.refresh_settings()
        self.refresh_overview()
        if self.current_tab == "topics":
            self.refresh_topics()
        elif self.current_tab == "modules":
            self.refresh_module_editor()
        elif self.current_tab == "tasks":
            self.refresh_tasks()

        details = [
            self.ui_text("Модуль импортирован.", "Modul zostal zaimportowany.", "Module imported."),
            f"ID: {result['module_id']}",
            f"Slug: {result['module_slug']}",
            f"{self.ui_text('Папка', 'Folder', 'Folder')}: {result['target_dir']}",
            f"{self.ui_text('Доступно модулей', 'Dostepne moduly', 'Available modules')}: {len(modules)}",
        ]
        if result.get("backup_path"):
            details.append(f"{self.ui_text('Резервная копия', 'Kopia zapasowa', 'Backup')}: {result['backup_path']}")
        messagebox.showinfo(APP_TITLE, "\n".join(details), parent=self)


class MinecraftCoachV23:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_TITLE} v23")
        self.root.configure(bg=BG)
        self.root.geometry("1320x840")
        self.root.minsize(960, 640)
        self.root.protocol("WM_DELETE_WINDOW", self.request_close)
        self.root.bind("<Escape>", lambda _event: "break")
        self.root.bind("<Unmap>", self.on_root_unmap, add="+")
        self.root.bind("<FocusOut>", self.on_root_focus_out, add="+")

        self.db = LocalDB(
            DB_FILE,
            seed_path=SEED_DB,
            data_dir=DATA_DIR,
            assets_dir=ELECTRYK_DIR,
            modules_dir=MODULES_DIR,
        )
        self.lan_server: LanAdminServer | None = None
        self.lan_url = ""

        self.current_topic: dict | None = None
        self.current_module: dict | None = None
        self.current_break_tasks: list[dict] = []
        self.current_task: dict | None = None
        self.current_index = 0
        self.lesson_blocks: list[dict] = []
        self.lesson_index = 0
        self.lesson_after_id = None
        self.lesson_seconds_left = 0
        self.memory_after_id = None
        self.memory_seconds_left = 0
        self.break_after_id = None
        self.break_deadline_ts: float | None = None
        self.program_mode = "child"
        self.break_lock_active = False
        self.password_dialog: tk.Toplevel | None = None
        self.password_dialog_open = False
        self.parent_panel_window: ParentPanelV23 | None = None
        self.shop_window: tk.Toplevel | None = None
        self.overlay_kind = "start"
        self.overlay_payload: dict | None = None
        self.layout_after_id = None
        self.geometry_after_id = None
        self.window_lock_applied = False
        self.window_lock_suspended = False
        self.window_restore_geometry = ""
        self.window_restore_state = "normal"
        self.manual_pause_after_id = None
        self.remote_sync_loop_after_id = None
        self.remote_sync_debounce_after_id = None
        self.remote_sync_poll_after_id = None
        self.remote_sync_inflight = False
        self.remote_sync_requested = False
        self.remote_sync_results: queue.SimpleQueue[dict[str, object] | None] = queue.SimpleQueue()
        self.manual_pause_seconds_left = 0
        self.manual_pause_state: dict | None = None
        self.session_pause_uses_remaining = 0

        self.reload_from_db()
        self.lang = self.settings.get("window_language", "ru")
        self.apply_saved_geometry()

        self.build_ui()
        self.root.bind("<Configure>", self.on_root_configure, add="+")
        self.refresh_language()
        self.show_start_screen()
        self.start_lan_server_if_needed()
        self.start_remote_sync_loop()
        self.root.after(120, self.apply_responsive_layout)
        self.tick_loop()

    def tt(self, key: str) -> str:
        return t(self.lang, key)

    def ui_text(self, ru: str, pl: str, en: str) -> str:
        return {"ru": ru, "pl": pl, "en": en}.get(self.lang, en)

    def pause_upgrade_bounds(self, level: int | None = None) -> tuple[int, int]:
        level = max(0, min(4, safe_int(level if level is not None else self.settings.get("pause_upgrade_level"), 0)))
        bounds = [(2, 4), (3, 4), (4, 5), (5, 6), (5, 7)]
        return bounds[level]

    def pause_upgrade_cost(self, level: int | None = None) -> int | None:
        level = max(0, min(4, safe_int(level if level is not None else self.settings.get("pause_upgrade_level"), 0)))
        costs = [300, 450, 550, 700]
        return costs[level] if level < len(costs) else None

    def pause_duration_bounds(self) -> tuple[int, int]:
        return self.pause_upgrade_bounds()

    def manual_pause_minutes(self) -> int:
        pause_min, pause_max = self.pause_duration_bounds()
        current = safe_int(self.settings.get("manual_pause_minutes"), pause_min)
        return min(pause_max, max(pause_min, current))

    def manual_pause_uses_limit(self) -> int:
        return min(2, max(1, safe_int(self.settings.get("manual_pause_uses"), 1)))

    def extra_pause_tokens(self) -> int:
        return max(0, safe_int(self.settings.get("shop_extra_pause_tokens"), 0))

    def remaining_pause_uses(self) -> int:
        if not self.current_topic:
            return 0
        return max(0, self.session_pause_uses_remaining) + self.extra_pause_tokens()

    def pause_button_text(self) -> str:
        remaining = self.remaining_pause_uses()
        if self.manual_pause_state:
            return self.ui_text("Пауза...", "Pauza...", "Pause...")
        if self.current_topic:
            return self.ui_text(
                f"Пауза ({remaining})",
                f"Pauza ({remaining})",
                f"Pause ({remaining})",
            )
        return self.ui_text("Пауза", "Pauza", "Pause")

    def menu_button_text(self) -> str:
        return self.ui_text("Главное меню", "Menu glowne", "Main menu")

    def waiting_note_text(self) -> str:
        return self.ui_text(
            "Можно открыть магазин или настройки.",
            "Mozna otworzyc sklep albo ustawienia.",
            "You can open the shop or settings.",
        )

    def pause_overlay_title(self) -> str:
        return self.ui_text("Пауза", "Pauza", "Pause")

    def pause_overlay_body(self) -> str:
        minutes = self.manual_pause_minutes()
        return self.ui_text(
            f"Сейчас пауза для ученика. После неё программа продолжит с того же места. Текущая длительность: {minutes} мин.",
            f"To jest pauza ucznia. Po niej program wroci do tego samego miejsca. Aktualna dlugosc: {minutes} min.",
            f"This is a student pause. After it ends, the program will continue from the same place. Current length: {minutes} min.",
        )

    def resume_now_text(self) -> str:
        return self.ui_text("Продолжить сейчас", "Wroc teraz", "Resume now")

    def lesson_action_text(self) -> str:
        return {
            "ru": "Начать задания",
            "pl": "Zacznij zadania",
            "en": "Start tasks",
        }.get(self.lang, "Start tasks")

    def lesson_ready_text(self) -> str:
        return {
            "ru": "Тему можно спокойно прочитать или сразу перейти к заданиям.",
            "pl": "Możesz spokojnie przeczytać temat albo od razu przejść do zadań.",
            "en": "You can read the lesson or jump straight to the tasks.",
        }.get(self.lang, "You can read the lesson or jump straight to the tasks.")

    def lesson_done_text(self) -> str:
        return {
            "ru": "Тема просмотрена. Можно переходить к заданиям.",
            "pl": "Temat został przeczytany. Można przejść do zadań.",
            "en": "Lesson reviewed. You can continue to the tasks.",
        }.get(self.lang, "Lesson reviewed. You can continue to the tasks.")

    def lesson_step_text(self, index: int, total: int) -> str:
        label = {
            "ru": "Урок",
            "pl": "Lekcja",
            "en": "Lesson",
        }.get(self.lang, "Lesson")
        return f"{label} {index} / {total}"

    def choice_options_for_task(self, task: dict) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()
        for value in list(task.get("options") or []) + list(task.get("accepted_answers") or []):
            text = str(value or "").strip()
            normalized = normalize_input(text)
            if not text or not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(text)
        return ordered

    def modules_heading_text(self) -> str:
        return {
            "ru": "Выберите модуль",
            "pl": "Wybierz moduł",
            "en": "Choose a module",
        }.get(self.lang, "Choose a module")

    def modules_subtitle_text(self) -> str:
        return {
            "ru": "Подключённые учебные модули",
            "pl": "Podłączone moduły nauki",
            "en": "Available learning modules",
        }.get(self.lang, "Available learning modules")

    def levels_heading_text(self) -> str:
        return {
            "ru": "Выберите уровень",
            "pl": "Wybierz poziom",
            "en": "Choose a level",
        }.get(self.lang, "Choose a level")

    def reload_from_db(self) -> None:
        self.settings = self.db.get_settings()
        self.stats = self.db.get_stats()
        self.tasks = self.db.all_tasks()
        self.supports = self.db.get_supports()
        if self.current_topic:
            refreshed = self.db.get_topic(self.current_topic["id"])
            self.current_topic = refreshed if refreshed else None

    def sync_modules_from_disk(self, *, refresh_start_screen: bool = True) -> list[dict]:
        had_topic = self.current_topic is not None
        modules = self.db.sync_modules_from_disk()
        self.reload_from_db()
        if self.current_topic is None and (refresh_start_screen or had_topic):
            self.show_start_screen()
        return modules

    def start_lan_server_if_needed(self) -> None:
        if not self.settings.get("lan_admin_enabled", True):
            self.lan_url = ""
            return
        try:
            if self.lan_server:
                self.lan_server.stop()
            self.lan_server = LanAdminServer(self)
            self.lan_url = self.lan_server.start()
        except Exception:
            self.lan_server = None
            self.lan_url = ""

    def format_seconds_compact(self, total_seconds: int | None) -> str:
        seconds = max(0, safe_int(total_seconds, 0))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def runtime_state_snapshot(self) -> dict[str, str]:
        if self.manual_pause_state:
            state = "manual_pause"
            state_label = self.ui_text("Пауза ученика", "Pauza ucznia", "Student pause")
        elif self.current_task:
            state = "task"
            state_label = self.ui_text("Активное задание", "Aktywne zadanie", "Active task")
        elif self.lesson_blocks:
            state = "lesson"
            state_label = self.ui_text("Учебный блок", "Blok nauki", "Lesson block")
        elif self.current_topic:
            state = "waiting"
            state_label = self.ui_text("Ожидание следующей паузы", "Oczekiwanie na kolejna pauze", "Waiting for the next break")
        else:
            state = "menu"
            state_label = self.ui_text("Главное меню", "Menu glowne", "Main menu")

        lesson_title = ""
        if self.lesson_blocks and 0 <= self.lesson_index < len(self.lesson_blocks):
            lesson_title = localized_value(self.lesson_blocks[self.lesson_index], "title", self.lang)

        task_title = localized_value(self.current_task or {}, "title", self.lang) if self.current_task else ""
        topic_title = localized_value(self.current_topic or {}, "title", self.lang) if self.current_topic else ""
        module_title = localized_value(self.current_module or {}, "title", self.lang) if self.current_module else ""

        return {
            "state": state,
            "state_label": state_label,
            "current_module": module_title,
            "current_topic": topic_title,
            "current_lesson": lesson_title,
            "current_task": task_title,
            "remaining_break": self.format_seconds_compact(self.remaining_break_seconds()) if self.current_topic else "",
            "manual_pause": self.format_seconds_compact(self.manual_pause_seconds_left) if self.manual_pause_state else self.ui_text("Не активна", "Nieaktywna", "Inactive"),
            "break_lock": self.ui_text("Включён", "Wlaczona", "Enabled") if self.break_lock_active else self.ui_text("Выключен", "Wylaczona", "Disabled"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def build_remote_sync_payload(self) -> dict[str, object]:
        return {
            "dashboard": self.db.get_dashboard_snapshot(),
            "runtime": self.runtime_state_snapshot(),
        }

    def start_remote_sync_loop(self) -> None:
        self.queue_remote_sync(1500)
        self.schedule_remote_sync_result_poll()
        self.schedule_remote_sync_loop()

    def schedule_remote_sync_loop(self) -> None:
        if self.remote_sync_loop_after_id:
            self.root.after_cancel(self.remote_sync_loop_after_id)
        self.remote_sync_loop_after_id = self.root.after(30000, self._remote_sync_loop_tick)

    def schedule_remote_sync_result_poll(self) -> None:
        if self.remote_sync_poll_after_id:
            self.root.after_cancel(self.remote_sync_poll_after_id)
        self.remote_sync_poll_after_id = self.root.after(800, self.poll_remote_sync_results)

    def _remote_sync_loop_tick(self) -> None:
        self.remote_sync_loop_after_id = None
        self.queue_remote_sync(0)
        self.schedule_remote_sync_loop()

    def poll_remote_sync_results(self) -> None:
        self.remote_sync_poll_after_id = None
        while True:
            try:
                result = self.remote_sync_results.get_nowait()
            except queue.Empty:
                break
            self.finish_remote_sync(result)
        self.schedule_remote_sync_result_poll()

    def queue_remote_sync(self, delay_ms: int = 1200) -> None:
        base_url = str(self.settings.get("server_base_url") or "").strip()
        if not base_url:
            return
        if self.remote_sync_debounce_after_id:
            self.root.after_cancel(self.remote_sync_debounce_after_id)
        self.remote_sync_debounce_after_id = self.root.after(delay_ms, self.perform_remote_sync)

    def perform_remote_sync(self) -> None:
        self.remote_sync_debounce_after_id = None
        base_url = str(self.settings.get("server_base_url") or "").strip()
        parent_hash = self.db.get_parent_password_hash()
        program_id = str(self.settings.get("program_id") or "").strip()
        if not base_url or not parent_hash or not program_id:
            return
        if self.remote_sync_inflight:
            self.remote_sync_requested = True
            return
        self.remote_sync_inflight = True
        self.remote_sync_requested = False
        payload = self.build_remote_sync_payload()
        worker = threading.Thread(
            target=self._remote_sync_worker,
            args=(base_url, program_id, parent_hash, payload),
            daemon=True,
        )
        worker.start()

    def _remote_sync_worker(
        self,
        base_url: str,
        program_id: str,
        parent_hash: str,
        payload: dict[str, object],
    ) -> None:
        result = push_remote_snapshot(
            base_url=base_url,
            program_id=program_id,
            parent_password_hash=parent_hash,
            payload=payload,
        )
        self.remote_sync_results.put(result)

    def finish_remote_sync(self, result: dict[str, object] | None = None) -> None:
        self.remote_sync_inflight = False
        ok = bool((result or {}).get("ok"))
        if self.remote_sync_requested:
            self.remote_sync_requested = False
            self.queue_remote_sync(400)
        elif not ok and self.settings.get("server_base_url"):
            self.queue_remote_sync(12000)

    def persist_stats(self) -> None:
        self.stats["last_activity"] = self.stats.get("last_activity") or ""
        self.db.save_stats(self.stats)
        self.queue_remote_sync()

    def cancel_lesson_timer(self) -> None:
        if self.lesson_after_id:
            self.root.after_cancel(self.lesson_after_id)
            self.lesson_after_id = None

    def cancel_memory_timer(self) -> None:
        if self.memory_after_id:
            self.root.after_cancel(self.memory_after_id)
            self.memory_after_id = None

    def cancel_break_timer(self) -> None:
        if self.break_after_id:
            self.root.after_cancel(self.break_after_id)
            self.break_after_id = None
        self.break_deadline_ts = None

    def remaining_break_seconds(self) -> int:
        if self.break_deadline_ts is None:
            return 0
        return max(0, int(round(self.break_deadline_ts - time.monotonic())))

    def cancel_manual_pause_timer(self) -> None:
        if self.manual_pause_after_id:
            self.root.after_cancel(self.manual_pause_after_id)
            self.manual_pause_after_id = None

    def update_pause_button(self) -> None:
        if not hasattr(self, "pause_btn"):
            return
        active = bool(self.current_topic) and self.manual_pause_state is None
        remaining = self.remaining_pause_uses()
        state = "normal" if active and remaining > 0 else "disabled"
        if self.manual_pause_state:
            state = "disabled"
        self.pause_btn.configure(
            text=self.pause_button_text(),
            state=state,
            bg=ACCENT if state == "normal" else CARD_2,
            fg="#111" if state == "normal" else MUTED,
        )
        menu_state = "normal" if self.current_topic or self.manual_pause_state else "disabled"
        self.menu_btn.configure(
            text=self.menu_button_text(),
            state=menu_state,
            bg=CARD if menu_state == "normal" else CARD_2,
            fg=TEXT if menu_state == "normal" else MUTED,
        )

    def hide_overlay(self) -> None:
        self.start_overlay.place_forget()

    def spend_coins(self, cost: int) -> bool:
        if int(self.stats.get("coins", 0) or 0) < cost:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text(
                    "Недостаточно монет для этой покупки.",
                    "Za malo monet na ten zakup.",
                    "Not enough coins for this purchase.",
                ),
                parent=self.root,
            )
            return False
        self.stats["coins"] = max(0, int(self.stats.get("coins", 0) or 0) - cost)
        self.persist_stats()
        self.update_coins()
        return True

    def reset_session_pause_uses(self) -> None:
        self.session_pause_uses_remaining = self.manual_pause_uses_limit()
        self.update_pause_button()

    def consume_pause_use(self) -> None:
        if self.session_pause_uses_remaining > 0:
            self.session_pause_uses_remaining -= 1
        elif self.extra_pause_tokens() > 0:
            self.settings = self.db.update_settings(
                {"shop_extra_pause_tokens": max(0, self.extra_pause_tokens() - 1)}
            )
            self.reload_from_db()
        self.update_pause_button()

    def viewport_width(self) -> int:
        self.root.update_idletasks()
        return max(self.root.winfo_width(), 960)

    def adaptive_columns(self, *, max_columns: int = 3, minimum_card_width: int = 320) -> int:
        width = self.viewport_width()
        columns = max(1, min(max_columns, width // minimum_card_width))
        if max_columns == 3 and columns == 1 and width >= 920:
            return 2
        return columns

    def apply_saved_geometry(self) -> None:
        geometry = str(self.settings.get("window_geometry") or "").strip()
        match = re.match(r"^(\d+x\d+)", geometry)
        if not match:
            return
        try:
            self.root.geometry(match.group(1))
        except Exception:
            return

    def lock_screen_geometry(self) -> str:
        return f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"

    def should_enforce_window_lock(self) -> bool:
        return bool(self.break_lock_active and not self.password_dialog_open and not self.window_lock_suspended)

    def suspend_window_lock(self, suspended: bool) -> None:
        self.window_lock_suspended = suspended
        self.apply_window_lock_state(force=True)

    def apply_window_lock_state(self, *, force: bool = False) -> None:
        locked = self.should_enforce_window_lock()
        if locked == self.window_lock_applied and not force:
            return
        if locked:
            if not self.window_restore_geometry:
                try:
                    self.window_restore_state = str(self.root.state())
                except Exception:
                    self.window_restore_state = "normal"
                try:
                    self.window_restore_geometry = self.root.geometry()
                except Exception:
                    self.window_restore_geometry = "1320x840"
            self.window_lock_applied = True
            try:
                self.root.resizable(False, False)
            except Exception:
                pass
            try:
                self.root.overrideredirect(True)
            except Exception:
                pass
            self.enforce_window_lock()
            return

        was_locked = self.window_lock_applied
        self.window_lock_applied = False
        try:
            self.root.overrideredirect(False)
        except Exception:
            pass
        try:
            self.root.resizable(True, True)
        except Exception:
            pass
        try:
            self.root.attributes("-topmost", False)
        except Exception:
            pass
        if was_locked:
            try:
                if self.window_restore_state == "zoomed":
                    self.root.state("zoomed")
                elif self.window_restore_geometry:
                    self.root.geometry(self.window_restore_geometry)
            except Exception:
                pass
        self.window_restore_geometry = ""
        self.window_restore_state = "normal"

    def enforce_window_lock(self) -> None:
        if not self.should_enforce_window_lock():
            self.apply_window_lock_state(force=True)
            return
        if not self.window_lock_applied:
            self.apply_window_lock_state(force=True)
            if not self.should_enforce_window_lock():
                return
        try:
            if self.root.state() == "iconic":
                self.root.deiconify()
        except Exception:
            try:
                self.root.deiconify()
            except Exception:
                pass
        try:
            self.root.attributes("-topmost", True)
        except Exception:
            pass
        try:
            self.root.geometry(self.lock_screen_geometry())
        except Exception:
            pass
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass

    def on_root_configure(self, event=None) -> None:
        if event is not None and event.widget is not self.root:
            return
        if self.layout_after_id:
            self.root.after_cancel(self.layout_after_id)
        self.layout_after_id = self.root.after(120, self.apply_responsive_layout)
        if self.should_enforce_window_lock():
            self.root.after(40, self.enforce_window_lock)
        if self.geometry_after_id:
            self.root.after_cancel(self.geometry_after_id)
        self.geometry_after_id = self.root.after(500, self.remember_window_geometry)

    def on_root_unmap(self, event=None) -> None:
        if event is not None and event.widget is not self.root:
            return
        if self.should_enforce_window_lock():
            self.root.after(40, self.enforce_window_lock)

    def on_root_focus_out(self, event=None) -> None:
        if self.should_enforce_window_lock():
            self.root.after(120, self.enforce_window_lock)

    def remember_window_geometry(self) -> None:
        self.geometry_after_id = None
        if self.window_lock_applied:
            return
        try:
            if self.root.state() != "normal":
                return
        except Exception:
            pass
        geometry = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
        if geometry != str(self.settings.get("window_geometry") or ""):
            self.db.update_settings({"window_geometry": geometry})
            self.settings["window_geometry"] = geometry

    def apply_responsive_layout(self) -> None:
        self.layout_after_id = None
        width = self.viewport_width()
        compact = width < 1280
        stacked_prompts = width < 1180
        self.main_card.pack_configure(padx=18 if compact else 36, pady=14 if compact else 24)
        self.card_top.pack_configure(padx=16 if compact else 24, pady=(16 if compact else 20, 8))
        self.body_wrap.pack_configure(padx=14 if compact else 22, pady=(0, 12 if compact else 18))
        self.title_label.config(font=("Segoe UI", 22 if compact else 28, "bold"))
        self.step_label.config(font=("Segoe UI", 11 if compact else 13, "bold"))
        prompt_font_size = 14 if width < 1080 else 16 if width < 1320 else 18
        self.ru_prompt.config(font=("Segoe UI", prompt_font_size))
        self.pl_prompt.config(font=("Segoe UI", prompt_font_size))

        prompt_wrap = max(260, width - 250) if stacked_prompts else max(260, (width - 420) // 2)
        self.ru_prompt.config(wraplength=prompt_wrap)
        self.pl_prompt.config(wraplength=prompt_wrap)
        self.input_hint_label.config(wraplength=max(320, width - 260))

        self.ru_box.pack_forget()
        self.pl_box.pack_forget()
        if stacked_prompts:
            self.ru_box.pack(fill="x", padx=0, pady=(0, 10))
            self.pl_box.pack(fill="x", padx=0)
        else:
            self.ru_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
            self.pl_box.pack(side="left", fill="both", expand=True, padx=(8, 0))

        side_width = 170 if width < 1240 else 230
        for frame in (self.side_left, self.side_right):
            if frame.winfo_children():
                frame.config(width=side_width)

        if self.start_overlay.winfo_ismapped():
            if self.overlay_kind == "start":
                self.render_start_screen()
            elif self.overlay_kind == "manual_pause":
                self.show_manual_pause_screen()
            elif self.overlay_kind == "module_levels" and self.overlay_payload:
                self.render_level_picker(self.overlay_payload["module"], self.overlay_payload["levels"])
            elif self.overlay_kind == "topic_picker" and self.overlay_payload:
                self.render_topic_picker(self.overlay_payload["topics"], title=self.overlay_payload["title"])

    def build_ui(self) -> None:
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.header = tk.Frame(self.container, bg=PANEL, height=68)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.mode_badge = tk.Label(self.header, text="—", fg=TEXT, bg=CARD, padx=16, pady=8, font=("Segoe UI", 12, "bold"))
        self.mode_badge.pack(side="left", padx=18, pady=10)
        self.mode_badge.configure(text="-")

        self.shop_btn = tk.Button(self.header, command=self.open_shop, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.shop_btn.pack(side="left", padx=(0, 8), pady=10)

        self.parent_btn = tk.Button(self.header, command=self.ask_parent_panel, bg=ACCENT_2, fg="white", relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.parent_btn.pack(side="left", padx=(0, 8), pady=10)

        self.pause_btn = tk.Button(self.header, command=self.begin_manual_pause, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.pause_btn.pack(side="left", padx=(0, 8), pady=10)

        self.menu_btn = tk.Button(self.header, command=self.ask_return_to_menu, bg=CARD, fg=TEXT, relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.menu_btn.pack(side="left", padx=(0, 8), pady=10)

        self.phone_btn = tk.Button(self.header, text="LAN", command=self.show_phone_info, bg=CARD, fg=TEXT, relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.phone_btn.pack(side="left", padx=(0, 8), pady=10)

        lang_box = tk.Frame(self.header, bg=PANEL)
        lang_box.pack(side="right", padx=16)
        self.lang_var = tk.StringVar(value=self.lang)
        self.lang_btn_text = tk.StringVar(value="")
        self.lang_menu_btn = tk.Menubutton(
            lang_box,
            textvariable=self.lang_btn_text,
            bg=CARD_2,
            fg=TEXT,
            activebackground=ACCENT_2,
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            direction="below",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.lang_menu = tk.Menu(
            self.lang_menu_btn,
            tearoff=0,
            bg=CENTER,
            fg=TEXT,
            activebackground=ACCENT_2,
            activeforeground="white",
            relief="flat",
        )
        for code, label in (("ru", "Русский"), ("pl", "Polski"), ("en", "English")):
            self.lang_menu.add_command(label=label, command=lambda current=code: self.change_language(current))
        self.lang_menu_btn.configure(menu=self.lang_menu)
        self.lang_menu_btn.pack(side="right", pady=10)

        self.coins_badge = tk.Label(self.header, text="0", fg=TEXT, bg=CARD, padx=16, pady=8, font=("Segoe UI", 12, "bold"))
        self.coins_badge.pack(side="right", padx=(0, 8), pady=10)

        self.main_card = tk.Frame(self.container, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        self.main_card.pack(fill="both", expand=True, padx=36, pady=24)

        self.card_top = tk.Frame(self.main_card, bg=CARD)
        self.card_top.pack(fill="x", padx=24, pady=(20, 8))
        self.step_label = tk.Label(self.card_top, text="", fg=MUTED, bg=CARD, font=("Segoe UI", 13, "bold"))
        self.step_label.pack(side="right")

        self.title_label = tk.Label(self.main_card, text="", fg=TEXT, bg=CARD, font=("Segoe UI", 28, "bold"))
        self.title_label.pack(pady=(6, 14))

        self.body_wrap = tk.Frame(self.main_card, bg=CARD)
        self.body_wrap.pack(fill="both", expand=True, padx=22, pady=(0, 18))

        self.side_left = tk.Frame(self.body_wrap, bg=CARD_2, width=0)
        self.side_left.pack(side="left", fill="y", padx=(0, 10))
        self.side_left.pack_propagate(False)

        self.center_panel = tk.Frame(self.body_wrap, bg=CENTER, highlightbackground=BORDER, highlightthickness=1)
        self.center_panel.pack(side="left", fill="both", expand=True)

        self.side_right = tk.Frame(self.body_wrap, bg=CARD_2, width=0)
        self.side_right.pack(side="left", fill="y", padx=(10, 0))
        self.side_right.pack_propagate(False)

        self.prompt_row = tk.Frame(self.center_panel, bg=CENTER)
        self.prompt_row.pack(fill="x", padx=18, pady=(18, 8))

        self.ru_box = tk.Frame(self.prompt_row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        self.ru_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.pl_box = tk.Frame(self.prompt_row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        self.pl_box.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.ru_box_title = tk.Label(self.ru_box, text="Русский", fg=TEXT, bg=CARD_2, font=("Segoe UI", 15, "bold"))
        self.ru_box_title.pack(anchor="w", padx=18, pady=(18, 8))
        self.ru_prompt = tk.Label(self.ru_box, text="", fg=TEXT, bg=CARD_2, justify="left", wraplength=360, font=("Segoe UI", 18))
        self.ru_prompt.pack(anchor="w", padx=18, pady=(0, 18))

        self.pl_box_title = tk.Label(self.pl_box, text="Polski", fg=TEXT, bg=CARD_2, font=("Segoe UI", 15, "bold"))
        self.pl_box_title.pack(anchor="w", padx=18, pady=(18, 8))
        self.pl_prompt = tk.Label(self.pl_box, text="", fg=TEXT, bg=CARD_2, justify="left", wraplength=360, font=("Segoe UI", 18))
        self.pl_prompt.pack(anchor="w", padx=18, pady=(0, 18))

        self.answer_area = tk.Frame(self.center_panel, bg=CENTER)
        self.answer_area.pack(fill="x", padx=24, pady=(14, 14))

        self.answer_entry = tk.Entry(self.answer_area, font=("Segoe UI", 22), width=18, justify="center")
        self.check_btn = tk.Button(self.answer_area, command=self.check_answer, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.next_btn = tk.Button(self.answer_area, command=self.mark_reading_done, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.memory_btn = tk.Button(self.answer_area, command=self.finish_memory_task, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.lesson_btn = tk.Button(self.answer_area, command=self.advance_from_lesson, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.input_hint_label = tk.Label(
            self.center_panel,
            text="",
            fg=MUTED,
            bg=CENTER,
            font=("Segoe UI", 11),
            wraplength=760,
            justify="center",
        )
        self.input_hint_label.pack(pady=(0, 8))

        self.lesson_timer_label = tk.Label(self.center_panel, text="", fg=ACCENT, bg=CENTER, font=("Segoe UI", 18, "bold"))
        self.lesson_timer_label.pack(pady=(0, 4))
        self.memory_timer_label = tk.Label(self.center_panel, text="", fg=ACCENT, bg=CENTER, font=("Segoe UI", 18, "bold"))
        self.memory_timer_label.pack(pady=(0, 4))
        self.feedback = tk.Label(self.center_panel, text="", fg=MUTED, bg=CENTER, font=("Segoe UI", 14, "bold"))
        self.feedback.pack(pady=(0, 16))

        self.start_overlay = tk.Frame(self.center_panel, bg=CENTER)
        self.start_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.update_coins()

    def refresh_language(self) -> None:
        self.reload_from_db()
        self.lang = self.settings.get("window_language", self.lang)
        self.root.title(f"{APP_TITLE} v23")
        self.lang_var.set(self.lang)
        self.lang_btn_text.set(
            {
                "ru": "Русский ▾",
                "pl": "Polski ▾",
                "en": "English ▾",
            }.get(self.lang, "English ▾")
        )
        self.lang_btn_text.set(
            {
                "ru": "RU / Русский",
                "pl": "PL / Polski",
                "en": "EN / English",
            }.get(self.lang, "EN / English")
        )
        self.shop_btn.config(text=self.tt("shop"))
        self.parent_btn.config(text=self.tt("settings"))
        self.phone_btn.config(text="LAN")
        self.check_btn.config(text=self.tt("check"))
        self.next_btn.config(text=self.tt("next"))
        self.memory_btn.config(text=self.tt("remembered"))
        self.lesson_btn.config(text=self.lesson_action_text())
        self.update_pause_button()
        self.update_coins()
        if self.current_task:
            self.show_task(self.current_task)
        elif self.current_topic and self.lesson_blocks:
            self.show_lesson_block(self.lesson_index)
        elif self.current_topic:
            self.show_waiting_state()
        else:
            self.show_start_screen()

    def change_language(self, value: str) -> None:
        self.db.update_settings({"window_language": value})
        self.reload_from_db()
        self.lang = value
        self.refresh_language()

    def clear_overlay(self) -> None:
        for widget in self.start_overlay.winfo_children():
            widget.destroy()
        self.start_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_manual_pause_screen(self) -> None:
        self.overlay_kind = "manual_pause"
        self.overlay_payload = None
        self.clear_overlay()
        self.hide_side_panels()
        self.title_label.config(text=self.pause_overlay_title())
        self.step_label.config(text=self.ui_text("Временная пауза", "Tymczasowa pauza", "Temporary pause"))
        self.ru_prompt.config(text=self.pause_overlay_body())
        self.pl_prompt.config(text=self.pause_overlay_body())
        for widget in self.answer_area.winfo_children():
            widget.pack_forget()
        self.input_hint_label.config(text="")
        self.lesson_timer_label.config(text="")
        self.memory_timer_label.config(text="")
        self.feedback.config(
            text=self.ui_text(
                "После окончания паузы программа вернётся к тому же месту.",
                "Po pauzie program wroci do tego samego miejsca.",
                "After the pause, the app will return to the same place.",
            ),
            fg=MUTED,
        )
        self.manual_pause_timer_var = tk.StringVar(value="")
        card = tk.Frame(self.start_overlay, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.place(relx=0.5, rely=0.52, anchor="center", relwidth=0.54, relheight=0.42)
        tk.Label(
            card,
            text=self.pause_overlay_title(),
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 26, "bold"),
        ).pack(pady=(26, 10))
        tk.Label(
            card,
            text=self.pause_overlay_body(),
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 12),
            wraplength=540,
            justify="center",
        ).pack(padx=20, pady=(0, 18))
        tk.Label(
            card,
            textvariable=self.manual_pause_timer_var,
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI", 30, "bold"),
        ).pack(pady=(0, 18))
        tk.Button(
            card,
            text=self.resume_now_text(),
            command=self.resume_from_manual_pause,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            padx=18,
            pady=10,
        ).pack(pady=(0, 22))

    def tick_manual_pause_timer(self) -> None:
        minutes, seconds = divmod(self.manual_pause_seconds_left, 60)
        if hasattr(self, "manual_pause_timer_var"):
            self.manual_pause_timer_var.set(f"{minutes:02d}:{seconds:02d}")
        if self.manual_pause_seconds_left <= 0:
            self.manual_pause_after_id = None
            self.resume_from_manual_pause()
            return
        self.manual_pause_seconds_left -= 1
        self.manual_pause_after_id = self.root.after(1000, self.tick_manual_pause_timer)

    def begin_manual_pause(self) -> None:
        if not self.current_topic or self.manual_pause_state is not None:
            return
        if self.remaining_pause_uses() <= 0:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text(
                    "Паузы закончились. Можно купить дополнительную паузу в магазине.",
                    "Pauzy sie skonczyly. Dodatkowa pauze mozna kupic w sklepie.",
                    "No pauses left. You can buy an extra pause in the shop.",
                ),
                parent=self.root,
            )
            return
        paused_state: dict[str, object]
        if self.current_task:
            paused_state = {
                "kind": "task",
                "task": dict(self.current_task),
                "current_break_tasks": [dict(item) for item in self.current_break_tasks],
                "current_index": self.current_index,
                "memory_seconds_left": self.memory_seconds_left,
            }
        elif self.lesson_blocks:
            paused_state = {
                "kind": "lesson",
                "lesson_blocks": [dict(item) for item in self.lesson_blocks],
                "lesson_index": self.lesson_index,
                "lesson_seconds_left": self.lesson_seconds_left,
                "current_break_tasks": [dict(item) for item in self.current_break_tasks],
                "current_index": self.current_index,
            }
        else:
            paused_state = {
                "kind": "waiting",
                "remaining_break_seconds": max(
                    1,
                    self.remaining_break_seconds() or safe_int(self.settings.get("break_seconds"), 300),
                ),
            }
        self.consume_pause_use()
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.cancel_break_timer()
        self.current_task = None
        self.lesson_blocks = []
        self.manual_pause_state = paused_state
        self.manual_pause_seconds_left = self.manual_pause_minutes() * 60
        self.set_break_lock(False)
        self.show_manual_pause_screen()
        self.tick_manual_pause_timer()
        self.update_pause_button()
        self.queue_remote_sync(200)

    def resume_from_manual_pause(self) -> None:
        state = dict(self.manual_pause_state or {})
        self.cancel_manual_pause_timer()
        self.manual_pause_state = None
        self.manual_pause_seconds_left = 0
        self.hide_overlay()
        kind = str(state.get("kind") or "waiting")
        if kind == "lesson":
            self.current_break_tasks = [dict(item) for item in (state.get("current_break_tasks") or [])]
            self.current_index = safe_int(state.get("current_index"), 0)
            self.lesson_blocks = [dict(item) for item in (state.get("lesson_blocks") or [])]
            self.lesson_index = min(
                max(0, safe_int(state.get("lesson_index"), 0)),
                max(0, len(self.lesson_blocks) - 1),
            )
            if self.lesson_blocks:
                self.show_lesson_block(self.lesson_index)
                self.cancel_lesson_timer()
                self.lesson_seconds_left = max(0, safe_int(state.get("lesson_seconds_left"), self.lesson_seconds_left))
                self.tick_lesson_timer()
            else:
                self.show_waiting_state()
                self.schedule_next_break()
        elif kind == "task":
            self.lesson_blocks = []
            self.current_break_tasks = [dict(item) for item in (state.get("current_break_tasks") or [])]
            self.current_index = safe_int(state.get("current_index"), 0)
            task = state.get("task")
            if isinstance(task, dict):
                self.show_task(task)
                if str(task.get("type") or "") == "memory":
                    self.cancel_memory_timer()
                    self.memory_seconds_left = max(0, safe_int(state.get("memory_seconds_left"), self.memory_seconds_left))
                    self.tick_memory_timer()
            else:
                self.show_waiting_state()
                self.schedule_next_break()
        else:
            self.show_waiting_state()
            self.schedule_next_break(
                delay_seconds=max(
                    1,
                    safe_int(state.get("remaining_break_seconds"), safe_int(self.settings.get("break_seconds"), 300)),
                )
            )
        self.update_pause_button()
        self.queue_remote_sync(200)

    def show_start_screen(self) -> None:
        self.cancel_break_timer()
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.cancel_manual_pause_timer()
        self.manual_pause_state = None
        self.manual_pause_seconds_left = 0
        self.set_break_lock(False)
        self.current_module = None
        self.current_topic = None
        self.current_break_tasks = []
        self.current_task = None
        self.lesson_blocks = []
        self.session_pause_uses_remaining = self.manual_pause_uses_limit()
        self.title_label.config(text=self.modules_heading_text())
        self.step_label.config(text="")
        self.overlay_kind = "start"
        self.overlay_payload = None
        self.update_pause_button()
        self.render_start_screen()
        self.queue_remote_sync(200)

    def render_start_screen(self) -> None:
        self.clear_overlay()
        width = self.viewport_width()
        modules = self.db.list_modules()
        column_count = self.adaptive_columns(max_columns=3, minimum_card_width=420)
        wrap = 220 if column_count == 3 else 280
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.94, relheight=0.88)
        tk.Label(card, text=self.modules_subtitle_text(), fg=TEXT, bg=CARD, font=("Segoe UI", 24 if width < 1180 else 28, "bold")).pack(pady=(24, 16))
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="both", expand=True, padx=20, pady=(8, 20))
        item_count = max(1, len(modules))
        row_count = (item_count + column_count - 1) // column_count
        for column in range(column_count):
            row.grid_columnconfigure(column, weight=1, uniform="start_modes", minsize=220)
        for row_index in range(row_count):
            row.grid_rowconfigure(row_index, weight=1, minsize=210)

        def mode_card(parent, title, desc, cmd, index):
            frame = tk.Frame(parent, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
            frame.grid(row=index // column_count, column=index % column_count, padx=12, pady=12, sticky="nsew")
            inner = tk.Frame(frame, bg=CARD_2)
            inner.pack(fill="both", expand=True, padx=16, pady=18)
            tk.Label(
                inner,
                text=title,
                fg=TEXT,
                bg=CARD_2,
                font=("Segoe UI", 16 if column_count == 3 else 18, "bold"),
                wraplength=wrap,
                justify="center",
            ).pack(pady=(4, 10))
            tk.Label(
                inner,
                text=desc,
                fg=MUTED,
                bg=CARD_2,
                justify="center",
                font=("Segoe UI", 12),
                wraplength=wrap,
            ).pack(fill="x")
            tk.Frame(inner, bg=CARD_2).pack(fill="both", expand=True, pady=(8, 0))
            tk.Button(
                inner,
                text=self.tt("select"),
                command=cmd,
                bg=ACCENT,
                fg="#111",
                relief="flat",
                font=("Segoe UI", 12, "bold"),
                padx=18,
                pady=8,
            ).pack(pady=(12, 0))

        if not modules:
            tk.Label(
                row,
                text={
                    "ru": "В папке modules пока не найдено ни одного учебного модуля.",
                    "pl": "W folderze modules nie znaleziono jeszcze żadnego modułu nauki.",
                    "en": "No learning modules were found in the modules folder yet.",
                }.get(self.lang, "No learning modules were found in the modules folder yet."),
                fg=MUTED,
                bg=CARD,
                font=("Segoe UI", 12),
                wraplength=520,
                justify="center",
            ).pack(expand=True)
            return

        for index, module in enumerate(modules):
            mode_card(
                row,
                localized_value(module, "title", self.lang),
                localized_value(module, "description", self.lang),
                lambda current=module: self.open_module(current),
                index,
            )

    def open_module(self, module: dict) -> None:
        self.current_module = module
        levels = self.db.list_levels(sphere_id=module["id"])
        if levels:
            self.overlay_kind = "module_levels"
            self.overlay_payload = {"module": module, "levels": levels}
            self.render_level_picker(module, levels)
            return
        topics = self.db.list_topics(sphere_id=module["id"])
        self.show_topic_picker(topics, title=localized_value(module, "title", self.lang))

    def render_level_picker(self, module: dict, levels: list[dict]) -> None:
        self.clear_overlay()
        width = self.viewport_width()
        compact = width < 1120
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.84 if compact else 0.74, relheight=0.78 if compact else 0.68)
        tk.Label(card, text=self.levels_heading_text(), fg=TEXT, bg=CARD, font=("Segoe UI", 22 if compact else 24, "bold")).pack(pady=(24, 8))
        tk.Label(card, text=localized_value(module, "title", self.lang), fg=MUTED, bg=CARD, font=("Segoe UI", 12)).pack(pady=(0, 12))
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="both", expand=True, padx=18, pady=(6, 6))
        current_code = str(self.level_var.get()) if hasattr(self, "level_var") else str(levels[0]["code"])
        self.level_var = tk.StringVar(value=current_code)
        column_count = 2 if compact else min(4, max(1, len(levels)))
        for column in range(column_count):
            row.grid_columnconfigure(column, weight=1, uniform="levels")
        for index, level in enumerate(levels):
            box = tk.Frame(row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1, width=140, height=84 if compact else 92)
            box.grid(row=index // column_count, column=index % column_count, padx=10, pady=10, sticky="nsew")
            box.pack_propagate(False)
            label = localized_value(level, "title", self.lang)
            tk.Radiobutton(
                box,
                text=label,
                variable=self.level_var,
                value=str(level["code"]),
                bg=CARD_2,
                fg=TEXT,
                selectcolor=CARD,
                activebackground=CARD_2,
                activeforeground=TEXT,
                font=("Segoe UI", 16, "bold"),
                indicatoron=0,
                wraplength=120,
                justify="center",
            ).pack(expand=True, fill="both", padx=10, pady=10)
        actions = tk.Frame(card, bg=CARD)
        actions.pack(fill="x", padx=18, pady=(4, 18))
        tk.Button(
            actions,
            text=self.tt("start"),
            command=lambda current_module=module, current_levels=levels: self.show_module_level_topics(current_module, current_levels),
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            padx=22,
            pady=10,
        ).pack()

    def show_module_level_topics(self, module: dict, levels: list[dict]) -> None:
        selected = next((level for level in levels if str(level["code"]) == self.level_var.get()), levels[0])
        topics = self.db.list_topics(sphere_id=module["id"], level_id=selected["id"])
        title = f"{localized_value(module, 'title', self.lang)} / {localized_value(selected, 'title', self.lang)}"
        self.show_topic_picker(topics, title=title)

    def show_topic_picker(self, topics: list[dict], *, title: str) -> None:
        self.overlay_kind = "topic_picker"
        self.overlay_payload = {"topics": topics, "title": title}
        self.render_topic_picker(topics, title=title)

    def render_topic_picker(self, topics: list[dict], *, title: str) -> None:
        self.clear_overlay()
        width = self.viewport_width()
        column_count = self.adaptive_columns(max_columns=3, minimum_card_width=380)
        card_wrap = 210 if column_count == 3 else 280 if column_count == 2 else 420
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9 if len(topics) > column_count else 0.82)
        tk.Label(card, text=title, fg=TEXT, bg=CARD, font=("Segoe UI", 22 if width < 1180 else 24, "bold")).pack(pady=(24, 16))
        grid = tk.Frame(card, bg=CARD)
        grid.pack(fill="both", expand=True, padx=20, pady=10)
        row_count = max(1, (len(topics) + column_count - 1) // column_count)
        for column in range(column_count):
            grid.grid_columnconfigure(column, weight=1, uniform="topics", minsize=220)
        for row in range(row_count):
            grid.grid_rowconfigure(row, weight=1, minsize=190 if column_count == 3 else 210)
        if not topics:
            tk.Label(
                grid,
                text={
                    "ru": "Для этого режима пока нет доступных тем.",
                    "pl": "Dla tego trybu nie ma jeszcze dostępnych tematów.",
                    "en": "No topics are available for this mode yet.",
                }.get(self.lang, "No topics are available for this mode yet."),
                fg=MUTED,
                bg=CARD,
                font=("Segoe UI", 12),
                wraplength=500,
                justify="center",
            ).pack(expand=True)
        for index, topic in enumerate(topics):
            frame = tk.Frame(grid, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
            frame.grid(row=index // column_count, column=index % column_count, padx=10, pady=10, sticky="nsew")
            inner = tk.Frame(frame, bg=CARD_2)
            inner.pack(fill="both", expand=True, padx=14, pady=16)
            title_text = localized_value(topic, "title", self.lang)
            description_text = localized_value(topic, "description", self.lang)
            tk.Label(inner, text=title_text, fg=TEXT, bg=CARD_2, font=("Segoe UI", 15, "bold"), wraplength=card_wrap, justify="center").pack(pady=(0, 8))
            tk.Label(inner, text=description_text, fg=MUTED, bg=CARD_2, font=("Segoe UI", 10), wraplength=card_wrap, justify="center").pack(fill="x")
            tk.Frame(inner, bg=CARD_2).pack(fill="both", expand=True, pady=(8, 0))
            tk.Button(inner, text=self.tt("select"), command=lambda current=topic: self.select_topic(current), bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(pady=(12, 0))
        tk.Button(card, text=self.tt("close"), command=self.show_start_screen, bg=CARD_2, fg=TEXT, relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(pady=(0, 22))

    def select_topic(self, topic: dict) -> None:
        if not self.db.tasks_for_topic(topic["id"]):
            messagebox.showinfo(
                APP_TITLE,
                {
                    "ru": "Для этой темы пока не найдено заданий.",
                    "pl": "Dla tego tematu nie znaleziono jeszcze zadań.",
                    "en": "No tasks are configured for this topic yet.",
                }.get(self.lang, "No tasks are configured for this topic yet."),
            )
            return
        self.current_topic = topic
        self.program_mode = topic["mode"]
        self.reset_session_pause_uses()
        badge = localized_value(topic, "title", self.lang)
        self.mode_badge.config(text=badge)
        self.stats["last_mode"] = f"{topic['mode']}:{topic['slug']}"
        self.overlay_kind = "hidden"
        self.overlay_payload = None
        self.hide_overlay()
        self.schedule_next_break()
        self.show_waiting_state()

    def build_break_tasks(self) -> None:
        if not self.current_topic:
            self.current_break_tasks = []
            return
        pool = self.db.tasks_for_topic(self.current_topic["id"])
        random.shuffle(pool)
        tasks_per_break = max(1, safe_int(self.settings.get("tasks_per_break"), 2))
        if len(pool) < tasks_per_break and pool:
            multiplier = tasks_per_break // len(pool) + 1
            pool = (pool * multiplier)[:tasks_per_break]
        self.current_break_tasks = pool[:tasks_per_break]
        self.current_index = 0

    def schedule_next_break(self, delay_seconds: int | None = None, *, consume_pending_bonus: bool = True) -> None:
        self.cancel_break_timer()
        self.build_break_tasks()
        base_delay = max(1, safe_int(delay_seconds, safe_int(self.settings.get("break_seconds"), 300)))
        pending_bonus = 0
        if consume_pending_bonus:
            pending_bonus = max(0, safe_int(self.settings.get("shop_pending_delay_bonus_seconds"), 0))
            if pending_bonus:
                self.settings = self.db.update_settings({"shop_pending_delay_bonus_seconds": 0})
                self.reload_from_db()
        total_delay = base_delay + pending_bonus
        self.break_deadline_ts = time.monotonic() + total_delay
        self.break_after_id = self.root.after(total_delay * 1000, self.start_next_break)

    def start_next_break(self) -> None:
        self.break_after_id = None
        self.break_deadline_ts = None
        if not self.current_topic or not self.current_break_tasks:
            self.show_waiting_state()
            return
        if self.settings.get("pause_minecraft_on_break", True):
            try_pause_minecraft_window()
        self.set_break_lock(True)
        self.lesson_blocks = self.db.lesson_blocks_for_topic(self.current_topic["id"])
        self.lesson_index = 0
        self.current_index = 0
        if self.lesson_blocks:
            self.show_lesson_block(0)
        else:
            self.show_task(self.current_break_tasks[0])

    def set_break_lock(self, active: bool) -> None:
        previous = self.break_lock_active
        self.break_lock_active = active
        expected_applied = self.should_enforce_window_lock()
        if previous != active or self.window_lock_applied != expected_applied:
            self.apply_window_lock_state(force=True)
        if active and self.should_enforce_window_lock():
            self.root.after(40, self.enforce_window_lock)

    def prompt_password_dialog(self, title: str, prompt: str) -> str | None:
        if self.password_dialog and self.password_dialog.winfo_exists():
            self.password_dialog.lift()
            self.password_dialog.focus_force()
            return None

        result: dict[str, str | None] = {"value": None}
        self.password_dialog_open = True
        self.apply_window_lock_state(force=True)
        dialog = tk.Toplevel(self.root)
        self.password_dialog = dialog
        dialog.title(title)
        dialog.configure(bg=CARD)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        try:
            dialog.attributes("-topmost", True)
        except Exception:
            pass
        try:
            dialog.lift(self.root)
        except Exception:
            pass

        card = tk.Frame(dialog, bg=CARD, padx=20, pady=18)
        card.pack(fill="both", expand=True)
        tk.Label(card, text=prompt, bg=CARD, fg=TEXT, font=("Segoe UI", 11), wraplength=320, justify="left").pack(anchor="w")
        entry = tk.Entry(card, show="*", bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 13), width=28)
        entry.pack(fill="x", pady=(12, 16))

        button_row = tk.Frame(card, bg=CARD)
        button_row.pack(fill="x")

        def close_with(value: str | None) -> None:
            result["value"] = value
            try:
                dialog.grab_release()
            except Exception:
                pass
            dialog.destroy()

        tk.Button(
            button_row,
            text=self.tt("close"),
            command=lambda: close_with(None),
            bg=CARD_2,
            fg=TEXT,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
        ).pack(side="right")
        tk.Button(
            button_row,
            text=self.tt("check"),
            command=lambda: close_with(entry.get().strip()),
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=8,
        ).pack(side="right", padx=(0, 8))

        dialog.protocol("WM_DELETE_WINDOW", lambda: close_with(None))
        dialog.bind("<Return>", lambda _event: close_with(entry.get().strip()))
        dialog.bind("<Escape>", lambda _event: close_with(None))

        dialog.update_idletasks()
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - dialog.winfo_reqwidth()) // 2)
        y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - dialog.winfo_reqheight()) // 2)
        dialog.geometry(f"+{x}+{y}")
        dialog.lift()
        dialog.focus_force()
        entry.focus_force()
        self.root.wait_window(dialog)
        self.password_dialog = None
        self.password_dialog_open = False
        self.apply_window_lock_state(force=True)
        return result["value"]

    def input_hint_for_task(self, task: dict) -> str:
        if (task.get("type") or "") != "input":
            return ""
        samples = [
            localized_value(task, "prompt", "ru"),
            localized_value(task, "prompt", "pl"),
            localized_value(task, "prompt", "en"),
            localized_value(task, "title", "ru"),
            localized_value(task, "title", "pl"),
            localized_value(task, "title", "en"),
        ]
        for sample in samples:
            match = re.search(r"\[([^\[\]\s]{1,8})\]", sample or "")
            if not match:
                continue
            token = match.group(1).strip()
            return {
                "ru": f"Подсказка: можно вводить просто {token} без квадратных скобок.",
                "pl": f"Wskazowka: mozna wpisac po prostu {token} bez nawiasow kwadratowych.",
                "en": f"Hint: you can type just {token} without square brackets.",
            }.get(self.lang, f"Hint: you can type just {token} without square brackets.")
        return ""

    def show_waiting_state(self) -> None:
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.set_break_lock(False)
        self.current_task = None
        self.lesson_blocks = []
        self.hide_side_panels()
        self.hide_overlay()
        self.title_label.config(text=self.tt("waiting_title"))
        self.step_label.config(text="")
        self.ru_prompt.config(text=self.tt("waiting_ru"))
        self.pl_prompt.config(text=self.tt("waiting_pl"))
        for widget in self.answer_area.winfo_children():
            widget.pack_forget()
        self.input_hint_label.config(text="")
        self.lesson_timer_label.config(text="")
        self.memory_timer_label.config(text="")
        self.feedback.config(text=self.waiting_note_text(), fg=MUTED)
        self.update_pause_button()
        self.queue_remote_sync(200)

    def hide_side_panels(self) -> None:
        for frame in (self.side_left, self.side_right):
            frame.config(width=0)
            for widget in frame.winfo_children():
                widget.destroy()

    def set_side_panel(self, side: str, title: str, content: str) -> None:
        frame = self.side_left if side == "left" else self.side_right
        for widget in frame.winfo_children():
            widget.destroy()
        frame.config(width=230)
        wraplength = max(150, int(frame.cget("width") or 230) - 24)
        tk.Label(frame, text=title, fg=TEXT, bg=CARD_2, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(12, 6))
        tk.Label(frame, text=content, fg=MUTED, bg=CARD_2, justify="left", wraplength=wraplength, font=("Segoe UI", 11)).pack(anchor="nw", padx=12, pady=(0, 12))
        frame.lift()

    def update_support_panels(self, task: dict) -> None:
        hint = task.get("hint_type", "")
        metadata = task.get("metadata") or {}
        self.hide_side_panels()
        support_ru = str(metadata.get("support_ru") or "").strip()
        support_pl = str(metadata.get("support_pl") or "").strip()
        if support_ru or support_pl:
            self.set_side_panel("left", str(metadata.get("support_title_ru") or "Подсказка"), support_ru or support_pl)
            self.set_side_panel("right", str(metadata.get("support_title_pl") or "Wskazówka"), support_pl or support_ru)
            return
        if hint == "letters":
            self.set_side_panel("left", "Русский", self.supports.get("letters_ru", ""))
            self.set_side_panel("right", "Polski", self.supports.get("letters_pl", ""))
        elif hint == "multiplication":
            self.set_side_panel("left", "Умножение", self.supports.get("multiplication_ru", ""))
            self.set_side_panel("right", "Mnożenie", self.supports.get("multiplication_pl", ""))
        elif hint == "reading":
            self.set_side_panel("left", "Чтение", self.supports.get("reading_ru", ""))
            self.set_side_panel("right", "Czytanie", self.supports.get("reading_pl", ""))
        else:
            self.set_side_panel("left", "Подсказка", self.supports.get("lesson_ru" if hint == "lesson" else "math_ru", ""))
            self.set_side_panel("right", "Wskazówka", self.supports.get("lesson_pl" if hint == "lesson" else "math_pl", ""))

    def show_lesson_block(self, index: int) -> None:
        self.cancel_lesson_timer()
        self.lesson_index = index
        block = self.lesson_blocks[index]
        self.current_task = None
        self.hide_overlay()
        self.set_break_lock(True)
        self.hide_side_panels()
        topic_title = localized_value(self.current_topic or {}, "title", self.lang)
        block_title = localized_value(block, "title", self.lang)
        self.title_label.config(text=f"{topic_title}: {block_title}" if block_title else topic_title)
        self.step_label.config(text=self.lesson_step_text(index + 1, len(self.lesson_blocks)))
        self.ru_prompt.config(text=localized_value(block, "content", "ru"))
        self.pl_prompt.config(text=localized_value(block, "content", "pl"))
        for widget in self.answer_area.winfo_children():
            widget.pack_forget()
        self.input_hint_label.config(text="")
        self.lesson_btn.config(state="normal", text=self.lesson_action_text())
        self.lesson_btn.pack()
        self.feedback.config(
            text={
                "ru": "Можно начать задания сразу или сначала спокойно прочитать тему.",
                "pl": "Mozesz zaczac zadania od razu albo najpierw spokojnie przeczytac temat.",
                "en": "You can start tasks now or read the lesson first.",
            }.get(self.lang, "You can start tasks now or read the lesson first."),
            fg=MUTED,
        )
        self.memory_timer_label.config(text="")
        self.feedback.config(text="Сначала изучи тему, затем начни задания.", fg=MUTED)
        self.feedback.config(
            text={
                "ru": "Можно начать задания сразу или сначала спокойно прочитать тему.",
                "pl": "Mozesz zaczac zadania od razu albo najpierw spokojnie przeczytac temat.",
                "en": "You can start tasks now or read the lesson first.",
            }.get(self.lang, "You can start tasks now or read the lesson first."),
            fg=MUTED,
        )
        self.feedback.config(text=self.lesson_ready_text(), fg=MUTED)
        self.lesson_seconds_left = max(5, safe_int(self.settings.get("lesson_seconds"), 45))
        self.update_pause_button()
        self.tick_lesson_timer()
        self.queue_remote_sync(200)

    def tick_lesson_timer(self) -> None:
        minutes, seconds = divmod(self.lesson_seconds_left, 60)
        self.lesson_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        if self.lesson_seconds_left <= 0:
            self.lesson_after_id = None
            self.lesson_btn.config(state="normal")
            self.feedback.config(
                text={
                    "ru": "Тема изучена. Можно переходить к заданиям.",
                    "pl": "Temat przeczytany. Mozna przejsc do zadan.",
                    "en": "Lesson reviewed. You can continue to the tasks.",
                }.get(self.lang, "Lesson reviewed. You can continue to the tasks."),
                fg=GOOD,
            )
            self.feedback.config(text="Тема изучена. Можно переходить к заданиям.", fg=GOOD)
            self.feedback.config(
                text={
                    "ru": "Тема изучена. Можно переходить к заданиям.",
                    "pl": "Temat przeczytany. Mozna przejsc do zadan.",
                    "en": "Lesson reviewed. You can continue to the tasks.",
                }.get(self.lang, "Lesson reviewed. You can continue to the tasks."),
                fg=GOOD,
            )
            self.feedback.config(text=self.lesson_done_text(), fg=GOOD)
            self.update_pause_button()
            return
        self.lesson_seconds_left -= 1
        self.lesson_after_id = self.root.after(1000, self.tick_lesson_timer)

    def advance_from_lesson(self) -> None:
        self.cancel_lesson_timer()
        self.lesson_index += 1
        if self.lesson_index < len(self.lesson_blocks):
            self.show_lesson_block(self.lesson_index)
            return
        self.lesson_timer_label.config(text="")
        if not self.current_break_tasks:
            self.show_waiting_state()
            return
        self.show_task(self.current_break_tasks[0])

    def show_task(self, task: dict) -> None:
        self.cancel_lesson_timer()
        self.current_task = task
        self.hide_overlay()
        self.lesson_timer_label.config(text="")
        self.memory_timer_label.config(text="")
        self.feedback.config(text="", fg=MUTED)
        self.update_coins()
        self.update_pause_button()
        self.queue_remote_sync(200)
        self.step_label.config(text=f"{self.tt('task')} {self.current_index + 1} {self.tt('of')} {len(self.current_break_tasks)}")
        self.title_label.config(text=f"{localized_value(task, 'title', 'ru')}  |  {localized_value(task, 'title', 'pl')}")
        self.ru_prompt.config(text=localized_value(task, "prompt", "ru"))
        self.pl_prompt.config(text=localized_value(task, "prompt", "pl"))
        self.update_support_panels(task)
        for widget in self.answer_area.winfo_children():
            widget.pack_forget()
        self.input_hint_label.config(text="")
        self.cancel_memory_timer()
        task_type = task.get("type")
        if task_type == "choice":
            grid = tk.Frame(self.answer_area, bg=CENTER)
            grid.pack(fill="x", expand=True)
            options = self.choice_options_for_task(task)
            column_count = 1 if self.viewport_width() < 1220 or any(len(option) > 28 for option in options) else 2
            option_wrap = 320 if column_count == 1 else 260
            for column in range(column_count):
                grid.grid_columnconfigure(column, weight=1, uniform="task_options")
            for index, option in enumerate(options):
                tk.Button(
                    grid,
                    text=option,
                    command=lambda current=option: self.check_answer(choice=current),
                    bg=ACCENT_2,
                    fg="white",
                    relief="flat",
                    font=("Segoe UI", 12, "bold"),
                    justify="center",
                    wraplength=option_wrap,
                    pady=12,
                    padx=14,
                ).grid(row=index // column_count, column=index % column_count, padx=8, pady=8, sticky="ew")
        elif task_type == "reading":
            self.next_btn.pack()
            self.feedback.config(text=self.tt("read_aloud"), fg=MUTED)
        elif task_type == "memory":
            self.memory_seconds_left = max(10, safe_int(self.settings.get("lesson_seconds"), 45))
            self.feedback.config(text=self.tt("memory_read"), fg=MUTED)
            self.memory_btn.config(state="disabled")
            self.memory_btn.pack()
            self.tick_memory_timer()
        else:
            self.answer_entry.delete(0, "end")
            self.answer_entry.pack(side="left", padx=(0, 12))
            self.check_btn.pack(side="left")
            self.input_hint_label.config(text=self.input_hint_for_task(task))
            self.answer_entry.focus_set()

    def tick_memory_timer(self) -> None:
        minutes, seconds = divmod(self.memory_seconds_left, 60)
        self.memory_timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        if self.memory_seconds_left <= 0:
            self.memory_after_id = None
            self.memory_btn.config(state="normal")
            self.feedback.config(text=self.tt("remembered"), fg=GOOD)
            return
        self.memory_seconds_left -= 1
        self.memory_after_id = self.root.after(1000, self.tick_memory_timer)

    def finish_memory_task(self) -> None:
        self.cancel_memory_timer()
        self.stats["correct"] += 1
        self.stats["coins"] += 5
        self.persist_stats()
        self.update_coins()
        self.feedback.config(text=self.tt("correct"), fg=GOOD)
        self.root.after(500, self.advance_task)

    def mark_reading_done(self) -> None:
        self.stats["correct"] += 1
        self.stats["coins"] += 5
        self.persist_stats()
        self.update_coins()
        self.feedback.config(text=self.tt("reading_done"), fg=GOOD)
        self.root.after(500, self.advance_task)

    def check_answer(self, choice: str | None = None) -> None:
        if not self.current_task:
            return
        given = choice if choice is not None else self.answer_entry.get().strip()
        if self.db.answer_matches(self.current_task, given):
            self.stats["correct"] += 1
            self.stats["coins"] += 5
            self.persist_stats()
            self.update_coins()
            self.feedback.config(text=self.tt("correct"), fg=GOOD)
            self.root.after(500, self.advance_task)
        else:
            self.stats["wrong"] += 1
            self.stats["coins"] = max(0, self.stats["coins"] - 1)
            self.persist_stats()
            self.update_coins()
            self.feedback.config(text=self.tt("wrong"), fg=BAD)

    def advance_task(self) -> None:
        self.current_index += 1
        if self.current_index >= len(self.current_break_tasks):
            self.stats["completed_breaks"] += 1
            if self.program_mode == "child":
                self.stats["child_completed"] += 1
            elif self.program_mode == "adult":
                self.stats["adult_completed"] += 1
            else:
                self.stats["memory_completed"] += 1
            self.stats["coins"] += 10
            self.persist_stats()
            self.update_coins()
            self.schedule_next_break()
            self.show_waiting_state()
            return
        self.show_task(self.current_break_tasks[self.current_index])

    def update_coins(self) -> None:
        self.coins_badge.config(text=f"{self.tt('coins')}: {self.stats.get('coins', 0)}")
        if hasattr(self, "shop_balance_var"):
            self.shop_balance_var.set(f"{self.tt('coins')}: {self.stats.get('coins', 0)}")

    def refresh_parent_panel_if_open(self) -> None:
        panel = self.parent_panel_window
        if panel and panel.winfo_exists():
            panel.refresh_settings()

    def close_shop_window(self) -> None:
        if self.shop_window and self.shop_window.winfo_exists():
            self.shop_window.destroy()
        self.shop_window = None

    def refresh_shop_window(self) -> None:
        if not self.shop_window or not self.shop_window.winfo_exists():
            return
        if not hasattr(self, "shop_content") or not self.shop_content.winfo_exists():
            return

        for widget in self.shop_content.winfo_children():
            widget.destroy()

        pending_bonus = max(0, safe_int(self.settings.get("shop_pending_delay_bonus_seconds"), 0))
        bonus_minutes, bonus_seconds = divmod(pending_bonus, 60)
        extra_pauses = self.extra_pause_tokens()
        upgrade_level = max(0, safe_int(self.settings.get("pause_upgrade_level"), 0))
        pause_min, pause_max = self.pause_duration_bounds()
        next_upgrade_cost = self.pause_upgrade_cost(upgrade_level)

        self.shop_balance_var.set(f"{self.tt('coins')}: {self.stats.get('coins', 0)}")
        self.shop_status_var.set(
            self.ui_text(
                "Покупки сохраняются между сессиями. Доп. время действует на ближайший интервал.",
                "Zakupy sa zapisywane miedzy sesjami. Dodatkowy czas dziala na najblizszy interwal.",
                "Purchases are saved between sessions. Extra time applies to the nearest interval.",
            )
        )

        grid = tk.Frame(self.shop_content, bg=BG)
        grid.pack(fill="both", expand=True)
        for column in range(3):
            grid.grid_columnconfigure(column, weight=1, uniform="shop")

        def shop_card(
            column: int,
            title: str,
            subtitle: str,
            status: str,
            price_label: str,
            button_text: str,
            command,
            *,
            state: str = "normal",
        ) -> None:
            card = tk.Frame(grid, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=column, padx=14, pady=14, sticky="nsew")
            inner = tk.Frame(card, bg=CARD)
            inner.pack(fill="both", expand=True, padx=18, pady=18)
            tk.Label(inner, text=title, bg=CARD, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
            tk.Label(inner, text=subtitle, bg=CARD, fg=MUTED, justify="left", wraplength=250, font=("Segoe UI", 11)).pack(anchor="w", pady=(10, 16))
            tk.Label(inner, text=status, bg=CARD_2, fg=TEXT, justify="left", wraplength=250, font=("Segoe UI", 11), padx=12, pady=10).pack(fill="x")
            tk.Frame(inner, bg=CARD).pack(fill="both", expand=True)
            bottom = tk.Frame(inner, bg=CARD)
            bottom.pack(fill="x", pady=(16, 0))
            tk.Label(bottom, text=price_label, bg=CARD, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
            tk.Button(
                bottom,
                text=button_text,
                command=command,
                state=state,
                bg=ACCENT if state == "normal" else CARD_2,
                fg="#111" if state == "normal" else MUTED,
                relief="flat",
                font=("Segoe UI", 11, "bold"),
                padx=14,
                pady=9,
            ).pack(anchor="w", pady=(12, 0))

        shop_card(
            0,
            self.ui_text("Доп. время", "Dodatkowy czas", "Extra time"),
            self.ui_text(
                "Случайно добавляет 2-4 минуты до следующего обязательного задания.",
                "Losowo dodaje 2-4 minuty do nastepnego obowiazkowego zadania.",
                "Randomly adds 2-4 minutes before the next mandatory task.",
            ),
            self.ui_text(
                f"В запасе: {bonus_minutes:02d}:{bonus_seconds:02d}",
                f"W zapasie: {bonus_minutes:02d}:{bonus_seconds:02d}",
                f"In reserve: {bonus_minutes:02d}:{bonus_seconds:02d}",
            ),
            f"100 {self.tt('coins').lower()}",
            self.ui_text("Купить время", "Kup czas", "Buy time"),
            self.buy_shop_delay_bonus,
        )

        shop_card(
            1,
            self.ui_text("Доп. пауза", "Dodatkowa pauza", "Extra pause"),
            self.ui_text(
                "Даёт ещё одну пользовательскую паузу поверх лимита занятия.",
                "Daje jedna dodatkowa pauze ponad limit tej sesji.",
                "Adds one more student pause on top of the current session limit.",
            ),
            self.ui_text(
                f"В запасе пауз: {extra_pauses}",
                f"Pauzy w zapasie: {extra_pauses}",
                f"Pauses in reserve: {extra_pauses}",
            ),
            f"250 {self.tt('coins').lower()}",
            self.ui_text("Купить паузу", "Kup pauze", "Buy pause"),
            self.buy_shop_extra_pause,
        )

        shop_card(
            2,
            self.ui_text("Апгрейд паузы", "Ulepszenie pauzy", "Pause upgrade"),
            self.ui_text(
                "Увеличивает доступную длительность паузы и сохраняется между сессиями.",
                "Zwiekasza dostepna dlugosc pauzy i zapisuje sie miedzy sesjami.",
                "Increases the available pause duration and persists between sessions.",
            ),
            self.ui_text(
                f"Уровень {upgrade_level}/4. Сейчас {pause_min}-{pause_max} мин.",
                f"Poziom {upgrade_level}/4. Teraz {pause_min}-{pause_max} min.",
                f"Level {upgrade_level}/4. Current range: {pause_min}-{pause_max} min.",
            ),
            (
                self.ui_text("Максимум", "Maksimum", "Maximum")
                if next_upgrade_cost is None
                else f"{next_upgrade_cost} {self.tt('coins').lower()}"
            ),
            (
                self.ui_text("Макс. уровень", "Max poziom", "Max level")
                if next_upgrade_cost is None
                else self.ui_text("Улучшить", "Ulepsz", "Upgrade")
            ),
            self.buy_shop_pause_upgrade,
            state="disabled" if next_upgrade_cost is None else "normal",
        )

    def open_shop(self) -> None:
        if self.shop_window and self.shop_window.winfo_exists():
            self.refresh_shop_window()
            self.shop_window.lift()
            self.shop_window.focus_force()
            return

        top = tk.Toplevel(self.root)
        self.shop_window = top
        top.title(self.tt("shop"))
        top.geometry("980x640")
        top.configure(bg=BG)
        top.resizable(True, True)
        top.protocol("WM_DELETE_WINDOW", self.close_shop_window)

        x = max(30, self.root.winfo_rootx() + 70)
        y = max(30, self.root.winfo_rooty() + 50)
        top.geometry(f"980x640+{x}+{y}")

        header = tk.Frame(top, bg=PANEL, height=78)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=self.ui_text("Магазин бонусов", "Sklep bonusow", "Bonus shop"), fg=TEXT, bg=PANEL, font=("Segoe UI", 24, "bold")).pack(side="left", padx=20, pady=16)
        self.shop_balance_var = tk.StringVar(value="")
        tk.Label(header, textvariable=self.shop_balance_var, fg=TEXT, bg=CARD, padx=16, pady=10, font=("Segoe UI", 12, "bold")).pack(side="right", padx=(0, 10), pady=14)
        tk.Button(
            header,
            text=self.tt("close"),
            command=self.close_shop_window,
            bg=ACCENT,
            fg="#111",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        ).pack(side="right", padx=(0, 14), pady=14)

        self.shop_content = tk.Frame(top, bg=BG)
        self.shop_content.pack(fill="both", expand=True, padx=20, pady=(18, 10))
        self.shop_status_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.shop_status_var, fg=MUTED, bg=BG, font=("Segoe UI", 11), wraplength=900, justify="center").pack(fill="x", padx=20, pady=(0, 18))
        self.refresh_shop_window()

    def buy_shop_delay_bonus(self) -> None:
        bonus_seconds = random.randint(120, 240)
        if not self.spend_coins(100):
            return
        waiting_now = bool(self.current_topic) and self.break_after_id is not None and not self.current_task and not self.lesson_blocks and self.manual_pause_state is None
        if waiting_now:
            total_delay = max(1, self.remaining_break_seconds()) + bonus_seconds
            self.cancel_break_timer()
            self.break_deadline_ts = time.monotonic() + total_delay
            self.break_after_id = self.root.after(total_delay * 1000, self.start_next_break)
        else:
            pending_bonus = max(0, safe_int(self.settings.get("shop_pending_delay_bonus_seconds"), 0))
            self.settings = self.db.update_settings({"shop_pending_delay_bonus_seconds": pending_bonus + bonus_seconds})
            self.reload_from_db()
        self.refresh_shop_window()
        self.refresh_parent_panel_if_open()
        messagebox.showinfo(
            APP_TITLE,
            self.ui_text(
                f"Добавлено {bonus_seconds // 60}-{bonus_seconds // 60 if bonus_seconds % 60 == 0 else (bonus_seconds // 60) + 1} мин. к интервалу.",
                f"Dodano okolo {bonus_seconds // 60}-{bonus_seconds // 60 if bonus_seconds % 60 == 0 else (bonus_seconds // 60) + 1} min do interwalu.",
                f"Added about {bonus_seconds // 60}-{bonus_seconds // 60 if bonus_seconds % 60 == 0 else (bonus_seconds // 60) + 1} min to the interval.",
            ),
            parent=self.shop_window or self.root,
        )

    def buy_shop_extra_pause(self) -> None:
        if not self.spend_coins(250):
            return
        self.settings = self.db.update_settings({"shop_extra_pause_tokens": self.extra_pause_tokens() + 1})
        self.reload_from_db()
        self.update_pause_button()
        self.refresh_shop_window()
        self.refresh_parent_panel_if_open()
        messagebox.showinfo(
            APP_TITLE,
            self.ui_text(
                "Дополнительная пауза добавлена в запас.",
                "Dodatkowa pauza zostala dodana do zapasu.",
                "An extra pause has been added to the reserve.",
            ),
            parent=self.shop_window or self.root,
        )

    def buy_shop_pause_upgrade(self) -> None:
        current_level = max(0, safe_int(self.settings.get("pause_upgrade_level"), 0))
        cost = self.pause_upgrade_cost(current_level)
        if cost is None:
            messagebox.showinfo(
                APP_TITLE,
                self.ui_text("Улучшение уже максимальное.", "To ulepszenie jest juz maksymalne.", "This upgrade is already maxed out."),
                parent=self.shop_window or self.root,
            )
            return
        if not self.spend_coins(cost):
            return
        new_level = min(4, current_level + 1)
        pause_min, pause_max = self.pause_upgrade_bounds(new_level)
        current_minutes = safe_int(self.settings.get("manual_pause_minutes"), pause_min)
        self.settings = self.db.update_settings(
            {
                "pause_upgrade_level": new_level,
                "manual_pause_minutes": min(pause_max, max(pause_min, current_minutes)),
            }
        )
        self.reload_from_db()
        self.update_pause_button()
        self.refresh_shop_window()
        self.refresh_parent_panel_if_open()
        messagebox.showinfo(
            APP_TITLE,
            self.ui_text(
                f"Пауза улучшена. Новый диапазон: {pause_min}-{pause_max} мин.",
                f"Pauza ulepszona. Nowy zakres: {pause_min}-{pause_max} min.",
                f"Pause upgraded. New range: {pause_min}-{pause_max} min.",
            ),
            parent=self.shop_window or self.root,
        )

    def show_phone_info(self) -> None:
        if not self.lan_url:
            messagebox.showinfo(APP_TITLE, "LAN panel is disabled in settings.")
            return
        messagebox.showinfo(
            APP_TITLE,
            f"LAN panel URL:\n{self.lan_url}\n\nProgram ID:\n{self.settings['program_id']}\n\nUse the same parent password as in the desktop app.",
        )

    def ask_parent_panel(self) -> None:
        if self.parent_panel_window and self.parent_panel_window.winfo_exists():
            self.parent_panel_window.bring_to_front()
            return
        password = self.prompt_password_dialog(self.tt("password"), self.tt("enter_parent_password"))
        if password is None:
            return
        if self.db.verify_parent_password(password):
            self.parent_panel_window = ParentPanelV23(self)
            return
        messagebox.showerror(APP_TITLE, self.tt("bad_password"), parent=self.root)

    def ask_return_to_menu(self) -> None:
        if not (self.current_topic or self.manual_pause_state):
            return
        password = self.prompt_password_dialog(
            self.tt("password"),
            self.ui_text(
                "Введите пароль родителя, чтобы вернуться в главное меню.",
                "Wpisz haslo rodzica, aby wrocic do menu glownego.",
                "Enter the parent password to return to the main menu.",
            ),
        )
        if password is None:
            return
        if self.db.verify_parent_password(password):
            self.show_start_screen()
            return
        messagebox.showerror(APP_TITLE, self.tt("bad_password"), parent=self.root)

    def request_close(self) -> None:
        password = self.prompt_password_dialog(self.tt("password"), self.tt("close_parent_password"))
        if password is None:
            return
        if password and self.db.verify_parent_password(password):
            self.cancel_break_timer()
            self.cancel_lesson_timer()
            self.cancel_memory_timer()
            self.cancel_manual_pause_timer()
            if self.remote_sync_loop_after_id:
                self.root.after_cancel(self.remote_sync_loop_after_id)
                self.remote_sync_loop_after_id = None
            if self.remote_sync_debounce_after_id:
                self.root.after_cancel(self.remote_sync_debounce_after_id)
                self.remote_sync_debounce_after_id = None
            if self.remote_sync_poll_after_id:
                self.root.after_cancel(self.remote_sync_poll_after_id)
                self.remote_sync_poll_after_id = None
            if self.lan_server:
                self.lan_server.stop()
            self.close_shop_window()
            self.root.destroy()
            return
        messagebox.showerror(APP_TITLE, self.tt("bad_password"), parent=self.root)

    def tick_loop(self) -> None:
        if self.current_task or self.lesson_blocks:
            self.set_break_lock(True)
        elif not self.break_lock_active and self.window_lock_applied:
            self.apply_window_lock_state(force=True)
        if self.should_enforce_window_lock():
            self.enforce_window_lock()
        self.root.after(1000, self.tick_loop)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    root = tk.Tk()
    app = MinecraftCoachV23(root)
    root.mainloop()


if __name__ == "__main__":
    main()
