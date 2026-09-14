// Register feature JS — client-side password confirmation hint.
// Owns only Register-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#register-form');
  const pw1 = document.querySelector('#id_password');
  const pw2 = document.querySelector('#id_password_confirm');

  if (!form || !pw1 || !pw2) return;

  form.addEventListener('submit', function (e) {
    if (pw1.value !== pw2.value) {
      e.preventDefault();
      alert('Passwords do not match.');
    }
  });
});
