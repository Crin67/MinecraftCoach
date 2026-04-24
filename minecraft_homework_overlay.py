import tkinter as tk
from tkinter import messagebox
import random
import time
import ctypes
from ctypes import wintypes

# ============================
# Настройки
# ============================
MIN_INTERVAL_MIN = 1   # минимум минут между заданиями
MAX_INTERVAL_MIN = 2 # максимум минут между заданиями
TASKS_PER_BREAK = 1    # сколько заданий подряд нужно решить
APP_TITLE = "Учимся и играем"
WINDOW_BG = "#FFF4C7"
CARD_BG = "#FFFFFF"
ACCENT = "#4CAF50"
BAD = "#E57373"
TEXT = "#2E2E2E"
SUBTEXT = "#555555"

# Включить попытку поставить Minecraft на паузу клавишей ESC
SEND_ESC_TO_PAUSE = True

# ============================
# WinAPI helpers
# ============================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002

GetForegroundWindow = user32.GetForegroundWindow
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextW = user32.GetWindowTextW
SetForegroundWindow = user32.SetForegroundWindow
ShowWindow = user32.ShowWindow
keybd_event = user32.keybd_event

SW_RESTORE = 9


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


# ============================
# Генератор заданий
# ============================
VOWELS = "аеёиоуыэюя"

SHORT_WORDS = [
    ("м_ма", "ама", "мама"),
    ("р_ка", "ека", "река"),
    ("с_но", "е", "сено"),
    ("к_т", "о", "кот"),
    ("д_м", "о", "дом"),
    ("л_са", "и", "лиса"),
    ("з_ма", "и", "зима"),
    ("р_ба", "ы", "рыба"),
]

READING_TEXTS = [
    "У Маши кот. Кот любит спать на окне.",
    "Саша идёт в школу. У него книга и карандаш.",
    "Во дворе растёт дерево. На дереве сидит птица.",
    "Летом дети играют в мяч и рисуют мелом.",
]


class TaskFactory:
    @staticmethod
    def make_math_task():
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        if random.choice([True, False]):
            prompt = f"Сколько будет {a} + {b}?"
            answer = str(a + b)
        else:
            if a < b:
                a, b = b, a
            prompt = f"Сколько будет {a} - {b}?"
            answer = str(a - b)
        return {
            "type": "input",
            "title": "Математика",
            "prompt": prompt,
            "answer": answer,
            "hint": "Напиши число и нажми Проверить",
        }

    @staticmethod
    def make_spelling_task():
        masked, missing, full = random.choice(SHORT_WORDS)
        return {
            "type": "input",
            "title": "Слово",
            "prompt": f"Вставь пропущенную букву: {masked}",
            "answer": missing,
            "hint": f"Какое слово получится целиком? {full}",
        }

    @staticmethod
    def make_reading_task():
        text = random.choice(READING_TEXTS)
        return {
            "type": "button",
            "title": "Чтение",
            "prompt": f"Прочитай вслух:\n\n{text}",
            "answer": "read_ok",
            "hint": "Когда ребёнок прочитает, нажмите кнопку ниже",
        }

    @staticmethod
    def random_task():
        return random.choice([
            TaskFactory.make_math_task,
            TaskFactory.make_math_task,
            TaskFactory.make_spelling_task,
            TaskFactory.make_reading_task,
        ])()


# ============================
# Интерфейс
# ============================
class HomeworkOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=WINDOW_BG)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_attempt)

        self.task_index = 0
        self.current_task = None
        self.break_active = False
        self.next_break_ts = self.make_next_break_time()

        self.root.state('zoomed')
        self.root.bind("<Escape>", lambda e: None)

        self.main = tk.Frame(root, bg=WINDOW_BG)
        self.main.pack(fill="both", expand=True)

        self.card = tk.Frame(self.main, bg=CARD_BG, bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.75, relheight=0.7)

        self.title_label = tk.Label(
            self.card, text="Играй и учись!", font=("Arial", 28, "bold"),
            bg=CARD_BG, fg=TEXT, wraplength=1000
        )
        self.title_label.pack(pady=(30, 10))

        self.prompt_label = tk.Label(
            self.card, text="Скоро появится первое задание.", font=("Arial", 24),
            bg=CARD_BG, fg=TEXT, wraplength=1000, justify="center"
        )
        self.prompt_label.pack(pady=10)

        self.hint_label = tk.Label(
            self.card, text="", font=("Arial", 16),
            bg=CARD_BG, fg=SUBTEXT, wraplength=1000, justify="center"
        )
        self.hint_label.pack(pady=(0, 20))

        self.entry = tk.Entry(self.card, font=("Arial", 28), justify="center")
        self.entry.pack(ipady=8, ipadx=10, pady=10)
        self.entry.bind("<Return>", lambda e: self.check_answer())

        self.button_row = tk.Frame(self.card, bg=CARD_BG)
        self.button_row.pack(pady=20)

        self.check_btn = tk.Button(
            self.button_row, text="Проверить", font=("Arial", 20, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT,
            command=self.check_answer, padx=20, pady=10
        )
        self.check_btn.grid(row=0, column=0, padx=10)

        self.read_btn = tk.Button(
            self.button_row, text="Прочитано!", font=("Arial", 20, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT,
            command=self.mark_read_done, padx=20, pady=10
        )
        self.read_btn.grid(row=0, column=1, padx=10)

        self.status_label = tk.Label(
            self.main, text="Ожидание задания...", font=("Arial", 16),
            bg=WINDOW_BG, fg=TEXT
        )
        self.status_label.pack(side="bottom", pady=18)

        self.hide_overlay()
        self.tick()

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
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass

    def hide_overlay(self):
        self.root.withdraw()

    def start_break(self):
        self.break_active = True
        self.task_index = 0

        if SEND_ESC_TO_PAUSE:
            try_pause_minecraft()

        self.show_overlay()
        self.load_next_task()

    def finish_break(self):
        self.break_active = False
        self.next_break_ts = self.make_next_break_time()
        self.status_label.config(text="Молодец! Можно дальше играть 🎮")
        self.hide_overlay()

    def load_next_task(self):
        self.current_task = TaskFactory.random_task()
        self.task_index += 1

        self.title_label.config(text=self.current_task["title"])
        self.prompt_label.config(text=self.current_task["prompt"])
        self.hint_label.config(text=self.current_task["hint"])
        self.entry.delete(0, tk.END)

        if self.current_task["type"] == "input":
            self.entry.pack(ipady=8, ipadx=10, pady=10)
            self.check_btn.grid()
            self.read_btn.grid_remove()
            self.entry.focus_set()
        else:
            self.entry.pack_forget()
            self.check_btn.grid_remove()
            self.read_btn.grid()

        self.status_label.config(text=f"Задание {self.task_index} из {TASKS_PER_BREAK}")

    def check_answer(self):
        if not self.current_task or self.current_task["type"] != "input":
            return
        user_answer = self.entry.get().strip().lower()
        good_answer = self.current_task["answer"].strip().lower()

        if user_answer == good_answer:
            self.after_correct()
        else:
            self.flash_bad("Попробуй ещё раз 🙂")

    def mark_read_done(self):
        if self.current_task and self.current_task["type"] == "button":
            self.after_correct()

    def after_correct(self):
        if self.task_index >= TASKS_PER_BREAK:
            self.finish_break()
        else:
            self.load_next_task()

    def flash_bad(self, msg):
        self.status_label.config(text=msg, fg=BAD)
        self.root.after(1200, lambda: self.status_label.config(text=f"Задание {self.task_index} из {TASKS_PER_BREAK}", fg=TEXT))

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
    root = tk.Tk()
    app = HomeworkOverlay(root)
    root.mainloop()


if __name__ == "__main__":
    main()
