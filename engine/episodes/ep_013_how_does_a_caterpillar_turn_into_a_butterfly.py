"""Episode 13 (EN): How does a caterpillar turn into a butterfly?"""
import math, random
from lib import *

BLUE_WINGS = ('#5b8cff', '#9fe0ff', '#24305e')
PINK_WINGS = ('#ff6fae', '#ffd1e6', '#5a2340')

def garden(c, t, seed=1, hy=1640, flowers_on=True):
    sky(c, '#4fb4ff', '#e3f6ff', mid='#9dd6ff')
    sunbeams(c, 800, 720, t, a=22)
    sun(c, 800, 720, 66, t)
    clouds(c, t, seed=seed, n=3, y0=640, y1=900, a=220)
    hills(c, hy, t=t, trees=False)
    if flowers_on:
        flower(c, 150, hy - 40, 0.55, t, seed=1, petal='#ff8fab', face_on=False)
        flower(c, 900, hy - 20, 0.5, t, seed=2, petal='#b28dff', face_on=False)

def big_leaf(c, x, y, s, t, bites=(), rot=0.0):
    """Large leaf lying sideways (tip to the right). bites = [(dx, dy, r)] in leaf space; they are cut out."""
    r = 120 * s
    pth = leaf_path(r)
    m = skia.Matrix(); m.setRotate(90 + rot); m.postTranslate(x, y); pth.transform(m)
    for bx, by, br in bites:
        cp = skia.Path(); cp.addCircle(x + bx, y + by, br)
        pth = skia.Op(pth, cp, skia.PathOp.kDifference_PathOp)
    c.drawPath(pth, P(color=col('#000000', 40), blur=10))
    c.drawPath(pth, lin(c, (0, y - r, 0, y + r), [col('#8fe36b'), col('#3fae4a')]))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawLine(-r * 1.0, 0, r * 1.45, 0, P(color=col('#2f8f3a', 160), stroke=r * 0.05))
    for k in range(-3, 4):
        bx = k * r * 0.33
        for sg in (-1, 1): c.drawLine(bx, 0, bx + r * 0.3, sg * r * 0.7, P(color=col('#2f8f3a', 110), stroke=r * 0.03))
    c.restore()
    c.drawOval(skia.Rect(x - r * 0.6, y - r * 0.6, x + r * 0.2, y - r * 0.35), P(color=col('#ffffff', 60), blur=8))
    c.restore()
    c.drawPath(pth, P(color=col('#2f7a33', 150), stroke=4))
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawLine(-r * 1.0, 0, -r * 1.35, r * 0.15, P(color=col('#6b8a2b'), stroke=r * 0.07))
    c.restore()

def qmarks(c, t, start=0.6):
    spots = [(170, 760), (880, 900), (140, 1100), (900, 1180), (200, 1420), (860, 1420)]
    for i, (sx, sy) in enumerate(spots):
        a = prog(t, start + i * 0.12, 0.35)
        if a <= 0: continue
        x = sx + math.sin(t * 1.3 + i) * 18; y = sy + math.cos(t * 1.7 + i * 2) * 22
        c.save(); c.translate(x, y); c.rotate(math.sin(t * 3 + i) * 15)
        text_block(c, '?', 0, 0, size=96 + (i % 3) * 16, fill=['#ffffff', '#ffe14d', '#ff8fab'][i % 3], scale=0.4 + 0.6 * ease_back(a, 2.5), alpha=int(255 * a))
        c.restore()

def twig(c, y, t):
    p = skia.Path(); p.moveTo(60, y + 20); p.cubicTo(300, y - 10, 600, y + 15, 960, y - 15)
    c.drawPath(p, P(color=col('#000000', 40), stroke=34, blur=6))
    c.drawPath(p, lin(c, (0, y - 20, 0, y + 20), [col('#a06a3a'), col('#6b4423')]))
    c.drawPath(p, P(color=col('#7a4f2a'), stroke=30))
    c.drawPath(p, P(color=col('#b07a48', 160), stroke=8))
    for lx, rot in [(180, -30), (760, 20)]:
        leaf(c, lx, y - 50, 0.7, t, '#5cc94a', seed=lx, face_on=False, rot=rot)

def stars_around(c, t, cx, cy, rx, ry, k, n=5, colr='#ffe14d'):
    if k <= 0: return
    for j in range(n):
        ang = t * 1.5 + j * 2 * math.pi / n
        px, py = cx + math.cos(ang) * rx, cy + math.sin(ang) * ry
        st = skia.Path()
        for q in range(10):
            rr = (20 if q % 2 == 0 else 8) * ease_back(k, 2); aa = q * math.pi / 5 + t * 2
            (st.moveTo if q == 0 else st.lineTo)(px + math.cos(aa) * rr, py + math.sin(aa) * rr)
        st.close(); c.drawPath(st, P(color=col(colr)))

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    garden(c, t)
    big_leaf(c, 470, 1300, 1.9, t, rot=-6)
    k = ease_out(prog(t, 0.1, 0.8))
    pts = caterpillar_pts(lerp(250, 450, k), 1210, 1.0, t)
    caterpillar(c, pts, 1.0, t, mood='wow' if t < 2.0 else 'happy')
    bx = 640 + math.cos(t * 0.9) * 160; by = 860 + math.sin(t * 1.8) * 60
    butterfly(c, bx, by, 0.65, t, rot=math.sin(t * 1.8) * 10)
    qmarks(c, t, 0.8)

def s1_sfx(D, cues): return [(0.2, 'pop')]

# ---------- 2: Egg -> tiny caterpillar ----------
def s2(c, t, D, cues):
    garden(c, t + 10, seed=2)
    big_leaf(c, 500, 1320, 2.2, t)
    t0 = cues[0]['start']
    # butterfly visits and leaves
    v = prog(t, t0 - 0.2, 2.6)
    bx = lerp(1150, -250, ease_in_out(v)); by = 1080 - math.sin(v * math.pi) * 60 + math.sin(t * 3) * 15
    if 0 < v < 1: butterfly(c, bx, by, 0.55, t, seed=3, colors=BLUE_WINGS, rot=-15)
    ea = ease_back(prog(t, t0 + 1.1, 0.4), 2.2)
    t1 = cues[1]['start']
    hatch = prog(t, t1 - 0.2, 0.8)
    ex, ey = 520, 1200
    if ea > 0 and hatch < 1:
        c.save(); c.translate(ex, ey); c.scale(ea, ea); c.rotate(math.sin(t * 20) * 6 * (hatch > 0)); egg(c, 0, 0, 55, t, crack=hatch); c.restore()
        if t > t0 + 1.3:
            c.drawCircle(ex + 70, ey - 70, 8 + 3 * math.sin(t * 6), P(color=col('#ffffff', 200)))
    if hatch >= 1:
        sh = prog(t, t1 + 0.6, 0.6)
        for sx in (-1, 1):
            c.save(); c.translate(ex + sx * (30 + 60 * sh), ey + 30 * sh); c.rotate(sx * 40 * sh)
            hp = skia.Path(); hp.addArc(skia.Rect(-44, -55, 44, 55), 90 if sx > 0 else 90, 180 * (-1 if sx > 0 else 1))
            c.drawPath(hp, P(color=col('#fff3c9', int(255 * (1 - sh)))))
            c.restore()
        g = ease_back(prog(t, t1 + 0.6, 0.6), 1.8)
        pts = caterpillar_pts(ex + 40 + (t - t1) * 25, ey + 20, 0.72 * g, t)
        caterpillar(c, pts, 0.72 * g, t, mood='happy')
        stars_around(c, t, ex + 40, ey, 200, 110, prog(t, t1 + 0.8, 0.5), n=4)

def s2_sfx(D, cues): return [(cues[0]['start'] + 1.1, 'pop'), (cues[1]['start'] + 0.3, 'boing'), (cues[1]['start'] + 0.8, 'sparkle')]

# ---------- 3: Eat, grow, new skin ----------
def s3(c, t, D, cues):
    garden(c, t + 20, seed=3)
    t0, t1 = cues[0]['start'], cues[1]['start']
    nb = int(clamp((t - t0) / 0.45, 0, 9))
    bites = [(230 - k * 30, -150 + (k % 2) * 20, 60) for k in range(nb)]
    big_leaf(c, 470, 1320, 2.3, t, bites=bites)
    grow = ease_in_out(prog(t, t0, (t1 - t0) + 0.3))
    s = lerp(0.6, 1.15, grow)
    hx = 640
    if t > t1:
        # old skin left behind, caterpillar wiggles forward
        m = ease_in_out(prog(t, t1 + 0.3, 1.6))
        skin = caterpillar_pts(330, 1215, 1.05, 0, crawl=False)
        for i, (px, py) in enumerate(skin[:-1]):
            c.drawCircle(px, py, 34 * 1.05 * (0.8 + 0.2 * i / 5), P(color=col('#e6f2c0', 150)))
            c.drawCircle(px, py, 34 * 1.05 * (0.8 + 0.2 * i / 5), P(color=col('#b7c98a', 170), stroke=3))
        pts = caterpillar_pts(lerp(330, 600, m), 1215, 1.15, t)
        caterpillar(c, pts, 1.15, t, body='#6fdc4a', mood='happy')
        stars_around(c, t, lerp(330, 600, m), 1150, 330, 150, prog(t, t1 + 1.9, 0.5), n=5)
    else:
        munch = 0.5 + 0.5 * math.sin(t * 9)
        pts = caterpillar_pts(330, 1215 + (1 - s) * 10, s, t)
        pts[-1] = (pts[-1][0] + munch * 8, pts[-1][1])
        caterpillar(c, pts, s, t, munch=munch)
        for k in range(3):
            u = (t * 1.3 + k / 3) % 1.0
            c.drawCircle(pts[-1][0] + 60 + u * 60, pts[-1][1] - 40 - u * 60, 9 * (1 - u), P(color=col('#7ed957', int(220 * (1 - u)))))

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.45 * k, 'pop') for k in range(1, 6)] + [(cues[1]['start'] + 0.3, 'boing')]

# ---------- 4: Hang upside down, make a chrysalis ----------
TX, TY = 540, 700
def s4(c, t, D, cues):
    garden(c, t + 30, seed=4)
    twig(c, TY, t)
    t0, t1 = cues[0]['start'], cues[1]['start']
    h = ease_in_out(prog(t, t0 + 0.2, 1.4))
    pts = caterpillar_pts(TX, TY + 15, 1.1, t, hang=h, crawl=h < 0.05)
    if h < 1:
        # comes down from the twig top -> hanging
        off = (1 - h)
        pts = [(x + off * 0, y - off * 30) for x, y in pts]
    w = ease_in_out(prog(t, t1 + 0.3, 1.8))
    ca = 1 - prog(w, 0.55, 0.3)
    if ca > 0: caterpillar(c, pts, 1.1, t, mood='happy', alpha=int(255 * ca))
    if w > 0:
        c.save(); c.clipRect(skia.Rect(0, 0, W, TY + 20 + 380 * w))
        chrysalis(c, TX, TY + 10, 1.15, t, face_on=w > 0.95)
        c.restore()
        if w < 1:
            yy = TY + 20 + 380 * w
            for j in range(5):
                c.drawCircle(TX - 100 + j * 50 + math.sin(t * 8 + j) * 6, yy, 8, P(color=col('#ffffff', 220)))
    stars_around(c, t, TX, TY + 230, 300, 230, prog(t, t1 + 2.1, 0.5), n=5)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 2.1, 'sparkle')]

# ---------- 5: Soup inside, new parts, building blocks ----------
BLK = ['#ff6b6b', '#ffd23f', '#4cd964', '#2fa8ff', '#b28dff', '#ff9f1c', '#ff8fab', '#3fd0c9']
def s5(c, t, D, cues):
    garden(c, t + 70, seed=5)
    c.drawRect(skia.Rect(0, 0, W, H), P(color=col('#1b2a5a', 150)))
    stars(c, t, seed=4, n=30, y0=600, y1=1500, a=0.5)
    t0, t1, t2 = cues[0]['start'], cues[1]['start'], cues[2]['start']
    cx, top, s = 330, 650, 1.85
    cut = chrysalis_path(cx, top, s)  # attach at top, scaled
    m = skia.Matrix(); m.setScale(1.0, 1.0)
    c.drawLine(cx, top - 30, cx, top + 45 * s, P(color=col('#6b4423'), stroke=12))
    c.drawPath(cut, P(color=col('#000000', 50), blur=12))
    c.drawPath(cut, lin(c, (0, top, 0, top + 150 * s), [col('#bff0a0'), col('#4fb85a')]))
    c.save(); c.clipPath(cut, doAntiAlias=True)
    soup = prog(t, t0 + 0.4, 1.0)
    c.drawRect(skia.Rect(0, top, W, top + 720), rad(cx, top + 380, 300, [col('#f4ffd6', int(230 * soup)), col('#bfe87a', int(230 * soup)), col('#8fd05a', int(230 * soup))]))
    for i in range(14):
        ang = t * (1.2 + (i % 3) * 0.4) + i
        rr = 40 + (i * 13) % 120
        x = cx + math.cos(ang) * rr * 0.9; y = top + 400 + math.sin(ang) * rr * 1.6
        c.drawCircle(x, y, 14 + (i % 4) * 5, P(color=col(['#ffffff', '#ffe14d', '#a6f07a'][i % 3], int(200 * soup))))
    bf = ease_out(prog(t, t1 + 0.4, 2.0))
    if bf > 0:
        butterfly(c, cx, top + 400, 0.95, t, flap=0.5, unfold=bf * 0.5, face_on=bf > 0.7, alpha=int(255 * bf))
    c.restore()
    c.drawPath(cut, P(color=col('#ffffff', 220), stroke=6))
    if soup > 0:
        for j in range(3):
            u = (t * 0.6 + j / 3) % 1.0
            c.drawCircle(cx - 120 + j * 120, top + 120 - u * 60, 10 * (1 - u), P(color=col('#ffffff', int(200 * (1 - u)))))
    # building blocks: caterpillar row -> butterfly shape
    b = ease_back(prog(t, t2, 0.4))
    if b > 0:
        r_ = ease_in_out(prog(t, t2 + 0.7, 1.6))
        row = [(600 + i * 40, 1180) for i in range(8)]
        wing = [(650, 1010), (610, 1080), (650, 1150), (690, 1080), (850, 1010), (890, 1080), (850, 1150), (770, 1080)]
        for i in range(8):
            x = lerp(row[i][0], wing[i][0], r_) + math.sin(r_ * math.pi) * (i - 4) * 12
            y = lerp(row[i][1], wing[i][1], r_) - math.sin(r_ * math.pi) * 120
            sz = 34 * b
            c.save(); c.translate(x, y); c.rotate(math.sin(r_ * math.pi) * 90 * (1 if i % 2 else -1))
            c.drawRoundRect(skia.Rect(-sz, -sz, sz, sz), 10, 10, lin(c, (0, -sz, 0, sz), [col(mix_hx(BLK[i], '#ffffff', 0.35)), col(BLK[i])]))
            c.drawRoundRect(skia.Rect(-sz, -sz, sz, sz), 10, 10, P(color=col('#000000', 50), stroke=4))
            c.drawCircle(-sz * 0.4, -sz * 0.4, sz * 0.2, P(color=col('#ffffff', 120)))
            c.restore()
        if r_ > 0.95:
            c.drawRoundRect(skia.Rect(760, 990, 780, 1180), 10, 10, P(color=col('#5a4030')))
            face(c, 770, 960, 34, t, 2)

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'sparkle'), (cues[1]['start'] + 0.4, 'sparkle'), (cues[2]['start'] + 0.7, 'whoosh'), (cues[2]['start'] + 2.3, 'pop')]

# ---------- 6: Out comes a butterfly ----------
def s6(c, t, D, cues):
    garden(c, t + 40, seed=6)
    twig(c, TY, t)
    t0, t1 = cues[0]['start'], cues[1]['start']
    clear = ease_in_out(prog(t, 0.1, 1.2))
    op = prog(t, t0 + 1.0, 0.6)
    if op < 1:
        chrysalis(c, TX, TY + 10, 1.15, t, clear=clear, shake=1.0 if t > t0 + 0.3 else 0, alpha=int(255 * (1 - op)), face_on=False)
    if op > 0:
        c.drawLine(TX, TY - 10, TX, TY + 40, P(color=col('#6b4423'), stroke=9))
        unf = ease_out(prog(t, t1 + 0.2, 1.8))
        fly = ease_in_out(prog(t, t1 + 2.4, 1.8))
        bx = lerp(TX, 760, fly) + math.sin(t * 3) * 20 * fly; by = lerp(TY + 230, 900, fly)
        flap = None if fly > 0 else (0.35 + 0.3 * unf + (0.15 * math.sin(t * 3) if unf > 0.9 else 0))
        butterfly(c, bx, by, 0.75 * ease_out(op), t, flap=flap, unfold=unf if t > t1 else 0.0, rot=lerp(0, -12, ease_in_out(prog(t, t1 + 1.8, 0.8))))
        if t > t1 + 0.3 and unf < 1:
            for j in range(4):
                u = (t * 1.5 + j / 4) % 1.0
                c.drawCircle(bx - 150 + j * 100, by - 20 - u * 50, 8 * (1 - u), P(color=col('#ffffff', int(220 * (1 - u)))))
        stars_around(c, t, bx, by, 280, 200, prog(t, t0 + 1.2, 0.5) * (1 - fly * 0.5), n=5)

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'boing'), (cues[0]['start'] + 1.0, 'sparkle'), (cues[1]['start'] + 2.4, 'whoosh')]

# ---------- 7: Bonus: taste with their feet ----------
def s7(c, t, D, cues):
    garden(c, t + 50, seed=7)
    big_leaf(c, 520, 1330, 2.2, t, rot=-4)
    t0, t1 = cues[0]['start'], cues[1]['start']
    land = ease_in_out(prog(t, 0.1, 1.6))
    bx = lerp(1150, 520, land); by = lerp(800, 1130, land) + math.sin(t * 3) * 10 * (1 - land)
    fl = None if land < 1 else 0.75 + 0.2 * math.sin(t * 2)
    s = 0.85
    if land >= 1:
        for sx in (-1, 1):
            for k, dy in enumerate((20, 50, 80)):
                c.drawLine(bx + sx * 10, by + dy * s, bx + sx * (40 + k * 12), by + (dy + 70) * s, P(color=col('#2b1d14'), stroke=6))
    butterfly(c, bx, by, s, t, flap=fl, seed=2, colors=PINK_WINGS)
    fa = prog(t, t0 + 1.2, 0.5)
    if fa > 0 and land >= 1:
        for sx in (-1, 1):
            for k in range(3):
                fx, fy = bx + sx * (40 + k * 12), by + ((20, 50, 80)[k] + 70) * s
                pul = 0.5 + 0.5 * math.sin(t * 6 + k + sx)
                c.drawCircle(fx, fy, 14 + 8 * pul, P(color=col('#ffe14d', int(200 * fa)), stroke=5))
    ya = ease_back(prog(t, t1 + 0.8, 0.5), 2)
    if ya > 0:
        c.save(); c.translate(760, 1000); c.scale(ya, ya); c.rotate(math.sin(t * 3) * 6)
        c.drawRoundRect(skia.Rect(-110, -60, 110, 60), 40, 40, P(color=col('#ffffff')))
        tl = skia.Path(); tl.moveTo(-60, 50); tl.lineTo(-100, 100); tl.lineTo(-20, 55); tl.close(); c.drawPath(tl, P(color=col('#ffffff')))
        text_block(c, 'Yum!', 0, 0, size=60, fill='#ff6b9a', stroke='#ffffff')
        c.restore()
    if t > t1 + 1.5:
        e = ease_back(prog(t, t1 + 1.5, 0.4), 2)
        for k in range(3):
            egg(c, 360 + k * 46, 1330 + (k % 2) * 10, 18 * e, t)

def s7_sfx(D, cues): return [(0.2, 'whoosh'), (cues[0]['start'] + 1.2, 'sparkle'), (cues[1]['start'] + 0.8, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    garden(c, t + 60, seed=8)
    s = max(0.0, ease_back(prog(t, 0.0, 0.7), 2.0))
    butterfly(c, 540, 1040 + math.sin(t * 2) * 20, 1.05 * s, t, seed=5)
    for i, wc in enumerate([BUTTERFLY_WINGS, BLUE_WINGS, PINK_WINGS, BLUE_WINGS]):
        ang = t * 0.8 + i * math.pi / 2
        butterfly(c, 540 + math.cos(ang) * 380, 1060 + math.sin(ang) * 300, 0.35, t, seed=i, colors=wc, face_on=False)
    follow_button(c, t, cues[-1]['start'])

def s8_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='How does a caterpillar turn into a butterfly?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('How does a caterpillar turn into a butterfly?', 'How does a CATERPILLAR become a BUTTERFLY?'),
            ("Let's find out!", "Let's find out!")], tail=1.1),
        dict(name='egg', draw=s2, sfx_fn=s2_sfx, lines=[
            ('It all starts with a tiny egg on a leaf.', 'It starts as a tiny EGG'),
            ('Out hatches a tiny, hungry caterpillar!', 'Out comes a CATERPILLAR!')], tail=1.6),
        dict(name='eat', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The caterpillar eats and eats, and grows and grows.', 'It EATS and GROWS!'),
            ('When its skin gets too tight, it wiggles out of it, like outgrowing your clothes!', 'Too tight? A NEW skin!')], tail=1.6),
        dict(name='hang', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Then it hangs upside down from a twig.', 'It hangs UPSIDE DOWN'),
            ('And it makes a hard case around itself, called a chrysalis.', 'It makes a CHRYSALIS')], tail=1.7),
        dict(name='soup', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Inside, something amazing happens. Its body turns into a kind of soup!', 'Inside: a kind of SOUP!'),
            ('That soup builds brand-new parts: wings, legs and antennae.', 'It builds new WINGS!'),
            ("It's like taking apart your building blocks and building something new!", 'Like rebuilding with BLOCKS!')], tail=1.6),
        dict(name='hatch', draw=s6, sfx_fn=s6_sfx, lines=[
            ('After a week or two, out comes a butterfly!', 'Out comes a BUTTERFLY!'),
            ('It pumps up its crumpled wings, lets them dry, and flies away!', 'Pump, DRY, fly away!')], tail=1.8),
        dict(name='feet', draw=s7, sfx_fn=s7_sfx, lines=[
            ('And guess what? Butterflies taste with their feet!', 'They TASTE with their FEET!'),
            ("That's how they find the right leaf for their eggs.", 'The right leaf for EGGS!')], tail=1.7),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.4),
    ])
