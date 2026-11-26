"""Episode 46 (EN, general audience): Why do we need bones?
Facts checked (Cleveland Clinic "Bones"; OpenStax/Univ. of Hawaii "Anatomy & Physiology: The functions of the
skeletal system"; WebMD "Five functions of bones"; NIH/NIAMS bone basics; widely cited red-cell production rate
~2 million per second, e.g. American Society of Hematology / textbooks):
- Adults usually have 206 bones (babies are born with more, which fuse).
- Jobs of the skeleton: support/shape, protection (skull -> brain, rib cage -> heart and lungs), movement (muscles
  attach via tendons and can only pull; bones act as levers at the joints), blood cell production in red marrow,
  mineral storage (about 99 % of the body's calcium is in bones and teeth; released into the blood when needed).
- Red marrow makes roughly 2 million red blood cells every second in an adult.
- Hands have 54 bones (27 each), feet 52 (26 each) -> 106 of 206, i.e. more than half.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def xray_bg(c, t):
    """Dark X-ray light box with a faint grid."""
    sky(c, '#0d1838', '#16295a')
    for i in range(12):
        x = i * 100 + 40
        c.drawLine(x, 0, x, H, P(color=col('#2f9bff', 22), stroke=2))
    for j in range(20):
        y = j * 100 + 20
        c.drawLine(0, y, W, y, P(color=col('#2f9bff', 22), stroke=2))
    # slow scan line
    sy = 600 + ((t * 260) % 1100)
    c.drawRect(skia.Rect(0, sy - 30, W, sy + 30), lin(c, (0, sy - 30, 0, sy + 30), [col('#7fd0ff', 0), col('#7fd0ff', 40), col('#7fd0ff', 0)]))

def counter_box(c, x, y, text, k, w=220, size=70, colr=NAVY):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawRoundRect(skia.Rect(-w, -78, w, 78), 40, 40, P(color=col('#ffffff', 240)))
    c.drawRoundRect(skia.Rect(-w, -78, w, 78), 40, 40, P(color=col(colr), stroke=6))
    text_block(c, text, 0, -4, size=size, fill=colr, hi=colr, stroke='#ffffff', maxw=2000)
    c.restore()

def tent(c, x, y, s, poles=1.0, sag=0.0):
    """Simple dome-ish tent; sag 0..1 collapses it when the poles are gone."""
    c.save(); c.translate(x, y); c.scale(s, s)
    h = lerp(-260, -50, ease_in_out(sag))
    p = skia.Path(); p.moveTo(-220, 0); p.cubicTo(-200, h * 0.9, -60, h, 0, h); p.cubicTo(60, h, 200, h * 0.9, 220, 0); p.close()
    c.drawPath(p, lin(c, (0, h, 0, 0), [col('#ffb84d'), col('#ff8a2b')]))
    c.drawPath(p, P(color=col('#c25a10'), stroke=6))
    door = skia.Path(); door.moveTo(-60, 0); door.cubicTo(-40, h * 0.5, 40, h * 0.5, 60, 0); door.close()
    c.drawPath(door, P(color=col('#c25a10', 200)))
    if poles > 0:
        for sx in (-1, 1):
            pp = skia.Path(); pp.moveTo(sx * 220, 0); pp.cubicTo(sx * 200, h * 0.9, sx * 60, h, 0, h)
            c.drawPath(pp, P(color=col('#ffffff', int(255 * poles)), stroke=10))
    c.restore()

# ---------- 1: Hook (cold open: X-ray already scanning) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    xray_bg(c, t)
    flick = 0.75 + 0.25 * math.sin(t * 9)
    xray_body(c, 540, 1590, 0.82, t, bones=min(1.0, 0.4 + t * 1.2) * flick if t < t1 else 1.0, arm_lift=0.0)
    n = int(206 * ease_out(prog(t, 0.2, 1.2)))
    counter_box(c, 540, 665, f'{n} BONES', ease_back(prog(t, 0.15, 0.4)) * (1 - prog(t, t1 - 0.2, 0.3)), w=250)
    if t > t1:
        for i, (lbl, x, y) in enumerate((('FRAME', 230, 700), ('ARMOR', 850, 760), ('MOTION', 210, 1180), ('BLOOD', 870, 1250), ('STORAGE', 540, 640))):
            label_pill(c, lbl, x if x < 900 else 860, y, size=40, k=ease_back(prog(t, t1 + 0.2 + i * 0.3, 0.35)), fill=NAVY, hi=HOT if i == 3 else SKYB)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.15, 'pop')] + [(t1 + 0.2 + i * 0.3, 'click') for i in range(5)]

# ---------- 2: Frame, like tent poles ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    hills(c, 1500, t=t, trees=False, flowers=False)
    gone = prog(t, t0 + 2.2, 0.4)
    sag = prog(t, t0 + 2.4, 1.0)
    back = prog(t, t0 + 4.6, 0.8)
    tent(c, 330, 1420, 1.1, poles=max(1 - gone, back), sag=sag * (1 - back))
    label_pill(c, 'POLES = frame', 330, 1520, size=40, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    if 2.4 < t - t0 < 4.6:
        label_pill(c, 'no poles?', 330, 1000, size=42, k=ease_back(prog(t, t0 + 2.5, 0.3)), fill=NAVY, hi=HOT)
    # mini skeleton on the right
    xray_body(c, 780, 1490, 0.62, t, skin=0.6, hi={'spine', 'legs'} if t > t0 + 1.0 else ())
    label_pill(c, 'BONES = frame', 780, 820, size=40, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi=SKYB)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.2, 'pop'), (t0 + 2.4, 'boing'), (t0 + 4.6, 'whoosh')]

# ---------- 3: Armor: skull and rib cage ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    xray_bg(c, t)
    hi = set()
    if t > t0 + 0.8: hi.add('skull')
    if t > t1 + 0.4: hi.add('ribs')
    c.save(); c.translate(540, 1000); s = 1.0 + 0.5 * ease_in_out(prog(t, t0, 1.2)); c.scale(s, s); c.translate(-540, -1000)
    xray_body(c, 540, 1900, 1.15, t, bones=0.0)
    # organs behind the bones
    bx, by, bs = 540, 1900, 1.15
    # brain
    c.drawOval(skia.Rect(bx - 60 * bs, by - 950 * bs, bx + 60 * bs, by - 860 * bs), P(color=col('#ffb3c6', 230)))
    for k in range(3):
        c.drawArc(skia.Rect(bx - 45 * bs, by - (940 - k * 22) * bs, bx + 45 * bs, by - (900 - k * 22) * bs), 200, 140, False, P(color=col('#e2728f', 200), stroke=4))
    lungs(c, bx, by - 560 * bs, 0.72 * bs, fill=0.5 + 0.3 * math.sin(t * 2), alpha=230)
    hb = 1 + 0.06 * max(0, math.sin(t * 7))
    c.save(); c.translate(bx + 20 * bs, by - 560 * bs); c.scale(hb, hb)
    hp = skia.Path(); hp.moveTo(0, 50); hp.cubicTo(-70, 0, -60, -60, -20, -55); hp.cubicTo(-5, -53, 0, -40, 0, -35); hp.cubicTo(0, -40, 5, -53, 20, -55); hp.cubicTo(60, -60, 70, 0, 0, 50); hp.close()
    c.drawPath(hp, lin(c, (0, -60, 0, 50), [col('#ff6f7f'), col('#e0304a')]))
    c.restore()
    xray_body(c, 540, 1900, 1.15, t, skin=0.0, hi=hi, hi_col='#ffd23f')
    c.restore()
    label_pill(c, 'SKULL guards the brain', 540, 660, size=42, k=ease_back(prog(t, t0 + 1.0, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=GOLD)
    label_pill(c, 'RIBS cage heart + lungs', 540, 1560, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.8, 'sparkle'), (t0 + 1.0, 'pop'), (t1 + 0.4, 'sparkle'), (t1 + 0.6, 'pop')]

# ---------- 4: Movement: muscles pull, bones are levers ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    xray_bg(c, t)
    lift = 0.5 - 0.5 * math.cos(max(0, t - t0 - 0.8) * 2.2)
    xray_body(c, 400, 1560, 0.9, t, arm_lift=lift, hi={'arms'})
    # muscle on the upper arm (pulls)
    sx0, sy0 = 400 + 132 * 0.9, 1560 - 720 * 0.9
    a1 = math.radians(lerp(82, -55, ease_in_out(lift)))
    mx, my = sx0 + math.cos(a1) * 100 * 0.9, sy0 + math.sin(a1) * 100 * 0.9
    bulge = 1 + 0.35 * lift
    c.save(); c.translate(mx, my); c.rotate(math.degrees(a1)); c.scale(1, bulge)
    c.drawOval(skia.Rect(-80, -22, 80, 22), P(color=col('#ff5c6e', 220)))
    c.drawOval(skia.Rect(-80, -22, 80, 22), P(color=col('#b8183f', 220), stroke=3))
    c.restore()
    label_pill(c, 'muscles PULL', 760, 1260, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    # lever icon
    k = ease_back(prog(t, t0 + 2.4, 0.4))
    if k > 0:
        c.save(); c.translate(760, 1480); c.scale(k, k)
        tilt = -10 + 20 * lift
        tri = skia.Path(); tri.moveTo(0, 0); tri.lineTo(-40, 60); tri.lineTo(40, 60); tri.close()
        c.drawPath(tri, P(color=col('#ffd23f')))
        c.save(); c.rotate(tilt); c.drawRoundRect(skia.Rect(-170, -14, 170, 6), 8, 8, P(color=col(BONE))); c.drawRoundRect(skia.Rect(-170, -14, 170, 6), 8, 8, P(color=col(BONE_EDGE), stroke=4)); c.restore()
        c.restore()
        label_pill(c, 'bones = LEVERS', 760, 1600, size=40, k=k, fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.8, 'whoosh'), (t0 + 1.0, 'pop'), (t0 + 2.4, 'pop')]

# ---------- 5: Blood factory (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    sec = ease_in_out(prog(t, t0 + 0.6, 1.0))
    long_bone(c, 360, 1120, 1.05, rot=-8, section=sec)
    label_pill(c, 'MARROW', 360, 760, size=46, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        rnd = random.Random(3)
        for i in range(26):
            ph = ((t - t1) * 0.45 + i / 26) % 1.0
            sx, sy = 380, 1000 + rnd.uniform(-120, 160)
            x = lerp(sx, 960, ph); y = sy + math.sin(ph * 6 + i) * 60 - ph * 80
            a = int(255 * min(1, ph * 6) * min(1, (1 - ph) * 4))
            c.save(); c.translate(x, y); c.rotate(i * 40 + t * 60)
            c.drawOval(skia.Rect(-26, -18, 26, 18), P(color=col('#e0304a', a)))
            c.drawOval(skia.Rect(-12, -7, 12, 7), P(color=col('#b81f38', a)))
            c.restore()
        n = int(2000000 * ease_out(prog(t, t1 + 0.3, 2.0)))
        counter_box(c, 640, 1500, f'{n:,} / SECOND', ease_back(prog(t, t1 + 0.2, 0.4)), w=330, size=56, colr='#c9283f')

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 1.4, 'pop'), (t1 + 0.2, 'ding')]

# ---------- 6: Calcium bank ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    long_bone(c, 300, 1100, 0.95, rot=0)
    # vault door look: label
    label_pill(c, 'CALCIUM bank', 300, 760, size=44, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi=SKYB)
    # coins flowing in then out
    for i in range(8):
        ph = ((t - t0) * 0.5 + i / 8) % 1.0
        out = (i % 2 == 1) and t > t0 + 2.5
        x = lerp(820, 360, ph) if not out else lerp(360, 820, ph)
        y = 1000 + i * 26 + math.sin(ph * 5) * 30
        a = int(255 * min(1, ph * 5) * min(1, (1 - ph) * 5)) if t > t0 else 0
        c.drawCircle(x, y, 34, P(color=col('#ffd23f', a))); c.drawCircle(x, y, 34, P(color=col('#c98a00', a), stroke=4))
        text_block(c, 'Ca', x, y - 2, size=30, fill='#7a5200', hi='#7a5200', stroke='#ffd23f', alpha=a)
    # blood vessel on the right
    c.drawRoundRect(skia.Rect(780, 760, 900, 1480), 60, 60, lin(c, (780, 0, 900, 0), [col('#c9283f'), col('#ff6f7f'), col('#c9283f')], vertical=False))
    label_pill(c, 'BLOOD', 700, 1560, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    n = int(99 * ease_out(prog(t, t0 + 1.6, 1.4)))
    counter_box(c, 330, 1560, f'{n}%', ease_back(prog(t, t0 + 1.6, 0.4)), w=150, size=64)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 1.0, 'pop'), (t0 + 1.6, 'pop'), (t0 + 2.5, 'whoosh')]

# ---------- 7: Wild part: over half are in hands and feet ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    xray_bg(c, t)
    on = t > t0 + 1.2
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    xray_body(c, 540, 1590, 0.82, t, hi={'hands', 'feet'} if on else (), hi_col=mix_hx('#ffd23f', '#ffffff', 0.3 * pulse))
    label_pill(c, 'HANDS 54', 230, 1060, size=44, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'FEET 52', 800, 1420, size=44, k=ease_back(prog(t, t0 + 1.9, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        counter_box(c, 540, 665, '106 of 206', ease_back(prog(t, t1 + 0.2, 0.4)), w=270, size=64, colr='#c9283f')

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 1.2, 'sparkle'), (t0 + 1.4, 'pop'), (t0 + 1.9, 'pop'), (t1 + 0.2, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, '#2f9bff', '#cfe8ff')
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0:
        for i, lbl in enumerate(('FRAME', 'ARMOR', 'MOTION', 'BLOOD', 'STORAGE')):
            label_pill(c, lbl, 540, 700 + i * 110, size=46, k=ease_back(prog(t, cues[0]['start'] + 0.3 + i * 0.35, 0.35)) * fo, fill=NAVY, hi=HOT if lbl == 'BLOOD' else SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#0b1036', int(160 * kk))))
        sun(c, 540, 1000 + 120 * (1 - kk), 110 * kk, t)
        label_pill(c, 'next: where the SUN goes at night', 540, 1300, size=40, k=kk, fill=NAVY, hi=GOLD)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.3 + i * 0.35, 'click') for i in range(5)] + [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do we need bones?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do we need bones?', 'Why do we need BONES?'),
            ('Your two hundred and six bones have five big jobs.', '206 bones, FIVE jobs')], tail=0.9),
        dict(name='frame', draw=s2, sfx_fn=s2_sfx, lines=[
            ('First, they are your frame. Like the poles in a tent, take them out, and everything sags.', 'Job 1: the FRAME')], tail=1.0),
        dict(name='armor', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Second, armor. Your skull guards your brain,', 'Job 2: ARMOR'),
            ('and your ribs make a cage around your heart and lungs.', 'RIBS cage heart and lungs')], tail=1.0),
        dict(name='levers', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Third, movement. Muscles can only pull, so they tug on bones, like levers.', 'Job 3: muscles PULL on levers')], tail=1.0),
        dict(name='marrow', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('Fourth, the surprise: inside many bones is marrow,', 'Job 4: MARROW'),
            ('a factory making about two million red blood cells every second.', '2 MILLION blood cells a second')], tail=1.2),
        dict(name='calcium', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Fifth, bones are a calcium bank. They hold almost all of it, and lend it to your blood when needed.', 'Job 5: a CALCIUM bank')], tail=1.0),
        dict(name='hands', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: more than half of your bones", 'More than HALF your bones'),
            ('are in your hands and feet. One hundred and six of them.', 'are in your HANDS and feet')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Bones hold you up, protect you, move you, make blood, and store calcium.', 'Frame, armor, motion, BLOOD, storage'),
            ('Next: where the Sun goes at night.', 'Next: where the SUN goes'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
