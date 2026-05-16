document.addEventListener('DOMContentLoaded', () => {
  const t = window.STRINGS || {};
  const modal = document.getElementById('modal-create');
  const btnCreate = document.getElementById('btn-create-presentation');
  const btnCancel = document.getElementById('btn-cancel-create');
  const form = document.getElementById('form-create-presentation');

  btnCreate.addEventListener('click', () => { modal.style.display = 'flex'; });

  btnCancel.addEventListener('click', () => {
    modal.style.display = 'none';
    form.reset();
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = { title: formData.get('title'), description: formData.get('description') };
    try {
      const result = await apiFetch('/api/presentations/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const container = document.getElementById('presentations-container');
      const newCard = document.createElement('article');
      newCard.className = 'presentation-card';
      newCard.setAttribute('data-presentation-id', result.presentation.id);
      newCard.innerHTML = `
        <div class="presentation-card-body">
          <h3><a href="/presentations/presentazione/${result.presentation.id}">${result.presentation.title}</a></h3>
          <p>${result.presentation.description || t.nessunaDesc}</p>
        </div>
        <div class="presentation-card-actions">
          <a href="/presentations/presentazione/${result.presentation.id}" class="btn btn-secondary">${t.apri}</a>
          <button class="btn btn-danger delete-presentation">${t.elimina}</button>
        </div>`;
      container.insertBefore(newCard, container.firstChild);
      const emptyMsg = document.getElementById('empty-state-msg');
      if (emptyMsg) emptyMsg.remove();
      modal.style.display = 'none';
      form.reset();
      showToast(t.presentazioneCreata);
    } catch (error) {
      if (!error.shouldReload) console.error('Errore creazione presentazione:', error);
    }
  });

  document.getElementById('presentations-container').addEventListener('click', async (e) => {
    if (!e.target.classList.contains('delete-presentation')) return;
    const card = e.target.closest('.presentation-card');
    const id = card.getAttribute('data-presentation-id');
    if (confirm(t.eliminareConferma)) {
      try {
        await apiFetch(`/api/presentations/${id}`, { method: 'DELETE' });
        card.style.transition = 'opacity 0.5s';
        card.style.opacity = '0';
        setTimeout(() => card.remove(), 500);
        showToast(t.presentazioneEliminata);
      } catch (error) {
        if (!error.shouldReload) console.error('Errore eliminazione presentazione:', error);
      }
    }
  });
});
