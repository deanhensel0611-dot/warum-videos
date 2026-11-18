"""Episode 18 (EN, general audience): How do big ships float?
Facts checked: Archimedes' principle - buoyant force = weight of displaced fluid; a floating ship sinks until the
displaced water weighs as much as the ship. Steel density ~7.85 g/cm3 (~8x water). Nimitz-class carrier ~100,000 t
full-load displacement. Seawater is denser than fresh water, so ships float higher in it; load lines (Plimsoll
marks) show separate limits for fresh and salt water.
"""
import math, random
from lib import *

SKY = ('#2f9bff', '#cdeeff', '#7cc6ff')
TX0, TY0, TX1, TY1, TLV = 110, 820, 970, 1570, 1060   # tank + water level

def sea_bg(c, t, wl=1250, seed=1):
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    clouds(c, t, seed=seed, n=3, y0=640, y1=900, a=200)
    return wl

def lab_bg(c, t):
    sky(c, '#dff1ff', '#f7fbff')
    c.drawRect(skia.Rect(0, TY1 - 10, W, H), lin(c, (0, TY1, 0, H), [col('#c7d8ea'), col('#a9bed6')]))

def cube(c, x, y, s, top, side, front, label=None, lab_col='#1b2a4a', alpha=255):
    d = s * 0.28
    f = skia.Rect(x - s / 2, y - s / 2, x + s / 2, y + s / 2)
    tp = skia.Path(); tp.moveTo(f.left(), f.top()); tp.lineTo(f.left() + d, f.top() - d); tp.lineTo(f.right() + d, f.top() - d); tp.lineTo(f.right(), f.top()); tp.close()
    sp = skia.Path(); sp.moveTo(f.right(), f.top()); sp.lineTo(f.right() + d, f.top() - d); sp.lineTo(f.right() + d, f.bottom() - d); sp.lineTo(f.right(), f.bottom()); sp.close()
    c.drawPath(tp, P(color=col(top, alpha))); c.drawPath(sp, P(color=col(side, alpha)))
    c.drawRect(f, lin(c, (0, f.top(), 0, f.bottom()), [col(front, alpha), col(side, alpha)]))
    for pth in (tp, sp): c.drawPath(pth, P(color=col('#1b2a4a', int(alpha * 0.5)), stroke=4))
    c.drawRect(f, P(color=col('#1b2a4a', int(alpha * 0.5)), stroke=4))
    if label: text_block(c, label, x, y, size=int(s * 0.32), fill='#ffffff', hi='#ffffff', stroke=lab_col)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    wl = sea_bg(c, t)
    if t < t1 - 0.2:
        ship(c, 540, wl, 1.25, t, kind='carrier')
        water_body(c, wl, t, y1=H, a=235)
        k = ease_back(prog(t, 0.8, 0.5))
        label_pill(c, '100,000 tons', 540, 1480, size=66, k=k, fill='#ff5c85')
        if t > 2.2:
            label_pill(c, 'floats', 540, 980 + math.sin(t * 3) * 8, size=56, k=ease_back(prog(t, 2.2, 0.4)), fill='#2f9bff')
    else:
        water_body(c, 1460, t, y1=H, a=235)
        k1 = ease_back(prog(t, t1, 0.5)); k2 = ease_back(prog(t, t1 + 0.5, 0.5))
        c.save(); c.translate(320, 1080); c.scale(k1, k1); cube(c, 0, 0, 260, '#e3e9f1', '#7d8a9c', '#b5c0ce', 'STEEL'); c.restore()
        c.save(); c.translate(760, 1080); c.scale(k2, k2); cube(c, 0, 0, 260, '#bfe6ff', '#1a7ad9', '#4fb3ff', 'WATER', lab_col='#0d4f9c', alpha=230); c.restore()
        if t > t1 + 1.3:
            k3 = ease_back(prog(t, t1 + 1.3, 0.4), 2.4)
            label_pill(c, '8× heavier', 320, 1330, size=52, k=k3, fill='#ff5c85')
            label_pill(c, 'same size', 760, 1330, size=52, k=k3, fill='#1a7ad9')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.8, 'pop'), (cues[1]['start'], 'pop'), (cues[1]['start'] + 0.5, 'pop'), (cues[1]['start'] + 1.3, 'click')]

# ---------- 2: Block sinks, bowl floats ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t)
    tank(c, TX0, TY0, TX1, TY1, TLV, t)
    # block: drops in, sinks to the floor
    u = prog(t, t0 + 0.4, 2.2)
    by = lerp(700, TY1 - 80, ease_in_out(u) if u < 1 else 1)
    steel_block(c, 330, by, 160, 110, rot=8 * (1 - u))
    if 0.15 < u < 0.95:
        rising_bubbles(c, t, seed=3, n=6, x0=280, x1=380, y0=TLV + 10, y1=by, rmin=6, rmax=12, speed=200)
    if t > t1:
        v = prog(t, t1 + 0.2, 1.0)
        bx = 700; byy = lerp(640, TLV - 10, ease_out(v)) + (math.sin(t * 2.5) * 6 if v >= 1 else 0)
        steel_bowl(c, bx, byy - 40, 300, 110, rot=math.sin(t * 2) * 3)
    tank(c, TX0, TY0, TX1, TY1, TLV, t, front=True)
    if u >= 1:
        label_pill(c, 'SINKS', 330, 1660 - 130, size=52, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill='#ff5c85', hi='#ff5c85')
    if t > t1 + 1.4:
        label_pill(c, 'FLOATS', 700, 900, size=52, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill='#2f9bff', hi='#2f9bff')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 1.0, 'click'), (cues[0]['start'] + 2.6, 'pop'), (cues[1]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 1.4, 'pop')]

# ---------- 3: Pushing water aside, water pushes back ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t)
    v = ease_in_out(prog(t, t0 + 0.3, 1.6))
    lvl = TLV - 70 * v
    tank(c, TX0, TY0, TX1, TY1, lvl, t)
    by = lerp(640, lvl - 40, v) + (math.sin(t * 2.4) * 5 if v >= 1 else 0)
    # marker: old level vs new level
    c.drawLine(TX0 - 30, TLV, TX0 + 50, TLV, P(color=col('#ff5c85'), stroke=8))
    if v > 0.2:
        c.drawLine(TX0 - 30, lvl, TX0 + 50, lvl, P(color=col('#2f9bff'), stroke=8))
        arrow(c, TX0 + 10, TLV - 6, TX0 + 10, lvl + 14, colr='#2f9bff', w=8)
    steel_bowl(c, 540, by - 70, 420, 150)
    tank(c, TX0, TY0, TX1, TY1, lvl, t, front=True)
    if t > t0 + 1.6:
        label_pill(c, 'water pushed ASIDE', 540, 1420, size=48, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill='#1b2a4a', hi='#2f9bff')
    if t > t1 + 0.3:
        k = ease_back(prog(t, t1 + 0.3, 0.5))
        for i, dx in enumerate((-140, 0, 140)):
            yy = by + 140 + math.sin(t * 5 + i) * 8
            arrow(c, 540 + dx, yy + 150, 540 + dx, yy + 150 - 150 * k, colr='#ffd23f', w=22)
        label_pill(c, 'pushes back UP', 540, 760, size=52, k=k, fill='#1b2a4a', hi='#e0a800')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] + 0.3, 'boing')]

# ---------- 4: Sinks until balanced; the carrier ----------
def scale_beam(c, x, y, tilt, left_lbl, right_lbl, k=1.0):
    c.save(); c.translate(x, y); c.scale(k, k)
    tri = skia.Path(); tri.moveTo(0, -10); tri.lineTo(-50, 120); tri.lineTo(50, 120); tri.close()
    c.drawPath(tri, P(color=col('#1b2a4a')))
    c.save(); c.rotate(tilt)
    c.drawRoundRect(skia.Rect(-330, -18, 330, 0), 9, 9, P(color=col('#1b2a4a')))
    c.restore()
    for sx, lbl, hx in ((-1, left_lbl, '#7d8a9c'), (1, right_lbl, '#2f9bff')):
        px = sx * 300 * math.cos(math.radians(tilt)); py = sx * 300 * math.sin(math.radians(tilt))
        c.drawLine(px, py - 9, px, py + 70, P(color=col('#1b2a4a'), stroke=5))
        c.drawRoundRect(skia.Rect(px - 120, py + 70, px + 120, py + 90), 10, 10, P(color=col('#1b2a4a')))
        c.drawRoundRect(skia.Rect(px - 105, py - 10 - 110 + 70, px + 105, py + 70), 18, 18, P(color=col(hx)))
        text_block(c, lbl, px, py + 15, size=40, fill='#ffffff', hi='#ffffff', stroke=hx, maxw=200)
    c.restore()

def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    if t < t1 - 0.2:
        lab_bg(c, t)
        dep = ease_in_out(prog(t, t0 + 0.3, 2.6))
        lvl = TLV - 30 - 50 * dep
        tank(c, TX0, 980, TX1, TY1, lvl, t)
        steel_bowl(c, 540, lvl - 110 + 110 * dep - 10 + math.sin(t * 2.4) * 4 * dep, 420, 150)
        for i in range(int(4 * dep + 0.999)):
            bx = 450 + (i % 2) * 90; byy = lvl - 125 + 110 * dep - (i // 2) * 60
            c.drawRoundRect(skia.Rect(bx - 40, byy - 50, bx + 40, byy), 6, 6, P(color=col(['#ff5c85', '#ffd23f', '#2f9bff', '#ff9f1c'][i])))
        tank(c, TX0, 980, TX1, TY1, lvl, t, front=True)
        tilt = lerp(-12, 0, ease_in_out(prog(t, t0 + 0.6, 2.4))) + (math.sin(t * 6) * 1.5 * (1 - prog(t, t0 + 3.0, 0.5)))
        scale_beam(c, 540, 730, tilt, 'ship', 'water moved', k=ease_back(prog(t, t0 + 0.1, 0.5)))
        if t > t0 + 3.1:
            label_pill(c, 'BALANCED', 540, 1640 - 120, size=52, k=ease_back(prog(t, t0 + 3.1, 0.4)), fill='#1b2a4a', hi='#e0a800')
    else:
        wl = sea_bg(c, t, seed=4)
        wl = 1150
        ship(c, 380, wl, 0.8, t, kind='carrier')
        water_body(c, wl, t, y1=H, a=235)
        # displaced water lifted out as a hull-shaped block
        u = ease_back(prog(t, t1 + 0.8, 0.8), 1.4)
        if u > 0:
            c.save(); c.translate(730, wl + 40 - 260 * u); c.scale(1.35, 1.35)
            hp = skia.Path(); hp.moveTo(-150, -30); hp.lineTo(150, -30); hp.cubicTo(140, 20, 110, 40, 90, 40); hp.lineTo(-120, 40); hp.cubicTo(-135, 40, -145, 20, -150, -30); hp.close()
            c.drawPath(hp, lin(c, (0, -30, 0, 40), [col('#7fd0ff', 235), col('#1a7ad9', 235)]))
            c.drawPath(hp, P(color=col('#ffffff', 220), stroke=5))
            c.restore()
            label_pill(c, '≈ 100,000 t water', 600, 1320, size=46, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill='#1a7ad9')
        label_pill(c, '100,000 t ship', 330, 880, size=46, k=ease_back(prog(t, t1, 0.4)), fill='#ff5c85')

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'pop'), (cues[0]['start'] + 3.1, 'pop'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 0.8, 'whoosh')]

# ---------- 5: A hull is mostly air ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    if t < t1 - 0.2:
        wl = sea_bg(c, t, seed=5); wl = 1180
        water_body(c, wl, t, y1=H, a=150)
        # x-ray cutaway of the ship: big air space inside the hull
        c.save(); c.translate(540, wl + 20); s = 1.35
        ship(c, 0, 0, s, t, kind='cargo', rock=False)
        k = ease_out(prog(t, t0 + 0.5, 0.8))
        if k > 0:
            ins = skia.Path(); ins.moveTo(-300 * s, -60 * s); ins.lineTo(330 * s, -60 * s); ins.cubicTo(320 * s, 10 * s, 290 * s, 56 * s, 240 * s, 56 * s); ins.lineTo(-280 * s, 56 * s); ins.cubicTo(-300 * s, 56 * s, -315 * s, 20 * s, -300 * s, -60 * s); ins.close()
            c.drawPath(ins, P(color=col('#eaf6ff', int(245 * k))))
            for i in range(14):
                ax = -260 * s + (i * 41 * s + t * 30) % (540 * s); ay = math.sin(t * 2 + i) * 18 * s
                c.drawCircle(ax, ay, 6 * s, P(color=col('#9fd2ff', int(200 * k))))
            text_block(c, 'AIR', 0, 0, size=110, fill='#2f9bff', hi='#2f9bff', stroke='#ffffff', alpha=int(255 * k))
        c.restore()
        water_body(c, wl, t, y1=H, a=110)
        if t > t0 + 2.0:
            label_pill(c, 'big + light for its size', 540, 1520, size=48, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill='#1b2a4a')
    else:
        lab_bg(c, t)
        f = ease_in_out(prog(t, t1 + 0.6, 2.0))
        sink = ease_in_out(prog(t, t1 + 2.0, 1.4))
        tank(c, TX0, TY0, TX1, TY1, TLV, t)
        by = lerp(TLV - 50, TY1 - 140, sink) + math.sin(t * 2.4) * 4 * (1 - sink)
        steel_bowl(c, 540, by, 420, 150, fill=f, rot=3 * math.sin(t * 2) * (1 - sink))
        if 0.05 < f < 0.95:
            for i in range(3):
                u = ((t * 2 + i / 3) % 1)
                c.drawCircle(540 + 180 + i * 10, lerp(TLV - 20, by + 20, u), 10, P(color=col('#4fb3ff', 220)))
        tank(c, TX0, TY0, TX1, TY1, TLV, t, front=True)
        if t > t1 + 3.2:
            label_pill(c, 'no air = no float', 540, 760, size=50, k=ease_back(prog(t, t1 + 3.2, 0.4)), fill='#ff5c85')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'sparkle'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 2.0, 'whoosh'), (cues[1]['start'] + 3.2, 'pop')]

# ---------- 6: Wild part: salt water vs fresh water ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    if t < t1 - 0.2:
        k = ease_in_out(prog(t, t0 + 1.2, 1.4))
        for i, (x0, x1, c1, c2, lbl, deep) in enumerate(((0, 535, '#8fd4ff', '#3f9fe0', 'FRESH water', 35), (545, W, '#2f9bff', '#0f4fa8', 'SALT water', 0))):
            c.save(); cl = skia.Path(); cl.addRect(skia.Rect(x0, 0, x1, H)); c.clipPath(cl)
            wl = 1150
            ship(c, (x0 + x1) / 2, wl + deep * k, 0.62, t + i, kind='cargo')
            water_body(c, wl, t, x0, x1, y1=H, c1=c1, c2=c2, a=235)
            c.restore()
            label_pill(c, lbl, (x0 + x1) / 2 - (30 if i else 0), 1470, size=44, k=ease_back(prog(t, t0 + 0.3 + i * 0.3, 0.4)), fill=c2)
        c.drawRect(skia.Rect(535, 600, 545, H), P(color=col('#ffffff')))
        if t > t0 + 2.8:
            label_pill(c, 'HIGHER', 740, 780, size=52, k=ease_back(prog(t, t0 + 2.8, 0.4)), fill='#1b2a4a', hi='#e0a800')
            arrow(c, 740, 960, 740, 860, colr='#ffd23f', w=16)
    else:
        wl = 1220
        ship(c, 360, wl, 1.0, t, kind='cargo', marks=True)
        water_body(c, wl, t, y1=H, a=235)
        def inner(cc):
            cc.drawRect(skia.Rect(240, 650, 840, 1250), P(color=col('#1b2a4a')))
            mx, my = 400, 950
            cc.drawCircle(mx, my, 110, P(color=col('#ffffff'), stroke=14)); cc.drawLine(mx - 160, my, mx + 160, my, P(color=col('#ffffff'), stroke=14))
            for j, (dy, lbl, hx) in enumerate(((-90, 'FRESH', '#8fd4ff'), (10, 'SALT', '#ffd23f'))):
                cc.drawLine(mx + 180, my + dy, mx + 280, my + dy, P(color=col('#ffffff'), stroke=14))
                text_block(cc, lbl, mx + 250, my + dy - 50, size=44, fill=hx, hi=hx, stroke='#1b2a4a', maxw=400)
        k = ease_back(prog(t, t1 + 0.4, 0.6))
        if k > 0:
            c.drawLine(360 - 150, wl - 26, 540, 1000, P(color=col('#ffffff', 200), stroke=6))
            magnifier(c, 540, 950, 300 * k, inner, t)

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 2.8, 'ding'), (cues[1]['start'] + 0.4, 'whoosh')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    wl = sea_bg(c, t, seed=7); wl = 1180
    x = lerp(380, 700, t / D)
    ship(c, x, wl, 1.0, t, kind='cargo')
    water_body(c, wl, t, y1=H, a=235)
    k = ease_back(prog(t, cues[1]['start'], 0.5)); fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    if k > 0 and fo > 0:
        c.save(); c.translate(540, 1470); c.scale(k, k)
        rnd = random.Random(2)
        for i in range(9):
            bx = -150 + i * 38; h = 120 + rnd.uniform(0, 70)
            p = grass_blade_path(bx, 40, h, 26, math.sin(t * 2 + i) * 14)
            c.drawPath(p, lin(c, (0, 40 - h, 0, 40), [col('#9be36a', int(255 * fo)), col('#3f9a2e', int(255 * fo))]))
        c.restore()
        label_pill(c, 'next: why is GRASS green?', 540, 1560, size=44, k=k, fill='#1b2a4a', hi='#3f9a2e', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s7_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do big ships float?',
    music=False, faces=False, ambience='water',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('An aircraft carrier weighs about a hundred thousand tons. So why does it float?', '100,000 TONS … and it FLOATS?'),
            ('Steel is almost eight times denser than water.', 'Steel: 8× DENSER than water')], tail=0.9),
        dict(name='bowl', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Drop a solid block of steel in water, and it sinks straight to the bottom.', 'A steel BLOCK sinks'),
            ('But shape the same steel into a bowl, and it floats.', 'Same steel as a BOWL? Floats!')], tail=1.1),
        dict(name='displace', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Anything you put in water pushes some water out of the way.', 'It PUSHES water aside'),
            ('And the water pushes back up, as hard as the weight of the water it moved.', 'The water pushes back UP')], tail=1.0),
        dict(name='balance', draw=s4, sfx_fn=s4_sfx, lines=[
            ('A ship settles until the water it pushed aside weighs as much as the ship. Then it floats.', 'Sinks until it is BALANCED'),
            ('That carrier pushes aside about a hundred thousand tons of seawater.', '100,000 TONS of water moved')], tail=1.3),
        dict(name='air', draw=s5, sfx_fn=s5_sfx, lines=[
            ("The trick is the shape. A hull is mostly air inside, so it's huge but light for its size.", 'A hull is mostly AIR'),
            ('Fill the bowl with water, and the trick stops working.', 'Fill it with WATER? It sinks')], tail=1.0),
        dict(name='salt', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part: the same ship floats higher in the salty sea than in a fresh water river.", 'Ships float HIGHER in salt water'),
            ('Salt water is denser, so big ships carry marks showing how deep they may sit in each kind of water.', 'Marks for FRESH and SALT')], tail=1.2),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Floating isn't about weight. It's about how much water you push aside.", 'It is about WATER pushed aside'),
            ('Next up: why grass is green.', 'Next: why is GRASS green?'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
