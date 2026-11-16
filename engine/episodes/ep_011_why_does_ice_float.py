"""Episode 11 (EN): Why does ice float?"""
import math, random
from lib import *

ROOM = ('#bfe6ff', '#fff3df')

def room_bg(c, t, table_y=1560):
    sky(c, ROOM[0], ROOM[1], mid='#e3f2ff')
    # window with a winter view
    wx0, wy0, wx1, wy1 = 70, 650, 270, 880
    c.drawRoundRect(skia.Rect(wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14), 26, 26, P(color=col('#ffffff')))
    c.save(); clip = skia.Path(); clip.addRoundRect(skia.Rect(wx0, wy0, wx1, wy1), 16, 16); c.clipPath(clip, doAntiAlias=True)
    c.drawRect(skia.Rect(wx0, wy0, wx1, wy1), lin(c, (0, wy0, 0, wy1), [col('#8fc9ff'), col('#e6f4ff')]))
    p = skia.Path(); p.moveTo(wx0, wy1 - 60); p.cubicTo(wx0 + 60, wy1 - 80, wx0 + 130, wy1 - 30, wx1, wy1 - 60); p.lineTo(wx1, wy1); p.lineTo(wx0, wy1); p.close()
    c.drawPath(p, P(color=col('#ffffff')))
    snow(c, t, seed=8, n=10, y0=wy0, y1=wy1, alpha=220)
    c.restore()
    c.drawLine((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1, P(color=col('#ffffff'), stroke=14))
    c.drawLine(wx0, (wy0 + wy1) / 2, wx1, (wy0 + wy1) / 2, P(color=col('#ffffff'), stroke=14))
    # table
    c.drawRect(skia.Rect(0, table_y, W, H), lin(c, (0, table_y, 0, H), [col('#e8a96a'), col('#c47f45')]))
    c.drawRect(skia.Rect(0, table_y, W, table_y + 18), P(color=col('#f6c28a')))
    for k in range(4):
        c.drawLine(0, table_y + 90 + k * 80, W, table_y + 70 + k * 85, P(color=col('#a86a36', 70), stroke=4))

def glass(c, cx, base, w, h, level, t, inside=None):
    """Drinking glass. level = water surface y. inside(c) draws things in the glass (before the water tint is applied)."""
    top = base - h; wt, wb = w / 2, w / 2 * 0.86
    shape = skia.Path(); shape.moveTo(cx - wt, top); shape.lineTo(cx + wt, top); shape.lineTo(cx + wb, base - 30)
    shape.quadTo(cx + wb, base, cx + wb - 30, base); shape.lineTo(cx - wb + 30, base); shape.quadTo(cx - wb, base, cx - wb, base - 30); shape.close()
    c.drawOval(skia.Rect(cx - wb - 20, base - 16, cx + wb + 20, base + 22), P(color=col('#000000', 45), blur=10))
    c.drawPath(shape, P(color=col('#ffffff', 70)))
    c.save(); c.clipPath(shape, doAntiAlias=True)
    wave = skia.Path(); wave.moveTo(cx - wt - 10, level)
    for i in range(0, int(w) + 21, 20):
        x = cx - wt - 10 + i; wave.lineTo(x, level + math.sin(x * 0.03 + t * 3) * 4)
    wave.lineTo(cx + wt + 10, base + 10); wave.lineTo(cx - wt - 10, base + 10); wave.close()
    c.drawPath(wave, lin(c, (0, level, 0, base), [col('#bfe9ff', 150), col('#5bb8f5', 170)]))
    if inside: inside(c)
    c.save(); c.clipPath(wave, doAntiAlias=True)
    c.drawRect(skia.Rect(cx - wt, level, cx + wt, base), P(color=col('#3aa0f0', 70)))
    c.restore()
    c.drawPath(wave, P(color=col('#ffffff', 200), stroke=5))
    c.restore()
    c.drawPath(shape, P(color=col('#ffffff', 230), stroke=8))
    c.drawLine(cx - wt + 40, top + 50, cx - wb + 40, base - 70, P(color=col('#ffffff', 160), stroke=14))
    c.drawLine(cx - wt + 75, top + 50, cx - wt + 75, top + 150, P(color=col('#ffffff', 110), stroke=8))

def question_marks(c, t, cx, cy, rr=330, start=0.6):
    spots = [(190, 1020), (860, 960), (175, 1260), (880, 1200), (200, 1470), (860, 1430)]
    for i in range(6):
        x = spots[i][0] + math.sin(t * 1.3 + i) * 18; y = spots[i][1] + math.cos(t * 1.7 + i * 2) * 22
        a = prog(t, start + i * 0.12, 0.35)
        if a > 0:
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96 + (i % 3) * 16, fill=['#ffffff', '#ffe14d', '#7fd0ff'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
            c.restore()

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    room_bg(c, t)
    k = max(0.0, ease_back(prog(t, 0.05, 0.7), 1.4))
    level = 1060
    def inside(c):
        drop = 1 - ease_out(prog(t, 0.1, 0.7))
        y = level + 40 - drop * 500 + math.sin(t * 2.2) * 8
        ice_cube(c, 520, y, 0.8, t, rot=math.sin(t * 1.5) * 4, mood='wow' if t < 2 else 'happy')
    c.save(); c.translate(540, 1560); c.scale(k, k); c.translate(-540, -1560)
    glass(c, 540, 1560, 470, 720, level, t, inside)
    c.restore()
    if t > 0.75:
        sp = prog(t, 0.75, 0.6)
        for j in range(8):
            a = j * math.pi / 7 + math.pi
            r_ = 60 + 160 * ease_out(sp)
            c.drawCircle(540 + math.cos(a) * r_, level - 10 + math.sin(a) * r_ * 0.6 + 140 * sp * sp, 12 * (1 - sp), P(color=col('#9fdcff', int(230 * (1 - sp)))))
    question_marks(c, t, 540, 1000, 360)
    dust(c, t, colr='#ffffff')

def s1_sfx(D, cues): return [(0.75, 'boing')]

# ---------- 2: Water molecules (liquid) ----------
def mol_liquid(i, t):
    rnd = random.Random(100 + i)
    bx, by = rnd.uniform(300, 780), rnd.uniform(880, 1340)
    return (bx + math.sin(t * rnd.uniform(1.2, 2.0) + i) * 70, by + math.cos(t * rnd.uniform(1.0, 1.8) + i * 2) * 60,
            math.sin(t * 1.5 + i) * 40)

def magnifier(c, cx, cy, r, inner, t, alpha=255):
    c.save(); clip = skia.Path(); clip.addCircle(cx, cy, r); c.clipPath(clip, doAntiAlias=True)
    inner(c)
    c.restore()
    c.drawCircle(cx, cy, r, P(color=col('#ffffff', alpha), stroke=26))
    c.drawCircle(cx, cy, r + 14, P(color=col('#3a5fa8', alpha), stroke=6))
    c.drawArc(skia.Rect(cx - r + 40, cy - r + 40, cx + r - 40, cy + r - 40), 200, 50, False, P(color=col('#ffffff', 120), stroke=16))

def s2(c, t, D, cues):
    room_bg(c, t + 10)
    glass(c, 540, 1560, 470, 720, 1060, t)
    zk = max(0.0, ease_back(prog(t, 0.15, 0.7), 1.6))
    if zk <= 0.01: return
    def inner(c):
        c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 780, 0, 1440), [col('#bfeaff'), col('#5fb6f2')]))
        for i in range(19):
            x, y, r = mol_liquid(i, t)
            water_molecule(c, x, y, 48, t, seed=i, rot=r)
    c.save(); c.translate(540, 1110); c.scale(zk, zk); c.translate(-540, -1110)
    magnifier(c, 540, 1110, 380, inner, t)
    c.restore()

def s2_sfx(D, cues): return [(0.2, 'whoosh')]

# ---------- 3: Freezing -> honeycomb with spaces ----------
def lattice():
    pts = []; R = 108; w = math.sqrt(3) * R
    centres = [(540 - w, 960), (540, 960), (540 + w, 960), (540 - w / 2, 960 + R * 1.5), (540 + w / 2, 960 + R * 1.5),
               (540 - w, 960 + R * 3), (540, 960 + R * 3), (540 + w, 960 + R * 3)]
    for cx, cy in centres:
        for k in range(6):
            a = math.radians(60 * k + 30); p = (round(cx + math.cos(a) * R, 1), round(cy + math.sin(a) * R, 1))
            if all(math.dist(p, q) > 5 for q in pts): pts.append(p)
    return pts, centres, R
LAT, CENTRES, LR = lattice()
EDGES = [(i, j) for i in range(len(LAT)) for j in range(i + 1, len(LAT)) if abs(math.dist(LAT[i], LAT[j]) - LR) < 3]

def s3(c, t, D, cues):
    f = ease_in_out(prog(t, cues[0]['start'] + 0.3, 2.2))
    sky(c, mix_hx('#7fc8ff', '#dff4ff', f), mix_hx('#2f86d8', '#9fd6ff', f), mid=mix_hx('#5fb6f2', '#bfe6ff', f))
    if f > 0.3: snow(c, t, seed=3, n=int(26 * f), alpha=int(200 * f))
    hl = ease_out(prog(t, cues[0]['start'] + 2.0, 0.6))
    if hl > 0:
        for i, j in EDGES:
            (x0, y0), (x1, y1) = LAT[i], LAT[j]
            c.drawLine(x0, y0, lerp(x0, x1, hl), lerp(y0, y1, hl), P(color=col('#ffffff', 230), stroke=12))
            c.drawLine(x0, y0, lerp(x0, x1, hl), lerp(y0, y1, hl), P(color=col('#7fbfe6', 200), stroke=4))
    sp = ease_back(prog(t, cues[1]['start'] + 0.3, 0.6), 2)
    if sp > 0:
        for k, (cx, cy) in enumerate(CENTRES):
            pul = 1 + 0.06 * math.sin(t * 4 + k)
            c.drawCircle(cx, cy, LR * 0.55 * sp * pul, P(color=col('#fff6b0', 90)))
            c.drawCircle(cx, cy, LR * 0.55 * sp * pul, P(color=col('#ffe14d', 220), stroke=6))
    for i, (lx, ly) in enumerate(LAT):
        x0, y0, r0 = mol_liquid(i % 13 + (i // 13) * 3, t)
        x0 = lerp(x0, 540, 0.0) + (i % 3 - 1) * 40; y0 = y0 + (i % 2) * 30
        x, y = lerp(x0, lx, f), lerp(y0, ly, f)
        rot = lerp(r0, math.degrees(math.atan2(ly - 1122, lx - 540)) + 90, f)
        water_molecule(c, x, y, 34, t, seed=i, rot=rot)
    dust(c, t, seed=4, n=14)

def s3_sfx(D, cues): return [(cues[0]['start'] + 2.0, 'sparkle'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 4: Kids holding hands in a circle ----------
def s4(c, t, D, cues):
    sky(c, '#4fb4ff', '#e3f6ff', mid='#9dd6ff')
    clouds(c, t, seed=4, n=3, y0=650, y1=850)
    p = skia.Path(); p.moveTo(0, 1150); p.cubicTo(300, 1100, 700, 1180, W, 1120); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, 1100, 0, H), [col('#9be27a'), col('#56b83a')]))
    k = ease_in_out(prog(t, cues[0]['start'] + 0.4, 1.6))
    cx, cy = 540, 1330; n = 8
    crowd = [(cx + (i % 4 - 1.5) * 52 + (i // 4) * 20, cy - 30 + (i // 4) * 55) for i in range(n)]
    ring = [(cx + math.cos(i / n * 2 * math.pi + 0.3) * 330, cy + math.sin(i / n * 2 * math.pi + 0.3) * 150) for i in range(n)]
    # area outline
    rx = lerp(150, 380, k); ry = lerp(80, 190, k)
    big = ease_out(prog(t, cues[1]['start'], 0.6))
    c.drawOval(skia.Rect(cx - rx, cy + 40 - ry, cx + rx, cy + 40 + ry), P(color=col('#ffffff', int(60 + 60 * big))))
    c.drawOval(skia.Rect(cx - rx, cy + 40 - ry, cx + rx, cy + 40 + ry), P(color=col('#ffe14d' if big > 0 else '#ffffff', 230), stroke=8))
    pos = [(lerp(a[0], b[0], k), lerp(a[1], b[1], k)) for a, b in zip(crowd, ring)]
    if k > 0.85:
        hp = skia.Path(); order = sorted(range(n), key=lambda i: math.atan2(ring[i][1] - cy, ring[i][0] - cx))
        for j, i in enumerate(order + [order[0]]):
            x, y = pos[i]; (hp.moveTo if j == 0 else hp.lineTo)(x, y - 70)
        c.drawPath(hp, P(color=col('#ff8fab', int(255 * prog(k, 0.85, 0.15))), stroke=8))
    for i in sorted(range(n), key=lambda i: pos[i][1]):
        x, y = pos[i]
        kid(c, x, y + 40, 0.42, t + i * 0.7, look_up=False, wave=(k >= 1 and i % 2 == 0 and t > cues[1]['start']))
    if big > 0:
        for j in range(4):
            a = t * 1.2 + j * math.pi / 2
            sx_, sy_ = cx + math.cos(a) * 470, cy + 40 + math.sin(a) * 230
            st = skia.Path()
            for q in range(10):
                rr = 22 if q % 2 == 0 else 9; aa = q * math.pi / 5 + t * 2
                (st.moveTo if q == 0 else st.lineTo)(sx_ + math.cos(aa) * rr * big, sy_ + math.sin(aa) * rr * big)
            st.close(); c.drawPath(st, P(color=col('#ffe14d')))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 5: Same water, more space; lighter for its size ----------
def balance(c, cx, cy, tilt, t, left, right):
    c.drawRect(skia.Rect(cx - 24, cy, cx + 24, cy + 230), lin(c, (cx - 24, 0, cx + 24, 0), [col('#c9d3e0'), col('#8d99ab')], vertical=False))
    c.drawRoundRect(skia.Rect(cx - 110, cy + 220, cx + 110, cy + 250), 14, 14, P(color=col('#8d99ab')))
    c.save(); c.translate(cx, cy); c.rotate(tilt)
    c.drawRoundRect(skia.Rect(-330, -14, 330, 14), 14, 14, lin(c, (0, -14, 0, 14), [col('#ffd23f'), col('#e09a00')]))
    c.restore()
    c.drawCircle(cx, cy, 24, P(color=col('#ff6b6b')))
    for sx, fn in ((-1, left), (1, right)):
        a = math.radians(tilt); px = cx + sx * 290 * math.cos(a); py = cy + sx * 290 * math.sin(a)
        c.drawLine(px, py, px, py + 40, P(color=col('#8d99ab'), stroke=6))
        c.drawRoundRect(skia.Rect(px - 120, py + 40, px + 120, py + 58), 9, 9, P(color=col('#c9d3e0')))
        fn(c, px, py + 40)

def s5(c, t, D, cues):
    sky(c, '#c9ecff', '#fff6e6', mid='#e6f5ff')
    # jar that freezes and grows
    f = ease_in_out(prog(t, cues[0]['start'] + 0.6, 2.0))
    jx, jb, jw = 540, 1080, 260
    lvl0 = jb - 220; lvl = lvl0 - 24 * f
    jar = skia.Rect(jx - jw / 2, jb - 330, jx + jw / 2, jb)
    c.drawRoundRect(jar, 30, 30, P(color=col('#ffffff', 90)))
    c.save(); clip = skia.Path(); clip.addRoundRect(jar, 30, 30); c.clipPath(clip, doAntiAlias=True)
    c.drawRect(skia.Rect(jx - jw, lvl, jx + jw, jb), lin(c, (0, lvl, 0, jb), [col(mix_hx('#7fd0ff', '#ffffff', f * 0.7)), col(mix_hx('#2f86d8', '#a9dcfa', f))]))
    if f > 0.5:
        for k in range(5): c.drawLine(jx - 90 + k * 40, lvl + 30, jx - 70 + k * 40, jb - 30, P(color=col('#ffffff', int(120 * f)), stroke=5))
    c.restore()
    c.drawRoundRect(jar, 30, 30, P(color=col('#ffffff', 240), stroke=8))
    c.drawLine(jx + jw / 2 + 10, lvl0, jx + jw / 2 + 60, lvl0, P(color=col('#ff6b6b'), stroke=7))
    if f > 0.05:
        c.drawLine(jx + jw / 2 + 10, lvl, jx + jw / 2 + 60, lvl, P(color=col('#2f6fd6'), stroke=7))
        if f > 0.6:
            curved = skia.Path(); ax = jx + jw / 2 + 95
            c.drawLine(ax, lvl0 - 4, ax, lvl + 18, P(color=col('#2f6fd6'), stroke=7))
            hd = skia.Path(); hd.moveTo(ax - 14, lvl + 22); hd.lineTo(ax, lvl + 2); hd.lineTo(ax + 14, lvl + 22); hd.close()
            c.drawPath(hd, P(color=col('#2f6fd6')))
    face(c, jx, jb - 110, 70, t, 2, 'wow' if 0.2 < f < 0.95 else 'happy')
    for i in range(4):
        sa = prog(t, cues[0]['start'] + 0.6 + i * 0.3, 0.5) * (1 - prog(t, cues[0]['start'] + 2.8, 0.5))
        if sa > 0: snowflake(c, jx - 200 + i * 130, jb - 380 - (i % 2) * 40, 20, t, i, int(230 * sa))
    # balance: same-size blocks, water heavier
    b = ease_back(prog(t, cues[1]['start'], 0.5))
    if b > 0:
        tilt = -9 * ease_in_out(prog(t, cues[1]['start'] + 0.6, 0.9)) + math.sin(t * 2) * 0.6
        def water_block(c, x, y):
            r = skia.Rect(x - 80, y - 160, x + 80, y)
            c.drawRoundRect(r, 18, 18, lin(c, (0, y - 160, 0, y), [col('#7fd0ff'), col('#2f80e0')]))
            c.drawRoundRect(r, 18, 18, P(color=col('#1f63c9'), stroke=5))
            face(c, x, y - 70, 52, t, 4)
        def ice_block(c, x, y):
            ice_cube(c, x - 8, y - 80, 0.8, t, seed=5)
        c.save(); c.translate(540, 1500); c.scale(b, b); c.translate(-540, -1500)
        balance(c, 540, 1250, tilt, t, ice_block, water_block)
        c.restore()
        lab = prog(t, cues[1]['start'] + 1.4, 0.4)
        if lab > 0:
            text_block(c, 'ICE', 252, 1560, size=58, alpha=int(255 * lab))
            text_block(c, 'WATER', 830, 1560, size=58, alpha=int(255 * lab))

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'sparkle'), (cues[1]['start'] + 0.1, 'pop'), (cues[1]['start'] + 0.7, 'boing')]

# ---------- 6: So it floats, like a beach ball ----------
def beach_ball(c, x, y, r, t):
    c.save(); c.translate(x, y); c.rotate(t * 20)
    cols_ = ['#ff5c5c', '#ffffff', '#ffd23f', '#ffffff', '#3fa9ff', '#ffffff']
    for i, h in enumerate(cols_):
        pth = skia.Path(); pth.moveTo(0, 0); pth.arcTo(skia.Rect(-r, -r, r, r), i * 60, 60, False); pth.close()
        c.drawPath(pth, P(color=col(h)))
    c.restore()
    c.drawCircle(x, y, r, rad(x - r * 0.4, y - r * 0.4, r * 1.8, [col('#ffffff', 90), col('#ffffff', 0), col('#000000', 60)], [0, 0.4, 1]))
    c.drawCircle(x, y, r * 0.16, P(color=col('#ffffff')))
    c.drawCircle(x, y, r, P(color=col('#000000', 50), stroke=4))

def pool_water(c, y, t, alpha=200):
    p = skia.Path(); p.moveTo(0, y)
    for i in range(0, W + 41, 40): p.lineTo(i, y + math.sin(i * 0.02 + t * 2) * 10)
    p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y, 0, H), [col('#5fd0ff', alpha), col('#1a6fd0', alpha)]))
    c.drawPath(p, P(color=col('#ffffff', 220), stroke=6))

def s6(c, t, D, cues):
    sky(c, '#3aa9ff', '#d8f2ff', mid='#86ccff')
    sun(c, 900, 760, 80, t)
    wy = 1180
    c.drawRect(skia.Rect(0, wy - 60, W, wy + 10), P(color=col('#f5f0e6')))
    for i in range(0, W, 90): c.drawLine(i, wy - 60, i, wy + 10, P(color=col('#d9d2c2'), stroke=3))
    tiles = skia.Rect(0, wy, W, H)
    c.drawRect(tiles, lin(c, (0, wy, 0, H), [col('#bff0ff'), col('#7fd0f0')]))
    for i in range(0, W + 1, 120): c.drawLine(i, wy, i, H, P(color=col('#ffffff', 120), stroke=3))
    for j in range(wy, H, 120): c.drawLine(0, j, W, j, P(color=col('#ffffff', 120), stroke=3))
    d0 = cues[0]['start'] + 0.2
    drop = ease_in_out(prog(t, d0, 0.7))
    land = d0 + 0.7
    bob = math.sin((t - land) * 5) * 40 * math.exp(-(t - land) * 1.6) if t > land else 0
    iy = lerp(700, wy + 28, drop) + bob + math.sin(t * 2) * 6
    under_ice = lambda: ice_cube(c, 400, iy, 0.75, t, seed=1, mood='happy' if t > land + 0.4 else 'wow', rot=math.sin(t * 1.4) * 5)
    bb = ease_out(prog(t, cues[1]['start'], 0.6))
    by = wy - 30 + math.sin(t * 2.3) * 8
    if bb > 0: beach_ball(c, 790, lerp(600, by, bb), 85, t)
    under_ice()
    pool_water(c, wy, t, 150)
    # re-draw the part of the ice that sticks out of the water (on top of the water tint)
    c.save(); c.clipRect(skia.Rect(0, 0, W, wy - 6)); under_ice(); c.restore()
    if bb > 0:
        c.save(); c.clipRect(skia.Rect(0, 0, W, wy - 6)); beach_ball(c, 790, lerp(600, by, bb), 85, t); c.restore()
    if t > land:
        sp = prog(t, land, 0.7)
        for j in range(9):
            a = math.pi + j * math.pi / 8
            r_ = 40 + 190 * ease_out(sp)
            c.drawCircle(400 + math.cos(a) * r_, wy + math.sin(a) * r_ * 0.8 + 260 * sp * sp, 13 * (1 - sp), P(color=col('#cfefff', int(255 * (1 - sp)))))
        if sp < 1: c.drawOval(skia.Rect(400 - 260 * sp, wy - 20 * sp, 400 + 260 * sp, wy + 20 * sp), P(color=col('#ffffff', int(200 * (1 - sp))), stroke=6))

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.85, 'whoosh'), (cues[0]['start'] + 0.95, 'boing'), (cues[1]['start'] + 0.3, 'boing')]

# ---------- 7: Bonus iceberg ----------
def iceberg_path():
    pts = [(360, 950), (420, 880), (470, 860), (530, 790), (590, 840), (640, 830), (700, 950),
           (800, 1000), (880, 1110), (860, 1230), (900, 1340), (820, 1460), (680, 1530), (560, 1555),
           (420, 1520), (290, 1450), (230, 1330), (190, 1200), (240, 1080), (300, 1000)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p

def s7(c, t, D, cues):
    wy = 950
    sky(c, '#5fb4ff', '#e6f6ff', mid='#a6dbff')
    clouds(c, t, seed=9, n=3, y0=640, y1=800, a=220)
    see = ease_in_out(prog(t, cues[1]['start'] + 0.2, 1.0))
    c.save(); c.translate(0, math.sin(t * 1.2) * 6)
    berg = iceberg_path()
    c.save(); c.clipRect(skia.Rect(0, 0, W, wy)); c.drawPath(berg, lin(c, (0, 800, 0, wy), [col('#ffffff'), col('#dff3ff')]))
    c.restore()
    c.restore()
    # ocean
    p = skia.Path(); p.moveTo(0, wy)
    for i in range(0, W + 41, 40): p.lineTo(i, wy + math.sin(i * 0.02 + t * 2) * 8)
    p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, wy, 0, H), [col('#3fa9ff'), col('#0b3f8f')]))
    if see > 0:
        c.save(); c.translate(0, math.sin(t * 1.2) * 6)
        c.save(); c.clipRect(skia.Rect(0, wy, W, H))
        c.drawPath(berg, lin(c, (0, wy, 0, 1560), [col('#d6f1ff', int(235 * see)), col('#8fd0f5', int(235 * see))]))
        c.drawPath(berg, P(color=col('#ffffff', int(160 * see)), stroke=6))
        c.restore()
        if see > 0.8: face(c, 540, 1240, 110, t, 3, 'wow' if t < cues[1]['start'] + 2.4 else 'happy')
        c.restore()
    c.save(); c.translate(0, math.sin(t * 1.2) * 6)
    c.save(); c.clipRect(skia.Rect(0, 0, W, wy)); c.drawPath(berg, P(color=col('#9fd0ee'), stroke=6)); c.restore()
    c.drawLine(530, 790, 560, 900, P(color=col('#cfe9fb'), stroke=6)); c.drawLine(470, 860, 455, 930, P(color=col('#cfe9fb'), stroke=5))
    c.restore()
    for i in range(0, W + 1, 40): pass
    wl = skia.Path(); wl.moveTo(0, wy)
    for i in range(0, W + 41, 40): wl.lineTo(i, wy + math.sin(i * 0.02 + t * 2) * 8)
    c.drawPath(wl, P(color=col('#ffffff', 230), stroke=6))
    fx = (t * 130) % (W + 400) - 200
    fish(c, fx, 1470, 0.45, t, seed=2)
    rising_bubbles(c, t, seed=6, n=8, y0=wy + 30, y1=1600, alpha=150)
    if see > 0.5:
        a = int(255 * prog(see, 0.5, 0.5))
        text_block(c, 'tip', 230, 850, size=56, alpha=a)
        c.drawLine(290, 850, 410, 880, P(color=col('#ffffff', a), stroke=6))

def s7_sfx(D, cues): return [(cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.2, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, '#7fd0ff', '#e6f6ff', mid='#b5e4ff')
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1040 + math.sin(t * 2) * 12); c.scale(s, s); ice_cube(c, 0, 0, 1.1, t, seed=3, rot=math.sin(t * 1.5) * 4); c.restore()
    for i in range(6):
        ang = t * 0.9 + i * math.pi / 3
        x, y = 540 + math.cos(ang) * 360, 1040 + math.sin(ang) * 300
        water_molecule(c, x, y, 40, t, seed=i, rot=math.sin(t * 2 + i) * 20)
    snow(c, t, seed=11, n=14, alpha=180)
    follow_button(c, t, cues[-1]['start'])

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why does ice float?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why does ice float?', 'Why does ICE float?'),
            ("Let's find out!", "Let's find out!")], tail=1.1),
        dict(name='molecules', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Water is made of tiny, tiny bits called molecules.', 'Water = tiny MOLECULES'),
            ('In liquid water, they tumble around, packed close together.', 'They tumble CLOSE together')], tail=1.5),
        dict(name='freeze', draw=s3, sfx_fn=s3_sfx, lines=[
            ('But when water freezes, the molecules hold hands.', 'Freezing: they HOLD HANDS!'),
            ('They line up in a pattern full of empty spaces, like a honeycomb.', 'A pattern full of SPACES')], tail=1.7),
        dict(name='circle', draw=s4, sfx_fn=s4_sfx, lines=[
            ("It's like kids holding hands in a big circle.", 'Like kids in a big CIRCLE'),
            ('They take up more room than kids squeezed into a crowd!', 'That takes MORE room!')], tail=1.7),
        dict(name='lighter', draw=s5, sfx_fn=s5_sfx, lines=[
            ('So when water turns to ice, it takes up more space.', 'Ice takes MORE space'),
            ('So a block of ice is lighter than the same size block of water.', 'So ice is LIGHTER for its size')], tail=1.8),
        dict(name='float', draw=s6, sfx_fn=s6_sfx, lines=[
            ("And that's why ice floats on top of water,", "That's why ice FLOATS!"),
            ('just like a beach ball in a pool!', 'Like a BEACH BALL in a pool')], tail=1.7),
        dict(name='iceberg', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? Icebergs are giant floating chunks of ice.', 'ICEBERGS float too!'),
            ('But most of an iceberg hides under the water. Only the tip pokes out!', 'Most of it hides UNDER water!')], tail=1.8),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
