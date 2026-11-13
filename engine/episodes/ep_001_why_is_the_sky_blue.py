"""Episode 1 (EN): Why is the sky blue?"""
import math, random
from lib import *

def path_pos(pts, u):
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = sum(segs); d = clamp(u) * L
    for i, s in enumerate(segs):
        if d <= s or i == len(segs) - 1:
            k = d / s if s else 0
            return lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k), i
        d -= s

def vel_of(f, t, dt=1 / 60):
    x1, y1 = f(t); x0, y0 = f(t - dt)
    return ((x1 - x0) / dt, (y1 - y0) / dt)

def trail(c, pts_hist, hexcol, width=14):
    for i in range(1, len(pts_hist)):
        a = int(170 * i / len(pts_hist))
        c.drawLine(*pts_hist[i - 1], *pts_hist[i], P(color=col(hexcol, a), stroke=width * i / len(pts_hist)))

RAINBOW = ['#ff4d4d', '#ff9f1c', '#ffe14d', '#4cd964', '#2f80ff', '#8e5cff']
DAY = ('#2f9bff', '#cdeeff')

def day_bg(c, t, seed=1, sunpos=None, trees=True, hy=1600):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    if sunpos: sunbeams(c, sunpos[0], sunpos[1], t, a=28)
    clouds(c, t, seed=seed, n=4)
    birds(c, t, seed=seed + 3, y=560)
    hills(c, hy, t=t, trees=trees)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    day_bg(c, t, 1, sunpos=(540, 1080))
    k = ease_back(prog(t, 0.05, 0.8), 1.4)
    sy = lerp(2150, 1080, k) + math.sin(t * 2) * 10
    sun(c, 540, sy, 200, t, mood='wow' if t < 2.2 else 'happy')
    rnd = random.Random(7)
    for i in range(7):
        ang = i / 7 * 2 * math.pi + t * 0.4; rr = 330 + 30 * math.sin(t * 2 + i)
        x = 540 + math.cos(ang) * rr; y = 1080 + math.sin(ang) * rr * 0.9
        a = prog(t, 0.6 + i * 0.12, 0.35)
        if a > 0:
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=100 + (i % 3) * 18, fill=['#ffffff', '#ffe14d', '#ff8fab'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
            c.restore()
    dust(c, t)

# ---------- 2: White light = all colors ----------
def s2(c, t, D, cues):
    day_bg(c, t + 20, 2, sunpos=(230, 820), trees=False)
    sx, sy = 230, 820; px, py = 640, 1150
    g = ease_in_out(prog(t, cues[0]['start'], 1.1))
    ex, ey = lerp(sx, px, g), lerp(sy, py, g)
    if g > 0:
        c.drawLine(sx, sy, ex, ey, P(color=col('#ffffff', 120), stroke=90, blur=24))
        c.drawLine(sx, sy, ex, ey, P(color=col('#ffffff'), stroke=34))
        for i in range(5):
            u = ((t * 0.8 + i / 5) % 1.0) * g
            c.drawCircle(lerp(sx, px, u), lerp(sy, py, u), 9, P(color=col('#fffbe0'), blur=3))
    sp = ease_out(prog(t, cues[1]['start'], 1.1))
    if sp > 0:
        for i, h in enumerate(RAINBOW):
            d = i * 0.06; s_ = ease_out(prog(t, cues[1]['start'] + d, 1.0))
            ty = 1000 + i * 110; tx = 1150
            bx, by = lerp(px, tx, s_), lerp(py, ty, s_)
            c.drawLine(px, py, bx, by, P(color=col(h, 110), stroke=56, blur=12))
            c.drawLine(px, py, bx, by, P(color=col(h), stroke=26))
            if s_ > 0.95:
                for j in range(3):
                    u = (t * 0.7 + j / 3 + i * 0.1) % 1.0
                    photon(c, lerp(px, tx, u), lerp(py, ty, u), 14, h, t, face_on=False)
    pa = ease_back(prog(t, cues[0]['start'] + 0.5, 0.5))
    if pa > 0:
        c.save(); c.translate(px, py); c.scale(pa, pa); c.rotate(math.sin(t * 1.5) * 3)
        s = 150; pr = skia.Path(); pr.moveTo(0, -s); pr.lineTo(s * 0.9, s * 0.6); pr.lineTo(-s * 0.9, s * 0.6); pr.close()
        c.drawPath(pr, lin(c, (0, -s, 0, s), [col('#ffffff', 220), col('#bfe8ff', 160)]))
        c.drawPath(pr, P(color=col('#ffffff'), stroke=8))
        hl = skia.Path(); hl.moveTo(-15, -s + 40); hl.lineTo(-s * 0.55, s * 0.4); c.drawPath(hl, P(color=col('#ffffff', 200), stroke=10))
        c.restore()
    sun(c, sx, sy, 130, t)
    if sp > 0.9: dust(c, t, seed=3, n=14, colr='#fff3b0')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 3: Light travels, meets air ----------
MOLS3 = [(330, 1000), (620, 900), (880, 1050), (250, 1280), (520, 1230), (800, 1330), (420, 1470)]
def s3(c, t, D, cues):
    day_bg(c, t + 40, 3, sunpos=(170, 720), hy=1660)
    sx, sy = 170, 720
    flow = prog(t, 0.2, 0.8)
    for i, h in enumerate(RAINBOW):
        f = lambda tt, i=i: (lerp(sx, 1000, (tt * 0.3 + i / 6) % 1.0) + math.sin(tt * 3 + i) * 25, lerp(sy, 1620, (tt * 0.3 + i / 6) % 1.0))
        x, y = f(t)
        if flow > 0:
            trail(c, [f(t - k * 0.02) for k in range(10, -1, -1)] if (t * 0.3 + i / 6) % 1.0 > 0.06 else [], h, 16)
            photon(c, x, y, 34, h, t, i, alpha=int(255 * flow), vel=vel_of(f, t))
    for i, (mx, my) in enumerate(MOLS3):
        a = prog(t, cues[1]['start'] + 0.15 * i, 0.4)
        if a > 0:
            c.save(); c.translate(mx, my + math.sin(t * 1.8 + i) * 10); s = ease_back(a, 2.2); c.scale(s, s); molecule(c, 0, 0, 48, t, i); c.restore()
    sun(c, sx, sy, 105, t)

# ---------- 4: Red straight, blue bounces ----------
MOLS4 = [(260, 900), (520, 820), (800, 930), (380, 1120), (720, 1120), (250, 1350), (560, 1420), (900, 1300)]
RED_PATH = [(120, 650), (980, 1560)]
BLUE_ORDER = [0, 1, 3, 4, 6, 7, 2]
def blue_path():
    pts = [(120, 650)]
    for mi in BLUE_ORDER:
        mx, my = MOLS4[mi]; px, py = pts[-1]; d = math.dist((mx, my), (px, py))
        pts.append((mx - (mx - px) / d * 62, my - (my - py) / d * 62))
    pts.append((1200, 560)); return pts
BLUE = blue_path()
def blue_hits(t0, t1):
    segs = [math.dist(BLUE[i], BLUE[i + 1]) for i in range(len(BLUE) - 1)]; L = sum(segs); acc = 0; out = []
    for i, s in enumerate(segs[:-1]):
        acc += s; out.append((BLUE_ORDER[i], t0 + (t1 - t0) * acc / L))
    return out

def s4(c, t, D, cues):
    sky(c, '#3aa9ff', '#d8f2ff', mid='#86ccff'); sunbeams(c, 120, 650, t, a=22)
    clouds(c, t + 10, seed=8, n=2, y0=1350, y1=1500, a=150)
    hills(c, 1680, t=t, trees=True)
    sun(c, 120, 650, 85, t)
    r0, r1 = cues[1]['start'], cues[2]['start'] - 0.2
    b0, b1 = cues[2]['start'] + 0.1, D - 0.4
    hits = blue_hits(b0, b1)
    for i, (mx, my) in enumerate(MOLS4):
        bump = 0
        for mi, ht in hits:
            if mi == i and 0 <= t - ht < 0.4: bump = math.sin((t - ht) / 0.4 * math.pi) * 0.28 * (1 - (t - ht) / 0.4 * 0.5)
        c.save(); c.translate(mx, my + math.sin(t * 1.8 + i) * 8); c.scale(1 + bump, 1 - bump * 0.6); molecule(c, 0, 0, 50, t, i); c.restore()
    if t >= r0:
        fr = lambda tt: path_pos(RED_PATH, ease_in_out(prog(tt, r0, r1 - r0)))[:2]
        trail(c, [fr(t - k * 0.02) for k in range(22, -1, -1)], '#ff4d4d', 22)
        x, y = fr(t); photon(c, x, y, 40, '#ff4d4d', t, 1, vel=vel_of(fr, t))
    if t >= b0:
        fb = lambda tt: path_pos(BLUE, prog(tt, b0, b1 - b0))[:2]
        trail(c, [fb(t - k * 0.02) for k in range(24, -1, -1)], '#2f80ff', 22)
        x, y = fb(t); photon(c, x, y, 40, '#2f80ff', t, 2, vel=vel_of(fb, t))
        for mi, ht in hits:
            if 0 <= t - ht < 0.5:
                k = (t - ht) / 0.5; mx, my = MOLS4[mi]
                c.drawCircle(mx, my, 60 + 90 * ease_out(k), P(color=col('#ffffff', int(200 * (1 - k))), stroke=8))
                for j in range(8):
                    ang = j * math.pi / 4 + 0.3
                    rr = 80 * (0.5 + ease_out(k))
                    c.drawCircle(mx + math.cos(ang) * rr, my + math.sin(ang) * rr, 11 * (1 - k), P(color=col('#ffe14d')))

def s4_sfx(D, cues):
    return [(cues[1]['start'] + 0.05, 'whoosh')] + [(ht, 'boing') for _, ht in blue_hits(cues[2]['start'] + 0.1, D - 0.4)]

# ---------- 5: Blue from everywhere ----------
def s5(c, t, D, cues):
    k = ease_in_out(prog(t, 0.2, cues[1]['start'] + 0.5))
    top = '#%02x%02x%02x' % tuple(int(lerp(a, b, k)) for a, b in zip((0xb9, 0xdc, 0xf5), (0x1a, 0x74, 0xff)))
    sky(c, top, '#e3f5ff'); clouds(c, t + 60, seed=5, n=3, y1=1000)
    birds(c, t, seed=6, y=480)
    hills(c, 1620, t=t)
    ex, ey = 540, 1340
    rnd = random.Random(11)
    for i in range(20):
        ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); dist0 = rnd.uniform(650, 950)
        sx_, sy_ = ex + math.cos(ang) * dist0, ey + math.sin(ang) * dist0
        off = rnd.random()
        a = prog(t, 0.3 + i * 0.07, 0.3)
        if a <= 0: continue
        def f(tt, sx_=sx_, sy_=sy_, off=off):
            u = ease_in_out((tt * 0.42 + off) % 1.0)
            return lerp(sx_, ex, u), lerp(sy_, ey - 30, u)
        u = (t * 0.42 + off) % 1.0
        x, y = f(t)
        fade = 1 - max(0, u - 0.85) / 0.15
        if u > 0.08: trail(c, [f(t - q * 0.025) for q in range(8, -1, -1)], '#2f80ff', 10)
        photon(c, x, y, 18, '#2f80ff', t, i, face_on=False, alpha=int(255 * a * fade))
    kid(c, 540, 1690, 1.05, t, wave=t > cues[1]['start'])
    if t > cues[1]['start']:
        s = ease_back(prog(t, cues[1]['start'], 0.5))
        for j in range(6):
            ang = t * 1.5 + j * 2 * math.pi / 6
            px, py = 540 + math.cos(ang) * 230 * s, 1330 + math.sin(ang) * 140 * s
            st = skia.Path()
            for q in range(10):
                rr = 18 if q % 2 == 0 else 8; aa = q * math.pi / 5 + t * 2
                (st.moveTo if q == 0 else st.lineTo)(px + math.cos(aa) * rr, py + math.sin(aa) * rr)
            st.close(); c.drawPath(st, P(color=col('#ffe14d')))
    dust(c, t, seed=12, n=14, colr='#cfe6ff')

def s5_sfx(D, cues): return [(cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 5b: Moon ----------
def s5b(c, t, D, cues):
    sky(c, '#03040b', '#1c2145', mid='#0b0e24')
    rnd = random.Random(21)
    for i in range(110):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 1550); tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(1.5, 4) + i)
        c.drawCircle(x, y, rnd.uniform(1.5, 4.5), P(color=col('#ffffff', int(90 + 160 * tw))))
    sh = (t * 0.25) % 1.4
    if sh < 0.5:
        k = sh / 0.5; x0, y0 = lerp(950, 300, k), lerp(150, 450, k)
        c.drawLine(x0, y0, x0 + 120, y0 - 55, P(color=col('#ffffff', int(200 * (1 - k))), stroke=4))
    ea = ease_back(prog(t, 0.3, 0.7))
    if ea > 0:
        c.save(); c.translate(820, 860); c.scale(ea, ea); c.rotate(t * 6)
        c.drawCircle(0, 0, 110, rad(0, 0, 110, [col('#6ab8ff', 140), col('#6ab8ff', 0)]))
        c.drawCircle(0, 0, 85, rad(-25, -30, 120, [col('#7ec3ff'), col('#1e66d9')]))
        for dx, dy, r in [(-30, -20, 30), (25, 25, 26), (10, -45, 18), (-40, 35, 14)]:
            c.drawCircle(dx, dy, r, P(color=col('#4cd964')))
        c.drawCircle(0, 0, 85, P(color=col('#ffffff', 60), stroke=4))
        c.restore()
    sun(c, 230, 820, 95, t)
    p = skia.Path(); p.moveTo(0, 1560); p.cubicTo(300, 1500, 700, 1620, W, 1530); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, 1500, 0, H), [col('#d3d6e0'), col('#8f93a3')]))
    for x, y, r in [(180, 1700, 70), (560, 1640, 45), (850, 1760, 90), (380, 1830, 40), (980, 1620, 30)]:
        c.drawOval(skia.Rect(x - r, y - r * 0.35, x + r, y + r * 0.35), P(color=col('#7d8192')))
        c.drawOval(skia.Rect(x - r * 0.85, y - r * 0.2, x + r * 0.85, y + r * 0.35), P(color=col('#a4a8b8')))
    fl = skia.Path(); c.drawLine(330, 1640, 330, 1420, P(color=col('#dddddd'), stroke=6))
    wv = math.sin(t * 2) * 6
    fl.moveTo(333, 1425); fl.quadTo(380, 1420 + wv, 430, 1430); fl.lineTo(430, 1495); fl.quadTo(380, 1490 + wv, 333, 1495); fl.close()
    c.drawPath(fl, P(color=col('#ff6b6b')))
    kid(c, 600, 1720, 0.95, t, helmet=True, wave=t > cues[1]['start'])

def s5b_sfx(D, cues): return [(0.1, 'whoosh'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 6: Sunset ----------
def s6(c, t, D, cues):
    k = ease_in_out(prog(t, 0.0, 1.8))
    sky(c, '#2a2a6e', '#ffc46b', mid='#ff7a59')
    if k < 1:
        c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, W, H), [col(DAY[0], int(255 * (1 - k))), col(DAY[1], int(255 * (1 - k)))]))
    rnd = random.Random(31)
    for i in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 600)
        c.drawCircle(x, y, rnd.uniform(1.5, 3.5), P(color=col('#ffffff', int(150 * k * (0.5 + 0.5 * math.sin(t * 3 + i))))))
    clouds(c, t, seed=13, n=3, y0=300, y1=900, a=int(120 + 60 * k))
    sun_y = lerp(900, 1540, k)
    sunbeams(c, 150, sun_y, t, a=int(30 * k))
    sun(c, 150, sun_y, 115, t)
    hills(c, 1620, c1='#4f8a3a', c2='#3c6e2c', t=t, dark=True)
    kid(c, 900, 1700, 0.85, t)
    A = (230, 1480); B = (840, 1400); CTRL = (540, 1150)
    def bez(u): return ((1 - u) ** 2 * A[0] + 2 * (1 - u) * u * CTRL[0] + u * u * B[0], (1 - u) ** 2 * A[1] + 2 * (1 - u) * u * CTRL[1] + u * u * B[1])
    g = ease_out(prog(t, cues[1]['start'], 1.6))
    for i in range(40):
        u = i / 40
        if u > g: break
        x, y = bez(u); c.drawCircle(x, y, 6 + 1.5 * math.sin(t * 5 - i * 0.5), P(color=col('#ffffff', 230)))
    if t > cues[1]['start'] + 0.6:
        for i, (x0, y0) in enumerate([(300, 1260), (450, 1200), (620, 1210), (760, 1290), (380, 1390), (680, 1360)]):
            a = prog(t, cues[1]['start'] + 0.6 + i * 0.1, 0.35)
            c.save(); c.translate(x0, y0 + math.sin(t * 2 + i) * 6); s = 0.6 * ease_back(a, 2.2); c.scale(s, s); molecule(c, 0, 0, 40, t, i); c.restore()
    if t > cues[2]['start']:
        cols_ = ['#2f80ff', '#ff4d4d', '#ff9f1c', '#2f80ff', '#ff9f1c', '#2f80ff', '#ff4d4d']
        for i, h in enumerate(cols_):
            def f(tt, i=i, h=h):
                u = ((tt - cues[2]['start']) * 0.3 + i / len(cols_)) % 1.0
                if h == '#2f80ff' and u > 0.45:
                    bx, by = bez(0.45); v = (u - 0.45) / 0.55
                    return bx + ease_out(v) * (220 if i % 2 else -200), by - ease_out(v) * 700
                return bez(u)
            u = ((t - cues[2]['start']) * 0.3 + i / len(cols_)) % 1.0
            x, y = f(t)
            al = 255 if not (h == '#2f80ff' and u > 0.45) else int(255 * (1 - (u - 0.45) / 0.55))
            photon(c, x, y, 26, h, t, i, face_on=False, alpha=al, vel=vel_of(f, t))
    dust(c, t, seed=14, n=12, colr='#ffe1b0')

def s6_sfx(D, cues): return [(0.1, 'whoosh'), (cues[2]['start'] + 0.1, 'sparkle')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    day_bg(c, t + 80, 7, sunpos=(540, 1080))
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1080 + math.sin(t * 2) * 12); c.scale(s, s); sun(c, 0, 0, 220, t); c.restore()
    for i, h in enumerate(RAINBOW):
        f = lambda tt, i=i: (540 + math.cos(tt * 0.9 + i * math.pi / 3) * 370, 1080 + math.sin(tt * 0.9 + i * math.pi / 3) * 340)
        x, y = f(t); photon(c, x, y, 32, h, t, i, vel=vel_of(f, t))
    if len(cues) > 1 and t > cues[-1]['start']:
        b = ease_back(prog(t, cues[-1]['start'], 0.55), 2.2); bob = 1 + 0.05 * math.sin(t * 6)
        c.save(); c.translate(540, 1530); c.scale(b * bob, b * bob)
        c.drawRoundRect(skia.Rect(-250, -66, 250, 94), 80, 80, P(color=col('#000000', 60), blur=10))
        c.drawRoundRect(skia.Rect(-250, -80, 250, 80), 80, 80, lin(c, (0, -80, 0, 80), [col('#ff5c85'), col('#e8264f')]))
        c.drawRoundRect(skia.Rect(-250, -80, 250, 80), 80, 80, P(color=col('#ffffff'), stroke=8))
        text_block(c, '+ Follow', 0, 0, size=80, fill='#ffffff', stroke='#b8183f')
        c.restore()
    dust(c, t, seed=15, n=20, colr='#fff3b0')

def s7_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why is the sky blue?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, lines=[
            ('Why is the sky blue?', 'Why is the sky BLUE?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='white', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Sunlight looks white.', 'Sunlight looks white …'),
            ("But it's actually made of all the colors of the rainbow!", "… but it has ALL the colors!")], tail=1.2),
        dict(name='air', draw=s3, lines=[
            ('This light zooms all the way down to Earth.', 'Light zooms down to Earth'),
            ('On its way, it bumps into tiny, tiny bits of air.', 'On the way: tiny bits of AIR!')], tail=1.2),
        dict(name='pinball', draw=s4, sfx_fn=s4_sfx, lines=[
            ('And here comes the trick!', 'Here comes the trick!'),
            ('Red light zooms almost straight through.', 'RED goes almost straight'),
            ('But blue light bounces around, like a ball in a pinball machine!', 'BLUE bounces – like pinball!')], tail=2.0),
        dict(name='everywhere', draw=s5, sfx_fn=s5_sfx, lines=[
            ('So blue light comes at you from all over the sky.', 'Blue comes from EVERYWHERE …'),
            ("And that's why the sky looks blue!", '… so the sky looks BLUE!')], tail=1.4),
        dict(name='moon', draw=s5b, sfx_fn=s5b_sfx, lines=[
            ("And guess what? There's no air on the Moon.", 'The Moon has NO AIR!'),
            ('Nothing bounces the light around, so the sky there is black, even in the daytime!', 'So its sky is BLACK – even by day!')], tail=1.4),
        dict(name='sunset', draw=s6, sfx_fn=s6_sfx, lines=[
            ('So why is the sky red in the evening?', 'Why is it RED at sunset?'),
            ('Then the sunlight has to travel a much longer way through the air.', 'Sunset: a much longer trip!'),
            ('The blue gets scattered away, and only red and orange make it to you.', 'Blue scatters away – RED gets through!')], tail=1.8),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.0),
    ])
