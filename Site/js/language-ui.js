import { defaultLanguage, languageNames, languageStorageKey, supportedLanguages } from "./config.js";
import { state } from "./state.js";
import { normalizeLanguage, refreshLoginMessage, translate } from "./core.js";
import { loadCatalog } from "./catalog.js";
import { renderDashboard } from "./dashboard.js";

function applyTranslations() {
  document.documentElement.lang = state.currentLanguage;
  document.documentElement.dataset.language = state.currentLanguage;
  if (document.body) {
    document.body.dataset.language = state.currentLanguage;
  }
  document.title = translate("meta.title");

  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute("content", translate("meta.description"));
  }

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = translate(element.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    element.innerHTML = translate(element.dataset.i18nHtml);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", translate(element.dataset.i18nPlaceholder));
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", translate(element.dataset.i18nAriaLabel));
  });

  document.querySelectorAll("[data-i18n-alt]").forEach((element) => {
    element.setAttribute("alt", translate(element.dataset.i18nAlt));
  });

  updateLanguageControls();

  refreshLoginMessage();
}

function setLanguage(language, options = {}) {
  state.currentLanguage = normalizeLanguage(language);
  if (options.persist !== false) {
    localStorage.setItem(languageStorageKey, state.currentLanguage);
  }
  applyTranslations();

  if (options.reloadCatalog !== false) {
    loadCatalog();
  }

  if (state.lastDashboardPayload && options.rerenderDashboard !== false) {
    renderDashboard(state.lastDashboardPayload);
  }
}

function hasSavedLanguage() {
  const savedRaw = localStorage.getItem(languageStorageKey);
  return Boolean(savedRaw && supportedLanguages.includes(normalizeLanguage(savedRaw)));
}

function hasQueryLanguage() {
  const rawQueryLanguage = new URLSearchParams(window.location.search).get("lang");
  return Boolean(rawQueryLanguage && supportedLanguages.includes(normalizeLanguage(rawQueryLanguage)));
}

function shouldPromptForLanguageChoice() {
  return !hasQueryLanguage() && !hasSavedLanguage();
}

function updateLanguageControls() {
  const currentLabel = document.getElementById("language-current-label");
  if (currentLabel) {
    currentLabel.textContent = languageNames[state.currentLanguage] || languageNames[defaultLanguage];
  }

  document.querySelectorAll("[data-language-choice]").forEach((button) => {
    const isActive = button.dataset.languageChoice === state.currentLanguage;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function closeLanguageMenu() {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  if (!trigger || !panel) return;

  panel.classList.add("hidden");
  trigger.setAttribute("aria-expanded", "false");
}

function toggleLanguageMenu(forceOpen) {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  if (!trigger || !panel) return;

  const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : panel.classList.contains("hidden");
  panel.classList.toggle("hidden", !shouldOpen);
  trigger.setAttribute("aria-expanded", String(shouldOpen));
}

function showLanguagePrompt() {
  const modal = document.getElementById("language-modal");
  if (!modal) return;

  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
}

function hideLanguagePrompt() {
  const modal = document.getElementById("language-modal");
  if (!modal) return;

  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
}

function initLanguageControls() {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  const modal = document.getElementById("language-modal");
  const modalDialog = modal?.querySelector(".language-modal__dialog");
  const continueButton = document.getElementById("language-modal-continue");

  updateLanguageControls();

  if (trigger) {
    trigger.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleLanguageMenu();
    });
  }

  if (panel) {
    panel.addEventListener("click", (event) => {
      event.stopPropagation();
    });
  }

  if (modalDialog) {
    modalDialog.addEventListener("click", (event) => {
      event.stopPropagation();
    });
  }

  document.querySelectorAll("[data-language-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.languageChoice);
      closeLanguageMenu();
      hideLanguagePrompt();
    });
  });

  if (continueButton) {
    continueButton.addEventListener("click", () => {
      setLanguage(defaultLanguage);
      hideLanguagePrompt();
    });
  }

  document.addEventListener("click", () => {
    closeLanguageMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    closeLanguageMenu();
    if (modal && !modal.classList.contains("hidden")) {
      setLanguage(state.currentLanguage);
      hideLanguagePrompt();
    }
  });
}


export {
  applyTranslations,
  setLanguage,
  hasSavedLanguage,
  hasQueryLanguage,
  shouldPromptForLanguageChoice,
  updateLanguageControls,
  closeLanguageMenu,
  toggleLanguageMenu,
  showLanguagePrompt,
  hideLanguagePrompt,
  initLanguageControls,
};
