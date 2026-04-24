const siteConfig = window.MinecraftCoachSiteConfig || {};
const apiBaseUrl = String(siteConfig.apiBaseUrl || "").replace(/\/+$/, "");
const buildApiUrl = (path) => `${apiBaseUrl}${path}`;

const catalogUrl = buildApiUrl("/downloads/catalog");
const loginUrl = buildApiUrl("/auth/login");
const dashboardUrl = buildApiUrl("/dashboard");
const sessionStorageKey = "minecraft-coach-session-token";

let refreshTimer = null;

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  if (!value) return "Размер пока неизвестен";
  const units = ["B", "KB", "MB", "GB"];
  let current = value;
  let index = 0;
  while (current >= 1024 && index < units.length - 1) {
    current /= 1024;
    index += 1;
  }
  return `${current.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "Нет данных";
  const date = new Date(
    typeof timestamp === "number" && timestamp < 1000000000000 ? timestamp * 1000 : timestamp
  );
  if (Number.isNaN(date.getTime())) return String(timestamp);
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function createModuleCard(module) {
  return `
    <article class="module-card">
      <div class="card-label">Учебный модуль</div>
      <h3>${module.title || module.slug}</h3>
      <p>${module.description || "Описание пока не заполнено, но модуль уже можно скачать и подключить в программу."}</p>
      <div class="module-meta">
        <span class="meta-chip">Тем: ${module.topic_count ?? 0}</span>
        <span class="meta-chip">Уровней: ${module.level_count ?? 0}</span>
      </div>
      <a class="button button-outline" href="${module.download_url}">Скачать модуль</a>
    </article>
  `;
}

async function loadCatalog() {
  const appMeta = document.getElementById("app-meta");
  const appTitle = document.getElementById("app-title");
  const appBtn = document.getElementById("download-app-btn");
  const heroBtn = document.getElementById("hero-download-btn");
  const status = document.getElementById("download-status");
  const modulesGrid = document.getElementById("modules-grid");

  try {
    const response = await fetch(catalogUrl, { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    const appInfo = payload.app || {};
    appTitle.textContent = appInfo.title || "Minecraft Coach Desktop";

    if (appInfo.available) {
      appMeta.textContent = `Файл: ${appInfo.filename} · ${formatBytes(appInfo.size_bytes)} · обновлён ${formatTimestamp(appInfo.updated_at)}`;
      appBtn.href = appInfo.download_url || "/downloads/app/latest";
      heroBtn.href = appInfo.download_url || "/downloads/app/latest";
      status.textContent = "Можно скачивать напрямую с сайта.";
      appBtn.classList.remove("is-disabled");
      heroBtn.classList.remove("is-disabled");
    } else {
      appMeta.textContent = "Файл приложения пока не найден в папке dist/.";
      appBtn.removeAttribute("href");
      heroBtn.removeAttribute("href");
      appBtn.classList.add("is-disabled");
      heroBtn.classList.add("is-disabled");
      status.textContent = "Загрузите или замените dist/MinecraftCoach.exe, и кнопка станет активной автоматически.";
    }

    const modules = Array.isArray(payload.modules) ? payload.modules : [];
    if (!modules.length) {
      modulesGrid.innerHTML = `
        <article class="module-card">
          <div class="card-label">Модули</div>
          <h3>Пока нет доступных модулей</h3>
          <p>Добавьте папки модулей в каталог <code>modules/</code>, и они появятся здесь автоматически.</p>
        </article>
      `;
      return;
    }
    modulesGrid.innerHTML = modules.map(createModuleCard).join("");
  } catch (error) {
    appMeta.textContent = "Не удалось получить каталог загрузок.";
    status.textContent = `Ошибка загрузки каталога: ${error instanceof Error ? error.message : String(error)}`;
    modulesGrid.innerHTML = `
      <article class="module-card">
        <div class="card-label">Ошибка</div>
        <h3>Каталог модулей недоступен</h3>
        <p>Проверьте, что backend запущен и отдаёт маршрут <code>/downloads/catalog</code>.</p>
      </article>
    `;
  }
}

function renderStateList(target, rows) {
  target.innerHTML = `
    <div class="state-list">
      ${rows
        .map(
          (row) => `
            <div class="state-row">
              <span>${row.label}</span>
              <strong>${row.value}</strong>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderDashboard(payload) {
  const sessionTitle = document.getElementById("session-title");
  const sessionUpdated = document.getElementById("session-updated");
  const dashboard = payload.dashboard || {};
  const stats = dashboard.stats || {};
  const counts = dashboard.counts || {};
  const settings = dashboard.settings || {};
  const runtime = payload.runtime || {};

  document.getElementById("monitor-dashboard").classList.remove("hidden");
  sessionTitle.textContent = `Сессия ${payload.program_id || dashboard.program_id || ""}`.trim();
  sessionUpdated.textContent = `Последнее обновление: ${formatTimestamp(payload.updated_at)}`;

  const statCards = [
    { label: "Монеты", value: stats.coins ?? 0 },
    { label: "Правильных", value: stats.correct ?? 0 },
    { label: "Ошибок", value: stats.wrong ?? 0 },
    { label: "Завершённых пауз", value: stats.completed_breaks ?? 0 },
    { label: "Тем всего", value: counts.topics ?? 0 },
    { label: "Заданий", value: counts.tasks ?? 0 },
    { label: "Детских тем", value: counts.child_topics ?? 0 },
    { label: "Взрослых тем", value: counts.adult_topics ?? 0 },
  ];

  document.getElementById("stats-grid").innerHTML = statCards
    .map(
      (card) => `
        <article class="stat-card">
          <div>${card.label}</div>
          <strong>${card.value}</strong>
        </article>
      `
    )
    .join("");

  renderStateList(document.getElementById("runtime-state"), [
    { label: "Текущий модуль", value: runtime.current_module || "Не выбран" },
    { label: "Текущая тема", value: runtime.current_topic || "Не выбрана" },
    { label: "Текущее задание", value: runtime.current_task || "Нет активного задания" },
    { label: "Состояние", value: runtime.state_label || runtime.state || "Неизвестно" },
    { label: "До следующей паузы", value: runtime.remaining_break || "Нет данных" },
    { label: "Пауза ученика", value: runtime.manual_pause || "Не активна" },
    { label: "Последний режим", value: stats.last_mode || "Нет данных" },
    { label: "Последняя активность", value: stats.last_activity || "Нет данных" },
  ]);

  renderStateList(document.getElementById("settings-state"), [
    { label: "ID программы", value: payload.program_id || dashboard.program_id || "—" },
    { label: "Язык окна", value: settings.window_language || "ru" },
    { label: "Интервал между паузами", value: `${settings.break_seconds ?? "—"} сек` },
    { label: "Заданий в паузе", value: settings.tasks_per_break ?? "—" },
    { label: "Время урока", value: `${settings.lesson_seconds ?? "—"} сек` },
    { label: "URL сервера", value: settings.server_base_url || "Не задан" },
  ]);
}

async function loadSessionDashboard() {
  const token = sessionStorage.getItem(sessionStorageKey);
  if (!token) return;
  const loginMessage = document.getElementById("login-message");
  try {
    const response = await fetch(dashboardUrl, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      throw new Error(errorPayload.detail || `HTTP ${response.status}`);
    }
    const payload = await response.json();
    renderDashboard(payload);
    loginMessage.textContent = "";
  } catch (error) {
    clearSessionState();
    loginMessage.textContent = `Не удалось открыть мониторинг: ${error instanceof Error ? error.message : String(error)}`;
  }
}

function clearSessionState() {
  sessionStorage.removeItem(sessionStorageKey);
  document.getElementById("monitor-dashboard").classList.add("hidden");
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

async function loginToSession(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const loginMessage = document.getElementById("login-message");
  const body = {
    program_id: form.program_id.value.trim(),
    parent_password: form.parent_password.value,
  };
  loginMessage.textContent = "Проверяем доступ...";

  try {
    const response = await fetch(loginUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || !payload.session_token) {
      throw new Error(payload.detail || payload.message || `HTTP ${response.status}`);
    }
    sessionStorage.setItem(sessionStorageKey, payload.session_token);
    loginMessage.textContent = "Вход выполнен. Загружаем данные...";
    await loadSessionDashboard();
    if (refreshTimer) {
      window.clearInterval(refreshTimer);
    }
    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
    form.parent_password.value = "";
  } catch (error) {
    clearSessionState();
    loginMessage.textContent = `Ошибка входа: ${error instanceof Error ? error.message : String(error)}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadCatalog();

  const form = document.getElementById("monitor-login-form");
  const refreshButton = document.getElementById("refresh-session-btn");
  const logoutButton = document.getElementById("logout-session-btn");

  form.addEventListener("submit", loginToSession);
  refreshButton.addEventListener("click", loadSessionDashboard);
  logoutButton.addEventListener("click", () => {
    clearSessionState();
    document.getElementById("login-message").textContent = "Сессия закрыта на этом устройстве.";
  });

  if (sessionStorage.getItem(sessionStorageKey)) {
    loadSessionDashboard();
    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
  }
});
