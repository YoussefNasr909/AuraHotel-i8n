(() => {
  const root = document.documentElement;
  const locale = root.dataset.locale || "en-US";

  document.querySelectorAll("[data-currency]").forEach((node) => {
    const amount = Number(node.dataset.currency);
    if (Number.isNaN(amount)) return;
    const currency = node.dataset.currencyCode || "USD";
    const suffix = node.textContent.includes("/") ? node.textContent.slice(node.textContent.indexOf("/")) : "";
    node.textContent = new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      maximumFractionDigits: 0,
    }).format(amount) + suffix;
  });

  document.querySelectorAll("[data-date]").forEach((node) => {
    const value = node.dataset.date;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return;
    node.textContent = new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(date);
  });

  document.querySelectorAll("[data-loading-form]").forEach((form) => {
    form.addEventListener("submit", () => {
      const submit = form.querySelector('button[type="submit"]');
      if (!submit || !form.checkValidity()) return;
      submit.disabled = true;
      submit.dataset.originalLabel = submit.innerHTML;
      submit.innerHTML = `<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> ${submit.dataset.loadingLabel || ""}`;
    });
  });

  const signupForm = document.querySelector("[data-signup-form]");
  if (!signupForm) return;

  const password = signupForm.querySelector("#signup-password");
  const confirmPassword = signupForm.querySelector("#signup-confirm-password");
  const meter = signupForm.querySelector("#password-strength");

  const scorePassword = (value) => {
    let score = 0;
    if (value.length >= 8) score += 1;
    if (/[A-Za-z]/.test(value)) score += 1;
    if (/\d/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;
    return score;
  };

  const updatePasswordState = () => {
    const value = password.value;
    const score = scorePassword(value);
    meter.dataset.score = String(score);
    meter.style.setProperty("--password-score", String(score));
    meter.textContent = value ? meter.dataset[`score${score}`] || "" : "";
    const mismatch = confirmPassword.value && confirmPassword.value !== value;
    confirmPassword.setCustomValidity(mismatch ? meter.dataset.matchError || "" : "");
  };

  password.addEventListener("input", updatePasswordState);
  confirmPassword.addEventListener("input", updatePasswordState);
})();
