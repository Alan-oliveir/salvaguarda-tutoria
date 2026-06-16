/* static/js/tutorado_detalhe.js */

document.addEventListener('DOMContentLoaded', function () {
  const btnCopiar  = document.querySelector('.btn-copiar');
  const tokenVal   = document.getElementById('tokenVal');
  const copiadoMsg = document.getElementById('copiadoMsg');

  if (btnCopiar && tokenVal) {
    btnCopiar.addEventListener('click', function () {
      navigator.clipboard.writeText(tokenVal.textContent.trim()).then(() => {
        if (copiadoMsg) {
          copiadoMsg.style.display = 'inline';
          setTimeout(() => copiadoMsg.style.display = 'none', 2000);
        }
      });
    });
  }
});