/* static/js/lista_tutorados.js */

document.addEventListener('DOMContentLoaded', function () {
  const buscaNome  = document.getElementById('buscaNome');
  const filtreSerie = document.getElementById('filtreSerie');

  function filtrar() {
    const nome  = buscaNome  ? buscaNome.value.toLowerCase()  : '';
    const serie = filtreSerie ? filtreSerie.value : '';

    document.querySelectorAll('.tutorado-card').forEach(card => {
      const nomeOk  = card.dataset.nome.includes(nome);
      const serieOk = !serie || card.dataset.serie === serie;
      card.style.display = (nomeOk && serieOk) ? '' : 'none';
    });
  }

  if (buscaNome)   buscaNome.addEventListener('input', filtrar);
  if (filtreSerie) filtreSerie.addEventListener('change', filtrar);
});
