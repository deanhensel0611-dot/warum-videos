"""Episode 23 (EN, general audience): What makes the wind blow?
Facts checked (NOAA/NWS education pages, Fox Weather "What makes wind", standard meteorology texts):
- The Sun heats Earth's surface unevenly; land heats (and cools) faster than water.
- Warm air expands, becomes less dense and rises; this leaves lower pressure at the surface. Cooler, denser air
  flows in from higher pressure -> wind. Air flows from high to low pressure.
- Sea breeze: on sunny days wind blows from sea to land; at night land cools faster -> land breeze (reversed).
- Globally the warm equator and cold poles drive large circulations; Earth's rotation deflects winds
  (Coriolis effect), which is why large storms rotate.
- Jet streams: fast winds near the top of the troposphere (~5-9 miles / 9-14 km up); speeds can exceed
  200 mph (up to ~275 mph). Eastbound flights use them as a tailwind and arrive earlier.
- Sun is ~93 million miles (150 million km) from Earth.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SPLIT = 470      # sea on the left, land on the right
GROUND = 1260

def beach(c, t, heat=0.0, night=0.0, sun_on=True, sun_y=760):
    top = mix_hx('#2f9bff', '#0f1838', night); bot = mix_hx('#cdeeff', '#2c3566', night)
    sky(c, top, bot)
    if night > 0.05:
        stars(c, t, seed=8, n=60, y1=1100, a=night)
    if sun_on and night < 0.95:
        sy = lerp(sun_y, 1500, night)
        sun(c, 230, sy, 70, t)
    water_body(c, GROUND + 20, t, x0=-20, x1=W + 20, y1=H, c1=mix_hx('#4fb3ff', '#1d3f7a', night), c2=mix_hx('#1a5fc9', '#0d1f45', night))
    p = skia.Path(); p.moveTo(SPLIT - 150, H + 10)
    p.cubicTo(SPLIT - 70, GROUND + 200, SPLIT - 10, GROUND - 6, SPLIT + 140, GROUND - 16)
    p.cubicTo(SPLIT + 300, GROUND - 24, W - 200, GROUND - 40, W + 20, GROUND - 34); p.lineTo(W + 20, H + 10); p.close()
    sand_hot = mix_hx('#ffd98a', '#ffb35c', heat)
    c.drawPath(p, lin(c, (0, GROUND - 30, 0, H), [col(mix_hx(sand_hot, '#5a4a3a', night * 0.7)), col(mix_hx('#e0a85a', '#3a2e24', night * 0.7))]))
    # wet-sand edge + dune ripples for texture
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawPath(p, P(color=col(mix_hx('#c98a4a', '#2a2018', night * 0.7), 160), stroke=26))
    rnd = random.Random(3)
    for i in range(14):
        x = rnd.uniform(SPLIT, W); y = rnd.uniform(GROUND + 40, H - 80); w_ = rnd.uniform(50, 110)
        arc = skia.Path(); arc.moveTo(x - w_, y); arc.quadTo(x, y - 18, x + w_, y)
        c.drawPath(arc, P(color=col(mix_hx('#d9984a', '#2a2018', night * 0.7), 150), stroke=6))
    c.restore()
    c.drawPath(p, P(color=col(mix_hx('#b87a3a', '#1a140f', night * 0.7)), stroke=4))
    if heat > 0.02:   # heat shimmer over the sand
        for i in range(6):
            x = SPLIT + 120 + i * 95
            pp = skia.Path(); pp.moveTo(x, GROUND - 40)
            for k in range(1, 9):
                pp.lineTo(x + math.sin(t * 5 + k * 1.2 + i) * 10, GROUND - 40 - k * 22)
            c.drawPath(pp, P(color=col('#ff9f1c', int(150 * heat)), stroke=6))

def balloon(c, x, y, s, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    env = skia.Path(); env.moveTo(0, 120); env.cubicTo(-150, 20, -130, -170, 0, -170); env.cubicTo(130, -170, 150, 20, 0, 120); env.close()
    c.drawPath(env, lin(c, (-130, 0, 130, 0), [col('#ff8aa6', a), col('#ff5c85', a), col('#d63e66', a)], vertical=False))
    c.save(); c.clipPath(env, doAntiAlias=True)
    for sx in (-60, 0, 60):
        c.drawRect(skia.Rect(sx - 14, -180, sx + 14, 130), P(color=col('#ffd23f', a)))
    c.restore()
    c.drawPath(env, P(color=col('#8a1530', a), stroke=4))
    for sx in (-30, 30): c.drawLine(sx * 0.6, 118, sx, 170, P(color=col(NAVY, a), stroke=4))
    c.drawRoundRect(skia.Rect(-34, 165, 34, 215), 8, 8, P(color=col('#a8683a', a)))
    c.restore()

def loop_flow(c, t, k=1.0, colr='#ffffff', alpha=230, x_up=820, x_down=230, y_top=820, y_low=1180, n=7, speed=0.12):
    """Circulation cell drawn as a rounded loop with moving chevrons. Runs up over x_up, across the top, down over x_down, back along the ground."""
    if k <= 0: return
    p = skia.Path(); r = 90
    p.moveTo(x_down + r, y_low); p.lineTo(x_up - r, y_low); p.quadTo(x_up, y_low, x_up, y_low - r)
    p.lineTo(x_up, y_top + r); p.quadTo(x_up, y_top, x_up - r, y_top)
    p.lineTo(x_down + r, y_top); p.quadTo(x_down, y_top, x_down, y_top + r)
    p.lineTo(x_down, y_low - r); p.quadTo(x_down, y_low, x_down + r, y_low)
    if x_up < x_down:
        pass
    meas = skia.PathMeasure(p, False); L = meas.getLength()
    seg = skia.Path(); meas.getSegment(0, L * k, seg, True)
    c.drawPath(seg, P(color=col(colr, int(alpha * 0.45)), stroke=14))
    if k >= 1:
        for i in range(n):
            u = (t * speed + i / n) % 1.0
            pos, tan = meas.getPosTan(L * u)
            ang = math.atan2(tan.y(), tan.x()); x, y = pos.x(), pos.y()
            ch = skia.Path(); s_ = 26
            ch.moveTo(x - math.cos(ang) * s_ - math.sin(ang) * s_, y - math.sin(ang) * s_ + math.cos(ang) * s_)
            ch.lineTo(x, y)
            ch.lineTo(x - math.cos(ang) * s_ + math.sin(ang) * s_, y - math.sin(ang) * s_ - math.cos(ang) * s_)
            c.drawPath(ch, P(color=col(colr, alpha), stroke=12))

# ---------- 1: Hook (cold open: flag already whipping in the wind) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    sky(c, '#2f9bff', '#cdeeff', mid='#7cc6ff')
    clouds(c, t * 3.0, seed=3, n=4, y0=640, y1=1000, speed=60)
    hills(c, 1560, t=t, trees=False, flowers=False)
    grass_field(c, 1600, t * 1.6, seed=5, n=60, hmin=90, hmax=180, wind=1.6)
    flag(c, 300, 1500, 1.15, t, wind=0.95 + 0.05 * math.sin(t * 3))
    wind_lines(c, t, y0=700, y1=1350, n=7, speed=950, seed=2)
    # the Sun slides in with its distance
    k = ease_back(prog(t, 0.4, 0.6))
    if k > 0:
        sun(c, lerp(1250, 820, ease_out(prog(t, 0.3, 0.8))), 760, 85, t)
        label_pill(c, '93,000,000 MILES', 680, 1250, size=50, k=k, fill=NAVY, hi='#e07a00')
    if t > t1:
        label_pill(c, 'it starts at the SUN', 680, 1350, size=44, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi='#e07a00')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.4, 'pop'), (cues[1]['start'] + 0.9, 'pop')]

# ---------- 2: Uneven heating – land warms faster than water ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    heat = ease_in_out(prog(t, t0 + 0.6, 2.2))
    beach(c, t, heat=heat)
    # sunrays reaching both sides
    for i, x in enumerate((180, 330, 640, 840)):
        u = ((t * 0.9 + i * 0.27) % 1.0)
        y = lerp(860, GROUND - 30, u)
        c.drawLine(x - 30, y - 120, x, y, P(color=col('#ffd23f', int(200 * (1 - u) + 40)), stroke=10))
    thermometer(c, 230, 1520, 0.8, level=lerp(0.25, 0.38, heat), hot='#2f9bff')
    thermometer(c, 760, 1520, 0.8, level=lerp(0.25, 0.9, heat))
    label_pill(c, 'WATER', 230, 1640 - 20, size=40, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill='#1f6fc4', hi='#1f6fc4')
    label_pill(c, 'LAND', 760, 1640 - 20, size=40, k=ease_back(prog(t, t0 + 0.7, 0.4)), fill='#e07a00', hi='#e07a00')
    if t > t1:
        label_pill(c, 'HOT sand', 760, 1000, size=48, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill='#e8264f', hi='#e8264f')
        label_pill(c, 'cool WATER', 300, 1000, size=48, k=ease_back(prog(t, t1 + 1.1, 0.4)), fill='#1f6fc4', hi='#1f6fc4')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 0.7, 'pop'), (cues[1]['start'] + 0.3, 'pop'), (cues[1]['start'] + 1.1, 'pop')]

# ---------- 3: Warm air spreads out and rises -> low pressure ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    beach(c, t, heat=1.0)
    rise = ease_in_out(prog(t, t0 + 0.8, 2.6))
    spread = lerp(0.55, 1.15, ease_out(prog(t, t0 + 0.2, 1.2)))
    cy = lerp(GROUND - 150, 820, rise)
    # warm air parcel
    c.drawCircle(760, cy, 170 * spread, rad(760, cy, 170 * spread, [col('#ffb35c', 110), col('#ff9f1c', 0)]))
    air_dots(c, 640, cy - 110, 880, cy + 110, t, n=24, spread=spread, seed=4, colr='#fff3d6', r=10)
    arrow(c, 760, cy + 200, 760, cy + 90 if rise > 0.05 else cy + 200, colr='#ffffff', w=16, alpha=int(230 * min(1, rise * 4)))
    # cool dense air over the sea
    air_dots(c, 120, GROUND - 260, 380, GROUND - 60, t, n=34, spread=0.62, seed=9, colr='#d6ecff', r=10, jiggle=0.6)
    bk = ease_back(prog(t, t0 + 1.4, 0.5))
    if bk > 0:
        balloon(c, 940, lerp(1250, 900, rise), 0.42 * bk)
    if t > t1:
        label_pill(c, 'LOW pressure', 760, GROUND + 90, size=46, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill='#e8264f', hi='#e8264f')
        label_pill(c, 'HIGH pressure', 250, GROUND + 90, size=46, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill='#1f6fc4', hi='#1f6fc4')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.3, 'pop'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 4: Cool air rushes in = wind (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    beach(c, t, heat=1.0)
    go = ease_in_out(prog(t, t0 + 0.5, 1.0))
    # flag on the beach swings from limp-ish to flying landward
    flag(c, 640, GROUND - 20, 0.85, t, wind=lerp(0.5, 1.0, go))
    wind_lines(c, t, y0=GROUND - 230, y1=GROUND - 70, n=5, speed=800 * go + 1, seed=11, alpha=int(220 * go), curl=True)
    if t > t1:
        loop_flow(c, t, k=ease_in_out(prog(t, t1 + 0.2, 1.4)), x_up=860, x_down=200, y_top=780, y_low=GROUND - 150)
        label_pill(c, 'HIGH  ->  LOW', 540, 1560, size=52, k=ease_back(prog(t, t1 + 1.2, 0.5), 2.2), fill=NAVY, hi='#ff5c85')

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'whoosh'), (cues[1]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 1.2, 'ding')]

# ---------- 5: At night the breeze flips ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    nt = ease_in_out(prog(t, 0.0, 1.8))
    beach(c, t, heat=1 - nt, night=nt)
    if nt > 0.6:
        moon(c, 860, 760, 60, t, phase=0.5, face_on=False)
    flip = ease_in_out(prog(t, t1 + 0.1, 1.2))
    # flag: flying landward (right) -> limp -> flying seaward (left, mirrored)
    w = abs(1 - 2 * flip)
    c.save()
    if flip > 0.5:
        c.translate(640, 0); c.scale(-1, 1); c.translate(-640, 0)
    flag(c, 640, GROUND - 20, 0.85, t, wind=lerp(0.5, 1.0, w))
    c.restore()
    if flip > 0.5:
        wind_lines(c, t, y0=GROUND - 230, y1=GROUND - 70, n=5, speed=700, seed=12, alpha=int(220 * (flip - 0.5) * 2), direction=-1)
    thermometer(c, 230, 1520, 0.8, level=0.36, hot='#2f9bff')
    thermometer(c, 760, 1520, 0.8, level=lerp(0.9, 0.2, ease_in_out(prog(t, t0 + 0.6, 2.0))))
    if t > t1:
        label_pill(c, 'LAND breeze', 260, 1120, size=50, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi='#2f9bff')

def s5_sfx(D, cues): return [(0.1, 'whoosh'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.8, 'pop')]

# ---------- 6: Whole planet: hot equator, cold poles, spin bends winds ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    k = ease_out(prog(t, 0.0, 1.0))
    R = 330 * lerp(0.6, 1.0, k)
    ex, ey = 520, 1110
    earth(c, ex, ey, R, t, rot=t * 0.03, face_on=False)
    # warm equator band + cold caps
    hb = ease_in_out(prog(t, t0 + 0.8, 0.8))
    if hb > 0:
        c.save(); cl = skia.Path(); cl.addCircle(ex, ey, R); c.clipPath(cl, doAntiAlias=True)
        c.drawRect(skia.Rect(ex - R, ey - R * 0.22, ex + R, ey + R * 0.22), lin(c, (0, ey - R * 0.22, 0, ey + R * 0.22), [col('#ff9f1c', 0), col('#ff9f1c', int(150 * hb)), col('#ff9f1c', 0)]))
        for sy in (-1, 1):
            c.drawOval(skia.Rect(ex - R * 0.7, ey + sy * R - R * 0.25, ex + R * 0.7, ey + sy * R + R * 0.25), P(color=col('#bfe6ff', int(170 * hb))))
        c.restore()
        label_pill(c, 'HOT', ex - R - 10 + 80, ey, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill='#e07a00', hi='#e07a00')
        label_pill(c, 'COLD', ex, ey - R - 40, size=40, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill='#1f6fc4', hi='#1f6fc4')
    if t > t1:
        bk = ease_in_out(prog(t, t1 + 0.2, 1.4))
        # winds bent into curves (trade-wind-like arcs, both hemispheres)
        for sy in (-1, 1):
            for i in range(3):
                yy = ey + sy * R * (0.32 + i * 0.18)
                pth = skia.Path(); x0 = ex + R * 0.6; pth.moveTo(x0, yy - sy * 60)
                pth.quadTo(ex + R * 0.1, yy + sy * 10, ex - R * 0.55 * bk, yy + sy * 50 * bk)
                meas = skia.PathMeasure(pth, False); seg = skia.Path(); meas.getSegment(0, meas.getLength() * bk, seg, True)
                c.drawPath(seg, P(color=col('#ffffff', 220), stroke=10))
        # swirling storm
        sk = ease_back(prog(t, t1 + 1.4, 0.5))
        if sk > 0:
            c.save(); c.translate(ex + R * 0.25, ey - R * 0.5); c.rotate(-t * 120); c.scale(sk, sk)
            for j in range(3):
                c.rotate(120)
                sp = skia.Path(); sp.moveTo(0, 0)
                for q in range(1, 20):
                    a_ = q * 0.28; r_ = q * 4.2
                    sp.lineTo(math.cos(a_) * r_, math.sin(a_) * r_)
                c.drawPath(sp, P(color=col('#ffffff', 230), stroke=12))
            c.restore()
        label_pill(c, "Earth's SPIN", ex, 1560, size=48, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s6_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 1.4, 'sparkle')]

# ---------- 7: Wild part: jet streams ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#0e2a6b', '#7cc6ff', mid='#2f6fd6')
    for i in range(3): cloud(c, (i * 420 - t * 40) % 1400 - 160, 1500 + i * 40, 1.3, a=230)
    # the jet stream: a fast, wavy ribbon
    band = ease_out(prog(t, 0.1, 1.0))
    for j in range(5):
        p = skia.Path(); first = True
        for i in range(0, 61):
            x = lerp(-60, W + 60, i / 60)
            y = 1020 + j * 26 + math.sin(x * 0.006 + 1.1) * 110
            (p.moveTo if first else p.lineTo)(x, y); first = False
        meas = skia.PathMeasure(p, False); L = meas.getLength(); seg = skia.Path(); meas.getSegment(0, L * band, seg, True)
        c.drawPath(seg, P(color=col('#ffffff', 60 + j * 10), stroke=20))
        for q in range(3):
            u = (t * 0.55 + q / 3 + j * 0.07) % 1.0
            s0 = skia.Path(); meas.getSegment(L * u, L * min(1, u + 0.08), s0, True)
            c.drawPath(s0, P(color=col('#ffd23f', int(220 * band)), stroke=10))
    label_pill(c, '200+ MPH', 540, 1300, size=56, k=ease_back(prog(t, t0 + 2.4, 0.5), 2.2), fill='#e8264f', hi='#e8264f')
    label_pill(c, '~6 miles UP', 820, 760, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        u = ease_in_out(prog(t, t1, D - t1))
        x = lerp(-250, 1250, u)
        y = 1020 + 52 + math.sin(x * 0.006 + 1.1) * 110
        slope = math.degrees(math.atan(math.cos(x * 0.006 + 1.1) * 110 * 0.006))
        airplane(c, x, y - 40, 0.55, rot=slope, t=t)
        label_pill(c, 'TAILWIND', 260, 760, size=44, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi='#ff5c85')

def s7_sfx(D, cues): return [(0.1, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 2.4, 'sparkle'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 0.8, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    sky(c, '#2f9bff', '#cdeeff', mid='#7cc6ff')
    clouds(c, t * 3.0, seed=6, n=3, y0=640, y1=900, speed=50)
    sun(c, 820, 800, 80, t)
    hills(c, 1560, t=t, trees=False, flowers=False)
    flag(c, 300, 1500, 1.0, t, wind=0.95)
    wind_lines(c, t, y0=880, y1=1300, n=5, speed=850, seed=4)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        bar_magnet(c, 640, 1120, 0.7 * k, rot=-8)
        label_pill(c, 'next: MAGNETS', 640, 1000, size=48, k=k, fill=NAVY, hi='#ff5c85')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='What makes the wind blow?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('What makes the wind blow?', 'What makes the WIND blow?'),
            ('It starts ninety-three million miles away, with the Sun.', 'It starts with the SUN')], tail=0.8),
        dict(name='heating', draw=s2, sfx_fn=s2_sfx, ambience='water', lines=[
            ("The Sun doesn't heat Earth evenly. Land warms up much faster than water.", 'Land heats FASTER than water'),
            ('Think of a beach: scorching sand, cool water.', 'HOT sand, cool water')], tail=0.8),
        dict(name='rises', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Warm air spreads out and gets lighter, so it rises, like a hot-air balloon.', 'Warm air RISES'),
            ('That leaves lower pressure near the ground.', 'LOW pressure below')], tail=0.9),
        dict(name='wind', draw=s4, sfx_fn=s4_sfx, ambience='water', lines=[
            ('Cooler, heavier air from over the sea slides in to fill the gap.', 'Cool air RUSHES in'),
            ("That moving air is wind. Air always flows from high pressure to low.", 'HIGH to LOW = WIND')], tail=1.4),
        dict(name='night', draw=s5, sfx_fn=s5_sfx, lines=[
            ('At night it flips: the land cools off faster than the sea.', 'At night it FLIPS'),
            ('So the breeze blows from the land out to sea.', 'Now: a LAND breeze')], tail=1.0),
        dict(name='planet', draw=s6, sfx_fn=s6_sfx, ambience='space', lines=[
            ('Zoom out, and the whole planet does this: hot equator, cold poles.', 'Hot EQUATOR, cold poles'),
            ("Earth's spin bends those winds into curves. That's why big storms swirl.", "Earth's SPIN bends them")], tail=1.1),
        dict(name='jetstream', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: about six miles up, rivers of wind called jet streams can top two hundred miles per hour.", 'JET STREAMS: 200+ mph'),
            ('Planes flying east ride them and land early.', 'Planes RIDE them east')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So wind is sunshine, turned into moving air.', 'Wind = SUNSHINE in motion'),
            ('Next up: how magnets work.', 'Next: how MAGNETS work'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
