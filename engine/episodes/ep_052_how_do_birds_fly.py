"""Episode 52 (EN, general audience): How do birds fly?
Facts checked (Wikipedia "Bird flight" (lift, downstroke/upstroke, pectoralis size); National Wildlife Federation
"The Mystery of Flight: A Bird Is Not A Plane"; Discover Wildlife "How do birds fly?"; Nature News 2016 / Hedenström et
al. 2016, Current Biology, "Record-breaking common swifts fly for 10 months without landing"; Audubon on the same study):
- A bird's wing is a curved airfoil; moving through air it deflects air downward, and the reaction pushes the wing up
  (lift) - the same principle as an airplane wing.
- Flapping: the downstroke is the power stroke; it pushes air down and backward, giving lift and forward thrust.
- On the upstroke the wing is partly folded / flexed and the primary feathers twist and separate, letting air through
  and reducing drag.
- The main flight muscle (pectoralis, pulls the wing down) is the biggest muscle; flight muscles can make up about
  15-25 % of a flying bird's body mass ("up to a quarter").
- Many bird bones are hollow (pneumatized), braced inside by thin struts: light but stiff.
- Common swifts (Apus apus) can stay airborne for about 10 months of their non-breeding period without landing
  (some individuals never landed in that time); they feed on flying insects on the wing.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def open_sky(c, t, seed=1):
    sky(c, '#7cc4ff', '#d8efff')
    clouds(c, t, seed=seed, n=4, y0=620, y1=1500, speed=60)

def air_push(c, x, y, ang, k, t, colr='#ffffff', n=3, L=180):
    """a few short streaks pushed in direction ang (deg)."""
    if k <= 0: return
    rd = math.radians(ang)
    for i in range(n):
        ph = (t * 1.6 + i / n) % 1.0
        ox = -math.sin(rd) * (i - 1) * 50; oy = math.cos(rd) * (i - 1) * 50
        sx = x + ox + math.cos(rd) * L * ph; sy = y + oy + math.sin(rd) * L * ph
        arrow(c, sx, sy, sx + math.cos(rd) * 70, sy + math.sin(rd) * 70, colr=colr, w=9, alpha=int(230 * k * (1 - ph)))

# ---------- 1: Hook (cold open: bird already flapping) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    open_sky(c, t)
    ph = (t * 1.6) % 1.0
    by = 1080 - 30 * math.sin(ph * 2 * math.pi)
    bird(c, 540, by, 1.5, t, flap=ph, rot=-4)
    if t > t1:
        down = 0.5 + 0.5 * math.sin((ph - 0.25) * 2 * math.pi)
        air_push(c, 470, 1180, 120, down, t, colr=SKYB)
        label_pill(c, 'air goes DOWN + BACK', 540, 1560, size=44, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'not just UP and DOWN', 540, 700, size=46, k=ease_back(prog(t, 0.5, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.5, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 2: Wing = airfoil, deflects air down -> lift ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    open_sky(c, t, seed=3)
    gk = ease_back(prog(t, t0 + 0.2, 0.5))
    if gk > 0:
        bird(c, 540 + 10 * math.sin(t), 880, 0.75 * gk, t, glide=True)
    # zoomed wing section
    sk = ease_out(prog(t, t0 + 1.0, 0.6))
    if sk > 0:
        c.drawRoundRect(skia.Rect(110, 1060, 970, 1500), 50, 50, P(color=col('#ffffff', int(90 * sk))))
        draw_airfoil(c, 540, 1260, 520 * sk, aoa=8, alpha=int(255 * sk))
        # streamlines bending down behind the wing
        for i in range(5):
            yy = 1150 + i * 50; p = skia.Path(); p.moveTo(150, yy)
            p.cubicTo(400, yy - 20, 650, yy + 10, 930, yy + 90 + i * 8)
            c.drawPath(p, P(color=col(SKYB, int(200 * sk)), stroke=6))
            ph = (t * 0.7 + i * 0.2) % 1.0
            c.drawCircle(lerp(150, 930, ph), yy + (90 + i * 8) * ph ** 2 - 10 * math.sin(ph * math.pi), 9, P(color=col('#ffffff', int(255 * sk))))
        label_pill(c, 'CURVED wing', 300, 1450, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        lk = ease_out(prog(t, t1 + 0.6, 0.6))
        arrow(c, 860, 1470, 860, 1470 + 110 * lk, colr=SKYB, w=16)
        arrow(c, 560, 1200, 560, 1200 - 150 * lk, colr=HOT, w=20)
        label_pill(c, 'LIFT', 720, 1090, size=48, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.4, 'pop'), (t1 + 0.6, 'whoosh'), (t1 + 1.0, 'pop')]

# ---------- 3: Downstroke = power stroke (aha) ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    open_sky(c, t, seed=5)
    # slow-motion downstroke, looping
    ph = 0.05 + 0.45 * ease_in_out(((t - t0) * 0.5) % 1.0) if t > t0 else 0.05
    drift = 80 * ease_in_out(prog(t, t1, 2.5))
    bx, by = 500 + drift, 1150 - drift * 0.8
    bird(c, bx, by, 1.6, t, flap=ph)
    label_pill(c, 'DOWNSTROKE = power', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        k = ease_out(prog(t, t1 + 0.2, 0.6))
        arrow(c, bx - 80, by + 160, bx - 80 - 190 * k, by + 160 + 190 * k, colr=SKYB, w=20)
        label_pill(c, 'air', bx - 280, by + 400, size=40, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi=SKYB)
        k2 = ease_out(prog(t, t1 + 1.0, 0.6))
        arrow(c, bx + 160, by - 160, bx + 160 + 170 * k2, by - 160 - 170 * k2, colr=HOT, w=22)
        label_pill(c, 'UP + FORWARD', 640, 1560, size=46, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi=HOT)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 1.0, 'ding'), (t1 + 1.4, 'pop')]

# ---------- 4: Upstroke: wing folds, feathers let air through ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    open_sky(c, t, seed=7)
    ph = 0.5 + 0.5 * ease_in_out(((t - t0 + 0.4) * 0.45) % 1.0)
    bird(c, 540, 1120, 1.6, t, flap=ph)
    # air slipping through the folded wing
    k = prog(t, t0 + 1.0, 0.5)
    for i in range(4):
        pp = (t * 0.9 + i / 4) % 1.0
        x = lerp(380, 700, (i + 0.5) / 4); y = lerp(1300, 700, pp)
        c.drawCircle(x + 10 * math.sin(t * 3 + i), y, 8, P(color=col('#ffffff', int(220 * k * math.sin(pp * math.pi)))))
    label_pill(c, 'UPSTROKE: wing folds', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'feathers let air THROUGH', 540, 1560, size=42, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.5, 'pop'), (t0 + 1.0, 'whoosh'), (t0 + 2.2, 'pop')]

# ---------- 5: Huge chest muscles ----------
def pie(c, x, y, r, frac, colr=HOT, k=1.0):
    if k <= 0: return
    c.drawCircle(x, y, r * k, P(color=col('#ffffff', 235)))
    c.drawArc(skia.Rect(x - r * k * 0.86, y - r * k * 0.86, x + r * k * 0.86, y + r * k * 0.86), -90, 360 * frac, True, P(color=col(colr)))
    c.drawCircle(x, y, r * k, P(color=col(NAVY), stroke=6))

def s5(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#7cc4ff')
    ph = 0.25 + 0.2 * math.sin(t * 2.2)
    bird(c, 420, 1150, 1.6, t, flap=ph)
    mk = ease_out(prog(t, t0 + 0.6, 0.6))
    if mk > 0:
        # chest muscle highlight drawn over the body
        c.save(); c.translate(420, 1150); c.scale(1.6, 1.6)
        mp = skia.Path(); mp.addOval(skia.Rect(-10, -30, 110, 38))
        c.drawPath(mp, P(color=col(HOT, int(150 * mk + 40 * mk * math.sin(t * 5)))))
        c.drawPath(mp, P(color=col('#ffffff', int(220 * mk)), stroke=4))
        c.restore()
    pie(c, 830, 760, 95, 0.25 * ease_out(prog(t, t0 + 1.6, 1.0)), k=ease_back(prog(t, t0 + 1.4, 0.4)))
    label_pill(c, 'CHEST muscles', 330, 720, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'up to 1/4 of its WEIGHT', 540, 1560, size=44, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=GOLD)

def s5_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.4, 'pop'), (t0 + 1.6, 'whoosh'), (t0 + 2.6, 'pop')]

# ---------- 6: Hollow bones ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#7cc4ff')
    sec = ease_in_out(prog(t, t0 + 1.0, 0.8))
    bk = ease_back(prog(t, t0 - 0.1, 0.5))
    hollow_bone(c, 540, 1080 + 10 * math.sin(t * 1.5), 1.15 * bk, section=sec)
    label_pill(c, 'HOLLOW inside', 540, 760, size=50, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        lk = ease_back(prog(t, t1 + 0.3, 0.4))
        arrow(c, 700, 1400, 640, 1120, colr=HOT, w=12, alpha=int(255 * min(1, lk)))
        label_pill(c, 'STRUTS for strength', 650, 1480, size=44, k=lk, fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 - 0.1, 'whoosh'), (t0 + 1.0, 'click'), (t0 + 1.2, 'pop'), (t1 + 0.3, 'pop')]

# ---------- 7: Wild part: swifts stay up for 10 months ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a6a', '#7cc4ff')
    clouds(c, t, seed=9, n=3, y0=900, y1=1500, speed=90)
    for i in range(3):
        x = 300 + i * 220 + 60 * math.sin(t * 0.8 + i * 2); y = 1050 + i * 90 + 40 * math.cos(t * 1.1 + i)
        swift_bird(c, x, y, 0.55 - 0.1 * i, t + i, rot=20 * math.sin(t * 0.7 + i))
    months = int(10 * ease_in_out(prog(t, t0 + 1.0, 3.0)))
    mk = ease_back(prog(t, t0 + 0.8, 0.4))
    if mk > 0:
        label_pill(c, f'{months} MONTHS in the air', 540, 700, size=48, k=mk, fill=NAVY, hi=GOLD)
    if t > t1:
        # insects caught on the wing
        for i in range(6):
            ix = 200 + i * 120 + 20 * math.sin(t * 4 + i); iy = 860 + 30 * math.cos(t * 3 + i)
            c.drawCircle(ix, iy, 5, P(color=col(NAVY, 200)))
        label_pill(c, 'eats ON THE WING', 540, 1560, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.8, 'pop'), (t0 + 1.0, 'whoosh'), (t1 + 0.4, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    open_sky(c, t, seed=11)
    bird(c, 540 + 40 * math.sin(t * 0.8), 1180 + 20 * math.sin(t * 2), 1.0, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'push air DOWN + BACK', 540, 700, size=44, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: why METAL feels cold', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
        slab(c, 400, 940, 280 * kk, 70 * kk, 'metal')
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do birds fly?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do birds actually fly?', 'How do BIRDS fly?'),
            ("It's not just flapping up and down. Every beat throws air down and back.", 'Air goes DOWN and back')], tail=0.9),
        dict(name='wing', draw=s2, sfx_fn=s2_sfx, lines=[
            ("A bird's wing is curved, a lot like an airplane wing.", 'Curved like a PLANE wing'),
            ('Moving through the air, it bends air downward, and that pushes the bird up.', 'Air down, bird UP')], tail=1.0),
        dict(name='down', draw=s3, sfx_fn=s3_sfx, trans='punch', lines=[
            ('The downstroke is the power stroke.', 'DOWNSTROKE = power'),
            ('It shoves air down and backward, so the bird goes up and forward.', 'Bird goes UP and FORWARD')], tail=1.1),
        dict(name='up', draw=s4, sfx_fn=s4_sfx, lines=[
            ('On the way back up, the wing folds in, and the feathers twist apart to let air slip through.', 'Upstroke: wing FOLDS')], tail=1.1),
        dict(name='muscle', draw=s5, sfx_fn=s5_sfx, lines=[
            ("All that flapping takes huge chest muscles, up to a quarter of the bird's weight.", 'Up to 1/4 of its WEIGHT')], tail=1.1),
        dict(name='bones', draw=s6, sfx_fn=s6_sfx, lines=[
            ('And many of its bones are hollow,', 'HOLLOW bones'),
            ('braced inside with thin struts. Light, but strong.', 'Light but STRONG')], tail=1.0),
        dict(name='swift', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: the common swift can stay in the air for about ten months.", '10 MONTHS without landing'),
            ('It even eats insects on the wing.', 'It eats ON THE WING')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So birds fly by pushing air down and back with every beat.', 'Push air DOWN and back'),
            ('Next: why metal feels colder than wood.', 'Next: why METAL feels cold'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
