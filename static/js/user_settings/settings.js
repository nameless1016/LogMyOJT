// Settings feature JS — submits the form automatically when a
// toggle is flipped, and provides instant visual feedback for Dark Mode.
// Owns only Settings-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.settings-autosave').forEach(function (toggle) {
    toggle.addEventListener('change', function () {
      // Instant theme toggle feedback for dark mode toggle
      if (toggle.name === 'dark_mode') {
        document.body.classList.toggle('dark-mode', toggle.checked);
      }
      toggle.closest('form').submit();
    });
  });
});
