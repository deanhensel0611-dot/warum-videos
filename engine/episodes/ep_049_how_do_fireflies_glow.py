"""Episode 49 (EN, general audience): How do fireflies glow?
Facts checked (Scientific American "How and why do fireflies light up?"; Scientific American "Scientists learn how
fireflies switch on their lights" on Trimmer et al. 2001, Science (nitric oxide flash control); PMC4207525 "Expression
of the nos gene and firefly flashing"; National Park Service, Great Smoky Mountains "Synchronous fireflies";
US DOE / energy.gov on incandescent bulbs (~90 % of energy given off as heat)):
- Fireflies (lightning bugs) are beetles (family Lampyridae), not flies. The light organ ("lantern") is in the
  last segments of the abdomen.
- Bioluminescence: the molecule luciferin reacts with oxygen, driven by the enzyme luciferase and the cell's energy
  molecule ATP (with magnesium); the reaction gives off light.
- It produces very little heat ("cold light"), unlike an incandescent bulb, which gives off about 90 % of its energy
  as heat.
- Flash control: oxygen reaches the lantern through tiny air tubes (tracheae). A nerve signal triggers nitric oxide,
  which briefly lets oxygen reach the light-making sites -> flash on; without oxygen, light off.
- Flashes are courtship signals: males of each species fly with their own flash pattern; females answer from the
  ground/vegetation.
- In a few places, e.g. Great Smoky Mountains National Park (Photinus carolinus), thousands of fireflies flash in
  synchrony for a couple of weeks each year.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
GLOW = '#d8ff4a'

def meadow(c, t, y=1450):
    night_sky(c, t, n=70, y1=y - 100)
    p = skia.Path(); p.moveTo(0, y); p.cubicTo(300, y - 60, 700, y + 30, W, y - 30); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y - 60, 0, H), [col('#1d3b2a'), col('#0f2118')]))
    rnd = random.Random(8)
    for i in range(70):
        x = rnd.uniform(0, W); h = rnd.uniform(50, 130); sw = 6 * math.sin(t * 1.5 + i)
        c.drawLine(x, y + 40, x + sw, y + 40 - h, P(color=col('#2c5a3c'), stroke=5))

def glow_dot(c, x, y, r, k, alpha=255):
    if k <= 0: return
    a = int(alpha * k)
    c.drawCircle(x, y, r * 3, rad(x, y, r * 3, [col(GLOW, int(a * 0.55)), col(GLOW, 0)]))
    c.drawCircle(x, y, r, P(color=col('#f6ffc0', a)))

def molecule_ball(c, x, y, r, colr, label, k=1.0):
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawCircle(0, 0, r, rad(-r * 0.3, -r * 0.35, r * 1.4, [col(mix_hx(colr, '#ffffff', 0.5)), col(colr), col(mix_hx(colr, '#000000', 0.3))], [0, 0.5, 1]))
    c.drawCircle(0, 0, r, P(color=col('#ffffff', 160), stroke=4))
    text_block(c, label, 0, -2, size=int(min(r * 0.42, 2.7 * r / len(label))), fill='#ffffff', hi='#ffffff', stroke=NAVY, maxw=2000)
    c.restore()

# ---------- 1: Hook (cold open: fireflies already blinking) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    meadow(c, t)
    rnd = random.Random(2)
    for i in range(14):
        x = rnd.uniform(120, 900); y = rnd.uniform(800, 1400) + 30 * math.sin(t + i)
        ph = (t * rnd.uniform(0.4, 0.8) + rnd.random()) % 1.0
        glow_dot(c, x + 20 * math.sin(t * 0.7 + i), y, 12, max(0, math.sin(ph * math.pi * 2)) ** 2)
    if t > t1:
        for i, (lbl, x) in enumerate((('no BATTERY', 290), ('no FIRE', 790))):
            label_pill(c, lbl, x, 700, size=44, k=ease_back(prog(t, t1 + 0.2 + i * 0.5, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, 'CHEMISTRY', 540, 1560, size=52, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=GOLD)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'sparkle'), (t1 + 0.2, 'pop'), (t1 + 0.7, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 2: They're beetles, lantern at the tail ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#1b2a6a', '#3b4fa0')
    k = ease_back(prog(t, t0 - 0.2, 0.6))
    g = 0.5 + 0.5 * math.sin(t * 3)
    firefly(c, 540, 1080, 2.2 * k, t, glow=g)
    label_pill(c, 'a BEETLE', 540, 700, size=52, k=ease_back(prog(t, t0 + 0.9, 0.4)), fill=NAVY, hi=SKYB)
    lk = ease_back(prog(t, t0 + 2.4, 0.4))
    if lk > 0:
        arrow(c, 840, 1480, 640, 1400, colr='#ffffff', w=12, alpha=int(255 * min(1, lk)))
        label_pill(c, 'LANTERN', 800, 1560, size=48, k=lk, fill=NAVY, hi=GOLD)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0, 'whoosh'), (t0 + 0.9, 'pop'), (t0 + 2.4, 'pop')]

# ---------- 3: The recipe ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a6a', '#3b4fa0')
    # lantern cell backdrop
    c.drawRoundRect(skia.Rect(90, 640, 990, 1600), 80, 80, P(color=col('#f3f0c8', 40)))
    c.drawRoundRect(skia.Rect(90, 640, 990, 1600), 80, 80, P(color=col('#f3f0c8', 120), stroke=5))
    mix = ease_in_out(prog(t, t1 + 1.6, 1.0))
    pos = [(300, 900), (780, 900), (300, 1300), (780, 1300)]
    items = [('#ffb627', 'luciferin', 120, t0 + 0.6), ('#4cc38a', 'luciferase', 120, t0 + 1.8),
             ('#2f9bff', 'OXYGEN', 90, t1 + 0.2), ('#ff5c85', 'ENERGY', 90, t1 + 0.8)]
    for (x, y), (colr, lbl, r, st) in zip(pos, items):
        k = ease_back(prog(t, st, 0.4))
        xx, yy = lerp(x, 540, mix * 0.75), lerp(y, 1100, mix * 0.75)
        molecule_ball(c, xx + 6 * math.sin(t * 3 + x), yy, r, colr, lbl, k * (1 - 0.5 * mix))
    if mix > 0:
        fk = prog(t, t1 + 2.2, 0.5)
        c.drawCircle(540, 1100, 260 * fk, rad(540, 1100, 260 * fk + 0.1, [col('#ffffff', int(255 * fk)), col(GLOW, int(200 * fk)), col(GLOW, 0)], [0, 0.35, 1]))
        label_pill(c, '= LIGHT', 540, 1500, size=54, k=ease_back(prog(t, t1 + 2.3, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.8, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.8, 'pop'), (t1 + 1.6, 'whoosh'), (t1 + 2.2, 'sparkle')]

# ---------- 4: Cold light (aha) ----------
def bulb(c, x, y, s, hot=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, -40, 200, rad(0, -40, 200, [col('#ffb35c', int(140 * hot)), col('#ff7a2b', 0)]))
    p = skia.Path(); p.addCircle(0, -60, 110)
    c.drawPath(p, P(color=col('#fff3c0', 230)))
    c.drawPath(p, P(color=col('#d9a441'), stroke=5))
    c.drawRect(skia.Rect(-50, 40, 50, 120), lin(c, (-50, 0, 50, 0), [col('#9aa3b0'), col('#dfe5ec'), col('#9aa3b0')], vertical=False))
    for k in range(4): c.drawLine(-50, 52 + k * 18, 50, 52 + k * 18, P(color=col('#6d7686'), stroke=4))
    fl = skia.Path(); fl.moveTo(-30, 30); fl.lineTo(-20, -60); fl.lineTo(-8, -40); fl.lineTo(4, -70); fl.lineTo(16, -40); fl.lineTo(30, 30)
    c.drawPath(fl, P(color=col('#ff8a00'), stroke=5))
    c.restore()

def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a6a', '#3b4fa0')
    firefly(c, 300, 1050, 1.3, t, glow=0.75 + 0.25 * math.sin(t * 4))
    label_pill(c, 'COLD light', 300, 700, size=50, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    # heat meter bars
    def meter(x, frac, colr, k):
        c.drawRoundRect(skia.Rect(x - 40, 1260, x + 40, 1560), 30, 30, P(color=col('#ffffff', 220)))
        h = 280 * frac * k
        c.drawRoundRect(skia.Rect(x - 30, 1550 - h, x + 30, 1550), 24, 24, P(color=col(colr)))
    meter(300, 0.08, SKYB, ease_out(prog(t, t0 + 1.2, 0.8)))
    if t > t1:
        bk = ease_back(prog(t, t1, 0.5))
        if bk > 0: bulb(c, 770, 1020, 1.0 * bk, hot=0.7 + 0.3 * math.sin(t * 5))
        meter(770, 0.9, '#ff6b2c', ease_out(prog(t, t1 + 0.6, 1.0)))
        label_pill(c, '~90% HEAT', 770, 700, size=48, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'ding'), (t1, 'pop'), (t1 + 1.0, 'pop')]

# ---------- 5: The switch: oxygen ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#0d1838', '#1b2a6a')
    on = 0.0
    if t > t1 + 0.6:
        on = 1.0 if ((t - t1 - 0.6) % 1.4) < 0.5 else 0.0
    # big lantern cross-section
    lp = skia.Path(); lp.addRoundRect(skia.Rect(240, 900, 840, 1420), 120, 120)
    c.drawPath(lp, P(color=col(mix_hx('#d9d2a8', '#f4ff8a', on))))
    if on: c.drawPath(lp, P(color=col(GLOW, 150), blur=40))
    c.drawPath(lp, P(color=col('#8a8460'), stroke=6))
    # air tubes (tracheae) branching in from the top
    tubes = [(540, 640, 540, 1000), (540, 760, 360, 1050), (540, 760, 720, 1050), (540, 860, 420, 1250), (540, 860, 660, 1250)]
    for (x0, y0, x1, y1) in tubes:
        c.drawLine(x0, y0, x1, y1, P(color=col('#cfd8e6'), stroke=22))
        c.drawLine(x0, y0, x1, y1, P(color=col('#8fa2bf'), stroke=8))
    label_pill(c, 'AIR tubes', 300, 760, size=42, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        # oxygen dots flowing in while 'on'
        for i in range(12):
            x0, y0, x1, y1 = tubes[i % 5]
            ph = ((t - t1) * 1.2 + i / 12) % 1.0
            if on or ph < 0.3:
                oxygen_dot(c, lerp(x0, x1, ph), lerp(y0, y1, ph), 10, t, alpha=230 if on else 120)
        # nerve signal pulse
        sp = ((t - t1 - 0.6) % 1.4) / 1.4 if t > t1 + 0.6 else 0
        c.drawLine(900, 640, 820, 980, P(color=col('#ffd23f', 160), stroke=6))
        c.drawCircle(lerp(900, 820, min(1, sp * 3)), lerp(640, 980, min(1, sp * 3)), 14, P(color=col('#ffd23f')))
        label_pill(c, 'NERVE signal', 780, 1560, size=42, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'ON' if on else 'OFF', 540, 1160, size=60, k=1.0, fill=NAVY, hi=GOLD if on else NAVY)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    flashes = [(t1 + 0.6 + 1.4 * i, 'click') for i in range(int(max(0, D - t1 - 0.6) / 1.4) + 1) if t1 + 0.6 + 1.4 * i < D - 0.2]
    return [(t0 + 0.8, 'pop'), (t1 + 0.3, 'pop')] + flashes

# ---------- 6: Why flash? A dating code ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    meadow(c, t, y=1380)
    # male flying, pattern: blink-blink-pause
    mx = 540 + 220 * math.sin(t * 0.6); my = 900 + 60 * math.sin(t * 1.3)
    cyc = (t - t0) % 2.0
    mg = 1.0 if (cyc < 0.25 or 0.5 < cyc < 0.75) else 0.0
    firefly(c, mx, my, 0.55, t, glow=mg, fly=True, rot=15 * math.sin(t))
    label_pill(c, 'each species: own CODE', 540, 680, size=42, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=GOLD)
    # code dots
    k = prog(t, t0 + 1.4, 0.3)
    for i, on in enumerate((1, 1, 0, 1, 1, 0)):
        glow_dot(c, 360 + i * 70, 780, 12, k * (1.0 if on else 0.25))
    if t > t1:
        cyc2 = (t - t1 - 0.4) % 2.0
        fg = 1.0 if (t > t1 + 0.4 and 1.0 < cyc2 < 1.3) else 0.15
        firefly(c, 760, 1440, 0.45, t, glow=fg, rot=-30)
        label_pill(c, 'she ANSWERS', 760, 1600, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.8, 'pop'), (t0 + 1.4, 'click'), (t1 + 0.6, 'pop'), (t1 + 1.4, 'sparkle')]

# ---------- 7: Wild part: synchronous fireflies ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_sky(c, t, n=60, y1=1100)
    # forest silhouettes
    for i in range(9):
        x = i * 135; h = 380 + 120 * math.sin(i * 1.7)
        tri = skia.Path(); tri.moveTo(x - 90, 1450); tri.lineTo(x, 1450 - h); tri.lineTo(x + 90, 1450); tri.close()
        c.drawPath(tri, P(color=col('#0f2118')))
    c.drawRect(skia.Rect(0, 1440, W, H), P(color=col('#0b1a12')))
    rnd = random.Random(11)
    sync = prog(t, t1 - 0.5, 1.5)
    period = 1.6
    for i in range(80):
        x = rnd.uniform(40, 1040); y = rnd.uniform(750, 1500)
        ph0 = rnd.random()
        ph = ((t / period) + ph0 * (1 - sync)) % 1.0
        k = 1.0 if ph < 0.18 else 0.0
        glow_dot(c, x + 10 * math.sin(t + i), y, 9, k)
    label_pill(c, 'THOUSANDS', 540, 680, size=50, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        label_pill(c, 'in SYNC', 540, 1580, size=52, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 1.0, 'pop'), (t1 + 1.0, 'sparkle')]

# ---------- 8: Outro ----------
def loaf(c, x, y, s):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-200, 60); p.cubicTo(-220, -90, -120, -150, 0, -150); p.cubicTo(120, -150, 220, -90, 200, 60); p.close()
    c.drawPath(p, lin(c, (0, -150, 0, 60), [col('#e0a050'), col('#b8742a')]))
    for k in range(3):
        c.drawLine(-90 + k * 80, -110, -50 + k * 80, -60, P(color=col('#f6d39a'), stroke=10))
    c.drawPath(p, P(color=col('#8a5420'), stroke=5))
    c.restore()

def s8(c, t, D, cues):
    meadow(c, t)
    for i in range(6):
        ph = t * 0.6 + i * 1.1
        firefly(c, 160 + i * 150, 1250 + 50 * math.sin(ph), 0.28, t, glow=max(0, math.sin(t * 2.5 + i * 1.7)), fly=True, rot=15 * math.sin(ph))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'chemistry + OXYGEN = cold light', 540, 700, size=40, k=k0, fill=NAVY, hi=GOLD)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why BREAD rises', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
        loaf(c, 540, 1040, 0.9 * kk)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do fireflies glow?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do fireflies glow?', 'How do FIREFLIES glow?'),
            ("No battery, no fire. It's pure chemistry.", 'No battery. Pure CHEMISTRY.')], tail=1.0),
        dict(name='beetle', draw=s2, sfx_fn=s2_sfx, lines=[
            ("First, fireflies aren't flies. They're beetles, with a light organ in the tail.", "They're BEETLES")], tail=1.0),
        dict(name='recipe', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Inside, a chemical called luciferin meets an enzyme, luciferase.', 'LUCIFERIN + luciferase'),
            ('Add oxygen and some energy, and the mix gives off light.', '+ OXYGEN + energy = light')], tail=1.1),
        dict(name='cold', draw=s4, sfx_fn=s4_sfx, trans='punch', lines=[
            ('And it makes almost no heat. Scientists call it cold light.', 'Almost no heat: COLD light'),
            ('An old light bulb wastes about ninety percent as heat.', 'Old bulbs: ~90% HEAT')], tail=1.0),
        dict(name='switch', draw=s5, sfx_fn=s5_sfx, lines=[
            ('To flash, the firefly controls the oxygen.', 'The switch is OXYGEN'),
            ('A nerve signal lets air rush in, and the lantern switches on.', 'Air rushes in: light ON')], tail=1.4),
        dict(name='code', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Why flash? To find a mate. Each species blinks its own code,', 'Each species has its own CODE'),
            ('and females answer from the grass.', 'Females ANSWER')], tail=1.2),
        dict(name='sync', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: in a few places, like the Great Smoky Mountains,", 'Great Smoky MOUNTAINS'),
            ('thousands of fireflies flash at the same time.', 'Thousands flash in SYNC')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So fireflies glow by mixing chemicals with oxygen into cold light.', 'Chemistry + OXYGEN = cold light'),
            ('Next: why bread rises.', 'Next: why BREAD rises'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
