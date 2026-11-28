"""Episode 55 (EN, general audience): How do glow sticks glow?
Facts checked (Wikipedia "Glow stick"; HowStuffWorks "How Light Sticks Work"; Compound Interest "The chemistry of
glow stick colours"; Frostburg State "How do light sticks work?"; Imperial College demonstration "Chemiluminescence"):
- A glow stick is a plastic tube holding a phenyl oxalate ester solution with a fluorescent dye; inside floats a small
  glass vial of hydrogen peroxide (plus catalyst).
- Bending the tube breaks the glass vial and the two liquids mix.
- Peroxide + oxalate ester react to form a high-energy, short-lived intermediate (1,2-dioxetanedione) that breaks
  down to CO2 and transfers its energy to the dye; the excited dye releases the energy as visible light
  (chemiluminescence). Very little heat is produced ("cold light").
- The colour depends on which fluorescent dye is used.
- Cold slows the reaction (dimmer but lasts much longer - storing an active stick in the freezer extends it);
  warmth speeds it up (brighter, but used up faster).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
GREEN = '#7dff5a'
O_RED = '#ff5c5c'

def night_bg(c, t, glow=0.0, colr=GREEN, cx=540, cy=1150):
    sky(c, '#0b1430', '#1b2a4a', mid='#12203f')
    stars(c, t, seed=5, n=40, y0=0, y1=1700, a=0.35)
    if glow > 0:
        c.drawCircle(cx, cy, 700, rad(cx, cy, 700, [col(colr, int(60 * glow)), col(colr, 0)]))

# ---------- molecules (plain, no faces) ----------
def peroxide(c, x, y, r, rot=0.0, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot)
    for sx in (-1, 1):
        hx, hy = sx * r * 1.45, -sx * r * 0.85
        c.drawLine(sx * r * 0.6, 0, hx, hy, P(color=col('#dfe6ef', a), stroke=r * 0.22))
        c.drawCircle(hx, hy, r * 0.5, rad(hx - r * 0.15, hy - r * 0.15, r * 0.7, [col('#ffffff', a), col('#d5dde9', a)]))
    for sx in (-1, 1):
        c.drawCircle(sx * r * 0.6, 0, r * 0.78, rad(sx * r * 0.6 - r * 0.25, -r * 0.3, r * 1.1, [col('#ffd0d0', a), col(O_RED, a), col('#c23a3a', a)], [0, 0.5, 1]))
    c.restore()

def oxalate(c, x, y, r, rot=0.0, alpha=255):
    """Plain stand-in for the big oxalate ester: a central C-C pair with two ring 'arms'."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot)
    for sx in (-1, 1):
        cx_ = sx * r * 1.9
        c.drawLine(sx * r * 0.45, 0, cx_ - sx * r * 0.7, 0, P(color=col('#9aa6ba', a), stroke=r * 0.2))
        hp = skia.Path()
        for k in range(6):
            ang = math.radians(60 * k + 30); px, py = cx_ + math.cos(ang) * r * 0.75, math.sin(ang) * r * 0.75
            (hp.moveTo if k == 0 else hp.lineTo)(px, py)
        hp.close()
        c.drawPath(hp, P(color=col('#c9d3e2', a)))
        c.drawPath(hp, P(color=col('#7d8aa3', a), stroke=r * 0.14))
    for sx in (-1, 1):
        c.drawCircle(sx * r * 0.45, 0, r * 0.55, rad(sx * r * 0.45 - r * 0.15, -r * 0.2, r * 0.8, [col('#ffffff', a), col('#9aa6ba', a), col('#5b6a86', a)], [0, 0.5, 1]))
        c.drawCircle(sx * r * 0.45, -r * 0.75, r * 0.38, rad(sx * r * 0.45, -r * 0.8, r * 0.5, [col('#ffd0d0', a), col(O_RED, a)]))
    c.restore()

def energy_mol(c, x, y, r, t, alpha=255, charge=1.0):
    """The short-lived, energy-packed intermediate: a small square ring with a pulsing glow."""
    a = int(alpha); pul = 0.85 + 0.15 * math.sin(t * 12)
    if charge > 0:
        c.drawCircle(x, y, r * 3.2 * pul, rad(x, y, r * 3.2 * pul, [col('#fff3a0', int(a * 0.7 * charge)), col('#ffd23f', int(a * 0.3 * charge)), col('#ffd23f', 0)], [0, 0.4, 1]))
    pts = [(-r, -r), (r, -r), (r, r), (-r, r)]
    for i in range(4):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % 4]
        c.drawLine(x + x0, y + y0, x + x1, y + y1, P(color=col('#ffffff', a), stroke=r * 0.22))
    for i, (px, py) in enumerate(pts):
        hx = O_RED if i % 2 == 0 else '#9aa6ba'
        c.drawCircle(x + px, y + py, r * 0.55, rad(x + px - r * 0.15, y + py - r * 0.2, r * 0.8, [col('#ffffff', a), col(hx, a)]))

def dye(c, x, y, r, colr, lit=0.0, alpha=255, rot=0.0):
    """Plain dye molecule: three fused rings; lit 0..1 makes it glow in colr."""
    a = int(alpha)
    if lit > 0:
        c.drawCircle(x, y, r * 4, rad(x, y, r * 4, [col(colr, int(a * 0.75 * lit)), col(colr, int(a * 0.25 * lit)), col(colr, 0)], [0, 0.35, 1]))
    c.save(); c.translate(x, y); c.rotate(rot)
    for k in (-1, 0, 1):
        hp = skia.Path(); cx_ = k * r * 1.5
        for j in range(6):
            ang = math.radians(60 * j + 30); px, py = cx_ + math.cos(ang) * r * 0.87, math.sin(ang) * r * 0.87
            (hp.moveTo if j == 0 else hp.lineTo)(px, py)
        hp.close()
        c.drawPath(hp, P(color=col(mix_hx('#3a4a6a', colr, 0.35 + 0.65 * lit), a)))
        c.drawPath(hp, P(color=col(mix_hx('#c9d3e2', '#ffffff', lit), a), stroke=r * 0.16))
    c.restore()

def light_wave(c, x0, y0, x1, y1, t, colr, k=1.0):
    """Little glowing wiggle travelling from (x0,y0) to (x1,y1)."""
    if k <= 0: return
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    p = skia.Path(); n = 60; first = True
    for i in range(n + 1):
        u = i / n * k; d = u * L
        off = math.sin(d * 0.06 - t * 14) * 22 * min(1, u * 4)
        px, py = x0 + ux * d - uy * off, y0 + uy * d + ux * off
        (p.moveTo if first else p.lineTo)(px, py); first = False
    c.drawPath(p, P(color=col(colr, 120), stroke=26, blur=10))
    c.drawPath(p, P(color=col(mix_hx(colr, '#ffffff', 0.4)), stroke=9))

# ---------- 1: Hook (cold open: stick already bending) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    bend = 28 * math.sin(math.pi * prog(t, 0.0, 0.9))
    gk = ease_out(prog(t, 0.8, 1.2))
    night_bg(c, t, gk)
    glow_stick(c, 540, 1150, 1.45, -8, GREEN, glow=gk, bend=bend, crack=prog(t, 0.45, 0.2), mix=gk, t=t)
    label_pill(c, 'no BATTERY', 300, 760, size=46, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'no FIRE', 780, 760, size=46, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'just CHEMISTRY', 540, 1560, size=50, k=ease_back(prog(t, t1 + 1.8, 0.4)), fill=NAVY, hi=GREEN)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.45, 'click'), (0.8, 'sparkle'), (t1 + 0.3, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.8, 'pop')]

# ---------- 2: Inside: a glass vial keeps two liquids apart ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    night_bg(c, t)
    zk = ease_in_out(prog(t, 0.0, 1.0))
    glow_stick(c, 540, 1130, lerp(1.2, 1.6, zk), 90 * zk, GREEN, glow=0.0, t=t)
    k1 = ease_back(prog(t, t0 + 1.4, 0.4)); k2 = ease_back(prog(t, t0 + 2.4, 0.4))
    if k1 > 0:
        arrow(c, 380, 900, 520, 990, colr='#ffffff', w=10, alpha=int(230 * prog(t, t0 + 1.5, 0.3)))
        label_pill(c, 'GLASS vial', 290, 860, size=42, k=k1, fill=NAVY, hi=SKYB)
        label_pill(c, 'peroxide', 290, 940, size=34, k=k1, fill=NAVY)
    if k2 > 0:
        arrow(c, 720, 1390, 585, 1320, colr='#ffffff', w=10, alpha=int(230 * prog(t, t0 + 2.5, 0.3)))
        label_pill(c, 'PLASTIC tube', 800, 1440, size=42, k=k2, fill=NAVY, hi=GOLD)
        label_pill(c, 'oxalate + dye', 800, 1520, size=34, k=k2, fill=NAVY)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(0.05, 'whoosh'), (t0 + 1.4, 'pop'), (t0 + 2.4, 'pop')]

# ---------- 3: Bend -> crack -> mix ----------
def s3(c, t, D, cues):
    t0 = cues[0]['start']
    bk = math.sin(math.pi * prog(t, t0 + 0.2, 1.2))
    ck = prog(t, t0 + 0.75, 0.2)
    night_bg(c, t)
    glow_stick(c, 540, 1180, 1.6, 0, GREEN, glow=0.15 * prog(t, t0 + 2.0, 1.5), bend=34 * bk, crack=ck, mix=prog(t, t0 + 1.0, 0.6), t=t)
    if ck > 0 and ck < 1 or 0 < t - (t0 + 0.75) < 0.5:
        fk = prog(t, t0 + 0.75, 0.5)
        c.drawCircle(540, 1180, 60 + 160 * ease_out(fk), P(color=col('#ffffff', int(220 * (1 - fk))), stroke=10))
    label_pill(c, 'CRACK', 540, 860, size=60, k=ease_back(prog(t, t0 + 0.8, 0.3)), fill=NAVY, hi=HOT)
    label_pill(c, 'the liquids MIX', 540, 1540, size=46, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=SKYB)

def s3_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.75, 'click'), (t0 + 0.8, 'pop'), (t0 + 1.8, 'pop')]

# ---------- 4: Reaction -> energy-packed molecule ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    night_bg(c, t)
    m = ease_in_out(prog(t, t0 + 0.3, 1.3))
    hit = t0 + 1.6
    if t < hit:
        peroxide(c, lerp(220, 440, m), 1150 + math.sin(t * 3) * 10, 72, rot=t * 30)
        oxalate(c, lerp(860, 650, m), 1150 + math.cos(t * 3) * 10, 64, rot=-t * 20)
    else:
        fk = prog(t, hit, 0.5)
        c.drawCircle(540, 1150, 80 + 260 * ease_out(fk), P(color=col('#fff3a0', int(230 * (1 - fk))), stroke=12))
        energy_mol(c, 540, 1150 + math.sin(t * 4) * 8, 70 * ease_back(prog(t, hit, 0.4)), t)
        # leftovers drift away
        dk = ease_out(prog(t, hit, 1.5))
        oxalate(c, 540 + 300 * dk, 1150 + 240 * dk, 56, rot=t * 20, alpha=int(200 * (1 - 0.5 * dk)))
    label_pill(c, 'PEROXIDE', 230, 900, size=40, k=ease_back(prog(t, t0 + 0.2, 0.4)) * (1 - prog(t, hit, 0.3)), fill=NAVY, hi=O_RED)
    label_pill(c, 'OXALATE', 850, 900, size=40, k=ease_back(prog(t, t0 + 0.5, 0.4)) * (1 - prog(t, hit, 0.3)), fill=NAVY, hi=SKYB)
    label_pill(c, 'packed with ENERGY', 540, 1540, size=46, k=ease_back(prog(t, hit + 0.5, 0.4)), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.5, 'pop'), (t0 + 0.3, 'whoosh'), (t0 + 1.6, 'sparkle'), (t0 + 2.1, 'pop')]

# ---------- 5: Energy -> dye -> light (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lit = ease_out(prog(t, t1 + 0.1, 0.5))
    night_bg(c, t, lit, cx=700, cy=1150)
    ek = prog(t, t0 + 0.8, 1.0)
    energy_mol(c, 280, 1150 + math.sin(t * 4) * 8, 60, t, charge=1 - ek)
    dye(c, 720, 1150, 56, GREEN, lit=lit, rot=math.sin(t * 1.5) * 6)
    if 0 < ek < 1:
        x = lerp(330, 690, ease_in_out(ek)); y = 1150 - math.sin(ek * math.pi) * 200
        c.drawCircle(x, y, 50, rad(x, y, 50, [col('#ffffff'), col('#ffd23f', 160), col('#ffd23f', 0)], [0, 0.4, 1]))
    for i, ang in enumerate((-60, -100, -140, -20)):
        wk = prog(t, t1 + 0.4 + i * 0.35, 1.0)
        if wk > 0:
            a_ = math.radians(ang)
            light_wave(c, 720, 1150, 720 + math.cos(a_) * 560, 1150 + math.sin(a_) * 480, t, GREEN, wk)
    label_pill(c, 'energy → DYE', 540, 1540, size=48, k=ease_back(prog(t, t0 + 1.6, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=GOLD)
    if t > t1:
        label_pill(c, 'the dye GLOWS', 540, 1540, size=52, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi='#3fbf2a')

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.8, 'whoosh'), (t0 + 1.6, 'pop'), (t1 + 0.1, 'ding')]

# ---------- 6: Different dye, different colour; cold light ----------
COLS6 = ['#ff5c85', '#ffb43c', '#ffe14d', '#7dff5a', '#5fd0ff', '#b98cff']

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_bg(c, t)
    for i, cc in enumerate(COLS6):
        k = ease_back(prog(t, t0 + 0.2 + i * 0.25, 0.4))
        if k <= 0: continue
        x = 140 + i * 160
        glow_stick(c, x, 1150 + math.sin(t * 2 + i) * 12, 0.85 * k, 90, cc, glow=0.95, crack=1.0, t=t + i)
    label_pill(c, 'new dye, new COLOR', 540, 760, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        th = ease_back(prog(t, t1 + 0.2, 0.4))
        if th > 0: thermometer(c, 900, 1500, 0.9 * th, level=0.25, hot=SKYB)
        label_pill(c, 'COLD light', 470, 1560, size=50, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=SKYB)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2 + i * 0.25, 'pop') for i in range(0, 6, 2)] + [(t0 + 1.0, 'pop'), (t1 + 0.2, 'click'), (t1 + 0.5, 'pop')]

# ---------- 7: Wild part: freezer vs warm water ----------
def freezer(c, x, y, w_, h_, t):
    c.drawRoundRect(skia.Rect(x - w_ / 2 - 18, y - h_ / 2 - 18, x + w_ / 2 + 18, y + h_ / 2 + 18), 30, 30, lin(c, (0, y - h_, 0, y + h_), [col('#eef2f7'), col('#b9c3d1')]))
    c.drawRoundRect(skia.Rect(x - w_ / 2, y - h_ / 2, x + w_ / 2, y + h_ / 2), 20, 20, lin(c, (0, y - h_ / 2, 0, y + h_ / 2), [col('#2a5ea8'), col('#163a73')]))
    rnd = random.Random(4)
    for i in range(18):
        snowflake(c, x + rnd.uniform(-w_ / 2 + 20, w_ / 2 - 20), y + rnd.uniform(-h_ / 2 + 20, h_ / 2 - 20), rnd.uniform(8, 16), t, seed=i, alpha=150)

def mug(c, x, y, t, steam=1.0):
    """Mug of warm water, (x, y) = bottom centre."""
    w_, h_ = 300, 330
    c.drawRoundRect(skia.Rect(x + w_ / 2 - 30, y - h_ + 80, x + w_ / 2 + 80, y - 90), 50, 50, P(color=col('#ff5c85'), stroke=30))
    c.drawRoundRect(skia.Rect(x - w_ / 2, y - h_, x + w_ / 2, y), 40, 40, lin(c, (x - w_ / 2, 0, x + w_ / 2, 0), [col('#e8264f'), col('#ff7a9a'), col('#c41f45')], vertical=False, pos=[0, 0.4, 1]))
    c.drawOval(skia.Rect(x - w_ / 2 + 12, y - h_ - 18, x + w_ / 2 - 12, y - h_ + 22), P(color=col('#7cc4ff')))
    for i in range(3):
        ph = (t * 0.5 + i / 3) % 1
        sx = x - 70 + i * 70; sy = y - h_ - 30 - ph * 200
        p = skia.Path(); p.moveTo(sx, sy + 60); p.cubicTo(sx - 25, sy + 30, sx + 25, sy + 10, sx, sy - 30)
        c.drawPath(p, P(color=col('#ffffff', int(150 * math.sin(ph * math.pi) * steam)), stroke=12))

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_bg(c, t)
    freezer(c, 290, 1200, 380, 560, t)
    glow_stick(c, 290, 1200, 0.62, 90, GREEN, glow=0.35, crack=1.0, t=t)
    hk = ease_out(prog(t, t1 + 1.6, 0.6))
    hot_glow = 1.0 - 0.75 * prog(t, t1 + 2.6, D - t1 - 2.8)
    if hk > 0:
        glow_stick(c, 790, 1060 + 120 * (1 - hk), 0.6, 80, GREEN, glow=hot_glow * hk, crack=1.0, t=t * 2, alpha=int(255 * hk))
        mug(c, 790, 1440, t, hk)
    label_pill(c, 'FREEZER: lasts longer', 290, 760, size=38, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'cold SLOWS it', 290, 1560, size=40, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'WARM: bright, short', 790, 860, size=38, k=ease_back(prog(t, t1 + 1.8, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.4, 'pop'), (t1 + 0.3, 'pop'), (t1 + 1.6, 'whoosh'), (t1 + 1.8, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night_bg(c, t, 0.8)
    glow_stick(c, 540, 1330, 1.3, -10, GREEN, glow=1.0, crack=1.0, t=t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'reaction → dye → LIGHT', 540, 700, size=44, k=k0, fill=NAVY, hi='#3fbf2a')
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: ROCKETS in space', 540, 820, size=44, k=kk, fill=NAVY, hi=HOT)
        rocket(c, 850, 1010, 0.36 * kk, 35, t, flame=0.8)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do glow sticks glow?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does a glow stick glow?', 'How do GLOW STICKS glow?'),
            ('No battery, no fire. Just two liquids meeting.', 'Just two LIQUIDS')], tail=1.0),
        dict(name='inside', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Inside the plastic tube floats a thin glass vial. It keeps two liquids apart.', 'A glass vial INSIDE')], tail=1.3),
        dict(name='crack', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Bend the stick, and the glass cracks. Now the liquids mix.', 'Bend, CRACK, mix')], tail=1.3),
        dict(name='react', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Peroxide meets the other chemical, and they form a short-lived molecule packed with energy.', 'A molecule full of ENERGY')], tail=1.2),
        dict(name='dye', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('It hands that energy to a dye molecule,', 'Energy goes to the DYE'),
            ('and the dye lets it go as light.', 'The dye GLOWS')], tail=1.5),
        dict(name='colors', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Swap the dye, and you get a different color.', 'New dye, new COLOR'),
            ('And it makes almost no heat. Cold light.', 'COLD light')], tail=1.1),
        dict(name='freezer', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: a freezer makes a glow stick last much longer.", 'FREEZER = lasts longer'),
            ('Cold slows the reaction down. Warm water does the opposite: brighter, but it fades fast.', 'Warm = brighter, SHORTER')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So a glow stick is a reaction that hands its energy to a dye.', 'Reaction, dye, LIGHT'),
            ('Next: how rockets move in empty space.', 'Next: ROCKETS in space'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
