import tkinter as tk
from tkinter import messagebox
import random
import time
import ctypes
import os
import wave
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

# Более спокойная палитра
WINDOW_BG = "#EAF0F4"
CARD_BG = "#F8FAFC"
PANEL_BG = "#EEF3F7"
ACCENT = "#6A8CAF"
ACCENT_2 = "#7CA982"
ACCENT_3 = "#CFAF75"
BAD = "#C06C84"
TEXT = "#28323C"
SUBTEXT = "#5E6A75"
SOFT_BORDER = "#D6E0E8"

APP_DIR = Path(__file__).resolve().parent
PREFERRED_RECORDINGS_DIR = APP_DIR / "recordings"


def get_recordings_dir():
    try:
        PREFERRED_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        test_file = PREFERRED_RECORDINGS_DIR / ".write_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return str(PREFERRED_RECORDINGS_DIR)
    except Exception:
        fallback = Path.home() / "Documents" / "MinecraftCoachRecordings"
        fallback.mkdir(parents=True, exist_ok=True)
        return str(fallback)


RECORDINGS_DIR = get_recordings_dir()

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
        "reading_ru": ["Сначала подумай, потом отвечай спокойно и внимательно.", "Мы тренируем чтение, математику и логику."],
        "reading_pl": ["Najpierw pomyśl, a potem odpowiedz spokojnie i uważnie.", "Ćwiczymy czytanie, matematykę i logikę."],
    },
}

RU_WORDS = {
    1: [("к_т", "о", "кот"), ("д_м", "о", "дом"), ("л_с", "е", "лес"), ("м_ч", "я", "мяч")],
    2: [("к_нига", "н", "книга"), ("з_ма", "и", "зима"), ("тр_ва", "а", "трава"), ("р_ка", "е", "река")],
    3: [("уч_ник", "е", "ученик"), ("к_рабль", "о", "корабль"), ("р_бота", "а", "работа")],
    4: [("пр_рода", "и", "природа"), ("инт_ресно", "е", "интересно"), ("пут_шествие", "е", "путешествие")],
}

PL_WORDS = {
    1: [("d_m", "o", "dom"), ("k_t", "o", "kot"), ("l_s", "a", "las"), ("b_t", "u", "but")],
    2: [("szk_ła", "o", "szkoła"), ("r_ka", "ę", "ręka"), ("ksi_żka", "ą", "książka")],
    3: [("przyjaci_l", "e", "przyjaciel"), ("sam_chód", "o", "samochód"), ("rodz_na", "i", "rodzina")],
    4: [("nauczyci_l", "e", "nauczyciel"), ("interesuj_cy", "ą", "interesujący"), ("matemat_ka", "y", "matematyka")],
}

RIDDLES_BY_GRADE = {
    1: [
        {"q_ru": "Что больше: 5 или 3?", "q_pl": "Co jest większe: 5 czy 3?", "opts": ["5", "3", "одинаково"], "a": "5"},
        {"q_ru": "У треугольника сколько углов?", "q_pl": "Ile kątów ma trójkąt?", "opts": ["2", "3", "4"], "a": "3"},
    ],
    2: [
        {"q_ru": "Продолжи: 2, 4, 6, ...", "q_pl": "Dokończ: 2, 4, 6, ...", "opts": ["7", "8", "10"], "a": "8"},
        {"q_ru": "Что лишнее: круг, квадрат, яблоко?", "q_pl": "Co nie pasuje: koło, kwadrat, jabłko?", "opts": ["круг", "квадрат", "яблоко"], "a": "яблоко"},
    ],
    3: [
        {"q_ru": "Если сегодня вторник, какой день будет после завтра?", "q_pl": "Jeśli dziś jest wtorek, jaki dzień będzie pojutrze?", "opts": ["среда", "четверг", "пятница"], "a": "четверг"},
        {"q_ru": "Продолжи: 3, 6, 9, ...", "q_pl": "Dokończ: 3, 6, 9, ...", "opts": ["10", "12", "15"], "a": "12"},
    ],
    4: [
        {"q_ru": "У Маши 12 яблок. Она дала 3 и ещё 2. Сколько осталось?", "q_pl": "Masza miała 12 jabłek. Dała 3 i jeszcze 2. Ile zostało?", "opts": ["5", "7", "9"], "a": "7"},
        {"q_ru": "Какое число делится на 2 и на 3?", "q_pl": "Która liczba dzieli się przez 2 i przez 3?", "opts": ["8", "12", "15"], "a": "12"},
    ],
}

LANGUAGE_SEQUENCE = ["ru", "pl"]


def pick_grade_items(mapping, grade):
    candidates = []
    for g in range(1, grade + 1):
        candidates.extend(mapping.get(g, []))
    return candidates


class TaskFactory:
    @staticmethod
    def build_bilingual(title_ru, title_pl, prompt_ru, prompt_pl, hint_ru, hint_pl, task_type, answer=None, options=None, record_audio=False):
        return {
            "type": task_type,
            "title_ru": title_ru,
            "title_pl": title_pl,
            "prompt_ru": prompt_ru,
            "prompt_pl": prompt_pl,
            "hint_ru": hint_ru,
            "hint_pl": hint_pl,
            "answer": answer,
            "options": options or [],
            "record_audio": record_audio,
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
            "Впиши ответ цифрами.", "Wpisz odpowiedź cyframi.",
            task_type="input", answer=answer,
        )

    @staticmethod
    def make_spelling_task(grade, focus_lang):
        if focus_lang == "ru":
            masked, missing, full = random.choice(pick_grade_items(RU_WORDS, grade))
            return TaskFactory.build_bilingual(
                "Русский язык", "Język rosyjski",
                f"Вставь букву: {masked}", f"Wstaw literę w rosyjskim słowie: {masked}",
                f"Подумай, какое слово получится.", f"Pomyśl, jakie powstanie słowo.",
                task_type="input", answer=missing,
            )
        masked, missing, full = random.choice(pick_grade_items(PL_WORDS, grade))
        return TaskFactory.build_bilingual(
            "Польский язык", "Język polski",
            f"Вставь букву в польское слово: {masked}", f"Wstaw literę: {masked}",
            "Подумай, какое слово получится.", "Pomyśl, jakie powstanie słowo.",
            task_type="input", answer=missing,
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
            "Нажми на правильный вариант.", "Kliknij poprawną odpowiedź.",
            task_type="choice", answer=answer.lower(), options=options,
        )

    @staticmethod
    def make_reading_task(grade, focus_lang):
        cfg = GRADE_CONFIGS[grade]
        if focus_lang == "ru":
            text = random.choice(cfg["reading_ru"])
            return TaskFactory.build_bilingual(
                "Чтение вслух", "Czytanie na głos",
                f"Прочитай вслух:\n\n{text}", f"Przeczytaj po rosyjsku na głos:\n\n{text}",
                "Идёт запись с микрофона. Нажми кнопку после чтения.",
                "Trwa nagrywanie z mikrofonu. Kliknij przycisk po przeczytaniu.",
                task_type="button", answer="ok", record_audio=True,
            )
        text = random.choice(cfg["reading_pl"])
        return TaskFactory.build_bilingual(
            "Чтение вслух", "Czytanie na głos",
            f"Прочитай по-польски вслух:\n\n{text}", f"Przeczytaj na głos:\n\n{text}",
            "Идёт запись с микрофона. Нажми кнопку после чтения.",
            "Trwa nagrywanie z mikrofonu. Kliknij przycisk po przeczytaniu.",
            task_type="button", answer="ok", record_audio=True,
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


class HintGateDialog(tk.Toplevel):
    def __init__(self, parent, grade, on_success):
        super().__init__(parent)
        self.parent = parent
        self.grade = grade
        self.on_success = on_success
        self.configure(bg=PANEL_BG)
        self.title("Подсказка / Wskazówka")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        riddle = random.choice(RIDDLES_BY_GRADE[grade])
        self.answer = str(riddle["a"]).strip().lower()

        wrapper = tk.Frame(self, bg=CARD_BG, bd=1, highlightthickness=1, highlightbackground=SOFT_BORDER)
        wrapper.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(wrapper, text="Открыть подсказку", font=("Arial", 18, "bold"), bg=CARD_BG, fg=TEXT).pack(pady=(12, 6))
        tk.Label(wrapper, text="Разгадай логическую загадку", font=("Arial", 12), bg=CARD_BG, fg=SUBTEXT).pack()
        tk.Label(wrapper, text="Odblokuj wskazówkę: rozwiąż zagadkę logiczną", font=("Arial", 12), bg=CARD_BG, fg=SUBTEXT).pack(pady=(0, 10))

        tk.Label(wrapper, text=riddle["q_ru"], font=("Arial", 15, "bold"), bg=CARD_BG, fg=TEXT, wraplength=520).pack(pady=(8, 4))
        tk.Label(wrapper, text=riddle["q_pl"], font=("Arial", 14), bg=CARD_BG, fg=SUBTEXT, wraplength=520).pack(pady=(0, 10))

        btns = tk.Frame(wrapper, bg=CARD_BG)
        btns.pack(pady=(4, 14))
        for opt in riddle["opts"]:
            tk.Button(
                btns,
                text=str(opt),
                font=("Arial", 14, "bold"),
                bg=ACCENT,
                fg="white",
                activebackground=ACCENT,
                padx=18,
                pady=10,
                command=lambda v=opt: self.check(v),
            ).pack(side="left", padx=6)

        self.status = tk.Label(wrapper, text="", font=("Arial", 12, "bold"), bg=CARD_BG, fg=BAD)
        self.status.pack(pady=(0, 12))

        self.update_idletasks()
        self.geometry(f"580x300+{max(80, self.winfo_screenwidth()//2-290)}+{max(80, self.winfo_screenheight()//2-150)}")
        self.grab_set()
        self.focus_force()

    def check(self, value):
        if str(value).strip().lower() == self.answer:
            try:
                self.on_success()
            finally:
                self.close()
        else:
            self.status.config(text="Неверно. Подумай ещё. / Niepoprawnie. Spróbuj jeszcze raz.")

    def close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


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
        self.hint_shown = False

        self.build_ui()
        self.show_level_screen()
        self.tick()

    def build_ui(self):
        self.main = tk.Frame(self.root, bg=WINDOW_BG)
        self.main.pack(fill="both", expand=True)

        self.card = tk.Frame(self.main, bg=CARD_BG, bd=0, highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.88)

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

        self.hint_frame = tk.Frame(self.card, bg=CARD_BG)
        self.hint_frame.pack(fill="x", padx=24, pady=(0, 8))
        self.hint_btn = tk.Button(
            self.hint_frame,
            text="Открыть подсказку / Otwórz wskazówkę",
            font=("Arial", 13, "bold"),
            bg=ACCENT_3,
            fg="white",
            activebackground=ACCENT_3,
            padx=18,
            pady=8,
            command=self.open_hint_gate,
        )
        self.hint_btn.pack()
        self.hint_ru = tk.Label(self.hint_frame, text="", font=("Arial", 13), bg=CARD_BG, fg=SUBTEXT, wraplength=1100)
        self.hint_pl = tk.Label(self.hint_frame, text="", font=("Arial", 13), bg=CARD_BG, fg=SUBTEXT, wraplength=1100)

        self.input_area = tk.Frame(self.card, bg=CARD_BG)
        self.input_area.pack(pady=(4, 6))
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
        self.start_screen.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.76)

        start_card = tk.Frame(self.start_screen, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        start_card.pack(fill="both", expand=True)
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
        self.start_screen.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.76)
        self.status_label.config(text="Сначала выберите класс / Najpierw wybierz klasę", fg=TEXT)

    def hide_task_card(self):
        self.card.place_forget()

    def show_task_card(self):
        self.start_screen.place_forget()
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.88)

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
        self.status_label.config(text="Молодец! Можно дальше играть 🎮", fg=TEXT)
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
            self.recording_path = os.path.join(RECORDINGS_DIR, f"grade{self.selected_grade}_{focus}_{now}")
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

    def open_hint_gate(self):
        if not self.break_active or self.hint_shown or not self.selected_grade:
            return
        HintGateDialog(self.root, self.selected_grade, self.reveal_hint)

    def reveal_hint(self):
        if not self.current_task:
            return
        self.hint_shown = True
        self.hint_ru.config(text=f"Подсказка: {self.current_task['hint_ru']}")
        self.hint_pl.config(text=f"Wskazówka: {self.current_task['hint_pl']}")
        self.hint_ru.pack()
        self.hint_pl.pack(pady=(2, 0))
        self.hint_btn.config(state="disabled", text="Подсказка открыта / Wskazówka odblokowana")

    def load_next_task(self):
        self.stop_recording_if_needed()
        if not self.lang_queue:
            self.finish_break()
            return

        focus_lang = self.lang_queue.pop(0)
        self.current_task = TaskFactory.random_task(self.selected_grade, focus_lang)
        self.task_index += 1
        self.hint_shown = False
        self.hint_ru.pack_forget()
        self.hint_pl.pack_forget()
        self.hint_btn.config(state="normal", text="Открыть подсказку / Otwórz wskazówkę")

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
        if self.task_index >= TASKS_PER_BREAK and not self.lang_queue:
            self.finish_break()
        else:
            self.load_next_task()

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
