import re
import itertools as it
import textwrap as tw

# cat('A', ['B', 'C'], 'D') == ['ABD', 'ACD']
def cat(*args):
    args = [a if isinstance(a, list) else [a] for a in args]
    return [''.join(a) for a in it.product(*args)]

class Builder:

    def __init__(self):
        self.ninja_script = ""

    def tmpl(self, cmd, inputs=[], outputs=[],
            ignored_inputs=[], ignored_outputs=[]):
        # TODO do this better (maybe don't make a rule per command)
        rulename = re.sub('[^\w.]', '.', '.'.join(cmd))
        # TODO do this better (trying to decide if file is in repo)
        if '/' in cmd[0] and cmd[0][0] != '/':
            inputs.append(cmd[0])
        # XXX can we just use ninja's $in and $out vars? the potential issue
        # is that that uses whitespace as a delimiter rather than :, which
        # could break filenames. then again, maybe : is equally likely to
        # cause such problems? and it would be sensible anyway to just
        # disallow spaces in filenames as a policy.
        # Actually, spaces will cause problems anyway b/c of the 'build' line
        return tw.dedent(f"""
        rule {rulename}
          command = lib/chk.py "$in" "$out" $
            '{' '.join(ignored_inputs)}' '{' '.join(ignored_outputs)}' $
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
