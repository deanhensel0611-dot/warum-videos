"""Episode 10 (EN): Where does thunder come from?"""
import math, random
from lib import *

STORM = ('#3a4a7a', '#8fa3c8')

def storm_sky(c, t, flash=0.0):
    sky(c, STORM[0], STORM[1], mid='#5b6d9a')
    if flash > 0: c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#ffffff', int(150 * flash))))

def flash_at(t, t_f, dur=0.35):
    """1 at the moment of a flash, fading out."""
    if t < t_f or t > t_f + dur: return 0.0
    return 1 - (t - t_f) / dur

def rain(c, t, seed=7, n=40, y0=700, y1=1700, alpha=150):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(-100, W); ph = rnd.uniform(0, 1)
        y = y0 + ((t * 900 + ph * (y1 - y0)) % (y1 - y0)); x = x0 + (y - y0) * 0.15
        c.drawLine(x, y, x + 8, y + 45, P(color=col('#dbe9ff', alpha), stroke=4))

def ice_bit(c, x, y, r, t, seed=0, plus=True):
    c.save(); c.translate(x, y); c.rotate(t * 40 + seed * 30)
    pth = skia.Path()
    for k in range(6):
        a = k * math.pi / 3; (pth.moveTo if k == 0 else pth.lineTo)(math.cos(a) * r, math.sin(a) * r)
    pth.close()
    c.drawPath(pth, rad(-r * 0.3, -r * 0.3, r * 1.4, [col('#ffffff'), col('#cfeaff'), col('#9fd0f5')]))
    c.drawPath(pth, P(color=col('#6fb8e6'), stroke=3))
    c.restore()
    face(c, x, y + r * 0.05, r * 0.8, t, seed, 'happy')
    cc = '#ffd23f' if plus else '#7fb2ff'
    c.drawCircle(x + r * 0.85, y - r * 0.85, r * 0.32, P(color=col(cc)))
    c.drawLine(x + r * 0.7, y - r * 0.85, x + r * 1.0, y - r * 0.85, P(color=col('#ffffff'), stroke=4))
    if plus: c.drawLine(x + r * 0.85, y - r, x + r * 0.85, y - r * 0.7, P(color=col('#ffffff'), stroke=4))

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    fl = flash_at(t, 1.0) + flash_at(t, 2.6) * 0.7
    storm_sky(c, t, fl)
    clouds(c, t, seed=3, n=3, y0=650, y1=900, a=120)
    hills(c, 1650, c1='#5f9a4a', c2='#477a38', t=t, trees=True, dark=True, flowers=False)
    house(c, 800, 1560, 1.0, lit=True)
    a = ease_back(prog(t, 0.0, 0.7))
    c.save(); c.translate(500, 860); c.scale(a, a); cloud_char(c, 0, 0, 1.25, t, seed=1, mood='wow' if t > 0.9 else 'happy', gray=0.7); c.restore()
    if fl > 0.2: lightning_bolt(c, 470, 960, 330, 1500, t, seed=int(t > 2.0) + 3, w=24, alpha=int(255 * min(1, fl * 1.5)))
    if t > 1.15:
        k = ease_back(prog(t, 1.15, 0.4), 2.5)
        c.save(); c.translate(760, 1180); c.rotate(-8 + math.sin(t * 20) * 3 * (1 - prog(t, 1.15, 0.6))); c.scale(k, k)
        text_block(c, 'BOOM!', 0, 0, size=120, fill='#ffe14d', hi='#ffe14d', stroke='#2b2f6a')
        c.restore()
    rain(c, t, n=25, y0=980, alpha=110)

def s1_sfx(D, cues): return [(1.0, 'whoosh'), (1.15, 'boing')]

# ---------- 2: Ice bits bump -> electricity ----------
def s2(c, t, D, cues):
    sky(c, '#2c3766', '#6a7cab')
    t0, t1 = cues[0]['start'], cues[1]['start']
    # inside the cloud: big soft cloud walls
    for i, (x, y, r) in enumerate([(-60, 700, 260), (1140, 760, 280), (-40, 1550, 300), (1120, 1500, 280), (540, 1750, 300)]):
        c.drawCircle(x, y, r, P(color=col('#c8d2e6', 200), blur=30))
    rnd = random.Random(4)
    pts = []
    for i in range(7):
        bx, by = rnd.uniform(220, 860), rnd.uniform(800, 1450)
        x = bx + math.sin(t * 1.7 + i * 1.3) * 110; y = by + math.cos(t * 1.3 + i) * 90
        pts.append((x, y))
    # bumps -> sparks
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = math.dist(pts[i], pts[j])
            if d < 130 and t > t0:
                mx, my = (pts[i][0] + pts[j][0]) / 2, (pts[i][1] + pts[j][1]) / 2
                for k in range(6):
                    ang = k * math.pi / 3 + t * 5
                    c.drawLine(mx + math.cos(ang) * 20, my + math.sin(ang) * 20, mx + math.cos(ang) * 45, my + math.sin(ang) * 45, P(color=col('#ffe14d', 230), stroke=6))
    a = ease_back(prog(t, 0.1, 0.6))
    for i, (x, y) in enumerate(pts):
        c.save(); c.translate(x, y); c.scale(a, a); ice_bit(c, 0, 0, 52, t, i, plus=(i % 2 == 0) if t > t1 else (i % 2 == 0)); c.restore()
    if t > t1:
        k = prog(t, t1, 0.8)
        # electricity glow building up
        for q in range(5):
            u = (t * 1.2 + q / 5) % 1.0
            x = 120 + q * 210; y = 1560 - u * 40
            zz = skia.Path(); zz.moveTo(x - 30, y); zz.lineTo(x, y - 30); zz.lineTo(x - 10, y - 30); zz.lineTo(x + 20, y - 70)
            c.drawPath(zz, P(color=col('#ffe14d', int(220 * k * math.sin(u * math.pi))), stroke=8))
        c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#ffe14d', int(30 * k * (0.6 + 0.4 * math.sin(t * 12))))))

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'boing'), (cues[0]['start'] + 1.6, 'boing'), (cues[1]['start'] + 0.2, 'sparkle')]

# ---------- 3: Giant spark = lightning (like a sock zap) ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    tf = t0 + 0.3
    fl = flash_at(t, tf, 0.6)
    storm_sky(c, t, fl)
    hills(c, 1660, c1='#5f9a4a', c2='#477a38', t=t, trees=False, dark=True, flowers=False)
    cloud_char(c, 520, 800, 1.2, t, seed=2, mood='wow' if t > tf else 'happy', gray=0.7)
    if t > tf and t < t1:
        al = 1.0 if t < tf + 1.2 else 1 - prog(t, tf + 1.2, 0.4)
        flick = 0.75 + 0.25 * math.sin(t * 40)
        lightning_bolt(c, 520, 900, 600, 1610, t, seed=11, w=28, alpha=int(255 * al * flick))
    # sock zap: kid's finger touching a door knob with a tiny spark
    if t > t1:
        b = ease_back(prog(t, t1, 0.5))
        c.save(); c.translate(540, 1300); c.scale(b, b)
        c.drawCircle(0, 0, 230, P(color=col('#ffffff', 235)))
        c.drawCircle(0, 0, 230, P(color=col('#ffe14d'), stroke=10))
        # sock
        sk = skia.Path(); sk.moveTo(-170, -110); sk.lineTo(-110, -110); sk.lineTo(-110, 30); sk.quadTo(-110, 70, -60, 80); sk.lineTo(-40, 80); sk.quadTo(-10, 90, -20, 120); sk.lineTo(-120, 120); sk.quadTo(-175, 120, -170, 60); sk.close()
        c.drawPath(sk, P(color=col('#ff8fab')))
        for q in range(3): c.drawLine(-170, -100 + q * 20, -110, -100 + q * 20, P(color=col('#ffffff'), stroke=7))
        # hand pointing to knob
        c.drawRoundRect(skia.Rect(-20, -40, 70, 10), 22, 22, P(color=col('#f6c9a0')))
        c.drawRoundRect(skia.Rect(40, -30, 110, -10), 10, 10, P(color=col('#f6c9a0')))
        c.drawCircle(175, -20, 32, rad(165, -30, 40, [col('#fff3b0'), col('#d9a400')]))
        if (t - t1) % 1.0 < 0.35:
            for k in range(5):
                ang = math.radians(150 + k * 15)
                c.drawLine(128, -20, 128 + math.cos(ang) * -30, -20 + math.sin(ang) * 30, P(color=col('#2f80ff'), stroke=6))
            c.drawCircle(128, -20, 12, P(color=col('#fff6a8'), blur=3))
        c.restore()

def s3_sfx(D, cues):
    t1 = cues[1]['start']
    return [(cues[0]['start'] + 0.3, 'whoosh')] + [(t1 + k, 'pop') for k in (0.0, 1.0, 2.0)]

# ---------- 4: Super hot air pushes out (balloon pop) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    storm_sky(c, t, 0)
    c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#1b2350', 120)))
    x0 = 300
    hot = ease_out(prog(t, t0 + 0.3, 1.2))
    # bolt (left), glowing red/orange air around
    for q in range(9):
        yy = 680 + q * 115
        c.drawCircle(x0 + math.sin(q * 1.7) * 40, yy, (60 + 110 * hot) * (1 + 0.06 * math.sin(t * 8 + q)), P(color=col('#ff8a2c', int(120 * hot)), blur=40))
    lightning_bolt(c, x0, 620, x0 + 20, 1600, t, seed=5, w=24, branches=False)
    if t0 + 0.8 < t < t1:
        k = ease_back(prog(t, t0 + 0.8, 0.5))
        c.save(); c.translate(760, 1050); c.scale(k, k)
        sun(c, 0, 0, 80, t, glow=False)
        text_block(c, 'cooler!', 0, 170, size=56, fill='#ffffff')
        c.restore()
    # balloon pop analogy (right side)
    if t > t1:
        bx, by = 760, 1120
        pop_t = t1 + 1.6
        if t < pop_t:
            g = 1 + 0.25 * ease_in_out(prog(t, t1, 1.5))
            c.save(); c.translate(bx, by); c.scale(g, g)
            c.drawOval(skia.Rect(-110, -140, 110, 120), rad(-40, -60, 220, [col('#ffb3c6'), col('#ff4d6d'), col('#c9184a')], [0, 0.45, 1]))
            c.drawOval(skia.Rect(-70, -110, -30, -50), P(color=col('#ffffff', 170)))
            kn = skia.Path(); kn.moveTo(-12, 120); kn.lineTo(12, 120); kn.lineTo(0, 138); kn.close(); c.drawPath(kn, P(color=col('#c9184a')))
            face(c, 0, 0, 80, t, 3, 'wow' if t > pop_t - 0.6 else 'happy')
            c.restore()
            c.drawLine(bx, by + 160, bx + math.sin(t * 2) * 10, by + 380, P(color=col('#ffffff', 200), stroke=4))
        else:
            k = ease_out(prog(t, pop_t, 0.6))
            for q in range(10):
                ang = q * 2 * math.pi / 10
                c.drawLine(bx + math.cos(ang) * (60 + 200 * k), by + math.sin(ang) * (60 + 200 * k), bx + math.cos(ang) * (100 + 260 * k), by + math.sin(ang) * (100 + 260 * k), P(color=col('#ffe14d', int(255 * (1 - k))), stroke=12))
            sound_rings(c, bx, by, t, pop_t, n=3, colr='#ffffff', speed=500, life=1.0, a0=0, sweep=360, both=False)
            text_block(c, 'POP!', bx, by, size=110, fill='#ffe14d', hi='#ffe14d', scale=0.6 + 0.4 * ease_back(prog(t, pop_t, 0.4), 2.5))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.6, 'pop'), (cues[1]['start'] + 1.62, 'boing')]

# ---------- 5: Sound wave -> BOOM ----------
def s5(c, t, D, cues):
    t0 = cues[0]['start']
    tf = t0 + 0.2
    fl = flash_at(t, tf, 0.5)
    storm_sky(c, t, fl)
    hills(c, 1660, c1='#5f9a4a', c2='#477a38', t=t, trees=True, dark=True, flowers=False)
    cloud_char(c, 300, 760, 0.9, t, seed=3, gray=0.7)
    if tf < t < tf + 0.9: lightning_bolt(c, 300, 840, 260, 1560, t, seed=8, w=22)
    sound_rings(c, 280, 1200, t, tf + 0.1, n=6, colr='#ffe14d', speed=600, life=1.6, w=16, a0=-50, sweep=100, both=False)
    kid(c, 860, 1700, 0.8, t, look_up=False)
    if t > tf + 1.0:
        k = ease_back(prog(t, tf + 1.0, 0.4), 2.5)
        c.save(); c.translate(560, 1000); c.rotate(-6 + math.sin(t * 25) * 2 * (1 - prog(t, tf + 1.0, 0.8))); c.scale(k, k)
        text_block(c, 'BOOM!', 0, 0, size=140, fill='#ffe14d', hi='#ffe14d', stroke='#2b2f6a')
        c.restore()
    rain(c, t, n=20, y0=900, alpha=90)

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 1.2, 'boing')]

# ---------- 6: Light is fast, sound is slow (race) ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#4a5d92', '#a9bbdc')
    hills(c, 1640, c1='#6aa652', c2='#4f8a3e', t=t, trees=False, dark=False, flowers=False)
    # track lanes
    for i, y in enumerate([1000, 1300]):
        c.drawRoundRect(skia.Rect(80, y - 70, 1000, y + 70), 70, 70, P(color=col('#ffffff', 50)))
        c.drawLine(940, y - 80, 940, y + 80, P(color=col('#ffffff', 200), stroke=8))
    # light ball races
    u1 = ease_in_out(prog(t, t0 + 0.4, 0.6))
    f1 = lambda tt: (lerp(180, 900, ease_in_out(prog(tt, t0 + 0.4, 0.6))), 1000)
    photon(c, *f1(t), 52, '#fff27a', t, 1, vel=((f1(t)[0] - f1(t - 1 / 60)[0]) * 60, 0))
    if u1 >= 1:
        text_block(c, 'FLASH', 600, 880, size=56, alpha=int(255 * prog(t, t0 + 1.0, 0.3)))
    # sound blob crawls (snail-ish)
    u2 = prog(t, t0 + 0.4, max(1.0, D - t0 - 1.4))
    sx = lerp(180, 900, u2); sy = 1300
    c.drawCircle(sx, sy, 58, rad(sx - 15, sy - 20, 80, [col('#ffd6a8'), col('#ff9f1c')]))
    face(c, sx, sy + 5, 50, t, 2, 'happy')
    sound_rings(c, sx + 30, sy, t, t0 + 0.4 + ((t - t0) // 0.8) * 0.8, n=1, colr='#ffffff', speed=120, life=0.8, w=8, a0=-45, sweep=90, both=False)
    if t > t1 + 0.4:
        text_block(c, 'boom ...', 600, 1430, size=56, alpha=int(255 * prog(t, t1 + 0.4, 0.3)))

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (D - 1.0, 'boing')]

# ---------- 7: Bonus: count the seconds + safety ----------
def s7(c, t, D, cues):
    t0, t1, t2 = cues[0]['start'], cues[1]['start'], cues[2]['start']
    storm_sky(c, t, flash_at(t, t0 + 0.4, 0.4))
    c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#1b2350', 60)))
    if t < t2:
        cloud_char(c, 820, 780, 0.6, t, seed=4, gray=0.7)
        if t0 + 0.4 < t < t0 + 0.9: lightning_bolt(c, 820, 830, 860, 1200, t, seed=2, w=14, branches=False)
        n = int(clamp((t - t0 - 0.6) / 0.9, 0, 3.999)) + 1 if t > t0 + 0.6 else 0
        for i in range(n):
            k = ease_back(prog(t, t0 + 0.6 + i * 0.9, 0.4), 2.5)
            c.save(); c.translate(250 + i * 190, 1130); c.scale(k, k)
            c.drawCircle(0, 0, 80, P(color=col('#ffffff')))
            c.drawCircle(0, 0, 80, P(color=col('#ffb627'), stroke=10))
            text_block(c, str(i + 1), 0, -5, size=90, fill='#2b3a6a', stroke='#ffffff')
            c.restore()
        if t > t1:
            k = ease_out(prog(t, t1, 1.2))
            # distance arrow: big number = far
            c.drawLine(200, 1400, lerp(200, 880, k), 1400, P(color=col('#ffe14d'), stroke=14))
            hd = skia.Path(); x = lerp(200, 880, k); hd.moveTo(x + 30, 1400); hd.lineTo(x - 15, 1370); hd.lineTo(x - 15, 1430); hd.close()
            c.drawPath(hd, P(color=col('#ffe14d')))
            if k > 0.9: text_block(c, 'far away!', 540, 1490, size=58, alpha=int(255 * prog(t, t1 + 1.0, 0.3)))
    else:
        b = ease_back(prog(t, t2, 0.5))
        rain(c, t, n=30, y0=600, alpha=100)
        hills(c, 1620, c1='#5f9a4a', c2='#477a38', t=t, trees=False, dark=True, flowers=False)
        c.save(); c.translate(430, 1600); c.scale(b, b)
        house(c, 0, 0, 4.2, lit=True)
        c.restore()
        w = ease_in_out(prog(t, t2 + 0.8, 1.6))
        if w < 1 and b > 0.5: kid(c, lerp(780, 430, w), 1610, 0.7, t, look_up=False, wave=w < 0.05)
        if w >= 1:
            k = ease_back(prog(t, t2 + 2.5, 0.4))
            c.drawRect(skia.Rect(430 + 16 * 4.2, 1600 - 48 * 4.2, 430 + 32 * 4.2, 1600 - 32 * 4.2), P(color=col('#ffe9a8')))
            if k > 0: face(c, 430 + 24 * 4.2, 1600 - 38 * 4.2, 26 * k, t, 3, 'happy')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh')] + [(cues[0]['start'] + 0.6 + i * 0.9, 'pop') for i in range(4)] + [(cues[2]['start'] + 0.1, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, '#2f9bff', '#cdeeff', mid='#7cc6ff')
    hills(c, 1680, t=t)
    rainbow(c, 540, 1500, 620, band=30, grow=ease_out(prog(t, 0.2, 1.2)), alpha=200)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1060 + math.sin(t * 2) * 12); c.scale(s, s); cloud_char(c, 0, 0, 1.2, t, seed=5, gray=0.1); c.restore()
    for i in range(4):
        ang = t * 0.9 + i * math.pi / 2
        x, y = 540 + math.cos(ang) * 380, 1080 + math.sin(ang) * 280
        c.save(); c.translate(x, y); c.rotate(math.sin(t * 2 + i) * 10)
        bolt = skia.Path(); bolt.moveTo(10, -50); bolt.lineTo(-25, 5); bolt.lineTo(2, 5); bolt.lineTo(-10, 50); bolt.lineTo(28, -8); bolt.lineTo(2, -8); bolt.close()
        c.drawPath(bolt, P(color=col('#ffe14d'))); c.drawPath(bolt, P(color=col('#e0a800'), stroke=4))
        c.restore()
    follow_button(c, t, cues[-1]['start'])

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Where does thunder come from?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Where does thunder come from?', 'Where does THUNDER come from?'),
            ("Let's find out!", "Let's find out!")], tail=1.0),
        dict(name='ice', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Inside a storm cloud, tiny bits of ice bump and rub together.', 'Ice bits BUMP inside the cloud'),
            ('That builds up lots and lots of electricity!', 'That makes ELECTRICITY!')], tail=1.2),
        dict(name='spark', draw=s3, sfx_fn=s3_sfx, lines=[
            ("Then, zap! It jumps out as a giant spark. That's lightning!", "A giant spark: LIGHTNING!"),
            ('Like the tiny zap you get after sliding in socks on a carpet, but way bigger!', 'Like a SOCK zap – but huge!')], tail=1.4),
        dict(name='hot', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Lightning makes the air super hot, even hotter than the surface of the Sun!', 'HOTTER than the Sun’s surface!'),
            ('The hot air pushes out super fast, like a balloon going pop!', 'Air pushes out – POP!')], tail=1.4),
        dict(name='boom', draw=s5, sfx_fn=s5_sfx, lines=[
            ("That push makes a giant sound wave. Boom! That's thunder!", "BOOM! That's THUNDER!")], tail=1.8),
        dict(name='race', draw=s6, sfx_fn=s6_sfx, lines=[
            ('We see the flash first, because light is super fast.', 'Light is SUPER fast'),
            ('Sound is much slower, so the boom comes later.', 'Sound is SLOWER')], tail=1.4),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? Count the seconds from the flash to the boom.', 'COUNT from flash to boom!'),
            ('The bigger the number, the farther away the storm is!', 'Big number = FAR away'),
            ('And when thunder roars, go indoors!', 'Thunder roars? Go INDOORS!')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
