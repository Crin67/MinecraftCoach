from __future__ import annotations

from tkinter import messagebox

from minecraft_coach.desktop_app import (
    APP_TITLE,
    DATA_DIR,
    DB_FILE,
    ELECTRYK_DIR,
    MODULES_DIR,
    ParentPanelV23,
    MinecraftCoachV23,
    localized_value,
    main,
    safe_int,
)

__all__ = [
    "APP_TITLE",
    "DATA_DIR",
    "DB_FILE",
    "ELECTRYK_DIR",
    "MODULES_DIR",
    "MinecraftCoachV23",
    "ParentPanelV23",
    "localized_value",
    "messagebox",
    "safe_int",
]


if __name__ == "__main__":
    main()
