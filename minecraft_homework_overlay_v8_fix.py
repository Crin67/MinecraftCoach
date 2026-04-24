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
COINS_PENALTY_WRONG = 1
SECONDS_PENALTY_WRONG = 30

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
CUSTOM_TASKS_FILE = DATA_DIR / "custom_tasks.json"

LOG_FILE = DATA_DIR / "app_log.txt"


DEFAULT_EDITABLE_TASKS = [
    {
        "task_id": "g1_add_1", "grade": 1, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 3 + 2?", "prompt_pl": "Ile będzie 3 + 2?",
        "answer": "5", "options": ["4", "6", "7", "5"],
        "record_audio": False, "voice_text": "Реши задание и нажми кнопку проверки.", "source": "built_in"
    },
    {
        "task_id": "g1_spell_ru_1", "grade": 1, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wpisz literę",
        "prompt_ru": "Вставь букву: к_т", "prompt_pl": "Wstaw literę: k_t",
        "answer": "о", "options": [],
        "record_audio": False, "voice_text": "Впиши правильную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g1_read_1", "grade": 1, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "мама", "prompt_pl": "mama",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_add_1", "grade": 2, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 12 + 7?", "prompt_pl": "Ile będzie 12 + 7?",
        "answer": "19", "options": ["17", "18", "19", "20"],
        "record_audio": False, "voice_text": "Реши пример и выбери правильный ответ.", "source": "built_in"
    },
    {
        "task_id": "g2_spell_pl_1", "grade": 2, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wpisz literę",
        "prompt_ru": "Польское слово: szk_ła", "prompt_pl": "Polskie słowo: szk_ła",
        "answer": "o", "options": [],
        "record_audio": False, "voice_text": "Впиши правильную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_read_1", "grade": 2, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Кот спит.", "prompt_pl": "Kot śpi.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g3_mul_1", "grade": 3, "type": "choice",
        "title_ru": "Таблица умножения", "title_pl": "Tabliczka mnożenia",
        "prompt_ru": "Сколько будет 4 × 3?", "prompt_pl": "Ile będzie 4 × 3?",
        "answer": "12", "options": ["7", "9", "12", "14"],
        "record_audio": False, "voice_text": "Реши пример и выбери ответ.", "source": "built_in"
    },
    {
        "task_id": "g3_div_1", "grade": 3, "type": "input",
        "title_ru": "Раздели", "title_pl": "Podziel",
        "prompt_ru": "Сколько будет 15 : 3?", "prompt_pl": "Ile będzie 15 : 3?",
        "answer": "5", "options": [],
        "record_audio": False, "voice_text": "Введи ответ и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g4_mul_1", "grade": 4, "type": "choice",
        "title_ru": "Таблица умножения", "title_pl": "Tabliczka mnożenia",
        "prompt_ru": "Сколько будет 7 × 8?", "prompt_pl": "Ile będzie 7 × 8?",
        "answer": "56", "options": ["48", "54", "56", "64"],
        "record_audio": False, "voice_text": "Реши пример и выбери ответ.", "source": "built_in"
    },
    {
        "task_id": "g4_read_1", "grade": 4, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Сегодня мы внимательно читаем и думаем.", "prompt_pl": "Dzisiaj uważnie czytamy i myślimy.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
]

def log_message(text):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except Exception:
        pass

def install_exception_logger():
    import sys, traceback
    def _hook(exc_type, exc, tb):
        msg = "".join(traceback.format_exception(exc_type, exc, tb))
        log_message(msg)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(APP_TITLE, f"Программа упала. Лог сохранён:\n{LOG_FILE}\n\n{exc}")
            root.destroy()
        except Exception:
            pass
    sys.excepthook = _hook



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
        "wrong_answers": 0,
        "time_penalty_seconds": 0,
        "correct_by_type": {"input": 0, "choice": 0, "button": 0},
        "history": [],
    }
    try:
        if STATS_FILE.exists():
            data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
            default.update(data)
            if "correct_by_type" not in default:
                default["correct_by_type"] = {"input": 0, "choice": 0, "button": 0}
            if "wrong_answers" not in default:
                default["wrong_answers"] = 0
            if "time_penalty_seconds" not in default:
                default["time_penalty_seconds"] = 0
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


def make_task_id(prefix="task"):
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


def normalize_task_dict(item, *, fallback_source="custom"):
    task_type = str(item.get("type", "input") or "input")
    task_id = str(item.get("task_id") or make_task_id(fallback_source))
    record_audio = bool(item.get("record_audio", False))
    title_ru = str(item.get("title_ru", "") or "")
    title_pl = str(item.get("title_pl", "") or "")
    prompt_ru = str(item.get("prompt_ru", "") or "")
    prompt_pl = str(item.get("prompt_pl", "") or "")
    answer = str(item.get("answer", "") or "")
    if task_type == "button" and not answer:
        answer = "ok"
    voice_text = str(item.get("voice_text", "") or "")
    if not voice_text:
        voice_text = "Прочитай, что написано, и нажми на кнопку." if task_type == "button" else "Сделай задание и нажми кнопку."
    options_val = item.get("options", [])
    options = [str(x) for x in options_val] if isinstance(options_val, list) else []
    return {
        "task_id": task_id,
        "grade": int(item.get("grade", 1) or 1),
        "type": task_type,
        "title_ru": title_ru,
        "title_pl": title_pl,
        "prompt_ru": prompt_ru,
        "prompt_pl": prompt_pl,
        "answer": answer,
        "options": options,
        "record_audio": record_audio,
        "voice_text": voice_text,
        "source": str(item.get("source", fallback_source) or fallback_source),
    }


def load_custom_tasks():
    merged = {}
    for item in DEFAULT_EDITABLE_TASKS:
        task = normalize_task_dict(item, fallback_source="built_in")
        merged[task["task_id"]] = task
    try:
        if CUSTOM_TASKS_FILE.exists():
            data = json.loads(CUSTOM_TASKS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    task = normalize_task_dict(item, fallback_source="custom")
                    merged[task["task_id"]] = task
    except Exception as e:
        log_message(f"load_custom_tasks error: {e}")
    return list(merged.values())


def save_custom_tasks(tasks):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        safe_tasks = [normalize_task_dict(item, fallback_source=str(item.get("source", "custom") if isinstance(item, dict) else "custom")) for item in (tasks or []) if isinstance(item, dict)]
        CUSTOM_TASKS_FILE.write_text(json.dumps(safe_tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log_message(f"save_custom_tasks error: {e}")




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
    def task_from_dict(data):
        return TaskFactory.build_bilingual(
            data.get("title_ru", "Задание"),
            data.get("title_pl", "Zadanie"),
            data.get("prompt_ru", ""),
            data.get("prompt_pl", ""),
            task_type=data.get("type", "input"),
            answer=str(data.get("answer", "")),
            options=data.get("options", []),
            record_audio=bool(data.get("record_audio", False)),
            voice_text=data.get("voice_text") or "Сделай задание и нажми кнопку.",
        )

    @staticmethod
    def random_task(grade, focus_lang, custom_tasks=None):
        custom_tasks = custom_tasks or []
        matching_custom = [t for t in custom_tasks if int(t.get("grade", 1)) == grade]
        if matching_custom and random.random() < 0.7:
            return TaskFactory.task_from_dict(random.choice(matching_custom))

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
    def __init__(self, parent, coins, on_close=None):
        super().__init__(parent)
        self.parent = parent
        self.coins = coins
        self.on_close = on_close
        self.configure(bg=WINDOW_BG)
        self.title("Магазин / Sklep")
        self.attributes("-topmost", True)
        self.transient(parent)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        wrapper_shadow = tk.Frame(self, bg=SHADOW)
        wrapper_shadow.pack(padx=18, pady=18)
        wrapper = tk.Frame(wrapper_shadow, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        wrapper.pack(padx=(0, 4), pady=(0, 4))

        header = tk.Frame(wrapper, bg=CARD_BG)
        header.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(header, text="Магазин наград / Sklep nagród", font=("Arial", 20, "bold"), bg=CARD_BG, fg=TEXT).pack(side="left")
        tk.Button(header, text="✕", command=self.close, font=("Arial", 14, "bold"), bg=CARD_BG, fg=SUBTEXT, relief="flat", bd=0).pack(side="right", padx=(12, 0))
        tk.Label(header, text=f"Монетки: {coins}", font=("Arial", 14, "bold"), bg=CARD_BG, fg=ACCENT_3).pack(side="right")

        tk.Label(wrapper, text="Карточки-заглушки. Позже сюда можно добавить настоящие награды.", font=("Arial", 12), bg=CARD_BG, fg=SUBTEXT).pack(padx=18, pady=(0, 12), anchor="w")

        grid = tk.Frame(wrapper, bg=CARD_BG)
        grid.pack(padx=18, pady=(0, 18))
        prices = [20, 35, 50, 75, 100, 150]
        for i, price in enumerate(prices):
            cell_shadow = tk.Frame(grid, bg=SHADOW)
            cell_shadow.grid(row=i // 3, column=i % 3, padx=12, pady=12)
            cell = tk.Frame(cell_shadow, bg="#FFF8E1", width=250, height=185, highlightthickness=1, highlightbackground="#E7D18E")
            cell.pack(padx=(0, 4), pady=(0, 4))
            cell.pack_propagate(False)
            tk.Label(cell, text="?", font=("Arial", 42, "bold"), bg="#FFF8E1", fg="#C8A740").pack(pady=(18, 8))
            tk.Label(cell, text="Секретная награда", font=("Arial", 13, "bold"), bg="#FFF8E1", fg=TEXT).pack()
            tk.Label(cell, text=f"Цена: {price} монет", font=("Arial", 11), bg="#FFF8E1", fg=SUBTEXT).pack(pady=(6, 12))
            tk.Button(cell, text="Скоро", font=("Arial", 11, "bold"), bg=ACCENT_3, fg="white", activebackground=ACCENT_3, state="disabled").pack()

        bottom = tk.Frame(wrapper, bg=CARD_BG)
        bottom.pack(fill="x", padx=18, pady=(0, 16))
        tk.Button(bottom, text="Закрыть / Zamknij", font=("Arial", 13, "bold"), bg=ACCENT, fg="white", activebackground=ACCENT, padx=18, pady=8, command=self.close).pack(side="right")

        self.update_idletasks()
        w = 920
        h = 560
        x = max(60, self.winfo_screenwidth() // 2 - w // 2)
        y = max(50, self.winfo_screenheight() // 2 - h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.focus_force()

    def close(self):
        try:
            if callable(self.on_close):
                self.on_close()
        finally:
            self.destroy()


class StatsDialog(tk.Toplevel):
    def __init__(self, parent, stats, on_close=None):
        super().__init__(parent)
        self.on_close = on_close
        self.title("Статистика / Statystyki")
        self.configure(bg=WINDOW_BG)
        self.attributes("-topmost", True)
        self.transient(parent)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

        shadow = tk.Frame(self, bg=SHADOW)
        shadow.pack(padx=18, pady=18)
        wrapper = tk.Frame(shadow, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        wrapper.pack(padx=(0, 4), pady=(0, 4))

        header = tk.Frame(wrapper, bg=CARD_BG)
        header.pack(fill="x", padx=18, pady=(18, 10))
        tk.Label(header, text="Статистика ребёнка", font=("Arial", 20, "bold"), bg=CARD_BG, fg=TEXT).pack(side="left")
        tk.Button(header, text="✕", command=self.close, font=("Arial", 14, "bold"), bg=CARD_BG, fg=SUBTEXT, relief="flat", bd=0).pack(side="right")

        info = [
            f"Монетки: {stats['coins']}",
            f"Решено заданий: {stats['total_tasks_completed']}",
            f"Завершено игровых пауз: {stats['total_breaks_completed']}",
            f"Ошибок: {stats.get('wrong_answers', 0)}",
            f"Начислено штрафного времени: {stats.get('time_penalty_seconds', 0)} сек.",
            f"Правильных заданий с вводом: {stats['correct_by_type'].get('input', 0)}",
            f"Правильных заданий с выбором: {stats['correct_by_type'].get('choice', 0)}",
            f"Прочитано вслух заданий: {stats['correct_by_type'].get('button', 0)}",
            f"Файл статистики: {STATS_FILE}",
        ]
        for line in info:
            tk.Label(wrapper, text=line, font=("Arial", 13), bg=CARD_BG, fg=TEXT, justify="left").pack(anchor="w", padx=18, pady=4)

        tk.Button(wrapper, text="Закрыть / Zamknij", font=("Arial", 13, "bold"), bg=ACCENT, fg="white", activebackground=ACCENT, padx=18, pady=8, command=self.close).pack(pady=18)

        self.update_idletasks()
        w = 700
        h = 380
        x = max(80, self.winfo_screenwidth() // 2 - w // 2)
        y = max(60, self.winfo_screenheight() // 2 - h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.focus_force()

    def close(self):
        try:
            if callable(self.on_close):
                self.on_close()
        finally:
            self.destroy()


class TaskEditorDialog(tk.Toplevel):
    def __init__(self, parent, tasks, on_save, current_task=None, current_grade=1, on_close=None):
        super().__init__(parent)
        self.parent = parent
        self.on_save = on_save
        self.on_close = on_close
        self.tasks = [normalize_task_dict(t, fallback_source=str(t.get("source", "custom"))) for t in tasks]
        self.current_task = current_task
        self.configure(bg=WINDOW_BG)
        self.title("Редактор заданий / Edytor zadań")
        self.attributes("-topmost", True)
        self.transient(parent)
        self.geometry("1280x780+60+50")
        self.protocol("WM_DELETE_WINDOW", self.close)

        outer = tk.Frame(self, bg=WINDOW_BG)
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        left = tk.Frame(outer, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        left.pack(side="left", fill="y")
        right = tk.Frame(outer, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        right.pack(side="left", fill="both", expand=True, padx=(16, 0))

        header_left = tk.Frame(left, bg=CARD_BG)
        header_left.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(header_left, text="Список заданий", font=("Arial", 16, "bold"), bg=CARD_BG, fg=TEXT).pack(side="left")
        tk.Button(header_left, text="✕", command=self.close, bg=CARD_BG, fg=SUBTEXT, relief="flat", font=("Arial", 12, "bold")).pack(side="right")

        self.filter_var = tk.StringVar(value="Все")
        filter_bar = tk.Frame(left, bg=CARD_BG)
        filter_bar.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(filter_bar, text="Фильтр:", bg=CARD_BG, fg=TEXT, font=("Arial", 10, "bold")).pack(side="left")
        tk.OptionMenu(filter_bar, self.filter_var, "Все", "built_in", "custom", command=lambda *_: self.refresh_list()).pack(side="left", padx=8)

        self.listbox = tk.Listbox(left, width=40, font=("Arial", 11))
        self.listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        buttons = tk.Frame(left, bg=CARD_BG)
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(buttons, text="Новое", command=self.new_task, bg=ACCENT, fg="white", relief="flat", font=("Arial", 11, "bold")).pack(fill="x", pady=4)
        tk.Button(buttons, text="Из текущего задания", command=self.copy_current_task, bg=ACCENT_2, fg="white", relief="flat", font=("Arial", 11, "bold")).pack(fill="x", pady=4)
        tk.Button(buttons, text="Удалить", command=self.delete_task, bg=BAD, fg="white", relief="flat", font=("Arial", 11, "bold")).pack(fill="x", pady=4)

        form = tk.Frame(right, bg=CARD_BG)
        form.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(form, text="Добавление и редактирование заданий", font=("Arial", 18, "bold"), bg=CARD_BG, fg=TEXT).pack(anchor="w", pady=(0, 8))
        tk.Label(form, text=f"Файл: {CUSTOM_TASKS_FILE}", font=("Arial", 10), bg=CARD_BG, fg=SUBTEXT).pack(anchor="w", pady=(0, 12))

        meta = tk.Frame(form, bg=CARD_BG)
        meta.pack(fill="x")
        for i in range(6):
            meta.grid_columnconfigure(i, weight=1)

        def mk_label(row, col, text_):
            tk.Label(meta, text=text_, font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=row, column=col, sticky="w", padx=6, pady=(6, 2))

        mk_label(0, 0, "Класс")
        self.grade_var = tk.StringVar(value=str(current_grade))
        tk.OptionMenu(meta, self.grade_var, "1", "2", "3", "4").grid(row=1, column=0, sticky="ew", padx=6)

        mk_label(0, 1, "Тип")
        self.type_var = tk.StringVar(value="input")
        tk.OptionMenu(meta, self.type_var, "input", "choice", "button").grid(row=1, column=1, sticky="ew", padx=6)

        mk_label(0, 2, "Ответ")
        self.answer_entry = tk.Entry(meta, font=("Arial", 12))
        self.answer_entry.grid(row=1, column=2, sticky="ew", padx=6)

        mk_label(0, 3, "Варианты")
        self.options_entry = tk.Entry(meta, font=("Arial", 12))
        self.options_entry.grid(row=1, column=3, sticky="ew", padx=6)

        mk_label(0, 4, "Источник")
        self.source_var = tk.StringVar(value="custom")
        tk.OptionMenu(meta, self.source_var, "custom", "built_in").grid(row=1, column=4, sticky="ew", padx=6)

        mk_label(0, 5, "ID")
        self.task_id_label = tk.Label(meta, text="—", bg=CARD_BG, fg=SUBTEXT, font=("Arial", 11))
        self.task_id_label.grid(row=1, column=5, sticky="w", padx=6)

        fields = tk.Frame(form, bg=CARD_BG)
        fields.pack(fill="both", expand=True, pady=(12, 0))
        fields.grid_columnconfigure(0, weight=1)
        fields.grid_columnconfigure(1, weight=1)

        tk.Label(fields, text="Заголовок RU", font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=0, column=0, sticky="w", padx=6)
        tk.Label(fields, text="Zagłówek PL", font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=0, column=1, sticky="w", padx=6)
        self.title_ru = tk.Entry(fields, font=("Arial", 12))
        self.title_pl = tk.Entry(fields, font=("Arial", 12))
        self.title_ru.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))
        self.title_pl.grid(row=1, column=1, sticky="ew", padx=6, pady=(0, 10))

        tk.Label(fields, text="Текст слева (русский)", font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=2, column=0, sticky="w", padx=6)
        tk.Label(fields, text="Текст справа (polski)", font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=2, column=1, sticky="w", padx=6)
        self.prompt_ru = tk.Text(fields, height=10, font=("Arial", 12), wrap="word")
        self.prompt_pl = tk.Text(fields, height=10, font=("Arial", 12), wrap="word")
        self.prompt_ru.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 10))
        self.prompt_pl.grid(row=3, column=1, sticky="nsew", padx=6, pady=(0, 10))
        fields.grid_rowconfigure(3, weight=1)

        tk.Label(fields, text="Голосовая фраза", font=("Arial", 11, "bold"), bg=CARD_BG, fg=TEXT).grid(row=4, column=0, sticky="w", padx=6)
        self.voice_entry = tk.Entry(fields, font=("Arial", 12))
        self.voice_entry.grid(row=5, column=0, sticky="ew", padx=6, pady=(0, 8))
        self.record_var = tk.BooleanVar(value=False)
        tk.Checkbutton(fields, text="Записывать микрофон", variable=self.record_var, bg=CARD_BG, fg=TEXT, activebackground=CARD_BG).grid(row=5, column=1, sticky="w", padx=6)

        action_bar = tk.Frame(form, bg=CARD_BG)
        action_bar.pack(fill="x", pady=(10, 0))
        tk.Button(action_bar, text="Сохранить запись", command=self.save_current, bg=ACCENT_2, fg="white", relief="flat", font=("Arial", 12, "bold"), padx=12, pady=8).pack(side="left")
        tk.Button(action_bar, text="Сохранить всё и закрыть", command=self.save_all_and_close, bg=ACCENT, fg="white", relief="flat", font=("Arial", 12, "bold"), padx=12, pady=8).pack(side="left", padx=10)
        tk.Button(action_bar, text="Закрыть", command=self.close, bg="#9AA8B5", fg="white", relief="flat", font=("Arial", 12, "bold"), padx=12, pady=8).pack(side="right")

        self.selected_index = None
        self.filtered_indices = []
        self.refresh_list()
        if self.tasks:
            self.listbox.selection_set(0)
            self.on_select()
        else:
            self.new_task()

    def close(self):
        try:
            if callable(self.on_close):
                self.on_close()
        finally:
            self.destroy()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.filtered_indices = []
        mode = self.filter_var.get()
        for idx, task in enumerate(self.tasks):
            src_name = task.get("source", "custom")
            if mode != "Все" and src_name != mode:
                continue
            label = f"[{src_name}] [{task.get('grade',1)} кл] {task.get('title_ru','Без названия')}"
            self.filtered_indices.append(idx)
            self.listbox.insert(tk.END, label)

    def clear_form(self):
        self.grade_var.set("1")
        self.type_var.set("input")
        self.source_var.set("custom")
        self.task_id_label.config(text="—")
        for e in [self.answer_entry, self.options_entry, self.title_ru, self.title_pl, self.voice_entry]:
            e.delete(0, tk.END)
        self.prompt_ru.delete("1.0", tk.END)
        self.prompt_pl.delete("1.0", tk.END)
        self.record_var.set(False)
        self.selected_index = None

    def task_from_form(self):
        options = [x.strip() for x in self.options_entry.get().split(",") if x.strip()]
        task_id = self.task_id_label.cget("text")
        if task_id == "—":
            task_id = make_task_id(self.source_var.get())
        task = {
            "task_id": task_id,
            "grade": int(self.grade_var.get() or 1),
            "type": self.type_var.get().strip() or "input",
            "title_ru": self.title_ru.get().strip() or "Задание",
            "title_pl": self.title_pl.get().strip() or "Zadanie",
            "prompt_ru": self.prompt_ru.get("1.0", tk.END).strip(),
            "prompt_pl": self.prompt_pl.get("1.0", tk.END).strip(),
            "answer": self.answer_entry.get().strip(),
            "options": options,
            "record_audio": bool(self.record_var.get()),
            "voice_text": self.voice_entry.get().strip() or ("Прочитай, что написано, и нажми на кнопку." if self.type_var.get() == "button" else "Сделай задание и нажми кнопку."),
            "source": self.source_var.get(),
        }
        return normalize_task_dict(task, fallback_source=self.source_var.get())

    def fill_form(self, task):
        self.clear_form()
        self.task_id_label.config(text=task.get("task_id", "—"))
        self.grade_var.set(str(task.get("grade",1)))
        self.type_var.set(task.get("type","input"))
        self.source_var.set(task.get("source", "custom"))
        self.answer_entry.insert(0, str(task.get("answer","")))
        self.options_entry.insert(0, ", ".join(task.get("options", [])))
        self.title_ru.insert(0, task.get("title_ru",""))
        self.title_pl.insert(0, task.get("title_pl",""))
        self.prompt_ru.insert("1.0", task.get("prompt_ru",""))
        self.prompt_pl.insert("1.0", task.get("prompt_pl",""))
        self.voice_entry.insert(0, task.get("voice_text",""))
        self.record_var.set(bool(task.get("record_audio", False)))

    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        real_idx = self.filtered_indices[sel[0]]
        self.selected_index = real_idx
        self.fill_form(self.tasks[self.selected_index])

    def new_task(self):
        self.clear_form()

    def copy_current_task(self):
        if not self.current_task:
            return
        task = normalize_task_dict(dict(self.current_task), fallback_source="custom")
        task["task_id"] = make_task_id("copy")
        task["source"] = "custom"
        task["grade"] = int(self.grade_var.get() or 1)
        self.fill_form(task)

    def save_current(self):
        task = self.task_from_form()
        if not task["prompt_ru"] or not task["prompt_pl"]:
            messagebox.showerror("Ошибка", "Заполните оба текста задания.")
            return False
        if task["type"] == "choice" and len(task["options"]) < 2:
            messagebox.showerror("Ошибка", "Для выбора нужно минимум 2 варианта.")
            return False
        if task["type"] == "button":
            task["answer"] = "ok"
        if self.selected_index is None:
            self.tasks.append(task)
            self.selected_index = len(self.tasks) - 1
        else:
            self.tasks[self.selected_index] = task
        self.refresh_list()
        try:
            view_idx = self.filtered_indices.index(self.selected_index)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(view_idx)
        except Exception:
            pass
        return True

    def delete_task(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = self.filtered_indices[sel[0]]
        del self.tasks[idx]
        self.refresh_list()
        self.clear_form()

    def save_all_and_close(self):
        if not self.save_current():
            return
        self.on_save(self.tasks)
        self.close()


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
        self.task_editor_window = None
        self.animating_card = False
        self.toast_window = None
        self.pending_penalty_seconds = 0
        self.stats = load_stats()
        self.custom_tasks = load_custom_tasks()

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

        self.tasks_btn = tk.Button(
            self.topbar,
            text="✏️ Задания",
            font=("Arial", 13, "bold"),
            bg=ACCENT_2,
            fg="white",
            activebackground=ACCENT_2,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            command=self.open_task_editor,
        )
        self.tasks_btn.pack(side="left")

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
        self.root.after(250, self.hide_overlay)

    def make_next_break_time(self):
        mins = random.randint(MIN_INTERVAL_MIN, MAX_INTERVAL_MIN)
        wait_seconds = mins * 60
        if self.pending_penalty_seconds:
            wait_seconds = max(60, wait_seconds - self.pending_penalty_seconds)
            self.pending_penalty_seconds = 0
        return time.time() + wait_seconds

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
        self.store_window = ShopDialog(self.root, self.stats["coins"], on_close=lambda: self.popup_closed("shop"))

    def open_stats(self):
        if self.stats_window and self.stats_window.winfo_exists():
            self.stats_window.lift()
            self.stats_window.focus_force()
            return
        self.stats_window = StatsDialog(self.root, self.stats, on_close=lambda: self.popup_closed("stats"))

    def save_custom_tasks_from_editor(self, tasks):
        self.custom_tasks = tasks
        save_custom_tasks(tasks)
        self.status_label.config(text=f"Задания сохранены: {len(tasks)}", fg=ACCENT_2)

    def open_task_editor(self):
        if self.task_editor_window and self.task_editor_window.winfo_exists():
            self.task_editor_window.lift()
            self.task_editor_window.focus_force()
            return
        current = self.current_task if self.break_active else None
        grade = self.selected_grade or 1
        self.task_editor_window = TaskEditorDialog(self.root, self.custom_tasks, self.save_custom_tasks_from_editor, current_task=current, current_grade=grade, on_close=lambda: self.popup_closed("editor"))

    def get_active_popup(self):
        for win in [self.store_window, self.stats_window, self.task_editor_window, self.toast_window]:
            try:
                if win and win.winfo_exists():
                    return win
            except Exception:
                pass
        return None

    def popup_closed(self, which):
        if which == "shop":
            self.store_window = None
        elif which == "stats":
            self.stats_window = None
        elif which == "editor":
            self.task_editor_window = None
        if self.break_active:
            try:
                self.root.attributes("-topmost", True)
                self.root.lift()
                if self.current_task and self.current_task.get("type") == "input":
                    self.focus_entry()
            except Exception:
                pass

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
        popup = self.get_active_popup()
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)
        if popup is None:
            self.root.attributes("-topmost", True)
            self.show_overlay()
            if self.current_task and self.current_task.get("type") == "input":
                self.focus_entry()
        else:
            try:
                self.root.attributes("-topmost", False)
                self.root.lower()
                popup.attributes("-topmost", True)
                popup.lift()
                try:
                    popup.focus_force()
                except Exception:
                    pass
            except Exception as e:
                log_message(f"Popup focus error: {e}")
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
        self.current_task = TaskFactory.random_task(self.selected_grade, focus_lang, self.custom_tasks)
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

    def show_result_popup(self, success, text):
        if self.toast_window and self.toast_window.winfo_exists():
            try:
                self.toast_window.destroy()
            except Exception:
                pass
        self.toast_window = tk.Toplevel(self.root)
        self.toast_window.overrideredirect(True)
        self.toast_window.attributes("-topmost", True)
        self.toast_window.configure(bg=SHADOW)
        inner_bg = "#E6F6EA" if success else "#FBEAEC"
        edge = ACCENT_2 if success else BAD
        icon = "✓" if success else "✕"
        inner = tk.Frame(self.toast_window, bg=inner_bg, highlightthickness=2, highlightbackground=edge)
        inner.pack(padx=(0, 4), pady=(0, 4))
        tk.Label(inner, text=icon, font=("Arial", 26, "bold"), bg=inner_bg, fg=edge).pack(pady=(14, 4), padx=30)
        tk.Label(inner, text=text, font=("Arial", 14, "bold"), bg=inner_bg, fg=TEXT, justify="center").pack(padx=24, pady=(0, 16))
        self.toast_window.update_idletasks()
        w = max(280, self.toast_window.winfo_width())
        h = max(120, self.toast_window.winfo_height())
        x = self.root.winfo_screenwidth() // 2 - w // 2
        y = max(80, self.root.winfo_screenheight() // 5)
        self.toast_window.geometry(f"{w}x{h}+{x}+{y}")
        self.root.after(1400, self.close_toast)

    def close_toast(self):
        try:
            if self.toast_window and self.toast_window.winfo_exists():
                self.toast_window.destroy()
        except Exception:
            pass
        self.toast_window = None

    def apply_wrong_penalty(self):
        self.stats["wrong_answers"] = self.stats.get("wrong_answers", 0) + 1
        self.stats["time_penalty_seconds"] = self.stats.get("time_penalty_seconds", 0) + SECONDS_PENALTY_WRONG
        self.pending_penalty_seconds += SECONDS_PENALTY_WRONG
        new_coins = max(0, self.stats.get("coins", 0) - COINS_PENALTY_WRONG)
        delta = new_coins - self.stats.get("coins", 0)
        self.stats["coins"] = new_coins
        self.stats.setdefault("history", []).append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "coins": delta,
            "reason": f"wrong_answer_penalty_{SECONDS_PENALTY_WRONG}s",
        })
        self.stats["history"] = self.stats["history"][-50:]
        save_stats(self.stats)
        self.update_coin_label()
        self.status_label.config(text=f"Неверно: -{COINS_PENALTY_WRONG} монета и следующее задание раньше на {SECONDS_PENALTY_WRONG} сек.", fg=BAD)
        self.show_result_popup(False, f"Неправильно\n-{COINS_PENALTY_WRONG} 🪙\nСледующая пауза раньше на {SECONDS_PENALTY_WRONG} сек.")

    def reward_for_correct(self):
        task_type = self.current_task.get("type", "input")
        self.stats["total_tasks_completed"] += 1
        self.stats["correct_by_type"][task_type] = self.stats["correct_by_type"].get(task_type, 0) + 1
        self.add_coins(COINS_PER_TASK, f"task_{task_type}")
        save_stats(self.stats)
        self.status_label.config(text=f"Верно! +{COINS_PER_TASK} монет 🪙", fg=ACCENT_2)
        self.show_result_popup(True, f"Правильно!\n+{COINS_PER_TASK} 🪙")

    def check_answer(self):
        if not self.current_task or self.current_task["type"] != "input":
            return
        user_answer = self.entry.get().strip().lower()
        good_answer = str(self.current_task["answer"]).strip().lower()
        if user_answer == good_answer:
            self.after_correct()
        else:
            self.apply_wrong_penalty()
            self.root.after(50, self.focus_entry)

    def check_choice(self, idx):
        if not self.current_task or self.current_task["type"] != "choice":
            return
        chosen = self.choice_buttons[idx].cget("text").strip().lower()
        good_answer = str(self.current_task["answer"]).strip().lower()
        if chosen == good_answer:
            self.after_correct()
        else:
            self.apply_wrong_penalty()

    def mark_button_done(self):
        if self.current_task and self.current_task["type"] == "button":
            self.after_correct()

    def after_correct(self):
        self.reward_for_correct()
        if self.task_index >= TASKS_PER_BREAK and not self.lang_queue:
            self.root.after(850, self.finish_break)
        else:
            self.root.after(850, self.load_next_task)

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
    install_exception_logger()
    log_message("Program start")
    root = tk.Tk()
    app = HomeworkOverlay(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_message(f"Fatal startup error: {e}")
        raise
