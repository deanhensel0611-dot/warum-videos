"""Episode 34 (EN, general audience): Why can we sometimes see the Moon during the day?
Facts checked (NASA "We asked a NASA scientist: why can you see the Moon during the day?", NASA Science "Moonlight",
Space.com "Why do we see the Moon in daylight?", EarthSky "When can you see a daytime moon?", Live Science
"Daytime moon", Universe Today "Moon albedo", West Texas A&M "Why is the Moon so bright?"):
- The Moon makes no light of its own; it reflects sunlight.
- It orbits Earth about once a month, so it rises on average ~50 minutes later each day; it is above the horizon
  about 12 h a day, and for a large part of the month part of that time is daylight -> visible by day on most days.
- The daytime sky is bright blue because air molecules scatter sunlight (Rayleigh scattering). Stars are too faint
  to be seen against it; the Moon is bright enough to show through.
- Near new Moon it is close to the Sun in the sky (lost in the glare); a full Moon is opposite the Sun and rises
  around sunset. Easiest in daylight: around the quarter phases - afternoon in the days before full Moon (waxing),
  morning in the days after full Moon (waning).
- The Moon's albedo is only ~0.12 (reflects ~12 % of sunlight), comparable to worn asphalt (NASA / Universe Today).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'

def day_bg(c, t, hills_y=1640):
    sky(c, '#5fb4ff', '#d8eeff', mid='#9fd2ff')
    clouds(c, t, seed=3, n=3, y0=700, y1=1300, speed=18, a=220)

def ray(c, x0, y0, x1, y1, k, colr='#ffd23f', w=10, alpha=255):
    if k <= 0: return
    arrow(c, x0, y0, lerp(x0, x1, k), lerp(y0, y1, k), colr=colr, w=w, alpha=alpha)

# ---------- 1: Hook (cold open: Moon already hanging in blue sky) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    day_bg(c, t)
    mx, my = 640 - t * 6, 940 - t * 4
    day_moon(c, mx, my, 150, phase=0.3, alpha=225)
    birds(c, t, seed=2, n=3, y=1150)
    hills(c, y=1660, t=t, trees=True, flowers=True)
    label_pill(c, '3 PM - broad DAYLIGHT', 540, 690, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'up by day most DAYS', 540, 1500, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi='#ff5c85')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 1.6, 'pop')]

# ---------- 2: Moon reflects sunlight like a bike reflector ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    sun(c, 130, 1080, 150, t, glow=True)
    mx, my = 760, 1080
    half_lit_ball(c, mx, my, 160, t, sun_dir=180, base='#e9edf5', dark='#2a3050')
    for i, dy in enumerate((-110, -40, 30, 100)):
        k = ease_out(prog(t, t0 + 0.4 + i * 0.12, 0.8))
        ray(c, 300, my + dy * 1.4, mx - 170, my + dy, k, w=9)
    if t > t1:
        ek = ease_back(prog(t, t1 + 0.2, 0.5))
        if ek > 0:
            earth(c, 330, 1450, 90 * ek, t, rot=t * 0.05, face_on=False)
        for i, (ox, oy) in enumerate(((-130, 60), (-110, 110), (-80, 140))):
            k = ease_out(prog(t, t1 + 0.6 + i * 0.12, 0.7))
            ray(c, mx + ox, my + oy, 420 - i * 20, 1380 + i * 25, k, colr='#ffffff', w=8, alpha=230)
    label_pill(c, 'no LIGHT of its own', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.9, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        label_pill(c, 'it REFLECTS sunlight', 700, 1580, size=42, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi='#e0a800')

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'whoosh'), (t0 + 0.9, 'pop'), (t1 + 0.5, 'pop'), (t1 + 1.6, 'click')]

# ---------- 3: Orbit -> rises ~50 min later each day ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    ex, ey, R = 600, 1110, 330
    # sunlight from the left
    for i in range(5):
        yy = 820 + i * 140
        c.drawLine(40, yy, 160, yy, P(color=col('#ffd23f', 150), stroke=8))
    sun(c, -40, 1110, 120, t, glow=True)
    c.drawCircle(ex, ey, R, P(color=col('#ffffff', 70), stroke=4))
    ang = math.radians(-90 + (t - t0) * 32)
    mx, my = ex + R * math.cos(ang), ey + R * math.sin(ang)
    curved_arrow(c, ex, ey, R + 50, math.degrees(ang) - 70, math.degrees(ang) - 15, colr='#ffffff', w=10,
                 alpha=int(220 * prog(t, t0 + 0.3, 0.5)))
    earth_top(c, ex, ey, 120, t, rot=t * 0.25, sun_dir=180)
    half_lit_ball(c, mx, my, 48, t, sun_dir=180, base='#e9edf5', dark='#2a3050')
    label_pill(c, 'once a MONTH', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.4, 0.5))
        if kk > 0:
            stopwatch(c, 150, 1500, 70 * kk, 50 / 60, label=None)
        label_pill(c, 'rises ~50 MIN later daily', 600, 1580, size=40, k=ease_back(prog(t, t1 + 0.7, 0.4)), fill=NAVY, hi='#ff5c85')

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.4, 'click'), (t1 + 0.7, 'pop')]

# ---------- 4: Blue veil hides stars, Moon shines through (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_sky(c, t, n=110, y1=1600)
    vk = ease_in_out(prog(t, t0 + 0.6, 2.2))
    # blue veil of scattered light
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, W, H), [col('#5fb4ff', int(255 * vk)), col('#9fd2ff', int(255 * vk)), col('#d8eeff', int(255 * vk))]))
    # air molecules scattering blue
    rnd = random.Random(4)
    for i in range(16):
        px, py = rnd.uniform(80, 900), rnd.uniform(700, 1550)
        px += math.sin(t * 1.5 + i) * 10; py += math.cos(t * 1.3 + i) * 10
        a = int(230 * vk)
        c.drawCircle(px, py, 13, P(color=col('#ffffff', a)))
        if (int(t * 3) + i) % 4 == 0:
            for k in range(4):
                an = k * math.pi / 2 + 0.6
                c.drawLine(px + math.cos(an) * 20, py + math.sin(an) * 20, px + math.cos(an) * 44, py + math.sin(an) * 44,
                           P(color=col('#2f9bff', int(a * 0.8)), stroke=5))
    day_moon(c, 700, 1060, 150, phase=0.3, alpha=int(lerp(255, 225, vk)))
    label_pill(c, 'a bright blue VEIL', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'stars: too FAINT', 300, 1400, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#9b4dff')
        kk = prog(t, t1 + 1.8, 0.6)
        if kk > 0:
            c.drawCircle(700, 1060, 210, P(color=col('#ffd23f', int(200 * kk)), stroke=10))
        label_pill(c, 'Moon: BRIGHT enough', 640, 1560, size=42, k=ease_back(prog(t, t1 + 1.8, 0.4)), fill=NAVY, hi='#e0a800')

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.6, 'pop'), (t1 + 1.8, 'ding')]

# ---------- 5: New Moon lost in glare, full Moon opposite the Sun ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    ex, ey = 620, 1110
    for i in range(5):
        yy = 820 + i * 140
        c.drawLine(40, yy, 160, yy, P(color=col('#ffd23f', 150), stroke=8))
    sun(c, -40, 1110, 120, t, glow=True)
    earth_top(c, ex, ey, 110, t, rot=t * 0.25, sun_dir=180)
    # new moon: between earth and sun
    k0 = ease_back(prog(t, t0 + 0.4, 0.5))
    if k0 > 0:
        nx = 340
        c.drawCircle(nx, ey, 150 * k0, rad(nx, ey, 150 * k0, [col('#fff6b0', 170), col('#fff6b0', 0)]))
        half_lit_ball(c, nx, ey, 44 * k0, t, sun_dir=180, base='#e9edf5', dark='#2a3050')
        label_pill(c, 'NEW: lost in glare', 360, 900, size=38, k=k0, fill=NAVY, hi='#e0a800')
    if t > t1:
        k1 = ease_back(prog(t, t1 + 0.3, 0.5))
        fx = 880
        half_lit_ball(c, fx, ey, 44 * k1, t, sun_dir=180, base='#e9edf5', dark='#2a3050')
        label_pill(c, 'FULL: rises at sunset', 640, 1330, size=38, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#9b4dff')

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t1 + 0.3, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 6: Best time: afternoon before full, morning after ----------
def sky_panel(c, x0, y0, x1, y1, t, sun_x, moon_x, phase, title, hi, k):
    if k <= 0: return
    c.save(); c.translate((x0 + x1) / 2, (y0 + y1) / 2); c.scale(k, k); c.translate(-(x0 + x1) / 2, -(y0 + y1) / 2)
    cl = skia.Path(); cl.addRoundRect(skia.Rect(x0, y0, x1, y1), 36, 36)
    c.save(); c.clipPath(cl, doAntiAlias=True)
    c.drawRect(skia.Rect(x0, y0, x1, y1), lin(c, (0, y0, 0, y1), [col('#5fb4ff'), col('#bfe3ff'), col('#ffe2b8')]))
    hy = y1 - 150
    sun(c, sun_x, hy - 30 + 10 * math.sin(t * 0.6), 52, t, glow=True)
    day_moon(c, moon_x, y0 + 230 + 8 * math.sin(t * 0.5), 66, phase=phase, alpha=235)
    p = skia.Path(); p.moveTo(x0, hy); p.cubicTo(x0 + 120, hy - 40, x1 - 140, hy + 20, x1, hy - 20); p.lineTo(x1, y1); p.lineTo(x0, y1); p.close()
    c.drawPath(p, lin(c, (0, hy - 40, 0, y1), [col('#7ed957'), col('#56b83a')]))
    c.restore()
    c.drawRoundRect(skia.Rect(x0, y0, x1, y1), 36, 36, P(color=col('#ffffff'), stroke=8))
    label_pill(c, title, (x0 + x1) / 2, y1 - 70, size=36, fill=NAVY, hi=hi)
    c.restore()

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fff4e6', '#ffe3c4'); dust(c, t, seed=8, n=10, a=70)
    kk = ease_back(prog(t, t0 + 0.3, 0.5))
    if kk > 0:
        c.save(); c.translate(540, 820); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-60, -60, 60, 60), 60, 60, P(color=col('#2a3050')))
        day_moon(c, 0, 0, 52, phase=0.25, alpha=255)
        c.drawCircle(0, 0, 52, P(color=col(NAVY), stroke=5))
        c.drawCircle(0, 0, 60, P(color=col(NAVY, 120), stroke=3))
        c.restore()
    label_pill(c, 'HALF Moon = easiest', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        # afternoon: sun low in the west (right), moon lit on the right
        sky_panel(c, 70, 930, 490, 1580, t, 400, 180, 0.27, 'AFTERNOON', '#e0a800', ease_back(prog(t, t1 + 0.2, 0.5)))
        # morning: sun low in the east (left), moon lit on the left
        sky_panel(c, 520, 930, 930, 1580, t, 610, 820, 0.73, 'MORNING', SKYB, ease_back(prog(t, t1 + 2.2, 0.5)))

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 0.6, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 2.2, 'whoosh')]

# ---------- 7: Wild part: the Moon is as dark as worn asphalt ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    gray_moon(c, 540, 1020, 260, t, glow=0.6)
    n = int(round(12 * ease_out(prog(t, t0 + 1.2, 1.6))))
    kk = ease_back(prog(t, t0 + 1.2, 0.4))
    if kk > 0:
        c.save(); c.translate(540, 1020); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-150, -70, 150, 70), 35, 35, P(color=col('#ffffff', 240)))
        text_block(c, f'{n}%', 0, -4, size=90, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'reflected SUNLIGHT', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi='#e0a800')
    if t > t1:
        ak = ease_out(prog(t, t1 + 0.3, 0.6))
        y0 = 1360
        c.save(); c.translate(0, 120 * (1 - ak))
        c.drawRoundRect(skia.Rect(90, y0, 990, y0 + 170), 30, 30, lin(c, (0, y0, 0, y0 + 170), [col('#5a5b60'), col('#3f4045')]))
        rnd = random.Random(3)
        for i in range(70):
            c.drawCircle(rnd.uniform(110, 970), rnd.uniform(y0 + 15, y0 + 155), rnd.uniform(2, 5), P(color=col(rnd.choice(['#77787d', '#2f3034', '#8a8b90']))))
        for i in range(4):
            c.drawRoundRect(skia.Rect(150 + i * 220, y0 + 76, 260 + i * 220, y0 + 94), 9, 9, P(color=col('#ffffff', 200)))
        c.restore()
        label_pill(c, 'like worn ASPHALT', 540, 1600 - 20, size=42, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi='#ff5c85')

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.2, 'click'), (t1 + 0.3, 'whoosh'), (t1 + 0.8, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    day_bg(c, t)
    day_moon(c, 540, 1000, 170, phase=0.3, alpha=230)
    hills(c, y=1700, t=t, trees=True, flowers=False)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: PENGUINS vs. cold', 540, 700, size=46, k=kk, fill=NAVY, hi=SKYB)
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why can we see the Moon during the day?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why can we see the Moon during the day?', 'Why is the MOON out by day?'),
            ("Isn't it a night thing? Actually, it's up in daylight on most days of the month.", "It's up in DAYLIGHT most days")], tail=0.8),
        dict(name='reflect', draw=s2, sfx_fn=s2_sfx, ambience='space', lines=[
            ('First, the Moon makes no light of its own.', 'It makes no LIGHT of its own'),
            ('It shines because sunlight bounces off it, like a bike reflector.', 'Sunlight BOUNCES off it')], tail=0.8),
        dict(name='orbit', draw=s3, sfx_fn=s3_sfx, ambience='space', lines=[
            ('The Moon circles Earth about once a month,', 'It circles Earth MONTHLY'),
            ('so it rises about fifty minutes later each day, often in daylight.', 'It rises 50 MINUTES later daily')], tail=0.8),
        dict(name='veil', draw=s4, sfx_fn=s4_sfx, lines=[
            ('By day, air scatters sunlight, so the sky glows blue like a bright veil.', 'The sky glows like a VEIL'),
            ('Faint stars get lost behind it, but the Moon is bright enough to shine through.', 'The Moon is BRIGHT enough')], tail=1.2),
        dict(name='glare', draw=s5, sfx_fn=s5_sfx, ambience='space', lines=[
            ("Near new Moon, it hides in the Sun's glare.", 'New Moon: lost in the GLARE'),
            ('A full Moon is opposite the Sun, so it rises at sunset.', 'Full Moon rises at SUNSET')], tail=0.8),
        dict(name='best', draw=s6, sfx_fn=s6_sfx, lines=[
            ('The easiest daytime Moon is around a half Moon.', 'Easiest: a HALF Moon'),
            ('Before full Moon, look in the afternoon. After full Moon, look in the morning.', 'AFTERNOON or MORNING')], tail=1.0),
        dict(name='asphalt', draw=s7, sfx_fn=s7_sfx, ambience='space', lines=[
            ("Here's the wild part: the Moon reflects only about twelve percent of sunlight.", 'Only 12 PERCENT reflected'),
            ('Its surface is as dark as worn asphalt.', 'As dark as ASPHALT')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So the daytime Moon is just bright enough to beat the blue sky.', 'Bright enough to beat the SKY'),
            ("Next: why penguins don't freeze.", "Next: why PENGUINS don't freeze"),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
