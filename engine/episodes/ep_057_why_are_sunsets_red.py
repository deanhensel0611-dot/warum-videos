"""Episode 57 (EN, general audience): Why are sunsets red?
Facts checked (NASA Space Place "Why is the sky blue?"; NOAA/NWS and NBC News "What makes skies blue ... or red?";
NASA Science "What does a sunrise/sunset look like on Mars?"; NASA SVS "Curiosity sees blue sunset on Mars" (2015)):
- Sunlight contains all visible colours. Gas molecules in air scatter short (blue) wavelengths much more strongly than
  long (red) ones (Rayleigh scattering) - that is why the daytime sky is blue.
- With the Sun low on the horizon, its light crosses far more atmosphere (about 38-40 times the overhead air mass at
  the horizon). Along that long path most blue light is scattered out, so the light that reaches us is mostly orange
  and red. Clouds lit from below by that light glow red/pink.
- On Mars the daytime sky is butterscotch, and sunsets have a blue glow around the Sun: fine Martian dust scatters
  blue light forward (towards the Sun's direction) more efficiently (Curiosity images, 2015).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
ORANGE = '#ff8a3c'
BLUE_L = '#3f8cff'

def dusk_sky(c, k):
    top = mix_hx('#2f9bff', '#2b2f78', k); mid = mix_hx('#7cc4ff', '#ff7a5c', k); bot = mix_hx('#cfe8ff', '#ffd27a', k)
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, 1400), [col(top), col(mid), col(bot)], pos=[0, 0.6, 1]))

def sunset_sea(c, t, sun_y=1250, k=1.0, cloud_glow=0.0):
    dusk_sky(c, k)
    sc = mix_hx('#ffd23f', '#ff6a3c', k)
    c.drawCircle(540, sun_y, 520, rad(540, sun_y, 520, [col('#ffd27a', 150), col('#ff9a5c', 60), col('#ff9a5c', 0)], [0, 0.4, 1]))
    c.drawCircle(540, sun_y, 120, rad(540, sun_y - 30, 150, [col('#fff6d0'), col(sc), col(mix_hx(sc, '#ff3c3c', 0.4))], [0, 0.55, 1]))
    if cloud_glow > 0:
        for (x, y, s) in ((230, 820, 1.2), (830, 760, 1.0), (620, 960, 0.8)):
            cloud(c, x, y, s, a=int(235 * cloud_glow))
            c.save(); c.translate(x, y + 20 * s)
            c.drawOval(skia.Rect(-150 * s, -10 * s, 150 * s, 40 * s), P(color=col('#ff6a8a', int(170 * cloud_glow)), blur=10))
            c.restore()
    # sea covers the lower half of the sun
    sea_y = 1300
    c.drawRect(skia.Rect(0, sea_y, W, H), lin(c, (0, sea_y, 0, H), [col(mix_hx('#3f6fb8', '#5a3c7a', k)), col(mix_hx('#1a3f8f', '#2b2050', k))]))
    for i in range(9):
        yy = sea_y + 20 + i * 34; ww = 220 - i * 18 + 20 * math.sin(t * 2 + i)
        c.drawRoundRect(skia.Rect(540 - ww, yy, 540 + ww, yy + 9), 5, 5, P(color=col(mix_hx('#ffd27a', '#ff7a5c', k), 200 - i * 18)))
    c.drawLine(0, sea_y, W, sea_y, P(color=col('#ffffff', 90), stroke=3))

COLORS = ['#ff3c3c', '#ff8a3c', '#ffe14d', '#5cd65c', '#3f8cff', '#8a5cff']

# ---------- 1: Hook (cold open: sun already setting) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    u = clamp(t / D)
    sunset_sea(c, t, sun_y=1200 + 90 * ease_in_out(u), k=0.75 + 0.25 * u)
    label_pill(c, 'same SUN', 540, 720, size=50, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'LONGER trip', 540, 840, size=50, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.05, 'sparkle'), (t1 + 0.3, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 2: Sunlight is every colour ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#1b2a4a', '#2b3f6a')
    sun(c, 150, 1100, 100, t, glow=True)
    bk = ease_out(prog(t, t0 + 0.2, 0.6))
    x1 = lerp(250, 560, bk)
    c.drawLine(250, 1100, x1, 1100, P(color=col('#ffffff', 120), stroke=60, blur=12))
    c.drawLine(250, 1100, x1, 1100, P(color=col('#ffffff'), stroke=30))
    sk = ease_out(prog(t, t0 + 0.8, 0.9))
    if sk > 0:
        for i, cc in enumerate(COLORS):
            ang = math.radians(-25 + i * 10)
            L = 480 * sk
            c.drawLine(560, 1100, 560 + math.cos(ang) * L, 1100 + math.sin(ang) * L, P(color=col(cc, 110), stroke=34, blur=8))
            c.drawLine(560, 1100, 560 + math.cos(ang) * L, 1100 + math.sin(ang) * L, P(color=col(cc), stroke=18))
        c.drawCircle(560, 1100, 26, P(color=col('#ffffff')))
    label_pill(c, 'WHITE light', 330, 900, size=44, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'ALL colors inside', 720, 1500, size=44, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 0.8, 'sparkle'), (t0 + 1.6, 'pop')]

# ---------- 3: Air scatters blue ----------
MOLS3 = [(260, 900), (470, 1180), (700, 880), (860, 1250), (330, 1400), (620, 1460), (900, 1010)]
BLUE_PATH = [(-60, 820), (260, 900), (700, 880), (470, 1180), (860, 1250), (620, 1460), (330, 1400), (-80, 1650)]

def path_at(pts, u):
    segs = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    L = sum(segs) * clamp(u)
    for i, s in enumerate(segs):
        if L <= s or i == len(segs) - 1:
            k = L / s if s else 0
            return lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)
        L -= s

def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#3aa9ff', '#d8f2ff', mid='#86ccff')
    for i, (mx, my) in enumerate(MOLS3):
        molecule(c, mx, my + math.sin(t * 1.8 + i) * 8, 46, t, i)
    # red goes straight through
    rk = prog(t, t0 + 0.3, 1.6)
    if 0 < rk < 1:
        f = lambda tt: (lerp(-60, 1140, prog(tt, t0 + 0.3, 1.6)), 1060)
        trail(c, [f(t - k * 0.02) for k in range(18, -1, -1)], '#ff4d4d', 20)
        photon(c, *f(t), 34, '#ff4d4d', t, 1, face_on=False)
    bk = prog(t, t0 + 1.2, D - t0 - 1.6)
    if 0 < bk < 1:
        f = lambda tt: path_at(BLUE_PATH, prog(tt, t0 + 1.2, D - t0 - 1.6))
        trail(c, [f(t - k * 0.02) for k in range(22, -1, -1)], BLUE_L, 20)
        photon(c, *f(t), 34, BLUE_L, t, 2, face_on=False)
    label_pill(c, 'RED: straight through', 540, 720, size=40, k=ease_back(prog(t, t0 + 0.8, 0.4)) * (1 - prog(t, t0 + 2.0, 0.3)), fill=NAVY, hi='#e8264f')
    if t > t0 + 2.0:
        label_pill(c, 'BLUE: bounced around', 540, 720, size=40, k=ease_back(prog(t, t0 + 2.1, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'blue SKY', 540, 1580, size=48, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SKYB)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 1.2, 'whoosh'), (t0 + 2.1, 'pop'), (t1 + 0.3, 'pop')]

# ---------- 4/5: Earth diagram, short vs long path ----------
EX, EY, ER, ATM = 640, 2000, 900, 160
OBS = (EX, EY - ER)

def earth_diag(c, t, night=0.0):
    sky(c, '#0b1430', '#1b2a4a')
    stars(c, t, seed=8, n=50, y0=0, y1=1500, a=0.5)
    c.drawCircle(EX, EY, ER + ATM, rad(EX, EY, ER + ATM, [col('#7cc4ff', 0), col('#9fd6ff', 200), col('#7cc4ff', 90)], [0.84, 0.86, 1]))
    c.drawCircle(EX, EY, ER + ATM, P(color=col('#d8efff', 200), stroke=5))
    c.drawCircle(EX, EY, ER, rad(EX - ER * 0.3, EY - ER * 0.7, ER * 1.6, [col('#6cc8ff'), col('#2f80ff'), col('#1a4fb8')], [0, 0.4, 1]))
    c.save(); clip = skia.Path(); clip.addCircle(EX, EY, ER); c.clipPath(clip, doAntiAlias=True)
    for (lx, ly, lw, lh) in ((-520, -760, 300, 120), (-160, -870, 420, 70), (260, -800, 360, 150), (-700, -520, 220, 200), (520, -560, 260, 180)):
        c.drawOval(skia.Rect(EX + lx - lw / 2, EY + ly - lh / 2, EX + lx + lw / 2, EY + ly + lh / 2), lin(c, (0, EY + ly - lh, 0, EY + ly + lh), [col('#7ed957'), col('#4fae3a')]))
    c.restore()
    c.drawCircle(EX, EY, ER, P(color=col('#ffffff', 140), stroke=5))
    label_pill(c, 'AIR', EX + 470, EY - ER - 40, size=34, k=1.0, fill=NAVY, hi=SKYB)

def you_pin(c, x, y, k=1.0):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    p = skia.Path(); p.moveTo(0, 0); p.cubicTo(-22, -34, -34, -50, -34, -70); p.cubicTo(-34, -94, -17, -106, 0, -106)
    p.cubicTo(17, -106, 34, -94, 34, -70); p.cubicTo(34, -50, 22, -34, 0, 0); p.close()
    c.drawPath(p, lin(c, (0, -106, 0, 0), [col('#ff7a9a'), col('#e8264f')]))
    c.drawPath(p, P(color=col('#ffffff'), stroke=5))
    c.drawCircle(0, -72, 12, P(color=col('#ffffff')))
    c.restore()

def beam(c, x0, y0, x1, y1, k, c0, c1, w=30):
    if k <= 0: return
    xe, ye = lerp(x0, x1, k), lerp(y0, y1, k)
    c.drawLine(x0, y0, xe, ye, P(color=col(c1, 90), stroke=w * 2, blur=10))
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap)
    paint.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [col(c0), col(c1)]))
    c.drawLine(x0, y0, xe, ye, paint)

def s4(c, t, D, cues):
    t0 = cues[0]['start']
    earth_diag(c, t)
    sun(c, OBS[0], 720, 70, t, glow=True)
    you_pin(c, OBS[0], OBS[1], ease_back(prog(t, t0 + 0.1, 0.4)))
    bk = ease_out(prog(t, t0 + 0.8, 0.8))
    beam(c, OBS[0], 800, OBS[0], OBS[1] - 110, bk, '#fff6d0', '#ffe68a', w=26)
    label_pill(c, 'NOON', 300, 760, size=48, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'SHORT path', 330, 1560, size=48, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.1, 'pop'), (t0 + 0.4, 'pop'), (t0 + 0.8, 'whoosh'), (t0 + 1.8, 'pop')]

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    earth_diag(c, t)
    sx = 70; sy = OBS[1]
    sun(c, sx, sy, 60, t, glow=True)
    you_pin(c, OBS[0], OBS[1], 1.0)
    bk = ease_in_out(prog(t, t0 + 0.6, 1.6))
    redk = ease_in_out(prog(t, t1, 1.2))
    beam(c, sx + 60, sy - 40, OBS[0] - 30, OBS[1] - 40, bk, '#fff6d0', mix_hx('#fff6d0', '#ff5a2c', redk), w=26)
    # blue light scattered out along the way
    if t > t1 - 0.3:
        rnd = random.Random(6)
        for i in range(22):
            st = t1 - 0.3 + i * 0.09
            ph = prog(t, st, 1.4)
            if ph <= 0 or ph >= 1: continue
            u = rnd.uniform(0.05, 0.9); bx = lerp(sx + 60, OBS[0] - 30, u); by = sy - 40
            ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = 260 * ease_out(ph)
            photon(c, bx + math.cos(ang) * d, by + math.sin(ang) * d, 18, BLUE_L, t, face_on=False, alpha=int(255 * (1 - ph)))
    label_pill(c, 'SUNSET', 300, 760, size=48, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi=ORANGE)
    label_pill(c, '~40× more air', 330, 1560, size=46, k=ease_back(prog(t, t0 + 2.2, 0.4)) * (1 - prog(t, t1 + 0.2, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'BLUE scattered away', 360, 1560, size=44, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 0.6, 'whoosh'), (t0 + 2.2, 'pop'), (t1 - 0.3, 'sparkle'), (t1 + 0.5, 'ding')]

# ---------- 6: What's left: red; clouds glow ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sunset_sea(c, t, sun_y=1260, k=1.0, cloud_glow=ease_out(prog(t, t1 + 0.2, 0.8)))
    rk = ease_out(prog(t, t0 + 0.3, 0.8))
    for i, cc in enumerate(('#ff3c3c', '#ff8a3c', '#ffb43c')):
        x = lerp(540, 300 + i * 240, rk)
        photon(c, x, 1100 + math.sin(t * 3 + i) * 12, 36 * rk, cc, t, i, face_on=False)
    label_pill(c, "what's LEFT: red + orange", 540, 700, size=42, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'CLOUDS light up', 540, 1580, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'sparkle'), (t1 + 0.4, 'pop')]

# ---------- 7: Wild part: blue sunsets on Mars ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    dk = ease_in_out(prog(t, t0 + 0.4, 1.6))
    top = mix_hx('#c9a27a', '#4a3a3a', dk); bot = mix_hx('#e8c9a0', '#8a6a5a', dk)
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, 1350), [col(top), col(bot)]))
    sy = 1180 + 60 * dk
    bl = ease_out(prog(t, t0 + 1.0, 1.4))
    c.drawCircle(540, sy, 420, rad(540, sy, 420, [col('#cfeaff', int(255 * bl)), col('#6fb0f0', int(200 * bl)), col('#5f9fe0', 0)], [0, 0.4, 1]))
    c.drawCircle(540, sy, 44, P(color=col('#f4fbff')))
    # ground
    g = skia.Path(); g.moveTo(0, 1300)
    for i in range(0, W + 1, 60): g.lineTo(i, 1300 + 30 * math.sin(i * 0.008 + 1) + 15 * math.sin(i * 0.03))
    g.lineTo(W, H); g.lineTo(0, H); g.close()
    c.drawPath(g, lin(c, (0, 1280, 0, H), [col(mix_hx('#b0603a', '#5a3020', dk)), col(mix_hx('#7a3a22', '#3a1a12', dk))]))
    rnd = random.Random(3)
    for i in range(9):
        rx, ry, rr = rnd.uniform(40, 1040), rnd.uniform(1360, 1650), rnd.uniform(14, 40)
        c.drawOval(skia.Rect(rx - rr * 1.4, ry - rr, rx + rr * 1.4, ry + rr * 0.4), P(color=col(mix_hx('#5a2a18', '#2a120a', dk))))
    label_pill(c, 'MARS', 540, 720, size=56, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=ORANGE)
    label_pill(c, 'BLUE sunset', 540, 840, size=48, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'fine DUST', 540, 1560, size=46, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=ORANGE)
        dust(c, t, seed=9, n=26, a=int(150 * prog(t, t1 + 0.3, 0.6)), colr='#f0d2a8')

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 1.0, 'sparkle'), (t0 + 2.0, 'pop'), (t1 + 0.5, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sunset_sea(c, t, sun_y=1290, k=1.0, cloud_glow=1.0)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'long path → blue LOST', 540, 700, size=44, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: how a MICROWAVE heats', 540, 820, size=40, k=kk, fill=NAVY, hi=HOT)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why are sunsets red?',
    music=False, faces=False, ambience='water',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why are sunsets red?', 'Why are SUNSETS red?'),
            ("The Sun doesn't change color. Its light just takes a longer trip.", 'A LONGER trip')], tail=0.9),
        dict(name='white', draw=s2, sfx_fn=s2_sfx, ambience='space', lines=[
            ('Sunlight looks white, but it is a mix of every color.', 'Sunlight = ALL colors')], tail=1.2),
        dict(name='scatter', draw=s3, sfx_fn=s3_sfx, ambience='wind', lines=[
            ('Air molecules scatter blue light the most, bouncing it all over the sky.', 'Air scatters BLUE'),
            ("That's why the daytime sky is blue.", 'Hence the blue SKY')], tail=1.0),
        dict(name='noon', draw=s4, sfx_fn=s4_sfx, ambience='space', lines=[
            ('At noon, sunlight comes from above and crosses a thin layer of air.', 'Noon: a SHORT path')], tail=1.2),
        dict(name='sunset', draw=s5, sfx_fn=s5_sfx, trans='punch', ambience='space', lines=[
            ('At sunset, it skims in sideways, through around forty times more air.', 'Sunset: a LONG path'),
            ('Along the way, most of the blue gets scattered out.', 'The BLUE gets lost')], tail=1.3),
        dict(name='left', draw=s6, sfx_fn=s6_sfx, lines=[
            ("What's left is mostly orange and red.", 'What reaches you: RED'),
            ('And clouds catch that light and glow, too.', 'CLOUDS glow too')], tail=1.0),
        dict(name='mars', draw=s7, sfx_fn=s7_sfx, ambience='wind', lines=[
            ("Here's the wild part: on Mars, sunsets are blue.", 'On MARS: blue sunsets'),
            ('Fine Martian dust sends blue light forward, so the glow around the Sun turns blue.', 'DUST sends blue forward')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So sunsets are red because the blue got lost on the long way.', 'The blue got LOST'),
            ('Next: how a microwave heats food.', 'Next: MICROWAVES'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
