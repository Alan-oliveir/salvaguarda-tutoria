/* static/js/disponibilidade.js */

document.addEventListener('DOMContentLoaded', function () {

  // Confirmação de exclusão de bloco de disponibilidade
  document.querySelectorAll('.btn-deletar-disp').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm('Remover este bloco de disponibilidade?')) {
        e.preventDefault();
      }
    });
  });

  // Validação client-side do formulário de nova disponibilidade
  const form = document.getElementById('formNovaDisponibilidade');
  if (form) {
    form.addEventListener('submit', function (e) {
      const inicio = form.querySelector('[name="hora_inicio"]').value;
      const fim    = form.querySelector('[name="hora_fim"]').value;

      if (inicio && fim && inicio >= fim) {
        e.preventDefault();
        if (typeof Toastify !== 'undefined') {
          Toastify({
            text: 'O horário de início deve ser antes do horário de fim.',
            duration: 3500,
            gravity: 'bottom',
            position: 'right',
            style: { background: 'var(--sg-error)' },
          }).showToast();
        } else {
          alert('O horário de início deve ser antes do horário de fim.');
        }
      }
    });
  }
});
