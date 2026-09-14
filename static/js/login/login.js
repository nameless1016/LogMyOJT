// Login feature JS — kept minimal on purpose.
// Handles only login-screen behavior (e.g. focusing the username field
// on load). It does not know about Register or Home.

document.addEventListener('DOMContentLoaded', function () {
  const usernameField = document.querySelector('#id_username');
  if (usernameField) {
    usernameField.focus();
  }
});
