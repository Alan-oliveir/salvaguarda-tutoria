/* static/js/calendario_tutorado.js */

document.addEventListener('DOMContentLoaded', function () {

  const calendarEl  = document.getElementById('calendar');
  const overlay     = document.getElementById('modalOverlay');
  const btnFechar   = document.getElementById('btnModalFechar');
  const btnCancelar = document.getElementById('btnModalCancelar');

  // Campos ocultos do formulário de agendamento
  const inputData    = document.getElementById('inputData');
  const inputHorario = document.getElementById('inputHorario');

  // Exibe data/hora humanizada no header do modal
  const modalDataLabel = document.getElementById('modalDataLabel');

  // Cache dos eventos de disponibilidade para validação client-side
  let disponibilidadeCache = [];

  // ── Helpers ──────────────────────────────────────────────────────────────

  function padZero(n) { return String(n).padStart(2, '0'); }

  function formatarDataHora(date) {
    const dias = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${dias[date.getDay()]}, ${padZero(date.getDate())} ${meses[date.getMonth()]} · ${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
  }

  function isoDate(date) {
    return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())}`;
  }

  function isoTime(date) {
    return `${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
  }

  function dentroDaDisponibilidade(date) {
    const isoD = isoDate(date);
    return disponibilidadeCache.some(ev => {
      const start = new Date(ev.start);
      const end   = new Date(ev.end);
      // Mesma data e dentro do bloco horário
      return isoDate(start) === isoD && date >= start && date < end;
    });
  }

  // ── Modal ────────────────────────────────────────────────────────────────

  function abrirModal(date) {
    inputData.value    = isoDate(date);
    inputHorario.value = isoTime(date);
    if (modalDataLabel) modalDataLabel.textContent = formatarDataHora(date);
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function fecharModal() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (btnFechar)   btnFechar.addEventListener('click',   fecharModal);
  if (btnCancelar) btnCancelar.addEventListener('click', fecharModal);
  if (overlay) {
    overlay.addEventListener('click', e => { if (e.target === overlay) fecharModal(); });
  }
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay?.classList.contains('open')) fecharModal();
  });

  // ── FullCalendar ─────────────────────────────────────────────────────────

  if (!calendarEl) return;

  const slotsUrl = calendarEl.dataset.slotsUrl;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    locale: 'pt-br',

    headerToolbar: {
      left:   'prev,next today',
      center: 'title',
      right:  'timeGridWeek,timeGridDay',
    },

    slotMinTime:   '07:00:00',
    slotMaxTime:   '23:00:00',
    slotDuration:  '00:30:00',
    snapDuration:  '00:30:00',
    allDaySlot:    false,
    height:        640,
    nowIndicator:  true,

    eventTimeFormat: {
      hour:     '2-digit',
      minute:   '2-digit',
      meridiem: false,
      hour12:   false,
    },

    // Carrega eventos + disponibilidades via JSON
    events: function (fetchInfo, successCallback, failureCallback) {
      fetch(`${slotsUrl}?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`)
        .then(r => {
          if (!r.ok) throw new Error('Erro ao carregar horários.');
          return r.json();
        })
        .then(data => {
          // Separa disponibilidades para cache local
          disponibilidadeCache = data.filter(
            ev => ev.extendedProps?.tipo === 'disponibilidade'
          );
          successCallback(data);
        })
        .catch(err => {
          console.error(err);
          failureCallback(err);
        });
    },

    // Clique em célula de tempo → verificar disponibilidade → abrir modal
    dateClick: function (info) {
      const clickedDate = info.date;

      if (!dentroDaDisponibilidade(clickedDate)) {
        if (typeof Toastify !== 'undefined') {
          Toastify({
            text: 'Este horário está fora da disponibilidade do seu tutor.',
            duration: 3000,
            gravity: 'bottom',
            position: 'right',
            style: { background: 'var(--sg-error)' },
          }).showToast();
        }
        return;
      }

      abrirModal(clickedDate);
    },

    // Clique em evento existente → ir para o detalhe
    eventClick: function (info) {
      const props = info.event.extendedProps;
      if (props.tipo === 'reuniao' && props.pk) {
        const base = calendarEl.dataset.detalheBase;
        window.location.href = `${base}${props.pk}/`;
      }
    },

    // Visual: cursor pointer em eventos, default em disponibilidade
    eventDidMount: function (info) {
      if (info.event.display === 'background') {
        info.el.style.cursor = 'pointer';
        info.el.title = 'Clique em um horário aqui para agendar';
      } else if (info.event.extendedProps?.tipo === 'reuniao') {
        info.el.style.cursor = 'pointer';
        info.el.title = `${info.event.title} — clique para ver detalhes`;
      }
    },
  });

  calendar.render();
});
