// Settings feature JS — submits the form automatically when a
// toggle is flipped, so preferences save without a separate click.
// Owns only Settings-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.settings-autosave').forEach(function (toggle) {
    toggle.addEventListener('change', function () {
      toggle.closest('form').submit();
    });
  });
});
