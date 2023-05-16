import itertools as it
import textwrap as tw
from os import path

# cat('A', ['B', 'C'], 'D') == ['ABD', 'ACD']
def cat(*args):
    args = [a if isinstance(a, list) else [a] for a in args]
    return [''.join(a) for a in it.product(*args)]

class Builder:

    tmpl = tw.dedent("""
    rule {0}
      command = {1}
      pool = console
    build {2}: {0} {1} {3}
    """)

    def __init__(self):
        self.ninja_script = tw.dedent(r"""
        rule gengraph
          command = { ninja -t graph | gvpr -i 'N[label!="src/*.py"]' | $
            dot -Tdot | gvcolor | dot -Tsvg | sed -n '$$!p'; $
            echo '<script><![CDATA['; cat lib/graph.js; $
            echo ']]></script></svg>'; } > $out
        build dag.svg: gengraph build.ninja
        """)

    def add(self, script, inputs=[], outputs=[]):
        if '/' not in script:
            script = './' + script
        self.ninja_script += self.tmpl.format(path.basename(script),
            script, ' '.join(outputs), ' '.join(inputs))

    def write(self):
        open("build.ninja", 'w').write(self.ninja_script)
