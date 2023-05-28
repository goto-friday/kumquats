#!/usr/bin/env python3

import csv
import json
import itertools as it
import yaml

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']

rows = it.islice(csv.reader(open("dat/asassn.csv")), 1, None)
rows = filter(lambda row: float(row[6]) < 0.05, rows)
dat = [(float(row[0]), float(row[5]), row[9]) for row in rows]
dat = [((d[0]-epoch)/period%1, d[1], d[2]) for d in dat]
dat_g = list(filter(lambda d: d[2] == 'g', dat))
dat_v = list(filter(lambda d: d[2] == 'V', dat))
phases_g = [x[0] for x in dat_g]
phases_v = [x[0] for x in dat_v]
mags_g = [x[1] for x in dat_g]
mags_v = [x[1] for x in dat_v]

buf = "phase,mag\n"
for r in dat_g:
    buf += f"{r[0]},{r[1]}\n"
open("dat/asassn_g.csv", 'w').write(buf)

buf = "phase,mag\n"
for r in dat_v:
    buf += f"{r[0]},{r[1]}\n"
open("dat/asassn_v.csv", 'w').write(buf)
