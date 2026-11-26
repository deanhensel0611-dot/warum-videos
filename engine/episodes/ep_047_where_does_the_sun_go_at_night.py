"""Episode 47 (EN, general audience): Where does the Sun go at night?
Facts checked (NASA Space Place "What causes day and night?"; NASA/Earth Observatory on Earth's rotation; Britannica
"Earth's rotation"; timeanddate.com "Atmospheric refraction"; Hong Kong Observatory "Effect of atmospheric refraction
on the times of sunrise and sunset"; Wikipedia "Sunset"):
- The Sun does not go anywhere: Earth spins on its axis about once every 24 hours (solar day), so each place turns
  into and out of sunlight. Night = your side faces away from the Sun; it's day on the other side.
- Earth spins toward the east (west to east), so the Sun appears to rise in the east and set in the west.
- Surface speed at the equator is about 1,670 km/h (about 1,040 mph); airliners cruise around 900 km/h.
- Atmospheric refraction near the horizon is about 34 arcminutes, a bit more than the Sun's apparent diameter
  (~32 arcminutes). So when the Sun's lower edge appears to touch the horizon at sunset, the Sun is geometrically
  already (just) below it.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def you_pin(c, x, y, k=1.0, ang=0.0, label='YOU'):
    """Coral map pin standing on a surface point; ang = outward direction in degrees (0 = up)."""
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(k, k)
    p = skia.Path(); p.moveTo(0, 0); p.cubicTo(-26, -40, -40, -60, -40, -84); p.cubicTo(-40, -112, -20, -126, 0, -126)
    p.cubicTo(20, -126, 40, -112, 40, -84); p.cubicTo(40, -60, 26, -40, 0, 0); p.close()
    c.drawPath(p, P(color=col('#000000', 60), blur=6))
    c.drawPath(p, lin(c, (0, -126, 0, 0), [col('#ff7a9a'), col('#e8264f')]))
    c.drawPath(p, P(color=col('#ffffff'), stroke=5))
    c.drawCircle(0, -86, 15, P(color=col('#ffffff')))
    c.restore()

def sunset_sky(c, k):
    """k 0 = day, 1 = dusk."""
    top = mix_hx('#2f9bff', '#2b2f78', k); mid = mix_hx('#7cc4ff', '#ff7a5c', k); bot = mix_hx('#cfe8ff', '#ffd27a', k)
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, 1500), [col(top), col(mid), col(bot)], pos=[0, 0.6, 1]))

def ground(c, y, ang=0.0, cx=540, dark=0.0):
    c.save(); c.translate(cx, y); c.rotate(ang)
    c.drawRect(skia.Rect(-1400, 0, 1400, 1600), lin(c, (0, 0, 0, 500), [col(mix_hx('#56b83a', '#1f4a2a', dark)), col(mix_hx('#3f9a2e', '#16351f', dark))]))
    c.drawLine(-1400, 0, 1400, 0, P(color=col(mix_hx('#8be26c', '#2f6a3a', dark)), stroke=10))
    for i in range(-6, 7):
        tree(c, i * 210 + 40, 4, 0.55, 0, seed=i + 9, dark=dark > 0.5)
    c.restore()

# ---------- 1: Hook (cold open: Sun already sinking) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    u = clamp(t / D)
    sunset_sky(c, 0.4 + 0.5 * u)
    sy = 1200 + 260 * ease_in_out(u)
    sun(c, 540, sy, 120, t, glow=True)
    ground(c, 1380, dark=0.3 * u)
    label_pill(c, 'where does it GO?', 540, 720, size=48, k=ease_back(prog(t, 0.2, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'NOWHERE.', 540, 720, size=64, k=ease_back(prog(t, t1 + 0.1, 0.4)), fill=NAVY, hi=HOT)
        you_pin(c, 820, 1380, ease_back(prog(t, t1 + 1.0, 0.4)))
        label_pill(c, 'YOU move', 820, 1160, size=42, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=SKYB)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.2, 'pop'), (t1 + 0.1, 'pop'), (t1 + 1.0, 'pop')]

# ---------- 2: Earth spins once a day (top view) ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    sun(c, -60, 1100, 220, t)
    for i in range(7):
        y = 860 + i * 80
        c.drawLine(180, y, 280, y, P(color=col('#fff3b0', 120), stroke=6))
    rot = -(t - t0) * 0.16
    ex, ey, er = 600, 1100, 300
    earth_top(c, ex, ey, er, t, rot=rot, sun_dir=180)
    ang = rot * 360 + 180
    px, py = ex + math.cos(math.radians(ang)) * er, ey + math.sin(math.radians(ang)) * er
    you_pin(c, px, py, 0.8, ang=ang + 90)
    curved_arrow(c, ex, ey, er + 60, 330, 210, '#ffd23f', w=12, alpha=230)
    k = ease_back(prog(t, t0 + 1.2, 0.4))
    if k > 0:
        c.save(); c.translate(600, 1580); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-200, -70, 200, 70), 36, 36, P(color=col('#ffffff', 240)))
        text_block(c, '24 HOURS', 0, -4, size=60, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'one SPIN', 600, 700, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.2, 'pop')]

# ---------- 3: Night = your side faces away; day on the other side ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    sun(c, -40, 1100, 200, t)
    ex, ey, er = 600, 1100, 290
    earth_top(c, ex, ey, er, t, rot=0.0, sun_dir=180, night=0.7)
    # pin swings from the day side (left) to the night side (right)
    ang = lerp(180, 0, ease_in_out(prog(t, t0 + 0.3, 2.2)))
    px, py = ex + math.cos(math.radians(ang)) * er, ey + math.sin(math.radians(ang)) * er
    you_pin(c, px, py, 0.8, ang=ang + 90)
    label_pill(c, 'NIGHT', 790, 760, size=48, k=ease_back(prog(t, t0 + 2.3, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'DAY over here', 400, 1540, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
        # sun rays still landing on the lit half
        for i in range(6):
            y = 880 + i * 85; ph = ((t - t1) * 1.2 + i * 0.2) % 1.0
            x = lerp(170, 310, ph)
            c.drawLine(x, y, x + 60, y, P(color=col('#fff3b0', int(220 * (1 - ph))), stroke=8))

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 2.3, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 4: You are moving fast ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    rot = (t - t0) * 0.08
    earth(c, 540, 1120, 330, t, rot=rot, face_on=False, sun_dir=180, night=0.55)
    # equator line
    c.drawOval(skia.Rect(210, 1100, 870, 1140), P(color=col('#ffd23f', 200), stroke=5))
    for i in range(5):
        ph = ((t - t0) * 0.9 + i / 5) % 1.0
        x = lerp(330, 760, ph)
        arrow(c, x, 1180, x + 60, 1180, colr='#ffffff', w=8, alpha=int(230 * math.sin(math.pi * ph)))
    n = int(1670 * ease_out(prog(t, t0 + 0.5, 1.6)))
    k = ease_back(prog(t, t0 + 0.4, 0.4))
    if k > 0:
        c.save(); c.translate(540, 700); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-250, -72, 250, 72), 40, 40, P(color=col('#ffffff', 240)))
        c.drawRoundRect(skia.Rect(-250, -72, 250, 72), 40, 40, P(color=col(HOT), stroke=6))
        text_block(c, f'{n:,} km/h', 0, -4, size=64, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    ak = ease_out(prog(t, t0 + 2.4, 0.8))
    if ak > 0:
        airplane(c, lerp(-200, 260, ak), 1420, 0.5, t=t)
        label_pill(c, 'faster than a JET', 680, 1570, size=42, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=SKYB)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 2.4, 'whoosh'), (t0 + 2.6, 'pop')]

# ---------- 5: Sunrise = your horizon tipping (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    # horizon rotates around a pivot while the Sun stays fixed
    if t < t1:
        ang = lerp(-16, 12, ease_in_out(prog(t, t0 + 0.2, 2.6)))
        dusk = 1 - prog(t, t0 + 0.2, 2.6)
    else:
        ang = lerp(12, -16, ease_in_out(prog(t, t1 + 0.2, 2.6)))
        dusk = prog(t, t1 + 0.2, 2.6)
    sunset_sky(c, 0.15 + 0.75 * dusk)
    sun(c, 760, 1300, 100, t)
    ground(c, 1330, ang=ang, cx=300, dark=0.4 * dusk)
    you_pin(c, 300, 1330, 0.9, ang=ang)
    label_pill(c, 'SUN stays put', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi=GOLD)
    if t < t1:
        label_pill(c, 'SUNRISE', 540, 820, size=50, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    else:
        label_pill(c, 'SUNSET', 540, 820, size=50, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=HOT)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.5, 'pop'), (t0 + 1.6, 'ding'), (t1 + 0.2, 'whoosh'), (t1 + 1.2, 'pop')]

# ---------- 6: Rises in the east because Earth spins east ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    sun(c, 540, 700, 80, t)
    rot = -(t - t0) * 0.12
    earth_top(c, 540, 1180, 300, t, rot=rot, sun_dir=270, night=0.65)
    # direction arrow (counter-clockwise seen from above the North Pole)
    a0 = -(t - t0) * 40
    for k in range(3):
        ang = math.radians(a0 + k * 120)
        x0, y0 = 540 + math.cos(ang) * 360, 1180 + math.sin(ang) * 360
        x1, y1 = 540 + math.cos(ang - 0.35) * 360, 1180 + math.sin(ang - 0.35) * 360
        arrow(c, x0, y0, x1, y1, colr='#ffd23f', w=12, alpha=230)
    label_pill(c, 'spins toward the EAST', 540, 1600, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'Sun rises in the EAST', 540, 840, size=40, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 2.0, 'pop')]

# ---------- 7: Wild part: the setting Sun is already below the horizon ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sunset_sky(c, 0.95)
    hy = 1150
    # seen Sun sitting on the horizon
    sun(c, 640, hy - 70, 70, t, glow=True)
    c.drawRect(skia.Rect(0, hy, W, H), lin(c, (0, hy, 0, H), [col('#2a5a3a'), col('#173524')]))
    c.drawLine(0, hy, W, hy, P(color=col('#8be26c'), stroke=6))
    # eye/observer on the left
    you_pin(c, 160, hy, 0.85)
    if t > t0 + 1.4:
        k = prog(t, t0 + 1.4, 0.6)
        # real (geometric) position: dashed circle below the horizon
        rp = P(color=col('#ffffff', int(230 * k)), stroke=6); rp.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
        c.drawCircle(640, hy + 90, 70, rp)
        label_pill(c, 'REALLY here', 640, hy + 230, size=40, k=ease_back(k), fill=NAVY, hi=HOT)
    if t > t1:
        u = ease_in_out(prog(t, t1 + 0.2, 1.4))
        p = skia.Path(); p.moveTo(640, hy + 90); p.quadTo(400, hy - 60, 160, hy - 90)
        seg = skia.Path(); m = skia.PathMeasure(p, False); m.getSegment(0, m.getLength() * u, seg, True)
        c.drawPath(seg, P(color=col('#fff3b0', 160), stroke=20, blur=6))
        c.drawPath(seg, P(color=col('#ffffff'), stroke=7))
        label_pill(c, 'air BENDS light', 420, 780, size=44, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'what you SEE', 640, hy - 230, size=40, k=ease_back(prog(t, t0 + 0.5, 0.4)) * (1 - prog(t, t1 + 0.8, 0.3)), fill=NAVY, hi=GOLD)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.5, 'pop'), (t0 + 1.4, 'sparkle'), (t1 + 0.2, 'whoosh'), (t1 + 1.0, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night_sky(c, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    earth_top(c, 540, 1120, 230 * (0.6 + 0.4 * fo), t, rot=-t * 0.1, sun_dir=180)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.4, 0.4)) * fo
    if k0 > 0: label_pill(c, 'Earth TURNS you away', 540, 700, size=46, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why we have EYEBROWS', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Where does the Sun go at night?',
    music=False, faces=False, ambience='space',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, ambience='wind', lines=[
            ('Where does the Sun go at night?', 'Where does the SUN go?'),
            ("Nowhere. It's you who moves.", "NOWHERE. You move.")], tail=1.0),
        dict(name='spin', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Earth spins like a merry-go-round, about once every twenty-four hours.', 'One SPIN every 24 hours')], tail=1.0),
        dict(name='night', draw=s3, sfx_fn=s3_sfx, lines=[
            ('When your side turns away from the Sun, you get night.', 'Facing away = NIGHT'),
            ("The Sun keeps shining. It's just daytime on the other side.", "It's DAY on the other side")], tail=1.0),
        dict(name='speed', draw=s4, sfx_fn=s4_sfx, lines=[
            ('And it spins fast. At the equator, the ground moves about sixteen hundred kilometers an hour. Faster than a jet.', 'Faster than a JET')], tail=1.0),
        dict(name='tip', draw=s5, sfx_fn=s5_sfx, trans='punch', ambience='wind', lines=[
            ('So a sunrise is really your horizon tipping down,', 'SUNRISE: your ground tips down'),
            ('and a sunset is it tipping up, in front of the Sun.', 'SUNSET: it tips up')], tail=1.0),
        dict(name='east', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Earth spins toward the east. That is why the Sun always rises in the east.', 'Rises in the EAST')], tail=1.0),
        dict(name='refraction', draw=s7, sfx_fn=s7_sfx, ambience='wind', lines=[
            ("Here's the wild part: when the setting Sun touches the horizon, it's already below it.", 'It is already BELOW'),
            ('The air bends its light over the edge to your eyes.', 'Air BENDS the light to you')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ("So the Sun doesn't go anywhere. Earth turns you away from it.", 'Earth TURNS you away'),
            ('Next: why we have eyebrows.', 'Next: why we have EYEBROWS'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
