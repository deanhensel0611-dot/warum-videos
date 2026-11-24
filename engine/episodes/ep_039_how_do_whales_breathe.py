"""Episode 39 (EN, general audience): How do whales breathe?
Facts checked (Scientific American "How do whales and dolphins sleep without drowning?", Marine Mammal Center "How do
whales sleep?", Open University "Studying mammals: return to the water", NOAA Fisheries whale facts, Quick et al. 2020
J. Exp. Biol. "Extreme diving in mammals: first estimates of behavioural aerobic dive limits in Cuvier's beaked whales"):
- Whales are mammals: they breathe air with lungs, they have no gills.
- The blowhole is the whale's nostril(s), which moved to the top of the head during evolution (baleen whales have two,
  toothed whales one), so a whale can breathe with only the top of its head at the surface.
- The visible "spout"/blow is mostly the warm, moist exhaled breath condensing in cooler air (plus a little sea water
  from around the blowhole) - not a fountain of sea water.
- Whales breathe out and in explosively within a second or two and exchange about 80-90 % of their lung air per
  breath; humans at rest exchange roughly 10-15 %.
- Underwater they store oxygen in blood and in muscles rich in myoglobin, and their heart rate slows (dive response).
- Whales and dolphins are conscious (voluntary) breathers; dolphins and some whales rest one brain hemisphere at a
  time (unihemispheric sleep) while the other stays alert, so they can keep surfacing to breathe.
- Record: a Cuvier's beaked whale stayed submerged for 222 minutes (3 h 42 min), Quick et al. 2020.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def ocean(c, t, surf=1150):
    sky(c, '#cfe9ff', '#eaf5ff')
    clouds(c, t, seed=3, n=2, y0=620, y1=900, speed=12, a=200)

def sea_over(c, t, surf=1150, a=165):
    water_body(c, surf, t, y1=H, c1='#3fa9ff', c2='#0f4a9e', amp=10, a=a)

# ---------- 1: Hook (cold open: whale already blowing at the surface) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    ocean(c, t)
    surf = 1150
    wx = 540 + 30 * math.sin(t * 0.4); wy = surf + 40
    whale(c, wx, wy, 0.95, t, swim=0.4)
    hx, hy = whale_hole(wx, wy, 0.95)
    sea_over(c, t, surf)
    k = ((t + 0.25) % 3.2) / 2.4
    whale_blow(c, hx, hy, 1.15, k, t)
    label_pill(c, 'a MAMMAL', 300, 760, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        lk = ease_back(prog(t, t1 + 0.4, 0.5))
        lungs(c, 540, 1560, 0.6 * lk, fill=0.5 + 0.3 * math.sin(t * 2))
        label_pill(c, 'NO gills', 820, 1450, size=40, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.2, 'click')]

# ---------- 2: Blowhole = nose on top, like a snorkel ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    ocean(c, t)
    surf = 1380
    # close-up on the head: whale big, head on screen
    rise = ease_out(prog(t, t0, 0.8))
    wx, s = 40, 1.55
    wy = surf + 120 - 150 * rise
    if t > t1:  # sinks until only the top of the head breaks the surface
        wy = surf - 30 + 140 * ease_in_out(prog(t, t1, 0.8))
    whale(c, wx, wy, s, t, swim=0.2)
    hx, hy = whale_hole(wx, wy, s)
    sea_over(c, t, surf)
    hk = ease_back(prog(t, t0 + 0.9, 0.4))
    if hk > 0:
        c.drawCircle(hx, hy, 46 * hk, P(color=col('#ffd23f'), stroke=8))
    label_pill(c, 'BLOWHOLE = nostrils', 470, 830, size=44, k=ease_back(prog(t, t0 + 1.1, 0.4)), fill=NAVY, hi=HOT)
    c.drawLine(470, 880, hx, hy - 50, P(color=col(NAVY, int(200 * prog(t, t0 + 1.1, 0.3))), stroke=5))
    if t > t1:
        ak = prog(t, t1 + 0.6, 0.4)
        ph = (t * 0.9) % 2.0
        up = ph < 1.0
        u = ph % 1.0
        if up: arrow(c, hx + 60, hy - 40, hx + 60, hy - 40 - 140 * u, colr=SKYB, w=14, alpha=int(255 * ak * (1 - u)))
        else: arrow(c, hx - 60, hy - 180, hx - 60, hy - 180 + 140 * u, colr=HOT, w=14, alpha=int(255 * ak * (1 - u)))
        label_pill(c, 'built-in SNORKEL', 540, 1600, size=44, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=SKYB)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.9, 'click'), (t0 + 1.1, 'pop'), (t1 + 0.6, 'whoosh'), (t1 + 1.0, 'pop')]

# ---------- 3: The blow is breath, not sea water ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#bcd8f2', '#e6f1fb')
    surf = 1350
    wx, wy = 520, surf + 30
    whale(c, wx, wy, 0.8, t, swim=0.3)
    hx, hy = whale_hole(wx, wy, 0.8)
    sea_over(c, t, surf)
    k = ((t - t0 + 0.2) % 3.0) / 2.6
    whale_blow(c, hx, hy, 1.3, k, t)
    # crossed-out "sea water" icon
    ck = ease_back(prog(t, t0 + 0.6, 0.4))
    if ck > 0:
        c.save(); c.translate(260, 780); c.scale(ck, ck)
        raindrop(c, 0, 0, 50, t, face_on=False)
        c.drawLine(-60, -60, 60, 60, P(color=col(HOT), stroke=12)); c.restore()
        label_pill(c, 'NOT sea water', 260, 900, size=38, k=ck, fill=NAVY, hi=HOT)
    if t > t1:
        tk = ease_back(prog(t, t1 + 0.3, 0.4))
        label_pill(c, 'WARM breath', 780, 760, size=40, k=tk, fill=NAVY, hi=HOT)
        label_pill(c, '+ COOL air', 780, 850, size=40, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, '= MIST', 780, 940, size=44, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t1 + 0.3, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 4: One huge breath in a second or two: 80-90 % vs ~15 % ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#eef6ff', '#d6e9fb')
    sw = ease_back(prog(t, t0 + 0.2, 0.4))
    sw *= 1 - prog(t, cues[1]['start'], 0.3)
    if sw > 0.01:
        frac = clamp((t - t0 - 0.6) / 2.0) * 0.5
        c.save(); c.translate(540, 1050); c.scale(sw, sw)
        stopwatch(c, 0, 0, 150, frac, label='1–2 s', accent=SKYB)
        c.restore()
    label_pill(c, 'OUT and IN, fast', 540, 760, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=SKYB)
    if t > t1:
        k = ease_out(prog(t, t1, 0.5))
        f1 = 0.85 * ease_in_out(prog(t, t1 + 0.6, 1.4)); f2 = 0.15 * ease_in_out(prog(t, t1 + 1.4, 1.0))
        lungs(c, 300, 1120, 1.15 * k, fill=f1, fresh=SKYB)
        lungs(c, 780, 1160, 0.75 * k, fill=f2, fresh=SKYB)
        label_pill(c, 'WHALE', 300, 800, size=42, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'YOU', 780, 900, size=42, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, '80–90% NEW air', 300, 1470, size=38, k=ease_back(prog(t, t1 + 1.8, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'about 15%', 780, 1420, size=38, k=ease_back(prog(t, t1 + 2.3, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.6, 'whoosh'), (t1, 'whoosh'), (t1 + 0.3, 'pop'), (t1 + 1.8, 'pop'), (t1 + 2.3, 'pop')]

# ---------- 5: Oxygen stored in blood + muscles, heart slows ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#0f4a9e', '#06224d')
    rising_bubbles(c, t, seed=5, n=10, y0=620, y1=1750, alpha=120)
    # muscle block with stored oxygen
    mk = ease_out(prog(t, t0, 0.6))
    c.save(); c.translate(0, 80 * (1 - mk))
    rect = skia.Rect(140, 760, 940, 1080)
    c.drawRoundRect(rect, 40, 40, lin(c, (0, 760, 0, 1080), [col('#8a2238', int(255 * mk)), col('#5a1024', int(255 * mk))]))
    for i in range(6):
        yy = 790 + i * 50
        c.drawLine(170, yy, 910, yy + 8, P(color=col('#b8405a', int(200 * mk)), stroke=5))
    rnd = random.Random(2)
    nk = prog(t, t0 + 1.4, 2.0)
    for i in range(int(26 * nk)):
        x, y = rnd.uniform(190, 890), rnd.uniform(800, 1040)
        oxygen_dot(c, x, y + 4 * math.sin(t * 3 + i), 15, t, seed=i)
    c.drawRoundRect(rect, 40, 40, P(color=col('#ffffff', int(120 * mk)), stroke=5))
    c.restore()
    label_pill(c, 'MUSCLES store oxygen', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'myoglobin', 540, 1150, size=36, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        hk = ease_back(prog(t, t1 + 0.2, 0.5))
        rate = lerp(2.2, 0.55, prog(t, t1 + 0.6, 2.5))
        ph = (t * rate) % 1.0
        sq = max(0.0, 1 - ph / 0.25) if ph < 0.25 else 0.0
        heart(c, 540, 1420, 0.55 * hk, t, squeeze=sq, vessels=False)
        label_pill(c, 'heart SLOWS down', 540, 1660, size=40, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=HOT)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.4, 'sparkle'), (t0 + 2.6, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.8, 'pop')]

# ---------- 6: Every breath is a choice -> half-brain sleep (aha) ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#13204a', '#0b1430')
    stars(c, t, seed=8, n=40, y0=620, y1=1000, a=0.6)
    bk = ease_back(prog(t, t0 + 0.2, 0.5))
    half = ease_in_out(prog(t, t1 + 0.5, 1.0))
    brain(c, 540, 1080, 1.25 * bk, t, glow=0.6 * prog(t, t1 + 1.4, 0.5) * (0.8 + 0.2 * math.sin(t * 4)), left=1 - 0.85 * half, right=1.0)
    label_pill(c, 'every breath = a CHOICE', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)) * (1 - prog(t, t1 + 0.3, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        zzz(c, 300, 900, t, size=70, alpha=int(255 * half))
        label_pill(c, 'ASLEEP', 330, 1340, size=40, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'AWAKE', 760, 1340, size=40, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
        # small whale surfacing below, driven by the awake half
        wk = prog(t, t1 + 1.6, 0.6)
        if wk > 0:
            wy = 1580 + 15 * math.sin(t * 1.5)
            whale(c, 520, wy, 0.32, t, alpha=int(255 * wk), swim=0.5)
            water_body(c, 1590, t, y1=1720, c1='#3fa9ff', c2='#0f4a9e', amp=6, a=int(200 * wk))

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.8, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.4, 'ding'), (t1 + 1.6, 'whoosh')]

# ---------- 7: Wild part: Cuvier's beaked whale 3 h 42 min ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#0f4a9e', '#03122e')
    rising_bubbles(c, t, seed=9, n=8, y0=620, y1=1750, alpha=100)
    dive = prog(t, t0, 3.0)
    wx = lerp(260, 640, dive); wy = lerp(820, 1000, dive)
    c.save(); c.translate(wx, wy); c.rotate(10 * (1 - dive) + 4)
    whale(c, 0, 0, 0.55, t, colr='#7d7f8c', belly='#c9c7c2', swim=0.6)
    c.restore()
    label_pill(c, "Cuvier's beaked whale", 540, 700, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    # timeline bars: movie ~2 h vs whale 3 h 42 min
    bk = prog(t, t1 + 0.2, 0.4)
    if bk > 0:
        x0 = 150; scale = 180  # px per hour
        c.drawRoundRect(skia.Rect(x0, 1250, x0 + scale * 2.0 * ease_out(prog(t, t1 + 0.4, 0.8)), 1320), 20, 20, P(color=col('#9fb0c8')))
        label_pill(c, 'a movie: ~2 h', x0 + 210, 1205, size=34, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY)
        L = scale * 3.7 * ease_out(prog(t, t1 + 1.2, 1.2))
        c.drawRoundRect(skia.Rect(x0, 1420, x0 + L, 1500), 20, 20, lin(c, (x0, 0, x0 + 700, 0), [col(SKYB), col('#ffd23f')], vertical=False))
        label_pill(c, '3 h 42 MIN', x0 + 330, 1570, size=46, k=ease_back(prog(t, t1 + 2.3, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.6, 'pop'), (t1 + 1.2, 'whoosh'), (t1 + 2.3, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    ocean(c, t)
    surf = 1250
    wx, wy = 520, surf + 40
    whale(c, wx, wy, 0.85, t, swim=0.4)
    hx, hy = whale_hole(wx, wy, 0.85)
    sea_over(c, t, surf)
    whale_blow(c, hx, hy, 1.0, ((t + 0.4) % 3.4) / 2.6, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: OWL heads', 540, 700, size=46, k=kk, fill=NAVY, hi=GOLD)
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do whales breathe?',
    music=False, faces=False, ambience='water',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do whales breathe?', 'How do WHALES breathe?'),
            ("They're mammals. No gills at all, just lungs, like yours.", 'No GILLS, just lungs')], tail=0.8),
        dict(name='blowhole', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Over millions of years, their nostrils moved to the top of the head. That is the blowhole.', 'The nose moved on TOP'),
            ('So a whale can breathe with just its head at the surface, like a built-in snorkel.', 'A built-in SNORKEL')], tail=0.8),
        dict(name='blow', draw=s3, sfx_fn=s3_sfx, lines=[
            ("And that famous spout? It's not a fountain of sea water.", 'The spout is not SEAWATER'),
            ("It's mostly warm breath turning to mist, like your breath on a cold day.", 'It is warm BREATH')], tail=0.8),
        dict(name='breath', draw=s4, sfx_fn=s4_sfx, lines=[
            ('A whale breathes out and in within a second or two,', 'Out and in in SECONDS'),
            ('and swaps about eighty to ninety percent of the air in its lungs. You swap about fifteen.', '80-90% vs your 15%')], tail=1.0),
        dict(name='oxygen', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Underwater, it stores oxygen in its blood and in muscles packed with a protein called myoglobin.', 'Oxygen stored in MUSCLES'),
            ('And its heart slows way down to make that oxygen last.', 'The heart SLOWS down')], tail=1.0),
        dict(name='sleep', draw=s6, sfx_fn=s6_sfx, trans='punch', lines=[
            ('Here is the catch: whales never breathe on autopilot. Every breath is a choice.', 'Every breath is a CHOICE'),
            ('So dolphins and some whales sleep with half their brain, while the other half stays awake to breathe.', 'HALF the brain sleeps')], tail=1.2),
        dict(name='record', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: one Cuvier's beaked whale stayed underwater for three hours and forty-two minutes.", '3 HOURS 42 on one breath'),
            ("That's longer than most movies.", 'Longer than a MOVIE')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So whales breathe air, through a nose on top of their head.', 'A NOSE on top of the head'),
            ('Next: how owls turn their heads so far.', 'Next: OWL heads'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
