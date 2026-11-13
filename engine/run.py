"""python3 engine/run.py <episode_module> <out_dir> [audio|preview|render]"""
import sys, os, json, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'episodes'))
import lib

mod, outdir, mode = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else 'render')
ep = __import__(mod).EPISODE
tl_path = os.path.join(outdir, 'timeline.json')
if os.path.exists(tl_path) and os.path.exists(os.path.join(outdir, 'audio.wav')) and mode != 'audio':
    timeline = json.load(open(tl_path)); audio = os.path.join(outdir, 'audio.wav')
else:
    timeline, total, audio = lib.build(ep, outdir)
total = sum(t['D'] for t in timeline)
print(f"Dauer: {total:.1f}s", [round(t['D'], 1) for t in timeline])
if mode == 'preview':
    prevs = [None] + [(tl['D'], tl['cues']) for tl in timeline[:-1]]
    pdir = os.path.join(outdir, 'preview'); os.makedirs(pdir, exist_ok=True)
    for tl in timeline:
        cues = tl['cues']; marks = [0.2, cues[-1]['start'] + 0.8]
        for j, t in enumerate(marks):
            lib.frame(ep, tl['si'], t, tl['D'], cues, os.path.join(pdir, f"s{tl['si']}_{j}.jpg"), prevs[tl['si']])
    print('preview ok')
elif mode == 'render':
    t0 = time.time()
    prevs = [None] + [(tl['D'], tl['cues']) for tl in timeline[:-1]]
    jobs = sorted([(mod, tl['si'], tl['D'], tl['cues'], outdir, prevs[tl['si']]) for tl in timeline], key=lambda j: -j[2])
    with Pool(2) as p: p.map(lib.render_scene, jobs)
    out = os.path.join(outdir, 'video.mp4')
    lib.assemble(outdir, len(timeline), audio, out)
    print('fertig', out, f'{time.time() - t0:.0f}s')
