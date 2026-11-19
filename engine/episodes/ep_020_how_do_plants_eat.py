"""Episode 20 (EN, general audience): How do plants eat?
Facts checked: plants make their own food by photosynthesis: roots take up water (carried up through xylem),
CO2 enters through leaf pores (stomata), chloroplasts use light energy to turn water + CO2 into sugar (glucose),
oxygen is released. Sugar is moved around (phloem) and used for energy and as building material (cellulose = wood,
fruit, starch stores). Soil supplies minerals (nitrogen, phosphorus, potassium ...), not the bulk of the mass.
Van Helmont (1600s): willow in a pot for 5 years gained about 164 lb, the soil lost only about 2 oz. Today we know
most of a plant's dry mass is carbon taken from CO2 in the air.
"""
import math, random
from lib import *

SKY = ('#2f9bff', '#cdeeff', '#7cc6ff')
WATER = '#2f9bff'

def bg_day(c, t):
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    sunbeams(c, 170, 760, t, a=26)
    sun(c, 170, 760, 100, t)
    clouds(c, t, seed=5, n=2, y0=700, y1=860, a=200)

def drift_co2(c, t, t0, n, x0, y0, x1, y1, seed=0, r=20, dur=2.2, alpha=255):
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + i * dur / n
        u = ((t - st) / dur) % 1.0 if t > st else -1
        if u < 0: continue
        sx, sy = x0 + rnd.uniform(-80, 80), y0 + rnd.uniform(-160, 160)
        x = lerp(sx, x1, ease_in_out(u)); y = lerp(sy, y1, ease_in_out(u)) + math.sin(u * 6 + i) * 20
        a = alpha * min(1, u * 5) * min(1, (1 - u) * 4)
        co2_molecule(c, x, y, r, t, seed=i, alpha=a)

# ---------- 1: Hook (cold open: plant already growing, CO2 streaming in) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    bg_day(c, t)
    soil(c, 1380, t)
    gk = 0.75 + 0.25 * ease_out(prog(t, 0, 2.5))
    plant(c, 560, 1380, gk * 1.25, t, seed=1, roots=True, root_k=1.0, leaves=6)
    drift_co2(c, t, 0.0, 6, 880, 820, 600, 980, seed=1, r=22)
    # crossed-out mouth icon
    k = ease_back(prog(t, 0.15, 0.4))
    if k > 0 and t < t1 + 0.2:
        c.save(); c.translate(250, 1180); c.scale(k, k)
        c.drawCircle(0, 0, 80, P(color=col('#ffffff', 235)))
        m = skia.Path(); m.moveTo(-40, -6); m.quadTo(0, 34, 40, -6); m.quadTo(0, 14, -40, -6); m.close()
        c.drawPath(m, P(color=col('#1b2a4a')))
        c.drawLine(-52, -52, 52, 52, P(color=col('#ff5c85'), stroke=14))
        c.restore()
        label_pill(c, 'no MOUTH', 250, 1310, size=42, k=k, fill='#1b2a4a', hi='#ff5c85')
    if t > t1:
        for i, (lbl, hx, x) in enumerate((('AIR', '#7d8a9c', 200), ('WATER', WATER, 440), ('LIGHT', '#e0a800', 680))):
            kk = ease_back(prog(t, t1 + 0.9 + i * 0.35, 0.4))
            label_pill(c, lbl, x, 1500, size=50, k=kk, fill=hx, hi=hx)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.15, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.25, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 2: Roots drink water, up through pipes like a straw ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    gy = 960
    soil(c, gy, t, seed=7)
    rk = ease_out(prog(t, 0, 1.4))
    x = 470
    plant(c, x, gy, 0.6, t, seed=3, roots=False, leaves=4)
    roots = root_paths(x, gy, 1.9, seed=5)
    for (p, a, m, e) in roots:
        meas = skia.PathMeasure(p, False); L = meas.getLength(); seg = skia.Path(); meas.getSegment(0, L * rk, seg, True)
        c.drawPath(seg, P(color=col('#f3e2c0'), stroke=18)); c.drawPath(seg, P(color=col('#c9a877'), stroke=5))
    # water drops in soil moving to root tips, then up the stem
    rnd = random.Random(2)
    for i in range(14):
        p, a, m, e = roots[i % len(roots)]
        st = t0 + 0.2 + i * 0.28
        u = prog(t, st, 1.6)
        if u <= 0: continue
        meas = skia.PathMeasure(p, False); L = meas.getLength()
        if u < 0.55:
            pos, _ = meas.getPosTan(L * (1 - u / 0.55))
            xx, yy = pos.x(), pos.y()
        else:
            v = (u - 0.55) / 0.45
            xx, yy = x + math.sin(t * 1.3 + 3) * 10 * 0.6 * v, gy - v * 300
        if u < 1:
            raindrop(c, xx, yy, 13, t, seed=i, face_on=False)
    # stem cut-away: pipe highlight
    if t > t1 - 0.3:
        k = ease_back(prog(t, t1, 0.5))
        def inner(cc):
            cc.drawRect(skia.Rect(0, 0, W, H), P(color=col('#e9ffe0')))
            for px in (-70, 0, 70):
                cc.drawRoundRect(skia.Rect(780 + px - 22, 700, 780 + px + 22, 1400), 22, 22, P(color=col('#bfe9ff')))
                cc.drawRoundRect(skia.Rect(780 + px - 22, 700, 780 + px + 22, 1400), 22, 22, P(color=col('#3f9a2e'), stroke=6))
                for j in range(5):
                    yy = 1400 - ((t * 260 + j * 150 + px * 3) % 700)
                    raindrop(cc, 780 + px, yy, 12, t, seed=j, face_on=False)
        magnifier(c, 780, 1050, 200 * k, inner, t)
        c.drawLine(x + 20, 800, 780 - 200 * k, 1050, P(color=col('#ffffff', int(200 * k)), stroke=6))
        label_pill(c, 'tiny PIPES', 780, 1300, size=46, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill='#1b2a4a', hi=WATER)

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'], 'pop'), (cues[1]['start'] + 0.6, 'click')]

# ---------- 3: Leaf pores (stomata) let CO2 in ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9ffe0', '#bff0a8')
    # leaf underside texture: cells
    rnd = random.Random(3)
    for r_ in range(-1, 12):
        for q in range(-1, 7):
            x = q * 180 + (90 if r_ % 2 else 0); y = 600 + r_ * 110
            c.drawRoundRect(skia.Rect(x - 84, y - 50, x + 84, y + 50), 40, 40, P(color=col('#cdf2b4')))
            c.drawRoundRect(skia.Rect(x - 84, y - 50, x + 84, y + 50), 40, 40, P(color=col('#8fd06f'), stroke=5))
    ok = 0.25 + 0.75 * ease_in_out(prog(t, t0 + 0.6, 1.0))
    zoom = 0.8 + 0.25 * ease_in_out(prog(t, 0, 2.0))
    stoma(c, 540, 1120, zoom * 1.25, ok, t)
    for i, (x, y, s_) in enumerate(((200, 760, 0.5), (860, 760, 0.45), (180, 1480, 0.5), (880, 1450, 0.5))):
        stoma(c, x, y, s_, ok * (0.8 + 0.2 * math.sin(i)), t)
    label_pill(c, 'STOMATA', 540, 1440, size=52, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill='#2f7d24', hi='#2f7d24')
    if t > t1 - 0.2:
        rnd = random.Random(8)
        for i in range(8):
            st = t1 - 0.2 + i * 0.3
            u = prog(t, st, 1.4)
            if u <= 0 or u >= 1: continue
            sx = rnd.choice((120, 960)); sy = rnd.uniform(700, 1000)
            x = lerp(sx, 540, ease_in_out(u)); y = lerp(sy, 1120, ease_in_out(u))
            co2_molecule(c, x, y, 26 * (1 - 0.5 * u), t, seed=i, alpha=255 * min(1, (1 - u) * 3))
        label_pill(c, 'CO2 in', 540, 760, size=50, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill='#5b6476')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 0.4, 'pop')]

# ---------- 4: Chloroplast kitchen: light + water + CO2 -> sugar + oxygen ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#2c5a3a', mid='#21403f')
    cx, cy = 540, 1100
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    on = ease_out(prog(t, t0 + 0.3, 0.6))
    c.drawCircle(cx, cy, 420, rad(cx, cy, 420, [col('#ffe14d', int(70 * on * (0.7 + 0.3 * pulse))), col('#ffe14d', 0)]))
    # chloroplast (same look as ep_019)
    r = 260
    c.save(); c.translate(cx, cy); c.rotate(math.sin(t * 1.3) * 3)
    c.drawOval(skia.Rect(-r, -r * 0.55, r, r * 0.55), rad(-r * 0.3, -r * 0.2, r * 1.3, [col('#b6f08a'), col('#4fbf3a'), col('#2f8a25')], [0, 0.5, 1]))
    c.drawOval(skia.Rect(-r, -r * 0.55, r, r * 0.55), P(color=col('#1f6b18', 200), stroke=r * 0.06))
    for i in range(5):
        gx = -r * 0.6 + i * r * 0.3
        for j in range(3):
            c.drawRoundRect(skia.Rect(gx - r * 0.1, -r * 0.18 + j * r * 0.13, gx + r * 0.1, -r * 0.1 + j * r * 0.13), r * 0.04, r * 0.04, P(color=col('#1f6b18', 190)))
    c.restore()
    # inputs flying in
    for i in range(3):
        u = prog(t, t0 + 0.2 + i * 0.4, 1.0)
        if 0 < u < 1:
            e = ease_in_out(u)
            if i == 0:   # light beam
                arrow(c, 120, 700, lerp(120, cx - 180, e), lerp(700, cy - 120, e), colr='#ffe14d', w=16)
            elif i == 1:
                raindrop(c, lerp(130, cx - 120, e), lerp(1500, cy + 60, e), 26, t, seed=1, face_on=False)
            else:
                co2_molecule(c, lerp(900, cx + 140, e), lerp(720, cy - 60, e), 28, t)
    for i, (lbl, x, y, hx) in enumerate((('light', 200, 760, '#e0a800'), ('water', 200, 1450, WATER), ('CO2', 830, 760, '#7d8a9c'))):
        kk = ease_back(prog(t, t0 + 0.4 + i * 0.4, 0.4)) * (1 - prog(t, t1, 0.3))
        label_pill(c, lbl, x, y, size=46, k=kk, fill=hx, hi=hx)
    if t > t1:
        ks = ease_back(prog(t, t1 + 0.2, 0.5))
        u = ease_out(prog(t, t1 + 0.2, 1.0))
        sugar_cubes(c, lerp(cx, 780, u), lerp(cy, 1450, u), 0.9 * ks, t, rot=math.sin(t * 2) * 5)
        label_pill(c, 'SUGAR', 780, 1580 - 40, size=46, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill='#ff5c85', hi='#ff5c85')
        for i in range(6):
            v = prog(t, t1 + 1.2 + i * 0.25, 1.6)
            if 0 < v < 1:
                oxygen_dot(c, lerp(cx - 60 + i * 20, 230 + i * 30, ease_out(v)), lerp(cy - 60, 720 + (i % 3) * 40, ease_out(v)), 16, t, alpha=255 * min(1, (1 - v) * 3))
        label_pill(c, 'OXYGEN out', 280, 1450, size=44, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill='#1aa6c9', hi='#1aa6c9')

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 0.8, 'pop'), (cues[0]['start'] + 1.2, 'pop'),
                             (cues[1]['start'] + 0.2, 'sparkle'), (cues[1]['start'] + 1.4, 'whoosh')]

# ---------- 5: Sugar becomes wood and fruit; soil = vitamins ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg_day(c, t)
    hills(c, 1500, t=t, trees=False, flowers=False)
    # apple tree built from sugar
    tx, ty = 560, 1470
    g = ease_out(prog(t, t0 + 0.2, 1.4))
    leafy_tree(c, tx, ty, 0.6 + 0.4 * g, t, seed=2)
    for i, (ax, ay) in enumerate(((-120, -330), (60, -420), (150, -300), (-40, -230), (-170, -440))):
        k = ease_back(prog(t, t0 + 1.0 + i * 0.2, 0.4))
        if k > 0:
            s_ = (0.6 + 0.4 * g)
            px, py = tx + ax * s_, ty + ay * s_
            c.drawCircle(px, py, 26 * k, rad(px - 8, py - 8, 34, [col('#ff8a8a'), col('#e8382f')]))
            c.drawLine(px, py - 24 * k, px + 4, py - 38 * k, P(color=col('#6b4423'), stroke=5))
    # sugar streaming up the trunk
    for i in range(5):
        v = ((t - t0) * 0.6 + i / 5) % 1.0
        if t > t0:
            sugar_cubes(c, tx + math.sin(v * 9) * 6, lerp(ty - 20, ty - 300, v), 0.22, t, alpha=255 * min(1, v * 5) * min(1, (1 - v) * 5))
    label_pill(c, 'sugar → WOOD + FRUIT', 540, 760, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)) * (1 - prog(t, t1, 0.3)), fill='#1b2a4a', hi='#e8382f')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.1, 0.5))
        # vitamin-pill bottle next to tree
        c.save(); c.translate(860, 1380); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-60, -110, 60, 70), 22, 22, lin(c, (0, -110, 0, 70), [col('#ffffff'), col('#dfe6ef')]))
        c.drawRoundRect(skia.Rect(-66, -150, 66, -105), 12, 12, P(color=col('#ff5c85')))
        c.drawRoundRect(skia.Rect(-46, -70, 46, 20), 10, 10, P(color=col('#ffd23f')))
        text_block(c, 'N P K', 0, -26, size=26, fill='#1b2a4a', stroke='#ffd23f')
        c.drawRoundRect(skia.Rect(-60, -110, 60, 70), 22, 22, P(color=col('#b9c4d3'), stroke=4))
        c.restore()
        label_pill(c, 'soil = VITAMINS', 540, 760, size=50, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill='#1b2a4a', hi='#c9773a')

def s5_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh')] + [(t0 + 1.0 + i * 0.2, 'pop') for i in range(5)] + [(cues[1]['start'] + 0.1, 'pop'), (cues[1]['start'] + 0.5, 'click')]

# ---------- 6: Wild part: van Helmont's willow ----------
def scale_bar(c, x, y, frac, label, hx, k=1.0):
    if k <= 0: return
    c.drawRoundRect(skia.Rect(x - 50, y - 520, x + 50, y), 24, 24, P(color=col('#ffffff', 60)))
    h = 520 * frac * k
    c.drawRoundRect(skia.Rect(x - 50, y - max(h, 8), x + 50, y), 24, 24, lin(c, (0, y - 520, 0, y), [col(mix_hx(hx, '#ffffff', 0.35)), col(hx)]))
    label_pill(c, label, x, y + 60, size=38, k=k, fill=hx, hi=hx)

def s6(c, t, D, cues):
    t0, t1, t2 = cues[0]['start'], cues[1]['start'], cues[2]['start']
    sky(c, '#fff4dc', '#ffe0b0')
    # year counter
    years = int(clamp((t - t0 - 0.6) / 2.4) * 5)
    gx = 380; py = 1430
    g = ease_in_out(prog(t, t0 + 0.6, 2.6))
    # pot
    pp = skia.Path(); pp.moveTo(gx - 230, py - 180); pp.lineTo(gx + 230, py - 180); pp.lineTo(gx + 180, py + 100); pp.lineTo(gx - 180, py + 100); pp.close()
    leafy_tree(c, gx, py - 180, 0.18 + 0.62 * g, t, seed=4)
    c.drawPath(pp, lin(c, (gx - 230, 0, gx + 230, 0), [col('#e07a4a'), col('#c25a2c')], vertical=False))
    c.drawRoundRect(skia.Rect(gx - 250, py - 220, gx + 250, py - 170), 16, 16, lin(c, (0, py - 220, 0, py - 170), [col('#f08d5c'), col('#cf6334')]))
    if t > t0 + 0.6:
        label_pill(c, f'year {max(1, years)}' if years < 5 else '5 YEARS', gx, 760, size=46, k=1.0 - prog(t, t2 - 0.3, 0.3), fill='#1b2a4a', hi='#ff5c85')
    kb = ease_out(prog(t, t1 + 0.1, 0.9))
    if t > t1:
        scale_bar(c, 790, 1340, 1.0 * kb, 'tree +164 lb', '#3f9a2e', k=1.0)
    if t > t1 + 1.6:
        kk = ease_back(prog(t, t1 + 1.6, 0.4))
        label_pill(c, 'soil −2 oz', 790, 1500, size=38, k=kk, fill='#8a5a35', hi='#8a5a35')
    if t > t2:
        k = ease_back(prog(t, t2 + 0.1, 0.5), 2.2)
        drift_co2(c, t, t2, 6, 120, 760, gx, py - 500, seed=3, r=18)
        label_pill(c, 'mostly made of AIR', 540, 700, size=52, k=k, fill='#1b2a4a', hi='#2f9bff')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[1]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 1.6, 'pop'), (cues[2]['start'] + 0.1, 'ding')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    bg_day(c, t)
    soil(c, 1440, t, seed=9)
    plant(c, 540, 1440, 1.0, t, seed=5, roots=True, leaves=6, glow=0.5 + 0.5 * math.sin(t * 3))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        onion(c, 260, 1180, 0.45 * k, t, rot=math.sin(t * 2) * 6, alpha=255 * fo)
        label_pill(c, 'next: ONIONS', 260, 1340, size=44, k=k, fill='#1b2a4a', hi='#9c5bb8', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s7_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do plants eat?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ("How do plants eat? They don't even have a mouth.", 'How do plants EAT?'),
            ('They cook their own food out of air, water and light.', 'They COOK their own food')], tail=1.0),
        dict(name='water', draw=s2, sfx_fn=s2_sfx, lines=[
            ('First, the roots soak up water from the soil.', 'Roots soak up WATER'),
            ('It rises up the stem through tiny pipes, like a drink through a straw.', 'Up through tiny PIPES')], tail=1.0),
        dict(name='pores', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Leaves are covered in tiny pores called stomata.', 'Tiny pores: STOMATA'),
            ('Carbon dioxide from the air drifts in through them.', 'CO2 from the air drifts IN')], tail=1.0),
        dict(name='kitchen', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Inside the leaf, sunlight powers a chemical kitchen called the chloroplast.', 'Sunlight powers the KITCHEN'),
            ('It turns water and carbon dioxide into sugar, and lets out oxygen. The air we breathe.', 'Out come SUGAR and OXYGEN')], tail=1.2),
        dict(name='uses', draw=s5, sfx_fn=s5_sfx, lines=[
            ('That sugar is fuel, and building material. It becomes leaves, wood and fruit.', 'Sugar becomes WOOD and FRUIT'),
            ('The soil only adds minerals. More like vitamins than a meal.', 'Soil = just the VITAMINS')], tail=1.1),
        dict(name='willow', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part: in the 1600s, a scientist grew a willow in a pot for five years.", 'A willow in a pot, 5 YEARS'),
            ('The tree gained over a hundred and sixty pounds. The soil lost about two ounces.', 'Tree +164 lb, soil −2 OZ'),
            ('Most of a tree is built from air.', 'Trees are built from AIR')], tail=1.6),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('So plants eat light, water and air, and cook their own sugar.', 'Light + water + air = FOOD'),
            ('Next up: why onions make you cry.', 'Next: why ONIONS make you cry'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
