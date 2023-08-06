from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from aspen import renderers

import json

class Renderer(renderers.Renderer):
    def compile(self, filepath, raw):
        return raw

    def render_content(self, context):
        return json.dumps(eval(self.compiled, globals(), context))


class Factory(renderers.Factory):
    Renderer = Renderer

