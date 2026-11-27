"""Episode 50 (EN, general audience): Why does bread rise?
Facts checked (Exploratorium "Science of Cooking: Bread"; Exploratorium "Yeast temperature"; WSU Ask Dr. Universe
"Why does bread expand in the oven?" (2026); Modernist Cuisine "The role of yeast in bread"; BAKERpedia "Yeast kill"):
- Baker's yeast (Saccharomyces cerevisiae) is a single-celled fungus; a packet of dry yeast holds billions of cells.
- In dough, yeast feeds on sugars (released from the flour's starch) and ferments them into carbon dioxide gas and
  ethanol (alcohol).
- Kneading flour + water develops gluten (glutenin + gliadin proteins), a stretchy elastic network that traps the gas
  in countless small bubbles, so the dough inflates (it typically about doubles while proofing).
- In the oven the trapped gas expands and water/alcohol turn to vapour -> a last burst of rising ("oven spring");
  yeast dies around 140 F / 60 C; proteins and starch set, so the bubbles become the holes of the crumb.
- Most of the alcohol evaporates during baking.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def kitchen(c, t, y=1450):
    sky(c, '#cfeaff', '#7cc4ff')
    # soft tiles on the wall
    for i in range(7):
        for j in range(9):
            x0 = i * 160 - 20 + (80 if j % 2 else 0); y0 = 640 + j * 90
            if y0 > y - 40: continue
            c.drawRoundRect(skia.Rect(x0 + 6, y0 + 6, x0 + 154, y0 + 84), 12, 12, P(color=col('#ffffff', 40)))
    c.drawRect(skia.Rect(0, y, W, y + 40), lin(c, (0, y, 0, y + 40), [col('#ffffff'), col('#dfe7f2')]))
    c.drawRect(skia.Rect(0, y + 40, W, H), lin(c, (0, y + 40, 0, H), [col('#9fb3cc'), col('#6f86a6')]))
    c.drawLine(0, y + 40, W, y + 40, P(color=col(NAVY, 90), stroke=4))

def dough_bubbles_rising(c, x, y, s, t, k, seed=3):
    """bubbles escaping straight up from a gluten-free mix (k 0..1 = strength)."""
    rnd = random.Random(seed)
    for i in range(14):
        ph = (t * rnd.uniform(0.35, 0.6) + rnd.random()) % 1.0
        bx = x + rnd.uniform(-220, 220) * s + 12 * math.sin(t * 2 + i)
        by = y - ph * 520 * s
        gas_bubble(c, bx, by, rnd.uniform(10, 20) * s, alpha=int(230 * k * (1 - ph)), colr='#5fb4ff')

# ---------- 1: Hook (cold open: dough already swelling) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    kitchen(c, t)
    rise = 0.15 + 0.85 * ease_in_out(prog(t, 0.0, 2.6))
    dough(c, 540, 1440, 1.25, t, rise=rise)
    label_pill(c, 'DOUBLES in size', 540, 700, size=50, k=ease_back(prog(t, 0.5, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        rnd = random.Random(4)
        for i in range(7):
            k = ease_back(prog(t, t1 + 0.3 + i * 0.12, 0.4))
            yeast_cell(c, rnd.uniform(160, 900), rnd.uniform(880, 1050) + 10 * math.sin(t * 2 + i), 34 * k, t, seed=i)
        label_pill(c, 'LIVING cells', 540, 1560, size=50, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=GOLD)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.5, 'pop'), (t1 + 0.3, 'sparkle'), (t1 + 1.2, 'pop')]

# ---------- 2: Yeast = a fungus, billions per packet ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    kitchen(c, t)
    dough(c, 540, 1440, 0.9, t, rise=0.5)
    lk = ease_out(prog(t, t0 - 0.2, 0.6))
    if lk > 0:
        def inner(cc):
            cc.drawRect(skia.Rect(0, 0, W, H), P(color=col('#f6ead0')))
            rnd = random.Random(9)
            for i in range(26):
                yx = rnd.uniform(220, 860); yy = rnd.uniform(760, 1340)
                yeast_cell(cc, yx + 8 * math.sin(t + i), yy + 8 * math.cos(t * 0.8 + i), rnd.uniform(34, 52), t,
                           bud=prog(t, t0 + 1.0 + i * 0.05, 1.2) * (1 if i % 3 == 0 else 0), seed=i)
        magnifier(c, 540, 1050, 340 * lk, inner, t)
    label_pill(c, 'YEAST = a fungus', 540, 660, size=48, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'BILLIONS per packet', 540, 1520, size=46, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 - 0.2, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 2.4, 'pop')]

# ---------- 3: Yeast eats sugar -> CO2 (+ a bit of alcohol) ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f6ead0', '#e9d4a8')
    yeast_cell(c, 540, 1080, 170, t, seed=2)
    # sugar coming in from the left
    for i in range(3):
        st = t0 + 0.4 + i * 0.7
        ph = prog(t, st, 1.2)
        if 0 < ph < 1:
            sugar_cubes(c, lerp(80, 430, ease_in_out(ph)), 1080 + (i - 1) * 90, 0.45 * (1 - 0.7 * ph), t, alpha=255 * (1 - prog(ph, 0.8, 0.2)))
    label_pill(c, 'SUGAR in', 230, 760, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        for i in range(8):
            ph = ((t - t1) * 0.55 + i / 8) % 1.0
            x = lerp(770, 915, ph); y = 1080 + (i % 4 - 1.5) * 140 * (0.5 + ph)
            co2_molecule(c, x, y - ph * 120, 30, t, seed=i, alpha=255 * min(1, (t - t1) * 2) * (1 - prog(ph, 0.85, 0.15)))
        label_pill(c, 'CO2 GAS out', 760, 760, size=46, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, '+ a bit of alcohol', 540, 1460, size=40, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.4, 'whoosh'), (t1 + 0.2, 'pop'), (t1 + 1.6, 'click')]

# ---------- 4: Gluten traps the gas (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f6ead0', '#e9d4a8')
    # left half of the line: gas escapes from a loose mix
    esc = 1 - prog(t, t1 - 0.2, 0.5)
    if esc > 0:
        c.saveLayerAlpha(None, int(255 * esc))
        c.drawRoundRect(skia.Rect(240, 1180, 840, 1440), 60, 60, P(color=col(DOUGH)))
        c.drawRoundRect(skia.Rect(240, 1180, 840, 1440), 60, 60, P(color=col('#c9a462'), stroke=5))
        dough_bubbles_rising(c, 540, 1240, 1.0, t, 1.0)
        c.restore()
        label_pill(c, 'gas ESCAPES', 540, 720, size=48, k=ease_back(prog(t, t0 + 0.6, 0.4)) * esc, fill=NAVY, hi=HOT)
    if t > t1 - 0.2:
        nk = ease_out(prog(t, t1 - 0.1, 0.8))
        st = prog(t, t1 + 1.2, 2.5)
        x0, x1 = lerp(540, 150, nk), lerp(540, 930, nk)
        c.save(); cl = skia.Path(); cl.addRoundRect(skia.Rect(140, 760, 940, 1500), 70, 70); c.clipPath(cl, doAntiAlias=True)
        c.drawRoundRect(skia.Rect(140, 760, 940, 1500), 70, 70, P(color=col('#fbeccb', int(255 * nk))))
        gluten_net(c, x0, 800, x1, 1460, t, stretch=st, alpha=int(230 * nk))
        rnd = random.Random(5)
        for i in range(10):
            bx = lerp(x0, x1, (i % 5 + 0.5) / 5) + rnd.uniform(-30, 30); by = 880 + (i // 5) * 330 + rnd.uniform(-40, 40) + 120
            gas_bubble(c, bx, by, (18 + 46 * ease_out(st)) * nk, alpha=240, colr='#5fb4ff')
        c.restore()
        c.drawRoundRect(skia.Rect(140, 760, 940, 1500), 70, 70, P(color=col('#c9a462', int(255 * nk)), stroke=6))
        label_pill(c, 'GLUTEN net', 540, 690, size=52, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'like BALLOONS', 540, 1570, size=46, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t1 + 0.2, 'ding'), (t1 + 1.2, 'whoosh'), (t1 + 2.0, 'pop')]

# ---------- 5: The oven ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, t, y=1500)
    g = ease_in_out(prog(t, t0, 1.5))
    oven(c, 470, 1080, 1.0, glow=g, t=t)
    # dough / loaf inside the oven window (window ~ x 190..750, y 920..1320)
    c.save(); cl = skia.Path(); cl.addRoundRect(skia.Rect(190, 920, 750, 1320), 22, 22); c.clipPath(cl, doAntiAlias=True)
    rise = 0.45 + 0.5 * ease_out(prog(t, t0 + 1.0, 2.5))
    bake = prog(t, t1 + 0.3, 2.0)
    if bake < 1:
        c.saveLayerAlpha(None, int(255 * (1 - bake)))
        dough(c, 470, 1238, 0.62 + 0.08 * rise, t, rise=rise)
        c.restore()
    if bake > 0:
        c.saveLayerAlpha(None, int(255 * bake)); bread_loaf(c, 470, 1238, 0.62, t=t); c.restore()
    c.restore()
    thermometer(c, 910, 1360, 1.15, level=0.15 + 0.75 * ease_in_out(prog(t, t0 + 0.5, (t1 + 1.0) - (t0 + 0.5))))
    label_pill(c, 'gas EXPANDS', 470, 690, size=48, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, '~140°F: yeast DIES', 470, 1570, size=44, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'click'), (t0 + 1.2, 'pop'), (t1 + 0.8, 'pop')]

# ---------- 6: Holes = frozen bubbles ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    kitchen(c, t)
    ck = ease_in_out(prog(t, t0 + 0.2, 0.9))
    slide = 120 * ck
    bread_loaf(c, 540 - slide * 0.6, 1440, 1.25, cut=ck)
    # zoom ring on one hole
    zk = ease_back(prog(t, t0 + 1.6, 0.5))
    if zk > 0:
        hx, hy = 470, 1180
        c.drawCircle(hx, hy, 60 * zk, P(color=col(HOT), stroke=8))
        arrow(c, hx + 80, hy - 220, hx + 34, hy - 70, colr=HOT, w=12, alpha=int(255 * min(1, zk)))
        label_pill(c, 'old GAS bubble', 600, 860, size=46, k=zk, fill=NAVY, hi=HOT)
    label_pill(c, 'set by the HEAT', 540, 1570, size=44, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=GOLD)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.6, 'pop'), (t0 + 2.6, 'pop')]

# ---------- 7: Wild part: alcohol bakes off ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, t)
    on_bread = prog(t, t1 - 0.3, 0.6)
    if on_bread < 1:
        c.saveLayerAlpha(None, int(255 * (1 - on_bread)))
        dough(c, 540, 1440, 1.2, t, rise=0.8 + 0.05 * math.sin(t * 2))
        rnd = random.Random(7)
        for i in range(6):
            yeast_cell(c, rnd.uniform(220, 860), rnd.uniform(1150, 1330), 26, t, seed=i)
        c.restore()
    if on_bread > 0:
        c.saveLayerAlpha(None, int(255 * on_bread)); bread_loaf(c, 540, 1440, 1.2, t=t, steam=1.0); c.restore()
        for i in range(5):
            ph = ((t - t1) * 0.45 + i / 5) % 1.0
            gas_wisp(c, 300 + i * 120, 1000 - ph * 300, 1.2, t, seed=i, alpha=int(170 * (1 - ph) * on_bread), colr='#bfe3ff')
    label_pill(c, 'dough makes ALCOHOL', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'it bakes AWAY', 540, 1570, size=48, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 1.0, 'pop'), (t1 - 0.3, 'whoosh'), (t1 + 0.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    kitchen(c, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    bread_loaf(c, 540, 1440, 0.9 + 0.02 * math.sin(t * 2), cut=0, t=t, steam=0.6)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'yeast GAS + gluten net', 540, 700, size=44, k=k0, fill=NAVY, hi=GOLD)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: MOON craters', 540, 820, size=44, k=kk, fill=NAVY, hi=HOT)
        gray_moon(c, 540, 1010, 110 * kk, t)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why does bread rise?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why does bread dough double in size?', 'Why does DOUGH rise?'),
            ("Because it's full of living cells, making gas.", "It's full of LIVING cells")], tail=0.9),
        dict(name='yeast', draw=s2, sfx_fn=s2_sfx, lines=[
            ("They're yeast, a single-celled fungus. A single packet holds billions of them.", 'YEAST: billions per packet')], tail=0.9),
        dict(name='eat', draw=s3, sfx_fn=s3_sfx, lines=[
            ('In the dough, yeast feeds on sugars from the flour,', 'Yeast eats SUGARS'),
            ('and gives off carbon dioxide gas, plus a little alcohol.', 'Out comes CO2 GAS')], tail=1.0),
        dict(name='gluten', draw=s4, sfx_fn=s4_sfx, trans='punch', lines=[
            ('But gas on its own would just escape.', 'Gas alone would ESCAPE'),
            ('Kneading builds gluten, a stretchy protein net that traps it like balloons.', 'GLUTEN traps it like balloons')], tail=1.1),
        dict(name='oven', draw=s5, sfx_fn=s5_sfx, lines=[
            ('In the oven, the heat makes the gas expand one last time.', 'Heat: the gas EXPANDS'),
            ('At about a hundred and forty degrees, the yeast dies.', '~140°F: yeast DIES')], tail=1.0),
        dict(name='holes', draw=s6, sfx_fn=s6_sfx, lines=[
            ('The heat sets the dough, so every hole in your slice is a gas bubble, frozen in place.', 'Every HOLE was a bubble')], tail=1.2),
        dict(name='alcohol', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: rising dough really does make alcohol.", 'Dough makes ALCOHOL'),
            ('Almost all of it evaporates in the oven.', 'It bakes AWAY')], tail=1.1),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So yeast makes the gas, and gluten holds it in.', 'Yeast GAS + gluten net'),
            ('Next: why the Moon is covered in craters.', 'Next: MOON craters'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
