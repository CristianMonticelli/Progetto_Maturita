document.addEventListener('DOMContentLoaded', () => {
  const CANVAS_W = 960;
  const CANVAS_H = 540;

  const slideId        = window.SLIDE_ID;
  const presentationId = window.PRESENTATION_ID;
  const S              = window.STRINGS || {};
  const canvas         = document.getElementById('slide-canvas');
  const canvasWrap     = document.getElementById('canvas-wrap');
  const canvasArea     = document.getElementById('canvas-area');

  let components = window.INITIAL_COMPONENTS || [];
  let selectedId = null;
  let tempId     = -1;

  let isDragging  = false;
  let isResizing  = false;
  let resizeDir   = '';
  let dragOffPct  = { x: 0, y: 0 };
  let resizeStart = {};

  function insertAtCursor(text) {
    const ta = document.getElementById('prop-content');
    if (!ta) return;
    const start = ta.selectionStart ?? ta.value.length;
    const end   = ta.selectionEnd   ?? ta.value.length;
    ta.value = ta.value.substring(0, start) + text + ta.value.substring(end);
    ta.selectionStart = ta.selectionEnd = start + text.length;
    ta.dispatchEvent(new Event('input'));
    ta.focus();
  }

  // Build char grid buttons
  document.querySelectorAll('.char-grid').forEach(grid => {
    const chars = grid.textContent.trim().split(/\s+/).filter(Boolean);
    grid.innerHTML = '';
    chars.forEach(ch => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'char-btn';
      btn.textContent = ch;
      btn.addEventListener('click', () => insertAtCursor(ch));
      grid.appendChild(btn);
    });
  });

  // Toggle emoji panel
  document.getElementById('btn-emoji').addEventListener('click', () => {
    const ep = document.getElementById('emoji-panel');
    const sp = document.getElementById('symbols-panel');
    sp.style.display = 'none';
    ep.style.display = ep.style.display === 'none' ? 'block' : 'none';
  });

  // Toggle symbols panel
  document.getElementById('btn-symbols').addEventListener('click', () => {
    const sp = document.getElementById('symbols-panel');
    const ep = document.getElementById('emoji-panel');
    ep.style.display = 'none';
    sp.style.display = sp.style.display === 'none' ? 'block' : 'none';
  });

  // Close panels when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#pr-content')) {
      document.getElementById('emoji-panel').style.display   = 'none';
      document.getElementById('symbols-panel').style.display = 'none';
    }
  });

  function scaleCanvas() {
    const availW = canvasArea.clientWidth  - 32;
    const availH = canvasArea.clientHeight - 32;
    const scale  = Math.min(availW / CANVAS_W, availH / CANVAS_H);
    canvas.style.transform = `scale(${scale})`;
    canvasWrap.style.width  = (CANVAS_W * scale) + 'px';
    canvasWrap.style.height = (CANVAS_H * scale) + 'px';
  }
  scaleCanvas();
  window.addEventListener('resize', scaleCanvas);

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\n/g,'<br>');
  }

  function mousePct(e) {
    const r = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - r.left) / r.width  * 100,
      y: (e.clientY - r.top)  / r.height * 100,
    };
  }

  function round1(v) { return Math.round(v * 10) / 10; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function renderAll() {
    canvas.innerHTML = '';
    [...components].sort((a,b) => (a.z_index||0)-(b.z_index||0)).forEach(renderComp);
  }

  function renderComp(comp) {
    const el = document.createElement('div');
    el.className = 'comp-el' + (comp.id === selectedId ? ' comp-selected' : '');
    el.dataset.id = comp.id;
    el.style.cssText = [
      `left:${comp.x}%`, `top:${comp.y}%`,
      `width:${comp.width}%`, `height:${comp.height}%`,
      `background:${(comp.bg_color && comp.bg_color !== 'transparent') ? comp.bg_color : 'transparent'}`,
      'border-radius:4px', 'padding:4px 8px',
    ].join(';');

    if (comp.type === 'title') {
      el.innerHTML = `<div style="font-size:${comp.font_size}px;font-weight:700;color:${comp.color};line-height:1.2;width:100%;height:100%;overflow:hidden;white-space:pre-wrap;">${esc(comp.content || 'Titolo')}</div>`;
    } else if (comp.type === 'text') {
      el.innerHTML = `<div style="font-size:${comp.font_size}px;color:${comp.color};line-height:1.5;width:100%;height:100%;overflow:hidden;white-space:pre-wrap;">${esc(comp.content || 'Testo')}</div>`;
    } else if (comp.type === 'image') {
      if (comp.image) {
        el.innerHTML = `<img src="${comp.image}" style="width:100%;height:100%;object-fit:contain;border-radius:4px;pointer-events:none;">`;
      } else {
        el.innerHTML = `<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#e8e8e8;color:#888;font-size:13px;border-radius:4px;border:2px dashed #bbb;box-sizing:border-box;">📷 ${esc(S.selezionaImmagine || 'Seleziona immagine')}</div>`;
      }
    } else if (comp.type === 'link') {
      el.innerHTML = `<div style="font-size:${comp.font_size}px;color:${comp.color};text-decoration:underline;line-height:1.4;width:100%;height:100%;overflow:hidden;white-space:nowrap;">${esc(comp.content || 'https://...')}</div>`;
    }

    if (comp.id === selectedId) {
      ['nw','n','ne','e','se','s','sw','w'].forEach(dir => {
        const h = document.createElement('div');
        h.className = `rh rh-${dir}`;
        h.dataset.dir = dir;
        el.appendChild(h);
      });
    }

    el.addEventListener('mousedown', onCompDown);
    canvas.appendChild(el);
  }

  function onCompDown(e) {
    if (e.target.classList.contains('rh')) {
      e.preventDefault();
      e.stopPropagation();
      const comp = getComp(+e.currentTarget.dataset.id);
      if (!comp) return;
      selectComp(comp.id);
      isResizing = true;
      resizeDir  = e.target.dataset.dir;
      const mp   = mousePct(e);
      resizeStart = { mx: mp.x, my: mp.y, x: comp.x, y: comp.y, w: comp.width, h: comp.height };
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    const id   = +e.currentTarget.dataset.id;
    selectComp(id);
    const comp = getComp(id);
    if (!comp) return;
    const mp   = mousePct(e);
    dragOffPct = { x: mp.x - comp.x, y: mp.y - comp.y };
    isDragging = true;
  }

  canvas.addEventListener('mousedown', e => { if (e.target === canvas) deselectAll(); });

  document.addEventListener('mousemove', e => {
    if (!isDragging && !isResizing) return;
    const mp   = mousePct(e);
    const comp = getComp(selectedId);
    if (!comp) return;
    const el   = canvas.querySelector(`[data-id="${selectedId}"]`);

    if (isDragging) {
      comp.x = round1(clamp(mp.x - dragOffPct.x, 0, 100 - comp.width));
      comp.y = round1(clamp(mp.y - dragOffPct.y, 0, 100 - comp.height));
      if (el) { el.style.left = comp.x + '%'; el.style.top = comp.y + '%'; }
      updatePosDisplay(comp);
    }

    if (isResizing) {
      const dx = mp.x - resizeStart.mx;
      const dy = mp.y - resizeStart.my;
      const MIN = 5;
      let {x, y, w, h} = resizeStart;

      if (resizeDir.includes('e')) w = Math.max(MIN, resizeStart.w + dx);
      if (resizeDir.includes('s')) h = Math.max(MIN, resizeStart.h + dy);
      if (resizeDir.includes('w')) { w = Math.max(MIN, resizeStart.w - dx); x = resizeStart.x + resizeStart.w - w; }
      if (resizeDir.includes('n')) { h = Math.max(MIN, resizeStart.h - dy); y = resizeStart.y + resizeStart.h - h; }

      x = clamp(x, 0, 100); y = clamp(y, 0, 100);
      w = Math.min(100 - x, w); h = Math.min(100 - y, h);

      comp.x = round1(x); comp.y = round1(y);
      comp.width = round1(w); comp.height = round1(h);

      if (el) {
        el.style.left = comp.x + '%'; el.style.top = comp.y + '%';
        el.style.width = comp.width + '%'; el.style.height = comp.height + '%';
      }
      updatePosDisplay(comp);
    }

    document.getElementById('coords-bar').textContent =
      `X:${comp.x.toFixed(1)}%  Y:${comp.y.toFixed(1)}%  W:${comp.width.toFixed(1)}%  H:${comp.height.toFixed(1)}%`;
  });

  document.addEventListener('mouseup', () => {
    if (isDragging || isResizing) {
      isDragging = false;
      isResizing = false;
      renderAll();
    }
  });

  function getComp(id) { return components.find(c => c.id === id) || null; }

  function selectComp(id) { selectedId = id; renderAll(); updateProps(); }

  function deselectAll() { selectedId = null; renderAll(); updateProps(); }

  const propsEmpty    = document.getElementById('props-empty');
  const propsBody     = document.getElementById('props-body');
  const propTypeLabel = document.getElementById('prop-type-label');
  const propContent   = document.getElementById('prop-content');
  const prContent     = document.getElementById('pr-content');
  const prImage       = document.getElementById('pr-image');
  const prFontsize    = document.getElementById('pr-fontsize');
  const prColor       = document.getElementById('pr-color');
  const propFs        = document.getElementById('prop-fs');
  const propFsVal     = document.getElementById('prop-fs-val');
  const propColor     = document.getElementById('prop-color');
  const propBgTr      = document.getElementById('prop-bg-tr');
  const propBgColor   = document.getElementById('prop-bg-color');
  const propImgPrev   = document.getElementById('prop-img-preview');
  const propImgFile   = document.getElementById('prop-img-file');

  function updatePosDisplay(comp) {
    document.getElementById('pi-x').textContent = comp.x.toFixed(1);
    document.getElementById('pi-y').textContent = comp.y.toFixed(1);
    document.getElementById('pi-w').textContent = comp.width.toFixed(1);
    document.getElementById('pi-h').textContent = comp.height.toFixed(1);
  }

  function updateProps() {
    if (!selectedId) {
      propsEmpty.style.display = 'block';
      propsBody.style.display  = 'none';
      return;
    }
    const comp = getComp(selectedId);
    if (!comp) return;

    propsEmpty.style.display = 'none';
    propsBody.style.display  = 'flex';

    const names = { title:'Titolo', text:'Testo', image:'Immagine', link:'Link' };
    propTypeLabel.textContent = names[comp.type] || comp.type;

    const isImg = comp.type === 'image';

    prContent.style.display  = isImg ? 'none' : 'flex';
    prImage.style.display    = isImg ? 'flex' : 'none';
    prFontsize.style.display = isImg ? 'none' : 'flex';
    prColor.style.display    = isImg ? 'none' : 'flex';

    if (!isImg) {
      propContent.value     = comp.content || '';
      propFs.value          = comp.font_size || 24;
      propFsVal.textContent = comp.font_size || 24;
      propColor.value       = comp.color || '#333333';
    }

    if (isImg && comp.image) {
      propImgPrev.innerHTML = `<img src="${comp.image}" style="max-width:100%;max-height:70px;border-radius:4px;">`;
    } else {
      propImgPrev.innerHTML = '';
    }

    const isTransp = !comp.bg_color || comp.bg_color === 'transparent';
    propBgTr.checked = isTransp;
    propBgColor.style.display = isTransp ? 'none' : 'inline-block';
    if (!isTransp) propBgColor.value = comp.bg_color;

    updatePosDisplay(comp);
  }

  propContent.addEventListener('input', () => {
    const comp = getComp(selectedId);
    if (!comp) return;
    comp.content = propContent.value;
    const inner = canvas.querySelector(`[data-id="${selectedId}"] div`);
    if (inner) inner.innerHTML = esc(comp.content);
  });

  propFs.addEventListener('input', () => {
    const v = +propFs.value;
    propFsVal.textContent = v;
    const comp = getComp(selectedId);
    if (!comp) return;
    comp.font_size = v;
    const inner = canvas.querySelector(`[data-id="${selectedId}"] div`);
    if (inner) inner.style.fontSize = v + 'px';
  });

  propColor.addEventListener('input', () => {
    const comp = getComp(selectedId);
    if (!comp) return;
    comp.color = propColor.value;
    const inner = canvas.querySelector(`[data-id="${selectedId}"] div`);
    if (inner) inner.style.color = propColor.value;
  });

  propBgTr.addEventListener('change', () => {
    const comp = getComp(selectedId);
    if (!comp) return;
    if (propBgTr.checked) {
      comp.bg_color = 'transparent';
      propBgColor.style.display = 'none';
    } else {
      propBgColor.style.display = 'inline-block';
      comp.bg_color = propBgColor.value;
    }
    const el = canvas.querySelector(`[data-id="${selectedId}"]`);
    if (el) el.style.background = comp.bg_color === 'transparent' ? 'transparent' : comp.bg_color;
  });

  propBgColor.addEventListener('input', () => {
    const comp = getComp(selectedId);
    if (!comp) return;
    comp.bg_color = propBgColor.value;
    const el = canvas.querySelector(`[data-id="${selectedId}"]`);
    if (el) el.style.background = comp.bg_color;
  });

  document.getElementById('prop-del').addEventListener('click', () => {
    if (selectedId === null) return;
    components = components.filter(c => c.id !== selectedId);
    selectedId = null;
    renderAll();
    updateProps();
  });

  propImgFile.addEventListener('change', async () => {
    const comp = getComp(selectedId);
    if (!comp || comp.type !== 'image' || !propImgFile.files[0]) return;
    const fd = new FormData();
    fd.append('image', propImgFile.files[0]);
    try {
      const res = await apiFetch(`/api/slides/${slideId}/upload_image`, { method:'POST', body: fd });
      comp.image = res.path;
      renderAll();
      updateProps();
    } catch { showToast(S.erroreCaricamento || 'Errore caricamento immagine', true); }
  });

  document.getElementById('bg-input').addEventListener('input', e => {
    canvas.style.background = e.target.value;
  });

  const addBtn  = document.getElementById('add-btn');
  const addMenu = document.getElementById('add-menu');
  addBtn.addEventListener('click', e => { e.stopPropagation(); addMenu.classList.toggle('open'); });
  document.addEventListener('click', () => addMenu.classList.remove('open'));

  const DEFAULTS = {
    title: { content:'Titolo', x:5,  y:5,  width:90, height:18, font_size:48, color:'#ff6600', bg_color:'transparent', image:null },
    text:  { content:'Testo',  x:5,  y:28, width:60, height:40, font_size:22, color:'#333333', bg_color:'transparent', image:null },
    image: { content:'',       x:63, y:5,  width:32, height:60, font_size:0,  color:'#000000', bg_color:'transparent', image:null },
link:  { content:'https://esempio.com', x:5, y:75, width:50, height:10, font_size:18, color:'#0066cc', bg_color:'transparent', image:null },
  };

  addMenu.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      const type = btn.dataset.type;
      const comp = { id: tempId--, type, z_index: 0, ...DEFAULTS[type] };
      components.push(comp);
      selectComp(comp.id);
      addMenu.classList.remove('open');
    });
  });

  document.addEventListener('keydown', e => {
    const tag = e.target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;

    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId !== null) {
      e.preventDefault();
      components = components.filter(c => c.id !== selectedId);
      selectedId = null;
      renderAll(); updateProps();
      return;
    }
    if (e.key === 'Escape') { deselectAll(); return; }

    if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key) && selectedId !== null) {
      e.preventDefault();
      const comp = getComp(selectedId);
      if (!comp) return;
      const step = e.shiftKey ? 5 : 1;
      if (e.key === 'ArrowLeft')  comp.x = clamp(comp.x - step, 0, 100 - comp.width);
      if (e.key === 'ArrowRight') comp.x = clamp(comp.x + step, 0, 100 - comp.width);
      if (e.key === 'ArrowUp')    comp.y = clamp(comp.y - step, 0, 100 - comp.height);
      if (e.key === 'ArrowDown')  comp.y = clamp(comp.y + step, 0, 100 - comp.height);
      comp.x = round1(comp.x); comp.y = round1(comp.y);
      renderAll(); updatePosDisplay(comp);
    }
  });

  document.getElementById('save-btn').addEventListener('click', async () => {
    const data = {
      bg_color: document.getElementById('bg-input').value,
      components: components.map(c => ({
        type:      c.type,
        content:   c.content || '',
        x:         c.x,
        y:         c.y,
        width:     c.width,
        height:    c.height,
        font_size: c.font_size || 0,
        color:     c.color     || '#333333',
        bg_color:  c.bg_color  || 'transparent',
        z_index:   c.z_index   || 0,
        image:     c.image     || null,
      }))
    };
    try {
      const res = await apiFetch(`/api/slides/${slideId}/components/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      components = res.components;
      selectedId = null;
      renderAll(); updateProps();
      showToast(S.salvata || 'Slide salvata!');
    } catch { showToast(S.erroreSalvataggio || 'Errore nel salvataggio.', true); }
  });

  renderAll();
  updateProps();
});
