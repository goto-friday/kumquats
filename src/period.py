#!/usr/bin/env python3

# why nterms=2?
# why samples_per_peak=100?
# how to choose period_lower_lim and period_upper_lim?
# https://iopscience.iop.org/article/10.3847/1538-4365/aab766

import json
import csv
import itertools as it

import yaml
import numpy as np
from astropy.timeseries import LombScargle
import matplotlib.pyplot as plt

c = yaml.load(open("dat/config.yml"), Loader=yaml.Loader)
known = json.load(open("dat/known.json"))
epoch = known[c['target']]['vsx']['Epoch']
# XXX tess?
hjd, mag, mag_err = [], [], []
for row in it.islice(csv.reader(open("dat/asassn.csv")), 1, None):
    if row[9] != 'V' or float(row[6]) >= 0.05:
        continue
    hjd.append(float(row[0]))
    mag.append(float(row[5]))
    mag_err.append(float(row[6]))

freq, psd = LombScargle(hjd, mag, mag_err, nterms=2).autopower(
    samples_per_peak=100,
    minimum_frequency=1/c['period_upper_lim'],
    maximum_frequency=1/c['period_lower_lim'])
period = 1/freq[np.argmax(psd)]

fig, ax = plt.subplots()
ax.set_xlabel("Period")
ax.set_ylabel("Power")
ax.plot(1/freq, psd)
ax.text(period+.001, max(psd)-.01, str(round(period, 6)))
fig.savefig("img/period/asassn.png")
open("dat/period.json", 'w').write(json.dumps(dict(period=period)))

"""
import lightkurve as lk

d = lk.search_lightcurve(c['target'],
    mission='TESS', author=c['tess_pipeline'])[0].download()
phase = ((d.time.value - epoch)/c['period'])%1
mag = d.time.value

freq, psd = LombScargle(phase, mag, nterms=2).autopower(
    samples_per_peak=100,
    minimum_frequency=1/c['period_upper_lim'],
    maximum_frequency=1/c['period_lower_lim'])

print(1/freq[np.argmax(psd)])
"""
