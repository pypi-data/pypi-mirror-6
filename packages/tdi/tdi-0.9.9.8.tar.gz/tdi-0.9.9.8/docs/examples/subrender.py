#!/usr/bin/env python
import warnings as _warnings
_warnings.resetwarnings()
_warnings.filterwarnings('error')

# BEGIN INCLUDE
from tdi import html
from tdi.tools import javascript

template = html.from_string("""
<html>
<body>
    <tdi tdi="-script">
    <div tdi="*html"><h1 tdi="h1">dynamic js-only-content</h1></div>
    <script tdi="*script">
        document.write('__html__')
    </script>
    </tdi>
</body>
</html>
""".lstrip())


class Model(object):
    def render_h1(self, node):
        node.content = u"My Heading"

    def render_script(self, node):
        html = node.html.render()
        javascript.fill(node.replace(None, node.script), dict(html=html))

template.render(Model())
