#!/usr/bin/env python3

import sys
import subprocess as sp
import xml.etree.ElementTree as ET

cmd = "ninja -t graph | gvpr -i 'N[label!=\"src/*.py\"]' | \
    dot -Tdot | gvcolor | dot -Tsvg"
r = sp.run(cmd, shell=True, check=True, capture_output=True)

ET.register_namespace("", "http://www.w3.org/2000/svg")
root = ET.fromstring(r.stdout.decode())

title = root[0].find('{http://www.w3.org/2000/svg}title')
root[0].remove(title)

for elem in root[0]:
    if elem.get('class') not in ('node', 'edge'):
        continue
    title = elem.find('{http://www.w3.org/2000/svg}title')
    elem.set('x-title', title.text)
    elem.remove(title)

script = ET.Element('script')
script.text = open("lib/graph.js").read()
root.append(script)

ET.ElementTree(root).write("dag.svg")
