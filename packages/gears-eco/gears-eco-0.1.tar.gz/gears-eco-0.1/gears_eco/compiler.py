import os
from gears.compilers import ExecCompiler


SOURCE = """(function() { %(namespace)s || (%(namespace)s = {});
    %(namespace)s["%(name)s"] = %(source)s;
}).call(this);"""


class EcoCompiler(ExecCompiler):
    result_mimetype = 'application/javascript'
    executable = 'node'
    params = [os.path.join(os.path.dirname(__file__), 'compiler.js')]

    def __call__(self, asset):
        super(EcoCompiler, self).__call__(asset)
        asset.processed_source = SOURCE % {
            'name': asset.attributes.path_without_suffix,
            'source': asset.processed_source,
            'namespace': 'this.JST',
        }