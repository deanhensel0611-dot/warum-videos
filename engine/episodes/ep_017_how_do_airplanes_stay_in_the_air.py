"""Episode 17 (EN, general audience): How do airplanes stay in the air?
Facts checked: lift = wing turns air downward (Newton 3) + pressure difference (lower above, higher below);
engines give thrust, not lift (gliders fly without engines); equal-transit-time is a myth: air over the top
arrives at the trailing edge first (Cambridge Univ. Eng. Dept., Babinsky). 747-8 max take-off weight ~448 t.
"""
import math, random
from lib import *

SKY = ('#2f9bff', '#cdeeff', '#7cc6ff')
CX, CY, CH = 540, 1080, 640    # airfoil centre + chord

def bg(c, t, speed=1.0, seed=1):
    sky(c, SKY[0], SKY[1], mid=SKY[2])
    rnd = random.Random(seed)
    for i in range(5):     # fast clouds = we are flying
        y = rnd.uniform(650, 1600); s = rnd.uniform(0.6, 1.3); sp = rnd.uniform(140, 260) * speed
        x = (rnd.uniform(0, 1600) - t * sp) % 1700 - 300
        cloud(c, x, y, s, a=150 + 60 * (s > 1))

def streamline(xx, d, t, down=230.0):
    """y of a streamline with offset d (neg = above) at x. Air bends round the wing and leaves it heading down."""
    u = (xx - (CX + CH * 0.30)) / 150.0
    dw = down * (1 / (1 + math.exp(-u))) * (1 / (1 + abs(d) / 260))
    bump = math.exp(-((xx - CX + 40) / (CH * 0.42)) ** 2)
    if d < 0: b = -70 * bump * (1 / (1 + abs(d) / 160))
    else: b = 25 * bump * (1 / (1 + d / 160))
    up = -18 * math.exp(-((xx - (CX - CH * 0.55)) / 120) ** 2) * (1 / (1 + abs(d) / 200))
    return CY + d + dw + b + up

OFFS = [-300, -195, -105, 100, 190, 290]

def draw_flow(c, t, a=1.0, down=230.0, speed_top=1.35):
    if a <= 0: return
    for d in OFFS:
        pts = [(x, streamline(x, d, t, down)) for x in range(-20, 1110, 15)]
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        c.drawPath(p, P(color=col('#ffffff', int(110 * a)), stroke=5))
        sp = 260 * (speed_top if d < 0 else 1.0)
        for k in range(6):
            x = (k * 190 + t * sp + (d % 97)) % 1130 - 20
            y = streamline(x, d, t, down); x2 = x - 46; y2 = streamline(x2, d, t, down)
            c.drawLine(x2, y2, x, y, P(color=col('#ffffff', int(235 * a)), stroke=10))

# ---------- 1: Hook (cold open: plane already in flight) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    bg(c, t, 1.4)
    x = 540 + math.sin(t * 0.8) * 20; y = 1060 + math.sin(t * 1.3) * 18
    airplane(c, x, y, 1.65, rot=-4 + math.sin(t * 1.1) * 1.5, t=t)
    # weight tag hanging under the plane
    k = ease_back(prog(t, 0.9, 0.5)) * (1 - prog(t, t1 + 0.1, 0.3))
    if k > 0:
        c.drawLine(x - 30, y + 90, x - 30, y + 250, P(color=col('#1b2a4a', int(200 * k)), stroke=5))
        label_pill(c, '400+ tons', x - 30, y + 310, size=64, k=k, fill='#ff5c85')
    if t > t1:
        k2 = ease_back(prog(t, t1 + 0.4, 0.5), 2.2)
        c.save(); c.translate(540, 1500); c.rotate(-6); c.scale(k2, k2)
        c.drawRoundRect(skia.Rect(-260, -70, 260, 70), 22, 22, P(color=col('#ffffff', 240)))
        text_block(c, 'TEXTBOOK', 0, 0, size=72, fill='#1b2a4a', hi='#1b2a4a', stroke='#ffffff')
        c.restore()
        s = prog(t, t1 + 1.3, 0.35)
        if s > 0:
            c.drawLine(300, 1500 + 40, lerp(300, 780, s), 1500 - 40 - 60 * s + 60 * s, P(color=col('#ff2d55'), stroke=18))
        if t > t1 + 1.7:
            label_pill(c, 'MYTH', 720, 1400, size=60, k=ease_back(prog(t, t1 + 1.7, 0.4), 2.5), fill='#ffffff', bg='#ff2d55')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.9, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 1.3, 'click')]

# ---------- 2: Wings are tilted and shove air down ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, 0.6, seed=2)
    aoa = 8 * ease_in_out(prog(t, t0 + 0.6, 1.2))
    draw_flow(c, t, a=prog(t, t1 - 0.2, 0.6), down=230 * ease_in_out(prog(t, t1, 1.5)))
    draw_airfoil(c, CX, CY, CH, aoa=aoa)
    # angle marker
    if t > t0 + 0.6 and t < t1 + 0.6:
        a = int(255 * min(prog(t, t0 + 0.6, 0.4), 1 - prog(t, t1, 0.6)))
        lx = CX - CH / 2 - 10
        c.drawLine(lx, CY, lx + 520, CY, P(color=col('#ffffff', a), stroke=5))
        c.drawArc(skia.Rect(lx + 280, CY - 280, lx + 840, CY + 280), 0, aoa, False, P(color=col('#ffd23f', a), stroke=10))
        if aoa > 3: label_pill(c, 'a few degrees', 760, 840, size=48, k=1, alpha=int(a * 0.95))
    if t > t1 + 1.2:
        k = ease_back(prog(t, t1 + 1.2, 0.5))
        for i, dx in enumerate((0, 120)):
            arrow(c, 740 + dx, 1250 + i * 20, 770 + dx, 1250 + 210 * k + i * 20, colr='#ff5c85', w=22)
        label_pill(c, 'air DOWN', 790, 1560, size=56, k=k, fill='#ff5c85', hi='#ff5c85')

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[1]['start'] - 0.1, 'whoosh'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 3: Push air down -> air pushes wing up (balloon analogy) ----------
def balloon(c, x, y, r, t, ang=0.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    c.drawOval(skia.Rect(-r * 0.9, -r, r * 0.9, r), rad(-r * 0.3, -r * 0.4, r * 1.5, [col('#ffb3c6'), col('#ff5c85'), col('#d93a64')], [0, 0.45, 1]))
    c.drawOval(skia.Rect(-r * 0.5, -r * 0.75, -r * 0.15, -r * 0.3), P(color=col('#ffffff', 140), blur=6))
    nk = skia.Path(); nk.moveTo(-r * 0.15, r * 0.95); nk.lineTo(r * 0.15, r * 0.95); nk.lineTo(r * 0.1, r * 1.15); nk.lineTo(-r * 0.1, r * 1.15); nk.close()
    c.drawPath(nk, P(color=col('#d93a64')))
    for i in range(4):
        u = ((t * 2.2 + i / 4) % 1.0)
        c.drawCircle(math.sin(i * 2.1 + t * 7) * 14 * u, r * 1.25 + u * 220, 12 * (1 - u) + 4, P(color=col('#ffffff', int(200 * (1 - u)))))
    c.restore()

def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, 0.6, seed=3)
    if t < t1 - 0.3:
        lift = 40 * ease_out(prog(t, t0 + 1.4, 1.5))
        c.save(); c.translate(0, -lift)
        draw_flow(c, t, a=1.0)
        draw_airfoil(c, CX, CY, CH, aoa=8)
        c.restore()
        k = ease_back(prog(t, t0 + 0.4, 0.5))
        arrow(c, 880, 1260, 880, 1260 + 260 * k, colr='#ff5c85', w=30)
        label_pill(c, 'air DOWN', 820, 1580, size=54, k=k, fill='#ff5c85', hi='#ff5c85')
        k2 = ease_back(prog(t, t0 + 1.4, 0.5))
        arrow(c, 500, 1040 - lift, 500, 1040 - lift - 330 * k2, colr='#ffd23f', w=36)
        label_pill(c, 'wing UP', 500, 650 + 60 * (1 - k2), size=54, k=k2, fill='#1b2a4a', hi='#e0a800')
    else:
        u = prog(t, t1 - 0.3, D - t1)
        y = lerp(1420, 820, ease_in_out(u)) + math.sin(t * 9) * 6
        x = 540 + math.sin(t * 3) * 25
        balloon(c, x, y, 150, t, ang=math.sin(t * 4) * 4)
        k = ease_back(prog(t, t1 + 0.6, 0.4))
        arrow(c, 820, y + 120, 820, y + 120 + 200 * k, colr='#ffffff', w=20)
        arrow(c, 260, y + 120, 260, y - 80 * k, colr='#ffd23f', w=24)
        label_pill(c, 'air out', 820, y + 390, size=46, k=k)
        label_pill(c, 'balloon up', 260, y - 160, size=46, k=k, fill='#1b2a4a')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 1.4, 'boing'), (cues[1]['start'] - 0.3, 'whoosh')]

# ---------- 4: Pressure: low above, high below ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1f6fd1', '#bfe3ff', mid='#5aa9f5')
    a = prog(t, t0 + 0.3, 0.8); b = prog(t, t1 + 0.2, 0.8)
    # air molecules: sparse above (low pressure), packed below (high pressure)
    rnd = random.Random(7)
    for i in range(170):
        bx, by = rnd.uniform(0, W), rnd.uniform(640, 1560); ph = rnd.random() * 6
        x = bx + math.sin(t * 2.3 + ph) * 16; y = by + math.cos(t * 2.9 + ph) * 16
        above = y < CY - 20 and abs(x - CX) < 420
        below = y > CY + 30 and abs(x - CX) < 420
        if above and rnd.random() < 0.65 * a: continue
        alpha = 170
        c.drawCircle(x, y, 9, P(color=col('#ffffff', alpha)))
    if below_extra := b:
        rnd2 = random.Random(9)
        for i in range(int(70 * b)):
            x = rnd2.uniform(CX - 380, CX + 380) + math.sin(t * 3 + i) * 12; y = rnd2.uniform(CY + 70, CY + 330) + math.cos(t * 2.5 + i) * 12
            c.drawCircle(x, y, 9, P(color=col('#ffffff', 200)))
    draw_airfoil(c, CX, CY, CH, aoa=8)
    if a > 0:
        label_pill(c, 'LOW pressure', 540, 760, size=56, k=ease_back(a), fill='#2f9bff', hi='#2f9bff')
    if b > 0:
        kb = ease_back(b)
        label_pill(c, 'HIGH pressure', 540, 1480, size=56, k=kb, fill='#ff5c85', hi='#ff5c85')
        for i, dx in enumerate((-200, 0, 200)):
            yy = CY + 160 + math.sin(t * 5 + i) * 8
            arrow(c, CX + dx, yy + 80, CX + dx, yy - 40 * kb, colr='#ffd23f', w=18)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'] + 0.2, 'pop'), (cues[2]['start'], 'whoosh')]

# ---------- 5: Engines push forward; gliders ----------
def glider(c, x, y, s, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    fu = skia.Path(); fu.moveTo(-230, -6); fu.cubicTo(-100, -20, 120, -30, 190, -14); fu.cubicTo(215, -6, 212, 12, 190, 16); fu.cubicTo(100, 22, -100, 12, -230, 6); fu.close()
    c.drawPath(fu, lin(c, (0, -30, 0, 22), [col('#ffffff'), col('#dfe8f5')]))
    c.drawPath(fu, P(color=col('#1b2a4a', 70), stroke=3))
    cp = skia.Path(); cp.moveTo(90, -22); cp.quadTo(130, -44, 170, -18); cp.close(); c.drawPath(cp, P(color=col('#1b2a4a')))
    tf = skia.Path(); tf.moveTo(-200, -4); tf.lineTo(-240, -90); tf.lineTo(-214, -90); tf.lineTo(-170, -6); tf.close(); c.drawPath(tf, P(color=col('#ff5c85')))
    c.drawRoundRect(skia.Rect(-60, -4, 70, 10), 6, 6, P(color=col('#2f9bff')))
    wg = skia.Path(); wg.moveTo(20, 2); wg.lineTo(-30, 150); wg.lineTo(-5, 152); wg.lineTo(50, 4); wg.close(); c.drawPath(wg, P(color=col('#2f9bff')))
    c.restore()

def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bg(c, t, 1.6 if t < t1 else 0.5, seed=5)
    if t < t1 + 0.4:
        out = ease_in_out(prog(t, t1 - 0.2, 0.6))
        x = 470 + 900 * out; y = 980 + math.sin(t * 1.4) * 12
        airplane(c, x, y, 1.3, rot=-3, t=t, flame=True)
        k = ease_back(prog(t, t0 + 0.5, 0.5))
        arrow(c, x - 360, y + 280, x - 360 + 520 * k, y + 280, colr='#ffd23f', w=30)
        label_pill(c, 'THRUST', x - 100, y + 400, size=58, k=k, fill='#1b2a4a', hi='#e0a800')
        if t > t0 + 1.6:
            k2 = ease_back(prog(t, t0 + 1.6, 0.4))
            for i in range(3):
                yy = 690 + i * 70
                u = ((t * 1.5 + i * 0.3) % 1)
                c.drawLine(lerp(1000, 80, u), yy, lerp(1000, 80, u) - 120, yy, P(color=col('#ffffff', int(200 * k2)), stroke=12))
            label_pill(c, 'fresh air → wings', 540, 1500, size=48, k=k2)
    else:
        u = prog(t, t1, D - t1)
        x = lerp(-150, 1150, u); y = lerp(860, 1180, u) + math.sin(t * 1.2) * 10
        glider(c, x, y, 1.5, rot=7)
        k = ease_back(prog(t, t1 + 0.9, 0.5))
        label_pill(c, 'no ENGINE', 540, 1470, size=58, k=k, fill='#ff5c85', hi='#ff5c85')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'whoosh'), (cues[1]['start'] - 0.2, 'whoosh'), (cues[1]['start'] + 0.9, 'pop')]

# ---------- 6: Wild part: top air arrives FIRST ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#2f6fd1', mid='#23458a')
    dust(c, t, seed=6, n=16)
    draw_flow(c, t, a=0.55)
    draw_airfoil(c, CX, CY, CH, aoa=8)
    le, te = CX - CH / 2 - 60, CX + CH / 2 + 60
    def run(t_start, dur_top, dur_bot):
        ut = prog(t, t_start, dur_top); ub = prog(t, t_start, dur_bot)
        xt = lerp(le, te + 200, ease_in_out(ut)); xb = lerp(le, te + 200, ease_in_out(ub))
        for (xx, d, hx) in ((xt, -150, '#ffd23f'), (xb, 150, '#ff5c85')):
            yy = streamline(xx, d, t)
            pts = [(xx - k * 12, streamline(xx - k * 12, d, t)) for k in range(14, -1, -1)]
            trail(c, pts, hx, 22)
            c.drawCircle(xx, yy, 26, rad(xx - 8, yy - 8, 40, [col('#ffffff'), col(hx)]))
            c.drawCircle(xx, yy, 26, P(color=col('#1b2a4a', 120), stroke=4))
        return ut, ub
    if t < t1:
        # the myth: both arrive together
        run(t0 + 0.5, 2.2, 2.2)
        if t > t0 + 2.6:
            kk = ease_back(prog(t, t0 + 2.6, 0.4))
            label_pill(c, 'meet at the back?', 540, 1500, size=50, k=kk)
            c.drawLine(300, 1500, lerp(300, 780, prog(t, t0 + 3.0, 0.3)), 1500, P(color=col('#ff2d55'), stroke=14)) if t > t0 + 3.0 else None
    else:
        ut, ub = run(t1 + 0.3, 1.2, 2.6)
        if ut >= 1:
            k = ease_back(prog(t, t1 + 1.5, 0.5), 2.2)
            label_pill(c, 'top: FIRST!', 540, 760, size=60, k=k, fill='#1b2a4a', hi='#e0a800')
        if ub >= 1 and t > t1 + 3.0:
            label_pill(c, 'bottom: way later', 540, 1500, size=50, k=ease_back(prog(t, t1 + 3.0, 0.4)), fill='#ff5c85')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.5, 'whoosh'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.5, 'ding')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    bg(c, t, 1.0, seed=7)
    x = 540 + math.sin(t * 0.7) * 30; y = 950 + math.sin(t * 1.2) * 14
    # downwash curls behind/below the plane
    for i in range(5):
        u = ((t * 0.8 + i / 5) % 1.0)
        c.drawCircle(x - 120 - u * 260, y + 120 + u * 260, 18 + u * 30, P(color=col('#ffffff', int(150 * (1 - u))), stroke=6))
    airplane(c, x, y, 1.4, rot=-4, t=t)
    k = ease_back(prog(t, cues[1]['start'], 0.5)); fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    if k > 0 and fo > 0:
        c.save(); c.translate(540, 1300); c.scale(k, k)
        ship(c, 0, 0, 0.45, t, kind='cargo', alpha=255 * fo)
        c.restore()
        label_pill(c, 'next: STEEL ships', 540, 1430, size=46, k=k, fill='#1b2a4a', hi='#2f9bff', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s7_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do airplanes stay in the air?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does a jet that weighs over four hundred tons stay in the air?', 'How does 400 TONS fly?'),
            ("The answer in a lot of textbooks is actually wrong.", 'The TEXTBOOK answer? Wrong.')], tail=1.0),
        dict(name='tilt', draw=s2, sfx_fn=s2_sfx, lines=[
            ('A wing meets the air at a slight angle, tilted up at the front.', 'Wings are TILTED a little'),
            ('As the plane moves, that wing shoves a huge amount of air downward.', 'They shove air DOWN')], tail=1.0),
        dict(name='newton', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Push air down, and the air pushes the wing up.', 'Push air down → wing goes UP'),
            ("It's the same trick as a balloon you let go: air rushes one way, the balloon flies the other.", 'Like a BALLOON letting go')], tail=0.8),
        dict(name='pressure', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Bending the air changes the pressure. Above the wing, it drops.', 'LOW pressure on top'),
            ('Below the wing, it rises, and that pushes up too.', 'HIGH pressure below'),
            ("Two sides of the same story: the wing turns air downward.", 'Same story: air turned DOWN')], tail=0.8),
        dict(name='engines', draw=s5, sfx_fn=s5_sfx, lines=[
            ("The engines don't hold the plane up. They push it forward, so fresh air keeps flowing over the wings.", 'Engines push it FORWARD'),
            ('That is why a glider can fly with no engine at all.', 'GLIDERS fly with no engine')], tail=0.9),
        dict(name='myth', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part. You may have learned that the air over the top has to meet the air below at the back.", 'The "meet at the back" idea …'),
            ('In reality, the air on top gets there first. Way first.', 'Top air arrives FIRST!')], tail=1.7),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('So: wings throw air down, and the air throws the plane up.', 'Air DOWN, plane UP'),
            ('Next up: how giant steel ships float.', 'Next: how STEEL ships float'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.2),
    ])
