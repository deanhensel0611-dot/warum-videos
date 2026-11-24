"""Episode 40 (EN, general audience): How can owls turn their heads so far?
Facts checked (Johns Hopkins Medicine study de Kok-Mercado et al., Science 2013, reported by National Geographic "How
owls twist their heads almost 360 degrees", NPR "How owls spin their heads without tearing arteries", Smithsonian
Magazine "Solving the mystery of owls' head-turning abilities", Live Science "Biological twist", Discover Magazine;
barn owl hearing: Cornell Lab / Audubon, Knudsen & Konishi):
- Owls can rotate their heads up to 270 degrees in either direction. A human neck turns roughly 70-90 degrees.
- Owl eyes are elongated tubes held in place by bony sclerotic rings; they cannot roll in their sockets, so the
  owl turns its whole head instead.
- Owls have 14 neck vertebrae (humans 7), and like all birds a single occipital condyle (one pivot point).
- In the neck the vertebral artery runs through bony holes that are about 10x wider than the artery, leaving
  room / an air cushion so it is not pinched when twisted (humans: holes about as wide as the artery).
- Blood vessels at the base of the head can widen to pool blood (reservoirs), keeping the brain and eyes supplied
  while the head is turned; small connections between vessels let blood take another route if one is squeezed.
- Barn owls have asymmetric ear openings (one higher than the other), so tiny differences in arrival time and
  loudness let them locate prey in total darkness.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
BLOOD = '#e8264f'

def dusk(c, t):
    sky(c, '#1c2a5a', '#5a6fb0', mid='#34478a')
    stars(c, t, seed=31, n=50, y0=600, y1=1100, a=0.7)

def soft_bg(c, t, top='#eef6ff', bot='#d6e9fb'):
    sky(c, top, bot); dust(c, t, seed=8, n=10, a=60)

def dial(c, x, y, r, deg, k=1.0):
    """Angle dial: arc swept by the head turn."""
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawCircle(0, 0, r, P(color=col('#ffffff', 60), stroke=6))
    p = skia.Path(); p.addArc(skia.Rect(-r, -r, r, r), -90, max(1, deg))
    c.drawPath(p, P(color=col('#ffd23f'), stroke=14))
    a = math.radians(-90 + deg)
    c.drawCircle(math.cos(a) * r, math.sin(a) * r, 14, P(color=col('#ffd23f')))
    text_block(c, f'{int(deg)}°', 0, 0, size=64, fill='#ffffff', stroke=NAVY)
    c.restore()

# ---------- 1: Hook (cold open: owl mid-turn) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    dusk(c, t)
    branch(c, -40, 1420, 900, 1440, w=46, t=t, leaves=False)
    # head sweeps 0 -> 270 and back, slow ease
    ph = (t * 0.35) % 2.0
    u = ease_in_out(ph if ph < 1 else 2 - ph)
    yaw = 270 * u
    owl(c, 430, 1425, 1.15, t, yaw=yaw)
    dial(c, 800, 820, 110, yaw, k=ease_back(prog(t, 0.2, 0.4)))
    if t > t1:
        label_pill(c, 'you: about 80°', 330, 1560, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.2, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 2: Eyes are tubes, fixed in bone ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    k1 = ease_back(prog(t, t0 + 0.2, 0.5))
    # human eyeball for comparison (rolls)
    if k1 > 0:
        c.save(); c.translate(290, 1100); c.scale(k1, k1)
        c.drawCircle(0, 0, 130, rad(-30, -30, 170, [col('#ffffff'), col('#e6ecf5')]))
        roll = 40 * math.sin(t * 2.4)
        c.drawCircle(roll, -20, 52, P(color=col('#5b8fd6')))
        c.drawCircle(roll, -20, 24, P(color=col('#0b0b10')))
        c.drawCircle(0, 0, 130, P(color=col('#9fb0c8'), stroke=5))
        c.restore()
        label_pill(c, 'ours ROLL', 290, 1330, size=38, k=k1, fill=NAVY, hi=SKYB)
    k2 = ease_back(prog(t, t0 + 1.2, 0.5))
    if k2 > 0:
        owl_eye_section(c, 760, 1110, 1.05 * k2)
        label_pill(c, 'owl: a TUBE', 760, 1400, size=38, k=k2, fill=NAVY, hi=HOT)
    label_pill(c, "owl eyes can't MOVE", 540, 720, size=44, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        rk = ease_back(prog(t, t1 + 0.4, 0.4))
        # highlight the bony ring
        for side in (-1, 1):
            c.drawRoundRect(skia.Rect(760 + side * 74 * 1.05 - 26, 1110 - 120 * 1.05, 760 + side * 74 * 1.05 + 26, 1110 - 20 * 1.05), 12, 12,
                            P(color=col('#ffd23f', int(255 * min(1, rk))), stroke=6))
        label_pill(c, 'locked in BONE', 760, 860, size=38, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=GOLD)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.6, 'pop'), (t0 + 1.2, 'pop'), (t1 + 0.4, 'click'), (t1 + 0.8, 'pop')]

# ---------- 3: 14 neck bones vs 7, one pivot ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t, top='#fff4e6', bot='#ffe3c4')
    n_owl = int(14 * prog(t, t0 + 0.4, 1.4) + 0.999)
    tw = 60 * math.sin(t * 1.6) * prog(t, t0 + 2.0, 0.6)
    if n_owl > 0:
        y0, y1 = 820, 1520
        vertebra_chain(c, 330, y1 - (y1 - y0) * n_owl / 14, y1, n_owl, t, twist=tw)
    k7 = prog(t, t0 + 1.8, 0.6)
    if k7 > 0:
        vertebra_chain(c, 760, 1520 - 350 * ease_out(k7), 1520, 7, t, alpha=int(255 * k7))
    label_pill(c, 'OWL: 14', 330, 1610, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'YOU: 7', 760, 1610, size=44, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        pk = ease_back(prog(t, t1 + 0.3, 0.5))
        c.drawCircle(330, 790, 34 * pk, P(color=col('#ffd23f')))
        c.drawCircle(330, 790, 34 * pk, P(color=col(NAVY), stroke=5))
        label_pill(c, 'ONE pivot', 520, 740, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4 + i * 0.1, 'click') for i in range(0, 14, 3)] + [(t0 + 1.0, 'pop'), (t0 + 2.0, 'pop'), (t1 + 0.3, 'pop')]

# ---------- 4: Wide bony tunnels for the artery ----------
def tunnel(c, x, y, R, art_r, slide, k=1.0, label=None):
    """Cross-section: bone ring with a hole of radius R, artery (radius art_r) sliding inside."""
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawCircle(0, 0, R + 60, rad(-20, -20, R + 90, [col('#fffaf0'), col('#e8dcc4')]))
    c.drawCircle(0, 0, R + 60, P(color=col('#b08a5a'), stroke=5))
    c.drawCircle(0, 0, R, P(color=col('#dfeaf7')))
    c.drawCircle(0, 0, R, P(color=col('#b08a5a'), stroke=5))
    ax = slide * max(0, R - art_r)
    c.drawCircle(ax, 0, art_r, rad(ax - art_r * 0.3, -art_r * 0.3, art_r * 1.4, [col('#ff8fa6'), col(BLOOD), col('#a8172a')], [0, 0.55, 1]))
    c.restore()

def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # twisting neck pinching a hose analogy (line 1)
    k = ease_back(prog(t, t0 + 0.2, 0.5))
    tw = prog(t, t0 + 0.8, 1.2)
    if t < t1 + 0.3:
        fo = 1 - prog(t, t1, 0.3)
        c.saveLayerAlpha(None, int(255 * fo))
        p = skia.Path(); p.moveTo(240, 1150)
        p.cubicTo(400, 1150 - 140 * tw, 680, 1150 + 140 * tw, 840, 1150)
        wd = lerp(46, 14, tw) * k
        c.drawPath(p, P(color=col('#a8172a'), stroke=wd + 8)); c.drawPath(p, P(color=col(BLOOD), stroke=wd))
        c.drawCircle(540, 1150, 70 * tw, P(color=col('#ffd23f', int(220 * tw)), stroke=8))
        label_pill(c, 'twist = PINCH?', 540, 900, size=44, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
        c.restore()
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.3, 0.5))
        slide = math.sin(t * 2.2)
        tunnel(c, 300, 1120, 42, 34, slide * 0.0, kk)
        tunnel(c, 750, 1120, 130, 34, slide, kk)
        label_pill(c, 'YOU', 300, 1330, size=38, k=kk, fill=NAVY, hi=SKYB)
        label_pill(c, 'OWL', 750, 1330, size=38, k=kk, fill=NAVY, hi=HOT)
        label_pill(c, '~10x WIDER tunnel', 540, 780, size=44, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'room to SLIDE', 750, 1430, size=36, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi=SKYB)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'pop'), (t0 + 0.8, 'whoosh'), (t0 + 1.4, 'boing'), (t1 + 0.3, 'pop'), (t1 + 1.2, 'pop'), (t1 + 2.0, 'pop')]

# ---------- 5: Blood reservoirs at the base of the head (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # simplified head silhouette (owl head outline) with vessels coming up from the neck
    hk = ease_out(prog(t, t0, 0.5))
    c.save(); c.translate(0, 60 * (1 - hk))
    head = skia.Path(); head.addOval(skia.Rect(250, 700, 830, 1180))
    c.drawPath(head, P(color=col('#a8774a', int(70 * hk))))
    c.drawPath(head, P(color=col('#a8774a', int(200 * hk)), stroke=6))
    c.drawRect(skia.Rect(420, 1160, 660, 1640), P(color=col('#a8774a', int(50 * hk))))
    # vessels
    bulge = ease_out(prog(t, t0 + 1.2, 1.0)) * (0.85 + 0.15 * math.sin(t * 5))
    for side in (-1, 1):
        x = 540 + side * 70
        v = skia.Path(); v.moveTo(x, 1640); v.lineTo(x, 1180); v.cubicTo(x, 1050, x + side * 120, 980, x + side * 140, 880)
        c.drawPath(v, P(color=col('#a8172a', int(255 * hk)), stroke=30)); c.drawPath(v, P(color=col(BLOOD, int(255 * hk)), stroke=22))
        r = 26 + 40 * bulge
        c.drawCircle(x, 1200, r, rad(x - r * 0.3, 1200 - r * 0.3, r * 1.4, [col('#ff8fa6', int(255 * hk)), col(BLOOD, int(255 * hk)), col('#a8172a', int(255 * hk))], [0, 0.55, 1]))
        # flowing blood dots
        meas = skia.PathMeasure(v, False); L = meas.getLength()
        for j in range(6):
            u = ((t * 0.45) + j / 6) % 1.0; pos, _ = meas.getPosTan(L * u)
            if pos is not None:
                px, py = pos; c.drawCircle(px, py, 7, P(color=col('#ffd0dc', int(220 * hk))))
    # eyes + brain targets
    for ex in (420, 660):
        c.drawCircle(ex, 880, 44, P(color=col('#ffc21f', int(255 * hk))))
        c.drawCircle(ex, 880, 20, P(color=col('#0b0b10', int(255 * hk))))
    c.restore()
    label_pill(c, 'blood RESERVOIRS', 540, 1300, size=42, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        gk = prog(t, t1 + 0.8, 0.5)
        for ex in (420, 660):
            c.drawCircle(ex, 880 + 60 * (1 - hk), 80, rad(ex, 880, 80, [col('#fff36b', int(150 * gk)), col('#fff36b', 0)]))
        label_pill(c, 'eyes + brain stay SUPPLIED', 540, 640, size=38, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.2, 'boing'), (t0 + 1.6, 'pop'), (t1 + 0.8, 'ding')]

# ---------- 6: Detours (backup roads) ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    soft_bg(c, t)
    # two parallel vessels with cross-links; one gets squeezed
    xA, xB, ya, yb = 360, 720, 760, 1520
    k = ease_out(prog(t, t0, 0.5))
    sq = ease_in_out(prog(t, t0 + 1.4, 0.8))
    links = [(980,), (1180,), (1380,)]
    for x in (xA, xB):
        c.drawLine(x, ya, x, yb, P(color=col('#a8172a', int(255 * k)), stroke=34))
        c.drawLine(x, ya, x, yb, P(color=col(BLOOD, int(255 * k)), stroke=26))
    lk = prog(t, t0 + 0.6, 0.6)
    for (y,) in links:
        c.drawLine(xA, y, lerp(xA, xB, lk), y, P(color=col('#a8172a', int(255 * k)), stroke=20))
        c.drawLine(xA, y, lerp(xA, xB, lk), y, P(color=col(BLOOD, int(255 * k)), stroke=13))
    # clamp on vessel B between y 1050 and 1150
    if sq > 0:
        for side in (-1, 1):
            c.drawRoundRect(skia.Rect(xB + side * lerp(70, 18, sq) - 16 + (16 if side < 0 else -16) * 0, 1060, xB + side * lerp(70, 18, sq) + 16, 1110), 10, 10, P(color=col(NAVY)))
        c.drawLine(xB - 20, 1085, xB + 20, 1085, P(color=col('#ffffff', int(255 * sq)), stroke=10))
    # blood particles: travel up B; when squeezed, detour via link at 1180 -> A -> link at 980 -> B
    for j in range(10):
        u = ((t * 0.32) + j / 10) % 1.0
        y = lerp(yb, ya, u)
        if sq < 0.5 or y > 1180 or y < 980:
            x = xB
        else:
            x = xA
        if sq >= 0.5 and 1170 < y < 1190: x = lerp(xB, xA, (1190 - y) / 20)
        c.drawCircle(x, y, 10, P(color=col('#ffd0dc', int(230 * k))))
    label_pill(c, 'squeezed', xB + 130, 1000, size=34, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'a DETOUR', 540, 700, size=46, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'like BACKUP roads', 540, 1620, size=42, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi=GOLD)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.4, 'click'), (t0 + 2.4, 'pop'), (t1 + 0.4, 'pop')]

# ---------- 7: Wild part: barn owl's lopsided ears ----------
def mouse(c, x, y, s, t, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    tl = skia.Path(); tl.moveTo(-60, 10); tl.cubicTo(-120, 0, -140, 50, -190, 30)
    c.drawPath(tl, P(color=col('#c79aa0', a), stroke=6))
    c.drawOval(skia.Rect(-70, -30, 60, 30), lin(c, (0, -30, 0, 30), [col('#b0a8a0', a), col('#857d76', a)]))
    c.drawCircle(50, -28, 20, P(color=col('#c8bfb6', a))); c.drawCircle(50, -28, 11, P(color=col('#e8b0b8', a)))
    p = skia.Path(); p.moveTo(40, -20); p.lineTo(100, 4); p.lineTo(40, 22); p.close()
    c.drawPath(p, P(color=col('#9a928a', a)))
    c.drawCircle(72, -4, 4, P(color=col('#111111', a)))
    c.restore()

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#0b1030', '#1c2a5a')
    stars(c, t, seed=12, n=60, y0=600, y1=1600, a=0.7)
    ok = ease_out(prog(t, t0, 0.6))
    owl(c, 540, 1300 + 100 * (1 - ok), 1.05, t, yaw=0, body='#d9a96a', face='#ffffff', eyes='#2a2a30', alpha=int(255 * ok))
    hy = 1300 - 390 * 1.05
    ek = ease_back(prog(t, t0 + 1.0, 0.4))
    # ear markers: left higher, right lower
    for (ex, ey, lab) in ((540 - 140, hy - 40, 'HIGH'), (540 + 140, hy + 50, 'LOW')):
        if ek > 0:
            c.drawCircle(ex, ey, 22 * ek, P(color=col('#ffd23f')))
            c.drawCircle(ex, ey, 22 * ek, P(color=col(NAVY), stroke=5))
    label_pill(c, 'ear: HIGH', 240, hy - 140, size=36, k=ek, fill=NAVY, hi=GOLD)
    label_pill(c, 'ear: LOW', 840, hy + 150, size=36, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        mk = prog(t, t1 + 0.2, 0.4)
        mouse(c, 240, 1560, 1.0, t, alpha=int(255 * mk))
        for k_ in range(3):
            st = t1 + 0.4 + k_ * 0.5
            sound_rings(c, 250, 1540, t, st, n=1, colr='#9fd8ff', speed=520, life=1.4, w=8, a0=-80, sweep=80, both=False)
        label_pill(c, 'found in the DARK', 540, 700, size=44, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi=SKYB)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'pop'), (t0 + 1.4, 'pop'), (t1 + 0.2, 'click'), (t1 + 1.4, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    dusk(c, t)
    branch(c, -40, 1360, 900, 1380, w=46, t=t, leaves=False)
    yaw = 270 * ease_in_out((math.sin(t * 0.6) + 1) / 2)
    owl(c, 540, 1365, 1.0, t, yaw=yaw)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: SHOOTING stars', 540, 700, size=46, k=kk, fill=NAVY, hi=GOLD)
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How can owls turn their heads so far?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How can owls turn their heads so far?', 'How do OWLS turn so far?'),
            ('Up to two hundred seventy degrees. Yours stops at about eighty.', 'Up to 270 DEGREES')], tail=0.8),
        dict(name='eyes', draw=s2, sfx_fn=s2_sfx, lines=[
            ("They have to. Owl eyes can't roll around like ours. They're shaped like tubes,", "Their eyes CAN'T move"),
            ('locked in place by a ring of bone, like binoculars glued to the face.', 'Locked in BONE')], tail=0.8),
        dict(name='neck', draw=s3, sfx_fn=s3_sfx, lines=[
            ('So the whole head turns instead, on a neck with fourteen bones. You have seven.', '14 neck BONES, you have 7'),
            ('And the skull sits on a single pivot point, so it swivels smoothly.', 'ONE pivot point')], tail=0.8),
        dict(name='tunnels', draw=s4, sfx_fn=s4_sfx, lines=[
            ('But twisting that far should pinch the blood vessels in the neck, like kinking a hose.', 'Twisting should PINCH'),
            ('In owls, the main artery runs through bony tunnels about ten times wider than it is, so it can slide.', 'Tunnels 10x WIDER')], tail=1.0),
        dict(name='reservoirs', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('And at the base of the head, the vessels can balloon out and pool extra blood.', 'Built-in blood RESERVOIRS'),
            ('So the brain and the eyes keep getting blood, even mid-turn.', 'Blood keeps FLOWING')], tail=1.2),
        dict(name='detour', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Small cross-connections give the blood a detour if one path gets squeezed,', 'A DETOUR for the blood'),
            ('like a city with backup roads.', 'Like BACKUP roads')], tail=1.0),
        dict(name='ears', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: barn owls have one ear higher than the other.", 'One ear HIGHER than the other'),
            ('The tiny difference in timing tells them exactly where a mouse is, even in total darkness.', 'They hunt in the DARK')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ("So owls turn their heads because their eyes can't move, and their necks are built for it.", 'Eyes FIXED, neck built for it'),
            ('Next: what shooting stars really are.', 'Next: SHOOTING stars'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
