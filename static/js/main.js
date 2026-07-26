document.addEventListener("DOMContentLoaded", function () {
  /* ---------- Theme toggle ---------- */
  const root = document.documentElement;
  const themeToggle = document.getElementById("theme-toggle");
  const themePanel = document.getElementById("theme-panel");
  const savedTheme = getPreference("ciq-theme", "dark");
  const savedAccent = getPreference("ciq-accent", "blue");
  let panelCloseTimer;
  applyTheme(savedTheme);
  applyAccent(savedAccent);

  if (themeToggle && themePanel) {
    themeToggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (themePanel.classList.contains("is-open")) closeThemePanel();
      else openThemePanel();
    });
    document.addEventListener("click", function (event) {
      if (themePanel.classList.contains("is-open") && !event.target.closest(".theme-settings-wrap")) closeThemePanel();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeThemePanel();
    });
  }

  document.querySelectorAll("[data-theme-option]").forEach(function (button) {
    button.addEventListener("click", function () { applyTheme(button.dataset.themeOption); });
  });
  document.querySelectorAll("[data-accent-option]").forEach(function (button) {
    button.addEventListener("click", function () { applyAccent(button.dataset.accentOption); });
  });

  function applyTheme(theme) {
    const value = theme === "light" ? "light" : "dark";
    root.setAttribute("data-theme", value);
    setPreference("ciq-theme", value);
    document.querySelectorAll("[data-theme-option]").forEach(function (button) {
      button.classList.toggle("active", button.dataset.themeOption === value);
      button.setAttribute("aria-pressed", String(button.dataset.themeOption === value));
    });
  }

  function applyAccent(accent) {
    const allowed = ["blue", "violet", "emerald", "orange", "rose", "cyan"];
    const value = allowed.includes(accent) ? accent : "blue";
    root.setAttribute("data-accent", value);
    setPreference("ciq-accent", value);
    document.querySelectorAll("[data-accent-option]").forEach(function (button) {
      button.classList.toggle("active", button.dataset.accentOption === value);
      button.setAttribute("aria-pressed", String(button.dataset.accentOption === value));
    });
  }

  function openThemePanel() {
    clearTimeout(panelCloseTimer);
    themePanel.hidden = false;
    themePanel.setAttribute("aria-hidden", "false");
    themeToggle.setAttribute("aria-expanded", "true");
    positionThemePanel();
    window.requestAnimationFrame(function () { themePanel.classList.add("is-open"); });
  }

  function closeThemePanel() {
    if (!themePanel) return;
    themePanel.classList.remove("is-open");
    themePanel.setAttribute("aria-hidden", "true");
    if (themeToggle) themeToggle.setAttribute("aria-expanded", "false");
    clearTimeout(panelCloseTimer);
    panelCloseTimer = window.setTimeout(function () { themePanel.hidden = true; }, 180);
  }

  function positionThemePanel() {
    if (!themeToggle || !themePanel) return;
    const trigger = themeToggle.getBoundingClientRect();
    const panelWidth = Math.min(300, window.innerWidth - 24);
    themePanel.style.width = panelWidth + "px";
    themePanel.style.top = (trigger.bottom + 10) + "px";
    themePanel.style.left = Math.max(12, Math.min(trigger.right - panelWidth, window.innerWidth - panelWidth - 12)) + "px";
  }

  window.addEventListener("resize", function () {
    if (themePanel && themePanel.classList.contains("is-open")) positionThemePanel();
  });

  function getPreference(key, fallback) {
    try { return localStorage.getItem(key) || fallback; } catch (error) { return fallback; }
  }

  function setPreference(key, value) {
    try { localStorage.setItem(key, value); } catch (error) { /* Storage may be disabled. */ }
  }

  /* ---------- Scroll progress bar ---------- */
  const progressBar = document.getElementById("scroll-progress");
  window.addEventListener("scroll", function () {
    if (!progressBar) return;
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    progressBar.style.width = pct + "%";

    const backToTop = document.getElementById("back-to-top");
    if (backToTop) {
      backToTop.classList.toggle("show", scrollTop > 400);
    }
  });

  /* ---------- Back to top ---------- */
  const backToTop = document.getElementById("back-to-top");
  if (backToTop) {
    backToTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------- GSAP hero entrance ---------- */
  if (window.gsap) {
    gsap.from(".hero-anim", {
      y: 24,
      duration: 0.9,
      stagger: 0.12,
      ease: "power3.out",
    });
  }

  /* ---------- Wishlist / Bookmark toggle (AJAX) ---------- */
  document.querySelectorAll("[data-toggle-wishlist]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      toggleAction(btn, btn.dataset.toggleWishlist, "wishlisted", "fa-heart");
    });
  });
  document.querySelectorAll("[data-toggle-bookmark]").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      toggleAction(btn, btn.dataset.toggleBookmark, "bookmarked", "fa-bookmark");
    });
  });

  function toggleAction(btn, url, key, iconClass) {
    fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((res) => res.json())
      .then((data) => {
        const active = data[key];
        btn.classList.toggle("active", active);
        const icon = btn.querySelector("i");
        if (icon) icon.className = active ? "fa-solid " + iconClass : "fa-regular " + iconClass;
      })
      .catch(() => {});
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }
});
