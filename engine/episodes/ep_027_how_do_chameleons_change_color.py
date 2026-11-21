"""Episode 27 (EN, general audience): How do chameleons change color?
Facts checked (Teyssier et al. 2015, Nature Communications 6:6368 "Photonic crystals cause active colour change in
chameleons"; University of Geneva press release 2015-03-10; Scientific American "The secret to chameleons' ability
to change color"; Nature news 519:265):
- Chameleon skin has a superficial layer of iridophore cells containing a lattice of guanine nanocrystals.
- Tight crystal spacing (relaxed animal) reflects short wavelengths (blue); when the animal is excited the lattice
  expands, so longer wavelengths (yellow, orange, red) are reflected. It is an active, reversible change.
- Yellow pigment cells (xanthophores) sit on top; blue reflected light seen through the yellow layer looks green.
- This is structural colour, the same principle as soap bubbles or peacock feathers (colour from structure).
- The big colour changes serve mainly social signalling (rivals, mates) and also respond to temperature;
  camouflage comes mostly from their baseline colouring, not from matching backgrounds.
- A deeper layer of larger, less ordered crystals reflects much of the sunlight's near-infrared; the authors
  suggest this gives passive heat protection.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def jungle_bg(c, t, top='#e6fff0', bot='#c7efd6'):
    sky(c, top, bot)
    dust(c, t, seed=5, n=14, a=70, colr='#ffffff')

def pulse_k(t, start, dur=2.0):
    return ease_in_out(prog(t, start, dur))

def skin_stack(c, x0, y0, w_, spacing, t, show_top=1.0, show_deep=0.0, light_k=1.0, rays=True):
    """Cross-section: yellow pigment layer (top), crystal layer (middle), optional deep layer, dark base."""
    hp, hc, hd = 90, 300, 150
    yc = y0 + hp; yd = yc + hc
    c.save()
    rr = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x0 + w_, yd + hd), 30, 30)
    c.clipRRect(rr, doAntiAlias=True)
    c.drawRect(skia.Rect(x0, y0, x0 + w_, yd + hd), P(color=col('#2a3550')))
    # crystal layer
    c.drawRect(skia.Rect(x0, yc, x0 + w_, yd), lin(c, (0, yc, 0, yd), [col('#e9f4ff'), col('#cfe2f5')]))
    crystal_lattice(c, x0, yc, w_, hc, spacing, t, r=10)
    # deep layer: bigger messy crystals
    if show_deep > 0:
        rnd = random.Random(7)
        c.drawRect(skia.Rect(x0, yd, x0 + w_, yd + hd), P(color=col('#cfd6e6', int(255 * show_deep))))
        for i in range(16):
            px, py = x0 + rnd.uniform(20, w_ - 20), yd + rnd.uniform(25, hd - 25)
            c.drawPath(hexagon_path(px, py, rnd.uniform(16, 26)), P(color=col('#f5f9ff', int(255 * show_deep))))
            c.drawPath(hexagon_path(px, py, rnd.uniform(16, 26)), P(color=col('#8a9bb8', int(200 * show_deep)), stroke=2))
    # yellow pigment layer
    if show_top > 0:
        c.drawRect(skia.Rect(x0, y0, x0 + w_, yc), P(color=col('#ffd23f', int(235 * show_top))))
        rnd = random.Random(3)
        for i in range(14):
            c.drawCircle(x0 + rnd.uniform(10, w_ - 10), y0 + rnd.uniform(18, hp - 18), rnd.uniform(9, 15), P(color=col('#f0b400', int(220 * show_top))))
    c.restore()
    c.drawRRect(rr, P(color=col(NAVY), stroke=6))
    return yc, yd

def light_in_out(c, x, ytop, ybounce, t, start, out_col, alpha=255, dx=110):
    """White light ray coming in, coloured ray reflected out."""
    k1 = ease_out(prog(t, start, 0.6)); k2 = ease_out(prog(t, start + 0.6, 0.6))
    if k1 > 0:
        arrow(c, x - dx, ytop - 220, lerp(x - dx, x, k1), lerp(ytop - 220, ybounce, k1), colr=NAVY, w=20, alpha=alpha)
        arrow(c, x - dx, ytop - 220, lerp(x - dx, x, k1), lerp(ytop - 220, ybounce, k1), colr='#ffffff', w=13, alpha=alpha)
    if k2 > 0:
        arrow(c, x, ybounce, lerp(x, x + dx, k2), lerp(ybounce, ytop - 220, k2), colr=NAVY, w=20, alpha=alpha)
        arrow(c, x, ybounce, lerp(x, x + dx, k2), lerp(ybounce, ytop - 220, k2), colr=out_col, w=13, alpha=alpha)

# ---------- 1: Hook (cold open: chameleon already shifting colour) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    jungle_bg(c, t)
    k = 0.5 - 0.5 * math.cos(t * 1.3)
    branch(c, -40, 1290, 1120, 1250, t=t)
    chameleon(c, 520, 1150, 1.2, t, colr=cham_color(k))
    label_pill(c, 'not PAINT', 300, 760, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.9, 0.5), 2.2)
        if kk > 0:
            c.save(); c.translate(720, 770); c.scale(kk, kk)
            c.drawRoundRect(skia.Rect(-190, -70, 190, 70), 35, 35, P(color=col('#ffffff', 240)))
            crystal_lattice(c, -170, -55, 120, 110, 0.15, t, r=8, clip=True)
            text_block(c, 'CRYSTALS', 55, 0, size=48, fill=NAVY, hi='#2f9bff', stroke='#ffffff')
            c.restore()

def s1_sfx(D, cues): return [(0.0, 'sparkle'), (0.3, 'pop'), (cues[1]['start'] + 0.9, 'pop')]

# ---------- 2: Myth: not mainly hiding; messages ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    if t < t1:
        # chameleon on a checkerboard of colours, trying to match: big X
        c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#f4f1ea')))
        cols_ = ['#ff5c85', '#2f9bff', '#ffd23f', '#3fbf6a']
        for j in range(9):
            for i in range(6):
                c.drawRect(skia.Rect(i * 180, 620 + j * 110, i * 180 + 180, 620 + j * 110 + 110), P(color=col(cols_[(i + j) % 4], 120)))
        branch(c, -40, 1290, 1120, 1250, t=t, leaves=False)
        chameleon(c, 540, 1150, 1.05, t, colr=CHAM_GREEN)
        label_pill(c, 'to HIDE?', 540, 760, size=50, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#ff5c85')
        xk = ease_back(prog(t, t0 + 2.4, 0.4))
        if xk > 0:
            c.save(); c.translate(540, 1050); c.scale(xk, xk)
            c.drawLine(-120, -120, 120, 120, P(color=col('#e8264f'), stroke=30)); c.drawLine(120, -120, -120, 120, P(color=col('#e8264f'), stroke=30))
            c.restore()
    else:
        jungle_bg(c, t, top='#fff3e6', bot='#ffe0c7')
        branch(c, -40, 1350, 1120, 1330, t=t)
        e = pulse_k(t, t1 + 0.6, 1.2)
        chameleon(c, 280, 1230, 0.75, t, colr=cham_color(0.15 + 0.8 * e))
        chameleon(c, 800, 1230, 0.75, t, colr=cham_color(0.1 + 0.7 * e), flip=True)
        for i, (w, x, y, dt) in enumerate((('RIVALS', 280, 820, 1.2), ('MATES', 800, 820, 2.0), ('TEMPERATURE', 540, 1560, 2.8))):
            label_pill(c, w, x, y, size=44, k=ease_back(prog(t, t1 + dt, 0.4)), fill=NAVY, hi='#ff6a3c')

def s2_sfx(D, cues):
    return [(cues[0]['start'] + 0.8, 'pop'), (cues[0]['start'] + 2.4, 'click'), (cues[1]['start'], 'whoosh'),
            (cues[1]['start'] + 1.2, 'pop'), (cues[1]['start'] + 2.0, 'pop'), (cues[1]['start'] + 2.8, 'pop')]

# ---------- 3: Zoom into the skin: grid of tiny crystals ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    jungle_bg(c, t)
    z = ease_in_out(prog(t, t0 + 0.2, 1.4))
    branch(c, -40, 1290 + 300 * z, 1120, 1250 + 300 * z, t=t)
    chameleon(c, 520, 1150 + 300 * z, 1.2, t, colr=CHAM_GREEN, alpha=255 * (1 - 0.6 * z))
    mk = ease_back(prog(t, t0 + 0.8, 0.6))
    if mk > 0:
        c.save(); c.translate(540, 1000); c.scale(mk, mk)
        c.drawCircle(0, 0, 300, P(color=col('#000000', 50), blur=14))
        c.save(); c.clipPath(skia.Path().addCircle(0, 0, 290), doAntiAlias=True)
        c.drawRect(skia.Rect(-300, -300, 300, 300), lin(c, (0, -300, 0, 300), [col('#e9f4ff'), col('#cfe2f5')]))
        crystal_lattice(c, -300, -300, 600, 600, 0.1 + 0.03 * math.sin(t * 2), t, r=14, clip=False)
        c.restore()
        c.drawCircle(0, 0, 290, P(color=col(NAVY), stroke=18))
        c.drawLine(205, 205, 300, 300, P(color=col(NAVY), stroke=34))
        c.restore()
        label_pill(c, 'tiny CRYSTALS', 540, 1420, size=46, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'in a neat GRID', 540, 1520, size=44, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi='#2f9bff')
        label_pill(c, 'nano-size', 760, 680, size=38, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill='#5a6a8a')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[0]['start'] + 1.8, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.4, 'pop')]

# ---------- 4: Spacing decides colour ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#eef4ff', '#dde8fb')
    sp = 0.05 if t < t1 else lerp(0.05, 0.95, ease_in_out(prog(t, t1 + 0.3, 2.4)))
    x0, y0, w_ = 140, 900, 800
    c.drawRoundRect(skia.Rect(x0, y0, x0 + w_, y0 + 420), 30, 30, lin(c, (0, y0, 0, y0 + 420), [col('#e9f4ff'), col('#cfe2f5')]))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x0 + w_, y0 + 420), 30, 30), doAntiAlias=True)
    crystal_lattice(c, x0, y0, w_, 420, sp, t, r=13, clip=False)
    c.restore()
    c.drawRoundRect(skia.Rect(x0, y0, x0 + w_, y0 + 420), 30, 30, P(color=col(NAVY), stroke=6))
    oc = crystal_color(sp)
    light_in_out(c, 540, y0, y0 + 60, t, t0 + 0.4, oc)
    if t < t1:
        label_pill(c, 'CLOSE = blue', 540, 1450, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#3a6bff')
    else:
        label_pill(c, 'SPREAD = yellow, orange, red', 540, 1450, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=oc if sp > 0.4 else '#2f9bff')
        # spacing gauge
        gx0, gx1, gy = 200, 880, 1570
        c.drawRoundRect(skia.Rect(gx0, gy - 14, gx1, gy + 14), 14, 14, lin(c, (gx0, 0, gx1, 0), [col(crystal_color(i / 5)) for i in range(6)], vertical=False))
        c.drawCircle(lerp(gx0, gx1, sp), gy, 26, P(color=col('#ffffff'))); c.drawCircle(lerp(gx0, gx1, sp), gy, 26, P(color=col(NAVY), stroke=6))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.3, 'sparkle'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 5: Yellow on top: blue + yellow = green; excited -> orange (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    jungle_bg(c, t)
    sp = 0.05 if t < t1 + 0.6 else lerp(0.05, 0.8, ease_in_out(prog(t, t1 + 0.6, 1.6)))
    x0, w_ = 90, 560
    yc, yd = skin_stack(c, x0, 760, w_, sp, t, show_top=ease_out(prog(t, t0 + 0.3, 0.6)))
    light_in_out(c, 340, 760, yc + 40, t, t0 + 1.4, crystal_color(sp), dx=100)
    # result swatch: chameleon on the right
    vis = mix_hx(CHAM_GREEN, cham_color(0.9), clamp((sp - 0.05) / 0.75))
    ck = ease_back(prog(t, t0 + 2.6, 0.5))
    if ck > 0:
        branch(c, 640, 1420, 1100, 1400, w=26, t=t, leaves=False)
        chameleon(c, 840, 1330, 0.55 * ck, t, colr=vis, flip=True)
    if t < t1:
        label_pill(c, 'BLUE + YELLOW', 360, 1400, size=44, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi='#2f9bff')
        label_pill(c, '= GREEN', 360, 1500, size=48, k=ease_back(prog(t, t0 + 2.8, 0.4)), fill=NAVY, hi='#2fa84f')
    else:
        label_pill(c, 'EXCITED', 840, 1520, size=48, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi='#ff6a3c')
        label_pill(c, 'crystals SPREAD', 360, 1450, size=44, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi='#ff9f1c')

def s5_sfx(D, cues):
    return [(cues[0]['start'] + 0.3, 'pop'), (cues[0]['start'] + 1.4, 'whoosh'), (cues[0]['start'] + 2.0, 'pop'), (cues[0]['start'] + 2.8, 'pop'),
            (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.2, 'ding')]

# ---------- 6: Structural colour, like soap bubbles and peacock feathers ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f1f4ff', '#e4e9fb')
    bk = ease_back(prog(t, t0 + 0.3, 0.6))
    if bk > 0:
        soap_bubble(c, 300, 1060 - 30 * math.sin(t * 1.2), 190 * bk, t)
        label_pill(c, 'soap BUBBLE', 300, 1340, size=42, k=bk, fill=NAVY, hi='#9b4dff')
    fk = ease_back(prog(t, t0 + 1.6, 0.6))
    if fk > 0:
        feather(c, 760, 1150, 0.95 * fk, t, rot=8 * math.sin(t * 0.9))
        label_pill(c, 'PEACOCK feather', 760, 1500, size=40, k=fk, fill=NAVY, hi='#1f9e8a')
    if t > t1:
        label_pill(c, 'no DYE needed', 540, 720, size=48, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi='#ff5c85')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] + 0.5, 'sparkle')]

# ---------- 7: Wild part: deeper crystal layer reflects the sun's heat ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fff4dc', '#ffe2b8')
    sunbeams(c, 780, 720, t, a=35)
    sun(c, 780, 720, 75, t, glow=True)
    yc, yd = skin_stack(c, 140, 860, 640, 0.1, t, show_top=1.0, show_deep=ease_out(prog(t, t0 + 0.6, 0.6)))
    # heat rays (red wavy) bouncing off the deep layer
    for j in range(3):
        st = t0 + 1.6 + j * 0.5
        if t < st: continue
        u = ((t - st) % 2.0) / 2.0
        x_in = 560 + j * 70
        ybot = yd + 70
        if u < 0.5:
            v = u / 0.5; xa, ya, xb, yb = x_in + 160, 760, x_in, ybot
        else:
            v = (u - 0.5) / 0.5; xa, ya, xb, yb = x_in, ybot, x_in - 300, 700
        pth = skia.Path(); n = 30
        for i in range(n + 1):
            w = min(v, i / n * v)
            px, py = lerp(xa, xb, w), lerp(ya, yb, w)
            nx, ny = -(yb - ya), (xb - xa); L = math.hypot(nx, ny) or 1
            off = 10 * math.sin(i * 1.2 - t * 12)
            (pth.moveTo if i == 0 else pth.lineTo)(px + nx / L * off, py + ny / L * off)
        c.drawPath(pth, P(color=col('#ff5c3b', 220), stroke=8))
    label_pill(c, 'DEEP crystal layer', 460, 1470, size=42, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#5a6a8a')
    if t > t1:
        label_pill(c, 'built-in SUNSHADE', 460, 1565, size=46, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#ff6a3c')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 1.6, 'whoosh'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    jungle_bg(c, t)
    k = 0.5 - 0.5 * math.cos(t * 1.1)
    branch(c, -40, 1170, 1120, 1130, t=t)
    chameleon(c, 520, 1035, 1.0, t, colr=cham_color(k))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: SPIDER WEBS', 520, 760, size=48, k=kk, fill=NAVY, hi='#9b4dff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do chameleons change color?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do chameleons change color?', 'How do CHAMELEONS change color?'),
            ("Not with paint or ink. They use tiny crystals.", 'They use CRYSTALS')], tail=0.8),
        dict(name='myth', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Most people think they change color to hide. Mostly, they don\'t.', 'Not mainly to HIDE'),
            ('Their color shows are messages to rivals and mates, and a reaction to temperature.', 'MESSAGES and temperature')], tail=0.8),
        dict(name='crystals', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Just under the surface of their skin is a layer of cells packed with tiny crystals,', 'A layer of tiny CRYSTALS'),
            ('lined up in a neat grid.', 'in a neat GRID')], tail=0.8),
        dict(name='spacing', draw=s4, sfx_fn=s4_sfx, lines=[
            ('When the crystals sit close together, they reflect blue light.', 'Close together: BLUE'),
            ('Spread them apart, and they reflect yellow, orange or red instead.', 'Spread apart: ORANGE, red')], tail=1.0),
        dict(name='green', draw=s5, sfx_fn=s5_sfx, lines=[
            ('On top sits a layer of yellow pigment. Blue light through yellow looks green.', 'Blue + yellow = GREEN'),
            ('So when a chameleon gets excited, the crystals spread, and green turns orange.', 'Excited = crystals SPREAD')], tail=1.2),
        dict(name='structure', draw=s6, sfx_fn=s6_sfx, lines=[
            ("It's the same trick as a soap bubble or a peacock feather:", 'Same trick as a BUBBLE'),
            ('color made by structure, not by dye.', 'Color from STRUCTURE')], tail=0.8),
        dict(name='sunshade', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: a second, deeper layer of bigger crystals reflects much of the sun's heat.", 'A DEEP layer reflects heat'),
            ('Scientists think it works like a built-in sunshade.', 'A built-in SUNSHADE')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So chameleons change color by tuning tiny crystals in their skin.', 'They TUNE tiny crystals'),
            ('Next up: how spiders make webs.', 'Next: SPIDER webs'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
