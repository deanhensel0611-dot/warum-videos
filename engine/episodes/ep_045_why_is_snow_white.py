"""Episode 45 (EN, general audience): Why is snow white?
Facts checked (Live Science "Why is snow white?", University of Alaska Fairbanks Geophysical Institute
"Blue snow and ice", Woods Hole Oceanographic Institution "Why is glacier ice blue?", NSIDC "Snow and climate /
albedo", CBS "Hey Ray: why is snow white"):
- Snow is made of ice crystals; ice itself is nearly transparent. Freshly fallen snow is mostly air (often >90 %).
- At each air-ice surface, part of the light is reflected and part refracted (bent) into the next crystal. In snow
  this repeats many times until the light exits again.
- Ice absorbs visible light only weakly and nearly equally across colors, so all wavelengths come back out mixed:
  white. Same reason crushed/shaved ice, foam or sugar look white while a clear block does not.
- Fresh snow reflects up to about 80-90 % of sunlight (high albedo).
- Ice absorbs slightly more red than blue; light that travels deep into snow or glacier ice loses some red, so deep
  holes in snow and glacier ice look blue.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
RAY = '#fff3b0'

def winter(c, t, y=1450, flakes=True):
    sky(c, '#5a8fd6', '#cfe5ff')
    if flakes: snow(c, t, seed=4, n=26, y1=y + 60, alpha=210)
    snow_ground(c, y)

def ice_cube(c, x, y, s, alpha=255, frost=0.0):
    """Clear ice cube (front + top faces); frost 0..1 turns it white/crushed-looking."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    top = skia.Path(); top.moveTo(-100, -100); top.lineTo(-40, -150); top.lineTo(140, -150); top.lineTo(100, -100); top.close()
    side = skia.Path(); side.moveTo(100, -100); side.lineTo(140, -150); side.lineTo(140, 50); side.lineTo(100, 100); side.close()
    front = skia.RRect.MakeRectXY(skia.Rect(-100, -100, 100, 100), 14, 14)
    fa = lambda base: int(a * lerp(min(1, base * 1.6), 0.95, frost))
    c.drawPath(top, P(color=col(mix_hx('#b9e2ff', '#ffffff', frost), fa(0.55))))
    c.drawPath(side, P(color=col(mix_hx('#6fb8f0', '#eef5ff', frost), fa(0.45))))
    c.drawRRect(front, P(color=col(mix_hx('#9fd2ff', '#ffffff', frost), fa(0.32))))
    for pth in (top, side):
        c.drawPath(pth, P(color=col('#3f8fe0', a), stroke=5))
    c.drawRRect(front, P(color=col('#3f8fe0', a), stroke=6))
    c.drawLine(-70, -70, -20, -80, P(color=col('#ffffff', int(a * 0.9)), stroke=8))
    c.drawLine(-75, -40, -75, 20, P(color=col('#ffffff', int(a * 0.6)), stroke=6))
    c.restore()

def ray_path(c, pts, u, colr=RAY, w=10, alpha=255, glow=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    seg = skia.Path(); m = skia.PathMeasure(p, False); L = m.getLength(); m.getSegment(0, L * clamp(u), seg, True)
    if glow: c.drawPath(seg, P(color=col(colr, int(alpha * 0.4)), stroke=w * 3, blur=w))
    c.drawPath(seg, P(color=col(colr, alpha), stroke=w))
    if 0 < u < 1:
        pos, _ = m.getPosTan(L * u)
        if pos is not None: c.drawCircle(pos.x(), pos.y(), w * 1.2, P(color=col('#ffffff', alpha)))

CRYSTALS = [(300, 900, 110, 10), (620, 860, 95, 35), (860, 1010, 85, 5), (420, 1150, 120, 25), (740, 1240, 105, 40),
            (250, 1400, 90, 15), (560, 1450, 100, 0), (880, 1420, 80, 20)]
BOUNCE = [(520, 600), (600, 880), (430, 1130), (720, 1250), (560, 1440), (300, 1390), (420, 1160), (260, 900), (180, 600)]

# ---------- 1: Hook (cold open: snow already falling) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    winter(c, t)
    label_pill(c, 'WHITE', 540, 760, size=56, k=ease_back(prog(t, 0.3, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=SKYB)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        if k > 0: ice_cube(c, 520, 1100, 1.6 * k)
        label_pill(c, 'ice is CLEAR', 540, 760, size=50, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s1_sfx(D, cues):
    return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.2, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 2: Crystals and lots of air ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    winter(c, t, flakes=False)
    k = ease_back(prog(t, t0, 0.5))
    def inner(cc):
        cc.drawRect(skia.Rect(0, 600, W, 1600), lin(cc, (0, 600, 0, 1600), [col('#20406e'), col('#16305a')]))
        for i, (x, y, r, rot) in enumerate(CRYSTALS):
            ice_crystal(cc, x, y + 10 * math.sin(t + i), r * 0.8, rot=rot + t * 4, alpha=255 * prog(t, t0 + 0.3 + i * 0.12, 0.3))
        rnd = random.Random(5)
        ak = prog(t, t0 + 2.0, 0.6)
        for i in range(22):
            x, y = rnd.uniform(180, 900), rnd.uniform(760, 1500)
            if all(math.hypot(x - cx, y - cy) > r for (cx, cy, r, _) in CRYSTALS):
                c2 = int(200 * ak); cc.drawCircle(x, y, 6, P(color=col('#9fd8ff', c2)))
    if k > 0:
        magnifier(c, 540, 1120, 440 * k, inner, t)
    label_pill(c, 'ice CRYSTALS', 300, 700, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'mostly AIR', 760, 1560, size=48, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 2.2, 'pop')]

# ---------- 3: Light bounces and bends, over and over ----------
def crystal_field(c, t, alpha=255):
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, H), [col('#1d3a66'), col('#132a4d')]))
    for i, (x, y, r, rot) in enumerate(CRYSTALS):
        ice_crystal(c, x, y, r, rot=rot + 3 * math.sin(t * 0.7 + i), alpha=alpha)

def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    crystal_field(c, t)
    if t < t1:
        # one hit: reflect + refract at the first crystal
        u = prog(t, t0 + 0.2, 1.0)
        ray_path(c, [(560, 560), (600, 860)], u)
        if u >= 1:
            v = prog(t, t0 + 1.2, 0.9)
            ray_path(c, [(600, 860), (820, 640)], v, alpha=200)
            ray_path(c, [(600, 860), (560, 1120)], v, alpha=200)
            label_pill(c, 'BOUNCES', 860, 760, size=42, k=ease_back(prog(t, t0 + 1.5, 0.4)), fill=NAVY, hi=GOLD)
            label_pill(c, 'BENDS through', 300, 1060, size=42, k=ease_back(prog(t, t0 + 2.1, 0.4)), fill=NAVY, hi=SKYB)
    else:
        u = ease_in_out(prog(t, t1 + 0.1, 3.4))
        ray_path(c, BOUNCE, u)
        for i, (x, y) in enumerate(BOUNCE[1:-1]):
            hk = prog(u, (i + 1) / (len(BOUNCE) - 1) - 0.02, 0.08)
            if hk > 0:
                c.drawCircle(x, y, 30 * hk, P(color=col('#ffffff', int(180 * (1 - hk * 0.5))), blur=6))
        label_pill(c, 'over and OVER', 760, 1580, size=46, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=GOLD)
        if u > 0.95:
            label_pill(c, 'back OUT', 220, 700, size=42, k=ease_back(prog(t, t1 + 3.5, 0.4)), fill=NAVY, hi=SKYB)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.5, 'pop'), (t0 + 2.1, 'pop'), (t1 + 0.1, 'whoosh')] + \
           [(t1 + 0.1 + 3.4 * (i + 1) / 8, 'click') for i in range(7)] + [(t1 + 3.5, 'pop')]

# ---------- 4: Every color comes back equally -> white (aha) ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    crystal_field(c, t, alpha=200)
    u = ease_in_out(prog(t, t0 + 0.2, 3.0))
    cols_ = ['#ff3b3b', '#ff9f1c', '#ffe14d', '#4cd964', '#2fa8ff', '#9b4dff']
    for k, colr in enumerate(cols_):
        off = (k - 2.5) * 9
        pts = [(x + off, y + off * 0.6) for (x, y) in BOUNCE]
        ray_path(c, pts, u, colr=colr, w=6, alpha=230, glow=False)
    # white beam coming back out at the top
    if u > 0.9:
        wk = ease_out(prog(t, t0 + 3.0, 0.6))
        c.drawCircle(180, 600, 90 * wk, rad(180, 600, 90 * wk + 0.1, [col('#ffffff', 255), col('#ffffff', 0)]))
        label_pill(c, '= WHITE', 380, 640, size=60, k=ease_back(prog(t, t0 + 3.1, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'ALL colors, treated the same', 600, 1580, size=40, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 3.0, 'ding')]

# ---------- 5: Same trick as shaved ice ----------
def s5(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#bfe3ff')
    ice_cube(c, 300, 1150, 1.2, alpha=255 * prog(t, t0 - 0.2, 0.3))
    label_pill(c, 'CLEAR cube', 300, 1400, size=42, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    ak = ease_out(prog(t, t0 + 1.4, 0.6))
    arrow(c, 470, 1150, lerp(470, 600, ak), 1150, colr='#ffffff', w=16, alpha=int(255 * min(1, ak * 2)))
    # shaved ice heap in a cup
    hk = ease_out(prog(t, t0 + 1.8, 1.2))
    cx, cy = 790, 1250
    cup = skia.Path(); cup.moveTo(cx - 130, cy - 40); cup.lineTo(cx + 130, cy - 40); cup.lineTo(cx + 95, cy + 160); cup.lineTo(cx - 95, cy + 160); cup.close()
    if hk > 0:
        rnd = random.Random(3)
        for i in range(int(70 * hk)):
            a = rnd.uniform(math.pi, 2 * math.pi); r = rnd.uniform(0, 140)
            x, y = cx + math.cos(a) * r, cy - 40 + math.sin(a) * r * 0.9 * hk
            c.drawCircle(x, y, rnd.uniform(12, 22), rad(x - 5, y - 6, 26, [col('#ffffff'), col('#e3eefb')]))
    c.drawPath(cup, lin(c, (0, cy - 40, 0, cy + 160), [col(HOT), col('#e8264f')]))
    c.drawLine(cx - 120, cy - 20, cx + 120, cy - 20, P(color=col('#ffffff', 180), stroke=10))
    label_pill(c, 'crushed = WHITE', 790, 1500, size=42, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 1.4, 'whoosh'), (t0 + 2.6, 'pop')]

# ---------- 6: Reflects up to ~90 % of sunlight ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    sun(c, 280, 780, 90, t)
    snow_ground(c, 1300)
    for i in range(5):
        ph = ((t - t0) * 0.7 + i / 5) % 1.0
        x0 = 380 + i * 110
        if t > t0:
            c.drawLine(lerp(300, x0, 0), 820, lerp(300, x0, 1), 1300, P(color=col('#ffd23f', 120), stroke=6))
            uy = lerp(1300, 760, ph)
            arrow(c, x0 + (uy - 1300) * -0.4, 1300 - (1300 - uy) * 0.2, x0 + (uy - 1300) * -0.55, uy, colr='#ffffff', w=10, alpha=int(230 * (1 - ph)))
    k = ease_back(prog(t, t0 + 0.6, 0.5))
    if k > 0:
        c.save(); c.translate(760, 1500); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-200, -80, 200, 80), 40, 40, P(color=col('#ffffff', 240)))
        c.drawRoundRect(skia.Rect(-200, -80, 200, 80), 40, 40, P(color=col(NAVY), stroke=6))
        n = int(90 * ease_out(prog(t, t0 + 0.8, 1.6)))
        text_block(c, f'up to {n}%', 0, -4, size=70, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'sunlight bounced BACK', 600, 680, size=42, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=GOLD)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.6, 'pop')]

# ---------- 7: Wild part: deep holes in snow glow blue ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#8fb8e8', '#dcecff')
    snow_ground(c, 720, glow_blue=0.4)
    hk = ease_out(prog(t, t0 + 0.6, 1.2))
    hx, hy = 520, 1080
    if hk > 0:
        p = skia.Path(); p.moveTo(hx - 120 * hk, 760); p.cubicTo(hx - 130 * hk, 1100, hx - 70 * hk, 1500 * hk + 760 * (1 - hk), hx, 1520 * hk + 760 * (1 - hk))
        p.cubicTo(hx + 70 * hk, 1500 * hk + 760 * (1 - hk), hx + 130 * hk, 1100, hx + 120 * hk, 760); p.close()
        c.drawPath(p, lin(c, (0, 760, 0, 1520), [col('#bfe3ff'), col('#4aa8ff'), col('#1f6fd6')]))
        c.drawPath(p, P(color=col('#3f8fe0', 120), blur=30))
        c.drawPath(p, P(color=col('#ffffff', 200), stroke=6))
    label_pill(c, 'it glows BLUE', 770, 1040, size=44, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        # light diving in: red fades out with depth, blue survives
        u = prog(t, t1 + 0.2, 2.0)
        for k, (colr, keep) in enumerate((('#ff3b3b', 0.0), ('#ffe14d', 0.6), ('#2fa8ff', 1.0))):
            y = lerp(800, 1420, u)
            fade = lerp(1.0, keep, prog(u, 0.2, 0.8))
            x = hx - 30 + k * 30
            c.drawLine(x, 800, x, y, P(color=col(colr, int(240 * fade)), stroke=10))
        label_pill(c, 'ice soaks up RED', 280, 1460, size=40, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 1.8, 'sparkle'), (t1 + 0.2, 'whoosh'), (t1 + 1.0, 'pop')]

# ---------- 8: Outro ----------
def bone(c, x, y, s, rot=0.0, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.drawCircle(sx * 110, sy * 24, 34, P(color=col('#fff6e0', a)))
    c.drawRoundRect(skia.Rect(-110, -26, 110, 26), 20, 20, P(color=col('#fff6e0', a)))
    p = skia.Path(); p.addRoundRect(skia.Rect(-110, -26, 110, 26), 20, 20)
    for sx in (-1, 1):
        for sy in (-1, 1): p.addCircle(sx * 110, sy * 24, 34)
    c.drawPath(p, P(color=col('#b08a5a', a), stroke=5))
    c.restore()

def s8(c, t, D, cues):
    winter(c, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.4, 0.4)) * fo
    if k0 > 0: label_pill(c, 'every color BACK = WHITE', 540, 700, size=44, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why we need BONES', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
        bone(c, 540, 1060, 1.1 * kk, rot=-12 + 5 * math.sin(t * 2))
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why is snow white?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why is snow white?', 'Why is SNOW white?'),
            ("It's made of ice, and ice is clear.", 'Snow is ice. Ice is CLEAR.')], tail=1.0),
        dict(name='crystals', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Snow is a jumble of tiny ice crystals, and a fresh pile is mostly air.', 'Ice crystals + lots of AIR')], tail=1.2),
        dict(name='bounce', draw=s3, sfx_fn=s3_sfx, lines=[
            ('When light hits a crystal, part of it bounces off, and part bends through.', 'Light BOUNCES and bends'),
            ('In snow, that happens over and over, until the light comes back out.', 'Over and OVER again')], tail=1.2),
        dict(name='white', draw=s4, sfx_fn=s4_sfx, trans='punch', lines=[
            ('And ice treats every color almost the same, so all colors come back out together. That mix is white.', 'ALL colors back = WHITE')], tail=1.2),
        dict(name='shaved', draw=s5, sfx_fn=s5_sfx, lines=[
            ("It's the same trick as shaved ice: a clear cube, crushed into tiny bits, turns white.", 'Crushed clear ice looks WHITE')], tail=1.2),
        dict(name='bright', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Fresh snow reflects up to about ninety percent of sunlight. That's why it's so bright.", 'Reflects up to 90% of SUNLIGHT')], tail=1.0),
        dict(name='blue', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: poke a deep hole in snow, and it glows blue inside.", 'Deep snow glows BLUE'),
            ('Ice soaks up a little red light, so light that travels deep comes out blue.', 'Ice absorbs a bit of RED')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So snow is white because it bounces every color right back.', 'Every color BACK = white'),
            ('Next: why we need bones.', 'Next: why we need BONES'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
