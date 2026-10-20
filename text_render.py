import html
import re

_TOKEN = re.compile(r'\[([^\]\n]+)\]\((https?://(?:[^\s()<>]|\([^\s()<>]+\))+)\)|`([^`\n]+)`|https?://(?:[^\s()<>]|\([^\s()<>]+\))+')

_HREF = re.compile(r'\\href\{\s*(https?://[^\s{}]+?)\s*\}(?:\{([^{}]*)\})?')
_TEXTCMD_PREFIX = re.compile(r'\\(?:textbf|textit|emph|textsc|texttt|text|mbox|textrm|ours|footnote)\{')
_ESCAPED = re.compile(r'\\([%&#_])')


def _strip_nested_commands(text):
    while True:
        m = _TEXTCMD_PREFIX.search(text)
        if not m:
            break
        start = m.start()
        pos = m.end()
        depth = 1
        while pos < len(text) and depth > 0:
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
            pos += 1
        if depth == 0:
            inner_content = text[m.end():pos - 1]
            text = text[:start] + inner_content + text[pos:]
        else:
            break
    return text


def _clean_latex(text):
    def _href(m):
        url, label = m.group(1), (m.group(2) or '').strip() or m.group(1)
        if label.lower() in ('link', 'url', 'here', 'this', '链接', '项目主页'):
            label = url
        return '[{}]({})'.format(label, url)

    text = _HREF.sub(_href, text)
    text = _strip_nested_commands(text)
    text = _ESCAPED.sub(r'\1', text)
    return text


def _clean_url(url):
    tail = ''
    while url:
        last = url[-1]
        if last in '。，；：！？、.,;:!?"\'' or (last in ')]}' and url.count(last) > url.count({')': '(', ']': '[', '}': '{'}[last])):
            tail = last + tail
            url = url[:-1]
        else:
            break
    return url, tail


def render_prose(value, code=False):
    text = _clean_latex(str(value or ''))
    if code:
        text = re.sub(r'\\([_`])', r'\1', text)
    parts, offset = [], 0
    for match in _TOKEN.finditer(text):
        parts.append(html.escape(text[offset:match.start()]))
        if match.group(3) is not None:
            parts.append('<code>' + html.escape(match.group(3)) + '</code>')
        else:
            raw_url = match.group(2) or match.group(0)
            url, tail = _clean_url(raw_url)
            label = match.group(1) or url
            if match.group(1) == raw_url:
                label = url
            parts.append(f'<a class="prose-link" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>')
            parts.append(html.escape(tail))
        offset = match.end()
    parts.append(html.escape(text[offset:]))
    return ''.join(parts).replace('\n', '<br>')
