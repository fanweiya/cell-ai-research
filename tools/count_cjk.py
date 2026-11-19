import re
import sys
from html.parser import HTMLParser


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "svg"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main(path):
    p = Text()
    p.feed(open(path, encoding="utf-8").read())
    text = "".join(p.parts)
    body = re.sub(r"\s+", "", text)
    print(path, len(re.findall(r"[一-鿿]", text)), "汉字", len(body), "非空白字符")


for f in sys.argv[1:]:
    main(f)
