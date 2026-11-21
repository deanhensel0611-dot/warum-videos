"""Episode 26 (EN, general audience): How do echoes work?
Facts checked (Wikipedia "Echo", JoVE Physics "Echo", Britannica "Echo", Wikipedia "Human echolocation"):
- Sound is a pressure wave: air is squeezed and stretched as the wave passes; in air at ~20 C it travels ~343 m/s.
- An echo is sound reflected back by a surface. Hard, smooth surfaces (rock, concrete) reflect well; soft, porous
  surfaces (curtains, carpet, fresh snow) absorb much of the sound.
- The ear/brain only hears a separate echo if the reflection arrives at least ~0.1 s after the original sound;
  sound covers ~34 m in 0.1 s, so the surface must be at least ~17 m away. Closer reflections blend into the
  original sound (reverberation).
- Echo delay gives distance: sound goes there and back, so distance = 343 m/s x time / 2 (1 s -> about 170 m).
- Bats and dolphins use echolocation; some blind people learn human echolocation with tongue clicks.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
WAVE = '#2f9bff'

def canyon_bg(c, t, top='#bfe4ff', bot='#ffe9cf'):
    sky(c, top, bot)
    clouds(c, t, seed=4, n=3, y0=640, y1=900, speed=14, a=200)

def rings_dir(c, x, y, t, start, a0, sweep=70, n=3, colr='#ffffff', speed=520, life=1.4, w=12):
    """Directional sound arcs only (one side)."""
    sound_rings(c, x, y, t, start, n=n, colr=colr, speed=speed, life=life, w=w, a0=a0, sweep=sweep, both=False)

def pulse(c, x0, x1, y, t, start, speed, colr='#ffffff', ret_at=None, w=12, alpha=230, h=110):
    """A wavefront (vertical arc) travelling from x0 to x1 and, if ret_at is given, bouncing back."""
    if t < start: return None
    d = (t - start) * speed
    L = abs(x1 - x0)
    if d <= L:
        x = x0 + math.copysign(d, x1 - x0); back = False
    elif ret_at is not None:
        x = x1 - math.copysign(min(d - L, L), x1 - x0); back = True
        if d - L > L: return None
    else:
        return None
    sgn = (1 if (x1 > x0) != back else -1)
    p = skia.Path(); p.moveTo(x - sgn * 30, y - h); p.quadTo(x + sgn * 30, y, x - sgn * 30, y + h)
    al = alpha if not back else int(alpha * 0.6)
    c.drawPath(p, P(color=col(colr, al), stroke=w))
    p2 = skia.Path(); p2.moveTo(x - sgn * 70, y - h * 0.75); p2.quadTo(x - sgn * 10, y, x - sgn * 70, y + h * 0.75)
    c.drawPath(p2, P(color=col(colr, int(al * 0.5)), stroke=w * 0.7))
    return x, back

# ---------- 1: Hook (cold open: shout already travelling) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    canyon_bg(c, t)
    cliff(c, 820, 900, 400, seed=5)
    cliff(c, 150, 1250, 300, side=-1, seed=8, c1='#d79a6a', c2='#b07045')
    megaphone(c, 120, 1150, 0.9, rot=-6)
    # shout leaves at 0.05 s, hits cliff, comes back
    period = 3.4
    st = 0.05 + ((t - 0.05) // period) * period if t > 0.05 else 0.05
    r = pulse(c, 280, 800, 1150, t, st, 520, colr=NAVY, ret_at=True, w=13)
    label_pill(c, 'HELLO!', 300, 960, size=50, k=ease_back(prog(t, 0.1, 0.35)), fill=NAVY, hi='#ff5c85')
    if r and r[1]:
        k = ease_back(prog(t, st + 1.0, 0.35))
        label_pill(c, '...hello!', 640, 1360, size=44, k=k, fill='#5a6a8a', alpha=200)
    if t > t1:
        label_pill(c, 'a moment LATE', 540, 1600, size=46, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s1_sfx(D, cues):
    return [(0.05, 'whoosh'), (0.1, 'pop'), (1.05, 'click'), (cues[1]['start'] + 1.6, 'pop')]

# ---------- 2: Sound = wave of squeezed air (ripple in a pond) ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9f5ff', '#d4ecff')
    # rows of air dots, compressed bands travelling right
    rnd = random.Random(2)
    for row in range(7):
        y = 820 + row * 80
        for i in range(22):
            bx = 60 + i * 42 + rnd.uniform(-6, 6)
            ph = (bx * 0.012 - t * 5.0)
            dx = 18 * math.sin(ph) if t > t0 + 0.3 else 0
            dens = 0.5 + 0.5 * math.cos(ph)
            colr = mix_hx('#8fc7ff', WAVE, dens if t > t0 + 0.3 else 0.3)
            c.drawCircle(bx + dx, y + rnd.uniform(-8, 8), 13, P(color=col(colr)))
    megaphone(c, 40, 1060, 0.7, alpha=255)
    if t > t0 + 0.8:
        label_pill(c, 'SQUEEZED air', 330, 740, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#2f9bff')
    # pond ripple inset
    if t > t0 + 2.2 and t < t1 + 0.2:
        k = ease_back(prog(t, t0 + 2.2, 0.5))
        c.save(); c.translate(760, 1470); c.scale(k, k)
        c.drawOval(skia.Rect(-170, -80, 170, 80), P(color=col('#4fb3ff')))
        for i in range(4):
            rr = ((t * 70 + i * 40) % 160)
            c.drawOval(skia.Rect(-rr, -rr * 0.45, rr, rr * 0.45), P(color=col('#ffffff', int(220 * (1 - rr / 160))), stroke=5))
        c.restore()
        label_pill(c, 'like a RIPPLE', 760, 1330, size=40, k=k, fill=NAVY, hi='#2f9bff')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.5, 0.5), 2.2)
        c.save(); c.translate(540, 1500); c.scale(k, k)
        text_block(c, '343 m', 0, -10, size=120, fill=NAVY, stroke='#ffffff')
        text_block(c, 'every SECOND', 0, 90, size=52, fill=NAVY, hi='#ff5c85', stroke='#ffffff')
        c.restore()

def s2_sfx(D, cues):
    return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[0]['start'] + 2.2, 'pop'), (cues[1]['start'] + 0.5, 'pop')]

# ---------- 3: Hard surface bounces it, like a ball off a wall ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    canyon_bg(c, t, top='#d8eeff', bot='#fff1dc')
    # stone wall right
    c.drawRect(skia.Rect(780, 640, 900, 1640), lin(c, (780, 0, 900, 0), [col('#c6ccd8'), col('#9aa3b5')], vertical=False))
    for j in range(10):
        yy = 640 + j * 100; off = 0 if j % 2 else 60
        c.drawLine(780, yy, 900, yy, P(color=col('#7d869a'), stroke=4))
        c.drawLine(780 + off, yy, 780 + off, yy + 100, P(color=col('#7d869a'), stroke=4))
    c.drawLine(780, 640, 780, 1640, P(color=col(NAVY), stroke=6))
    label_pill(c, 'HARD', 840, 1600 - 20, size=40, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi='#ff5c85')
    # ball bouncing (top half)
    per = 1.6; u = ((t - t0) % per) / per if t > t0 else 0
    xb = lerp(180, 742, 1 - abs(1 - 2 * u)); yb = 920 + 40 * math.sin(u * math.pi)
    sq = max(0, 1 - abs(u - 0.5) / 0.05) if 0.45 < u < 0.55 else 0
    hist = []
    for k in range(10):
        uu = u - k * 0.02
        if uu < 0: break
        hist.append((lerp(180, 742, 1 - abs(1 - 2 * uu)), 920 + 40 * math.sin(uu * math.pi)))
    if len(hist) > 2: trail(c, hist[::-1], '#ff5c85', 14)
    ball(c, xb, yb, 38, squash=sq)
    # sound pulse bouncing (bottom half)
    if t > t1:
        st = t1 + 0.4 + ((t - t1 - 0.4) // 2.2) * 2.2 if t > t1 + 0.4 else t1 + 0.4
        pulse(c, 200, 770, 1300, t, st, 600, colr=WAVE, ret_at=True)
        megaphone(c, 60, 1300, 0.75)
        label_pill(c, 'BOUNCES back', 420, 1540, size=44, k=ease_back(prog(t, t1 + 1.3, 0.4)), fill=NAVY, hi='#2f9bff')

def s3_sfx(D, cues):
    s = [(cues[0]['start'] + 0.5, 'pop')]
    for k in range(4):
        tt = cues[0]['start'] + 0.8 + k * 1.6
        if tt < cues[1]['start']: s.append((tt, 'click'))
    s += [(cues[1]['start'] + 0.4, 'whoosh'), (cues[1]['start'] + 1.3, 'pop')]
    return s

# ---------- 4: Soft things swallow sound (empty vs furnished room) ----------
def room(c, x, y, w_, h_, furnished, t, st):
    c.drawRoundRect(skia.Rect(x, y, x + w_, y + h_), 24, 24, P(color=col('#fff8ef')))
    c.drawRect(skia.Rect(x, y + h_ * 0.78, x + w_, y + h_), P(color=col('#e8cfae')))
    c.drawRoundRect(skia.Rect(x, y, x + w_, y + h_), 24, 24, P(color=col(NAVY), stroke=7))
    cx, cy = x + w_ / 2, y + h_ * 0.45
    if furnished:
        # curtains, sofa, rug
        for sx in (x + 16, x + w_ - 76):
            pth = skia.Path(); pth.moveTo(sx, y + 14); pth.lineTo(sx + 60, y + 14)
            pth.quadTo(sx + 70, y + h_ * 0.4, sx + 60, y + h_ * 0.76); pth.lineTo(sx, y + h_ * 0.76); pth.close()
            c.drawPath(pth, lin(c, (sx, 0, sx + 60, 0), [col('#ff8fa8'), col('#ff5c85')], vertical=False))
            for k in range(3): c.drawLine(sx + 12 + k * 18, y + 30, sx + 12 + k * 18, y + h_ * 0.74, P(color=col('#d94a70', 140), stroke=3))
        c.drawRoundRect(skia.Rect(cx - 120, y + h_ * 0.6, cx + 120, y + h_ * 0.8), 22, 22, P(color=col('#2f9bff')))
        c.drawRoundRect(skia.Rect(cx - 130, y + h_ * 0.52, cx + 130, y + h_ * 0.64), 22, 22, P(color=col('#5fb2ff')))
        c.drawOval(skia.Rect(cx - 150, y + h_ * 0.84, cx + 150, y + h_ * 0.95), P(color=col('#ffd23f')))
    # sound rings from centre; empty room: rings bounce (many), furnished: fade quickly
    life = 2.0 if not furnished else 0.6
    c.save(); c.clipRect(skia.Rect(x + 4, y + 4, x + w_ - 4, y + h_ - 4))
    for i in range(6):
        tt = (t - st - i * 0.3)
        if tt < 0: continue
        tt = tt % 2.4
        if tt > life: continue
        r = 30 + 260 * tt
        # reflect: show ring and its mirror images off the walls for the empty room
        al = int(220 * (1 - tt / life))
        c.drawCircle(cx, cy, r, P(color=col(WAVE, al), stroke=8))
        if not furnished and r > w_ / 2:
            c.drawCircle(x - (cx - x), cy, r, P(color=col(WAVE, int(al * 0.7)), stroke=7))
            c.drawCircle(x + w_ + (x + w_ - cx), cy, r, P(color=col(WAVE, int(al * 0.7)), stroke=7))
    c.restore()

def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f3eee8', '#e6ddd2')
    k1 = ease_back(prog(t, 0.0, 0.5))
    if t < t1:
        c.save(); c.translate(540, 1100); c.scale(k1, k1); c.translate(-540, -1100)
        room(c, 140, 760, 800, 640, True, t, t0 + 0.3)
        c.restore()
        label_pill(c, 'SOFT = quiet', 540, 1550, size=48, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi='#ff5c85')
    else:
        mv = ease_in_out(prog(t, t1, 0.8))
        c.save(); c.translate(lerp(0, -255, mv), 0); c.translate(540, 1100); c.scale(lerp(1, 0.6, mv), lerp(1, 0.6, mv)); c.translate(-540, -1100)
        room(c, 140, 760, 800, 640, True, t, t0 + 0.3)
        c.restore()
        k2 = ease_back(prog(t, t1 + 0.5, 0.5))
        c.save(); c.translate(795, 1100); c.scale(0.6 * k2, 0.6 * k2); c.translate(-540, -1100)
        room(c, 140, 760, 800, 640, False, t, t1 + 0.6)
        c.restore()
        label_pill(c, 'furnished', 285, 840, size=38, k=k2, fill=NAVY)
        label_pill(c, 'EMPTY', 795, 840, size=40, k=k2, fill=NAVY, hi='#2f9bff')
        label_pill(c, 'EMPTY rooms ring', 540, 1450, size=46, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s4_sfx(D, cues):
    return [(0.0, 'pop'), (cues[0]['start'] + 1.2, 'pop'), (cues[1]['start'], 'whoosh'), (cues[1]['start'] + 0.5, 'pop'), (cues[1]['start'] + 1.6, 'pop')]

# ---------- 5: The 17-metre rule (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    canyon_bg(c, t, top='#cfe9ff', bot='#fff0dd')
    # ruler / distance bar between source and wall
    wx = lerp(420, 840, ease_in_out(prog(t, t1 + 0.2, 1.2)))
    c.drawRect(skia.Rect(wx, 820, wx + 70, 1420), lin(c, (wx, 0, wx + 70, 0), [col('#c6ccd8'), col('#9aa3b5')], vertical=False))
    c.drawLine(wx, 820, wx, 1420, P(color=col(NAVY), stroke=6))
    megaphone(c, 70, 1120, 0.75)
    per = 1.8
    st = t0 + 0.2 + ((t - t0 - 0.2) // per) * per if t > t0 + 0.2 else 1e9
    pulse(c, 200, wx, 1120, t, st, 700 if t < t1 else 1100, colr=WAVE, ret_at=True)
    # brain-merge indicator
    if t < t1:
        label_pill(c, 'under 0.1 s', 540, 740, size=46, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi='#ff5c85')
        k = ease_back(prog(t, t0 + 2.0, 0.4))
        label_pill(c, '= ONE blurry sound', 540, 1540, size=46, k=k, fill=NAVY, hi='#ff5c85')
    else:
        # distance arrow + 17 m badge
        ak = ease_out(prog(t, t1 + 1.4, 0.6))
        if ak > 0:
            arrow(c, 210, 1480, lerp(210, wx - 10, ak), 1480, colr=NAVY, w=10)
            arrow(c, wx - 10, 1480, lerp(wx - 10, 210, ak), 1480, colr=NAVY, w=10)
        bk = ease_back(prog(t, t1 + 2.0, 0.5), 2.4)
        if bk > 0:
            c.save(); c.translate(520, 760); c.scale(bk, bk)
            c.drawRoundRect(skia.Rect(-210, -80, 210, 80), 40, 40, P(color=col('#ffd23f')))
            c.drawRoundRect(skia.Rect(-210, -80, 210, 80), 40, 40, P(color=col(NAVY), stroke=7))
            text_block(c, '17 m+', 0, 0, size=96, fill=NAVY, stroke='#ffd23f')
            c.restore()
        label_pill(c, 'then: a real ECHO', 540, 1590, size=44, k=ease_back(prog(t, t1 + 3.0, 0.4)), fill=NAVY, hi='#2f9bff')

def s5_sfx(D, cues):
    return [(cues[0]['start'] + 0.6, 'pop'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 2.0, 'ding'), (cues[1]['start'] + 3.0, 'pop')]

# ---------- 6: Measure distance with an echo ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    canyon_bg(c, t, top='#bde3ff', bot='#ffe7c9')
    cliff(c, 860, 1000, 300, seed=11)
    megaphone(c, 70, 1250, 0.7)
    st = t0 + 0.3
    pulse(c, 190, 860, 1250, t, st, 670 * 2 / 2.0, colr=NAVY, ret_at=True)
    frac = clamp((t - st) / 2.0) if t > st else 0
    stopwatch(c, 330, 880, 120, frac * 0.5 if frac < 1 else 0.5 + 0.0 * t, label=f'{min(1.0, frac):.1f} s')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.3, 0.5), 2.2)
        c.save(); c.translate(540, 1520); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-330, -70, 330, 70), 35, 35, P(color=col('#ffffff', 240)))
        text_block(c, '1 s = about 170 m', 0, 0, size=58, fill=NAVY, stroke='#ffffff')
        c.restore()
        label_pill(c, 'there AND back', 640, 760, size=42, k=ease_back(prog(t, t1 + 1.8, 0.4)), fill=NAVY, hi='#ff5c85')

def s6_sfx(D, cues):
    return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 2.3, 'click'), (cues[1]['start'] + 0.3, 'pop'), (cues[1]['start'] + 1.8, 'pop')]

# ---------- 7: Wild part: bats, and some blind people, see with echoes ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1b2a4a', '#36306a')
    stars(c, t, seed=4, n=60, y1=1500)
    c.drawCircle(850, 1440, 60, P(color=col('#fff4c2', 230)))
    bx = lerp(170, 360, 0.5 + 0.5 * math.sin(t * 0.6)); by = 1080 + 40 * math.sin(t * 1.3)
    bat(c, bx, by, 0.85, t, colr='#8a78c8')
    # moth
    mx, my = 760 + 40 * math.sin(t * 2.1), 1180 + 30 * math.cos(t * 1.7)
    for sx in (-1, 1):
        c.drawOval(skia.Rect(mx + (0 if sx > 0 else -34), my - 22 + 6 * math.sin(t * 20), mx + (34 if sx > 0 else 0), my + 10), P(color=col('#f2e3c0')))
    c.drawOval(skia.Rect(mx - 6, my - 18, mx + 6, my + 18), P(color=col('#b89a6a')))
    per = 1.3
    st = t0 + 0.4 + ((t - t0 - 0.4) // per) * per if t > t0 + 0.4 else 1e9
    rings_dir(c, bx + 50, by, t, st, a0=-25, sweep=50, colr='#9fd2ff', speed=420, life=1.0)
    if t > st + 0.85 and t < st + 1.3:
        rings_dir(c, mx, my, t, st + 0.85, a0=155, sweep=50, colr='#ffd23f', speed=380, life=0.45, n=1)
    label_pill(c, 'ECHO vision', 540, 1600, size=46, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.4, 0.5))
        label_pill(c, 'tongue CLICKS', 540, 760, size=46, k=k, fill=NAVY, hi='#ffd23f', bg='#ffffff')
        for j in range(3):
            stt = t1 + 1.0 + j * 0.7
            if t > stt:
                sound_rings(c, 540, 900, t, stt, n=1, colr='#ffffff', speed=380, life=0.8, w=8, both=True)

def s7_sfx(D, cues):
    s = [(cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.4, 'pop')]
    s += [(cues[1]['start'] + 1.0 + j * 0.7, 'click') for j in range(3)]
    return s

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    canyon_bg(c, t)
    cliff(c, 820, 1000, 400, seed=5)
    megaphone(c, 120, 1180, 0.8, rot=-6)
    st = 0.3 + (t // 2.4) * 2.4
    pulse(c, 280, 800, 1180, t, st, 600, colr=NAVY, ret_at=True)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: CHAMELEONS', 480, 760, size=48, k=k, fill=NAVY, hi='#3fbf6a')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues):
    return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do echoes work?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do echoes work?', 'How do ECHOES work?'),
            ('Shout at a cliff, and your own voice comes back to you, a moment late.', 'Your voice comes BACK')], tail=0.8),
        dict(name='wave', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Sound is a wave of squeezed air, spreading like a ripple on a pond.', 'Sound = a WAVE of air'),
            ('It races along at about three hundred and forty-three meters every second.', '343 meters per SECOND')], tail=0.8),
        dict(name='bounce', draw=s3, sfx_fn=s3_sfx, lines=[
            ('When that wave hits something hard, like rock or concrete,', 'It hits something HARD'),
            ('it bounces back, the same way a ball bounces off a wall.', 'and BOUNCES back')], tail=0.8),
        dict(name='soft', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Soft things, like curtains, carpets or fresh snow, swallow sound instead.', 'SOFT things swallow it'),
            ("That's why an empty room sounds so echoey, and a furnished one doesn't.", 'EMPTY rooms echo')], tail=1.0),
        dict(name='rule', draw=s5, sfx_fn=s5_sfx, lines=[
            ('If the bounce returns in under a tenth of a second, your brain blends it in.', 'Too fast = ONE sound'),
            ('So for a real echo, the wall must be at least seventeen meters away.', '17 METERS or more')], tail=1.0),
        dict(name='measure', draw=s6, sfx_fn=s6_sfx, lines=[
            ('You can even use an echo as a ruler.', 'An echo is a RULER'),
            ('Each second of delay means the cliff is about a hundred and seventy meters away.', '1 second = 170 METERS')], tail=1.0),
        dict(name='bats', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: bats hunt in total darkness using their own echoes.", 'Bats SEE with echoes'),
            ('And some blind people learn to do it too, with quick tongue clicks.', 'So can some PEOPLE')], tail=1.0),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So an echo is just sound, bouncing back from far away.', 'Sound that BOUNCES back'),
            ('Next up: how chameleons change color.', 'Next: CHAMELEONS'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
