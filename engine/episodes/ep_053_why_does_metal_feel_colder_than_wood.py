"""Episode 53 (EN, general audience): Why does metal feel colder than wood?
Facts checked (HyperPhysics "Steel and wood at zero Celsius"; University of Illinois Physics Van "Cold metal" and "Why do
metals feel cold or hot to the touch?"; IFLScience "Why does metal feel colder than wood even when it's actually the same
temperature"; APS "Getting warmer, getting colder"):
- Objects left in the same room reach the same (room) temperature; a thermometer reads the same on metal and wood.
- Skin is warmer than room air (skin surface roughly 90 F / 32-34 C), so heat flows from the finger into the object.
- Metals conduct heat far better than wood (steel ~15-50 W/m*K, aluminium ~200, wood ~0.1-0.2: hundreds to thousands of
  times more), so metal keeps pulling heat out of the skin quickly; wood lets the contact spot warm up and the heat
  flow drops.
- Our thermoreceptors respond to the skin's temperature / rate of heat loss, not to the object's temperature.
- Same reason an ice cube melts faster on a metal block than on a wooden/plastic one at room temperature: metal
  delivers heat to the ice faster (classic demo).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
HEAT = '#ff7a3c'

def table(c, t, y=1330):
    sky(c, '#d8efff', '#9fd0ff')
    c.drawRect(skia.Rect(0, y, W, H), lin(c, (0, y, 0, H), [col('#f4f7fb'), col('#c9d6e6')]))
    c.drawLine(0, y, W, y, P(color=col(NAVY, 70), stroke=4))

def heat_stream(c, x0, y0, x1, y1, t, rate, n=10, seed=1, spread=40, alpha=1.0):
    """heat dots travelling from (x0,y0) to (x1,y1); rate = speed factor (0 = none)."""
    if rate <= 0 or alpha <= 0: return
    rnd = random.Random(seed)
    for i in range(n):
        ph = (t * 0.6 * rate + i / n) % 1.0
        ox = rnd.uniform(-spread, spread)
        heat_dot(c, lerp(x0 + ox, x1 + ox * 2.5, ph), lerp(y0, y1, ph), 9, alpha=int(235 * alpha * math.sin(ph * math.pi)), colr=HEAT)

# ---------- 1: Hook (cold open: finger already on the metal) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    table(c, t)
    slab(c, 120, 1250, 360, 110, 'metal')
    slab(c, 600, 1250, 360, 110, 'wood')
    tap = 1 - ease_in_out(prog(t, 2.2, 0.6))
    fingertip(c, 330, 1225 - 40 * (1 - tap), 0.9, cold=ease_out(prog(t, 0.2, 1.0)) * tap)
    label_pill(c, 'METAL: cold!', 300, 720, size=46, k=ease_back(prog(t, 0.4, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'WOOD: fine', 780, 720, size=46, k=ease_back(prog(t, 1.0, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        label_pill(c, 'SAME temperature', 540, 1560, size=50, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.2, 'click'), (0.4, 'pop'), (1.0, 'pop'), (t1 + 1.2, 'pop')]

# ---------- 2: Thermometers read the same ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    table(c, t)
    slab(c, 120, 1250, 360, 110, 'metal')
    slab(c, 600, 1250, 360, 110, 'wood')
    lev = 0.5 * ease_out(prog(t, t0 + 0.6, 1.2))
    for i, x in enumerate((330, 810)):
        k = ease_back(prog(t, t0 + 0.1 + i * 0.3, 0.5))
        if k > 0: thermometer(c, x, 1170, 1.4 * k, level=lev, hot=HOT)
        label_pill(c, '~70°F', x, 1560, size=46, k=ease_back(prog(t, t0 + 1.8 + i * 0.3, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.1, 'pop'), (t0 + 0.4, 'pop'), (t0 + 0.6, 'whoosh'), (t0 + 1.8, 'click'), (t0 + 2.1, 'click')]

# ---------- 3: Your skin is warmer -> heat flows out ----------
def s3(c, t, D, cues):
    t0 = cues[0]['start']
    table(c, t, y=1400)
    slab(c, 200, 1320, 680, 160, 'metal')
    fingertip(c, 540, 1300, 1.6, fade_top=640)
    # warm glow in the fingertip
    c.drawCircle(540, 1170, 120, rad(540, 1170, 120, [col(HEAT, 110), col(HEAT, 0)]))
    label_pill(c, 'skin ~90°F', 260, 760, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    hk = prog(t, t0 + 2.0, 0.6)
    heat_stream(c, 540, 1200, 540, 1460, t, 1.0, n=10, alpha=hk)
    label_pill(c, 'HEAT flows out', 540, 1590, size=46, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=HEAT)

def s3_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.8, 'pop'), (t0 + 2.0, 'whoosh'), (t0 + 2.4, 'pop')]

# ---------- 4: Metal pulls heat away fast (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    table(c, t, y=1400)
    slab(c, 120, 1320, 840, 160, 'metal')
    fingertip(c, 540, 1300, 1.6, cold=ease_out(prog(t, t0 + 1.0, 2.0)) * 0.9, fade_top=640)
    rate = 1.0 + 2.5 * ease_in_out(prog(t, t0 + 0.6, 1.0))
    # heat spreading sideways through the metal
    rnd = random.Random(3)
    for i in range(22):
        ph = (t * 0.5 * rate + i / 22) % 1.0
        side = -1 if i % 2 else 1
        x = 540 + side * ph * rnd.uniform(250, 400); y = 1330 + ph * rnd.uniform(20, 110)
        heat_dot(c, x, y, 8, alpha=int(230 * math.sin(ph * math.pi) * prog(t, t0 + 0.4, 0.4)), colr=HEAT)
    label_pill(c, 'METAL moves heat FAST', 540, 740, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HEAT)
    if t > t1:
        label_pill(c, '100s of times faster than wood', 540, 1590, size=38, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'whoosh'), (t0 + 0.8, 'ding'), (t1 + 0.6, 'pop')]

# ---------- 5: Wood keeps the heat where it is ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    table(c, t, y=1400)
    slab(c, 120, 1320, 840, 160, 'wood')
    fingertip(c, 540, 1300, 1.6, fade_top=640)
    wk = ease_in_out(prog(t, t0 + 0.8, 2.0))
    # warm spot under the finger
    c.drawOval(skia.Rect(540 - 170, 1300, 540 + 170, 1360), P(color=col(HEAT, int(160 * wk)), blur=18))
    slow = 1 - 0.85 * wk
    heat_stream(c, 540, 1240, 540, 1330, t, 0.6 * slow + 0.05, n=5, spread=30, alpha=0.4 + 0.6 * slow)
    label_pill(c, 'WOOD: poor conductor', 540, 740, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        label_pill(c, 'the spot WARMS UP', 540, 1590, size=44, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=HEAT)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 6: Nerves feel heat loss, not the object ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#7cc4ff')
    fingertip(c, 540, 1180, 1.5, fade_top=640)
    # nerve endings
    nk = ease_out(prog(t, t0 + 0.4, 1.0))
    for i, dx in enumerate((-50, 0, 50)):
        p = skia.Path(); p.moveTo(540 + dx * 0.5, 900); p.cubicTo(540 + dx, 1000, 540 + dx * 1.3, 1080, 540 + dx * 0.9, 1100 + 40 * nk)
        c.drawPath(p, P(color=col('#ffd23f', int(230 * nk)), stroke=7))
        sp = ((t - t0) * 0.8 + i * 0.3) % 1.0
        if nk > 0.5: c.drawCircle(540 + dx * 0.5 * (1 - sp) + dx * 0.9 * sp, lerp(1140, 900, sp), 10, P(color=col('#ffffff')))
    label_pill(c, 'NERVES', 300, 980, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        gk = ease_back(prog(t, t1 + 0.2, 0.4))
        gauge(c, 300, 1450, 120 * gk, 0.9 * ease_out(prog(t, t1 + 0.4, 1.0)), label='metal', accent=SKYB)
        gauge(c, 780, 1450, 120 * gk, 0.25 * ease_out(prog(t, t1 + 0.4, 1.0)), label='wood', accent=GOLD)
        label_pill(c, 'HEAT LOSS', 540, 730, size=50, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'sparkle'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.9, 'pop')]

# ---------- 7: Wild part: ice melts faster on metal ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    table(c, t)
    slab(c, 120, 1250, 360, 110, 'metal')
    slab(c, 600, 1250, 360, 110, 'wood')
    m = prog(t, t0 + 0.8, D - t0 - 1.0)
    for x, speed, i in ((330, 1.0, 0), (810, 0.25, 1)):
        melt = clamp(m * speed * 1.15)
        pr = 60 + 110 * melt
        c.drawOval(skia.Rect(x - pr, 1215 - 16, x + pr, 1215 + 14), P(color=col('#8fd0f7', 200)))
        s = 0.9 * (1 - 0.65 * melt)
        ice_cube(c, x - 10, 1215 - 100 * s, s, t, face_on=False)
    label_pill(c, 'ICE on both', 540, 720, size=48, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'METAL melts it faster', 540, 1560, size=46, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.8, 'sparkle'), (t1 + 0.3, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    table(c, t)
    slab(c, 120, 1250, 360, 110, 'metal')
    slab(c, 600, 1250, 360, 110, 'wood')
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'metal STEALS heat fast', 540, 700, size=46, k=k0, fill=NAVY, hi=HEAT)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why SALT melts ice', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
        ice_cube(c, 540, 1010, 0.5 * kk, t, face_on=False)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why does metal feel colder than wood?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why does metal feel colder than wood?', 'Why does METAL feel colder?'),
            ("Here's the twist: in the same room, they're the same temperature.", 'Same TEMPERATURE')], tail=0.9),
        dict(name='thermo', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Stick a thermometer on each, and both read the same, about seventy degrees.', 'Both read ~70°F')], tail=1.35),
        dict(name='skin', draw=s3, sfx_fn=s3_sfx, lines=[
            ('But your skin is warmer, around ninety degrees. So when you touch either one, heat flows out of your finger.', 'Heat flows OUT of you')], tail=1.35),
        dict(name='metal', draw=s4, sfx_fn=s4_sfx, trans='punch', lines=[
            ('Metal is great at moving heat. It pulls it away and spreads it out,', 'Metal pulls heat AWAY'),
            ('hundreds of times faster than wood.', '100s of times FASTER')], tail=1.0),
        dict(name='wood', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Wood is a poor conductor.', 'Wood: poor CONDUCTOR'),
            ('The spot under your finger warms up, and the heat flow almost stops.', 'The heat flow STOPS')], tail=1.35),
        dict(name='nerves', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Your nerves don't measure the object's temperature.", "Nerves don't measure OBJECTS"),
            ("They feel how fast you're losing heat.", 'They feel HEAT LOSS')], tail=1.1),
        dict(name='ice', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: put ice on both, and it melts faster on the metal.", 'Ice melts faster on METAL'),
            ('Same reason: metal delivers heat faster.', 'Metal moves heat FASTER')], tail=1.6),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So metal feels cold because it steals your heat fast.', 'Metal STEALS heat fast'),
            ('Next: why salt melts ice.', 'Next: why SALT melts ice'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
