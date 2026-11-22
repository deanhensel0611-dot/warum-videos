"""Episode 33 (EN, general audience): How do earthquakes happen?
Facts checked (USGS "The Science of Earthquakes" / "Earthquake facts", British Geological Survey "What causes
earthquakes?", National Geographic "Earthquakes", Michigan Tech "Where do earthquakes happen?"):
- Earth's outer shell (lithosphere) is broken into large tectonic plates that move slowly, a few centimetres per
  year - roughly the speed fingernails grow (USGS comparison). Motion is driven by heat/convection in the mantle.
- At faults, rough edges stick because of friction while the plates keep moving; the rock deforms and stores
  elastic strain energy (elastic rebound theory, Reid 1910).
- When the stress overcomes friction, the rock slips suddenly (seconds) and the stored energy is released as
  seismic waves that travel through the ground and cause the shaking.
- USGS: an estimated ~500,000 detectable earthquakes happen worldwide each year; ~100,000 can be felt - most are
  too small to notice.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
ROCK = '#c98a5b'
HOT = '#ff7a3d'

def soft_bg(c, t, top='#fff4e6', bot='#ffe3c4'):
    sky(c, top, bot)
    dust(c, t, seed=8, n=10, a=70, colr='#ffffff')

# ---- top-view fault with a road crossing it (elastic rebound) ----
def fault_view(c, t, bend, slip, D=120, y0=760, y1=1500, xf=540, flash=0.0, arrows=0.0):
    """bend 0..1: elastic bending while stuck; slip 0..1: snap to offset."""
    # fields
    for (xa, xb, g1, g2, d) in ((60, xf, '#8fd16a', '#6fbf4f', -1), (xf, W - 60, '#9ad874', '#78c455', 1)):
        sh = d * D * slip
        c.save(); cl = skia.Path(); cl.addRoundRect(skia.Rect(60, y0, W - 60, y1), 40, 40); c.clipPath(cl, doAntiAlias=True)
        c.drawRect(skia.Rect(xa, y0, xb, y1), lin(c, (0, y0, 0, y1), [col(g1), col(g2)]))
        rnd = random.Random(1 if d < 0 else 2)
        for k in range(14):
            px = rnd.uniform(xa + 30, xb - 30); py = rnd.uniform(y0 + 30, y1 - 30) + sh * 0.0
            c.drawLine(px - 18, py, px + 18, py, P(color=col('#5aa83f', 160), stroke=5))
        c.restore()
    # road
    def ry(x):
        dx = x - xf; s_ = 1 if dx > 0 else -1
        bent = s_ * D * (1 - math.exp(-abs(dx) / 170))
        off = s_ * D
        return (y0 + y1) / 2 + lerp(bent * bend, off, slip)
    c.save(); clr = skia.Path(); clr.addRoundRect(skia.Rect(60, y0, W - 60, y1), 40, 40); c.clipPath(clr, doAntiAlias=True)
    for side in (-1, 1):
        p = skia.Path(); first = True
        xs = [xf + side * (2 + i * 8) for i in range(0, 61)]
        for x in xs:
            x = min(max(x, 60), W - 60)
            (p.moveTo if first else p.lineTo)(x, ry(x)); first = False
        c.drawPath(p, P(color=col('#6b7280'), stroke=70))
        c.drawPath(p, P(color=col('#ffffff', 220), stroke=6))
    c.restore()
    # fault line
    fp = skia.Path(); fp.moveTo(xf, y0)
    for i in range(1, 15):
        fp.lineTo(xf + (9 if i % 2 else -9), lerp(y0, y1, i / 14))
    c.drawPath(fp, P(color=col('#7a4a2a'), stroke=10))
    if flash > 0:
        c.drawCircle(xf, (y0 + y1) / 2, 240, rad(xf, (y0 + y1) / 2, 240, [col('#ffd23f', int(220 * flash)), col('#ffd23f', 0)]))
    if arrows > 0:
        a = int(255 * arrows)
        arrow(c, 220, y1 - 60, 220, y1 - 260, colr=NAVY, w=16, alpha=a)
        arrow(c, 860, y0 + 60, 860, y0 + 260, colr=NAVY, w=16, alpha=a)
    c.drawRoundRect(skia.Rect(60, y0, W - 60, y1), 40, 40, P(color=col(NAVY, 200), stroke=6))

# ---- cross-section ----
def cross_section(c, t, ysurf=980, houses=True, shake=0.0):
    c.drawRect(skia.Rect(0, ysurf, W, H), lin(c, (0, ysurf, 0, H), [col('#d9a06b'), col('#b8743f')]))
    for k, yy in enumerate((1130, 1290, 1450)):
        p = skia.Path(); p.moveTo(0, yy)
        for i in range(0, W + 41, 40): p.lineTo(i, yy + 14 * math.sin(i * 0.01 + k))
        c.drawPath(p, P(color=col('#a7653a', 120), stroke=5))
    p = skia.Path(); p.moveTo(0, ysurf)
    for i in range(0, W + 21, 20):
        p.lineTo(i, ysurf + shake * 14 * math.sin(i * 0.03 - t * 22))
    p.lineTo(W, ysurf + 40); p.lineTo(0, ysurf + 40); p.close()
    c.drawPath(p, P(color=col('#6fbf4f')))
    if houses:
        for i, x in enumerate((220, 860)):
            ang = shake * 3 * math.sin(t * 18 + i)
            house(c, x, ysurf + shake * 14 * math.sin(x * 0.03 - t * 22), 0.7, ang=ang)

# ---------- 1: Hook (cold open: ground already sliding) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    soft_bg(c, t)
    sl = 0.5 + 0.5 * math.sin(t * 0.8)
    fault_view(c, t, bend=0.0, slip=0.25 * sl, D=120, arrows=1.0)
    label_pill(c, 'moving RIGHT NOW', 540, 690, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'as fast as NAILS grow', 540, 1580, size=42, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi='#2f9bff')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 2: Plates like a cracked eggshell ----------
CRACKS = [[(-0.95, -0.2), (-0.5, -0.1), (-0.2, -0.35), (0.25, -0.25), (0.6, -0.5), (0.8, -0.6)],
          [(-0.2, -0.35), (-0.1, 0.1), (-0.3, 0.5), (-0.2, 0.97)],
          [(0.25, -0.25), (0.35, 0.2), (0.75, 0.35), (0.98, 0.15)],
          [(-0.1, 0.1), (0.35, 0.2)], [(-0.6, -0.8), (-0.5, -0.1)]]

def cracks(c, x, y, r, k, colr='#ffd23f', w=9):
    for line in CRACKS:
        p = skia.Path(); n = len(line)
        m = max(2, int(n * k + 0.999)) if k > 0 else 0
        for i, (px, py) in enumerate(line[:m]):
            (p.moveTo if i == 0 else p.lineTo)(x + px * r, y + py * r)
        if m: c.drawPath(p, P(color=col(colr), stroke=w))

def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    r = 330
    c.save(); cl = skia.Path(); cl.addCircle(540, 1130, r); c.clipPath(cl, doAntiAlias=True)
    earth(c, 540, 1130, r, t, rot=t * 0.02, face_on=False)
    cracks(c, 540, 1130, r, ease_in_out(prog(t, t0 + 0.5, 1.6)))
    c.restore()
    label_pill(c, 'TECTONIC plates', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        ek = ease_back(prog(t, t1 + 0.3, 0.5))
        if ek > 0:
            c.save(); c.translate(790, 1520); c.scale(ek, ek)
            c.drawOval(skia.Rect(-85, -110, 85, 110), rad(-30, -40, 160, [col('#ffffff'), col('#f1e6d2')]))
            cracks(c, 0, 0, 80, 1.0, colr='#b08a5e', w=5)
            c.drawOval(skia.Rect(-85, -110, 85, 110), P(color=col('#c9b48a'), stroke=4))
            c.restore()
            label_pill(c, 'like an EGGSHELL', 380, 1560, size=40, k=ek, fill=NAVY, hi='#b08a3e')

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.5, 'whoosh'), (t0 + 1.4, 'pop'), (t1 + 0.3, 'pop')]

# ---------- 3: Heat keeps plates sliding, a few cm per year ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#e9f4ff', bot='#d6ebff')
    ys = 900
    # mantle
    c.drawRect(skia.Rect(0, ys + 90, W, H), lin(c, (0, ys, 0, H), [col('#ff9a4d'), col('#e2502a')]))
    # convection loops
    hk = ease_out(prog(t, t0 + 0.4, 0.8))
    for cx, d in ((290, 1), (790, -1)):
        a0 = (t * 60 * d) % 360
        curved_arrow(c, cx, 1300, 170, a0, a0 + 250 * d if d > 0 else a0 - 250, colr='#ffe0b0', w=14, alpha=int(230 * hk))
    # plates (two slabs moving apart)
    mv = 30 * math.sin(t * 0.7) + (t - t0) * 6
    for xa, xb, d in ((-40, 535, -1), (545, W + 40, 1)):
        dx = d * min(60, max(0, mv))
        c.drawRoundRect(skia.Rect(xa + dx, ys, xb + dx, ys + 100), 18, 18, lin(c, (0, ys, 0, ys + 100), [col('#d9a06b'), col('#a7653a')]))
        c.drawRect(skia.Rect(xa + dx, ys - 18, xb + dx, ys + 6), P(color=col('#6fbf4f')))
    label_pill(c, 'HEAT from inside', 540, 1520, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        arrow(c, 380, 820, 180, 820, colr=NAVY, w=14); arrow(c, 700, 820, 900, 820, colr=NAVY, w=14)
        label_pill(c, 'a few CM per year', 540, 700, size=44, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi='#2f9bff')

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.3, 'pop')]

# ---------- 4: Stuck at the fault -> rock bends, stores energy ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    bend = ease_in_out(prog(t, t0 + 0.8, t1 - t0 + 2.0))
    fault_view(c, t, bend=bend, slip=0.0, D=130, arrows=ease_out(prog(t, t0 + 0.3, 0.5)))
    label_pill(c, 'STUCK', 540, 700, size=50, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        # energy meter
        ek = prog(t, t1, 0.4)
        x0, x1, y = 260, 820, 1580
        c.drawRoundRect(skia.Rect(x0, y - 26, x1, y + 26), 26, 26, P(color=col('#ffffff', int(220 * ek))))
        c.drawRoundRect(skia.Rect(x0, y - 26, x0 + (x1 - x0) * bend, y + 26), 26, 26, lin(c, (x0, 0, x1, 0), [col('#ffd23f'), col(HOT)]))
        c.drawRoundRect(skia.Rect(x0, y - 26, x1, y + 26), 26, 26, P(color=col(NAVY, int(200 * ek)), stroke=5))
        label_pill(c, 'ENERGY', 540, 1500, size=40, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.6, 'pop'), (t1 + 0.2, 'pop')]

# ---------- 5: Snap! (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    ts = t0 + 1.6
    slip = ease_out(prog(t, ts, 0.35))
    jit = 6 * math.sin(t * 60) * (1 - prog(t, ts, 1.2)) if t > ts else 0
    c.save(); c.translate(jit, 0)
    fault_view(c, t, bend=1.0, slip=slip, D=130, flash=max(0, 1 - prog(t, ts, 1.0)) if t > ts else 0)
    c.restore()
    label_pill(c, 'SNAP', 540, 700, size=60, k=ease_back(prog(t, ts, 0.4), 2.4), fill=NAVY, hi='#ff5c85')
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.4, 0.5), 2.2)
        c.save(); c.translate(540, 1580); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-260, -60, 260, 60), 30, 30, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-260, -60, 260, 60), 30, 30, P(color=col(NAVY), stroke=6))
        text_block(c, 'EARTHQUAKE', 0, 0, size=58, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 1.6, 'whoosh'), (t0 + 1.65, 'boing'), (t1 + 0.4, 'ding')]

# ---------- 6: Seismic waves like ripples ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#e9f4ff', bot='#d6ebff')
    ys = 980
    shake = 0.0
    if t > t1:
        shake = min(1, (t - t1) * 2) * (1 - prog(t, t1 + 2.6, 0.8))
    cross_section(c, t, ysurf=ys, shake=shake)
    fx, fy = 540, 1420
    c.save(); cl = skia.Path(); cl.addRect(skia.Rect(0, ys + 30, W, H)); c.clipPath(cl, doAntiAlias=True)
    for k in range(6):
        tt = (t - t0 - 0.3 - k * 0.45)
        if tt < 0: continue
        r = (tt * 380) % 900
        c.drawCircle(fx, fy, r, P(color=col('#ffffff', int(220 * max(0, 1 - r / 900))), stroke=10))
    c.restore()
    c.save(); c.translate(fx, fy); c.drawPath(star_path(34), P(color=col('#ffd23f'))); c.drawPath(star_path(34), P(color=col(NAVY), stroke=4)); c.restore()
    label_pill(c, 'SEISMIC waves', 540, 1620 - 40, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'the SHAKING', 540, 760, size=46, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 0.3, 'pop')]

# ---------- 7: Wild part: ~500,000 detectable quakes a year ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#f1ecff', bot='#e1ebff')
    # seismograph paper
    x0, x1, yc = 100, 980, 1180
    c.drawRoundRect(skia.Rect(x0, 960, x1, 1400), 30, 30, P(color=col('#ffffff')))
    for k in range(1, 6):
        c.drawLine(x0 + 10, 960 + k * 73, x1 - 10, 960 + k * 73, P(color=col('#cfe0f5'), stroke=2))
    pen = 820
    p = skia.Path(); first = True
    rnd = random.Random(5)
    spikes = {rnd.randint(0, 220): rnd.uniform(0.3, 1.0) for _ in range(9)}
    for i in range(0, 221):
        x = pen - (220 - i) * 3.2
        if x < x0 + 10: continue
        idx = i + int(t * 40)
        a = 6 + 4 * math.sin(idx * 1.7)
        big = spikes.get(idx % 221, 0)
        y = yc + math.sin(idx * 2.3) * a + (math.sin(idx * 3.1) * 140 * big if big else 0)
        (p.moveTo if first else p.lineTo)(x, y); first = False
    c.drawPath(p, P(color=col(NAVY), stroke=4))
    c.drawCircle(pen, yc, 12, P(color=col('#ff5c85')))
    c.drawRoundRect(skia.Rect(x0, 960, x1, 1400), 30, 30, P(color=col(NAVY), stroke=6))
    n = int(500000 * ease_out(prog(t, t0 + 1.0, 2.4)))
    kk = ease_back(prog(t, t0 + 1.0, 0.4))
    if kk > 0:
        c.save(); c.translate(540, 800); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-300, -70, 300, 70), 35, 35, P(color=col('#ffffff', 240)))
        text_block(c, f'{n:,}', 0, -4, size=80, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'per YEAR', 540, 1490, size=44, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi='#9b4dff')
    if t > t1:
        label_pill(c, 'most too SMALL to feel', 540, 1590, size=42, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi='#2f9bff')

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.0, 'pop'), (t0 + 1.2, 'click'), (t0 + 2.4, 'pop'), (t1 + 0.5, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    soft_bg(c, t)
    fault_view(c, t, bend=0.0, slip=1.0, D=110, y0=820, y1=1420)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: the MOON by day', 540, 700, size=46, k=kk, fill=NAVY, hi='#2f9bff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do earthquakes happen?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do earthquakes happen?', 'How do EARTHQUAKES happen?'),
            ('The ground under you is moving right now, about as fast as your fingernails grow.', 'The ground is MOVING right now')], tail=0.8),
        dict(name='plates', draw=s2, sfx_fn=s2_sfx, ambience='space', lines=[
            ("Earth's outer shell is broken into giant pieces called tectonic plates,", 'Giant pieces: tectonic PLATES'),
            ('like the cracked shell of a boiled egg.', 'Like a cracked EGGSHELL')], tail=0.8),
        dict(name='moving', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Heat from deep inside the Earth keeps those plates slowly sliding,', 'HEAT keeps them sliding'),
            ('a few centimeters every year.', 'A few CENTIMETERS a year')], tail=0.8),
        dict(name='stuck', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Where two plates meet, at a fault, their rough edges get stuck.', 'At a FAULT, edges get stuck'),
            ('The plates keep pushing, so the rock slowly bends and stores energy, like a bending ruler.', 'The rock BENDS and stores energy')], tail=0.8),
        dict(name='snap', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('Eventually, the friction gives way, and the rock snaps into place in seconds.', 'Then it SNAPS'),
            ("All that stored energy is released at once. That's an earthquake.", "That's an EARTHQUAKE")], tail=1.2),
        dict(name='waves', draw=s6, sfx_fn=s6_sfx, lines=[
            ('The energy races through the ground as seismic waves, like ripples on a pond,', 'Waves, like RIPPLES on a pond'),
            ("and that is the shaking we feel.", "That's the SHAKING we feel")], tail=0.8),
        dict(name='count', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: instruments pick up around half a million earthquakes every year.", 'HALF A MILLION a year'),
            ('Most of them are far too small for anyone to feel.', 'Most are too SMALL to feel')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So an earthquake is stuck rock suddenly slipping and letting its energy go.', 'Stuck rock suddenly SLIPS'),
            ('Next up: why we can sometimes see the Moon during the day.', 'Next: the MOON in daylight'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
