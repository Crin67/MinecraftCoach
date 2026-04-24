from __future__ import annotations

from collections import defaultdict

from minecraft_coach.builtin_content import (
    adult_tasks,
    adult_topic_descriptions,
    lesson_blocks_by_topic,
)


def build_module() -> dict:
    topic_meta = [
        ("topic-adult-basics", "basics", "adult", "basics", 1, "База", "Podstawy", "Basics"),
        ("topic-adult-safety", "safety", "adult", "safety", 2, "Защита", "Ochrona", "Safety"),
        ("topic-adult-cables", "cables", "adult", "cables", 3, "Кабели", "Kable", "Cables"),
        ("topic-adult-motors", "motors", "adult", "motors", 4, "Двигатели", "Silniki", "Motors"),
        ("topic-adult-practice", "practice", "adult", "practice", 5, "Практика", "Praktyka", "Practice"),
        ("topic-memory-core", "memory-core", "memory", "memory", 6, "Запоминание", "Zapamiętywanie", "Memory"),
    ]
    descriptions = adult_topic_descriptions()
    lessons = lesson_blocks_by_topic()
    tasks_by_topic: dict[str, list[dict]] = defaultdict(list)

    for task in adult_tasks():
        topic_id = "topic-memory-core" if task.get("theme") == "memory" else f"topic-adult-{task.get('theme')}"
        item = dict(task)
        item["topic_id"] = topic_id
        if topic_id == "topic-memory-core":
            item["mode"] = "memory"
        item["source"] = "module:electrician"
        tasks_by_topic[topic_id].append(item)

    topics = []
    for topic_id, slug, mode, theme, sort_order, title_ru, title_pl, title_en in topic_meta:
        description = descriptions.get(topic_id, {})
        topics.append(
            {
                "id": topic_id,
                "slug": slug,
                "mode": mode,
                "grade": None,
                "theme": theme,
                "sort_order": sort_order,
                "title_ru": title_ru,
                "title_pl": title_pl,
                "title_en": title_en,
                "description_ru": description.get("ru", ""),
                "description_pl": description.get("pl", ""),
                "description_en": description.get("en", ""),
                "metadata": {"managed_by_module": "electrician"},
                "lessons": lessons.get(topic_id, []),
                "tasks": tasks_by_topic.get(topic_id, []),
            }
        )

    return {
        "id": "sphere-adult",
        "slug": "electrician",
        "sort_order": 2,
        "title_ru": "Модуль Электрик",
        "title_pl": "Moduł Elektryk",
        "title_en": "Electrician Module",
        "description_ru": "Электрика, защита, кабели, двигатели, практика и режим запоминания.",
        "description_pl": "Elektryka, ochrona, kable, silniki, praktyka i tryb zapamiętywania.",
        "description_en": "Electricity, protection, cables, motors, practice, and memory mode.",
        "metadata": {"managed_by_module": "electrician"},
        "levels": [],
        "topics": topics,
    }
