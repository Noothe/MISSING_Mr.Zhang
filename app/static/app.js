const messagesEl = document.querySelector("#messages");
const chatForm = document.querySelector("#chatForm");
const messageInput = document.querySelector("#messageInput");
const profileForm = document.querySelector("#profileForm");
const statusBox = document.querySelector("#statusBox");
const schoolList = document.querySelector("#schoolList");
const schoolSearch = document.querySelector("#schoolSearch");
const sourceInfo = document.querySelector("#sourceInfo");
const syncButton = document.querySelector("#syncButton");

const history = [
  {
    role: "assistant",
    content:
      "先说清楚：我是非官方张雪峰风格志愿顾问，不是本人，也不是官方机构。\n\n你要真想填志愿，别上来只问“哪个学校好”。先把省份、选科、分数、位次、预算、城市偏好、专业禁忌说清楚。没有这些，给建议就是不负责任。",
  },
];

function profile() {
  const data = new FormData(profileForm);
  return Object.fromEntries(data.entries());
}

function renderMessages() {
  messagesEl.innerHTML = "";
  for (const item of history) {
    const node = document.createElement("div");
    node.className = `message ${item.role}`;
    node.textContent = item.content;
    messagesEl.appendChild(node);
  }
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function health() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const dot = statusBox.querySelector(".dot");
    dot.classList.toggle("ok", data.ok);
    statusBox.querySelector("span:last-child").textContent = data.hasDeepSeekKey
      ? `DeepSeek 已配置：${data.model}`
      : "DeepSeek Key 未配置，当前为离线演示模式";
  } catch {
    statusBox.querySelector("span:last-child").textContent = "服务未启动";
  }
}

function renderSchools(payload) {
  sourceInfo.textContent = `来源：${payload.source || "本地种子数据"} | 更新：${payload.syncedAt || "未同步"}`;
  schoolList.innerHTML = "";
  for (const school of payload.schools || []) {
    const card = document.createElement("article");
    card.className = "school";
    const tags = (school.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
    card.innerHTML = `
      <strong>${escapeHtml(school.name)}</strong>
      <span>${escapeHtml([school.province, school.city, school.level, school.type].filter(Boolean).join(" / "))}</span>
      <div class="tags">${tags}</div>
    `;
    schoolList.appendChild(card);
  }
}

async function loadSchools() {
  const params = new URLSearchParams();
  const keyword = schoolSearch.value.trim();
  if (keyword) params.set("q", keyword);
  const res = await fetch(`/api/schools?${params.toString()}`);
  renderSchools(await res.json());
}

async function syncSchools() {
  syncButton.disabled = true;
  syncButton.textContent = "同步中";
  try {
    const res = await fetch("/api/sync/schools", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "同步失败");
    renderSchools(data);
  } catch (error) {
    sourceInfo.textContent = error.message;
  } finally {
    syncButton.disabled = false;
    syncButton.textContent = "同步";
  }
}

async function sendMessage(event) {
  event.preventDefault();
  const content = messageInput.value.trim();
  if (!content) return;

  history.push({ role: "user", content });
  messageInput.value = "";
  renderMessages();

  const pending = { role: "assistant", content: "等我按数据和边界核一下。" };
  history.push(pending);
  renderMessages();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history.filter((item) => item !== pending), profile: profile() }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "请求失败");
    pending.content = `${data.answer}\n\n数据状态：${data.sources?.schoolSource || "本地数据"}，更新时间：${
      data.sources?.syncedAt || "未同步"
    }。`;
  } catch (error) {
    pending.content = `请求失败：${error.message}`;
  }
  renderMessages();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

if (chatForm && schoolSearch) {
  chatForm.addEventListener("submit", sendMessage);
  schoolSearch.addEventListener("input", () => loadSchools());
  syncButton.addEventListener("click", syncSchools);

  renderMessages();
  health();
  loadSchools();
}
