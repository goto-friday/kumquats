#!/usr/bin/env python3

import json
import yaml
from lib.x import Builder, cat

config = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
b = Builder()

b.add("build.py",
    inputs = cat('lib/', ['x.py', 'graph.js']),
    outputs = ['build.ninja'])

b.add("src/query.py",
    inputs = ['dat/config.yml'],
    outputs = ['dat/known.json'])

b.add("src/calibrate.py",
    inputs = ['dat/config.yml'] +
        cat('dat/', ['known', 'stars', 'period'], '.json'),
    outputs = cat('dat/', config['filters'], '.csv'))

b.add("src/period.py",
    inputs = cat('dat/', ['config.yml', 'known.json', 'asassn.csv']),
    outputs = ['dat/period.json', 'img/period/asassn.png'])

b.add("src/color_index.py",
    inputs = cat('dat/', ['config.yml', 'known.json']) +
        cat('dat/', config['filters'], '.csv'),
    outputs = ['img/color_index.png'])

b.add("src/lightcurves.py",
    inputs = ['dat/config.yml'] +
        cat('dat/', ['known', 'period'], '.json') +
        cat('dat/', config['filters'], '.csv'),
    outputs = ['img/lightcurves/all.png'])

b.add("src/tess.py",
    inputs = ['dat/config.yml'] +
        cat('dat/', ['known', 'period'], '.json'),
    outputs = ['img/lightcurves/tess.png'])

b.add("src/asassn.py",
    inputs = cat('dat/', ['config.yml', 'asassn.csv']) +
        cat('dat/', ['known', 'period'], '.json'),
    outputs = ['img/lightcurves/asassn.png'])

b.write()
