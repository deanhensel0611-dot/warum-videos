"""Episode 2 (EN): Why do we have day and night?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')

# ---------- 1: Hook – half day, half night ----------
def s1(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    clouds(c, t, seed=2, n=3, y0=700, y1=1100)
    # night half (right), with a gently wobbling border
    k = ease_out(prog(t, 0.1, 0.9))
    bx = lerp(W + 60, 540, k)
    pth = skia.Path(); pth.moveTo(bx, 0)
    for i in range(21):
        yy = i * H / 20; pth.lineTo(bx + math.sin(yy * 0.006 + t * 2) * 30, yy)
    pth.lineTo(W, H); pth.lineTo(W, 0); pth.close()
    c.save(); c.clipPath(pth, doAntiAlias=True)
    sky(c, '#060a24', '#2a2f6b', mid='#121845'); stars(c, t, seed=4, n=70)
    c.restore()
    hills(c, 1640, t=t, trees=False)
    c.save(); c.clipPath(pth, doAntiAlias=True)
    c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#0a1238', 150)))
    c.restore()
    s = ease_back(prog(t, 0.2, 0.7), 1.8)
    c.save(); c.translate(280, 1050 + math.sin(t * 2) * 10); c.scale(s, s); sun(c, 0, 0, 150, t, mood='wow' if t < 2 else 'happy'); c.restore()
    m = ease_back(prog(t, 0.5, 0.7), 1.8)
    c.save(); c.translate(800, 1000 + math.sin(t * 2 + 1) * 10); c.scale(m, m); moon(c, 0, 0, 120, t, 0.5, mood='wow' if t < 2 else 'happy'); c.restore()
    for i in range(5):
        a = prog(t, 0.9 + i * 0.12, 0.35)
        if a > 0:
            ang = i / 5 * 2 * math.pi + t * 0.4
            x = 540 + math.cos(ang) * 380; y = 1100 + math.sin(ang) * 300
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=100 + (i % 3) * 16, fill=['#ffffff', '#ffe14d', '#ff8fab'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
            c.restore()
    dust(c, t)

def s1_sfx(D, cues): return [(0.15, 'whoosh')]

# ---------- 2: Earth is a spinning ball ----------
def s2(c, t, D, cues):
    space(c, t, seed=5)
    s = ease_back(prog(t, 0.1, 0.8), 1.6)
    spin = t * 0.08 + ease_in_out(prog(t, cues[1]['start'], 2.5)) * 0.5
    c.save(); c.translate(540, 1100); c.scale(s, s)
    earth(c, 0, 0, 290, t, rot=spin, mood='wow' if t > cues[1]['start'] and t < cues[1]['start'] + 1.5 else 'happy')
    c.restore()
    if t > cues[1]['start']:
        a = int(255 * prog(t, cues[1]['start'], 0.4))
        c.save(); c.translate(540, 1100); c.scale(1, 0.32)
        off = (t * 120) % 360
        curved_arrow(c, 0, 0, 400, 20 + off * 0, 160, colr='#ffe14d', w=16, alpha=a)
        c.restore()
        # little sparkle trail around the equator
        for j in range(6):
            ang = t * 2.2 + j * math.pi / 3
            if math.sin(ang) > 0:
                x = 540 + math.cos(ang) * 400; y = 1100 + math.sin(ang) * 128
                c.drawCircle(x, y, 9, P(color=col('#fff3b0', a)))

def s2_sfx(D, cues): return [(0.15, 'pop'), (cues[1]['start'] + 0.1, 'whoosh')]

# ---------- 3: The Sun lights one side – like a flashlight ----------
def s3(c, t, D, cues):
    space(c, t, seed=6, n=90)
    sx, sy = 120, 1000; ex, ey = 700, 1080
    g = ease_out(prog(t, cues[0]['start'] + 0.3, 1.0))
    if g > 0:
        beam = skia.Path(); beam.moveTo(sx, sy - 60); beam.lineTo(ex, ey - 300); beam.lineTo(ex, ey + 300); beam.lineTo(sx, sy + 60); beam.close()
        c.drawPath(beam, lin(c, (sx, 0, ex, 0), [col('#fff6b0', int(150 * g)), col('#fff6b0', int(40 * g))], vertical=False))
        for i in range(6):
            u = (t * 0.6 + i / 6) % 1.0
            yy = lerp(sy, ey + (i - 2.5) * 90, u)
            c.drawCircle(lerp(sx + 80, ex - 240, u), yy, 7, P(color=col('#ffffff', int(200 * g))))
    sun(c, sx, sy, 140, t)
    night = 0.0 + 0.7 * ease_in_out(prog(t, cues[0]['start'] + 0.6, 1.0))
    earth(c, ex, ey, 230, t, rot=t * 0.05, sun_dir=180, night=night)
    if t > cues[1]['start']:
        a = ease_back(prog(t, cues[1]['start'], 0.5))
        c.save(); c.translate(780, 1430); c.scale(a, a); c.rotate(-20)
        # cute flashlight
        c.drawRoundRect(skia.Rect(-90, -26, 40, 26), 12, 12, P(color=col('#ff6b6b')))
        hd = skia.Path(); hd.moveTo(40, -26); hd.lineTo(90, -46); hd.lineTo(90, 46); hd.lineTo(40, 26); hd.close()
        c.drawPath(hd, P(color=col('#ffd23f')))
        c.drawRect(skia.Rect(86, -46, 96, 46), P(color=col('#fff6b0')))
        c.drawRect(skia.Rect(-50, -30, -36, 30), P(color=col('#c94a4a')))
        c.restore()
    if t > cues[0]['start'] + 1.2:
        a = int(255 * prog(t, cues[0]['start'] + 1.2, 0.4))
        text_block(c, 'DAY', 600, 740, size=70, fill='#ffe14d', hi='#ffe14d', alpha=a)
        text_block(c, 'NIGHT', 860, 740, size=70, fill='#bcc8ff', hi='#bcc8ff', alpha=a)

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.05, 'pop')]

# ---------- 4: Your home rides along ----------
def s4(c, t, D, cues):
    space(c, t, seed=7, n=90)
    sx, sy = 70, 1000; ex, ey = 600, 1060; r = 240
    sunbeams(c, sx, sy, t, a=18)
    sun(c, sx, sy, 95, t)
    # Earth turns counter-clockwise (seen from above the North Pole): house goes night -> day (line 2) -> night (line 3)
    t1, t2 = cues[1]['start'], cues[2]['start']
    if t < t1 + 0.6: ang = lerp(300, 185, ease_in_out(prog(t, 0, t1 + 0.6)))
    elif t < t2 - 0.2: ang = lerp(185, 170, prog(t, t1 + 0.6, t2 - 0.8 - t1))
    elif t < t2 + 1.8: ang = lerp(170, 10, ease_in_out(prog(t, t2 - 0.2, 2.0)))
    else: ang = lerp(10, -10, prog(t, t2 + 1.8, D - t2 - 1.8))
    rot = (ang - 300) / 360
    earth_top(c, ex, ey, r, t, rot=rot, sun_dir=180)
    hx, hy = ex + math.cos(math.radians(ang)) * r, ey + math.sin(math.radians(ang)) * r
    lit = math.cos(math.radians(ang)) < 0
    pop = ease_back(prog(t, cues[0]['start'], 0.5), 2)
    if pop > 0:
        house(c, hx, hy, 0.85 * pop, ang + 90, lit=lit)
        if not lit: zzz(c, hx + 60, hy - 40, t, size=46)
        # pointer bubble
        bx, by = ex - 40, ey + r + 150
        lab = 'DAY' if lit else 'NIGHT'
        if t > t1 - 0.1:
            text_block(c, lab, bx, by, size=96, fill='#ffe14d' if lit else '#bcc8ff', hi='#ffe14d' if lit else '#bcc8ff')

def s4_sfx(D, cues): return [(cues[1]['start'] + 0.05, 'sparkle'), (cues[2]['start'] + 0.05, 'boing')]

# ---------- 5: One spin = one day; the Sun seems to move ----------
def s5(c, t, D, cues):
    u = prog(t, 0.3, D - 0.6)
    ang = lerp(math.pi * 1.05, math.pi * 2.05, u)  # left horizon -> top -> right horizon -> below
    sxp, syp = 540 + math.cos(ang) * 470, 1550 + math.sin(ang) * 820
    dayk = clamp(-math.sin(ang) * 2.0)
    top = mix_hex('#0a1238', DAY[0], dayk); bot = mix_hex('#2a2f6b', DAY[1], dayk)
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, H), [top, bot]))
    stars(c, t, seed=8, n=80, a=1 - dayk)
    if dayk > 0.05: clouds(c, t, seed=9, n=3, y0=700, y1=1100, a=int(230 * dayk))
    # dotted path of the sun across the sky
    for i in range(30):
        a_ = lerp(math.pi * 1.05, math.pi * 1.95, i / 29)
        c.drawCircle(540 + math.cos(a_) * 470, 1550 + math.sin(a_) * 820, 6, P(color=col('#ffffff', 90)))
    if syp < 1600: sun(c, sxp, syp, 95, t)
    hills(c, 1620, t=t, trees=True, dark=dayk < 0.5)
    kid(c, 540, 1700, 0.85, t, wave=t > cues[1]['start'])

def s5_sfx(D, cues): return [(cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 6: Bonus – the other side is asleep ----------
def s6(c, t, D, cues):
    space(c, t, seed=10)
    ex, ey, r = 540, 1110, 230
    sunbeams(c, 540, 600, t, a=14)
    s = ease_back(prog(t, 0.0, 0.6), 1.6)
    c.save(); c.translate(540, 660); c.scale(s, s); sun(c, 0, 0, 90, t); c.restore()
    earth_top(c, ex, ey, r, t, rot=t * 0.01, sun_dir=-90)
    house(c, ex, ey - r, 0.9, 0, lit=True)
    kid(c, ex + 120, ey - r - 10, 0.42, t, wave=True)
    a = ease_back(prog(t, cues[0]['start'] + 0.8, 0.6), 1.8)
    if a > 0:
        house(c, ex, ey + r, 0.9 * a, 180, lit=False)
        zzz(c, ex + 90, ey + r + 150, t, size=50)
        c.save(); c.translate(260, 1450); c.scale(a, a); moon(c, 0, 0, 70, t, 0.5); c.restore()
    if t > cues[1]['start']:
        for j in range(5):
            ang = t * 1.4 + j * 2 * math.pi / 5
            px, py = ex + 120 + math.cos(ang) * 110, ey - r - 160 + math.sin(ang) * 40
            c.drawCircle(px, py, 9, P(color=col('#ffe14d')))

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'pop'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    space(c, t, seed=11)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1080 + math.sin(t * 2) * 12); c.scale(s, s)
    earth(c, 0, 0, 220, t, rot=t * 0.15); c.restore()
    for i in range(2):
        ang = t * 0.8 + i * math.pi
        x = 540 + math.cos(ang) * 380; y = 1080 + math.sin(ang) * 260
        if i == 0: sun(c, x, y, 75, t)
        else: moon(c, x, y, 60, t, 0.5)
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=20, colr='#fff3b0')

def s7_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why do we have day and night?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why do we have day and night?', 'Why DAY and NIGHT?'),
            ("Let's find out!", "Let's find out!")], tail=0.7),
        dict(name='spin', draw=s2, sfx_fn=s2_sfx, lines=[
            ('We all live on a giant ball called Earth.', 'We live on a giant ball: EARTH!'),
            ('And Earth is always spinning, round and round, like a spinning top!', 'Earth SPINS – like a top!'),
            ("It spins so smoothly that we don't even feel it!", "We don't even FEEL it!")], tail=1.2),
        dict(name='flashlight', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The Sun shines on Earth, but it can only light up one side at a time.', 'The Sun lights ONE side'),
            ('Just like a flashlight shining on a ball!', 'Like a FLASHLIGHT on a ball!')], tail=1.2),
        dict(name='home', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Your home is riding along on the spinning Earth.', 'Your HOME rides along!'),
            ("When your side faces the Sun, it's daytime!", 'Facing the Sun: DAY!'),
            ("And when your side turns away from the Sun, it's nighttime!", 'Turned away: NIGHT!')], tail=1.6),
        dict(name='oneday', draw=s5, sfx_fn=s5_sfx, lines=[
            ('One full spin takes one whole day and night.', 'One spin = ONE day!'),
            ("That's why the Sun seems to move across the sky.", 'The Sun SEEMS to move …'),
            ('But really, it is Earth that is turning!', '… but EARTH is turning!')], tail=1.6),
        dict(name='bonus', draw=s6, sfx_fn=s6_sfx, lines=[
            ("And guess what? Right now, it's nighttime for kids on the other side of the world!", 'Other side of the world: NIGHT!'),
            ("While you're playing, they're fast asleep!", "While you play, they SLEEP!")], tail=1.6),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
