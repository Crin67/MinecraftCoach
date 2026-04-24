
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
import sqlite3
import random
import uuid
import json
from datetime import datetime

APP_TITLE = "Minecraft Coach"
BG = "#081229"
PANEL = "#0f1b3d"
CARD = "#152654"
CARD_2 = "#0d1738"
CENTER = "#0a1433"
TEXT = "#f3f7ff"
MUTED = "#b8c5eb"
BORDER = "#304483"
ACCENT = "#f2c24e"
ACCENT_2 = "#4d7cff"
GOOD = "#43c08a"
BAD = "#e0646b"
DEFAULT_BREAK_SECONDS = 300
TASKS_PER_BREAK = 2

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "coach_data"
DATA_DIR.mkdir(exist_ok=True)
DB_FILE = DATA_DIR / "coach.db"

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_input(s: str) -> str:
    s = (s or "").strip().lower()
    repl = {
        "ё": "е", "ę": "e", "é": "e", "è": "e", "ê": "e", "ë": "e",
        "ó": "o", "ö": "o", "ò": "o", "ô": "o", "õ": "o", "ø": "o",
        "ą": "a", "á": "a", "à": "a", "â": "a", "ä": "a", "ã": "a",
        "ć": "c", "č": "c", "ł": "l", "ń": "n", "ś": "s", "š": "s",
        "ź": "z", "ż": "z", "ž": "z", "ý": "y", "ÿ": "y",
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "í": "i", "ì": "i", "î": "i", "ï": "i",
        # похожие кириллица/латиница
        "е": "e", "о": "o", "а": "a", "р": "p", "с": "c", "у": "y", "к": "k", "х": "x", "м": "m", "т": "t",
    }
    return "".join(repl.get(ch, ch) for ch in s)

TR = {
    "ru": {
        "shop": "Магазин",
        "parent": "Родитель",
        "coins": "Монеты",
        "choose_mode": "Выберите режим",
        "who_studies": "Кто будет учиться?",
        "child_program": "Детская программа",
        "adult_program": "Взрослая программа",
        "memory_program": "Режим запоминания",
        "child_desc": "Классы 1–4\nматематика, чтение, слова",
        "adult_desc": "электрика: база, защита,\nкабели, двигатели и практика",
        "memory_desc": "формулы, правила,\nопределения и схемы",
        "select": "Выбрать",
        "select_grade": "Выберите класс",
        "start": "Старт",
        "select_theme": "Выберите тему",
        "waiting_title": "Ждём следующее задание",
        "waiting_ru": "Программа работает. Когда придёт время, задание откроется здесь.",
        "waiting_pl": "Program działa. Gdy nadejdzie czas, zadanie pojawi się tutaj.",
        "waiting_note": "Открой магазин или родительскую панель.",
        "check": "Проверить",
        "next": "Дальше",
        "remembered": "Запомнил / Запомнила",
        "task": "Задание",
        "of": "из",
        "correct": "Правильно",
        "wrong": "Неправильно. Попробуй ещё раз.",
        "reading_done": "Задание засчитано",
        "read_aloud": "Прочитай текст вслух и нажми кнопку.",
        "memory_read": "Запоминай правило. После таймера нажми кнопку.",
        "password": "Пароль",
        "enter_parent_password": "Введите пароль родителя",
        "bad_password": "Неверный пароль",
        "close_parent_password": "Введите пароль родителя для закрытия",
        "close": "Закрыть",
        "parent_panel": "Родительская панель",
        "overview": "Обзор",
        "tasks": "Задания",
        "supports": "Подсказки",
        "settings": "Настройки",
        "language": "Язык интерфейса",
        "save": "Сохранить",
        "break_seconds": "Интервал (сек)",
        "password_saved": "Пароль сохранён",
        "interval_saved": "Интервал сохранён",
        "enter_number": "Введите число",
        "shop_stub": "Пока это заглушка для будущего магазина.",
        "soon": "Скоро",
        "mode_child": "Детская",
        "mode_adult": "Взрослая",
        "mode_memory": "Запоминание",
        "adult_stats": "Взрослых сессий",
        "child_stats": "Детских сессий",
        "memory_stats": "Сессий запоминания",
        "completed_breaks": "Завершено пауз",
        "correct_answers": "Правильных",
        "wrong_answers": "Ошибок",
        "program_id": "ID программы",
        "app_lang_saved": "Язык интерфейса сохранён",
        "theme_basics": "База",
        "theme_safety": "Защита",
        "theme_cables": "Кабели",
        "theme_motors": "Двигатели",
        "theme_practice": "Практика",
        "theme_memory": "Запоминание",
    },
    "pl": {
        "shop": "Sklep",
        "parent": "Rodzic",
        "coins": "Monety",
        "choose_mode": "Wybierz tryb",
        "who_studies": "Kto będzie się uczyć?",
        "child_program": "Program dziecięcy",
        "adult_program": "Program dla dorosłych",
        "memory_program": "Tryb zapamiętywania",
        "child_desc": "Klasy 1–4\nmatematyka, czytanie, słowa",
        "adult_desc": "elektryka: podstawy, ochrona,\nkable, silniki i praktyka",
        "memory_desc": "wzory, zasady,\ndefinicje i schematy",
        "select": "Wybierz",
        "select_grade": "Wybierz klasę",
        "start": "Start",
        "select_theme": "Wybierz temat",
        "waiting_title": "Czekamy na kolejne zadanie",
        "waiting_ru": "Program działa. Gdy nadejdzie czas, zadanie pojawi się tutaj.",
        "waiting_pl": "Program działa. Gdy nadejdzie czas, zadanie pojawi się tutaj.",
        "waiting_note": "Otwórz sklep albo panel rodzica.",
        "check": "Sprawdź",
        "next": "Dalej",
        "remembered": "Zapamiętałem / Zapamiętałam",
        "task": "Zadanie",
        "of": "z",
        "correct": "Dobrze",
        "wrong": "Źle. Spróbuj jeszcze raz.",
        "reading_done": "Zadanie zaliczone",
        "read_aloud": "Przeczytaj tekst na głos i naciśnij przycisk.",
        "memory_read": "Zapamiętaj zasadę. Po timerze naciśnij przycisk.",
        "password": "Hasło",
        "enter_parent_password": "Wpisz hasło rodzica",
        "bad_password": "Nieprawidłowe hasło",
        "close_parent_password": "Wpisz hasło rodzica, aby zamknąć program",
        "close": "Zamknij",
        "parent_panel": "Panel rodzica",
        "overview": "Przegląd",
        "tasks": "Zadania",
        "supports": "Podpowiedzi",
        "settings": "Ustawienia",
        "language": "Język interfejsu",
        "save": "Zapisz",
        "break_seconds": "Interwał (sek)",
        "password_saved": "Hasło zapisane",
        "interval_saved": "Interwał zapisany",
        "enter_number": "Wpisz liczbę",
        "shop_stub": "Na razie to tylko makieta przyszłego sklepu.",
        "soon": "Wkrótce",
        "mode_child": "Dziecięcy",
        "mode_adult": "Dorosły",
        "mode_memory": "Zapamiętywanie",
        "adult_stats": "Sesje dorosłe",
        "child_stats": "Sesje dziecięce",
        "memory_stats": "Sesje zapamiętywania",
        "completed_breaks": "Ukończone przerwy",
        "correct_answers": "Poprawne",
        "wrong_answers": "Błędy",
        "program_id": "ID programu",
        "app_lang_saved": "Język interfejsu zapisany",
        "theme_basics": "Podstawy",
        "theme_safety": "Ochrona",
        "theme_cables": "Kable",
        "theme_motors": "Silniki",
        "theme_practice": "Praktyka",
        "theme_memory": "Zapamiętywanie",
    },
    "en": {
        "shop": "Shop",
        "parent": "Parent",
        "coins": "Coins",
        "choose_mode": "Choose mode",
        "who_studies": "Who will study?",
        "child_program": "Kids program",
        "adult_program": "Adult program",
        "memory_program": "Memory mode",
        "child_desc": "Grades 1–4\nmath, reading, words",
        "adult_desc": "electricity: basics, protection,\ncables, motors and practice",
        "memory_desc": "formulas, rules,\ndefinitions and schemes",
        "select": "Choose",
        "select_grade": "Choose grade",
        "start": "Start",
        "select_theme": "Choose topic",
        "waiting_title": "Waiting for the next task",
        "waiting_ru": "The program is running. When the time comes, the task will appear here.",
        "waiting_pl": "The program is running. When the time comes, the task will appear here.",
        "waiting_note": "Open the shop or parent panel.",
        "check": "Check",
        "next": "Next",
        "remembered": "I remembered it",
        "task": "Task",
        "of": "of",
        "correct": "Correct",
        "wrong": "Wrong. Try again.",
        "reading_done": "Task completed",
        "read_aloud": "Read the text aloud and press the button.",
        "memory_read": "Memorize the rule. After the timer ends, press the button.",
        "password": "Password",
        "enter_parent_password": "Enter parent password",
        "bad_password": "Wrong password",
        "close_parent_password": "Enter parent password to close the app",
        "close": "Close",
        "parent_panel": "Parent panel",
        "overview": "Overview",
        "tasks": "Tasks",
        "supports": "Hints",
        "settings": "Settings",
        "language": "Interface language",
        "save": "Save",
        "break_seconds": "Interval (sec)",
        "password_saved": "Password saved",
        "interval_saved": "Interval saved",
        "enter_number": "Enter a number",
        "shop_stub": "This is still a placeholder for the future shop.",
        "soon": "Soon",
        "mode_child": "Child",
        "mode_adult": "Adult",
        "mode_memory": "Memory",
        "adult_stats": "Adult sessions",
        "child_stats": "Child sessions",
        "memory_stats": "Memory sessions",
        "completed_breaks": "Completed breaks",
        "correct_answers": "Correct",
        "wrong_answers": "Wrong",
        "program_id": "Program ID",
        "app_lang_saved": "Interface language saved",
        "theme_basics": "Basics",
        "theme_safety": "Safety",
        "theme_cables": "Cables",
        "theme_motors": "Motors",
        "theme_practice": "Practice",
        "theme_memory": "Memory",
    }
}

def t(lang, key):
    return TR.get(lang, TR["ru"]).get(key, key)

class DB:
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.init()

    def init(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS stats (k TEXT PRIMARY KEY, v TEXT)")
        c.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            mode TEXT,
            grade INTEGER,
            theme TEXT,
            type TEXT,
            title_ru TEXT, title_pl TEXT,
            prompt_ru TEXT, prompt_pl TEXT,
            answer_json TEXT,
            options_json TEXT,
            hint_type TEXT,
            source TEXT
        )""")
        c.execute("CREATE TABLE IF NOT EXISTS supports (k TEXT PRIMARY KEY, v TEXT)")
        self.conn.commit()
        self.seed_defaults()

    def set(self, table, k, v):
        self.conn.execute(f"INSERT OR REPLACE INTO {table} (k, v) VALUES (?, ?)", (k, str(v)))
        self.conn.commit()

    def get(self, table, k, default=None):
        row = self.conn.execute(f"SELECT v FROM {table} WHERE k=?", (k,)).fetchone()
        return row["v"] if row else default

    def get_settings(self):
        defaults = {
            "parent_password": "1234",
            "break_seconds": str(DEFAULT_BREAK_SECONDS),
            "window_language": "ru",
            "program_id": str(uuid.uuid4())[:8],
        }
        for k, v in defaults.items():
            if self.get("settings", k) is None:
                self.set("settings", k, v)
        return {k: self.get("settings", k, v) for k, v in defaults.items()}

    def get_stats(self):
        defaults = {
            "coins": "0",
            "correct": "0",
            "wrong": "0",
            "completed_breaks": "0",
            "adult_completed": "0",
            "child_completed": "0",
            "memory_completed": "0",
            "last_mode": "",
            "last_activity": now_str(),
        }
        for k, v in defaults.items():
            if self.get("stats", k) is None:
                self.set("stats", k, v)
        out = {}
        for k, v in defaults.items():
            raw = self.get("stats", k, v)
            out[k] = int(raw) if str(raw).isdigit() else raw
        return out

    def save_stats(self, stats):
        for k, v in stats.items():
            self.set("stats", k, v)

    def all_tasks(self):
        rows = self.conn.execute("SELECT * FROM tasks ORDER BY mode, COALESCE(grade,0), theme, id").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["answer"] = json.loads(d.pop("answer_json") or "null")
            d["options"] = json.loads(d.pop("options_json") or "[]")
            out.append(d)
        return out

    def upsert_task(self, task):
        self.conn.execute(
            """INSERT OR REPLACE INTO tasks
            (id,mode,grade,theme,type,title_ru,title_pl,prompt_ru,prompt_pl,answer_json,options_json,hint_type,source)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                task.get("id"), task.get("mode"), task.get("grade"), task.get("theme"), task.get("type"),
                task.get("title_ru", ""), task.get("title_pl", ""),
                task.get("prompt_ru", ""), task.get("prompt_pl", ""),
                json.dumps(task.get("answer"), ensure_ascii=False),
                json.dumps(task.get("options", []), ensure_ascii=False),
                task.get("hint_type", "math"),
                task.get("source", "built_in"),
            )
        )
        self.conn.commit()

    def delete_task(self, task_id):
        self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def get_supports(self):
        base = default_supports()
        for k, v in base.items():
            if self.get("supports", k) is None:
                self.set("supports", k, v)
        return {k: self.get("supports", k, v) for k, v in base.items()}

    def save_support(self, k, v):
        self.set("supports", k, v)

    def seed_defaults(self):
        existing = self.conn.execute("SELECT COUNT(*) c FROM tasks").fetchone()["c"]
        existing_ids = {r["id"] for r in self.conn.execute("SELECT id FROM tasks")}
        builtins = make_child_tasks() + make_adult_tasks()
        for task in builtins:
            if task["id"] not in existing_ids:
                self.upsert_task(task)
        for k, v in default_supports().items():
            if self.get("supports", k) is None:
                self.set("supports", k, v)

def default_supports():
    return {
        "letters_ru": "Гласные: А Е Ё И О У Ы Э Ю Я\nСогласные: Б В Г Д Ж З Й К Л М Н П Р С Т Ф Х Ц Ч Ш Щ",
        "letters_pl": "Samogłoski: A Ą E Ę I O Ó U Y\nSpółgłoski: B C Ć D F G H J K L Ł M N Ń P R S Ś T W Z Ź Ż",
        "multiplication_ru": "Таблица: 7×1=7, 7×2=14, 7×3=21, 7×4=28, 7×5=35\nСмотри на pattern и продолжай.",
        "multiplication_pl": "Tabliczka: 7×1=7, 7×2=14, 7×3=21, 7×4=28, 7×5=35\nPatrz na wzór i kontynuuj.",
        "reading_ru": "Прочитай текст вслух спокойно. Потом нажми кнопку проверки.",
        "reading_pl": "Przeczytaj tekst na głos spokojnie. Potem naciśnij przycisk sprawdzenia.",
        "lesson_ru": "Сначала прочитай правило, потом ответь на вопрос по смыслу.",
        "lesson_pl": "Najpierw przeczytaj zasadę, potem odpowiedz na pytanie.",
        "math_ru": "Считай по шагам. Можно проговорить пример вслух.",
        "math_pl": "Licz krok po kroku. Można powiedzieć działanie na głos.",
    }

def make_child_tasks():
    tasks = []
    def add(grade, idx, typ, title_ru, title_pl, pr_ru, pr_pl, answer, opts=None, hint="math"):
        tasks.append({
            "id": f"c{grade}_{idx:02d}",
            "mode": "child",
            "grade": grade,
            "theme": None,
            "type": typ,
            "title_ru": title_ru,
            "title_pl": title_pl,
            "prompt_ru": pr_ru,
            "prompt_pl": pr_pl,
            "answer": answer,
            "options": opts or [],
            "hint_type": hint,
            "source": "built_in",
        })

    # Grade 1 - 20 tasks
    idx = 1
    for a, b in [(2,3),(4,5),(6,2),(7,1),(5,5),(8,3)]:
        add(1, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} + {b}?", f"Ile będzie {a} + {b}?", str(a+b)); idx += 1
    for a, b in [(7,2),(9,4),(10,3),(12,5),(8,6)]:
        add(1, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} - {b}?", f"Ile będzie {a} - {b}?", str(a-b)); idx += 1
    for ru, pl, ans in [("л_с", "l_s", ["и","i"]), ("д_м", "d_m", ["о","o"]), ("с_к", "s_k", ["о","o"]), ("м_р", "m_r", ["и","i"])]:
        add(1, idx, "input", "Вставь букву", "Wstaw literę", f"Вставь букву: {ru}", f"Wstaw literę: {pl}", ans, hint="letters"); idx += 1
    add(1, idx, "choice", "Выбери слово", "Wybierz słowo", "Выбери слово МАМА", "Wybierz słowo MAMA", "МАМА", ["МАК","КОТ","МАМА","ДОМ"], "letters"); idx += 1
    add(1, idx, "choice", "Выбери ответ", "Wybierz odpowiedź", "Сколько будет 9 + 1?", "Ile będzie 9 + 1?", "10", ["8","10","11","12"]); idx += 1
    add(1, idx, "choice", "Выбери ответ", "Wybierz odpowiedź", "Сколько будет 7 - 3?", "Ile będzie 7 - 3?", "4", ["3","4","5","6"]); idx += 1
    add(1, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: МАМА И ПАПА", "Przeczytaj na głos: MAMA I TATA", "__read__", hint="reading"); idx += 1
    add(1, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: ДОМ И САД", "Przeczytaj na głos: DOM I SAD", "__read__", hint="reading"); idx += 1
    add(1, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: У КОТА ХВОСТ", "Przeczytaj na głos: KOT MA OGON", "__read__", hint="reading"); idx += 1

    # Grade 2 - 20 tasks
    idx = 1
    for a, b in [(14,6),(17,3),(23,4),(18,7),(12,8),(25,5)]:
        add(2, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} - {b}?", f"Ile będzie {a} - {b}?", str(a-b)); idx += 1
    for a, b in [(11,9),(15,6),(18,5),(14,7),(22,8)]:
        add(2, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} + {b}?", f"Ile będzie {a} + {b}?", str(a+b)); idx += 1
    for a, b in [(3,4),(2,5),(6,3),(4,4)]:
        add(2, idx, "choice", "Умножение", "Mnożenie", f"Сколько будет {a} × {b}?", f"Ile będzie {a} × {b}?", str(a*b), [str(a*b), str(a*b+2), str(a*b-1), str(a*b+4)], "multiplication"); idx += 1
    for ru, pl, ans in [("р_ка", "r_ka", ["е","e","ę"]), ("м_ре", "m_rze", ["о","o"]), ("к_са", "k_sa", ["о","o"]), ("л_са", "l_sa", ["и","i"])]:
        add(2, idx, "input", "Вставь букву", "Wstaw literę", f"Вставь букву: {ru}", f"Wstaw literę: {pl}", ans, hint="letters"); idx += 1
    add(2, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: У ЛИСЫ ПУШИСТЫЙ ХВОСТ", "Przeczytaj na głos: LIS MA PUSZYSTY OGON", "__read__", hint="reading"); idx += 1

    # Grade 3 - 20 tasks
    idx = 1
    for a, b in [(7,6),(8,4),(9,3),(6,8),(5,7),(4,9)]:
        add(3, idx, "input", "Умножение", "Mnożenie", f"Сколько будет {a} × {b}?", f"Ile będzie {a} × {b}?", str(a*b), hint="multiplication"); idx += 1
    for a, b in [(24,6),(36,4),(27,3),(35,5),(18,2)]:
        add(3, idx, "choice", "Деление", "Dzielenie", f"Сколько будет {a} : {b}?", f"Ile będzie {a} : {b}?", str(a//b), [str(a//b), str(a//b+1), str(a//b+2), str(max(1, a//b-1))], "math"); idx += 1
    for a, b in [(125,25),(300,50),(240,30),(450,50)]:
        add(3, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} - {b}?", f"Ile będzie {a} - {b}?", str(a-b)); idx += 1
    for ru, pl, ans in [("дру_ба", "przyja_ń", ["ж","z"]), ("кла_с", "kla_s", ["с","s"]), ("тра_а", "tra_a", ["в","w"]), ("бе_ег", "brz_g", ["р","e"])]:
        add(3, idx, "input", "Вставь букву", "Wstaw literę", f"Вставь букву: {ru}", f"Wstaw literę: {pl}", ans, hint="letters"); idx += 1
    add(3, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: ЗИМОЙ ПАДАЕТ БЕЛЫЙ СНЕГ", "Przeczytaj na głos: ZIMĄ PADA BIAŁY ŚNIEG", "__read__", hint="reading"); idx += 1

    # Grade 4 - 20 tasks
    idx = 1
    for a, b in [(8,7),(9,8),(12,6),(11,7),(15,4),(14,5)]:
        add(4, idx, "choice", "Умножение", "Mnożenie", f"Сколько будет {a} × {b}?", f"Ile będzie {a} × {b}?", str(a*b), [str(a*b), str(a*b+2), str(a*b-3), str(a*b+5)], "multiplication"); idx += 1
    for a, b in [(144,12),(180,9),(96,8),(200,5),(81,9)]:
        add(4, idx, "input", "Деление", "Dzielenie", f"Сколько будет {a} : {b}?", f"Ile będzie {a} : {b}?", str(a//b)); idx += 1
    for a, b in [(125,75),(350,150),(240,160),(1000,250)]:
        add(4, idx, "input", "Сосчитай", "Policz", f"Сколько будет {a} + {b}?", f"Ile będzie {a} + {b}?", str(a+b)); idx += 1
    for question, answer, opts in [
        ("Выбери правильное слово: дружба", "дружба", ["дружьба","друшба","дружба","друщба"]),
        ("Выбери правильное слово: лестница", "лестница", ["лестница","лесница","лестнеца","лестниса"]),
        ("Выбери правильное слово: солнце", "солнце", ["сонце","солнце","солце","солънце"]),
        ("Выбери правильное слово: чувство", "чувство", ["чувство","чуство","чувстно","чувствa"]),
    ]:
        add(4, idx, "choice", "Русский", "Rosyjski", question, "Wybierz poprawne słowo", answer, opts, "letters"); idx += 1
    add(4, idx, "reading", "Прочитай", "Przeczytaj", "Прочитай вслух: СОЛНЦЕ ОСВЕЩАЕТ ЗЕМЛЮ И МОРЕ", "Przeczytaj na głos: SŁOŃCE OŚWIETLA ZIEMIĘ I MORZE", "__read__", hint="reading"); idx += 1

    return tasks

def make_adult_tasks():
    tasks = []
    def add(theme, idx, typ, tr, tp, pr, pp, answer="__read__", opts=None, hint="lesson"):
        tasks.append({
            "id": f"a_{theme}_{idx:02d}",
            "mode": "adult",
            "grade": None,
            "theme": theme,
            "type": typ,
            "title_ru": tr,
            "title_pl": tp,
            "prompt_ru": pr,
            "prompt_pl": pp,
            "answer": answer,
            "options": opts or [],
            "hint_type": hint,
            "source": "built_in",
        })

    # Basics
    basics = [
        ("memory","Напряжение","Napięcie","Напряжение U = работа по переносу единичного заряда. Закон Ома для участка: U = I × R.","Napięcie U = praca przeniesienia ładunku. Prawo Ohma dla odcinka: U = I × R."),
        ("memory","Ток","Prąd","Сила тока I = Q / t. Ток — направленное движение заряженных частиц.","Natężenie prądu I = Q / t. Prąd to uporządkowany ruch ładunków."),
        ("memory","Мощность","Moc","Для участка цепи постоянного тока: P = U × I.","Dla odcinka obwodu prądu stałego: P = U × I."),
        ("memory","Полная мощность","Moc pozorna","Для переменного тока полная мощность: S = U × I.","Dla prądu zmiennego moc pozorna: S = U × I."),
        ("memory","Активная и реактивная","Moc czynna i bierna","Связь мощностей: S² = P² + Q². Коэффициент мощности: cosφ = P / S.","Zależność mocy: S² = P² + Q². Współczynnik mocy: cosφ = P / S."),
        ("choice","Закон Ома","Prawo Ohma","Какая формула закона Ома для участка цепи?","Jaki jest wzór prawa Ohma dla odcinka obwodu?","I = U / R",["I = U / R","I = U × R","I = R / U","I = P / U"]),
        ("choice","Переменный ток","Prąd zmienny","Что меняется в переменном токе?","Co zmienia się w prądzie zmiennym?","Направление и значение тока",["Только цвет кабеля","Направление и значение тока","Только длина провода","Ничего"]),
        ("memory","Поле","Pole","Электрическое поле действует на заряд. Потенциал и напряжение связаны разностью потенциалов: U_AB = V_A − V_B.","Pole elektryczne działa na ładunek. Napięcie: U_AB = V_A − V_B."),
    ]
    for i, row in enumerate(basics,1): add("basics", i, *row)

    safety = [
        ("memory","Автомат","Wyłącznik","Автоматический выключатель защищает проводку от перегрузки и короткого замыкания.","Wyłącznik automatyczny chroni instalację przed przeciążeniem i zwarciem."),
        ("memory","УЗО","RCD","УЗО защищает от тока утечки и повышает безопасность человека.","RCD chroni przed prądem upływu i zwiększa bezpieczeństwo człowieka."),
        ("memory","Заземление","Uziemienie","Защитное заземление уменьшает риск поражения током при повреждении изоляции.","Uziemienie ochronne zmniejsza ryzyko porażenia przy uszkodzeniu izolacji."),
        ("choice","Что делает автомат?","Co robi wyłącznik?","Что защищает автоматический выключатель?","Co chroni wyłącznik automatyczny?","Проводку от перегрузки и КЗ",["Человека от всех рисков","Проводку от перегрузки и КЗ","Только лампы","Только счётчик"]),
        ("choice","Зачем УЗО?","Po co RCD?","Для чего нужно УЗО?","Do czego służy RCD?","Для защиты от тока утечки",["Для защиты от тока upływu","Для повышения напряжения","Для охлаждения кабеля","Для работы мотора"]),
        ("memory","Системы заземления","Układy uziemienia","TN-C, TN-S, TN-C-S, TT и IT — основные системы заземления, которые нужно различать.","TN-C, TN-S, TN-C-S, TT i IT to podstawowe układy uziemienia."),
    ]
    for i, row in enumerate(safety,1): add("safety", i, *row)

    cables = [
        ("memory","Сопротивление","Rezystancja","Сопротивление проводника: R = ρ × l / S. Чем меньше сечение, тем больше нагрев.","Rezystancja przewodnika: R = ρ × l / S. Im mniejszy przekrój, tym większe grzanie."),
        ("memory","Индуктивность","Indukcyjność","Для катушки: u = L × di/dt, X_L = 2πfL. Напряжение на индуктивности опережает ток на 90°.","Dla cewki: u = L × di/dt, X_L = 2πfL. Napięcie na indukcyjności wyprzedza prąd o 90°."),
        ("memory","Ёмкость","Pojemność","Для конденсатора: i = C × du/dt, X_C = 1 / (2πfC). Напряжение на ёмкости отстаёт от тока на 90°.","Dla kondensatora: i = C × du/dt, X_C = 1/(2πfC). Napięcie na pojemności opóźnia się o 90° względem prądu."),
        ("memory","Генри","Henr","1 H = 1 V·s / A. Один генри — такая индуктивность, при которой изменение тока на 1 А/с даёт ЭДС 1 В.","1 H = 1 V·s / A. Jeden henr oznacza indukcyjność, przy której zmiana prądu 1 A/s daje 1 V."),
        ("choice","Материал жил","Materiał żył","Из чего обычно делают токопроводящие жилы?","Z czego zwykle robi się żyły przewodzące?","Из меди или алюминия",["Из стекла","Из бумаги","Из меди или алюминия","Из резины"]),
        ("choice","Соединение","Łączenie","Почему опасно брать слишком тонкий кабель?","Dlaczego zbyt cienki kabel jest niebezpieczny?","Он может перегреваться",["Jest ładniejszy","Może się przegrzewać","Lepiej przewodzi","Nie ma różnicy"]),
    ]
    for i, row in enumerate(cables,1): add("cables", i, *row)

    motors = [
        ("memory","Двигатели","Silniki","Есть двигатели постоянного тока, переменного тока и универсальные. BLDC — бесщёточный двигатель постоянного тока.","Są silniki prądu stałego, zmiennego i uniwersalne. BLDC to bezszczotkowy silnik prądu stałego."),
        ("memory","Индукция","Indukcja","Электромагнитная индукция: ε = − dΦ / dt. Ток возникает при изменении магнитного потока.","Indukcja elektromagnetyczna: ε = − dΦ / dt. Prąd powstaje przy zmianie strumienia magnetycznego."),
        ("memory","Внутреннее сопротивление","Rezystancja wewnętrzna","Для источника: E = U + U_w, а U = E − I × R_w. Больший ток даёт больший спад напряжения.","Dla źródła: E = U + U_w, a U = E − I × R_w. Większy prąd daje większy spadek napięcia."),
        ("choice","Индукция","Indukcja","Кто открыл закон электромагнитной индукции?","Kto odkrył prawo indukcji elektromagnetycznej?","Майкл Фарадей",["Michael Faraday","Thomas Edison","Georg Ohm","Nikola Tesla"]),
        ("choice","Тип двигателя","Typ silnika","Как называется бесщёточный двигатель постоянного тока?","Jak nazywa się bezszczotkowy silnik prądu stałego?","BLDC",["RCD","BLDC","TN-C","PWM"]),
    ]
    for i, row in enumerate(motors,1): add("motors", i, *row)

    practice = [
        ("memory","Инструмент","Narzędzia","Электрику нужны: индикатор напряжения, отвёртки, стриппер, пассатижи, изоляционные материалы.","Elektryk potrzebuje: wskaźnika napięcia, śrubokrętów, strippera, szczypiec i materiałów izolacyjnych."),
        ("memory","Розетки и свет","Gniazda i światło","Розетки, выключатели и светильники размещают с учётом безопасности, удобства и нагрузки.","Gniazda, wyłączniki i oprawy planuje się z myślą o bezpieczeństwie, wygodzie i obciążeniu."),
        ("memory","Светодиоды","LED","Для светодиодной ленты нужен подходящий блок питания с запасом по мощности.","Dla taśmy LED нужен odpowiedni zasilacz z zapasem mocy."),
        ("choice","Индикатор","Wskaźnik","Что используют для проверки наличия напряжения?","Czego używa się do sprawdzenia obecności napięcia?","Индикатор напряжения",["Pędzel","Linijka","Wskaźnik napięcia","Spinacz"]),
        ("choice","Освещение","Oświetlenie","Какой тип освещения считается современным и экономичным?","Jaki typ oświetlenia jest nowoczesny i oszczędny?","Светодиодное",["Газовое","Лампа накаливания","Светодиодное","Керосиновое"]),
    ]
    for i, row in enumerate(practice,1): add("practice", i, *row)

    # separate memory-only bank
    mem_cards = [
        ("Формула 1","Wzór 1","I = U / R","I = U / R"),
        ("Формула 2","Wzór 2","U = I × R","U = I × R"),
        ("Формула 3","Wzór 3","R = U / I","R = U / I"),
        ("Формула 4","Wzór 4","P = U × I","P = U × I"),
        ("Формула 5","Wzór 5","S = U × I","S = U × I"),
        ("Формула 6","Wzór 6","S² = P² + Q²","S² = P² + Q²"),
        ("Формула 7","Wzór 7","cosφ = P / S","cosφ = P / S"),
        ("Формула 8","Wzór 8","u = L × di / dt","u = L × di / dt"),
        ("Формула 9","Wzór 9","i = C × du / dt","i = C × du / dt"),
        ("Формула 10","Wzór 10","X_L = 2πfL","X_L = 2πfL"),
        ("Формула 11","Wzór 11","X_C = 1 / (2πfC)","X_C = 1 / (2πfC)"),
        ("Формула 12","Wzór 12","ε = − dΦ / dt","ε = − dΦ / dt"),
        ("Правило 1","Zasada 1","На резисторе напряжение и ток в фазе.","Na rezystorze napięcie i prąd są w fazie."),
        ("Правило 2","Zasada 2","На индуктивности напряжение опережает ток на 90°.","Na indukcyjności napięcie wyprzedza prąd o 90°."),
        ("Правило 3","Zasada 3","На ёмкости напряжение отстаёт от тока на 90°.","Na pojemności napięcie opóźnia się o 90° względem prądu."),
        ("Правило 4","Zasada 4","1 H = 1 V·s / A","1 H = 1 V·s / A"),
        ("Правило 5","Zasada 5","U = E − I × R_w","U = E − I × R_w"),
        ("Правило 6","Zasada 6","E = U + U_w","E = U + U_w"),
        ("Правило 7","Zasada 7","Активная мощность совершает полезную работу.","Moc czynna wykonuje pracę użyteczną."),
        ("Правило 8","Zasada 8","Реактивная мощность нагружает сеть, но не выполняет полезной работы.","Moc bierna obciąża sieć, ale nie wykonuje pracy użytecznej."),
    ]
    for i, (tr,tp,pr,pp) in enumerate(mem_cards,1):
        add("memory", i, "memory", tr, tp, pr, pp)
    return tasks

class ParentPanel(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.lang = app.lang
        self.title(t(self.lang, "parent_panel"))
        self.geometry("1220x820")
        self.configure(bg=BG)
        self.transient(app.root)
        self.grab_set()
        self.current = None
        self.selected_task_id = None
        self.build()
        self.show("overview")

    def tt(self, key):
        return t(self.lang, key)

    def build(self):
        top = tk.Frame(self, bg=PANEL, height=64)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text=self.tt("parent_panel"), bg=PANEL, fg=TEXT, font=("Segoe UI", 22, "bold")).pack(side="left", padx=18, pady=12)
        tk.Button(top, text=self.tt("close"), command=self.destroy, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(side="right", padx=14, pady=12)

        wrap = tk.Frame(self, bg=BG)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        self.menu = tk.Frame(wrap, bg=CARD, width=190)
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        self.body = tk.Frame(wrap, bg=BG)
        self.body.pack(side="left", fill="both", expand=True, padx=(14,0))

        self.menu_buttons = {}
        for key in ["overview", "tasks", "supports", "settings"]:
            btn = tk.Button(self.menu, text=self.tt(key), command=lambda k=key: self.show(k),
                            bg=CARD_2, fg=TEXT, relief="flat", anchor="w", padx=18, pady=12,
                            font=("Segoe UI", 12, "bold"))
            btn.pack(fill="x", padx=10, pady=(10 if key == "overview" else 0, 8))
            self.menu_buttons[key] = btn

        self.frames = {k: tk.Frame(self.body, bg=BG) for k in ["overview", "tasks", "supports", "settings"]}
        self.build_overview()
        self.build_tasks()
        self.build_supports()
        self.build_settings()

    def show(self, key):
        if self.current:
            self.frames[self.current].pack_forget()
            self.menu_buttons[self.current].config(bg=CARD_2)
        self.current = key
        self.frames[key].pack(fill="both", expand=True)
        self.menu_buttons[key].config(bg=ACCENT_2)
        if key == "overview":
            self.refresh_overview()
        elif key == "tasks":
            self.refresh_task_list()
        elif key == "supports":
            self.refresh_support_list()
        self.lift()

    def pane_title(self, parent, title):
        tk.Label(parent, text=title, bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0,12))

    def build_overview(self):
        f = self.frames["overview"]
        self.pane_title(f, self.tt("overview"))
        self.ov_text = tk.Text(f, height=18, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Consolas", 12))
        self.ov_text.pack(fill="both", expand=False)
        self.ov_text.config(state="disabled")

    def refresh_overview(self):
        self.app.reload_from_db()
        s = self.app.stats
        txt = (
            f"{self.tt('program_id')}: {self.app.settings['program_id']}\n"
            f"{self.tt('coins')}: {s['coins']}\n"
            f"{self.tt('correct_answers')}: {s['correct']}\n"
            f"{self.tt('wrong_answers')}: {s['wrong']}\n"
            f"{self.tt('completed_breaks')}: {s['completed_breaks']}\n"
            f"{self.tt('child_stats')}: {s['child_completed']}\n"
            f"{self.tt('adult_stats')}: {s['adult_completed']}\n"
            f"{self.tt('memory_stats')}: {s['memory_completed']}\n"
            f"Last mode: {s['last_mode']}\n"
            f"Last activity: {s['last_activity']}\n"
            f"Tasks in DB: {len(self.app.tasks)}\n"
        )
        self.ov_text.config(state="normal")
        self.ov_text.delete("1.0", "end")
        self.ov_text.insert("1.0", txt)
        self.ov_text.config(state="disabled")

    def build_tasks(self):
        f = self.frames["tasks"]
        self.pane_title(f, self.tt("tasks"))
        top = tk.Frame(f, bg=BG)
        top.pack(fill="both", expand=True)

        left = tk.Frame(top, bg=BG, width=350)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        right = tk.Frame(top, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12,0))

        filter_row = tk.Frame(left, bg=BG)
        filter_row.pack(fill="x")
        tk.Label(filter_row, text="Mode", bg=BG, fg=MUTED).pack(side="left")
        self.task_mode_var = tk.StringVar(value="all")
        tk.OptionMenu(filter_row, self.task_mode_var, "all", "child", "adult").pack(side="left", padx=8)
        tk.Label(filter_row, text="Grade/Theme", bg=BG, fg=MUTED).pack(side="left", padx=(10,0))
        self.task_filter_var = tk.StringVar(value="all")
        tk.Entry(filter_row, textvariable=self.task_filter_var, width=12).pack(side="left", padx=8)
        tk.Button(filter_row, text=self.tt("save"), command=self.refresh_task_list, bg=ACCENT_2, fg="white", relief="flat").pack(side="left", padx=8)

        self.task_list = tk.Listbox(left, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat", font=("Consolas", 10))
        self.task_list.pack(fill="both", expand=True, pady=(10,0))
        self.task_list.bind("<<ListboxSelect>>", self.load_selected_task)

        form = tk.Frame(right, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="both", expand=True)

        self.task_entries = {}
        fields = [("id","ID"),("mode","Mode"),("grade","Grade"),("theme","Theme"),("type","Type"),
                  ("title_ru","Title RU"),("title_pl","Title PL"),("prompt_ru","Prompt RU"),
                  ("prompt_pl","Prompt PL"),("answer","Answer"),("options","Options (; separated)"),("hint_type","Hint")]
        for i, (key, label) in enumerate(fields):
            tk.Label(form, text=label, bg=CARD, fg=MUTED).grid(row=i, column=0, sticky="w", padx=12, pady=6)
            if key in ("prompt_ru","prompt_pl","answer","options"):
                ent = tk.Text(form, height=3 if "prompt" in key else 2, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
                ent.grid(row=i, column=1, sticky="ew", padx=12, pady=6)
            else:
                ent = tk.Entry(form, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
                ent.grid(row=i, column=1, sticky="ew", padx=12, pady=6)
            self.task_entries[key] = ent
        form.grid_columnconfigure(1, weight=1)

        btns = tk.Frame(form, bg=CARD)
        btns.grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=12, pady=12)
        tk.Button(btns, text=self.tt("save"), command=self.save_task, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(side="left", padx=(0,8))
        tk.Button(btns, text="Delete", command=self.delete_task, bg=BAD, fg="white", relief="flat", padx=14, pady=8).pack(side="left")

    def refresh_task_list(self):
        self.app.reload_from_db()
        self.task_map = {}
        mode = self.task_mode_var.get()
        filt = self.task_filter_var.get().strip().lower()
        self.task_list.delete(0, "end")
        items = []
        for task in self.app.tasks:
            if mode != "all" and task["mode"] != mode:
                continue
            token = str(task.get("grade") or task.get("theme") or "")
            if filt and filt not in token.lower():
                continue
            items.append(task)
        for task in items:
            label = f"{task['id']} | {task['mode']} | {task.get('grade') or task.get('theme') or '-'} | {task['type']} | {task['title_ru']}"
            idx = self.task_list.size()
            self.task_list.insert("end", label)
            self.task_map[idx] = task

    def _set_widget(self, widget, value):
        if isinstance(widget, tk.Text):
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
        else:
            widget.delete(0, "end")
            widget.insert(0, value)

    def _get_widget(self, widget):
        if isinstance(widget, tk.Text):
            return widget.get("1.0", "end").strip()
        return widget.get().strip()

    def load_selected_task(self, event=None):
        sel = self.task_list.curselection()
        if not sel:
            return
        task = self.task_map.get(sel[0])
        if not task:
            return
        self.selected_task_id = task["id"]
        for key, widget in self.task_entries.items():
            value = task.get(key, "")
            if key == "answer":
                value = json.dumps(task.get("answer"), ensure_ascii=False)
            elif key == "options":
                value = "; ".join(task.get("options", []))
            self._set_widget(widget, str(value if value is not None else ""))

    def save_task(self):
        task = {}
        for key, widget in self.task_entries.items():
            task[key] = self._get_widget(widget)
        try:
            answer_raw = task["answer"]
            task["answer"] = json.loads(answer_raw) if answer_raw.startswith("[") else answer_raw
        except Exception:
            task["answer"] = task["answer"]
        task["options"] = [x.strip() for x in task["options"].split(";") if x.strip()]
        task["grade"] = int(task["grade"]) if task["grade"] else None
        task["source"] = "custom"
        self.app.db.upsert_task(task)
        self.app.reload_from_db()
        self.refresh_task_list()
        self.app.refresh_language()

    def delete_task(self):
        if self.selected_task_id:
            self.app.db.delete_task(self.selected_task_id)
            self.app.reload_from_db()
            self.refresh_task_list()

    def build_supports(self):
        f = self.frames["supports"]
        self.pane_title(f, self.tt("supports"))
        wrap = tk.Frame(f, bg=BG)
        wrap.pack(fill="both", expand=True)
        left = tk.Listbox(wrap, bg=CARD, fg=TEXT, selectbackground=ACCENT_2, selectforeground="white", relief="flat")
        left.pack(side="left", fill="y", padx=(0,12))
        self.support_list = left
        self.support_editor = tk.Text(wrap, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.support_editor.pack(side="left", fill="both", expand=True)
        btns = tk.Frame(f, bg=BG)
        btns.pack(fill="x", pady=10)
        tk.Button(btns, text=self.tt("save"), command=self.save_support, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(side="left")
        self.support_list.bind("<<ListboxSelect>>", self.load_support)

    def refresh_support_list(self):
        self.app.reload_from_db()
        self.support_keys = list(self.app.supports.keys())
        self.support_list.delete(0, "end")
        for key in self.support_keys:
            self.support_list.insert("end", key)

    def load_support(self, event=None):
        sel = self.support_list.curselection()
        if not sel:
            return
        key = self.support_keys[sel[0]]
        self.current_support_key = key
        self.support_editor.delete("1.0", "end")
        self.support_editor.insert("1.0", self.app.supports.get(key, ""))

    def save_support(self):
        if not hasattr(self, "current_support_key"):
            return
        val = self.support_editor.get("1.0", "end").strip()
        self.app.db.save_support(self.current_support_key, val)
        self.app.reload_from_db()

    def build_settings(self):
        f = self.frames["settings"]
        self.pane_title(f, self.tt("settings"))
        card = tk.Frame(f, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")
        tk.Label(card, text=self.tt("password"), bg=CARD, fg=MUTED).grid(row=0, column=0, sticky="w", padx=12, pady=12)
        self.pass_entry = tk.Entry(card, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.pass_entry.grid(row=0, column=1, sticky="ew", padx=12, pady=12)
        self.pass_entry.insert(0, self.app.settings["parent_password"])

        tk.Label(card, text=self.tt("break_seconds"), bg=CARD, fg=MUTED).grid(row=1, column=0, sticky="w", padx=12, pady=12)
        self.break_entry = tk.Entry(card, bg=CENTER, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.break_entry.grid(row=1, column=1, sticky="ew", padx=12, pady=12)
        self.break_entry.insert(0, str(self.app.break_seconds))

        tk.Label(card, text=self.tt("language"), bg=CARD, fg=MUTED).grid(row=2, column=0, sticky="w", padx=12, pady=12)
        self.lang_var = tk.StringVar(value=self.app.lang)
        tk.OptionMenu(card, self.lang_var, "ru", "pl", "en").grid(row=2, column=1, sticky="w", padx=12, pady=12)

        tk.Label(card, text=self.tt("program_id"), bg=CARD, fg=MUTED).grid(row=3, column=0, sticky="w", padx=12, pady=12)
        tk.Label(card, text=self.app.settings["program_id"], bg=CARD, fg=TEXT, font=("Consolas", 12, "bold")).grid(row=3, column=1, sticky="w", padx=12, pady=12)

        btns = tk.Frame(card, bg=CARD)
        btns.grid(row=4, column=0, columnspan=2, sticky="w", padx=12, pady=12)
        tk.Button(btns, text=self.tt("save"), command=self.save_settings, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=16, pady=8).pack(side="left")
        card.grid_columnconfigure(1, weight=1)

    def save_settings(self):
        self.app.settings["parent_password"] = self.pass_entry.get().strip() or "1234"
        self.app.db.set("settings", "parent_password", self.app.settings["parent_password"])
        try:
            self.app.break_seconds = max(30, int(self.break_entry.get().strip()))
            self.app.db.set("settings", "break_seconds", self.app.break_seconds)
        except Exception:
            messagebox.showerror(APP_TITLE, self.tt("enter_number"))
            return
        self.app.lang = self.lang_var.get()
        self.app.db.set("settings", "window_language", self.app.lang)
        self.app.reload_from_db()
        self.app.refresh_language()
        self.lang = self.app.lang
        messagebox.showinfo(APP_TITLE, self.tt("app_lang_saved"))
        self.destroy()

class MinecraftCoachRelease:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=BG)
        self.root.geometry("1320x820")
        self.root.minsize(1120, 720)
        self.root.protocol("WM_DELETE_WINDOW", self.request_close)
        self.db = DB(DB_FILE)
        self.reload_from_db()
        self.lang = self.settings.get("window_language", "ru")
        self.break_seconds = int(self.settings.get("break_seconds", DEFAULT_BREAK_SECONDS))
        self.program_mode = "child"
        self.child_grade = 1
        self.adult_theme = "basics"
        self.current_break_tasks = []
        self.current_index = 0
        self.current_task = None
        self.break_after_id = None
        self.memory_after_id = None
        self.memory_seconds_left = 0
        self.build_ui()
        self.refresh_language()
        self.show_start_screen()
        self.tick_loop()

    def tt(self, key):
        return t(self.lang, key)

    def reload_from_db(self):
        self.settings = self.db.get_settings()
        self.stats = self.db.get_stats()
        self.tasks = self.db.all_tasks()
        self.supports = self.db.get_supports()

    def persist_stats(self):
        self.stats["last_activity"] = now_str()
        self.db.save_stats(self.stats)

    def build_ui(self):
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)

        self.header = tk.Frame(self.container, bg=PANEL, height=68)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.mode_badge = tk.Label(self.header, text="—", fg=TEXT, bg=CARD, padx=16, pady=8, font=("Segoe UI", 12, "bold"))
        self.mode_badge.pack(side="left", padx=18, pady=10)

        self.shop_btn = tk.Button(self.header, command=self.open_shop, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.shop_btn.pack(side="left", padx=(0, 8), pady=10)

        self.parent_btn = tk.Button(self.header, command=self.ask_parent_panel, bg=ACCENT_2, fg="white", relief="flat", font=("Segoe UI", 11, "bold"), padx=14, pady=8)
        self.parent_btn.pack(side="left", padx=(0, 8), pady=10)

        lang_box = tk.Frame(self.header, bg=PANEL)
        lang_box.pack(side="right", padx=16)
        self.lang_var = tk.StringVar(value=self.lang)
        tk.OptionMenu(lang_box, self.lang_var, "ru", "pl", "en", command=self.change_language).pack(side="right", pady=14)

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
        self.body_wrap.pack(fill="both", expand=True, padx=22, pady=(0,18))

        self.side_left = tk.Frame(self.body_wrap, bg=CARD_2, width=0)
        self.side_left.pack(side="left", fill="y", padx=(0,10))
        self.side_left.pack_propagate(False)

        self.center_panel = tk.Frame(self.body_wrap, bg=CENTER, highlightbackground=BORDER, highlightthickness=1)
        self.center_panel.pack(side="left", fill="both", expand=True)

        self.side_right = tk.Frame(self.body_wrap, bg=CARD_2, width=0)
        self.side_right.pack(side="left", fill="y", padx=(10,0))
        self.side_right.pack_propagate(False)

        prompt_row = tk.Frame(self.center_panel, bg=CENTER)
        prompt_row.pack(fill="x", padx=18, pady=(18, 8))

        self.ru_box = tk.Frame(prompt_row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        self.ru_box.pack(side="left", fill="both", expand=True, padx=(0,8))
        self.pl_box = tk.Frame(prompt_row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        self.pl_box.pack(side="left", fill="both", expand=True, padx=(8,0))

        self.ru_box_title = tk.Label(self.ru_box, text="Русский", fg=TEXT, bg=CARD_2, font=("Segoe UI", 15, "bold"))
        self.ru_box_title.pack(anchor="w", padx=18, pady=(18,8))
        self.ru_prompt = tk.Label(self.ru_box, text="", fg=TEXT, bg=CARD_2, justify="left", wraplength=360, font=("Segoe UI", 18))
        self.ru_prompt.pack(anchor="w", padx=18, pady=(0,18))

        self.pl_box_title = tk.Label(self.pl_box, text="Polski", fg=TEXT, bg=CARD_2, font=("Segoe UI", 15, "bold"))
        self.pl_box_title.pack(anchor="w", padx=18, pady=(18,8))
        self.pl_prompt = tk.Label(self.pl_box, text="", fg=TEXT, bg=CARD_2, justify="left", wraplength=360, font=("Segoe UI", 18))
        self.pl_prompt.pack(anchor="w", padx=18, pady=(0,18))

        self.answer_area = tk.Frame(self.center_panel, bg=CENTER)
        self.answer_area.pack(fill="x", padx=24, pady=(14, 14))

        self.answer_entry = tk.Entry(self.answer_area, font=("Segoe UI", 22), width=16, justify="center")
        self.check_btn = tk.Button(self.answer_area, command=self.check_answer, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.next_btn = tk.Button(self.answer_area, command=self.mark_reading_done, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.memory_btn = tk.Button(self.answer_area, command=self.finish_memory_task, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=10)
        self.memory_timer_label = tk.Label(self.center_panel, text="", fg=ACCENT, bg=CENTER, font=("Segoe UI", 18, "bold"))
        self.memory_timer_label.pack(pady=(0,4))
        self.feedback = tk.Label(self.center_panel, text="", fg=MUTED, bg=CENTER, font=("Segoe UI", 14, "bold"))
        self.feedback.pack(pady=(0,16))

        self.start_overlay = tk.Frame(self.center_panel, bg=CENTER)
        self.start_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.update_coins()

    def refresh_language(self):
        self.reload_from_db()
        self.lang = self.settings.get("window_language", self.lang)
        self.root.title(APP_TITLE)
        self.shop_btn.config(text=self.tt("shop"))
        self.parent_btn.config(text=self.tt("parent"))
        self.update_coins()
        self.check_btn.config(text=self.tt("check"))
        self.next_btn.config(text=self.tt("next"))
        self.memory_btn.config(text=self.tt("remembered"))
        if hasattr(self, "current_task") and self.current_task:
            self.show_task(self.current_task)
        else:
            self.show_start_screen()

    def change_language(self, value):
        self.lang = value
        self.db.set("settings", "window_language", value)
        self.refresh_language()

    def clear_overlay(self):
        for w in self.start_overlay.winfo_children():
            w.destroy()
        self.start_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_start_screen(self):
        self.clear_overlay()
        self.title_label.config(text=self.tt("choose_mode"))
        self.step_label.config(text="")
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", width=860, height=430)
        tk.Label(card, text=self.tt("who_studies"), fg=TEXT, bg=CARD, font=("Segoe UI", 28, "bold")).pack(pady=(30,18))
        row = tk.Frame(card, bg=CARD)
        row.pack(pady=20)

        def mode_card(parent, title, desc, cmd):
            frm = tk.Frame(parent, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1, width=240, height=220)
            frm.pack(side="left", padx=12)
            frm.pack_propagate(False)
            tk.Label(frm, text=title, fg=TEXT, bg=CARD_2, font=("Segoe UI", 18, "bold")).pack(pady=(24,10))
            tk.Label(frm, text=desc, fg=MUTED, bg=CARD_2, justify="center", font=("Segoe UI", 12)).pack()
            tk.Button(frm, text=self.tt("select"), command=cmd, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=18, pady=8).pack(pady=18)
            return frm

        mode_card(row, self.tt("child_program"), self.tt("child_desc"), self.show_child_select)
        mode_card(row, self.tt("adult_program"), self.tt("adult_desc"), self.show_adult_select)
        mode_card(row, self.tt("memory_program"), self.tt("memory_desc"), self.start_memory_mode)

    def show_child_select(self):
        self.clear_overlay()
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", width=680, height=320)
        tk.Label(card, text=self.tt("select_grade"), fg=TEXT, bg=CARD, font=("Segoe UI", 24, "bold")).pack(pady=(28,18))
        row = tk.Frame(card, bg=CARD)
        row.pack(pady=16)
        self.grade_var = tk.IntVar(value=self.child_grade)
        for g in [1,2,3,4]:
            box = tk.Frame(row, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1, width=120, height=88)
            box.pack(side="left", padx=10)
            box.pack_propagate(False)
            tk.Radiobutton(box, text=f"{g}", variable=self.grade_var, value=g, bg=CARD_2, fg=TEXT, selectcolor=CARD,
                           activebackground=CARD_2, activeforeground=TEXT, font=("Segoe UI", 18, "bold"), indicatoron=0).pack(expand=True, fill="both", padx=10, pady=10)
        tk.Button(card, text=self.tt("start"), command=self.start_child, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=22, pady=10).pack(pady=24)

    def show_adult_select(self):
        self.clear_overlay()
        card = tk.Frame(self.start_overlay, bg=CARD)
        card.place(relx=0.5, rely=0.5, anchor="center", width=760, height=420)
        tk.Label(card, text=self.tt("select_theme"), fg=TEXT, bg=CARD, font=("Segoe UI", 24, "bold")).pack(pady=(28,18))
        self.theme_var = tk.StringVar(value=self.adult_theme)
        themes = [("basics", self.tt("theme_basics")), ("safety", self.tt("theme_safety")), ("cables", self.tt("theme_cables")), ("motors", self.tt("theme_motors")), ("practice", self.tt("theme_practice"))]
        inner = tk.Frame(card, bg=CARD)
        inner.pack(pady=12)
        for i, (key, label) in enumerate(themes):
            tk.Radiobutton(inner, text=label, variable=self.theme_var, value=key, bg=CARD, fg=TEXT, selectcolor=CARD_2, activebackground=CARD, activeforeground=TEXT, font=("Segoe UI", 13)).grid(row=i, column=0, sticky="w", padx=120, pady=6)
        tk.Button(card, text=self.tt("start"), command=self.start_adult, bg=ACCENT, fg="#111", relief="flat", font=("Segoe UI", 12, "bold"), padx=22, pady=10).pack(pady=22)

    def start_child(self):
        self.program_mode = "child"
        self.child_grade = self.grade_var.get()
        self.stats["last_mode"] = f"child_{self.child_grade}"
        self.mode_badge.config(text=f"{self.tt('mode_child')}: {self.child_grade}")
        self.start_overlay.place_forget()
        self.schedule_next_break()
        self.show_waiting_state()

    def start_adult(self):
        self.program_mode = "adult"
        self.adult_theme = self.theme_var.get()
        self.stats["last_mode"] = f"adult_{self.adult_theme}"
        self.mode_badge.config(text=f"{self.tt('mode_adult')}: {self.tt('theme_' + self.adult_theme)}")
        self.start_overlay.place_forget()
        self.schedule_next_break()
        self.show_waiting_state()

    def start_memory_mode(self):
        self.program_mode = "memory"
        self.stats["last_mode"] = "memory"
        self.mode_badge.config(text=f"{self.tt('mode_memory')}")
        self.start_overlay.place_forget()
        self.schedule_next_break()
        self.show_waiting_state()

    def build_break_tasks(self):
        if self.program_mode == "child":
            pool = [t for t in self.tasks if t["mode"] == "child" and int(t.get("grade") or 0) == self.child_grade]
            self.stats["child_completed"] += 1
        elif self.program_mode == "adult":
            pool = [t for t in self.tasks if t["mode"] == "adult" and t.get("theme") == self.adult_theme]
            self.stats["adult_completed"] += 1
        else:
            pool = [t for t in self.tasks if t["mode"] == "adult" and t.get("theme") == "memory"]
            self.stats["memory_completed"] += 1
        random.shuffle(pool)
        if len(pool) < TASKS_PER_BREAK:
            pool = pool * max(1, TASKS_PER_BREAK)
        self.current_break_tasks = pool[:TASKS_PER_BREAK]
        self.current_index = 0
        self.persist_stats()

    def schedule_next_break(self):
        if self.break_after_id:
            self.root.after_cancel(self.break_after_id)
        self.build_break_tasks()
        self.break_after_id = self.root.after(max(1000, self.break_seconds * 1000), self.start_next_break)

    def start_next_break(self):
        self.current_index = 0
        self.show_task(self.current_break_tasks[0])

    def show_waiting_state(self):
        self.hide_side_panels()
        self.title_label.config(text=self.tt("waiting_title"))
        self.step_label.config(text="")
        self.ru_prompt.config(text=self.tt("waiting_ru"))
        self.pl_prompt.config(text=self.tt("waiting_pl"))
        for w in self.answer_area.winfo_children():
            w.pack_forget()
        self.memory_timer_label.config(text="")
        self.feedback.config(text=self.tt("waiting_note"), fg=MUTED)

    def hide_side_panels(self):
        for fr in (self.side_left, self.side_right):
            fr.config(width=0)
            for w in fr.winfo_children():
                w.destroy()

    def set_side_panel(self, side, title, content):
        frame = self.side_left if side == "left" else self.side_right
        for w in frame.winfo_children():
            w.destroy()
        frame.config(width=230)
        tk.Label(frame, text=title, fg=TEXT, bg=CARD_2, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(12,6))
        tk.Label(frame, text=content, fg=MUTED, bg=CARD_2, justify="left", wraplength=200, font=("Segoe UI", 11)).pack(anchor="nw", padx=12, pady=(0,12))
        frame.lift()

    def update_support_panels(self, task):
        hint = task.get("hint_type", "")
        self.hide_side_panels()
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

    def show_task(self, task):
        self.current_task = task
        self.memory_timer_label.config(text="")
        self.feedback.config(text="", fg=MUTED)
        self.update_coins()
        self.step_label.config(text=f"{self.tt('task')} {self.current_index + 1} {self.tt('of')} {len(self.current_break_tasks)}")
        self.title_label.config(text=f"{task.get('title_ru','Задание')}  |  {task.get('title_pl','Zadanie')}")
        self.ru_prompt.config(text=task.get("prompt_ru", ""))
        self.pl_prompt.config(text=task.get("prompt_pl", ""))
        self.update_support_panels(task)
        for w in self.answer_area.winfo_children():
            w.pack_forget()
        if self.memory_after_id:
            self.root.after_cancel(self.memory_after_id)
            self.memory_after_id = None
        if task.get("type") == "choice":
            grid = tk.Frame(self.answer_area, bg=CENTER)
            grid.pack()
            opts = task.get("options", [])
            for i, opt in enumerate(opts):
                tk.Button(grid, text=opt, command=lambda o=opt: self.check_answer(choice=o), bg=ACCENT_2, fg="white", relief="flat", font=("Segoe UI", 12, "bold"), width=20, pady=12).grid(row=i//2, column=i%2, padx=8, pady=8)
        elif task.get("type") == "reading":
            self.next_btn.pack()
            self.feedback.config(text=self.tt("read_aloud"), fg=MUTED)
        elif task.get("type") == "memory":
            self.memory_seconds_left = 60
            self.memory_timer_label.config(text="01:00")
            self.feedback.config(text=self.tt("memory_read"), fg=MUTED)
            self.memory_btn.pack()
            self.memory_btn.config(state="disabled")
            self.tick_memory_timer()
        else:
            self.answer_entry.delete(0, "end")
            self.answer_entry.pack(side="left", padx=(0,12))
            self.check_btn.pack(side="left")
            self.answer_entry.focus_set()

    def tick_memory_timer(self):
        mins, secs = divmod(self.memory_seconds_left, 60)
        self.memory_timer_label.config(text=f"{mins:02d}:{secs:02d}")
        if self.memory_seconds_left <= 0:
            self.memory_btn.config(state="normal")
            self.feedback.config(text=self.tt("remembered"), fg=GOOD)
            return
        self.memory_seconds_left -= 1
        self.memory_after_id = self.root.after(1000, self.tick_memory_timer)

    def finish_memory_task(self):
        self.stats["correct"] += 1
        self.stats["coins"] += 5
        self.persist_stats()
        self.update_coins()
        self.feedback.config(text=self.tt("correct"), fg=GOOD)
        self.root.after(500, self.advance_task)

    def mark_reading_done(self):
        self.stats["correct"] += 1
        self.stats["coins"] += 5
        self.persist_stats()
        self.update_coins()
        self.feedback.config(text=self.tt("reading_done"), fg=GOOD)
        self.root.after(500, self.advance_task)

    def answer_ok(self, task, given):
        answer = task.get("answer")
        if answer == "__read__":
            return True
        if isinstance(answer, list):
            return normalize_input(given) in [normalize_input(x) for x in answer]
        return normalize_input(given) == normalize_input(str(answer))

    def check_answer(self, choice=None):
        given = choice if choice is not None else self.answer_entry.get().strip()
        if self.answer_ok(self.current_task, given):
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

    def advance_task(self):
        self.current_index += 1
        if self.current_index >= len(self.current_break_tasks):
            self.stats["completed_breaks"] += 1
            self.stats["coins"] += 10
            self.persist_stats()
            self.update_coins()
            self.schedule_next_break()
            self.show_waiting_state()
            return
        self.show_task(self.current_break_tasks[self.current_index])

    def update_coins(self):
        self.coins_badge.config(text=f"🪙 {self.stats.get('coins',0)}")

    def open_shop(self):
        top = tk.Toplevel(self.root)
        top.title(self.tt("shop"))
        top.geometry("1040x700")
        top.configure(bg=BG)
        tk.Label(top, text=f"{self.tt('shop')} / Sklep", fg=TEXT, bg=BG, font=("Segoe UI", 24, "bold")).pack(pady=20)
        grid = tk.Frame(top, bg=BG)
        grid.pack(fill="both", expand=True, padx=24, pady=14)
        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)
        prices = [25, 50, 75, 100, 125, 150]
        for i, price in enumerate(prices):
            card = tk.Frame(grid, bg=CARD, highlightbackground=BORDER, highlightthickness=1, width=280, height=220)
            card.grid(row=i//3, column=i%3, padx=18, pady=18, sticky="nsew")
            card.grid_propagate(False)
            inner = tk.Frame(card, bg=CARD)
            inner.pack(expand=True, fill="both")
            tk.Label(inner, text="?", fg=TEXT, bg=CARD, font=("Segoe UI", 42, "bold")).pack(pady=(28,10))
            tk.Label(inner, text=self.tt("soon"), fg=TEXT, bg=CARD, font=("Segoe UI", 16, "bold")).pack()
            tk.Label(inner, text=f"{price} {self.tt('coins').lower()}", fg=MUTED, bg=CARD, font=("Segoe UI", 13)).pack(pady=(8,0))
        tk.Label(top, text=self.tt("shop_stub"), fg=MUTED, bg=BG, font=("Segoe UI", 11)).pack(pady=(0,16))

    def ask_parent_panel(self):
        pw = simpledialog.askstring(self.tt("password"), self.tt("enter_parent_password"), show="*")
        if pw == self.settings.get("parent_password", "1234"):
            ParentPanel(self)
        elif pw is not None:
            messagebox.showerror(APP_TITLE, self.tt("bad_password"))

    def request_close(self):
        pw = simpledialog.askstring(self.tt("password"), self.tt("close_parent_password"), show="*")
        if pw == self.settings.get("parent_password", "1234"):
            self.root.destroy()

    def tick_loop(self):
        self.root.after(1000, self.tick_loop)

def main():
    root = tk.Tk()
    app = MinecraftCoachRelease(root)
    root.mainloop()

if __name__ == "__main__":
    main()
