"""Episode 24 (EN, general audience): How do magnets work?
Facts checked (Live Science "Why do magnets have north and south poles?", Colorado State LSOP "Everything you need
to know about magnetism", HowStuffWorks "How magnets work", Physics Classroom "Magnetic poles"):
- Electrons have an intrinsic property called spin that makes each one behave like a tiny magnet (magnetic moment).
- In most materials electrons pair up with opposite spins, so their magnetism cancels.
- In ferromagnetic metals (iron, nickel, cobalt) neighbouring atoms' moments line up in regions called domains.
- Unmagnetised iron: domains point in random directions and cancel. Magnet: most domains point the same way.
- Every magnet has a north and a south pole; opposite poles attract, like poles repel. Cutting a magnet gives two
  smaller magnets, each with N and S.
- A magnet magnetises nearby steel/iron (induced magnetism): domains align, so a paperclip can hold another clip.
- Earth's field comes from moving molten iron in the outer core (geodynamo). The magnetic pole in the Arctic is,
  physically, a magnetic south pole - that's why it attracts the north end of a compass needle.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def lab_bg(c, t, top='#e9f3ff', bot='#c9e2ff'):
    sky(c, top, bot)
    dust(c, t, seed=7, n=14, a=90)

def atom(c, x, y, s, t, alpha=255, electrons=True):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    for k, ang in enumerate((0, 60, -60)):
        c.save(); c.rotate(ang)
        c.drawOval(skia.Rect(-300, -95, 300, 95), P(color=col('#2f9bff', int(a * 0.6)), stroke=6))
        if electrons:
            u = t * 0.9 + k * 2.1
            ex, ey = math.cos(u) * 300, math.sin(u) * 95
            c.drawCircle(ex, ey, 36, rad(ex, ey, 36, [col('#7cc6ff', int(a * 0.5)), col('#7cc6ff', 0)]))
            c.drawCircle(ex, ey, 18, P(color=col('#2f9bff', a)))
        c.restore()
    rnd = random.Random(2)
    for i in range(9):
        px, py = rnd.uniform(-30, 30), rnd.uniform(-30, 30)
        c.drawCircle(px, py, 24, rad(px - 8, py - 8, 34, [col('#ffffff', a), col('#ff5c85' if i % 2 else '#ffd23f', a)]))
    c.restore()

def clip_pos(i, t):
    """Hook: clip i jumps from the table up to the magnet (staggered, already in motion at t=0)."""
    start = -0.25 + i * 0.35
    u = clamp((t - start) / 0.55)
    x = 330 + i * 140
    y0, y1 = 1470, 900
    return x, lerp(y0, y1, u * u), u

# ---------- 1: Hook (cold open: clips already leaping) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    lab_bg(c, t)
    c.drawRect(skia.Rect(0, 1540, W, H), lin(c, (0, 1540, 0, H), [col('#c98a4a'), col('#8a5a2e')]))
    c.drawLine(0, 1540, W, 1540, P(color=col('#6b4423'), stroke=6))
    field_lines(c, 540, 790, 0.9, k=1.0, t=t, alpha=120, colr='#2f9bff', n=3)
    bar_magnet(c, 540, 790, 1.15)
    for i in range(4):
        x, y, u = clip_pos(i, t)
        rot = lerp(80, 0, u)
        if u >= 1: rot = math.sin(t * 6 + i) * 3
        paperclip(c, x, y + 85 if u < 1 else 950, 1.0, rot)
    label_pill(c, 'NO battery', 540, 1300, size=52, k=ease_back(prog(t, 0.5, 0.4)), fill='#e8264f', hi='#e8264f')
    if t > t1:
        label_pill(c, 'the secret: ATOMS', 540, 1400, size=46, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi='#2f9bff')

def s1_sfx(D, cues): return [(0.3, 'click'), (0.65, 'click'), (1.0, 'click'), (0.5, 'pop'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 2: Each electron is a tiny magnet; usually they cancel ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=31, n=80)
    z = ease_in_out(prog(t, 0.0, 1.4))
    atom(c, 540, 1050, lerp(1.0, 0.75, z), t, alpha=255 * (1 - 0.6 * prog(t, t0 + 1.4, 0.6)))
    k = ease_back(prog(t, t0 + 1.4, 0.5))
    if k > 0 and t < t1:
        spin_electron(c, 540, 1050, 70 * k, t, up=True)
        label_pill(c, 'SPIN', 540, 1300, size=48, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi='#d9a400')
    if t > t1:
        p = ease_in_out(prog(t, t1 + 0.1, 0.9))
        spin_electron(c, lerp(540, 420, p), 1050, 70, t, up=True)
        spin_electron(c, lerp(900, 660, p), 1050, 70, t, up=False, seed=3)
        label_pill(c, '= CANCEL', 540, 1330, size=50, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill='#e8264f', hi='#e8264f')

def s2_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[0]['start'] + 2.2, 'pop'), (cues[1]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 1.0, 'click')]

# ---------- 3: In iron they line up -> domains ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t)
    # row of atoms whose arrows swing into line
    al = ease_in_out(prog(t, t0 + 1.0, 1.4))
    fo = 1 - prog(t, t1 - 0.2, 0.5)
    if fo > 0:
        rnd = random.Random(5)
        for i in range(5):
            for j in range(3):
                x, y = 220 + i * 160, 900 + j * 180
                a0 = rnd.uniform(-180, 180); ang = math.radians(a0 * (1 - al))
                c.drawCircle(x, y, 52, P(color=col('#aeb8c7', int(255 * fo))))
                c.drawCircle(x, y, 52, P(color=col('#5b6476', int(255 * fo)), stroke=4))
                arrow(c, x - math.cos(ang) * 38, y - math.sin(ang) * 38, x + math.cos(ang) * 38, y + math.sin(ang) * 38, colr='#e8264f', w=9, alpha=int(255 * fo))
        label_pill(c, 'IRON atoms', 540, 1520, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)) * fo, fill=NAVY, hi='#5b6476')
    if t > t1 - 0.2:
        k = ease_out(prog(t, t1 - 0.2, 0.7))
        c.save(); c.translate(540, 1100); c.scale(lerp(0.7, 1.0, k), lerp(0.7, 1.0, k)); c.translate(-540, -1100)
        c.saveLayerAlpha(None, int(255 * k))
        domains(c, 90, 800, 900, 600, 0.0, t, seed=4)
        c.restore(); c.restore()
        label_pill(c, 'DOMAINS', 540, 1520, size=54, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill='#e8264f', hi='#e8264f')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 1.0, 'whoosh'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 4: Nail = random, magnet = aligned (aha) ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t)
    al = ease_in_out(prog(t, t1 + 0.3, 1.6))
    domains(c, 90, 820, 900, 560, al, t, seed=4, target=180.0)
    if t < t1:
        label_pill(c, 'iron NAIL', 540, 1500, size=50, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi='#5b6476')
    else:
        label_pill(c, 'MAGNET', 540, 1500, size=56, k=ease_back(prog(t, t1 + 1.9, 0.5), 2.2), fill='#e8264f', hi='#e8264f')
        pk = ease_back(prog(t, t1 + 2.0, 0.4))
        if pk > 0:
            for x, L, cl in ((120, 'N', MAG_N), (960, 'S', MAG_S)):
                c.save(); c.translate(x, 1100); c.scale(pk, pk)
                c.drawCircle(0, 0, 56, P(color=col(cl))); c.drawCircle(0, 0, 56, P(color=col('#ffffff'), stroke=6))
                text_block(c, L, 0, 0, size=60, fill='#ffffff', stroke=NAVY)
                c.restore()

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.9, 'ding')]

# ---------- 5: Poles: opposites attract; cut = two magnets ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t, top='#fff4ec', bot='#ffe2d2')
    if t < t1 - 0.1:
        # top pair: S | N -> attract (snap together); bottom pair: S | S -> repel
        u = prog(t, t0 + 0.6, 0.7); u = u * u
        gap = lerp(260, 0, u)
        bar_magnet(c, 540 - 190 - gap / 2, 900, 0.95, rot=0)        # S on the right
        bar_magnet(c, 540 + 190 + gap / 2, 900, 0.95, rot=0)        # N on the left
        r = ease_out(prog(t, t0 + 1.6, 0.6)); jit = math.sin(t * 30) * 4 * (1 - r)
        bar_magnet(c, 540 - 200 - lerp(20, 120, r), 1300, 0.95, rot=0)    # S on the right
        bar_magnet(c, 540 + 200 + lerp(20, 120, r) + jit, 1300, 0.95, rot=180)  # S on the left
        label_pill(c, 'ATTRACT', 540, 1050, size=44, k=ease_back(prog(t, t0 + 1.3, 0.4)), fill='#e8264f', hi='#e8264f')
        label_pill(c, 'REPEL', 540, 1450, size=44, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill=NAVY, hi='#2f9bff')
    else:
        cut = ease_in_out(prog(t, t1 + 0.9, 0.6))
        if cut <= 0:
            bar_magnet(c, 540, 1100, 1.3)
            # scissors line
            x = 540; yy = 1100
            for k in range(6):
                c.drawLine(x, yy - 160 + k * 60, x, yy - 130 + k * 60, P(color=col(NAVY), stroke=6))
        else:
            off = 90 * cut
            # left half and right half, each becomes a full N|S magnet
            for sx in (-1, 1):
                bar_magnet(c, 540 + sx * (124 + off), 1100, 1.3, w_=190, h_=120)
            label_pill(c, 'TWO magnets', 540, 1400, size=50, k=ease_back(prog(t, t1 + 1.5, 0.4)), fill='#e8264f', hi='#e8264f')

def s5_sfx(D, cues): return [(cues[0]['start'] + 1.25, 'click'), (cues[0]['start'] + 1.3, 'pop'), (cues[0]['start'] + 1.6, 'whoosh'), (cues[0]['start'] + 2.2, 'pop'), (cues[1]['start'] + 0.9, 'whoosh'), (cues[1]['start'] + 1.5, 'pop')]

# ---------- 6: Magnet magnetizes a paperclip chain ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    lab_bg(c, t)
    field_lines(c, 540, 760, 0.85, k=ease_out(prog(t, 0.0, 1.0)), t=t, alpha=110, colr='#2f9bff', n=3)
    bar_magnet(c, 540, 760, 1.15)
    # zoom bubble showing the clip's domains lining up
    al = ease_in_out(prog(t, t0 + 1.2, 1.5))
    sw = lambda i: math.sin(t * 2.2 + i) * 4
    paperclip(c, 380, 905, 1.0, sw(0))
    k = ease_back(prog(t, t0 + 0.6, 0.5))
    if k > 0:
        c.save(); c.translate(720, 1150); c.scale(k, k)
        cl = skia.Path(); cl.addCircle(0, 0, 230)
        c.drawCircle(0, 0, 238, P(color=col('#0b1a3a', 50), blur=10))
        c.save(); c.clipPath(cl, doAntiAlias=True)
        domains(c, -230, -230, 460, 460, al, t, seed=9, cols_=3, rows=3, arrows_per=4, target=90.0)
        c.restore()
        c.drawCircle(0, 0, 230, P(color=col('#ffffff'), stroke=12))
        c.restore()
        c.drawLine(420, 940, 560, 1020, P(color=col('#ffffff', int(230 * min(1, k))), stroke=8))
    if t > t1:
        drop = ease_out(prog(t, t1 + 0.4, 0.5))
        paperclip(c, 380, lerp(1500, 1070, drop), 1.0, sw(1) + lerp(70, 0, drop))
        drop2 = ease_out(prog(t, t1 + 1.3, 0.5))
        paperclip(c, 380, lerp(1500, 1235, drop2), 1.0, sw(2) + lerp(70, 0, drop2))
        label_pill(c, 'TEMPORARY magnet', 540, 1560, size=44, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill='#e8264f', hi='#e8264f')
    else:
        paperclip(c, 380, 1500, 1.0, 70)

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 1.2, 'whoosh'), (cues[1]['start'] + 0.8, 'click'), (cues[1]['start'] + 0.9, 'pop'), (cues[1]['start'] + 1.7, 'click')]

# ---------- 7: Wild part: Earth is a magnet, north = magnetic south ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=17)
    ex, ey, R = 470, 1110, 300
    field_lines(c, ex, ey, 1.05, k=ease_out(prog(t, t0 + 1.0, 1.4)), t=t, alpha=170, colr='#7cc6ff', n=4, rot=90)
    earth(c, ex, ey, R, t, rot=t * 0.02, face_on=False)
    # molten core
    ck = ease_out(prog(t, t0 + 1.6, 0.8))
    if ck > 0:
        c.save(); cl = skia.Path(); cl.addCircle(ex, ey, R); c.clipPath(cl, doAntiAlias=True)
        c.drawCircle(ex, ey, R * 0.5 * ck, rad(ex, ey, R * 0.5, [col('#fff1a1'), col('#ff9f1c'), col('#e8382f')], [0, 0.5, 1]))
        for i in range(3):
            curved_arrow(c, ex, ey, R * (0.2 + i * 0.1) * ck, t * 90 + i * 120, t * 90 + i * 120 + 200, colr='#ffffff', w=6, alpha=int(200 * ck))
        c.restore()
        label_pill(c, 'molten IRON', ex, ey + R + 70, size=42, k=ease_back(prog(t, t0 + 2.2, 0.4)), fill='#e07a00', hi='#e07a00')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.4, 0.5))
        c.save(); c.translate(ex, ey - R - 20); c.scale(k, k)
        c.drawCircle(0, 0, 56, P(color=col(MAG_S))); c.drawCircle(0, 0, 56, P(color=col('#ffffff'), stroke=6))
        text_block(c, 'S', 0, 0, size=60, fill='#ffffff', stroke=NAVY)
        c.restore()
        label_pill(c, 'ARCTIC', ex, ey - R - 110, size=40, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi='#2f9bff')
        ck2 = ease_back(prog(t, t1 + 1.6, 0.5))
        if ck2 > 0:
            # compass beside the globe, needle swinging to point at the pole
            sw = ease_out(prog(t, t1 + 1.9, 1.2))
            ang = lerp(120, -29, sw) + math.sin(t * 9) * 6 * (1 - sw)
            c.save(); c.translate(830, 1440); c.scale(ck2, ck2); compass(c, 0, 0, 110, ang); c.restore()

def s7_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 1.0, 'sparkle'), (cues[0]['start'] + 2.2, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.6, 'pop'), (cues[1]['start'] + 1.9, 'whoosh')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    lab_bg(c, t)
    field_lines(c, 540, 890, 1.9, k=ease_out(prog(t, 0.2, 1.2)), t=t, alpha=110, colr='#2f9bff', n=3)
    domains(c, 140, 760, 800, 260, 1.0, t, seed=4, cols_=4, rows=2, target=180.0, tint=False)
    for i in range(4):
        x, _, u = clip_pos(i, t - 0.8)
        rot = lerp(80, 0, u) if u < 1 else math.sin(t * 6 + i) * 3
        paperclip(c, x, lerp(1560, 1110, u * u), 1.0, rot)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        heart(c, 540, 1360, 0.32 * k, t, squeeze=0.5 + 0.5 * math.sin(t * 7))
        label_pill(c, 'next: your HEART', 540, 1530, size=46, k=k, fill=NAVY, hi='#ff5c85')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(0.9, 'click'), (1.25, 'click'), (cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do magnets work?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do magnets work?', 'How do MAGNETS work?'),
            ('No battery, no plug. The secret is hiding inside the atoms.', 'The secret: inside ATOMS')], tail=0.8),
        dict(name='electron', draw=s2, sfx_fn=s2_sfx, ambience='space', lines=[
            ('Every atom has electrons, and each one acts like a tiny magnet, thanks to its spin.', 'Each ELECTRON is a tiny magnet'),
            ('In most materials, they pair up and cancel out.', 'Usually they CANCEL out')], tail=0.9),
        dict(name='domains', draw=s3, sfx_fn=s3_sfx, lines=[
            ("But in iron, the atoms' tiny magnets line up with their neighbors.", 'In IRON they line up'),
            ('They form patches called domains.', 'Patches called DOMAINS')], tail=1.0),
        dict(name='aligned', draw=s4, sfx_fn=s4_sfx, lines=[
            ('In a plain iron nail, the domains point every which way and cancel.', 'A nail: domains point ANYWHERE'),
            ('In a magnet, most point the same way, like a crowd facing the stage.', 'Magnet: all point the SAME way')], tail=1.4),
        dict(name='poles', draw=s5, sfx_fn=s5_sfx, lines=[
            ('That gives a magnet two poles. Opposites attract, like poles push apart.', 'Opposites ATTRACT'),
            ('Cut one in half, and you get two smaller magnets.', 'Cut it: TWO magnets')], tail=1.0),
        dict(name='clips', draw=s6, sfx_fn=s6_sfx, lines=[
            ('A magnet even lines up the domains in a steel paperclip.', 'It lines up the CLIP too'),
            ('So the clip becomes a temporary magnet, and grabs the next one.', 'Clips become MAGNETS')], tail=1.0),
        dict(name='earth', draw=s7, sfx_fn=s7_sfx, ambience='space', lines=[
            ("Here's the wild part: Earth is a giant magnet, powered by molten iron in its core.", 'EARTH is a magnet'),
            ("And its magnetic pole up north is actually a south pole. That's why compasses point there.", 'Up north: a magnetic SOUTH pole')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So a magnet is countless tiny magnets, all pointing the same way.', 'Tiny magnets, all ALIGNED'),
            ('Next up: how your heart works.', 'Next: how your HEART works'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
