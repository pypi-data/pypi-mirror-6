#!/usr/bin/env python
import warnings as _warnings
_warnings.resetwarnings()
_warnings.filterwarnings('error')

from tdi import html

template = html.from_string("""
<node tdi="item">
    <node tdi="nested">
        <node tdi="subnested"></node>
    </node><tdi tdi=":-nested">
    </tdi>
</node>
""".lstrip())

class Model(object):
    def render_item(self, node):
        def sep(node):
            node.hiddenelement = False
        node.nested.repeat(self.repeat_nested, itemlist=[1, 2, 3, 4])
        return True

    def repeat_nested(self, node, item):
        node['j'] = item

model = Model()
template.render(model)
