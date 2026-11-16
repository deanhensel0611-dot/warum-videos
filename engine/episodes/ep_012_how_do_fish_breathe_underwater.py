"""Episode 12 (EN): How do fish breathe underwater?"""
import math, random
from lib import *

O2 = '#5ff0ff'

def qmarks(c, t, start=0.6):
    spots = [(170, 760), (900, 820), (150, 1080), (910, 1130), (200, 1380), (880, 1420)]
    for i, (sx, sy) in enumerate(spots):
        a = prog(t, start + i * 0.12, 0.35)
        if a <= 0: continue
        x = sx + math.sin(t * 1.3 + i) * 18; y = sy + math.cos(t * 1.7 + i * 2) * 22
        c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
        text_block(c, '?', 0, 0, size=96 + (i % 3) * 16, fill=['#ffffff', '#ffe14d', '#7fe3ff'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
        c.restore()

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    underwater(c, t)
    rising_bubbles(c, t, seed=3, n=16)
    k = ease_out(prog(t, 0.05, 1.0))
    x = lerp(-300, 540, k); y = 1100 + math.sin(t * 1.8) * 25
    fish(c, x, y, 1.8, t, mouth=0.5 + 0.5 * math.sin(t * 4), gill=0.5 + 0.5 * math.sin(t * 4 - 1.2))
    for j in range(3):
        u = ((t * 0.7 + j / 3) % 1.0)
        bubble(c, x + 200 + math.sin(t * 3 + j) * 10, y - 40 - u * 380, 14 + 10 * u, int(220 * (1 - u)))
    qmarks(c, t, 0.8)

def s1_sfx(D, cues): return [(0.2, 'whoosh')]

# ---------- 2: We need oxygen, fish too ----------
def s2(c, t, D, cues):
    sea_y = 1230
    sky(c, '#3aa9ff', '#d8f2ff', mid='#86ccff')
    sun(c, 860, 720, 70, t)
    clouds(c, t, seed=2, n=2, y0=650, y1=760, a=220)
    beach = skia.Path(); beach.moveTo(0, 1000); beach.cubicTo(200, 990, 380, 1080, 470, sea_y + 20); beach.lineTo(0, sea_y + 20); beach.close()
    sea(c, sea_y, t)
    c.save(); c.clipRect(skia.Rect(0, sea_y + 20, W, H))
    c.drawRect(skia.Rect(0, sea_y + 20, W, H), lin(c, (0, sea_y, 0, H), [col('#3fa9ff', 0), col('#0b3f8f', 200)]))
    c.restore()
    c.drawPath(beach, lin(c, (0, 1000, 0, sea_y), [col('#ffe3a3'), col('#e9b968')]))
    # kid breathing in oxygen
    kx, ky = 230, 1150
    kid(c, kx, ky, 0.62, t, look_up=False, wave=t > cues[1]['start'] + 0.3)
    nose = (kx, ky - 305 * 0.62 + 10)
    a1 = prog(t, cues[0]['start'] + 0.3, 0.4)
    if a1 > 0:
        for i in range(6):
            u = (t * 0.45 + i / 6) % 1.0
            sx_, sy_ = 620 + (i % 3) * 90, 700 + (i % 2) * 120
            x = lerp(sx_, nose[0] + 50, ease_in_out(u)); y = lerp(sy_, nose[1], ease_in_out(u)) + math.sin(u * 6 + i) * 20
            oxygen_dot(c, x, y, 16, t, alpha=int(255 * a1 * min(1, (1 - u) * 5)))
    # fish
    f = ease_out(prog(t, cues[1]['start'], 0.8))
    if f > 0:
        fx = lerp(1300, 700, f); fy = 1500 + math.sin(t * 2) * 15
        fish(c, fx, fy, 1.1, t, flip=True, seed=2)
        for j in range(3):
            ang = t * 2 + j * 2.1
            oxygen_dot(c, fx + math.cos(ang) * 200, fy + math.sin(ang) * 110, 14, t, alpha=int(255 * f))
    rising_bubbles(c, t, seed=4, n=6, y0=sea_y + 40, y1=1700, alpha=150)

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'sparkle'), (cues[1]['start'] + 0.1, 'whoosh')]

# ---------- 3: Oxygen hides in the water ----------
def s3(c, t, D, cues):
    underwater(c, t + 10, seed=3)
    fish(c, 250 + math.sin(t * 0.6) * 40, 1450, 0.7, t, seed=4)
    rising_bubbles(c, t, seed=5, n=8, alpha=140)
    zk = max(0.0, ease_back(prog(t, cues[0]['start'] + 0.2, 0.7), 1.6))
    if zk <= 0.01: return
    def inner(c):
        c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 720, 0, 1400), [col('#bfeaff'), col('#4fa8ee')]))
        rnd = random.Random(12)
        for i in range(14):
            bx, by = rnd.uniform(300, 780), rnd.uniform(800, 1360)
            water_molecule(c, bx + math.sin(t * 1.5 + i) * 40, by + math.cos(t * 1.3 + i * 2) * 35, 40, t, seed=i, rot=math.sin(t + i) * 40, face_on=False, alpha=200)
        glow = ease_out(prog(t, cues[0]['start'] + 1.0, 0.6))
        for i in range(6):
            bx, by = 330 + (i % 3) * 210, 900 + (i // 3) * 300
            x = bx + math.sin(t * 1.1 + i * 2) * 50; y = by + math.cos(t * 0.9 + i) * 40
            s_ = ease_back(prog(t, cues[0]['start'] + 1.0 + i * 0.12, 0.4), 2.2)
            if s_ > 0:
                oxygen_dot(c, x, y, 30 * s_, t, seed=i, face_on=True, alpha=255)
                sp = 0.5 + 0.5 * math.sin(t * 6 + i)
                c.drawCircle(x + 36, y - 36, 6 * sp * glow, P(color=col('#ffffff')))
    c.save(); c.translate(540, 1080); c.scale(zk, zk); c.translate(-540, -1080)
    magnifier(c, 540, 1080, 400, inner, t)
    c.restore()
    if t > cues[1]['start']:
        a = prog(t, cues[1]['start'] + 0.2, 0.4)
        text_block(c, 'O = oxygen', 540, 1560, size=58, alpha=int(255 * a))

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 1.0, 'sparkle')]

# ---------- 4: In through the mouth, out over the gills ----------
FX, FY, FS = 520, 1120, 2.2
def s4(c, t, D, cues):
    underwater(c, t + 20, seed=4, weeds=True)
    gulp = 0.5 + 0.5 * math.sin(t * 3.2)
    gill = 0.5 + 0.5 * math.sin(t * 3.2 - 1.6)
    mx, my = FX + 0.9 * 130 * FS, FY + 0.18 * 80 * FS          # mouth
    gx, gy = FX + 0.35 * 130 * FS - 20, FY + 60                  # behind the gill flap
    a_in = prog(t, cues[0]['start'] + 0.2, 0.5)
    a_out = prog(t, cues[1]['start'] + 0.2, 0.5)
    # incoming water stream (in front of the mouth)
    for i in range(10):
        u = (t * 0.55 + i / 10) % 1.0
        x = lerp(1060, mx + 10, u); y = my + math.sin(u * 7 + i) * 40 * (1 - u)
        al = int(255 * a_in * min(1, u * 6) * min(1, (1 - u) * 8))
        if i % 3 == 0: oxygen_dot(c, x, y, 13, t, alpha=al)
        else: bubble(c, x, y, 11, int(al * 0.8))
    fish(c, FX, FY, FS, t, mouth=gulp * a_in + 0.15, gill=gill * max(a_out, 0.2), seed=1)
    # outgoing water from the gills (oxygen gone -> plain bubbles)
    for i in range(8):
        u = (t * 0.5 + i / 8) % 1.0
        x = gx - 30 - u * 260; y = gy + 50 + u * 220 + math.sin(u * 6 + i) * 25
        al = int(220 * a_out * min(1, u * 6) * min(1, (1 - u) * 6))
        bubble(c, x, y, 10 + 4 * u, al)
    if a_in > 0:
        ar = skia.Path(); ar.moveTo(1010, my - 120); ar.quadTo(900, my - 150, mx + 60, my - 70)
        c.drawPath(ar, P(color=col('#ffffff', int(230 * a_in)), stroke=12))
        hd = skia.Path(); hd.moveTo(mx + 40, my - 95); hd.lineTo(mx + 50, my - 55); hd.lineTo(mx + 85, my - 78); hd.close()
        c.drawPath(hd, P(color=col('#ffffff', int(230 * a_in))))
    if a_out > 0:
        ar = skia.Path(); ar.moveTo(gx - 40, gy + 150); ar.quadTo(gx - 120, gy + 300, gx - 300, gy + 330)
        c.drawPath(ar, P(color=col('#ffe14d', int(240 * a_out)), stroke=12))
        hd = skia.Path(); hd.moveTo(gx - 290, gy + 300); hd.lineTo(gx - 330, gy + 335); hd.lineTo(gx - 285, gy + 360); hd.close()
        c.drawPath(hd, P(color=col('#ffe14d', int(240 * a_out))))
        text_block(c, 'gills', gx - 120, gy - 300, size=56, alpha=int(255 * a_out))
        c.drawLine(gx - 100, gy - 265, gx - 10, gy - 95, P(color=col('#ffffff', int(255 * a_out)), stroke=6))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.3, 'whoosh')]

# ---------- 5: Gills catch the oxygen ----------
def s5(c, t, D, cues):
    sky(c, '#2a8fe0', '#0b3f8f', mid='#1f6fc4')
    rising_bubbles(c, t, seed=8, n=8, alpha=110)
    zk = ease_out(prog(t, 0.0, 0.6))
    ys = [800 + i * 130 for i in range(7)]
    # big red blood vessel on the left that collects the oxygen
    vx = 200
    c.drawRoundRect(skia.Rect(vx - 34, 700, vx + 34, 1640), 34, 34, lin(c, (vx - 34, 0, vx + 34, 0), [col('#ff6b7a'), col('#d8233f')], vertical=False))
    for k in range(6):
        yy = (t * 160 + k * 160) % 940 + 700
        c.drawCircle(vx, yy, 14, P(color=col('#ffb3bd', 200)))
    for i, y in enumerate(ys):
        L = 700 * zk; x0 = vx
        sw = math.sin(t * 2 + i) * 6
        c.drawLine(x0, y, x0 + L, y + sw, P(color=col('#ff8a96'), stroke=34))
        for k in range(1, 18):
            px = x0 + L * k / 18
            if px > x0 + L - 10: break
            for sgn in (-1, 1):
                c.drawLine(px, y + sw * k / 18, px + 14, y + sgn * 38 + sw * k / 18, P(color=col('#ff6b7a'), stroke=9))
        c.drawLine(x0, y, x0 + L, y + sw, P(color=col('#ffd0d6', 160), stroke=8))
    # water flowing past, oxygen gets caught
    t1 = cues[1]['start']
    for i in range(14):
        rnd = random.Random(i)
        row = rnd.randrange(len(ys)); y_row = ys[row] + rnd.choice([-65, 65])
        period = 3.0; ph = rnd.uniform(0, period)
        u = ((t + ph) % period) / period
        x = lerp(1150, 120, u); y = y_row + math.sin(u * 8 + i) * 12
        caught = t > t1 and (t + ph) % period > 0.0 and x < 760
        if caught:
            # pulled in to the filament and along it to the blood vessel
            cx_ = lerp(760, vx, (760 - x) / 640); cy_ = lerp(y_row, ys[row], min(1, (760 - x) / 120))
            hexc = mix_hx(O2, '#ff3b5c', clamp((760 - x) / 500))
            oxygen_dot(c, max(vx, cx_), cy_, 15, t, hexcol=hexc)
        else:
            oxygen_dot(c, x, y, 15, t, alpha=int(255 * min(1, u * 8)))
    for i in range(10):
        u = (t * 0.4 + i / 10) % 1.0
        bubble(c, lerp(1150, 0, u), 760 + (i * 97) % 820, 9, int(150 * min(1, u * 6)))
    if t > t1:
        a = prog(t, t1 + 0.4, 0.4)
        for i in range(3):
            sx_, sy_ = 560 + i * 120, 1580
            pass
        text_block(c, 'blood', vx + 10, 660, size=50, alpha=int(255 * a), fill='#ffd0d6')

def s5_sfx(D, cues): return [(cues[1]['start'] + 0.4, 'sparkle')]

# ---------- 6: Blood carries oxygen everywhere ----------
def s6(c, t, D, cues):
    underwater(c, t + 30, seed=6)
    rising_bubbles(c, t, seed=9, n=10, alpha=150)
    x = 520 + math.sin(t * 0.8) * 50; y = 1130 + math.sin(t * 1.6) * 20; s = 2.2
    fish(c, x, y, s, t, gill=0.5 + 0.5 * math.sin(t * 3), seed=6)
    g = ease_in_out(prog(t, cues[0]['start'] + 0.3, 1.2))
    if g > 0:
        G = (x + 0.3 * 130 * s, y + 10)
        tg = [(x - 115 * s, y), (x - 40 * s, y - 55 * s), (x - 30 * s, y + 55 * s), (x - 85 * s, y + 30 * s), (x - 80 * s, y - 32 * s)]
        def bez(T, u):
            cx_, cy_ = (G[0] + T[0]) / 2, (G[1] + T[1]) / 2 + (T[1] - G[1]) * 0.3 - 20
            return ((1 - u) ** 2 * G[0] + 2 * (1 - u) * u * cx_ + u * u * T[0], (1 - u) ** 2 * G[1] + 2 * (1 - u) * u * cy_ + u * u * T[1])
        for j, T in enumerate(tg):
            gj = clamp(g * 1.3 - j * 0.05)
            pth = skia.Path(); pth.moveTo(*G)
            for k in range(1, 21):
                if k / 20 > gj: break
                pth.lineTo(*bez(T, k / 20))
            c.drawPath(pth, P(color=col('#ff3b5c', 90), stroke=22, blur=6))
            c.drawPath(pth, P(color=col('#ff4d6a'), stroke=9))
            if g >= 1:
                for k in range(3):
                    u = (t * 0.5 + k / 3 + j * 0.13) % 1.0
                    px, py = bez(T, u)
                    oxygen_dot(c, px, py, 11, t, hexcol='#ff9aa8', alpha=int(255 * min(1, (1 - u) * 5)))
        c.drawCircle(*G, 22 + 3 * math.sin(t * 5), P(color=col('#ff3b5c')))
    hp = prog(t, cues[-1]['start'] + 0.3, 0.6)
    if hp > 0:
        for j in range(5):
            ang = t * 1.5 + j * 2 * math.pi / 5
            px, py = x + math.cos(ang) * 420, y + math.sin(ang) * 260
            st = skia.Path()
            for q in range(10):
                rr = (20 if q % 2 == 0 else 8) * ease_back(hp, 2); aa = q * math.pi / 5 + t * 2
                (st.moveTo if q == 0 else st.lineTo)(px + math.cos(aa) * rr, py + math.sin(aa) * rr)
            st.close(); c.drawPath(st, P(color=col('#ffe14d')))

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[-1]['start'] + 0.3, 'sparkle')]

# ---------- 7: Bonus: sharks keep swimming ----------
def s7(c, t, D, cues):
    underwater(c, t + 40, seed=7, weeds=True)
    sx = 1250 - ((t * 150) % 1800) * 0.0 - ease_in_out(prog(t, 0.1, 2.0)) * 620
    sy = 1100 + math.sin(t * 1.5) * 25
    # stream lines rushing past the shark
    for i in range(12):
        rnd = random.Random(i)
        yy = sy + rnd.uniform(-220, 220); L = rnd.uniform(80, 180)
        x = ((rnd.uniform(0, W) + t * 700) % (W + 400)) - 200
        c.drawLine(x, yy, x + L, yy, P(color=col('#ffffff', 110), stroke=6))
    fish(c, sx, sy, 1.9, t, kind='shark', flip=True, seed=3, wiggle=1.6)
    a = prog(t, cues[1]['start'] + 0.2, 0.5)
    if a > 0:
        hx = sx - 0.28 * 190 * 1.9 + 40
        for i in range(6):
            u = (t * 0.9 + i / 6) % 1.0
            x = lerp(sx - 420, hx, u); y = sy + (i - 2.5) * 16 + math.sin(u * 5 + i) * 6
            oxygen_dot(c, x, y, 11, t, alpha=int(255 * a * min(1, (1 - u) * 5)))
        c.drawCircle(hx, sy, 80 + 8 * math.sin(t * 5), P(color=col('#ffe14d', int(220 * a)), stroke=8))
    rising_bubbles(c, t, seed=11, n=8, alpha=140)

def s7_sfx(D, cues): return [(0.2, 'whoosh'), (cues[1]['start'] + 0.3, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    underwater(c, t + 50, seed=8)
    s = max(0.0, ease_back(prog(t, 0.0, 0.7), 2.0))
    c.save(); c.translate(540, 1050 + math.sin(t * 2) * 12); c.scale(s, s)
    fish(c, 0, 0, 1.8, t, gill=0.5 + 0.5 * math.sin(t * 3), mouth=0.3 + 0.3 * math.sin(t * 3), seed=8)
    c.restore()
    for i in range(6):
        ang = t * 0.9 + i * math.pi / 3
        oxygen_dot(c, 540 + math.cos(ang) * 400, 1050 + math.sin(ang) * 300, 22, t, seed=i, face_on=True)
    rising_bubbles(c, t, seed=12, n=14, alpha=170)
    follow_button(c, t, cues[-1]['start'])

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='How do fish breathe underwater?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('How do fish breathe underwater?', 'How do FISH breathe underwater?'),
            ("Let's find out!", "Let's find out!")], tail=1.1),
        dict(name='oxygen', draw=s2, sfx_fn=s2_sfx, lines=[
            ('We breathe air. It has oxygen in it, and our bodies need oxygen.', 'Our bodies need OXYGEN'),
            ('Fish need oxygen too!', 'Fish need it TOO!')], tail=1.8),
        dict(name='inwater', draw=s3, sfx_fn=s3_sfx, lines=[
            ("Here's the secret: water has tiny bits of oxygen mixed into it.", 'Oxygen hides in the WATER!'),
            ('Way too small to see!', 'Too TINY to see!')], tail=1.8),
        dict(name='gulp', draw=s4, sfx_fn=s4_sfx, lines=[
            ('A fish gulps water in through its mouth.', 'Water goes in the MOUTH'),
            ('Then the water flows out over its gills, on the sides of its head.', '… and out over the GILLS')], tail=2.0),
        dict(name='catch', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Gills look like tiny feathery combs, full of tiny blood vessels.', 'Gills: like feathery COMBS'),
            ('As the water flows past, they catch the oxygen, like a net!', 'They CATCH the oxygen!')], tail=2.0),
        dict(name='body', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Then the fish's blood carries the oxygen all around its body.", 'Blood carries it EVERYWHERE'),
            ("That's how fish breathe underwater!", "That's how fish BREATHE!")], tail=1.9),
        dict(name='shark', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? Some sharks have to keep swimming,', 'Some SHARKS keep swimming!'),
            ('so fresh water keeps flowing over their gills!', 'Fresh water over the GILLS')], tail=1.8),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
