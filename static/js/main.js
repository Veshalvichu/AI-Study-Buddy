// ── THEME TOGGLE ─────────────────────────────────────────────────────────
const saved = localStorage.getItem("sb-theme") || "dark";
document.documentElement.setAttribute("data-theme", saved);
updateThemeIcon(saved);

const toggleBtn = document.getElementById("themeToggle");
if (toggleBtn) {
  toggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next    = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sb-theme", next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  const icon = document.querySelector(".theme-icon");
  if (icon) icon.textContent = theme === "dark" ? "🌙" : "☀️";
}
