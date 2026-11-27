"""Episode 51 (EN, general audience): Why does the Moon have craters?
Facts checked (NASA Space Place "Why does the Moon have craters?"; NASA Science "Lunar craters"; The Conversation "Why the
Moon is such a cratered place"; ScienceAlert / NASA GRAIL on the South Pole-Aitken basin):
- Lunar craters are impact craters: asteroids, meteoroids and comets hit the surface at very high speed (typically
  tens of thousands of mph); the energy blasts out a crater roughly 10-20 times wider than the impactor.
- The Moon has almost no atmosphere, so even small rocks reach the ground (on Earth, most small meteoroids burn up).
- With no wind, rain, flowing water or plate tectonics, craters on the Moon stay for billions of years.
- Earth is hit too (even more, being bigger), but erosion, water, vegetation and moving plates erase or bury most
  craters; only ~200 are confirmed.
- Biggest lunar crater: South Pole-Aitken basin on the far side, about 2,500 km (~1,550 miles) across - roughly twice
  the width of Texas (~1,250 km / ~775 miles).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def moonscape(c, t, y=1250, seed=4):
    space(c, t)
    moon_ground(c, y, t, seed=seed)

def incoming(c, t, st, dur, x0, y0, x1, y1, r=26, seed=1):
    """rock flying in from (x0,y0) to (x1,y1) between st and st+dur. returns impact progress (0 before impact)."""
    ph = prog(t, st, dur)
    if 0 < ph < 1:
        x, y = lerp(x0, x1, ph), lerp(y0, y1, ph)
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        c.drawLine(x - (x1 - x0) * 0.15, y - (y1 - y0) * 0.15, x, y, P(color=col('#ffffff', 60), stroke=r * 0.8, blur=6))
        space_rock(c, x, y, r, rot=t * 90, seed=seed)
    return prog(t, st + dur, 0.9)

# ---------- 1: Hook (cold open: rocks already raining onto the Moon) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    space(c, t)
    sh = 1 - ease_in_out(prog(t, t1 - 0.2, 0.8))
    mx = lerp(700, 540, sh); my = lerp(1150, 1080, sh); mr = lerp(260, 380, sh)
    gray_moon(c, mx, my, mr, t, glow=0.3)
    for i, (ang, st) in enumerate(((210, 0.0), (240, 0.6), (195, 1.2), (225, 1.8))):
        ph = prog(t, st, 0.7)
        if 0 < ph < 1:
            rd = math.radians(ang); hx = mx + math.cos(rd) * mr * 0.7; hy = my + math.sin(rd) * mr * 0.7
            sx, sy = hx - 500 * math.cos(math.radians(ang - 150)), hy - 500
            meteor(c, lerp(sx, hx, ph), lerp(sy, hy, ph), math.degrees(math.atan2(hy - sy, hx - sx)), 180 * ph, r=8)
        impact_flash(c, mx + math.cos(math.radians(ang)) * mr * 0.7, my + math.sin(math.radians(ang)) * mr * 0.7, prog(t, st + 0.7, 0.8), r=60)
    label_pill(c, 'COVERED in craters', 540, 690, size=48, k=ease_back(prog(t, 0.4, 0.4)) * sh, fill=NAVY, hi=GOLD)
    if t > t1:
        ek = ease_back(prog(t, t1 + 0.3, 0.5))
        earth(c, 240, 1330, 150 * ek, t, rot=t * 0.1, face_on=False)
        label_pill(c, 'Earth gets hit TOO', 400, 1560, size=46, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.7, 'boing'), (1.3, 'boing'), (0.4, 'pop'), (t1 + 0.3, 'whoosh'), (t1 + 0.9, 'pop')]

# ---------- 2: Every crater = a space rock ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    moonscape(c, t)
    k = incoming(c, t, t0 + 0.1, 1.1, 1000, 640, 520, 1330, r=34, seed=3)
    if k > 0:
        crater(c, 520, 1330, 150 * ease_out(min(1, k * 2)), fresh=1 - k * 0.5)
        impact_flash(c, 520, 1330, k, r=240)
    label_pill(c, 'a SPACE ROCK', 300, 720, size=50, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'every crater = a HIT', 540, 1560, size=46, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 0.3, 'pop'), (t0 + 1.2, 'boing'), (t0 + 2.0, 'pop')]

# ---------- 3: Speed -> crater much bigger than the rock ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    moonscape(c, t, y=1180, seed=7)
    # speed gauge
    gk = ease_back(prog(t, t0 + 0.2, 0.5))
    if gk > 0 and t < t1 + 0.4:
        a = 255 * (1 - prog(t, t1, 0.4))
        gauge(c, 540, 1000, 190 * gk, ease_out(prog(t, t0 + 0.5, 1.6)) * 0.95, alpha=a, label='mph')
        label_pill(c, 'TENS OF THOUSANDS of mph', 540, 700, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        ck = ease_out(prog(t, t1 + 0.2, 0.8))
        crater(c, 560, 1380, 300 * ck, base='#8e8f95')
        rk = ease_back(prog(t, t1 + 0.6, 0.4))
        space_rock(c, 180, 1300, 26 * rk, seed=5)
        if rk > 0.5:
            label_pill(c, 'rock', 180, 1220, size=38, k=rk, fill=NAVY)
        mk = prog(t, t1 + 1.2, 0.6)
        if mk > 0:
            xL, xR = 560 - 340, 560 - 340 + 680 * mk
            c.drawLine(xL, 1600, xR, 1600, P(color=col('#ffffff'), stroke=8))
            c.drawLine(xL, 1575, xL, 1625, P(color=col('#ffffff'), stroke=8))
            if mk >= 1: c.drawLine(xR, 1575, xR, 1625, P(color=col('#ffffff'), stroke=8))
        label_pill(c, '10–20× WIDER', 560, 720, size=52, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.5, 'whoosh'), (t1 + 0.2, 'boing'), (t1 + 0.6, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 4: Earth has an air shield, the Moon doesn't ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    # top half: Earth's sky
    c.save(); c.clipRect(skia.Rect(0, 0, W, 1110))
    sky(c, '#1b2a6a', '#7cc4ff')
    stars(c, t, n=40, y1=700, a=0.6)
    hills(c, y=1020, t=t, trees=True)
    for i in range(3):
        ph = prog(t, t0 + 0.2 + i * 0.6, 1.0)
        if 0 < ph < 1:
            hx = 300 + i * 220 + 260 * ph; hy = 640 + 220 * ph
            meteor(c, hx, hy, 40, 220 * ph, r=7, alpha=255 * (1 - prog(ph, 0.6, 0.4)))
    c.restore()
    label_pill(c, "Earth: AIR burns them up", 540, 1050, size=40, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
    # bottom half: Moon
    c.save(); c.clipRect(skia.Rect(0, 1110, W, H))
    space(c, t); moon_ground(c, 1380, t, seed=9)
    if t > t1:
        for i in range(3):
            k = incoming(c, t, t1 + 0.1 + i * 0.5, 0.5, 980 - i * 60, 1120, 300 + i * 220, 1460, r=12, seed=i + 2)
            if k > 0:
                crater(c, 300 + i * 220, 1460, 46 * ease_out(min(1, k * 2)), fresh=1 - k * 0.5)
                impact_flash(c, 300 + i * 220, 1460, k, r=80)
    c.restore()
    c.drawLine(0, 1110, W, 1110, P(color=col('#ffffff'), stroke=8))
    if t > t1:
        label_pill(c, 'Moon: NO SHIELD', 540, 1580, size=46, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.6, 'boing'), (t1 + 1.1, 'boing'), (t1 + 0.8, 'pop')]

# ---------- 5: Nothing erases them (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    moonscape(c, t, y=1150, seed=12)
    crater(c, 540, 1360, 260, base='#8e8f95')
    # crossed-out eraser icons: wind, rain, plates
    icons = [('WIND', 230), ('RAIN', 540), ('PLATES', 850)]
    for i, (lbl, x) in enumerate(icons):
        k = ease_back(prog(t, t0 + 0.5 + i * 0.35, 0.4))
        if k <= 0: continue
        c.save(); c.translate(x, 760); c.scale(k, k)
        c.drawCircle(0, 0, 90, P(color=col('#ffffff', 235)))
        if lbl == 'WIND':
            for j in range(3): c.drawLine(-50, -30 + j * 30, 40 - j * 15, -30 + j * 30, P(color=col(SKYB), stroke=12))
        elif lbl == 'RAIN':
            for j in range(3): raindrop(c, -40 + j * 40, -5 + (j % 2) * 20, 18, t, face_on=False)
        else:
            c.drawRect(skia.Rect(-60, -20, -6, 30), P(color=col('#a87b52'))); c.drawRect(skia.Rect(6, -30, 60, 20), P(color=col('#a87b52')))
        c.drawCircle(0, 0, 90, P(color=col(HOT), stroke=10))
        c.drawLine(-62, -62, 62, 62, P(color=col(HOT), stroke=12))
        c.restore()
        label_pill(c, lbl, x, 900, size=34, k=k, fill=NAVY)
    if t > t1:
        yrs = int(4_000_000_000 * ease_in_out(prog(t, t1 + 0.2, 2.2)) / 1_000_000) * 1_000_000
        label_pill(c, f'{yrs:,} years', 540, 1580, size=48, k=ease_back(prog(t, t1 + 0.1, 0.4)), fill=NAVY, hi=GOLD)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'ding'), (t0 + 0.5, 'pop'), (t0 + 0.85, 'pop'), (t0 + 1.2, 'pop'), (t1 + 0.1, 'whoosh')]

# ---------- 6: Earth erases its craters ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#7cc4ff', '#cfeaff')
    clouds(c, t, n=3, y0=650, y1=900)
    heal = ease_in_out(prog(t, t0 + 1.0, 3.2))
    hills(c, y=1250, t=t, trees=False)
    # crater on Earth being worn down and grown over
    cr = 230 * (1 - 0.65 * heal)
    if cr > 1:
        crater(c, 540, 1400, cr, base=mix_hx('#a07a52', '#56b83a', heal), squash=0.5 * (1 - 0.6 * heal))
    for i in range(6):
        tk = ease_back(prog(t, t0 + 1.8 + i * 0.25, 0.5))
        if tk > 0: tree(c, 260 + i * 110, 1440 + (i % 2) * 40, 0.55 * tk, t, seed=i)
    if heal > 0.1:
        rain_k = 1 - prog(t, t0 + 3.2, 0.6)
        for i in range(16):
            ph = (t * 1.4 + i / 16) % 1.0
            raindrop(c, 120 + (i * 57) % 840, 700 + ph * 600, 9, t, face_on=False, alpha=int(200 * rain_k))
    label_pill(c, 'Earth ERASES its craters', 540, 1580, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.0, 'whoosh'), (t0 + 1.8, 'sparkle')]

# ---------- 7: Wild part: the biggest crater ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    mr = 380; cy = 1190
    gray_moon(c, 540, cy, mr, t)
    # South Pole-Aitken basin outline (lower part of the disc)
    bk = ease_out(prog(t, t0 + 0.8, 1.0))
    c.save(); cl = skia.Path(); cl.addCircle(540, cy, mr); c.clipPath(cl, doAntiAlias=True)
    rect = skia.Rect(540 - 270, cy + 60, 540 + 270, cy + 420)
    c.drawOval(rect, P(color=col('#3a3b40', int(120 * bk))))
    c.drawArc(rect, 0, 360 * bk, False, P(color=col(GOLD), stroke=10))
    c.restore()
    mk = prog(t, t1 + 0.2, 0.7)
    if mk > 0:
        y = cy + 240; xL = 270; xR = lerp(270, 810, mk)
        c.drawLine(xL, y, xR, y, P(color=col('#ffffff'), stroke=8))
        c.drawLine(xL, y - 22, xL, y + 22, P(color=col('#ffffff'), stroke=8))
        if mk >= 1: c.drawLine(xR, y - 22, xR, y + 22, P(color=col('#ffffff'), stroke=8))
    label_pill(c, '~1,500 MILES wide', 540, 650, size=50, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        label_pill(c, '≈ 2× TEXAS', 540, 755, size=46, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.8, 'whoosh'), (t0 + 1.4, 'pop'), (t1 + 0.2, 'click'), (t1 + 0.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    space(c, t)
    gray_moon(c, 540, 1180, 300, t, glow=0.2)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'no air + no ERASER = craters', 540, 700, size=40, k=k0, fill=NAVY, hi=GOLD)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: how BIRDS fly', 540, 820, size=44, k=kk, fill=NAVY, hi=HOT)
        bird(c, 540 + 30 * math.sin(t), 1000, 0.6 * kk, t)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why does the Moon have craters?',
    music=False, faces=False, ambience='space',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why is the Moon covered in craters?', 'Why so many CRATERS?'),
            ('Earth gets hit too. It just hides the scars.', 'Earth gets hit TOO')], tail=0.9),
        dict(name='rock', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every crater is a scar, left by a space rock slamming into the surface.', 'Each one: a space ROCK')], tail=1.0),
        dict(name='blast', draw=s3, sfx_fn=s3_sfx, lines=[
            ('They hit at tens of thousands of miles per hour.', 'Tens of thousands of MPH'),
            ('The blast digs a hole ten to twenty times wider than the rock.', 'Hole: 10–20× WIDER')], tail=1.0),
        dict(name='air', draw=s4, sfx_fn=s4_sfx, lines=[
            ("On Earth, the air burns up most small rocks before they land.", "Earth's AIR burns them up"),
            ('The Moon has almost no air, so even pebbles hit the ground.', 'Moon: no air, no SHIELD')], tail=1.1),
        dict(name='erase', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('And nothing erases them. No wind, no rain, no moving plates.', 'Nothing ERASES them'),
            ('So craters there can last for billions of years.', 'They last BILLIONS of years')], tail=1.2),
        dict(name='earth', draw=s6, sfx_fn=s6_sfx, lines=[
            ('On Earth, weather, water and moving plates wipe most craters away.', 'Earth ERASES its craters')], tail=1.3),
        dict(name='biggest', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: the Moon's biggest crater is about fifteen hundred miles wide.", '~1,500 MILES wide'),
            ("That's about twice as wide as Texas.", 'About 2× TEXAS')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So the Moon keeps every hit, because nothing wipes it clean.', 'The Moon KEEPS every hit'),
            ('Next: how birds fly.', 'Next: how BIRDS fly'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
