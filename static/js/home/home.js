// Home feature JS — interactive student dashboard.
// Controls Log Hours modal, Placement Drawer toggles, and progress bar animation.
// Owns only Home-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  const btnToggleLog = document.querySelector('#btn-toggle-log');
  const btnOpenFirstLog = document.querySelector('#btn-open-first-log');
  const logModal = document.querySelector('#log-modal');
  const btnCloseLogModal = document.querySelector('#btn-close-log-modal');
  const btnCancelLogModal = document.querySelector('#btn-cancel-log-modal');

  const btnToggleEdit = document.querySelector('#btn-toggle-edit-placement');
  const editDrawer = document.querySelector('#placement-edit-drawer');
  const btnClosePlacementDrawer = document.querySelector('#btn-close-placement-drawer');
  const btnCancelPlacementDrawer = document.querySelector('#btn-cancel-placement-drawer');

  function openLogModal() {
    if (logModal) {
      logModal.style.display = 'flex';
      const timeIn = document.querySelector('#id_time_in');
      if (timeIn) timeIn.focus();
    }
  }

  // Open Log Modal
  if (btnToggleLog) btnToggleLog.addEventListener('click', openLogModal);
  if (btnOpenFirstLog) btnOpenFirstLog.addEventListener('click', openLogModal);

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

  function closeEditDrawer() {
    if (editDrawer) editDrawer.style.display = 'none';
  }

  if (btnClosePlacementDrawer) btnClosePlacementDrawer.addEventListener('click', closeEditDrawer);
  if (btnCancelPlacementDrawer) btnCancelPlacementDrawer.addEventListener('click', closeEditDrawer);

  // Toggle Edit Placement Drawer
  if (btnToggleEdit && editDrawer) {
    btnToggleEdit.addEventListener('click', function () {
      if (editDrawer.style.display === 'none' || !editDrawer.style.display) {
        editDrawer.style.display = 'block';
        editDrawer.scrollIntoView({ behavior: 'smooth' });
      } else {
        closeEditDrawer();
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
