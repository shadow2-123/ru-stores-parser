const out = document.getElementById("out");
const status = document.getElementById("status");
const btn = document.getElementById("btn");
const names = { dns: "DNS", citilink: "Ситилинк" };

function money(value) {
  if (value == null) return "нет цены";
  return new Intl.NumberFormat("ru-RU").format(value) + " ₽";
}

function mark(el, value) {
  if (!el) return;
  el.textContent = value;
  const good = value === "success" || value === "online" || value === "empty";
  el.className = good ? "ok" : "bad";
  if (value === "—") el.className = "";
}

function setShopRow(shop, value, detail) {
  const row = document.querySelector(`tr[data-shop="${shop}"]`);
  if (!row) return;
  mark(row.querySelector(".shop-status"), value);
  const detailEl = row.querySelector(".shop-detail");
  if (detailEl) detailEl.textContent = detail || "";
}

async function refreshHealth() {
  try {
    const r = await fetch("/health");
    const data = await r.json();
    const chrome = document.getElementById("chrome-status");
    mark(chrome, data.chrome_cdp ? "online" : "offline");
    document.getElementById("chrome-detail").textContent = data.chrome_cdp
      ? "порт 9222 доступен"
      : "нет ответа на 9222";
    for (const shop of data.shops || []) {
      setShopRow(shop.shop, shop.status, shop.detail || "health");
    }
    document.getElementById("health-updated").textContent =
      "health: " + new Date().toLocaleTimeString("ru-RU");
  } catch {
    mark(document.getElementById("chrome-status"), "offline");
    document.getElementById("health-updated").textContent = "health недоступен";
  }
}

document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("q").value.trim();
  if (!q) return;

  btn.disabled = true;
  status.textContent = "Ищем в магазинах…";
  out.innerHTML = "";

  try {
    const response = await fetch("/search?q=" + encodeURIComponent(q));
    const raw = await response.text();
    if (!response.ok) {
      status.textContent = "HTTP " + response.status + ": " + raw.slice(0, 200);
      return;
    }

    let data;
    try {
      data = JSON.parse(raw);
    } catch {
      status.textContent = "Ответ не JSON: " + raw.slice(0, 200);
      return;
    }

    status.textContent = "Запрос: " + data.query;

    for (const shop of data.results || []) {
      const answered = shop.status === "success" || shop.status === "empty";
      setShopRow(
        shop.shop,
        shop.status,
        answered ? shop.count + " товаров" : shop.error || "нет ответа"
      );

      const block = document.createElement("div");
      block.className = "shop-block";
      block.innerHTML =
        "<h3>" +
        (names[shop.shop] || shop.shop) +
        " · " +
        shop.status +
        " · " +
        shop.count +
        "</h3>";

      if (shop.error) {
        const p = document.createElement("p");
        p.className = "err";
        p.textContent = shop.error;
        block.appendChild(p);
      }

      for (const it of shop.items || []) {
        const row = document.createElement("div");
        row.className = "item";
        const a = document.createElement("a");
        a.href = it.url || "#";
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = it.title || it.product_id || "";
        const price = document.createElement("div");
        price.className = "price";
        price.textContent = money(it.price);
        row.appendChild(a);
        row.appendChild(price);
        block.appendChild(row);
      }
      out.appendChild(block);
    }
  } catch (err) {
    status.textContent = "Сеть: " + (err && err.message ? err.message : err);
  } finally {
    btn.disabled = false;
  }
});

refreshHealth();
setInterval(refreshHealth, 30000);