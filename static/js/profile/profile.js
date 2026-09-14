// Profile feature JS — live-preview a newly chosen profile image
// before it's uploaded. Owns only Profile-screen behavior.

document.addEventListener('DOMContentLoaded', function () {
  const input = document.querySelector('#id_profile_image');
  const preview = document.querySelector('#avatar-preview-img');
  const initial = document.querySelector('#avatar-initial');
  if (!input || !preview) return;

  input.addEventListener('change', function () {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function (e) {
      preview.src = e.target.result;
      preview.style.display = 'block';
      if (initial) initial.style.display = 'none';
    };
    reader.readAsDataURL(file);
  });
});
