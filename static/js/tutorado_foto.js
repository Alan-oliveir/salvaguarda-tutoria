/* static/js/tutorado_foto.js */

document.addEventListener('DOMContentLoaded', function () {
  const fotoInput = document.getElementById('fotoInput');

  if (fotoInput) {
    fotoInput.addEventListener('change', function () {
      const preview = document.getElementById('fotoPreview');
      if (!preview || !this.files || !this.files[0]) return;

      const reader = new FileReader();
      reader.onload = e => {
        preview.innerHTML = `<img src="${e.target.result}" alt="preview">`;
      };
      reader.readAsDataURL(this.files[0]);
    });
  }
});