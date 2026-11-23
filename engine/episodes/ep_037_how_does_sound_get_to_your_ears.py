"""Episode 37 (EN, general audience): How does sound get to your ears?
Facts checked (NIDCD/NIH "How do we hear?", Johns Hopkins Medicine "How the ear works", Scientific American "How do
the hammer, anvil and stirrup amplify sound into the inner ear?", ASU Ask a Biologist "How do we hear?", RNID "How
the ear works", MSD Manual "Biology of the ears"):
- Sound is a vibration: a vibrating object pushes on air; air molecules pass the push on to their neighbours as a
  pressure wave, the air itself only moves back and forth a little. Speed in air ~343 m/s at 20 C.
- The outer ear (pinna) collects sound and funnels it through the ear canal to the eardrum, which vibrates.
- The eardrum passes the vibration to three tiny bones of the middle ear - malleus (hammer), incus (anvil), stapes
  (stirrup) - which amplify it (lever action + large eardrum vs. small oval window) and pass it into the cochlea.
- The cochlea is a snail-shaped, fluid-filled organ in the inner ear. The vibrations make the fluid ripple; a
  travelling wave on the basilar membrane moves sensory hair cells, which turn the motion into electrical signals.
  High pitches are detected near the base (entrance) of the cochlea, low pitches near the apex (deeper in).
- The auditory nerve carries the signals to the brain, which interprets them as sound.
- The stapes is the smallest bone in the human body, about 3 mm - roughly the size of a grain of rice.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'

def soft_bg(c, t, top='#eef6ff', bot='#d6e9fb'):
    sky(c, top, bot); dust(c, t, seed=8, n=10, a=60)

def drum(c, x, y, s, t, hit=0.0):
    """Snare-style drum, (x, y) = centre of the top; hit 0..1 = vibration strength."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRect(skia.Rect(-200, 0, 200, 220), lin(c, (-200, 0, 200, 0), [col('#e8264f'), col('#ff5c85'), col('#c2183e')], vertical=False, pos=[0, 0.45, 1]))
    for i in range(7):
        xx = -180 + i * 60
        c.drawLine(xx, 20, xx + 30, 200, P(color=col('#ffd23f'), stroke=6)); c.drawLine(xx + 30, 20, xx, 200, P(color=col('#ffd23f'), stroke=6))
    c.drawOval(skia.Rect(-200, 190, 200, 250), P(color=col('#c2183e')))
    c.drawRoundRect(skia.Rect(-206, 196, 206, 226), 14, 14, P(color=col('#d9dee8')))
    c.drawRoundRect(skia.Rect(-206, -6, 206, 24), 14, 14, P(color=col('#d9dee8')))
    v = hit * 10 * math.sin(t * 50)
    c.drawOval(skia.Rect(-200, -60 + v * 0.3, 200, 60 - v * 0.3), lin(c, (0, -60, 0, 60), [col('#ffffff'), col('#e9eef6')]))
    c.drawOval(skia.Rect(-200, -60, 200, 60), P(color=col('#c9d1df'), stroke=8))
    if hit > 0:
        for k in range(3):
            c.drawOval(skia.Rect(-60 - k * 45, -18 - k * 13, 60 + k * 45, 18 + k * 13), P(color=col('#9fb0c8', int(150 * hit)), stroke=3))
    c.restore()

def stick(c, x, y, ang):
    c.save(); c.translate(x, y); c.rotate(ang)
    c.drawRoundRect(skia.Rect(-12, -300, 12, 0), 12, 12, lin(c, (-12, 0, 12, 0), [col('#e8b77a'), col('#b77f45')], vertical=False))
    c.drawCircle(0, 0, 16, P(color=col('#f0c48a')))
    c.restore()

# ---------- 1: Hook (cold open: drum already being hit) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    soft_bg(c, t)
    period = 0.75
    ph = (t % period) / period
    ang = -40 + 40 * (1 - abs(1 - ph * 2)) if ph < 0.5 else -40 * (ph - 0.5) * 2
    hit = max(0.0, 1 - (t % period) / 0.4)
    drum(c, 540, 1260, 1.25, t, hit=hit)
    stick(c, 700, 1200, 40 + ang)
    n_hits = int(t / period)
    for k in range(max(0, n_hits - 2), n_hits + 1):
        sound_rings(c, 540, 1230, t, k * period, n=3, colr='#2f9bff', speed=520, life=1.4, w=12, a0=-150, sweep=120, both=False)
    label_pill(c, 'every sound = a SHAKE', 540, 690, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop')]

# ---------- 2: Air molecules pass the push on ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    cols_, rows = 13, 8
    x0, x1, y0, y1 = 80, 960, 880, 1420
    wave_x = lerp(x0 - 200, x1 + 200, ((t - t0) * 0.35) % 1.0)
    dk = prog(t, t0, 0.4)
    for r in range(rows):
        for i in range(cols_):
            bx = lerp(x0, x1, i / (cols_ - 1)); by = lerp(y0, y1, r / (rows - 1)) + (18 if i % 2 else 0)
            d = bx - wave_x
            push = 34 * math.exp(-(d / 90) ** 2) * (1 if d < 0 else 0.6) * dk
            px = bx + push; py = by + math.sin(t * 3 + i + r) * 3
            special = (r == 4 and i == 6)
            colr = HOT if special else '#7fb8ff'
            c.drawCircle(px, py, 18, P(color=col(colr, int(255 * dk))))
            c.drawCircle(px, py, 18, P(color=col(NAVY, int(150 * dk)), stroke=3))
    # compression band indicator
    c.drawRect(skia.Rect(wave_x - 40, y0 - 60, wave_x + 40, y1 + 60), P(color=col('#ffd23f', int(70 * dk)), blur=20))
    label_pill(c, 'molecules BUMP neighbors', 540, 700, size=42, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        arrow(c, 300, 1560, 780, 1560, colr=NAVY, w=14, alpha=int(255 * prog(t, t1 + 0.3, 0.4)))
        label_pill(c, '~343 m per SECOND', 540, 1640, size=40, k=ease_back(prog(t, t1 + 2.2, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, 'this one barely MOVES', 560, 800 + 0, size=36, k=ease_back(prog(t, t1 + 0.8, 0.4)) * (1 - prog(t, t1 + 2.1, 0.3)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t1 + 0.3, 'whoosh'), (t1 + 0.8, 'pop'), (t1 + 2.2, 'pop')]

# ---------- 3: Outer ear funnels to the eardrum ----------
EAR_X, EAR_Y, EAR_S = 30, 1150, 0.9

def wave_in(c, t, start, x_end):
    for k in range(4):
        tt = t - start - k * 0.35
        if tt < 0: continue
        u = (tt * 0.6) % 1.0
        x = lerp(-60, x_end, u)
        c.drawArc(skia.Rect(x - 80, EAR_Y - 90, x + 80, EAR_Y + 90), -50, 100, False, P(color=col(SKYB, int(230 * (1 - u * 0.6))), stroke=10))

def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    dk = ease_out(prog(t, t0, 0.5))
    c.save(); c.translate(0, 80 * (1 - dk))
    ear_section(c, EAR_X, EAR_Y, EAR_S, t, drum=1.0 if t > t1 + 0.4 else 0.0,
                hi=({'pinna', 'canal'} if t < t1 else {'drum'}), alpha=int(255 * dk))
    c.restore()
    c.save(); cl = skia.Path(); cl.addRect(skia.Rect(0, EAR_Y - 60, EAR_X + 520 * EAR_S, EAR_Y + 60)); c.clipPath(cl, doAntiAlias=True)
    wave_in(c, t, t0 + 0.4, EAR_X + 500 * EAR_S)
    c.restore()
    label_pill(c, 'a FUNNEL', 300, 760, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'EARDRUM', 500, 1530, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)
        arrow(c, 500, 1470, EAR_X + 525 * EAR_S, EAR_Y + 70, colr=NAVY, w=10, alpha=int(230 * prog(t, t1 + 0.6, 0.3)))

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.6, 'pop')]

# ---------- 4: Three tiny bones amplify (zoom) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#fff4e6', bot='#ffe3c4')
    z = 2.6; cx, cy = 600, -50  # zoom into the middle ear
    c.save(); c.translate(540, 1150); c.scale(z * EAR_S, z * EAR_S); c.translate(-cx, -cy)
    ear_section(c, 0, 0, 1.0, t, drum=1.0, bones=1.0 if t > t0 + 0.6 else 0.0)
    c.restore()
    names = [('HAMMER', 260, 860, HOT, 446, 1000), ('ANVIL', 640, 820, '#e0a000', 545, 1020), ('STIRRUP', 760, 1420, SKYB, 700, 1260)]
    for i, (nm, lx, ly, hi, px, py) in enumerate(names):
        kk_ = ease_back(prog(t, t0 + 1.4 + i * 0.6, 0.4))
        if kk_ > 0:
            c.drawLine(lx, ly, lerp(lx, px, min(1, kk_)), lerp(ly, py, min(1, kk_)), P(color=col(NAVY, 200), stroke=5))
            c.drawCircle(px, py, 9 * min(1, kk_), P(color=col(NAVY)))
        label_pill(c, nm, lx, ly, size=40, k=ease_back(prog(t, t0 + 1.4 + i * 0.6, 0.4)), fill=NAVY, hi=hi)
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.4, 0.5), 2.2)
        c.save(); c.translate(540, 1620); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-210, -50, 210, 50), 25, 25, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-210, -50, 210, 50), 25, 25, P(color=col(NAVY), stroke=5))
        text_block(c, 'STRONGER', 0, 0, size=50, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.4, 'pop'), (t0 + 2.0, 'pop'), (t0 + 2.6, 'pop'), (t1 + 0.4, 'boing')]

# ---------- 5: Cochlea + hair cells -> electric signals (aha) ----------
def hair_cells(c, x0, x1, y, t, wave_k, glow_k):
    n = 14
    for i in range(n):
        x = lerp(x0, x1, i / (n - 1))
        bend = wave_k * 18 * math.sin(t * 9 - i * 0.7)
        c.drawRoundRect(skia.Rect(x - 18, y, x + 18, y + 80), 14, 14, P(color=col('#ffd0dc')))
        c.drawRoundRect(skia.Rect(x - 18, y, x + 18, y + 80), 14, 14, P(color=col('#d0708a'), stroke=3))
        for k in (-8, 0, 8):
            c.drawLine(x + k, y, x + k + bend, y - 44, P(color=col('#8a4a6a'), stroke=4))
        if glow_k > 0:
            g = glow_k * (0.5 + 0.5 * math.sin(t * 9 - i * 0.7))
            c.drawCircle(x, y + 100, 22, rad(x, y + 100, 22, [col('#fff36b', int(255 * g)), col('#ffd23f', 0)]))

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # left: cochlea (zoomed); right side kept clear of platform UI
    c.save(); c.translate(380, 1000); s = 1.9; c.scale(s, s); c.translate(-840, -40)
    cp = cochlea_path(840, 40)
    c.drawPath(cp, P(color=col('#5a9fd6'), stroke=40)); c.drawPath(cp, P(color=col('#a8e0ff'), stroke=32))
    meas = skia.PathMeasure(cp, False); L = meas.getLength()
    fk = prog(t, t0 + 0.5, 0.5)
    for j in range(22):
        u = ((t * 0.5 + j / 22) % 1.0); pos, _ = meas.getPosTan(L * u)
        if pos is None: continue
        px, py = pos
        c.drawCircle(px, py, 6 + 3 * math.sin(t * 12 + j), P(color=col('#ffffff', int(230 * fk))))
    c.restore()
    label_pill(c, 'COCHLEA', 380, 760, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'full of FLUID', 780, 1000, size=38, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        k = ease_out(prog(t, t1 + 0.2, 0.5))
        c.save(); c.translate(0, 60 * (1 - k))
        c.drawRoundRect(skia.Rect(90, 1330, 930, 1500), 30, 30, P(color=col('#ffffff', int(235 * k))))
        c.drawRoundRect(skia.Rect(90, 1330, 930, 1500), 30, 30, P(color=col(NAVY, int(200 * k)), stroke=5))
        c.saveLayerAlpha(None, int(255 * k))
        hair_cells(c, 150, 870, 1370, t, wave_k=1.0, glow_k=prog(t, t1 + 1.6, 0.5))
        c.restore()
        c.restore()
        label_pill(c, 'HAIR CELLS', 300, 1290, size=36, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)
        kk = ease_back(prog(t, t1 + 1.6, 0.5), 2.2)
        c.save(); c.translate(540, 1600); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-280, -50, 280, 50), 25, 25, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-280, -50, 280, 50), 25, 25, P(color=col(NAVY), stroke=5))
        text_block(c, 'ELECTRIC signals', 0, 0, size=46, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.4, 'pop'), (t1 + 0.6, 'pop'), (t1 + 1.6, 'ding')]

# ---------- 6: High notes near the entrance, low deeper; nerve -> brain ----------
def brain(c, x, y, s, t, glow=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow > 0:
        c.drawCircle(0, 0, 200, rad(0, 0, 200, [col('#ffd23f', int(170 * glow)), col('#ffd23f', 0)]))
    p = skia.Path(); p.addOval(skia.Rect(-150, -105, 150, 105))
    c.drawPath(p, lin(c, (0, -105, 0, 105), [col('#ffc1d0'), col('#f49ab2')]))
    for (a0, a1, b0, b1) in ((-110, -60, 20, -40), (-40, -80, 60, -20), (40, -70, 110, -10), (-120, 10, -40, 50), (-20, 20, 70, 60), (80, 10, 130, 50)):
        q = skia.Path(); q.moveTo(a0, a1); q.cubicTo((a0 + b0) / 2, a1 - 30, (a0 + b0) / 2, b1 + 30, b0, b1)
        c.drawPath(q, P(color=col('#d0708a'), stroke=6))
    c.drawLine(0, -100, 0, 100, P(color=col('#d0708a', 150), stroke=5))
    c.drawPath(p, P(color=col('#c0607a'), stroke=6))
    c.restore()

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#f1ecff', bot='#e1ebff')
    # unrolled cochlea strip
    x0, x1, y = 110, 930, 1050
    k = ease_out(prog(t, t0, 0.6))
    c.drawRoundRect(skia.Rect(x0, y - 60, lerp(x0 + 60, x1, k), y + 60), 60, 60, lin(c, (x0, 0, x1, 0), [col('#a8e0ff'), col('#d6f0ff')], vertical=False))
    c.drawRoundRect(skia.Rect(x0, y - 60, lerp(x0 + 60, x1, k), y + 60), 60, 60, P(color=col('#5a9fd6'), stroke=6))
    # high (fast) wiggle near entrance, low (slow) wave deeper in
    hk = prog(t, t0 + 0.8, 0.4); lk = prog(t, t0 + 2.0, 0.4)
    for (xa, xb, f, ak, colr) in ((x0 + 30, 420, 0.12, hk, HOT), (560, x1 - 30, 0.035, lk, '#9b4dff')):
        if ak <= 0: continue
        p = skia.Path()
        for i in range(0, 81):
            xx = lerp(xa, xb, i / 80); yy = y + 38 * math.sin(xx * f - t * 8) * ak
            (p.moveTo if i == 0 else p.lineTo)(xx, yy)
        c.drawPath(p, P(color=col(colr), stroke=8))
    label_pill(c, 'HIGH notes', 270, 900, size=38, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'LOW notes', 740, 900, size=38, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi='#9b4dff')
    label_pill(c, 'entrance', 220, 1160, size=30, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY)
    label_pill(c, 'deep inside', 800, 1160, size=30, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY)
    label_pill(c, 'pitch has a PLACE', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi='#e0a000')
    if t > t1:
        nk = prog(t, t1 + 0.2, 0.8)
        np_ = skia.Path(); np_.moveTo(540, 1120); np_.cubicTo(540, 1250, 700, 1300, 700, 1400)
        meas = skia.PathMeasure(np_, False); L = meas.getLength(); seg = skia.Path(); meas.getSegment(0, L * nk, seg, True)
        c.drawPath(seg, P(color=col('#ffd23f'), stroke=16)); c.drawPath(seg, P(color=col('#e0a800'), stroke=4))
        if nk >= 1:
            u = ((t - t1) * 1.4) % 1.0; pos, _ = meas.getPosTan(L * u)
            if pos is not None:
                px, py = pos; c.drawCircle(px, py, 18, rad(px, py, 18, [col('#ffffff'), col('#fff36b', 0)]))
        bk = ease_back(prog(t, t1 + 0.8, 0.5))
        if bk > 0:
            brain(c, 700, 1470, 0.75 * bk, t, glow=prog(t, t1 + 1.6, 0.5) * (0.7 + 0.3 * math.sin(t * 6)))
        label_pill(c, 'the BRAIN hears it', 330, 1600, size=38, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 2.0, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.8, 'pop'), (t1 + 1.6, 'sparkle')]

# ---------- 7: Wild part: stirrup = smallest bone, size of a rice grain ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#fff4e6', bot='#ffe3c4')
    sk = ease_back(prog(t, t0 + 0.3, 0.6))
    shrink = ease_in_out(prog(t, t1 + 0.2, 1.4))
    s = lerp(3.2, 0.9, shrink) * sk
    if s > 0.01:
        stirrup(c, 540 - 120 * shrink, 1080, s, rot=math.sin(t * 1.2) * 3)
    label_pill(c, 'the SMALLEST bone', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        rk = ease_back(prog(t, t1 + 1.0, 0.5))
        if rk > 0:
            c.save(); c.translate(680, 1080); c.rotate(-15); c.scale(rk, rk)
            c.drawOval(skia.Rect(-55, -22, 55, 22), rad(-15, -8, 60, [col('#ffffff'), col('#f3ecd9')]))
            c.drawOval(skia.Rect(-55, -22, 55, 22), P(color=col('#cfc3a0'), stroke=3))
            c.restore()
        # ruler
        rk2 = ease_out(prog(t, t1 + 1.6, 0.5))
        if rk2 > 0:
            c.save(); c.translate(0, 60 * (1 - rk2))
            c.drawRoundRect(skia.Rect(240, 1300, 840, 1400), 14, 14, P(color=col('#ffe08a', int(255 * rk2))))
            for i in range(0, 13):
                xx = 280 + i * 45
                c.drawLine(xx, 1300, xx, 1300 + (40 if i % 2 == 0 else 24), P(color=col(NAVY, int(255 * rk2)), stroke=4))
            c.drawRoundRect(skia.Rect(240, 1300, 840, 1400), 14, 14, P(color=col(NAVY, int(200 * rk2)), stroke=5))
            c.restore()
        label_pill(c, 'about 3 MM', 540, 1520, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=SKYB)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 1.0, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 1.0, 'pop'), (t1 + 1.6, 'click')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    soft_bg(c, t)
    ear_section(c, EAR_X, 1100, EAR_S, t, drum=1.0, bones=1.0, fluid=1.0, nerve=1.0)
    c.save(); cl = skia.Path(); cl.addRect(skia.Rect(0, 1100 - 60, EAR_X + 520 * EAR_S, 1100 + 60)); c.clipPath(cl, doAntiAlias=True)
    c.translate(0, -50); wave_in(c, t, 0.0, EAR_X + 500 * EAR_S)
    c.restore()
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: why things FALL', 540, 700, size=46, k=kk, fill=NAVY, hi=HOT)
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How does sound get to your ears?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does sound get into your ears?', 'How does SOUND reach your ears?'),
            ('Every sound you have ever heard started with something shaking.', 'Every sound starts with a SHAKE')], tail=0.8),
        dict(name='air', draw=s2, sfx_fn=s2_sfx, lines=[
            ('The shaking pushes the air, and molecules pass it on like dominoes.', 'Molecules BUMP their neighbors'),
            ('The air barely moves. Only the push travels, about three hundred forty meters a second.', 'Only the PUSH travels')], tail=0.8),
        dict(name='funnel', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Your outer ear catches the push and funnels it down the ear canal,', 'Your ear is a FUNNEL'),
            ('right onto the eardrum, a thin skin stretched tight like a drum.', 'It hits the EARDRUM')], tail=0.8),
        dict(name='bones', draw=s4, sfx_fn=s4_sfx, lines=[
            ('The eardrum shakes three tiny bones: hammer, anvil and stirrup.', 'Three tiny BONES'),
            ('Working like levers, they make the push stronger.', 'They make the push STRONGER')], tail=0.8),
        dict(name='cochlea', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('The stirrup pushes on the cochlea, a snail-shaped tube full of fluid.', 'The COCHLEA: a fluid-filled snail'),
            ('Thousands of hair cells ride the ripples and turn them into electrical signals.', 'Hair cells make ELECTRIC signals')], tail=1.2),
        dict(name='brain', draw=s6, sfx_fn=s6_sfx, lines=[
            ('High notes are picked up near the entrance, low notes deeper inside.', 'HIGH near the entrance, LOW deep'),
            ('A nerve carries the signals to your brain, which turns them into sound.', 'The BRAIN turns it into sound')], tail=1.0),
        dict(name='stirrup', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: the stirrup is the smallest bone in your body,", 'The SMALLEST bone in your body'),
            ('about three millimeters, the size of a grain of rice.', 'About the size of a RICE grain')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So sound is a push passed through the air and turned into signals.', 'A PUSH turned into signals'),
            ('Next: why things fall down.', 'Next: why things FALL'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
