/* static/js/detalhe_reuniao.js */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Confirmação de exclusão ── */
  const btnDeletar = document.getElementById('btnDeletarReuniao');
  if (btnDeletar) {
    btnDeletar.addEventListener('click', function (e) {
      if (!confirm('Tem certeza que deseja excluir esta reunião? Esta ação não pode ser desfeita.')) {
        e.preventDefault();
      }
    });
  }

  /* ── Copiar link ── */
  const btnCopiarLink = document.getElementById('btnCopiarLink');
  if (btnCopiarLink) {
    btnCopiarLink.addEventListener('click', function () {
      const link = this.dataset.link;
      if (!link) return;
      navigator.clipboard.writeText(link).then(() => {
        if (typeof Toastify !== 'undefined') {
          Toastify({
            text: 'Link copiado!',
            duration: 2000,
            gravity: 'bottom',
            position: 'right',
            style: { background: 'var(--sg-success)' }
          }).showToast();
        }
      });
    });
  }
});
