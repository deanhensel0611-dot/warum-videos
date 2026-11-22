"""Episode 32 (EN, general audience): How do bats find their way in the dark?
Facts checked (Maryland DNR "Bat echolocation", Scientific American "How do bats echolocate?", Ohio State Museum of
Biological Diversity "Bat sounds", Surlykke & Kalko 2008 PLoS ONE via NBC News "Bats can put on the loudest rock concert"):
- Bats are not blind; many species navigate and hunt in the dark by echolocation.
- They emit high-pitched calls, mostly ultrasonic (above ~20 kHz, the upper limit of human hearing), and listen to
  the echoes that bounce back from objects and prey.
- The delay between call and echo tells the distance; echoes also reveal size, shape, texture and movement direction.
- When closing in on prey, call rate rises sharply into a "feeding buzz" of up to ~200 calls per second.
- Some bats call at up to ~140 dB (measured close to the bat), louder than a rock concert - but it's too high-pitched for us to hear.
"""
import math, random
from lib import *

_bat = bat
def bat(c, x, y, s, t, **kw):
    kw.setdefault('colr', '#7b68b5')
    _bat(c, x, y, s, t, **kw)

NAVY = '#1b2a4a'
CALL = '#5ff0ff'
ECHO = '#ff5c85'

def night(c, t):
    night_sky(c, t, y1=1500)
    c.drawCircle(860, 760, 150, rad(860, 760, 150, [col('#fff6d0', 70), col('#fff6d0', 0)]))
    c.drawCircle(860, 760, 62, rad(840, 740, 80, [col('#fffbe8'), col('#e9e2c2')]))
    for dx, dy, rr in ((-18, -10, 12), (20, 18, 9), (8, -28, 6)):
        c.drawCircle(860 + dx, 760 + dy, rr, P(color=col('#d8cfa8', 160)))

def ground(c, t, y=1560):
    p = skia.Path(); p.moveTo(0, y)
    for i in range(0, W + 41, 40):
        p.lineTo(i, y - 40 * math.sin(i * 0.004 + 0.8))
    p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y - 60, 0, H), [col('#1f3a4a'), col('#0f1c2e')]))

def moth_outline():
    pts = []
    for sx in (-1, 1):
        for i in range(9):
            a = i / 8 * math.pi * 1.6 - 0.3
            pts.append((sx * (65 + 55 * math.cos(a)), -25 + 38 * math.sin(a) - 10))
        for i in range(5):
            a = i / 4 * math.pi + 0.2
            pts.append((sx * (40 + 35 * math.cos(a)), 40 + 30 * math.sin(a)))
    pts += [(0, -25), (0, 0), (0, 25), (0, 50)]
    random.Random(3).shuffle(pts)
    return pts
MOTH_PTS = moth_outline()

# ---------- 1: Hook (cold open: bat already flying, moth in the dark) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    night(c, t)
    bx = 300 + 120 * math.sin(t * 0.9); by = 1080 + 60 * math.sin(t * 1.7)
    bat(c, bx, by, 1.0, t)
    moth(c, 780, 1280 + 30 * math.sin(t * 2.3), 0.7, t)
    label_pill(c, 'NOT blind', 540, 700, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=ECHO)
    if t > t1:
        for k in range(3):
            sound_rings(c, bx + 60, by, t, t1 + 0.3 + k * 1.1, n=3, colr=CALL, both=False, a0=-30, sweep=60)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.3, 'sparkle')]

# ---------- 2: Very high-pitched calls, too high for us ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night(c, t)
    bat(c, 300, 920 + 30 * math.sin(t * 2), 0.9, t)
    for k in range(6):
        sound_rings(c, 360, 920, t, t0 + 0.3 + k * 0.7, n=3, colr=CALL, both=False, a0=-30, sweep=60, speed=520)
    label_pill(c, 'HIGH pitch', 560, 700, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#1fa8c9')
    if t > t1 - 0.4:
        bk = ease_out(prog(t, t1 - 0.4, 1.0))
        x0 = 140
        c.drawRoundRect(skia.Rect(x0, 1220, x0 + 800 * bk, 1300), 20, 20, P(color=col('#ffffff', 40)))
        # humans: 0-20 kHz, bats: ~20-120 kHz drawn on a 0-125 kHz scale
        hx = x0 + 800 * 20 / 125
        c.drawRoundRect(skia.Rect(x0, 1220, x0 + (hx - x0) * bk, 1300), 20, 20, P(color=col('#ffd23f')))
        if bk > 0.3:
            c.drawRoundRect(skia.Rect(hx, 1340, hx + (800 - (hx - x0)) * ease_out(prog(t, t1, 0.8)), 1420), 20, 20, P(color=col(CALL)))
        if bk > 0.5:
            c.drawLine(hx, 1200, hx, 1440, P(color=col('#ffffff', 200), stroke=4))
            label_pill(c, '20 kHz', hx, 1480, size=30, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY)
        label_pill(c, 'YOU hear this', x0 + 150, 1170, size=36, k=ease_back(prog(t, t1, 0.4)), fill=NAVY, hi='#e0a800')
        label_pill(c, 'BAT calls', hx + 400, 1480, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#1fa8c9')

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'sparkle'), (t0 + 0.8, 'pop'), (t1 - 0.4, 'whoosh'), (t1, 'pop'), (t1 + 0.6, 'pop')]

# ---------- 3: Sound bounces back as an echo ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night(c, t)
    ground(c, t)
    tree(c, 790, 1560, 2.4, t, dark=True)
    bx, by = 230, 1030 + 25 * math.sin(t * 2)
    bat(c, bx, by, 0.8, t)
    # outgoing call -> hits tree -> echo returns
    for k in range(4):
        st = t0 + 0.3 + k * 1.6
        tt = t - st
        if tt < 0: continue
        u = tt / 1.0
        if u < 1:
            r = lerp(60, 520, u)
            pth = skia.Path(); pth.addArc(skia.Rect(bx - r, by - r, bx + r, by + r), -25, 50)
            c.drawPath(pth, P(color=col(CALL, int(230 * (1 - 0.3 * u))), stroke=14))
        elif u < 2:
            v = u - 1; ex = 780; r = lerp(40, 520, v)
            pth = skia.Path(); pth.addArc(skia.Rect(ex - r, by - r, ex + r, by + r), 155, 50)
            c.drawPath(pth, P(color=col(ECHO, int(230 * (1 - 0.6 * v))), stroke=14))
    label_pill(c, 'CALL', 420, 860, size=42, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi='#1fa8c9')
    if t > t1 - 0.3:
        label_pill(c, 'ECHO', 560, 1250, size=42, k=ease_back(prog(t, t1 - 0.3, 0.4)), fill=NAVY, hi=ECHO)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.5, 'pop'), (t0 + 1.3, 'boing'), (t1 - 0.3, 'pop')]

# ---------- 4: Echo delay = distance ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_sky(c, t, y1=1500)
    bat(c, 180, 1100 + 20 * math.sin(t * 2), 0.65, t)
    # near moth (top lane) and far tree (bottom lane)
    lanes = [(900, 470, 0.35, 'CLOSE: fast echo', 960), (1290, 920, 0.75, 'FAR: slow echo', 1290)]
    k1 = ease_back(prog(t, t0 + 0.3, 0.4))
    moth(c, 470, 940, 0.55 * k1, t)
    k2 = ease_back(prog(t, t0 + 0.6, 0.4))
    if k2 > 0: tree(c, 880, 1540, 1.5 * k2, t, dark=True)
    period = 2.2
    for (ly, ox, dur, lab, py) in lanes:
        pass
    tt = ((t - t0 - 0.8) % period) if t > t0 + 0.8 else -1
    if tt >= 0:
        for oy, ox, dur, yy in ((940, 470, 0.35, 940), (1330, 900, 0.75, 1330)):
            x0 = 240
            if tt < dur:
                x = lerp(x0, ox - 60, tt / dur); c.drawCircle(x, lerp(1100, yy, tt / dur), 13, P(color=col(CALL)))
            elif tt < 2 * dur:
                x = lerp(ox - 60, x0, (tt - dur) / dur); c.drawCircle(x, lerp(yy, 1100, (tt - dur) / dur), 13, P(color=col(ECHO)))
    sk = ease_back(prog(t, t1 - 0.2, 0.4))
    if sk > 0:
        frac_near = min(0.3, ((t - t1) % period) / period) if t > t1 else 0
        stopwatch(c, 700, 800, 80 * sk, 0.18 if t > t1 + 0.5 else frac_near, label=None)
        stopwatch(c, 700, 1180, 80 * sk, 0.42 if t > t1 + 1.2 else min(0.42, max(0, t - t1) * 0.35), label=None)
        label_pill(c, 'CLOSE', 700, 920, size=36, k=sk, fill=NAVY, hi='#1fa8c9')
        label_pill(c, 'FAR', 700, 1300, size=36, k=sk, fill=NAVY, hi=ECHO)
    label_pill(c, 'TIME = distance', 540, 1600, size=44, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#ffd23f')

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 0.6, 'pop'), (t0 + 1.4, 'click'), (t1 - 0.2, 'pop'), (t1 + 0.5, 'click')]

# ---------- 5: A picture made of sound (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#060a24', '#141a4a')
    # sonar grid
    for r in range(1, 6):
        c.drawCircle(540, 1150, r * 110, P(color=col(CALL, 40), stroke=3))
    sw = (t * 1.2) % (2 * math.pi)
    c.drawLine(540, 1150, 540 + math.cos(sw) * 560, 1150 + math.sin(sw) * 560, P(color=col(CALL, 90), stroke=6))
    k = ease_in_out(prog(t, t0 + 0.4, max(1.5, t1 - t0)))
    echo_map(c, MOTH_PTS, 540, 1150, 2.6, k)
    if t > t1:
        mk = ease_out(prog(t, t1 + 0.3, 0.8))
        moth(c, 540, 1150, 2.2, t, flap=6, alpha=int(200 * mk))
        label_pill(c, 'SIZE  SHAPE  DIRECTION', 540, 1580, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#1fa8c9')
    label_pill(c, 'a picture of SOUND', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi='#1fa8c9')

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'sparkle'), (t0 + 1.2, 'ding'), (t1 + 0.3, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 6: Feeding buzz: up to ~200 calls per second ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night(c, t)
    u = ease_in_out(prog(t, t0, t1 - t0 + 2.0))
    mx = 760 + 80 * math.sin(t * 2.6); my = 1050 + 60 * math.sin(t * 3.4)
    bx = lerp(180, mx - 220, u); by = lerp(1300, my + 40, u)
    moth(c, mx, my, 0.55, t, rot=0.3 * math.sin(t * 3))
    bat(c, bx, by, 0.85, t, flap_speed=12)
    rate = int(lerp(10, 200, ease_in_out(prog(t, t0 + 0.4, t1 - t0 + 1.2))))
    per = max(0.06, 1.0 / (2 + rate / 12))
    nrings = 10
    last = (t - t0) // per if t > t0 else 0
    for k in range(nrings):
        st = t0 + (last - k) * per
        if st < t0: continue
        sound_rings(c, bx + 50, by - 10, t, st, n=1, colr=CALL, both=False, a0=-30, sweep=60, speed=600, life=0.5, w=8)
    kk = ease_back(prog(t, t0 + 0.4, 0.4))
    if kk > 0:
        c.save(); c.translate(540, 760); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-250, -62, 250, 62), 31, 31, P(color=col('#ffffff', 235)))
        text_block(c, f'{rate} calls/sec', 0, 0, size=56, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    if t > t1:
        label_pill(c, 'FEEDING buzz', 540, 1560, size=46, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=ECHO)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.4, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 0.5, 'pop')]

# ---------- 7: Wild part: 140 dB, louder than a rock concert ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1a1f5c', '#3b3f8f')
    stars(c, t, 5, 60, y1=1500)
    # decibel meter
    x0, x1, y = 160, 920, 1150
    lvl = ease_out(prog(t, t0 + 0.6, 2.4))
    c.drawRoundRect(skia.Rect(x0, y - 50, x1, y + 50), 50, 50, P(color=col('#ffffff', 50)))
    fillx = lerp(x0, x1, lvl * 140 / 150)
    c.save(); cl = skia.Path(); cl.addRoundRect(skia.Rect(x0, y - 50, x1, y + 50), 50, 50); c.clipPath(cl, doAntiAlias=True)
    c.drawRect(skia.Rect(x0, y - 50, fillx, y + 50), lin(c, (x0, 0, x1, 0), [col('#3fbf6a'), col('#ffd23f'), col(ECHO)]))
    c.restore()
    for db, lab, yy in ((60, 'talking 60', 1260), (110, 'rock concert 110+', 1040)):
        xx = lerp(x0, x1, db / 150)
        c.drawLine(xx, y - 70, xx, y + 70, P(color=col('#ffffff', 220), stroke=5))
        label_pill(c, lab, min(max(xx, 250), 830), yy, size=32, k=ease_back(prog(t, t0 + 0.4 + db / 200, 0.4)), fill=NAVY)
    kk = ease_back(prog(t, t0 + 2.8, 0.5), 2.2)
    if kk > 0:
        c.save(); c.translate(540, 800); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-200, -66, 200, 66), 33, 33, P(color=col(ECHO)))
        text_block(c, 'BAT: 140 dB', 0, 0, size=56, fill='#ffffff', hi='#ffffff', stroke='#b8183f')
        c.restore()
    bat(c, 820, 1440, 0.6, t)
    if t > t1:
        mk = ease_back(prog(t, t1 + 0.4, 0.4))
        if mk > 0:
            c.save(); c.translate(320, 1440); c.scale(mk, mk)
            # speaker-with-cross icon = "we hear nothing"
            p = skia.Path(); p.moveTo(-60, -25); p.lineTo(-30, -25); p.lineTo(5, -60); p.lineTo(5, 60); p.lineTo(-30, 25); p.lineTo(-60, 25); p.close()
            c.drawPath(p, P(color=col('#ffffff')))
            c.drawLine(30, -30, 80, 30, P(color=col(ECHO), stroke=12)); c.drawLine(80, -30, 30, 30, P(color=col(ECHO), stroke=12))
            c.restore()
            label_pill(c, 'SILENT to us', 320, 1580, size=38, k=mk, fill=NAVY, hi=ECHO)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 0.7, 'pop'), (t0 + 0.95, 'pop'), (t0 + 2.8, 'boing'), (t1 + 0.4, 'click')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night(c, t)
    bx = 540 + 200 * math.sin(t * 0.8); by = 1150 + 60 * math.sin(t * 1.6)
    bat(c, bx, by, 0.9, t)
    sound_rings(c, bx + 60, by, t, math.floor(t / 1.2) * 1.2, n=3, colr=CALL, both=False, a0=-30, sweep=60)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: EARTHQUAKES', 540, 720, size=48, k=kk, fill=NAVY, hi='#c9792b')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do bats find their way in the dark?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do bats fly in total darkness?', 'How do BATS fly in the dark?'),
            ("They're not blind. They see with sound.", 'They see with SOUND')], tail=0.8),
        dict(name='calls', draw=s2, sfx_fn=s2_sfx, lines=[
            ('A bat shouts out very high-pitched calls,', 'Very HIGH-pitched calls'),
            ('far too high for human ears to hear.', 'Too high for HUMAN ears')], tail=0.9),
        dict(name='echo', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The sound hits a tree or an insect,', 'The sound HITS something'),
            ('and bounces back as an echo, like a ball off a wall.', 'and bounces back: ECHO')], tail=0.8),
        dict(name='timing', draw=s4, sfx_fn=s4_sfx, lines=[
            ('The longer the echo takes to come back, the farther away the object is.', 'Longer echo = FARTHER away'),
            ('A quick echo means close. A slow one means far.', 'QUICK = close, SLOW = far')], tail=1.0),
        dict(name='picture', draw=s5, sfx_fn=s5_sfx, lines=[
            ("From all those echoes, the bat's brain builds a picture made of sound.", 'A picture made of SOUND'),
            ('It can tell an insect\'s size, shape, and which way it is flying.', 'SIZE, shape, direction')], tail=1.2),
        dict(name='buzz', draw=s6, sfx_fn=s6_sfx, lines=[
            ('When a bat closes in on a moth, it calls faster and faster,', 'Faster and FASTER'),
            ('up to about two hundred calls per second. That is called a feeding buzz.', 'Up to 200 calls per SECOND')], tail=0.9),
        dict(name='loud', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: some bats call at up to one hundred forty decibels, louder than a rock concert.", 'LOUDER than a rock concert'),
            ('We just never hear it, because the pitch is too high.', 'And we hear NOTHING')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So bats find their way by shouting and listening to the echoes.', 'Shout, then LISTEN'),
            ('Next up: how earthquakes happen.', 'Next: how EARTHQUAKES happen'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
