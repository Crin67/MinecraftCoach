const siteConfig = window.MinecraftCoachSiteConfig || {};
const apiBaseUrl = String(siteConfig.apiBaseUrl || "").replace(/\/+$/, "");
const buildApiUrl = (path) => `${apiBaseUrl}${path}`;

const catalogUrl = buildApiUrl("/downloads/catalog");
const loginUrl = buildApiUrl("/auth/login");
const dashboardUrl = buildApiUrl("/dashboard");
const sessionStorageKey = "minecraft-coach-session-token";

let refreshTimer = null;

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    const replacements = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return replacements[char] || char;
  });
}

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

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function humanize(value, fallback = "—") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

function humanizeBoolean(value, truthy, falsy) {
  if (value === true) return truthy;
  if (value === false) return falsy;
  return humanize(value);
}

function setButtonState(button, href, enabled) {
  if (!button) return;

  if (enabled) {
    button.href = href;
    button.classList.remove("is-disabled");
    return;
  }

  button.removeAttribute("href");
  button.classList.add("is-disabled");
}

function setSessionVisibility(isVisible) {
  const dashboard = document.getElementById("monitor-dashboard");
  const emptyState = document.getElementById("monitor-empty-state");

  if (dashboard) {
    dashboard.classList.toggle("hidden", !isVisible);
  }

  if (emptyState) {
    emptyState.classList.toggle("hidden", isVisible);
  }
}

function createModuleCard(module) {
  const title = escapeHtml(module.title || module.slug || "Новый модуль");
  const slug = escapeHtml(module.slug || "");
  const description = escapeHtml(
    module.description || "Описание пока не заполнено, но модуль уже можно скачать и подключить в программу."
  );
  const topicCount = escapeHtml(module.topic_count ?? 0);
  const levelCount = escapeHtml(module.level_count ?? 0);
  const downloadUrl = escapeHtml(module.download_url || "#");

  return `
    <article class="module-card panel">
      <div class="module-card__header">
        <div>
          <div class="card-label">Учебный модуль</div>
          <h3>${title}</h3>
        </div>
        <span class="module-slug">${slug}</span>
      </div>
      <p>${description}</p>
      <div class="module-meta">
        <span class="meta-chip">Тем: ${topicCount}</span>
        <span class="meta-chip">Уровней: ${levelCount}</span>
      </div>
      <a class="button button-outline" href="${downloadUrl}">Скачать модуль</a>
    </article>
  `;
}

async function loadCatalog() {
  const appMeta = document.getElementById("app-meta");
  const appTitle = document.getElementById("app-title");
  const appButton = document.getElementById("download-app-btn");
  const heroButton = document.getElementById("hero-download-btn");
  const status = document.getElementById("download-status");
  const modulesGrid = document.getElementById("modules-grid");

  if (!appMeta || !appTitle || !appButton || !heroButton || !status || !modulesGrid) {
    return;
  }

  try {
    const response = await fetch(catalogUrl, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    const appInfo = payload.app || {};
    appTitle.textContent = appInfo.title || "Minecraft Coach Desktop";

    if (appInfo.available) {
      const directUrl = appInfo.download_url || "/downloads/app/latest";
      appMeta.textContent = `Файл: ${appInfo.filename} · ${formatBytes(appInfo.size_bytes)} · обновлён ${formatTimestamp(appInfo.updated_at)}`;
      status.textContent = "Сборка доступна для прямого скачивания с сайта.";
      setButtonState(appButton, directUrl, true);
      setButtonState(heroButton, directUrl, true);
    } else {
      appMeta.textContent = "Файл приложения пока не найден в папке dist/.";
      status.textContent = "Загрузите или замените dist/MinecraftCoach.exe, и кнопки станут активными автоматически.";
      setButtonState(appButton, "", false);
      setButtonState(heroButton, "", false);
    }

    const modules = Array.isArray(payload.modules) ? payload.modules : [];

    if (!modules.length) {
      modulesGrid.innerHTML = `
        <article class="module-card panel">
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
    setButtonState(appButton, "", false);
    setButtonState(heroButton, "", false);
    modulesGrid.innerHTML = `
      <article class="module-card panel">
        <div class="card-label">Ошибка</div>
        <h3>Каталог модулей недоступен</h3>
        <p>Проверьте, что backend запущен и отвечает на маршрут <code>/downloads/catalog</code>.</p>
      </article>
    `;
  }
}

function renderStateList(target, rows) {
  if (!target) return;

  target.innerHTML = `
    <div class="state-list">
      ${rows
        .map(
          (row) => `
            <div class="state-row">
              <span>${escapeHtml(row.label)}</span>
              <strong>${escapeHtml(row.value)}</strong>
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
  const statsGrid = document.getElementById("stats-grid");
  const dashboard = payload.dashboard || {};
  const stats = dashboard.stats || {};
  const counts = dashboard.counts || {};
  const settings = dashboard.settings || {};
  const runtime = payload.runtime || {};

  setSessionVisibility(true);

  if (sessionTitle) {
    sessionTitle.textContent = `Сессия ${payload.program_id || dashboard.program_id || ""}`.trim();
  }

  if (sessionUpdated) {
    sessionUpdated.textContent = `Последнее обновление: ${formatTimestamp(payload.updated_at)}`;
  }

  if (statsGrid) {
    const statCards = [
      { label: "Монеты", value: humanize(stats.coins, "0") },
      { label: "Правильных", value: humanize(stats.correct, "0") },
      { label: "Ошибок", value: humanize(stats.wrong, "0") },
      { label: "Завершённых пауз", value: humanize(stats.completed_breaks, "0") },
      { label: "Тем всего", value: humanize(counts.topics, "0") },
      { label: "Заданий", value: humanize(counts.tasks, "0") },
      { label: "Детских тем", value: humanize(counts.child_topics, "0") },
      { label: "Взрослых тем", value: humanize(counts.adult_topics, "0") },
    ];

    statsGrid.innerHTML = statCards
      .map(
        (card) => `
          <article class="stat-card">
            <div>${escapeHtml(card.label)}</div>
            <strong>${escapeHtml(card.value)}</strong>
          </article>
        `
      )
      .join("");
  }

  renderStateList(document.getElementById("runtime-state"), [
    { label: "Текущий модуль", value: humanize(runtime.current_module, "Не выбран") },
    { label: "Текущая тема", value: humanize(runtime.current_topic, "Не выбрана") },
    { label: "Текущее задание", value: humanize(runtime.current_task, "Нет активного задания") },
    { label: "Состояние", value: humanize(runtime.state_label || runtime.state, "Неизвестно") },
    { label: "До следующей паузы", value: humanize(runtime.remaining_break, "Нет данных") },
    { label: "Ручная пауза", value: humanizeBoolean(runtime.manual_pause, "Активна", "Не активна") },
    { label: "Последний режим", value: humanize(stats.last_mode, "Нет данных") },
    { label: "Последняя активность", value: humanize(stats.last_activity, "Нет данных") },
  ]);

  renderStateList(document.getElementById("settings-state"), [
    { label: "ID программы", value: humanize(payload.program_id || dashboard.program_id, "—") },
    { label: "Язык окна", value: humanize(settings.window_language, "ru") },
    { label: "Интервал между паузами", value: `${humanize(settings.break_seconds, "—")} сек` },
    { label: "Заданий в паузе", value: humanize(settings.tasks_per_break, "—") },
    { label: "Время урока", value: `${humanize(settings.lesson_seconds, "—")} сек` },
    { label: "URL сервера", value: humanize(settings.server_base_url, "Не задан") },
  ]);
}

function clearSessionState() {
  sessionStorage.removeItem(sessionStorageKey);
  setSessionVisibility(false);

  if (refreshTimer) {
    window.clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

async function loadSessionDashboard() {
  const token = sessionStorage.getItem(sessionStorageKey);
  const loginMessage = document.getElementById("login-message");

  if (!token) {
    setSessionVisibility(false);
    return;
  }

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

    if (loginMessage) {
      loginMessage.textContent = "";
    }
  } catch (error) {
    clearSessionState();

    if (loginMessage) {
      loginMessage.textContent = `Не удалось открыть мониторинг: ${error instanceof Error ? error.message : String(error)}`;
    }
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

  if (loginMessage) {
    loginMessage.textContent = "Проверяем доступ...";
  }

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

    if (loginMessage) {
      loginMessage.textContent = "Вход выполнен. Загружаем данные...";
    }

    await loadSessionDashboard();

    if (refreshTimer) {
      window.clearInterval(refreshTimer);
    }

    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
    form.parent_password.value = "";
  } catch (error) {
    clearSessionState();

    if (loginMessage) {
      loginMessage.textContent = `Ошибка входа: ${error instanceof Error ? error.message : String(error)}`;
    }
  }
}

function initRevealAnimations() {
  const items = document.querySelectorAll(".reveal");

  if (!items.length) {
    return;
  }

  if (!("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.16,
      rootMargin: "0px 0px -8% 0px",
    }
  );

  items.forEach((item) => observer.observe(item));
}

function initHeaderState() {
  const header = document.querySelector(".site-header");

  if (!header) return;

  const sync = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 12);
  };

  sync();
  window.addEventListener("scroll", sync, { passive: true });
}

document.addEventListener("DOMContentLoaded", () => {
  initRevealAnimations();
  initHeaderState();
  loadCatalog();
  setSessionVisibility(false);

  const form = document.getElementById("monitor-login-form");
  const refreshButton = document.getElementById("refresh-session-btn");
  const logoutButton = document.getElementById("logout-session-btn");

  if (form) {
    form.addEventListener("submit", loginToSession);
  }

  if (refreshButton) {
    refreshButton.addEventListener("click", loadSessionDashboard);
  }

  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      clearSessionState();
      const loginMessage = document.getElementById("login-message");
      if (loginMessage) {
        loginMessage.textContent = "Сессия закрыта на этом устройстве.";
      }
    });
  }

  if (sessionStorage.getItem(sessionStorageKey)) {
    loadSessionDashboard();
    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
  }
});
