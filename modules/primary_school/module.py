from __future__ import annotations

from collections import defaultdict

from minecraft_homework_overlay_v21 import make_child_tasks


def build_module() -> dict:
    tasks_by_grade: dict[int, list[dict]] = defaultdict(list)
    for task in make_child_tasks():
        grade = int(task.get("grade") or 1)
        item = dict(task)
        item["topic_id"] = f"topic-child-{grade}"
        item["source"] = "module:primary-school"
        tasks_by_grade[grade].append(item)

    grade_content = {
        1: {
            "title_ru": "1 класс",
            "title_pl": "Klasa 1",
            "title_en": "Grade 1",
            "description_ru": "Первые числа, простые слова, чтение и вставка букв.",
            "description_pl": "Pierwsze liczby, proste słowa, czytanie i wstawianie liter.",
            "description_en": "First numbers, simple words, reading, and missing letters.",
            "lesson_ru": "Сначала вспоминаем буквы и простые примеры на сложение и вычитание. Потом читаем короткое слово или вставляем букву.",
            "lesson_pl": "Najpierw przypominamy sobie litery oraz proste dodawanie i odejmowanie. Potem czytamy krótkie słowo albo wstawiamy literę.",
            "lesson_en": "First we review letters and very simple addition and subtraction. Then we read short words or fill in a letter.",
        },
        2: {
            "title_ru": "2 класс",
            "title_pl": "Klasa 2",
            "title_en": "Grade 2",
            "description_ru": "Счёт в пределах десятков, первые умножения, чтение и орфография.",
            "description_pl": "Liczenie w zakresie dziesiątek, pierwsze mnożenie, czytanie i ortografia.",
            "description_en": "Counting within tens, first multiplication, reading, and spelling.",
            "lesson_ru": "Во втором классе важно считать без спешки, замечать закономерности и тренировать чтение коротких фраз.",
            "lesson_pl": "W drugiej klasie ważne jest spokojne liczenie, zauważanie wzorów i ćwiczenie czytania krótkich zdań.",
            "lesson_en": "In grade two it is important to count calmly, notice patterns, and practice short reading tasks.",
        },
        3: {
            "title_ru": "3 класс",
            "title_pl": "Klasa 3",
            "title_en": "Grade 3",
            "description_ru": "Умножение, деление, чтение и более длинные задания.",
            "description_pl": "Mnożenie, dzielenie, czytanie i dłuższe zadania.",
            "description_en": "Multiplication, division, reading, and longer tasks.",
            "lesson_ru": "Сначала выбираем правильное действие: умножение, деление или вычисление по шагам. Потом спокойно читаем и отвечаем.",
            "lesson_pl": "Najpierw wybieramy właściwe działanie: mnożenie, dzielenie albo liczenie krok po kroku. Potem spokojnie czytamy i odpowiadamy.",
            "lesson_en": "First choose the right operation: multiplication, division, or step-by-step calculation. Then read and answer calmly.",
        },
        4: {
            "title_ru": "4 класс",
            "title_pl": "Klasa 4",
            "title_en": "Grade 4",
            "description_ru": "Более сложный счёт, деление, выбор правильного слова и чтение.",
            "description_pl": "Trudniejsze liczenie, dzielenie, wybór poprawnego słowa i czytanie.",
            "description_en": "More complex arithmetic, division, correct word choice, and reading.",
            "lesson_ru": "В четвёртом классе важно сочетать математику, чтение и внимательность к слову. Сначала думаем, потом отвечаем.",
            "lesson_pl": "W czwartej klasie ważne jest łączenie matematyki, czytania i uważności na słowo. Najpierw myślimy, potem odpowiadamy.",
            "lesson_en": "In grade four it is important to combine math, reading, and careful spelling. Think first, answer second.",
        },
    }

    levels = []
    topics = []
    for grade in (1, 2, 3, 4):
        info = grade_content[grade]
        levels.append(
            {
                "id": f"level-child-{grade}",
                "code": str(grade),
                "sort_order": grade,
                "title_ru": info["title_ru"],
                "title_pl": info["title_pl"],
                "title_en": info["title_en"],
            }
        )
        topics.append(
            {
                "id": f"topic-child-{grade}",
                "level_id": f"level-child-{grade}",
                "slug": f"grade-{grade}-core",
                "mode": "child",
                "grade": grade,
                "theme": None,
                "sort_order": grade,
                "title_ru": f"{info['title_ru']}: основные навыки",
                "title_pl": f"{info['title_pl']}: podstawowe umiejętności",
                "title_en": f"{info['title_en']}: core skills",
                "description_ru": info["description_ru"],
                "description_pl": info["description_pl"],
                "description_en": info["description_en"],
                "metadata": {"managed_by_module": "primary-school"},
                "lessons": [
                    {
                        "title_ru": info["title_ru"],
                        "title_pl": info["title_pl"],
                        "title_en": info["title_en"],
                        "content_ru": info["lesson_ru"],
                        "content_pl": info["lesson_pl"],
                        "content_en": info["lesson_en"],
                    }
                ],
                "tasks": tasks_by_grade.get(grade, []),
            }
        )

    return {
        "id": "sphere-child",
        "slug": "primary-school",
        "sort_order": 1,
        "title_ru": "Модуль Начальная школа",
        "title_pl": "Moduł Szkoła podstawowa",
        "title_en": "Primary School Module",
        "description_ru": "1–4 класс: математика, чтение, слова и базовые навыки.",
        "description_pl": "Klasy 1–4: matematyka, czytanie, słowa i podstawowe umiejętności.",
        "description_en": "Grades 1–4: math, reading, words, and core skills.",
        "metadata": {"managed_by_module": "primary-school"},
        "levels": levels,
        "topics": topics,
    }
