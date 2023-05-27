#!/usr/bin/env python3

import json
import yaml
from lib.x import Builder, cat

config = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
b = Builder()

b.add(["lib/gengraph.py"],
    inputs = ['build.ninja'] + ['lib/graph.js'],
    outputs = ['dag.svg'])

b.add(["./build.py"],
    inputs = ['lib/x.py'] +
        cat('dat/', ['config.yml', 'known.json']),
    outputs = ['build.ninja'])

b.add(["src/query.py"],
    inputs = ['dat/config.yml'],
    outputs = ['dat/known.json'])

b.add(["src/calibrate.py"],
    inputs = ['dat/config.yml'] +
        cat('dat/', ['known', 'stars', 'period'], '.json'),
    outputs = cat('dat/', config['filters'], '.csv'))

b.add(["src/period.py"],
    inputs = ['matplotlibrc'] +
        cat('dat/', ['config.yml', 'known.json', 'asassn.csv']),
    outputs = ['dat/period.json', 'img/period/asassn.png'])

b.add(["src/color_index.py"],
    inputs = ['matplotlibrc'] +
        cat('dat/', ['config.yml', 'known.json']) +
        cat('dat/', config['filters'], '.csv'),
    outputs = ['img/color_index.png'])

b.add(["src/lightcurves.py"],
    inputs =  ['matplotlibrc'] +
        ['dat/config.yml'] +
        cat('dat/', ['known', 'period'], '.json') +
        cat('dat/', config['filters'], '.csv'),
    outputs = ['img/lightcurves/all.png'] +
        cat('img/lightcurves/', config['filters'], '.png'))

b.add(["src/tess.py"],
    inputs = ['matplotlibrc'] +
        ['dat/config.yml'] +
        cat('dat/', ['known', 'period'], '.json'),
    outputs = ['img/lightcurves/tess.png'])

b.add(["src/asassn.py"],
    inputs = ['matplotlibrc'] +
        cat('dat/', ['config.yml', 'asassn.csv']) +
        cat('dat/', ['known', 'period'], '.json'),
    outputs = ['img/lightcurves/asassn.png'])

b.add(["src/screencast.py", "main"],
    inputs = ['screencasts/main.yml'] + cat('screencasts/main/',
        ['sab.mov', 'tm.mov', 'jb.mp4', 'elle.mp4']),
    outputs = ['screencasts/main/out.mp4'],
    ignored_inputs = ['screencasts/main/slides/*'],
    ignored_outputs = ['screencasts/main/slides/*'])

b.add(["src/screencast.py", "aavso"],
    inputs = ['screencasts/aavso.yml'] + cat('screencasts/aavso/',
            ['intro.mov', 'end.mov', 'sab.mov', 'tm.mp4', 'jb.mp4', 'elle.mp4']),
    outputs = ['screencasts/aavso/out.mp4'],
    ignored_inputs = ['screencasts/aavso/slides/*'],
    ignored_outputs = ['screencasts/aavso/slides/*'])

b.write()
