// static/js/tutorado_foto.js
// Preview da foto antes do upload — compartilhado entre cadastrar e editar tutorado

function previewFoto(input) {
  const preview = document.getElementById('fotoPreview');

  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.innerHTML = `<img src="${e.target.result}" alt="preview">`;
    };
    reader.readAsDataURL(input.files[0]);
  }
}
