"""Episode 9 (EN): Why do we have seasons?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
TILT = 23.5

def season_panel(c, x, y, w, h, kind, t):
    """Small rounded picture card for a season."""
    c.save(); clip = skia.Path(); clip.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), 40, 40))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - w / 2 + 6, y - h / 2 + 12, x + w / 2 + 6, y + h / 2 + 12), 40, 40), P(color=col('#000000', 50), blur=10))
    c.clipPath(clip, doAntiAlias=True)
    skies = dict(spring=('#7cc6ff', '#e2f6ff'), summer=('#2f9bff', '#bfe9ff'), autumn=('#ff9f6b', '#ffe3b8'), winter=('#9fb4d6', '#eef4fb'))
    c.drawRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), lin(c, (0, y - h / 2, 0, y + h / 2), [col(skies[kind][0]), col(skies[kind][1])]))
    gy = y + h * 0.28
    gcol = dict(spring='#7ed957', summer='#56b83a', autumn='#c9b14a', winter='#f4f8fc')[kind]
    c.drawOval(skia.Rect(x - w, gy, x + w, gy + h), P(color=col(gcol)))
    if kind == 'summer': sun(c, x + w * 0.22, y - h * 0.22, w * 0.13, t)
    if kind == 'spring':
        for i, p in enumerate(['#ff8fab', '#ffd23f', '#c79bff']):
            flower(c, x - w * 0.25 + i * w * 0.25, gy - 10, 0.35, t, i, petal=p, face_on=False)
    if kind == 'autumn':
        leafy_tree(c, x, gy + 20, 0.38, t, autumn=1.0, seed=2)
    if kind == 'winter':
        pth = skia.Path()
        c.drawCircle(x, gy - 20, 45, P(color=col('#ffffff'))); c.drawCircle(x, gy - 85, 32, P(color=col('#ffffff')))
        c.drawCircle(x - 10, gy - 90, 4, P(color=col('#2b1d0e'))); c.drawCircle(x + 10, gy - 90, 4, P(color=col('#2b1d0e')))
        c.drawLine(x, gy - 82, x + 20, gy - 78, P(color=col('#ff9f1c'), stroke=6))
        for i in range(8):
            rnd = random.Random(i); xx = x - w / 2 + rnd.uniform(0, w); yy = y - h / 2 + ((t * 40 + rnd.uniform(0, h)) % h)
            snowflake(c, xx, yy, 8, t, i)
    c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), 40, 40), P(color=col('#ffffff'), stroke=8))

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    space(c, t, seed=3)
    a = ease_back(prog(t, 0.1, 0.8), 1.5)
    c.save(); c.translate(540, 1110); c.scale(a, a); tilted_earth(c, 0, 0, 170, t, mood='wow' if t < 2.0 else 'happy'); c.restore()
    for i, (kind, ang) in enumerate([('spring', -135), ('summer', -45), ('autumn', 45), ('winter', 135)]):
        k = ease_back(prog(t, 0.6 + i * 0.25, 0.5))
        if k <= 0: continue
        r = 330
        x = 540 + math.cos(math.radians(ang)) * r * 0.95; y = 1110 + math.sin(math.radians(ang)) * r * 1.05
        c.save(); c.translate(x, y + math.sin(t * 2 + i) * 8); c.scale(k, k); season_panel(c, 0, 0, 250, 250, kind, t); c.restore()

def s1_sfx(D, cues): return [(0.1, 'whoosh')] + [(0.6 + i * 0.25, 'pop') for i in range(4)]

# ---------- 2: One trip around the Sun + tilt ----------
def orbit_pos(u, cx=540, cy=1100, rx=360, ry=180):
    a = 2 * math.pi * u
    return cx + math.cos(a) * rx, cy + math.sin(a) * ry

def s2(c, t, D, cues):
    space(c, t, seed=5)
    t0, t1 = cues[0]['start'], cues[1]['start']
    g = ease_in_out(prog(t, t0, 0.8))
    pth = skia.Path(); pth.addOval(skia.Rect(540 - 360, 1100 - 180, 540 + 360, 1100 + 180))
    c.drawPath(pth, P(color=col('#ffffff', int(90 * g)), stroke=5))
    u = 0.25 + ease_in_out(prog(t, t0, max(1.0, t1 - t0 - 0.1)))
    ex, ey = orbit_pos(u)
    grow = ease_in_out(prog(t, t1, 0.8))
    ey += 110 * grow
    behind = math.sin(2 * math.pi * u) < 0
    def draw_earth():
        tilt = TILT * ease_in_out(prog(t, t1 + 0.2, 0.8)) if t > t1 else 0
        sc_ = (0.85 + 0.15 * math.sin(2 * math.pi * u)) * (1 + 0.6 * grow)
        tilted_earth(c, ex, ey, 85 * sc_, t, tilt=tilt, sun_dir=math.degrees(math.atan2(1100 - ey, 540 - ex)), face_on=True, axis=t > t1)
    if behind: draw_earth()
    sunbeams(c, 540, 1100, t, a=18); sun(c, 540, 1100, 120, t)
    if not behind: draw_earth()
    if t > t0 + 0.4:
        text_block(c, '1 year', 540, 1460, size=64, alpha=int(255 * prog(t, t0 + 0.4, 0.4) * (1 - prog(t, t1, 0.4))))
    # spinning top analogy
    if t > t1 + 1.2:
        k = ease_back(prog(t, t1 + 1.2, 0.5))
        c.drawOval(skia.Rect(800 - 70 * k, 1572, 800 + 70 * k, 1588), P(color=col('#000000', 90), blur=4))
        c.save(); c.translate(800, 1520); c.scale(k * 1.3, k * 1.3); c.rotate(-TILT + math.sin(t * 3) * 3)
        tp = skia.Path(); tp.moveTo(0, 60); tp.lineTo(-80, -20); tp.quadTo(0, -70, 80, -20); tp.close()
        c.drawPath(tp, lin(c, (-80, 0, 80, 0), [col('#ff6b6b'), col('#ffd23f')], vertical=False))
        c.drawOval(skia.Rect(-80, -42, 80, 0), lin(c, (0, -42, 0, 0), [col('#ffe680'), col('#ffb627')]))
        sw = (t * 2.5) % 1.0
        c.drawLine(-60 + sw * 120, -14, -40 + sw * 80, 30, P(color=col('#ffffff', 170), stroke=8))
        c.drawLine(0, -50, 0, -110, P(color=col('#8a5a2b'), stroke=12))
        c.restore()

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 0.3, 'boing')]

# ---------- 3/4: Leaning toward / away ----------
def big_tilt_scene(c, t, D, cues, summer=True):
    space(c, t, seed=7 if summer else 9)
    t0, t1 = cues[0]['start'], cues[1]['start']
    sx, sy = 120, 1080
    tilt = -TILT if summer else TILT   # negative: top leans left, towards the sun
    sunbeams(c, sx, sy, t, a=22, length=1300)
    # rays
    for i in range(7):
        yy = 820 + i * 90
        u = (t * 0.6 + i * 0.13) % 1.0
        c.drawLine(sx + 140, yy, 560, yy, P(color=col('#fff3b0', 70), stroke=10))
        c.drawCircle(lerp(sx + 140, 560, u), yy, 9, P(color=col('#fff3b0', int(220 * math.sin(u * math.pi)))))
    sun(c, sx, sy, 130, t)
    ex, ey = 700, 1080; r = 230
    a = ease_back(prog(t, 0.1, 0.6))
    c.save(); c.translate(ex, ey); c.scale(a, a)
    tilted_earth(c, 0, 0, r, t, tilt=tilt, sun_dir=180, face_on=False, night=0.45)
    # highlight "our" half (north): a glowing marker
    k = prog(t, t0 + 0.6, 0.5)
    if k > 0:
        ang = math.radians(tilt - 90 + (-28 if summer else 28))
        px, py = math.cos(math.radians(tilt - 90)) * r * 0.62, math.sin(math.radians(tilt - 90)) * r * 0.62
        house(c, px, py, 0.5 * ease_back(k), ang=tilt)
    c.restore()
    if t > t1:
        b = ease_back(prog(t, t1, 0.6))
        x0, y0 = 830, 1500
        c.save(); c.translate(x0 - 150, y0); c.scale(b, b)
        if summer:
            sun(c, -120, -40, 45, t, glow=False)
            text_block(c, 'LONG DAYS', 120, -40, size=50, fill='#ffffff')
        else:
            snowflake(c, -150, -40, 40, t)
            text_block(c, 'SHORT DAYS', 100, -40, size=50, fill='#ffffff')
        c.restore()
        if not summer: snow(c, t, seed=2, n=18, y0=620, y1=1700, alpha=int(200 * prog(t, t1 + 0.4, 0.6)))

def s3(c, t, D, cues): big_tilt_scene(c, t, D, cues, True)
def s4(c, t, D, cues): big_tilt_scene(c, t, D, cues, False)
def s34_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 5: Flashlight analogy ----------
def s5(c, t, D, cues):
    sky(c, '#1b2350', '#3a4a8a', mid='#26306a')
    t0, t1 = cues[0]['start'], cues[1]['start']
    gy = 1500
    c.drawRect(skia.Rect(0, gy, W, H), lin(c, (0, gy, 0, H), [col('#6a5a8a'), col('#4a3f66')]))
    # straight torch
    on1 = prog(t, t0 + 0.2, 0.3)
    if on1 > 0:
        bm = skia.Path(); bm.moveTo(300 - 40, 900); bm.lineTo(300 + 40, 900); bm.lineTo(300 + 95, gy); bm.lineTo(300 - 95, gy); bm.close()
        c.drawPath(bm, lin(c, (0, 900, 0, gy), [col('#fff6b0', int(150 * on1)), col('#fff6b0', int(60 * on1))]))
        c.drawOval(skia.Rect(300 - 100, gy - 22, 300 + 100, gy + 22), P(color=col('#fff6b0', int(250 * on1)), blur=6))
        c.drawOval(skia.Rect(300 - 60, gy - 12, 300 + 60, gy + 12), P(color=col('#ffffff', int(250 * on1))))
    flashlight(c, 300, 900, 90, 1.0, on1)
    if t > t0 + 0.9:
        k = ease_back(prog(t, t0 + 0.9, 0.5))
        c.save(); c.translate(300, 1575); c.scale(k, k); text_block(c, 'BRIGHT!', 0, 0, size=62, fill='#fff6b0'); c.restore()
    # slanted torch
    on2 = prog(t, t1 + 0.2, 0.3)
    lx, ly = 900, 1000
    if on2 > 0:
        bm = skia.Path(); bm.moveTo(lx - 30, ly - 30); bm.lineTo(lx + 30, ly + 30); bm.lineTo(720, gy); bm.lineTo(420, gy); bm.close()
        c.drawPath(bm, lin(c, (0, ly, 0, gy), [col('#fff6b0', int(110 * on2)), col('#fff6b0', int(35 * on2))]))
        c.drawOval(skia.Rect(400, gy - 24, 740, gy + 24), P(color=col('#fff6b0', int(130 * on2)), blur=8))
    flashlight(c, lx, ly, 135, 1.0, on2)
    if t > t1 + 0.9:
        k = ease_back(prog(t, t1 + 0.9, 0.5))
        c.save(); c.translate(640, 1575); c.scale(k, k); text_block(c, 'weaker', 0, 0, size=52, fill='#cfe6ff'); c.restore()

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'pop'), (cues[1]['start'] + 0.2, 'pop')]

# ---------- 6: Opposite halves ----------
def s6(c, t, D, cues):
    space(c, t, seed=11)
    t0, t1 = cues[0]['start'], cues[1]['start']
    sx, sy = 120, 1080
    sunbeams(c, sx, sy, t, a=18, length=1200); sun(c, sx, sy, 110, t)
    ex, ey, r = 640, 1080, 250
    tilted_earth(c, ex, ey, r, t, tilt=-TILT, sun_dir=180, face_on=False, night=0.4)
    k = ease_back(prog(t, t0 + 0.3, 0.5))
    # top label
    if k > 0:
        c.save(); c.translate(ex + 30, ey - r - 70); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-150, -50, 150, 50), 50, 50, P(color=col('#ffb627')))
        text_block(c, 'SUMMER', 0, 0, size=56, fill='#ffffff', hi='#ffffff', stroke='#b86a00'); c.restore()
    k2 = ease_back(prog(t, t0 + 1.4, 0.5))
    if k2 > 0:
        c.save(); c.translate(ex - 40, ey + r + 75); c.scale(k2, k2)
        c.drawRoundRect(skia.Rect(-150, -50, 150, 50), 50, 50, P(color=col('#5aa9ff')))
        text_block(c, 'WINTER', 0, 0, size=56, fill='#ffffff', hi='#ffffff', stroke='#1f4f9a'); c.restore()
    if t > t1:
        b = ease_back(prog(t, t1, 0.6))
        c.save(); c.translate(860, 1460); c.scale(b, b)
        # tiny Christmas tree at the beach
        c.drawOval(skia.Rect(-110, 40, 110, 80), P(color=col('#ffd98a')))
        for i, (wd, y0) in enumerate([(70, 40), (55, -10), (40, -55)]):
            p = skia.Path(); p.moveTo(-wd, y0); p.lineTo(0, y0 - 60); p.lineTo(wd, y0); p.close(); c.drawPath(p, P(color=col('#2fae4a')))
        c.drawCircle(0, -118, 12, P(color=col('#ffd23f')))
        for dx, dy, h in [(-30, 20, '#ff6b6b'), (25, -15, '#5aa9ff'), (-10, -40, '#ff6b6b')]: c.drawCircle(dx, dy, 8, P(color=col(h)))
        c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 7: Bonus: closest in January ----------
def s7(c, t, D, cues):
    space(c, t, seed=13)
    t0, t1 = cues[0]['start'], cues[1]['start']
    cx, cy = 600, 1100
    pth = skia.Path(); pth.addOval(skia.Rect(cx - 400, cy - 260, cx + 400, cy + 260))
    c.drawPath(pth, P(color=col('#ffffff', 70), stroke=5))
    sx, sy = cx - 150, cy   # sun slightly off-centre (exaggerated!)
    sunbeams(c, sx, sy, t, a=16, length=1000); sun(c, sx, sy, 100, t)
    # Earth sits at the near point, shivering, with a scarf
    k = ease_back(prog(t, t0 + 0.2, 0.6))
    ex, ey = cx - 400, cy
    c.save(); c.translate(ex + 30 + math.sin(t * 30) * 2 * (t > t0 + 0.8), ey); c.scale(k, k)
    tilted_earth(c, 0, 0, 80, t, tilt=TILT, sun_dir=0, face_on=True, mood='wow', axis=True)
    c.drawRoundRect(skia.Rect(-70, 50, 70, 78), 14, 14, P(color=col('#ff6b6b')))
    c.restore()
    if t > t0 + 0.8:
        a = prog(t, t0 + 0.8, 0.4)
        c.save(); c.translate(ex + 40, ey - 200)
        c.drawRoundRect(skia.Rect(-120, -45, 120, 45), 45, 45, P(color=col('#ffffff', int(230 * a))))
        text_block(c, 'January', 0, 0, size=50, fill='#2b3a6a', hi='#2b3a6a', stroke='#ffffff', alpha=int(255 * a))
        c.restore()
    if t > t1:
        b = ease_back(prog(t, t1 + 0.5, 0.6))
        if b > 0:
            c.save(); c.translate(740, 1420); c.scale(b, b); tilted_earth(c, 0, 0, 100, t, tilt=TILT, face_on=True); c.restore()
            text_block(c, 'TILT!', 420, 1440, size=72, alpha=int(255 * prog(t, t1 + 0.8, 0.3)))

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    space(c, t, seed=15)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1060 + math.sin(t * 2) * 12); c.scale(s, s); tilted_earth(c, 0, 0, 170, t); c.restore()
    for i, kind in enumerate(['spring', 'summer', 'autumn', 'winter']):
        ang = t * 0.6 + i * math.pi / 2
        c.save(); c.translate(540 + math.cos(ang) * 340, 1060 + math.sin(ang) * 260); season_panel(c, 0, 0, 160, 160, kind, t); c.restore()
    follow_button(c, t, cues[-1]['start'])

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why do we have seasons?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why do we have seasons?', 'Why do we have SEASONS?'),
            ("Let's find out!", "Let's find out!")], tail=1.0),
        dict(name='orbit', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every year, the Earth takes one big trip around the Sun.', 'One big trip around the SUN'),
            ('And the Earth is a little bit tilted, like a spinning top that leans to one side!', 'The Earth is TILTED!')], tail=1.6),
        dict(name='summer', draw=s3, sfx_fn=s34_sfx, lines=[
            ('When our half of the Earth leans toward the Sun, the sunlight shines down more straight.', 'Leaning TOWARD the Sun'),
            ("We get long, warm days. That's summer!", 'Long warm days: SUMMER!')], tail=1.4),
        dict(name='winter', draw=s4, sfx_fn=s34_sfx, lines=[
            ('Half a year later, our half leans away from the Sun.', 'Leaning AWAY from the Sun'),
            ("The sunlight comes in slanted, and the days are short. That's winter!", 'Short cold days: WINTER!')], tail=1.4),
        dict(name='torch', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Shine a flashlight straight down, and you get a small, bright spot.', 'Straight: a BRIGHT spot'),
            ('Shine it slanted, and the light spreads out and gets weaker.', 'Slanted: it SPREADS out')], tail=1.4),
        dict(name='halves', draw=s6, sfx_fn=s6_sfx, lines=[
            ("When it's summer on one half of the Earth, it's winter on the other half!", 'One half SUMMER, one half WINTER'),
            ('So in Australia, Christmas comes in summer!', 'Summer CHRISTMAS in Australia!')], tail=1.6),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? The Earth is closest to the Sun in January!', 'CLOSEST to the Sun in January!'),
            ("So seasons don't come from being near or far. It's all about the tilt!", "It's all about the TILT!")], tail=1.8),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
