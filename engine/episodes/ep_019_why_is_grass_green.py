"""Episode 19 (EN, general audience): Why is grass green?
Facts checked: sunlight is a mix of all visible colours; chloroplasts contain chlorophyll, which absorbs mainly
blue and red light and absorbs green least, so more green is reflected/transmitted (leaves still absorb some green).
Photosynthesis: light + water + CO2 -> sugar (+ oxygen). Chlorophyll fluoresces deep red under UV light
(classic demo with chlorophyll extracted from spinach/leaves).
"""
import math, random
from lib import *

SKY = ('#2f9bff', '#cdeeff', '#7cc6ff')
SPEC = ['#ff3b3b', '#ff9f1c', '#ffe14d', '#4cd964', '#2fa8ff', '#3a5bff', '#9b4dff']
GREEN = '#3fd65a'

def field(c, t, ground=1500, sun_xy=(170, 760), n=70):
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    sunbeams(c, *sun_xy, t, a=28)
    sun(c, *sun_xy, 110, t)
    clouds(c, t, seed=3, n=2, y0=700, y1=900, a=200)
    grass_field(c, ground, t, n=n, hmin=140, hmax=320)

def beam(c, x0, y0, x1, y1, hx, w=14, k=1.0, a=255, dash=None):
    if k <= 0: return
    x = lerp(x0, x1, k); y = lerp(y0, y1, k)
    c.drawLine(x0, y0, x, y, P(color=col(hx, int(a * 0.35)), stroke=w * 2.2, blur=6))
    arrow(c, x0, y0, x, y, colr=hx, w=w, alpha=a)

def big_blade(c, x, y, h, t, w_=200):
    bend = math.sin(t * 1.4) * 18
    p = grass_blade_path(x, y, h, w_, bend)
    c.drawPath(p, P(color=col('#0b1a3a', 50), blur=12))
    c.drawPath(p, lin(c, (0, y - h, 0, y), [col('#9be36a'), col('#3f9a2e')]))
    vein = skia.Path(); vein.moveTo(x, y); vein.quadTo(x + bend * 0.5, y - h * 0.55, x + bend, y - h + 30)
    c.drawPath(vein, P(color=col('#ffffff', 70), stroke=5))
    return bend

def chloroplast(c, x, y, r, t, seed=0, alpha=255, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot + math.sin(t * 1.3 + seed) * 4)
    c.drawOval(skia.Rect(-r, -r * 0.55, r, r * 0.55), rad(-r * 0.3, -r * 0.2, r * 1.3, [col('#b6f08a', alpha), col('#4fbf3a', alpha), col('#2f8a25', alpha)], [0, 0.5, 1]))
    c.drawOval(skia.Rect(-r, -r * 0.55, r, r * 0.55), P(color=col('#1f6b18', int(alpha * 0.8)), stroke=r * 0.06))
    for i in range(5):     # grana stacks
        gx = -r * 0.6 + i * r * 0.3
        for j in range(3):
            c.drawRoundRect(skia.Rect(gx - r * 0.1, -r * 0.18 + j * r * 0.13, gx + r * 0.1, -r * 0.1 + j * r * 0.13), r * 0.04, r * 0.04, P(color=col('#1f6b18', int(alpha * 0.75))))
    c.restore()

def eye(c, x, y, s, t, alpha=255):
    c.save(); c.translate(x, y); c.scale(s, s)
    blink = 1.0 if (t % 3.0) > 0.15 else 0.15
    ep = skia.Path(); ep.moveTo(-120, 0); ep.quadTo(0, -95 * blink, 120, 0); ep.quadTo(0, 95 * blink, -120, 0); ep.close()
    c.drawPath(ep, P(color=col('#ffffff', alpha)))
    c.save(); c.clipPath(ep, doAntiAlias=True)
    c.drawCircle(0, 0, 52, rad(0, 0, 52, [col('#7fd06b', alpha), col('#2f8a25', alpha)]))
    c.drawCircle(0, 0, 24, P(color=col('#0b1a3a', alpha)))
    c.drawCircle(-14, -16, 11, P(color=col('#ffffff', alpha)))
    c.restore()
    c.drawPath(ep, P(color=col('#1b2a4a', alpha), stroke=9))
    c.restore()

# ---------- 1: Hook (cold open on swaying grass) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    field(c, t, ground=1520, n=80)
    bx, by, bh = 600, 1560, 760
    bend = big_blade(c, bx, by, bh, t)
    if t > t1 - 0.2:
        tip = (bx + bend * 0.6, by - bh * 0.55)
        for i, hx in enumerate(SPEC[::2]):
            k = prog(t, t1 + i * 0.15, 0.6)
            sx0, sy0 = 140, 760 + i * 30
            beam(c, sx0 + 120, sy0 + 60, tip[0] - 20, tip[1] - 30 + i * 20, hx, w=12, k=ease_out(k), a=int(255 * (1 - prog(t, t1 + 1.2, 0.4)) if hx != SPEC[3] else 255))
        g = prog(t, t1 + 1.1, 0.7)
        if g > 0:
            beam(c, tip[0] + 30, tip[1], 900, 760, GREEN, w=18, k=ease_out(g))
            label_pill(c, 'green: sent BACK', 760, 1100, size=50, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill='#2f8a25', hi='#2f8a25')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (cues[1]['start'], 'sparkle'), (cues[1]['start'] + 1.1, 'whoosh'), (cues[1]['start'] + 1.6, 'pop')]

# ---------- 2: Sunlight = every colour ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#2f4f8a', mid='#22396a')
    dust(c, t, seed=2, n=20)
    px, py = 520, 1100
    k = ease_out(prog(t, t0 + 0.2, 0.8))
    # white beam in
    beam(c, 0, 900, px - 70, py - 10, '#ffffff', w=26, k=k)
    tri = skia.Path(); tri.moveTo(px, py - 190); tri.lineTo(px - 170, py + 110); tri.lineTo(px + 170, py + 110); tri.close()
    c.drawPath(tri, P(color=col('#ffffff', 60), blur=14))
    c.drawPath(tri, lin(c, (px - 170, 0, px + 170, 0), [col('#e8f6ff', 200), col('#b5dcff', 150)], vertical=False))
    c.drawPath(tri, P(color=col('#ffffff', 230), stroke=6))
    f = ease_out(prog(t, t0 + 1.0, 1.0))
    for i, hx in enumerate(SPEC):
        beam(c, px + 60, py - 10 + i * 6, 920, 880 + i * 95, hx, w=14, k=f)
    if t > t1:
        names = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
        for i, (hx, nm) in enumerate(zip(SPEC, names)):
            kk = ease_back(prog(t, t1 + i * 0.12, 0.35))
            if kk > 0:
                c.save(); c.translate(780, 840 + i * 95 - 4); c.scale(kk, kk)
                text_block(c, nm, 0, 0, size=40, fill=hx, hi=hx, stroke='#0b1a3a', maxw=500)
                c.restore()
        label_pill(c, 'WHITE light = ALL colors', 540, 1530, size=48, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill='#1b2a4a', hi='#ff5c85')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 1.0, 'sparkle'), (cues[1]['start'], 'click'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 3: Chloroplasts full of chlorophyll ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9ffe0', '#bff0a8')
    z = ease_in_out(prog(t, t0 + 0.2, 1.4))
    # leaf surface -> cells
    rnd = random.Random(5)
    cw, chh = lerp(260, 400, z), lerp(150, 230, z)
    c.save(); c.translate(540, 1100)
    for r_ in range(-4, 5):
        for q in range(-3, 4):
            x = q * cw + (cw / 2 if r_ % 2 else 0); y = r_ * chh
            if abs(y) > 520: continue
            c.drawRoundRect(skia.Rect(x - cw / 2 + 6, y - chh / 2 + 6, x + cw / 2 - 6, y + chh / 2 - 6), 40, 40, lin(c, (0, y - chh / 2, 0, y + chh / 2), [col('#d8f7c4'), col('#b8eaa0')]))
            c.drawRoundRect(skia.Rect(x - cw / 2 + 6, y - chh / 2 + 6, x + cw / 2 - 6, y + chh / 2 - 6), 40, 40, P(color=col('#5fae46'), stroke=6))
            for j in range(4):
                ox = rnd.uniform(-0.3, 0.3) * cw + math.sin(t + j + q) * 6; oy = rnd.uniform(-0.25, 0.25) * chh
                chloroplast(c, x + ox, y + oy, lerp(26, 42, z), t, seed=j + q, rot=rnd.uniform(-30, 30))
    c.restore()
    label_pill(c, 'CHLOROPLASTS', 540, 700, size=54, k=ease_back(prog(t, t0 + 1.8, 0.4)) * (1 - prog(t, t1, 0.3)), fill='#2f8a25', hi='#2f8a25')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.3, 0.6))
        def inner(cc):
            cc.drawCircle(540, 1180, 400, P(color=col('#e9ffe0')))
            chloroplast(cc, 540, 1180, 240, t, seed=3)
            for i in range(10):
                ang = i / 10 * 2 * math.pi + t * 0.6
                mx, my = 540 + math.cos(ang) * 150, 1180 + math.sin(ang) * 75
                c_ = math.sin(t * 3 + i)
                cc.drawCircle(mx, my, 14 + 3 * c_, P(color=col('#1f9e2f')))
                cc.drawCircle(mx - 4, my - 4, 5, P(color=col('#ffffff', 170)))
        magnifier(c, 540, 1180, 300 * k, inner, t)
        label_pill(c, 'CHLOROPHYLL', 540, 1560, size=54, k=ease_back(prog(t, t1 + 1.1, 0.4)), fill='#1b2a4a', hi='#2f8a25')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 1.8, 'pop'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.1, 'pop')]

# ---------- 4: Eats red + blue, makes sugar ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#2c5a3a', mid='#21403f')
    cx, cy = 540, 1150
    glow = 0
    if t < t1 - 0.2:
        for i, hx in enumerate(SPEC):
            st = t0 + 0.3 + i * 0.18
            k = ease_out(prog(t, st, 0.7))
            sy = 700 + i * 30
            if hx in ('#4cd964',):
                # green bounces back out
                beam(c, 80, sy, cx - 80, cy - 40, GREEN, w=12, k=k)
                if k >= 1:
                    beam(c, cx - 60, cy - 60, 960, 700, GREEN, w=16, k=ease_out(prog(t, st + 0.7, 0.7)))
            elif hx in ('#ff3b3b', '#3a5bff', '#2fa8ff', '#9b4dff'):
                beam(c, 80, sy, cx - 60 + i * 10, cy - 40, hx, w=12, k=k, a=int(255 * (1 - prog(t, st + 0.9, 0.4))))
                glow += prog(t, st + 0.7, 0.5)
            else:
                beam(c, 80, sy, cx - 60, cy - 40, hx, w=10, k=k, a=int(160 * (1 - prog(t, st + 0.9, 0.4))))
        c.drawCircle(cx, cy, 380, rad(cx, cy, 380, [col('#ffe14d', int(30 * glow)), col('#ffe14d', 0)]))
        chloroplast(c, cx, cy, 280, t, seed=1)
        if t > t0 + 2.0:
            label_pill(c, 'RED + BLUE: eaten', 540, 1500, size=48, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill='#1b2a4a', hi='#ff3b3b')
    else:
        k = [ease_back(prog(t, t1 + 0.1 + i * 0.5, 0.4)) for i in range(4)]
        chloroplast(c, 540, 1100, 200, t, seed=2)
        c.drawCircle(540, 1100, 260, rad(540, 1100, 260, [col('#ffe14d', 50), col('#ffe14d', 0)]))
        for (lbl, x, y, kk, hx) in (('light', 200, 760, k[0], '#e0a800'), ('water', 200, 1430, k[1], '#2f9bff'), ('CO2', 880 - 30, 760, k[2], '#7d8a9c')):
            label_pill(c, lbl, x, y, size=48, k=kk, fill=hx, hi=hx)
            if kk > 0.5: arrow(c, x + (80 if x < 540 else -80), y + (60 if y < 1100 else -60), 540 + (-150 if x < 540 else 150), 1100 + (-80 if y < 1100 else 80), colr='#ffffff', w=10, alpha=200)
        if k[3] > 0:
            c.save(); c.translate(800, 1440); c.scale(k[3], k[3]); c.rotate(math.sin(t * 2) * 5)
            for dx, dy in ((-40, 20), (40, 20), (0, -40)):
                c.drawRoundRect(skia.Rect(dx - 40, dy - 40, dx + 40, dy + 40), 10, 10, P(color=col('#ffffff')))
                c.drawRoundRect(skia.Rect(dx - 40, dy - 40, dx + 40, dy + 40), 10, 10, P(color=col('#c9d3df'), stroke=4))
            c.restore()
            label_pill(c, 'SUGAR', 800, 1560, size=48, k=k[3], fill='#ff5c85', hi='#ff5c85')
            arrow(c, 640, 1200, 740, 1340, colr='#ffd23f', w=14)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] + 0.1, 'pop'), (cues[1]['start'] + 0.6, 'pop'), (cues[1]['start'] + 1.1, 'pop'), (cues[1]['start'] + 1.6, 'sparkle')]

# ---------- 5: Green bounces back into your eyes ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    field(c, t, ground=1560, sun_xy=(160, 740), n=60)
    bx, by = 420, 1600
    bend = big_blade(c, bx, by, 680, t, w_=140)
    tip = (bx + bend * 0.6, by - 680 * 0.55)
    k = ease_out(prog(t, t0 + 0.3, 0.8))
    beam(c, 230, 830, tip[0] - 10, tip[1] - 40, '#ffffff', w=16, k=k)
    g = ease_out(prog(t, t0 + 1.4, 1.0))
    if g > 0:
        for j in range(3):
            beam(c, tip[0] + 40, tip[1] - 20 + j * 40, 760, 980 + j * 30, GREEN, w=14, k=g)
    ke = ease_back(prog(t, t0 + 1.2, 0.5))
    if ke > 0:
        c.drawCircle(830, 1000, 170 * ke, P(color=col('#ffffff', 200)))
        eye(c, 830, 1000, 0.95 * ke, t)
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.2, 0.5), 2.2)
        label_pill(c, 'you see GREEN', 650, 1280, size=56, k=kk, fill='#2f8a25', hi='#2f8a25')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 1.2, 'pop'), (cues[1]['start'] + 0.2, 'ding')]

# ---------- 6: Wild part: chlorophyll glows red under UV ----------
def uv_lamp(c, x, y, ang, on=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    if on > 0:
        cone = skia.Path(); cone.moveTo(70, -40); cone.lineTo(700, -230); cone.lineTo(700, 230); cone.lineTo(70, 40); cone.close()
        c.drawPath(cone, lin(c, (70, 0, 700, 0), [col('#b06bff', int(150 * on)), col('#7a3dff', 0)], vertical=False))
    c.drawRoundRect(skia.Rect(-160, -34, 40, 34), 18, 18, lin(c, (0, -34, 0, 34), [col('#4a566a'), col('#2b3445')]))
    c.drawRoundRect(skia.Rect(30, -52, 90, 52), 14, 14, P(color=col('#2b3445')))
    c.drawRoundRect(skia.Rect(80, -44, 96, 44), 6, 6, P(color=col('#c99bff', int(120 + 135 * on))))
    c.restore()

def jar(c, x, y, t, liquid, glow=0.0):
    w_, h_ = 230, 300
    body = skia.Rect(x - w_ / 2, y - h_, x + w_ / 2, y)
    if glow > 0:
        c.drawCircle(x, y - h_ * 0.4, 330, rad(x, y - h_ * 0.4, 330, [col('#ff2d3d', int(150 * glow)), col('#ff2d3d', 0)]))
    c.drawRoundRect(body, 40, 40, P(color=col('#ffffff', 40)))
    lq = skia.Rect(x - w_ / 2 + 10, y - h_ * 0.7 + math.sin(t * 2) * 3, x + w_ / 2 - 10, y - 10)
    c.drawRoundRect(lq, 32, 32, lin(c, (0, lq.top(), 0, lq.bottom()), [col(liquid), col(mix_hx(liquid, '#000000', 0.3))]))
    c.drawRoundRect(body, 40, 40, P(color=col('#ffffff', 200), stroke=7))
    c.drawRoundRect(skia.Rect(x - w_ / 2 - 12, y - h_ - 24, x + w_ / 2 + 12, y - h_ + 6), 12, 12, P(color=col('#c9d3df')))
    c.drawLine(x - w_ / 2 + 30, y - h_ + 40, x - w_ / 2 + 30, y - 40, P(color=col('#ffffff', 120), stroke=10))

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    dark = prog(t, t1 - 0.4, 0.8)
    sky(c, mix_hx('#1b2a4a', '#07040f', dark), mix_hx('#2c5a3a', '#120a24', dark))
    jx, jy = 600, 1450
    on = prog(t, t1 + 0.4, 0.3); glow = ease_in_out(prog(t, t1 + 0.9, 1.0))
    liquid = mix_hx('#2fa84a', '#ff2d3d', glow)
    if t < t1 + 0.2:
        # crushed leaves -> green extract
        for i in range(7):
            u = prog(t, t0 + 0.5 + i * 0.15, 0.9)
            lx = lerp(200 + i * 110, jx - 60 + (i % 3) * 50, ease_in_out(u)); ly = lerp(760 + (i % 2) * 70, jy - 200, ease_in_out(u) ** 2)
            if u < 1: leaf(c, lx, ly, 0.5, t, colr='#5cc94a', seed=i, face_on=False, rot=t * 90 + i * 40)
    jar(c, jx, jy, t, liquid, glow)
    if dark > 0:
        uv_lamp(c, 170, 860, 32, on)
    if glow > 0.3:
        label_pill(c, 'deep RED glow', 540, 760, size=56, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill='#ff2d3d', hi='#ff2d3d', bg='#ffffff')
    if t < t1 and t > t0 + 2.4:
        label_pill(c, 'chlorophyll', jx, jy + 70, size=46, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill='#2f8a25')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'whoosh'), (cues[0]['start'] + 2.4, 'pop'), (cues[1]['start'] + 0.4, 'click'), (cues[1]['start'] + 1.0, 'sparkle')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    field(c, t, ground=1480, sun_xy=(540, 900), n=90)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        c.save(); c.translate(540, 1300); c.scale(k, k)
        c.drawCircle(0, 0, 90, P(color=col('#ffffff', int(220 * fo))))
        # seedling icon
        c.drawLine(0, 50, 0, -10, P(color=col('#3f9a2e', int(255 * fo)), stroke=10))
        leaf(c, -30, -25, 0.32, t, colr='#5cc94a', face_on=False, rot=-40, alpha=255 * fo)
        leaf(c, 30, -35, 0.32, t, colr='#7ed957', face_on=False, rot=40, alpha=255 * fo)
        c.restore()
        label_pill(c, 'next: how plants EAT', 540, 1450, size=46, k=k, fill='#1b2a4a', hi='#3f9a2e', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s7_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why is grass green?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why is grass green?', 'Why is GRASS green?'),
            ("Because green is the one color of sunlight it doesn't really want.", "Green is the light it DOESN'T want")], tail=1.0),
        dict(name='white', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Sunlight looks white, but it is really a mix of every color.', 'White sunlight …'),
            ('Red, orange, yellow, green, blue, and violet, all at once.', '… is ALL colors at once')], tail=1.1),
        dict(name='cells', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Zoom into a blade of grass, and you find tiny structures called chloroplasts.', 'Inside: CHLOROPLASTS'),
            ("They're packed with a pigment called chlorophyll.", 'Packed with CHLOROPHYLL')], tail=1.2),
        dict(name='eat', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Chlorophyll soaks up mostly red and blue light.', 'It soaks up RED and BLUE'),
            ('The plant uses that energy to turn water and carbon dioxide into sugar, its food.', 'Light + water + CO2 → SUGAR')], tail=1.2),
        dict(name='bounce', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Green is the light it uses least, so a lot more of it bounces back.', 'GREEN bounces back'),
            ('Right into your eyes. That is the green you see.', 'Right into your EYES')], tail=1.4),
        dict(name='glow', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part: chlorophyll can glow. Take it out of crushed leaves.", 'Chlorophyll can GLOW'),
            ('Then shine ultraviolet light on it, and it lights up deep red.', 'Under UV light: deep RED')], tail=1.8),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('So grass is green because green is the light it uses least.', 'Green = the light it uses LEAST'),
            ('Next up: how plants actually eat.', 'Next: how plants EAT'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
