"""Small safe formatter for cached prose; raw HTML is always escaped."""
import html
import re

_TOKEN = re.compile(r'\[([^\]\n]+)\]\((https?://[^\s<>]+?)\)|`([^`\n]+)`|https?://[^\s<>`]+')

_HREF = re.compile(r'\\href\{\s*(https?://[^\s{}]+?)\s*\}(?:\{([^{}]*)\})?')
_TEXTCMD = re.compile(r'\\(?:textbf|textit|emph|textsc|texttt|text|mbox|textrm|ours|footnote)\{([^{}]*)\}')
_ESCAPED = re.compile(r'\\([%&#_])')


def _clean_latex(text):
    """Strip LaTeX macros that leak in from arXiv abstracts before HTML rendering."""

    def _href(m):
        url, label = m.group(1), (m.group(2) or '').strip() or m.group(1)
        if label.lower() in ('link', 'url', 'here', 'this', '链接', '项目主页'):
            label = url
        return '[{}]({})'.format(label, url)

    text = _HREF.sub(_href, text)
    text = _TEXTCMD.sub(r'\1', text)
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
