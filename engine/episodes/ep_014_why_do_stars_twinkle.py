"""Episode 14 (EN): Why do stars twinkle?"""
import math, random
from lib import *

DARK_HILLS = dict(c1='#3c6e4a', c2='#2b5238', dark=True, flowers=False)

def night_bg(c, t, seed=21, hy=1620, trees=True):
    night_sky(c, t, seed=seed, n=90, y1=hy - 120)
    moonglow = rad(900, 300, 500, [col('#9fb4ff', 40), col('#9fb4ff', 0)])
    c.drawRect(skia.Rect(0, 0, W, H), moonglow)
    hills(c, hy, t=t, trees=trees, **DARK_HILLS)

def wob(t, seed=0):
    """Smooth pseudo-random flicker 0..1."""
    return 0.5 + 0.22 * math.sin(t * 7.3 + seed) + 0.17 * math.sin(t * 11.9 + seed * 2.1) + 0.11 * math.sin(t * 17.3 + seed * 0.7)

def air_blob(c, x, y, r, t, warm=True, seed=0, alpha=255, face_on=True):
    hx = '#ffb27a' if warm else '#8fd0ff'
    a = int(alpha)
    c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.3, r * 1.4, [col('#ffffff', int(a * 0.55)), col(hx, int(a * 0.5)), col(hx, int(a * 0.25))], [0, 0.5, 1]))
    c.drawCircle(x, y, r, P(color=col('#ffffff', int(a * 0.35)), stroke=4))
    if face_on and a > 200: face(c, x, y + r * 0.1, r * 0.55, t, seed)

# ---------- 1: Hook ----------
def s1(c, t, D, cues):
    night_bg(c, t, 21)
    a = ease_back(prog(t, 0.05, 0.8), 1.6)
    br = wob(t, 1)
    c.save(); c.translate(540, 980 + math.sin(t * 2) * 10); c.scale(a, a)
    star_char(c, 0, 0, 170, t, mood='wow' if t < 2.0 else 'happy', bright=0.6 + 0.9 * br, rot=math.sin(t * 1.5) * 6)
    c.restore()
    for i in range(6):
        ang = i / 6 * 2 * math.pi + t * 0.5
        x, y = 540 + math.cos(ang) * 330, 980 + math.sin(ang) * 300
        k = prog(t, 0.5 + i * 0.12, 0.3)
        if k > 0: twinkle(c, x, y, 34 * ease_back(k) * (0.6 + 0.6 * wob(t, i * 3)), '#fff3b0', rot=t * 30)
    kid(c, 540, 1700, 0.8, t, wave=t > cues[-1]['start'])

def s1_sfx(D, cues): return [(0.2, 'sparkle')]

# ---------- 2: Stars are giant suns, far away ----------
def s2(c, t, D, cues):
    t1 = cues[1]['start']
    k = ease_in_out(prog(t, t1 - 0.6, 2.2))
    top = mix_hx('#2f9bff', '#0b1036', k); bot = mix_hx('#cdeeff', '#3b3f8f', k)
    sky(c, top, bot)
    if k > 0.2: stars(c, t, 33, 80, y1=1500, a=(k - 0.2) / 0.8)
    r = lerp(230, 9, k); x = lerp(540, 760, k); y = lerp(1050, 760, k)
    if k < 0.97:
        sun(c, x, y, r, t, mood='happy')
    else:
        twinkle(c, x, y, 40 * (0.7 + 0.5 * wob(t, 2)), '#fff3b0', rot=t * 20)
    if t > t1 + 1.2:
        # little dotted "far away" path from viewer to star
        g = ease_out(prog(t, t1 + 1.2, 1.0))
        for i in range(14):
            u = i / 14
            if u > g: break
            c.drawCircle(lerp(300, 740, u), lerp(1450, 790, u), 7, P(color=col('#ffffff', 170)))
    hills(c, 1640, t=t, trees=False, c1=mix_hx('#7ed957', '#3c6e4a', k), c2=mix_hx('#56b83a', '#2b5238', k), flowers=False)
    kid(c, 300, 1720, 0.75, t)

def s2_sfx(D, cues): return [(cues[1]['start'] - 0.4, 'whoosh'), (cues[1]['start'] + 1.6, 'sparkle')]

# ---------- 3: Long trip, then our air ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_sky(c, t, seed=41, n=80, y1=1100)
    air = ease_in_out(prog(t, t1, 0.9))
    # air layer above the ground
    if air > 0:
        c.drawRect(skia.Rect(0, 1150, W, 1650), lin(c, (0, 1150, 0, 1650), [col('#6fb8ff', 0), col('#6fb8ff', int(110 * air)), col('#9fd6ff', int(150 * air))], pos=[0, 0.35, 1]))
        for i in range(6):
            x = (i * 210 + t * 40) % (W + 200) - 100
            y = 1300 + (i % 3) * 90
            sw = skia.Path(); sw.moveTo(x - 80, y); sw.cubicTo(x - 30, y - 40, x + 30, y + 40, x + 80, y)
            c.drawPath(sw, P(color=col('#ffffff', int(120 * air)), stroke=7))
    hills(c, 1660, t=t, trees=True, **DARK_HILLS)
    star_char(c, 540, 700, 80, t, bright=0.9, rot=math.sin(t) * 5)
    # light ball zooming down
    T = 2.6
    for q in range(2):
        start = t0 + 0.3 + q * 1.5
        if t < start: continue
        u = ((t - start) / T) % 1.0
        def f(tt, start=start):
            uu = ((tt - start) / T) % 1.0
            yy = lerp(790, 1560, uu)
            wig = 0 if yy < 1180 else math.sin(tt * 14 + q) * 30 * air * (yy - 1180) / 380
            return 540 + wig, yy
        x, y = f(t)
        if u > 0.06: trail(c, [f(t - k * 0.02) for k in range(12, -1, -1)], '#fff3b0', 18)
        photon(c, x, y, 28, '#ffe14d', t, q, alpha=int(255 * min(1, (1 - u) * 6)))

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 0.2, 'whoosh')]

# ---------- 4: Moving air bends light ----------
BLOBS = [(170, 1000, True), (420, 1080, False), (690, 990, True), (900, 1100, False), (280, 1260, False), (560, 1300, True), (820, 1330, True), (150, 1470, True), (450, 1500, False), (740, 1510, False)]
def blob_pos(i, t):
    bx, by, w = BLOBS[i]
    return bx + math.sin(t * 0.9 + i * 1.7) * 50, by + math.cos(t * 0.7 + i) * 30, w

def bent_path(t):
    pts = []
    for k in range(25):
        y = lerp(640, 1600, k / 24)
        x = 540
        if y > 900:
            x += (math.sin(t * 2.3 + y * 0.012) * 55 + math.sin(t * 3.7 - y * 0.02) * 30) * (y - 900) / 700
        pts.append((x, y))
    return pts

def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#151a4a', '#3d58a8', mid='#26307a'); stars(c, t, 51, 50, y1=900)
    for i in range(len(BLOBS)):
        a = ease_back(prog(t, t0 + i * 0.12, 0.45))
        if a <= 0: continue
        x, y, w = blob_pos(i, t)
        c.save(); c.translate(x, y); c.scale(a, a); air_blob(c, 0, 0, 78, t, w, i); c.restore()
    if t0 + 1.2 < t:
        k = prog(t, t0 + 1.2, 1.0)
        for i in range(4):
            cx = 160 + i * 250; cy = 880 + (i % 2) * 60
            curved_arrow(c, cx, cy, 55, t * 160 + i * 90, t * 160 + i * 90 + 250, '#ffffff', 9, alpha=int(150 * k))
    if t > t1 - 0.2:
        g = ease_out(prog(t, t1 - 0.2, 1.0))
        pts = bent_path(t); n = max(2, int(len(pts) * g))
        pth = skia.Path(); pth.moveTo(*pts[0])
        for p in pts[1:n]: pth.lineTo(*p)
        glow = P(color=col('#fff3b0', 110), stroke=46, blur=14); glow.setPathEffect(skia.CornerPathEffect.Make(60))
        core = P(color=col('#fffbe0'), stroke=16); core.setPathEffect(skia.CornerPathEffect.Make(60))
        c.drawPath(pth, glow); c.drawPath(pth, core)
        x, y = pts[n - 1]; photon(c, x, y, 26, '#ffe14d', t, 4, face_on=False)
    star_char(c, 540, 650, 62, t, bright=0.8)

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.2 + i * 0.25, 'pop') for i in range(3)] + [(cues[1]['start'], 'whoosh')]

# ---------- 5: Wiggle -> twinkle ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_bg(c, t + 30, 61)
    sx, sy = 560, 720
    ex, ey = 520, 1340
    pth = skia.Path(); pth.moveTo(sx, sy + 60)
    for k in range(1, 21):
        u = k / 20; y = lerp(sy + 60, ey, u)
        x = lerp(sx, ex, u) + math.sin(t * 9 + u * 9) * 40 * math.sin(u * math.pi) * (1 if t > t0 else 0.2)
        pth.lineTo(x, y)
    g = P(color=col('#fff3b0', 70), stroke=34, blur=10); g.setPathEffect(skia.CornerPathEffect.Make(40))
    cr = P(color=col('#fffbe0', 200), stroke=10); cr.setPathEffect(skia.CornerPathEffect.Make(40))
    c.drawPath(pth, g); c.drawPath(pth, cr)
    br = wob(t * 0.8, 5) if t > t0 else 0.5
    if t > t1:
        br = 0.15 + 0.85 * clamp((math.sin((t - t1) * 5.0) * 0.5 + 0.5) ** 0.7)
    sc = 0.85 + 0.3 * br
    star_char(c, sx, sy, 90 * sc, t, bright=0.3 + 1.2 * br, rot=math.sin(t * 2) * 5)
    if br > 0.6:
        twinkle(c, sx + 120, sy - 70, 46 * (br - 0.4), '#ffffff', rot=t * 40)
        twinkle(c, sx - 115, sy + 40, 34 * (br - 0.4), '#fff3b0', rot=-t * 30)
    if t > t1:
        # brightness meter on the left
        mx, my0, my1 = 150, 1300, 820
        c.drawRoundRect(skia.Rect(mx - 30, my1, mx + 30, my0), 30, 30, P(color=col('#ffffff', 60)))
        lvl = lerp(my0, my1, br)
        c.drawRoundRect(skia.Rect(mx - 22, lvl, mx + 22, my0 - 8), 22, 22, lin(c, (0, my1, 0, my0), [col('#fffbd6'), col('#ffb627')]))
        c.drawRoundRect(skia.Rect(mx - 30, my1, mx + 30, my0), 30, 30, P(color=col('#ffffff', 200), stroke=5))
    kid(c, 520, 1720, 0.85, t, wave=t > t1 + 1.5)

def s5_sfx(D, cues): return [(cues[1]['start'] + k * 1.26 + 0.3, 'sparkle') for k in range(2)]

# ---------- 5b: Low stars twinkle more (more air) ----------
def s5b(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night_sky(c, t, seed=91, n=80, y1=1450)
    ex, ey = 260, 1380
    air = ease_in_out(prog(t, t1 - 0.2, 0.9))
    # air layer as a thick band hugging the ground
    c.drawRect(skia.Rect(0, 1080, W, 1700), lin(c, (0, 1080, 0, 1700), [col('#6fb8ff', 0), col('#6fb8ff', int(90 + 90 * air)), col('#a9dcff', int(120 + 100 * air))], pos=[0, 0.4, 1]))
    hills(c, 1660, t=t, trees=False, **DARK_HILLS)
    hi = (330, 690); lo = (900, 1150)
    def ray(a, b, amp, seg=22):
        pth = skia.Path(); pth.moveTo(*a)
        for k in range(1, seg + 1):
            u = k / seg; x = lerp(a[0], b[0], u); y = lerp(a[1], b[1], u)
            inair = clamp((y - 1080) / 200)
            nx, ny = -(b[1] - a[1]), (b[0] - a[0]); L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
            w = math.sin(t * 10 + u * 14) * amp * inair * air
            pth.lineTo(x + nx * w, y + ny * w)
        return pth
    for (a, amp, delay) in ((hi, 10, 0.0), (lo, 34, 0.4)):
        g = ease_out(prog(t, t0 + delay, 0.8))
        if g <= 0: continue
        b = (lerp(a[0], ex, g), lerp(a[1], ey - 60, g))
        pth = ray(a, b, amp)
        gp = P(color=col('#fff3b0', 80), stroke=30, blur=10); gp.setPathEffect(skia.CornerPathEffect.Make(40))
        cp = P(color=col('#fffbe0', 210), stroke=9); cp.setPathEffect(skia.CornerPathEffect.Make(40))
        c.drawPath(pth, gp); c.drawPath(pth, cp)
    star_char(c, hi[0], hi[1], 62, t, bright=0.8, rot=math.sin(t) * 4)
    br = wob(t * 1.3, 9) if t > t1 else 0.6
    star_char(c, lo[0], lo[1], 52 * (0.8 + 0.4 * br), t, seed=3, bright=0.2 + 1.5 * br, mood='wow' if t > t1 else 'happy')
    if t > t1 and br > 0.55:
        twinkle(c, lo[0] + 75, lo[1] - 60, 40 * (br - 0.3), '#ffffff', rot=t * 50)
    kid(c, ex, 1730, 0.75, t)

def s5b_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 6: Bonus: no twinkle in space ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#02030a', '#141a3e', mid='#080b22')
    rnd = random.Random(71)
    for i in range(120):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H); r = rnd.uniform(1.5, 4.5)
        c.drawCircle(x, y, r, P(color=col('#ffffff', 230)))
    earth(c, 980, 1800, 520, t, rot=t * 0.02, face_on=False)
    # thin air line around Earth
    c.drawCircle(980, 1800, 540, P(color=col('#8fd0ff', 120), stroke=16, blur=6))
    star_char(c, 300, 760, 70, t, bright=0.7, face_on=True)
    star_char(c, 820, 700, 48, t, seed=2, bright=0.7, face_on=False)
    fl = math.sin(t * 1.1) * 25
    c.save(); c.translate(500, 1250 + fl); c.rotate(-12 + math.sin(t * 0.8) * 6)
    kid(c, 0, 0, 0.95, t, helmet=True, wave=t > t1)
    c.restore()
    if t > t1 + 0.4:
        k = ease_back(prog(t, t1 + 0.4, 0.5))
        c.save(); c.translate(780, 950); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-140, -55, 140, 55), 40, 40, P(color=col('#ffffff', 235)))
        text_block(c, 'steady!', 0, 0, size=60, fill='#2b3a8a', stroke='#ffffff')
        c.restore()

def s6_sfx(D, cues): return [(0.1, 'whoosh'), (cues[1]['start'] + 0.4, 'pop')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    night_bg(c, t + 70, 81)
    s = ease_back(prog(t, 0.0, 0.7), 2.0)
    c.save(); c.translate(540, 1030 + math.sin(t * 2) * 12); c.scale(s, s)
    star_char(c, 0, 0, 160, t, bright=0.7 + 0.8 * wob(t, 3), rot=math.sin(t * 1.4) * 6)
    c.restore()
    for i in range(6):
        ang = t * 0.9 + i * math.pi / 3
        x, y = 540 + math.cos(ang) * 360, 1030 + math.sin(ang) * 300
        star_char(c, x, y, 40, t, seed=i, face_on=False, bright=0.4 + 0.8 * wob(t, i), rot=t * 40 + i * 20)
    follow_button(c, t, cues[-1]['start'])

def s7_sfx(D, cues): return [(0.1, 'sparkle'), (cues[-1]['start'] + 0.1, 'pop')]

EPISODE = dict(
    title='Why do stars twinkle?',
    music=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lines=[
            ('Why do stars twinkle?', 'Why do stars TWINKLE?'),
            ("Let's find out!", "Let's find out!")], tail=0.9),
        dict(name='suns', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every star is a giant sun, just like ours.', 'Every star is a giant SUN!'),
            ('But they are so far away, they look like tiny dots of light.', 'So FAR away, they look TINY')], tail=1.6),
        dict(name='trip', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Starlight travels for a very, very long time to reach us.', 'Starlight takes a LONG trip'),
            ('And at the very end, it has to pass through our air.', 'At the end: through our AIR!')], tail=1.5),
        dict(name='bend', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Our air is always moving. Warm and cool bits swirl around.', 'Warm and cool air SWIRLS'),
            ('Each bit bends the light a tiny bit, like looking through wavy water.', 'It BENDS light – like wavy water!')], tail=1.4),
        dict(name='twinkle', draw=s5, sfx_fn=s5_sfx, lines=[
            ('So the starlight wiggles and jiggles on its way to your eyes.', 'Starlight WIGGLES to your eyes'),
            ("Brighter, dimmer, brighter. That's the twinkle!", "Bright, dim, bright: TWINKLE!")], tail=1.6),
        dict(name='low', draw=s5b, sfx_fn=s5b_sfx, lines=[
            ('Stars low in the sky twinkle even more.', 'LOW stars twinkle even MORE'),
            ('Their light has to travel through much more air to reach you!', 'Their light crosses MORE air!')], tail=1.5),
        dict(name='space', draw=s6, sfx_fn=s6_sfx, lines=[
            ("And guess what? Up in space, there's no air.", 'In SPACE there is no air!'),
            ("So astronauts see the stars shine steady, with no twinkle at all!", 'Stars shine STEADY up there!')], tail=1.5),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, lines=[
            ('Now you know!', 'Now you know!'),
            ('Can you explain it to a grown-up?', 'Explain it to a GROWN-UP!'),
            ('Follow for more why questions!', 'Follow for more WHY questions!')], tail=2.2),
    ])
