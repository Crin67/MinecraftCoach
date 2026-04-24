import tkinter as tk
from tkinter import messagebox
import random
import time
import ctypes
import os
import wave
import subprocess
import json
from datetime import datetime
from pathlib import Path

# ============================
# Настройки
# ============================
MIN_INTERVAL_MIN = 0
MAX_INTERVAL_MIN = 1
TASKS_PER_BREAK = 2
SEND_ESC_TO_PAUSE = True
FORCE_FOCUS_EVERY_MS = 350
APP_TITLE = "Minecraft Coach Kids"
COINS_PER_TASK = 5
COINS_PER_BREAK = 10

# Спокойная палитра
WINDOW_BG = "#E8EEF2"
CARD_BG = "#F7FAFC"
PANEL_BG = "#EEF3F7"
ACCENT = "#6A8CAF"
ACCENT_2 = "#7CA982"
ACCENT_3 = "#E8C35D"
BAD = "#C06C84"
TEXT = "#28323C"
SUBTEXT = "#5E6A75"
SOFT_BORDER = "#D6E0E8"
SHADOW = "#D8E0E7"

APP_DIR = Path(__file__).resolve().parent
PREFERRED_RECORDINGS_DIR = APP_DIR / "recordings"
PREFERRED_DATA_DIR = APP_DIR / "coach_data"


def ensure_writable_dir(preferred: Path, fallback_name: str):
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        test_file = preferred / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return preferred
    except Exception:
        fallback = Path.home() / "Documents" / fallback_name
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


RECORDINGS_DIR = ensure_writable_dir(PREFERRED_RECORDINGS_DIR, "MinecraftCoachRecordings")
DATA_DIR = ensure_writable_dir(PREFERRED_DATA_DIR, "MinecraftCoachData")
STATS_FILE = DATA_DIR / "stats.json"


# ============================
# Опциональная запись микрофона
# ============================
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except Exception:
    sd = None
    SOUNDDEVICE_AVAILABLE = False

try:
    import lameenc
    LAMEENC_AVAILABLE = True
except Exception:
    lameenc = None
    LAMEENC_AVAILABLE = False

# ============================
# WinAPI helpers
# ============================
user32 = ctypes.windll.user32
VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002
SW_RESTORE = 9
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040
GetForegroundWindow = user32.GetForegroundWindow
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextW = user32.GetWindowTextW
SetForegroundWindow = user32.SetForegroundWindow
ShowWindow = user32.ShowWindow
keybd_event = user32.keybd_event
SetWindowPos = user32.SetWindowPos


def get_foreground_title():
    hwnd = GetForegroundWindow()
    length = GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buff, length + 1)
    return hwnd, buff.value


def press_escape():
    keybd_event(VK_ESCAPE, 0, 0, 0)
    time.sleep(0.04)
    keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, 0)


def try_pause_minecraft():
    hwnd, title = get_foreground_title()
    if "minecraft" in (title or "").lower():
        press_escape()
        return True, title
    return False, title


def force_window_topmost(hwnd):
    try:
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        ShowWindow(hwnd, SW_RESTORE)
        SetForegroundWindow(hwnd)
    except Exception:
        pass


def speak_async_windows(text):
    if os.name != "nt" or not text:
        return
    try:
        safe = text.replace('"', '`"')
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "Add-Type -AssemblyName System.Speech; "
                "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$speak.Rate = -1; "
                f'$speak.SpeakAsync("{safe}") | Out-Null'
            ),
        ]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# ============================
# Аудиозапись
# ============================
class MicRecorder:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.frames = []
        self.is_recording = False

    def start(self):
        if not SOUNDDEVICE_AVAILABLE:
            raise RuntimeError("Установите sounddevice для записи микрофона")
        self.frames = []

        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.frames.append(bytes(indata))

        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            callback=callback,
        )
        self.stream.start()
        self.is_recording = True

    def stop_and_save(self, base_path_without_ext):
        if not self.is_recording:
            return None

        self.is_recording = False
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
        finally:
            self.stream = None

        raw_bytes = b"".join(self.frames)
        if not raw_bytes:
            return None

        os.makedirs(os.path.dirname(base_path_without_ext), exist_ok=True)

        if LAMEENC_AVAILABLE:
            mp3_path = base_path_without_ext + ".mp3"
            encoder = lameenc.Encoder()
            encoder.set_bit_rate(128)
            encoder.set_in_sample_rate(self.sample_rate)
            encoder.set_channels(self.channels)
            encoder.set_quality(2)
            mp3_data = encoder.encode(raw_bytes) + encoder.flush()
            with open(mp3_path, "wb") as f:
                f.write(mp3_data)
            return mp3_path

        wav_path = base_path_without_ext + ".wav"
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(raw_bytes)
        return wav_path


# ============================
# Статистика
# ============================
def load_stats():
    default = {
        "coins": 0,
        "total_tasks_completed": 0,
        "total_breaks_completed": 0,
        "correct_by_type": {"input": 0, "choice": 0, "button": 0},
        "history": [],
    }
    try:
        if STATS_FILE.exists():
            data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
            default.update(data)
            if "correct_by_type" not in default:
                default["correct_by_type"] = {"input": 0, "choice": 0, "button": 0}
            return default
    except Exception:
        pass
    return default


def save_stats(stats):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


# ============================
# Данные
# ============================
GRADE_CONFIGS = {
    1: {
        "label": "1 класс / Klasa 1",
        "math_add_max": 10,
        "math_sub_max": 10,
        "mul_max": 0,
        "division_max": 0,
        "reading_ru": ["ма", "мама", "кот", "дом", "луна"],
        "reading_pl": ["kot", "dom", "mama", "las", "Ala ma kota."],
    },
    2: {
        "label": "2 класс / Klasa 2",
        "math_add_max": 20,
        "math_sub_max": 20,
        "mul_max": 2,
        "division_max": 0,
        "reading_ru": ["Мама мыла раму.", "Кот спит.", "У нас урок.", "Соня читает книгу."],
        "reading_pl": ["Ala lubi szkołę.", "Tata czyta książkę.", "To jest nasz dom.", "Ola ma lalkę."],
    },
    3: {
        "label": "3 класс / Klasa 3",
        "math_add_max": 50,
        "math_sub_max": 50,
        "mul_max": 5,
        "division_max": 5,
        "reading_ru": ["Сегодня мы решаем задачу и читаем вслух.", "Весной на улице тепло и солнечно."],
        "reading_pl": ["Dzisiaj liczymy i czytamy na głos.", "Wiosną jest ciepło i słonecznie."],
    },
    4: {
        "label": "4 класс / Klasa 4",
        "math_add_max": 100,
        "math_sub_max": 100,
        "mul_max": 10,
        "division_max": 10,
        "reading_ru": ["Сегодня мы будем внимательно читать, считать и думать.", "Осенью листья меняют цвет и падают на землю."],
        "reading_pl": ["Dzisiaj będziemy uważnie czytać, liczyć i myśleć.", "Jesienią liście zmieniają kolor i spadają na ziemię."],
    },
}

RU_WORDS = {
    1: [("м_ма", "а", "мама"), ("к_т", "о", "кот"), ("д_м", "о", "дом")],
    2: [("р_ка", "у", "рука"), ("кн_га", "и", "книга"), ("шк_ла", "о", "школа")],
    3: [("мол_ко", "о", "молоко"), ("карт_на", "и", "картина"), ("учен_к", "и", "ученик")],
    4: [("интер_сный", "е", "интересный"), ("матем_тика", "а", "математика"), ("б_седа", "е", "беседа")],
}

PL_WORDS = {
    1: [("m_ma", "a", "mama"), ("k_t", "o", "kot"), ("d_m", "o", "dom")],
    2: [("szk_ła", "o", "szkoła"), ("ksi_żka", "ą", "książka"), ("r_ka", "ę", "ręka")],
    3: [("czyt_nie", "a", "czytanie"), ("u_zeń", "c", "uczeń"), ("wios_a", "n", "wiosna")],
    4: [("nauczyci_l", "e", "nauczyciel"), ("interesuj_cy", "ą", "interesujący"), ("matemat_ka", "y", "matematyka")],
}

LANGUAGE_SEQUENCE = ["ru", "pl"]


def pick_grade_items(mapping, grade):
    candidates = []
    for g in range(1, grade + 1):
        candidates.extend(mapping.get(g, []))
    return candidates


class TaskFactory:
    @staticmethod
    def build_bilingual(title_ru, title_pl, prompt_ru, prompt_pl, task_type, answer=None, options=None, record_audio=False, voice_text=None):
        return {
            "type": task_type,
            "title_ru": title_ru,
            "title_pl": title_pl,
            "prompt_ru": prompt_ru,
            "prompt_pl": prompt_pl,
            "answer": answer,
            "options": options or [],
            "record_audio": record_audio,
            "voice_text": voice_text or "Реши задание и нажми кнопку проверки.",
        }

    @staticmethod
    def make_math_task(grade, focus_lang):
        cfg = GRADE_CONFIGS[grade]
        mode = random.choice(["add", "sub"] + (["mul"] if cfg["mul_max"] else []) + (["div"] if cfg["division_max"] else []))

        if mode == "add":
            a = random.randint(0, cfg["math_add_max"])
            b = random.randint(0, cfg["math_add_max"])
            answer = str(a + b)
            pr_ru = f"Реши пример: {a} + {b} = ?"
            pr_pl = f"Rozwiąż przykład: {a} + {b} = ?"
            title_ru = "Математика"
            title_pl = "Matematyka"
        elif mode == "sub":
            a = random.randint(0, cfg["math_sub_max"])
            b = random.randint(0, a)
            answer = str(a - b)
            pr_ru = f"Реши пример: {a} - {b} = ?"
            pr_pl = f"Rozwiąż przykład: {a} - {b} = ?"
            title_ru = "Математика"
            title_pl = "Matematyka"
        elif mode == "mul":
            a = random.randint(1, cfg["mul_max"])
            b = random.randint(1, 10 if grade >= 4 else 5)
            answer = str(a * b)
            pr_ru = f"Таблица умножения: {a} × {b} = ?"
            pr_pl = f"Tabliczka mnożenia: {a} × {b} = ?"
            title_ru = "Умножение"
            title_pl = "Mnożenie"
        else:
            b = random.randint(1, cfg["division_max"])
            answer_num = random.randint(1, 10 if grade >= 4 else 5)
            a = b * answer_num
            answer = str(answer_num)
            pr_ru = f"Деление: {a} ÷ {b} = ?"
            pr_pl = f"Dzielenie: {a} ÷ {b} = ?"
            title_ru = "Деление"
            title_pl = "Dzielenie"

        return TaskFactory.build_bilingual(
            title_ru, title_pl, pr_ru, pr_pl,
            task_type="input", answer=answer,
            voice_text="Реши пример и напиши ответ в окошке."
        )

    @staticmethod
    def make_spelling_task(grade, focus_lang):
        if focus_lang == "ru":
            masked, missing, full = random.choice(pick_grade_items(RU_WORDS, grade))
            return TaskFactory.build_bilingual(
                "Русский язык", "Język rosyjski",
                f"Вставь букву: {masked}", f"Wstaw literę w rosyjskim słowie: {masked}",
                task_type="input", answer=missing,
                voice_text="Вставь пропущенную букву и напиши её в окошке."
            )
        masked, missing, full = random.choice(pick_grade_items(PL_WORDS, grade))
        return TaskFactory.build_bilingual(
            "Польский язык", "Język polski",
            f"Вставь букву в польское слово: {masked}", f"Wstaw literę: {masked}",
            task_type="input", answer=missing,
            voice_text="Вставь пропущенную букву и напиши её в окошке."
        )

    @staticmethod
    def make_choice_task(grade, focus_lang):
        if focus_lang == "ru":
            items = [
                ("Какая первая буква в слове КОТ?", "Jaka jest pierwsza litera w słowie KOT?", "К", ["К", "М", "Т", "О"]),
                ("Выбери слово ДОМ", "Wybierz słowo DOM", "ДОМ", ["ТОМ", "ДОМ", "КОТ", "СОМ"]),
                ("Сколько будет 3 + 2?", "Ile będzie 3 + 2?", "5", ["4", "5", "6", "7"]),
            ]
            if grade >= 3:
                items.append(("Сколько будет 4 × 3?", "Ile będzie 4 × 3?", "12", ["7", "12", "14", "16"]))
        else:
            items = [
                ("Какая первая буква в слове DOM?", "Jaka jest pierwsza litera w słowie DOM?", "D", ["D", "M", "O", "B"]),
                ("Выбери слово KOT", "Wybierz słowo KOT", "KOT", ["KOT", "DOM", "LAS", "RĘKA"]),
                ("Сколько будет 4 + 1?", "Ile będzie 4 + 1?", "5", ["4", "5", "6", "7"]),
            ]
            if grade >= 3:
                items.append(("Сколько будет 3 × 4?", "Ile będzie 3 × 4?", "12", ["10", "11", "12", "13"]))

        pr_ru, pr_pl, answer, options = random.choice(items)
        options = options[:]
        random.shuffle(options)
        return TaskFactory.build_bilingual(
            "Выбери ответ", "Wybierz odpowiedź",
            pr_ru, pr_pl,
            task_type="choice", answer=answer.lower(), options=options,
            voice_text="Выбери правильный ответ кнопкой."
        )

    @staticmethod
    def make_reading_task(grade, focus_lang):
        cfg = GRADE_CONFIGS[grade]
        if focus_lang == "ru":
            text = random.choice(cfg["reading_ru"])
            return TaskFactory.build_bilingual(
                "Чтение вслух", "Czytanie na głos",
                f"Прочитай вслух:\n\n{text}", f"Przeczytaj po rosyjsku na głos:\n\n{text}",
                task_type="button", answer="ok", record_audio=True,
                voice_text="Прочитай, что написано, и нажми на кнопку."
            )
        text = random.choice(cfg["reading_pl"])
        return TaskFactory.build_bilingual(
            "Чтение вслух", "Czytanie na głos",
            f"Прочитай по-польски вслух:\n\n{text}", f"Przeczytaj na głos:\n\n{text}",
            task_type="button", answer="ok", record_audio=True,
            voice_text="Прочитай, что написано, и нажми на кнопку."
        )

    @staticmethod
    def random_task(grade, focus_lang):
        choices = [
            TaskFactory.make_math_task,
            TaskFactory.make_math_task,
            TaskFactory.make_spelling_task,
            TaskFactory.make_choice_task,
            TaskFactory.make_reading_task,
        ]
        if grade >= 3:
            choices.append(TaskFactory.make_math_task)
        maker = random.choice(choices)
        return maker(grade, focus_lang)


class ShopDialog(tk.Toplevel):
    def __init__(self, parent, coins):
        super().__init__(parent)
        self.parent = parent
        self.coins = coins
        self.configure(bg=WINDOW_BG)
        self.title("Магазин / Sklep")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        wrapper_shadow = tk.Frame(self, bg=SHADOW)
        wrapper_shadow.pack(padx=18, pady=18)
        wrapper = tk.Frame(wrapper_shadow, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        wrapper.pack(padx=(0, 4), pady=(0, 4))

        header = tk.Frame(wrapper, bg=CARD_BG)
        header.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(header, text="Магазин наград / Sklep nagród", font=("Arial", 20, "bold"), bg=CARD_BG, fg=TEXT).pack(side="left")
        tk.Label(header, text=f"Монетки: {coins}", font=("Arial", 14, "bold"), bg=CARD_BG, fg=ACCENT_3).pack(side="right")

        tk.Label(wrapper, text="Карточки-заглушки. Позже сюда можно добавить настоящие награды.", font=("Arial", 12), bg=CARD_BG, fg=SUBTEXT).pack(padx=18, pady=(0, 12))

        grid = tk.Frame(wrapper, bg=CARD_BG)
        grid.pack(padx=18, pady=(0, 18))
        prices = [20, 35, 50, 75, 100, 150]
        for i, price in enumerate(prices):
            cell_shadow = tk.Frame(grid, bg=SHADOW)
            cell_shadow.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            cell = tk.Frame(cell_shadow, bg="#FFF8E1", width=180, height=170, highlightthickness=1, highlightbackground="#E7D18E")
            cell.pack(padx=(0, 4), pady=(0, 4))
            cell.pack_propagate(False)
            tk.Label(cell, text="?", font=("Arial", 40, "bold"), bg="#FFF8E1", fg="#C8A740").pack(pady=(16, 6))
            tk.Label(cell, text="Секретная награда", font=("Arial", 12, "bold"), bg="#FFF8E1", fg=TEXT).pack()
            tk.Label(cell, text=f"Цена: {price} монет", font=("Arial", 11), bg="#FFF8E1", fg=SUBTEXT).pack(pady=(4, 10))
            tk.Button(cell, text="Скоро", font=("Arial", 11, "bold"), bg=ACCENT_3, fg="white", activebackground=ACCENT_3, state="disabled").pack()

        tk.Button(wrapper, text="Закрыть / Zamknij", font=("Arial", 13, "bold"), bg=ACCENT, fg="white", activebackground=ACCENT, padx=18, pady=8, command=self.destroy).pack(pady=(0, 16))

        self.update_idletasks()
        w = 660
        h = 500
        x = max(80, self.winfo_screenwidth() // 2 - w // 2)
        y = max(60, self.winfo_screenheight() // 2 - h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.focus_force()


class StatsDialog(tk.Toplevel):
    def __init__(self, parent, stats):
        super().__init__(parent)
        self.title("Статистика / Statystyki")
        self.configure(bg=WINDOW_BG)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        shadow = tk.Frame(self, bg=SHADOW)
        shadow.pack(padx=18, pady=18)
        wrapper = tk.Frame(shadow, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        wrapper.pack(padx=(0, 4), pady=(0, 4))

        tk.Label(wrapper, text="Статистика ребёнка", font=("Arial", 20, "bold"), bg=CARD_BG, fg=TEXT).pack(pady=(18, 12))
        info = [
            f"Монетки: {stats['coins']}",
            f"Решено заданий: {stats['total_tasks_completed']}",
            f"Завершено игровых пауз: {stats['total_breaks_completed']}",
            f"Правильных заданий с вводом: {stats['correct_by_type'].get('input', 0)}",
            f"Правильных заданий с выбором: {stats['correct_by_type'].get('choice', 0)}",
            f"Прочитано вслух заданий: {stats['correct_by_type'].get('button', 0)}",
            f"Файл статистики: {STATS_FILE}",
        ]
        for line in info:
            tk.Label(wrapper, text=line, font=("Arial", 13), bg=CARD_BG, fg=TEXT, justify="left").pack(anchor="w", padx=18, pady=3)

        tk.Button(wrapper, text="Закрыть / Zamknij", font=("Arial", 13, "bold"), bg=ACCENT, fg="white", activebackground=ACCENT, padx=18, pady=8, command=self.destroy).pack(pady=18)

        self.update_idletasks()
        w = 640
        h = 320
        x = max(80, self.winfo_screenwidth() // 2 - w // 2)
        y = max(60, self.winfo_screenheight() // 2 - h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.focus_force()


class HomeworkOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=WINDOW_BG)
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)
        self.root.bind("<Escape>", lambda e: "break")

        self.break_active = False
        self.selected_grade = None
        self.next_break_ts = None
        self.task_index = 0
        self.lang_queue = []
        self.current_task = None
        self.recorder = None
        self.recording_path = None
        self.store_window = None
        self.stats_window = None
        self.animating_card = False
        self.stats = load_stats()

        self.build_ui()
        self.update_coin_label()
        self.show_level_screen()
        self.tick()

    def build_ui(self):
        self.main = tk.Frame(self.root, bg=WINDOW_BG)
        self.main.pack(fill="both", expand=True)

        self.topbar = tk.Frame(self.main, bg=WINDOW_BG)
        self.topbar.pack(fill="x", padx=18, pady=(14, 0))

        self.shop_button_shadow = tk.Frame(self.topbar, bg="#D9BD61")
        self.shop_button_shadow.pack(side="left")
        self.shop_btn = tk.Button(
            self.shop_button_shadow,
            text="🛒 Магазин / Sklep",
            font=("Arial", 15, "bold"),
            bg=ACCENT_3,
            fg="white",
            activebackground=ACCENT_3,
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            command=self.open_shop,
        )
        self.shop_btn.pack(padx=(0, 3), pady=(0, 3))

        self.stats_btn = tk.Button(
            self.topbar,
            text="📊 Статистика",
            font=("Arial", 13, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            command=self.open_stats,
        )
        self.stats_btn.pack(side="left", padx=12)

        self.coin_label = tk.Label(self.topbar, text="", font=("Arial", 15, "bold"), bg=WINDOW_BG, fg=TEXT)
        self.coin_label.pack(side="right", padx=8)

        self.card_shadow = tk.Frame(self.main, bg=SHADOW)
        self.card = tk.Frame(self.card_shadow, bg=CARD_BG, bd=0, highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.card.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))

        self.header = tk.Frame(self.card, bg=CARD_BG)
        self.header.pack(fill="x", padx=24, pady=(18, 8))

        self.grade_label = tk.Label(self.header, text="", font=("Arial", 15, "bold"), bg=CARD_BG, fg=ACCENT)
        self.grade_label.pack(side="left")

        self.progress_label = tk.Label(self.header, text="", font=("Arial", 15, "bold"), bg=CARD_BG, fg=SUBTEXT)
        self.progress_label.pack(side="right")

        self.title_label = tk.Label(self.card, text="", font=("Arial", 28, "bold"), bg=CARD_BG, fg=TEXT)
        self.title_label.pack(pady=(4, 10))

        self.columns = tk.Frame(self.card, bg=CARD_BG)
        self.columns.pack(fill="both", expand=True, padx=24, pady=8)
        self.columns.grid_columnconfigure(0, weight=1)
        self.columns.grid_columnconfigure(1, weight=1)
        self.columns.grid_rowconfigure(0, weight=1)

        self.left_panel = tk.Frame(self.columns, bg=PANEL_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.right_panel = tk.Frame(self.columns, bg=PANEL_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        tk.Label(self.left_panel, text="Русский", font=("Arial", 18, "bold"), bg=PANEL_BG, fg=TEXT).pack(pady=(16, 8))
        tk.Label(self.right_panel, text="Polski", font=("Arial", 18, "bold"), bg=PANEL_BG, fg=TEXT).pack(pady=(16, 8))

        self.prompt_ru = tk.Label(self.left_panel, text="", font=("Arial", 22), bg=PANEL_BG, fg=TEXT, wraplength=520, justify="center")
        self.prompt_ru.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        self.prompt_pl = tk.Label(self.right_panel, text="", font=("Arial", 22), bg=PANEL_BG, fg=TEXT, wraplength=520, justify="center")
        self.prompt_pl.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        self.input_area = tk.Frame(self.card, bg=CARD_BG)
        self.input_area.pack(pady=(8, 6))
        self.entry = tk.Entry(self.input_area, font=("Arial", 30), justify="center", relief="solid", bd=2, width=12)
        self.entry.pack(ipady=8, ipadx=10)
        self.entry.bind("<Return>", lambda e: self.check_answer())
        self.entry.bind("<Button-1>", lambda e: self.root.after(20, self.focus_entry))
        self.entry.bind("<FocusOut>", lambda e: self.root.after(10, self.focus_entry_if_needed()))

        self.choice_frame = tk.Frame(self.card, bg=CARD_BG)
        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.choice_frame,
                text="",
                font=("Arial", 18, "bold"),
                bg=ACCENT,
                fg="white",
                activebackground=ACCENT,
                padx=20,
                pady=16,
                width=12,
                command=lambda idx=i: self.check_choice(idx),
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            self.choice_buttons.append(btn)
        self.choice_frame.grid_columnconfigure(0, weight=1)
        self.choice_frame.grid_columnconfigure(1, weight=1)

        self.controls = tk.Frame(self.card, bg=CARD_BG)
        self.controls.pack(pady=(8, 14))
        self.check_btn = tk.Button(
            self.controls,
            text="Проверить / Sprawdź",
            font=("Arial", 20, "bold"),
            bg=ACCENT_2,
            fg="white",
            activebackground=ACCENT_2,
            padx=22,
            pady=12,
            command=self.check_answer,
        )
        self.check_btn.grid(row=0, column=0, padx=8)
        self.next_btn = tk.Button(
            self.controls,
            text="Готово / Gotowe",
            font=("Arial", 20, "bold"),
            bg=ACCENT_2,
            fg="white",
            activebackground=ACCENT_2,
            padx=22,
            pady=12,
            command=self.mark_button_done,
        )
        self.next_btn.grid(row=0, column=1, padx=8)

        self.status_label = tk.Label(self.main, text="", font=("Arial", 16, "bold"), bg=WINDOW_BG, fg=TEXT)
        self.status_label.pack(side="bottom", pady=10)

        self.start_screen = tk.Frame(self.main, bg=WINDOW_BG)
        self.start_screen.place(relx=0.5, rely=0.53, anchor="center", relwidth=0.78, relheight=0.76)

        start_shadow = tk.Frame(self.start_screen, bg=SHADOW)
        start_shadow.pack(fill="both", expand=True)
        start_card = tk.Frame(start_shadow, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        start_card.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))
        tk.Label(start_card, text="Minecraft Coach Kids", font=("Arial", 30, "bold"), bg=CARD_BG, fg=TEXT).pack(pady=(32, 12))
        tk.Label(start_card, text="Выберите уровень сложности по классу школы\nWybierz poziom trudności według klasy", font=("Arial", 16), bg=CARD_BG, fg=SUBTEXT).pack(pady=(0, 22))

        self.grade_buttons_frame = tk.Frame(start_card, bg=CARD_BG)
        self.grade_buttons_frame.pack(pady=12)
        for grade in sorted(GRADE_CONFIGS):
            cfg = GRADE_CONFIGS[grade]
            tk.Button(
                self.grade_buttons_frame,
                text=cfg["label"],
                font=("Arial", 18, "bold"),
                bg=ACCENT,
                fg="white",
                activebackground=ACCENT,
                width=22,
                pady=12,
                command=lambda g=grade: self.select_grade(g),
            ).pack(pady=10)

        self.start_info = tk.Label(
            start_card,
            text=(
                "1 класс: простые примеры, буквы, чтение коротких слов\n"
                "2 класс: примеры посложнее, короткие предложения\n"
                "3 класс: умножение, деление, логика\n"
                "4 класс: большие числа, таблица умножения, чтение длиннее"
            ),
            font=("Arial", 14),
            bg=CARD_BG,
            fg=SUBTEXT,
            justify="center",
        )
        self.start_info.pack(pady=(18, 8))

    def show_level_screen(self):
        self.hide_task_card()
        self.start_screen.lift()
        self.start_screen.place(relx=0.5, rely=0.53, anchor="center", relwidth=0.78, relheight=0.76)
        self.status_label.config(text="Сначала выберите класс / Najpierw wybierz klasę", fg=TEXT)

    def hide_task_card(self):
        self.card_shadow.place_forget()

    def animate_task_card(self):
        self.animating_card = True
        steps = 10
        start_w, start_h, start_y = 0.72, 0.68, 0.57
        end_w, end_h, end_y = 0.92, 0.88, 0.52

        def step(i=0):
            t = i / steps
            rw = start_w + (end_w - start_w) * t
            rh = start_h + (end_h - start_h) * t
            ry = start_y + (end_y - start_y) * t
            self.card_shadow.place(relx=0.5, rely=ry, anchor="center", relwidth=rw, relheight=rh)
            if i < steps:
                self.root.after(18, lambda: step(i + 1))
            else:
                self.animating_card = False

        step(0)

    def show_task_card(self):
        self.start_screen.place_forget()
        self.animate_task_card()

    def select_grade(self, grade):
        self.selected_grade = grade
        self.next_break_ts = self.make_next_break_time()
        self.status_label.config(text=f"Выбран уровень: {GRADE_CONFIGS[grade]['label']}", fg=TEXT)
        self.hide_task_card()

    def make_next_break_time(self):
        mins = random.randint(MIN_INTERVAL_MIN, MAX_INTERVAL_MIN)
        return time.time() + mins * 60

    def on_close_attempt(self):
        if self.break_active:
            return
        if messagebox.askyesno(APP_TITLE, "Закрыть программу?"):
            self.root.destroy()

    def focus_entry(self):
        if self.break_active and self.current_task and self.current_task.get("type") == "input":
            try:
                self.entry.focus_force()
                self.entry.icursor(tk.END)
            except Exception:
                pass

    def focus_entry_if_needed(self):
        return lambda: self.focus_entry()

    def show_overlay(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        self.root.lift()
        try:
            force_window_topmost(self.root.winfo_id())
            self.root.focus_force()
        except Exception:
            pass

    def hide_overlay(self):
        self.root.withdraw()

    def update_coin_label(self):
        self.coin_label.config(text=f"🪙 Монетки: {self.stats['coins']}")

    def add_coins(self, amount, reason=""):
        self.stats["coins"] += amount
        if reason:
            self.stats["history"].append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "coins": amount,
                "reason": reason,
            })
            self.stats["history"] = self.stats["history"][-50:]
        save_stats(self.stats)
        self.update_coin_label()

    def open_shop(self):
        if self.store_window and self.store_window.winfo_exists():
            self.store_window.lift()
            self.store_window.focus_force()
            return
        self.store_window = ShopDialog(self.root, self.stats["coins"])

    def open_stats(self):
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            self.stats_window.focus_force()
            return
        self.stats_window = StatsDialog(self.root, self.stats)

    def start_break(self):
        if not self.selected_grade:
            self.show_overlay()
            self.show_level_screen()
            return
        self.break_active = True
        self.task_index = 0
        self.lang_queue = LANGUAGE_SEQUENCE[:]
        if SEND_ESC_TO_PAUSE:
            try_pause_minecraft()
        self.show_overlay()
        self.show_task_card()
        self.load_next_task()
        self.keep_overlay_active()

    def finish_break(self):
        self.stop_recording_if_needed()
        self.break_active = False
        self.next_break_ts = self.make_next_break_time()
        self.stats["total_breaks_completed"] += 1
        self.add_coins(COINS_PER_BREAK, "break_completed")
        save_stats(self.stats)
        self.status_label.config(text=f"Молодец! Пауза завершена. +{COINS_PER_BREAK} монет 🎉", fg=ACCENT_2)
        self.hide_overlay()

    def keep_overlay_active(self):
        if not self.break_active:
            return
        self.show_overlay()
        if self.current_task and self.current_task.get("type") == "input":
            self.focus_entry()
        self.root.after(FORCE_FOCUS_EVERY_MS, self.keep_overlay_active)

    def start_recording_if_needed(self):
        if not self.current_task or not self.current_task.get("record_audio"):
            return
        try:
            self.recorder = MicRecorder()
            self.recorder.start()
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            focus = self.lang_queue[0] if self.lang_queue else "done"
            self.recording_path = os.path.join(str(RECORDINGS_DIR), f"grade{self.selected_grade}_{focus}_{now}")
            self.status_label.config(text=f"Идёт запись микрофона... Папка: {RECORDINGS_DIR}", fg=ACCENT)
        except Exception as e:
            self.recorder = None
            self.recording_path = None
            self.status_label.config(text=f"Запись не запустилась: {e}", fg=BAD)

    def stop_recording_if_needed(self):
        if not self.recorder:
            return
        try:
            path = self.recorder.stop_and_save(self.recording_path)
            if path:
                self.status_label.config(text=f"Запись сохранена: {path}", fg=ACCENT)
        except Exception as e:
            self.status_label.config(text=f"Не удалось сохранить запись: {e}", fg=BAD)
        finally:
            self.recorder = None
            self.recording_path = None

    def load_next_task(self):
        self.stop_recording_if_needed()
        if not self.lang_queue:
            self.finish_break()
            return

        focus_lang = self.lang_queue.pop(0)
        self.current_task = TaskFactory.random_task(self.selected_grade, focus_lang)
        self.task_index += 1

        self.grade_label.config(text=GRADE_CONFIGS[self.selected_grade]["label"])
        self.progress_label.config(text=f"Задание {self.task_index} из {TASKS_PER_BREAK}")
        self.title_label.config(text=f"{self.current_task['title_ru']}  |  {self.current_task['title_pl']}")
        self.prompt_ru.config(text=self.current_task["prompt_ru"])
        self.prompt_pl.config(text=self.current_task["prompt_pl"])
        self.entry.delete(0, tk.END)

        self.entry.pack_forget()
        self.choice_frame.pack_forget()
        self.check_btn.grid_remove()
        self.next_btn.grid_remove()

        task_type = self.current_task["type"]
        if task_type == "input":
            self.entry.pack(ipady=8, ipadx=10)
            self.check_btn.grid()
            self.root.after(80, self.focus_entry)
            self.status_label.config(text="Введите ответ / Wpisz odpowiedź", fg=TEXT)
        elif task_type == "choice":
            for i, btn in enumerate(self.choice_buttons):
                btn.config(text=self.current_task["options"][i], state="normal")
            self.choice_frame.pack(pady=8)
            self.status_label.config(text="Выберите ответ / Wybierz odpowiedź", fg=TEXT)
        else:
            self.next_btn.grid()
            self.start_recording_if_needed()
            self.status_label.config(text="Прочитай вслух и нажми кнопку / Przeczytaj na głos i kliknij", fg=TEXT)

        speak_async_windows(self.current_task.get("voice_text", ""))

    def reward_for_correct(self):
        task_type = self.current_task.get("type", "input")
        self.stats["total_tasks_completed"] += 1
        self.stats["correct_by_type"][task_type] = self.stats["correct_by_type"].get(task_type, 0) + 1
        self.add_coins(COINS_PER_TASK, f"task_{task_type}")
        save_stats(self.stats)
        self.status_label.config(text=f"Верно! +{COINS_PER_TASK} монет 🪙", fg=ACCENT_2)

    def check_answer(self):
        if not self.current_task or self.current_task["type"] != "input":
            return
        user_answer = self.entry.get().strip().lower()
        good_answer = str(self.current_task["answer"]).strip().lower()
        if user_answer == good_answer:
            self.after_correct()
        else:
            self.flash_bad("Попробуй ещё раз / Spróbuj jeszcze raz")
            self.root.after(50, self.focus_entry)

    def check_choice(self, idx):
        if not self.current_task or self.current_task["type"] != "choice":
            return
        chosen = self.choice_buttons[idx].cget("text").strip().lower()
        good_answer = str(self.current_task["answer"]).strip().lower()
        if chosen == good_answer:
            self.after_correct()
        else:
            self.flash_bad("Попробуй ещё раз / Spróbuj jeszcze raz")

    def mark_button_done(self):
        if self.current_task and self.current_task["type"] == "button":
            self.after_correct()

    def after_correct(self):
        self.reward_for_correct()
        if self.task_index >= TASKS_PER_BREAK and not self.lang_queue:
            self.root.after(450, self.finish_break)
        else:
            self.root.after(450, self.load_next_task)

    def flash_bad(self, msg):
        self.status_label.config(text=msg, fg=BAD)
        self.root.after(1200, lambda: self.status_label.config(text=self.progress_label.cget("text"), fg=TEXT) if self.break_active else None)

    def tick(self):
        if self.selected_grade and not self.break_active:
            seconds_left = int(max(0, (self.next_break_ts or time.time()) - time.time()))
            mins = seconds_left // 60
            secs = seconds_left % 60
            self.status_label.config(text=f"Следующее задание через {mins:02d}:{secs:02d}", fg=TEXT)
            if time.time() >= (self.next_break_ts or 0):
                self.start_break()
        self.root.after(1000, self.tick)


def main():
    root = tk.Tk()
    app = HomeworkOverlay(root)
    root.mainloop()


if __name__ == "__main__":
    main()
