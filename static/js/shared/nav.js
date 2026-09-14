// Shared nav chrome JS — the username dropdown (Profile / Settings /
// Log out) appears identically on every authenticated screen, so its
// open/close behavior lives here rather than being duplicated or
// owned by any single feature.

document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.querySelector('#nav-user-toggle');
  const dropdown = document.querySelector('#nav-dropdown');
  if (!toggle || !dropdown) return;

  function closeDropdown() {
    dropdown.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  function openDropdown() {
    dropdown.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
  }

  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    if (dropdown.classList.contains('open')) {
      closeDropdown();
    } else {
      openDropdown();
    }
  });

  document.addEventListener('click', function (e) {
    if (!dropdown.contains(e.target) && e.target !== toggle) {
      closeDropdown();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDropdown();
  });
});
