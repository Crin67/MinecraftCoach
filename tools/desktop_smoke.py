from __future__ import annotations

import shutil
import socket
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import tkinter as tk

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from minecraft_homework_overlay_v23 import MinecraftCoachV23, ParentPanelV23


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def first_topic_for_module(app: MinecraftCoachV23, module: dict) -> dict:
    levels = app.db.list_levels(sphere_id=module["id"])
    if levels:
        topics = app.db.list_topics(sphere_id=module["id"], level_id=levels[0]["id"])
    else:
        topics = app.db.list_topics(sphere_id=module["id"])
    assert_true(bool(topics), "Desktop smoke expected at least one topic for the first module")
    return topics[0]


def first_module_copy() -> Path:
    source_modules = ROOT_DIR / "modules"
    module_folders = sorted(path for path in source_modules.iterdir() if path.is_dir())
    assert_true(bool(module_folders), "Desktop smoke expected at least one bundled module folder")

    temp_root = Path(tempfile.mkdtemp())
    temp_modules_dir = temp_root / "modules"
    temp_modules_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(module_folders[0], temp_modules_dir / module_folders[0].name)
    return temp_root


def cleanup_app(app: MinecraftCoachV23, root: tk.Tk) -> None:
    app.cancel_break_timer()
    app.cancel_lesson_timer()
    app.cancel_memory_timer()
    app.cancel_manual_pause_timer()
    if app.remote_sync_loop_after_id:
        root.after_cancel(app.remote_sync_loop_after_id)
        app.remote_sync_loop_after_id = None
    if app.remote_sync_debounce_after_id:
        root.after_cancel(app.remote_sync_debounce_after_id)
        app.remote_sync_debounce_after_id = None
    if app.remote_sync_poll_after_id:
        root.after_cancel(app.remote_sync_poll_after_id)
        app.remote_sync_poll_after_id = None
    stop_lan_server = getattr(app, "stop_lan_server", None)
    if callable(stop_lan_server):
        stop_lan_server()
    elif getattr(app, "lan_server", None):
        app.lan_server.stop()
        app.lan_server = None
        app.lan_url = ""


def open_parent_settings(app: MinecraftCoachV23) -> ParentPanelV23:
    if hasattr(app, "open_modal_overlay"):
        app.open_modal_overlay("settings", relwidth=1.0, relheight=1.0, replace=True)
        return ParentPanelV23(app, initial_tab="settings")

    panel = ParentPanelV23(app)
    panel.show("settings")
    return panel


def main() -> None:
    temp_root = first_module_copy()
    root = tk.Tk()
    root.geometry("1320x840")

    with (
        patch("minecraft_homework_overlay_v23.messagebox.showinfo", lambda *args, **kwargs: None),
        patch("minecraft_homework_overlay_v23.messagebox.showerror", lambda *args, **kwargs: None),
    ):
        app = MinecraftCoachV23(root)
        try:
            root.update_idletasks()
            root.update()

            temp_modules_dir = temp_root / "modules"
            app.db.modules_dir = temp_modules_dir
            app.sync_modules_from_disk(refresh_start_screen=True)
            root.update_idletasks()
            root.update()

            modules = app.db.list_modules()
            assert_true(bool(modules), "Desktop smoke expected synced modules")
            module = modules[0]
            topic = first_topic_for_module(app, module)

            app.select_topic(topic)
            root.update_idletasks()
            root.update()
            assert_true(app.current_topic is not None, "Topic selection should set current_topic")

            app.start_next_break()
            root.update_idletasks()
            root.update()
            assert_true(
                bool(app.current_task or app.lesson_blocks),
                "Break start should show a lesson block or a task",
            )

            app.begin_manual_pause()
            root.update_idletasks()
            root.update()
            assert_true(app.manual_pause_state is not None, "Manual pause should capture state")

            app.resume_from_manual_pause()
            root.update_idletasks()
            root.update()
            assert_true(app.manual_pause_state is None, "Resume should clear manual pause state")

            panel = open_parent_settings(app)
            root.update_idletasks()
            root.update()

            panel.refresh_settings()
            panel.save_settings(show_message=False, close_panel=False)
            root.update_idletasks()
            root.update()

            panel.show("modules")
            panel.refresh_module_editor()
            root.update_idletasks()
            root.update()
            assert_true(bool(panel.module_rows), "Module editor should list copied modules")

            panel.module_list.selection_clear(0, "end")
            panel.module_list.selection_set(0)
            panel.load_selected_module_manifest()
            root.update_idletasks()
            root.update()
            panel.save_selected_module_manifest()
            root.update_idletasks()
            root.update()

            free_port = find_free_port()
            app.db.update_settings({"lan_admin_enabled": True, "lan_admin_port": free_port})
            app.reload_from_db()
            start_lan_server = getattr(app, "start_lan_server_if_needed")
            try:
                started = start_lan_server(manual=True)
            except TypeError:
                started = start_lan_server()
            if started is None:
                started = bool(getattr(app, "lan_url", ""))
            assert_true(bool(started), "LAN server should start in desktop smoke")
            assert_true(bool(app.lan_url), "LAN smoke expected a non-empty LAN URL")
            stop_lan_server = getattr(app, "stop_lan_server", None)
            if callable(stop_lan_server):
                stop_lan_server()
            elif getattr(app, "lan_server", None):
                app.lan_server.stop()
                app.lan_server = None
                app.lan_url = ""

            panel.close_panel()
            root.update_idletasks()
            root.update()
            print("Desktop smoke passed.")
        finally:
            cleanup_app(app, root)
            root.destroy()
            shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
