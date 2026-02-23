  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash-pill:not(.flash-danger)').forEach((el) => {
      setTimeout(() => {
        const inst = bootstrap.Alert.getOrCreateInstance(el);
        inst.close();
      }, 5000);
    });
  });

  document.addEventListener('DOMContentLoaded', () => {
    const modalEl = document.getElementById('editGroupModal');
    const formEl = document.getElementById('editGroupForm');

    const idEl = document.getElementById('edit_group_id');
    const nameEl = document.getElementById('edit_name');
    const stufeEl = document.getElementById('edit_stufe');
    const fachEl = document.getElementById('edit_fach');
    const themaEl = document.getElementById('edit_thema');
    const appointmentEl = document.getElementById('edit_appointment');
    const placeEl = document.getElementById('edit_place');

    // Helper: Bootstrap validation styles zurücksetzen
    const resetValidation = () => {
      formEl.classList.remove('was-validated');
      [nameEl, stufeEl, fachEl, themaEl, appointmentEl, placeEl].forEach((field) => {
        field.classList.remove('is-valid', 'is-invalid');
        field.setCustomValidity('');
      });
    };

    // Wenn Modal geöffnet wird: Daten aus dem geklickten Button übernehmen
    modalEl.addEventListener('show.bs.modal', (event) => {
      const btn = event.relatedTarget;
      if (!btn) return;

      const groupId = btn.getAttribute('data-group-id') || '';
      const groupName = btn.getAttribute('data-group-name') || '';
      const groupGrade = btn.getAttribute('data-group-grade') || '';
      const groupSubject = btn.getAttribute('data-group-subject') || '';
      const groupTopic = btn.getAttribute('data-group-topic') || '';
      const appointmentEl = document.getElementById('edit_appointment');
      const groupPlace = btn.getAttribute('data-group-place') || '';

      // Form Action setzen: /groups/<id>/edit
      formEl.action = `/groups/${groupId}/edit`;

      // Felder befüllen
      idEl.value = groupId;
      nameEl.value = groupName;
      fachEl.value = groupSubject;
      themaEl.value = groupTopic;
      placeEl.value = groupPlace || '';

      // Date setzen
      const ts = btn.dataset.groupAppointment;

      if (ts) {
        // Unix datetime-local (YYYY-MM-DDTHH:MM)
        const d = new Date(parseInt(ts) * 1000);
        d.setHours(d.getHours() + 1);
        appointmentEl.value = d.toISOString().slice(0, 16);
      } else {
        appointmentEl.value = '';
      }

      if (groupGrade) {
        stufeEl.value = groupGrade;
      } else {
        stufeEl.value = '';
      }

      resetValidation();
    });

    // Optional: beim Schließen aufräumen
    modalEl.addEventListener('hidden.bs.modal', () => {
      formEl.reset();
      resetValidation();
      formEl.action = '';
      appointmentEl.value = '';
    });

    // Bootstrap Validation (Submit)
    formEl.addEventListener('submit', (event) => {
      if (!formEl.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      formEl.classList.add('was-validated');
    }, false);
  });



// Validierung unten
  document.addEventListener('DOMContentLoaded', () => {
  'use strict';

    const forms = document.querySelectorAll('.needs-validation');

    const validateField = (field) => {
      // nur felder validieren, die der browser auch kennt
      if (!(field instanceof HTMLInputElement ||
            field instanceof HTMLSelectElement ||
            field instanceof HTMLTextAreaElement)) return;

      if (field.disabled) return;

      //SPEZIALFALL: datetime-local darf nicht in der Vergangenheit liegen
      if (field.type === 'datetime-local') {
        const val = field.value;

        if (!val) {
          // optionales Feld
          field.setCustomValidity('');
        } else {
          const chosen = new Date(val);
          const now = new Date();

          if (isNaN(chosen.getTime())) {
            field.setCustomValidity('invalid-datetime');
          } else if (chosen.getTime() < now.getTime()) {
            field.setCustomValidity('past-datetime');
          } else {
            field.setCustomValidity('');
          }
        }
      }

      // Feld-Validity prüfen (HTML5)
      if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
      } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
      }
    };

    Array.from(forms).forEach((form) => {
      const fields = form.querySelectorAll('input, select, textarea');

      fields.forEach((field) => {

        field.addEventListener('change', () => validateField(field));

        field.addEventListener('blur', () => validateField(field));
      });

      form.addEventListener('submit', (event) => {
        // alle felder einmal prüfen
        fields.forEach((field) => validateField(field));

        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add('was-validated');
      }, false);
    });
  });