/* static/js/lista_reunioes.js */

document.addEventListener('DOMContentLoaded', function () {

  /* ── Filtros client-side ── */
  const selectTutorado = document.getElementById('filtroTutorado');
  const selectMateria  = document.getElementById('filtroMateria');
  const selectStatus   = document.getElementById('filtroStatus');
  const cards          = document.querySelectorAll('.reuniao-card');

  function filtrar() {
    const tutorado = selectTutorado ? selectTutorado.value : '';
    const materia  = selectMateria  ? selectMateria.value  : '';
    const status   = selectStatus   ? selectStatus.value   : '';

    cards.forEach(card => {
      const okT = !tutorado || card.dataset.tutorado === tutorado;
      const okM = !materia  || card.dataset.materia  === materia;
      const okS = !status   || card.dataset.status   === status;
      card.style.display = (okT && okM && okS) ? '' : 'none';
    });
  }

  if (selectTutorado) selectTutorado.addEventListener('change', filtrar);
  if (selectMateria)  selectMateria.addEventListener('change',  filtrar);
  if (selectStatus)   selectStatus.addEventListener('change',   filtrar);

  /* ── Modal de nova reunião ── */
  const overlay   = document.getElementById('modalOverlay');
  const btnAbrir  = document.getElementById('btnNovaReuniao');
  const btnFechar = document.getElementById('btnModalFechar');
  const btnCancel = document.getElementById('btnModalCancelar');

  function abrirModal() {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function fecharModal() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (btnAbrir)  btnAbrir.addEventListener('click', abrirModal);
  if (btnFechar) btnFechar.addEventListener('click', fecharModal);
  if (btnCancel) btnCancel.addEventListener('click', fecharModal);

  // Fechar clicando fora do modal
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) fecharModal();
    });
  }

  // Fechar com Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay && overlay.classList.contains('open')) {
      fecharModal();
    }
  });

  /* ── Confirmação de exclusão ── */
  document.querySelectorAll('.btn-deletar').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm('Tem certeza que deseja excluir esta reunião?')) {
        e.preventDefault();
      }
    });
  });
});