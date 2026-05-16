document.addEventListener('DOMContentLoaded', () => {
  const t = window.STRINGS || {};

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
