from __future__ import annotations

import json
import random
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Callable

from .app_shared import APP_TITLE, normalize_input, t
from .lan_admin import LanAdminServer
from .local_db import LocalDB
from .module_installer import (
    ModuleImportError,
    import_module_source,
    list_installed_modules,
)


def _runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _bundle_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root).resolve()
    return Path(__file__).resolve().parents[1]


def _first_existing_path(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


RUNTIME_DIR = _runtime_root()
BUNDLE_DIR = _bundle_root()
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
MODULE_BACKUPS_DIR = RUNTIME_DIR / "module_backups"

LANGUAGES = {
    "ru": ("Русский", "Выберите язык"),
    "pl": ("Polski", "Wybierz język"),
    "en": ("English", "Choose language"),
}

PALETTE = {
    "bg": "#101214",
    "surface": "#181c20",
    "panel": "#22282e",
    "card": "#262d33",
    "card_hover": "#303841",
    "text": "#f5f1e8",
    "muted": "#b9c0c7",
    "line": "#3e4852",
    "accent": "#f3bd3f",
    "accent_text": "#17120a",
    "teal": "#3f8f7a",
    "good": "#45a979",
    "bad": "#d85656",
}

COPY = {
    "ru": {
        "title": "Minecraft Coach",
        "language_intro": "Сначала выберите язык интерфейса.",
        "main": "Главное меню",
        "play": "Играть",
        "settings": "Настройки",
        "shop": "Магазин",
        "exit": "Выход",
        "modules": "Модули",
        "scan_modules": "Сканировать папку модулей",
        "modules_empty": "В папке modules пока нет доступных модулей.",
        "levels": "Уровни",
        "topics": "Темы",
        "back": "Назад",
        "start_now": "Начать сейчас",
        "waiting": "Ожидание следующего задания",
        "selected_topic": "Выбранная тема",
        "settings_saved": "Настройки сохранены.",
        "bad_number": "Введите корректное число.",
        "import_module": "Импортировать модуль",
        "refresh": "Обновить",
        "module_saved": "Модуль сохранён.",
        "json_only": "Сохранение доступно только для module.json.",
        "no_tasks": "Для этой темы пока не найдено заданий.",
        "lesson_ready": "Можно прочитать тему или сразу перейти к заданиям.",
        "lesson_done": "Тема изучена. Можно переходить к заданиям.",
        "pause": "Пауза",
        "pause_left": "Пауза активна",
        "resume": "Продолжить",
        "no_pauses": "Паузы закончились. Дополнительную паузу можно купить в магазине.",
        "answer_hint": "Введите ответ и нажмите Enter.",
        "coins": "Монеты",
        "correct": "Правильно",
        "wrong": "Неверно. Попробуй ещё раз.",
        "completed": "Блок завершён. Следующее задание появится позже.",
        "buy": "Купить",
        "extra_time": "Дополнительное время",
        "extra_pause": "Дополнительная пауза",
        "pause_upgrade": "Улучшение паузы",
        "not_enough": "Недостаточно монет.",
        "lan_started": "LAN-панель запущена",
    },
    "pl": {
        "title": "Minecraft Coach",
        "language_intro": "Najpierw wybierz język interfejsu.",
        "main": "Menu główne",
        "play": "Graj",
        "settings": "Ustawienia",
        "shop": "Sklep",
        "exit": "Wyjście",
        "modules": "Moduły",
        "scan_modules": "Skanuj folder modułów",
        "modules_empty": "W folderze modules nie ma jeszcze dostępnych modułów.",
        "levels": "Poziomy",
        "topics": "Tematy",
        "back": "Wstecz",
        "start_now": "Zacznij teraz",
        "waiting": "Oczekiwanie na kolejne zadanie",
        "selected_topic": "Wybrany temat",
        "settings_saved": "Ustawienia zapisane.",
        "bad_number": "Wpisz poprawną liczbę.",
        "import_module": "Importuj moduł",
        "refresh": "Odśwież",
        "module_saved": "Moduł zapisany.",
        "json_only": "Zapis jest dostępny tylko dla module.json.",
        "no_tasks": "Dla tego tematu nie znaleziono jeszcze zadań.",
        "lesson_ready": "Możesz przeczytać temat albo od razu przejść do zadań.",
        "lesson_done": "Temat przeczytany. Można przejść do zadań.",
        "pause": "Pauza",
        "pause_left": "Pauza aktywna",
        "resume": "Kontynuuj",
        "no_pauses": "Pauzy się skończyły. Dodatkową pauzę można kupić w sklepie.",
        "answer_hint": "Wpisz odpowiedź i naciśnij Enter.",
        "coins": "Monety",
        "correct": "Dobrze",
        "wrong": "Źle. Spróbuj jeszcze raz.",
        "completed": "Blok ukończony. Kolejne zadanie pojawi się później.",
        "buy": "Kup",
        "extra_time": "Dodatkowy czas",
        "extra_pause": "Dodatkowa pauza",
        "pause_upgrade": "Ulepszenie pauzy",
        "not_enough": "Za mało monet.",
        "lan_started": "Panel LAN uruchomiony",
    },
    "en": {
        "title": "Minecraft Coach",
        "language_intro": "Choose the interface language first.",
        "main": "Main menu",
        "play": "Play",
        "settings": "Settings",
        "shop": "Shop",
        "exit": "Exit",
        "modules": "Modules",
        "scan_modules": "Scan modules folder",
        "modules_empty": "No available modules were found in the modules folder.",
        "levels": "Levels",
        "topics": "Topics",
        "back": "Back",
        "start_now": "Start now",
        "waiting": "Waiting for the next task",
        "selected_topic": "Selected topic",
        "settings_saved": "Settings saved.",
        "bad_number": "Enter a valid number.",
        "import_module": "Import module",
        "refresh": "Refresh",
        "module_saved": "Module saved.",
        "json_only": "Saving is available only for module.json.",
        "no_tasks": "No tasks are configured for this topic yet.",
        "lesson_ready": "You can read the lesson or go straight to tasks.",
        "lesson_done": "Lesson reviewed. You can continue to the tasks.",
        "pause": "Pause",
        "pause_left": "Pause is active",
        "resume": "Resume",
        "no_pauses": "No pauses left. You can buy an extra pause in the shop.",
        "answer_hint": "Enter the answer and press Enter.",
        "coins": "Coins",
        "correct": "Correct",
        "wrong": "Wrong. Try again.",
        "completed": "Block completed. The next task will appear later.",
        "buy": "Buy",
        "extra_time": "Extra time",
        "extra_pause": "Extra pause",
        "pause_upgrade": "Pause upgrade",
        "not_enough": "Not enough coins.",
        "lan_started": "LAN panel started",
    },
}


def localized_value(item: dict[str, Any] | None, base: str, lang: str) -> str:
    item = item or {}
    for code in (lang, "ru", "pl", "en"):
        value = item.get(f"{base}_{code}")
        if value:
            return str(value)
    return str(item.get(base, ""))


def safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


class ScrollFrame(tk.Frame):
    def __init__(self, parent: tk.Misc, *, bg: str) -> None:
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.body = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.body.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_body_width)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _sync_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_body_width(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=max(1, event.width))

    def _on_mousewheel(self, event: tk.Event) -> None:
        if not self.winfo_ismapped():
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class ParentPanelV23(tk.Toplevel):
    def __init__(self, app: "MinecraftCoachV23", initial_tab: str = "settings") -> None:
        super().__init__(app.root)
        self.app = app
        self.current_tab = initial_tab
        self.title(app.text("settings"))
        self.configure(bg=PALETTE["bg"])
        self.geometry("900x620")
        self.minsize(720, 520)
        self.protocol("WM_DELETE_WINDOW", self.close_panel)

        self.settings_vars: dict[str, tk.StringVar] = {}
        self.module_rows: list[dict[str, Any]] = []
        self.module_list = tk.Listbox(
            self,
            bg=PALETTE["surface"],
            fg=PALETTE["text"],
            selectbackground=PALETTE["teal"],
            relief="flat",
            font=("Segoe UI", 11),
        )
        self.module_editor = tk.Text(
            self,
            bg=PALETTE["surface"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            relief="flat",
            font=("Consolas", 10),
            wrap="none",
        )
        self.status_var = tk.StringVar(value="")
        self.body = tk.Frame(self, bg=PALETTE["bg"])
        self.body.pack(fill="both", expand=True)
        self.show(initial_tab)

    def text(self, key: str) -> str:
        return self.app.text(key)

    def close_panel(self) -> None:
        if self.winfo_exists():
            self.destroy()

    def show(self, tab: str) -> None:
        self.current_tab = tab
        for child in self.body.winfo_children():
            child.destroy()
        if tab == "modules":
            self._build_modules()
        else:
            self._build_settings()

    def _build_settings(self) -> None:
        header = tk.Frame(self.body, bg=PALETTE["bg"])
        header.pack(fill="x", padx=24, pady=(24, 10))
        tk.Label(
            header,
            text=self.text("settings"),
            bg=PALETTE["bg"],
            fg=PALETTE["text"],
            font=("Segoe UI", 24, "bold"),
        ).pack(side="left")
        self._button(header, self.text("modules"), lambda: self.show("modules")).pack(side="right")

        form = tk.Frame(self.body, bg=PALETTE["panel"], padx=22, pady=22)
        form.pack(fill="x", padx=24, pady=12)
        fields = [
            ("window_language", self.app.tt("language")),
            ("break_seconds", self.app.tt("break_seconds")),
            ("tasks_per_break", "Tasks per break"),
            ("lesson_seconds", "Lesson seconds"),
            ("manual_pause_uses", "Pauses per session"),
            ("manual_pause_minutes", "Pause minutes"),
            ("lan_admin_port", "LAN port"),
            ("server_base_url", "Server API URL"),
        ]
        self.settings_vars = {}
        for row, (key, label) in enumerate(fields):
            tk.Label(form, text=label, bg=PALETTE["panel"], fg=PALETTE["muted"], font=("Segoe UI", 10, "bold")).grid(
                row=row,
                column=0,
                sticky="w",
                pady=7,
            )
            var = tk.StringVar(value=str(self.app.settings.get(key, "")))
            self.settings_vars[key] = var
            tk.Entry(
                form,
                textvariable=var,
                bg=PALETTE["surface"],
                fg=PALETTE["text"],
                insertbackground=PALETTE["text"],
                relief="flat",
                font=("Segoe UI", 11),
            ).grid(row=row, column=1, sticky="ew", padx=(18, 0), pady=7, ipady=7)
        form.grid_columnconfigure(1, weight=1)

        footer = tk.Frame(self.body, bg=PALETTE["bg"])
        footer.pack(fill="x", padx=24, pady=12)
        self._button(footer, self.text("save"), lambda: self.save_settings()).pack(side="left")
        self._button(footer, self.text("close"), self.close_panel, tone="quiet").pack(side="right")
        tk.Label(footer, textvariable=self.status_var, bg=PALETTE["bg"], fg=PALETTE["muted"], font=("Segoe UI", 10)).pack(
            side="left",
            padx=14,
        )
        self.refresh_settings()

    def _build_modules(self) -> None:
        header = tk.Frame(self.body, bg=PALETTE["bg"])
        header.pack(fill="x", padx=24, pady=(24, 10))
        tk.Label(
            header,
            text=self.text("modules"),
            bg=PALETTE["bg"],
            fg=PALETTE["text"],
            font=("Segoe UI", 24, "bold"),
        ).pack(side="left")
        self._button(header, self.text("settings"), lambda: self.show("settings"), tone="quiet").pack(side="right")

        toolbar = tk.Frame(self.body, bg=PALETTE["bg"])
        toolbar.pack(fill="x", padx=24, pady=(0, 12))
        self._button(toolbar, self.text("refresh"), self.refresh_module_editor).pack(side="left")
        self._button(toolbar, self.text("import_module"), self.import_module).pack(side="left", padx=(10, 0))

        split = tk.Frame(self.body, bg=PALETTE["bg"])
        split.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        split.grid_columnconfigure(0, weight=1)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)
        self.module_list = tk.Listbox(
            split,
            bg=PALETTE["surface"],
            fg=PALETTE["text"],
            selectbackground=PALETTE["teal"],
            relief="flat",
            font=("Segoe UI", 11),
        )
        self.module_list.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.module_editor = tk.Text(
            split,
            bg=PALETTE["surface"],
            fg=PALETTE["text"],
            insertbackground=PALETTE["text"],
            relief="flat",
            font=("Consolas", 10),
            wrap="none",
        )
        self.module_editor.grid(row=0, column=1, sticky="nsew")
        self.module_list.bind("<<ListboxSelect>>", lambda _event: self.load_selected_module_manifest())

        footer = tk.Frame(self.body, bg=PALETTE["bg"])
        footer.pack(fill="x", padx=24, pady=(0, 20))
        self._button(footer, self.text("save"), self.save_selected_module_manifest).pack(side="left")
        tk.Label(footer, textvariable=self.status_var, bg=PALETTE["bg"], fg=PALETTE["muted"], font=("Segoe UI", 10)).pack(
            side="left",
            padx=14,
        )
        self.refresh_module_editor()

    def _button(self, parent: tk.Misc, text: str, command: Callable[[], None], *, tone: str = "primary") -> tk.Button:
        bg = PALETTE["accent"] if tone == "primary" else PALETTE["card"]
        fg = PALETTE["accent_text"] if tone == "primary" else PALETTE["text"]
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=PALETTE["card_hover"],
            activeforeground=PALETTE["text"],
            relief="flat",
            padx=16,
            pady=9,
            font=("Segoe UI", 10, "bold"),
        )

    def refresh_settings(self) -> None:
        for key, var in self.settings_vars.items():
            var.set(str(self.app.settings.get(key, "")))

    def save_settings(self, *, show_message: bool = True, close_panel: bool = False) -> None:
        numeric_keys = {
            "break_seconds",
            "tasks_per_break",
            "lesson_seconds",
            "manual_pause_uses",
            "manual_pause_minutes",
            "lan_admin_port",
        }
        payload: dict[str, Any] = {}
        for key, var in self.settings_vars.items():
            value = var.get().strip()
            if key in numeric_keys:
                try:
                    payload[key] = int(value)
                except ValueError:
                    self.status_var.set(self.text("bad_number"))
                    return
            elif key == "window_language":
                payload[key] = value if value in LANGUAGES else self.app.lang
            else:
                payload[key] = value
        self.app.settings = self.app.db.update_settings(payload)
        self.app.reload_from_db()
        self.app.refresh_current_screen()
        if show_message:
            self.status_var.set(self.text("settings_saved"))
        if close_panel:
            self.close_panel()

    def refresh_module_editor(self) -> None:
        self.app.sync_modules_from_disk(refresh_start_screen=False)
        self.module_rows = list_installed_modules(self.app.db.modules_dir)
        self.module_list.delete(0, "end")
        for row in self.module_rows:
            title = localized_value(row, "title", self.app.lang) or str(row.get("slug") or row.get("id"))
            suffix = "json" if str(row.get("manifest_type")) == "json" else "py"
            self.module_list.insert("end", f"{title}  ({suffix})")
        self.module_editor.delete("1.0", "end")
        if self.module_rows:
            self.module_list.selection_set(0)
            self.load_selected_module_manifest()

    def selected_module_row(self) -> dict[str, Any] | None:
        selection = self.module_list.curselection()
        if not selection:
            return None
        index = int(selection[0])
        if index >= len(self.module_rows):
            return None
        return self.module_rows[index]

    def load_selected_module_manifest(self) -> None:
        row = self.selected_module_row()
        self.module_editor.delete("1.0", "end")
        if not row:
            return
        manifest = Path(row["manifest_path"])
        if manifest.suffix.lower() == ".json":
            self.module_editor.insert("1.0", manifest.read_text(encoding="utf-8"))
        else:
            payload = row.get("payload") or {}
            self.module_editor.insert("1.0", json.dumps(payload, ensure_ascii=False, indent=2))
        if row.get("error"):
            self.status_var.set(str(row["error"]))
        else:
            self.status_var.set(str(manifest))

    def save_selected_module_manifest(self) -> None:
        row = self.selected_module_row()
        if not row:
            return
        manifest = Path(row["manifest_path"])
        if manifest.suffix.lower() != ".json":
            self.status_var.set(self.text("json_only"))
            return
        raw = self.module_editor.get("1.0", "end").strip()
        json.loads(raw or "{}")
        manifest.write_text(raw + "\n", encoding="utf-8")
        self.app.sync_modules_from_disk(refresh_start_screen=False)
        self.status_var.set(self.text("module_saved"))

    def import_module(self) -> None:
        source = filedialog.askopenfilename(
            parent=self,
            title=self.text("import_module"),
            filetypes=[("Modules", "*.zip *.json *.py"), ("All files", "*.*")],
        )
        if not source:
            return
        try:
            import_module_source(Path(source), self.app.db.modules_dir, backups_dir=MODULE_BACKUPS_DIR)
        except ModuleImportError as exc:
            self.status_var.set(str(exc))
            return
        self.refresh_module_editor()


class MinecraftCoachV23:
    def __init__(self, root: tk.Tk) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.root = root
        self.root.title(f"{APP_TITLE} v23")
        self.root.configure(bg=PALETTE["bg"])
        self.root.minsize(760, 560)
        self.root.protocol("WM_DELETE_WINDOW", self.request_close)

        self.db = LocalDB(
            DB_FILE,
            seed_path=SEED_DB,
            data_dir=DATA_DIR,
            assets_dir=ELECTRYK_DIR,
            modules_dir=MODULES_DIR,
        )
        self.lan_server: LanAdminServer | None = None
        self.lan_url = ""
        self.lan_server_manual_requested = False
        self.parent_panel_window: ParentPanelV23 | None = None
        self.shop_window: tk.Toplevel | None = None
        self.shop_content: tk.Frame | None = None
        self.shop_status_var = tk.StringVar(value="")
        self.shop_balance_var = tk.StringVar(value="")

        self.current_screen = "language"
        self.current_module: dict[str, Any] | None = None
        self.current_level: dict[str, Any] | None = None
        self.current_topic: dict[str, Any] | None = None
        self.current_break_tasks: list[dict[str, Any]] = []
        self.current_task: dict[str, Any] | None = None
        self.current_index = 0
        self.lesson_blocks: list[dict[str, Any]] = []
        self.lesson_index = 0
        self.program_mode = "child"
        self.manual_pause_state: dict[str, Any] | None = None
        self.manual_pause_seconds_left = 0
        self.session_pause_uses_remaining = 0

        self.break_after_id: str | None = None
        self.break_deadline_ts: float | None = None
        self.lesson_after_id: str | None = None
        self.lesson_seconds_left = 0
        self.memory_after_id: str | None = None
        self.memory_seconds_left = 0
        self.manual_pause_after_id: str | None = None
        self.geometry_after_id: str | None = None
        self.remote_sync_loop_after_id = None
        self.remote_sync_debounce_after_id = None
        self.remote_sync_poll_after_id = None

        self.reload_from_db()
        self.lang = str(self.settings.get("window_language") or "ru")
        self.root.geometry(str(self.settings.get("window_geometry") or "1180x760"))
        self.root.bind("<Configure>", self.on_root_configure, add="+")

        self.content = tk.Frame(self.root, bg=PALETTE["bg"])
        self.content.pack(fill="both", expand=True)
        self.status_var = tk.StringVar(value="")
        self.timer_var = tk.StringVar(value="")
        self.feedback_var = tk.StringVar(value="")
        self.answer_entry: tk.Entry | None = None
        self.memory_button: tk.Button | None = None
        self.task_image_ref: tk.PhotoImage | None = None
        self.show_language_screen()
        self.start_lan_server_if_needed()

    def tt(self, key: str) -> str:
        return t(self.lang, key)

    def text(self, key: str) -> str:
        return COPY.get(self.lang, COPY["en"]).get(key, key)

    def ui_text(self, ru: str, pl: str, en: str) -> str:
        return {"ru": ru, "pl": pl, "en": en}.get(self.lang, en)

    def reload_from_db(self) -> None:
        self.settings = self.db.get_settings()
        self.stats = self.db.get_stats()
        self.supports = self.db.get_supports()
        self.lang = str(self.settings.get("window_language") or getattr(self, "lang", "ru"))

    def refresh_current_screen(self) -> None:
        screen = self.current_screen
        if screen == "main":
            self.show_main_menu()
        elif screen == "modules":
            self.show_modules_screen()
        elif screen == "levels" and self.current_module:
            self.show_levels_screen(self.current_module)
        elif screen == "topics" and self.current_module:
            self.show_topics_screen(self.current_module, self.current_level)
        elif screen == "waiting":
            self.show_waiting_state()

    def on_root_configure(self, event: tk.Event) -> None:
        if event.widget is not self.root:
            return
        if self.geometry_after_id:
            self.root.after_cancel(self.geometry_after_id)
        self.geometry_after_id = self.root.after(800, self.save_window_geometry)

    def save_window_geometry(self) -> None:
        self.geometry_after_id = None
        if self.root.state() == "normal":
            self.settings = self.db.update_settings({"window_geometry": self.root.geometry()})

    def clear_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self.answer_entry = None
        self.task_image_ref = None
        self.feedback_var.set("")
        self.timer_var.set("")

    def start_page(self) -> tk.Frame:
        self.clear_content()
        page = ScrollFrame(self.content, bg=PALETTE["bg"])
        page.pack(fill="both", expand=True)
        return page.body

    def viewport_width(self) -> int:
        self.root.update_idletasks()
        return max(1, self.root.winfo_width())

    def page_padding(self) -> int:
        return 18 if self.viewport_width() < 900 else 34

    def text_wrap(self, *, reserve: int = 120, max_width: int = 940, min_width: int = 260) -> int:
        width = self.viewport_width() - (self.page_padding() * 2) - reserve
        return max(min_width, min(max_width, width))

    def card_columns(self, *, item_min_width: int = 320, max_columns: int = 3) -> int:
        available = max(1, self.viewport_width() - self.page_padding() * 2)
        return max(1, min(max_columns, available // item_min_width))

    def button(
        self,
        parent: tk.Misc,
        label: str,
        command: Callable[[], None],
        *,
        tone: str = "primary",
        fill: str | None = None,
    ) -> tk.Button:
        bg = PALETTE["accent"] if tone == "primary" else PALETTE["card"]
        fg = PALETTE["accent_text"] if tone == "primary" else PALETTE["text"]
        if tone == "danger":
            bg = PALETTE["bad"]
            fg = "white"
        button = tk.Button(
            parent,
            text=label,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=PALETTE["card_hover"],
            activeforeground=PALETTE["text"],
            relief="flat",
            padx=18,
            pady=11,
            font=("Segoe UI", 11, "bold"),
            wraplength=max(140, min(260, self.viewport_width() // 3)),
            justify="center",
        )
        if fill:
            button.pack(fill=fill)
        return button

    def build_header(self, parent: tk.Misc, title: str, *, back: Callable[[], None] | None = None) -> tk.Frame:
        header = tk.Frame(parent, bg=PALETTE["bg"])
        pad = self.page_padding()
        header.pack(fill="x", padx=pad, pady=(22, 16))
        header.grid_columnconfigure(1, weight=1)
        column = 0
        if back:
            self.button(header, "<", back, tone="quiet").grid(row=0, column=0, sticky="w", padx=(0, 12))
            column = 1
        tk.Label(
            header,
            text=title,
            bg=PALETTE["bg"],
            fg=PALETTE["text"],
            font=("Segoe UI", 26, "bold"),
            wraplength=self.text_wrap(reserve=220, max_width=760),
            justify="left",
        ).grid(row=0, column=column, sticky="w")
        badge = tk.Label(
            header,
            text=f"{self.text('coins')}: {self.stats.get('coins', 0)}",
            bg=PALETTE["panel"],
            fg=PALETTE["text"],
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        )
        if self.viewport_width() < 860:
            badge.grid(row=1, column=column, sticky="w", pady=(10, 0))
        else:
            badge.grid(row=0, column=2, sticky="e", padx=(12, 0))
        return header

    def show_language_screen(self) -> None:
        self.current_screen = "language"
        self.cancel_all_timers()
        page = self.start_page()
        wrap = tk.Frame(page, bg=PALETTE["bg"])
        wrap.pack(fill="both", expand=True, padx=self.page_padding(), pady=(42, 34))
        tk.Label(
            wrap,
            text=APP_TITLE,
            bg=PALETTE["bg"],
            fg=PALETTE["text"],
            font=("Segoe UI", 34, "bold"),
        ).pack(anchor="center")
        tk.Label(
            wrap,
            text=COPY.get(self.lang, COPY["en"])["language_intro"],
            bg=PALETTE["bg"],
            fg=PALETTE["muted"],
            font=("Segoe UI", 13),
            wraplength=self.text_wrap(reserve=80, max_width=720),
            justify="center",
        ).pack(anchor="center", pady=(8, 28))
        row = tk.Frame(wrap, bg=PALETTE["bg"])
        row.pack(fill="x", anchor="center")
        columns = self.card_columns(item_min_width=210, max_columns=3)
        for column in range(columns):
            row.grid_columnconfigure(column, weight=1, uniform="languages")
        for index, (code, (label, prompt)) in enumerate(LANGUAGES.items()):
            card = tk.Frame(row, bg=PALETTE["card"], padx=24, pady=22)
            card.grid(row=index // columns, column=index % columns, sticky="nsew", padx=8, pady=8)
            tk.Label(card, text=label, bg=PALETTE["card"], fg=PALETTE["text"], font=("Segoe UI", 18, "bold"), wraplength=220).pack()
            tk.Label(
                card,
                text=prompt,
                bg=PALETTE["card"],
                fg=PALETTE["muted"],
                font=("Segoe UI", 10),
                wraplength=220,
                justify="center",
            ).pack(pady=(6, 16))
            self.button(card, "OK", lambda selected=code: self.set_language(selected)).pack(fill="x")

    def set_language(self, lang: str) -> None:
        self.lang = lang if lang in LANGUAGES else "en"
        self.settings = self.db.update_settings({"window_language": self.lang})
        self.reload_from_db()
        self.show_main_menu()

    def show_main_menu(self) -> None:
        self.current_screen = "main"
        self.cancel_all_timers()
        self.current_module = None
        self.current_level = None
        self.current_topic = None
        self.current_task = None
        self.lesson_blocks = []
        page = self.start_page()
        self.build_header(page, self.text("main"))

        body = tk.Frame(page, bg=PALETTE["bg"])
        body.pack(fill="both", expand=True, padx=self.page_padding(), pady=(0, 34))
        narrow = self.viewport_width() < 980
        body.grid_columnconfigure(0, weight=1)
        if not narrow:
            body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        actions = tk.Frame(body, bg=PALETTE["panel"], padx=24, pady=24)
        actions.grid(row=0, column=0, sticky="nsew", padx=(0, 0 if narrow else 16), pady=(0, 16 if narrow else 0))
        for label, command, tone in [
            (self.text("play"), self.show_modules_screen, "primary"),
            (self.text("settings"), self.open_settings, "quiet"),
            (self.text("shop"), self.open_shop, "quiet"),
            (self.text("exit"), self.request_close, "danger"),
        ]:
            self.button(actions, label, command, tone=tone).pack(fill="x", pady=7)

        stats = tk.Frame(body, bg=PALETTE["surface"], padx=24, pady=24)
        stats.grid(row=1 if narrow else 0, column=0 if narrow else 1, sticky="nsew")
        snapshot = self.db.get_dashboard_snapshot()
        rows = [
            ("Program ID", snapshot["program_id"]),
            (self.text("modules"), snapshot["counts"]["modules"]),
            ("Topics", snapshot["counts"]["topics"]),
            ("Tasks", snapshot["counts"]["tasks"]),
            (self.text("coins"), self.stats.get("coins", 0)),
        ]
        for label, value in rows:
            tk.Label(stats, text=label, bg=PALETTE["surface"], fg=PALETTE["muted"], font=("Segoe UI", 10, "bold")).pack(
                anchor="w",
                pady=(0, 3),
            )
            tk.Label(stats, text=str(value), bg=PALETTE["surface"], fg=PALETTE["text"], font=("Segoe UI", 18, "bold")).pack(
                anchor="w",
                pady=(0, 15),
            )

    def show_modules_screen(self) -> None:
        self.current_screen = "modules"
        self.cancel_all_timers()
        self.current_task = None
        self.lesson_blocks = []
        modules = self.sync_modules_from_disk(refresh_start_screen=False)
        page = self.start_page()
        self.build_header(page, self.text("modules"), back=self.show_main_menu)
        toolbar = tk.Frame(page, bg=PALETTE["bg"])
        toolbar.pack(fill="x", padx=self.page_padding(), pady=(0, 14))
        self.button(toolbar, self.text("scan_modules"), self.show_modules_screen).pack(side="left")

        grid = tk.Frame(page, bg=PALETTE["bg"])
        grid.pack(fill="both", expand=True, padx=self.page_padding(), pady=(0, 30))
        if not modules:
            tk.Label(
                grid,
                text=self.text("modules_empty"),
                bg=PALETTE["bg"],
                fg=PALETTE["muted"],
                font=("Segoe UI", 14),
            ).pack(anchor="w", pady=18)
            return
        columns = self.card_columns(item_min_width=330, max_columns=3)
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="modules")
        for index, module in enumerate(modules):
            self.module_card(grid, module, index, columns)

    def module_card(self, parent: tk.Frame, module: dict[str, Any], index: int, columns: int) -> None:
        card = tk.Frame(parent, bg=PALETTE["card"], padx=18, pady=18)
        card.grid(row=index // columns, column=index % columns, sticky="nsew", padx=8, pady=8)
        title = localized_value(module, "title", self.lang) or str(module.get("slug"))
        desc = localized_value(module, "description", self.lang)
        wrap = self.text_wrap(reserve=120, max_width=320)
        tk.Label(card, text=title, bg=PALETTE["card"], fg=PALETTE["text"], font=("Segoe UI", 16, "bold"), wraplength=wrap).pack(
            anchor="w",
        )
        tk.Label(card, text=desc, bg=PALETTE["card"], fg=PALETTE["muted"], font=("Segoe UI", 10), wraplength=wrap, justify="left").pack(
            anchor="w",
            pady=(8, 18),
        )
        self.button(card, self.text("play"), lambda item=module: self.select_module(item)).pack(anchor="w")

    def select_module(self, module: dict[str, Any]) -> None:
        self.current_module = module
        self.current_level = None
        levels = self.db.list_levels(sphere_id=module["id"])
        if levels:
            self.show_levels_screen(module)
        else:
            self.show_topics_screen(module)

    def show_levels_screen(self, module: dict[str, Any]) -> None:
        self.current_screen = "levels"
        page = self.start_page()
        self.build_header(page, self.text("levels"), back=self.show_modules_screen)
        levels = self.db.list_levels(sphere_id=module["id"])
        self.simple_card_grid(page, levels, lambda level: localized_value(level, "title", self.lang), lambda level: self.show_topics_screen(module, level))

    def show_topics_screen(self, module: dict[str, Any], level: dict[str, Any] | None = None) -> None:
        self.current_screen = "topics"
        self.current_module = module
        self.current_level = level
        page = self.start_page()
        back = lambda: self.show_levels_screen(module) if self.db.list_levels(sphere_id=module["id"]) else self.show_modules_screen()
        self.build_header(page, self.text("topics"), back=back)
        topics = self.db.list_topics(sphere_id=module["id"], level_id=level["id"] if level else None)
        self.simple_card_grid(
            page,
            topics,
            lambda topic: localized_value(topic, "title", self.lang),
            self.select_topic,
            description=lambda topic: localized_value(topic, "description", self.lang),
        )

    def simple_card_grid(
        self,
        parent: tk.Misc,
        items: list[dict[str, Any]],
        title: Callable[[dict[str, Any]], str],
        command: Callable[[dict[str, Any]], None],
        *,
        description: Callable[[dict[str, Any]], str] | None = None,
    ) -> None:
        grid = tk.Frame(parent, bg=PALETTE["bg"])
        grid.pack(fill="both", expand=True, padx=self.page_padding(), pady=(0, 30))
        columns = self.card_columns(item_min_width=300, max_columns=3)
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="cards")
        for index, item in enumerate(items):
            card = tk.Frame(grid, bg=PALETTE["card"], padx=18, pady=18)
            card.grid(row=index // columns, column=index % columns, sticky="nsew", padx=8, pady=8)
            wrap = self.text_wrap(reserve=120, max_width=320)
            tk.Label(card, text=title(item), bg=PALETTE["card"], fg=PALETTE["text"], font=("Segoe UI", 15, "bold"), wraplength=wrap).pack(
                anchor="w",
            )
            if description:
                tk.Label(
                    card,
                    text=description(item),
                    bg=PALETTE["card"],
                    fg=PALETTE["muted"],
                    font=("Segoe UI", 10),
                    wraplength=wrap,
                    justify="left",
                ).pack(anchor="w", pady=(8, 18))
            self.button(card, self.text("start_now"), lambda current=item: command(current)).pack(anchor="w")

    def select_topic(self, topic: dict[str, Any]) -> None:
        if not self.db.tasks_for_topic(topic["id"]):
            messagebox.showinfo(APP_TITLE, self.text("no_tasks"), parent=self.root)
            return
        self.cancel_all_timers()
        self.current_topic = topic
        self.program_mode = str(topic.get("mode") or "child")
        self.stats["last_mode"] = f"{self.program_mode}:{topic.get('slug', '')}"
        self.reset_session_pause_uses()
        self.schedule_next_break()
        self.show_waiting_state()

    def sync_modules_from_disk(self, *, refresh_start_screen: bool = True) -> list[dict[str, Any]]:
        modules = self.db.sync_modules_from_disk()
        if refresh_start_screen and self.current_screen == "modules":
            self.show_modules_screen()
        return modules

    def show_waiting_state(self) -> None:
        self.current_screen = "waiting"
        self.current_task = None
        self.lesson_blocks = []
        page = self.start_page()
        title = localized_value(self.current_topic, "title", self.lang) if self.current_topic else self.text("waiting")
        self.build_header(page, self.text("waiting"), back=self.show_modules_screen)
        panel = tk.Frame(page, bg=PALETTE["panel"], padx=26, pady=24)
        panel.pack(fill="x", padx=self.page_padding(), pady=(8, 18))
        tk.Label(panel, text=self.text("selected_topic"), bg=PALETTE["panel"], fg=PALETTE["muted"], font=("Segoe UI", 10, "bold")).pack(
            anchor="w",
        )
        tk.Label(panel, text=title, bg=PALETTE["panel"], fg=PALETTE["text"], font=("Segoe UI", 22, "bold"), wraplength=self.text_wrap(max_width=860)).pack(
            anchor="w",
            pady=(6, 16),
        )
        tk.Label(panel, textvariable=self.timer_var, bg=PALETTE["panel"], fg=PALETTE["accent"], font=("Segoe UI", 16, "bold")).pack(
            anchor="w",
            pady=(0, 16),
        )
        row = tk.Frame(panel, bg=PALETTE["panel"])
        row.pack(anchor="w")
        for label, command, tone in [
            (self.text("start_now"), self.start_next_break, "primary"),
            (self.text("pause"), self.begin_manual_pause, "quiet"),
            (self.text("shop"), self.open_shop, "quiet"),
        ]:
            self.button(row, label, command, tone=tone).pack(side="left", padx=(0, 10), pady=(0, 8))
        self.update_waiting_timer()

    def update_waiting_timer(self) -> None:
        if self.current_screen != "waiting":
            return
        remaining = self.remaining_break_seconds()
        if remaining:
            minutes, seconds = divmod(remaining, 60)
            self.timer_var.set(f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_waiting_timer)
        else:
            self.timer_var.set("")

    def build_break_tasks(self) -> None:
        if not self.current_topic:
            self.current_break_tasks = []
            return
        pool = self.db.tasks_for_topic(self.current_topic["id"])
        random.shuffle(pool)
        tasks_per_break = max(1, safe_int(self.settings.get("tasks_per_break"), 2))
        if pool and len(pool) < tasks_per_break:
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
        self.cancel_break_timer()
        if not self.current_topic:
            self.show_main_menu()
            return
        if not self.current_break_tasks:
            self.build_break_tasks()
        if not self.current_break_tasks:
            self.show_waiting_state()
            return
        self.lesson_blocks = self.db.lesson_blocks_for_topic(self.current_topic["id"])
        self.lesson_index = 0
        self.current_index = 0
        if self.lesson_blocks:
            self.show_lesson_block(0)
        else:
            self.show_task(self.current_break_tasks[0])

    def show_lesson_block(self, index: int) -> None:
        self.cancel_lesson_timer()
        self.current_screen = "lesson"
        self.lesson_index = index
        self.current_task = None
        page = self.start_page()
        block = self.lesson_blocks[index]
        title = localized_value(block, "title", self.lang) or localized_value(self.current_topic, "title", self.lang)
        self.build_header(page, title, back=self.show_waiting_state)
        panel = tk.Frame(page, bg=PALETTE["panel"], padx=26, pady=24)
        panel.pack(fill="both", expand=True, padx=self.page_padding(), pady=(0, 34))
        tk.Label(
            panel,
            text=localized_value(block, "content", self.lang),
            bg=PALETTE["panel"],
            fg=PALETTE["text"],
            font=("Segoe UI", 15),
            wraplength=self.text_wrap(max_width=940),
            justify="left",
        ).pack(anchor="w", fill="x")
        tk.Label(panel, textvariable=self.timer_var, bg=PALETTE["panel"], fg=PALETTE["accent"], font=("Segoe UI", 16, "bold")).pack(
            anchor="w",
            pady=(18, 8),
        )
        tk.Label(panel, text=self.text("lesson_ready"), bg=PALETTE["panel"], fg=PALETTE["muted"], font=("Segoe UI", 11)).pack(
            anchor="w",
            pady=(0, 18),
        )
        self.button(panel, self.text("start_now"), self.advance_from_lesson).pack(anchor="w")
        self.lesson_seconds_left = max(5, safe_int(self.settings.get("lesson_seconds"), 45))
        self.tick_lesson_timer()

    def tick_lesson_timer(self) -> None:
        minutes, seconds = divmod(self.lesson_seconds_left, 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")
        if self.lesson_seconds_left <= 0:
            self.lesson_after_id = None
            self.feedback_var.set(self.text("lesson_done"))
            return
        self.lesson_seconds_left -= 1
        self.lesson_after_id = self.root.after(1000, self.tick_lesson_timer)

    def advance_from_lesson(self) -> None:
        self.cancel_lesson_timer()
        self.lesson_index += 1
        if self.lesson_index < len(self.lesson_blocks):
            self.show_lesson_block(self.lesson_index)
            return
        self.lesson_blocks = []
        if not self.current_break_tasks:
            self.show_waiting_state()
            return
        self.show_task(self.current_break_tasks[0])

    def show_task(self, task: dict[str, Any]) -> None:
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.current_screen = "task"
        self.current_task = task
        page = self.start_page()
        step = f"{self.tt('task')} {self.current_index + 1} {self.tt('of')} {len(self.current_break_tasks)}"
        self.build_header(page, step, back=self.show_waiting_state)
        panel = tk.Frame(page, bg=PALETTE["panel"], padx=26, pady=24)
        panel.pack(fill="both", expand=True, padx=self.page_padding(), pady=(0, 34))
        tk.Label(
            panel,
            text=localized_value(task, "title", self.lang),
            bg=PALETTE["panel"],
            fg=PALETTE["muted"],
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            panel,
            text=localized_value(task, "prompt", self.lang),
            bg=PALETTE["panel"],
            fg=PALETTE["text"],
            font=("Segoe UI", 20, "bold"),
            wraplength=self.text_wrap(max_width=940),
            justify="left",
        ).pack(anchor="w", fill="x", pady=(8, 22))
        tk.Label(panel, textvariable=self.feedback_var, bg=PALETTE["panel"], fg=PALETTE["muted"], font=("Segoe UI", 12, "bold")).pack(
            anchor="w",
            pady=(0, 14),
        )

        task_type = str(task.get("type") or task.get("task_type") or "input")
        if task_type == "choice":
            self.render_choice_task(panel, task)
        elif task_type == "reading":
            self.feedback_var.set(self.tt("read_aloud"))
            self.button(panel, self.tt("next"), lambda: self.check_answer(choice="__read__")).pack(anchor="w")
        elif task_type == "memory":
            self.feedback_var.set(self.tt("memory_read"))
            self.memory_seconds_left = max(10, safe_int(self.settings.get("lesson_seconds"), 45))
            self.memory_button = self.button(panel, self.tt("remembered"), lambda: self.check_answer(choice="__memory__"))
            self.memory_button.configure(state="disabled")
            self.memory_button.pack(anchor="w")
            tk.Label(panel, textvariable=self.timer_var, bg=PALETTE["panel"], fg=PALETTE["accent"], font=("Segoe UI", 16, "bold")).pack(
                anchor="w",
                pady=(14, 0),
            )
            self.tick_memory_timer()
        else:
            self.answer_entry = tk.Entry(
                panel,
                bg=PALETTE["surface"],
                fg=PALETTE["text"],
                insertbackground=PALETTE["text"],
                relief="flat",
                font=("Segoe UI", 16),
            )
            self.answer_entry.pack(fill="x", ipady=10, pady=(0, 12))
            self.answer_entry.bind("<Return>", lambda _event: self.check_answer())
            self.button(panel, self.tt("check"), self.check_answer).pack(anchor="w")
            tk.Label(panel, text=self.text("answer_hint"), bg=PALETTE["panel"], fg=PALETTE["muted"], font=("Segoe UI", 10)).pack(
                anchor="w",
                pady=(10, 0),
            )
            self.answer_entry.focus_set()

    def render_choice_task(self, parent: tk.Frame, task: dict[str, Any]) -> None:
        grid = tk.Frame(parent, bg=PALETTE["panel"])
        grid.pack(fill="x")
        options = self.choice_options_for_task(task)
        columns = 1 if self.viewport_width() < 980 or any(len(option) > 28 for option in options) else 2
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="choices")
        for index, option in enumerate(options):
            self.button(grid, option, lambda value=option: self.check_answer(choice=value), tone="quiet").grid(
                row=index // columns,
                column=index % columns,
                sticky="ew",
                padx=6,
                pady=6,
            )

    def choice_options_for_task(self, task: dict[str, Any]) -> list[str]:
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

    def tick_memory_timer(self) -> None:
        minutes, seconds = divmod(self.memory_seconds_left, 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")
        if self.memory_seconds_left <= 0:
            self.memory_after_id = None
            if self.memory_button:
                self.memory_button.configure(state="normal")
            return
        self.memory_seconds_left -= 1
        self.memory_after_id = self.root.after(1000, self.tick_memory_timer)

    def check_answer(self, choice: str | None = None) -> None:
        if not self.current_task:
            return
        given = choice if choice is not None else (self.answer_entry.get().strip() if self.answer_entry else "")
        if self.db.answer_matches(self.current_task, given):
            self.stats["correct"] += 1
            self.stats["coins"] += 5
            self.persist_stats()
            self.feedback_var.set(self.tt("correct"))
            self.root.after(500, self.advance_task)
        else:
            self.stats["wrong"] += 1
            self.stats["coins"] = max(0, self.stats["coins"] - 1)
            self.persist_stats()
            self.feedback_var.set(self.tt("wrong"))

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
            self.schedule_next_break()
            self.show_waiting_state()
            self.status_var.set(self.text("completed"))
            return
        self.show_task(self.current_break_tasks[self.current_index])

    def persist_stats(self) -> None:
        self.stats["last_activity"] = datetime.now().replace(microsecond=0).isoformat()
        self.db.save_stats(self.stats)
        self.reload_from_db()
        self.update_shop_balance()

    def pause_upgrade_bounds(self, level: int | None = None) -> tuple[int, int]:
        level = max(0, min(4, safe_int(level if level is not None else self.settings.get("pause_upgrade_level"), 0)))
        return [(2, 4), (3, 4), (4, 5), (5, 6), (5, 7)][level]

    def pause_upgrade_cost(self, level: int | None = None) -> int | None:
        level = max(0, min(4, safe_int(level if level is not None else self.settings.get("pause_upgrade_level"), 0)))
        costs = [300, 450, 550, 700]
        return costs[level] if level < len(costs) else None

    def manual_pause_minutes(self) -> int:
        pause_min, pause_max = self.pause_upgrade_bounds()
        return min(pause_max, max(pause_min, safe_int(self.settings.get("manual_pause_minutes"), pause_min)))

    def manual_pause_uses_limit(self) -> int:
        return min(2, max(1, safe_int(self.settings.get("manual_pause_uses"), 1)))

    def extra_pause_tokens(self) -> int:
        return max(0, safe_int(self.settings.get("shop_extra_pause_tokens"), 0))

    def reset_session_pause_uses(self) -> None:
        self.session_pause_uses_remaining = self.manual_pause_uses_limit()

    def remaining_pause_uses(self) -> int:
        if not self.current_topic:
            return 0
        return max(0, self.session_pause_uses_remaining) + self.extra_pause_tokens()

    def consume_pause_use(self) -> None:
        if self.session_pause_uses_remaining > 0:
            self.session_pause_uses_remaining -= 1
        elif self.extra_pause_tokens() > 0:
            self.settings = self.db.update_settings({"shop_extra_pause_tokens": max(0, self.extra_pause_tokens() - 1)})
            self.reload_from_db()

    def begin_manual_pause(self) -> None:
        if not self.current_topic or self.manual_pause_state is not None:
            return
        if self.remaining_pause_uses() <= 0:
            messagebox.showinfo(APP_TITLE, self.text("no_pauses"), parent=self.root)
            return
        if self.current_task:
            state = {
                "kind": "task",
                "task": dict(self.current_task),
                "current_break_tasks": [dict(item) for item in self.current_break_tasks],
                "current_index": self.current_index,
                "memory_seconds_left": self.memory_seconds_left,
            }
        elif self.lesson_blocks:
            state = {
                "kind": "lesson",
                "lesson_blocks": [dict(item) for item in self.lesson_blocks],
                "lesson_index": self.lesson_index,
                "current_break_tasks": [dict(item) for item in self.current_break_tasks],
                "current_index": self.current_index,
                "lesson_seconds_left": self.lesson_seconds_left,
            }
        else:
            state = {"kind": "waiting", "remaining_break_seconds": self.remaining_break_seconds()}
        self.consume_pause_use()
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.cancel_break_timer()
        self.current_task = None
        self.lesson_blocks = []
        self.manual_pause_state = state
        self.manual_pause_seconds_left = self.manual_pause_minutes() * 60
        self.show_manual_pause_screen()
        self.tick_manual_pause_timer()

    def show_manual_pause_screen(self) -> None:
        self.current_screen = "pause"
        page = self.start_page()
        self.build_header(page, self.text("pause"))
        panel = tk.Frame(page, bg=PALETTE["panel"], padx=26, pady=24)
        panel.pack(fill="x", padx=self.page_padding(), pady=(10, 30))
        tk.Label(panel, text=self.text("pause_left"), bg=PALETTE["panel"], fg=PALETTE["text"], font=("Segoe UI", 20, "bold")).pack(
            anchor="w",
        )
        tk.Label(panel, textvariable=self.timer_var, bg=PALETTE["panel"], fg=PALETTE["accent"], font=("Segoe UI", 22, "bold")).pack(
            anchor="w",
            pady=18,
        )
        self.button(panel, self.text("resume"), self.resume_from_manual_pause).pack(anchor="w")

    def tick_manual_pause_timer(self) -> None:
        minutes, seconds = divmod(max(0, self.manual_pause_seconds_left), 60)
        self.timer_var.set(f"{minutes:02d}:{seconds:02d}")
        if self.manual_pause_seconds_left <= 0:
            self.manual_pause_after_id = None
            self.resume_from_manual_pause()
            return
        self.manual_pause_seconds_left -= 1
        self.manual_pause_after_id = self.root.after(1000, self.tick_manual_pause_timer)

    def resume_from_manual_pause(self) -> None:
        state = dict(self.manual_pause_state or {})
        self.cancel_manual_pause_timer()
        self.manual_pause_state = None
        self.manual_pause_seconds_left = 0
        kind = str(state.get("kind") or "waiting")
        if kind == "lesson":
            self.current_break_tasks = [dict(item) for item in state.get("current_break_tasks") or []]
            self.current_index = safe_int(state.get("current_index"), 0)
            self.lesson_blocks = [dict(item) for item in state.get("lesson_blocks") or []]
            self.lesson_index = min(max(0, safe_int(state.get("lesson_index"), 0)), max(0, len(self.lesson_blocks) - 1))
            if self.lesson_blocks:
                self.show_lesson_block(self.lesson_index)
                self.lesson_seconds_left = max(0, safe_int(state.get("lesson_seconds_left"), self.lesson_seconds_left))
            else:
                self.show_waiting_state()
                self.schedule_next_break()
        elif kind == "task":
            self.current_break_tasks = [dict(item) for item in state.get("current_break_tasks") or []]
            self.current_index = safe_int(state.get("current_index"), 0)
            task = state.get("task")
            if isinstance(task, dict):
                self.show_task(task)
                self.memory_seconds_left = max(0, safe_int(state.get("memory_seconds_left"), self.memory_seconds_left))
            else:
                self.show_waiting_state()
                self.schedule_next_break()
        else:
            remaining = max(1, safe_int(state.get("remaining_break_seconds"), safe_int(self.settings.get("break_seconds"), 300)))
            self.schedule_next_break(delay_seconds=remaining, consume_pending_bonus=False)
            self.show_waiting_state()

    def open_settings(self) -> None:
        if self.parent_panel_window and self.parent_panel_window.winfo_exists():
            self.parent_panel_window.lift()
            return
        self.parent_panel_window = ParentPanelV23(self, initial_tab="settings")

    def open_shop(self) -> None:
        if self.shop_window and self.shop_window.winfo_exists():
            self.refresh_shop_window()
            self.shop_window.lift()
            return
        self.shop_window = tk.Toplevel(self.root)
        self.shop_window.title(self.text("shop"))
        self.shop_window.configure(bg=PALETTE["bg"])
        self.shop_window.geometry("820x520")
        self.shop_window.minsize(620, 420)
        self.shop_window.protocol("WM_DELETE_WINDOW", self.close_shop_window)
        header = tk.Frame(self.shop_window, bg=PALETTE["bg"])
        header.pack(fill="x", padx=24, pady=(22, 12))
        tk.Label(header, text=self.text("shop"), bg=PALETTE["bg"], fg=PALETTE["text"], font=("Segoe UI", 24, "bold")).pack(
            side="left",
        )
        tk.Label(header, textvariable=self.shop_balance_var, bg=PALETTE["panel"], fg=PALETTE["text"], padx=14, pady=8).pack(
            side="right",
        )
        shop_scroll = ScrollFrame(self.shop_window, bg=PALETTE["bg"])
        shop_scroll.pack(fill="both", expand=True, padx=24, pady=10)
        self.shop_content = shop_scroll.body
        tk.Label(
            self.shop_window,
            textvariable=self.shop_status_var,
            bg=PALETTE["bg"],
            fg=PALETTE["muted"],
            font=("Segoe UI", 10),
        ).pack(fill="x", padx=24, pady=(0, 18))
        self.refresh_shop_window()

    def close_shop_window(self) -> None:
        if self.shop_window and self.shop_window.winfo_exists():
            self.shop_window.destroy()
        self.shop_window = None
        self.shop_content = None

    def refresh_shop_window(self) -> None:
        if not self.shop_content:
            return
        for child in self.shop_content.winfo_children():
            child.destroy()
        self.update_shop_balance()
        pending_bonus = max(0, safe_int(self.settings.get("shop_pending_delay_bonus_seconds"), 0))
        extra_pauses = self.extra_pause_tokens()
        upgrade_level = max(0, safe_int(self.settings.get("pause_upgrade_level"), 0))
        pause_min, pause_max = self.pause_upgrade_bounds()
        cards = [
            (self.text("extra_time"), f"+{pending_bonus // 60:02d}:{pending_bonus % 60:02d}", "100", self.buy_shop_delay_bonus),
            (self.text("extra_pause"), str(extra_pauses), "250", self.buy_shop_extra_pause),
            (
                self.text("pause_upgrade"),
                f"{upgrade_level}/4 · {pause_min}-{pause_max} min",
                str(self.pause_upgrade_cost(upgrade_level) or "max"),
                self.buy_shop_pause_upgrade,
            ),
        ]
        columns = 1 if self.shop_window and self.shop_window.winfo_width() < 760 else 3
        for col in range(columns):
            self.shop_content.grid_columnconfigure(col, weight=1, uniform="shop")
        for index, (title, status, price, command) in enumerate(cards):
            card = tk.Frame(self.shop_content, bg=PALETTE["card"], padx=18, pady=18)
            card.grid(row=index // columns, column=index % columns, sticky="nsew", padx=8, pady=8)
            tk.Label(card, text=title, bg=PALETTE["card"], fg=PALETTE["text"], font=("Segoe UI", 15, "bold"), wraplength=240).pack(
                anchor="w",
            )
            tk.Label(card, text=status, bg=PALETTE["card"], fg=PALETTE["muted"], font=("Segoe UI", 12)).pack(anchor="w", pady=(10, 18))
            label = f"{self.text('buy')} · {price}"
            self.button(card, label, command).pack(anchor="w")

    def update_shop_balance(self) -> None:
        self.shop_balance_var.set(f"{self.text('coins')}: {self.stats.get('coins', 0)}")

    def spend_coins(self, amount: int) -> bool:
        if int(self.stats.get("coins", 0)) < amount:
            self.shop_status_var.set(self.text("not_enough"))
            return False
        self.stats["coins"] = max(0, int(self.stats.get("coins", 0)) - amount)
        self.persist_stats()
        return True

    def buy_shop_delay_bonus(self) -> None:
        bonus_seconds = random.randint(120, 240)
        if not self.spend_coins(100):
            return
        waiting_now = self.current_topic and self.break_after_id is not None and not self.current_task and not self.lesson_blocks
        if waiting_now:
            total_delay = max(1, self.remaining_break_seconds()) + bonus_seconds
            self.schedule_next_break(delay_seconds=total_delay, consume_pending_bonus=False)
        else:
            pending_bonus = max(0, safe_int(self.settings.get("shop_pending_delay_bonus_seconds"), 0))
            self.settings = self.db.update_settings({"shop_pending_delay_bonus_seconds": pending_bonus + bonus_seconds})
            self.reload_from_db()
        self.refresh_shop_window()

    def buy_shop_extra_pause(self) -> None:
        if not self.spend_coins(250):
            return
        self.settings = self.db.update_settings({"shop_extra_pause_tokens": self.extra_pause_tokens() + 1})
        self.reload_from_db()
        self.refresh_shop_window()

    def buy_shop_pause_upgrade(self) -> None:
        current_level = max(0, safe_int(self.settings.get("pause_upgrade_level"), 0))
        cost = self.pause_upgrade_cost(current_level)
        if cost is None:
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
        self.refresh_shop_window()

    def start_lan_server_if_needed(self, manual: bool = False) -> bool:
        if self.lan_server and self.lan_url:
            return True
        if not manual and not self.settings.get("lan_admin_autostart"):
            return False
        if not self.settings.get("lan_admin_enabled", True):
            return False
        self.lan_server_manual_requested = bool(manual)
        try:
            self.lan_server = LanAdminServer(self)
            self.lan_url = self.lan_server.start()
            return bool(self.lan_url)
        except Exception as exc:
            self.lan_server = None
            self.lan_url = ""
            if manual:
                messagebox.showerror(APP_TITLE, str(exc), parent=self.root)
            return False

    def stop_lan_server(self) -> None:
        if self.lan_server:
            self.lan_server.stop()
        self.lan_server = None
        self.lan_url = ""

    def remaining_break_seconds(self) -> int:
        if self.break_deadline_ts is None:
            return 0
        return max(0, int(round(self.break_deadline_ts - time.monotonic())))

    def cancel_break_timer(self) -> None:
        if self.break_after_id:
            self.root.after_cancel(self.break_after_id)
            self.break_after_id = None
        self.break_deadline_ts = None

    def cancel_lesson_timer(self) -> None:
        if self.lesson_after_id:
            self.root.after_cancel(self.lesson_after_id)
            self.lesson_after_id = None

    def cancel_memory_timer(self) -> None:
        if self.memory_after_id:
            self.root.after_cancel(self.memory_after_id)
            self.memory_after_id = None

    def cancel_manual_pause_timer(self) -> None:
        if self.manual_pause_after_id:
            self.root.after_cancel(self.manual_pause_after_id)
            self.manual_pause_after_id = None

    def cancel_all_timers(self) -> None:
        self.cancel_break_timer()
        self.cancel_lesson_timer()
        self.cancel_memory_timer()
        self.cancel_manual_pause_timer()

    def queue_remote_sync(self, delay_ms: int = 0) -> None:
        return

    def start_remote_sync_loop(self) -> None:
        return

    def request_close(self) -> None:
        self.cancel_all_timers()
        if self.geometry_after_id:
            self.root.after_cancel(self.geometry_after_id)
            self.geometry_after_id = None
        self.stop_lan_server()
        self.close_shop_window()
        if self.parent_panel_window and self.parent_panel_window.winfo_exists():
            self.parent_panel_window.destroy()
        self.root.destroy()


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    root = tk.Tk()
    MinecraftCoachV23(root)
    root.mainloop()
