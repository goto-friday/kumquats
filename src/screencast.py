#!/usr/bin/env python3

# If ffmpeg appears to freeze, try reencoding the audio of that input file:
#   $ ffmpeg -i FILE.mp4 -c:v copy NEW.mp4

# Args:
# -n: dry run; optional
# -c: use cached slides; optional
# file: spec file in yaml format

# TODO use https://github.com/kkroening/ffmpeg-python
# TODO do something about the "deprecated pixel format" warning
# TODO reencode audio automatically to fix the freezing issue?
# TODO fix aspect ratio of aavso slide
# TODO implement text overlays (see ~/astro/aavso_scast/a.awk)
# TODO set slide dimensions w/ ffmpeg
# TODO support different slide aspect ratios
# TODO maybe fade

import os
import sys
import shutil
import subprocess as sp
from pathlib import Path
from urllib import request
import yaml

def run(cmd, **kwargs):
    try:
        return sp.run(cmd, check=True, **kwargs)
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

cached_slides, dry_run = [False] * 2
for arg in sys.argv:
    if arg[0] != '-':
        break
    for c in arg[1:]:
        match c:
            case 'c': cached_slides = True
            case 'n': dry_run = True

name = sys.argv[-1]
cfg_file = "screencasts" / Path(name + '.yml')
if not cfg_file.exists():
    exit(f"'{cfg_file}' does not exist")

cfg = yaml.load(open(cfg_file), Loader=yaml.Loader)
dir = Path("screencasts") / name
slides_dir = dir / "slides"
slides_url = cfg['slides']
sections = cfg['sections']

if not cached_slides and not dry_run:
    shutil.rmtree(slide_dir, ignore_errors=True)
    slide_dir.mkdir()
    with request.urlopen(slides_url+"/export?format=pdf") as r:
        split_pdf(r.read(), slide_dir / '%d.png')

# Sort by slide index
slides = [slide_dir / f for f in
    sorted(os.listdir(slide_dir), key=lambda f: int(f[:f.index('.')]))]
cmd = ['ffprobe', '-v', 'error', '-show_entries', \
    'stream=width,height', '-of', 'csv=s=\\ :p=0', slides[0]]
width, height = run(cmd, capture_output=True).stdout.strip().split()
width, height = int(width), int(height)

s1, s2, s3 = [""] * 3
slideno, t_first, elapsed = [0] * 3
inputs = []
for i, rec in enumerate(sections):
    inputs += ['-i', dir / rec['file']]
    s1 += f"crop=ih*4/3, \
        scale=640x480, \
        setdar=4/3, \
        pad={width}+640:{height}, \
            drawtext=text='{rec['name']}':y=480-text_h:fontsize=18:\
            box=1:boxcolor=black:fontcolor=white [{i}v];"
    s2 += f"[{i}v][{i}:a]"
    if 'times' not in rec and elapsed == 0:
        s3 = f"[tmpv][{len(sections)}:v] overlay=640 [tmpv];"
    elif 'times' in rec:
        for t in rec['times']:
            t += elapsed
            s3 += f"[tmpv][{slideno+len(sections)}:v] overlay='if(\
                between(t, {t_first}, {t}), 640, NAN)' [tmpv];"
            t_first = t
            slideno += 1
    cmd = ['ffprobe', '-show_entries', 'format=duration', '-v',
        'error', '-of', 'csv=p=0', dir / rec['file']]
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
    dir / 'out.mp4'
]

print(cmd)
if not dry_run:
    run(cmd)
