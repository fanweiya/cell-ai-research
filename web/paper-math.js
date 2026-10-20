/* Abstracts are escaped text, hydrated on expansion. Never interpret them as HTML. */
function renderPaperMath(element) {
  if (!window.renderMathInElement || element.dataset.mathRendered) return;
  // arXiv abstracts also contain text-mode small caps around inline math.
  const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    if (node.parentElement.closest('code, pre, .katex')) continue;
    const source = node.textContent;
    const command = /\\textsc\s*\{/g;
    let match, offset = 0;
    const fragment = document.createDocumentFragment();
    while ((match = command.exec(source))) {
      let end = command.lastIndex, depth = 1;
      for (; end < source.length && depth; end++) {
        if (source[end] === '\\') { end++; continue; }
        if (source[end] === '{') depth++;
        if (source[end] === '}') depth--;
      }
      if (depth) break;
      fragment.append(source.slice(offset, match.index));
      const span = document.createElement('span');
      span.className = 'latex-smallcaps';
      span.textContent = source.slice(command.lastIndex, end - 1);
      fragment.append(span);
      offset = end;
      command.lastIndex = end;
    }
    if (offset) { fragment.append(source.slice(offset)); node.replaceWith(fragment); }
  }
  renderMathInElement(element, {
    delimiters: [
      {left:'$$', right:'$$', display:true},
      {left:'\\[', right:'\\]', display:true},
      {left:'\\(', right:'\\)', display:false},
      {left:'$', right:'$', display:false},
    ],
    throwOnError:false, trust:false, strict:'ignore', maxExpand:1000,
    errorColor:'inherit', ignoredClasses:['katex'],
  });
  element.dataset.mathRendered = 'true';
}
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.paper-details[open] .abs-body').forEach(renderPaperMath);
});
