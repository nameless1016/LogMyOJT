// Shared alert dismiss handling for CSP compliance (no inline onclick handlers)
document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', function (e) {
    const closeBtn = e.target.closest('.alert-close');
    if (closeBtn) {
      const alertBox = closeBtn.closest('.alert');
      if (alertBox) {
        alertBox.remove();
      }
    }
  });
});
