const siteConfig = window.MinecraftCoachSiteConfig || {};
const apiBaseUrl = String(siteConfig.apiBaseUrl || "").replace(/\/+$/, "");
const buildApiUrl = (path) => `${apiBaseUrl}${path}`;

const loginUrl = buildApiUrl("/auth/login");
const dashboardUrl = buildApiUrl("/dashboard");
const sessionStorageKey = "minecraft-coach-session-token";
const languageStorageKey = "minecraft-coach-language";
const supportedLanguages = ["ru", "pl", "en", "it", "de", "uk"];
const defaultLanguage = "en";

const languageNames = {
  ru: "Русский",
  pl: "Polski",
  en: "English",
  it: "Italiano",
  de: "Deutsch",
  uk: "Українська",
};

const languageLocales = {
  ru: "ru-RU",
  pl: "pl-PL",
  en: "en-US",
  it: "it-IT",
  de: "de-DE",
  uk: "uk-UA",
};


export {
  siteConfig,
  apiBaseUrl,
  buildApiUrl,
  loginUrl,
  dashboardUrl,
  sessionStorageKey,
  languageStorageKey,
  supportedLanguages,
  defaultLanguage,
  languageNames,
  languageLocales,
};
