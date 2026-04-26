from __future__ import annotations

import unittest

from minecraft_coach.app_shared import default_supports, make_child_tasks, normalize_input, t


class AppSharedTests(unittest.TestCase):
    def test_normalize_input_keeps_expected_ascii_shape(self) -> None:
        self.assertEqual(normalize_input("  ABC  "), "abc")

    def test_translation_lookup_uses_selected_language(self) -> None:
        self.assertEqual(t("en", "settings"), "Settings")
        self.assertEqual(t("pl", "settings"), "Ustawienia")

    def test_default_supports_exposes_expected_sections(self) -> None:
        supports = default_supports()

        self.assertIn("letters_ru", supports)
        self.assertIn("math_pl", supports)

    def test_make_child_tasks_returns_built_in_tasks(self) -> None:
        tasks = make_child_tasks()

        self.assertGreater(len(tasks), 0)
        self.assertTrue(all(task["mode"] == "child" for task in tasks))


if __name__ == "__main__":
    unittest.main()
