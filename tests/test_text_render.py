import unittest
from text_render import render_prose


class TextRenderTests(unittest.TestCase):
    def test_trailing_punctuation_and_markdown(self):
        for source in ['https://github.com/NEXGEM/STP-Bench。', '[https://github.com/NEXGEM/STP-Bench。](https://github.com/NEXGEM/STP-Bench。)']:
            rendered = render_prose(source)
            self.assertIn('href="https://github.com/NEXGEM/STP-Bench"', rendered)
            self.assertTrue(rendered.endswith('</a>。'))

    def test_security_and_balanced_parentheses(self):
        rendered = render_prose('<script>alert(1)</script> https://example.org/Ab_(CD)。')
        self.assertNotIn('<script>', rendered)
        self.assertIn('href="https://example.org/Ab_(CD)"', rendered)
        self.assertNotIn('<a ', render_prose('[bad](javascript:alert(1))'))

    def test_math_preserved_and_code_escapes(self):
        self.assertEqual(render_prose(r'$\mathrm{\Phi}$'), r'$\mathrm{\Phi}$')
        self.assertIn('<code>plots.py</code>', render_prose(r'需要 \`plots.py\` 和 collate\_fn', code=True))
