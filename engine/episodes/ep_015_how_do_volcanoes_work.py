"""Episode 15 (EN): How do volcanoes work?"""
import math, random
from lib import *

DAY = ('#4fb0ff', '#d6f0ff')
SURF = 1010            # ground surface in the cut-away scenes
CH = (540, 1400)        # magma chamber centre

def day_bg(c, t, seed=1, hy=1660):
    sky(c, DAY[0], DAY[1], mid='#8fd0ff')
    clouds(c, t, seed=seed, n=3, y0=650, y1=900)
    birds(c, t, seed=seed + 2, y=700)
    hills(c, hy, t=t, trees=True, flowers=True)

def smoke(c, x, y, t, n=4, a=190, spread=1.0, speed=60, size=1.0):
    for i in range(n):
        u = (t * speed / 300 + i / n) % 1.0
        px = x + math.sin(u * 4 + i) * 40 * spread + u * 90 * spread
        py = y - u * 300
        puff(c, px, py, (40 + 70 * u) * size, alpha=int(a * (1 - u) * min(1, u * 5)))

def ground_section(c, t, heat=1.0, top=SURF):
    """Cut-away of the ground: soil, rock layers, getting hotter deeper down."""
    layers = [('#7ed957', '#56b83a', 0, 24), ('#9b6b43', '#80552f', 24, 120), ('#8a5a3c', '#6f4430', 120, 300),
              ('#7a4a36', '#6a3a2c', 300, 520), ('#6e3a2c', '#5a2c24', 520, 960)]
    for c1, c2, y0, y1 in layers:
        c.drawRect(skia.Rect(0, top + y0, W, top + y1), lin(c, (0, top + y0, 0, top + y1), [col(c1), col(c2)]))
        if y0 > 0:
            wv = skia.Path(); wv.moveTo(0, top + y0)
            for k in range(1, 13): wv.lineTo(k * W / 12, top + y0 + math.sin(k * 1.7 + y0) * 8)
            c.drawPath(wv, P(color=col('#3a1c10', 70), stroke=5))
    rnd = random.Random(3)
    for i in range(26):
        x, y, r = rnd.uniform(30, W - 30), rnd.uniform(top + 60, top + 900), rnd.uniform(10, 26)
        c.drawOval(skia.Rect(x - r, y - r * 0.6, x + r, y + r * 0.6), P(color=col('#4a2616', 60)))
    if heat > 0:
        c.drawRect(skia.Rect(0, top + 250, W, H), lin(c, (0, top + 250, 0, H), [col('#ff7a1a', 0), col('#ff7a1a', int(110 * heat)), col('#ffb627', int(170 * heat))], pos=[0, 0.6, 1]))

def chamber(c, t, fill=1.0, glow=1.0):
    x, y = CH
    c.drawOval(skia.Rect(x - 330, y - 170, x + 330, y + 170), rad(x, y, 330, [col('#ff9f1c', int(120 * glow)), col('#ff9f1c', 0)]))
    p = skia.Path()
    for k in range(37):
        a = k / 36 * 2 * math.pi
        rr = 1 + 0.05 * math.sin(a * 4 + t * 2)
        (p.moveTo if k == 0 else p.lineTo)(x + math.cos(a) * 250 * rr, y + math.sin(a) * 115 * rr)
    p.close()
    c.drawPath(p, P(color=col('#3a1c10')))
    c.save(); c.clipPath(p, doAntiAlias=True)
    top = y + 115 - 230 * fill
    c.drawRect(skia.Rect(x - 270, top, x + 270, y + 130), lin(c, (0, top, 0, y + 130), [col('#fff3a0'), col('#ff9f1c'), col('#e8382f')], pos=[0, 0.35, 1]))
    c.restore()
    c.drawPath(p, P(color=col('#2a120a'), stroke=10))

def conduit(c, t, fill=0.0, top=None):
    """Pipe from the chamber up to the crater. fill 0..1 = how far magma has climbed."""
    x = CH[0]; y0 = CH[1] - 100; y1 = top
    p = skia.Path(); p.moveTo(x - 26, y0); p.cubicTo(x - 40, y0 - 150, x - 14, y1 + 120, x - 22, y1)
    p.lineTo(x + 22, y1); p.cubicTo(x + 14, y1 + 120, x + 40, y0 - 150, x + 26, y0); p.close()
    c.drawPath(p, P(color=col('#3a1c10')))
    if fill > 0:
        c.save(); c.clipPath(p, doAntiAlias=True)
        yy = lerp(y0, y1 - 10, fill)
        c.drawRect(skia.Rect(x - 60, yy, x + 60, y0 + 10), lin(c, (0, yy, 0, y0), [col('#fff3a0'), col('#ff7a1a')]))
        c.restore()

def cone_section(c, t, s=0.62, x=540):
    """Cut-away volcano cone above the ground surface."""
    pth = volcano_path(x, SURF + 4, s)
    c.drawPath(pth, lin(c, (0, SURF - 560 * s, 0, SURF), [col('#b7774e'), col('#8a5236')]))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    for k in range(1, 6):
        lp = volcano_path(x, SURF + 4, s * (1 - k * 0.13))
        c.drawPath(lp, P(color=col('#5e3424', 70), stroke=6))
    c.restore()
    c.drawPath(pth, P(color=col('#3a1c10', 110), stroke=5))
    return SURF + 4 - 560 * s

def lava_spray(c, x, y, t, t0, n=10, power=1.0, seed=1):
    if t < t0: return
    rnd = random.Random(seed)
    for i in range(n):
        ph = rnd.random(); vx = rnd.uniform(-260, 260) * power; vy = rnd.uniform(-900, -650) * power
        T = 1.3; u = ((t - t0) / T + ph) % 1.0
        if t - t0 < ph * T: continue
        tt = u * T
        px = x + vx * tt; py = y + vy * tt + 900 * tt * tt
        r = rnd.uniform(14, 26)
        if py > SURF - 10: continue
        c.drawCircle(px, py, r * 2, rad(px, py, r * 2, [col('#ff9f1c', 120), col('#ff9f1c', 0)]))
        c.drawCircle(px, py, r, rad(px - r * 0.3, py - r * 0.3, r * 1.4, [col('#fff3a0'), col('#ff8a1a'), col('#e8382f')]))

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    day_bg(c, t, 1)
    a = ease_back(prog(t, 0.05, 0.8), 1.5)
    c.save(); c.translate(540, 1650); c.scale(1, a); c.translate(-540, -1650)
    volcano(c, 540, 1650, 1.05, t, mood='wow' if t < 2.0 else 'happy', glow=0.5 + 0.2 * math.sin(t * 3))
    c.restore()
    if a > 0.9: smoke(c, 560, 1000, t, n=4, a=200)
    for i in range(5):
        k = prog(t, 0.6 + i * 0.15, 0.35)
        if k <= 0: continue
        ang = -math.pi * (0.15 + 0.7 * i / 4)
        x, y = 540 + math.cos(ang) * 420, 1180 + math.sin(ang) * 330
        c.save(); c.translate(x, y + math.sin(t * 2 + i) * 10); c.rotate(math.sin(t * 3 + i) * 12)
        text_block(c, '?', 0, 0, size=100, fill=['#ffffff', '#ffe14d', '#ff8fab'][i % 3], scale=ease_back(k, 2.5))
        c.restore()

def s1_sfx(D, cues): return [(0.2, 'boing')]

# ---------- 2: Deep down it's hot, rock melts ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, DAY[0], DAY[1])
    heat = ease_in_out(prog(t, t0 + 0.5, 2.0))
    ground_section(c, t, heat)
    for i, (tx, s_) in enumerate([(160, 0.7), (900, 0.85)]): tree(c, tx, SURF + 10, s_, t, i)
    # thermometer
    tx, ty0, ty1 = 900, 1500, 1110
    c.drawRoundRect(skia.Rect(tx - 34, ty1 - 20, tx + 34, ty0 + 10), 34, 34, P(color=col('#ffffff', 235)))
    c.drawCircle(tx, ty0 + 30, 58, P(color=col('#ffffff', 235)))
    lvl = lerp(ty0, ty1 + 20, heat)
    c.drawRoundRect(skia.Rect(tx - 16, lvl, tx + 16, ty0 + 20), 16, 16, P(color=col('#ff4d3a')))
    c.drawCircle(tx, ty0 + 30, 42, P(color=col('#ff4d3a')))
    for k in range(5): c.drawLine(tx + 18, ty1 + 30 + k * 85, tx + 30, ty1 + 30 + k * 85, P(color=col('#c03a2a'), stroke=4))
    # digging arrow down
    g = ease_out(prog(t, t0, 1.2))
    if g > 0:
        y1 = lerp(SURF + 40, 1300, g)
        c.drawLine(380, SURF + 40, 380, y1, P(color=col('#ffffff', 200), stroke=14))
        ah = skia.Path(); ah.moveTo(350, y1 - 10); ah.lineTo(410, y1 - 10); ah.lineTo(380, y1 + 34); ah.close(); c.drawPath(ah, P(color=col('#ffffff', 200)))
    # magma blobs appear
    for i, (x, y, r) in enumerate([(300, 1500, 70), (520, 1530, 86), (720, 1480, 62)]):
        k = ease_back(prog(t, t1 + 0.3 + i * 0.25, 0.5))
        if k <= 0: continue
        c.save(); c.translate(x, y + math.sin(t * 2 + i) * 8); c.scale(k, k); magma_blob(c, 0, 0, r, t, seed=i, mood='happy'); c.restore()

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh')] + [(cues[1]['start'] + 0.3 + i * 0.25, 'pop') for i in range(3)]

# ---------- 3: Magma is lighter, floats up ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, DAY[0], DAY[1]); clouds(c, t, seed=4, n=2, y0=640, y1=760)
    ground_section(c, t, 0.8)
    top = cone_section(c, t)
    fill = ease_in_out(prog(t, t1, D - t1 - 0.3))
    chamber(c, t, fill=0.15 + 0.6 * fill)
    conduit(c, t, 0.0, top)
    for i in range(5):
        ph = i / 5
        u = ((t - t0) * 0.22 + ph) % 1.0 if t > t0 else ph * 0.3
        x = 220 + i * 160 + math.sin(t * 1.3 + i) * 20
        x = lerp(x, CH[0] + (i - 2) * 60, ease_in_out(u))
        y = lerp(1880, CH[1] + 40, ease_in_out(u))
        al = int(255 * min(1, (1 - u) * 5, u * 8 + 0.2))
        magma_blob(c, x, y, 46, t, seed=i, alpha=al)
        if 0.1 < u < 0.8:
            c.drawLine(x + 70, y + 30, x + 70, y - 40, P(color=col('#ffffff', int(al * 0.7)), stroke=8))
            ah = skia.Path(); ah.moveTo(x + 52, y - 30); ah.lineTo(x + 88, y - 30); ah.lineTo(x + 70, y - 58); ah.close(); c.drawPath(ah, P(color=col('#ffffff', int(al * 0.7))))
    # honey jar analogy
    if t > t1 + 0.3:
        k = ease_back(prog(t, t1 + 0.3, 0.5))
        c.save(); c.translate(870, 820); c.scale(k, k)
        c.drawCircle(0, 0, 120, P(color=col('#ffffff', 235)))
        c.drawCircle(0, 0, 120, P(color=col('#ffb627'), stroke=8))
        honey_jar(c, 0, 20, 0.62, t, fill=1.0, face_on=False)
        bu = ((t - t1) * 0.45) % 1.0
        bubble(c, math.sin(bu * 6) * 6, lerp(55, -30, bu), 12, alpha=230)
        c.restore()

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 4: Gas bubbles push -> eruption ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    te = t1 + 2.0
    shake = 0
    if t1 < t < te: shake = math.sin(t * 60) * 5 * prog(t, t1, te - t1)
    c.save(); c.translate(shake, 0)
    sky(c, DAY[0], DAY[1])
    ground_section(c, t, 0.9)
    top = cone_section(c, t)
    chamber(c, t, fill=0.8, glow=1.0 + 0.5 * prog(t, t1, 2))
    up = prog(t, te - 0.8, 0.8) ** 2
    conduit(c, t, up, top)
    # bubbles in the chamber growing
    rnd = random.Random(5)
    grow = 1 + 0.8 * prog(t, t1, 2.0)
    for i in range(9):
        bx = CH[0] + rnd.uniform(-180, 180); by0 = CH[1] + rnd.uniform(-20, 70)
        by = by0 - ((t * 25 + i * 13) % 40)
        if t > t0 + i * 0.12:
            bubble(c, bx, by, rnd.uniform(9, 16) * grow, alpha=220)
    if t > te:
        lava_spray(c, 540, top + 6, t, te, n=9, power=0.5, seed=2)
        smoke(c, 560, top - 40, t, n=4, a=200, size=1.0)
    c.restore()
    # soda bottle analogy (generic, no label)
    if t > t0 + 1.0:
        k = ease_back(prog(t, t0 + 1.0, 0.5))
        sh = math.sin(t * 30) * 6 * (1 if t0 + 1.6 < t < te else 0)
        c.save(); c.translate(180 + sh, 820); c.scale(k, k); c.rotate(sh)
        c.drawCircle(0, 0, 135, P(color=col('#ffffff', 235)))
        c.drawCircle(0, 0, 135, P(color=col('#4cd964'), stroke=8))
        b = skia.Path(); b.moveTo(-40, 95); b.lineTo(-40, -10); b.quadTo(-40, -45, -14, -60); b.lineTo(-14, -82); b.lineTo(14, -82); b.lineTo(14, -60); b.quadTo(40, -45, 40, -10); b.lineTo(40, 95); b.close()
        c.drawPath(b, lin(c, (0, -82, 0, 95), [col('#b8f5c8', 230), col('#4cd964', 230)]))
        c.drawPath(b, P(color=col('#2f9e4a'), stroke=5))
        for q in range(6):
            bx = -22 + (q * 17) % 44; by = 80 - ((t * 120 + q * 30) % 140)
            c.drawCircle(bx, by, 6, P(color=col('#ffffff', 220)))
        cap_y = -96 if t < te else -96 - min(70, (t - te) * 400)
        c.drawRoundRect(skia.Rect(-20, cap_y, 20, cap_y + 18), 6, 6, P(color=col('#ff4d6d')))
        if t > te:
            for q in range(5):
                ang = -math.pi / 2 + (q - 2) * 0.35; rr = 30 + ((t - te) * 160) % 60
                c.drawCircle(math.cos(ang) * rr, -90 + math.sin(ang) * rr, 7, P(color=col('#dfffe8', 230)))
        c.restore()
    if t > te:
        k = ease_back(prog(t, te, 0.4), 2.5)
        c.save(); c.translate(780, 760); c.rotate(-8); c.scale(k, k)
        text_block(c, 'WHOOSH!', 0, 0, size=96, fill='#ffe14d', stroke='#7a2a10')
        c.restore()

def s4_sfx(D, cues):
    te = cues[1]['start'] + 2.0
    return [(cues[0]['start'] + 0.3 + i * 0.4, 'pop') for i in range(3)] + [(te, 'whoosh'), (te + 0.1, 'boing')]

# ---------- 5: Lava cools into new rock ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    day_bg(c, t + 20, 5, hy=1700)
    volcano(c, 540, 1600, 0.95, t, mood='happy', glow=0.8, lava_drips=ease_out(prog(t, 0.2, 2.5)), seed=2)
    smoke(c, 560, 1040, t, n=3, a=170, size=0.9)
    cool = ease_in_out(prog(t, t1 + 0.4, 2.4))
    x, y = 790, 1380
    k = ease_back(prog(t, t0 + 0.6, 0.5))
    if k > 0:
        c.save(); c.translate(x, y); c.scale(k, k)
        magma_blob(c, 0, 0, 110, t * (1 - cool * 0.9), seed=4, cool=cool, mood='wow' if cool > 0.95 else 'happy')
        c.restore()
        if 0.05 < cool < 0.95:
            for i in range(3):
                u = (t * 0.8 + i / 3) % 1.0
                c.drawCircle(x - 60 + i * 60 + math.sin(u * 8) * 10, y - 130 - u * 120, 18 + 12 * u, P(color=col('#ffffff', int(150 * (1 - u))), blur=6))
    if t > t0 + 0.8 and cool < 0.5:
        c.save(); c.translate(x, y - 190); c.scale(ease_back(prog(t, t0 + 0.8, 0.4)), 1)
        c.drawRoundRect(skia.Rect(-110, -46, 110, 46), 34, 34, P(color=col('#ffffff', 235)))
        text_block(c, 'LAVA', 0, 0, size=62, fill='#e8382f', hi='#e8382f', stroke='#ffffff')
        c.restore()
    if cool > 0.95:
        c.save(); c.translate(x, y - 190); c.scale(ease_back(prog(t, t1 + 2.8, 0.4)), 1)
        c.drawRoundRect(skia.Rect(-110, -46, 110, 46), 34, 34, P(color=col('#ffffff', 235)))
        text_block(c, 'ROCK', 0, 0, size=62, fill='#5b5f6b', hi='#5b5f6b', stroke='#ffffff')
        c.restore()

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[1]['start'] + 2.8, 'sparkle')]

# ---------- 6: Layer on layer, volcano grows ----------
LAYER_COLS = ['#7a4a36', '#a8693f', '#6b4a3a', '#b7774e', '#8a5236', '#c58a5c']
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, DAY[0], DAY[1], mid='#8fd0ff'); clouds(c, t, seed=6, n=3, y0=640, y1=820)
    base = 1600
    c.drawRect(skia.Rect(0, base - 6, W, H), lin(c, (0, base, 0, H), [col('#7ed957'), col('#56b83a')]))
    n = 6
    for i in range(n - 1, -1, -1):
        k = ease_back(prog(t, t0 + 0.2 + i * (D - t0 - 1.5) / n, 0.7), 1.3)
        if k <= 0: continue
        s = (0.36 + i * 0.11) * clamp(k, 0, 1.2)
        pth = volcano_path(540, base, s, crater=0.9)
        c.drawPath(pth, lin(c, (0, base - 560 * s, 0, base), [col(mix_hx(LAYER_COLS[i], '#ffffff', 0.15)), col(LAYER_COLS[i])]))
        c.drawPath(pth, P(color=col('#3a1c10', 90), stroke=5))
        if i == int(clamp((t - t0 - 0.2) / ((D - t0 - 1.5) / n), 0, n - 1)) and k < 1.1:
            # fresh glowing edge on the newest layer
            c.drawPath(pth, P(color=col('#ff9f1c', int(200 * (1 - clamp(k)))), stroke=14, blur=4))
    # height ruler
    hgt = max([0.36 + i * 0.11 for i in range(n) if t > t0 + 0.2 + i * (D - t0 - 1.5) / n] or [0.36])
    yy = base - 560 * hgt
    c.drawLine(940, base - 20, 940, yy, P(color=col('#ffffff', 220), stroke=10))
    ah = skia.Path(); ah.moveTo(912, yy + 10); ah.lineTo(968, yy + 10); ah.lineTo(940, yy - 30); ah.close(); c.drawPath(ah, P(color=col('#ffffff', 220)))
    face(c, 540, base - 560 * hgt * 0.42, 120 * hgt / 0.91, t, 3, 'happy')
    kid(c, 170, 1720, 0.6, t, wave=t > t1)

def s6_sfx(D, cues):
    t0 = cues[0]['start']; n = 6
    return [(t0 + 0.2 + i * (D - t0 - 1.5) / n, 'pop') for i in range(n)]

# ---------- 7: Bonus: Hawaii grew from the ocean floor ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#4fb0ff', '#e0f5ff'); clouds(c, t, seed=9, n=2, y0=640, y1=760)
    sea_y = 1090
    floor = 1700
    c.drawRect(skia.Rect(0, sea_y, W, H), lin(c, (0, sea_y, 0, H), [col('#4ab6ff'), col('#1a5fc9'), col('#0f3f8f')]))
    for i in range(5):
        u = (t * 0.1 + i * 0.2) % 1.0
        c.drawLine(lerp(-50, W, u), sea_y + 40 + i * 120, lerp(-50, W, u) + 120, sea_y + 40 + i * 120, P(color=col('#ffffff', 50), stroke=6))
    c.drawRect(skia.Rect(0, floor, W, H), lin(c, (0, floor, 0, H), [col('#e8c98a'), col('#c9a66a')]))
    grow = ease_in_out(prog(t, 0.3, t1 + 1.0))
    s = lerp(0.25, 1.5, grow)
    volcano(c, 540, floor + 10, s, t, face_on=True, glow=0.6, mood='happy', seed=5, rock=('#8a6a5a', '#6b4a3a', '#4a3226'))
    peak = floor + 10 - 560 * s
    # water surface over the underwater part
    c.drawRect(skia.Rect(0, sea_y, W, floor), P(color=col('#2f80ff', 70)))
    wv = skia.Path(); wv.moveTo(0, sea_y)
    for k in range(1, 25): wv.lineTo(k * W / 24, sea_y + math.sin(k * 1.2 + t * 3) * 8)
    c.drawPath(wv, P(color=col('#ffffff', 200), stroke=8))
    rising_bubbles(c, t, seed=3, n=10, y0=sea_y + 60, y1=floor, alpha=150)
    if peak < sea_y - 60:
        k = ease_back(prog(t, t1 + 1.0, 0.6))
        # palm tree on the island
        px, py = 660, sea_y - 20 - (sea_y - 60 - peak) * 0.25
        c.save(); c.translate(px, py); c.scale(k, k)
        tr = skia.Path(); tr.moveTo(-10, 0); tr.quadTo(10, -90, 40, -170); tr.lineTo(54, -166); tr.quadTo(26, -90, 12, 0); tr.close()
        c.drawPath(tr, P(color=col('#8a5a2c')))
        for q in range(5):
            c.save(); c.translate(47, -170); c.rotate(-150 + q * 50 + math.sin(t * 2 + q) * 4)
            lf = skia.Path(); lf.moveTo(0, 0); lf.quadTo(50, -30, 110, 10); lf.quadTo(50, -5, 0, 0); c.drawPath(lf, P(color=col('#3fbf6a')))
            c.restore()
        c.restore()
        if t > t1 + 1.3:
            j = ease_back(prog(t, t1 + 1.3, 0.4))
            c.save(); c.translate(300, 860); c.scale(j, j)
            c.drawRoundRect(skia.Rect(-140, -50, 140, 50), 40, 40, P(color=col('#ffffff', 235)))
            text_block(c, 'Island!', 0, 0, size=62, fill='#1a5fc9', stroke='#ffffff')
            c.restore()
    fish(c, 200 + (t * 60) % 300, 1450, 0.5, t, seed=1)

def s7_sfx(D, cues): return [(0.2, 'whoosh'), (cues[1]['start'] + 1.0, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    day_bg(c, t + 60, 8)
    s = ease_back(prog(t, 0.0, 0.7), 1.6)
    c.save(); c.translate(540, 1650); c.scale(1, s); c.translate(-540, -1650)
    volcano(c, 540, 1650, 0.95, t, mood='happy', glow=0.6 + 0.2 * math.sin(t * 3), seed=4)
    c.restore()
    smoke(c, 560, 1100, t, n=4, a=190, size=0.9)
    for i in range(5):
        ang = t * 0.8 + i * 2 * math.pi / 5
        x, y = 540 + math.cos(ang) * 400, 1000 + math.sin(ang) * 140
        magma_blob(c, x, y, 34, t, seed=i, face_on=True)
    follow_button(c, t, cues[-1]['start'], y=790)

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='How do volcanoes work?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('How do volcanoes work?', 'How do VOLCANOES work?'),
            ("Let's find out!", "Let's find out!")], tail=0.9),
        dict(name='hot', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Deep, deep under the ground, it is super hot.', 'Deep down it is SUPER hot!'),
            ('So hot that some rock melts into a thick, glowing goo called magma!', 'Rock melts into MAGMA!')], tail=1.5),
        dict(name='rise', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Magma is lighter than the hard rock all around it.', 'Magma is LIGHTER than rock'),
            ('So it slowly floats up, like a bubble rising in honey!', 'It floats UP – like a honey bubble!')], tail=1.6),
        dict(name='erupt', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Magma is full of gas bubbles, like a shaken bottle of soda.', 'Full of GAS bubbles – like soda!'),
            ('The bubbles push and push, until, whoosh! Out it comes!', 'They PUSH, PUSH … WHOOSH!')], tail=2.6),
        dict(name='lava', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Once it comes out, we call it lava.', 'Outside, magma is called LAVA'),
            ('The lava cools down and turns into hard, new rock.', 'Lava cools into NEW ROCK')], tail=1.8),
        dict(name='layers', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Again and again, layer on layer,', 'Layer on LAYER …'),
            ('the new rock builds the volcano bigger and bigger!', '… the volcano grows BIGGER!')], tail=1.8),
        dict(name='hawaii', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? The islands of Hawaii were made by volcanoes!', 'HAWAII was made by volcanoes!'),
            ('They grew all the way up from the bottom of the ocean.', 'They grew up from the OCEAN floor!')], tail=1.8),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.2),
    ])
