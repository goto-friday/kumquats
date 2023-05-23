#!/usr/bin/env python3

import json
import yaml
from lib.x import Builder, cat

config = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
b = Builder()

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

#b.add("src/screencasts.py",
#    inputs = ['dat/screencasts.yml'] +
#        cat('screencasts/main/', ['sab', 'tm'], '.mov') +
#        cat('screencasts/main/', ['elle', 'jb'], '.mp4'),
#    outputs = ['screencasts/main/out.mp4'],
#    ignored_inputs = ['screencasts/main/slides/*'],
#    ignored_outputs = ['screencasts/main/slides/*'])

b.write()
