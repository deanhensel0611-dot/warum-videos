"""Episode 43 (EN, general audience): How do ants find their way home?
Facts checked (Wittlinger, Wehner & Wolf 2006 Science "The ant odometer: stepping on stilts and stumps";
Wittlinger et al. 2007 J Exp Biol "The desert ant odometer: a stride integrator..."; Wehner 2003/2020 reviews on
Cataglyphis path integration and the polarized-light compass (J Comp Physiol A); Deneubourg et al. 1990 double-bridge
experiments on pheromone trails; Britannica "ant"):
- Many ant species lay chemical (pheromone) trails; nestmates follow them and reinforce them, so busy/short routes
  get stronger and the shortest route usually wins.
- Desert ants (Cataglyphis, e.g. in the Sahara) forage alone on hot sand without scent trails. They search on winding
  paths, then return in a straight line to the nest: path integration (like a sailor's dead reckoning).
- Direction: a sky compass using the Sun and the pattern of polarized skylight.
- Distance: they count/integrate their steps (stride integrator).
- Stilts experiment: ants with stilts (bristles glued to their legs) overshot the nest on the way back; ants with
  shortened legs undershot -> they really measure distance with their steps.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
ANT = '#4a2a1a'
SCENT = '#7be08a'

def desert(c, t, horizon=760, shimmer=True):
    sky(c, '#6fbcff', '#d6eeff')
    c.drawCircle(860, 330, 200, rad(860, 330, 200, [col('#fff6b0', 160), col('#fff6b0', 0)]))
    p = skia.Path(); p.moveTo(-20, horizon + 40); p.cubicTo(250, horizon - 40, 520, horizon + 30, 760, horizon - 10)
    p.cubicTo(900, horizon - 30, 1000, horizon + 10, W + 20, horizon); p.lineTo(W + 20, H); p.lineTo(-20, H); p.close()
    c.drawPath(p, lin(c, (0, horizon - 40, 0, H), [col('#f6d79a'), col('#ecc27a'), col('#d9a85e')], pos=[0, 0.4, 1]))
    rnd = random.Random(3)
    for i in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(horizon + 60, H)
        c.drawCircle(x, y, rnd.uniform(1.5, 3.5), P(color=col('#c99a52', 160)))
    if shimmer:
        for i in range(4):
            yy = horizon + 30 + i * 22
            p2 = skia.Path(); p2.moveTo(0, yy)
            for xx in range(0, W + 40, 40):
                p2.lineTo(xx, yy + math.sin(xx * 0.03 + t * 4 + i) * 5)
            c.drawPath(p2, P(color=col('#ffffff', 50), stroke=3))

def nest(c, x, y, s=1.0):
    c.drawOval(skia.Rect(x - 70 * s, y - 24 * s, x + 70 * s, y + 24 * s), P(color=col('#c99a52')))
    c.drawOval(skia.Rect(x - 70 * s, y - 24 * s, x + 70 * s, y + 24 * s), P(color=col('#a87a3a'), stroke=6 * s))
    c.drawOval(skia.Rect(x - 28 * s, y - 11 * s, x + 28 * s, y + 11 * s), P(color=col('#3a2412')))

def crumb(c, x, y, s=1.0):
    p = skia.Path(); p.moveTo(x - 26 * s, y + 10 * s); p.lineTo(x - 18 * s, y - 16 * s); p.lineTo(x + 10 * s, y - 22 * s)
    p.lineTo(x + 28 * s, y - 2 * s); p.lineTo(x + 16 * s, y + 18 * s); p.close()
    c.drawPath(p, lin(c, (0, y - 22 * s, 0, y + 18 * s), [col('#ffe7a8'), col('#e9b55a')]))
    c.drawPath(p, P(color=col('#b07a2a'), stroke=4 * s))

def polyline_at(pts, u):
    """Point and heading at fraction u along a polyline."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    L = sum(segs); d = clamp(u) * L
    for (a, b), sl in zip(zip(pts, pts[1:]), segs):
        if d <= sl or sl == segs[-1]:
            f = d / sl if sl > 0 else 0
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        d -= sl
    return pts[-1][0], pts[-1][1], 0

def draw_partial(c, pts, u, paint):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    seg = skia.Path(); m = skia.PathMeasure(p, False); m.getSegment(0, m.getLength() * clamp(u), seg, True)
    c.drawPath(seg, paint)

NEST = (540, 1460)
FOOD = (330, 820)
def zigzag_pts():
    rnd = random.Random(8); pts = [NEST]; x, y = NEST
    for i in range(1, 12):
        f = i / 11
        x = lerp(NEST[0], FOOD[0], f) + (rnd.uniform(-170, 170) if i < 11 else 0)
        y = lerp(NEST[1], FOOD[1], f) + (rnd.uniform(-60, 60) if i < 11 else 0)
        pts.append((clamp(x, 140, 900), y))
    return pts
ZZ = zigzag_pts()

def dashed(c, x0, y0, x1, y1, colr, w=8, alpha=255, dash=26):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap, Color=col(colr, alpha),
                   PathEffect=skia.DashPathEffect.Make([dash, dash * 0.8], 0))
    c.drawLine(x0, y0, x1, y1, p)

# ---------- 1: Hook (cold open: ant already zigzagging) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    desert(c, t, horizon=640)
    nest(c, *NEST)
    crumb(c, *FOOD, s=1.2)
    u = prog(t, -0.6, t1 + 0.6)
    draw_partial(c, ZZ, u, P(color=col(HOT, 200), stroke=7))
    if t < t1 + 0.6:
        x, y, h = polyline_at(ZZ, u)
        ant(c, x, y, 1.5, t, rot=h, colr=ANT)
    else:
        v = ease_in_out(prog(t, t1 + 0.8, 1.8))
        dashed(c, FOOD[0], FOOD[1], lerp(FOOD[0], NEST[0], v), lerp(FOOD[1], NEST[1], v), NAVY, w=9)
        h = math.degrees(math.atan2(NEST[1] - FOOD[1], NEST[0] - FOOD[0]))
        ant(c, lerp(FOOD[0], NEST[0], v), lerp(FOOD[1], NEST[1], v), 1.5, t, rot=h, colr=ANT, walk=1.0 if v < 1 else 0)
        crumb(c, lerp(FOOD[0], NEST[0], v) + math.cos(math.radians(h)) * 70, lerp(FOOD[1], NEST[1], v) + math.sin(math.radians(h)) * 70, s=0.5)
        label_pill(c, 'STRAIGHT back', 760, 1120, size=44, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'ZIGZAG out', 760, 900, size=44, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.3, 'pop'), (t1 + 0.8, 'whoosh'), (t1 + 1.0, 'pop')]

# ---------- 2: Scent trails; the shortest route wins ----------
def forest_floor(c):
    sky(c, '#8bc47a', '#5e9a55')
    rnd = random.Random(2)
    for i in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(620, H)
        leaf(c, x, y, rnd.uniform(0.25, 0.45), 0, colr=mix_hx('#6fae5a', '#a8c46a', rnd.random()), seed=i, face_on=False, rot=rnd.uniform(0, 360), alpha=150)

def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    forest_floor(c)
    A, B = (540, 1500), (540, 700)
    nest(c, *A)
    crumb(c, B[0], B[1], s=1.3)
    short = [A, (430, 1300), (400, 1100), (430, 900), B]
    long_ = [A, (720, 1380), (880, 1150), (850, 900), (700, 760), B]
    if t < t1:
        k = prog(t, t0, 3.0)
        draw_partial(c, short, k, P(color=col(SCENT, 180), stroke=22, blur=6))
        for i in range(5):
            u = ((t - t0) * 0.22 + i * 0.2) % 1.0
            if u < k:
                x, y, h = polyline_at(short, u); ant(c, x, y, 0.8, t + i, rot=h, colr=ANT)
        label_pill(c, 'SCENT trail', 760, 1180, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#2f9a4a')
    else:
        u2 = t - t1
        sk = 0.5 + 0.5 * ease_out(prog(t, t1, 3.0)); lk = 0.6 - 0.45 * ease_out(prog(t, t1, 3.0))
        for path, strength in ((long_, lk), (short, sk)):
            c.drawPath(_path_of(path), P(color=col(SCENT, int(230 * strength)), stroke=10 + 26 * strength, blur=6))
        for i in range(8):
            uu = (u2 * 0.25 + i / 8) % 1.0
            x, y, h = polyline_at(short, uu); ant(c, x, y, 0.75, t + i, rot=h, colr=ANT)
        for i in range(2):
            uu = (u2 * 0.15 + i / 2) % 1.0
            x, y, h = polyline_at(long_, uu); ant(c, x, y, 0.75, t + i, rot=h, colr=ANT, alpha=200)
        label_pill(c, 'SHORTEST route wins', 540, 1600, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi='#2f9a4a')

def _path_of(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    return p

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'sparkle'), (t1 + 1.6, 'pop')]

# ---------- 3: Desert ants: no trail; compass + step count ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    desert(c, t)
    sun(c, 860, 330, 70, t)
    x = lerp(200, 640, prog(t, t0, 5.0))
    ant(c, x, 1250, 1.6, t, rot=0, colr=ANT, legs_long=1.15)
    label_pill(c, 'hunts ALONE', 330, 950, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'NO trail', 330, 1070, size=44, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        if k > 0:
            c.save(); c.translate(320, 1480); c.scale(k, k)
            compass(c, 0, 0, 105, -90 + 10 * math.sin(t * 2), t)
            c.restore()
        k2 = ease_back(prog(t, t1 + 1.0, 0.5))
        if k2 > 0:
            c.save(); c.translate(760, 1480); c.scale(k2, k2)
            c.drawRoundRect(skia.Rect(-130, -80, 130, 80), 30, 30, P(color=col('#ffffff')))
            c.drawRoundRect(skia.Rect(-130, -80, 130, 80), 30, 30, P(color=col(NAVY), stroke=6))
            n = int(max(0, t - t1 - 1.0) * 37)
            text_block(c, f'{n:04d}', 0, -6, size=70, fill=NAVY, hi=NAVY, stroke='#ffffff')
            c.restore()
            label_pill(c, 'STEPS', 760, 1610, size=36, k=k2, fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.6, 'pop'), (t1 + 0.2, 'pop'), (t1 + 1.0, 'click')]

# ---------- 4: The sky is the compass (Sun + polarized light) ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f7fe0', '#bfe3ff')
    sx, sy = 700, 900
    pk = ease_out(prog(t, t0 + 1.4, 1.2))
    # polarization pattern: short bars arranged in rings around the Sun, oriented along the rings
    for ring in range(1, 6):
        rr = ring * 130
        n = 10 + ring * 5
        for j in range(n):
            a = 2 * math.pi * j / n + t * 0.05
            x, y = sx + math.cos(a) * rr, sy + math.sin(a) * rr
            if not (0 < x < W - 60 and 620 < y < 1480): continue
            tx, ty = -math.sin(a) * 18, math.cos(a) * 18
            c.drawLine(x - tx, y - ty, x + tx, y + ty, P(color=col('#ffffff', int(200 * pk * (1 - ring * 0.1))), stroke=6))
    sun(c, sx, sy, 80, t)
    # ground strip with the ant looking up
    c.drawRect(skia.Rect(0, 1480, W, H), lin(c, (0, 1480, 0, H), [col('#ecc27a'), col('#d9a85e')]))
    ant(c, 300, 1560, 1.5, t, rot=-60, walk=0.3, colr=ANT, legs_long=1.15)
    arrow(c, 340, 1490, sx - 100, sy + 90, colr='#ffd23f', w=12, alpha=int(230 * prog(t, t0 + 0.5, 0.4)))
    label_pill(c, 'the SUN', sx, sy + 170, size=42, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'POLARIZED light pattern', 540, 700, size=42, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=SKYB)
    if len(cues) > 1 and t > cues[1]['start']:
        label_pill(c, 'works even if the Sun is hidden', 540, 1380, size=34, k=ease_back(prog(t, cues[1]['start'] + 0.3, 0.4)), fill=NAVY, hi=SKYB)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    ev = [(t0 + 0.5, 'pop'), (t0 + 1.4, 'sparkle'), (t0 + 1.6, 'pop')]
    if len(cues) > 1: ev.append((cues[1]['start'] + 0.3, 'pop'))
    return ev

# ---------- 5: Step counting + adding up the route -> home vector ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    desert(c, t, horizon=640, shimmer=False)
    if t < t1 + 0.3:
        fo = 1 - prog(t, t1, 0.3)
        c.saveLayerAlpha(None, int(255 * fo))
        x = lerp(160, 760, prog(t, t0, 4.0))
        ant(c, x, 1120, 2.4, t, rot=0, colr=ANT, legs_long=1.15)
        # footprints with step numbers
        n = int(prog(t, t0, 4.0) * 12)
        for i in range(n):
            fx = 160 + i * 50
            c.drawCircle(fx, 1230 + (i % 2) * 24, 7, P(color=col('#a87a3a')))
            if i % 3 == 2:
                text_block(c, str(i + 1), fx, 1300, size=34, fill=NAVY, stroke='#ffffff')
        label_pill(c, 'built-in STEP counter', 540, 760, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=GOLD)
        c.restore()
    if t > t1:
        nest(c, *NEST)
        u = prog(t, t1 + 0.2, 2.4)
        draw_partial(c, ZZ, u, P(color=col(HOT, 200), stroke=7))
        x, y, h = polyline_at(ZZ, u)
        # live home vector from the ant back to the nest
        if u > 0.02:
            arrow(c, x, y, lerp(x, NEST[0], 0.82), lerp(y, NEST[1], 0.82), colr=SKYB, w=14, alpha=230)
        ant(c, x, y, 1.1, t, rot=h, colr=ANT)
        label_pill(c, 'always knows the way HOME', 540, 720, size=42, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.6, 'click'), (t0 + 2.6, 'click'), (t1 + 0.2, 'whoosh'), (t1 + 0.8, 'pop')]

# ---------- 6: Wild part: stilts make them overshoot (aha) ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    desert(c, t, horizon=640, shimmer=False)
    nx = 500
    for row, (yy, legs, lab, hc) in enumerate(((1020, 1.0, 'normal legs', SKYB), (1380, 1.6, 'on STILTS', HOT))):
        nest(c, nx, yy + 50, 0.9)
        if t > t0 + 0.6:
            label_pill(c, lab, 260, yy - 110, size=46, k=ease_back(prog(t, t0 + 0.6 + row * 0.4, 0.4)), fill=NAVY, hi=hc)
        if t < t1:
            x = 180; walk = 0.0
        else:
            target = nx if row == 0 else nx + 260
            v = ease_out(prog(t, t1 + 0.1, 2.6))
            x = lerp(180, target, v); walk = 1.0 if v < 0.97 else 0.0
        ant(c, x, yy, 1.5, t, rot=0, walk=walk, colr=ANT, legs_long=legs)
    if t > t1 + 2.6:
        label_pill(c, 'walked PAST the nest', 700, 1530, size=44, k=ease_back(prog(t, t1 + 2.6, 0.4)), fill=NAVY, hi=HOT)
    k = ease_back(prog(t, t0 + 0.2, 0.4))
    label_pill(c, 'real EXPERIMENT', 540, 720, size=42, k=k, fill=NAVY, hi=GOLD)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.6, 'pop'), (t0 + 1.0, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 2.6, 'ding')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    desert(c, t)
    nest(c, 540, 1460)
    for i in range(4):
        u = (t * 0.12 + i / 4) % 1.0
        x, y, h = polyline_at([(130, 820), (330, 1050), (540, 1460)], u)
        ant(c, x, y, 0.9, t + i, rot=h, colr=ANT)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.4, 0.4)) * fo
    if k0 > 0: label_pill(c, 'SMELL, SKY + STEPS', 540, 700, size=46, k=k0, fill=NAVY, hi=HOT)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why POPCORN pops', 540, 820, size=42, k=kk, fill=NAVY, hi=GOLD)
        popcorn_kernel(c, 820, 1050, 1.2 * kk, rot=10)
        popcorn_puff(c, 960 - 80, 1180, 0.9, k=kk, seed=3)
    follow_button(c, t, cues[2]['start'], y=1560)

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do ants find their way home?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do ants find their way home?', 'How do ANTS find home?'),
            ('This one zigzags out, then walks a perfectly straight line back.', 'Zigzag out, STRAIGHT back')], tail=1.4),
        dict(name='scent', draw=s2, sfx_fn=s2_sfx, ambience='forest', lines=[
            ('Many ants leave a scent trail that the others can follow.', 'They leave a SCENT trail'),
            ('Busy trails smell stronger, so the shortest route usually wins.', 'SHORTEST route wins')], tail=1.2),
        dict(name='desert', draw=s3, sfx_fn=s3_sfx, lines=[
            ('But desert ants hunt alone on scorching sand, with no trail at all.', 'Desert ants: NO trail'),
            ('So they navigate like old sailors: with a compass and a step count.', 'A COMPASS and a step count')], tail=0.9),
        dict(name='sky', draw=s4, sfx_fn=s4_sfx, lines=[
            ("Their compass is the sky. They read the Sun's position and a pattern of polarized light.", 'The SKY is their compass')], tail=1.0),
        dict(name='steps', draw=s5, sfx_fn=s5_sfx, lines=[
            ('And they count their steps, like a built-in pedometer.', 'A built-in STEP counter'),
            ('Adding up every turn and step, they always know the way home.', 'Always know the way HOME')], tail=1.4),
        dict(name='stilts', draw=s6, sfx_fn=s6_sfx, trans='punch', lines=[
            ("Here's the wild part: scientists glued tiny stilts onto ants' legs.", 'Scientists gave ants STILTS'),
            ('With longer steps, they walked right past their nest. They really count steps!', 'They walked PAST the nest')], tail=1.8),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('So ants find home by smell, or by sky compass and step counting.', 'SMELL, SKY and STEPS'),
            ('Next: why popcorn pops.', 'Next: why POPCORN pops'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
