// static/js/tutorado_detalhe.js
// Copia o token de acesso do tutorado para a área de transferência

function copiarToken() {
  const token = document.getElementById('tokenVal').textContent.trim();
  const msg   = document.getElementById('copiadoMsg');

  navigator.clipboard.writeText(token).then(() => {
    msg.style.display = 'inline';
    setTimeout(() => msg.style.display = 'none', 2000);
  });
}
