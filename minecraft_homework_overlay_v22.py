
import json, os, sqlite3, random, shutil, time, uuid
import tkinter as tk
from tkinter import messagebox

APP_TITLE = "Minecraft Coach v22"
BG = "#07133a"
CARD = "#14265f"
CARD2 = "#0c1d54"
ACCENT = "#edc34b"
TEXT = "#f6f7fb"
MUTED = "#c5d0f0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "coach_data")
DB_PATH = os.path.join(DATA_DIR, "coach.db")
SEED_DB = os.path.join(BASE_DIR, "coach_seed_v22.db")

I18N = {
    "ru": {
        "parent_panel": "Родительская панель",
        "overview": "Обзор",
        "tasks": "Задания",
        "supports": "Подсказки",
        "settings": "Настройки",
        "close": "Закрыть",
        "who": "Кто будет учиться?",
        "child_program": "Детская программа",
        "child_desc": "Классы 1–4\nматематика, чтение, слова",
        "adult_program": "Взрослая программа",
        "adult_desc": "электрика: база, защита,\nкабели, двигатели и практика",
        "memory_mode": "Режим запоминания",
        "memory_desc": "формулы, правила,\nопределения и схемы",
        "choose": "Выбрать",
        "shop": "Магазин / Sklep",
        "save": "Сохранить",
        "delete": "Удалить",
        "filter_all": "all",
        "grade_theme": "Класс/Тема",
        "language": "Язык",
        "coins": "Монеты",
        "program_id": "ID программы",
        "total_tasks": "Всего заданий",
    },
    "pl": {
        "parent_panel": "Panel rodzica",
        "overview": "Przegląd",
        "tasks": "Zadania",
        "supports": "Podpowiedzi",
        "settings": "Ustawienia",
        "close": "Zamknij",
        "who": "Kto będzie się uczyć?",
        "child_program": "Program dziecięcy",
        "child_desc": "Klasy 1–4\nmatematyka, czytanie, słowa",
        "adult_program": "Program dla dorosłych",
        "adult_desc": "elektryka: podstawy, ochrona,\nkable, silniki i praktyka",
        "memory_mode": "Tryb zapamiętywania",
        "memory_desc": "wzory, zasady,\ndefinicje i schematy",
        "choose": "Wybierz",
        "shop": "Sklep / Shop",
        "save": "Zapisz",
        "delete": "Usuń",
        "filter_all": "all",
        "grade_theme": "Klasa/Temat",
        "language": "Język",
        "coins": "Monety",
        "program_id": "ID programu",
        "total_tasks": "Liczba zadań",
    },
    "en": {
        "parent_panel": "Parent Panel",
        "overview": "Overview",
        "tasks": "Tasks",
        "supports": "Hints",
        "settings": "Settings",
        "close": "Close",
        "who": "Who will study?",
        "child_program": "Kids program",
        "child_desc": "Grades 1–4\nmath, reading, words",
        "adult_program": "Adult program",
        "adult_desc": "electricity: basics, safety,\ncables, motors and practice",
        "memory_mode": "Memory mode",
        "memory_desc": "formulas, rules,\ndefinitions and diagrams",
        "choose": "Choose",
        "shop": "Shop",
        "save": "Save",
        "delete": "Delete",
        "filter_all": "all",
        "grade_theme": "Grade/Theme",
        "language": "Language",
        "coins": "Coins",
        "program_id": "Program ID",
        "total_tasks": "Total tasks",
    },
}

def ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        if os.path.exists(SEED_DB):
            shutil.copyfile(SEED_DB, DB_PATH)
        else:
            raise FileNotFoundError("coach_seed_v22.db not found next to the script")

class DB:
    def __init__(self, path):
        self.path = path
    def conn(self):
        return sqlite3.connect(self.path)
    def get_setting(self, key, default=""):
        with self.conn() as con:
            row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row[0] if row else default
    def set_setting(self, key, value):
        with self.conn() as con:
            con.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
    def get_stats(self):
        with self.conn() as con:
            row = con.execute("SELECT coins, solved_total, wrong_total FROM stats WHERE id=1").fetchone()
            return {"coins": row[0], "solved": row[1], "wrong": row[2]}
    def tasks(self, mode="all", grade="all"):
        q = "SELECT id, mode, grade_theme, theme, type, title_ru, title_pl, title_en, prompt_ru, prompt_pl, prompt_en, answer, options_json, hint_ru, hint_pl, hint_en FROM tasks WHERE 1=1"
        args = []
        if mode != "all":
            q += " AND mode=?"
            args.append(mode)
        if grade != "all":
            q += " AND grade_theme=?"
            args.append(grade)
        q += " ORDER BY id"
        with self.conn() as con:
            rows = con.execute(q, args).fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r[0], "mode": r[1], "grade_theme": r[2], "theme": r[3], "type": r[4],
                "title_ru": r[5], "title_pl": r[6], "title_en": r[7],
                "prompt_ru": r[8], "prompt_pl": r[9], "prompt_en": r[10],
                "answer": r[11], "options_json": r[12] or "[]",
                "hint_ru": r[13], "hint_pl": r[14], "hint_en": r[15],
            })
        return out
    def upsert_task(self, item):
        with self.conn() as con:
            con.execute("""
            INSERT INTO tasks(id,mode,grade_theme,theme,type,title_ru,title_pl,title_en,prompt_ru,prompt_pl,prompt_en,answer,options_json,hint_ru,hint_pl,hint_en)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                mode=excluded.mode, grade_theme=excluded.grade_theme, theme=excluded.theme, type=excluded.type,
                title_ru=excluded.title_ru, title_pl=excluded.title_pl, title_en=excluded.title_en,
                prompt_ru=excluded.prompt_ru, prompt_pl=excluded.prompt_pl, prompt_en=excluded.prompt_en,
                answer=excluded.answer, options_json=excluded.options_json,
                hint_ru=excluded.hint_ru, hint_pl=excluded.hint_pl, hint_en=excluded.hint_en
            """, (
                item["id"], item["mode"], item["grade_theme"], item["theme"], item["type"],
                item["title_ru"], item["title_pl"], item["title_en"],
                item["prompt_ru"], item["prompt_pl"], item["prompt_en"],
                item["answer"], item["options_json"], item["hint_ru"], item["hint_pl"], item["hint_en"]
            ))
    def delete_task(self, task_id):
        with self.conn() as con:
            con.execute("DELETE FROM tasks WHERE id=?", (task_id,))

class App:
    def __init__(self, root):
        self.root = root
        self.db = DB(DB_PATH)
        self.lang = self.db.get_setting("language", "ru")
        self.t = I18N[self.lang]
        self.root.title(APP_TITLE)
        self.root.geometry("1180x760")
        self.root.configure(bg=BG)
        self.build_start()

    def _(self, key):
        return I18N[self.lang].get(key, key)

    def set_lang(self, lang):
        self.lang = lang
        self.db.set_setting("language", lang)
        self.t = I18N[self.lang]
        for w in self.root.winfo_children():
            w.destroy()
        self.build_start()

    def build_topbar(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", padx=24, pady=(16, 8))
        tk.Label(bar, text=APP_TITLE, bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(side="left")
        lang_frame = tk.Frame(bar, bg=BG)
        lang_frame.pack(side="right")
        for code in ("ru", "pl", "en"):
            tk.Button(lang_frame, text=code.upper(), bg=ACCENT if code == self.lang else CARD,
                      fg="black" if code == self.lang else TEXT, bd=0, padx=10, pady=6,
                      command=lambda c=code: self.set_lang(c)).pack(side="left", padx=4)

    def build_start(self):
        self.root.configure(bg=BG)
        self.build_topbar(self.root)
        outer = tk.Frame(self.root, bg="#182b66")
        outer.pack(fill="both", expand=True, padx=24, pady=16)

        title = tk.Label(outer, text=self._("who"), bg="#182b66", fg=TEXT, font=("Segoe UI", 28, "bold"))
        title.pack(pady=(22, 18))

        row = tk.Frame(outer, bg="#182b66")
        row.pack(pady=14)

        cards = [
            (self._("child_program"), self._("child_desc"), lambda: self.launch_mode("child")),
            (self._("adult_program"), self._("adult_desc"), lambda: self.launch_mode("adult")),
            (self._("memory_mode"), self._("memory_desc"), lambda: self.launch_mode("memorize")),
        ]
        for name, desc, cmd in cards:
            c = tk.Frame(row, bg=CARD, width=260, height=250, highlightbackground="#4360b8", highlightthickness=1)
            c.pack(side="left", padx=16)
            c.pack_propagate(False)
            tk.Label(c, text=name, bg=CARD, fg=TEXT, font=("Segoe UI", 19, "bold"), wraplength=220, justify="center").pack(pady=(34, 18), padx=14)
            tk.Label(c, text=desc, bg=CARD, fg=MUTED, font=("Segoe UI", 13), wraplength=210, justify="center").pack(padx=16)
            tk.Button(c, text=self._("choose"), bg=ACCENT, fg="black", bd=0, padx=28, pady=14,
                      font=("Segoe UI", 14, "bold"), command=cmd).pack(pady=28)

        bottom = tk.Frame(outer, bg="#182b66")
        bottom.pack(fill="x", side="bottom", pady=18, padx=16)
        tk.Button(bottom, text=self._("shop"), bg=CARD, fg=TEXT, bd=0, padx=20, pady=10, command=self.open_shop).pack(side="left")
        tk.Button(bottom, text=self._("parent_panel"), bg=CARD, fg=TEXT, bd=0, padx=20, pady=10, command=self.open_parent).pack(side="right")

    def launch_mode(self, mode):
        self.open_parent(default_tab="overview", focus_mode=mode)

    def open_shop(self):
        win = tk.Toplevel(self.root)
        win.title(self._("shop"))
        win.geometry("980x620")
        win.configure(bg=BG)
        tk.Label(win, text=self._("shop"), bg=BG, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(pady=24)
        grid = tk.Frame(win, bg=BG)
        grid.pack(padx=18, pady=10, anchor="w")
        prices = [25, 50, 75, 100, 125, 150]
        for i, p in enumerate(prices):
            card = tk.Frame(grid, bg=CARD, width=160, height=170, highlightbackground="#4560a6", highlightthickness=1)
            card.grid(row=i//3, column=i%3, padx=16, pady=16)
            card.grid_propagate(False)
            tk.Label(card, text="?", bg=CARD, fg=TEXT, font=("Segoe UI", 36, "bold")).pack(pady=(22, 8))
            tk.Label(card, text="Скоро\nSoon", bg=CARD, fg=MUTED, font=("Segoe UI", 12), justify="center").pack()
            tk.Label(card, text=str(p), bg=CARD, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(side="bottom", pady=12)

    def open_parent(self, default_tab="overview", focus_mode="all"):
        win = tk.Toplevel(self.root)
        win.title(self._("parent_panel"))
        win.geometry("1260x820")
        win.configure(bg=BG)

        hdr = tk.Frame(win, bg=BG)
        hdr.pack(fill="x", padx=18, pady=16)
        tk.Label(hdr, text=self._("parent_panel"), bg=BG, fg=TEXT, font=("Segoe UI", 24, "bold")).pack(side="left")
        tk.Button(hdr, text=self._("close"), bg=ACCENT, fg="black", bd=0, padx=18, pady=10, command=win.destroy).pack(side="right")

        body = tk.Frame(win, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=(0,18))

        sidebar = tk.Frame(body, bg=CARD, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        content = tk.Frame(body, bg=CARD2)
        content.pack(side="left", fill="both", expand=True)

        state = {"tab": default_tab}

        def show_tab(name):
            state["tab"] = name
            for child in content.winfo_children():
                child.destroy()
            for key, btn in nav_buttons.items():
                btn.configure(bg="#4e79ea" if key == name else CARD2)
            if name == "overview":
                self.parent_overview(content, focus_mode)
            elif name == "tasks":
                self.parent_tasks(content, focus_mode)
            elif name == "settings":
                self.parent_settings(content)
            else:
                self.parent_placeholder(content, name)

        nav_buttons = {}
        for key in ("overview", "tasks", "supports", "settings"):
            btn = tk.Button(sidebar, text=self._(key), bg=CARD2, fg=TEXT, bd=0, padx=20, pady=22,
                            font=("Segoe UI", 14, "bold"), anchor="w", command=lambda k=key: show_tab(k))
            btn.pack(fill="x", pady=4, padx=10)
            nav_buttons[key] = btn

        show_tab(default_tab)

    def parent_placeholder(self, parent, key):
        tk.Label(parent, text=self._(key), bg=CARD2, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(anchor="nw", padx=24, pady=24)
        tk.Label(parent, text="Section under construction", bg=CARD2, fg=MUTED, font=("Segoe UI", 14)).pack(anchor="nw", padx=24)

    def parent_overview(self, parent, focus_mode):
        stats = self.db.get_stats()
        tasks = self.db.tasks(mode=focus_mode if focus_mode != "all" else "all")
        pid = self.db.get_setting("program_id", "")
        tk.Label(parent, text=self._("overview"), bg=CARD2, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(anchor="nw", padx=24, pady=22)
        cards = tk.Frame(parent, bg=CARD2)
        cards.pack(anchor="nw", padx=24, pady=8)
        for title, value in [
            (self._("program_id"), pid),
            (self._("coins"), str(stats["coins"])),
            (self._("total_tasks"), str(len(tasks))),
        ]:
            box = tk.Frame(cards, bg=CARD, width=260, height=110, highlightbackground="#4560a6", highlightthickness=1)
            box.pack(side="left", padx=10)
            box.pack_propagate(False)
            tk.Label(box, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 13)).pack(anchor="w", padx=18, pady=(18,6))
            tk.Label(box, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 22, "bold"), wraplength=220, justify="left").pack(anchor="w", padx=18)

    def parent_tasks(self, parent, focus_mode):
        tk.Label(parent, text=self._("tasks"), bg=CARD2, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(anchor="nw", padx=24, pady=(20,8))
        top = tk.Frame(parent, bg=CARD2)
        top.pack(fill="x", padx=24, pady=(0,10))

        mode_var = tk.StringVar(value=focus_mode if focus_mode != "all" else "all")
        grade_var = tk.StringVar(value="all")
        tk.Label(top, text="Mode", bg=CARD2, fg=TEXT).pack(side="left")
        mode_menu = tk.OptionMenu(top, mode_var, "all", "child", "adult", "memorize")
        mode_menu.config(width=8)
        mode_menu.pack(side="left", padx=(6,18))
        tk.Label(top, text=self._("grade_theme"), bg=CARD2, fg=TEXT).pack(side="left")
        grade_entry = tk.Entry(top, textvariable=grade_var, width=10)
        grade_entry.pack(side="left", padx=(6,10))

        main = tk.Frame(parent, bg=CARD2)
        main.pack(fill="both", expand=True, padx=24, pady=8)

        left = tk.Frame(main, bg=CARD)
        left.pack(side="left", fill="y")
        right = tk.Frame(main, bg=CARD)
        right.pack(side="left", fill="both", expand=True, padx=(18,0))

        listbox = tk.Listbox(left, width=45, height=28, bg="#19306e", fg=TEXT, selectbackground="#4e79ea",
                             font=("Consolas", 11), bd=0, highlightthickness=0)
        listbox.pack(fill="both", expand=True, padx=2, pady=2)

        fields = {}
        form = tk.Frame(right, bg=CARD)
        form.pack(fill="both", expand=True, padx=18, pady=18)

        field_names = [
            ("id", "ID"), ("mode", "Mode"), ("grade_theme", "Grade"), ("theme", "Theme"), ("type", "Type"),
            ("title_ru", "Title RU"), ("title_pl", "Title PL"), ("title_en", "Title EN"),
            ("prompt_ru", "Prompt RU"), ("prompt_pl", "Prompt PL"), ("prompt_en", "Prompt EN"),
            ("answer", "Answer"), ("options_json", "Options JSON"), ("hint_ru", "Hint RU"),
        ]
        row = 0
        for key, label in field_names:
            tk.Label(form, text=label, bg=CARD, fg=TEXT, font=("Segoe UI", 11)).grid(row=row, column=0, sticky="w", padx=(0,12), pady=6)
            if key.startswith("prompt") or key == "options_json":
                widget = tk.Text(form, width=60, height=4, bg="#0b1b4b", fg=TEXT, insertbackground=TEXT, bd=0)
                widget.grid(row=row, column=1, sticky="ew", pady=6)
            else:
                widget = tk.Entry(form, width=70, bg="#0b1b4b", fg=TEXT, insertbackground=TEXT, bd=0)
                widget.grid(row=row, column=1, sticky="ew", pady=6)
            fields[key] = widget
            row += 1

        form.grid_columnconfigure(1, weight=1)

        def current_items():
            return self.db.tasks(mode_var.get(), grade_var.get().strip() or "all")

        data = []

        def refresh():
            nonlocal data
            data = current_items()
            listbox.delete(0, "end")
            for item in data:
                title = item.get(f"title_{self.lang}") or item["title_ru"] or item["id"]
                listbox.insert("end", f'{item["id"]}  [{item["mode"]}/{item["grade_theme"]}]  {title}')

        def load_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            item = data[sel[0]]
            for key, w in fields.items():
                val = item.get(key, "")
                if isinstance(w, tk.Text):
                    w.delete("1.0", "end")
                    w.insert("1.0", val)
                else:
                    w.delete(0, "end")
                    w.insert(0, val)

        def extract():
            item = {}
            for key, w in fields.items():
                if isinstance(w, tk.Text):
                    item[key] = w.get("1.0", "end").strip()
                else:
                    item[key] = w.get().strip()
            if not item["id"]:
                item["id"] = "USR-" + uuid.uuid4().hex[:8].upper()
            item.setdefault("title_en","")
            item.setdefault("prompt_en","")
            item.setdefault("hint_pl","")
            item.setdefault("hint_en","")
            return item

        listbox.bind("<<ListboxSelect>>", load_selected)
        tk.Button(top, text=self._("save"), bg="#4e79ea", fg="white", bd=0, padx=12, pady=8,
                  command=lambda: (self.db.upsert_task(extract()), refresh())).pack(side="left", padx=8)
        tk.Button(form, text=self._("save"), bg=ACCENT, fg="black", bd=0, padx=18, pady=12,
                  command=lambda: (self.db.upsert_task(extract()), refresh())).grid(row=row, column=0, pady=16, sticky="w")
        tk.Button(form, text=self._("delete"), bg="#de6b6b", fg="white", bd=0, padx=18, pady=12,
                  command=lambda: self._delete_selected(listbox, refresh)).grid(row=row, column=1, pady=16, sticky="w")
        mode_var.trace_add("write", lambda *args: refresh())
        grade_var.trace_add("write", lambda *args: refresh())
        refresh()
        if data:
            listbox.selection_set(0)
            load_selected()

    def _delete_selected(self, listbox, refresh):
        sel = listbox.curselection()
        if not sel:
            return
        line = listbox.get(sel[0])
        task_id = line.split()[0]
        self.db.delete_task(task_id)
        refresh()

    def parent_settings(self, parent):
        tk.Label(parent, text=self._("settings"), bg=CARD2, fg=TEXT, font=("Segoe UI", 28, "bold")).pack(anchor="nw", padx=24, pady=(20,8))
        box = tk.Frame(parent, bg=CARD, highlightbackground="#4560a6", highlightthickness=1)
        box.pack(anchor="nw", padx=24, pady=12)
        tk.Label(box, text=self._("language"), bg=CARD, fg=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=18, pady=(18,6))
        row = tk.Frame(box, bg=CARD)
        row.pack(anchor="w", padx=18, pady=(0,18))
        for code in ("ru","pl","en"):
            tk.Button(row, text=code.upper(), bg=ACCENT if code == self.lang else CARD2,
                      fg="black" if code == self.lang else TEXT, bd=0, padx=14, pady=8,
                      command=lambda c=code: self.set_lang(c)).pack(side="left", padx=6)

def main():
    ensure_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
