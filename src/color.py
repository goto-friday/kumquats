#!/usr/bin/env python3

import json
import csv
import itertools as it
import yaml
import matplotlib.pyplot as plt

def readin(filt):
    return [dict(phase=float(row[1]), mag=float(row[5]))
        for row in it.islice(csv.reader(open(f"dat/{filt}.csv")), 1, None)]

def bin(state):
    ret = {}
    for filt in c['filters']:
        pts = list(map(lambda x: x['mag'], filter(lambda x:
            any([interval['start'] <= x['phase'] <= interval['end']
            for interval in eclipses[state]]), dat[filt])))
        ret[filt] = dict(mean=sum(pts)/len(pts), n_pts=len(pts))
    return ret

def color_index(dat):
    # To include all filters, change 2 to 1 in both loops below
    filts = list(dat.keys())
    ret = {'B-V': {
        'c_idx': dat['B']['mean'] - dat['V']['mean'],
        'n_pts': dat['B']['n_pts'] + dat['V']['n_pts']}}
    for i in range(len(filts)-2):
        f1 = filts[i]
        for j in range(i+2, len(filts)):
            f2 = filts[j]
            ret[f1+'-'+f2] = {
                'c_idx': dat[f1]['mean'] - dat[f2]['mean'],
                'n_pts': dat[f1]['n_pts'] + dat[f2]['n_pts']}
    return ret

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
dat = {filt: readin(filt) for filt in c['filters']}

eclipses = dict(c['eclipses'].copy(), none=[])
ecl_list = sorted(it.chain(*eclipses.values()), key=lambda k: k['start'])
for i in range(len(ecl_list)-1):
    r = dict(start=ecl_list[i]['end'], end=ecl_list[i+1]['start'])
    eclipses['none'].append(r)

d = {state: color_index(bin(state)) for state in eclipses.keys()}
#states = list(d.keys())
states = ['primary', 'none', 'secondary']

markers = ['^', 'o', 2, 's', 3, 'd', 'v']
fig, ax = plt.subplots()
for i, combo in enumerate(d[states[0]].keys()):
    ax.plot([s[0].upper() + s[1:] for s in states],
        [d[s][combo]['c_idx'] for s in states],
        marker=markers[i], label=combo)
ax.set_ylabel("Color index")
ax.grid(axis='y')
fig.legend(loc='outside lower right', ncols=4)
fig.savefig("img/color_index.png")
