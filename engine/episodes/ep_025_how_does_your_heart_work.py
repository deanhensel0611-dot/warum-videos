"""Episode 25 (EN, general audience): How does your heart work?
Facts checked (Texas Heart Institute "Heart anatomy", WebMD "What triggers a heartbeat", HonorHealth "How the heart
works", Science News Explores "Anatomy of a heartbeat"):
- The heart is a muscular pump about the size of a fist; it beats roughly 100,000 times a day.
- It works as two pumps: the right side sends oxygen-poor blood to the lungs, the left side sends oxygen-rich blood
  to the rest of the body.
- Four chambers: two upper atria receive/collect blood, two lower ventricles pump it out.
- Valves act as one-way doors so blood can't flow backwards; the "lub-dub" heart sounds are made by the valves
  closing (lub = AV valves, dub = aortic/pulmonary valves).
- Each beat starts with an electrical impulse from the sinoatrial (SA) node in the right atrium, the heart's
  natural pacemaker; the impulse spreads through the atria first, then (via the AV node) the ventricles.
- The heartbeat is generated inside the heart itself (it is "autorhythmic"); the brain/nervous system only
  speeds it up or slows it down.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def warm_bg(c, t, top='#fff4ec', bot='#ffe2d2'):
    sky(c, top, bot)
    dust(c, t, seed=3, n=14, a=80, colr='#ffffff')

def beat(t, bpm=72, offset=0.0):
    ph = ((t + offset) * bpm / 60.0) % 1.0
    return math.sin(math.pi * ph / 0.28) if ph < 0.28 else 0.0

def ecg(c, t, y, x0=40, x1=W - 40, alpha=230, colr='#ff5c85', bpm=72):
    """Scrolling heart-monitor trace."""
    p = skia.Path(); first = True
    period = 60.0 / bpm * 260
    for i in range(0, 201):
        x = lerp(x0, x1, i / 200)
        u = ((x - x0 + t * 260) % period) / period
        if 0.30 < u < 0.34: dy = -lerp(0, 30, (u - 0.30) / 0.04)
        elif 0.40 < u < 0.43: dy = lerp(0, 20, (u - 0.40) / 0.03)
        elif 0.43 <= u < 0.46: dy = lerp(20, -150, (u - 0.43) / 0.03)
        elif 0.46 <= u < 0.49: dy = lerp(-150, 40, (u - 0.46) / 0.03)
        elif 0.49 <= u < 0.52: dy = lerp(40, 0, (u - 0.49) / 0.03)
        elif 0.62 < u < 0.74: dy = -math.sin((u - 0.62) / 0.12 * math.pi) * 40
        else: dy = 0
        (p.moveTo if first else p.lineTo)(x, y + dy); first = False
    c.drawPath(p, P(color=col(colr, int(alpha * 0.4)), stroke=16, blur=6))
    c.drawPath(p, P(color=col(colr, alpha), stroke=8))

def lungs(c, x, y, s, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-12, -150, 12, -40), 10, 10, P(color=col('#b9c4d4', a)))
    for sx in (-1, 1):
        lp = skia.Path(); lp.moveTo(sx * 20, -60)
        lp.cubicTo(sx * 140, -120, sx * 170, 60, sx * 140, 120); lp.cubicTo(sx * 100, 150, sx * 30, 130, sx * 25, 90); lp.close()
        c.drawPath(lp, lin(c, (0, -100, 0, 140), [col('#ffc4d0', a), col('#ff8fa3', a)]))
        c.drawPath(lp, P(color=col('#d9506e', a), stroke=5))
        c.drawLine(sx * 10, -45, sx * 60, 10, P(color=col('#d9506e', int(a * 0.7)), stroke=6))
    c.restore()

def bottle(c, x, y, s, sq, alpha=255):
    """Squeezable water bottle; sq 0..1 squeezes the middle and shoots a jet."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    w_ = lerp(90, 52, sq)
    p = skia.Path(); p.moveTo(-90, 160); p.lineTo(-90, 40); p.quadTo(-w_, -20, -90, -70); p.lineTo(-60, -130); p.lineTo(60, -130)
    p.lineTo(90, -70); p.quadTo(w_, -20, 90, 40); p.lineTo(90, 160); p.close()
    c.drawPath(p, lin(c, (-90, 0, 90, 0), [col('#9fd6f5', a), col('#d4efff', a), col('#7cc6ff', a)], vertical=False))
    c.drawPath(p, P(color=col('#1f6fc4', a), stroke=5))
    c.drawRoundRect(skia.Rect(-30, -175, 30, -128), 8, 8, P(color=col('#ff5c85', a)))
    if sq > 0.05:
        for i in range(6):
            yy = -190 - i * 40 * sq
            c.drawCircle(math.sin(i) * 6, yy, 14 - i, P(color=col('#2f9bff', int(a * sq))))
    c.restore()

def brain(c, x, y, s, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.addOval(skia.Rect(-170, -110, 170, 110))
    c.drawPath(p, lin(c, (0, -110, 0, 110), [col('#ffd0dc', a), col('#f7a8bb', a)]))
    c.drawPath(p, P(color=col('#c9607e', a), stroke=6))
    for i, (x0, y0) in enumerate(((-110, -40), (-40, -70), (40, -60), (110, -20), (-90, 40), (0, 20), (90, 50))):
        q = skia.Path(); q.moveTo(x0 - 40, y0); q.cubicTo(x0 - 20, y0 - 30, x0 + 20, y0 + 30, x0 + 40, y0)
        c.drawPath(q, P(color=col('#c9607e', int(a * 0.8)), stroke=6))
    c.drawLine(0, -105, 0, 105, P(color=col('#c9607e', int(a * 0.5)), stroke=5))
    c.restore()

# ---------- 1: Hook (cold open: heart already beating, monitor running) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    warm_bg(c, t)
    b = beat(t)
    heart(c, 540, 1080, 0.9, t, squeeze=b, glow=0.5 + 0.5 * b)
    ecg(c, t, 1450)
    k = ease_back(prog(t, 0.5, 0.4))
    n = int(lerp(0, 100000, ease_out(prog(t, 0.5, 1.8))))
    label_pill(c, f'{n:,} beats / DAY', 540, 1590, size=50, k=k, fill='#e8264f', hi='#e8264f')
    if t > t1:
        label_pill(c, 'NO breaks', 800, 720, size=44, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi='#ff5c85')

def s1_sfx(D, cues): return [(0.0, 'pop'), (0.5, 'pop'), (cues[1]['start'] + 2.0, 'pop')]

# ---------- 2: A fist-sized pump; squeeze like a bottle ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    warm_bg(c, t)
    mv = ease_in_out(prog(t, t1 - 0.2, 0.8))
    b = beat(t, bpm=60)
    heart(c, lerp(540, 330, mv), 1120, lerp(0.85, 0.62, mv), t, squeeze=b, glow=0.3 * b)
    label_pill(c, 'MUSCLE', 540 - 210 * mv, 1560, size=48, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill='#e8264f', hi='#e8264f')
    label_pill(c, '~ fist SIZE', 540 - 210 * mv, 740, size=44, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        bk = ease_back(prog(t, t1 + 0.4, 0.5))
        bottle(c, 790, 1180, 1.0 * bk, b)
        label_pill(c, 'SQUEEZE', 790, 1560, size=48, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill='#1f6fc4', hi='#1f6fc4')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.0, 'pop')]

# ---------- 3: Two pumps: lungs + body ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    warm_bg(c, t, top='#eaf4ff', bot='#ffe9e9')
    ck = ease_in_out(prog(t, t0 + 0.4, 0.9))
    b = beat(t, bpm=60)
    hl = None
    if t > t1: hl = ['RA', 'RV'] if t < t1 + 3.2 else ['LA', 'LV']
    heart(c, 540, 1230, 0.85, t, squeeze=b, chambers=ck, valves=1 - b, hi=hl)
    sp = ease_back(prog(t, t0 + 1.2, 0.5))
    if sp > 0 and t < t1:
        c.drawLine(540, 950, 540, 1530, P(color=col('#ffffff', int(200 * min(1, sp))), stroke=10))
        label_pill(c, 'PUMP 1', 330, 1600, size=44, k=sp, fill='#3d5bb8', hi='#3d5bb8')
        label_pill(c, 'PUMP 2', 750, 1600, size=44, k=sp, fill='#e8264f', hi='#e8264f')
    if t > t1:
        lk = ease_back(prog(t, t1 + 0.6, 0.5))
        if lk > 0:
            lungs(c, 230, 780, 0.95 * lk)
            u = (t * 0.8) % 1.0
            arrow(c, 380, 1050, lerp(380, 300, 0.5), lerp(1050, 900, 0.5), colr='#3d5bb8', w=14, alpha=int(255 * min(1, lk)))
            label_pill(c, 'LUNGS', 230, 960, size=44, k=lk, fill='#3d5bb8', hi='#3d5bb8')
            c.drawCircle(lerp(380, 300, u), lerp(1050, 900, u), 12, P(color=col(HEART_LOW)))
        bk = ease_back(prog(t, t1 + 3.4, 0.5))
        if bk > 0:
            for i, (dx, dy) in enumerate(((1, -0.6), (1, 0.1), (0.8, 0.8))):
                x0, y0 = 790, 1000
                arrow(c, x0, y0, x0 + dx * 120 * bk, y0 + dy * 120 * bk, colr='#e8264f', w=12)
            label_pill(c, 'whole BODY', 790, 800, size=44, k=bk, fill='#e8264f', hi='#e8264f')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 1.2, 'pop'), (cues[1]['start'] + 0.6, 'pop'), (cues[1]['start'] + 3.4, 'pop')]

# ---------- 4: Four chambers: top collect, bottom pump ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    warm_bg(c, t)
    top = t < t1
    b = beat(t, bpm=60) if not top else 0.15 * beat(t, bpm=60)
    heart(c, 540, 1170, 1.0, t, squeeze=b, chambers=1.0, valves=0.0 if top else 1 - b, hi=['RA', 'LA'] if top else ['RV', 'LV'])
    if top:
        # blood dots flowing into the top rooms
        for i in range(6):
            u = (t * 0.6 + i / 6) % 1.0
            c.drawCircle(350, lerp(700, 950, u), 12, P(color=col(HEART_LOW, int(255 * (1 - u)))))
            c.drawCircle(700, lerp(700, 950, u), 12, P(color=col(HEART_O2, int(255 * (1 - u)))))
        label_pill(c, 'COLLECT', 540, 700, size=48, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    else:
        label_pill(c, 'PUMP', 540, 1600, size=52, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill='#e8264f', hi='#e8264f')
        k4 = ease_back(prog(t, t1 + 2.3, 0.5), 2.2)
        if k4 > 0:
            c.save(); c.translate(870, 720); c.scale(k4, k4)
            c.drawCircle(0, 0, 72, P(color=col('#ff5c85'))); c.drawCircle(0, 0, 72, P(color=col('#ffffff'), stroke=7))
            text_block(c, '4', 0, 0, size=90, fill='#ffffff', stroke='#b8183f')
            c.restore()

def s4_sfx(D, cues): return [(cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 2.3, 'pop')]

# ---------- 5: Valves = one-way doors; lub-dub (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    warm_bg(c, t, top='#fff0f3', bot='#ffd9e0')
    z = ease_in_out(prog(t, 0.0, 1.2))
    cyc = (t * 0.8) % 1.0
    v = ease_in_out(clamp((cyc - 0.4) / 0.15)) if cyc < 0.9 else 1 - ease_in_out((cyc - 0.9) / 0.1)
    c.save(); c.translate(540, 1150); s_ = lerp(1.0, 1.7, z); c.scale(s_, s_); c.translate(-540, -1150)
    heart(c, 540, 1150 + 120 * z, 0.9, t, squeeze=0.0, chambers=1.0, valves=v, vessels=True)
    c.restore()
    label_pill(c, 'VALVE', 300, 760, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#ff5c85')
    label_pill(c, 'ONE-WAY', 760, 760, size=46, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1 + 1.4:
        for j, (word, dt) in enumerate((('LUB', 0.0), ('DUB', 0.6))):
            st = t1 + 1.6 + dt
            if t > st:
                sound_rings(c, 540, 1300, t, st, n=2, colr='#ffffff', both=True, speed=500)
                label_pill(c, word, 360 + j * 360, 1580, size=64, k=ease_back(prog(t, st, 0.4), 2.4), fill='#e8264f', hi='#e8264f')

def s5_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] + 1.6, 'click'), (cues[1]['start'] + 2.2, 'click'), (cues[1]['start'] + 2.7, 'ding')]

# ---------- 6: The spark: built-in pacemaker, top first then bottom ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#3a2a5e')
    dust(c, t, seed=8, n=20, a=90)
    period = 1.6
    ph = ((t - t0) % period) / period if t > t0 else -1
    spark = ph / 0.7 if 0 <= ph < 0.7 else -1
    sq = math.sin(math.pi * clamp((ph - 0.25) / 0.45)) if ph > 0.25 else 0
    heart(c, 540, 1150, 0.95, t, squeeze=sq * 0.8, chambers=0.65, valves=1.0, spark=spark if t > t1 else -1)
    # SA node
    nk = ease_back(prog(t, t0 + 0.6, 0.4))
    if nk > 0:
        x, y = 540 - 0.95 * 180, 1150 - 0.95 * 190
        fl = 1.0 if 0 <= ph < 0.12 else 0.4
        c.drawCircle(x, y, 60 * nk, rad(x, y, 60 * nk, [col('#fff6b0', int(255 * fl)), col('#ffd23f', 0)]))
        c.drawCircle(x, y, 16 * nk, P(color=col('#fff6b0')))
        label_pill(c, 'PACEMAKER', 300, 760, size=44, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#d9a400')
    if t > t1:
        label_pill(c, 'TOP, then BOTTOM', 540, 1600, size=46, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi='#d9a400')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'sparkle'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.8, 'pop')]

# ---------- 7: Wild part: the brain doesn't start it ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    warm_bg(c, t, top='#efe9ff', bot='#ffe2ec')
    bk = ease_back(prog(t, t0 + 0.4, 0.5))
    brain(c, 540, 820, 0.75 * bk)
    b = beat(t, bpm=72 if t < t1 + 1.0 else lerp(72, 110, ease_in_out(prog(t, t1 + 1.0, 1.0))))
    heart(c, 540, 1300, 0.6, t, squeeze=b, glow=0.4 * b)
    if t < t1:
        xk = ease_back(prog(t, t0 + 2.6, 0.4))
        if xk > 0:
            c.save(); c.translate(540, 1010); c.scale(xk, xk)
            c.drawLine(-60, -60, 60, 60, P(color=col('#e8264f'), stroke=22)); c.drawLine(60, -60, -60, 60, P(color=col('#e8264f'), stroke=22))
            c.restore()
        label_pill(c, 'spark: INSIDE', 540, 1620, size=46, k=ease_back(prog(t, t0 + 3.4, 0.4)), fill='#e8264f', hi='#e8264f')
    else:
        # nerve line + speed dial
        dk = ease_out(prog(t, t1, 0.6))
        c.drawLine(540, 900, 540, lerp(900, 1100, dk), P(color=col('#ffd23f', 220), stroke=10))
        gk = ease_back(prog(t, t1 + 0.4, 0.5))
        if gk > 0:
            c.save(); c.translate(860, 1300); c.scale(gk, gk)
            pth = skia.Path(); pth.addArc(skia.Rect(-110, -110, 110, 110), 180, 180)
            c.drawPath(pth, P(color=col('#ffffff'), stroke=30))
            pth2 = skia.Path(); pth2.addArc(skia.Rect(-110, -110, 110, 110), 180, 180 * (0.3 + 0.5 * ease_in_out(prog(t, t1 + 1.0, 1.0))))
            c.drawPath(pth2, P(color=col('#ff5c85'), stroke=30))
            ang = math.radians(180 + 180 * (0.3 + 0.5 * ease_in_out(prog(t, t1 + 1.0, 1.0))))
            c.drawLine(0, 0, math.cos(ang) * 90, math.sin(ang) * 90, P(color=col(NAVY), stroke=10))
            c.drawCircle(0, 0, 14, P(color=col(NAVY)))
            c.restore()
        label_pill(c, 'SPEED only', 540, 1620, size=46, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi='#ff5c85')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 2.6, 'click'), (cues[0]['start'] + 3.4, 'sparkle'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 0.8, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    warm_bg(c, t)
    b = beat(t)
    heart(c, 540, 1060, 0.75, t, squeeze=b, glow=0.4 + 0.4 * b)
    ecg(c, t, 1380, alpha=200)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        sound_rings(c, 540, 760, t, cues[1]['start'], n=4, colr='#2f9bff', both=True)
        label_pill(c, 'next: ECHOES', 540, 760, size=48, k=k, fill=NAVY, hi='#2f9bff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How does your heart work?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does your heart work?', 'How does your HEART work?'),
            ('It beats about a hundred thousand times a day, and never takes a break.', '100,000 BEATS a day')], tail=0.8),
        dict(name='pump', draw=s2, sfx_fn=s2_sfx, lines=[
            ("It's a muscle about the size of your fist, and its job is simple: pump.", 'A fist-sized PUMP'),
            ('Each beat squeezes blood out, like squeezing a water bottle.', 'Each beat SQUEEZES')], tail=0.8),
        dict(name='two', draw=s3, sfx_fn=s3_sfx, lines=[
            ("It's really two pumps, side by side.", 'TWO pumps in one'),
            ('The right side sends blood to your lungs to pick up oxygen. The left side sends it to your whole body.', 'LUNGS first, then the BODY')], tail=1.0),
        dict(name='chambers', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Each side has two rooms: a top chamber that collects blood,', 'Top rooms COLLECT'),
            ('and a bottom chamber that pumps it out. Four in total.', 'Bottom rooms PUMP')], tail=1.0),
        dict(name='valves', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Between them sit valves: one-way doors that stop blood flowing backwards.', 'VALVES: one-way doors'),
            ('That lub-dub sound of a heartbeat? The valves snapping shut.', 'LUB-DUB = valves CLOSING')], tail=1.4),
        dict(name='spark', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Every beat starts with a tiny electrical spark from a built-in pacemaker.', 'It starts with a SPARK'),
            ('The signal sweeps down: the top chambers squeeze first, then the bottom ones.', 'Top first, then BOTTOM')], tail=1.0),
        dict(name='brain', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: your brain doesn't start your heartbeat. The spark is made inside the heart itself.", "The brain doesn't START it"),
            ('Your brain can only speed it up or slow it down.', 'It only sets the SPEED')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So your heart is two pumps, four rooms, and one little spark.', 'Two pumps, four rooms, one SPARK'),
            ('Next up: how echoes work.', 'Next: how ECHOES work'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
