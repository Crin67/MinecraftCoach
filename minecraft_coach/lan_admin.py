from __future__ import annotations

import json
import secrets
import socket
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


SESSION_TTL_SECONDS = 60 * 60 * 6


class LanAdminServer:
    def __init__(self, app, *, host: str = "0.0.0.0") -> None:
        self.app = app
        self.host = host
        self.httpd: ThreadingHTTPServer | None = None
        self.sessions: dict[str, float] = {}
        self.url: str | None = None

    def start(self) -> str:
        if self.httpd:
            return self.url or ""
        port = int(self.app.settings.get("lan_admin_port", 8765) or 8765)
        manager = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args) -> None:
                return

            def _read_json(self) -> dict:
                length = int(self.headers.get("Content-Length", "0") or 0)
                raw = self.rfile.read(length).decode("utf-8", errors="ignore") if length else "{}"
                try:
                    return json.loads(raw or "{}")
                except Exception:
                    return {}

            def _read_form(self) -> dict[str, str]:
                length = int(self.headers.get("Content-Length", "0") or 0)
                raw = self.rfile.read(length).decode("utf-8", errors="ignore") if length else ""
                data = parse_qs(raw, keep_blank_values=True)
                return {key: values[0] if values else "" for key, values in data.items()}

            def _send_json(self, payload: dict, status: int = 200, *, session_id: str | None = None) -> None:
                raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                if session_id:
                    self.send_header(
                        "Set-Cookie",
                        f"mc_session={session_id}; HttpOnly; SameSite=Strict; Max-Age={SESSION_TTL_SECONDS}",
                    )
                self.end_headers()
                self.wfile.write(raw)

            def _send_html(self, html: str, status: int = 200, *, session_id: str | None = None) -> None:
                raw = html.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                if session_id:
                    self.send_header(
                        "Set-Cookie",
                        f"mc_session={session_id}; HttpOnly; SameSite=Strict; Max-Age={SESSION_TTL_SECONDS}",
                    )
                self.end_headers()
                self.wfile.write(raw)

            def _redirect(self, location: str) -> None:
                self.send_response(303)
                self.send_header("Location", location)
                self.end_headers()

            def _session_id(self) -> str | None:
                jar = cookies.SimpleCookie()
                header = self.headers.get("Cookie")
                if header:
                    jar.load(header)
                cookie = jar.get("mc_session")
                return cookie.value if cookie else None

            def _authorized(self) -> bool:
                session_id = self._session_id()
                return manager.is_session_valid(session_id)

            def _require_auth(self) -> bool:
                if self._authorized():
                    return True
                if "text/html" in (self.headers.get("Accept") or ""):
                    self._redirect("/")
                else:
                    self._send_json({"ok": False, "error": "forbidden"}, status=403)
                return False

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/":
                    if self._authorized():
                        self._send_html(manager.dashboard_html())
                    else:
                        self._send_html(manager.login_html())
                    return
                if parsed.path == "/dashboard":
                    if not self._require_auth():
                        return
                    self._send_html(manager.dashboard_html())
                    return
                if parsed.path == "/api/dashboard":
                    if not self._require_auth():
                        return
                    self._send_json({"ok": True, "data": manager.dashboard_data()})
                    return
                if parsed.path == "/content":
                    if not self._require_auth():
                        return
                    self._send_json({"ok": True, "data": manager.content_data()})
                    return
                if parsed.path == "/logout":
                    manager.destroy_session(self._session_id())
                    self.send_response(303)
                    self.send_header("Location", "/")
                    self.send_header("Set-Cookie", "mc_session=; Max-Age=0; HttpOnly; SameSite=Strict")
                    self.end_headers()
                    return
                self._send_json({"ok": False, "error": "not_found"}, status=404)

            def do_POST(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/auth/login":
                    data = self._read_form()
                    program_id = data.get("program_id", "").strip()
                    password = data.get("password", "")
                    expected_program_id = manager.app.settings.get("program_id", "")
                    if program_id != expected_program_id or not manager.app.db.verify_parent_password(password):
                        self._send_html(manager.login_html(error="Неверный ID программы или пароль."), status=403)
                        return
                    session_id = manager.create_session()
                    self._send_html(manager.dashboard_html(), session_id=session_id)
                    return
                if parsed.path == "/sync/push":
                    if not self._require_auth():
                        return
                    self._send_json({"ok": True, "direction": "push", "message": "Server sync scaffold is ready. Configure backend URL later."})
                    return
                if parsed.path == "/sync/pull":
                    if not self._require_auth():
                        return
                    self._send_json({"ok": True, "direction": "pull", "message": "Server sync scaffold is ready. Configure backend URL later."})
                    return
                self._send_json({"ok": False, "error": "not_found"}, status=404)

            def do_PUT(self) -> None:
                parsed = urlparse(self.path)
                if not self._require_auth():
                    return
                payload = self._read_json()
                if parsed.path == "/settings":
                    settings_payload = {
                        key: payload[key]
                        for key in (
                            "break_seconds",
                            "tasks_per_break",
                            "lesson_seconds",
                            "window_language",
                            "lan_admin_port",
                            "server_base_url",
                        )
                        if key in payload
                    }
                    manager.app.db.update_settings(settings_payload)
                    if payload.get("parent_password"):
                        manager.app.db.update_parent_password(str(payload["parent_password"]))
                    manager.app.reload_from_db()
                    self._send_json({"ok": True, "data": manager.dashboard_data()})
                    return
                if parsed.path.startswith("/topics/"):
                    topic_id = parsed.path.split("/")[-1]
                    updated = manager.app.db.update_topic(topic_id, payload)
                    manager.app.reload_from_db()
                    self._send_json({"ok": updated is not None, "data": updated})
                    return
                if parsed.path.startswith("/tasks/"):
                    task_id = parsed.path.split("/")[-1]
                    updated = manager.app.db.update_task(task_id, payload)
                    manager.app.reload_from_db()
                    self._send_json({"ok": updated is not None, "data": updated})
                    return
                self._send_json({"ok": False, "error": "not_found"}, status=404)

        self.httpd = ThreadingHTTPServer((self.host, port), Handler)
        self.url = f"http://{self.local_ip()}:{port}"
        return self._serve_in_background()

    def _serve_in_background(self) -> str:
        import threading

        if not self.httpd:
            return ""
        thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        thread.start()
        return self.url or ""

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        self.httpd = None
        self.sessions.clear()

    def local_ip(self) -> str:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def create_session(self) -> str:
        token = secrets.token_urlsafe(32)
        self.sessions[token] = time.time() + SESSION_TTL_SECONDS
        return token

    def is_session_valid(self, session_id: str | None) -> bool:
        if not session_id:
            return False
        expires_at = self.sessions.get(session_id)
        if not expires_at:
            return False
        if expires_at < time.time():
            self.sessions.pop(session_id, None)
            return False
        return True

    def destroy_session(self, session_id: str | None) -> None:
        if session_id:
            self.sessions.pop(session_id, None)

    def dashboard_data(self) -> dict:
        return self.app.db.get_dashboard_snapshot()

    def content_data(self) -> dict:
        return self.app.db.get_content_snapshot()

    def login_html(self, *, error: str = "") -> str:
        program_id = self.app.settings.get("program_id", "")
        error_html = f"<div class='error'>{error}</div>" if error else ""
        return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Minecraft Coach LAN</title>
  <style>
    :root {{
      --bg:#09152f; --card:#132650; --text:#f5f8ff; --muted:#b7c7eb; --accent:#f2c24e; --danger:#ef7e7e;
      --border:#2b4588;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Segoe UI, sans-serif; background:linear-gradient(180deg,#081127,#132650); color:var(--text); min-height:100vh; display:grid; place-items:center; padding:20px; }}
    .card {{ width:min(480px,100%); background:rgba(19,38,80,.95); border:1px solid var(--border); border-radius:24px; padding:24px; }}
    h1 {{ margin:0 0 10px; font-size:28px; }}
    p {{ color:var(--muted); line-height:1.5; }}
    label {{ display:block; margin:14px 0 6px; color:var(--muted); }}
    input {{ width:100%; padding:14px 16px; border-radius:14px; border:1px solid var(--border); background:#0a1839; color:var(--text); font-size:16px; }}
    button {{ width:100%; margin-top:18px; padding:14px 16px; border:none; border-radius:14px; background:var(--accent); color:#111; font-weight:700; font-size:16px; }}
    code {{ background:#0a1839; padding:4px 8px; border-radius:10px; }}
    .error {{ background:rgba(239,126,126,.14); border:1px solid rgba(239,126,126,.45); color:#ffd1d1; padding:12px 14px; border-radius:14px; margin:14px 0; }}
  </style>
</head>
<body>
  <form class="card" method="post" action="/auth/login">
    <h1>Панель родителя</h1>
    <p>Вход с телефона по локальной сети. Используйте <code>{program_id}</code> как ID программы и пароль родителя.</p>
    {error_html}
    <label for="program_id">ID программы</label>
    <input id="program_id" name="program_id" value="{program_id}" required>
    <label for="password">Пароль родителя</label>
    <input id="password" name="password" type="password" required>
    <button type="submit">Войти</button>
  </form>
</body>
</html>"""

    def dashboard_html(self) -> str:
        snapshot = self.content_data()
        dashboard = self.dashboard_data()
        payload = json.dumps({"content": snapshot, "dashboard": dashboard}, ensure_ascii=False).replace("</", "<\\/")
        return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Minecraft Coach Dashboard</title>
  <style>
    :root {{
      --bg:#081127; --card:#132650; --card2:#0d1b40; --text:#f5f8ff; --muted:#b7c7eb; --accent:#f2c24e; --border:#314a88;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Segoe UI, sans-serif; background:linear-gradient(180deg,#09152f,#10234b); color:var(--text); }}
    .wrap {{ width:min(1100px, calc(100% - 24px)); margin:0 auto; padding:18px 0 36px; }}
    .hero, .card {{ background:rgba(19,38,80,.96); border:1px solid var(--border); border-radius:22px; }}
    .hero {{ padding:18px; margin-bottom:16px; }}
    .hero h1 {{ margin:0 0 6px; font-size:28px; }}
    .muted {{ color:var(--muted); }}
    .stats {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:16px; }}
    .stat {{ background:var(--card2); border:1px solid var(--border); border-radius:18px; padding:14px; }}
    .stat .n {{ font-size:28px; font-weight:700; margin-top:6px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .card {{ padding:16px; }}
    label {{ display:block; margin:10px 0 6px; color:var(--muted); }}
    input, select, textarea {{ width:100%; padding:12px 14px; border-radius:14px; border:1px solid var(--border); background:#09152f; color:var(--text); }}
    textarea {{ min-height:260px; font-family:Consolas, monospace; resize:vertical; }}
    button, .btn {{
      display:inline-flex; align-items:center; justify-content:center; gap:8px;
      border:none; border-radius:14px; background:var(--accent); color:#111;
      padding:12px 16px; font-weight:700; cursor:pointer; text-decoration:none;
    }}
    .row {{ display:flex; gap:10px; flex-wrap:wrap; }}
    .small {{ font-size:13px; }}
    .topbar {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }}
    .save-msg {{ margin-top:10px; color:#c8f4c1; min-height:22px; }}
    @media (max-width: 900px) {{
      .grid, .stats {{ grid-template-columns:1fr; }}
      .row > * {{ width:100%; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="topbar">
        <div>
          <h1>Minecraft Coach</h1>
          <div class="muted">Локальная панель управления с телефона</div>
          <div class="muted small">ID программы: <strong>{dashboard["program_id"]}</strong></div>
        </div>
        <div class="row">
          <a class="btn" href="/content">JSON контент</a>
          <a class="btn" href="/logout">Выйти</a>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><div>Монеты</div><div class="n">{dashboard["stats"]["coins"]}</div></div>
        <div class="stat"><div>Правильных</div><div class="n">{dashboard["stats"]["correct"]}</div></div>
        <div class="stat"><div>Ошибок</div><div class="n">{dashboard["stats"]["wrong"]}</div></div>
        <div class="stat"><div>Заданий</div><div class="n">{dashboard["counts"]["tasks"]}</div></div>
      </div>
    </section>

    <section class="grid">
      <article class="card">
        <h2>Настройки</h2>
        <label>Интервал между паузами (сек)</label>
        <input id="break_seconds" type="number" min="30">
        <label>Количество заданий в паузе</label>
        <input id="tasks_per_break" type="number" min="1">
        <label>Время на учебный блок (сек)</label>
        <input id="lesson_seconds" type="number" min="5">
        <label>LAN port</label>
        <input id="lan_admin_port" type="number" min="1024" max="65535">
        <label>Server API URL</label>
        <input id="server_base_url" type="text" placeholder="https://example.com/api">
        <label>Язык интерфейса</label>
        <select id="window_language">
          <option value="ru">RU</option>
          <option value="pl">PL</option>
          <option value="en">EN</option>
        </select>
        <label>Новый пароль родителя</label>
        <input id="parent_password" type="password" placeholder="Оставьте пустым, если не меняете">
        <div class="muted small" style="margin-top:10px">Changing the LAN port takes effect after restarting the desktop app.</div>
        <div class="row" style="margin-top:14px">
          <button onclick="saveSettings()">Сохранить настройки</button>
        </div>
        <div id="settings_msg" class="save-msg"></div>
      </article>

      <article class="card">
        <h2>Темы и уроки</h2>
        <label>Тема</label>
        <select id="topic_select"></select>
        <label>JSON темы</label>
        <textarea id="topic_editor"></textarea>
        <div class="row" style="margin-top:14px">
          <button onclick="saveTopic()">Сохранить тему</button>
        </div>
        <div id="topic_msg" class="save-msg"></div>
      </article>

      <article class="card">
        <h2>Задания</h2>
        <label>Задание</label>
        <select id="task_select"></select>
        <label>JSON задания</label>
        <textarea id="task_editor"></textarea>
        <div class="row" style="margin-top:14px">
          <button onclick="saveTask()">Сохранить задание</button>
        </div>
        <div id="task_msg" class="save-msg"></div>
      </article>

      <article class="card">
        <h2>Ресурсы</h2>
        <div class="muted">Книга и изображения из папки <code>Electryk</code> уже индексируются в локальную БД для будущей серверной синхронизации.</div>
        <pre id="asset_preview" class="small" style="white-space:pre-wrap;margin-top:14px;background:#09152f;border:1px solid var(--border);border-radius:14px;padding:12px;"></pre>
      </article>
    </section>
  </div>

  <script>
    const STATE = {payload};
    const content = STATE.content;
    const dashboard = STATE.dashboard;

    const settingIds = ["break_seconds", "tasks_per_break", "lesson_seconds", "lan_admin_port", "server_base_url", "window_language"];
    for (const id of settingIds) {{
      document.getElementById(id).value = dashboard.settings[id];
    }}

    const topicSelect = document.getElementById("topic_select");
    const taskSelect = document.getElementById("task_select");
    const topicEditor = document.getElementById("topic_editor");
    const taskEditor = document.getElementById("task_editor");
    const assetPreview = document.getElementById("asset_preview");

    function pretty(value) {{
      return JSON.stringify(value, null, 2);
    }}

    function topicPayload(topic) {{
      const lesson = content.lesson_blocks.find(item => item.topic_id === topic.id) || {{}};
      return {{
        id: topic.id,
        title_ru: topic.title_ru,
        title_pl: topic.title_pl,
        title_en: topic.title_en,
        description_ru: topic.description_ru,
        description_pl: topic.description_pl,
        description_en: topic.description_en,
        lesson_ru: lesson.content_ru || "",
        lesson_pl: lesson.content_pl || "",
        lesson_en: lesson.content_en || ""
      }};
    }}

    function fillTopics() {{
      topicSelect.innerHTML = "";
      for (const topic of content.topics) {{
        const opt = document.createElement("option");
        opt.value = topic.id;
        opt.textContent = `${{topic.mode}} | ${{topic.title_ru}}`;
        topicSelect.appendChild(opt);
      }}
      if (content.topics.length) {{
        topicEditor.value = pretty(topicPayload(content.topics[0]));
      }}
    }}

    function fillTasks() {{
      taskSelect.innerHTML = "";
      for (const task of content.tasks) {{
        const opt = document.createElement("option");
        opt.value = task.id;
        opt.textContent = `${{task.mode}} | ${{task.title_ru}}`;
        taskSelect.appendChild(opt);
      }}
      if (content.tasks.length) {{
        taskEditor.value = pretty(content.tasks[0]);
      }}
    }}

    topicSelect.addEventListener("change", () => {{
      const topic = content.topics.find(item => item.id === topicSelect.value);
      if (topic) {{
        topicEditor.value = pretty(topicPayload(topic));
      }}
    }});

    taskSelect.addEventListener("change", () => {{
      const task = content.tasks.find(item => item.id === taskSelect.value);
      if (task) {{
        taskEditor.value = pretty(task);
      }}
    }});

    async function putJson(url, payload) {{
      const response = await fetch(url, {{
        method: "PUT",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      return response.json();
    }}

    async function saveSettings() {{
      const payload = {{
        break_seconds: Number(document.getElementById("break_seconds").value || 300),
        tasks_per_break: Number(document.getElementById("tasks_per_break").value || 2),
        lesson_seconds: Number(document.getElementById("lesson_seconds").value || 45),
        lan_admin_port: Number(document.getElementById("lan_admin_port").value || 8765),
        server_base_url: document.getElementById("server_base_url").value.trim(),
        window_language: document.getElementById("window_language").value,
        parent_password: document.getElementById("parent_password").value
      }};
      const result = await putJson("/settings", payload);
      document.getElementById("settings_msg").textContent = result.ok ? "Настройки сохранены" : "Не удалось сохранить настройки";
    }}

    async function saveTopic() {{
      const topicId = topicSelect.value;
      try {{
        const payload = JSON.parse(topicEditor.value);
        const result = await putJson(`/topics/${{topicId}}`, payload);
        document.getElementById("topic_msg").textContent = result.ok ? "Тема сохранена" : "Не удалось сохранить тему";
      }} catch (_error) {{
        document.getElementById("topic_msg").textContent = "Invalid JSON";
      }}
    }}

    async function saveTask() {{
      const taskId = taskSelect.value;
      try {{
        const payload = JSON.parse(taskEditor.value);
        const result = await putJson(`/tasks/${{taskId}}`, payload);
        document.getElementById("task_msg").textContent = result.ok ? "Задание сохранено" : "Не удалось сохранить задание";
      }} catch (_error) {{
        document.getElementById("task_msg").textContent = "Invalid JSON";
      }}
    }}

    assetPreview.textContent = pretty(content.assets.slice(0, 12));
    fillTopics();
    fillTasks();
  </script>
</body>
</html>"""
