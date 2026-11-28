"""Episode 56 (EN, general audience): How do rockets move in empty space?
Facts checked (NASA Glenn "Rocket Principles" and "Rocket Thrust"; Live Science "How do space rockets work without
air?"; Smithsonian Air and Space "Ask an Explainer"; Discover "Yes, rockets can fly in a vacuum"):
- Rockets work by Newton's third law: the engine pushes exhaust gas out the back at high speed, and the gas pushes
  the rocket forward. They don't need air to push against.
- A loose, untied balloon is the standard analogy (air out one way, balloon goes the other).
- Exhaust leaves at thousands of metres per second (roughly 2.5-4.5 km/s, i.e. several thousand mph).
- Burning needs an oxidizer; with no air in space, rockets carry their own (e.g. liquid oxygen tanks; solid motors
  have it mixed in).
- With nothing to slow it (no air drag), a coasting spacecraft keeps moving after the engine stops (Newton's first law).
- Rocket engines produce more thrust in vacuum than at sea level, because the surrounding air pressure pushes back
  on the nozzle exit (thrust = mdot*ve + (pe - pa)*Ae; pa = 0 in space).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
FIRE = '#ff9a3c'

def star_stream(c, t, speed=1.0, seed=3, n=60, dirx=0.0, diry=1.0):
    """Streaking stars that suggest motion (move along (dirx, diry))."""
    rnd = random.Random(seed)
    for i in range(n):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H); v = rnd.uniform(200, 700) * speed; r = rnd.uniform(1.5, 4)
        x = (x0 + dirx * v * t) % W; y = (y0 + diry * v * t) % H
        L = min(80, v * 0.06)
        if L > 4:
            c.drawLine(x, y, x - dirx * L, y - diry * L, P(color=col('#ffffff', 120), stroke=r))
        c.drawCircle(x, y, r, P(color=col('#ffffff', 220)))

def gas_puffs(c, x, y, t, dirx, diry, k=1.0, n=14, spread=40, speed=900, colr='#ffd23f', r0=12, seed=2, hot=True):
    """Exhaust particles leaving (x, y) along (dirx, diry)."""
    if k <= 0: return
    rnd = random.Random(seed)
    for i in range(n):
        ph = (t * speed / 600 + i / n) % 1.0
        off = rnd.uniform(-1, 1) * spread * (0.3 + ph)
        px = x + dirx * ph * 600 - diry * off; py = y + diry * ph * 600 + dirx * off
        a = int(230 * k * (1 - ph))
        cc = mix_hx(colr, '#ff5c3c', ph) if hot else colr
        c.drawCircle(px, py, r0 * (0.7 + ph), P(color=col(cc, a)))

# ---------- 1: Hook (cold open: rocket already firing in space) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    space(c, t)
    star_stream(c, t, 0.8)
    rocket(c, 540 + math.sin(t * 1.3) * 10, 1050, 0.85, math.sin(t * 0.9) * 2, t, flame=1.0)
    label_pill(c, 'EMPTY space', 540, 700, size=50, k=ease_back(prog(t, 0.3, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'no AIR to push on?', 540, 700, size=50, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.05, 'whoosh'), (0.3, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 2: Balloon analogy ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#d8efff', '#9fd0ff')
    clouds(c, t, seed=6, n=3, y0=700, y1=1500, a=200)
    go = t0 + 0.7
    if t < go:
        x = 300; y = 1150; squash = 0.0
        balloon(c, x, y, 120, '#ff5c85', rot=90 + math.sin(t * 4) * 3, string=False, t=t)
    else:
        u = prog(t, go, 5.5)
        x = lerp(300, 900, ease_in_out(u)) ; y = 1150 + math.sin(u * 7) * 50
        rot = 90 + math.sin(u * 10) * 10
        a_ = math.radians(rot + 90)
        nx, ny = x + math.cos(a_) * 140 * (1 - 0.45 * u), y + math.sin(a_) * 140 * (1 - 0.45 * u)
        for i in range(9):
            ph = ((t - go) * 2.5 + i / 9) % 1.0
            px = nx - ph * 260 + math.sin(i * 3) * 20 * ph; py = ny + math.sin(i * 2.1) * 50 * ph
            c.drawCircle(px, py, 14 + 26 * ph, P(color=col('#ffffff', int(200 * (1 - ph)))))
        balloon(c, x, y, 120, '#ff5c85', rot=rot, squash=u, string=False, t=t)
    ka = ease_back(prog(t, go + 0.3, 0.4))
    if ka > 0:
        arrow(c, 380, 1450, 140, 1450, colr=SKYB, w=16, alpha=int(255 * min(1, ka)))
        label_pill(c, 'AIR back', 260, 1540, size=42, k=ka, fill=NAVY, hi=SKYB)
        arrow(c, 700, 1450, 940, 1450, colr=HOT, w=16, alpha=int(255 * min(1, ka)))
        label_pill(c, 'BALLOON forward', 800, 1540, size=42, k=ease_back(prog(t, go + 0.7, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 1.0, 'whoosh'), (t0 + 1.3, 'pop'), (t0 + 1.7, 'pop')]

# ---------- 3: Rocket blasts hot gas out ----------
def s3(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    fk = ease_out(prog(t, t0 + 0.6, 0.6))
    ck = ease_out(prog(t, t0 + 0.2, 0.6))
    rocket(c, 540, 980, 0.95, 0, t, flame=fk, cut=ck)
    gas_puffs(c, 540, 1300, t, 0, 1, k=fk, n=16, spread=60, speed=1400, r0=14)
    label_pill(c, 'FUEL burns', 230, 900, size=42, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'HOT GAS out', 840, 1430, size=44, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'thousands of MPH', 840, 1530, size=36, k=ease_back(prog(t, t0 + 3.2, 0.4)), fill=NAVY, hi=FIRE)

def s3_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'click'), (t0 + 0.6, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 1.8, 'pop'), (t0 + 3.2, 'pop')]

# ---------- 4: Action / reaction (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t)
    star_stream(c, t, 0.5 * prog(t, t0 + 1.0, 1.0))
    rise = 60 * ease_in_out(prog(t, t0 + 1.0, D - t0 - 1.0))
    rocket(c, 540, 1050 - rise, 0.8, 0, t, flame=1.0)
    gk = ease_back(prog(t, t0 + 0.4, 0.4))
    if gk > 0:
        arrow(c, 820, 1150, 820, 1150 + 340 * min(1, gk), colr=FIRE, w=22)
        label_pill(c, 'GAS pushed back', 820, 1560, size=42, k=gk, fill=NAVY, hi=FIRE)
    rk = ease_back(prog(t, t0 + 1.2, 0.4))
    if rk > 0:
        arrow(c, 260, 1300, 260, 1300 - 420 * min(1, rk), colr=SKYB, w=22)
        label_pill(c, 'ROCKET pushed forward', 300, 790, size=40, k=rk, fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, "NEWTON'S 3rd law", 540, 690, size=46, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'whoosh'), (t0 + 1.2, 'ding'), (t1 + 0.3, 'pop')]

# ---------- 5: Bring your own oxygen ----------
def s5(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    ck = ease_out(prog(t, t0 + 0.3, 0.6))
    rocket(c, 540, 1000, 1.05, 0, t, flame=0.6, cut=ck)
    ka = ease_back(prog(t, t0 + 1.4, 0.4)); kb = ease_back(prog(t, t0 + 2.2, 0.4))
    if ka > 0:
        arrow(c, 320, 860, 470, 890, colr='#ffffff', w=10, alpha=int(230 * min(1, ka)))
        label_pill(c, 'FUEL', 230, 850, size=46, k=ka, fill=NAVY, hi=GOLD)
    if kb > 0:
        arrow(c, 780, 1080, 620, 1060, colr='#ffffff', w=10, alpha=int(230 * min(1, kb)))
        label_pill(c, 'OXYGEN', 860, 1090, size=46, k=kb, fill=NAVY, hi=SKYB)
    label_pill(c, 'no air = BRING your own', 540, 1580, size=40, k=ease_back(prog(t, t0 + 3.0, 0.4)), fill=NAVY, hi=HOT)

def s5_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.3, 'click'), (t0 + 1.4, 'pop'), (t0 + 2.2, 'pop'), (t0 + 3.0, 'pop')]

# ---------- 6: Engine off -> it keeps coasting ----------
def s6(c, t, D, cues):
    t0 = cues[0]['start']
    space(c, t)
    off = prog(t, t0 + 0.9, 0.4)
    x = lerp(150, 950, prog(t, 0, D))
    rocket(c, x, 1150, 0.55, 90, t, flame=1 - off)
    # equally spaced ghost positions (constant speed)
    for i in range(1, 3):
        gx = x - i * 400
        if gx > 40 and t > t0 + 1.4:
            rocket(c, gx, 1150, 0.55, 90, t, alpha=int(70 * (1 - i / 3) * prog(t, t0 + 1.4, 0.5)))
    label_pill(c, 'ENGINE off', 540, 760, size=48, k=ease_back(prog(t, t0 + 0.9, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'nothing SLOWS it', 540, 1500, size=48, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi=SKYB)

def s6_sfx(D, cues):
    t0 = cues[0]['start']
    return [(0.1, 'whoosh'), (t0 + 0.9, 'click'), (t0 + 2.2, 'pop')]

# ---------- 7: Wild part: stronger in space ----------
def thrust_bar(c, x, y, frac, colr, label, k=1.0):
    if k <= 0: return
    h = 320
    c.drawRoundRect(skia.Rect(x - 40, y - h, x + 40, y), 20, 20, P(color=col('#ffffff', 60)))
    hh = h * frac * k
    c.drawRoundRect(skia.Rect(x - 40, y - hh, x + 40, y), 20, 20, lin(c, (0, y - h, 0, y), [col(mix_hx(colr, '#ffffff', 0.3)), col(colr)]))
    label_pill(c, label, x, y + 60, size=34, k=k, fill=NAVY)

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    # left: launch pad in air; right: space
    c.save(); c.clipRect(skia.Rect(0, 0, W / 2, H))
    sky(c, '#2f9bff', '#cfe8ff')
    c.drawRect(skia.Rect(0, 1380, W, H), lin(c, (0, 1380, 0, H), [col('#9aa6ba'), col('#6b778c')]))
    rocket(c, 310, 980, 0.6, 0, t, flame=0.85)
    if t > t1:
        air_dots(c, 20, 640, 520, 1360, t, n=26, seed=4, r=9, alpha=int(200 * prog(t, t1 + 0.2, 0.5)))
    c.restore()
    c.save(); c.clipRect(skia.Rect(W / 2, 0, W, H))
    space(c, t)
    rocket(c, 860, 980, 0.6, 0, t, flame=1.0, vac=1.0)
    c.restore()
    c.drawLine(W / 2, 600, W / 2, H, P(color=col('#ffffff'), stroke=6))
    bk = ease_out(prog(t, t0 + 1.0, 0.8))
    thrust_bar(c, 110, 1300, 0.78, SKYB, 'ground', bk)
    thrust_bar(c, 670, 1300, 0.86, HOT, 'space', bk)
    label_pill(c, 'MORE push in space', 540, 700, size=46, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'air pushes BACK', 290, 1560, size=38, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 1.0, 'sparkle'), (t0 + 1.6, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    space(c, t)
    star_stream(c, t, 0.6)
    rocket(c, 540, 1180, 0.6, 0, t, flame=1.0)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'throw gas BACK, go forward', 540, 700, size=42, k=k0, fill=NAVY, hi=HOT)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why SUNSETS are red', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
        sun(c, 870, 990, 60 * kk, t, glow=True)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do rockets move in empty space?',
    music=False, faces=False, ambience='space',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does a rocket move in empty space?', 'How do ROCKETS move in space?'),
            ("There's no air out there to push against.", 'No AIR to push against')], tail=0.9),
        dict(name='balloon', draw=s2, sfx_fn=s2_sfx, ambience='wind', lines=[
            ("Here's the trick. Let go of a blown-up balloon: air rushes out the back, and the balloon shoots forward.", 'Like a loose BALLOON')], tail=1.2),
        dict(name='gas', draw=s3, sfx_fn=s3_sfx, lines=[
            ('A rocket does the same, just much harder. It burns fuel and blasts hot gas out at thousands of miles an hour.', 'Hot gas, super FAST')], tail=1.2),
        dict(name='newton', draw=s4, sfx_fn=s4_sfx, trans='punch', lines=[
            ('It pushes the gas backward, and the gas pushes the rocket forward.', 'Gas back, rocket FORWARD'),
            ("That's Newton's third law.", "NEWTON'S third law")], tail=1.2),
        dict(name='oxygen', draw=s5, sfx_fn=s5_sfx, lines=[
            ('No air also means no oxygen for burning, so rockets bring their own.', 'They BRING their own oxygen')], tail=1.3),
        dict(name='coast', draw=s6, sfx_fn=s6_sfx, lines=[
            ('And once the engine shuts off, nothing slows it down. It just keeps going.', 'It keeps GOING')], tail=1.1),
        dict(name='vacuum', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: rocket engines push harder in space than on the ground.", 'STRONGER in space'),
            ('Down here, the air around the nozzle pushes back.', 'Air pushes BACK')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So rockets move by throwing gas the other way.', 'Throw gas BACK, go forward'),
            ('Next: why sunsets are red.', 'Next: why SUNSETS are red'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
