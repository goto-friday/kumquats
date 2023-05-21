import re
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

    def tmpl(self, cmd, inputs=[], outputs=[],
            ignored_inputs=[], ignored_outputs=[]):
        rulename = re.sub('[^\w.]', '.', cmd[0])
        # TODO do this better (trying to decide if file is in repo)
        if '/' in cmd[0] and cmd[0][0] != '/':
            inputs.append(cmd[0])
        return tw.dedent(f"""
        rule {rulename}
          command = lib/chk.py '{':'.join(inputs)}' '{':'.join(outputs)}' $
            '{':'.join(ignored_inputs)}' '{':'.join(ignored_outputs)}' $
            {' '.join(cmd)}
          pool = console
        build {' '.join(outputs)}: {rulename} {' '.join(inputs)}
        """)

    def add(self, cmd, inputs=[], outputs=[],
            ignored_inputs=[], ignored_outputs=[]):
        self.ninja_script += self.tmpl(cmd,
            inputs=inputs, outputs=outputs,
            ignored_inputs=ignored_inputs, ignored_outputs=ignored_outputs)

    def write(self):
        open("build.ninja", 'w').write(self.ninja_script)
