/**
 * AURA Hotel — Formatting Engine
 *
 * Handles client-side currency and date formatting based on locale.
 */
(() => {
  "use strict";

  const DEFAULTS = {
    region: "US",
    currency: "USD",
    unitSystem: "metric",
    temperatureUnit: "celsius",
    timeFormat: "12h",
    themeMode: "system",
    colorTheme: "global",
  };

  /* ============================
     Formatting Utilities
     ============================ */
  function getLocale() {
    return document.documentElement.dataset.locale || "en-US";
  }

  function formatAllCurrencies(prefs) {
    document.querySelectorAll("[data-currency]").forEach((el) => {
      const amount = Number(el.dataset.currency);
      if (Number.isNaN(amount)) return;

      // Use explicit code if present, otherwise use user preference
      const code = el.dataset.currencyCode || prefs.currency;
      const formatted = new Intl.NumberFormat(getLocale(), {
        style: "currency",
        currency: code,
        maximumFractionDigits: code === "JPY" ? 0 : 2,
      }).format(amount);

      const suffix = el.textContent.includes("/") ? el.textContent.slice(el.textContent.indexOf("/")) : "";
      el.textContent = formatted + suffix;
    });
  }

  function formatAllDates() {
    const locale = getLocale();
    document.querySelectorAll("[data-date]").forEach((el) => {
      const date = new Date(el.dataset.date);
      if (Number.isNaN(date.getTime())) return;
      el.textContent = new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(date);
    });
  }

  /* ============================
     UI Interaction Logic
     ============================ */
  function initUI() {
    // Form Loading Spinners
    document.querySelectorAll("[data-loading-form]").forEach((form) => {
      form.addEventListener("submit", () => {
        const submit = form.querySelector('button[type="submit"]');
        if (!submit || !form.checkValidity()) return;
        submit.disabled = true;
        submit.innerHTML = `<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> ${submit.dataset.loadingLabel || ""}`;
      });
    });

    // Password Strength
    const signupForm = document.querySelector("[data-signup-form]");
    if (signupForm) {
      const password = signupForm.querySelector("#signup-password");
      const confirm = signupForm.querySelector("#signup-confirm-password");
      const meter = signupForm.querySelector("#password-strength");

      const updatePassword = () => {
        const val = password.value;
        let score = 0;
        if (val.length >= 8) score++;
        if (/[A-Za-z]/.test(val)) score++;
        if (/\d/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;

        meter.style.setProperty("--password-score", String(score));
        meter.textContent = val ? meter.dataset[`score${score}`] || "" : "";

        const mismatch = confirm.value && confirm.value !== val;
        confirm.setCustomValidity(mismatch ? meter.dataset.matchError || "" : "");
      };

      password?.addEventListener("input", updatePassword);
      confirm?.addEventListener("input", updatePassword);
    }
  }

  /* ============================
     Initialization
     ============================ */
  function init() {
    formatAllCurrencies(DEFAULTS);
    formatAllDates();
    initUI();
  }

  window.addEventListener("DOMContentLoaded", init);
})();
