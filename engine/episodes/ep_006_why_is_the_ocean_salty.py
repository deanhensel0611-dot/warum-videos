"""Episode 6 (EN): Why is the ocean salty?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
GRAY = ('#7d8aa3', '#c9d2e0')

def mountains(c, y, t, snow=True):
    for x0, h, w, cc in [(-80, 560, 520, '#8a94a8'), (330, 700, 600, '#7b869c'), (760, 520, 520, '#8f99ad')]:
        p = skia.Path(); p.moveTo(x0, y); p.lineTo(x0 + w / 2, y - h); p.lineTo(x0 + w, y); p.close()
        c.drawPath(p, lin(c, (0, y - h, 0, y), [col(cc), col('#5d677b')]))
        if snow:
            s = skia.Path(); s.moveTo(x0 + w / 2, y - h); s.lineTo(x0 + w / 2 - 70, y - h + 120); s.lineTo(x0 + w / 2 - 20, y - h + 95)
            s.lineTo(x0 + w / 2 + 20, y - h + 125); s.lineTo(x0 + w / 2 + 70, y - h + 120); s.close()
            c.drawPath(s, P(color=col('#ffffff')))

def rain_streaks(c, t, x0, x1, y0, y1, n=30, seed=4, a=120):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1); off = rnd.random()
        y = y0 + ((t * 0.9 + off) % 1.0) * (y1 - y0)
        c.drawLine(x, y, x - 8, y + 40, P(color=col('#ffffff', a), stroke=4))

def piggy(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-110, -40, 50, 110):
        c.drawRoundRect(skia.Rect(lx - 24, 70, lx + 24, 160), 18, 18, P(color=col('#f58fae')))
    c.drawOval(skia.Rect(-230, -150, 210, 130), rad(-60, -80, 300, [col('#ffc2d4'), col('#f58fae')]))
    c.drawOval(skia.Rect(-230, -150, 210, 130), P(color=col('#d9607f'), stroke=6))
    for ex in (60, 150):
        e = skia.Path(); e.moveTo(ex - 40, -125); e.lineTo(ex, -205); e.lineTo(ex + 30, -110); e.close()
        c.drawPath(e, P(color=col('#f58fae'))); c.drawPath(e, P(color=col('#d9607f'), stroke=5))
    c.drawOval(skia.Rect(185, -40, 265, 50), P(color=col('#ff9fbb')))
    c.drawOval(skia.Rect(185, -40, 265, 50), P(color=col('#d9607f'), stroke=5))
    for nx in (212, 238): c.drawOval(skia.Rect(nx - 7, -6, nx + 7, 16), P(color=col('#b8456a')))
    tail = skia.Path(); tail.moveTo(-228, -10); tail.cubicTo(-290, -40, -290, 30, -250, 20)
    c.drawPath(tail, P(color=col('#d9607f'), stroke=8))
    c.drawRoundRect(skia.Rect(-70, -152, 40, -134), 9, 9, P(color=col('#8a2f4c')))
    face(c, 110, -40, 80, t, 4)
    c.restore()

def skyscraper(c, x, y, w, h):
    c.drawRect(skia.Rect(x - w / 2, y - h, x + w / 2, y), lin(c, (0, y - h, 0, y), [col('#9fb3d1'), col('#6f84a6')]))
    for j in range(int(h // 60) - 1):
        for i in range(3):
            c.drawRect(skia.Rect(x - w / 2 + 18 + i * (w - 36) / 3, y - h + 30 + j * 60, x - w / 2 + 18 + i * (w - 36) / 3 + (w - 36) / 3 - 14, y - h + 30 + j * 60 + 30), P(color=col('#dff1ff')))
    c.drawRect(skia.Rect(x - 6, y - h - 70, x + 6, y - h), P(color=col('#6f84a6')))

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 860, 760, t, a=18)
    sun(c, 860, 760, 90, t)
    sea(c, 1180, t)
    sand = skia.Path(); sand.moveTo(0, 1500); sand.cubicTo(300, 1440, 700, 1480, W, 1560); sand.lineTo(W, H); sand.lineTo(0, H); sand.close()
    c.drawPath(sand, lin(c, (0, 1450, 0, H), [col('#ffe3a3'), col('#f2c46d')]))
    kid(c, 300, 1720, 0.75, t)
    a = ease_back(prog(t, 0.3, 0.6), 2.0)
    if a > 0:
        c.save(); c.translate(640, 1330); c.scale(a, a); salt_crystal(c, 0, 0, 1.6, t, mood='wow' if t < 1.8 else 'happy'); c.restore()
    for i in range(3):
        aa = prog(t, 1.0 + i * 0.15, 0.35)
        if aa > 0:
            x, y = [(160, 900), (900, 1050), (820, 1400)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab'][i], scale=0.4 + 0.6 * ease_back(aa, 2.5), alpha=int(255 * aa))
            c.restore()

def s1_sfx(D, cues): return [(0.3, 'pop')]

# ---------- 2: Rain on rocks washes off tiny bits of salt ----------
def s2(c, t, D, cues):
    sky(c, GRAY[0], GRAY[1])
    mountains(c, 1300, t)
    hills(c, 1500, c1='#6fc44f', c2='#4ea53a', t=t, trees=False, flowers=False)
    cloud_char(c, 540, 760, 0.95, t, gray=0.5)
    rain_streaks(c, t, 200, 880, 880, 1560, n=26, a=150)
    t1 = cues[1]['start']
    rock(c, 330, 1560, 1.0, t, 1)
    rock(c, 760, 1580, 0.85, t, 2, mood='wow' if t > t1 + 0.4 else 'happy')
    if t > t1:
        for i in range(8):
            u = ((t - t1) * 0.45 + i / 8) % 1.0
            sx = 330 if i % 2 == 0 else 760
            x = sx + (i % 3 - 1) * 60 + u * 120
            y = 1460 + u * 140
            a = int(255 * prog(t, t1, 0.4) * math.sin(u * math.pi))
            salt_crystal(c, x, y, 0.35, t, i, face_on=False, alpha=a)

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.3, 'sparkle')]

# ---------- 3: Rivers carry the salt to the sea ----------
def s3(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    mountains(c, 1000, t)
    hills(c, 1150, t=t, trees=True, flowers=False)
    sea(c, 1500, t)
    rv = skia.Path(); rv.moveTo(160, 980); rv.cubicTo(500, 1100, 120, 1250, 450, 1330); rv.cubicTo(700, 1400, 860, 1380, 980, 1520)
    c.drawPath(rv, P(color=col('#3fa9ff'), stroke=70))
    c.drawPath(rv, P(color=col('#8fd3ff'), stroke=24))
    meas = skia.PathMeasure(rv, False); L = meas.getLength()
    for i in range(6):
        u = (t * 0.12 + i / 6) % 1.0
        pos, _ = meas.getPosTan(u * L)
        salt_crystal(c, pos.x(), pos.y() - 20, 0.42, t, i, face_on=True)
    t1 = cues[1]['start']
    if t > t1:
        a = ease_back(prog(t, t1, 0.5))
        c.save(); c.translate(270, 1450); c.scale(a, a)
        c.drawCircle(0, 0, 150, P(color=col('#ffffff', 230)))
        c.drawCircle(0, 0, 150, P(color=col('#2b6cc9'), stroke=10))
        c.drawCircle(0, 0, 130, P(color=col('#bfe6ff')))
        salt_crystal(c, 30, 20, 0.35, t, 3, face_on=False)
        c.drawLine(100, 100, 170, 170, P(color=col('#2b6cc9'), stroke=22))
        c.restore()
        text_block(c, 'just a tiny bit!', 300, 1290 - 0 * a, size=46, alpha=int(255 * prog(t, t1 + 0.6, 0.3)))

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.05, 'pop')]

# ---------- 4: Water goes up, salt stays behind ----------
def s4(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 800, 780, t, a=24)
    sun(c, 800, 780, 110, t)
    sea(c, 1240, t)
    t0, t1 = cues[0]['start'], cues[1]['start']
    a = prog(t, t0 + 0.8, 0.6)
    for i in range(10):
        u = (t * 0.35 + i / 10) % 1.0
        x = 100 + i * 92 + math.sin(t + i) * 10
        y = 1240 - u * 520
        vapor(c, x, y, 1.0, t, seed=i, alpha=int(255 * a * math.sin(u * math.pi)))
    for i in range(5):
        x = 170 + i * 185; y = 1400 + (i % 2) * 90
        tried = prog(t, t1 + 0.2 + i * 0.1, 0.4)
        jump = math.sin(min(1, tried) * math.pi) * 60 if t < t1 + 1.5 else 0
        salt_crystal(c, x, y - jump, 0.8, t, i, mood='wow' if t1 < t < t1 + 1.6 else 'happy')
    if t > t1 + 1.6:
        k = int(255 * prog(t, t1 + 1.6, 0.4))
        text_block(c, 'stay!', 540, 1640, size=58, alpha=k)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'whoosh'), (cues[1]['start'] + 0.3, 'boing')]

# ---------- 5: It builds up for millions of years (piggy bank) ----------
def s5(c, t, D, cues):
    sky(c, '#4aa3ff', '#e2f6ff', mid='#8fd0ff')
    t0, t1 = cues[0]['start'], cues[1]['start']
    sea(c, 1380, t)
    if t < t1 - 0.2:
        rate = 0.6
        for i in range(7):
            u = ((t - t0) * rate + i / 7) % 1.0
            if t - t0 < i / 7 / rate: continue
            salt_crystal(c, 200 + i * 110, lerp(760, 1390, u), 0.45, t, i, face_on=False, alpha=int(255 * min(1, (1 - u) * 6)))
        lvl = ease_in_out(prog(t, t0, t1 - t0))
        c.drawRect(skia.Rect(0, 1395, W, H), P(color=col('#ffffff', int(90 * lvl))))
    else:
        c.drawRect(skia.Rect(0, 1360, W, H), lin(c, (0, 1360, 0, H), [col('#ffe3a3'), col('#f2c46d')]))
        k = ease_back(prog(t, t1 - 0.2, 0.6))
        c.save(); c.translate(540, 1200); c.scale(k, k); piggy(c, 0, 0, 1.15, t); c.restore()
        for i in range(4):
            u = ((t - t1) * 0.8 + i / 4) % 1.0
            salt_crystal(c, 480 + (i % 2) * 40, lerp(700, 1020, u), 0.4, t, i, face_on=False, alpha=int(255 * min(1, (1 - u) * 5) * prog(t, t1 + 0.4, 0.3)))
        a = prog(t, t1 + 1.6, 0.4)
        text_block(c, 'millions of years', 540, 1530, size=54, alpha=int(255 * a))

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.3 + i * 0.8, 'pop') for i in range(3)] + [(cues[1]['start'] + 0.1, 'boing')]

# ---------- 6: Bonus – salt as tall as a skyscraper ----------
def s6(c, t, D, cues):
    sky(c, '#4aa3ff', '#e2f6ff', mid='#8fd0ff')
    clouds(c, t, seed=11, n=3, y0=640, y1=820)
    t0, t1 = cues[0]['start'], cues[1]['start']
    ground = 1580
    skyscraper(c, 760, ground, 200, 820)
    h = 820 * ease_in_out(prog(t, t1 + 0.2, 2.6))
    if h > 0:
        c.drawRect(skia.Rect(0, ground - h, 600, ground), lin(c, (0, ground - h, 0, ground), [col('#ffffff'), col('#dceaf5')]))
        rnd = random.Random(4)
        for i in range(40):
            x, yy = rnd.uniform(20, 580), rnd.uniform(0, 1)
            if yy * 820 < h: c.drawRect(skia.Rect(x, ground - yy * 820, x + 14, ground - yy * 820 + 14), P(color=col('#b9d0e3')))
        c.drawRect(skia.Rect(0, ground - h, 600, ground), P(color=col('#9fbdd6'), stroke=5))
        salt_crystal(c, 300, ground - h - 60, 1.0, t, 3, mood='wow' if h > 700 else 'happy')
    c.drawRect(skia.Rect(0, ground, W, H), lin(c, (0, ground, 0, H), [col('#7ed957'), col('#56b83a')]))
    if t > t0 + 0.6 and h < 10:
        a = ease_back(prog(t, t0 + 0.6, 0.5))
        c.save(); c.translate(300, 1250); c.scale(a, a); salt_crystal(c, 0, 0, 1.4, t, 1, mood='wow'); c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 2.8, 'sparkle')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 540, 1060, t, a=18)
    sea(c, 1500, t)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1060 + math.sin(t * 2) * 12); c.scale(s, s); salt_crystal(c, 0, 0, 2.2, t, 1); c.restore()
    for i in range(5):
        ang = t * 0.9 + i * 2 * math.pi / 5
        raindrop(c, 540 + math.cos(ang) * 340, 1080 + math.sin(ang) * 250, 34, t, i, shape='round')
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=16, colr='#ffffff')

def s7_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why is the ocean salty?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why is the ocean salty?', 'Why is the ocean SALTY?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='rocks', draw=s2, sfx_fn=s2_sfx, lines=[
            ('It all starts with rain, falling on rocks and mountains.', 'Rain falls on ROCKS'),
            ('Little by little, the rain washes off tiny, tiny bits of salt, like rinsing sprinkles off a cookie.', 'It washes off tiny bits of SALT')], tail=1.0),
        dict(name='river', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Rivers carry the salt all the way down to the sea, like a big water slide.', 'Rivers carry it to the SEA!'),
            ("There's only a tiny bit in each river, so river water doesn't taste salty.", 'Too little to TASTE')], tail=1.0),
        dict(name='stays', draw=s4, sfx_fn=s4_sfx, lines=[
            ('In the sea, the Sun warms the water, and some of it floats up into the sky.', 'Water floats UP'),
            ("But the salt can't float away. It stays behind in the sea!", 'But the SALT stays behind!')], tail=1.4),
        dict(name='piggy', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Rivers keep bringing more and more salt, and it never leaves.', 'More and MORE salt!'),
            ("It's like a piggy bank, where you put coins in, but never take any out. After millions of years, the sea got salty!", 'Like a PIGGY bank of salt!')], tail=1.4),
        dict(name='bonus', draw=s6, sfx_fn=s6_sfx, lines=[
            ('And guess what? If you took all the salt out of the ocean,', 'All the salt in the OCEAN...'),
            ('and spread it over all the land, it would be as tall as a skyscraper!', 'As tall as a SKYSCRAPER!')], tail=2.0),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
