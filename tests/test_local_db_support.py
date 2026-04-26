from __future__ import annotations

import unittest

from minecraft_coach.local_db_support import (
    accepted_answers_from_task,
    normalize_stats_payload,
    normalize_task_records,
    public_settings_dict,
    task_topic_defaults,
)


class LocalDbSupportTests(unittest.TestCase):
    def test_task_topic_defaults_match_supported_modes(self) -> None:
        self.assertEqual(task_topic_defaults({"mode": "child", "grade": 3}), ("topic-child-3", "level-child-3"))
        self.assertEqual(task_topic_defaults({"mode": "adult", "theme": "memory"}), ("topic-memory-core", None))
        self.assertEqual(task_topic_defaults({"mode": "adult", "theme": "fractions"}), ("topic-adult-fractions", None))

    def test_normalize_task_records_applies_defaults(self) -> None:
        tasks = normalize_task_records([{"grade": 2, "title_ru": "Счет"}])

        self.assertEqual(tasks[0]["mode"], "child")
        self.assertEqual(tasks[0]["type"], "input")
        self.assertEqual(tasks[0]["title_en"], "Счет")
        self.assertEqual(tasks[0]["prompt_ru"], "Счет")

    def test_normalize_stats_payload_maps_legacy_keys(self) -> None:
        stats = normalize_stats_payload({"coins": "7", "solved_total": "4", "wrong_total": 2, "total_breaks_completed": "3"})

        self.assertEqual(stats["coins"], 7)
        self.assertEqual(stats["correct"], 4)
        self.assertEqual(stats["wrong"], 2)
        self.assertEqual(stats["completed_breaks"], 3)

    def test_accepted_answers_from_task_keeps_special_types(self) -> None:
        self.assertEqual(accepted_answers_from_task({"type": "reading"}), ["__read__"])
        self.assertEqual(accepted_answers_from_task({"type": "memory"}), ["__memory__"])
        self.assertEqual(accepted_answers_from_task({"answer": ["A", "B", ""]}), ["A", "B"])

    def test_public_settings_dict_hides_password_fields(self) -> None:
        public = public_settings_dict({"window_language": "ru", "parent_password_hash": "hash", "parent_password": "1234"})

        self.assertEqual(public, {"window_language": "ru"})


if __name__ == "__main__":
    unittest.main()
