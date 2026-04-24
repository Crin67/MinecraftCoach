import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import random
import time
import ctypes
import os
import sys
import wave
import subprocess
import json
import threading
import shutil
import unicodedata
import re
from datetime import datetime
from pathlib import Path

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
SETTINGS_FILE = DATA_DIR / "settings.json"

LOG_FILE = DATA_DIR / "app_log.txt"



DEFAULT_EDITABLE_TASKS = [
    # ===== 1 класс / Klasa 1 =====
    {
        "task_id": "g1_choice_1", "grade": 1, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 4 + 3?", "prompt_pl": "Ile będzie 4 + 3?",
        "answer": "7", "options": ["6", "7", "8", "9"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g1_choice_2", "grade": 1, "type": "choice",
        "title_ru": "Выбери слово", "title_pl": "Wybierz słowo",
        "prompt_ru": "Выбери слово КОТ", "prompt_pl": "Wybierz słowo KOT",
        "answer": "КОТ", "options": ["ДОМ", "КОТ", "ТОК", "СОМ"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g1_choice_3", "grade": 1, "type": "choice",
        "title_ru": "Первая буква", "title_pl": "Pierwsza litera",
        "prompt_ru": "Какая первая буква в слове МАМА?", "prompt_pl": "Jaka jest pierwsza litera w słowie MAMA?",
        "answer": "М", "options": ["М", "А", "К", "О"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g1_input_1", "grade": 1, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 8 - 3?", "prompt_pl": "Ile będzie 8 - 3?",
        "answer": "5", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g1_input_2", "grade": 1, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Вставь букву: д_м", "prompt_pl": "Wstaw literę: d_m",
        "answer": "о", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g1_input_3", "grade": 1, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Польское слово: l_s", "prompt_pl": "Polskie słowo: l_s",
        "answer": "a", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g1_read_1", "grade": 1, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "мама", "prompt_pl": "mama",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g1_read_2", "grade": 1, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "кот", "prompt_pl": "kot",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g1_read_3", "grade": 1, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "дом", "prompt_pl": "dom",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },

    # ===== 2 класс / Klasa 2 =====
    {
        "task_id": "g2_choice_1", "grade": 2, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 14 + 8?", "prompt_pl": "Ile będzie 14 + 8?",
        "answer": "22", "options": ["20", "21", "22", "23"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g2_choice_2", "grade": 2, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 17 - 9?", "prompt_pl": "Ile będzie 17 - 9?",
        "answer": "8", "options": ["6", "7", "8", "9"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g2_choice_3", "grade": 2, "type": "choice",
        "title_ru": "Выбери слово", "title_pl": "Wybierz słowo",
        "prompt_ru": "Выбери польское слово SZKOŁA", "prompt_pl": "Wybierz polskie słowo SZKOŁA",
        "answer": "SZKOŁA", "options": ["SZKOŁA", "KOT", "DOM", "LAS"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g2_input_1", "grade": 2, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 19 - 7?", "prompt_pl": "Ile będzie 19 - 7?",
        "answer": "12", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g2_input_2", "grade": 2, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Вставь букву: шк_ла", "prompt_pl": "Wstaw literę: szk_ła",
        "answer": "о", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_input_3", "grade": 2, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Польское слово: r_ka", "prompt_pl": "Polskie słowo: r_ka",
        "answer": "ę", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_read_1", "grade": 2, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Кот спит.", "prompt_pl": "Kot śpi.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_read_2", "grade": 2, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "У нас урок.", "prompt_pl": "Mamy lekcję.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g2_read_3", "grade": 2, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Мама читает.", "prompt_pl": "Mama czyta.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },

    # ===== 3 класс / Klasa 3 =====
    {
        "task_id": "g3_choice_1", "grade": 3, "type": "choice",
        "title_ru": "Таблица умножения", "title_pl": "Tabliczka mnożenia",
        "prompt_ru": "Сколько будет 6 × 4?", "prompt_pl": "Ile będzie 6 × 4?",
        "answer": "24", "options": ["20", "22", "24", "26"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g3_choice_2", "grade": 3, "type": "choice",
        "title_ru": "Деление", "title_pl": "Dzielenie",
        "prompt_ru": "Сколько будет 18 : 3?", "prompt_pl": "Ile będzie 18 : 3?",
        "answer": "6", "options": ["5", "6", "7", "8"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g3_choice_3", "grade": 3, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 27 + 15?", "prompt_pl": "Ile będzie 27 + 15?",
        "answer": "42", "options": ["40", "41", "42", "43"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g3_input_1", "grade": 3, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 8 × 3?", "prompt_pl": "Ile będzie 8 × 3?",
        "answer": "24", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g3_input_2", "grade": 3, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 32 - 14?", "prompt_pl": "Ile będzie 32 - 14?",
        "answer": "18", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g3_input_3", "grade": 3, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Польское слово: ksią_kа", "prompt_pl": "Polskie słowo: ksią_ka",
        "answer": "ż", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g3_read_1", "grade": 3, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Сегодня мы читаем внимательно.", "prompt_pl": "Dzisiaj czytamy uważnie.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g3_read_2", "grade": 3, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Весной на улице тепло.", "prompt_pl": "Wiosną na dworze jest ciepło.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g3_read_3", "grade": 3, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Мы решаем задачу вместе.", "prompt_pl": "Rozwiązujemy zadanie razem.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },

    # ===== 4 класс / Klasa 4 =====
    {
        "task_id": "g4_choice_1", "grade": 4, "type": "choice",
        "title_ru": "Таблица умножения", "title_pl": "Tabliczka mnożenia",
        "prompt_ru": "Сколько будет 7 × 8?", "prompt_pl": "Ile będzie 7 × 8?",
        "answer": "56", "options": ["54", "56", "58", "64"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g4_choice_2", "grade": 4, "type": "choice",
        "title_ru": "Деление", "title_pl": "Dzielenie",
        "prompt_ru": "Сколько будет 72 : 9?", "prompt_pl": "Ile będzie 72 : 9?",
        "answer": "8", "options": ["6", "7", "8", "9"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g4_choice_3", "grade": 4, "type": "choice",
        "title_ru": "Выбери ответ", "title_pl": "Wybierz odpowiedź",
        "prompt_ru": "Сколько будет 48 + 27?", "prompt_pl": "Ile będzie 48 + 27?",
        "answer": "75", "options": ["73", "74", "75", "76"],
        "record_audio": False, "voice_text": "Выбери правильный ответ кнопкой.", "source": "built_in"
    },
    {
        "task_id": "g4_input_1", "grade": 4, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 96 : 8?", "prompt_pl": "Ile będzie 96 : 8?",
        "answer": "12", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g4_input_2", "grade": 4, "type": "input",
        "title_ru": "Впиши ответ", "title_pl": "Wpisz odpowiedź",
        "prompt_ru": "Сколько будет 37 + 28?", "prompt_pl": "Ile będzie 37 + 28?",
        "answer": "65", "options": [],
        "record_audio": False, "voice_text": "Напиши ответ в окошке.", "source": "built_in"
    },
    {
        "task_id": "g4_input_3", "grade": 4, "type": "input",
        "title_ru": "Вставь букву", "title_pl": "Wstaw literę",
        "prompt_ru": "Польское слово: przyjaci_ł", "prompt_pl": "Polskie słowo: przyjaci_ł",
        "answer": "ó", "options": [],
        "record_audio": False, "voice_text": "Вставь пропущенную букву и нажми кнопку.", "source": "built_in"
    },
    {
        "task_id": "g4_read_1", "grade": 4, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Сегодня мы внимательно читаем и думаем.", "prompt_pl": "Dzisiaj uważnie czytamy i myślimy.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g4_read_2", "grade": 4, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Осенью листья падают на землю.", "prompt_pl": "Jesienią liście spadają na ziemię.",
        "answer": "ok", "options": [],
        "record_audio": True, "voice_text": "Прочитай, что написано, и нажми на кнопку.", "source": "built_in"
    },
    {
        "task_id": "g4_read_3", "grade": 4, "type": "button",
        "title_ru": "Прочитай", "title_pl": "Przeczytaj",
        "prompt_ru": "Мы сначала считаем, а потом проверяем ответ.", "prompt_pl": "Najpierw liczymy, a potem sprawdzamy odpowiedź.",
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
    accepted_answers = [str(x) for x in item.get("accepted_answers", [])] if isinstance(item.get("accepted_answers", []), list) else []
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
        "accepted_answers": accepted_answers,
        "theme": str(item.get("theme", "") or ""),
        "support_mode": str(item.get("support_mode", "") or ""),
        "support_factor": int(item.get("support_factor", 0) or 0),
        "lesson_ru": str(item.get("lesson_ru", "") or ""),
        "lesson_pl": str(item.get("lesson_pl", "") or ""),
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


def load_settings():
    default = {
        "parent_password": "1234",
    }
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                default.update(data)
    except Exception as e:
        log_message(f"load_settings error: {e}")
    return default


def save_settings(settings):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log_message(f"save_settings error: {e}")


CYRILLIC_TO_LATIN_EQ = str.maketrans({
    "а": "a", "е": "e", "ё": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
    "к": "k", "м": "m", "т": "t", "в": "b", "н": "h", "і": "i", "й": "i",
    "А": "A", "Е": "E", "Ё": "E", "О": "O", "Р": "P", "С": "C", "У": "Y", "Х": "X",
    "К": "K", "М": "M", "Т": "T", "В": "B", "Н": "H", "І": "I", "Й": "I",
})

POLISH_BASE_EQ = {
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    "Ą": "a", "Ć": "c", "Ę": "e", "Ł": "l", "Ń": "n", "Ó": "o", "Ś": "s", "Ź": "z", "Ż": "z",
}

RUSSIAN_VOWELS = "А Е Ё И О У Ы Э Ю Я"
RUSSIAN_CONSONANTS = "Б В Г Д Ж З Й К Л М Н П Р С Т Ф Х Ц Ч Ш Щ"
POLISH_VOWELS = "A Ą E Ę I O Ó U Y"
POLISH_CONSONANTS = "B C Ć D F G H J K L Ł M N Ń P Q R S Ś T V W X Z Ź Ż"

def strip_diacritics(text):
    text = ''.join(POLISH_BASE_EQ.get(ch, ch) for ch in text)
    norm = unicodedata.normalize('NFKD', text)
    return ''.join(ch for ch in norm if not unicodedata.combining(ch))


def normalize_user_input(text):
    text = (text or '').strip().lower()
    text = text.translate(CYRILLIC_TO_LATIN_EQ)
    text = strip_diacritics(text)
    text = text.replace('ё', 'е')
    text = re.sub(r'\s+', '', text)
    return text


def answer_variants(answer):
    raw = str(answer or '').strip()
    base = normalize_user_input(raw)
    variants = {raw.lower(), base}
    if len(raw) == 1:
        for k in POLISH_BASE_EQ:
            if normalize_user_input(k) == base:
                variants.add(str(k).lower())
        for k, v in {"е":"e","ё":"e","э":"e","о":"o","а":"a","с":"c","р":"p","у":"y","х":"x","к":"k","м":"m","т":"t"}.items():
            if normalize_user_input(k) == base:
                variants.add(k)
                variants.add(v)
    return sorted({v for v in variants if v})


def is_answer_match(user_answer, expected_answer, extra_answers=None):
    pool = set(answer_variants(expected_answer))
    for item in (extra_answers or []):
        pool.update(answer_variants(item))
    return normalize_user_input(user_answer) in {normalize_user_input(x) for x in pool}


def get_support_content(task):
    theme = task.get('theme') or ''
    mode = task.get('support_mode') or ''
    if mode == 'letters' or theme == 'spelling':
        return {
            'ru_title': 'Буквы-помощники',
            'pl_title': 'Litery pomocnicze',
            'ru_body': f'Гласные:\n{RUSSIAN_VOWELS}\n\nСогласные:\n{RUSSIAN_CONSONANTS}\n\nСмотри на слово и вставь одну букву.',
            'pl_body': f'Samogłoski:\n{POLISH_VOWELS}\n\nSpółgłoski:\n{POLISH_CONSONANTS}\n\nPopatrz na wyraz i wstaw jedną literę.',
        }
    if mode == 'multiplication' or theme == 'multiplication':
        factor = task.get('support_factor') or 7
        rows = [f'{factor} × {i} = {factor*i}' for i in range(1, 4)] + [f'{factor} × 4 = ?']
        return {
            'ru_title': 'Опора по умножению',
            'pl_title': 'Podpowiedź do mnożenia',
            'ru_body': 'Смотри на образец:\n' + '\n'.join(rows),
            'pl_body': 'Spójrz na wzór:\n' + '\n'.join(rows),
        }
    if mode == 'reading' or theme == 'reading':
        return {
            'ru_title': 'Как отвечать',
            'pl_title': 'Jak odpowiedzieć',
            'ru_body': 'Прочитай текст вслух. Потом нажми большую кнопку снизу.',
            'pl_body': 'Przeczytaj tekst na głos. Potem kliknij duży przycisk na dole.',
        }
    if mode == 'math' or theme == 'math':
        return {
            'ru_title': 'Как решать',
            'pl_title': 'Jak liczyć',
            'ru_body': 'Считай по шагам. Можно представить палочки или кубики.',
            'pl_body': 'Licz krok po kroku. Możesz wyobrazić sobie patyczki lub klocki.',
        }
    if theme == 'lesson':
        return {
            'ru_title': 'Тема',
            'pl_title': 'Temat',
            'ru_body': task.get('lesson_ru', 'Прочитай правило и нажми кнопку.'),
            'pl_body': task.get('lesson_pl', 'Przeczytaj zasadę i kliknij przycisk.'),
        }
    return {
        'ru_title': 'Подсказка',
        'pl_title': 'Podpowiedź',
        'ru_body': 'Наведи мышкой на боковую панель, чтобы увидеть помощь.',
        'pl_body': 'Najedź myszką na boczny panel, aby zobaczyć pomoc.',
    }


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
    def build_bilingual(title_ru, title_pl, prompt_ru, prompt_pl, task_type, answer=None, options=None, record_audio=False, voice_text=None, accepted_answers=None, theme="", support_mode="", support_factor=0, lesson_ru="", lesson_pl=""):
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
            "accepted_answers": accepted_answers or [],
            "theme": theme,
            "support_mode": support_mode,
            "support_factor": support_factor,
            "lesson_ru": lesson_ru,
            "lesson_pl": lesson_pl,
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
            voice_text="Реши пример и напиши ответ в окошке.",
            theme="multiplication" if mode == "mul" else "math",
            support_mode="multiplication" if mode == "mul" else "math",
            support_factor=a if mode == "mul" else 0
        )

    @staticmethod
    def make_spelling_task(grade, focus_lang):
        if focus_lang == "ru":
            masked, missing, full = random.choice(pick_grade_items(RU_WORDS, grade))
            return TaskFactory.build_bilingual(
                "Русский язык", "Język rosyjski",
                f"Вставь букву: {masked}", f"Wstaw literę w rosyjskim słowie: {masked}",
                task_type="input", answer=missing,
                voice_text="Вставь пропущенную букву и напиши её в окошке.",
                accepted_answers=answer_variants(missing),
                theme="spelling", support_mode="letters"
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
            voice_text="Выбери правильный ответ кнопкой.",
            theme="multiplication" if "×" in pr_ru else "math",
            support_mode="multiplication" if "×" in pr_ru else "math",
            support_factor=int(re.search(r"(\d+)\s*[×x]", pr_ru).group(1)) if "×" in pr_ru and re.search(r"(\d+)\s*[×x]", pr_ru) else 0
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
                voice_text="Прочитай, что написано, и нажми на кнопку.",
                theme="reading", support_mode="reading"
            )
        text = random.choice(cfg["reading_pl"])
        return TaskFactory.build_bilingual(
            "Чтение вслух", "Czytanie na głos",
            f"Прочитай по-польски вслух:\n\n{text}", f"Przeczytaj na głos:\n\n{text}",
            task_type="button", answer="ok", record_audio=True,
            voice_text="Прочитай, что написано, и нажми на кнопку."
        )

    @staticmethod
    def make_lesson_task(grade, focus_lang):
        lessons = {
            1: (
                "Гласные можно тянуть голосом: а, о, у, ы, э, я, ё, ю, е, и.",
                "Samogłoski można śpiewać głosem: a, ą, e, ę, i, o, ó, u, y.",
                "Запомни: гласные тянутся, согласные встречают преграду.",
                "Zapamiętaj: samogłoski śpiewają, spółgłoski spotykają przeszkodę."
            ),
            2: (
                "В слове сначала прочитай весь слог, а потом вставляй пропущенную букву.",
                "Najpierw przeczytaj cały wyraz lub sylabę, a dopiero potem wpisz brakującą literę.",
                "Совет: произнеси слово медленно и послушай звук.",
                "Wskazówka: powiedz wyraz powoli i posłuchaj dźwięku."
            ),
            3: (
                "При умножении можно смотреть на повторение: 4 × 3 — это 4 + 4 + 4.",
                "Przy mnożeniu możesz patrzeć na powtarzanie: 4 × 3 to 4 + 4 + 4.",
                "Подсказка: умножение — это несколько одинаковых групп.",
                "Wskazówka: mnożenie to kilka takich samych grup."
            ),
            4: (
                "В орфографии помогает правило и проверочное слово. Читай, думай, потом пиши.",
                "W ortografii pomaga zasada i wyraz pokrewny. Najpierw czytaj i myśl, potem pisz.",
                "Подсказка: ищи знакомую часть слова и вспоминай правило.",
                "Wskazówka: szukaj znajomej części wyrazu i przypominaj sobie zasadę."
            ),
        }
        lesson_ru, lesson_pl, short_ru, short_pl = lessons[grade]
        return TaskFactory.build_bilingual(
            "Правило дня", "Zasada dnia",
            short_ru + "\n\nНажми кнопку, когда прочитаешь.",
            short_pl + "\n\nKliknij przycisk, gdy przeczytasz.",
            task_type="button", answer="ok", record_audio=False,
            voice_text="Прочитай правило и нажми на кнопку.",
            theme="lesson", support_mode="lesson", lesson_ru=lesson_ru, lesson_pl=lesson_pl
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
            accepted_answers=data.get("accepted_answers", []),
            theme=data.get("theme", ""),
            support_mode=data.get("support_mode", ""),
            support_factor=int(data.get("support_factor", 0) or 0),
            lesson_ru=data.get("lesson_ru", ""),
            lesson_pl=data.get("lesson_pl", ""),
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
            TaskFactory.make_lesson_task,
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
        self.feedback_active = False
        self.pending_penalty_seconds = 0
        self.stats = load_stats()
        self.settings = load_settings()
        self.custom_tasks = load_custom_tasks()
        save_settings(self.settings)

        self.tray_icon = None
        self.tray_thread = None
        self.tray_supported = False
        self.pystray_mod = None
        self.pil_image_mod = None
        self._init_tray_support()

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

        self.left_hotspot = tk.Frame(self.main, bg=WINDOW_BG, width=18)
        self.right_hotspot = tk.Frame(self.main, bg=WINDOW_BG, width=18)
        self.left_hotspot.place(x=0, rely=0.5, anchor="w", relheight=0.72)
        self.right_hotspot.place(relx=1.0, x=0, rely=0.5, anchor="e", relheight=0.72)

        self.left_slide = tk.Frame(self.main, bg="#F4F7FB", highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.right_slide = tk.Frame(self.main, bg="#F4F7FB", highlightthickness=1, highlightbackground=SOFT_BORDER)
        self.slide_width = 265
        self.slide_visible_left = False
        self.slide_visible_right = False

        self.left_slide_title = tk.Label(self.left_slide, text="Русская помощь", font=("Arial", 16, "bold"), bg="#F4F7FB", fg=TEXT)
        self.left_slide_title.pack(anchor="w", padx=16, pady=(16, 6))
        self.left_slide_body = tk.Label(self.left_slide, text="", font=("Arial", 13), justify="left", wraplength=220, bg="#F4F7FB", fg=TEXT)
        self.left_slide_body.pack(fill="both", expand=True, padx=16, pady=(0, 16), anchor="nw")

        self.right_slide_title = tk.Label(self.right_slide, text="Polska pomoc", font=("Arial", 16, "bold"), bg="#F4F7FB", fg=TEXT)
        self.right_slide_title.pack(anchor="w", padx=16, pady=(16, 6))
        self.right_slide_body = tk.Label(self.right_slide, text="", font=("Arial", 13), justify="left", wraplength=220, bg="#F4F7FB", fg=TEXT)
        self.right_slide_body.pack(fill="both", expand=True, padx=16, pady=(0, 16), anchor="nw")

        for widget in (self.left_hotspot, self.left_slide):
            widget.bind("<Enter>", lambda e: self.show_side_panel("left"))
            widget.bind("<Leave>", lambda e: self.schedule_hide_side_panel("left"))
        for widget in (self.right_hotspot, self.right_slide):
            widget.bind("<Enter>", lambda e: self.show_side_panel("right"))
            widget.bind("<Leave>", lambda e: self.schedule_hide_side_panel("right"))

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

        self.feedback_overlay = tk.Frame(self.main, bg="#DDE7EE")
        self.feedback_shadow = tk.Frame(self.feedback_overlay, bg=SHADOW)
        self.feedback_shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.52, relheight=0.34)
        self.feedback_card = tk.Frame(self.feedback_shadow, bg="#EAF7EE", highlightthickness=3, highlightbackground=ACCENT_2)
        self.feedback_card.pack(fill="both", expand=True, padx=(0, 8), pady=(0, 8))
        self.feedback_icon = tk.Label(self.feedback_card, text="✓", font=("Arial", 76, "bold"), bg="#EAF7EE", fg=ACCENT_2)
        self.feedback_icon.pack(pady=(34, 8))
        self.feedback_text = tk.Label(self.feedback_card, text="", font=("Arial", 28, "bold"), bg="#EAF7EE", fg=TEXT, justify="center")
        self.feedback_text.pack(padx=40, pady=(0, 26))
        self.feedback_hint = tk.Label(self.feedback_card, text="Подготовься к следующему заданию", font=("Arial", 16), bg="#EAF7EE", fg=SUBTEXT)
        self.feedback_hint.pack(pady=(0, 24))

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

    def update_side_panels(self, task=None):
        task = task or self.current_task or {}
        data = get_support_content(task)
        self.left_slide_title.config(text=data.get("ru_title", "Подсказка"))
        self.left_slide_body.config(text=data.get("ru_body", ""))
        self.right_slide_title.config(text=data.get("pl_title", "Podpowiedź"))
        self.right_slide_body.config(text=data.get("pl_body", ""))
        self.position_side_panels()

    def position_side_panels(self):
        self.root.update_idletasks()
        h = max(280, int(self.root.winfo_height() * 0.66))
        y = max(90, int(self.root.winfo_height() * 0.18))
        left_x = 0 if self.slide_visible_left else -self.slide_width + 18
        right_x = self.root.winfo_width() - self.slide_width if self.slide_visible_right else self.root.winfo_width() - 18
        self.left_slide.place(x=left_x, y=y, width=self.slide_width, height=h)
        self.right_slide.place(x=right_x, y=y, width=self.slide_width, height=h)
        self.left_hotspot.place(x=0, y=y, width=18, height=h)
        self.right_hotspot.place(x=self.root.winfo_width()-18, y=y, width=18, height=h)

        # Панели должны быть поверх карточки задания, а не под ней.
        # Используем lift на каждом reposition, чтобы порядок слоёв не сбивался
        # после анимаций, обновлений fullscreen и показа overlay.
        try:
            self.left_slide.lift()
            self.right_slide.lift()
            self.left_hotspot.lift()
            self.right_hotspot.lift()
        except Exception:
            pass

    def animate_side_panel(self, side, show=True):
        frame = self.left_slide if side == "left" else self.right_slide
        shown_attr = "slide_visible_left" if side == "left" else "slide_visible_right"
        setattr(self, shown_attr, show)
        self.position_side_panels()
        start = frame.winfo_x()
        if side == "left":
            target = 0 if show else -self.slide_width + 18
        else:
            target = self.root.winfo_width() - self.slide_width if show else self.root.winfo_width() - 18
        delta = (target - start) / 6.0
        def step(n=0, x=start):
            if n >= 6:
                self.position_side_panels()
                return
            x2 = int(x + delta)
            frame.place_configure(x=x2)
            try:
                frame.lift()
            except Exception:
                pass
            self.root.after(16, lambda: step(n+1, x2))
        step()

    def show_side_panel(self, side):
        self.animate_side_panel(side, True)

    def schedule_hide_side_panel(self, side):
        def hide_if_outside():
            x = self.root.winfo_pointerx() - self.root.winfo_rootx()
            y = self.root.winfo_pointery() - self.root.winfo_rooty()
            widgets = [self.left_slide, self.left_hotspot] if side == "left" else [self.right_slide, self.right_hotspot]
            inside = False
            for w in widgets:
                try:
                    wx, wy, ww, wh = w.winfo_x(), w.winfo_y(), w.winfo_width(), w.winfo_height()
                    if wx <= x <= wx + ww and wy <= y <= wy + wh:
                        inside = True
                        break
                except Exception:
                    pass
            if not inside:
                self.animate_side_panel(side, False)
        self.root.after(120, hide_if_outside)

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
        log_message(f"Grade selected: {grade}; next_break_ts={self.next_break_ts}")
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
        if self.confirm_parent_exit():
            self.exit_app(force=True)

    def confirm_parent_exit(self):
        try:
            pwd = simpledialog.askstring(
                APP_TITLE,
                "Введите пароль родителя для закрытия программы",
                parent=self.root,
                show="*",
            )
        except Exception as e:
            log_message(f"Password dialog error: {e}")
            pwd = None

        if pwd is None:
            return False

        expected = str(self.settings.get("parent_password", "1234"))
        if str(pwd) == expected:
            return True

        try:
            messagebox.showerror(APP_TITLE, "Неверный пароль")
        except Exception:
            pass
        return False

    def focus_entry(self):
        if self.break_active and self.current_task and self.current_task.get("type") == "input":
            try:
                self.entry.focus_force()
                self.entry.icursor(tk.END)
            except Exception:
                pass

    def focus_entry_if_needed(self):
        return lambda: self.focus_entry()


    def _init_tray_support(self):
        try:
            import pystray
            from PIL import Image
            self.pystray_mod = pystray
            self.pil_image_mod = Image
            self.tray_supported = True
            log_message("Tray support enabled")
        except Exception as e:
            self.tray_supported = False
            log_message(f"Tray support unavailable: {e}")

    def _build_tray_image(self):
        if not self.pil_image_mod:
            return None
        try:
            return self.pil_image_mod.open(resource_path("app.ico"))
        except Exception as e:
            log_message(f"Tray icon load failed: {e}")
            try:
                return self.pil_image_mod.new("RGBA", (64, 64), (106, 140, 175, 255))
            except Exception:
                return None

    def _ensure_tray_icon(self):
        if not self.tray_supported:
            return False
        if self.tray_icon is not None:
            return True
        try:
            image = self._build_tray_image()
            pystray = self.pystray_mod

            def on_open(icon=None, item=None):
                self.root.after(0, self.restore_from_tray)

            def on_shop(icon=None, item=None):
                def _open():
                    self.restore_from_tray()
                    self.root.after(200, self.open_shop)
                self.root.after(0, _open)

            def on_stats(icon=None, item=None):
                def _open():
                    self.restore_from_tray()
                    self.root.after(200, self.open_stats)
                self.root.after(0, _open)

            def on_exit(icon=None, item=None):
                self.root.after(0, self.on_close_attempt)

            menu = pystray.Menu(
                pystray.MenuItem("Открыть", on_open, default=True),
                pystray.MenuItem("Магазин", on_shop),
                pystray.MenuItem("Статистика", on_stats),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Выход", on_exit),
            )

            self.tray_icon = pystray.Icon("MinecraftCoach", image, APP_TITLE, menu)
            return True
        except Exception as e:
            log_message(f"_ensure_tray_icon failed: {e}")
            self.tray_icon = None
            return False

    def minimize_to_tray(self):
        if not self._ensure_tray_icon():
            self.root.iconify()
            return

        try:
            self.root.attributes("-fullscreen", False)
        except Exception:
            pass

        try:
            self.root.withdraw()
        except Exception as e:
            log_message(f"withdraw before tray failed: {e}")
            self.root.iconify()

        try:
            if self.tray_thread is None or not self.tray_thread.is_alive():
                self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
                self.tray_thread.start()
                log_message("Tray icon started")
        except Exception as e:
            log_message(f"minimize_to_tray failed: {e}")
            try:
                self.root.iconify()
            except Exception:
                pass

    def stop_tray_icon(self):
        icon = self.tray_icon
        self.tray_icon = None
        if icon is not None:
            try:
                icon.stop()
                log_message("Tray icon stopped")
            except Exception as e:
                log_message(f"stop_tray_icon warning: {e}")

    def restore_from_tray(self):
        self.stop_tray_icon()
        try:
            self.root.deiconify()
            self.root.state("normal")
        except Exception as e:
            log_message(f"restore_from_tray deiconify warning: {e}")
        try:
            self.root.attributes("-topmost", True)
            self.root.lift()
            self.root.focus_force()
        except Exception as e:
            log_message(f"restore_from_tray focus warning: {e}")

    def exit_app(self, force=False):
        if not force:
            if not self.confirm_parent_exit():
                return
        self.stop_tray_icon()
        try:
            self.root.destroy()
        except Exception:
            pass

    def show_overlay(self):
        log_message("show_overlay called")
        self.stop_tray_icon()
        self.root.deiconify()
        try:
            self.root.state("normal")
        except Exception:
            pass
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        self.root.lift()
        try:
            force_window_topmost(self.root.winfo_id())
            self.root.focus_force()
        except Exception as e:
            log_message(f"show_overlay focus warning: {e}")

    def hide_overlay(self):
        log_message("hide_overlay called -> tray")
        try:
            self.root.attributes("-fullscreen", False)
        except Exception:
            pass
        self.minimize_to_tray()

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
        for win in [self.store_window, self.stats_window, self.task_editor_window]:
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
        log_message("start_break called")
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
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)

        if self.feedback_active:
            self.root.attributes("-topmost", True)
            self.show_overlay()
            self.feedback_overlay.lift()
            self.root.after(FORCE_FOCUS_EVERY_MS, self.keep_overlay_active)
            return

        popup = self.get_active_popup()
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
        self.update_side_panels(self.current_task)
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
            if self.current_task.get("theme") == "lesson":
                self.status_label.config(text="Прочитай правило и нажми кнопку / Przeczytaj zasadę i kliknij", fg=TEXT)
            else:
                self.status_label.config(text="Прочитай вслух и нажми кнопку / Przeczytaj na głos i kliknij", fg=TEXT)

        speak_async_windows(self.current_task.get("voice_text", ""))


    def show_result_popup(self, success, text):
        self.feedback_active = True
        self.root.deiconify()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.show_overlay()

        inner_bg = "#EAF7EE" if success else "#FCECEF"
        edge = ACCENT_2 if success else BAD
        icon = "✓" if success else "✕"

        self.feedback_card.configure(bg=inner_bg, highlightbackground=edge)
        self.feedback_icon.configure(text=icon, bg=inner_bg, fg=edge)
        self.feedback_text.configure(text=text, bg=inner_bg, fg=TEXT)
        self.feedback_hint.configure(bg=inner_bg, fg=SUBTEXT)

        self.feedback_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.feedback_overlay.lift()
        self.feedback_shadow.lift()

        self.root.after(1300, self.close_toast)

    def close_toast(self):
        self.feedback_overlay.place_forget()
        self.feedback_active = False
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
        user_answer = self.entry.get().strip()
        good_answer = str(self.current_task["answer"]).strip()
        extras = self.current_task.get("accepted_answers", [])
        if is_answer_match(user_answer, good_answer, extras):
            self.after_correct()
        else:
            self.apply_wrong_penalty()
            self.root.after(50, self.focus_entry)

    def check_choice(self, idx):
        if not self.current_task or self.current_task["type"] != "choice":
            return
        chosen = self.choice_buttons[idx].cget("text").strip()
        good_answer = str(self.current_task["answer"]).strip()
        if is_answer_match(chosen, good_answer, self.current_task.get("accepted_answers", [])):
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
                log_message("tick reached break time -> start_break")
                self.start_break()
        self.root.after(1000, self.tick)



# ===== v16 patch: editable supports, sounds, local parent panel =====
import math as _v16_math
import html as _v16_html
import socket as _v16_socket
import urllib.parse as _v16_urlparse
import http.server as _v16_http
import socketserver as _v16_socketserver
try:
    import winsound as _v16_winsound
except Exception:
    _v16_winsound = None

SUPPORTS_FILE = DATA_DIR / "supports.json"
DEFAULT_SUPPORTS = {
    "letters": {"ru_title": "Буквы-помощники", "pl_title": "Litery pomocnicze", "ru_body": "Гласные:\n{RUSSIAN_VOWELS}\n\nСогласные:\n{RUSSIAN_CONSONANTS}\n\nСмотри на слово и вставь одну букву.", "pl_body": "Samogłoski:\n{POLISH_VOWELS}\n\nSpółgłoski:\n{POLISH_CONSONANTS}\n\nPopatrz na wyraz i wstaw jedną literę."},
    "multiplication": {"ru_title": "Опора по умножению", "pl_title": "Podpowiedź do mnożenia", "ru_body": "Смотри на образец:\n{rows}", "pl_body": "Spójrz na wzór:\n{rows}"},
    "reading": {"ru_title": "Как отвечать", "pl_title": "Jak odpowiedzieć", "ru_body": "Прочитай текст вслух. Потом нажми большую кнопку снизу.", "pl_body": "Przeczytaj tekst na głos. Potem kliknij duży przycisk na dole."},
    "math": {"ru_title": "Как решать", "pl_title": "Jak liczyć", "ru_body": "Считай по шагам. Можно представить палочки или кубики.", "pl_body": "Licz krok po kroku. Możesz wyobrazić sobie patyczki lub klocki."},
    "lesson": {"ru_title": "Тема", "pl_title": "Temat", "ru_body": "Прочитай правило и нажми кнопку.", "pl_body": "Przeczytaj zasadę i kliknij przycisk."},
    "default": {"ru_title": "Подсказка", "pl_title": "Podpowiedź", "ru_body": "Наведи мышкой на боковую панель, чтобы увидеть помощь.", "pl_body": "Najedź myszką na boczny panel, aby zobaczyć pomoc."},
}

def load_supports():
    data = json.loads(json.dumps(DEFAULT_SUPPORTS, ensure_ascii=False))
    try:
        if SUPPORTS_FILE.exists():
            raw = json.loads(SUPPORTS_FILE.read_text(encoding='utf-8'))
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if isinstance(value, dict):
                        data.setdefault(key, {}).update(value)
    except Exception as e:
        log_message(f"load_supports error: {e}")
    return data

def save_supports(data):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SUPPORTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        log_message(f"save_supports error: {e}")

def get_support_content(task, support_data=None):
    support_data = support_data or load_supports()
    theme = task.get('theme') or ''
    mode = task.get('support_mode') or ''
    if mode == 'letters' or theme == 'spelling':
        base = dict(support_data.get('letters', DEFAULT_SUPPORTS['letters']))
        base['ru_body'] = base.get('ru_body', '').replace('{RUSSIAN_VOWELS}', RUSSIAN_VOWELS).replace('{RUSSIAN_CONSONANTS}', RUSSIAN_CONSONANTS)
        base['pl_body'] = base.get('pl_body', '').replace('{POLISH_VOWELS}', POLISH_VOWELS).replace('{POLISH_CONSONANTS}', POLISH_CONSONANTS)
        return base
    if mode == 'multiplication' or theme == 'multiplication':
        factor = task.get('support_factor') or 7
        rows = [f'{factor} × {i} = {factor*i}' for i in range(1, 4)] + [f'{factor} × 4 = ?']
        base = dict(support_data.get('multiplication', DEFAULT_SUPPORTS['multiplication']))
        base['ru_body'] = base.get('ru_body', '').replace('{rows}', '\n'.join(rows))
        base['pl_body'] = base.get('pl_body', '').replace('{rows}', '\n'.join(rows))
        return base
    if mode == 'reading' or theme == 'reading':
        return dict(support_data.get('reading', DEFAULT_SUPPORTS['reading']))
    if mode == 'math' or theme == 'math':
        return dict(support_data.get('math', DEFAULT_SUPPORTS['math']))
    if theme == 'lesson':
        base = dict(support_data.get('lesson', DEFAULT_SUPPORTS['lesson']))
        base['ru_body'] = task.get('lesson_ru', '') or base.get('ru_body', '')
        base['pl_body'] = task.get('lesson_pl', '') or base.get('pl_body', '')
        return base
    return dict(support_data.get('default', DEFAULT_SUPPORTS['default']))

def _v16_make_tone_sequence(path, sequence, rate=22050, volume=0.12, pause=0.03):
    import struct
    frames = []
    for freq, dur in sequence:
        total = int(rate * dur)
        fade = max(1, int(rate * min(0.02, dur / 4)))
        for i in range(total):
            env = 1.0
            if i < fade:
                env = i / fade
            elif total - i < fade:
                env = max(0.0, (total - i) / fade)
            sample = _v16_math.sin(2 * _v16_math.pi * freq * (i / rate))
            frames.append(struct.pack('<h', int(32767 * volume * env * sample)))
        for _ in range(int(rate * pause)):
            frames.append(struct.pack('<h', 0))
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def _v16_ensure_sound_assets():
    assets = DATA_DIR / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    music = assets / 'bg_music.wav'
    ok = assets / 'correct.wav'
    bad = assets / 'wrong.wav'
    if not music.exists():
        _v16_make_tone_sequence(music, [(523,0.18),(659,0.18),(784,0.18),(659,0.18),(587,0.18),(523,0.28)], volume=0.05, pause=0.05)
    if not ok.exists():
        _v16_make_tone_sequence(ok, [(659,0.10),(880,0.12),(1046,0.14)], volume=0.15, pause=0.02)
    if not bad.exists():
        _v16_make_tone_sequence(bad, [(330,0.14),(247,0.18)], volume=0.15, pause=0.02)
    return {'music': music, 'ok': ok, 'bad': bad}

class _V16SoundManager:
    def __init__(self, settings):
        self.settings = settings
        self.assets = _v16_ensure_sound_assets()
    def start_music(self):
        if _v16_winsound is None or not self.settings.get('music_enabled', True):
            return
        try:
            _v16_winsound.PlaySound(str(self.assets['music']), _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_LOOP | _v16_winsound.SND_NODEFAULT)
        except Exception as e:
            log_message(f'music start error: {e}')
    def stop_music(self):
        if _v16_winsound is None:
            return
        try:
            _v16_winsound.PlaySound(None, 0)
        except Exception as e:
            log_message(f'music stop error: {e}')
    def play_correct(self):
        if _v16_winsound is None or not self.settings.get('sounds_enabled', True):
            return
        try:
            _v16_winsound.PlaySound(str(self.assets['ok']), _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_NODEFAULT)
        except Exception as e:
            log_message(f'correct sound error: {e}')
    def play_wrong(self):
        if _v16_winsound is None or not self.settings.get('sounds_enabled', True):
            return
        try:
            _v16_winsound.PlaySound(str(self.assets['bad']), _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_NODEFAULT)
        except Exception as e:
            log_message(f'wrong sound error: {e}')

class SupportEditorDialog(tk.Toplevel):
    def __init__(self, parent, supports, on_save, on_close=None):
        super().__init__(parent)
        self.supports = json.loads(json.dumps(supports, ensure_ascii=False))
        self.on_save = on_save
        self.on_close = on_close
        self.title('Подсказки и правила / Podpowiedzi i zasady')
        self.configure(bg=WINDOW_BG)
        self.attributes('-topmost', True)
        self.geometry('1180x760+80+60')
        self.protocol('WM_DELETE_WINDOW', self.close)
        outer = tk.Frame(self, bg=WINDOW_BG)
        outer.pack(fill='both', expand=True, padx=16, pady=16)
        left = tk.Frame(outer, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        left.pack(side='left', fill='y')
        right = tk.Frame(outer, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        right.pack(side='left', fill='both', expand=True, padx=(16,0))
        tk.Label(left, text='Тип панели', font=('Arial',16,'bold'), bg=CARD_BG, fg=TEXT).pack(anchor='w', padx=12, pady=(12,8))
        self.listbox = tk.Listbox(left, width=28, font=('Arial', 12))
        self.listbox.pack(fill='both', expand=True, padx=12, pady=(0,12))
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        for key in ['letters', 'math', 'multiplication', 'reading', 'lesson', 'default']:
            self.listbox.insert(tk.END, key)
        tk.Label(right, text='Редактор боковых подсказок и правил', font=('Arial',18,'bold'), bg=CARD_BG, fg=TEXT).pack(anchor='w', padx=16, pady=(16,8))
        tk.Label(right, text=f'Файл: {SUPPORTS_FILE}', font=('Arial',10), bg=CARD_BG, fg=SUBTEXT).pack(anchor='w', padx=16, pady=(0,8))
        fields = tk.Frame(right, bg=CARD_BG)
        fields.pack(fill='both', expand=True, padx=16, pady=8)
        fields.grid_columnconfigure(0, weight=1)
        fields.grid_columnconfigure(1, weight=1)
        tk.Label(fields, text='Заголовок RU', font=('Arial',11,'bold'), bg=CARD_BG, fg=TEXT).grid(row=0, column=0, sticky='w', padx=6)
        tk.Label(fields, text='Zagłówek PL', font=('Arial',11,'bold'), bg=CARD_BG, fg=TEXT).grid(row=0, column=1, sticky='w', padx=6)
        self.ru_title = tk.Entry(fields, font=('Arial',12))
        self.pl_title = tk.Entry(fields, font=('Arial',12))
        self.ru_title.grid(row=1, column=0, sticky='ew', padx=6, pady=(0,10))
        self.pl_title.grid(row=1, column=1, sticky='ew', padx=6, pady=(0,10))
        tk.Label(fields, text='Текст RU', font=('Arial',11,'bold'), bg=CARD_BG, fg=TEXT).grid(row=2, column=0, sticky='w', padx=6)
        tk.Label(fields, text='Tekst PL', font=('Arial',11,'bold'), bg=CARD_BG, fg=TEXT).grid(row=2, column=1, sticky='w', padx=6)
        self.ru_body = tk.Text(fields, font=('Arial',12), wrap='word', height=18)
        self.pl_body = tk.Text(fields, font=('Arial',12), wrap='word', height=18)
        self.ru_body.grid(row=3, column=0, sticky='nsew', padx=6, pady=(0,10))
        self.pl_body.grid(row=3, column=1, sticky='nsew', padx=6, pady=(0,10))
        fields.grid_rowconfigure(3, weight=1)
        tk.Label(right, text='Можно использовать {rows}, {RUSSIAN_VOWELS}, {RUSSIAN_CONSONANTS}, {POLISH_VOWELS}, {POLISH_CONSONANTS}.', font=('Arial',10), bg=CARD_BG, fg=SUBTEXT).pack(anchor='w', padx=16, pady=(0,10))
        bar = tk.Frame(right, bg=CARD_BG)
        bar.pack(fill='x', padx=16, pady=(0,16))
        tk.Button(bar, text='Сохранить текущую', command=self.save_current, bg=ACCENT_2, fg='white', relief='flat', font=('Arial',12,'bold')).pack(side='left')
        tk.Button(bar, text='Сохранить всё и закрыть', command=self.save_all_and_close, bg=ACCENT, fg='white', relief='flat', font=('Arial',12,'bold')).pack(side='left', padx=10)
        tk.Button(bar, text='Закрыть', command=self.close, bg='#9AA8B5', fg='white', relief='flat', font=('Arial',12,'bold')).pack(side='right')
        self.current_key = 'letters'
        self.listbox.selection_set(0)
        self.on_select()
    def on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.current_key = self.listbox.get(sel[0])
        data = self.supports.get(self.current_key, {})
        self.ru_title.delete(0, tk.END); self.ru_title.insert(0, data.get('ru_title',''))
        self.pl_title.delete(0, tk.END); self.pl_title.insert(0, data.get('pl_title',''))
        self.ru_body.delete('1.0', tk.END); self.ru_body.insert('1.0', data.get('ru_body',''))
        self.pl_body.delete('1.0', tk.END); self.pl_body.insert('1.0', data.get('pl_body',''))
    def save_current(self):
        self.supports[self.current_key] = {'ru_title': self.ru_title.get().strip(), 'pl_title': self.pl_title.get().strip(), 'ru_body': self.ru_body.get('1.0', tk.END).strip(), 'pl_body': self.pl_body.get('1.0', tk.END).strip()}
        return True
    def save_all_and_close(self):
        self.save_current(); self.on_save(self.supports); self.close()
    def close(self):
        try:
            if callable(self.on_close):
                self.on_close()
        finally:
            self.destroy()

class ParentPanelServer:
    def __init__(self, app):
        self.app = app
        self.httpd = None
        self.thread = None
        self.url = None
    def start(self):
        if self.thread and self.thread.is_alive():
            return self.url
        app = self.app
        port = int(app.settings.get('parent_panel_port', 8765) or 8765)
        class Handler(_v16_http.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass
            def _html(self, body, status=200):
                raw = body.encode('utf-8'); self.send_response(status); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def _redirect(self, location):
                self.send_response(303); self.send_header('Location', location); self.end_headers()
            def do_GET(self):
                parsed = _v16_urlparse.urlparse(self.path)
                qs = _v16_urlparse.parse_qs(parsed.query)
                password = qs.get('password', [''])[0]
                if parsed.path == '/api/stats':
                    if password != str(app.settings.get('parent_password', '1234')):
                        raw = b'{"error":"forbidden"}'; self.send_response(403); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw); return
                    raw = json.dumps(app.stats, ensure_ascii=False, indent=2).encode('utf-8'); self.send_response(200); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw); return
                if password != str(app.settings.get('parent_password', '1234')):
                    return self._html("""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Панель родителя</title><style>
body{font-family:Arial,sans-serif;background:#eef3f7;margin:0;color:#233548} .wrap{max-width:560px;margin:0 auto;padding:22px} .card{background:#fff;border:1px solid #d6e0e8;border-radius:18px;padding:22px;box-shadow:0 10px 30px rgba(0,0,0,.06)}
h1{margin:0 0 10px;font-size:28px} p{color:#5e6a75;line-height:1.45} input,button{width:100%;box-sizing:border-box;border-radius:14px;border:1px solid #cfdbe5;font-size:18px;padding:14px} button{margin-top:12px;border:none;background:#6A8CAF;color:#fff;font-weight:700}
</style></head><body><div class='wrap'><div class='card'><h1>Панель родителя</h1><p>Открой панель на телефоне или компьютере и введи пароль родителя. Интерфейс адаптирован под касание и редактирование без мелких кнопок.</p><form method='GET' action='/'><input type='password' name='password' placeholder='Пароль родителя'><button>Войти</button></form></div></div></body></html>""")
                tasks_json = _v16_html.escape(json.dumps(app.custom_tasks, ensure_ascii=False, indent=2))
                supports_json = _v16_html.escape(json.dumps(app.supports, ensure_ascii=False, indent=2))
                hist = ''.join(f"<li>{_v16_html.escape(item.get('time',''))}: {_v16_html.escape(str(item.get('reason','')))} ({int(item.get('coins', 0)):+})</li>" for item in app.stats.get('history', [])[-12:][::-1]) or '<li>Пока пусто</li>'
                body = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Parent Panel</title><style>
:root{{--bg:#eef3f7;--card:#ffffff;--text:#233548;--sub:#5e6a75;--border:#d6e0e8;--accent:#6A8CAF;--accent2:#7CA982;--shadow:0 10px 30px rgba(0,0,0,.06)}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--text)}} .wrap{{max-width:1240px;margin:0 auto;padding:16px}} .hero{{background:linear-gradient(135deg,#f6fbff,#eef3f7);border:1px solid var(--border);border-radius:20px;padding:18px;box-shadow:var(--shadow);margin-bottom:16px}}
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}} .stat{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:14px}} .stat .n{{font-size:28px;font-weight:700;margin-top:6px}} .pill{{display:inline-block;background:#fff7d6;border:1px solid #ecd388;border-radius:999px;padding:6px 10px;font-size:13px;font-weight:700}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} .card{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;box-shadow:var(--shadow)}} h1,h2,h3{{margin:0 0 12px}} p{{margin:0 0 10px;color:var(--sub);line-height:1.45}} textarea{{width:100%;height:58vh;min-height:340px;border:1px solid var(--border);border-radius:14px;padding:14px;font-family:Consolas,monospace;font-size:15px;line-height:1.4;resize:vertical;background:#fbfdff}} .actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}} button,a.btn{{appearance:none;border:none;border-radius:14px;padding:12px 16px;font-size:16px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}} button.primary,a.primary{{background:var(--accent);color:#fff}} a.secondary{{background:#fff;border:1px solid var(--border);color:var(--text)}} ul.history{{padding-left:18px;margin:0;max-height:240px;overflow:auto}} ul.history li{{margin:0 0 8px;color:var(--sub)}} .toolbar{{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 0}} .urlbox{{word-break:break-all;background:#f8fbfd;border:1px dashed var(--border);border-radius:12px;padding:10px}}
@media (max-width: 900px){{.grid,.cards{{grid-template-columns:1fr}} .wrap{{padding:12px}} textarea{{height:42vh;min-height:260px}} button,a.btn{{width:100%}} .actions{{flex-direction:column}} }}
</style></head><body><div class='wrap'><div class='hero'><div class='pill'>Панель родителя · touch friendly</div><h1 style='margin-top:10px'>Управление с телефона</h1><p>Здесь можно редактировать задания и боковые подсказки так же, как на компьютере, но в удобном формате для телефона: крупные поля, большие кнопки и адаптивные блоки.</p><div class='toolbar'><a class='btn secondary' href='/?password={_v16_urlparse.quote(password)}'>Обновить</a><a class='btn secondary' href='/api/stats?password={_v16_urlparse.quote(password)}'>Открыть stats JSON</a></div><div class='cards'><div class='stat'><div>Монеты</div><div class='n'>{app.stats.get('coins',0)}</div></div><div class='stat'><div>Решено заданий</div><div class='n'>{app.stats.get('total_tasks_completed',0)}</div></div><div class='stat'><div>Ошибок</div><div class='n'>{app.stats.get('wrong_answers',0)}</div></div></div><div style='margin-top:14px'><div style='font-weight:700;margin-bottom:6px'>Ссылка для телефона</div><div class='urlbox'>{_v16_html.escape(app.parent_panel_url or '')}?password={_v16_html.escape(password)}</div></div></div><div class='grid'><div class='card'><h2>Последние события</h2><ul class='history'>{hist}</ul></div><div class='card'><h2>Как пользоваться</h2><p>1. Открой эту панель на телефоне в той же сети.</p><p>2. Исправь или добавь задания в левом блоке.</p><p>3. Обнови боковые подсказки и правила в правом блоке.</p><p>4. Нажми сохранить — изменения сразу появятся в программе.</p></div><form class='card' method='POST' action='/save_tasks'><input type='hidden' name='password' value='{_v16_html.escape(password)}'><h2>Задания JSON</h2><p>Можно редактировать, добавлять и обновлять карточки. Для телефона поле стало шире и удобнее для прокрутки.</p><textarea name='payload'>{tasks_json}</textarea><div class='actions'><button class='primary'>Сохранить задания</button></div></form><form class='card' method='POST' action='/save_supports'><input type='hidden' name='password' value='{_v16_html.escape(password)}'><h2>Подсказки и правила JSON</h2><p>Здесь меняются боковые панели и учебные карточки для разных тем.</p><textarea name='payload'>{supports_json}</textarea><div class='actions'><button class='primary'>Сохранить подсказки</button></div></form></div></div></body></html>"""
                self._html(body)
            def do_POST(self):
                size = int(self.headers.get('Content-Length', '0') or 0)
                raw = self.rfile.read(size).decode('utf-8', errors='ignore')
                data = _v16_urlparse.parse_qs(raw)
                password = data.get('password', [''])[0]
                payload = data.get('payload', [''])[0]
                if password != str(app.settings.get('parent_password', '1234')):
                    return self._html('<h3>Неверный пароль</h3>', 403)
                try:
                    parsed = json.loads(payload)
                    if self.path == '/save_tasks':
                        if not isinstance(parsed, list): raise ValueError('tasks must be a list')
                        app.custom_tasks = [normalize_task_dict(x, fallback_source=str(x.get('source', 'custom'))) for x in parsed]
                        save_custom_tasks(app.custom_tasks)
                    elif self.path == '/save_supports':
                        if not isinstance(parsed, dict): raise ValueError('supports must be a dict')
                        app.supports = parsed; save_supports(app.supports)
                    app.root.after(0, lambda: app.status_label.config(text='Данные обновлены из панели родителя', fg=ACCENT_2))
                    self._redirect('/?password=' + _v16_urlparse.quote(password))
                except Exception as e:
                    self._html(f'<h3>Ошибка сохранения</h3><pre>{_v16_html.escape(str(e))}</pre>', 500)
        class _Srv(_v16_socketserver.ThreadingTCPServer): allow_reuse_address = True
        try:
            self.httpd = _Srv(('0.0.0.0', port), Handler)
            ip = self._local_ip(); self.url = f'http://{ip}:{port}/'; self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True); self.thread.start(); log_message(f'Parent panel started at {self.url}')
        except Exception as e:
            log_message(f'Parent panel start error: {e}')
        return self.url
    def stop(self):
        try:
            if self.httpd: self.httpd.shutdown(); self.httpd.server_close()
        except Exception as e:
            log_message(f'Parent panel stop error: {e}')
    def _local_ip(self):
        try:
            sock = _v16_socket.socket(_v16_socket.AF_INET, _v16_socket.SOCK_DGRAM); sock.connect(('8.8.8.8', 80)); ip = sock.getsockname()[0]; sock.close(); return ip
        except Exception:
            return '127.0.0.1'

_old_init = HomeworkOverlay.__init__
def _v16_init(self, root):
    _old_init(self, root)
    self.supports = load_supports()
    self.sound = _V16SoundManager(getattr(self, 'settings', {'music_enabled': True, 'sounds_enabled': True}))
    self.parent_server = ParentPanelServer(self)
    self.parent_panel_url = self.parent_server.start() or ''
    self.support_editor_window = None
    try:
        self.supports_btn = tk.Button(self.topbar, text='📚 Подсказки', font=('Arial', 13, 'bold'), bg='#7C91A7', fg='white', activebackground='#7C91A7', relief='flat', bd=0, padx=14, pady=10, command=self.open_support_editor)
        self.supports_btn.pack(side='left', padx=12, before=self.coin_label)
    except Exception as e:
        log_message(f'support button patch error: {e}')
HomeworkOverlay.__init__ = _v16_init

def _v16_update_side_panels(self, task=None):
    task = task or self.current_task or {}
    data = get_support_content(task, getattr(self, 'supports', None))
    self.left_slide_title.config(text=data.get('ru_title', 'Подсказка'))
    self.left_slide_body.config(text=data.get('ru_body', ''))
    self.right_slide_title.config(text=data.get('pl_title', 'Podpowiedź'))
    self.right_slide_body.config(text=data.get('pl_body', ''))
    self.position_side_panels()
HomeworkOverlay.update_side_panels = _v16_update_side_panels

def _v16_save_supports_from_editor(self, supports):
    self.supports = supports; save_supports(supports); self.update_side_panels(self.current_task); self.status_label.config(text='Подсказки и правила сохранены', fg=ACCENT_2)
HomeworkOverlay.save_supports_from_editor = _v16_save_supports_from_editor

def _v16_open_support_editor(self):
    if getattr(self, 'support_editor_window', None) and self.support_editor_window.winfo_exists(): self.support_editor_window.lift(); self.support_editor_window.focus_force(); return
    self.support_editor_window = SupportEditorDialog(self.root, getattr(self, 'supports', load_supports()), self.save_supports_from_editor, on_close=lambda: self.popup_closed('supports'))
HomeworkOverlay.open_support_editor = _v16_open_support_editor

def _v16_get_active_popup(self):
    for win in [getattr(self, 'store_window', None), getattr(self, 'stats_window', None), getattr(self, 'task_editor_window', None), getattr(self, 'support_editor_window', None)]:
        try:
            if win and win.winfo_exists(): return win
        except Exception:
            pass
    return None
HomeworkOverlay.get_active_popup = _v16_get_active_popup

_old_popup_closed = HomeworkOverlay.popup_closed
def _v16_popup_closed(self, which):
    if which == 'supports': self.support_editor_window = None
    return _old_popup_closed(self, which)
HomeworkOverlay.popup_closed = _v16_popup_closed

_old_show_overlay = HomeworkOverlay.show_overlay
def _v16_show_overlay(self):
    try:
        if hasattr(self, 'sound'): self.sound.start_music()
    except Exception:
        pass
    return _old_show_overlay(self)
HomeworkOverlay.show_overlay = _v16_show_overlay

_old_hide_overlay = HomeworkOverlay.hide_overlay
def _v16_hide_overlay(self):
    try:
        if hasattr(self, 'sound'): self.sound.stop_music()
    except Exception:
        pass
    return _old_hide_overlay(self)
HomeworkOverlay.hide_overlay = _v16_hide_overlay

_old_exit_app = HomeworkOverlay.exit_app
def _v16_exit_app(self, force=False):
    try:
        if hasattr(self, 'sound'): self.sound.stop_music()
        if hasattr(self, 'parent_server'): self.parent_server.stop()
    except Exception:
        pass
    return _old_exit_app(self, force)
HomeworkOverlay.exit_app = _v16_exit_app

_old_apply_wrong_penalty = HomeworkOverlay.apply_wrong_penalty
def _v16_apply_wrong_penalty(self):
    try:
        if hasattr(self, 'sound'): self.sound.play_wrong()
    except Exception:
        pass
    return _old_apply_wrong_penalty(self)
HomeworkOverlay.apply_wrong_penalty = _v16_apply_wrong_penalty

_old_reward_for_correct = HomeworkOverlay.reward_for_correct
def _v16_reward_for_correct(self):
    try:
        if hasattr(self, 'sound'): self.sound.play_correct()
    except Exception:
        pass
    return _old_reward_for_correct(self)
HomeworkOverlay.reward_for_correct = _v16_reward_for_correct

_old_select_grade = HomeworkOverlay.select_grade
def _v16_select_grade(self, grade):
    result = _old_select_grade(self, grade)
    try:
        if getattr(self, 'parent_panel_url', ''):
            self.status_label.config(text=f"Выбран уровень: {GRADE_CONFIGS[grade]['label']} | Родительская панель: {self.parent_panel_url}", fg=TEXT)
    except Exception:
        pass
    return result
HomeworkOverlay.select_grade = _v16_select_grade


# ===== v17 patch: parent hub + QR + custom music =====
# ===== v18 patch: sound restart fix + mobile parent panel =====
try:
    import tkinter.ttk as _v17_ttk
except Exception:
    _v17_ttk = None
try:
    from PIL import ImageTk as _v17_ImageTk
except Exception:
    _v17_ImageTk = None
try:
    import qrcode as _v17_qrcode
except Exception:
    _v17_qrcode = None


def _v17_assets_dir():
    assets = DATA_DIR / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    return assets


def _v17_make_calm_music(path):
    seq = [
        (392,0.55),(440,0.55),(523,0.75),(440,0.55),
        (349,0.60),(392,0.60),(440,0.75),(392,0.55),
        (330,0.60),(349,0.60),(392,0.80),(349,0.60),
        (294,0.65),(330,0.65),(349,0.90),(330,0.60),
    ]
    _v16_make_tone_sequence(path, seq, rate=22050, volume=0.03, pause=0.10)


def _v17_ensure_sound_assets():
    assets = _v17_assets_dir()
    music = assets / 'bg_music_long.wav'
    ok = assets / 'correct.wav'
    bad = assets / 'wrong.wav'
    if not music.exists():
        _v17_make_calm_music(music)
    if not ok.exists():
        _v16_make_tone_sequence(ok, [(659,0.10),(880,0.12),(1046,0.14)], volume=0.12, pause=0.02)
    if not bad.exists():
        _v16_make_tone_sequence(bad, [(330,0.14),(247,0.18)], volume=0.12, pause=0.02)
    return {'music': music, 'ok': ok, 'bad': bad}


class _V17SoundManager:
    def __init__(self, settings):
        self.settings = settings
        self.assets = _v17_ensure_sound_assets()
        self.music_playing = False
        self.last_music_path = None
        self._resume_timer = None
        self._lock = threading.Lock()

    def _music_path(self):
        custom = str(self.settings.get('music_file', '') or '').strip()
        if custom and os.path.exists(custom):
            return custom
        return str(self.assets['music'])

    def _cancel_resume(self):
        try:
            if self._resume_timer:
                self._resume_timer.cancel()
        except Exception:
            pass
        self._resume_timer = None

    def start_music(self, force_restart=False):
        if _v16_winsound is None or not self.settings.get('music_enabled', True):
            return
        try:
            music_path = self._music_path()
            with self._lock:
                if self.music_playing and self.last_music_path == music_path and not force_restart:
                    return
                self._cancel_resume()
                _v16_winsound.PlaySound(music_path, _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_LOOP | _v16_winsound.SND_NODEFAULT)
                self.music_playing = True
                self.last_music_path = music_path
        except Exception as e:
            log_message(f'v18 music start error: {e}')

    def stop_music(self):
        if _v16_winsound is None:
            return
        try:
            with self._lock:
                self._cancel_resume()
                _v16_winsound.PlaySound(None, 0)
                self.music_playing = False
        except Exception as e:
            log_message(f'v18 music stop error: {e}')

    def _resume_music_later(self, delay=0.8):
        if _v16_winsound is None or not self.settings.get('music_enabled', True):
            return
        self._cancel_resume()
        def _resume():
            try:
                self.start_music(force_restart=True)
            except Exception as e:
                log_message(f'v18 music resume error: {e}')
        self._resume_timer = threading.Timer(delay, _resume)
        self._resume_timer.daemon = True
        self._resume_timer.start()

    def play_correct(self):
        if _v16_winsound is None or not self.settings.get('sounds_enabled', True):
            return
        try:
            _v16_winsound.PlaySound(str(self.assets['ok']), _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_NODEFAULT)
            self.music_playing = False
            self._resume_music_later(0.55)
        except Exception as e:
            log_message(f'v18 correct sound error: {e}')

    def play_wrong(self):
        if _v16_winsound is None or not self.settings.get('sounds_enabled', True):
            return
        try:
            _v16_winsound.PlaySound(str(self.assets['bad']), _v16_winsound.SND_FILENAME | _v16_winsound.SND_ASYNC | _v16_winsound.SND_NODEFAULT)
            self.music_playing = False
            self._resume_music_later(0.7)
        except Exception as e:
            log_message(f'v18 wrong sound error: {e}')


class ParentHubDialog(tk.Toplevel):
    def __init__(self, parent, app, on_close=None):
        super().__init__(parent)
        self.app = app
        self.on_close = on_close
        self.title('Родительская панель / Panel rodzica')
        self.configure(bg=WINDOW_BG)
        self.geometry('1220x820+60+40')
        self.minsize(1100, 760)
        self.attributes('-topmost', True)
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.qr_image = None

        wrap = tk.Frame(self, bg=WINDOW_BG)
        wrap.pack(fill='both', expand=True, padx=14, pady=14)
        card = tk.Frame(wrap, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        card.pack(fill='both', expand=True)

        head = tk.Frame(card, bg=CARD_BG)
        head.pack(fill='x', padx=18, pady=(14, 8))
        tk.Label(head, text='Родительская панель', font=('Arial', 22, 'bold'), bg=CARD_BG, fg=TEXT).pack(side='left')
        tk.Button(head, text='Закрыть', font=('Arial', 12, 'bold'), bg=BAD, fg='white', activebackground=BAD, relief='flat', bd=0, padx=16, pady=8, command=self.close).pack(side='right')

        self.note = tk.Label(card, text='Здесь собраны управление заданиями, правилами, музыкой, статистикой и подключением телефона.', font=('Arial', 12), bg=CARD_BG, fg=SUBTEXT)
        self.note.pack(anchor='w', padx=18)

        notebook = _v17_ttk.Notebook(card) if _v17_ttk else None
        if notebook:
            notebook.pack(fill='both', expand=True, padx=18, pady=14)
        else:
            notebook = tk.Frame(card, bg=CARD_BG)
            notebook.pack(fill='both', expand=True, padx=18, pady=14)

        self.tab_overview = tk.Frame(notebook if _v17_ttk else notebook, bg=CARD_BG)
        self.tab_audio = tk.Frame(notebook if _v17_ttk else notebook, bg=CARD_BG)
        self.tab_remote = tk.Frame(notebook if _v17_ttk else notebook, bg=CARD_BG)
        if _v17_ttk:
            notebook.add(self.tab_overview, text='Обзор')
            notebook.add(self.tab_audio, text='Музыка и настройки')
            notebook.add(self.tab_remote, text='Телефон и QR')
        else:
            self.tab_overview.pack(fill='both', expand=True)
            self.tab_audio.pack_forget()
            self.tab_remote.pack_forget()

        self._build_overview_tab()
        self._build_audio_tab()
        self._build_remote_tab()
        self.refresh_all()

    def _section(self, parent, title):
        box = tk.Frame(parent, bg=CARD_BG, highlightthickness=1, highlightbackground=SOFT_BORDER)
        tk.Label(box, text=title, font=('Arial', 15, 'bold'), bg=CARD_BG, fg=TEXT).pack(anchor='w', padx=14, pady=(12, 10))
        return box

    def _build_overview_tab(self):
        top = tk.Frame(self.tab_overview, bg=CARD_BG)
        top.pack(fill='x', pady=6)
        self.stats_text = tk.Label(top, text='', font=('Arial', 12), bg=CARD_BG, fg=TEXT, justify='left')
        self.stats_text.pack(anchor='w', padx=8, pady=(4, 12))

        grid = tk.Frame(self.tab_overview, bg=CARD_BG)
        grid.pack(fill='both', expand=True)
        left = self._section(grid, 'Редакторы и управление')
        right = self._section(grid, 'Быстрые действия')
        left.pack(side='left', fill='both', expand=True, padx=(0, 10), pady=8)
        right.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=8)

        for text_, cmd in [
            ('✏️ Открыть редактор заданий', self.app.open_task_editor),
            ('📚 Открыть редактор подсказок и правил', self.app.open_support_editor),
            ('🛒 Открыть магазин', self.app.open_shop),
            ('📊 Открыть статистику', self.app.open_stats),
        ]:
            tk.Button(left, text=text_, font=('Arial', 12, 'bold'), bg=ACCENT, fg='white', activebackground=ACCENT, relief='flat', bd=0, padx=16, pady=10, command=cmd).pack(fill='x', padx=14, pady=6)

        tk.Label(right, text='Пароль родителя', font=('Arial', 12, 'bold'), bg=CARD_BG, fg=TEXT).pack(anchor='w', padx=14, pady=(6, 4))
        pwd_row = tk.Frame(right, bg=CARD_BG)
        pwd_row.pack(fill='x', padx=14)
        self.new_pwd1 = tk.Entry(pwd_row, show='*', font=('Arial', 13))
        self.new_pwd1.pack(fill='x', pady=4)
        self.new_pwd2 = tk.Entry(pwd_row, show='*', font=('Arial', 13))
        self.new_pwd2.pack(fill='x', pady=4)
        tk.Button(right, text='Сменить пароль', font=('Arial', 12, 'bold'), bg=ACCENT_2, fg='white', activebackground=ACCENT_2, relief='flat', bd=0, padx=16, pady=10, command=self.change_password).pack(anchor='w', padx=14, pady=8)
        self.password_status = tk.Label(right, text='', font=('Arial', 11), bg=CARD_BG, fg=SUBTEXT)
        self.password_status.pack(anchor='w', padx=14, pady=(2, 8))

        tk.Button(right, text='Обновить данные', font=('Arial', 12, 'bold'), bg=ACCENT_3, fg='white', activebackground=ACCENT_3, relief='flat', bd=0, padx=16, pady=10, command=self.refresh_all).pack(anchor='w', padx=14, pady=8)

    def _build_audio_tab(self):
        sec = self._section(self.tab_audio, 'Музыка и звуки')
        sec.pack(fill='both', expand=True, pady=8)

        self.music_enabled_var = tk.BooleanVar(value=bool(self.app.settings.get('music_enabled', True)))
        self.sounds_enabled_var = tk.BooleanVar(value=bool(self.app.settings.get('sounds_enabled', True)))
        tk.Checkbutton(sec, text='Включить фоновую музыку', variable=self.music_enabled_var, font=('Arial', 12), bg=CARD_BG, fg=TEXT, selectcolor=CARD_BG, command=self.save_audio_settings).pack(anchor='w', padx=14, pady=(2, 6))
        tk.Checkbutton(sec, text='Включить звуки правильного/неправильного ответа', variable=self.sounds_enabled_var, font=('Arial', 12), bg=CARD_BG, fg=TEXT, selectcolor=CARD_BG, command=self.save_audio_settings).pack(anchor='w', padx=14, pady=(2, 10))

        tk.Label(sec, text='Своя фоновая музыка (лучше WAV)', font=('Arial', 12, 'bold'), bg=CARD_BG, fg=TEXT).pack(anchor='w', padx=14, pady=(6, 4))
        row = tk.Frame(sec, bg=CARD_BG)
        row.pack(fill='x', padx=14, pady=(0, 8))
        self.music_path_var = tk.StringVar(value=str(self.app.settings.get('music_file', '') or ''))
        tk.Entry(row, textvariable=self.music_path_var, font=('Arial', 12), state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 8), ipady=4)
        tk.Button(row, text='Выбрать WAV', font=('Arial', 11, 'bold'), bg=ACCENT, fg='white', activebackground=ACCENT, relief='flat', bd=0, padx=12, pady=8, command=self.choose_music).pack(side='left', padx=4)
        tk.Button(row, text='Очистить', font=('Arial', 11, 'bold'), bg=BAD, fg='white', activebackground=BAD, relief='flat', bd=0, padx=12, pady=8, command=self.clear_music).pack(side='left', padx=4)

        row2 = tk.Frame(sec, bg=CARD_BG)
        row2.pack(fill='x', padx=14, pady=(0, 10))
        tk.Button(row2, text='▶ Проверить музыку', font=('Arial', 11, 'bold'), bg=ACCENT_2, fg='white', activebackground=ACCENT_2, relief='flat', bd=0, padx=12, pady=8, command=self.preview_music).pack(side='left', padx=(0, 8))
        tk.Button(row2, text='■ Остановить', font=('Arial', 11, 'bold'), bg=SUBTEXT, fg='white', activebackground=SUBTEXT, relief='flat', bd=0, padx=12, pady=8, command=self.stop_music).pack(side='left', padx=8)
        tk.Label(sec, text='Встроенная музыка стала длиннее и мягче. Если выбрана своя музыка, будет использоваться она.', font=('Arial', 11), bg=CARD_BG, fg=SUBTEXT, justify='left').pack(anchor='w', padx=14, pady=(4, 10))
        self.audio_status = tk.Label(sec, text='', font=('Arial', 11), bg=CARD_BG, fg=SUBTEXT)
        self.audio_status.pack(anchor='w', padx=14, pady=(2, 12))

    def _build_remote_tab(self):
        top = self._section(self.tab_remote, 'Подключение телефона')
        top.pack(fill='x', pady=8)
        self.url_var = tk.StringVar(value='')
        row = tk.Frame(top, bg=CARD_BG)
        row.pack(fill='x', padx=14, pady=(0, 12))
        tk.Entry(row, textvariable=self.url_var, font=('Arial', 13), state='readonly').pack(side='left', fill='x', expand=True, padx=(0, 8), ipady=4)
        tk.Button(row, text='Копировать', font=('Arial', 11, 'bold'), bg=ACCENT, fg='white', activebackground=ACCENT, relief='flat', bd=0, padx=12, pady=8, command=self.copy_url).pack(side='left', padx=4)
        tk.Button(row, text='Перезапустить ссылку', font=('Arial', 11, 'bold'), bg=ACCENT_2, fg='white', activebackground=ACCENT_2, relief='flat', bd=0, padx=12, pady=8, command=self.restart_remote).pack(side='left', padx=4)
        tk.Label(top, text='Открой эту ссылку на телефоне в той же Wi‑Fi сети. Для удобства можно отсканировать QR-код ниже.', font=('Arial', 11), bg=CARD_BG, fg=SUBTEXT, justify='left').pack(anchor='w', padx=14, pady=(0, 12))

        qr_sec = self._section(self.tab_remote, 'QR-код')
        qr_sec.pack(fill='both', expand=True, pady=8)
        self.qr_label = tk.Label(qr_sec, text='QR-код готовится...', font=('Arial', 12), bg=CARD_BG, fg=TEXT)
        self.qr_label.pack(padx=18, pady=18)
        self.remote_status = tk.Label(qr_sec, text='', font=('Arial', 11), bg=CARD_BG, fg=SUBTEXT, justify='left')
        self.remote_status.pack(anchor='w', padx=14, pady=(2, 12))

    def refresh_stats_text(self):
        st = self.app.stats
        text = (
            f"Монетки: {st.get('coins', 0)}\n"
            f"Решено заданий: {st.get('total_tasks_completed', 0)}\n"
            f"Завершено перерывов: {st.get('breaks_completed', 0)}\n"
            f"Ошибок: {st.get('wrong_answers', 0)}\n"
            f"Штрафных секунд накоплено: {st.get('penalty_seconds_total', 0)}\n"
            f"Выбранный класс: {GRADE_CONFIGS.get(self.app.selected_grade, {}).get('label', 'ещё не выбран')}"
        )
        self.stats_text.config(text=text)

    def save_audio_settings(self):
        self.app.settings['music_enabled'] = bool(self.music_enabled_var.get())
        self.app.settings['sounds_enabled'] = bool(self.sounds_enabled_var.get())
        save_settings(self.app.settings)
        if hasattr(self.app, 'sound'):
            self.app.sound.settings = self.app.settings
            self.app.sound.stop_music()
            if self.app.break_active and self.app.settings.get('music_enabled', True):
                self.app.sound.start_music()
        self.audio_status.config(text='Настройки звука сохранены', fg=ACCENT_2)

    def choose_music(self):
        path = filedialog.askopenfilename(parent=self, title='Выберите WAV файл', filetypes=[('WAV files', '*.wav')])
        if not path:
            return
        try:
            assets = _v17_assets_dir()
            target = assets / 'custom_bg.wav'
            shutil.copy2(path, target)
            self.app.settings['music_file'] = str(target)
            save_settings(self.app.settings)
            self.music_path_var.set(str(target))
            if hasattr(self.app, 'sound'):
                self.app.sound.settings = self.app.settings
                self.app.sound.stop_music()
                if self.app.break_active and self.app.settings.get('music_enabled', True):
                    self.app.sound.start_music()
            self.audio_status.config(text='Своя музыка сохранена', fg=ACCENT_2)
        except Exception as e:
            self.audio_status.config(text=f'Ошибка музыки: {e}', fg=BAD)
            log_message(f'choose_music error: {e}')

    def clear_music(self):
        self.app.settings['music_file'] = ''
        save_settings(self.app.settings)
        self.music_path_var.set('')
        if hasattr(self.app, 'sound'):
            self.app.sound.settings = self.app.settings
            self.app.sound.stop_music()
            if self.app.break_active and self.app.settings.get('music_enabled', True):
                self.app.sound.start_music()
        self.audio_status.config(text='Своя музыка очищена. Будет играть встроенная.', fg=ACCENT_2)

    def preview_music(self):
        self.save_audio_settings()
        if hasattr(self.app, 'sound'):
            self.app.sound.stop_music()
            self.app.sound.start_music()
        self.audio_status.config(text='Пробное воспроизведение запущено', fg=ACCENT_2)

    def stop_music(self):
        if hasattr(self.app, 'sound'):
            self.app.sound.stop_music()
        self.audio_status.config(text='Музыка остановлена', fg=SUBTEXT)

    def change_password(self):
        p1 = self.new_pwd1.get().strip()
        p2 = self.new_pwd2.get().strip()
        if len(p1) < 4:
            self.password_status.config(text='Пароль должен быть не короче 4 символов', fg=BAD)
            return
        if p1 != p2:
            self.password_status.config(text='Пароли не совпадают', fg=BAD)
            return
        self.app.settings['parent_password'] = p1
        save_settings(self.app.settings)
        self.new_pwd1.delete(0, tk.END)
        self.new_pwd2.delete(0, tk.END)
        self.password_status.config(text='Пароль сохранён', fg=ACCENT_2)

    def restart_remote(self):
        try:
            if hasattr(self.app, 'parent_server'):
                self.app.parent_server.stop()
                self.app.parent_panel_url = self.app.parent_server.start() or ''
            self.refresh_remote_block()
            self.remote_status.config(text='Ссылка для телефона обновлена', fg=ACCENT_2)
        except Exception as e:
            self.remote_status.config(text=f'Ошибка подключения: {e}', fg=BAD)
            log_message(f'restart_remote error: {e}')

    def copy_url(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.url_var.get())
            self.remote_status.config(text='Ссылка скопирована', fg=ACCENT_2)
        except Exception as e:
            self.remote_status.config(text=f'Не удалось скопировать: {e}', fg=BAD)

    def refresh_remote_block(self):
        url = getattr(self.app, 'parent_panel_url', '') or ''
        self.url_var.set(url)
        if not url:
            self.qr_label.config(text='Ссылка ещё не создана', image='')
            self.qr_image = None
            return
        if _v17_qrcode and _v17_ImageTk:
            try:
                img = _v17_qrcode.make(url)
                img = img.resize((230, 230))
                self.qr_image = _v17_ImageTk.PhotoImage(img)
                self.qr_label.config(image=self.qr_image, text='')
                self.remote_status.config(text='Открой ссылку или отсканируй QR-код телефоном', fg=SUBTEXT)
                return
            except Exception as e:
                log_message(f'QR generation error: {e}')
        self.qr_label.config(text=f'QR-код недоступен\nОткрой ссылку вручную:\n{url}', image='', justify='center')
        self.qr_image = None
        self.remote_status.config(text='Для QR-кода при сборке установи пакет qrcode[pil]', fg=SUBTEXT)

    def refresh_all(self):
        self.refresh_stats_text()
        self.music_enabled_var.set(bool(self.app.settings.get('music_enabled', True)))
        self.sounds_enabled_var.set(bool(self.app.settings.get('sounds_enabled', True)))
        self.music_path_var.set(str(self.app.settings.get('music_file', '') or ''))
        self.refresh_remote_block()

    def close(self):
        try:
            if self.on_close:
                self.on_close()
        finally:
            self.destroy()


def _v17_ask_parent_password(self, prompt='Введите пароль родителя'):
    try:
        pwd = simpledialog.askstring(APP_TITLE, prompt, parent=self.root, show='*')
    except Exception as e:
        log_message(f'ask_parent_password error: {e}')
        return False
    if pwd is None:
        return False
    expected = str(self.settings.get('parent_password', '1234'))
    if str(pwd) == expected:
        return True
    try:
        messagebox.showerror(APP_TITLE, 'Неверный пароль')
    except Exception:
        pass
    return False
HomeworkOverlay.ask_parent_password = _v17_ask_parent_password


def _v17_confirm_parent_exit(self):
    return self.ask_parent_password('Введите пароль родителя для закрытия программы')
HomeworkOverlay.confirm_parent_exit = _v17_confirm_parent_exit


_old_v16_init2 = HomeworkOverlay.__init__
def _v17_init(self, root):
    _old_v16_init2(self, root)
    self.settings.setdefault('music_enabled', True)
    self.settings.setdefault('sounds_enabled', True)
    self.settings.setdefault('music_file', '')
    save_settings(self.settings)
    try:
        self.sound.stop_music()
    except Exception:
        pass
    self.sound = _V17SoundManager(self.settings)
    self.parent_hub_window = None
    try:
        self.parent_btn = tk.Button(self.topbar, text='👨 Родитель', font=('Arial', 13, 'bold'), bg='#8B7EC8', fg='white', activebackground='#8B7EC8', relief='flat', bd=0, padx=14, pady=10, command=self.open_parent_hub)
        self.parent_btn.pack(side='left', padx=12, before=self.coin_label)
    except Exception as e:
        log_message(f'parent button patch error: {e}')
HomeworkOverlay.__init__ = _v17_init


def _v17_open_parent_hub(self):
    if not self.ask_parent_password('Введите пароль родителя для открытия панели'):
        return
    if getattr(self, 'parent_hub_window', None) and self.parent_hub_window.winfo_exists():
        self.parent_hub_window.lift(); self.parent_hub_window.focus_force(); return
    self.parent_hub_window = ParentHubDialog(self.root, self, on_close=lambda: self.popup_closed('parent'))
HomeworkOverlay.open_parent_hub = _v17_open_parent_hub


_old_v16_get_active_popup2 = HomeworkOverlay.get_active_popup
def _v17_get_active_popup(self):
    wins = [
        getattr(self, 'store_window', None),
        getattr(self, 'stats_window', None),
        getattr(self, 'task_editor_window', None),
        getattr(self, 'support_editor_window', None),
        getattr(self, 'parent_hub_window', None),
    ]
    for win in wins:
        try:
            if win and win.winfo_exists():
                return win
        except Exception:
            pass
    return None
HomeworkOverlay.get_active_popup = _v17_get_active_popup


_old_v16_popup_closed2 = HomeworkOverlay.popup_closed
def _v17_popup_closed(self, which):
    if which == 'parent':
        self.parent_hub_window = None
    return _old_v16_popup_closed2(self, which)
HomeworkOverlay.popup_closed = _v17_popup_closed


def main():
    install_exception_logger()
    log_message('Program start')
    root = tk.Tk()

    try:
        root.iconbitmap(resource_path('app.ico'))
    except Exception as e:
        log_message(f'Icon load skipped: {e}')

    app = HomeworkOverlay(root)
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log_message(f'Fatal startup error: {e}')
        raise
