"""Episode 4 (EN): Where does rain come from?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
GRAY = ('#7d8aa3', '#c9d2e0')

def falling_rain(c, t, x0, x1, y0, y1, n=14, seed=1, faces=True, r=22, speed=520, alpha=255):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1); off = rnd.random()
        y = y0 + ((t * speed / (y1 - y0) + off) % 1.0) * (y1 - y0)
        raindrop(c, x, y, r, t, i, face_on=faces, alpha=alpha)

def puddle_splash(c, x, y, t, period=0.9, off=0.0):
    k = ((t + off) % period) / period
    c.drawOval(skia.Rect(x - 30 - 60 * k, y - 8 - 10 * k, x + 30 + 60 * k, y + 8 + 10 * k), P(color=col('#ffffff', int(200 * (1 - k))), stroke=5))

def umbrella(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(t * 1.5) * 4)
    c.drawLine(0, 0, 0, 260, P(color=col('#5a3a20'), stroke=10))
    hk = skia.Path(); hk.addArc(skia.Rect(-30, 230, 0, 290), 0, 180); c.drawPath(hk, P(color=col('#5a3a20'), stroke=10))
    top = skia.Path(); top.moveTo(-210, 10); top.cubicTo(-200, -170, 200, -170, 210, 10)
    for i in range(6, -1, -1):
        xx = -210 + i * 70
        if i < 6: top.quadTo(xx + 35, -25, xx, 10)
    top.close()
    c.drawPath(top, lin(c, (0, -150, 0, 10), [col('#ffd23f'), col('#ff9f1c')]))
    for xx in (-70, 70): c.drawLine(0, -140, xx, 5, P(color=col('#e07b00'), stroke=5))
    c.restore()

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    sky(c, GRAY[0], GRAY[1])
    hills(c, 1640, c1='#6fc44f', c2='#4ea53a', t=t, trees=True)
    a = ease_back(prog(t, 0.05, 0.8), 1.5)
    c.save(); c.translate(540, lerp(500, 800, a)); cloud_char(c, 0, 0, 1.25, t, mood='wow' if t < 2 else 'happy', gray=0.55); c.restore()
    if t > 0.6:
        c.save(); clip = skia.Path(); clip.addRect(0, 900, W, 1700); c.clipPath(clip)
        falling_rain(c, t, 260, 820, 860, 1720, n=10, seed=3, r=24)
        c.restore()
    for i, x in enumerate([300, 620, 860]): puddle_splash(c, x, 1760, t, off=i * 0.3)
    umbrella(c, 230, 1350, 0.7, t)
    kid(c, 230, 1720, 0.75, t)
    for i in range(3):
        aa = prog(t, 1.0 + i * 0.15, 0.35)
        if aa > 0:
            x, y = [(150, 820), (930, 800), (860, 1120)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab'][i], scale=0.4 + 0.6 * ease_back(aa, 2.5), alpha=int(255 * aa))
            c.restore()

def s1_sfx(D, cues): return [(0.1, 'whoosh')]

# ---------- 2: The Sun warms the water -> vapor ----------
def s2(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 760, 820, t, a=26)
    sun(c, 760, 820, 120, t)
    sea(c, 1450, t)
    warm = ease_in_out(prog(t, cues[0]['start'] + 1.0, 1.5))
    c.drawRect(skia.Rect(0, 1440, W, H), lin(c, (0, 1440, 0, H), [col('#ffd23f', int(60 * warm)), col('#ff9f1c', 0)]))
    if t > cues[1]['start'] - 0.5:
        a = prog(t, cues[1]['start'] - 0.5, 0.6)
        for i in range(9):
            u = (t * 0.35 + i / 9) % 1.0
            x = 120 + i * 95 + math.sin(t + i) * 10
            y = 1440 - u * 620
            vapor(c, x, y, 1.0, t, seed=i, alpha=int(255 * a * math.sin(u * math.pi)))
    if t > cues[2]['start']:
        # wet T-shirt drying on a line
        a = ease_back(prog(t, cues[2]['start'], 0.5))
        c.save(); c.translate(250, 900); c.scale(a, a)
        c.drawLine(-170, -60, 170, -60, P(color=col('#ffffff'), stroke=5))
        sh = skia.Path(); sh.moveTo(-60, -60); sh.lineTo(-110, -20); sh.lineTo(-80, 10); sh.lineTo(-55, -10); sh.lineTo(-55, 90)
        sh.lineTo(55, 90); sh.lineTo(55, -10); sh.lineTo(80, 10); sh.lineTo(110, -20); sh.lineTo(60, -60); sh.quadTo(0, -30, -60, -60); sh.close()
        c.drawPath(sh, P(color=col('#ff6b6b')))
        for j in range(3):
            u = (t * 0.5 + j / 3) % 1.0
            vapor(c, -30 + j * 30, -70 - u * 60, 0.6, t, seed=j, alpha=int(255 * math.sin(u * math.pi)))
        c.restore()

def s2_sfx(D, cues): return [(cues[1]['start'] + 0.1, 'whoosh'), (cues[2]['start'] + 0.05, 'pop')]

# ---------- 3: Up where it's cold -> tiny droplets ----------
def s3(c, t, D, cues):
    sky(c, '#4aa3ff', '#d9f1ff', mid='#8ccfff')
    sea(c, 1600, t)
    # cold zone at the top
    c.drawRect(skia.Rect(0, 0, W, 1050), lin(c, (0, 550, 0, 1050), [col('#e8f6ff', 120), col('#e8f6ff', 0)]))
    rnd = random.Random(5)
    for i in range(12):
        x0 = rnd.uniform(140, 900); off = rnd.random()
        u = (t * 0.3 + off) % 1.0
        y = lerp(1580, 760, u)
        if y > 960:
            vapor(c, x0 + math.sin(t * 2 + i) * 10, y, 1.3, t, seed=i, alpha=int(230 * min(1, (1 - u) * 4)))
        else:
            k = clamp((960 - y) / 120)
            raindrop(c, x0, y, 12 + 10 * k, t, i, face_on=False, shape='round', alpha=int(255 * k))
    # snowflake-ish cold sparkles
    if t > cues[0]['start'] + 1.5:
        for j in range(8):
            x = 120 + j * 120; y = 700 + math.sin(t * 2 + j) * 20
            a = int(200 * prog(t, cues[0]['start'] + 1.5, 0.5))
            for q in range(3):
                ang = q * math.pi / 3 + t
                c.drawLine(x - math.cos(ang) * 14, y - math.sin(ang) * 14, x + math.cos(ang) * 14, y + math.sin(ang) * 14, P(color=col('#ffffff', a), stroke=4))
    if t > cues[1]['start']:
        a = ease_back(prog(t, cues[1]['start'], 0.5))
        c.save(); c.translate(540, 860); c.scale(a, a)
        raindrop(c, 0, 0, 55, t, 2, shape='round', mood='wow')
        c.restore()

def s3_sfx(D, cues): return [(cues[1]['start'] + 0.05, 'pop')]

# ---------- 4: Lots of droplets make a cloud ----------
def s4(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    hills(c, 1660, t=t, trees=True)
    form = ease_in_out(prog(t, cues[0]['start'] + 0.3, 2.2))
    rnd = random.Random(8)
    for i in range(36):
        sx_, sy_ = rnd.uniform(60, 1020), rnd.uniform(700, 1500)
        tx, ty = 540 + rnd.uniform(-220, 220), 1020 + rnd.uniform(-90, 90)
        x, y = lerp(sx_, tx, form) + math.sin(t * 2 + i) * 8, lerp(sy_, ty, form) + math.cos(t * 2 + i) * 8
        raindrop(c, x, y, 14, t, i, face_on=False, shape='round', alpha=int(255 * (1 - clamp((form - 0.7) / 0.3))))
    if form > 0.6:
        s = ease_back(clamp((form - 0.6) / 0.4), 1.6)
        c.save(); c.translate(540, 1030); c.scale(s, s); cloud_char(c, 0, 0, 1.3, t, mood='happy'); c.restore()
    if t > cues[1]['start']:
        # sponge analogy
        a = ease_back(prog(t, cues[1]['start'], 0.5))
        c.save(); c.translate(820, 1420); c.scale(a, a); c.rotate(-8)
        c.drawRoundRect(skia.Rect(-110, -65, 110, 65), 22, 22, P(color=col('#ffe14d')))
        c.drawRoundRect(skia.Rect(-110, 20, 110, 65), 22, 22, P(color=col('#4cd964')))
        for dx, dy, r in [(-60, -30, 12), (-10, -10, 9), (40, -35, 11), (70, 0, 8), (-80, 5, 7), (10, -45, 6)]:
            c.drawCircle(dx, dy, r, P(color=col('#e0b400')))
        face(c, 0, -5, 55, t, 4)
        c.restore()
        for j in range(3):
            u = (t * 1.2 + j / 3) % 1.0
            raindrop(c, 780 + j * 40, 1500 + u * 80, 9, t, j, face_on=False, alpha=int(255 * (1 - u)))

def s4_sfx(D, cues): return [(cues[0]['start'] + 2.0, 'sparkle'), (cues[1]['start'] + 0.05, 'boing')]

# ---------- 5: Droplets bump and grow ----------
def s5(c, t, D, cues):
    # inside the cloud
    sky(c, '#e9eef7', '#b9c4d8')
    rnd = random.Random(12)
    for i in range(14):
        x = rnd.uniform(0, W); y = rnd.uniform(600, 1700); r = rnd.uniform(90, 200)
        c.drawCircle(x + math.sin(t * 0.5 + i) * 20, y, r, P(color=col('#ffffff', 120), blur=30))
    t0 = cues[0]['start']
    g = ease_in_out(prog(t, t0 + 0.6, D - t0 - 1.5))
    # several small drops gather into one big drop in the centre
    n = 8
    for i in range(n):
        ang = i / n * 2 * math.pi + t * 0.5
        rr = lerp(380, 0, clamp(g * 1.3 - i * 0.04))
        if rr <= 5: continue
        raindrop(c, 540 + math.cos(ang) * rr, 1080 + math.sin(ang) * rr * 0.8, 46, t, i, face_on=True, shape='round')
    big = 46 + 90 * g
    bump = math.sin(t * 9) * 0.04 * (1 if g < 1 else 0)
    raindrop(c, 540, 1080, big, t, 1, shape='round', mood='wow' if g > 0.8 else 'happy', squash=bump)
    if t > cues[1]['start']:
        a = int(255 * prog(t, cues[1]['start'], 0.4))
        # weight arrow
        c.drawLine(540, 1080 + big + 30, 540, 1080 + big + 170, P(color=col('#2f5fd0', a), stroke=14))
        hd = skia.Path(); hd.moveTo(500, 1080 + big + 160); hd.lineTo(580, 1080 + big + 160); hd.lineTo(540, 1080 + big + 215); hd.close()
        c.drawPath(hd, P(color=col('#2f5fd0', a)))

def s5_sfx(D, cues):
    return [(cues[0]['start'] + 1.0 + i * 0.7, 'boing') for i in range(4)]

# ---------- 6: Too heavy -> rain -> back to the sea ----------
def s6(c, t, D, cues):
    sky(c, GRAY[0], '#dfe7f2')
    sunbeams(c, 960, 640, t, a=10)
    hills(c, 1560, c1='#6fc44f', c2='#4ea53a', t=t, trees=False, flowers=False)
    # river down to the sea at the bottom right
    rv = skia.Path(); rv.moveTo(250, 1500); rv.cubicTo(380, 1600, 300, 1700, 520, 1760); rv.cubicTo(700, 1810, 800, 1780, W, 1720)
    c.drawPath(rv, P(color=col('#3fa9ff'), stroke=60))
    for j in range(5):
        u = (t * 0.3 + j / 5) % 1.0
        c.drawCircle(lerp(260, W, u), 1500 + 260 * math.sin(u * math.pi * 0.9), 8, P(color=col('#ffffff', 180)))
    c.save(); clip = skia.Path(); clip.addRect(0, 900, W, 1560); c.clipPath(clip)
    falling_rain(c, t, 200, 860, 920, 1560, n=12, seed=6, r=22, speed=600)
    c.restore()
    cloud_char(c, 540, 820, 1.25, t, mood='happy', gray=0.45 + 0.1 * math.sin(t))
    if t > cues[1]['start']:
        a = int(255 * prog(t, cues[1]['start'], 0.5))
        c.save(); c.translate(0, 0)
        curved_arrow(c, 540, 1180, 360, 60, -50, colr='#ffffff', w=12, alpha=a)
        c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.3, 'sparkle')]

# ---------- 7: Bonus – the real shape of a raindrop ----------
def s7(c, t, D, cues):
    sky(c, '#6ec3ff', '#e2f6ff')
    clouds(c, t, seed=17, n=3, y0=650, y1=1000)
    t0, t1 = cues[0]['start'], cues[1]['start']
    a = ease_back(prog(t, t0 + 0.3, 0.5))
    if a > 0:
        c.save(); c.translate(540, 1080); c.scale(a, a)
        raindrop(c, 0, 0, 120, t, 1, shape='tear', alpha=255 if t < t1 else int(255 * (1 - prog(t, t1, 0.4))))
        if t > t0 + 1.6 and t < t1 + 0.4:
            k = prog(t, t0 + 1.6, 0.3); al = int(255 * min(k, 1 - prog(t, t1, 0.4)))
            c.drawLine(-160, -260, 160, 140, P(color=col('#ff4d4d', al), stroke=26))
            c.drawLine(160, -260, -160, 140, P(color=col('#ff4d4d', al), stroke=26))
        c.restore()
    if t > t1:
        b = ease_back(prog(t, t1 + 0.2, 0.5))
        c.save(); c.translate(300, 1160); c.scale(b, b); raindrop(c, 0, 0, 70, t, 3, shape='round'); c.restore()
        b2 = ease_back(prog(t, t1 + 1.6, 0.5))
        if b2 > 0:
            c.save(); c.translate(720, 1140); c.scale(b2, b2); raindrop(c, 0, 0, 120, t, 4, shape='bun', mood='wow'); c.restore()
        if t > t1 + 0.6:
            text_block(c, 'small', 300, 1330, size=60, alpha=int(255 * prog(t, t1 + 0.6, 0.3)))
        if t > t1 + 2.0:
            text_block(c, 'big', 720, 1330, size=60, alpha=int(255 * prog(t, t1 + 2.0, 0.3)))

def s7_sfx(D, cues): return [(cues[0]['start'] + 1.6, 'boing'), (cues[1]['start'] + 0.2, 'pop'), (cues[1]['start'] + 1.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 540, 1060, t, a=18)
    hills(c, 1660, t=t)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1000 + math.sin(t * 2) * 12); c.scale(s, s); cloud_char(c, 0, 0, 1.2, t); c.restore()
    for i in range(5):
        ang = t * 0.9 + i * 2 * math.pi / 5
        raindrop(c, 540 + math.cos(ang) * 380, 1050 + math.sin(ang) * 300, 34, t, i, shape='round')
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=16, colr='#ffffff')

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Where does rain come from?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Where does rain come from?', 'Where does RAIN come from?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='vapor', draw=s2, sfx_fn=s2_sfx, lines=[
            ('It all starts when the Sun warms up water in oceans, lakes and even puddles.', 'The Sun WARMS the water'),
            ('Some of the water turns into an invisible gas, called water vapor, and floats away.', 'Water turns into VAPOR!'),
            ("That's also why wet clothes dry in the sunshine!", 'Like wet clothes DRYING!')], tail=1.0),
        dict(name='cold', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The vapor rises up, up, up, high into the sky, where the air is cold.', "Up high, it's COLD"),
            ('There, it turns back into tiny, tiny water droplets.', 'Vapor turns into TINY droplets')], tail=1.0),
        dict(name='cloud', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Lots and lots of these tiny droplets together make a cloud!', 'Tiny droplets make a CLOUD!'),
            ('A cloud is a bit like a giant sponge, full of water.', 'Like a giant SPONGE!')], tail=1.0),
        dict(name='grow', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Inside the cloud, the droplets bump into each other and join together.', 'Droplets BUMP and join'),
            ('They get bigger and heavier, like a rolling snowball.', 'Bigger and HEAVIER!')], tail=1.4),
        dict(name='fall', draw=s6, sfx_fn=s6_sfx, lines=[
            ("When they're too heavy to float, they fall down as rain!", 'Too heavy? They FALL as rain!'),
            ('The rain flows back to rivers and the sea, and it all starts again!', 'Back to the sea – and AGAIN!')], tail=1.4),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ("And guess what? Raindrops aren't really shaped like tears!", "Raindrops aren't TEAR-shaped!"),
            ('Small ones are round, and big ones look a bit like a hamburger bun!', 'Big ones look like a BURGER bun!')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
