from __future__ import annotations

import copy
import unicodedata

from .child_tasks_data import CHILD_TASKS

APP_TITLE = "Minecraft Coach"
BG = "#101214"
PANEL = "#1b1f23"
CARD = "#242a30"
CARD_2 = "#1f252b"
CENTER = "#15191d"
TEXT = "#f5f1e8"
MUTED = "#b9c0c7"
BORDER = "#3d464f"
ACCENT = "#f3bd3f"
ACCENT_2 = "#3f8f7a"
GOOD = "#45a979"
BAD = "#d85656"
DEFAULT_BREAK_SECONDS = 300
TASKS_PER_BREAK = 2

TR = {
    "ru": {
        "shop": "Магазин",
        "parent": "Родитель",
        "coins": "Монеты",
        "settings": "Настройки",
        "language": "Язык",
        "save": "Сохранить",
        "close": "Закрыть",
        "check": "Проверить",
        "next": "Дальше",
        "start": "Старт",
        "task": "Задание",
        "of": "из",
        "correct": "Правильно",
        "wrong": "Неверно. Попробуй ещё раз.",
        "reading_done": "Задание засчитано",
        "read_aloud": "Прочитай текст вслух и нажми кнопку.",
        "memory_read": "Запомни правило. После таймера нажми кнопку.",
        "remembered": "Запомнил / Запомнила",
        "password": "Пароль",
        "enter_parent_password": "Введите пароль родителя",
        "bad_password": "Неверный пароль",
        "close_parent_password": "Введите пароль родителя для закрытия",
        "break_seconds": "Интервал (сек)",
        "enter_number": "Введите число",
    },
    "pl": {
        "shop": "Sklep",
        "parent": "Rodzic",
        "coins": "Monety",
        "settings": "Ustawienia",
        "language": "Język",
        "save": "Zapisz",
        "close": "Zamknij",
        "check": "Sprawdź",
        "next": "Dalej",
        "start": "Start",
        "task": "Zadanie",
        "of": "z",
        "correct": "Dobrze",
        "wrong": "Źle. Spróbuj jeszcze raz.",
        "reading_done": "Zadanie zaliczone",
        "read_aloud": "Przeczytaj tekst na głos i naciśnij przycisk.",
        "memory_read": "Zapamiętaj zasadę. Po timerze naciśnij przycisk.",
        "remembered": "Zapamiętałem / Zapamiętałam",
        "password": "Hasło",
        "enter_parent_password": "Wpisz hasło rodzica",
        "bad_password": "Nieprawidłowe hasło",
        "close_parent_password": "Wpisz hasło rodzica, aby zamknąć program",
        "break_seconds": "Interwał (sek)",
        "enter_number": "Wpisz liczbę",
    },
    "en": {
        "shop": "Shop",
        "parent": "Parent",
        "coins": "Coins",
        "settings": "Settings",
        "language": "Language",
        "save": "Save",
        "close": "Close",
        "check": "Check",
        "next": "Next",
        "start": "Start",
        "task": "Task",
        "of": "of",
        "correct": "Correct",
        "wrong": "Wrong. Try again.",
        "reading_done": "Task completed",
        "read_aloud": "Read the text aloud and press the button.",
        "memory_read": "Memorize the rule. Press the button after the timer.",
        "remembered": "I remembered it",
        "password": "Password",
        "enter_parent_password": "Enter parent password",
        "bad_password": "Wrong password",
        "close_parent_password": "Enter parent password to close the app",
        "break_seconds": "Interval (sec)",
        "enter_number": "Enter a number",
    },
}


def t(lang: str, key: str) -> str:
    return TR.get(lang, TR["ru"]).get(key, key)


def normalize_input(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip().lower())
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    lookalikes = {
        "ё": "е",
        "і": "i",
        "ї": "i",
        "є": "e",
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
    }
    return "".join(lookalikes.get(char, char) for char in without_marks)


def default_supports() -> dict[str, str]:
    return {
        "letters_ru": "Гласные: А Е Ё И О У Ы Э Ю Я\nСогласные: Б В Г Д Ж З Й К Л М Н П Р С Т Ф Х Ц Ч Ш Щ",
        "letters_pl": "Samogłoski: A Ą E Ę I O Ó U Y\nSpółgłoski: B C Ć D F G H J K L Ł M N Ń P R S Ś T W Z Ź Ż",
        "multiplication_ru": "Таблица: 7×1=7, 7×2=14, 7×3=21, 7×4=28, 7×5=35. Смотри на закономерность.",
        "multiplication_pl": "Tabliczka: 7×1=7, 7×2=14, 7×3=21, 7×4=28, 7×5=35. Patrz na wzór.",
        "reading_ru": "Прочитай текст вслух спокойно. Потом нажми кнопку проверки.",
        "reading_pl": "Przeczytaj tekst na głos spokojnie. Potem naciśnij przycisk sprawdzenia.",
        "lesson_ru": "Сначала прочитай правило, потом ответь на вопрос по смыслу.",
        "lesson_pl": "Najpierw przeczytaj zasadę, potem odpowiedz na pytanie.",
        "math_ru": "Считай по шагам. Можно проговорить пример вслух.",
        "math_pl": "Licz krok po kroku. Można powiedzieć działanie na głos.",
    }


def make_child_tasks() -> list[dict]:
    return copy.deepcopy(CHILD_TASKS)


__all__ = [
    "ACCENT",
    "ACCENT_2",
    "APP_TITLE",
    "BAD",
    "BG",
    "BORDER",
    "CARD",
    "CARD_2",
    "CENTER",
    "DEFAULT_BREAK_SECONDS",
    "GOOD",
    "MUTED",
    "PANEL",
    "TASKS_PER_BREAK",
    "TEXT",
    "TR",
    "default_supports",
    "make_child_tasks",
    "normalize_input",
    "t",
]
