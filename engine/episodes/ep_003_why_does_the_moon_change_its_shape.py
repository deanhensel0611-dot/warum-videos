"""Episode 3 (EN): Why does the Moon change its shape?"""
import math, random
from lib import *

def night_bg(c, t, seed=21, hills_y=1640):
    sky(c, '#060a24', '#2a2f6b', mid='#121845'); stars(c, t, seed=seed, n=100)
    hills(c, hills_y, c1='#3f6e45', c2='#2e5535', t=t, trees=True, dark=True, flowers=False)

# ---------- 1: Hook – many moon shapes ----------
def s1(c, t, D, cues):
    night_bg(c, t)
    phases = [0.12, 0.25, 0.5, 0.75, 0.88]
    pos = [(200, 820), (540, 760), (880, 820), (330, 1150), (750, 1150)]
    for i, (ph, (x, y)) in enumerate(zip(phases, pos)):
        a = ease_back(prog(t, 0.1 + i * 0.18, 0.5), 2.0)
        if a <= 0: continue
        c.save(); c.translate(x, y + math.sin(t * 2 + i) * 10); c.scale(a, a)
        moon(c, 0, 0, 105 if i != 2 else 135, t, ph, mood='wow' if i == 2 and t < 2.2 else 'happy')
        c.restore()
    for i in range(4):
        a = prog(t, 1.0 + i * 0.15, 0.35)
        if a > 0:
            x, y = [(120, 1000), (960, 1000), (540, 1340), (540, 990)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab', '#ffffff'][i], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
            c.restore()
    dust(c, t, colr='#fff3b0', n=12)

def s1_sfx(D, cues): return [(0.1 + i * 0.18, 'pop') for i in range(5)]

# ---------- 2: No own light – the Sun lights it up ----------
def s2(c, t, D, cues):
    space(c, t, seed=22)
    mx, my, r = 640, 1080, 220
    lit = ease_in_out(prog(t, cues[1]['start'] + 0.4, 1.2))
    sx = lerp(-200, 110, ease_out(prog(t, cues[1]['start'], 0.8)))
    if lit > 0:
        beam = skia.Path(); beam.moveTo(sx, 1020); beam.lineTo(mx, my - r - 40); beam.lineTo(mx, my + r + 40); beam.lineTo(sx, 1140); beam.close()
        c.drawPath(beam, lin(c, (sx, 0, mx, 0), [col('#fff6b0', int(140 * lit)), col('#fff6b0', int(30 * lit))], vertical=False))
    # dark moon that fills with light from the left
    c.drawCircle(mx, my, r, P(color=col('#4a5274')))
    if lit > 0:
        c.save(); clip = skia.Path(); clip.addCircle(mx, my, r); c.clipPath(clip, doAntiAlias=True)
        w = lerp(0, r * 2, lit)
        c.drawRect(skia.Rect(mx - r, my - r, mx - r + w * 0.5, my + r), P(color=col('#fff1b8')))
        c.restore()
    c.drawCircle(mx, my, r, P(color=col('#8a93c0', 160), stroke=6))
    face(c, mx, my + 10, r * 0.85, t, 2.1, 'wow' if lit > 0.5 else 'happy')
    sun(c, sx, 1080, 130, t)

def s2_sfx(D, cues): return [(cues[1]['start'] + 0.05, 'whoosh'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 3: Always one half lit ----------
def s3(c, t, D, cues):
    space(c, t, seed=23)
    sunbeams(c, 40, 1080, t, a=20)
    sun(c, 40, 1080, 120, t)
    mx, my, r = 620, 1080, 250
    s = ease_back(prog(t, 0.1, 0.6), 1.6)
    c.save(); c.translate(mx, my); c.scale(s, s)
    half_lit_ball(c, 0, 0, r, t, sun_dir=180, face_on=True)
    c.restore()
    if t > cues[0]['start'] + 1.0:
        a = int(255 * prog(t, cues[0]['start'] + 1.0, 0.4))
        text_block(c, 'BRIGHT', mx - 125, my + r + 110, size=60, fill='#ffe14d', hi='#ffe14d', alpha=a)
    if t > cues[1]['start']:
        a = int(255 * prog(t, cues[1]['start'], 0.4))
        text_block(c, 'DARK', mx + 125, my + r + 110, size=60, fill='#9aa7ff', hi='#9aa7ff', alpha=a)

def s3_sfx(D, cues): return [(cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'] + 0.05, 'pop')]

# ---------- 4: The Moon travels around the Earth ----------
def s4(c, t, D, cues):
    space(c, t, seed=24)
    sunbeams(c, -60, 1080, t, a=16)
    sun(c, -60, 1080, 150, t)
    ex, ey, R = 560, 1100, 330
    path = skia.Path(); path.addCircle(ex, ey, R)
    c.drawPath(path, P(color=col('#ffffff', 70), stroke=4))
    earth(c, ex, ey, 120, t, rot=t * 0.1, sun_dir=180, night=0.45)
    ang = -math.pi / 2 - (t - 0.3) * 0.55 if t > 0.3 else -math.pi / 2
    mx, my = ex + math.cos(ang) * R, ey + math.sin(ang) * R
    # dotted trail behind the moon
    for k in range(1, 14):
        a2 = ang + k * 0.07
        c.drawCircle(ex + math.cos(a2) * R, ey + math.sin(a2) * R, 7 * (1 - k / 14), P(color=col('#fff1b8', int(200 * (1 - k / 14)))))
    half_lit_ball(c, mx, my, 70, t, sun_dir=180, face_on=True)
    if t > cues[1]['start']:
        a = int(255 * prog(t, cues[1]['start'], 0.4))
        # a little calendar
        c.save(); c.translate(840, 1520)
        c.drawRoundRect(skia.Rect(-80, -70, 80, 70), 16, 16, P(color=col('#ffffff', a)))
        c.drawRoundRect(skia.Rect(-80, -70, 80, -30), 16, 16, P(color=col('#ff6b6b', a)))
        c.drawRect(skia.Rect(-80, -46, 80, -30), P(color=col('#ff6b6b', a)))
        for i in range(4):
            for j in range(3):
                c.drawRect(skia.Rect(-62 + i * 33, -18 + j * 28, -42 + i * 33, -2 + j * 28), P(color=col('#9aa7c8', a)))
        c.restore()

def s4_sfx(D, cues): return [(0.3, 'whoosh'), (cues[1]['start'] + 0.05, 'pop')]

# ---------- 5: We see different amounts of the bright side ----------
def s5(c, t, D, cues):
    night_bg(c, t, seed=25)
    t1 = cues[1]['start']
    # phase sweeps from a thin sliver to full and back, timed to line 2
    if t < t1: ph = 0.08 + 0.04 * ease_in_out(prog(t, 0, t1))
    else: ph = lerp(0.12, 0.92, ease_in_out(prog(t, t1, D - t1 - 0.6)))
    moon(c, 540, 980, 200, t, ph, mood='happy')
    kid(c, 540, 1720, 0.8, t, wave=0.45 < ph < 0.55)
    # little phase strip
    for i, p in enumerate([0.12, 0.25, 0.5, 0.75, 0.88]):
        x = 220 + i * 160
        on = abs(ph - p) < 0.09
        s = 1.25 if on else 1.0
        moon(c, x, 1300, 42 * s, t, p, face_on=False, glow=on, dark_a=110)

def s5_sfx(D, cues): return [(cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 6: It is always round ----------
def s6(c, t, D, cues):
    night_bg(c, t, seed=26)
    mx, my, r = 540, 1040, 230
    reveal = ease_in_out(prog(t, cues[0]['start'] + 1.2, 1.0))
    moon(c, mx, my, r, t, 0.15, mood='wow' if reveal > 0.3 else 'happy', dark_a=int(60 + 120 * reveal))
    if reveal > 0:
        c.drawCircle(mx, my, r + 12 + 6 * math.sin(t * 4), P(color=col('#ffe14d', int(230 * reveal)), stroke=10))
        for j in range(8):
            ang = j * math.pi / 4 + t
            rr = r + 60 + 15 * math.sin(t * 5 + j)
            c.drawCircle(mx + math.cos(ang) * rr, my + math.sin(ang) * rr, 10 * reveal, P(color=col('#ffe14d')))
    if t > cues[1]['start']:
        a = ease_back(prog(t, cues[1]['start'], 0.6))
        c.save(); c.translate(870, 1330); c.scale(a, a); sun(c, 0, 0, 70, t); c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 1.2, 'sparkle')]

# ---------- 7: Bonus – always the same side ----------
def s7(c, t, D, cues):
    space(c, t, seed=27)
    ex, ey, R = 540, 1100, 330
    path = skia.Path(); path.addCircle(ex, ey, R)
    c.drawPath(path, P(color=col('#ffffff', 60), stroke=4))
    earth(c, ex, ey, 130, t, rot=t * 0.1)
    ang = -math.pi / 2 + t * 0.6
    mx, my = ex + math.cos(ang) * R, ey + math.sin(ang) * R
    c.save(); c.translate(mx, my); c.rotate(math.degrees(ang) - 90)
    # moon whose face always points to the Earth
    c.drawCircle(0, 0, 85, rad(-25, -30, 130, [col('#fffdf0'), col('#f2d77a')]))
    for dx, dy, rr in [(-30, 30, 14), (35, 40, 10), (20, -45, 12)]:
        c.drawCircle(dx, dy, rr, P(color=col('#e6c96a')))
    face(c, 0, -20, 60, t, 2.1, 'happy', (0, -1))
    c.restore()
    # dashed "look" line from moon face to Earth
    if t > cues[1]['start']:
        a = int(200 * prog(t, cues[1]['start'], 0.4))
        for k in range(1, 7):
            u = k / 7
            c.drawCircle(lerp(mx, ex, u * 0.6 + 0.1), lerp(my, ey, u * 0.6 + 0.1), 6, P(color=col('#ffe14d', a)))

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night_bg(c, t, seed=28)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1050 + math.sin(t * 2) * 12); c.scale(s, s); moon(c, 0, 0, 200, t, 0.5); c.restore()
    for i, p in enumerate([0.12, 0.25, 0.75, 0.88]):
        ang = t * 0.8 + i * math.pi / 2
        moon(c, 540 + math.cos(ang) * 360, 1050 + math.sin(ang) * 300, 50, t, p, face_on=False, dark_a=100)
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=20, colr='#fff3b0')

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why does the Moon change its shape?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why does the Moon change its shape?', 'Why does the MOON change shape?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='light', draw=s2, sfx_fn=s2_sfx, lines=[
            ("First, the Moon doesn't make its own light.", "The Moon can't SHINE by itself"),
            ('It shines because the Sun lights it up, like a lamp shining on a ball!', 'The SUN lights it up!')], tail=1.2),
        dict(name='half', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The Sun always lights up one half of the Moon.', 'The Sun lights HALF the Moon'),
            ('The other half stays dark.', 'The other half stays DARK')], tail=1.0),
        dict(name='orbit', draw=s4, sfx_fn=s4_sfx, lines=[
            ('And the Moon is always traveling around the Earth, in a big circle.', 'The Moon circles the EARTH'),
            ('It takes about a month to go all the way around.', 'One trip: about a MONTH!')], tail=1.4),
        dict(name='phases', draw=s5, sfx_fn=s5_sfx, lines=[
            ('As it travels, we see different amounts of its bright side.', 'We see MORE or LESS bright side'),
            ('First a thin sliver, then half, then a big round full moon, and then back again!', 'Sliver … half … FULL!')], tail=1.4),
        dict(name='round', draw=s6, sfx_fn=s6_sfx, lines=[
            ('So the Moon never really changes its shape. It is always a round ball!', 'The Moon is ALWAYS round!'),
            ('We just see more or less of the part the Sun is lighting up.', 'We just see the SUNNY part')], tail=1.4),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? We always see the same side of the Moon!', 'We always see the SAME side!'),
            ('The Moon turns just the right way, so the same face always looks at us.', 'The same FACE looks at us!')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
