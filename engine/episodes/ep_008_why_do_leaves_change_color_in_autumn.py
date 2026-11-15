"""Episode 8 (EN): Why do leaves change color in autumn?"""
import math, random
from lib import *

DAY = ('#2f9bff', '#cdeeff')
FALL = ('#ff9f6b', '#ffe3b8')

def fall_sky(c, k):
    """k 0 = summer blue, 1 = warm autumn sky."""
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, W, H), [col(mix_hx(DAY[0], '#6f8fd8', k)), col(mix_hx('#7cc6ff', '#ffb98a', k)), col(mix_hx(DAY[1], FALL[1], k))]))

def ground(c, t, y=1640, k=0.0):
    hills(c, y, c1=('#7ed957' if k < 0.5 else '#b7c95a'), c2=('#56b83a' if k < 0.5 else '#8fa83e'), t=t, trees=False, flowers=k < 0.5)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    k = ease_in_out(prog(t, 0.4, 2.2))
    fall_sky(c, k)
    sunbeams(c, 900, 700, t, a=16); sun(c, 900, 700, 70, t)
    ground(c, t, 1660, k)
    leafy_tree(c, 300, 1640, 1.25, t, autumn=k, seed=1)
    a = ease_back(prog(t, 0.1, 0.7))
    lc = mix_hex('#5cc94a', '#ff6b2c', k)
    c.save(); c.translate(720, 1180 + math.sin(t * 2) * 15); c.scale(a, a)
    leaf(c, 0, 0, 2.6, t, '#5cc94a', 1, mood='wow' if t < 2.2 else 'happy', layer=('#ff7a2c', k))
    c.restore()
    for i in range(3):
        aa = prog(t, 1.0 + i * 0.15, 0.35)
        if aa > 0:
            x, y = [(560, 820), (920, 900), (880, 1450)][i]
            c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
            text_block(c, '?', 0, 0, size=96, fill=['#ffffff', '#ffe14d', '#ff8fab'][i], scale=0.4 + 0.6 * ease_back(aa, 2.5), alpha=int(255 * aa))
            c.restore()
    if k > 0.3: falling_leaves(c, t, seed=2, n=6, s=0.3, alpha=int(255 * prog(t, 1.2, 0.6)))

def s1_sfx(D, cues): return [(0.1, 'whoosh'), (1.2, 'sparkle')]

# ---------- 2: Chlorophyll makes food from sunlight ----------
def s2(c, t, D, cues):
    sky(c, DAY[0], DAY[1], mid='#7cc6ff')
    t0, t1 = cues[0]['start'], cues[1]['start']
    sx, sy = 190, 760
    sunbeams(c, sx, sy, t, a=22)
    ground(c, t, 1700)
    lx, ly = 600, 1150
    a = ease_back(prog(t, 0.1, 0.6))
    c.save(); c.translate(lx, ly); c.scale(a, a); leaf(c, 0, 0, 3.2, t, '#4cc04a', 2); c.restore()
    # green "chlorophyll" sparkles inside the leaf
    if t > t0 + 0.6:
        rnd = random.Random(5)
        for i in range(10):
            ap = prog(t, t0 + 0.6 + i * 0.08, 0.3)
            px = lx + rnd.uniform(-120, 120); py = ly + rnd.uniform(-200, 80)
            c.drawCircle(px, py + math.sin(t * 3 + i) * 6, 13 * ease_back(ap), P(color=col('#1f9a35', 220)))
            c.drawCircle(px - 3, py - 4 + math.sin(t * 3 + i) * 6, 4 * ap, P(color=col('#c8ffb0')))
    # sunlight goes in, sugar goes out
    if t > t1:
        g = ease_out(prog(t, t1, 0.8))
        for i in range(5):
            u = ((t - t1) * 0.6 + i / 5) % 1.0
            px, py = lerp(sx + 60, lx - 60, u), lerp(sy + 40, ly - 80, u)
            photon(c, px, py, 18, '#ffe14d', t, i, face_on=False, alpha=int(255 * g * math.sin(u * math.pi)))
        for i in range(3):
            u = ((t - t1 - 0.6) * 0.45 + i / 3) % 1.0
            if t - t1 < 0.6: break
            px, py = lerp(lx + 30, 940, u), lerp(ly + 120, 1500, u)
            al = int(255 * math.sin(u * math.pi))
            c.save(); c.translate(px, py); c.rotate(t * 60 + i * 30)
            c.drawRoundRect(skia.Rect(-24, -24, 24, 24), 8, 8, P(color=col('#ffffff', al)))
            c.drawRoundRect(skia.Rect(-24, -24, 24, 24), 8, 8, P(color=col('#f3a6c0', al), stroke=5))
            c.restore()
    sun(c, sx, sy, 110, t)

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'sparkle'), (cues[1]['start'] + 0.2, 'whoosh')]

# ---------- 3: Shorter, colder days -> tree stops making green ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    k = ease_in_out(prog(t, t0, 2.2))
    fall_sky(c, k * 0.8)
    sx = 900; sy = lerp(760, 1560, k)
    sunbeams(c, sx, sy, t, a=int(20 * (1 - k * 0.6))); sun(c, sx, sy, 85, t)
    clouds(c, t, seed=4, n=3, y0=600, y1=1000, a=int(160 + 60 * k))
    ground(c, t, 1660, k)
    # wind lines
    if k > 0.4:
        for j in range(4):
            u = (t * 0.9 + j / 4) % 1.0; yy = 820 + j * 140
            x0 = lerp(-200, W, u)
            c.drawLine(x0, yy, x0 + 160, yy, P(color=col('#ffffff', int(170 * math.sin(u * math.pi))), stroke=8))
    leafy_tree(c, 270, 1640, 1.15, t, autumn=0.0, seed=3)
    # leaf with "green factory" switching off
    ga = 1 - ease_in_out(prog(t, t1 + 0.3, 1.6))
    lc = mix_hex('#9bc34a', '#5cc94a', ga)
    c.save(); c.translate(650, 1010); leaf(c, 0, 0, 1.9, t, '#d8c74a', 4, mood='wow' if t > t1 + 0.3 else 'happy', layer=('#4cc04a', ga)); c.restore()
    if t > t1 + 0.2:
        # little "green paint" drops stopping
        for i in range(3):
            u = ((t - t1) * 0.8 + i / 3) % 1.0
            al = int(230 * ga * (1 - u))
            c.drawCircle(650 + (i - 1) * 40, 760 - u * 60, 12, P(color=col('#2fae4a', al)))
    snow_a = prog(t, t1, 1.0) * 0.0  # no snow yet: still autumn

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.4, 'boing')]

# ---------- 4: Yellow & orange were hiding under a green blanket ----------
def s4(c, t, D, cues):
    fall_sky(c, 0.6)
    ground(c, t, 1700, 0.7)
    t0, t1 = cues[0]['start'], cues[1]['start']
    pull = ease_in_out(prog(t, t0 + 0.5, 2.0))
    base = ['#ffd23f', '#ff9f1c', '#ffbe3b']
    for i, (x, y, rot) in enumerate([(300, 1150, -14), (780, 1100, 12), (540, 1330, 0)]):
        a = ease_back(prog(t, 0.1 + i * 0.15, 0.5))
        c.save(); c.translate(x, y); c.scale(a, a)
        cov = 1 - pull
        if i == 2 and t > t1:  # show the 'blanket' again: cover up, then pull it off
            cov = ease_in_out(prog(t, t1 + 0.2, 0.7)) * (1 - ease_in_out(prog(t, t1 + 1.8, 0.9)))
        leaf(c, 0, 0, 1.75 if i < 2 else 2.0, t, base[i], i + 1, mood='wow' if cov < 0.1 else 'happy', rot=rot, layer=('#4cc04a', cov))
        c.restore()
    # sparkles when revealed
    if pull > 0.6:
        rnd = random.Random(9)
        for i in range(14):
            x, y = rnd.uniform(160, 920), rnd.uniform(850, 1550)
            tw = 0.5 + 0.5 * math.sin(t * 5 + i)
            c.drawCircle(x, y, 6 + 6 * tw, P(color=col('#fff3b0', int(220 * tw * prog(pull, 0.6, 0.4))), blur=2))

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.6, 'whoosh'), (cues[0]['start'] + 2.2, 'sparkle'), (cues[1]['start'] + 0.2, 'whoosh')]

# ---------- 5: Some make new red -> colourful painting ----------
def s5(c, t, D, cues):
    fall_sky(c, 0.85)
    sunbeams(c, 880, 760, t, a=14); sun(c, 880, 760, 70, t)
    t0, t1 = cues[0]['start'], cues[1]['start']
    ground(c, t, 1690, 1.0)
    k = ease_in_out(prog(t, t1, 2.2))
    for i, (x, s) in enumerate([(170, 0.8), (920, 0.85), (540, 1.0)]):
        leafy_tree(c, x, 1650 - (i == 2) * 20, s, t, autumn=0.25 + 0.75 * k, seed=i + 5)
    # red leaf "painting itself"
    r = ease_out(prog(t, t0 + 0.4, 1.4))
    if r > 0:
        c.save(); c.translate(540, 980 + math.sin(t * 2) * 10)
        leaf(c, 0, 0, 1.6, t, '#ffbe3b', 5, mood='happy', layer=('#e8382f', r))
        c.restore()
        # brush
        bxp = 540 + math.cos(t * 4) * 70; byp = lerp(1100, 850, r)
        if r < 1:
            c.save(); c.translate(bxp + 110, byp - 60); c.rotate(30)
            c.drawRoundRect(skia.Rect(-10, -150, 10, 0), 8, 8, P(color=col('#a86b3c')))
            c.drawRoundRect(skia.Rect(-16, 0, 16, 50), 12, 12, P(color=col('#e8382f')))
            c.restore()
    if k > 0.2: falling_leaves(c, t, seed=6, n=7, s=0.3, alpha=int(255 * prog(k, 0.2, 0.4)))

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'sparkle'), (cues[1]['start'] + 0.3, 'sparkle')]

# ---------- 6: Leaves fall, tree rests, spring brings new green ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    w = ease_in_out(prog(t, t0 + 0.8, 1.6)) * (1 - ease_in_out(prog(t, t1, 0.8)))
    sp = ease_in_out(prog(t, t1, 1.8))
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, W, H), [col(mix_hx(mix_hx('#7f9bd8', '#9fb4d6', w), DAY[0], sp)), col(mix_hx(mix_hx('#ffd0a8', '#e6eef7', w), DAY[1], sp))]))
    gy = 1660
    ground(c, t, gy, 1.0 if sp < 0.5 else 0.0)
    if w > 0.01:
        c.drawRect(skia.Rect(0, gy - 40, W, H), lin(c, (0, gy - 100, 0, H), [col('#ffffff', int(230 * w)), col('#e7f1fb', int(255 * w))]))
    bare = ease_in_out(prog(t, t0 + 0.2, 1.8)) * (1 - sp)
    leafy_tree(c, 540, 1660, 1.45, t, autumn=1.0 - sp, seed=8, bare=bare, face_on=True, mood='happy')
    if bare > 0.05 and sp < 0.5:
        falling_leaves(c, t, seed=8, n=10, s=0.32, y0=700, y1=1700, alpha=int(255 * (1 - prog(t, t0 + 2.4, 0.6))))
    if w > 0.3: snow(c, t, seed=8, n=26, alpha=int(230 * w))
    if bare > 0.85 and sp < 0.1 and t > t0 + 1.8:
        zzz(c, 700, 920, t, 70, alpha=int(255 * prog(t, t0 + 1.8, 0.4)))
    if sp > 0:
        rnd = random.Random(3)
        for i in range(6):
            ap = ease_back(prog(t, t1 + 0.6 + i * 0.12, 0.4))
            if ap <= 0: continue
            x = 540 + rnd.uniform(-230, 230); y = 1660 * 0 + 1660 - 1.45 * rnd.uniform(330, 560)
            c.save(); c.translate(x, y); c.scale(ap, ap); leaf(c, 0, 0, 0.45, t, '#7ee05a', i, face_on=False, rot=rnd.uniform(-40, 40)); c.restore()
        for i, (x, p) in enumerate([(150, '#ff8fab'), (930, '#ffd23f')]):
            fa = ease_back(prog(t, t1 + 1.0 + i * 0.2, 0.5))
            if fa > 0:
                c.save(); c.translate(x, 1600); c.scale(fa, fa); flower(c, 0, 0, 0.55, t, i, petal=p); c.restore()

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 7: Bonus: pine needles stay green ----------
def pine(c, x, y, s, t, face_on=True, snow_a=1.0, seed=0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(t * 1.2 + seed) * 1.0)
    c.drawOval(skia.Rect(-160, -16, 160, 16), P(color=col('#000000', 45), blur=8))
    c.drawRect(skia.Rect(-26, -110, 26, 0), P(color=col('#7a4a26')))
    for i, (wd, y0, hh) in enumerate([(170, -90, 220), (140, -230, 200), (105, -360, 180)]):
        p = skia.Path(); p.moveTo(-wd, y0); p.lineTo(0, y0 - hh); p.lineTo(wd, y0); p.close()
        c.drawPath(p, lin(c, (0, y0 - hh, 0, y0), [col('#3fbf5a'), col('#1f7a3a')]))
        if snow_a > 0:
            sp = skia.Path(); sp.moveTo(-wd * 0.55, y0 - hh * 0.45); sp.lineTo(0, y0 - hh); sp.lineTo(wd * 0.55, y0 - hh * 0.45)
            sp.quadTo(wd * 0.25, y0 - hh * 0.35, 0, y0 - hh * 0.5); sp.quadTo(-wd * 0.25, y0 - hh * 0.35, -wd * 0.55, y0 - hh * 0.45); sp.close()
            c.drawPath(sp, P(color=col('#ffffff', int(240 * snow_a))))
    if face_on: face(c, 0, -190, 80, t, seed, 'happy')
    c.restore()

def s7(c, t, D, cues):
    sky(c, '#7fa6d9', '#eef4fb', mid='#b9cfe8')
    t0, t1 = cues[0]['start'], cues[1]['start']
    gy = 1650
    hills(c, gy, c1='#f4f8fc', c2='#dfe9f4', t=t, trees=False, flowers=False)
    leafy_tree(c, 150, 1640, 0.6, t, autumn=1.0, seed=11, bare=1.0)
    a = ease_back(prog(t, 0.1, 0.6))
    c.save(); c.translate(480, 1640); c.scale(a, a); pine(c, 0, 0, 1.55, t); c.restore()
    snow(c, t, seed=12, n=30)
    if t > t1:
        r = ease_back(prog(t, t1, 0.5))
        c.save(); c.translate(790, 880); c.scale(r, r)
        c.drawCircle(0, 0, 130, P(color=col('#ffffff', 210)))
        c.drawCircle(0, 0, 130, P(color=col('#8fc3e8'), stroke=6))
        for q in range(-3, 4):
            ang = math.radians(q * 14)
            nd = skia.Path(); nd.moveTo(0, 75); nd.lineTo(math.sin(ang) * 150, 75 - math.cos(ang) * 150)
            c.drawPath(nd, P(color=col('#2f9a45'), stroke=14))
        for q in range(4):
            u = (t * 0.8 + q / 4) % 1.0
            c.drawCircle(-80 + q * 50, -110 + u * 160, 10, P(color=col('#6cc4ff', int(230 * (1 - u)))))
        c.drawArc(skia.Rect(-110, -110, 110, 110), 200, 140, False, P(color=col('#ffffff', 230), stroke=10))
        c.restore()

def s7_sfx(D, cues): return [(0.1, 'whoosh'), (cues[1]['start'] + 0.1, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    fall_sky(c, 0.6)
    sunbeams(c, 540, 1060, t, a=16)
    ground(c, t, 1680, 1.0)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1060 + math.sin(t * 2) * 12); c.scale(s, s); leaf(c, 0, 0, 3.0, t, '#ff7a2c', 3); c.restore()
    for i, h in enumerate(['#5cc94a', '#ffd23f', '#ff9f1c', '#e8382f', '#ff6b2c', '#ffbe3b']):
        ang = t * 0.9 + i * 2 * math.pi / 6
        leaf(c, 540 + math.cos(ang) * 360, 1080 + math.sin(ang) * 300, 0.6, t, h, i, face_on=False, rot=math.degrees(ang) + 90)
    follow_button(c, t, cues[-1]['start'])
    dust(c, t, seed=15, n=16, colr='#fff3b0')

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why do leaves change color in autumn?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why do leaves change color in autumn?', 'Why do leaves change COLOR?'),
            ("Let's find out!", "Let's find out!")], tail=0.8),
        dict(name='green', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Leaves are green because of a special green stuff, called chlorophyll.', 'Green CHLOROPHYLL!'),
            ('It helps the tree make its food from sunlight!', 'It makes FOOD from sunlight!')], tail=1.5),
        dict(name='autumn', draw=s3, sfx_fn=s3_sfx, lines=[
            ('In autumn, the days get shorter and colder.', 'SHORTER, colder days'),
            ('So the tree stops making new green.', 'The tree stops making GREEN')], tail=1.7),
        dict(name='hidden', draw=s4, sfx_fn=s4_sfx, lines=[
            ('But yellow and orange were hiding in the leaf all summer long!', 'YELLOW and ORANGE were hiding!'),
            ('The green was covering them up, like a big blanket.', 'Green was like a BLANKET')], tail=1.7),
        dict(name='red', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Some leaves even make brand new red colors in autumn.', 'Some make brand NEW red!'),
            ('So the trees look like a big, colorful painting!', 'A colorful PAINTING!')], tail=1.7),
        dict(name='rest', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Then the leaves fall down, and the tree rests all winter.', 'Leaves FALL, the tree rests'),
            ('And in spring, brand new green leaves grow!', 'Spring: NEW green leaves!')], tail=1.6),
        dict(name='bonus', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? Most pine trees stay green all winter long!', 'Pine trees stay GREEN!'),
            ('Their needles have a waxy coat, like a tiny raincoat.', 'A tiny wax RAINCOAT!')], tail=1.8),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
