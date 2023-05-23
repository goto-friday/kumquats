#!/usr/bin/env python3

# if ffmpeg appears to freeze, try reencoding the audio of that input file:
#   $ ffmpeg -i INPUT.mp4 -c:v copy OUTPUT.mp4

# TODO use https://github.com/kkroening/ffmpeg-python

import os
import sys
import shutil
import subprocess as sp
from os import path
from urllib import request
import yaml

cached_slides, dry_run = [False] * 2
for arg in sys.argv:
    if arg[0] != '-':
        continue
    for c in arg[1:]:
        if c == 'c':
            cached_slides = True
        elif c == 'n':
            dry_run = True

# TODO use kwargs
def run(cmd, input=None, capture_output=False):
    try:
        return sp.run(cmd, input=input, capture_output=capture_output, check=True)
    except sp.CalledProcessError as e:
        exit(e.stderr.decode() if capture_output else e)

def split_pdf(inp, out):
    return run(['gs',
        '-dBATCH',
        '-dNOPAUSE',
        '-dTextAlphaBits=4',
        '-dGraphicsAlphaBits=4',
        '-sDEVICE=png16m',
        f'-sOutputFile={out}',
        '-'], input=inp)

def screencast(name, dat):
    sections = dat['sections']
    slides_url = dat['slides']
    dir = path.join('screencasts', name)
    slide_dir = path.join(dir, 'slides')

    if not cached_slides and not dry_run:
        shutil.rmtree(slide_dir, ignore_errors=True)
        os.makedirs(slide_dir)
        with request.urlopen(slides_url+"/export?format=pdf") as r:
            split_pdf(r.read(), path.join(slide_dir, '%d.png'))

    # Sort by slide index
    slides = [path.join(slide_dir, f) for f in
        sorted(os.listdir(slide_dir), key=lambda f: int(f[:f.index('.')]))]
    cmd = ['ffprobe', '-v', 'error', '-show_entries', \
        'stream=width,height', '-of', 'csv=s=\\ :p=0', slides[0]]
    width, height = run(cmd, capture_output=True).stdout.strip().split()
    width, height = int(width), int(height)

    s1, s2, s3 = [""] * 3
    slideno, t_first, elapsed = [0] * 3
    inputs = []
    for i, rec in enumerate(sections):
        inputs += ['-i', path.join(dir, rec['file'])]
        s1 += f"crop=ih*4/3, \
            scale=320x240, \
            setdar=4/3, \
            pad={width}+320:{height}, \
                drawtext=text='{rec['name']}':y=240-text_h:fontsize=18:\
                box=1:boxcolor=black:fontcolor=white [{i}v];"
        s2 += f"[{i}v][{i}:a]"
        for t in rec['times']:
            t += elapsed
            # XXX can we pass tmpv implicitly?
            s3 += f"[tmpv][{slideno+len(sections)}:v] overlay='if(between(\
                t, {t_first}, {t}), 320, NAN)' [tmpv];"
            t_first = t
            slideno += 1
        cmd = ['ffprobe', '-show_entries', 'format=duration', '-v',
            'error', '-of', 'csv=p=0', path.join(dir, rec['file'])]
        elapsed += float(run(cmd, capture_output=True).stdout.strip())

    for s in slides:
        inputs += ['-i', s]
    filt = s1 + s2 + f"concat=n={len(sections)}:a=1 [tmpv][tmpa]; \
        [tmpa] speechnorm=e=50 [outa];" + s3[:-1]

    cmd = ['time', 'ffmpeg', '-hide_banner', '-y'] + inputs + [
        '-filter_complex', filt,
        '-map', '[tmpv]',
        '-map', '[outa]',
        '-framerate', '25',
        '-pix_fmt', 'yuv420p',
        '-fps_mode', 'vfr',
        path.join(dir, 'out.mp4')
    ]

    print(cmd)
    if not dry_run:
        run(cmd)


spec = yaml.load(open("dat/screencasts.yml"), Loader=yaml.Loader)
for scast in spec:
    screencast(scast, spec[scast])
