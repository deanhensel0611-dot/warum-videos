"""Episode 22 (EN, general audience): Why do we get goosebumps?
Facts checked: goosebumps = piloerection. Each hair follicle has a tiny smooth muscle (arrector pili). The sympathetic
nervous system makes it contract on cold or strong emotion; the hair is pulled upright and the skin around it is
raised into a bump. In furry animals raised fur traps an insulating layer of air, and makes the animal look bigger
when threatened; porcupine quills are modified hairs raised the same way. Humans kept the reflex with little body
hair (a vestigial reflex). Strong emotions, e.g. moving music, can trigger it too ("chills"/frisson).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
COLD = ('#bfe6ff', '#e9f6ff')

def cold_bg(c, t, top='#9fd4ff', bot='#e9f6ff'):
    sky(c, top, bot)
    snow(c, t, seed=4, n=30, y1=1500, alpha=200)

def fur_slab(c, t, y, up, warm=0.0, x0=60, x1=1020, n=46, colr='#c98a4a', seed=2):
    """Animal skin with fur. up 0..1 raises the fur; warm draws the trapped warm-air layer."""
    rnd = random.Random(seed)
    h = lerp(60, 260, up)
    if warm > 0:
        c.drawRect(skia.Rect(x0, y - h - 10, x1, y), lin(c, (0, y - h - 10, 0, y), [col('#ffb35c', 0), col('#ff9f1c', int(150 * warm))]))
    for i in range(n):
        x = lerp(x0 + 10, x1 - 10, i / (n - 1)) + rnd.uniform(-6, 6)
        lean = lerp(70, 8, up) + rnd.uniform(-8, 8) + math.sin(t * 2 + i) * 4
        L = lerp(150, 270, up) + rnd.uniform(-20, 20)
        ex, ey = x + math.sin(math.radians(lean)) * L, y - math.cos(math.radians(lean)) * L
        p = skia.Path(); p.moveTo(x, y); p.quadTo(x + (ex - x) * 0.3, y - L * 0.5 * math.cos(math.radians(lean)), ex, ey)
        c.drawPath(p, P(color=col(mix_hx(colr, '#5a3418', rnd.random() * 0.4)), stroke=9))
    c.drawRect(skia.Rect(x0 - 40, y, x1 + 40, y + 240), lin(c, (0, y, 0, y + 240), [col('#ffcfb0'), col('#f0a58c')]))
    c.drawLine(x0 - 40, y, x1 + 40, y, P(color=col('#d98572'), stroke=6))

def critter(c, x, y, s, t, puff, quills=False):
    """Plain round furry animal silhouette (side view) with natural eye; puff 0..1 fluffs it up."""
    c.save(); c.translate(x, y); c.scale(s, s)
    R = 170 * (1 + 0.35 * puff)
    n = 64
    body = skia.Path()
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        spike = (40 + 90 * puff) * (1 if i % 2 else 0.25) if quills else (18 + 40 * puff) * (0.6 + 0.4 * math.sin(i * 2.7))
        r = R + spike
        px, py = math.cos(a) * r * 1.15, math.sin(a) * r * 0.85
        if py > R * 0.6: py = R * 0.6 + (py - R * 0.6) * 0.3
        (body.moveTo if i == 0 else body.lineTo)(px, py)
    body.close()
    c.drawOval(skia.Rect(-R * 1.2, R * 0.55, R * 1.2, R * 0.8), P(color=col('#0b1a3a', 40), blur=10))
    c.drawPath(body, lin(c, (0, -R, 0, R), [col('#a9744a' if quills else '#d79a5e'), col('#6b4423' if quills else '#a8683a')]))
    c.drawPath(body, P(color=col('#5a3418'), stroke=5))
    # head bump + eye + nose (natural, no cartoon features)
    hx, hy = R * 1.05, -R * 0.05
    c.drawCircle(hx, hy, 70, P(color=col('#e8b98a')))
    c.drawCircle(hx + 18, hy - 18, 13, P(color=col('#1b1b1b')))
    c.drawCircle(hx + 22, hy - 22, 4, P(color=col('#ffffff')))
    c.drawCircle(hx + 66, hy + 10, 11, P(color=col('#3a2416')))
    for lx in (-R * 0.6, -R * 0.2, R * 0.3, R * 0.7):
        c.drawRoundRect(skia.Rect(lx - 18, R * 0.55, lx + 18, R * 0.55 + 60), 16, 16, P(color=col('#6b4423')))
    c.restore()

def music_note(c, x, y, s, alpha=255, colr='#ffd23f'):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-12)
    c.drawOval(skia.Rect(-34, -22, 30, 22), P(color=col(colr, a)))
    c.drawRect(skia.Rect(20, -150, 30, 0), P(color=col(colr, a)))
    f = skia.Path(); f.moveTo(30, -150); f.cubicTo(70, -130, 80, -100, 62, -70); f.cubicTo(66, -100, 50, -115, 30, -118); f.close()
    c.drawPath(f, P(color=col(colr, a)))
    c.restore()

# ---------- 1: Hook (cold open: bumps already rising) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    cold_bg(c, t)
    u = ease_in_out(prog(t, 0.0, 1.6))
    skin_section(c, 1080, t, bump=u, hair_up=u, muscle_k=u, show_muscle=0.0, hairs=(180, 540, 900))
    if t > t1:
        k = ease_back(prog(t, t1 + 0.6, 0.4))
        label_pill(c, 'made for FUR', 540, 1520, size=52, k=k, fill=NAVY, hi='#c98a4a')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.6, 'pop'), (0.9, 'pop'), (1.2, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 2: Each hair has a tiny muscle ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fff4ec', '#ffe2d2')
    z = ease_in_out(prog(t, 0.0, 1.5))
    c.save(); c.translate(540, 1100); s_ = lerp(1.0, 1.45, z); c.scale(s_, s_); c.translate(-540, -1100)
    skin_section(c, 860, t, bump=0, hair_up=0, muscle_k=0.15 * (0.5 + 0.5 * math.sin(t * 4)) * prog(t, t0 + 1.4, 0.5), show_muscle=prog(t, t0 + 1.2, 0.6), hairs=(540,), y1=1700)
    c.restore()
    label_pill(c, 'hair FOLLICLE', 300, 1510, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi='#c9705c')
    label_pill(c, 'MUSCLE', 790, 1510, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill='#e8264f', hi='#e8264f')
    if t > t1:
        label_pill(c, 'arrector pili', 790, 1400, size=40, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill='#e8264f')

def s2_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.4, 'click')]

# ---------- 3: Cold -> nerve signal -> squeeze -> hair up + bump ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    cold_bg(c, t, top='#bfe0ff', bot='#f2f9ff')
    sig = prog(t, t0 + 0.6, 1.0)
    sq = ease_in_out(prog(t, t1 - 0.2, 1.2))
    skin_section(c, 960, t, bump=sq, hair_up=sq, muscle_k=max(sq, 0.3 * sig), show_muscle=1.0, hairs=(300, 780))
    # nerve signal travelling in from the left
    if 0 < sig:
        c.drawLine(0, 1420, 380, 1420, P(color=col('#ffd23f', 160), stroke=8))
        for hx in (300, 780):
            c.drawLine(hx, 1420, hx + 50, 1180, P(color=col('#ffd23f', 160), stroke=6))
        if sig < 1:
            px = lerp(-20, 800, sig)
            c.drawCircle(px, 1420, 22, rad(px, 1420, 40, [col('#fff6b0'), col('#ffd23f', 0)]))
            c.drawCircle(px, 1420, 12, P(color=col('#fff6b0')))
        label_pill(c, 'nerve SIGNAL', 220, 1520, size=42, k=ease_back(prog(t, t0 + 0.8, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi='#d9a400')
    if t > t1:
        label_pill(c, 'SQUEEZE', 540, 1520, size=50, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill='#e8264f', hi='#e8264f')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 4: Raised fur traps warm air (puffy jacket) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    cold_bg(c, t)
    up = ease_in_out(prog(t, t0 + 0.5, 1.2))
    fur_slab(c, t, 1300, up, warm=ease_out(prog(t, t0 + 1.4, 1.0)))
    # cold arrows bouncing off
    for i in range(4):
        u = ((t * 0.7 + i * 0.25) % 1.0)
        x = 180 + i * 230
        top = 1300 - lerp(150, 290, up)
        if u < 0.6:
            y = lerp(700, top, u / 0.6)
        else:
            y = lerp(top, 760, (u - 0.6) / 0.4)
        arrow(c, x, y - 90 if u < 0.6 else y + 90, x, y, colr='#2f9bff', w=12, alpha=int(200 * up + 40))
    label_pill(c, 'warm AIR layer', 540, 1600 - 60, size=44, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill='#e07a00', hi='#e07a00')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        c.save(); c.translate(820, 830); c.scale(k, k)
        for i in range(4):
            c.drawRoundRect(skia.Rect(-90, -110 + i * 52, 90, -62 + i * 52), 24, 24, lin(c, (0, -110 + i * 52, 0, -62 + i * 52), [col('#ff8aa6'), col('#e8264f')]))
        c.drawRoundRect(skia.Rect(-12, -110, 12, 100), 6, 6, P(color=col('#ffd23f')))
        c.restore()

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'whoosh'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] + 0.2, 'pop')]

# ---------- 5: Fluffed = bigger; quills are hairs too ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#cdeeff', mid='#7cc6ff')
    hills(c, 1500, t=t, trees=False, flowers=False)
    if t < t1 - 0.1:
        p = ease_back(prog(t, t0 + 0.8, 0.8), 1.2)
        critter(c, 500, 1180, 1.0, t, p)
        label_pill(c, 'looks BIGGER', 540, 760, size=50, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#ff5c85')
    else:
        p = ease_back(prog(t, t1 + 0.6, 0.6), 1.3)
        critter(c, 500, 1180, 0.95, t, p, quills=True)
        label_pill(c, 'QUILLS = hairs', 540, 760, size=50, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi='#c98a4a')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 6: We lost the fur, kept the reflex ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fff4ec', '#ffe2d2')
    m = ease_in_out(prog(t, t0 + 0.6, 1.6))      # fur -> human skin
    if m < 1:
        c.saveLayerAlpha(None, int(255 * (1 - m)))
        fur_slab(c, t, 1200, 0.2, x0=80, x1=1000)
        c.restore()
    if m > 0:
        b = ease_back(prog(t, t1 + 0.2, 0.6)) if t > t1 else 0
        c.saveLayerAlpha(None, int(255 * m))
        skin_section(c, 1200, t, bump=b, hair_up=b, muscle_k=b, show_muscle=0.0, hairs=(160, 420, 680, 940), y1=1700)
        c.restore()
    label_pill(c, 'fur: GONE', 300, 760, size=46, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#c98a4a')
    label_pill(c, 'reflex: KEPT', 760, 760, size=46, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        label_pill(c, 'GOOSEBUMPS', 540, 1560, size=56, k=ease_back(prog(t, t1 + 0.6, 0.5), 2.2), fill='#e8264f', hi='#e8264f')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[0]['start'] + 2.2, 'pop'), (cues[1]['start'] + 0.6, 'ding')]

# ---------- 7: Wild part: music triggers it too ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2a1f4a', '#5a3a7a', mid='#3a2a5e')
    dust(c, t, seed=5, n=26)
    # speaker cone pulsing
    beat = 0.5 + 0.5 * math.sin(t * 8)
    k = ease_back(prog(t, t0 + 0.2, 0.5))
    c.save(); c.translate(200, 900); c.scale(k, k)
    c.drawRoundRect(skia.Rect(-120, -170, 120, 170), 30, 30, lin(c, (0, -170, 0, 170), [col('#3a4458'), col('#1f2533')]))
    c.drawCircle(0, 40, 80 + 6 * beat, P(color=col('#5b6476')))
    c.drawCircle(0, 40, 34, P(color=col('#1b2a4a')))
    c.drawCircle(0, -100, 30, P(color=col('#5b6476')))
    c.restore()
    if k > 0.5: sound_rings(c, 320, 940, t, t0 + 0.4, n=3, colr='#ffd23f', both=False)
    for i in range(5):
        u = ((t - t0) * 0.35 + i / 5) % 1.0
        if t > t0 + 0.4:
            music_note(c, lerp(330, 880, u), 940 - math.sin(u * 3.14) * 280 + i * 20, 0.7, alpha=255 * min(1, u * 5) * min(1, (1 - u) * 4), colr=['#ffd23f', '#ff5c85', '#2f9bff'][i % 3])
    if t > t1 - 0.3:
        b = 0.5 + 0.5 * math.sin((t - t1) * 5) if t > t1 + 1.0 else ease_out(prog(t, t1 - 0.3, 1.2))
        c.save(); c.translate(0, 0)
        skin_section(c, 1430, t, bump=b, hair_up=b, muscle_k=b, show_muscle=0.0, hairs=(520, 860), y1=H)
        c.restore()
        label_pill(c, 'same NERVES', 540, 1580, size=50, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill='#5a3a7a', hi='#ff5c85')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'pop'), (cues[0]['start'] + 0.6, 'sparkle'), (cues[1]['start'] - 0.3, 'whoosh'), (cues[1]['start'] + 0.4, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    cold_bg(c, t)
    b = 0.5 + 0.5 * math.sin(t * 2)
    skin_section(c, 1300, t, bump=b, hair_up=b, muscle_k=b, show_muscle=0.0, hairs=(180, 540, 900), y1=1700)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        for i in range(3):
            x = 300 + i * 220; y = 900 + math.sin(t * 3 + i) * 20
            arrow(c, x - 140, y, x + 40, y, colr='#ffffff', w=14, alpha=int(230 * fo * min(1, k)))
        label_pill(c, 'next: WIND', 540, 760, size=50, k=k, fill=NAVY, hi='#2f9bff', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do we get goosebumps?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do we get goosebumps?', 'Why do we get GOOSEBUMPS?'),
            ("It's a trick built for fur. And we barely have any.", 'A trick built for FUR')], tail=0.9),
        dict(name='muscle', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every hair on your body grows from a little pocket, with a tiny muscle attached.', 'Every hair has a tiny MUSCLE'),
            ("It's called the arrector pili.", 'The ARRECTOR PILI')], tail=0.9),
        dict(name='squeeze', draw=s3, sfx_fn=s3_sfx, lines=[
            ('When you get cold, your nerves tell those muscles to squeeze.', 'Cold? The nerves FIRE'),
            ('The hair stands up, and the skin around it bulges into a bump.', 'Hair UP, skin BUMPS')], tail=0.9),
        dict(name='fur', draw=s4, sfx_fn=s4_sfx, lines=[
            ('On a furry animal, raised fur traps a thick layer of warm air.', 'Raised fur TRAPS warm air'),
            ('Like puffing up a down jacket.', 'Like a PUFFY jacket')], tail=1.0),
        dict(name='bigger', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Animals also fluff up when they feel threatened, to look bigger.', 'Fluffed up = looks BIGGER'),
            ('Porcupine quills are hairs too, raised by the same reflex.', 'QUILLS are hairs too')], tail=1.0),
        dict(name='us', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Our ancestors lost most of their fur, but kept the reflex.', 'Lost the fur, kept the REFLEX'),
            ('So now, all it does is give us bumps.', 'Now it just makes BUMPS')], tail=1.4),
        dict(name='music', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: a great song or a big movie moment can trigger them too.", 'MUSIC can trigger them too'),
            ('Strong emotions fire the very same nerves.', 'Same NERVES, big feelings')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So goosebumps are a fur-fluffing reflex, minus the fur.', 'A fur reflex, minus the FUR'),
            ('Next up: what makes the wind blow.', 'Next: what makes WIND blow'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
