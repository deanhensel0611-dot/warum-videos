"""Episode 31 (EN, general audience): Why are bubbles round?
Facts checked (Wikipedia "Soap bubble" / "Soap film" / "Plateau's laws", Cornell SimScience "Why are bubbles round?",
UIUC Physics Van "Bubble shapes", Brilliant "Math of soap bubbles and honeycombs"):
- A soap bubble film is a thin layer of water between two layers of soap (surfactant) molecules.
- Surface tension (water molecules attracting each other) makes the film behave like a stretched elastic skin that
  tries to minimise its area; the trapped air pushes outward equally in all directions.
- For a given enclosed volume, the sphere has the smallest surface area (unit volume: cube area 6.0, sphere ~4.84).
- A bubble blown from a square/odd-shaped wand still becomes spherical once it closes off.
- Free-floating water in microgravity (ISS) also pulls itself into a sphere because of surface tension.
- Plateau's laws: where three soap films meet, they meet along a line at 120 degrees; honeycomb (hexagon) walls also
  meet at 120 degrees.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SOAP = '#ff5c85'

def bg(c, t, top='#e9f4ff', bot='#cfe6ff'):
    sky(c, top, bot)
    dust(c, t, seed=6, n=12, a=70, colr='#ffffff')

def square_wand(c, x, y, s, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawLine(0, 120, 0, 420, P(color=col('#2f9bff', a), stroke=22))
    c.drawRoundRect(skia.Rect(-120, -120, 120, 120), 14, 14, P(color=col('#2f9bff', a), stroke=22))
    c.drawRoundRect(skia.Rect(-120, -120, 120, 120), 14, 14, P(color=col('#dff3ff', int(a * 0.25))))
    c.restore()

def soap_mol(c, x, y, s, up=True, t=0.0, seed=0, alpha=255):
    """Surfactant: round water-loving head + wiggly tail pointing into the air."""
    a = int(alpha); d = -1 if up else 1
    p = skia.Path(); p.moveTo(x, y)
    for i in range(1, 9):
        u = i / 8
        p.lineTo(x + math.sin(u * 7 + seed + t * 3) * 7 * s, y + d * u * 70 * s)
    c.drawPath(p, P(color=col('#f2a33a', a), stroke=7 * s))
    c.drawCircle(x, y, 15 * s, P(color=col(SOAP, a)))
    c.drawCircle(x - 4 * s, y - 5 * s, 4.5 * s, P(color=col('#ffffff', int(a * 0.7))))

# ---------- 1: Hook (cold open: square wand, round bubble already coming out) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    bg(c, t)
    square_wand(c, 300, 1150, 1.0)
    label_pill(c, 'SQUARE wand', 300, 1620, size=42, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi='#2f9bff')
    u = (t * 0.45) % 1.0
    for k, off in enumerate((0.0, 0.5)):
        uu = (t * 0.32 + off) % 1.0
        x = lerp(300, 820, ease_out(uu)); y = lerp(1150, 760, uu) + 30 * math.sin(uu * 7 + k)
        r = lerp(60, 140, ease_out(min(1, uu * 2.5)))
        soap_bubble(c, x, y, r, t, alpha=int(255 * min(1, (1 - uu) * 4)))
    if t > t1:
        k = ease_back(prog(t, t1 + 0.6, 0.4))
        label_pill(c, 'ROUND bubble', 780, 1300, size=42, k=k, fill=NAVY, hi=SOAP)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 2: The film: water between two soap layers ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t)
    soap_bubble(c, 540, 880, 170, t)
    zk = ease_out(prog(t, t0 + 0.3, 0.8))
    if zk > 0:
        # connector from bubble wall to the zoom panel
        c.drawLine(690, 950, 540 + 420 * zk, 1100, P(color=col(NAVY, int(120 * zk)), stroke=4))
        c.save(); clip = skia.Path(); clip.addRoundRect(skia.Rect(90, 1060, 990, 1560), 50, 50)
        c.drawPath(clip, P(color=col('#ffffff', int(240 * zk))))
        c.drawPath(clip, P(color=col(NAVY, int(200 * zk)), stroke=5))
        c.clipPath(clip, doAntiAlias=True)
        wb = ease_in_out(prog(t, t0 + 0.6, 0.8))
        c.drawRect(skia.Rect(90, 1310 - 100 * wb, 990, 1310 + 100 * wb), P(color=col('#6cc4ff', int(220 * wb))))
        for i in range(10):
            x = 130 + i * 92
            c.drawCircle(x + 10 * math.sin(t * 2 + i), 1310 + 14 * math.cos(t * 2.3 + i), 9, P(color=col('#ffffff', int(160 * wb))))
        if t > t1:
            for i in range(10):
                x = 135 + i * 92
                kk = ease_back(prog(t, t1 + 0.2 + i * 0.05, 0.35))
                if kk > 0:
                    soap_mol(c, x, 1205 + (1 - kk) * -60, 1.0, up=True, t=t, seed=i, alpha=255)
                    soap_mol(c, x + 46, 1415 + (1 - kk) * 60, 1.0, up=False, t=t, seed=i + 3, alpha=255)
        c.restore()
        label_pill(c, 'WATER', 790, 1310, size=40, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'SOAP layers', 300, 760, size=44, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=SOAP)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 1.2, 'pop'), (t1 + 0.2, 'sparkle'), (t1 + 0.8, 'pop')]

# ---------- 3: Surface tension: water pulls on its neighbours -> elastic skin ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, top='#eef9ff', bot='#d6f0ff')
    if t < t1 + 0.3:
        a = 255 * (1 - prog(t, t1, 0.3))
        pts = [(300 + i * 160, 980 + j * 160) for j in range(3) for i in range(4)]
        pull = 0.5 + 0.5 * math.sin(t * 5)
        for i, (x, y) in enumerate(pts):
            for (x2, y2) in pts:
                if 0 < math.hypot(x2 - x, y2 - y) <= 161 and (x2, y2) > (x, y):
                    c.drawLine(x, y, x2, y2, P(color=col('#2f9bff', int(a * (0.45 + 0.4 * pull))), stroke=6 + 3 * pull))
        for i, (x, y) in enumerate(pts):
            water_molecule(c, x + 6 * math.sin(t * 3 + i), y + 6 * math.cos(t * 3 + i), 40, t, seed=i, face_on=False, alpha=a)
        label_pill(c, 'PULLING on neighbours', 540, 760, size=42, k=ease_back(prog(t, t0 + 0.6, 0.4)) * (a / 255), fill=NAVY, hi='#2f9bff')
    if t > t1:
        k = ease_out(prog(t, t1 + 0.2, 0.5))
        sq = 0.82 + 0.1 * math.sin((t - t1) * 3)
        r = 320 * sq
        c.drawCircle(540, 1180, r, P(color=col('#dff3ff', int(150 * k))))
        c.drawCircle(540, 1180, r, P(color=col('#2f9bff', int(255 * k)), stroke=16))
        for i in range(8):
            ang = i * math.pi / 4
            x0, y0 = 540 + math.cos(ang) * (r + 150), 1180 + math.sin(ang) * (r + 150)
            x1, y1 = 540 + math.cos(ang) * (r + 30), 1180 + math.sin(ang) * (r + 30)
            if 640 < y1 < 1560 and 60 < x1 < 1000:
                arrow(c, x0, y0, x1, y1, colr=SOAP, w=12, alpha=int(255 * k))
        label_pill(c, 'ELASTIC skin', 540, 1180, size=48, k=ease_back(prog(t, t1 + 0.7, 0.4)), fill=NAVY, hi=SOAP)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.1, 'pop'), (t0 + 0.6, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.7, 'boing')]

# ---------- 4: Air pushes back equally in every direction ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t)
    r = 300 + 8 * math.sin(t * 2)
    soap_bubble(c, 540, 1130, r, t)
    air_dots(c, 340, 930, 740, 1330, t, n=26, colr='#9fd4ff', r=12)
    ok = ease_out(prog(t, t0 + 0.6, 0.6))
    for i in range(12):
        ang = i * math.pi / 6 + 0.26
        L = 60 + 40 * ok
        x0, y0 = 540 + math.cos(ang) * (r - 110), 1130 + math.sin(ang) * (r - 110)
        x1, y1 = 540 + math.cos(ang) * (r - 110 + L * 1.8), 1130 + math.sin(ang) * (r - 110 + L * 1.8)
        arrow(c, x0, y0, x1, y1, colr='#2f9bff', w=11, alpha=int(255 * ok))
    label_pill(c, 'AIR pushes out', 540, 760, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'EVERY direction', 540, 1560, size=44, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SOAP)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.3, 'pop')]

# ---------- 5: Smallest surface for the volume = sphere (aha) ----------
def iso_cube(c, x, y, s, alpha=255):
    a = int(alpha)
    top = skia.Path(); top.moveTo(x, y - s); top.lineTo(x + s * 0.87, y - s * 0.5); top.lineTo(x, y); top.lineTo(x - s * 0.87, y - s * 0.5); top.close()
    lft = skia.Path(); lft.moveTo(x - s * 0.87, y - s * 0.5); lft.lineTo(x, y); lft.lineTo(x, y + s); lft.lineTo(x - s * 0.87, y + s * 0.5); lft.close()
    rgt = skia.Path(); rgt.moveTo(x + s * 0.87, y - s * 0.5); rgt.lineTo(x, y); rgt.lineTo(x, y + s); rgt.lineTo(x + s * 0.87, y + s * 0.5); rgt.close()
    for pth, hc in ((top, '#e6f4ff'), (lft, '#9fd4ff'), (rgt, '#6cb8f0')):
        c.drawPath(pth, P(color=col(hc, a))); c.drawPath(pth, P(color=col(NAVY, a), stroke=5))

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, top='#fff8e6', bot='#ffeccc')
    ck = ease_back(prog(t, t0 + 0.2, 0.5))
    if ck > 0:
        c.save(); c.translate(300, 1000); c.rotate(6 * math.sin(t * 1.5)); c.scale(ck, ck); iso_cube(c, 0, 0, 150); c.restore()
    sk = ease_back(prog(t, t0 + 0.8, 0.5))
    if sk > 0:
        soap_bubble(c, 780, 1000, 165 * sk, t)
    label_pill(c, 'same AIR inside', 540, 720, size=44, k=ease_back(prog(t, t0 + 1.3, 0.4)) * (1 - prog(t, t1 + 0.6, 0.3)), fill=NAVY, hi='#2f9bff')
    # surface-area bars (unit volume: cube 6.0, sphere 4.84)
    bk = ease_out(prog(t, t1 - 0.6, 1.2)) if t > t1 - 0.6 else 0
    for x, val, hc, lab in ((300, 6.0, '#8aa0bf', 'AREA 6.0'), (780, 4.84, SOAP, 'AREA 4.8')):
        h_ = 40 * val * bk
        c.drawRoundRect(skia.Rect(x - 70, 1480 - h_, x + 70, 1480), 14, 14, P(color=col(hc)))
        if bk > 0.3: label_pill(c, lab, x, 1550, size=38, k=ease_back(prog(t, t1 - 0.2, 0.4)), fill=NAVY, hi=hc if hc == SOAP else NAVY)
    if t > t1:
        kk = ease_back(prog(t, t1 + 1.0, 0.5), 2.2)
        c.save(); c.translate(780, 790); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-230, -60, 230, 60), 30, 30, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-230, -60, 230, 60), 30, 30, P(color=col(NAVY), stroke=6))
        text_block(c, 'SMALLEST', 0, 0, size=58, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.8, 'pop'), (t0 + 1.3, 'click'), (t1 - 0.6, 'whoosh'), (t1 + 1.0, 'ding')]

# ---------- 6: Water in space does the same ----------
def blob(c, x, y, r, t, wob, alpha=255):
    p = skia.Path(); n = 72
    for i in range(n + 1):
        th = i / n * 2 * math.pi
        rr = r * (1 + wob * (0.12 * math.sin(3 * th + t * 4) + 0.07 * math.sin(5 * th - t * 6)))
        (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(th), y + rr * math.sin(th))
    p.close(); a = int(alpha)
    c.drawPath(p, rad(x - r * 0.3, y - r * 0.4, r * 1.6, [col('#e8f7ff', a), col('#6cc4ff', a), col('#2f80ff', a)], [0, 0.45, 1]))
    c.drawPath(p, P(color=col('#1f63c9', int(a * 0.5)), stroke=4))
    c.drawOval(skia.Rect(x - r * 0.55, y - r * 0.6, x - r * 0.15, y - r * 0.25), P(color=col('#ffffff', int(a * 0.75)), blur=3))

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    wob = 1.6 * (1 - ease_out(prog(t, t0 + 0.5, max(2.5, t1 - t0 + 1.5))))
    blob(c, 540 + 20 * math.sin(t * 0.7), 1120 + 14 * math.cos(t * 0.9), 220, t, wob)
    label_pill(c, 'water in SPACE', 540, 760, size=44, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'pulls into a BALL', 540, 1500, size=44, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=SOAP)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 0.8, 'boing'), (t1 + 0.4, 'pop')]

# ---------- 7: Wild part: walls meet at 120 degrees, like a honeycomb ----------
def bubble_cluster(c, cx, cy, r, t, k=1.0):
    d = r * 1.15
    cs = [(cx + d / math.sqrt(3) * math.cos(a), cy + d / math.sqrt(3) * math.sin(a)) for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6)]
    a = int(255 * k)
    for i, (x, y) in enumerate(cs):
        c.save()
        for j, (x2, y2) in enumerate(cs):
            if j != i:
                cl = skia.Path(); cl.addCircle(x2, y2, r); c.clipPath(cl, skia.ClipOp.kDifference, True)
        soap_bubble(c, x, y, r, t + i, alpha=a)
        c.restore()
    # straight shared walls from the centre to the outer intersection points
    h = math.sqrt(max(0, r * r - (d / 2) ** 2))
    ends = []
    for i in range(3):
        (x1, y1), (x2, y2) = cs[i], cs[(i + 1) % 3]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        vx, vy = mx - cx, my - cy; L = math.hypot(vx, vy)
        ex, ey = mx + vx / L * h, my + vy / L * h
        ends.append((ex, ey))
        c.drawLine(cx, cy, ex, ey, P(color=col('#ffffff', a), stroke=10))
        c.drawLine(cx, cy, ex, ey, P(color=col('#5aa9ff', a), stroke=4))
    return ends

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, top='#f1ecff', bot='#e1ebff')
    mk = ease_out(prog(t, t0 + 0.3, 1.0))
    cy = 1080
    if t < t1 + 0.5:
        al = 1 - prog(t, t1 + 0.1, 0.4)
        c.saveLayerAlpha(None, int(255 * al))
        ends = bubble_cluster(c, 540, cy, 210, t, k=mk)
        ak = ease_out(prog(t, t0 + 2.0, 0.6))
        if ak > 0:
            for (ex, ey) in ends:
                pass
            angs = [math.degrees(math.atan2(ey - cy, ex - 540)) for ex, ey in ends]
            for i in range(3):
                a0 = angs[i]; sw = ((angs[(i + 1) % 3] - a0) % 360)
                c.drawArc(skia.Rect(540 - 60, cy - 60, 540 + 60, cy + 60), a0 + 8, (sw - 16) * ak, False, P(color=col('#ffd23f'), stroke=9))
            label_pill(c, '120°', 540, 1460, size=54, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=NAVY)
        c.restore()
        label_pill(c, 'shared WALLS', 540, 720, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)) * al, fill=NAVY, hi='#2f9bff')
    if t > t1 + 0.5:
        hk = ease_back(prog(t, t1 + 0.5, 0.6))
        c.save(); c.translate(540, 1100); c.scale(hk, hk); c.translate(-540, -1100)
        honeycomb(c, 260, 900, 5, 4, 70)
        c.restore()
        label_pill(c, 'like a HONEYCOMB', 540, 1500, size=46, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi='#e8a200')
        label_pill(c, '120° everywhere', 540, 740, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=NAVY)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 1.0, 'pop'), (t0 + 2.0, 'sparkle'), (t0 + 2.4, 'click'), (t1 + 0.7, 'whoosh'), (t1 + 1.2, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    bg(c, t)
    for k, off in enumerate((0.0, 0.33, 0.66)):
        uu = (t * 0.18 + off) % 1.0
        soap_bubble(c, 200 + k * 330 + 40 * math.sin(t + k), lerp(1500, 750, uu), 70 + 30 * k, t + k, alpha=int(255 * min(1, (1 - uu) * 5, uu * 5)))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        bat(c, 790, 980, 0.8 * kk, t)
        label_pill(c, 'next: BATS', 400, 980, size=48, k=kk, fill=NAVY, hi='#9b4dff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why are bubbles round?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why are bubbles round?', 'Why are BUBBLES round?'),
            ('Blow through a square wand, and you still get a perfect sphere.', 'Square wand, ROUND bubble')], tail=0.8),
        dict(name='film', draw=s2, sfx_fn=s2_sfx, lines=[
            ('A bubble is a super thin layer of water,', 'A thin layer of WATER'),
            ('sandwiched between two layers of soap.', 'between two layers of SOAP')], tail=0.9),
        dict(name='tension', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Water molecules pull on their neighbors.', 'Water PULLS on itself'),
            ('So the film acts like a stretched elastic skin, always trying to shrink.', 'Like an ELASTIC skin')], tail=0.8),
        dict(name='air', draw=s4, sfx_fn=s4_sfx, lines=[
            ('But the air trapped inside pushes back,', 'The AIR pushes back'),
            ('with the same force in every direction.', 'Equally in EVERY direction')], tail=0.8),
        dict(name='sphere', draw=s5, sfx_fn=s5_sfx, lines=[
            ('So the film shrinks until it wraps that air with as little surface as possible.', 'As little SURFACE as possible'),
            ('And for any amount of air, the shape with the smallest surface is a sphere.', 'The SPHERE wins')], tail=1.2),
        dict(name='space', draw=s6, sfx_fn=s6_sfx, ambience='space', lines=[
            ('Same reason water floating in space wobbles,', 'Water in SPACE'),
            ('then pulls itself into a perfect ball.', 'pulls into a BALL')], tail=1.0),
        dict(name='angles', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: when bubbles stick together, their shared walls always meet at 120 degrees.", 'Walls meet at 120 DEGREES'),
            ('The exact same angle as the walls of a honeycomb.', 'Just like a HONEYCOMB')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So bubbles are round because the film pulls itself into the smallest surface it can.', 'The SMALLEST surface wins'),
            ('Next up: how bats find their way in the dark.', 'Next: how BATS see in the dark'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
