"""Episode 38 (EN, general audience): Why do things fall down?
Facts checked (NASA "The Apollo 15 Hammer-Feather Drop" + NSSDC page, NASA APOD 2011-11-01, Britannica "Newton's law of
gravitation", National Academies "One Universe: motion", NASA/Glenn "Newton's cannon / orbits"):
- Every object with mass attracts every other object (Newton's law of universal gravitation). The pull between
  everyday objects is tiny; it only becomes strong for huge masses like Earth.
- Earth pulls everything toward its centre - "down" means toward the centre of Earth, everywhere on the globe.
- Near the surface, falling objects accelerate at ~9.8 m/s^2: about 10 m/s faster every second (air resistance
  ignored). 0 -> 60 mph (26.8 m/s) takes ~2.7 s of free fall.
- Without air, all objects fall at the same rate regardless of mass (Galileo). A feather falls slowly on Earth only
  because of air resistance.
- Apollo 15, 2 Aug 1971: on the Moon (no air) a hammer and a falcon feather were dropped together and hit the
  ground at the same time.
- The Moon is in free fall around Earth: it constantly falls toward Earth but moves sideways (~1 km/s) fast enough
  that it keeps missing (Newton's cannonball idea of an orbit).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def soft_bg(c, t, top='#eef6ff', bot='#d6e9fb'):
    sky(c, top, bot); dust(c, t, seed=8, n=10, a=60)

def ground(c, y=1500, colr='#7ed957', dark='#56b83a'):
    c.drawRect(skia.Rect(-20, y, W + 20, H), lin(c, (0, y, 0, y + 200), [col(colr), col(dark)]))
    c.drawLine(-20, y, W + 20, y, P(color=col('#ffffff', 90), stroke=4))

def pull_arrows(c, cx, cy, r, t, n=10, k=1.0, colr=SKYB, inner=None):
    """Arrows pointing inward to the centre from all around a globe."""
    for i in range(n):
        a = 2 * math.pi * i / n + 0.2
        pulse = (t * 0.8 + i * 0.13) % 1.0
        r0 = r + 230 - 60 * pulse; r1 = (inner or r + 40)
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        x1, y1 = cx + math.cos(a) * r1, cy + math.sin(a) * r1
        arrow(c, x0, y0, x1, y1, colr=colr, w=12, alpha=int(230 * k))

# ---------- 1: Hook (cold open: apple already falling) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    soft_bg(c, t)
    ground(c)
    # apple falls on loop, accelerating (y = 0.5 g t^2 scaled)
    period = 1.3
    ph = t % period
    y = 640 + 0.5 * 980 * ph * ph * 0.95
    land = y >= 1440
    yy = min(y, 1440)
    squash = 0.0
    if land: squash = max(0.0, 1 - (y - 1440) / 260)
    for k in range(1, 5):  # motion ghosts
        tp = ph - k * 0.06
        if tp > 0 and not land:
            gy = 640 + 0.5 * 980 * tp * tp * 0.95
            apple(c, 540, gy, 60, alpha=60 - k * 12)
    c.save(); c.translate(540, yy + 60); c.scale(1 + 0.12 * squash, 1 - 0.1 * squash); apple(c, 0, -60, 60); c.restore()
    if land:
        c.drawOval(skia.Rect(470, 1492, 610, 1512), P(color=col('#000000', 40), blur=6))
    # pull arrow from the ground
    pk = prog(t, 0.4, 0.5)
    arrow(c, 860, 900, 860, 1380, colr=SKYB, w=22, alpha=int(240 * pk))
    label_pill(c, 'EARTH pulls', 770, 820, size=44, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'on YOU too', 300, 1620, size=42, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    return [(0.0, 'whoosh'), (0.3, 'pop'), (1.25, 'boing'), (cues[1]['start'] + 1.0, 'pop')]

# ---------- 2: Every mass pulls, but only huge masses pull hard ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # two balls drift very slightly together with tiny arrows
    k = ease_back(prog(t, t0, 0.5))
    drift = 18 * prog(t, t0 + 0.6, 4.0)
    if t < t1 + 0.3:
        fo = 1 - prog(t, t1, 0.3)
        c.saveLayerAlpha(None, int(255 * fo))
        ball(c, 300 + drift, 1080, 90 * k, colr=HOT)
        apple(c, 780 - drift, 1080, 80 * k)
        ak = prog(t, t0 + 0.8, 0.4)
        arrow(c, 410 + drift, 1080, 455 + drift, 1080, colr=NAVY, w=8, alpha=int(255 * ak))
        arrow(c, 670 - drift, 1080, 625 - drift, 1080, colr=NAVY, w=8, alpha=int(255 * ak))
        label_pill(c, 'tiny PULL', 540, 1260, size=40, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, 'even an APPLE pulls', 540, 760, size=46, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
        c.restore()
    if t > t1:
        ek = ease_out(prog(t, t1 + 0.1, 0.8))
        r = lerp(40, 360, ek)
        earth(c, 540, 1500 + (1 - ek) * 300, r, t, rot=t * 0.02, face_on=False)
        ak2 = prog(t, t1 + 0.9, 0.4)
        apple(c, 540, 1000 + 40 * math.sin(t * 2), 60, alpha=int(255 * ak2))
        arrow(c, 540, 1070, 540, 1110 + 30 * ak2, colr=SKYB, w=22, alpha=int(255 * ak2))
        label_pill(c, 'HUGE mass = big pull', 540, 760, size=46, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'pop'), (t0 + 0.8, 'click'), (t0 + 1.6, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 0.9, 'pop')]

# ---------- 3: Down = toward the centre ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#0b1030', bot='#1c2145')
    stars(c, t, seed=4, n=70, y0=600, y1=1800)
    cx, cy, r = 540, 1120, 260
    earth(c, cx, cy, r, t, rot=t * 0.03, face_on=False)
    pull_arrows(c, cx, cy, r, t, n=8, k=prog(t, t0 + 0.3, 0.5))
    # centre dot
    dk = ease_back(prog(t, t0 + 1.0, 0.4))
    c.drawCircle(cx, cy, 14 * dk, P(color=col('#ffd23f')))
    c.drawCircle(cx, cy, 14 * dk, P(color=col(NAVY), stroke=4))
    label_pill(c, 'DOWN = toward the center', 540, 700, size=42, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        # apples around the globe all fall toward the centre
        for i, ang in enumerate((-60, 30, 150, 250)):
            a = math.radians(ang)
            u = ((t - t1) * 0.7 + i * 0.25) % 1.0
            dist = lerp(r + 190, r + 40, u * u)
            ak = prog(t, t1 + 0.2 + i * 0.25, 0.3)
            apple(c, cx + math.cos(a) * dist, cy + math.sin(a) * dist, 34, rot=ang + 90, alpha=int(255 * ak))
        label_pill(c, 'nobody falls OFF', 540, 1520, size=42, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=HOT)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'click'), (t1 + 0.2, 'pop'), (t1 + 0.7, 'pop'), (t1 + 1.2, 'pop')]

# ---------- 4: Speeds up ~10 m/s every second ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # strobe picture: ball positions after 0, 1, 2, 3 "ticks" (distances 1:3:5)
    x = 330; y0 = 650; unit = 90
    for i in range(4):
        k = ease_back(prog(t, t0 + 0.4 + i * 0.6, 0.35))
        yy = y0 + unit * (i * i) * 1.0
        if k > 0:
            ball(c, x, yy, 42 * k, colr=HOT, alpha=255 if i == 3 else 150)
            if i > 0:
                label_pill(c, f'{i * 10} m/s', x + 230, yy, size=38, k=k, fill=NAVY, hi=SKYB)
            else:
                label_pill(c, '0 m/s', x + 230, yy, size=38, k=k, fill=NAVY)
        if i > 0 and k > 0:
            ya = y0 + unit * ((i - 1) ** 2)
            c.drawLine(x - 90, ya, x - 90, yy, P(color=col(SKYB, int(200 * min(1, k))), stroke=8))
            c.drawLine(x - 105, yy, x - 75, yy, P(color=col(SKYB, int(200 * min(1, k))), stroke=6))
    label_pill(c, '+10 m/s EVERY second', 540, 1560, size=42, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        # speedometer: 0 -> 60 mph in under 3 s
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        c.save(); c.translate(790, 1150); c.scale(k, k)
        c.drawCircle(0, 0, 150, P(color=col('#ffffff', 240)))
        c.drawCircle(0, 0, 150, P(color=col(NAVY), stroke=8))
        for i in range(7):
            a = math.radians(150 + i * 40)
            c.drawLine(math.cos(a) * 118, math.sin(a) * 118, math.cos(a) * 138, math.sin(a) * 138, P(color=col(NAVY), stroke=6))
        frac = ease_in_out(prog(t, t1 + 0.6, 2.4))
        a = math.radians(150 + 240 * frac)
        c.drawLine(0, 0, math.cos(a) * 110, math.sin(a) * 110, P(color=col(HOT), stroke=10))
        c.drawCircle(0, 0, 16, P(color=col(NAVY)))
        text_block(c, f'{int(60 * frac)} mph', 0, 80, size=40, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
        label_pill(c, 'in under 3 SECONDS', 790, 1370, size=36, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4 + i * 0.6, 'click') for i in range(4)] + [(t0 + 2.6, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.6, 'whoosh')]

# ---------- 5: Heavy vs light: same fall without air (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    ground(c, 1500)
    # left half: in air (feather drifts) ; right half: no air (both drop together) - shown after t1
    def drop(tt, fall_time=1.3):
        u = clamp(tt / fall_time)
        return lerp(700, 1440, u * u)
    T = (t - t0 - 0.5) % 3.4
    vac = t > t1 + 0.2
    hx = 380; fx = 700
    hy = drop(T)
    if not vac:
        fy = lerp(720, 1440, clamp(T / 3.2))
        fsw = math.sin(T * 3.5) * 40
        label_pill(c, 'with AIR', 540, 1640, size=40, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi=SKYB)
        for i in range(6):
            yy = 760 + i * 120 + ((t * 60) % 120)
            c.drawCircle(150 + (i * 137) % 780, yy, 6, P(color=col('#9fc6ee', 180)))
    else:
        T2 = (t - t1 - 0.2) % 2.4
        hy = drop(T2, 1.3); fy = hy; fsw = 0
        c.drawRoundRect(skia.Rect(160, 650, 920, 1470), 30, 30, P(color=col('#1b2a4a', 30)))
        c.drawRoundRect(skia.Rect(160, 650, 920, 1470), 30, 30, P(color=col(NAVY, 160), stroke=6))
        label_pill(c, 'NO air', 540, 1640, size=44, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=HOT)
        if hy >= 1430:
            label_pill(c, 'SAME time', 540, 760, size=48, k=ease_back(prog(T2, 1.3, 0.3)), fill=NAVY, hi=GOLD)
    hammer(c, hx, min(hy, 1440) - 60, 0.75, rot=-90 + (0 if vac else 5 * math.sin(t)))
    quill(c, fx + fsw, min(fy, 1440) - 90, 0.75, rot=70 + 25 * math.sin(t * 2.2) * (0 if vac else 1))
    label_pill(c, 'HEAVY', hx, 640 if not vac else 600, size=36, k=ease_back(prog(t, t0 + 0.2, 0.4)) * (0 if vac else 1), fill=NAVY, hi=HOT)
    label_pill(c, 'LIGHT', fx, 640, size=36, k=ease_back(prog(t, t0 + 0.2, 0.4)) * (0 if vac else 1), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.5, 'whoosh'), (t1 + 0.2, 'whoosh'), (t1 + 1.5, 'ding')]

# ---------- 6: Apollo 15 on the Moon ----------
def moon_ground(c, y=1420):
    p = skia.Path(); p.moveTo(-20, y)
    for i in range(12):
        x = i * 100; p.quadTo(x + 50, y - 18 * math.sin(i * 1.7), x + 100, y)
    p.lineTo(W + 20, H); p.lineTo(-20, H); p.close()
    c.drawPath(p, lin(c, (0, y - 20, 0, y + 400), [col('#b9b9bd'), col('#7a7b80')]))
    rnd = random.Random(3)
    for i in range(10):
        cx, cy, rr = rnd.uniform(40, 1000), rnd.uniform(y + 40, y + 420), rnd.uniform(14, 40)
        c.drawOval(skia.Rect(cx - rr, cy - rr * 0.35, cx + rr, cy + rr * 0.35), P(color=col('#6a6b70', 160)))

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#03040b', '#141832'); stars(c, t, seed=6, n=80, y1=1400)
    earth(c, 170, 1020, 60, t, rot=t * 0.02, face_on=False, sun_dir=200, night=0.5)
    moon_ground(c)
    label_pill(c, '1971: on the MOON', 400, 700, size=44, k=ease_back(prog(t, t0 + 0.2, 0.4)), fill=NAVY, hi=SKYB)
    # slow lunar fall (1/6 g) synced to second line
    start = t1 + 0.1
    u = clamp((t - start) / 1.9)
    y = lerp(860, 1370, u * u) if t > start else 860
    hammer(c, 420, y - 40, 0.7, rot=-90)
    quill(c, 660, y - 70, 0.7, rot=75)
    if u >= 1:
        dk = prog(t, start + 1.9, 0.6)
        for x in (420, 660):
            c.drawOval(skia.Rect(x - 90 * dk - 20, 1395, x + 90 * dk + 20, 1425), P(color=col('#d0d0d4', int(160 * (1 - dk))), blur=8))
        label_pill(c, 'TOGETHER', 540, 1560, size=48, k=ease_back(prog(t, start + 1.9, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'no air = no drag', 540, 1690, size=34, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SKYB)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.2, 'pop'), (t1 + 0.3, 'pop'), (t1 + 2.0, 'click'), (t1 + 2.0, 'pop')]

# ---------- 7: Wild part: the Moon is falling too ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#03040b', '#1c2145'); stars(c, t, seed=21, n=110, y0=600, y1=1800)
    cx, cy = 480, 1130
    earth(c, cx, cy, 150, t, rot=t * 0.05, face_on=False)
    R = 360
    # orbit trace
    ok = prog(t, t0 + 0.3, 0.6)
    c.drawCircle(cx, cy, R, P(color=col('#ffffff', int(60 * ok)), stroke=4))
    ang = -60 + (t - t0) * 22
    a = math.radians(ang)
    mx, my = cx + math.cos(a) * R, cy + math.sin(a) * R
    gray_moon(c, mx, my, 50, t)
    # fall arrow (to Earth) and sideways arrow
    fk = prog(t, t0 + 0.8, 0.4)
    arrow(c, mx - math.cos(a) * 60, my - math.sin(a) * 60, mx - math.cos(a) * 170, my - math.sin(a) * 170, colr=HOT, w=14, alpha=int(255 * fk))
    if t > t1:
        sk = prog(t, t1 + 0.2, 0.4)
        tx, ty = -math.sin(a), math.cos(a)
        arrow(c, mx + tx * 60, my + ty * 60, mx + tx * 200, my + ty * 200, colr='#ffd23f', w=14, alpha=int(255 * sk))
        label_pill(c, 'sideways: ~1 KM per second', 540, 1650, size=36, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'it keeps MISSING', 540, 1560, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'FALLING right now', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.4, 'pop'), (t1 + 1.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    soft_bg(c, t)
    cx, cy, r = 540, 1150, 230
    earth(c, cx, cy, r, t, rot=t * 0.03, face_on=False)
    pull_arrows(c, cx, cy, r, t, n=8, k=0.9)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: how WHALES breathe', 540, 700, size=44, k=kk, fill=NAVY, hi=SKYB)
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do things fall down?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do things fall down?', 'Why do things FALL?'),
            ('Because the entire planet is pulling on you, right now.', 'The whole PLANET pulls on you')], tail=0.8),
        dict(name='mass', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Everything with mass pulls on everything else. Even this apple pulls on that ball.', 'Every MASS pulls'),
            ("But the pull is tiny unless something is huge. And Earth is huge.", 'Only HUGE things pull hard')], tail=0.8),
        dict(name='center', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Earth pulls everything toward its center. That is what down really means.', 'DOWN = toward the center'),
            ("That's why nobody on the other side of the planet falls off.", 'Nobody falls OFF')], tail=0.8),
        dict(name='speed', draw=s4, sfx_fn=s4_sfx, lines=[
            ('A falling object speeds up by about ten meters per second, every second.', 'FASTER every second'),
            ("That's zero to sixty miles an hour in under three seconds.", '0 to 60 in under 3 SECONDS')], tail=0.8),
        dict(name='same', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('So does a hammer fall faster than a feather? Only because of the air.', 'Heavy vs light? It is the AIR'),
            ('Take the air away, and everything falls at exactly the same speed.', 'No air: SAME speed')], tail=1.2),
        dict(name='moon_test', draw=s6, sfx_fn=s6_sfx, lines=[
            ('In 1971, astronauts tested it on the Moon, with a hammer and a feather.', '1971: tested on the MOON'),
            ('No air up there, so both hit the ground at the same moment.', 'They landed TOGETHER')], tail=1.2),
        dict(name='moon_falls', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: the Moon is falling toward Earth right now.", 'The MOON is falling too'),
            ('It just moves sideways so fast, about a kilometer every second, that it keeps missing.', 'It keeps MISSING')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So things fall because Earth pulls everything toward its center.', 'Earth PULLS everything'),
            ('Next: how whales breathe.', 'Next: how WHALES breathe'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
