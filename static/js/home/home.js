// Home feature JS — interactive student dashboard.
// Controls Log Hours modal, Placement Drawer toggles, and progress bar animation.
// Owns only Home-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  const btnToggleLog = document.querySelector('#btn-toggle-log');
  const logModal = document.querySelector('#log-modal');
  const btnCloseLogModal = document.querySelector('#btn-close-log-modal');
  const btnCancelLogModal = document.querySelector('#btn-cancel-log-modal');

  const btnToggleEdit = document.querySelector('#btn-toggle-edit-placement');
  const editDrawer = document.querySelector('#placement-edit-drawer');

  // Open Log Modal
  if (btnToggleLog && logModal) {
    btnToggleLog.addEventListener('click', function () {
      logModal.style.display = 'flex';
      const timeIn = document.querySelector('#id_time_in');
      if (timeIn) timeIn.focus();
    });
  }

  // Close Log Modal
  function closeLogModal() {
    if (logModal) logModal.style.display = 'none';
  }

  if (btnCloseLogModal) btnCloseLogModal.addEventListener('click', closeLogModal);
  if (btnCancelLogModal) btnCancelLogModal.addEventListener('click', closeLogModal);

  if (logModal) {
    logModal.addEventListener('click', function (e) {
      if (e.target === logModal) closeLogModal();
    });
  }

  // Toggle Edit Placement Drawer
  if (btnToggleEdit && editDrawer) {
    btnToggleEdit.addEventListener('click', function () {
      if (editDrawer.style.display === 'none' || !editDrawer.style.display) {
        editDrawer.style.display = 'block';
        editDrawer.scrollIntoView({ behavior: 'smooth' });
      } else {
        editDrawer.style.display = 'none';
      }
    });
  }

  // Keyboard shortcut: Escape closes modal/drawer
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeLogModal();
      if (editDrawer) editDrawer.style.display = 'none';
    }
  });

  // Smooth progress bar fill
  const progressBar = document.querySelector('.progress-bar-fill');
  if (progressBar) {
    const targetWidth = progressBar.style.width;
    progressBar.style.width = '0%';
    setTimeout(function () {
      progressBar.style.width = targetWidth;
    }, 100);
  }
});
