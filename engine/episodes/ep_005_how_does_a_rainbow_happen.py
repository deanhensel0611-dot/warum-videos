"""Episode 5 (EN): How does a rainbow happen?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
NAMES = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

def seg(c, p0, p1, k, hexcol, w=14, alpha=255):
    if k <= 0: return
    x = lerp(p0[0], p1[0], k); y = lerp(p0[1], p1[1], k)
    c.drawLine(p0[0], p0[1], x, y, P(color=col(hexcol, int(alpha * 0.35)), stroke=w * 2.2, blur=6))
    c.drawLine(p0[0], p0[1], x, y, P(color=col(hexcol, alpha), stroke=w))

def rain_streaks(c, t, x0, x1, y0, y1, n=30, seed=4, a=110):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1); off = rnd.random()
        y = y0 + ((t * 0.9 + off) % 1.0) * (y1 - y0)
        c.drawLine(x, y, x - 8, y + 40, P(color=col('#ffffff', a), stroke=4))

def drop_light(c, t, cx, cy, R, k_in, k_split, k_back, k_out):
    """Light path through one big raindrop: in from the left, split, bounce at the back, out lower-left."""
    E = (cx - R * 0.93, cy - R * 0.36)
    seg(c, (-40, E[1]), E, k_in, '#ffffff', w=22)
    for i, h in enumerate(RAINBOW):
        u = i / 6
        ab = math.radians(-32 + u * 26)           # point at the back of the drop
        B = (cx + math.cos(ab) * R * 0.97, cy + math.sin(ab) * R * 0.97)
        ax = math.radians(118 + u * 14)           # exit point lower-left
        X = (cx + math.cos(ax) * R * 0.97, cy + math.sin(ax) * R * 0.97)
        dx, dy = math.cos(math.radians(150 + u * 12)), math.sin(math.radians(150 + u * 12))
        O = (X[0] + dx * 420, X[1] + dy * 420 * 0.6 + 120)
        seg(c, E, B, k_split, h, w=9)
        seg(c, B, X, k_back, h, w=9)
        seg(c, X, O, k_out, h, w=12)

def plane(c, x, y, s, t):
    c.save(); c.translate(x, y + math.sin(t * 2) * 6); c.scale(s, s)
    c.drawPath(_wing(-1), P(color=col('#c9d8ee')))
    c.drawRoundRect(skia.Rect(-170, -42, 170, 42), 42, 42, lin(c, (0, -42, 0, 42), [col('#ffffff'), col('#dfe8f6')]))
    tail = skia.Path(); tail.moveTo(-150, -20); tail.lineTo(-195, -105); tail.lineTo(-140, -105); tail.lineTo(-95, -30); tail.close()
    c.drawPath(tail, P(color=col('#ff6b6b')))
    for i in range(4): c.drawCircle(-80 + i * 42, -8, 11, P(color=col('#8fd3ff')))
    c.drawPath(_wing(1), P(color=col('#b3c6e3')))
    face(c, 135, 2, 34, t, 7)
    c.restore()

def _wing(d):
    w = skia.Path(); w.moveTo(-20, 10 * d); w.lineTo(-90, 95 * d); w.lineTo(-40, 95 * d); w.lineTo(60, 10 * d); w.close(); return w

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    sky(c, '#5aaeff', '#e4f5ff', mid='#9ad3ff')
    sunbeams(c, 160, 700, t, a=18)
    sun(c, 160, 700, 80, t)
    rainbow(c, 560, 1560, 470, band=30, grow=ease_in_out(prog(t, 0.2, 1.6)))
    cloud_char(c, 820, 760, 0.7, t, gray=0.35, mood='happy')
    hills(c, 1640, t=t, trees=True)
    kid(c, 300, 1720, 0.75, t, wave=True)
    for i in range(3):
        aa = prog(t, 1.0 + i * 0.15, 0.35)
        if aa > 0:
            x, y = [(160, 1000), (930, 1080), (820, 1300)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab'][i], scale=0.4 + 0.6 * ease_back(aa, 2.5), alpha=int(255 * aa))
            c.restore()

def s1_sfx(D, cues): return [(0.3, 'sparkle')]

# ---------- 2: Sunlight is a mix of all colors ----------
def s2(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 170, 820, t, a=20)
    sun(c, 170, 820, 110, t)
    t1 = cues[1]['start']
    x = lerp(330, 560, ease_out(prog(t, 0.3, 1.4)))
    spread = ease_back(prog(t, t1 - 0.2, 0.8), 1.4)
    if spread < 1:
        photon(c, x, 1120, 90 * (1 - spread * 0.6), '#ffffff', t, 1, face_on=spread < 0.1, vel=(200, 0))
    if spread > 0:
        for i, h in enumerate(RAINBOW):
            ang = math.radians(-90 + i * 360 / 7 + t * 20)
            rr = 250 * spread
            px = x + math.cos(ang) * rr; py = 1120 + math.sin(ang) * rr
            photon(c, px, py, 52, h, t, i)
    dust(c, t, seed=3, n=12, colr='#ffffff')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] - 0.1, 'sparkle')]

# ---------- 3: After rain, the air is full of drops; light bends ----------
def s3(c, t, D, cues):
    sky(c, '#4f9fe8', '#d7eeff', mid='#86c3f5')
    rain_streaks(c, t, 0, W, 600, 1700, n=26, a=70)
    t1 = cues[1]['start']
    rnd = random.Random(2)
    for i in range(9):
        x, y = rnd.uniform(130, 900), rnd.uniform(700, 1500)
        if abs(x - 600) < 260 and abs(y - 1100) < 260 and t > t1 - 0.5: continue
        raindrop(c, x, y + math.sin(t * 2 + i) * 10, 34, t, i, shape='round')
    if t > t1 - 0.5:
        a = ease_back(prog(t, t1 - 0.5, 0.6))
        c.save(); c.translate(600, 1100); c.scale(a, a); c.translate(-600, -1100)
        raindrop(c, 600, 1100, 230, t, 2, shape='round', face_on=False, alpha=230)
        k = prog(t, t1 + 0.3, 1.0)
        E = (600 - 230 * 0.93, 1100 - 230 * 0.36)
        seg(c, (-40, E[1]), E, prog(t, t1, 0.4), '#ffffff', w=22)
        seg(c, E, (600 + 200, 1100 + 30), k, '#ffffff', w=18)
        face(c, 600, 1180, 120, t, 3, 'wow' if k > 0.3 else 'happy')
        c.restore()

def s3_sfx(D, cues): return [(cues[1]['start'] - 0.4, 'pop'), (cues[1]['start'] + 0.3, 'whoosh')]

# ---------- 4: Each color bends differently -> they spread ----------
def s4(c, t, D, cues):
    sky(c, '#3f8fe0', '#cfe8ff', mid='#7ab8f0')
    raindrop(c, 600, 1100, 260, t, 2, shape='round', face_on=False, alpha=230)
    t0, t1 = cues[0]['start'], cues[1]['start']
    drop_light(c, t, 600, 1100, 260, 1.0, ease_in_out(prog(t, t0 + 0.3, 1.6)), 0, 0)
    face(c, 600, 1210, 110, t, 3, 'happy')
    if t > t1:
        # little team of colored balls running apart
        for i, h in enumerate(RAINBOW):
            a = ease_back(prog(t, t1 + i * 0.08, 0.5))
            if a <= 0: continue
            ang = math.radians(200 + i * 22)
            rr = 70 + 140 * ease_out(prog(t, t1 + 0.4, 1.2))
            photon(c, 330 + math.cos(ang) * rr * 0.9, 1580 + math.sin(ang) * rr * 0.55 - 60, 30 * a, h, t, i)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'sparkle'), (cues[1]['start'] + 0.1, 'boing')]

# ---------- 5: Bounce at the back, come out; millions of drops ----------
def s5(c, t, D, cues):
    sky(c, '#3f8fe0', '#cfe8ff', mid='#7ab8f0')
    t0, t1 = cues[0]['start'], cues[1]['start']
    zoom = ease_in_out(prog(t, t1 - 0.3, 1.2))
    if zoom < 1:
        al = int(255 * (1 - zoom))
        c.save(); c.translate(600, 1100); c.scale(1 - 0.75 * zoom, 1 - 0.75 * zoom); c.translate(-600, -1100)
        raindrop(c, 600, 1100, 260, t, 2, shape='round', face_on=False, alpha=int(230 * (1 - zoom)))
        drop_light(c, t, 600, 1100, 260, 1.0, 1.0, ease_in_out(prog(t, t0 + 0.6, 1.0)), ease_out(prog(t, t0 + 1.6, 1.2)))
        if zoom < 0.3: face(c, 600, 1210, 110, t, 3, 'wow' if t > t0 + 1.0 else 'happy')
        c.restore()
    if zoom > 0:
        rnd = random.Random(9)
        for i in range(60):
            x, y = rnd.uniform(80, 980), rnd.uniform(680, 1520)
            dot = int(255 * zoom)
            raindrop(c, x, y, 11, t, i, shape='round', face_on=False, alpha=int(dot * 0.7))
        rainbow(c, 540, 1560, 470, band=34, grow=ease_in_out(prog(t, t1 + 0.6, 1.4)), alpha=int(255 * zoom))

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.7, 'boing'), (cues[1]['start'] + 0.7, 'sparkle')]

# ---------- 6: Sun behind you, rain in front; red outside ----------
def s6(c, t, D, cues):
    sky(c, '#6a9fd8', '#e0efff', mid='#9cc4ec')
    sunbeams(c, 130, 720, t, a=22)
    sun(c, 130, 720, 80, t)
    c.drawRect(skia.Rect(470, 0, W, 1650), lin(c, (470, 0, W, 0), [col('#5a6f8f', 0), col('#5a6f8f', 90)], vertical=False))
    rain_streaks(c, t, 520, W, 560, 1640, n=24, a=120)
    t0, t1 = cues[0]['start'], cues[1]['start']
    rainbow(c, 680, 1640, 370, band=28, grow=ease_in_out(prog(t, t0 + 0.4, 1.4)))
    hills(c, 1650, t=t, trees=False)
    kid(c, 330, 1680, 0.7, t)
    if t > t0 + 0.2:
        a = int(230 * prog(t, t0 + 0.2, 0.5))
        for j, yy in enumerate([800, 860]):
            off = (t * 300 + j * 80) % 120
            for xx in range(240 + int(off), 520, 120):
                c.drawLine(xx, yy + (xx - 240) * 0.35, xx + 50, yy + (xx + 50 - 240) * 0.35, P(color=col('#fff3a0', a), stroke=10))
    if t > t1:
        a1 = prog(t, t1 + 0.1, 0.4); a2 = prog(t, t1 + 1.2, 0.4)
        text_block(c, 'red', 790, 1230, size=58, fill='#ff3b3b', hi='#ff3b3b', alpha=int(255 * a1), scale=0.6 + 0.4 * ease_back(a1))
        c.drawLine(760, 1255, 740, 1300, P(color=col('#ffffff', int(255 * a1)), stroke=8))
        text_block(c, 'purple', 680, 1520, size=52, fill='#c79bff', hi='#c79bff', alpha=int(255 * a2), scale=0.6 + 0.4 * ease_back(a2))

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'sparkle'), (cues[1]['start'] + 0.1, 'pop'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 7: Bonus – rainbows are circles ----------
def s7(c, t, D, cues):
    sky(c, '#4aa3ff', '#e2f6ff', mid='#8fd0ff')
    t0, t1 = cues[0]['start'], cues[1]['start']
    rainbow(c, 540, 1120, 360, band=30, grow=1.0, a0=0, sweep=360)
    reveal = ease_in_out(prog(t, t1 + 0.8, 1.4))
    gy = lerp(1120, 1720, reveal)
    hills(c, gy, t=t, trees=True)
    if reveal > 0.1:
        clouds(c, t, seed=31, n=3, y0=1450, y1=1600, a=int(220 * reveal))
    px = lerp(-250, 1300, prog(t, t1 - 0.2, D - t1 - 0.2))
    if t > t1 - 0.2: plane(c, px, 720, 0.8, t)
    if t > t0 + 1.2 and reveal < 0.05:
        a = prog(t, t0 + 1.2, 0.4)
        text_block(c, '?', 540, 1300, size=110, fill='#ffe14d', alpha=int(255 * a), scale=0.5 + 0.5 * ease_back(a))

def s7_sfx(D, cues): return [(cues[0]['start'] + 1.2, 'pop'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 1.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    rainbow(c, 540, 1300, 420, band=30, grow=ease_in_out(prog(t, 0.0, 1.0)))
    hills(c, 1660, t=t)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1080 + math.sin(t * 2) * 12); c.scale(s, s); sun(c, 0, 0, 120, t); c.restore()
    for i, h in enumerate(RAINBOW):
        ang = t * 0.9 + i * 2 * math.pi / 7
        photon(c, 540 + math.cos(ang) * 330, 1080 + math.sin(ang) * 240, 30, h, t, i)
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=16, colr='#ffffff')

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='How does a rainbow happen?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('How does a rainbow happen?', 'How does a RAINBOW happen?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='mix', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Sunlight looks white, but it is really a mix of all the colors!', 'Sunlight is ALL colors mixed!'),
            ('Red, orange, yellow, green, blue and purple, all traveling together, like a team.', 'All colors travel TOGETHER')], tail=1.0),
        dict(name='bend', draw=s3, sfx_fn=s3_sfx, lines=[
            ('After it rains, the air is full of tiny water drops.', 'The air is full of DROPS'),
            ('When sunlight goes into a drop, it bends, like a car turning a corner.', 'Light BENDS in the drop!')], tail=1.0),
        dict(name='split', draw=s4, sfx_fn=s4_sfx, lines=[
            ('But each color bends a tiny bit differently.', 'Each color bends DIFFERENTLY'),
            ('So the team splits up, and the colors spread apart!', 'The colors SPREAD apart!')], tail=1.2),
        dict(name='bounce', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Then the light bounces off the back of the drop, like a ball off a wall, and comes back out.', 'It BOUNCES back out!'),
            ('Millions of drops do this together, and paint a giant rainbow!', 'Millions of drops = RAINBOW!')], tail=1.6),
        dict(name='behind', draw=s6, sfx_fn=s6_sfx, lines=[
            ("That's why you see a rainbow when the Sun is behind you, and the rain is in front of you.", 'Sun BEHIND you, rain in FRONT'),
            ('And red is always on the outside, and purple on the inside!', 'RED outside, PURPLE inside!')], tail=1.4),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? A rainbow is really a whole circle!', 'A rainbow is a CIRCLE!'),
            ('The ground hides the bottom half. But from an airplane, you can sometimes see the whole circle!', 'From a PLANE: the whole circle!')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
