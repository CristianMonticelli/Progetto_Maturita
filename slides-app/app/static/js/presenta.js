const TOTAL = window.TOTAL_SLIDES || 0;
let cur = 0;
let hideTimer = null;

function scaleSlides() {
  const view = document.getElementById('slideView');
  const vw = view.clientWidth;
  const vh = view.clientHeight;
  const scale = Math.min(vw / 960, vh / 540);
  const offX = (vw - 960 * scale) / 2;
  const offY = (vh - 540 * scale) / 2;
  document.querySelectorAll('.slide-frame').forEach(f => {
    f.style.transform = `scale(${scale})`;
    f.style.transformOrigin = 'top left';
    f.style.left = offX + 'px';
    f.style.top  = offY + 'px';
  });
  const es = document.getElementById('endScreen');
  es.style.width  = vw + 'px';
  es.style.height = vh + 'px';
}

scaleSlides();
window.addEventListener('resize', scaleSlides);

function showSlide(i) {
  document.querySelectorAll('.slide-frame').forEach(f => f.classList.remove('active'));
  document.getElementById('endScreen').classList.remove('active');
  if (i < TOTAL) {
    document.getElementById(`sf-${i}`).classList.add('active');
    document.getElementById('curSlide').textContent = i + 1;
  } else {
    document.getElementById('endScreen').classList.add('active');
    document.getElementById('curSlide').textContent = TOTAL;
  }
  document.querySelectorAll('.dot').forEach((d,idx) => d.classList.toggle('active', idx === i));
  document.getElementById('prevBtn').disabled = i === 0;
  document.getElementById('nextBtn').disabled = i >= TOTAL;
}

function nextSlide() { if (cur < TOTAL) { cur++; showSlide(cur); } }
function prevSlide() { if (cur > 0)     { cur--; showSlide(cur); } }
function goTo(i)     { if (i >= 0 && i < TOTAL) { cur = i; showSlide(cur); } }

function exitPres() {
  window.location.href = window.EXIT_URL || '/';
}

function showUI() {
  document.getElementById('topBar').classList.remove('hidden');
  document.getElementById('bottomBar').classList.remove('hidden');
}
function hideUI() {
  document.getElementById('topBar').classList.add('hidden');
  document.getElementById('bottomBar').classList.add('hidden');
}
function resetHide() { clearTimeout(hideTimer); hideTimer = setTimeout(hideUI, 3000); }

document.addEventListener('mousemove',  () => { showUI(); resetHide(); });
document.addEventListener('touchstart', () => { showUI(); resetHide(); });

document.addEventListener('keydown', e => {
  switch(e.key) {
    case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown': e.preventDefault(); nextSlide(); break;
    case 'ArrowLeft':  case 'ArrowUp':  case 'PageUp':              e.preventDefault(); prevSlide(); break;
    case 'Escape': exitPres(); break;
    case 'f': case 'F':
      e.preventDefault();
      document.fullscreenElement ? document.exitFullscreen()
        : document.documentElement.requestFullscreen().catch(()=>{});
      break;
  }
  resetHide();
});

showSlide(0);
setTimeout(() => document.getElementById('kbdHint').classList.add('hidden'), 3500);
resetHide();
