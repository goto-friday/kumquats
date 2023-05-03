#!/usr/bin/env python3

# cmag = calibrated magnitude
# mag = magnitude in image
# cmag_targ - mag_targ = cmag_comp - mag_comp
# cmag_targ = cmag_comp - mag_comp + mag_targ
# mag = 2.5*log10(flux)
# cmag_targ = cmag_comp - 2.5*log10(flux_comp) + 2.5*log10(flux_targ)
# cmag_targ = cmag_comp - 2.5*log10(flux_comp) - (-2.5*log10(flux_targ))
# cmag_targ = cmag_comp - 2.5*log10(flux_comp/flux_targ)

import json
import math as m

period = 1.715779
hjd0 = 2458066.914
filters = ['B', 'V', 'SG', 'SI', 'SR']
# TODO source?
comp = "comp98"
chk = "comp117"

known = json.load(open("dat/known.json"))
stars = json.load(open("dat/stars.json"))

c1mags = [11.967, 11.644, 11.764, 11.619, 11.620]

for i in range(len(filters)):
    with open(f"dat/{filters[i]}.csv", "w") as f:
        f.write("hjd,phase,V765Cas flux,comp1 flux,comp2 flux,mag\n")
        for hjd in stars["target"][filters[i]]:
            if hjd not in stars[comp][filters[i]] or \
                hjd not in stars[chk][filters[i]]:
                    continue
            t_flux = stars['target'][filters[i]][hjd][1]
            c1_flux = stars[comp][filters[i]][hjd][1]
            c2_flux = stars[chk][filters[i]][hjd][1]
            comp_mag = known[comp]['mags'][filters[i]]
            f.write(",".join([str(x) for x in [
                hjd,
                ((float(hjd)-hjd0)/period)%1,
                round(t_flux),
                round(c1_flux),
                round(c2_flux),
                (comp_mag-2.5*m.log10(t_flux/c1_flux))
            ]])+'\n')
