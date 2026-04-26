import { dashboardUrl, loginUrl, sessionStorageKey } from "./config.js";
import { state } from "./state.js";
import { escapeHtml, formatTimestamp, humanize, humanizeBoolean, setLoginMessage, setSessionVisibility, translate } from "./core.js";

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

  state.lastDashboardPayload = payload;
  setSessionVisibility(true);

  if (sessionTitle) {
    sessionTitle.textContent = translate("dynamic.sessionTitle", {
      programId: payload.program_id || dashboard.program_id || "",
    }).trim();
  }

  if (sessionUpdated) {
    sessionUpdated.textContent = translate("dynamic.sessionUpdated", {
      updatedAt: formatTimestamp(payload.updated_at),
    });
  }

  if (statsGrid) {
    const statCards = [
      { label: translate("dynamic.stats.coins"), value: humanize(stats.coins, "dynamic.noData") },
      { label: translate("dynamic.stats.correct"), value: humanize(stats.correct, "dynamic.noData") },
      { label: translate("dynamic.stats.wrong"), value: humanize(stats.wrong, "dynamic.noData") },
      {
        label: translate("dynamic.stats.completedBreaks"),
        value: humanize(stats.completed_breaks, "dynamic.noData"),
      },
      { label: translate("dynamic.stats.topics"), value: humanize(counts.topics, "dynamic.noData") },
      { label: translate("dynamic.stats.tasks"), value: humanize(counts.tasks, "dynamic.noData") },
      {
        label: translate("dynamic.stats.childTopics"),
        value: humanize(counts.child_topics, "dynamic.noData"),
      },
      {
        label: translate("dynamic.stats.adultTopics"),
        value: humanize(counts.adult_topics, "dynamic.noData"),
      },
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
    {
      label: translate("dynamic.runtime.currentModule"),
      value: humanize(runtime.current_module, "dynamic.runtime.notSelectedModule"),
    },
    {
      label: translate("dynamic.runtime.currentTopic"),
      value: humanize(runtime.current_topic, "dynamic.runtime.notSelectedTopic"),
    },
    {
      label: translate("dynamic.runtime.currentTask"),
      value: humanize(runtime.current_task, "dynamic.runtime.noActiveTask"),
    },
    {
      label: translate("dynamic.runtime.state"),
      value: humanize(runtime.state_label || runtime.state, "dynamic.runtime.unknown"),
    },
    {
      label: translate("dynamic.runtime.nextBreak"),
      value: humanize(runtime.remaining_break, "dynamic.runtime.noData"),
    },
    {
      label: translate("dynamic.runtime.manualPause"),
      value: humanizeBoolean(
        runtime.manual_pause,
        "dynamic.runtime.manualPauseActive",
        "dynamic.runtime.manualPauseInactive",
        "dynamic.runtime.noData"
      ),
    },
    {
      label: translate("dynamic.runtime.lastMode"),
      value: humanize(stats.last_mode, "dynamic.runtime.noData"),
    },
    {
      label: translate("dynamic.runtime.lastActivity"),
      value: humanize(stats.last_activity, "dynamic.runtime.noData"),
    },
  ]);

  renderStateList(document.getElementById("settings-state"), [
    {
      label: translate("dynamic.settings.programId"),
      value: humanize(payload.program_id || dashboard.program_id, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.windowLanguage"),
      value: humanize(settings.window_language, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.breakInterval"),
      value: `${humanize(settings.break_seconds, "dynamic.noData")} sec`,
    },
    {
      label: translate("dynamic.settings.tasksPerBreak"),
      value: humanize(settings.tasks_per_break, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.lessonTime"),
      value: `${humanize(settings.lesson_seconds, "dynamic.noData")} sec`,
    },
    {
      label: translate("dynamic.settings.serverUrl"),
      value: humanize(settings.server_base_url, "dynamic.settings.notSet"),
    },
  ]);
}

function clearSessionState() {
  sessionStorage.removeItem(sessionStorageKey);
  state.lastDashboardPayload = null;
  setSessionVisibility(false);

  if (state.refreshTimer) {
    window.clearInterval(state.refreshTimer);
    state.refreshTimer = null;
  }
}

async function loadSessionDashboard() {
  const token = sessionStorage.getItem(sessionStorageKey);

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
    setLoginMessage();
  } catch (error) {
    clearSessionState();
    setLoginMessage("dynamic.monitorOpenError", {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

async function loginToSession(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const body = {
    program_id: form.program_id.value.trim(),
    parent_password: form.parent_password.value,
  };

  setLoginMessage("dynamic.loginChecking");

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
    setLoginMessage("dynamic.loginLoading");

    await loadSessionDashboard();

    if (state.refreshTimer) {
      window.clearInterval(state.refreshTimer);
    }

    state.refreshTimer = window.setInterval(loadSessionDashboard, 15000);
    form.parent_password.value = "";
  } catch (error) {
    clearSessionState();
    setLoginMessage("dynamic.loginError", {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}


export { renderStateList, renderDashboard, clearSessionState, loadSessionDashboard, loginToSession };
