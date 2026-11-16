// Register feature JS — real-time client-side password validation.
// Owns only Register-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('#register-form');
  const pw1 = document.querySelector('#id_password');
  const pw2 = document.querySelector('#id_password_confirm');
  const matchError = document.querySelector('#password-match-error');

  if (!form || !pw1 || !pw2) return;

  function validatePasswords() {
    if (!pw2.value) {
      if (matchError) matchError.style.display = 'none';
      pw2.classList.remove('input-error');
      return true;
    }

    if (pw1.value !== pw2.value) {
      if (matchError) {
        matchError.textContent = 'Passwords do not match.';
        matchError.style.display = 'block';
      }
      pw2.classList.add('input-error');
      return false;
    } else {
      if (matchError) matchError.style.display = 'none';
      pw2.classList.remove('input-error');
      return true;
    }
  }

  pw1.addEventListener('input', function () {
    if (pw2.value) validatePasswords();
  });

  pw2.addEventListener('input', validatePasswords);

  form.addEventListener('submit', function (e) {
    const isMatching = validatePasswords();
    if (!isMatching) {
      e.preventDefault();
      pw2.focus();
    }
  });
});
