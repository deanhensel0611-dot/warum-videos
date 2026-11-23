"""Episode 35 (EN, general audience): Why don't penguins freeze?
Facts checked (Cool Antarctica "How do penguins keep warm?", The Conversation "How can penguins stay warm in the
freezing waters of Antarctica", University of Glasgow / J. Exp. Biol. 2013 "Emperor penguin plumage", Gilbert et
al. 2006 "Huddling behavior in emperor penguins" (Polar Biology), British Antarctic Survey, Australian Antarctic
Division):
- Emperor penguins breed through the Antarctic winter; air temperatures can drop to about -40 C (with wind chill far
  lower). -40 is the same on the Celsius and Fahrenheit scales.
- Densely packed, overlapping stiff feathers form a windproof, waterproof outer layer (waterproofed with oil from the
  preen gland); a layer of down/afterfeathers underneath traps insulating air.
- A layer of fat (blubber) under the skin insulates and stores energy. Core body temperature ~38 C.
- Countercurrent heat exchange: arteries carrying warm blood to the feet and flippers run alongside veins carrying cold
  blood back, so heat passes into the returning blood; feet are kept just above freezing, little heat is lost.
- Huddles of hundreds to thousands of emperor penguins: temperature inside huddles measured above 20 C and up to
  ~37.5 C (Gilbert et al. 2006); the birds slowly shift positions so everyone gets turns at the warm centre.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
ICE = '#e8f4ff'
HOT = '#ff5c85'
COLD = '#2f9bff'

def polar_bg(c, t, ground=1520, blizzard=1.0):
    sky(c, '#9fc4e8', '#e9f3ff', mid='#c4dcf3')
    p = skia.Path(); p.moveTo(0, ground - 120); p.cubicTo(260, ground - 230, 520, ground - 140, 720, ground - 200)
    p.cubicTo(860, ground - 240, 980, ground - 170, W, ground - 190); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, ground - 240, 0, ground), [col('#dbe9f7'), col('#c5d9ee')]))
    c.drawRect(skia.Rect(0, ground, W, H), lin(c, (0, ground, 0, H), [col('#f4f9ff'), col('#d3e4f5')]))
    if blizzard > 0:
        snow(c, t, seed=4, n=int(46 * blizzard), alpha=int(230 * min(1, blizzard)))
        wind_lines(c, t, y0=700, y1=1450, n=6, speed=1100, alpha=int(120 * blizzard))

# ---------- 1: Hook (cold open: blizzard already blowing) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    polar_bg(c, t)
    penguin(c, 430, 1560, 1.25, t, seed=0)
    penguin(c, 160, 1500, 0.8, t, seed=2, alpha=235)
    thermometer(c, 860, 1440, s=1.15, level=0.08, hot=COLD)
    label_pill(c, '-40 °C = -40 °F', 540, 690, size=52, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=COLD)
    if t > t1:
        label_pill(c, 'ALL winter long', 760, 1620, size=40, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 1.4, 'pop')]

# ---------- 2: Feathers: roof tiles + down jacket ----------
def feather_tile(c, x, y, w_, h_, alpha=255, oil=0.0):
    p = skia.Path(); p.moveTo(x - w_ / 2, y - h_)
    p.lineTo(x - w_ / 2, y - h_ * 0.35); p.cubicTo(x - w_ / 2, y + h_ * 0.1, x + w_ / 2, y + h_ * 0.1, x + w_ / 2, y - h_ * 0.35)
    p.lineTo(x + w_ / 2, y - h_); p.close()
    c.drawPath(p, lin(c, (0, y - h_, 0, y), [col('#1d2230', alpha), col('#3a4458', alpha)]))
    c.drawLine(x, y - h_ * 0.9, x, y - h_ * 0.15, P(color=col('#5a6680', int(alpha * 0.8)), stroke=3))
    if oil > 0:
        c.drawOval(skia.Rect(x - w_ * 0.3, y - h_ * 0.45, x - w_ * 0.05, y - h_ * 0.3), P(color=col('#ffffff', int(120 * oil)), blur=2))
    c.drawPath(p, P(color=col('#0f121a', int(alpha * 0.7)), stroke=2.5))

def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9f3ff', '#d2e6fa'); dust(c, t, seed=8, n=10, a=60)
    # skin line and down layer
    top, skin = 900, 1430
    dk = ease_out(prog(t, t1 + 0.2, 0.8))
    c.drawRect(skia.Rect(60, skin, 1020, skin + 140), lin(c, (0, skin, 0, skin + 140), [col('#f2b8a0'), col('#e8957a')]))
    if dk > 0:
        rnd = random.Random(3)
        for i in range(40):
            px, py = rnd.uniform(90, 990), rnd.uniform(1260, skin - 10)
            r = rnd.uniform(16, 30) * dk
            c.drawCircle(px + math.sin(t + i) * 4, py, r, P(color=col('#ffffff', 200), blur=3))
        air_dots(c, 100, 1270, 980, skin - 20, t, n=18, colr='#ffb36b', r=9, alpha=int(220 * dk), jiggle=0.6)
    # overlapping feather rows (from the bottom up, each row covers the next)
    rows = 5; n_vis = ease_out(prog(t, t0 + 0.1, 1.6)) * rows
    for r_ in range(rows):
        if r_ >= n_vis: break
        a = int(255 * clamp(n_vis - r_))
        yb = top + 90 + r_ * 70; off = 60 if r_ % 2 else 0
        for i in range(-1, 9):
            feather_tile(c, 100 + off + i * 120, yb + math.sin(t * 2 + i + r_) * 2, 120, 170, alpha=a, oil=prog(t, t0 + 2.2, 0.6))
    # wind + water bouncing off
    wk = prog(t, t0 + 1.6, 0.4)
    if wk > 0:
        for i in range(3):
            u = ((t - t0) * 0.9 + i / 3) % 1.0
            x = lerp(-40, 520, u); yy = 780 + i * 30
            arrow(c, x - 160, yy, x, yy + 40 * u, colr='#ffffff', w=10, alpha=int(230 * wk * (1 - u)))
        for i in range(4):
            u = ((t - t0) * 0.7 + i / 4) % 1.0
            dx = 600 + i * 90; dy = lerp(640, 930, min(1, u * 1.6)) if u < 0.62 else 930 - (u - 0.62) * 400
            dxx = dx + (max(0, u - 0.62) * 500)
            raindrop(c, dxx, dy, 18, t, face_on=False, alpha=int(255 * wk))
    label_pill(c, 'like ROOF TILES', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=COLD)
    if t > t1:
        label_pill(c, 'trapped WARM air', 540, 1620, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#ff8a3d')

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 0.8, 'pop'), (t0 + 1.6, 'whoosh'), (t1 + 0.2, 'sparkle'), (t1 + 0.6, 'pop')]

# ---------- 3: Blubber like wall insulation ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9f3ff', '#d2e6fa'); dust(c, t, seed=8, n=10, a=60)
    cx, cy = 540, 1640
    k = ease_out(prog(t, t0 + 0.2, 0.9))
    # layers as semicircles from outside in
    layers = [(820, '#232a3a', 'feathers'), (720, '#f2b8a0', 'skin'), (700, '#ffd98a', 'blubber'), (520, '#ff8a8a', 'core')]
    bk = ease_out(prog(t, t0 + 1.0, 1.0))
    for i, (R, colr, _) in enumerate(layers):
        if colr == '#ffd98a':
            R = lerp(700, 700, 1); inner = lerp(700, 520, bk)
        rr = R * k
        c.drawCircle(cx, cy, rr, P(color=col(colr)))
    # blubber band texture
    if bk > 0:
        rnd = random.Random(2)
        for i in range(26):
            an = rnd.uniform(math.pi * 1.05, math.pi * 1.95); rr = rnd.uniform(540, 690) * k
            c.drawCircle(cx + math.cos(an) * rr, cy + math.sin(an) * rr, rnd.uniform(10, 22), P(color=col('#ffe9b8', int(200 * bk))))
    # feather texture
    for i in range(30):
        an = math.pi + (i + 0.5) / 30 * math.pi; r0, r1 = 735 * k, 810 * k
        c.drawLine(cx + math.cos(an) * r0, cy + math.sin(an) * r0, cx + math.cos(an + 0.03) * r1, cy + math.sin(an + 0.03) * r1, P(color=col('#46506a'), stroke=6))
    # core glow
    gk = 0.7 + 0.3 * math.sin(t * 3)
    c.drawCircle(cx, cy, 480 * k, rad(cx, cy, 480 * k, [col('#ff5c85', int(140 * gk)), col('#ff5c85', 0)]))
    label_pill(c, 'BLUBBER', 540, 1010, size=48, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi='#e0a000')
    if t > t1:
        label_pill(c, 'core: ~38 °C', 540, 1330, size=42, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=HOT)
        # cold arrows bouncing off
        for i, xx in enumerate((220, 540, 860)):
            u = ((t - t1) * 0.8 + i * 0.33) % 1.0
            y0 = lerp(640, 800, min(1, u * 2))
            a = int(220 * (1 - u))
            arrow(c, xx, y0 - 80, xx, y0, colr=COLD, w=12, alpha=a)
    label_pill(c, 'a fat LAYER', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi='#e0a000')

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.5, 'pop'), (t0 + 1.2, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 4: Feet on ice ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    polar_bg(c, t, ground=1400, blizzard=0.3)
    penguin(c, 540, 1440, 1.9, t, sway=0.4)
    # frost sparkle on the ice under the feet
    for i in range(6):
        twinkle(c, 300 + i * 95, 1470 + (i % 2) * 30, 16 + 6 * math.sin(t * 4 + i), alpha=200)
    label_pill(c, 'FEET on ice all day', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=COLD)
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.3, 0.5))
        thermometer(c, 900, 1300, s=0.8 * kk if kk > 0 else 0.01, level=0.15, hot=COLD, alpha=255 if kk > 0 else 0)
        label_pill(c, 'why no FROSTBITE?', 540, 1600, size=44, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.4, 'pop'), (t1 + 0.3, 'pop'), (t1 + 0.8, 'pop')]

# ---------- 5: Countercurrent heat swap (aha) ----------
def vessel(c, x, y0, y1, c_top, c_bot, t, down=True, w=70):
    c.drawRoundRect(skia.Rect(x - w / 2, y0, x + w / 2, y1), w / 2, w / 2, lin(c, (0, y0, 0, y1), [col(c_top), col(c_bot)]))
    c.drawRoundRect(skia.Rect(x - w / 2, y0, x + w / 2, y1), w / 2, w / 2, P(color=col('#ffffff', 180), stroke=5))
    for i in range(7):
        u = ((t * 0.35 + i / 7) % 1.0)
        yy = lerp(y0 + 30, y1 - 30, u if down else 1 - u)
        cc = mix_hex(c_top, c_bot, clamp((yy - y0) / (y1 - y0)))
        c.drawCircle(x, yy, 14, P(color=col('#ffffff', 170)))
        c.drawCircle(x, yy, 9, P(color=cc))

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9f3ff', '#d2e6fa'); dust(c, t, seed=8, n=10, a=60)
    y0, y1 = 820, 1400
    k = ease_out(prog(t, t0 + 0.2, 0.6))
    xa, xv = 400, 640
    c.save(); c.translate(0, 80 * (1 - k))
    # foot on ice
    c.drawRoundRect(skia.Rect(120, 1470, 960, 1600), 30, 30, lin(c, (0, 1470, 0, 1600), [col('#f4faff'), col('#bcd8f2')]))
    fp = skia.Path(); fp.moveTo(300, 1470); fp.cubicTo(330, 1400, 720, 1400, 760, 1470); fp.close()
    c.drawPath(fp, P(color=col('#2a2f3a')))
    c.drawLine(300, 1470, 780, 1470, P(color=col('#2a2f3a'), stroke=10))
    vessel(c, xa, y0, y1, '#ff4d6d', '#ffb0b0', t, down=True)
    swap = prog(t, t1 - 0.3, 0.8)
    vessel(c, xv, y0, y1, mix_hx('#7fb2ff', '#ff7a8a', swap * 0.75), '#7fb2ff', t, down=False)
    c.restore()
    label_pill(c, 'warm DOWN', 400, 760 + 80 * (1 - k), size=36, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'cold UP', 680, 760 + 80 * (1 - k), size=36, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=COLD)
    if swap > 0:
        for i in range(5):
            yy = 900 + i * 100
            u = ((t - t1) * 1.2 + i * 0.2) % 1.0
            xx = lerp(xa + 50, xv - 50, u)
            arrow(c, xx - 30, yy, xx + 20, yy, colr='#ff8a3d', w=10, alpha=int(255 * swap * math.sin(math.pi * u)))
        kk = ease_back(prog(t, t1 + 0.6, 0.5), 2.2)
        c.save(); c.translate(820, 1120); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-120, -50, 120, 50), 25, 25, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-120, -50, 120, 50), 25, 25, P(color=col(NAVY), stroke=5))
        text_block(c, 'HEAT', 0, 0, size=50, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()
        label_pill(c, 'just above FREEZING', 540, 1640, size=40, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi=COLD)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.4, 'pop'), (t1 + 0.6, 'ding'), (t1 + 2.0, 'pop')]

# ---------- 6: Wild part: huddle as warm as ~37 C ----------
HUDDLE = None
def huddle_pts():
    global HUDDLE
    if HUDDLE is None:
        pts = []; ring = 0
        for ring, n in enumerate((1, 7, 13, 19, 25)):
            for i in range(n):
                a = 2 * math.pi * i / n + ring * 0.3
                pts.append((ring * 62, a))
        HUDDLE = pts
    return HUDDLE

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f4f9ff', '#d3e4f5')
    snow(c, t, seed=6, n=26, alpha=180)
    cx, cy = 540, 1130
    hk = ease_out(prog(t, t0 + 0.3, 1.4))
    glow = prog(t, t0 + 1.6, 1.2)
    c.drawCircle(cx, cy, 300, rad(cx, cy, 300, [col('#ff8a3d', int(170 * glow)), col('#ffd23f', int(80 * glow)), col('#ffd23f', 0)], [0, 0.5, 1]))
    shuffle = (t - t1) * 0.06 if t > t1 else 0
    for i, (r, a) in enumerate(huddle_pts()):
        rr = r * (0.5 + 0.5 * hk) + 260 * (1 - hk)
        aa = a + shuffle * (1 + r / 200)
        x, y = cx + math.cos(aa) * rr, cy + math.sin(aa) * rr * 0.92
        penguin_top(c, x, y, 0.95, rot=math.degrees(aa) + 180 + 10 * math.sin(t + i), alpha=int(255 * prog(t, t0 + i * 0.02, 0.3)))
    n = int(round(37 * ease_out(prog(t, t0 + 1.6, 1.6))))
    kk = ease_back(prog(t, t0 + 1.6, 0.4))
    label_pill(c, f'up to {n} °C INSIDE', 540, 700, size=46, k=kk, fill=NAVY, hi=HOT)
    if t > t1:
        for sgn in (1, -1):
            curved_arrow(c, cx, cy, 380, 200 + sgn * 0 + (t * 20) % 360, 260 + (t * 20) % 360, colr=NAVY, w=10, alpha=200)
        label_pill(c, 'they take TURNS', 540, 1600, size=44, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=COLD)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 1.6, 'pop'), (t0 + 1.8, 'click'), (t1 + 0.3, 'whoosh'), (t1 + 0.5, 'pop')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    polar_bg(c, t, blizzard=0.6)
    penguin(c, 330, 1590, 0.85, t, seed=1)
    penguin(c, 740, 1600, 0.9, t, seed=3, flip=True)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: SEED to plant', 540, 700, size=46, k=kk, fill=NAVY, hi='#3fae3a')
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1060)

def s7_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title="Why don't penguins freeze?",
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ("Why don't penguins freeze?", "Why don't PENGUINS freeze?"),
            ('Emperor penguins spend the whole Antarctic winter outside, at down to minus forty degrees.', 'Down to MINUS 40 degrees')], tail=0.8),
        dict(name='feathers', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Trick one: stiff, oily feathers overlap like roof tiles, so wind and water stay out.', 'Feathers overlap like ROOF TILES'),
            ('Underneath, fluffy down traps warm air, like a puffer jacket.', 'Down works like a PUFFER jacket')], tail=0.8),
        dict(name='blubber', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Trick two: a thick layer of fat called blubber, insulation like in the walls of a house.', 'A fat layer called BLUBBER'),
            ('It keeps their core at about thirty-eight degrees Celsius.', 'Core stays at 38 °C')], tail=0.8),
        dict(name='feet', draw=s4, sfx_fn=s4_sfx, lines=[
            ('But their feet stand on ice, day and night.', 'But their FEET stand on ice'),
            ('So why no frostbite?', 'So why no FROSTBITE?')], tail=0.6),
        dict(name='swap', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('Warm blood flowing down to the feet runs right next to cold blood coming back.', 'Warm and cold blood run SIDE BY SIDE'),
            ('It hands over its heat on the way, so the feet stay just above freezing and almost no heat is lost.', 'The HEAT gets swapped')], tail=1.2),
        dict(name='huddle', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part: inside a big huddle, it can get as warm as thirty-seven degrees Celsius.", 'Up to 37 °C INSIDE'),
            ('And they take turns, slowly shuffling between the cold edge and the warm middle.', 'They take TURNS in the middle')], tail=1.2),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Feathers, fat, a heat swap and teamwork. That is how penguins beat the cold.', 'Feathers, fat, heat swap, TEAMWORK'),
            ('Next: how a seed grows into a plant.', 'Next: how a SEED grows'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
