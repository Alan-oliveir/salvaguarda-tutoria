// static/js/lista_tutorados.js
// Filtra os cards de tutorados por nome e série em tempo real

function filtrar() {
  const nome  = document.getElementById('buscaNome').value.toLowerCase();
  const serie = document.getElementById('filtreSerie').value;

  document.querySelectorAll('.tutorado-card').forEach(card => {
    const nomeOk  = card.dataset.nome.includes(nome);
    const serieOk = !serie || card.dataset.serie === serie;
    card.style.display = (nomeOk && serieOk) ? '' : 'none';
  });
}
