const names = { dns: "DNS", citilink: "Ситилинк", ozon: "Ozon" };
const rowsEl = document.getElementById("rows");
const status = document.getElementById("status");
const btn = document.getElementById("btn");
const healthList = document.getElementById("health-list");

let items = [];
let sortKey = "price";
let sortDir = 1;

function coef() {
  const n = parseFloat(String(document.getElementById("coef").value).replace(",", "."));
  return Number.isFinite(n) && n > 0 ? n : 1;
}

function money(v) {
  if (v == null) return "—";
  return new Intl.NumberFormat("ru-RU").format(Math.round(v)) + " руб.";
}

function renderRows() {
  const k = coef();
  const copy = items.map((it) => ({
    ...it,
    priced: it.price == null ? null : it.price * k,
  }));

  copy.sort((a, b) => {
    if (sortKey === "shop") {
      const byShop = String(a.shop).localeCompare(String(b.shop), "ru");
      if (byShop !== 0) return byShop * sortDir;
      const ap = a.price;
      const bp = b.price;
      if (ap == null && bp == null) return 0;
      if (ap == null) return 1;
      if (bp == null) return -1;
      return ap - bp;
    }

    const av = a[sortKey];
    const bv = b[sortKey];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;
    if (bv == null) return -1;
    return (av - bv) * sortDir;
  });

  rowsEl.innerHTML = "";
  for (const it of copy) {
    const tr = document.createElement("tr");
    const title = it.title || "—";
    const nameCell = it.url
      ? `<a href="${it.url}" target="_blank" rel="noopener">${title}</a>`
      : title;
    tr.innerHTML = `
      <td>${names[it.shop] || it.shop}</td>
      <td>${nameCell}</td>
      <td>${money(it.price)}</td>
      <td>${money(it.priced)}</td>
    `;
    rowsEl.appendChild(tr);
  }
}

function setHealthItem(id, label, state, text) {
  let li = document.querySelector(`[data-health="${id}"]`);
  if (!li) {
    li = document.createElement("li");
    li.dataset.health = id;
    healthList.appendChild(li);
  }
  const cls =
    state === "success" || state === "ok" || state === "online" || state === "empty"
      ? "ok"
      : state === "timeout" || state === "slow"
        ? "warn"
        : "down";
  li.innerHTML = `<span class="dot ${cls}"></span>${label} <em>${text || state}</em>`;
}

async function refreshChrome() {
  try {
    const r = await fetch("/health/chrome");
    const data = await r.json();
    setHealthItem("chrome", "Chrome CDP", data.chrome_cdp ? "online" : "down", data.chrome_cdp ? "ok" : "down");
  } catch {
    setHealthItem("chrome", "Chrome CDP", "down", "нет связи");
  }
  const upd = document.getElementById("health-updated");
  if (upd) upd.textContent = new Date().toLocaleTimeString("ru-RU");
}

async function refreshShopHealth(shop) {
  const r = await fetch("/health/" + shop);
  const data = await r.json();
  setHealthItem(shop, names[shop] || shop, data.status, data.detail || data.status);
}

async function loadShop(shop) {
  setHealthItem(shop, names[shop], "slow", "ищем…");
  const r = await fetch(
    "/search/" + shop + "?q=" + encodeURIComponent(document.getElementById("q").value.trim())
  );
  const raw = await r.text();
  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    setHealthItem(shop, names[shop], "down", "не JSON");
    return;
  }
  if (!r.ok) {
    setHealthItem(shop, names[shop], "down", "HTTP " + r.status);
    return;
  }
  setHealthItem(
    shop,
    names[shop],
    data.status,
    data.status + (data.count != null ? " · " + data.count : "")
  );
  if (Array.isArray(data.items)) {
    for (const it of data.items) {
      items.push({
        shop,
        title: it.title,
        url: it.url,
        price: it.price,
      });
    }
    renderRows();
  }
}

document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("q").value.trim();
  if (!q) return;
  btn.disabled = true;
  items = [];
  rowsEl.innerHTML = "";
  status.textContent = "Ищем…";
  try {
    await Promise.allSettled([
  loadShop("dns"),
  loadShop("citilink"),
  loadShop("ozon"),
]);
    status.textContent = "Готово · строк: " + items.length;
  } catch (err) {
    status.textContent = err && err.message ? err.message : "ошибка запроса";
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("coef").addEventListener("input", renderRows);

for (const th of document.querySelectorAll("th[data-sort]")) {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    if (sortKey === key) sortDir *= -1;
    else {
      sortKey = key;
      sortDir = 1;
    }
    document.querySelectorAll("th[data-sort]").forEach((x) => x.classList.remove("active"));
    th.classList.add("active");
    renderRows();
  });
}

const themeToggle = document.getElementById("theme-toggle");
const coefInput = document.getElementById("coef");

if (localStorage.getItem("theme") === "dark") {
  themeToggle.checked = true;
}
const savedCoef = localStorage.getItem("coef");
if (savedCoef) {
  coefInput.value = savedCoef;
}

themeToggle.addEventListener("change", () => {
  localStorage.setItem("theme", themeToggle.checked ? "dark" : "light");
});

coefInput.addEventListener("input", () => {
  localStorage.setItem("coef", coefInput.value);
  renderRows();
});

document.getElementById("warmup").addEventListener("click", async () => {
  const b = document.getElementById("warmup");
  b.disabled = true;
  status.textContent = "Обновляю сессии…";
  try {
    const r = await fetch("/warmup", { method: "POST" });
    const data = await r.json();
    for (const shop of data.shops || []) {
      setHealthItem(
        shop.shop,
        names[shop.shop] || shop.shop,
        shop.ok ? "ok" : "down",
        shop.detail
      );
    }
    status.textContent = data.ok ? "Сессии обновлены" : "Обновилось с ошибками";
  } catch (err) {
    status.textContent = "Не удалось обновить сессии";
  } finally {
    b.disabled = false;
  }
});


refreshChrome();
setInterval(refreshChrome, 30000);