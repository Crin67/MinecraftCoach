
import tkinter as tk
from tkinter import messagebox
import random
import time
import ctypes
from ctypes import wintypes
import os
import threading
import wave
from datetime import datetime

# ============================
# Настройки
# ============================
MIN_INTERVAL_MIN = 5
MAX_INTERVAL_MIN = 10

# За один перерыв будет 2 задания:
# 1) русское
# 2) польское
TASKS_PER_BREAK = 2
LANGUAGE_SEQUENCE = ["ru", "pl"]

APP_TITLE = "Учимся и играем"
WINDOW_BG = "#FFF4C7"
CARD_BG = "#FFFFFF"
ACCENT = "#4CAF50"
BAD = "#E57373"
TEXT = "#2E2E2E"
SUBTEXT = "#555555"
SECONDARY = "#5C6BC0"

SEND_ESC_TO_PAUSE = True
RECORDINGS_DIR = "recordings"
FORCE_FOCUS_EVERY_MS = 500

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
    title_lower = (title or "").lower()
    if "minecraft" in title_lower:
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
            raise RuntimeError("Для записи микрофона установите sounddevice")
        self.frames = []

        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.frames.append(bytes(indata))

        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            callback=callback
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
            mp3_data = encoder.encode(raw_bytes)
            mp3_data += encoder.flush()
            with open(mp3_path, "wb") as f:
                f.write(mp3_data)
            return mp3_path

        wav_path = base_path_without_ext + ".wav"
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # int16
            wf.setframerate(self.sample_rate)
            wf.writeframes(raw_bytes)
        return wav_path


# ============================
# Данные заданий
# ============================
RU_SHORT_WORDS = [
    ("к_т", "о", "кот"),
    ("д_м", "о", "дом"),
    ("л_с", "е", "лес"),
    ("м_ч", "я", "мяч"),
    ("р_к", "а", "рак"),
    ("с_к", "о", "сок"),
    ("л_к", "у", "лук"),
    ("ж_к", "у", "жук"),
]

PL_SHORT_WORDS = [
    ("d_m", "o", "dom"),
    ("k_t", "o", "kot"),
    ("l_s", "a", "las"),
    ("r_ba", "y", "ryba"),
    ("m_cha", "u", "mucha"),
    ("s_na", "z", "szna"),  # не используем как подсказку целиком, только букву
    ("n_ga", "o", "noga"),
    ("b_t", "u", "but"),
]

PL_SHORT_WORDS = [
    ("d_m", "o", "dom"),
    ("k_t", "o", "kot"),
    ("l_s", "a", "las"),
    ("r_ba", "y", "ryba"),
    ("n_ga", "o", "noga"),
    ("b_t", "u", "but"),
    ("m_cha", "u", "mucha"),
    ("r_ka", "ę", "ręka"),
]

RU_READING_TEXTS = [
    "ма",
    "мама",
    "кот",
    "дом",
    "луна",
]

PL_READING_TEXTS = [
    "Ala ma kota.",
    "Tata czyta książkę.",
    "To jest dom.",
    "Kot lubi mleko.",
    "Mama i Ola idą do szkoły.",
]

RU_LETTER_CHOICE = [
    ("Какой первый звук в слове КОТ?", "К", ["К", "М", "Т", "О"]),
    ("Какая буква нужна: д_м", "О", ["А", "О", "У", "И"]),
    ("Выбери слово ДОМ", "ДОМ", ["ТОМ", "ДОМ", "КОТ", "СОМ"]),
]

PL_LETTER_CHOICE = [
    ("Jaka jest pierwsza litera w słowie KOT?", "K", ["K", "M", "T", "O"]),
    ("Wstaw literę: d_m", "o", ["a", "o", "u", "e"]),
    ("Wybierz słowo DOM", "DOM", ["TOM", "DOM", "KOT", "LAS"]),
]


class TaskFactory:
    @staticmethod
    def make_math_task(lang="ru"):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        do_add = random.choice([True, False])

        if do_add:
            answer = str(a + b)
            prompt = f"Сколько будет {a} + {b}?" if lang == "ru" else f"Ile będzie {a} + {b}?"
        else:
            if a < b:
                a, b = b, a
            answer = str(a - b)
            prompt = f"Сколько будет {a} - {b}?" if lang == "ru" else f"Ile będzie {a} - {b}?"

        return {
            "type": "input",
            "lang": lang,
            "title": "Математика" if lang == "ru" else "Matematyka",
            "prompt": prompt,
            "answer": answer,
            "hint": "Напиши число и нажми Проверить" if lang == "ru" else "Wpisz liczbę i kliknij Sprawdź",
        }

    @staticmethod
    def make_spelling_task(lang="ru"):
        if lang == "ru":
            masked, missing, full = random.choice(RU_SHORT_WORDS)
            return {
                "type": "input",
                "lang": lang,
                "title": "Русский язык",
                "prompt": f"Вставь букву: {masked}",
                "answer": missing,
                "hint": f"Подумай, какое слово получится: {full}",
            }
        masked, missing, full = random.choice(PL_SHORT_WORDS)
        return {
            "type": "input",
            "lang": lang,
            "title": "Język polski",
            "prompt": f"Wstaw literę: {masked}",
            "answer": missing,
            "hint": f"Pomyśl, jakie wyjdzie słowo: {full}",
        }

    @staticmethod
    def make_choice_task(lang="ru"):
        if lang == "ru":
            prompt, answer, options = random.choice(RU_LETTER_CHOICE)
            title = "Русский язык"
            hint = "Нажми на правильный ответ"
        else:
            prompt, answer, options = random.choice(PL_LETTER_CHOICE)
            title = "Język polski"
            hint = "Kliknij poprawną odpowiedź"

        opts = options[:]
        random.shuffle(opts)
        return {
            "type": "choice",
            "lang": lang,
            "title": title,
            "prompt": prompt,
            "answer": answer.lower(),
            "options": opts,
            "hint": hint,
        }

    @staticmethod
    def make_reading_task(lang="pl"):
        texts = RU_READING_TEXTS if lang == "ru" else PL_READING_TEXTS
        text = random.choice(texts)

        if lang == "ru":
            return {
                "type": "button",
                "lang": lang,
                "title": "Русская речь",
                "prompt": f"Скажи или прочитай вслух:\n\n{text}",
                "answer": "ok",
                "hint": "Сейчас пойдёт запись с микрофона. Нажмите Дальше, когда ребёнок закончит.",
                "record_audio": True,
            }

        return {
            "type": "button",
            "lang": lang,
            "title": "Czytanie po polsku",
            "prompt": f"Przeczytaj na głos:\n\n{text}",
            "answer": "ok",
            "hint": "Teraz trwa nagrywanie z mikrofonu. Kliknij Dalej, gdy dziecko skończy.",
            "record_audio": True,
        }

    @staticmethod
    def random_task(lang):
        if lang == "ru":
            candidates = [
                TaskFactory.make_math_task,
                TaskFactory.make_math_task,
                TaskFactory.make_spelling_task,
                TaskFactory.make_choice_task,
                TaskFactory.make_choice_task,
                TaskFactory.make_reading_task,
            ]
        else:
            candidates = [
                TaskFactory.make_math_task,
                TaskFactory.make_spelling_task,
                TaskFactory.make_choice_task,
                TaskFactory.make_choice_task,
                TaskFactory.make_reading_task,
                TaskFactory.make_reading_task,
            ]
        maker = random.choice(candidates)
        return maker(lang)


# ============================
# Интерфейс
# ============================
class HomeworkOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=WINDOW_BG)
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        self.task_index = 0
        self.current_task = None
        self.break_active = False
        self.next_break_ts = self.make_next_break_time()
        self.lang_queue = []
        self.recorder = None
        self.recording_path = None

        self.root.bind("<Escape>", lambda e: "break")

        self.main = tk.Frame(root, bg=WINDOW_BG)
        self.main.pack(fill="both", expand=True)

        self.card = tk.Frame(self.main, bg=CARD_BG, bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.82, relheight=0.78)

        self.lang_label = tk.Label(
            self.card, text="", font=("Arial", 18, "bold"),
            bg=CARD_BG, fg=SECONDARY
        )
        self.lang_label.pack(pady=(18, 0))

        self.title_label = tk.Label(
            self.card, text="Играй и учись!", font=("Arial", 30, "bold"),
            bg=CARD_BG, fg=TEXT, wraplength=1200
        )
        self.title_label.pack(pady=(14, 10))

        self.prompt_label = tk.Label(
            self.card, text="Скоро появится первое задание.", font=("Arial", 28),
            bg=CARD_BG, fg=TEXT, wraplength=1200, justify="center"
        )
        self.prompt_label.pack(pady=12)

        self.hint_label = tk.Label(
            self.card, text="", font=("Arial", 16),
            bg=CARD_BG, fg=SUBTEXT, wraplength=1100, justify="center"
        )
        self.hint_label.pack(pady=(0, 18))

        self.entry = tk.Entry(
            self.card, font=("Arial", 34), justify="center",
            relief="solid", bd=2
        )
        self.entry.pack(ipady=10, ipadx=20, pady=12)
        self.entry.bind("<Return>", lambda e: self.check_answer())
        self.entry.bind("<Button-1>", lambda e: self.root.after(20, self.focus_entry))
        self.entry.bind("<FocusOut>", lambda e: self.root.after(10, self.focus_entry_if_needed()))

        self.choice_frame = tk.Frame(self.card, bg=CARD_BG)
        self.choice_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.choice_frame,
                text="",
                font=("Arial", 24, "bold"),
                bg=SECONDARY,
                fg="white",
                activebackground=SECONDARY,
                command=lambda idx=i: self.check_choice(idx),
                padx=20, pady=18, width=10
            )
            r = i // 2
            c = i % 2
            btn.grid(row=r, column=c, padx=14, pady=14, sticky="nsew")
            self.choice_buttons.append(btn)
        self.choice_frame.grid_columnconfigure(0, weight=1)
        self.choice_frame.grid_columnconfigure(1, weight=1)

        self.button_row = tk.Frame(self.card, bg=CARD_BG)
        self.button_row.pack(pady=18)

        self.check_btn = tk.Button(
            self.button_row, text="Проверить / Sprawdź", font=("Arial", 22, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT,
            command=self.check_answer, padx=24, pady=12
        )
        self.check_btn.grid(row=0, column=0, padx=10)

        self.next_btn = tk.Button(
            self.button_row, text="Дальше / Dalej", font=("Arial", 22, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT,
            command=self.mark_button_done, padx=24, pady=12
        )
        self.next_btn.grid(row=0, column=1, padx=10)

        self.status_label = tk.Label(
            self.main, text="Ожидание задания...", font=("Arial", 18, "bold"),
            bg=WINDOW_BG, fg=TEXT
        )
        self.status_label.pack(side="bottom", pady=16)

        self.hide_overlay()
        self.tick()

    def focus_entry(self):
        if self.break_active and self.current_task and self.current_task.get("type") == "input":
            try:
                self.entry.focus_force()
                self.entry.icursor(tk.END)
            except Exception:
                pass

    def focus_entry_if_needed(self):
        return lambda: self.focus_entry()

    def make_next_break_time(self):
        mins = random.randint(MIN_INTERVAL_MIN, MAX_INTERVAL_MIN)
        return time.time() + mins * 60

    def on_close_attempt(self):
        if self.break_active:
            return
        if messagebox.askyesno(APP_TITLE, "Закрыть программу?"):
            self.root.destroy()

    def show_overlay(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        self.root.lift()
        self.root.update_idletasks()
        try:
            hwnd = self.root.winfo_id()
            force_window_topmost(hwnd)
        except Exception:
            pass
        try:
            self.root.focus_force()
        except Exception:
            pass

    def hide_overlay(self):
        self.root.withdraw()

    def start_break(self):
        self.break_active = True
        self.task_index = 0
        self.lang_queue = LANGUAGE_SEQUENCE[:]

        if SEND_ESC_TO_PAUSE:
            try_pause_minecraft()

        self.show_overlay()
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
            lang = self.current_task.get("lang", "xx")
            self.recording_path = os.path.join(RECORDINGS_DIR, f"{lang}_{now}")
            self.status_label.config(text="Идёт запись микрофона... / Trwa nagrywanie mikrofonu...", fg=SECONDARY)
        except Exception as e:
            self.recorder = None
            self.recording_path = None
            self.status_label.config(
                text=f"Запись не запустилась: {e}",
                fg=BAD
            )

    def stop_recording_if_needed(self):
        if not self.recorder:
            return
        try:
            saved_path = self.recorder.stop_and_save(self.recording_path)
            if saved_path:
                self.status_label.config(text=f"Запись сохранена: {saved_path}", fg=SECONDARY)
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

        lang = self.lang_queue.pop(0)
        self.current_task = TaskFactory.random_task(lang)
        self.task_index += 1

        self.lang_label.config(
            text="Русское задание" if lang == "ru" else "Zadanie po polsku"
        )
        self.title_label.config(text=self.current_task["title"])
        self.prompt_label.config(text=self.current_task["prompt"])
        self.hint_label.config(text=self.current_task["hint"])
        self.entry.delete(0, tk.END)

        self.entry.pack_forget()
        self.choice_frame.pack_forget()
        self.check_btn.grid_remove()
        self.next_btn.grid_remove()

        task_type = self.current_task["type"]

        if task_type == "input":
            self.entry.pack(ipady=10, ipadx=20, pady=14)
            self.check_btn.grid()
            self.root.after(80, self.focus_entry)
        elif task_type == "choice":
            options = self.current_task["options"]
            for i, btn in enumerate(self.choice_buttons):
                if i < len(options):
                    btn.config(text=options[i], state="normal")
                    btn.grid()
                else:
                    btn.grid_remove()
            self.choice_frame.pack(pady=12)
        else:
            self.next_btn.grid()
            self.start_recording_if_needed()

        self.status_label.config(text=f"Задание {self.task_index} из {TASKS_PER_BREAK}", fg=TEXT)

    def check_answer(self):
        if not self.current_task or self.current_task["type"] != "input":
            return
        user_answer = self.entry.get().strip().lower()
        good_answer = self.current_task["answer"].strip().lower()

        if user_answer == good_answer:
            self.after_correct()
        else:
            self.flash_bad("Попробуй ещё раз / Spróbuj jeszcze raz 🙂")
            self.root.after(50, self.focus_entry)

    def check_choice(self, idx):
        if not self.current_task or self.current_task["type"] != "choice":
            return
        chosen = self.choice_buttons[idx].cget("text").strip().lower()
        good_answer = self.current_task["answer"].strip().lower()

        if chosen == good_answer:
            self.after_correct()
        else:
            self.flash_bad("Попробуй ещё раз / Spróbuj jeszcze raz 🙂")

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
        self.root.after(
            1400,
            lambda: self.status_label.config(text=f"Задание {self.task_index} из {TASKS_PER_BREAK}", fg=TEXT)
            if self.break_active else None
        )

    def tick(self):
        if not self.break_active:
            seconds_left = int(max(0, self.next_break_ts - time.time()))
            mins = seconds_left // 60
            secs = seconds_left % 60
            self.status_label.config(text=f"Следующее задание через {mins:02d}:{secs:02d}", fg=TEXT)
            if time.time() >= self.next_break_ts:
                self.start_break()
        self.root.after(1000, self.tick)


def main():
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    root = tk.Tk()
    app = HomeworkOverlay(root)
    root.mainloop()


if __name__ == "__main__":
    main()
