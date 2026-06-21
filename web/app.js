const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

const storeColors = {
  Amazon: "#315f86",
  "Amazon Fresh": "#167c80",
  Publix: "#2f6b3f",
  Aldi: "#b56b21",
  "Sam's Club": "#6b4fa3",
};

const els = {
  noteInput: document.querySelector("#noteInput"),
  zipInput: document.querySelector("#zipInput"),
  webhookInput: document.querySelector("#webhookInput"),
  sourceInput: document.querySelector("#sourceInput"),
  loadNoteButton: document.querySelector("#loadNoteButton"),
  analyzeButton: document.querySelector("#analyzeButton"),
  storeToggles: document.querySelector("#storeToggles"),
  catalogStatus: document.querySelector("#catalogStatus"),
  listCount: document.querySelector("#listCount"),
  splitTotal: document.querySelector("#splitTotal"),
  singleStore: document.querySelector("#singleStore"),
  matchedCount: document.querySelector("#matchedCount"),
  avgServing: document.querySelector("#avgServing"),
  updatedStatus: document.querySelector("#updatedStatus"),
  itemsBody: document.querySelector("#itemsBody"),
  storePlans: document.querySelector("#storePlans"),
  missingPanel: document.querySelector("#missingPanel"),
  missingList: document.querySelector("#missingList"),
  missingCount: document.querySelector("#missingCount"),
};

let selectedStores = [];

async function init() {
  const state = await getJson("/api/state");
  selectedStores = state.settings.stores;
  renderStoreToggles(state.settings.stores);
  els.noteInput.value = state.note || "";
  els.webhookInput.value = state.settings.endpoint;
  els.sourceInput.value = state.settings.source.path || "data/grocery-list.txt";
  els.catalogStatus.textContent = `${state.catalog.rows} sample catalog rows`;
  renderAnalysis(state.analysis);
  bindEvents();
  refreshIcons();
}

function bindEvents() {
  els.analyzeButton.addEventListener("click", analyze);
  els.noteInput.addEventListener("input", debounce(analyze, 350));
  els.zipInput.addEventListener("change", analyze);
  els.loadNoteButton.addEventListener("click", async () => {
    const payload = await getJson("/api/latest-note");
    els.noteInput.value = payload.text || "";
    await analyze();
  });
}

function renderStoreToggles(stores) {
  els.storeToggles.innerHTML = stores.map((store) => `
    <label class="toggle">
      <input type="checkbox" value="${escapeHtml(store)}" checked>
      <span class="store-swatch" style="background:${storeColors[store] || "#667069"}"></span>
      <span>${escapeHtml(store)}</span>
    </label>
  `).join("");

  els.storeToggles.querySelectorAll("input").forEach((input) => {
    input.addEventListener("change", () => {
      selectedStores = Array.from(els.storeToggles.querySelectorAll("input:checked")).map((node) => node.value);
      analyze();
    });
  });
}

async function analyze() {
  if (!selectedStores.length) {
    selectedStores = Array.from(els.storeToggles.querySelectorAll("input:checked")).map((node) => node.value);
  }
  els.updatedStatus.textContent = "Analyzing";
  const analysis = await postJson("/api/analyze", {
    text: els.noteInput.value,
    stores: selectedStores,
    zip: els.zipInput.value,
  });
  renderAnalysis(analysis);
}

function renderAnalysis(analysis) {
  els.listCount.textContent = `${analysis.item_count} ${analysis.item_count === 1 ? "item" : "items"}`;
  els.splitTotal.textContent = money.format(analysis.split_total || 0);
  els.matchedCount.textContent = `${analysis.matched_count} / ${analysis.item_count}`;
  els.avgServing.textContent = analysis.average_price_per_serving == null
    ? "$0.00"
    : money.format(analysis.average_price_per_serving);

  const single = analysis.cheapest_single_store;
  els.singleStore.textContent = single ? `${money.format(single.total)} ${single.store}` : "Missing";
  els.itemsBody.innerHTML = analysis.items.map(renderItemRow).join("");
  els.storePlans.innerHTML = analysis.store_totals.map(renderStorePlan).join("");
  renderMissing(analysis.missing);
  els.updatedStatus.textContent = "Ready";
  refreshIcons();
}

function renderItemRow(item) {
  const offer = item.best_offer;
  if (!offer) {
    return `
      <tr>
        <td><strong>${escapeHtml(item.name)}</strong></td>
        <td>${escapeHtml(item.quantity_label)}</td>
        <td colspan="5" class="muted">No catalog match</td>
      </tr>
    `;
  }
  return `
    <tr>
      <td><strong>${escapeHtml(item.name)}</strong></td>
      <td>${escapeHtml(item.quantity_label)}</td>
      <td>${storePill(offer.store)}</td>
      <td>${linkOrText(offer.product, offer.url)}</td>
      <td>
        ${escapeHtml(offer.package_desc)}
        ${offer.package_count > 1 ? `<div class="muted">${offer.package_count} packages</div>` : ""}
      </td>
      <td class="price">${money.format(offer.total_price)}</td>
      <td>${offer.price_per_serving == null ? "n/a" : money.format(offer.price_per_serving)}</td>
    </tr>
  `;
}

function renderStorePlan(plan) {
  const missingLabel = plan.missing_count ? `${plan.missing_count} missing` : `${plan.matched_count} matched`;
  const items = plan.items.slice(0, 6).map((item) => `
    <div class="store-item">
      <span>${escapeHtml(item.item)}</span>
      <strong>${money.format(item.total_price)}</strong>
    </div>
  `).join("");

  return `
    <article class="store-plan">
      <header>
        <div>
          <h3>${storePill(plan.store)}</h3>
          <p class="muted">${missingLabel}</p>
        </div>
        <div class="store-total">${money.format(plan.total)}</div>
      </header>
      <div class="store-items">${items || `<span class="muted">No matches</span>`}</div>
    </article>
  `;
}

function renderMissing(missing) {
  els.missingPanel.classList.toggle("hidden", missing.length === 0);
  els.missingCount.textContent = `${missing.length} ${missing.length === 1 ? "item" : "items"}`;
  els.missingList.innerHTML = missing.map((item) => `<span class="missing-chip">${escapeHtml(item.name)}</span>`).join("");
}

function storePill(store) {
  return `
    <span class="store-pill">
      <span class="store-dot" style="background:${storeColors[store] || "#667069"}"></span>
      ${escapeHtml(store)}
    </span>
  `;
}

function linkOrText(text, url) {
  if (!url) return escapeHtml(text);
  return `<a href="${escapeAttribute(url)}" target="_blank" rel="noreferrer">${escapeHtml(text)}</a>`;
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`GET ${url} failed`);
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`POST ${url} failed`);
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

function debounce(fn, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), wait);
  };
}

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

init().catch((error) => {
  els.catalogStatus.textContent = error.message;
});
