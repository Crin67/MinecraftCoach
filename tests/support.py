from __future__ import annotations


def sample_module_payload(*, module_id: str = "sample-module", slug: str = "sample-module") -> dict:
    return {
        "id": module_id,
        "slug": slug,
        "sort_order": 10,
        "title_ru": "Sample RU",
        "title_pl": "Sample PL",
        "title_en": "Sample EN",
        "description_ru": "Sample description RU",
        "description_pl": "Sample description PL",
        "description_en": "Sample description EN",
        "levels": [
            {
                "id": f"{module_id}-level-1",
                "code": "L1",
                "sort_order": 1,
                "title_ru": "Level RU",
                "title_pl": "Level PL",
                "title_en": "Level EN",
            }
        ],
        "topics": [
            {
                "id": f"{module_id}-topic-1",
                "slug": f"{slug}-topic-1",
                "mode": "adult",
                "title_ru": "Topic RU",
                "title_pl": "Topic PL",
                "title_en": "Topic EN",
                "description_ru": "Topic description RU",
                "description_pl": "Topic description PL",
                "description_en": "Topic description EN",
                "lessons": [
                    {
                        "title_ru": "Lesson RU",
                        "title_pl": "Lesson PL",
                        "title_en": "Lesson EN",
                        "content_ru": "Lesson content RU",
                        "content_pl": "Lesson content PL",
                        "content_en": "Lesson content EN",
                    }
                ],
                "tasks": [
                    {
                        "id": f"{module_id}-task-1",
                        "type": "input",
                        "mode": "adult",
                        "title_ru": "Task RU",
                        "title_pl": "Task PL",
                        "title_en": "Task EN",
                        "prompt_ru": "Prompt RU",
                        "prompt_pl": "Prompt PL",
                        "prompt_en": "Prompt EN",
                        "answer": "42",
                    }
                ],
            }
        ],
    }
