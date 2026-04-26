import { defaultLanguage, languageLocales, languageNames, languageStorageKey, supportedLanguages } from "./config.js";
import { translations } from "./translations.js";
import { state } from "./state.js";

function normalizeLanguage(language) {
  const code = String(language || "")
    .trim()
    .toLowerCase()
    .replace("_", "-")
    .split("-", 1)[0];

  return supportedLanguages.includes(code) ? code : defaultLanguage;
}

function resolveInitialLanguage() {
  const params = new URLSearchParams(window.location.search);
  const rawQueryLanguage = params.get("lang");
  const queryLanguage = normalizeLanguage(rawQueryLanguage);

  if (rawQueryLanguage && supportedLanguages.includes(queryLanguage)) {
    return queryLanguage;
  }

  const savedRaw = localStorage.getItem(languageStorageKey);
  if (savedRaw) {
    const saved = normalizeLanguage(savedRaw);
    if (supportedLanguages.includes(saved)) {
      return saved;
    }
  }

  return defaultLanguage;
}

function getLocale() {
  return languageLocales[state.currentLanguage] || languageLocales[defaultLanguage];
}

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

function getNestedValue(object, path) {
  return String(path || "")
    .split(".")
    .reduce((current, segment) => (current && current[segment] !== undefined ? current[segment] : undefined), object);
}

function translate(key, replacements = {}, language = state.currentLanguage) {
  let value = getNestedValue(translations[language], key);
  if (value === undefined) {
    value = getNestedValue(translations[defaultLanguage], key);
  }
  if (typeof value !== "string") {
    return key;
  }

  return value.replace(/\{(\w+)\}/g, (_, token) => {
    const replacement = replacements[token];
    return replacement === undefined || replacement === null ? "" : String(replacement);
  });
}

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  if (!value) return translate("dynamic.sizeUnknown");

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
  if (!timestamp) return translate("dynamic.noData");

  const date = new Date(
    typeof timestamp === "number" && timestamp < 1000000000000 ? timestamp * 1000 : timestamp
  );

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return new Intl.DateTimeFormat(getLocale(), {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function humanize(value, fallbackKey = "dynamic.noData") {
  if (value === null || value === undefined || value === "") {
    return translate(fallbackKey);
  }
  return String(value);
}

function humanizeBoolean(value, truthyKey, falsyKey, fallbackKey = "dynamic.noData") {
  if (value === true) return translate(truthyKey);
  if (value === false) return translate(falsyKey);
  return translate(fallbackKey);
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

function setLoginMessage(key = "", replacements = {}) {
  state.loginMessageState = key ? { key, replacements } : null;
  const message = document.getElementById("login-message");
  if (!message) return;
  message.textContent = key ? translate(key, replacements) : "";
}

function refreshLoginMessage() {
  if (!state.loginMessageState) {
    setLoginMessage();
    return;
  }
  setLoginMessage(state.loginMessageState.key, state.loginMessageState.replacements);
}


export {
  normalizeLanguage,
  resolveInitialLanguage,
  getLocale,
  escapeHtml,
  getNestedValue,
  translate,
  formatBytes,
  formatTimestamp,
  humanize,
  humanizeBoolean,
  setButtonState,
  setSessionVisibility,
  setLoginMessage,
  refreshLoginMessage,
};
