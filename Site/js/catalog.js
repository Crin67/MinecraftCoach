import { buildApiUrl } from "./config.js";
import { state } from "./state.js";
import { escapeHtml, formatBytes, formatTimestamp, setButtonState, translate } from "./core.js";

function createModuleCard(module) {
  const title = escapeHtml(module.title || module.slug || translate("dynamic.moduleCardLabel"));
  const slug = escapeHtml(module.slug || "");
  const description = escapeHtml(
    module.description || translate("dynamic.moduleFallbackDescription")
  );
  const topicCount = module.topic_count ?? 0;
  const levelCount = module.level_count ?? 0;
  const downloadUrl = escapeHtml(module.download_url || "#");

  return `
    <article class="module-card panel">
      <div class="module-card__header">
        <div>
          <div class="card-label">${escapeHtml(translate("dynamic.moduleCardLabel"))}</div>
          <h3>${title}</h3>
        </div>
        <span class="module-slug">${slug}</span>
      </div>
      <p>${description}</p>
      <div class="module-meta">
        <span class="meta-chip">${escapeHtml(translate("dynamic.moduleTopics", { count: topicCount }))}</span>
        <span class="meta-chip">${escapeHtml(translate("dynamic.moduleLevels", { count: levelCount }))}</span>
      </div>
      <a class="button button-outline" href="${downloadUrl}">${escapeHtml(translate("dynamic.moduleDownload"))}</a>
    </article>
  `;
}

function getCatalogUrl() {
  const query = new URLSearchParams({ lang: state.currentLanguage });
  return `${buildApiUrl("/downloads/catalog")}?${query.toString()}`;
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
    const response = await fetch(getCatalogUrl(), {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    const appInfo = payload.app || {};
    appTitle.textContent = appInfo.title || translate("dynamic.appTitleDefault");

    if (appInfo.available) {
      const directUrl = appInfo.download_url || "/downloads/app/latest";
      appMeta.textContent = translate("dynamic.downloadMeta", {
        filename: appInfo.filename,
        size: formatBytes(appInfo.size_bytes),
        updatedAt: formatTimestamp(appInfo.updated_at),
      });
      status.textContent = translate("dynamic.downloadReady");
      setButtonState(appButton, directUrl, true);
      setButtonState(heroButton, directUrl, true);
    } else {
      appMeta.textContent = translate("dynamic.downloadMissingMeta");
      status.textContent = translate("dynamic.downloadMissingStatus");
      setButtonState(appButton, "", false);
      setButtonState(heroButton, "", false);
    }

    const modules = Array.isArray(payload.modules) ? payload.modules : [];

    if (!modules.length) {
      modulesGrid.innerHTML = `
        <article class="module-card panel">
          <div class="card-label">${escapeHtml(translate("modules.eyebrow"))}</div>
          <h3>${escapeHtml(translate("dynamic.modulesEmptyTitle"))}</h3>
          <p>${translate("dynamic.modulesEmptyText")}</p>
        </article>
      `;
      return;
    }

    modulesGrid.innerHTML = modules.map(createModuleCard).join("");
  } catch (error) {
    appMeta.textContent = translate("dynamic.catalogErrorMeta");
    status.textContent = translate("dynamic.catalogErrorStatus", {
      error: error instanceof Error ? error.message : String(error),
    });
    setButtonState(appButton, "", false);
    setButtonState(heroButton, "", false);
    modulesGrid.innerHTML = `
      <article class="module-card panel">
        <div class="card-label">${escapeHtml(translate("nav.modules"))}</div>
        <h3>${escapeHtml(translate("dynamic.catalogErrorTitle"))}</h3>
        <p>${translate("dynamic.catalogErrorText")}</p>
      </article>
    `;
  }
}


export { createModuleCard, getCatalogUrl, loadCatalog };
