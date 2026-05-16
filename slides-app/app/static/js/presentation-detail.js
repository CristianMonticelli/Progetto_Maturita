function scalePreviews() {
  document.querySelectorAll('.slide-preview-outer').forEach(outer => {
    const inner = outer.querySelector('.slide-preview-inner');
    if (!inner) return;
    const scale = outer.clientWidth / 960;
    inner.style.transform = `scale(${scale})`;
  });
}
scalePreviews();
window.addEventListener('resize', scalePreviews);

document.addEventListener('DOMContentLoaded', () => {
  const presentationId = window.PRESENTATION_ID;
  const S = window.STRINGS || {};
  const container = document.getElementById('slides-container');

  function buildComponentHtml(comp) {
    const bgStyle = (comp.bg_color && comp.bg_color !== 'transparent')
      ? `background:${comp.bg_color};border-radius:4px;` : '';
    const style = `left:${comp.x}%;top:${comp.y}%;width:${comp.width}%;height:${comp.height}%;${bgStyle}`;
    if (comp.type === 'image' && comp.image) {
      return `<div class="sp-comp" style="${style}"><img src="${comp.image}" style="width:100%;height:100%;object-fit:contain;border-radius:4px;pointer-events:none;"></div>`;
    } else if (comp.type === 'title') {
      return `<div class="sp-comp" style="${style}"><div style="font-size:${comp.font_size||48}px;font-weight:700;color:${comp.color||'#ff6600'};line-height:1.2;white-space:pre-wrap;width:100%;height:100%;overflow:hidden;">${comp.content||''}</div></div>`;
    } else if (comp.type === 'text') {
      return `<div class="sp-comp" style="${style}"><div style="font-size:${comp.font_size||22}px;color:${comp.color||'#333333'};line-height:1.5;white-space:pre-wrap;width:100%;height:100%;overflow:hidden;">${comp.content||''}</div></div>`;
    } else if (comp.type === 'link') {
      return `<div class="sp-comp" style="${style}"><div style="font-size:${comp.font_size||18}px;color:${comp.color||'#0066cc'};text-decoration:underline;line-height:1.4;white-space:nowrap;width:100%;height:100%;overflow:hidden;">${comp.content||''}</div></div>`;
    }
    return '';
  }

  function buildSlideHtml(slide, index) {
    const components = slide.components || [];
    const compsHtml = components.length > 0
      ? components.map(c => buildComponentHtml(c)).join('')
      : `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#bbb;font-size:1em;">${S.nessunElemento || ''}</div>`;
    return `
      <div class="slide-group" data-slide-id="${slide.id}">
        <div class="slide-preview-outer" onclick="window.location='/slides/${slide.id}/modifica'">
          <span class="slide-number-badge">${index}</span>
          <div class="slide-preview-inner" style="background:${slide.bg_color || '#ffffff'};">
            ${compsHtml}
          </div>
        </div>
        <div class="ppt-slide-controls">
          <a href="/slides/${slide.id}/modifica" class="btn btn-secondary">${S.modificaSlide || ''}</a>
          <button class="btn move-slide-up" data-slide-id="${slide.id}">${S.spostaSu || ''}</button>
          <button class="btn move-slide-down" data-slide-id="${slide.id}">${S.spostaGiu || ''}</button>
          <button class="btn btn-danger delete-slide" data-slide-id="${slide.id}">${S.elimina || ''}</button>
        </div>
      </div>`;
  }

  document.querySelectorAll('.add-slide-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const bgColor = document.getElementById('new-bg').value;
      const template = btn.dataset.template;
      try {
        const res = await apiFetch(`/api/presentations/${presentationId}/slides`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bg_color: bgColor, template }),
        });
        const emptyMsg = document.getElementById('empty-slides-msg');
        if (emptyMsg) emptyMsg.remove();
        const index = container.querySelectorAll('.slide-group').length + 1;
        container.insertAdjacentHTML('beforeend', buildSlideHtml(res.slide, index));
        scalePreviews();
        showToast(S.slideAggiunta || 'Slide aggiunta!');
      } catch {}
    });
  });

  container.addEventListener('click', async e => {
    const up   = e.target.classList.contains('move-slide-up');
    const down = e.target.classList.contains('move-slide-down');
    if (!up && !down) return;
    e.preventDefault();
    e.stopPropagation();
    const slideId = e.target.dataset.slideId;
    try {
      await apiFetch(`/api/slides/${slideId}/${up ? 'move_up' : 'move_down'}`, { method: 'POST' });
      window.location.reload();
    } catch {}
  });

  container.addEventListener('click', async e => {
    if (!e.target.classList.contains('delete-slide')) return;
    e.stopPropagation();
    const slideId = e.target.dataset.slideId;
    if (!confirm(S.eliminareSlide || '')) return;
    try {
      await apiFetch(`/api/slides/${slideId}`, { method: 'DELETE' });
      const group = e.target.closest('.slide-group');
      group.style.transition = 'opacity 0.4s';
      group.style.opacity = '0';
      setTimeout(() => group.remove(), 400);
      showToast(S.slideEliminata || 'Slide eliminata.');
    } catch {}
  });

  document.getElementById('import-pptx-input').addEventListener('change', async function() {
    if (!this.files[0]) return;
    showToast(S.importazioneInCorso || 'Importazione in corso...');
    const fd = new FormData();
    fd.append('file', this.files[0]);
    try {
      const res = await apiFetch(`/api/presentations/${presentationId}/import`, {
        method: 'POST',
        body: fd,
      });
      showToast(`${S.importate || 'Importate'} ${res.slides_added} ${S.slide || 'slide!'}`);
      setTimeout(() => window.location.reload(), 1200);
    } catch {
      showToast(S.erroreImportazione || 'Errore importazione.', true);
    }
    this.value = '';
  });
});
