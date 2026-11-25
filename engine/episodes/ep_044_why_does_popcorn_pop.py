"""Episode 44 (EN, general audience): Why does popcorn pop?
Facts checked (Popcorn Board "What makes popcorn pop?", USDA National Agricultural Library "How does popcorn pop?",
Scientific American "Explore the pop in popcorn", Virot & Ponomarenko 2015 J. R. Soc. Interface "Popcorn: critical
temperature, jump and sound", Mental Floss "Why does popcorn pop"):
- A popcorn kernel has a hard, moisture-tight hull (pericarp) around soft starch and a little water (ideal ~13.5-14 %).
- Heating turns the water into steam; the tough hull traps it, so pressure builds (~135 psi, about 9 atmospheres).
- The hull bursts at about 180 C (~355 F) (Virot & Ponomarenko measured ~180 C).
- The hot, gelatinized starch expands into a foam (popcorn expands about 40-50x its original size) and sets as it
  cools: the white fluffy flake.
- Other corn types don't pop well: their hulls are more porous, so steam leaks out slowly instead of building up.
- The popping sound comes from the release of water vapor (steam escaping), not from the hull fracturing
  (Virot & Ponomarenko 2015, who compared it to a champagne cork).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def kitchen(c, top='#2f9bff', bottom='#bfe3ff'):
    sky(c, top, bottom)
    rnd = random.Random(1)
    for i in range(6):
        x, y = rnd.uniform(80, 1000), rnd.uniform(650, 1600)
        c.drawCircle(x, y, rnd.uniform(60, 120), P(color=col('#ffffff', 18)))

def pan(c, x, y, w_=760, heat=0.0, t=0.0):
    c.drawOval(skia.Rect(x - w_ / 2 - 10, y - 50, x + w_ / 2 + 10, y + 90), P(color=col('#0b1a3a', 60), blur=14))
    c.drawOval(skia.Rect(x - w_ / 2, y - 70, x + w_ / 2, y + 70), lin(c, (0, y - 70, 0, y + 70), [col('#5b6478'), col('#2c3242')]))
    c.drawOval(skia.Rect(x - w_ / 2 + 26, y - 52, x + w_ / 2 - 26, y + 48), lin(c, (0, y - 52, 0, y + 48), [col('#232837'), col('#3b4252')]))
    if heat > 0:
        c.drawOval(skia.Rect(x - w_ / 2 + 26, y - 52, x + w_ / 2 - 26, y + 48), P(color=col('#ff6b2c', int(70 * heat)), blur=20))
    c.drawRoundRect(skia.Rect(x + w_ / 2 - 10, y - 18, x + w_ / 2 + 220, y + 14), 14, 14, P(color=col(NAVY)))

def heat_waves(c, x0, x1, y, t, k=1.0, colr='#ff6b2c'):
    for i in range(5):
        xx = lerp(x0, x1, (i + 0.5) / 5)
        p = skia.Path(); p.moveTo(xx, y)
        for j in range(1, 9):
            p.lineTo(xx + math.sin(t * 6 + j + i) * 10, y - j * 14)
        c.drawPath(p, P(color=col(colr, int(160 * k)), stroke=6))

def steam_wisp(c, x, y, t, k=1.0, seed=0, h=140):
    rnd = random.Random(seed)
    for j in range(6):
        u = ((t * 0.9 + j / 6 + rnd.random()) % 1.0)
        c.drawCircle(x + math.sin(t * 3 + j) * 12 * u, y - u * h, 10 + 18 * u, P(color=col('#ffffff', int(150 * k * (1 - u))), blur=6))

KPOS = [(300, 1380), (420, 1405), (540, 1385), (660, 1410), (780, 1388), (360, 1430), (600, 1440), (720, 1432)]

# ---------- 1: Hook (cold open: kernels already popping) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    kitchen(c)
    pan(c, 540, 1420, heat=1.0, t=t)
    for i, (x, y) in enumerate(KPOS):
        pt = 0.4 + i * 0.55
        jig = math.sin(t * 40 + i) * 3
        if t < pt:
            popcorn_kernel(c, x + jig, y, 0.7, rot=i * 40, heat=0.6)
        else:
            u = t - pt
            jy = -900 * u + 1600 * u * u
            yy = min(y, y + jy) if u < 0.56 else y - 10
            popcorn_puff(c, x + (i - 3) * 30 * min(u, 0.56), yy, 0.8, rot=i * 50 + u * 200 * (u < 0.56), k=ease_back(prog(t, pt, 0.15)), seed=i)
    label_pill(c, 'POP!', 540, 780, size=60, k=ease_back(prog(t, 0.45, 0.3)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        if k > 0:
            c.save(); c.translate(540, 950); c.scale(k, k)
            gauge(c, 0, 0, 150, 0.15 + 0.7 * prog(t, t1 + 0.3, 1.5), label='PRESSURE')
            c.restore()

def s1_sfx(D, cues):
    ev = [(0.0, 'whoosh')] + [(0.4 + i * 0.55, 'pop') for i in range(len(KPOS))]
    return ev + [(cues[1]['start'] + 0.2, 'click')]

# ---------- 2: What's inside a kernel ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    kitchen(c, '#ffd23f', '#fff1c4')
    k = ease_back(prog(t, t0 - 0.2, 0.5))
    sec = ease_in_out(prog(t, t0 + 0.6, 0.8))
    if k > 0:
        popcorn_kernel(c, 560, 1110, 4.6 * k, rot=-6 + 3 * math.sin(t), section=sec, t=t)
    for j, (txt, hc, x, y, tx, ty, st) in enumerate((('hard SHELL', HOT, 250, 760, 470, 900, 0.6),
                                                    ('soft STARCH', GOLD, 250, 1500, 470, 1250, 1.6),
                                                    ('~14% WATER', SKYB, 830, 1460, 590, 1120, 2.6))):
        kk = ease_back(prog(t, t0 + st, 0.4))
        if kk > 0:
            c.drawLine(x, y, lerp(x, tx, min(1, kk)), lerp(y, ty, min(1, kk)), P(color=col(NAVY, 200), stroke=5))
            c.drawCircle(tx, ty, 9 * min(1, kk), P(color=col(NAVY)))
            label_pill(c, txt, x, y, size=46, k=kk, fill=NAVY, hi=hc)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'pop'), (t0 + 0.6, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.6, 'pop'), (t0 + 2.6, 'pop')]

# ---------- 3: Water -> steam, trapped by the shell ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, '#ff9f6b', '#ffe1c4')
    heat = ease_out(prog(t, t0, 1.5))
    heat_waves(c, 300, 820, 1640, t, k=heat)
    st = ease_in_out(prog(t, t0 + 0.6, 2.0))
    shake = math.sin(t * 50) * 3 * st
    popcorn_kernel(c, 560 + shake, 1110, 4.6, rot=-6, section=1.0, steam=st, heat=heat * 0.7, t=t)
    label_pill(c, 'water -> STEAM', 540, 720, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        kk = ease_out(prog(t, t1 + 0.3, 0.5))
        # steam pushes out, the shell pushes back
        for j in range(6):
            a = math.radians(j * 60 + 20)
            ph = ((t - t1) * 1.5 + j * 0.17) % 1.0
            r0 = lerp(60, 150, ph)
            x, y = 560 + math.cos(a) * r0, 1110 + math.sin(a) * r0 * 1.3
            arrow(c, 560 + math.cos(a) * 40, 1110 + math.sin(a) * 52, x, y, colr='#ffffff', w=10, alpha=int(220 * kk))
        c.drawPath(_shell_outline(560, 1110, 4.6, -6), P(color=col(HOT, int(255 * kk)), stroke=12))
        label_pill(c, 'TRAPPED', 540, 1560, size=50, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def _shell_outline(x, y, s, rot):
    p = kernel_path(1.0); m = skia.Matrix(); m.setTranslate(x, y); m.preRotate(rot); m.preScale(s, s)
    p.transform(m); return p

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.3, 'boing'), (t1 + 0.6, 'pop')]

# ---------- 4: Pressure ~9x, bursts at ~180 C ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, '#ff5c85', '#ffd1dc')
    heat_waves(c, 300, 820, 1640, t, k=1.0)
    burst = t1 + 2.6
    if t < burst:
        pr = ease_in_out(prog(t, t0, 3.0))
        sh = math.sin(t * 60) * 6 * pr
        popcorn_kernel(c, 560 + sh, 1250, 3.2, rot=-6, heat=0.8, swell=pr * (1 + prog(t, t1, 2.6)))
    else:
        u = prog(t, burst, 0.25)
        c.drawCircle(560, 1250, 420 * u, P(color=col('#ffffff', int(200 * (1 - u))), blur=20))
        popcorn_puff(c, 560, 1230, 3.2, k=ease_back(prog(t, burst, 0.3)), seed=5)
        label_pill(c, 'BANG', 540, 1560, size=56, k=ease_back(prog(t, burst + 0.1, 0.3)), fill=NAVY, hi=HOT)
    k = ease_back(prog(t, t0, 0.5))
    if k > 0:
        c.save(); c.translate(300, 820); c.scale(k * 0.75, k * 0.75)
        gauge(c, 0, 0, 150, 0.1 + 0.8 * ease_in_out(prog(t, t0 + 0.3, 2.5)), label='~9x')
        c.restore()
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.1, 0.5))
        if kk > 0:
            c.save(); c.translate(820, 1000); c.scale(kk * 0.75, kk * 0.75)
            thermometer(c, 0, 0, 1.0, level=lerp(0.4, 0.95, prog(t, t1 + 0.2, 2.4)))
            c.restore()
            label_pill(c, '180°C / 356°F', 780, 1100, size=40, k=kk, fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'click'), (t1 + 0.1, 'pop'), (t1 + 2.6, 'boing'), (t1 + 2.7, 'pop')]

# ---------- 5: Starch foam ~40x bigger (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, '#2f9bff', '#bfe3ff')
    g = ease_out(prog(t, t0, 2.4))
    popcorn_kernel(c, 230, 1380, 0.9, rot=-10)
    label_pill(c, 'kernel', 230, 1500, size=38, k=ease_back(prog(t, t0 + 0.2, 0.4)), fill=NAVY, hi=NAVY)
    popcorn_puff(c, 640, 1130, lerp(0.8, 4.2, g), rot=t * 4, seed=7)
    # foam bubbles visible inside the flake
    if g > 0.6:
        rnd = random.Random(2)
        for i in range(16):
            bx, by = 640 + rnd.uniform(-120, 120), 1130 + rnd.uniform(-100, 100)
            c.drawCircle(bx, by, rnd.uniform(8, 16), P(color=col('#e2c48c', int(120 * prog(g, 0.6, 0.4))), stroke=3))
    label_pill(c, '~40x BIGGER', 640, 760, size=54, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'starch FOAM', 640, 1500, size=44, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=GOLD)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.6, 'ding'), (t1 + 0.2, 'pop')]

# ---------- 6: Regular corn: leaky shell, no pop ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    kitchen(c, '#7fb8ff', '#e6f2ff')
    heat_waves(c, 140, 940, 1640, t, k=0.8)
    # left: popcorn (sealed) pops; right: field corn leaks steam
    pt = t0 + 3.0
    if t < pt:
        popcorn_kernel(c, 300 + math.sin(t * 50) * 3 * prog(t, t0, 2), 1180, 2.6, rot=-5, heat=0.7)
    else:
        popcorn_puff(c, 300, 1160, 2.4, k=ease_back(prog(t, pt, 0.3)), seed=2)
    c.save(); c.translate(780, 1180); c.scale(2.6, 2.6)
    p = kernel_path(1.0)
    c.drawPath(p, lin(c, (0, -46, 0, 50), [col('#ffe066'), col('#e8b400')]))
    c.drawPath(p, P(color=col('#b58a00'), stroke=2.5))
    c.drawOval(skia.Rect(-20, 30, 20, 62), P(color=col('#f6e2a8')))
    rnd = random.Random(4)
    for i in range(10):  # tiny pores in the hull
        c.drawCircle(rnd.uniform(-24, 24), rnd.uniform(-30, 30), 2.2, P(color=col('#8a6a00', 200)))
    c.restore()
    lk = prog(t, t0 + 0.8, 0.6)
    for j, (dx, dy) in enumerate(((-50, -100), (40, -110), (70, -40))):
        steam_wisp(c, 780 + dx, 1180 + dy, t + j * 0.3, k=lk, seed=j, h=160)
    label_pill(c, 'popcorn: SEALED', 300, 860, size=40, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'regular corn: LEAKY', 760, 1460, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'NO pop', 780, 860, size=44, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.8, 'whoosh'), (t0 + 1.4, 'pop'), (t0 + 2.4, 'click'), (t0 + 3.0, 'pop')]

# ---------- 7: Wild part: the pop sound is escaping steam ----------
def bottle(c, x, y, s=1.0, cork_off=0.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-70, 220); p.lineTo(-70, -10); p.cubicTo(-70, -80, -24, -90, -24, -150); p.lineTo(-24, -230)
    p.lineTo(24, -230); p.lineTo(24, -150); p.cubicTo(24, -90, 70, -80, 70, -10); p.lineTo(70, 220); p.close()
    c.drawPath(p, lin(c, (-70, 0, 70, 0), [col('#8fd0ff'), col('#d6efff'), col('#5fa8e0')], vertical=False, pos=[0, 0.35, 1]))
    c.drawPath(p, P(color=col(NAVY), stroke=5))
    c.drawRoundRect(skia.Rect(-60, 20, 60, 120), 14, 14, P(color=col('#ffffff', 230)))
    cy = -250 - 260 * cork_off
    c.save(); c.translate(0, cy); c.rotate(160 * cork_off)
    c.drawRoundRect(skia.Rect(-22, -40, 22, 30), 8, 8, lin(c, (0, -40, 0, 30), [col('#e2b77a'), col('#b8844a')]))
    c.restore()
    if cork_off > 0:
        steam_wisp(c, 0, -240, t, k=1 - cork_off * 0.5, seed=3, h=120)
    c.restore()

def s7(c, t, D, cues):
    t0 = cues[0]['start']
    kitchen(c, '#1b2a4a', '#3a5fa8')
    # kernel bursting with a jet of steam + sound rings
    bt = t0 + 1.4
    if t < bt:
        popcorn_kernel(c, 330 + math.sin(t * 60) * 4, 1150, 2.6, rot=-5, heat=0.8)
    else:
        popcorn_puff(c, 330, 1150, 2.3, k=ease_back(prog(t, bt, 0.3)), seed=4)
        steam_wisp(c, 330, 1030, t, k=1 - prog(t, bt + 1.2, 1.0), seed=1, h=220)
        sound_rings(c, 330, 1150, t, bt, n=3, colr='#ffd23f', both=True)
    label_pill(c, 'NOT the shell cracking', 540, 720, size=40, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'escaping STEAM', 330, 1460, size=42, k=ease_back(prog(t, bt + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    ck = ease_back(prog(t, t0 + 2.4, 0.5))
    if ck > 0:
        co = ease_out(prog(t, t0 + 3.4, 0.7))
        bottle(c, 780, 1260, 0.9 * ck, cork_off=co, t=t)
        if co > 0: sound_rings(c, 780, 1030, t, t0 + 3.4, n=3, colr='#ffd23f', both=True)
        label_pill(c, 'like a CORK', 780, 1520, size=42, k=ck, fill=NAVY, hi=GOLD)

def s7_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.4, 'pop'), (t0 + 1.8, 'pop'), (t0 + 2.4, 'pop'), (t0 + 3.4, 'whoosh')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    kitchen(c)
    # bowl of popcorn
    c.drawOval(skia.Rect(240, 1180, 840, 1260), P(color=col('#0b1a3a', 50), blur=12))
    rnd = random.Random(9)
    for i in range(14):
        popcorn_puff(c, 540 + rnd.uniform(-230, 230), 1110 + rnd.uniform(-90, 40) - abs(rnd.uniform(-1, 1)) * 40, 0.9, rot=rnd.uniform(0, 360), seed=i)
    bp = skia.Path(); bp.moveTo(230, 1120); bp.cubicTo(250, 1330, 830, 1330, 850, 1120); bp.close()
    c.drawPath(bp, lin(c, (0, 1120, 0, 1300), [col('#ff5c85'), col('#e8264f')]))
    for j in range(4):
        c.drawLine(300 + j * 160, 1130, 320 + j * 150, 1270, P(color=col('#ffffff', 200), stroke=26))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.4, 0.4)) * fo
    if k0 > 0: label_pill(c, 'trapped STEAM = POP', 540, 700, size=46, k=k0, fill=NAVY, hi=HOT)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why SNOW is white', 540, 820, size=42, k=kk, fill=NAVY, hi=SKYB)
        for i in range(5):
            snowflake(c, 200 + i * 170, 950 + 20 * math.sin(t * 2 + i), 22 * kk, t, seed=i)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why does popcorn pop?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why does popcorn pop?', 'Why does POPCORN pop?'),
            ('Every kernel is a tiny pressure cooker.', 'A tiny PRESSURE cooker')], tail=0.9),
        dict(name='inside', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Inside a hard, sealed shell sits soft starch and a little water, about fourteen percent.', 'Starch + about 14% WATER')], tail=1.4),
        dict(name='steam', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Heat it, and that water turns into steam.', 'Water turns to STEAM'),
            ('But the shell is so tough and watertight, the steam is trapped.', 'The steam is TRAPPED')], tail=0.9),
        dict(name='pressure', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Pressure climbs to about nine times normal air pressure.', 'About 9x AIR pressure'),
            ('At around a hundred and eighty degrees Celsius, the shell bursts.', 'BURSTS at about 180°C')], tail=1.4),
        dict(name='foam', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('The soft starch puffs into a foam, around forty times bigger, and sets as it cools.', 'Starch FOAM, ~40x bigger'),
            ("That's the fluffy white part you eat.", 'The fluffy part you EAT')], tail=1.0),
        dict(name='leaky', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Regular corn can't do this. Its shell is leaky, so the steam just seeps out.", 'Leaky shell = NO pop')], tail=1.6),
        dict(name='sound', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: the pop isn't the shell cracking. It's the steam escaping, like a cork from a bottle.", 'The POP = escaping STEAM')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So popcorn pops because trapped steam blows it open.', 'Trapped STEAM blows it open'),
            ('Next: why snow is white.', 'Next: why SNOW is white'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
