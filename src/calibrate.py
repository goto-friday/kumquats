#!/usr/bin/env python3

import json
import io
import math as m
import yaml

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
stars = json.load(open("dat/stars.json"))
period = json.load(open("dat/period.json"))['period']
epoch = known[c['target']]['vsx']['Epoch']

for filt in c['filters']:
    targ = stars['target'][filt]
    comp = stars[c['comp']][filt]
    chk = stars[c['check']][filt]
    comp_mag = known[c['comp']]['apass9'][filt+'mag']

    out = io.StringIO()
    print("hjd,phase,target flux,comp flux,check flux,mag", file=out)
    for hjd in filter(lambda hjd: hjd in comp and hjd in chk, targ):
        targ_flux = targ[hjd][1]
        comp_flux = comp[hjd][1]
        chk_flux = chk[hjd][1]
        phase = (float(hjd) - epoch)/period % 1
        mag = comp_mag - 2.5 * m.log10(targ_flux/comp_flux)
        print(hjd, phase, targ_flux, comp_flux, chk_flux, mag,
            sep=',', file=out)
    open(f"dat/{filt}.csv", 'w').write(out.getvalue())
