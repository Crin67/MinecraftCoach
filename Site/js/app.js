import { sessionStorageKey } from "./config.js";
import { state } from "./state.js";
import { resolveInitialLanguage, setLoginMessage, setSessionVisibility } from "./core.js";
import { loadCatalog } from "./catalog.js";
import { clearSessionState, loadSessionDashboard, loginToSession } from "./dashboard.js";
import { initHeaderState, initRevealAnimations } from "./chrome.js";
import { initLanguageControls, setLanguage, shouldPromptForLanguageChoice, showLanguagePrompt } from "./language-ui.js";

export function initApp() {
  state.currentLanguage = resolveInitialLanguage();
  const promptForLanguage = shouldPromptForLanguageChoice();

  setLanguage(state.currentLanguage, {
    reloadCatalog: false,
    rerenderDashboard: false,
    persist: !promptForLanguage,
  });

  initLanguageControls();
  if (promptForLanguage) {
    showLanguagePrompt();
  }
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
      setLoginMessage("dynamic.sessionClosed");
    });
  }

  if (sessionStorage.getItem(sessionStorageKey)) {
    loadSessionDashboard();
    state.refreshTimer = window.setInterval(loadSessionDashboard, 15000);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp, { once: true });
} else {
  initApp();
}
