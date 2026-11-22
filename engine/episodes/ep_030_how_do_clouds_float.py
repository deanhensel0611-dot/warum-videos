"""Episode 30 (EN, general audience): How do clouds float?
Facts checked (USGS Water Science School "How much does a cloud weigh?", Scientific American "Why do clouds float
when they have so much water in them?", Live Science "Why do clouds float?", Wikipedia "Cloud physics"):
- Clouds are made of very small water droplets (and/or ice crystals), typically ~0.01-0.02 mm across; a raindrop is
  about 2 mm, i.e. roughly 100 times wider.
- Such small droplets have a tiny fall speed (around 1 cm/s) because air resistance nearly balances their weight.
- Rising air (updrafts / convection from sun-warmed ground) moves upward faster than the droplets fall, so they stay aloft.
- When droplets collide and merge into much bigger drops, they fall faster than the updraft can hold them -> rain.
- An average cumulus cloud holds ~500 metric tons (~1.1 million pounds) of water - USGS compares it to ~100 elephants.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def day_sky(c, t, top='#4fb0ff', bot='#cdeaff'):
    sky(c, top, bot)
    dust(c, t, seed=4, n=10, a=60, colr='#ffffff')

def big_cloud(c, x, y, s, t, gray=0.0):
    cloud_char(c, x + 10 * math.sin(t * 0.6), y + 6 * math.sin(t * 0.9), s, t, gray=gray, face_on=False)

def droplet_field(c, cx, cy, w_, h_, t, n=40, r=10, seed=1, alpha=230, fall=0.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = cx + rnd.uniform(-w_ / 2, w_ / 2) + 6 * math.sin(t * rnd.uniform(1, 2) + i)
        y = cy + rnd.uniform(-h_ / 2, h_ / 2) + 6 * math.cos(t * rnd.uniform(1, 2) + i) + fall
        rr = r * rnd.uniform(0.7, 1.2)
        raindrop(c, x, y, rr, t, shape='round', face_on=False, alpha=alpha)

# ---------- 1: Hook (cold open: cloud already drifting, a drop falls straight out) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    day_sky(c, t)
    clouds(c, t, seed=3, n=3, y0=1250, y1=1500, speed=30, a=170)
    big_cloud(c, 540, 1000, 1.55, t)
    label_pill(c, 'made of WATER', 540, 700, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        u = prog(t, t1 + 0.6, 1.1)
        if 0 < u < 1:
            raindrop(c, 760, lerp(1150, 1700, ease_in_out(u) ** 1.5), 26, t, face_on=False)
        q = ease_back(prog(t, t1 + 1.8, 0.4))
        if q > 0:
            c.save(); c.translate(760, 1400); c.scale(q, q)
            c.drawCircle(0, 0, 70, P(color=col('#ff5c85')))
            text_block(c, '?', 0, 4, size=90, fill='#ffffff', hi='#ffffff', stroke='#b8183f')
            c.restore()

def s1_sfx(D, cues): return [(0.3, 'pop'), (cues[1]['start'] + 0.6, 'whoosh'), (cues[1]['start'] + 1.8, 'boing')]

# ---------- 2: Billions of tiny droplets (zoom lens) ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    day_sky(c, t)
    big_cloud(c, 540, 900, 1.3, t)
    mk = ease_out(prog(t, t0 + 0.3, 0.7))
    if t < t1 + 0.3 and mk > 0:
        def inner(cc):
            cc.drawRect(skia.Rect(0, 0, W, H), P(color=col('#eef7ff')))
            droplet_field(cc, 540, 1150, 560, 560, t, n=46, r=16, seed=2)
        magnifier(c, 540, 1150, 260 * mk, inner, t)
        label_pill(c, 'BILLIONS of droplets', 540, 1500, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.3, 0.5))
        c.drawRoundRect(skia.Rect(60, 640, W - 60, 1560), 48, 48, P(color=col('#eef7ff', int(240 * min(1, prog(t, t1, 0.3))))))
        if k > 0: raindrop(c, 330, 1130, 120 * k, t, face_on=False)
        if k > 0: label_pill(c, 'RAINDROP', 330, 1370, size=40, k=k, fill=NAVY, hi='#2f9bff')
        k2 = ease_back(prog(t, t1 + 0.9, 0.5))
        if k2 > 0:
            raindrop(c, 760, 1110, 7 * k2, t, shape='round', face_on=False)
            c.drawCircle(760, 1110, 60, P(color=col(NAVY, int(200 * k2)), stroke=4))
            label_pill(c, 'cloud drop', 760, 1370, size=40, k=k2, fill=NAVY)
            label_pill(c, '100x SMALLER', 540, 780, size=50, k=ease_back(prog(t, t1 + 1.5, 0.4)), fill=NAVY, hi='#ff5c85')

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.3, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.5, 'click')]

# ---------- 3: They fall incredibly slowly ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fdf6e3', '#f6e6c4')
    # sunbeam from the top-left with drifting dust
    p = skia.Path(); p.moveTo(-100, 560); p.lineTo(260, 560); p.lineTo(1180, 1700); p.lineTo(620, 1700); p.close()
    c.drawPath(p, P(color=col('#ffffff', 90), blur=30))
    # two lanes
    for lx in (300, 780):
        c.drawRoundRect(skia.Rect(lx - 120, 700, lx + 120, 1560), 40, 40, P(color=col('#ffffff', 120)))
        c.drawRoundRect(skia.Rect(lx - 120, 700, lx + 120, 1560), 40, 40, P(color=col(NAVY, 60), stroke=4))
    # raindrop zips down repeatedly
    u = ((t - t0) * 1.4) % 1.0 if t > t0 else 0
    if t > t0:
        trail(c, [(300, lerp(720, 1540, max(0, u - 0.08 * k))) for k in range(6, -1, -1)], '#7fc6ff', 20)
        raindrop(c, 300, lerp(720, 1540, u), 40, t, face_on=False)
    label_pill(c, 'RAIN: fast', 300, 1620, size=40, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi='#2f9bff')
    # cloud droplet barely moves
    dy = 900 + (t - t0) * 6 if t > t0 else 900
    raindrop(c, 780, dy + 8 * math.sin(t * 1.5), 14, t, shape='round', face_on=False)
    c.drawCircle(780, dy + 8 * math.sin(t * 1.5), 46, P(color=col(NAVY, 140), stroke=4))
    label_pill(c, '1 cm per SECOND', 780, 1620, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        dust(c, t, seed=11, n=26, a=200, colr='#d9b56a')

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.4, 'pop'), (t1 + 0.2, 'sparkle')]

# ---------- 4: Warm air rises ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    day_sky(c, t, top='#5bb6ff', bot='#e3f3ff')
    sun(c, 900, 760, 80, t)
    hills(c, y=1500, t=t, trees=True)
    hk = prog(t, t0 + 0.5, 1.2)
    for i, x in enumerate((260, 540, 820)):
        updraft(c, x, 1480, 900, t, alpha=int(220 * hk), seed=i, colr='#ff9f6b')
    label_pill(c, 'WARM air rises', 330, 760, size=44, k=ease_back(prog(t, t0 + 0.9, 0.4)), fill=NAVY, hi='#ff7a3d')
    if t > t1:
        droplet_field(c, 540, 1000, 700, 160, t, n=22, r=12, seed=5, alpha=int(255 * prog(t, t1 + 0.2, 0.4)))
        label_pill(c, 'UPDRAFT', 540, 1600, size=48, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#ff7a3d')

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.5, 'whoosh'), (t0 + 0.9, 'pop'), (t1 + 0.2, 'sparkle'), (t1 + 0.6, 'pop')]

# ---------- 5: Rising air holds them up (aha) ----------
def fan(c, x, y, s, t, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-130, -40, 130, 40), 20, 20, P(color=col('#dfe7f2', a)))
    c.drawRoundRect(skia.Rect(-130, -40, 130, 40), 20, 20, P(color=col(NAVY, a), stroke=6))
    for i in range(-4, 5):
        c.drawLine(i * 26, -24, i * 26, 24, P(color=col('#8796b0', a), stroke=6))
    c.restore()

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    day_sky(c, t)
    # left: ball on an air stream
    fan(c, 290, 1500, 1.0, t)
    updraft(c, 290, 1460, 1000, t, colr='#ffffff', alpha=230, speed=380, spacing=110)
    by = 1050 + 40 * math.sin(t * 2.4)
    ball(c, 290, by, 60, colr='#ff5c85')
    label_pill(c, 'AIR stream', 290, 1620, size=40, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi='#2f9bff')
    # right: droplets held over the same kind of stream
    rk = ease_out(prog(t, t0 + 1.4, 0.6))
    if rk > 0:
        updraft(c, 790, 1460, 1000, t, colr='#ff9f6b', alpha=int(230 * rk), speed=380, spacing=110, seed=2)
        droplet_field(c, 790, 1050, 260, 200, t, n=14, r=14, seed=7, alpha=int(255 * rk))
        label_pill(c, 'DROPLETS', 790, 1620, size=40, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.3, 0.5), 2.2)
        c.save(); c.translate(540, 760); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-280, -66, 280, 66), 33, 33, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-280, -66, 280, 66), 33, 33, P(color=col(NAVY), stroke=6))
        text_block(c, 'HELD UP', 0, 0, size=64, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.6, 'pop'), (t1 + 0.3, 'ding')]

# ---------- 6: Merge -> too heavy -> rain ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    g = ease_in_out(prog(t, t0, 3.0))
    day_sky(c, t, top=mix_hx('#4fb0ff', '#7d8fae', g), bot=mix_hx('#cdeaff', '#c9d2e0', g))
    big_cloud(c, 540, 860, 1.35, t, gray=g * 0.8)
    m = ease_in_out(prog(t, t0 + 0.6, 2.2))
    # several drops converge into one
    for i in range(6):
        ang = i * 1.047 + 0.3
        rr = 230 * (1 - m)
        if m < 0.98:
            raindrop(c, 540 + math.cos(ang) * rr, 1200 + math.sin(ang) * rr * 0.6, 22, t, shape='round', face_on=False)
    if t < t1 + 0.6:
        raindrop(c, 540, 1200, 22 + 30 * m, t, shape='round', face_on=False, alpha=255 * min(1, m * 3))
    label_pill(c, 'drops MERGE', 540, 1480, size=44, k=ease_back(prog(t, t0 + 0.9, 0.4)) * (1 - prog(t, t1 + 0.4, 0.3)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        rnd = random.Random(4)
        for j in range(26):
            x = rnd.uniform(160, 920); sp = rnd.uniform(0.9, 1.3)
            u = ((t - t1) * sp + rnd.random()) % 1.0
            if t - t1 < u / sp * 0.0 + 0.0: continue
            raindrop(c, x, lerp(1040, 1650, u), 18, t, face_on=False, alpha=int(255 * min(1, (t - t1) * 3)))
        label_pill(c, 'too HEAVY: rain', 540, 1580, size=46, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi='#ff5c85')

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'whoosh'), (t0 + 0.9, 'pop'), (t0 + 2.8, 'boing'), (t1 + 0.1, 'whoosh'), (t1 + 0.5, 'pop')]

# ---------- 7: Wild part: 500 tons = ~100 elephants ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    day_sky(c, t, top='#4aa8ff', bot='#d8eeff')
    big_cloud(c, 540, 870, 1.25, t)
    n = int(500 * ease_out(prog(t, t0 + 1.2, 1.8)))
    if t > t0 + 1.0:
        kk = ease_back(prog(t, t0 + 1.0, 0.4))
        c.save(); c.translate(540, 880); c.scale(kk, kk)
        text_block(c, f'{n} TONS', 0, 0, size=90, fill=NAVY, hi='#1b2a4a', stroke='#ffffff')
        c.restore()
    if t > t1:
        shown = int(100 * ease_in_out(prog(t, t1 + 0.4, 2.6)))
        for i in range(shown):
            r_, cc = divmod(i, 10)
            elephant(c, 150 + cc * 86, 1140 + r_ * 40, 0.2, colr='#8f9bb3')
        label_pill(c, '= 100 ELEPHANTS', 540, 1570, size=46, k=ease_back(prog(t, t1 + 2.4, 0.4)), fill=NAVY, hi='#ff5c85')

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 1.0, 'pop'), (t0 + 1.2, 'click'), (t1 + 0.4, 'whoosh'), (t1 + 2.4, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    day_sky(c, t)
    clouds(c, t, seed=8, n=3, y0=1250, y1=1450, speed=26, a=180)
    big_cloud(c, 540, 1020, 1.3, t)
    for i, x in enumerate((360, 540, 720)):
        updraft(c, x, 1500, 1260, t, colr='#ff9f6b', alpha=150, seed=i)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        soap_bubble(c, 780, 720, 60, t)
        label_pill(c, 'next: BUBBLES', 470, 720, size=48, k=kk, fill=NAVY, hi='#ff5c85')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do clouds float?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do clouds float?', 'How do CLOUDS float?'),
            ("They're made of water, and water normally falls right out of the sky.", "They're made of WATER")], tail=0.8),
        dict(name='droplets', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Zoom in, and a cloud is billions of tiny water droplets.', 'BILLIONS of tiny droplets'),
            ('Each one is about a hundred times smaller than a raindrop.', '100x SMALLER than a raindrop')], tail=0.9),
        dict(name='slow', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Drops that small fall incredibly slowly, about one centimeter per second,', 'They fall SUPER slowly'),
            ('like dust drifting in a sunbeam.', 'Like DUST in a sunbeam')], tail=0.8),
        dict(name='updraft', draw=s4, sfx_fn=s4_sfx, ambience='wind', lines=[
            ('Meanwhile, the sun warms the ground, and warm air rises.', 'WARM air rises'),
            ('That rising air, an updraft, moves up faster than the droplets fall.', 'Rising air beats the FALL')], tail=0.8),
        dict(name='held', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Think of a ball floating on a stream of air.', 'Like a BALL on an air stream'),
            ('The rising air holds the droplets up, so the whole cloud hangs there.', 'Rising air HOLDS them up')], tail=1.2),
        dict(name='rain', draw=s6, sfx_fn=s6_sfx, lines=[
            ('But when droplets bump together and merge into bigger drops,', 'Droplets MERGE'),
            ("they get too heavy for the air to hold, and fall as rain.", 'Too HEAVY: rain')], tail=0.8),
        dict(name='weight', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: one fluffy cloud can hold around five hundred tons of water.", '500 TONS of water'),
            ('That is about as heavy as a hundred elephants, floating over your head.', 'As heavy as 100 ELEPHANTS')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So clouds float because their droplets are tiny, and rising air keeps them up.', 'Tiny drops + RISING air'),
            ('Next up: why bubbles are round.', 'Next: why BUBBLES are round'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
