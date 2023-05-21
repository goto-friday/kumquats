import itertools as it
import textwrap as tw
from os import path

# cat('A', ['B', 'C'], 'D') == ['ABD', 'ACD']
def cat(*args):
    args = [a if isinstance(a, list) else [a] for a in args]
    return [''.join(a) for a in it.product(*args)]

class Builder:

    # TODO move graph generator command into separate script and maybe
    # generate this rule from build.py
    def __init__(self):
        self.ninja_script = tw.dedent(r"""
        rule gengraph
          command = { ninja -t graph | gvpr -i 'N[label!="src/*.py"]' | $
            dot -Tdot | gvcolor | dot -Tsvg | sed -n '$$!p'; $
            echo '<script><![CDATA['; cat lib/graph.js; $
            echo ']]></script></svg>'; } > $out
        build dag.svg: gengraph build.ninja lib/graph.js
        """)

    def tmpl(self, arg0, inputs=[], outputs=[],
            ignored_inputs=[], ignored_outputs=[]):
        inputs.append(arg0)
        return tw.dedent(f"""
        rule {path.basename(arg0)}
          command = lib/chk.py '{':'.join(inputs)}' '{':'.join(outputs)}' $
            '{':'.join(ignored_inputs)}' '{':'.join(ignored_outputs)}' {arg0}
          pool = console
        build {' '.join(outputs)}: {path.basename(arg0)} {' '.join(inputs)}
        """)

    def add(self, script, inputs=[], outputs=[],
            ignored_inputs=[], ignored_outputs=[]):
        if '/' not in script:
            script = './' + script
        self.ninja_script += self.tmpl(script,
            inputs=inputs, outputs=outputs,
            ignored_inputs=ignored_inputs, ignored_outputs=ignored_outputs)

    def write(self):
        open("build.ninja", 'w').write(self.ninja_script)
