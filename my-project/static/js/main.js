// Minimal progressive enhancements for the blog UI.
document.addEventListener("DOMContentLoaded", () => {
  // Confirm destructive actions marked with data-confirm.
  document.querySelectorAll("[data-confirm]").forEach((element) => {
    element.addEventListener("click", (event) => {
      if (!window.confirm(element.dataset.confirm)) {
        event.preventDefault();
      }
    });
  });
});
