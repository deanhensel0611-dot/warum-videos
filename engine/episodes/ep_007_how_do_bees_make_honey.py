"""Episode 7 (EN): How do bees make honey?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
HIVE_IN = ('#ffcf66', '#f2a93b')

def meadow(c, t, y=1600, seed=0):
    hills(c, y, t=t, trees=False, flowers=True)

def wind_lines(c, x, y, t, alpha=255, d=1):
    for j in range(3):
        u = (t * 1.6 + j / 3) % 1.0
        yy = y + j * 26
        x0 = x + d * u * 120
        c.drawLine(x0, yy, x0 + d * 70, yy, P(color=col('#ffffff', int(alpha * math.sin(u * math.pi))), stroke=7))

def honey_drop(c, x, y, r, hexcol='#ffb703', face_on=True, t=0.0, seed=0, mood='happy'):
    pth = skia.Path(); pth.moveTo(x, y - r * 1.8); pth.cubicTo(x + r * 0.4, y - r * 1.1, x + r, y - r * 0.6, x + r, y)
    pth.arcTo(skia.Rect(x - r, y - r, x + r, y + r), 0, 180, False); pth.cubicTo(x - r, y - r * 0.6, x - r * 0.4, y - r * 1.1, x, y - r * 1.8); pth.close()
    c.drawPath(pth, rad(x - r * 0.3, y - r * 0.4, r * 2, [col('#fff3b0'), col(hexcol), col('#d97a00')], [0, 0.5, 1]))
    c.drawPath(pth, P(color=col('#c06a00', 160), stroke=max(2, r * 0.06)))
    c.drawOval(skia.Rect(x - r * 0.55, y - r * 0.6, x - r * 0.2, y - r * 0.1), P(color=col('#ffffff', 190)))
    if face_on: face(c, x, y + r * 0.05, r * 0.85, t, seed, mood)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 880, 720, t, a=18)
    sun(c, 880, 720, 80, t)
    meadow(c, t, 1560)
    for i, (x, p) in enumerate([(180, '#ff8fab'), (420, '#c79bff'), (680, '#ffffff')]):
        flower(c, x, 1330 + (i % 2) * 40, 0.8, t, i, petal=p)
    honey_jar(c, 820, 1640, 0.9, t)
    a = ease_out(prog(t, 0.0, 1.2))
    bx = lerp(-150, 520, a) + math.sin(t * 2) * 40; by = 1000 + math.sin(t * 3) * 50
    bee(c, bx, by, 0.9, t, mood='wow' if t < 2.0 else 'happy')
    for i in range(3):
        aa = prog(t, 1.0 + i * 0.15, 0.35)
        if aa > 0:
            x, y = [(160, 900), (900, 1020), (300, 1180)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab'][i], scale=0.4 + 0.6 * ease_back(aa, 2.5), alpha=int(255 * aa))
            c.restore()

def s1_sfx(D, cues): return [(0.1, 'whoosh')]

# ---------- 2: Nectar, sipped with a straw-like tongue ----------
def s2(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    meadow(c, t, 1640)
    t0, t1 = cues[0]['start'], cues[1]['start']
    flower(c, 470, 1230, 1.7, t, 1, petal='#ff8fab')
    land = ease_out(prog(t, 0.2, 1.4))
    bx, by = lerp(1100, 700, land), lerp(780, 930, land)
    if t > t1:
        k = ease_out(prog(t, t1, 0.6))
        hx, hy = bx - 95, by + 25
        ex, ey = lerp(hx, 520, k), lerp(hy, 1220, k)
        c.drawLine(hx, hy, ex, ey, P(color=col('#3a2a1a'), stroke=10))
        for j in range(4):
            u = ((t - t1) * 0.8 + j / 4) % 1.0
            if k > 0.95:
                c.drawCircle(lerp(ex, hx, u), lerp(ey, hy, u), 10, P(color=col('#ffd23f')))
    bee(c, bx, by, 1.1, t, flip=True, mood='happy')
    if t > t0 + 0.6:
        a = prog(t, t0 + 0.6, 0.4)
        for j in range(5):
            ang = t * 1.2 + j * 1.25
            c.drawCircle(470 + math.cos(ang) * 30, 1230 + math.sin(ang) * 30, 9, P(color=col('#ffe680', int(220 * a))))

def s2_sfx(D, cues): return [(0.3, 'whoosh'), (cues[1]['start'] + 0.1, 'pop')]

# ---------- 3: Honey stomach, fly home ----------
def s3(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    meadow(c, t, 1640)
    t0, t1 = cues[0]['start'], cues[1]['start']
    fly = ease_in_out(prog(t, t1 + 0.3, 2.4))
    beehive(c, 820, 1640, lerp(0.6, 0.85, fly), t)
    bx = lerp(430, 760, fly); by = lerp(1060, 1450, fly) + math.sin(t * 3) * 20 * (1 - fly)
    s = lerp(1.6, 0.35, fly)
    bee(c, bx, by, s, t)
    if fly < 0.3:
        fill = ease_in_out(prog(t, t0 + 0.6, 2.0))
        a = int(255 * (1 - fly / 0.3))
        cx, cy, r = bx - 5 * s, by, 42 * s
        c.drawCircle(cx, cy, r, P(color=col('#ffffff', int(a * 0.85))))
        c.save(); clip = skia.Path(); clip.addCircle(cx, cy, r); c.clipPath(clip, doAntiAlias=True)
        c.drawRect(skia.Rect(cx - r, cy + r - 2 * r * fill, cx + r, cy + r), P(color=col('#ffc93c', a)))
        c.restore()
        c.drawCircle(cx, cy, r, P(color=col('#c06a00', a), stroke=5))
        if t > t0 + 0.8:
            text_block(c, 'honey stomach', 430, 1360, size=54, alpha=int(a * prog(t, t0 + 0.8, 0.3)))

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'sparkle'), (cues[1]['start'] + 0.3, 'whoosh')]

# ---------- 4: Bees pass it along and add helpers ----------
def s4(c, t, D, cues):
    sky(c, HIVE_IN[0], HIVE_IN[1])
    honeycomb(c, -40, 640, 13, 13, 52)
    c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#ffe7a3', 110)))
    t0, t1 = cues[0]['start'], cues[1]['start']
    bee(c, 260, 1150, 1.0, t)
    bee(c, 820, 1150, 1.0, t, flip=True, seed=3)
    u = (t * 0.45) % 1.0
    k = 0.5 - 0.5 * math.cos(u * 2 * math.pi)
    x = lerp(400, 680, k); y = 1150 - math.sin(k * math.pi) * 120
    gold = prog(t, t1 + 0.3, 2.0)
    honey_drop(c, x, y + 40, 46, hexcol='#ffe680' if gold < 0.5 else '#ffb703', t=t, seed=2)
    if t > t1:
        for j in range(8):
            a = prog(t, t1 + j * 0.15, 0.3)
            ang = j * math.pi / 4 + t
            sx_, sy_ = x + math.cos(ang) * 110, y + 30 + math.sin(ang) * 110
            sz = 18 * a
            c.drawLine(sx_ - sz, sy_, sx_ + sz, sy_, P(color=col('#ffffff', int(255 * a)), stroke=6))
            c.drawLine(sx_, sy_ - sz, sx_, sy_ + sz, P(color=col('#ffffff', int(255 * a)), stroke=6))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'boing'), (cues[1]['start'] + 0.2, 'sparkle')]

# ---------- 5: Wax rooms, wings as fans ----------
def s5(c, t, D, cues):
    sky(c, HIVE_IN[0], HIVE_IN[1])
    t0, t1 = cues[0]['start'], cues[1]['start']
    dry = ease_in_out(prog(t, t1 + 0.3, 3.0))
    def fill(i, j):
        n = j * 7 + i
        return (clamp(prog(t, t0 + 0.4 + n * 0.08, 0.4) * (0.6 + 0.4 * dry)), 0)
    honeycomb(c, 120, 1180, 7, 5, 78, fill)
    if t > t1:
        a = prog(t, t1, 0.4)
        for i, x in enumerate([260, 820]):
            bee(c, x, 900 + math.sin(t * 2 + i) * 15, 0.85, t * 1.6, seed=i, flip=(i == 1))
            wind_lines(c, x + (-60 if i == 0 else 60), 1030, t, int(255 * a), d=1 if i == 0 else -1)
        for j in range(6):
            u = (t * 0.5 + j / 6) % 1.0
            vapor(c, 260 + j * 110, 1180 - u * 220, 0.8, t, seed=j, alpha=int(200 * a * math.sin(u * math.pi)))

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.4 + i * 0.5, 'pop') for i in range(3)] + [(cues[1]['start'] + 0.2, 'whoosh')]

# ---------- 6: Wax lid -> honey ----------
def s6(c, t, D, cues):
    sky(c, HIVE_IN[0], HIVE_IN[1])
    t0, t1 = cues[0]['start'], cues[1]['start']
    def fill(i, j):
        n = j * 7 + i
        return (1.0, ease_back(prog(t, t0 + 0.3 + n * 0.09, 0.35)))
    honeycomb(c, 120, 960, 7, 5, 78, fill)
    bee(c, 540 + math.sin(t * 1.3) * 300, 820 + math.sin(t * 2.6) * 30, 0.7, t, flip=math.cos(t * 1.3) < 0)
    if t > t1:
        a = ease_back(prog(t, t1, 0.6), 2.0)
        c.save(); c.translate(540, 1620); c.scale(a, a); honey_jar(c, 0, 0, 1.0, t); c.restore()
        dust(c, t, seed=4, n=12, colr='#fff6dc')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3 + i * 0.6, 'pop') for i in range(4)] + [(cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 7: Bonus – 12 bees, 1 teaspoon ----------
def s7(c, t, D, cues):
    sky(c, '#6ec3ff', '#e2f6ff')
    meadow(c, t, 1660)
    t0, t1 = cues[0]['start'], cues[1]['start']
    n_show = int(clamp((t - t0 - 0.4) / 2.4) * 12 + 0.999) if t > t0 + 0.4 else 0
    for i in range(12):
        if i >= n_show: break
        a = ease_back(prog(t, t0 + 0.4 + i * 0.2, 0.4))
        ang = -math.pi + (i + 0.5) / 12 * math.pi
        x = 540 + math.cos(ang) * 400; y = 1240 + math.sin(ang) * 520
        c.save(); c.translate(x, y); c.scale(a, a); bee(c, 0, 0, 0.42, t, seed=i, flip=(x > 540)); c.restore()
    # spoon
    sa = ease_back(prog(t, t1, 0.5))
    if sa > 0:
        c.save(); c.translate(540, 1150); c.scale(sa * 0.9, sa * 0.9); c.rotate(-20)
        c.drawRoundRect(skia.Rect(-20, 0, 20, 300), 20, 20, P(color=col('#c9d3e0')))
        c.drawOval(skia.Rect(-80, -120, 80, 20), lin(c, (0, -120, 0, 20), [col('#eef3f9'), col('#b4c0d0')]))
        c.drawOval(skia.Rect(-62, -100, 62, 5), P(color=col('#ffb703')))
        c.drawOval(skia.Rect(-40, -85, -10, -65), P(color=col('#ffffff', 170)))
        c.restore()
    if t > t1 + 0.8:
        text_block(c, '12 bees = 1 spoon', 540, 1560, size=58, alpha=int(255 * prog(t, t1 + 0.8, 0.3)))

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4 + i * 0.4, 'pop') for i in range(6)] + [(cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 540, 1060, t, a=18)
    meadow(c, t, 1660)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1060 + math.sin(t * 2) * 12); c.scale(s, s); bee(c, 0, 0, 1.2, t); c.restore()
    for i, p in enumerate(['#ff8fab', '#c79bff', '#ffffff', '#ffd23f', '#8fd3ff']):
        ang = t * 0.9 + i * 2 * math.pi / 5
        flower(c, 540 + math.cos(ang) * 360, 1080 + math.sin(ang) * 260, 0.45, t, i, petal=p, stem=False)
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=16, colr='#ffffff')

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='How do bees make honey?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('How do bees make honey?', 'How do bees make HONEY?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='nectar', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Bees visit flowers to find a sweet juice, called nectar.', 'Flowers have sweet NECTAR'),
            ('They sip it up with their long tongue, like a tiny straw!', 'A tongue like a STRAW!')], tail=1.0),
        dict(name='stomach', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The bee keeps the nectar in a special tummy, called a honey stomach. It is like a backpack inside!', 'A special HONEY stomach!'),
            ('When it is full, the bee flies home to the hive.', 'Fly home to the HIVE!')], tail=1.4),
        dict(name='pass', draw=s4, sfx_fn=s4_sfx, lines=[
            ('At the hive, the bee passes the nectar to other bees, from mouth to mouth.', 'Bees PASS it along'),
            ('Each bee adds special helpers, called enzymes, that slowly turn the nectar into honey.', 'Nectar turns into HONEY!')], tail=1.4),
        dict(name='fan', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Then the bees put it into tiny six-sided rooms, made of wax.', 'Tiny WAX rooms'),
            ('And they flap their wings like little fans, to dry it until it is thick and sticky!', 'Wings work like FANS!')], tail=1.4),
        dict(name='lid', draw=s6, sfx_fn=s6_sfx, lines=[
            ('When it is ready, the bees close each room with a wax lid.', 'A wax LID on top'),
            ('Now it is honey!', 'Now it is HONEY!')], tail=1.6),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? It takes about twelve bees, working their whole lives,', 'TWELVE busy bees...'),
            ('to make just one teaspoon of honey!', 'for ONE teaspoon of honey!')], tail=2.0),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
