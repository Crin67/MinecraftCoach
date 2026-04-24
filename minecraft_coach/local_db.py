from __future__ import annotations

import json
import random
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from minecraft_homework_overlay_v21 import (
    DEFAULT_BREAK_SECONDS,
    TASKS_PER_BREAK,
    default_supports,
    make_child_tasks,
    normalize_input,
)

from .module_loader import load_modules
from .builtin_content import (
    BUILT_IN_CONTENT_VERSION,
    adult_tasks as curated_adult_tasks,
    adult_topic_descriptions,
    lesson_blocks_by_topic,
)
from .security import hash_password, is_password_hash, verify_password


SCHEMA_VERSION = 1

DEFAULT_SETTINGS: dict[str, Any] = {
    "window_language": "ru",
    "window_geometry": "1320x840",
    "break_seconds": DEFAULT_BREAK_SECONDS,
    "tasks_per_break": TASKS_PER_BREAK,
    "lesson_seconds": 45,
    "manual_pause_uses": 1,
    "manual_pause_minutes": 2,
    "pause_upgrade_level": 0,
    "shop_extra_pause_tokens": 0,
    "shop_pending_delay_bonus_seconds": 0,
    "lan_admin_enabled": True,
    "lan_admin_port": 8765,
    "pause_minecraft_on_break": True,
    "pause_audio_during_break": False,
    "server_base_url": "",
}

DEFAULT_PARENT_PASSWORD = "1234"
BUILT_IN_CONTENT_STATE_KEY = "built_in_content_version"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _json_loads(raw: str | None, default: Any) -> Any:
    if raw in (None, ""):
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def _safe_title(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    return value or fallback


def _path_relative_to(path: Path, base: Path) -> Path | None:
    try:
        return path.relative_to(base)
    except ValueError:
        return None


class LocalDB:
    def __init__(
        self,
        path: Path,
        *,
        seed_path: Path | None = None,
        data_dir: Path | None = None,
        assets_dir: Path | None = None,
        modules_dir: Path | None = None,
    ):
        self.path = Path(path)
        self.seed_path = Path(seed_path) if seed_path else None
        self.data_dir = Path(data_dir) if data_dir else self.path.parent
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self.modules_dir = Path(modules_dir) if modules_dir else self.path.parent.parent / "modules"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_database()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    def _ensure_database(self) -> None:
        if self.path.exists():
            if self._has_new_schema(self.path):
                self._ensure_schema_up_to_date()
                self._ensure_seed_data()
                self._index_assets()
                self._ensure_password_hash()
                return
            legacy = self._read_legacy_payload(self.path)
            self._backup_database(self.path)
            self.path.unlink()
            self._create_schema()
            self._seed_new_schema(legacy)
            self._index_assets()
            self._ensure_password_hash()
            return

        if self.seed_path and self.seed_path.exists():
            legacy = self._read_legacy_payload(self.seed_path)
            self._create_schema()
            self._seed_new_schema(legacy)
        else:
            self._create_schema()
            self._seed_new_schema(None)
        self._index_assets()
        self._ensure_password_hash()

    def _ensure_seed_data(self) -> None:
        with self.connect() as con:
            counts = {
                table: int(
                    con.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()["total"]
                )
                for table in ("programs", "settings", "spheres", "topics", "tasks", "supports")
            }
        if all(counts.values()):
            with self.connect() as con:
                now = utc_now()
                self._seed_taxonomy(con, now=now)
                self._apply_builtin_topic_descriptions(con, now=now)
                self._ensure_default_supports(con, now=now)
                self._ensure_default_tasks(con, now=now)
                self._seed_lesson_blocks(con, now=now)
                self._ensure_built_in_content(con, now=now)
                self._sync_modules(con, now=now)
            return
        legacy = self._read_legacy_payload(self.seed_path) if self.seed_path and self.seed_path.exists() else None
        self._seed_new_schema(legacy)

    def _ensure_default_supports(self, con: sqlite3.Connection, *, now: str) -> None:
        for key, value in default_supports().items():
            con.execute(
                """
                INSERT OR IGNORE INTO supports(key, content, updated_at)
                VALUES (?, ?, ?)
                """,
                (key, str(value), now),
            )

    def _ensure_default_tasks(self, con: sqlite3.Connection, *, now: str) -> None:
        existing_ids = {
            row["id"] for row in con.execute("SELECT id FROM tasks").fetchall()
        }
        for task in self._normalize_tasks(self._legacy_builtin_tasks()):
            if task["id"] in existing_ids:
                continue
            self._upsert_task_in_tx(con, task, now=now)

    def _apply_builtin_topic_descriptions(self, con: sqlite3.Connection, *, now: str) -> None:
        for topic_id, localized in adult_topic_descriptions().items():
            con.execute(
                """
                UPDATE topics
                SET description_ru=?,
                    description_pl=?,
                    description_en=?,
                    updated_at=?
                WHERE id=?
                """,
                (
                    localized["ru"],
                    localized["pl"],
                    localized["en"],
                    now,
                    topic_id,
                ),
            )

    def _sync_state_int(self, con: sqlite3.Connection, key: str, default: int = 0) -> int:
        row = con.execute(
            "SELECT value_json FROM sync_state WHERE key=?",
            (key,),
        ).fetchone()
        if not row:
            return default
        try:
            return int(_json_loads(row["value_json"], default))
        except Exception:
            return default

    def _set_sync_state_in_tx(
        self,
        con: sqlite3.Connection,
        key: str,
        value: Any,
        *,
        now: str | None = None,
    ) -> None:
        now = now or utc_now()
        con.execute(
            """
            INSERT OR REPLACE INTO sync_state(key, value_json, updated_at)
            VALUES (?, ?, ?)
            """,
            (key, _json_dumps(value), now),
        )

    def _replace_curated_lesson_blocks(self, con: sqlite3.Connection, *, now: str) -> None:
        for topic_id, blocks in lesson_blocks_by_topic().items():
            if not self._topic_exists(con, topic_id):
                continue
            con.execute("DELETE FROM lesson_blocks WHERE topic_id=?", (topic_id,))
            for index, block in enumerate(blocks, start=1):
                con.execute(
                    """
                    INSERT INTO lesson_blocks(
                        id, topic_id, sort_order, kind, title_ru, title_pl, title_en,
                        content_ru, content_pl, content_en, metadata_json, created_at, updated_at
                    ) VALUES (?, ?, ?, 'intro', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"lesson-{topic_id}-{index:02d}",
                        topic_id,
                        index,
                        block["title_ru"],
                        block["title_pl"],
                        block["title_en"],
                        block["content_ru"],
                        block["content_pl"],
                        block["content_en"],
                        _json_dumps(
                            {
                                "source": "built_in",
                                "content_version": BUILT_IN_CONTENT_VERSION,
                            }
                        ),
                        now,
                        now,
                    ),
                )

    def _ensure_built_in_content(self, con: sqlite3.Connection, *, now: str) -> None:
        self._apply_builtin_topic_descriptions(con, now=now)
        con.execute(
            """
            DELETE FROM tasks
            WHERE source='legacy'
              AND mode='adult'
              AND LOWER(COALESCE(theme, ''))='memorize'
            """
        )
        current_version = self._sync_state_int(con, BUILT_IN_CONTENT_STATE_KEY, default=0)
        if current_version >= BUILT_IN_CONTENT_VERSION:
            return

        curated_tasks = self._normalize_tasks(curated_adult_tasks())
        curated_ids = {task["id"] for task in curated_tasks}
        placeholders = ", ".join("?" for _ in curated_ids)
        con.execute(
            f"""
            DELETE FROM tasks
            WHERE source='built_in'
              AND mode='adult'
              AND id NOT IN ({placeholders})
            """,
            tuple(sorted(curated_ids)),
        )

        for task in curated_tasks:
            self._upsert_task_in_tx(con, task, now=now)
        self._replace_curated_lesson_blocks(con, now=now)
        self._set_sync_state_in_tx(
            con,
            BUILT_IN_CONTENT_STATE_KEY,
            BUILT_IN_CONTENT_VERSION,
            now=now,
        )

    def _sync_modules(self, con: sqlite3.Connection, *, now: str) -> None:
        modules = load_modules(self.modules_dir)
        active_module_slugs: set[str] = set()
        for module in modules:
            module_id = str(module.get("id") or module.get("slug") or "")
            if not module_id:
                continue
            module_slug = str(module.get("slug") or module_id)
            module_source = f"module:{module_slug}"
            active_module_slugs.add(module_slug)
            self._upsert_module_sphere(con, module, now=now)

            levels = list(module.get("levels") or [])
            topics = list(module.get("topics") or [])
            level_ids: list[str] = []
            topic_ids: list[str] = []
            for level in levels:
                level_id = self._upsert_module_level(con, module_id, level, now=now)
                level_ids.append(level_id)
            if level_ids:
                placeholders = ", ".join("?" for _ in level_ids)
                con.execute(
                    f"DELETE FROM levels WHERE sphere_id=? AND id NOT IN ({placeholders})",
                    (module_id, *level_ids),
                )

            for topic in topics:
                topic_payload = dict(topic)
                topic_payload.setdefault("module_slug", module_slug)
                topic_id = self._upsert_module_topic(con, module_id, topic_payload, now=now)
                topic_ids.append(topic_id)
                self._replace_module_lessons(con, topic_id, topic_payload.get("lessons") or [], now=now)
                self._replace_module_tasks(
                    con,
                    topic_id,
                    topic_payload.get("tasks") or [],
                    module_source=module_source,
                    now=now,
                )

            if topic_ids:
                rows = con.execute(
                    "SELECT id, metadata_json FROM topics WHERE sphere_id=?",
                    (module_id,),
                ).fetchall()
                for row in rows:
                    metadata = _json_loads(row["metadata_json"], {})
                    if metadata.get("managed_by_module") != module_slug:
                        continue
                    if row["id"] in topic_ids:
                        continue
                    con.execute("DELETE FROM topics WHERE id=?", (row["id"],))
            self._prune_orphan_levels(con, sphere_id=module_id)

        self._remove_stale_module_topics(con, active_module_slugs=active_module_slugs)
        self._prune_orphan_levels(con)

    def _remove_stale_module_topics(
        self,
        con: sqlite3.Connection,
        *,
        active_module_slugs: set[str],
    ) -> None:
        rows = con.execute(
            """
            SELECT id, metadata_json
            FROM topics
            """
        ).fetchall()
        for row in rows:
            metadata = _json_loads(row["metadata_json"], {})
            module_slug = str(metadata.get("managed_by_module") or "").strip()
            if not module_slug:
                continue
            if module_slug in active_module_slugs:
                continue
            con.execute("DELETE FROM topics WHERE id=?", (row["id"],))

    def _prune_orphan_levels(
        self,
        con: sqlite3.Connection,
        *,
        sphere_id: str | None = None,
    ) -> None:
        if sphere_id:
            con.execute(
                """
                DELETE FROM levels
                WHERE sphere_id=?
                  AND id NOT IN (
                    SELECT DISTINCT level_id
                    FROM topics
                    WHERE level_id IS NOT NULL
                  )
                """,
                (sphere_id,),
            )
            return
        con.execute(
            """
            DELETE FROM levels
            WHERE sphere_id IN (
                SELECT id
                FROM spheres
                WHERE COALESCE(source, '') = 'module'
            )
              AND id NOT IN (
                SELECT DISTINCT level_id
                FROM topics
                WHERE level_id IS NOT NULL
            )
            """
        )

    def _upsert_module_sphere(self, con: sqlite3.Connection, module: dict[str, Any], *, now: str) -> None:
        metadata = dict(module.get("metadata") or {})
        metadata["managed_by_module"] = str(module.get("slug") or module.get("id") or "")
        sphere_id = str(module.get("id"))
        slug = str(module.get("slug") or module.get("id"))
        sort_order = int(module.get("sort_order") or 100)
        title_ru = _safe_title(module.get("title_ru"), str(module.get("slug") or module.get("id")))
        title_pl = _safe_title(module.get("title_pl"), str(module.get("slug") or module.get("id")))
        title_en = _safe_title(module.get("title_en"), str(module.get("title_pl") or module.get("title_ru") or module.get("slug") or module.get("id")))
        description_ru = str(module.get("description_ru") or "")
        description_pl = str(module.get("description_pl") or "")
        description_en = str(module.get("description_en") or "")
        manifest_path = str(module.get("manifest_path") or "")
        metadata_json = _json_dumps(metadata)
        con.execute(
            """
            INSERT OR IGNORE INTO spheres(
                id, slug, sort_order, title_ru, title_pl, title_en,
                description_ru, description_pl, description_en,
                source, manifest_path, metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sphere_id,
                slug,
                sort_order,
                title_ru,
                title_pl,
                title_en,
                description_ru,
                description_pl,
                description_en,
                "module",
                manifest_path,
                metadata_json,
                now,
                now,
            ),
        )
        con.execute(
            """
            UPDATE spheres
            SET slug=?,
                sort_order=?,
                title_ru=?,
                title_pl=?,
                title_en=?,
                description_ru=?,
                description_pl=?,
                description_en=?,
                source='module',
                manifest_path=?,
                metadata_json=?,
                updated_at=?
            WHERE id=?
            """,
            (
                slug,
                sort_order,
                title_ru,
                title_pl,
                title_en,
                description_ru,
                description_pl,
                description_en,
                manifest_path,
                metadata_json,
                now,
                sphere_id,
            ),
        )

    def _upsert_module_level(
        self,
        con: sqlite3.Connection,
        sphere_id: str,
        level: dict[str, Any],
        *,
        now: str,
    ) -> str:
        level_id = str(level.get("id") or f"{sphere_id}-level-{level.get('code') or '1'}")
        code = str(level.get("code") or level_id)
        sort_order = int(level.get("sort_order") or 0)
        title_ru = _safe_title(level.get("title_ru"), str(level.get("code") or level_id))
        title_pl = _safe_title(level.get("title_pl"), str(level.get("code") or level_id))
        title_en = _safe_title(level.get("title_en"), str(level.get("title_pl") or level.get("title_ru") or level.get("code") or level_id))
        con.execute(
            """
            INSERT OR IGNORE INTO levels(
                id, sphere_id, code, sort_order, title_ru, title_pl, title_en, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                level_id,
                sphere_id,
                code,
                sort_order,
                title_ru,
                title_pl,
                title_en,
                now,
                now,
            ),
        )
        con.execute(
            """
            UPDATE levels
            SET sphere_id=?,
                code=?,
                sort_order=?,
                title_ru=?,
                title_pl=?,
                title_en=?,
                updated_at=?
            WHERE id=?
            """,
            (
                sphere_id,
                code,
                sort_order,
                title_ru,
                title_pl,
                title_en,
                now,
                level_id,
            ),
        )
        return level_id

    def _upsert_module_topic(
        self,
        con: sqlite3.Connection,
        sphere_id: str,
        topic: dict[str, Any],
        *,
        now: str,
    ) -> str:
        topic_id = str(topic.get("id") or f"{sphere_id}-topic-{topic.get('slug') or uuid.uuid4().hex[:8]}")
        metadata = dict(topic.get("metadata") or {})
        metadata["managed_by_module"] = str(topic.get("module_slug") or metadata.get("managed_by_module") or "")
        slug = str(topic.get("slug") or topic_id)
        mode = str(topic.get("mode") or "adult")
        sort_order = int(topic.get("sort_order") or 0)
        title_ru = _safe_title(topic.get("title_ru"), "Тема")
        title_pl = _safe_title(topic.get("title_pl"), "Temat")
        title_en = _safe_title(topic.get("title_en"), topic.get("title_pl") or topic.get("title_ru") or "Topic")
        description_ru = str(topic.get("description_ru") or "")
        description_pl = str(topic.get("description_pl") or "")
        description_en = str(topic.get("description_en") or "")
        metadata_json = _json_dumps(metadata)
        con.execute(
            """
            INSERT OR IGNORE INTO topics(
                id, sphere_id, level_id, slug, mode, grade, theme, sort_order,
                title_ru, title_pl, title_en,
                description_ru, description_pl, description_en,
                metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                topic_id,
                sphere_id,
                topic.get("level_id"),
                slug,
                mode,
                topic.get("grade"),
                topic.get("theme"),
                sort_order,
                title_ru,
                title_pl,
                title_en,
                description_ru,
                description_pl,
                description_en,
                metadata_json,
                now,
                now,
            ),
        )
        con.execute(
            """
            UPDATE topics
            SET sphere_id=?,
                level_id=?,
                slug=?,
                mode=?,
                grade=?,
                theme=?,
                sort_order=?,
                title_ru=?,
                title_pl=?,
                title_en=?,
                description_ru=?,
                description_pl=?,
                description_en=?,
                metadata_json=?,
                updated_at=?
            WHERE id=?
            """,
            (
                sphere_id,
                topic.get("level_id"),
                slug,
                mode,
                topic.get("grade"),
                topic.get("theme"),
                sort_order,
                title_ru,
                title_pl,
                title_en,
                description_ru,
                description_pl,
                description_en,
                metadata_json,
                now,
                topic_id,
            ),
        )
        return topic_id

    def _replace_module_lessons(
        self,
        con: sqlite3.Connection,
        topic_id: str,
        lessons: list[dict[str, Any]],
        *,
        now: str,
    ) -> None:
        con.execute("DELETE FROM lesson_blocks WHERE topic_id=?", (topic_id,))
        for index, lesson in enumerate(lessons, start=1):
            con.execute(
                """
                INSERT INTO lesson_blocks(
                    id, topic_id, sort_order, kind, title_ru, title_pl, title_en,
                    content_ru, content_pl, content_en, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(lesson.get("id") or f"lesson-{topic_id}-{index:02d}"),
                    topic_id,
                    int(lesson.get("sort_order") or index),
                    str(lesson.get("kind") or "intro"),
                    _safe_title(lesson.get("title_ru"), "Урок"),
                    _safe_title(lesson.get("title_pl"), "Lekcja"),
                    _safe_title(lesson.get("title_en"), lesson.get("title_pl") or lesson.get("title_ru") or "Lesson"),
                    str(lesson.get("content_ru") or ""),
                    str(lesson.get("content_pl") or ""),
                    str(lesson.get("content_en") or ""),
                    _json_dumps(dict(lesson.get("metadata") or {})),
                    now,
                    now,
                ),
            )

    def _replace_module_tasks(
        self,
        con: sqlite3.Connection,
        topic_id: str,
        tasks: list[dict[str, Any]],
        *,
        module_source: str,
        now: str,
    ) -> None:
        normalized_tasks: list[dict[str, Any]] = []
        for index, task in enumerate(tasks, start=1):
            item = dict(task)
            item["topic_id"] = topic_id
            item["source"] = module_source
            item["sort_order"] = int(item.get("sort_order") or index)
            normalized_tasks.append(self._normalize_tasks([item])[0])

        task_ids = [task["id"] for task in normalized_tasks]
        if task_ids:
            placeholders = ", ".join("?" for _ in task_ids)
            con.execute(
                f"""
                DELETE FROM tasks
                WHERE topic_id=?
                  AND id NOT IN ({placeholders})
                  AND (
                    source IN ('built_in', 'legacy')
                    OR source LIKE 'module:%'
                  )
                """,
                (topic_id, *task_ids),
            )
        else:
            con.execute(
                """
                DELETE FROM tasks
                WHERE topic_id=?
                  AND (
                    source IN ('built_in', 'legacy')
                    OR source LIKE 'module:%'
                  )
                """,
                (topic_id,),
            )

        for task in normalized_tasks:
            self._upsert_task_in_tx(con, task, now=now)

    def _backup_database(self, source: Path) -> None:
        backup_name = f"{source.stem}_legacy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{source.suffix}"
        backup_path = source.with_name(backup_name)
        shutil.copyfile(source, backup_path)

    def _has_new_schema(self, db_path: Path) -> bool:
        try:
            with sqlite3.connect(db_path) as con:
                row = con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='programs'"
                ).fetchone()
                return bool(row)
        except Exception:
            return False

    def _ensure_schema_up_to_date(self) -> None:
        with self.connect() as con:
            self._create_tables(con)
            current = con.execute(
                "SELECT value FROM meta WHERE key='schema_version'"
            ).fetchone()
            if not current:
                con.execute(
                    "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)",
                    (str(SCHEMA_VERSION),),
                )

    def _create_schema(self) -> None:
        with self.connect() as con:
            self._create_tables(con)

    def _create_tables(self, con: sqlite3.Connection) -> None:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS programs (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                locale TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS spheres (
                id TEXT PRIMARY KEY,
                slug TEXT NOT NULL UNIQUE,
                sort_order INTEGER NOT NULL,
                title_ru TEXT NOT NULL,
                title_pl TEXT NOT NULL,
                title_en TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS levels (
                id TEXT PRIMARY KEY,
                sphere_id TEXT NOT NULL REFERENCES spheres(id) ON DELETE CASCADE,
                code TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                title_ru TEXT NOT NULL,
                title_pl TEXT NOT NULL,
                title_en TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(sphere_id, code)
            );

            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                sphere_id TEXT NOT NULL REFERENCES spheres(id) ON DELETE CASCADE,
                level_id TEXT REFERENCES levels(id) ON DELETE SET NULL,
                slug TEXT NOT NULL,
                mode TEXT NOT NULL,
                grade INTEGER,
                theme TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                title_ru TEXT NOT NULL,
                title_pl TEXT NOT NULL,
                title_en TEXT NOT NULL,
                description_ru TEXT NOT NULL,
                description_pl TEXT NOT NULL,
                description_en TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS lesson_blocks (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL DEFAULT 0,
                kind TEXT NOT NULL DEFAULT 'intro',
                title_ru TEXT NOT NULL,
                title_pl TEXT NOT NULL,
                title_en TEXT NOT NULL,
                content_ru TEXT NOT NULL,
                content_pl TEXT NOT NULL,
                content_en TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL DEFAULT 0,
                mode TEXT NOT NULL,
                grade INTEGER,
                theme TEXT,
                task_type TEXT NOT NULL,
                hint_type TEXT NOT NULL DEFAULT 'math',
                source TEXT NOT NULL DEFAULT 'built_in',
                title_ru TEXT NOT NULL,
                title_pl TEXT NOT NULL,
                title_en TEXT NOT NULL DEFAULT '',
                prompt_ru TEXT NOT NULL,
                prompt_pl TEXT NOT NULL,
                prompt_en TEXT NOT NULL DEFAULT '',
                answer_display TEXT NOT NULL DEFAULT '',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS accepted_answers (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                answer_value TEXT NOT NULL,
                normalized_value TEXT NOT NULL,
                is_primary INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS task_options (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                sort_order INTEGER NOT NULL DEFAULT 0,
                option_value TEXT NOT NULL,
                is_correct INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                topic_id TEXT REFERENCES topics(id) ON DELETE SET NULL,
                sphere_id TEXT REFERENCES spheres(id) ON DELETE SET NULL,
                kind TEXT NOT NULL,
                rel_path TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS supports (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stats_summary (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                coins INTEGER NOT NULL DEFAULT 0,
                correct INTEGER NOT NULL DEFAULT 0,
                wrong INTEGER NOT NULL DEFAULT 0,
                completed_breaks INTEGER NOT NULL DEFAULT 0,
                adult_completed INTEGER NOT NULL DEFAULT 0,
                child_completed INTEGER NOT NULL DEFAULT 0,
                memory_completed INTEGER NOT NULL DEFAULT 0,
                last_mode TEXT NOT NULL DEFAULT '',
                last_activity TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stats_events (
                id TEXT PRIMARY KEY,
                program_id TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                event_payload_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                synced_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sync_state (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_topics_mode_grade
            ON topics(mode, grade, sort_order);

            CREATE INDEX IF NOT EXISTS idx_tasks_topic_order
            ON tasks(topic_id, sort_order);

            CREATE INDEX IF NOT EXISTS idx_lesson_blocks_topic_order
            ON lesson_blocks(topic_id, sort_order);

            CREATE INDEX IF NOT EXISTS idx_assets_scope
            ON assets(sphere_id, topic_id, kind, rel_path);

            CREATE INDEX IF NOT EXISTS idx_stats_events_sync
            ON stats_events(synced_at, created_at);
            """
        )
        con.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        con.execute(
            """
            INSERT OR IGNORE INTO stats_summary(
                id, coins, correct, wrong, completed_breaks, adult_completed,
                child_completed, memory_completed, last_mode, last_activity, updated_at
            ) VALUES (1, 0, 0, 0, 0, 0, 0, 0, '', '', ?)
            """,
            (utc_now(),),
        )
        self._ensure_sphere_columns(con)

    def _ensure_sphere_columns(self, con: sqlite3.Connection) -> None:
        columns = {
            row["name"] for row in con.execute("PRAGMA table_info(spheres)").fetchall()
        }
        additions = {
            "description_ru": "TEXT NOT NULL DEFAULT ''",
            "description_pl": "TEXT NOT NULL DEFAULT ''",
            "description_en": "TEXT NOT NULL DEFAULT ''",
            "source": "TEXT NOT NULL DEFAULT 'legacy'",
            "manifest_path": "TEXT NOT NULL DEFAULT ''",
            "metadata_json": "TEXT NOT NULL DEFAULT '{}'",
        }
        for name, ddl in additions.items():
            if name in columns:
                continue
            con.execute(f"ALTER TABLE spheres ADD COLUMN {name} {ddl}")

    def _seed_new_schema(self, legacy: dict[str, Any] | None) -> None:
        now = utc_now()
        settings = dict(DEFAULT_SETTINGS)
        settings.update((legacy or {}).get("settings", {}))
        stats = self._normalize_stats((legacy or {}).get("stats", {}))
        legacy_tasks = [
            task
            for task in ((legacy or {}).get("tasks") or [])
            if str(task.get("source") or "").lower() not in {"built_in", "legacy"}
        ]
        tasks = self._normalize_tasks(legacy_tasks)
        supports = (legacy or {}).get("supports") or default_supports()
        program_id = settings.get("program_id") or str(uuid.uuid4())[:8].upper()
        locale = settings.get("window_language", "ru")
        with self.connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO programs(id, display_name, locale, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (program_id, "Minecraft Coach Desktop", locale, now, now),
            )
            settings["program_id"] = program_id
            for key, value in settings.items():
                self._set_setting_in_tx(con, key, value, now=now)
            for key, value in supports.items():
                con.execute(
                    """
                    INSERT OR REPLACE INTO supports(key, content, updated_at)
                    VALUES (?, ?, ?)
                    """,
                    (key, str(value), now),
                )
            self._seed_taxonomy(con, now=now)
            self._apply_builtin_topic_descriptions(con, now=now)
            for task in tasks:
                self._upsert_task_in_tx(con, task, now=now)
            self._seed_lesson_blocks(con, now=now)
            self._ensure_built_in_content(con, now=now)
            self._sync_modules(con, now=now)
            self._save_stats_in_tx(con, stats, now=now, event_type="legacy_import")

    def _legacy_builtin_tasks(self) -> list[dict[str, Any]]:
        return list(make_child_tasks()) + list(curated_adult_tasks())

    def _seed_taxonomy(self, con: sqlite3.Connection, *, now: str) -> None:
        sphere_rows = [
            ("sphere-child", "child", 1, "Дети", "Dzieci", "Kids"),
            ("sphere-adult", "adult", 2, "Электрика", "Elektryka", "Electricity"),
            ("sphere-memory", "memory", 3, "Запоминание", "Zapamiętywanie", "Memory"),
        ]
        for row in sphere_rows:
            con.execute(
                """
                INSERT OR IGNORE INTO spheres(
                    id, slug, sort_order, title_ru, title_pl, title_en, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*row, now, now),
            )

        for grade in (1, 2, 3, 4):
            con.execute(
                """
                INSERT OR IGNORE INTO levels(
                    id, sphere_id, code, sort_order, title_ru, title_pl, title_en, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"level-child-{grade}",
                    "sphere-child",
                    str(grade),
                    grade,
                    f"Класс {grade}",
                    f"Klasa {grade}",
                    f"Grade {grade}",
                    now,
                    now,
                ),
            )

        topic_rows = []
        for grade in (1, 2, 3, 4):
            topic_rows.append(
                (
                    f"topic-child-{grade}",
                    "sphere-child",
                    f"level-child-{grade}",
                    f"grade-{grade}-core",
                    "child",
                    grade,
                    None,
                    grade,
                    f"Класс {grade}: основные навыки",
                    f"Klasa {grade}: podstawowe umiejętności",
                    f"Grade {grade}: core skills",
                    "Перед заданиями ребёнок изучает короткую подсказку и затем отвечает на вопросы.",
                    "Przed zadaniami dziecko czyta krótką wskazówkę, a potem odpowiada na pytania.",
                    "Before tasks the learner reviews a short hint and then answers questions.",
                )
            )

        adult_topics = [
            ("basics", 1, "База", "Podstawy", "Basics"),
            ("safety", 2, "Защита", "Ochrona", "Safety"),
            ("cables", 3, "Кабели", "Kable", "Cables"),
            ("motors", 4, "Двигатели", "Silniki", "Motors"),
            ("practice", 5, "Практика", "Praktyka", "Practice"),
        ]
        for theme, order, title_ru, title_pl, title_en in adult_topics:
            topic_rows.append(
                (
                    f"topic-adult-{theme}",
                    "sphere-adult",
                    None,
                    theme,
                    "adult",
                    None,
                    theme,
                    order,
                    title_ru,
                    title_pl,
                    title_en,
                    f"Короткий учебный блок по теме «{title_ru}», а затем вопросы и тесты.",
                    f"Krótki blok nauki na temat „{title_pl}”, a potem pytania i testy.",
                    f"A short lesson about “{title_en}”, followed by questions and tests.",
                )
            )

        topic_rows.append(
            (
                "topic-memory-core",
                "sphere-memory",
                None,
                "memory-core",
                "memory",
                None,
                "memory",
                1,
                "Карточки на запоминание",
                "Fiszki do zapamiętywania",
                "Memory cards",
                "Сначала прочитай правило или формулу, затем подтвердить запоминание.",
                "Najpierw przeczytaj zasadę lub wzór, a potem potwierdź zapamiętanie.",
                "Read the rule or formula first, then confirm that you memorized it.",
            )
        )

        for row in topic_rows:
            con.execute(
                """
                INSERT OR IGNORE INTO topics(
                    id, sphere_id, level_id, slug, mode, grade, theme, sort_order,
                    title_ru, title_pl, title_en,
                    description_ru, description_pl, description_en,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*row, now, now),
            )

    def _topic_defaults_for_task(self, task: dict[str, Any]) -> tuple[str, str | None]:
        mode = task.get("mode") or "child"
        if mode == "child":
            grade = int(task.get("grade") or 1)
            return f"topic-child-{grade}", f"level-child-{grade}"
        if mode == "adult":
            theme = (task.get("theme") or "basics").strip().lower()
            if theme == "memory":
                return "topic-memory-core", None
            return f"topic-adult-{theme}", None
        return "topic-memory-core", None

    def _topic_exists(self, con: sqlite3.Connection, topic_id: str | None) -> bool:
        if not topic_id:
            return False
        row = con.execute("SELECT 1 FROM topics WHERE id=? LIMIT 1", (topic_id,)).fetchone()
        return bool(row)

    def _resolve_topic_id_for_task(self, con: sqlite3.Connection, task: dict[str, Any]) -> str:
        explicit_topic_id = task.get("topic_id")
        if self._topic_exists(con, explicit_topic_id):
            return str(explicit_topic_id)

        topic_id, _level_id = self._topic_defaults_for_task(task)
        if self._topic_exists(con, topic_id):
            return topic_id

        mode = str(task.get("mode") or "").strip().lower()
        if mode == "child":
            grade = task.get("grade")
            try:
                grade_value = int(grade)
            except Exception:
                grade_value = 1
            grade_value = min(4, max(1, grade_value))
            fallback = f"topic-child-{grade_value}"
            if self._topic_exists(con, fallback):
                return fallback
            return "topic-child-1"

        if mode == "adult":
            theme = str(task.get("theme") or "").strip().lower()
            if theme == "memory":
                return "topic-memory-core"
            if self._topic_exists(con, "topic-adult-practice"):
                return "topic-adult-practice"
            return "topic-adult-basics"

        return "topic-memory-core"

    def _normalize_tasks(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for index, task in enumerate(tasks, start=1):
            normalized = {
                "id": str(task.get("id") or f"task-{index:04d}"),
                "mode": task.get("mode") or ("child" if task.get("grade") else "adult"),
                "grade": task.get("grade"),
                "theme": task.get("theme"),
                "type": task.get("type") or task.get("task_type") or "input",
                "title_ru": _safe_title(task.get("title_ru"), "Задание"),
                "title_pl": _safe_title(task.get("title_pl"), "Zadanie"),
                "title_en": _safe_title(task.get("title_en"), task.get("title_pl") or task.get("title_ru") or "Task"),
                "prompt_ru": _safe_title(task.get("prompt_ru"), task.get("title_ru") or "Задание"),
                "prompt_pl": _safe_title(task.get("prompt_pl"), task.get("title_pl") or "Zadanie"),
                "prompt_en": _safe_title(task.get("prompt_en"), task.get("prompt_pl") or task.get("prompt_ru") or "Task"),
                "answer": task.get("answer", ""),
                "options": list(task.get("options") or []),
                "hint_type": task.get("hint_type") or "math",
                "source": task.get("source") or "built_in",
                "metadata": dict(task.get("metadata") or {}),
                "sort_order": int(task.get("sort_order") or 0),
            }
            if normalized["mode"] == "child" and normalized["grade"] is None:
                normalized["grade"] = 1
            out.append(normalized)
        return out

    def _normalize_stats(self, stats: dict[str, Any]) -> dict[str, Any]:
        return {
            "coins": int(stats.get("coins", 0) or 0),
            "correct": int(
                stats.get("correct")
                or stats.get("total_tasks_completed")
                or stats.get("solved_total")
                or 0
            ),
            "wrong": int(
                stats.get("wrong")
                or stats.get("wrong_answers")
                or stats.get("wrong_total")
                or 0
            ),
            "completed_breaks": int(
                stats.get("completed_breaks")
                or stats.get("total_breaks_completed")
                or 0
            ),
            "adult_completed": int(stats.get("adult_completed", 0) or 0),
            "child_completed": int(stats.get("child_completed", 0) or 0),
            "memory_completed": int(stats.get("memory_completed", 0) or 0),
            "last_mode": str(stats.get("last_mode", "") or ""),
            "last_activity": str(stats.get("last_activity", "") or ""),
        }

    def _set_setting_in_tx(self, con: sqlite3.Connection, key: str, value: Any, *, now: str | None = None) -> None:
        now = now or utc_now()
        con.execute(
            """
            INSERT OR REPLACE INTO settings(key, value_json, updated_at)
            VALUES (?, ?, ?)
            """,
            (key, _json_dumps(value), now),
        )

    def _save_stats_in_tx(
        self,
        con: sqlite3.Connection,
        stats: dict[str, Any],
        *,
        now: str | None = None,
        event_type: str = "stats_snapshot",
    ) -> None:
        now = now or utc_now()
        normalized = self._normalize_stats(stats)
        con.execute(
            """
            INSERT OR REPLACE INTO stats_summary(
                id, coins, correct, wrong, completed_breaks, adult_completed,
                child_completed, memory_completed, last_mode, last_activity, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalized["coins"],
                normalized["correct"],
                normalized["wrong"],
                normalized["completed_breaks"],
                normalized["adult_completed"],
                normalized["child_completed"],
                normalized["memory_completed"],
                normalized["last_mode"],
                normalized["last_activity"],
                now,
            ),
        )
        program_id = self.get_program_id(con=con)
        con.execute(
            """
            INSERT INTO stats_events(
                id, program_id, event_type, event_payload_json, created_at, synced_at
            ) VALUES (?, ?, ?, ?, ?, NULL)
            """,
            (str(uuid.uuid4()), program_id, event_type, _json_dumps(normalized), now),
        )

    def _seed_lesson_blocks(self, con: sqlite3.Connection, *, now: str) -> None:
        rows = con.execute("SELECT id, mode, grade, theme, title_ru, title_pl, title_en, description_ru, description_pl, description_en FROM topics").fetchall()
        for row in rows:
            existing = con.execute(
                "SELECT 1 FROM lesson_blocks WHERE topic_id=? LIMIT 1",
                (row["id"],),
            ).fetchone()
            if existing:
                continue
            content_ru, content_pl, content_en = self._lesson_content_for_topic(con, row)
            con.execute(
                """
                INSERT INTO lesson_blocks(
                    id, topic_id, sort_order, kind, title_ru, title_pl, title_en,
                    content_ru, content_pl, content_en, metadata_json, created_at, updated_at
                ) VALUES (?, ?, 1, 'intro', ?, ?, ?, ?, ?, ?, '{}', ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    row["id"],
                    row["title_ru"],
                    row["title_pl"],
                    row["title_en"],
                    content_ru,
                    content_pl,
                    content_en,
                    now,
                    now,
                ),
            )

    def _lesson_content_for_topic(self, con: sqlite3.Connection, topic_row: sqlite3.Row) -> tuple[str, str, str]:
        support_map = self.get_supports(con=con)
        mode = topic_row["mode"]
        grade = topic_row["grade"]
        theme = topic_row["theme"]
        if mode == "child":
            if grade == 1:
                ru = support_map.get("letters_ru") or topic_row["description_ru"]
                pl = support_map.get("letters_pl") or topic_row["description_pl"]
            elif grade == 2:
                ru = support_map.get("math_ru") or topic_row["description_ru"]
                pl = support_map.get("math_pl") or topic_row["description_pl"]
            else:
                ru = support_map.get("reading_ru") or topic_row["description_ru"]
                pl = support_map.get("reading_pl") or topic_row["description_pl"]
            return str(ru), str(pl), topic_row["description_en"]
        if mode == "adult":
            if theme == "basics":
                ru = "Изучи основы темы: напряжение, ток, мощность и базовые формулы. Затем ответь на вопросы."
                pl = "Przeczytaj podstawy tematu: napięcie, prąd, moc i podstawowe wzory. Następnie odpowiedz na pytania."
                en = "Review voltage, current, power, and the core formulas. Then answer the questions."
            elif theme == "safety":
                ru = "Сначала повтори защиту, автоматы, УЗО и правила безопасности. Потом переходи к тесту."
                pl = "Najpierw powtórz ochronę, wyłączniki, RCD i zasady bezpieczeństwa. Potem przejdź do testu."
                en = "Review protection devices, RCD, and safety rules before moving to the test."
            elif theme == "cables":
                ru = "Повтори материалы проводников, сопротивление и выбор кабеля. После этого реши задания."
                pl = "Powtórz materiały przewodników, rezystancję i dobór przewodu. Potem rozwiąż zadania."
                en = "Review conductors, resistance, and cable selection before solving tasks."
            elif theme == "motors":
                ru = "Изучи типы двигателей и принципы индукции. После этого начни вопросы."
                pl = "Przeczytaj o typach silników i zasadach indukcji. Potem rozpocznij pytania."
                en = "Study motor types and induction principles before answering questions."
            else:
                ru = topic_row["description_ru"]
                pl = topic_row["description_pl"]
                en = topic_row["description_en"]
            return str(ru), str(pl), str(en)
        return (
            "Сначала прочитай карточку и попробуй запомнить формулу или правило. Затем подтвердить запоминание.",
            "Najpierw przeczytaj kartę i spróbuj zapamiętać wzór lub zasadę. Potem potwierdź zapamiętanie.",
            "Read the card first, try to memorize the rule or formula, then confirm it.",
        )

    def _upsert_task_in_tx(self, con: sqlite3.Connection, task: dict[str, Any], *, now: str | None = None) -> None:
        now = now or utc_now()
        topic_id = self._resolve_topic_id_for_task(con, task)
        con.execute(
            """
            INSERT OR REPLACE INTO tasks(
                id, topic_id, sort_order, mode, grade, theme, task_type, hint_type,
                source, title_ru, title_pl, title_en, prompt_ru, prompt_pl, prompt_en,
                answer_display, metadata_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task["id"],
                topic_id,
                int(task.get("sort_order") or 0),
                task.get("mode") or "child",
                task.get("grade"),
                task.get("theme"),
                task.get("type") or task.get("task_type") or "input",
                task.get("hint_type") or "math",
                task.get("source") or "custom",
                _safe_title(task.get("title_ru"), "Задание"),
                _safe_title(task.get("title_pl"), "Zadanie"),
                _safe_title(task.get("title_en"), task.get("title_pl") or task.get("title_ru") or "Task"),
                _safe_title(task.get("prompt_ru"), task.get("title_ru") or "Задание"),
                _safe_title(task.get("prompt_pl"), task.get("title_pl") or "Zadanie"),
                _safe_title(task.get("prompt_en"), task.get("prompt_pl") or task.get("prompt_ru") or "Task"),
                self._answer_display(task.get("answer")),
                _json_dumps(task.get("metadata") or {}),
                now,
                now,
            ),
        )
        con.execute("DELETE FROM accepted_answers WHERE task_id=?", (task["id"],))
        con.execute("DELETE FROM task_options WHERE task_id=?", (task["id"],))
        for index, answer in enumerate(self._accepted_answers_from_task(task), start=1):
            con.execute(
                """
                INSERT INTO accepted_answers(
                    id, task_id, answer_value, normalized_value, is_primary, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    task["id"],
                    answer,
                    normalize_input(answer),
                    1 if index == 1 else 0,
                    now,
                    now,
                ),
            )
        correct_answers = {normalize_input(item) for item in self._accepted_answers_from_task(task)}
        for index, option in enumerate(task.get("options") or [], start=1):
            con.execute(
                """
                INSERT INTO task_options(
                    id, task_id, sort_order, option_value, is_correct, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    task["id"],
                    index,
                    option,
                    1 if normalize_input(option) in correct_answers else 0,
                    now,
                    now,
                ),
            )

    def _answer_display(self, answer: Any) -> str:
        if isinstance(answer, list):
            return ", ".join(str(item) for item in answer)
        return str(answer or "")

    def _accepted_answers_from_task(self, task: dict[str, Any]) -> list[str]:
        task_type = task.get("type") or task.get("task_type")
        answer = task.get("answer")
        if task_type == "reading":
            return ["__read__"]
        if task_type == "memory":
            return ["__memory__"]
        if isinstance(answer, list):
            return [str(item) for item in answer if str(item).strip()]
        if answer in (None, ""):
            return []
        return [str(answer)]

    def _read_legacy_payload(self, source: Path) -> dict[str, Any]:
        payload: dict[str, Any] = {"settings": {}, "stats": {}, "tasks": [], "supports": {}}
        with sqlite3.connect(source) as con:
            con.row_factory = sqlite3.Row
            table_names = {
                row["name"] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            if "settings" in table_names:
                cols = {row["name"] for row in con.execute("PRAGMA table_info(settings)")}
                if {"k", "v"} <= cols:
                    for row in con.execute("SELECT k, v FROM settings"):
                        payload["settings"][row["k"]] = row["v"]
                elif {"key", "value"} <= cols:
                    for row in con.execute("SELECT key, value FROM settings"):
                        payload["settings"][row["key"]] = row["value"]

            if "stats" in table_names:
                cols = {row["name"] for row in con.execute("PRAGMA table_info(stats)")}
                if {"k", "v"} <= cols:
                    for row in con.execute("SELECT k, v FROM stats"):
                        payload["stats"][row["k"]] = row["v"]
                elif {"coins", "solved_total", "wrong_total"} <= cols:
                    row = con.execute(
                        "SELECT coins, solved_total, wrong_total FROM stats LIMIT 1"
                    ).fetchone()
                    if row:
                        payload["stats"]["coins"] = row["coins"]
                        payload["stats"]["solved_total"] = row["solved_total"]
                        payload["stats"]["wrong_total"] = row["wrong_total"]

            if "supports" in table_names:
                cols = {row["name"] for row in con.execute("PRAGMA table_info(supports)")}
                if {"k", "v"} <= cols:
                    for row in con.execute("SELECT k, v FROM supports"):
                        payload["supports"][row["k"]] = row["v"]

            if "tasks" in table_names:
                cols = {row["name"] for row in con.execute("PRAGMA table_info(tasks)")}
                rows = con.execute("SELECT * FROM tasks").fetchall()
                for row in rows:
                    item = dict(row)
                    if "answer_json" in cols:
                        answer = _json_loads(item.get("answer_json"), item.get("answer_json"))
                    else:
                        answer = item.get("answer")
                    options_raw = item.get("options_json")
                    options = _json_loads(options_raw, [])
                    mode = item.get("mode") or "child"
                    grade = item.get("grade")
                    theme = item.get("theme")
                    if "grade_theme" in cols and item.get("grade_theme"):
                        grade_theme = str(item["grade_theme"])
                        if mode == "child" and grade is None:
                            try:
                                grade = int(grade_theme)
                            except Exception:
                                grade = None
                        if mode != "child" and not theme:
                            theme = grade_theme
                    payload["tasks"].append(
                        {
                            "id": item.get("id") or str(uuid.uuid4()),
                            "mode": mode if mode != "memorize" else "memory",
                            "grade": grade,
                            "theme": theme,
                            "type": item.get("type") or "input",
                            "title_ru": item.get("title_ru", ""),
                            "title_pl": item.get("title_pl", ""),
                            "title_en": item.get("title_en", ""),
                            "prompt_ru": item.get("prompt_ru", ""),
                            "prompt_pl": item.get("prompt_pl", ""),
                            "prompt_en": item.get("prompt_en", ""),
                            "answer": answer,
                            "options": options or [],
                            "hint_type": item.get("hint_type") or "math",
                            "source": item.get("source") or "legacy",
                        }
                    )

        self._merge_legacy_json_files(payload)
        return payload

    def _merge_legacy_json_files(self, payload: dict[str, Any]) -> None:
        settings_path = self.data_dir / "settings.json"
        if settings_path.exists():
            try:
                settings_data = json.loads(settings_path.read_text(encoding="utf-8"))
                payload["settings"].update(settings_data)
            except Exception:
                pass

        stats_path = self.data_dir / "stats.json"
        if stats_path.exists():
            try:
                stats_data = json.loads(stats_path.read_text(encoding="utf-8"))
                payload["stats"].update(stats_data)
            except Exception:
                pass

        custom_tasks_path = self.data_dir / "custom_tasks.json"
        if custom_tasks_path.exists():
            try:
                custom_tasks = json.loads(custom_tasks_path.read_text(encoding="utf-8"))
                for index, task in enumerate(custom_tasks, start=1):
                    payload["tasks"].append(
                        {
                            "id": task.get("id") or f"custom-json-{index:04d}",
                            "mode": task.get("mode") or ("child" if task.get("grade") else "adult"),
                            "grade": task.get("grade"),
                            "theme": task.get("theme"),
                            "type": task.get("type") or "input",
                            "title_ru": task.get("title_ru", ""),
                            "title_pl": task.get("title_pl", ""),
                            "title_en": task.get("title_en", ""),
                            "prompt_ru": task.get("prompt_ru", task.get("title_ru", "")),
                            "prompt_pl": task.get("prompt_pl", task.get("title_pl", "")),
                            "prompt_en": task.get("prompt_en", ""),
                            "answer": task.get("answer", ""),
                            "options": task.get("options") or [],
                            "hint_type": task.get("hint_type") or "math",
                            "source": task.get("source") or "json_custom",
                        }
                    )
            except Exception:
                pass

    def _index_assets(self) -> None:
        if not self.assets_dir or not self.assets_dir.exists():
            return
        now = utc_now()
        with self.connect() as con:
            for path in sorted(self.assets_dir.rglob("*")):
                if not path.is_file():
                    continue
                suffix = path.suffix.lower()
                if suffix not in {".pdf", ".jpg", ".jpeg", ".png", ".webp"}:
                    continue
                rel_path = self._asset_rel_path(path)
                kind = "document" if suffix == ".pdf" else "image"
                con.execute(
                    """
                    INSERT OR IGNORE INTO assets(
                        id, topic_id, sphere_id, kind, rel_path, title, metadata_json, created_at, updated_at
                    ) VALUES (?, NULL, 'sphere-adult', ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        kind,
                        rel_path,
                        path.name,
                        _json_dumps({"size": path.stat().st_size}),
                        now,
                        now,
                    ),
                )

    def _asset_rel_path(self, path: Path) -> str:
        bases: list[Path] = [self.path.parent.parent]
        if self.assets_dir:
            bases.append(self.assets_dir.parent)
        for base in bases:
            rel_path = _path_relative_to(path, base)
            if rel_path is not None:
                return rel_path.as_posix()
        if self.assets_dir:
            inner_path = _path_relative_to(path, self.assets_dir)
            if inner_path is not None:
                return (Path(self.assets_dir.name) / inner_path).as_posix()
            return (Path(self.assets_dir.name) / path.name).as_posix()
        return path.name

    def _ensure_password_hash(self) -> None:
        settings = self.get_settings()
        raw_value = settings.get("parent_password_hash") or settings.get("parent_password")
        with self.connect() as con:
            con.execute("DELETE FROM settings WHERE key='parent_password'")
        if raw_value and is_password_hash(str(raw_value)):
            return
        password = str(raw_value or DEFAULT_PARENT_PASSWORD)
        self.update_parent_password(password)

    def get_program_id(self, *, con: sqlite3.Connection | None = None) -> str:
        owns_connection = con is None
        con = con or self.connect()
        try:
            row = con.execute("SELECT id FROM programs ORDER BY created_at LIMIT 1").fetchone()
            if row:
                return row["id"]
            program_id = str(uuid.uuid4())[:8].upper()
            now = utc_now()
            con.execute(
                """
                INSERT INTO programs(id, display_name, locale, created_at, updated_at)
                VALUES (?, 'Minecraft Coach Desktop', 'ru', ?, ?)
                """,
                (program_id, now, now),
            )
            return program_id
        finally:
            if owns_connection:
                con.close()

    def get_settings(self) -> dict[str, Any]:
        with self.connect() as con:
            rows = con.execute("SELECT key, value_json FROM settings").fetchall()
        settings = dict(DEFAULT_SETTINGS)
        for row in rows:
            settings[row["key"]] = _json_loads(row["value_json"], row["value_json"])
        settings["program_id"] = self.get_program_id()
        if "parent_password_hash" not in settings:
            settings["parent_password_hash"] = hash_password(DEFAULT_PARENT_PASSWORD)
        return settings

    def _public_settings(self, settings: dict[str, Any] | None = None) -> dict[str, Any]:
        public_settings = dict(settings or self.get_settings())
        public_settings.pop("parent_password_hash", None)
        public_settings.pop("parent_password", None)
        return public_settings

    def update_settings(self, updates: dict[str, Any]) -> dict[str, Any]:
        allowed = set(DEFAULT_SETTINGS.keys())
        now = utc_now()
        with self.connect() as con:
            for key, value in updates.items():
                if key not in allowed:
                    continue
                self._set_setting_in_tx(con, key, value, now=now)
            if "window_language" in updates:
                con.execute(
                    "UPDATE programs SET locale=?, updated_at=? WHERE id=?",
                    (str(updates["window_language"]), now, self.get_program_id(con=con)),
                )
        return self.get_settings()

    def sync_modules_from_disk(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            self._sync_modules(con, now=utc_now())
        return self.list_modules()

    def update_parent_password(self, password: str) -> None:
        if not password:
            password = DEFAULT_PARENT_PASSWORD
        now = utc_now()
        with self.connect() as con:
            self._set_setting_in_tx(con, "parent_password_hash", hash_password(password), now=now)

    def get_parent_password_hash(self) -> str:
        with self.connect() as con:
            row = con.execute(
                "SELECT value FROM settings WHERE key='parent_password_hash' LIMIT 1"
            ).fetchone()
        return str(row["value"]) if row and row["value"] else ""

    def verify_parent_password(self, password: str) -> bool:
        settings = self.get_settings()
        stored_hash = str(settings.get("parent_password_hash", ""))
        return verify_password(password, stored_hash)

    def get_stats(self) -> dict[str, Any]:
        with self.connect() as con:
            row = con.execute("SELECT * FROM stats_summary WHERE id=1").fetchone()
        if not row:
            return self._normalize_stats({})
        return {
            "coins": int(row["coins"]),
            "correct": int(row["correct"]),
            "wrong": int(row["wrong"]),
            "completed_breaks": int(row["completed_breaks"]),
            "adult_completed": int(row["adult_completed"]),
            "child_completed": int(row["child_completed"]),
            "memory_completed": int(row["memory_completed"]),
            "last_mode": row["last_mode"],
            "last_activity": row["last_activity"],
        }

    def save_stats(self, stats: dict[str, Any]) -> None:
        with self.connect() as con:
            self._save_stats_in_tx(con, stats, now=utc_now())

    def get_supports(self, *, con: sqlite3.Connection | None = None) -> dict[str, str]:
        owns_connection = con is None
        con = con or self.connect()
        try:
            rows = con.execute("SELECT key, content FROM supports ORDER BY key").fetchall()
            if rows:
                return {row["key"]: row["content"] for row in rows}
            return {key: str(value) for key, value in default_supports().items()}
        finally:
            if owns_connection:
                con.close()

    def save_support(self, key: str, value: str) -> None:
        with self.connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO supports(key, content, updated_at)
                VALUES (?, ?, ?)
                """,
                (key, value, utc_now()),
            )

    def list_modules(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                """
                SELECT spheres.*, COUNT(topics.id) AS topic_count
                FROM spheres
                LEFT JOIN topics ON topics.sphere_id = spheres.id
                WHERE COALESCE(spheres.source, '') = 'module'
                GROUP BY spheres.id
                HAVING COUNT(topics.id) > 0
                ORDER BY spheres.sort_order, spheres.title_ru
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def list_levels(self, sphere_slug: str | None = None, *, sphere_id: str | None = None) -> list[dict[str, Any]]:
        if not sphere_slug and not sphere_id:
            return []
        with self.connect() as con:
            if sphere_id:
                rows = con.execute(
                    """
                    SELECT levels.*, spheres.slug AS sphere_slug
                    FROM levels
                    JOIN spheres ON spheres.id = levels.sphere_id
                    WHERE spheres.id = ?
                    ORDER BY levels.sort_order
                    """,
                    (sphere_id,),
                ).fetchall()
            else:
                rows = con.execute(
                    """
                    SELECT levels.*, spheres.slug AS sphere_slug
                    FROM levels
                    JOIN spheres ON spheres.id = levels.sphere_id
                    WHERE spheres.slug = ?
                    ORDER BY levels.sort_order
                    """,
                    (sphere_slug,),
                ).fetchall()
        return [dict(row) for row in rows]

    def list_topics(
        self,
        *,
        mode: str | None = None,
        sphere_slug: str | None = None,
        sphere_id: str | None = None,
        level_id: str | None = None,
        grade: int | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT topics.*, spheres.slug AS sphere_slug
            FROM topics
            JOIN spheres ON spheres.id = topics.sphere_id
            WHERE 1=1
        """
        args: list[Any] = []
        if mode:
            query += " AND topics.mode = ?"
            args.append(mode)
        if sphere_slug:
            query += " AND spheres.slug = ?"
            args.append(sphere_slug)
        if sphere_id:
            query += " AND spheres.id = ?"
            args.append(sphere_id)
        if level_id:
            query += " AND COALESCE(topics.level_id, '') = ?"
            args.append(level_id)
        if grade is not None:
            query += " AND COALESCE(topics.grade, -1) = ?"
            args.append(grade)
        query += " ORDER BY topics.sort_order, topics.title_ru"
        with self.connect() as con:
            rows = con.execute(query, args).fetchall()
        return [dict(row) for row in rows]

    def get_topic(self, topic_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM topics WHERE id=?", (topic_id,)).fetchone()
        return dict(row) if row else None

    def lesson_blocks_for_topic(self, topic_id: str) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM lesson_blocks WHERE topic_id=? ORDER BY sort_order, title_ru",
                (topic_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def tasks_for_topic(self, topic_id: str) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(
                """
                SELECT * FROM tasks
                WHERE topic_id=?
                ORDER BY sort_order, id
                """,
                (topic_id,),
            ).fetchall()
        return [self._hydrate_task(dict(row)) for row in rows]

    def all_tasks(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM tasks ORDER BY mode, COALESCE(grade,0), COALESCE(theme,''), sort_order, id").fetchall()
        return [self._hydrate_task(dict(row)) for row in rows]

    def _hydrate_task(self, task_row: dict[str, Any]) -> dict[str, Any]:
        task_id = task_row["id"]
        with self.connect() as con:
            answers = con.execute(
                """
                SELECT answer_value, is_primary
                FROM accepted_answers
                WHERE task_id=?
                ORDER BY is_primary DESC, rowid
                """,
                (task_id,),
            ).fetchall()
            options = con.execute(
                """
                SELECT option_value, is_correct
                FROM task_options
                WHERE task_id=?
                ORDER BY sort_order, rowid
                """,
                (task_id,),
            ).fetchall()
            topic = con.execute(
                "SELECT slug FROM topics WHERE id=?",
                (task_row["topic_id"],),
            ).fetchone()
        accepted = [row["answer_value"] for row in answers]
        if task_row["task_type"] == "reading":
            answer: Any = "__read__"
        elif task_row["task_type"] == "memory":
            answer = "__memory__"
        elif len(accepted) > 1:
            answer = accepted
        elif len(accepted) == 1:
            answer = accepted[0]
        else:
            answer = task_row.get("answer_display", "")
        task_row["type"] = task_row.pop("task_type")
        task_row["answer"] = answer
        task_row["metadata"] = _json_loads(task_row.pop("metadata_json", None), {})
        task_row["options"] = [row["option_value"] for row in options]
        task_row["correct_options"] = [row["option_value"] for row in options if row["is_correct"]]
        task_row["topic_slug"] = topic["slug"] if topic else ""
        task_row["accepted_answers"] = accepted
        return task_row

    def answer_matches(self, task: dict[str, Any], given: str) -> bool:
        task_type = task.get("type") or task.get("task_type")
        if task_type in {"reading", "memory"}:
            return True
        answers = task.get("accepted_answers") or []
        if not answers:
            raw_answer = task.get("answer")
            if isinstance(raw_answer, list):
                answers = [str(item) for item in raw_answer]
            elif raw_answer not in (None, ""):
                answers = [str(raw_answer)]
        normalized_given = normalize_input(given)
        candidate_values = {normalized_given}
        if normalized_given.startswith("[") and normalized_given.endswith("]"):
            candidate_values.add(normalized_given[1:-1].strip())
        elif normalized_given:
            candidate_values.add(f"[{normalized_given}]")

        normalized_answers: set[str] = set()
        for answer in answers:
            normalized_answer = normalize_input(answer)
            if not normalized_answer:
                continue
            normalized_answers.add(normalized_answer)
            if normalized_answer.startswith("[") and normalized_answer.endswith("]"):
                normalized_answers.add(normalized_answer[1:-1].strip())

        return bool(candidate_values & normalized_answers)

    def upsert_task(self, task: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_tasks([task])[0]
        normalized["sort_order"] = int(task.get("sort_order") or 0)
        if task.get("topic_id"):
            normalized["topic_id"] = str(task["topic_id"])
        with self.connect() as con:
            self._upsert_task_in_tx(con, normalized, now=utc_now())
        return self.get_task(normalized["id"]) or normalized

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return self._hydrate_task(dict(row)) if row else None

    def delete_task(self, task_id: str) -> None:
        with self.connect() as con:
            con.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def count_tasks(self) -> int:
        with self.connect() as con:
            row = con.execute("SELECT COUNT(*) AS total FROM tasks").fetchone()
        return int(row["total"]) if row else 0

    def count_assets(self) -> int:
        with self.connect() as con:
            row = con.execute("SELECT COUNT(*) AS total FROM assets").fetchone()
        return int(row["total"]) if row else 0

    def update_topic(self, topic_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        now = utc_now()
        fields = {
            "title_ru": payload.get("title_ru"),
            "title_pl": payload.get("title_pl"),
            "title_en": payload.get("title_en"),
            "description_ru": payload.get("description_ru"),
            "description_pl": payload.get("description_pl"),
            "description_en": payload.get("description_en"),
        }
        assignments = []
        args: list[Any] = []
        for key, value in fields.items():
            if value is None:
                continue
            assignments.append(f"{key}=?")
            args.append(str(value))
        if assignments:
            assignments.append("updated_at=?")
            args.append(now)
            args.append(topic_id)
            with self.connect() as con:
                con.execute(
                    f"UPDATE topics SET {', '.join(assignments)} WHERE id=?",
                    args,
                )
                lesson_ru = payload.get("lesson_ru")
                lesson_pl = payload.get("lesson_pl")
                lesson_en = payload.get("lesson_en")
                if any(value is not None for value in (lesson_ru, lesson_pl, lesson_en)):
                    lesson = con.execute(
                        """
                        SELECT id FROM lesson_blocks
                        WHERE topic_id=?
                        ORDER BY sort_order, rowid
                        LIMIT 1
                        """,
                        (topic_id,),
                    ).fetchone()
                    if lesson:
                        con.execute(
                            """
                            UPDATE lesson_blocks
                            SET content_ru=COALESCE(?, content_ru),
                                content_pl=COALESCE(?, content_pl),
                                content_en=COALESCE(?, content_en),
                                updated_at=?
                            WHERE id=?
                            """,
                            (lesson_ru, lesson_pl, lesson_en, now, lesson["id"]),
                        )
        return self.get_topic(topic_id)

    def update_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        existing = self.get_task(task_id)
        if not existing:
            return None
        merged = dict(existing)
        merged.update(payload)
        if "type" not in merged and "task_type" in merged:
            merged["type"] = merged["task_type"]
        if "accepted_answers" in payload and "answer" not in payload:
            answers = payload.get("accepted_answers") or []
            merged["answer"] = answers if len(answers) != 1 else answers[0]
        return self.upsert_task(merged)

    def get_content_snapshot(self) -> dict[str, Any]:
        with self.connect() as con:
            spheres = [dict(row) for row in con.execute("SELECT * FROM spheres ORDER BY sort_order").fetchall()]
            levels = [dict(row) for row in con.execute("SELECT * FROM levels ORDER BY sort_order").fetchall()]
            topics = [dict(row) for row in con.execute("SELECT * FROM topics ORDER BY sort_order").fetchall()]
            lessons = [dict(row) for row in con.execute("SELECT * FROM lesson_blocks ORDER BY sort_order").fetchall()]
            assets = [dict(row) for row in con.execute("SELECT * FROM assets ORDER BY rel_path").fetchall()]
        settings = self.get_settings()
        return {
            "program_id": self.get_program_id(),
            "settings": self._public_settings(settings),
            "stats": self.get_stats(),
            "supports": self.get_supports(),
            "spheres": spheres,
            "levels": levels,
            "topics": topics,
            "lesson_blocks": lessons,
            "tasks": self.all_tasks(),
            "assets": assets,
        }

    def get_dashboard_snapshot(self) -> dict[str, Any]:
        settings = self.get_settings()
        stats = self.get_stats()
        topic_counts = {
            "child_topics": len(self.list_topics(mode="child")),
            "adult_topics": len(self.list_topics(mode="adult")),
            "memory_topics": len(self.list_topics(mode="memory")),
            "topics": len(self.list_topics()),
        }
        return {
            "program_id": settings["program_id"],
            "settings": self._public_settings(settings),
            "stats": stats,
            "counts": {
                "modules": len(self.list_modules()),
                "tasks": self.count_tasks(),
                "assets": self.count_assets(),
                **topic_counts,
            },
        }
