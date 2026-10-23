/* Full-library search stays independent of the displayed batch. */
const paperList = { cards: [], matches: [], byId: new Map(), limit: 30, timer: null, observer: null, marks: new Map(), allOpen: false };
function hydratePaperDetails(details) {
  details.querySelector(':scope > summary').textContent = details.open ? '收起论文详情' : '展开论文详情';
  if (!details.open) return;
  const template = details.querySelector('template');
  if (template) {
    template.replaceWith(template.content.cloneNode(true));
    details.querySelector('.abs-sec')?.setAttribute('open', '');
  }
  details.querySelectorAll('.abs-body').forEach(element => window.renderPaperMath?.(element));
}
function initPaperList() {
  initFilterLayout();
  const data = new Map(PAPERS_DB.map(p => [p.id, p]));
  paperList.cards = [...document.querySelectorAll('.card[data-paper-id]')];
  paperList.cards.forEach(card => {
    const p = data.get(card.dataset.paperId) || {};
    // Decode the generator's escaped author string once, outside the input handler.
    const decoder = document.createElement('textarea'); decoder.innerHTML = p.authors || '';
    const template = card.querySelector('template');
    card.searchText = [p.id, p.title_en, p.title_zh, p.abstract, p.abstract_zh,
      p.key_points, decoder.value, ...(p.task_types || []), p.paradigm || '', (p.jev_score ? 'jev' : ''), template?.content.textContent || ''].join(' ').toLocaleLowerCase();
    paperList.byId.set(card.dataset.paperId, card);
  });
  initPaperRail();
  applyPaperFilters();
  initAutoLoading();
  window.addEventListener('hashchange', revealPaperHash);
  revealPaperHash();
}
function renderPaperBatch() {
  const displayed = new Set(paperList.matches.slice(0, paperList.limit));
  paperList.cards.forEach(card => { card.style.display = displayed.has(card) ? '' : 'none'; });
  const shown = Math.min(paperList.limit, paperList.matches.length);
  document.getElementById('resultCount').textContent = `找到 ${paperList.matches.length} 篇 · 已显示 ${shown} 篇`;
  document.getElementById('emptyResults').hidden = paperList.matches.length !== 0;
  const more = document.getElementById('loadMorePapers');
  more.hidden = shown >= paperList.matches.length;
  more.textContent = '继续向下滚动，自动载入更多论文';
  if (paperList.loadObserver) { paperList.loadObserver.unobserve(more); paperList.loadObserver.observe(more); }
  if (paperList.allOpen) expandDetails(paperList.matches.slice(0, paperList.limit));
  document.getElementById('expandBtn').textContent = paperList.allOpen ? '收起已显示论文' : '展开已显示论文';
  window.updatePaperRail?.();
}
function applyPaperFilters() {
  clearTimeout(paperList.timer);
  paperList.timer = null;
  const query = (document.getElementById('searchInput')?.value || '').trim().toLocaleLowerCase();
  paperList.matches = paperList.cards.filter(card => {
    let filter = true;
    if (activeFilter === 'code') filter = card.dataset.code === '1';
    else if (activeFilter === 'jev') filter = parseFloat(card.dataset.jev || '0') >= 5.5;
    return (!query || card.searchText.includes(query)) && filter
      && (activeMonth === 'all' || card.dataset.date.slice(0,7) === activeMonth);
  });
  paperList.limit = 30;
  renderPaperBatch();
}
window.getFilteredPaperIds = () => {
  // A pending debounce must not make Copilot use the previous search results.
  if (paperList.timer) { applyPaperFilters(); paperList.timer = null; }
  return paperList.matches.map(card => card.dataset.paperId);
};
function doSearch() {
  clearTimeout(paperList.timer);
  paperList.timer = setTimeout(() => { paperList.timer = null; applyPaperFilters(); }, 150);
}
function doFilter(value, button) {
  activeFilter = value;
  document.querySelectorAll('.fbtn').forEach(b => b.classList.toggle('active', b === button));
  applyPaperFilters();
}
function doMonthFilter(value) { activeMonth = value || 'all'; applyPaperFilters(); }
function resetPaperFilters() {
  document.getElementById('searchInput').value = '';
  document.getElementById('monthSelect').value = 'all'; activeMonth = 'all';
  doFilter('all', document.querySelector('.fbtn'));
}
function loadMorePapers() {
  if (paperList.limit >= paperList.matches.length) return;
  paperList.limit += 30; renderPaperBatch();
}
function initAutoLoading() {
  const sentinel = document.getElementById('loadMorePapers');
  const main = document.querySelector('.main-content');
  const mobile = window.matchMedia('(max-width: 1024px)');
  const observe = () => {
    paperList.loadObserver?.disconnect();
    if ('IntersectionObserver' in window) {
      paperList.loadObserver = new IntersectionObserver(entries => {
        if (entries.some(e => e.isIntersecting) && !sentinel.hidden) loadMorePapers();
      }, {root: mobile.matches ? null : main, rootMargin:'0px 0px 600px 0px'});
      paperList.loadObserver.observe(sentinel);
    }
  };
  observe(); mobile.addEventListener('change', observe);
}
function expandDetails(cards) {
  cards.map(c => c.querySelector('.paper-details')).filter(Boolean).forEach(d => {
    d.open = true; hydratePaperDetails(d);
    d.querySelectorAll('details.sec').forEach(section => { section.open = true; });
  });
}
function toggleAll() {
  const details = paperList.matches.slice(0, paperList.limit).map(c => c.querySelector('.paper-details')).filter(Boolean);
  const open = details.some(d => !d.open || [...d.querySelectorAll('details.sec')].some(section => !section.open));
  details.forEach(d => {
    d.open = open; hydratePaperDetails(d);
    d.querySelectorAll('details.sec').forEach(section => { section.open = open; });
  });
  paperList.allOpen = open;
  document.getElementById('expandBtn').textContent = open ? '收起已显示论文' : '展开已显示论文';
}
function revealPaperHash() {
  let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
  if (!id.startsWith('paper-')) return;
  const card = paperList.byId.get(id.slice(6)); if (!card) return;
  if (!paperList.matches.includes(card)) resetPaperFilters();
  paperList.limit = Math.max(paperList.limit, paperList.matches.indexOf(card) + 1);
  renderPaperBatch();
  const details = card.querySelector('.paper-details');
  details.open = true; hydratePaperDetails(details);
  card.scrollIntoView({block:'start'}); card.focus({preventScroll:true});
}
function initPaperRail() {
  const rail = document.getElementById('paperRail'), main = document.querySelector('.main-content');
  if (!rail || !main) return;
  if ('IntersectionObserver' in window) {
    const visible = new Map();
    let active = null;
    paperList.observer = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) visible.set(e.target, e.intersectionRatio); else visible.delete(e.target); });
      const next = [...visible.keys()].find(card => card.style.display !== 'none')?.dataset.paperId;
      if (active === next) return;
      paperList.marks.get(active)?.classList.remove('active');
      paperList.marks.get(next)?.classList.add('active'); active = next;
    }, {root:main, rootMargin:'0px 0px -55% 0px', threshold:0});
    paperList.cards.forEach(card => paperList.observer.observe(card));
  }
  window.updatePaperRail = () => {
    rail.replaceChildren(); paperList.marks.clear();
    paperList.matches.slice(0,paperList.limit).forEach((card, index) => {
      const mark = document.createElement('button'); mark.type = 'button'; mark.className = 'paper-rail-mark';
      const title = card.querySelector('.tzh')?.textContent || card.dataset.paperId;
      mark.setAttribute('aria-label', `跳转到论文 ${index+1}：${title}`);
      const tooltip = document.createElement('span'); tooltip.className = 'paper-rail-tooltip'; tooltip.textContent = title;
      mark.appendChild(tooltip);
      mark.onclick = () => { card.scrollIntoView({behavior:'smooth',block:'start'}); card.focus({preventScroll:true}); };
      paperList.marks.set(card.dataset.paperId, mark); rail.appendChild(mark);
    });
  };
}
function toggleSidebar() {
  const collapsed = document.querySelector('.app-container').classList.toggle('collapsed');
  const button = document.getElementById('sidebarToggle');
  button.textContent = collapsed ? '▶' : '◀'; button.style.left = collapsed ? '0' : '272px';
  document.querySelector('.sidebar').inert = collapsed;
}
function initFilterLayout() {
  const media = window.matchMedia('(max-width: 1024px)');
  const arrange = () => {
    const dialog = document.getElementById('mobileFilters');
    if (dialog.open) dialog.close();
    document.getElementById(media.matches ? 'mobileFilterSlot' : 'desktopFilterSlot').append(document.getElementById('paperFilters'));
    if (media.matches) {
      document.querySelector('.app-container').classList.remove('collapsed');
      document.querySelector('.sidebar').inert = false;
      const toggle=document.getElementById('sidebarToggle'); toggle.style.left='272px'; toggle.textContent='◀';
    }
  };
  arrange(); media.addEventListener('change', arrange);
}
function openMobileFilters() { document.getElementById('mobileFilters').showModal(); }
function closeMobileFilters() { document.getElementById('mobileFilters').close(); document.getElementById('mobileFilterButton').focus(); }
