"""Episode 16 (EN): Why does the Sun shine?"""
import math, random
from lib import *

H_COL = '#5fa8ff'    # hydrogen
HE_COL = '#ff7fb0'   # helium
DAY = ('#2f9bff', '#cdeeff')

def flash(c, x, y, k, r=120):
    """Energy burst, k = 0..1 progress."""
    if k <= 0 or k >= 1: return
    a = 1 - k
    c.drawCircle(x, y, r * (0.4 + k), rad(x, y, r * (0.4 + k), [col('#ffffff', int(255 * a)), col('#fff3a0', int(200 * a)), col('#ffb627', 0)]))
    for j in range(8):
        ang = j * math.pi / 4 + 0.2
        r0, r1 = r * (0.3 + k * 0.8), r * (0.6 + k * 1.2)
        c.drawLine(x + math.cos(ang) * r0, y + math.sin(ang) * r0, x + math.cos(ang) * r1, y + math.sin(ang) * r1, P(color=col('#fff3a0', int(255 * a)), stroke=10))

def sun_section(c, x, y, r, t, core_glow=1.0):
    """Sun cut in half: glowing layers with a bright core."""
    c.drawCircle(x, y, r * 1.5, rad(x, y, r * 1.5, [col('#fff6b0', 130), col('#fff6b0', 0)]))
    c.drawCircle(x, y, r, rad(x, y, r, [col('#ffd23f'), col('#ff9f1c'), col('#ff6b2c')], [0, 0.7, 1]))
    for k, (rr, hx, a) in enumerate([(0.72, '#ffb627', 255), (0.42, '#ffe14d', 255), (0.25, '#fffbe0', 255)]):
        wob = 1 + 0.015 * math.sin(t * 3 + k)
        c.drawCircle(x, y, r * rr * wob, rad(x, y, r * rr, [col('#ffffff', a), col(hx, a)], [0, 1]))
    c.drawCircle(x, y, r * 0.3, rad(x, y, r * 0.3, [col('#ffffff', int(200 * core_glow)), col('#ffffff', 0)]))
    for k in (0.42, 0.72, 1.0):
        c.drawCircle(x, y, r * k, P(color=col('#e8701a', 90), stroke=4))
    # bubbling surface granules
    for i in range(18):
        ang = i / 18 * 2 * math.pi + t * 0.15
        c.drawCircle(x + math.cos(ang) * r * 0.86, y + math.sin(ang) * r * 0.86, r * 0.06 * (1 + 0.3 * math.sin(t * 4 + i)), P(color=col('#ffd23f', 160)))

def hydrogen(c, x, y, r, t, seed=0, vel=(0, 0), alpha=255):
    photon(c, x, y, r, H_COL, t, seed, vel=vel, alpha=alpha)

def helium(c, x, y, r, t, seed=0, alpha=255):
    photon(c, x, y, r, HE_COL, t, seed, alpha=alpha)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    k = ease_back(prog(t, 0.05, 0.9), 1.3)
    sy = lerp(1900, 1040, k) + math.sin(t * 2) * 10
    sunbeams(c, 540, sy, t, a=30)
    clouds(c, t, seed=2, n=3, y0=650, y1=900)
    sun(c, 540, sy, 210, t, mood='wow' if t < 2.0 else 'happy')
    hills(c, 1640, t=t, trees=True)
    for i in range(6):
        ang = i / 6 * 2 * math.pi + t * 0.4
        x, y = 540 + math.cos(ang) * 360, 1040 + math.sin(ang) * 330
        a = prog(t, 0.6 + i * 0.12, 0.35)
        if a > 0:
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=100, fill=['#ffffff', '#ffe14d', '#ff8fab'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
            c.restore()

def s1_sfx(D, cues): return [(0.2, 'whoosh')]

# ---------- 2: The Sun is a star, a giant ball of gas ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=31)
    sx, sy, sr = 540, 1080, 330
    c.drawCircle(sx, sy, sr * 1.25, rad(sx, sy, sr * 1.25, [col('#fff6b0', 120), col('#fff6b0', 0)]))
    sun(c, sx, sy, 240, t, glow=True)
    # gas swirls on the surface
    if t > t1:
        fill = ease_in_out(prog(t, t1 + 0.6, 2.4))
        # tiny Earths filling the Sun
        c.save(); clip = skia.Path(); clip.addCircle(sx, sy, 240); c.clipPath(clip, doAntiAlias=True)
        rnd = random.Random(4); n = 420
        for i in range(int(n * fill)):
            ang = rnd.uniform(0, 2 * math.pi); rr = 240 * math.sqrt(rnd.random())
            x, y = sx + math.cos(ang) * rr, sy + math.sin(ang) * rr
            c.drawCircle(x, y, 5.5, P(color=col('#2f80ff', 220)))
            c.drawCircle(x - 1.5, y - 1.5, 2.5, P(color=col('#5fd068', 230)))
        c.restore()
        k = ease_back(prog(t, t1, 0.5))
        c.save(); c.translate(880, 1460); c.scale(k, k)
        earth(c, 0, 0, 30, t, face_on=False)
        c.restore()
        if t > t1 + 0.4:
            g = prog(t, t1 + 0.4, 0.4)
            c.drawLine(840, 1430, 760, 1350, P(color=col('#ffffff', int(200 * g)), stroke=6))
    if t > t1 + 3.2:
        k = ease_back(prog(t, t1 + 3.2, 0.5), 2.2)
        c.save(); c.translate(540, 1480); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-230, -60, 230, 60), 50, 50, P(color=col('#ffffff', 240)))
        text_block(c, '1,000,000+', 0, 0, size=72, fill='#2f80ff', stroke='#ffffff')
        c.restore()

def s2_sfx(D, cues): return [(cues[1]['start'] + 0.1, 'pop'), (cues[1]['start'] + 0.6, 'sparkle'), (cues[1]['start'] + 3.2, 'pop')]

# ---------- 3: Squeezed + hot in the middle, hydrogen bits zoom ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=41)
    sx, sy = 540, 1350
    sun_section(c, sx, sy, 300, t, core_glow=0.6 + 0.4 * math.sin(t * 4))
    # squeeze arrows
    sq = 1 + 0.06 * math.sin(t * 5)
    if t > t0 + 0.6:
        a = prog(t, t0 + 0.6, 0.5)
        for j in range(6):
            ang = j * math.pi / 3 + math.pi / 6
            r0, r1 = 260 * sq, 170 * sq
            x0, y0 = sx + math.cos(ang) * r0, sy + math.sin(ang) * r0
            x1, y1 = sx + math.cos(ang) * r1, sy + math.sin(ang) * r1
            c.drawLine(x0, y0, x1, y1, P(color=col('#ffffff', int(220 * a)), stroke=12))
            hd = skia.Path(); nx, ny = math.cos(ang), math.sin(ang)
            hd.moveTo(x1 - nx * 18, y1 - ny * 18); hd.lineTo(x1 + nx * 12 - ny * 20, y1 + ny * 12 + nx * 20); hd.lineTo(x1 + nx * 12 + ny * 20, y1 + ny * 12 - nx * 20); hd.close()
            c.drawPath(hd, P(color=col('#ffffff', int(220 * a))))
    # zoom lens with hydrogen bits
    if t > t1 - 0.3:
        k = ease_back(prog(t, t1 - 0.3, 0.6))
        lx, ly, lr = 540, 820, 190 * k
        c.drawLine(sx, sy, lx, ly + lr, P(color=col('#ffffff', 160), stroke=6))
        def inner(cc):
            cc.drawCircle(lx, ly, lr, rad(lx, ly, lr, [col('#fffbe0'), col('#ffd23f'), col('#ff9f1c')]))
            for i in range(5):
                def f(tt, i=i):
                    return (lx + math.sin(tt * (2.1 + i * 0.37) + i * 2) * 130, ly + math.sin(tt * (1.7 + i * 0.29) + i) * 130)
                x, y = f(t); vx = (f(t)[0] - f(t - 1 / 60)[0]) * 60; vy = (f(t)[1] - f(t - 1 / 60)[1]) * 60
                hydrogen(cc, x, y, 30, t, i, vel=(vx, vy))
        magnifier(c, lx, ly, lr, inner, t)
        if t > t1 + 0.5:
            j = ease_back(prog(t, t1 + 0.5, 0.4))
            c.save(); c.translate(200, 1000); c.scale(j, j)
            c.drawRoundRect(skia.Rect(-135, -44, 135, 44), 36, 36, P(color=col('#ffffff', 240)))
            text_block(c, 'hydrogen', 0, 0, size=50, fill=H_COL, stroke='#ffffff')
            c.restore()

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[1]['start'] - 0.2, 'pop')]

# ---------- 4: Crash, stick together -> helium + energy ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#ffb627', '#fff3a0', mid='#ffd23f')
    c.drawCircle(540, 1100, 700, rad(540, 1100, 700, [col('#ffffff', 120), col('#ffffff', 0)]))
    dust(c, t, seed=4, n=20, colr='#fffbe0')
    cx, cy = 540, 1120
    rnd = random.Random(12)
    for i in range(16):
        bx, by = rnd.uniform(60, 1020), rnd.uniform(650, 1620); sp = rnd.uniform(0.6, 1.2)
        x = bx + math.sin(t * sp + i) * 70; y = by + math.cos(t * sp * 0.8 + i * 2) * 60
        if math.dist((x, y), (cx, cy)) < 330: continue
        photon(c, x, y, 20, H_COL if i % 3 else HE_COL, t, i, face_on=False, alpha=170)
    # phase 1: pairs crash (t0+0.6 .. t0+1.6), phase 2: merge into helium (t1-0.2)
    m1 = prog(t, t0 + 0.4, 1.0) ** 2
    pairs = [((-330, -260), (-90, -90)), ((330, -260), (90, -90)), ((-330, 280), (-90, 90)), ((330, 280), (90, 90))]
    m2 = prog(t, t1 + 1.4, 0.8) ** 2
    if m2 < 1:
        for i, ((x0, y0), (x1, y1)) in enumerate(pairs):
            x = cx + lerp(x0, x1, m1); y = cy + lerp(y0, y1, m1)
            x = lerp(x, cx, m2); y = lerp(y, cy, m2)
            hydrogen(c, x, y, 52, t, i, vel=((x1 - x0) * (1 - m1) * 3, (y1 - y0) * (1 - m1) * 3))
    th = t1 + 2.2
    if t >= th:
        k = ease_back(prog(t, th, 0.5), 2.0)
        c.save(); c.translate(cx, cy + math.sin(t * 2) * 8); c.scale(k, k)
        helium(c, 0, 0, 130, t, 3)
        c.restore()
        if t > th + 0.4:
            j = ease_back(prog(t, th + 0.4, 0.4))
            c.save(); c.translate(cx, cy + 240); c.scale(j, j)
            c.drawRoundRect(skia.Rect(-130, -46, 130, 46), 36, 36, P(color=col('#ffffff', 240)))
            text_block(c, 'helium', 0, 0, size=56, fill=HE_COL, stroke='#ffffff')
            c.restore()
    # crash flashes
    if t > t0 + 1.4:
        flash(c, cx, cy, prog(t, t0 + 1.4, 0.7), 150)
    tb = t1 + 3.5
    if t > tb:
        for q in range(3):
            st = tb + q * 0.35
            flash(c, cx + [-260, 250, 0][q], cy + [-300, -260, 380][q], prog(t, st, 0.8), 140)
        c.drawCircle(cx, cy, 400, P(color=col('#ffffff', int(90 * (1 - prog(t, tb, 1.2))))))

def s4_sfx(D, cues): return [(cues[0]['start'] + 1.4, 'boing'), (cues[1]['start'] + 2.2, 'pop'), (cues[1]['start'] + 3.5, 'sparkle')]

# ---------- 5: Trillions of times -> light + heat ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sx, sy = 230, 790
    sunbeams(c, sx, sy, t, a=36, n=12)
    # many tiny pops inside the sun
    sun(c, sx, sy, 160, t)
    rnd = random.Random(8)
    n = int(lerp(3, 16, ease_in_out(prog(t, t0 + 0.3, 2.5))))
    for i in range(n):
        ph = rnd.random(); ang = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(110, 175)
        k = ((t * 1.3 + ph) % 1.0)
        flash(c, sx + math.cos(ang) * rr, sy + math.sin(ang) * rr, k, 28)
    clouds(c, t, seed=5, n=2, y0=1050, y1=1150, a=200)
    hills(c, 1640, t=t, trees=True)
    if t > t1:
        a = prog(t, t1, 0.6)
        for i in range(4):
            u = ((t - t1) * 0.5 + i / 4) % 1.0
            x = lerp(sx + 120, 700, u); y = lerp(sy + 120, 1380, u)
            photon(c, x, y, 26, '#ffe14d', t, i, alpha=int(255 * a * min(1, (1 - u) * 5)), vel=(500, 600))
        # warm glow around the kid
        c.drawCircle(720, 1480, 260, rad(720, 1480, 260, [col('#ffb627', int(80 * a)), col('#ffb627', 0)]))
    kid(c, 720, 1700, 0.85, t, wave=t > t1 + 0.6)
    if t > t1 + 1.0:
        for i, (lbl, x, y, hx) in enumerate([('LIGHT', 440, 1150, '#ffe14d'), ('HEAT', 900, 1180, '#ff7a45')]):
            j = ease_back(prog(t, t1 + 1.0 + i * 0.4, 0.4))
            c.save(); c.translate(x, y); c.scale(j, j)
            c.drawRoundRect(skia.Rect(-125, -46, 125, 46), 36, 36, P(color=col('#ffffff', 240)))
            text_block(c, lbl, 0, 0, size=56, fill=hx, hi=hx, stroke='#ffffff')
            c.restore()

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'sparkle'), (cues[1]['start'] + 1.0, 'pop'), (cues[1]['start'] + 1.4, 'pop')]

# ---------- 6: Bonus: 8 minutes to Earth ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=61)
    sx, sy = 120, 1100; ex, ey = 900, 1100
    sun(c, sx, sy, 190, t)
    earth(c, ex, ey, 85, t, rot=t * 0.05, face_on=True, mood='happy')
    # dotted path
    for i in range(22):
        x = lerp(sx + 210, ex - 100, i / 21)
        c.drawCircle(x, sy, 5, P(color=col('#ffffff', 90)))
    T0 = t0 + 0.6; T1 = D - 1.0
    u = ease_in_out(prog(t, T0, T1 - T0))
    if t > T0:
        f = lambda tt: (lerp(sx + 210, ex - 100, ease_in_out(prog(tt, T0, T1 - T0))), sy + math.sin(tt * 4) * 18)
        if 0.02 < u < 0.98: trail(c, [f(t - k * 0.03) for k in range(14, -1, -1)], '#fff3b0', 18)
        x, y = f(t)
        if u < 1: photon(c, x, y, 34, '#ffe14d', t, 2, vel=(400, 0))
        else: flash(c, ex, ey, prog(t, T1, 0.8), 160)
    # clock
    k = ease_back(prog(t, t1 - 0.2, 0.5))
    if k > 0:
        cx, cy = 540, 1420
        c.save(); c.translate(cx, cy); c.scale(k, k)
        c.drawCircle(0, 0, 120, P(color=col('#ffffff', 245)))
        c.drawCircle(0, 0, 120, P(color=col('#2f80ff'), stroke=12))
        for q in range(12):
            a = q * math.pi / 6
            c.drawLine(math.sin(a) * 95, -math.cos(a) * 95, math.sin(a) * 108, -math.cos(a) * 108, P(color=col('#1b2a4a'), stroke=6))
        mins = 8 * u
        ma = mins / 60 * 2 * math.pi; sa = mins * 2 * math.pi
        c.drawLine(0, 0, math.sin(sa) * 85, -math.cos(sa) * 85, P(color=col('#ff4d6d'), stroke=6))
        c.drawLine(0, 0, math.sin(ma) * 70, -math.cos(ma) * 70, P(color=col('#1b2a4a'), stroke=12))
        c.drawCircle(0, 0, 10, P(color=col('#1b2a4a')))
        c.restore()
        c.save(); c.translate(cx, cy + 180); c.scale(k, k)
        text_block(c, f'{int(round(mins))} min', 0, 0, size=72, fill='#ffffff', stroke='#1b2a4a')
        c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[1]['start'] - 0.2, 'pop'), (D - 1.0, 'sparkle')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    sunbeams(c, 540, 1040, t, a=30)
    clouds(c, t + 40, seed=7, n=3, y0=650, y1=900)
    hills(c, 1660, t=t, trees=True)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1040 + math.sin(t * 2) * 12); c.scale(s, s); sun(c, 0, 0, 200, t); c.restore()
    for i in range(6):
        ang = t * 0.9 + i * math.pi / 3
        x, y = 540 + math.cos(ang) * 380, 1040 + math.sin(ang) * 330
        if i % 2: helium(c, x, y, 34, t, i)
        else: hydrogen(c, x, y, 30, t, i)
    follow_button(c, t, cues[-1]['start'])

def s7_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why does the Sun shine?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why does the Sun shine?', 'Why does the SUN shine?'),
            ("Let's find out!", "Let's find out!")], tail=0.9),
        dict(name='star', draw=s2, sfx_fn=s2_sfx, lines=[
            ('The Sun is a star: a giant ball of super hot gas.', 'The Sun is a STAR!'),
            ("It's so big, more than a million Earths could fit inside!", 'A MILLION Earths fit inside!')], tail=1.9),
        dict(name='core', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Deep in its middle, the Sun is squeezed super tight, and super hot.', 'Its middle: SQUEEZED and HOT'),
            ('There, tiny bits called hydrogen zoom around and crash into each other.', 'Tiny HYDROGEN bits crash!')], tail=1.4),
        dict(name='fusion', draw=s4, sfx_fn=s4_sfx, lines=[
            ('When they crash really hard, they stick together.', 'Crash! They STICK together'),
            ('Step by step, they become something new, called helium. And pop! A burst of energy comes out!', 'New HELIUM … and ENERGY!')], tail=1.4),
        dict(name='light', draw=s5, sfx_fn=s5_sfx, lines=[
            ('This happens trillions and trillions of times, every second.', 'TRILLIONS of times a second!'),
            ('All those tiny bursts make the light and heat we see and feel!', 'That makes LIGHT and HEAT!'),
            ("But never look straight at the Sun. It's way too bright for your eyes!", 'NEVER stare at the SUN!')], tail=1.6),
        dict(name='eight', draw=s6, sfx_fn=s6_sfx, lines=[
            ('And guess what? Sunlight is super fast.', 'Sunlight is SUPER fast …'),
            ('But it still takes about eight minutes to get all the way to us!', '… but it takes 8 MINUTES to us!')], tail=2.4),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.2),
    ])
