function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.style.background = isError ? '#d63600' : '#ff6600';
  toast.style.opacity = '1';
  setTimeout(() => { toast.style.opacity = '0'; }, 2500);
}

async function apiFetch(url, options = {}) {
  let response;
  try {
    response = await fetch(url, { credentials: 'same-origin', ...options });
  } catch (networkError) {
    showToast('Errore di rete. Controlla la connessione.', true);
    throw networkError;
  }

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    showToast('Sessione scaduta. Ricarica la pagina.', true);
    const err = new Error('Non-JSON response');
    err.shouldReload = true;
    throw err;
  }

  const data = await response.json();

  if (!response.ok) {
    const msg = data.error || 'Errore sconosciuto.';
    showToast(msg, true);
    if (response.status === 401 && data.redirect) {
      setTimeout(() => { window.location.href = data.redirect; }, 2000);
    }
    throw data;
  }
  return data;
}

document.getElementById('btn-logout')?.addEventListener('click', async () => {
  await apiFetch('/api/auth/logout', { method: 'POST' });
  window.location.href = '/auth/login';
});

const langDropdown = document.querySelector('.lang-dropdown');
const langBtn = document.querySelector('.lang-btn');

if (langBtn && langDropdown) {
  langBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    langDropdown.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!langDropdown.contains(e.target)) {
      langDropdown.classList.remove('open');
    }
  });
  langDropdown.querySelectorAll('.lang-menu a').forEach(a => {
    a.addEventListener('click', () => { langDropdown.classList.remove('open'); });
  });
}
