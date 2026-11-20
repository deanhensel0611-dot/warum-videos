"""Warum?-Videos: kleine Engine für 9:16-Erklärvideos für Kinder.
Zeichnen mit Skia, Stimme mit Piper (Thorsten, Deutsch), Musik synthetisch.
"""
import math, os, random, subprocess, wave, json
import numpy as np
import skia

W, H, FPS = 1080, 1920, 60
# Output is supersampled: layout stays in 1080x1920 units, pixels are rendered at SS x that (1440x2560 by default).
SS = float(os.environ.get('WARUM_SS', str(4 / 3)))
OW, OH = int(round(W * SS)) // 2 * 2, int(round(H * SS)) // 2 * 2
SR = 44100
FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
VOICE = os.environ.get('WARUM_VOICE', 'af_heart')
KOKORO_DIR = os.environ.get('KOKORO_DIR', '/tmp/kokoro')
_kok = None
_fm = skia.FontMgr()
TF = _fm.makeFromFile(FONT_PATH, 0)

# ---------------- Farben & Easing ----------------
def col(h, a=255):
    h = h.lstrip('#')
    return skia.ColorSetARGB(int(a), int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, start, dur): return clamp((t - start) / dur) if dur > 0 else float(t >= start)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in_out(x): return 3 * x * x - 2 * x * x * x
def ease_back(x, s=1.7):
    x -= 1
    return x * x * ((s + 1) * x + s) + 1

def mix_hex(h1, h2, t, a=255):
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    c = [int(lerp(int(h1[i:i+2], 16), int(h2[i:i+2], 16), t)) for i in (0, 2, 4)]
    return skia.ColorSetARGB(int(a), *c)

def P(**kw):
    p = skia.Paint(AntiAlias=True)
    if 'color' in kw: p.setColor(kw['color'])
    if kw.get('stroke'):
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(kw['stroke'])
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if kw.get('blur'):
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, kw['blur']))
    return p

# ---------------- Hintergründe ----------------
def lin(c, rect, cols, vertical=True, pos=None):
    x0, y0, x1, y1 = rect
    pts = [(0, y0), (0, y1)] if vertical else [(x0, 0), (x1, 0)]
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeLinear(points=pts, colors=cols, positions=pos))
    return p

def rad(cx, cy, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeRadial(center=(cx, cy), radius=r, colors=cols, positions=pos))
    return p

def sky(c, top, bottom, mid=None):
    cols = [col(top), col(mid), col(bottom)] if mid else [col(top), col(bottom)]
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, W, H), cols))

def sunbeams(c, x, y, t, a=40, n=10, length=1600):
    c.save(); c.translate(x, y); c.rotate(t * 4)
    for i in range(n):
        c.save(); c.rotate(i * 360 / n)
        p = skia.Path(); p.moveTo(0, 0); p.lineTo(-90, -length); p.lineTo(90, -length); p.close()
        c.drawPath(p, rad(0, 0, length, [col('#ffffff', a), col('#ffffff', 0)]))
        c.restore()
    c.restore()

def cloud(c, x, y, s=1.0, a=240):
    parts = [(-70, 10, 55), (0, -20, 75), (75, 5, 60), (-20, 30, 55), (40, 30, 55), (110, 30, 40), (-110, 32, 38)]
    for dx, dy, r in parts:
        c.drawCircle(x + dx * s, y + (dy + 10) * s, r * s, P(color=col('#a9cbe6', int(a * 0.55))))
    for dx, dy, r in parts:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P(color=col('#ffffff', a)))
    for dx, dy, r in parts[:3]:
        c.drawCircle(x + (dx - 12) * s, y + (dy - 14) * s, r * 0.45 * s, P(color=col('#ffffff', a), blur=6))

def clouds(c, t, seed=1, n=4, y0=180, y1=1300, speed=22, a=235):
    rnd = random.Random(seed)
    for i in range(n):
        y = rnd.uniform(y0, y1); s = rnd.uniform(0.55, 1.15)
        x = (rnd.uniform(0, W + 500) + t * speed * s) % (W + 500) - 250
        cloud(c, x, y, s, int(a * (0.75 + 0.25 * s)))

def birds(c, t, seed=2, n=3, y=520):
    rnd = random.Random(seed)
    for i in range(n):
        bx = (rnd.uniform(-300, W) + t * rnd.uniform(60, 90)) % (W + 300) - 150
        by = y + rnd.uniform(-80, 120) + math.sin(t * 1.5 + i) * 15
        f = math.sin(t * 10 + i * 2) * 14; s = rnd.uniform(0.8, 1.2)
        p = skia.Path(); p.moveTo(bx - 26 * s, by - f * s); p.quadTo(bx - 12 * s, by - 10 * s, bx, by)
        p.quadTo(bx + 12 * s, by - 10 * s, bx + 26 * s, by - f * s)
        c.drawPath(p, P(color=col('#30406a', 200), stroke=5))

def tree(c, x, y, s, t, seed=0, dark=False):
    sway = math.sin(t * 1.6 + seed) * 2.5
    c.save(); c.translate(x, y); c.rotate(sway); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-12, -110, 12, 0), 8, 8, P(color=col('#6b4423' if not dark else '#4a2f1a')))
    g1, g2 = ('#5cc94a', '#2f8f3a') if not dark else ('#3f7a35', '#24502a')
    for dx, dy, r in [(0, -170, 70), (-45, -135, 52), (45, -130, 55), (0, -120, 50)]:
        c.drawCircle(dx, dy, r, rad(dx - r * 0.3, dy - r * 0.4, r * 1.4, [col(g1), col(g2)]))
    for dx, dy in [(-20, -180), (25, -150), (-35, -125)]:
        c.drawCircle(dx, dy, 7, P(color=col('#ff6b6b' if not dark else '#b04a4a')))
    c.restore()

def hills(c, y=1600, c1='#7ed957', c2='#56b83a', t=0.0, trees=True, dark=False, flowers=True):
    back = '#a5e08f' if not dark else '#5e7d4f'
    p = skia.Path(); p.moveTo(0, y - 40); p.cubicTo(200, y - 150, 420, y - 90, 560, y - 120)
    p.cubicTo(760, y - 170, 900, y - 90, W, y - 110); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y - 170, W, y + 200), [col(back), col(c1)]))
    if trees:
        for i, (tx, ty, ts) in enumerate([(120, y - 60, 0.8), (930, y - 70, 0.95), (720, y - 90, 0.6)]):
            tree(c, tx, ty, ts, t, i, dark)
    p = skia.Path(); p.moveTo(0, y + 40)
    p.cubicTo(250, y - 60, 450, y + 40, 650, y - 10); p.cubicTo(820, y - 50, 950, y - 30, W, y)
    p.lineTo(W, H); p.lineTo(0, H); p.close(); c.drawPath(p, lin(c, (0, y - 60, W, H), [col(c2), col(c1)]))
    p = skia.Path(); p.moveTo(0, y + 120)
    p.cubicTo(300, y + 40, 600, y + 160, W, y + 70); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y + 40, W, H), [col(c1), col(c2)]))
    rnd = random.Random(5)
    for i in range(40):
        gx = rnd.uniform(0, W); gy = rnd.uniform(y + 150, H - 20); sw = math.sin(t * 2 + i) * 4
        gc = col('#3f9a2f' if not dark else '#2c5a24')
        for k in (-1, 0, 1):
            c.drawLine(gx + k * 8, gy, gx + k * 14 + sw, gy - 26 - abs(k) * -6, P(color=gc, stroke=4))
    if flowers:
        for i in range(14):
            fx = rnd.uniform(30, W - 30); fy = rnd.uniform(y + 170, H - 40)
            fc = rnd.choice(['#ff8fab', '#ffd23f', '#ffffff', '#b28dff'])
            if dark: fc = '#c98a8a'
            for k in range(5):
                a = k * 2 * math.pi / 5 + t * 0.3
                c.drawCircle(fx + math.cos(a) * 10, fy + math.sin(a) * 10, 8, P(color=col(fc)))
            c.drawCircle(fx, fy, 6, P(color=col('#ffb627')))

def dust(c, t, seed=9, n=18, a=120, colr='#ffffff'):
    rnd = random.Random(seed)
    for i in range(n):
        x = (rnd.uniform(0, W) + math.sin(t * 0.5 + i) * 40) % W
        y = (rnd.uniform(0, H) - t * rnd.uniform(15, 35)) % H
        tw = 0.5 + 0.5 * math.sin(t * 3 + i * 1.7)
        c.drawCircle(x, y, 3 + 3 * tw, P(color=col(colr, int(a * tw)), blur=2))

def vignette(c, a=70):
    c.drawRect(skia.Rect(0, 0, W, H), rad(W / 2, H / 2, H * 0.75, [col('#000000', 0), col('#000000', 0), col('#0b1a3a', a)], [0, 0.6, 1]))

# ---------------- Figuren ----------------
FACES = True  # set per episode via EPISODE['faces']; False = general-audience style without faces

def face(c, x, y, r, t=0.0, blink_seed=0, mood='happy', look=(0, 0)):
    if not FACES: return
    ex = r * 0.36; ey = -r * 0.12; er = r * 0.14
    ph = (t * 0.7 + blink_seed * 0.37) % 3.2
    blink = ph < 0.12
    lx, ly = look
    for sx in (-1, 1):
        cx = x + sx * ex; cy = y + ey
        if blink:
            c.drawArc(skia.Rect(cx - er, cy - er * 0.6, cx + er, cy + er * 0.6), 10, 160, False, P(color=col('#2b1d0e'), stroke=r * 0.06))
        else:
            c.drawOval(skia.Rect(cx - er * 0.85, cy - er * 1.1, cx + er * 0.85, cy + er * 1.1), P(color=col('#2b1d0e')))
            c.drawCircle(cx - er * 0.25 + lx * er * 0.3, cy - er * 0.45 + ly * er * 0.3, er * 0.38, P(color=col('#ffffff')))
            c.drawCircle(cx + er * 0.3 + lx * er * 0.3, cy + er * 0.35 + ly * er * 0.3, er * 0.16, P(color=col('#ffffff')))
    for sx in (-1, 1):
        c.drawOval(skia.Rect(x + sx * r * 0.56 - r * 0.15, y + r * 0.1 - r * 0.09, x + sx * r * 0.56 + r * 0.15, y + r * 0.1 + r * 0.09), P(color=col('#ff6f8a', 150), blur=r * 0.03))
    if mood == 'wow':
        c.drawOval(skia.Rect(x - r * 0.11, y + r * 0.13, x + r * 0.11, y + r * 0.4), P(color=col('#5a1f1f')))
        c.drawOval(skia.Rect(x - r * 0.06, y + r * 0.28, x + r * 0.06, y + r * 0.38), P(color=col('#ff8a8a')))
    else:
        mp = skia.Path(); mp.moveTo(x - r * 0.22, y + r * 0.12)
        mp.quadTo(x, y + r * 0.42, x + r * 0.22, y + r * 0.12); mp.close()
        c.drawPath(mp, P(color=col('#5a1f1f')))
        c.drawOval(skia.Rect(x - r * 0.1, y + r * 0.22, x + r * 0.1, y + r * 0.3), P(color=col('#ff8a8a')))

def sun(c, x, y, r, t, mood='happy', glow=True):
    if glow:
        c.drawCircle(x, y, r * 1.9, rad(x, y, r * 1.9, [col('#fff6b0', 150), col('#fff6b0', 0)]))
    breathe = 1 + 0.025 * math.sin(t * 2.4)
    c.save(); c.translate(x, y); c.scale(breathe, 1 / breathe); c.rotate(t * 18)
    for i in range(14):
        c.save(); c.rotate(i * 360 / 14)
        L = r * (1.42 + 0.08 * math.sin(t * 4 + i * 1.3))
        p = skia.Path(); p.moveTo(-r * 0.14, -r * 0.98); p.quadTo(-r * 0.05, -L * 0.9, 0, -L); p.quadTo(r * 0.05, -L * 0.9, r * 0.14, -r * 0.98); p.close()
        c.drawPath(p, lin(c, (0, -L, 0, -r), [col('#ffcf3f'), col('#ff9f1c')]))
        c.restore()
    c.restore()
    c.save(); c.translate(x, y); c.scale(breathe, 1 / breathe)
    c.drawCircle(0, 0, r, rad(-r * 0.3, -r * 0.35, r * 1.5, [col('#fff1a1'), col('#ffd23f'), col('#ffa62b')], [0, 0.45, 1]))
    c.drawCircle(0, 0, r, P(color=col('#f08c00', 160), stroke=r * 0.04))
    c.drawOval(skia.Rect(-r * 0.55, -r * 0.75, -r * 0.05, -r * 0.45), P(color=col('#ffffff', 120), blur=r * 0.06))
    face(c, 0, r * 0.05, r, t, 0.5, mood)
    c.restore()

def photon(c, x, y, r, hexcol, t=0.0, seed=0, face_on=True, alpha=255, vel=(0, 0)):
    a = int(alpha)
    c.drawCircle(x, y, r * 2.1, rad(x, y, r * 2.1, [col(hexcol, int(a * 0.5)), col(hexcol, 0)]))
    sp = math.hypot(*vel); st = min(0.35, sp / 3000)
    c.save(); c.translate(x, y)
    if st > 0.01:
        c.rotate(math.degrees(math.atan2(vel[1], vel[0]))); c.scale(1 + st, 1 - st * 0.6); c.rotate(-math.degrees(math.atan2(vel[1], vel[0])))
    c.drawCircle(0, 0, r, rad(-r * 0.35, -r * 0.4, r * 1.6, [col('#ffffff', a), col(hexcol, a), col(hexcol, a)], [0, 0.35, 1]))
    c.drawCircle(0, 0, r, P(color=col('#000000', int(a * 0.12)), stroke=r * 0.07))
    if face_on and a > 200:
        face(c, 0, r * 0.08, r * 0.95, t, seed)
    c.restore()

def molecule(c, x, y, r, t, seed=0, alpha=255):
    wob = math.sin(t * 3 + seed) * 6; a = int(alpha)
    c.drawOval(skia.Rect(x - r * 1.4, y + r * 0.7, x + r * 1.4, y + r * 1.0), P(color=col('#5f8fb5', int(a * 0.15)), blur=6))
    for dx in (-r * 0.55, r * 0.55):
        cy = y + wob * (1 if dx > 0 else -1) * 0.3
        c.drawCircle(x + dx, cy, r * 0.78, rad(x + dx - r * 0.25, cy - r * 0.3, r * 1.2, [col('#ffffff', a), col('#d4efff', a), col('#9fd6f5', a)], [0, 0.5, 1]))
        c.drawCircle(x + dx, cy, r * 0.78, P(color=col('#6fb8e6', a), stroke=3.5))
    if a > 200:
        face(c, x, y + 4, r * 0.8, t, seed + 2)

def kid(c, x, y, s=1.0, t=0.0, look_up=True, wave=False, helmet=False):
    """x,y = Füße."""
    bob = math.sin(t * 2.2) * 4 * s
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect(-90, -12, 90, 14), P(color=col('#000000', 50), blur=6))
    for sx in (-1, 1):
        c.drawRoundRect(skia.Rect(sx * 38 - 20, -75, sx * 38 + 20, -10), 16, 16, P(color=col('#35548f')))
        c.drawRoundRect(skia.Rect(sx * 38 - 30, -24, sx * 38 + 30, 6), 15, 15, P(color=col('#ffffff')))
        c.drawRoundRect(skia.Rect(sx * 38 - 30, -24, sx * 38 + 30, 6), 15, 15, P(color=col('#c9d3e0'), stroke=4))
    c.translate(0, bob)
    for sx in (-1, 1):
        ang = (-130 + math.sin(t * 8) * 25) if (wave and sx == 1) else (sx * 15 + math.sin(t * 2.2 + sx) * 4)
        c.save(); c.translate(sx * 62, -195); c.rotate(ang if sx == 1 else -abs(ang) if wave else ang)
        c.drawRoundRect(skia.Rect(-16, 0, 16, 105), 16, 16, P(color=col('#ff6b6b')))
        c.drawCircle(0, 108, 20, P(color=col('#f6c9a0')))
        c.restore()
    body = skia.Rect(-72, -235, 72, -55)
    c.drawRoundRect(body, 62, 62, lin(c, (0, -235, 0, -55), [col('#ff7b7b'), col('#e84d5b')]))
    c.drawRoundRect(skia.Rect(-40, -180, 40, -130), 10, 10, P(color=col('#ffd23f')))
    c.drawCircle(0, -155, 12, P(color=col('#ff9f1c')))
    hy = -305
    c.drawCircle(0, hy, 88, rad(-25, hy - 30, 130, [col('#ffe0c2'), col('#f2bf93')]))
    for sx in (-1, 1): c.drawCircle(sx * 86, hy + 10, 18, P(color=col('#f2bf93')))
    hair = skia.Path(); hair.moveTo(-92, hy + 5)
    hair.cubicTo(-100, hy - 110, 100, hy - 120, 92, hy + 5); hair.quadTo(60, hy - 50, 10, hy - 40); hair.quadTo(-40, hy - 60, -92, hy + 5); hair.close()
    c.drawPath(hair, lin(c, (0, hy - 120, 0, hy), [col('#7a4a26'), col('#4f2f17')]))
    tuft = skia.Path(); tuft.moveTo(-5, hy - 95); tuft.quadTo(15 + math.sin(t * 3) * 6, hy - 150, 35, hy - 120); tuft.quadTo(15, hy - 115, 10, hy - 92); tuft.close()
    c.drawPath(tuft, P(color=col('#5f381b')))
    face(c, 0, hy + 22, 76, t, 3, 'happy', (0, -1) if look_up else (0, 0))
    if helmet:
        c.drawCircle(0, hy, 128, rad(-40, hy - 50, 180, [col('#ffffff', 90), col('#bfe3ff', 40), col('#bfe3ff', 20)]))
        c.drawCircle(0, hy, 128, P(color=col('#ffffff', 230), stroke=9))
        c.drawArc(skia.Rect(-100, hy - 100, 100, hy + 100), 200, 50, False, P(color=col('#ffffff', 200), stroke=12))
    c.restore()

# ---------------- Text ----------------
_font_cache = {}
def font(size):
    if size not in _font_cache: _font_cache[size] = skia.Font(TF, size)
    return _font_cache[size]

def wrap(text, size, maxw):
    f = font(size); words = text.split(' '); lines = []; cur = ''
    for w_ in words:
        tryl = (cur + ' ' + w_).strip()
        if f.measureText(tryl) <= maxw or not cur: cur = tryl
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def text_block(c, text, cx, cy, size=94, maxw=880, fill='#ffffff', hi='#ffe14d', stroke='#1b2a4a', scale=1.0, alpha=255, reveal=None):
    """Wörter in GROSSBUCHSTABEN (>=3 Buchstaben) werden hervorgehoben.
    reveal=None: alle Wörter voll. reveal=k (float): Wörter < k voll, Wort k aktiv (leicht größer), danach gedimmt."""
    lines = wrap(text, size, maxw); f = font(size); lh = size * 1.18
    c.save(); c.translate(cx, cy); c.scale(scale, scale)
    y0 = -lh * (len(lines) - 1) / 2 + size * 0.35
    wi = 0
    for i, ln in enumerate(lines):
        words = ln.split(' '); widths = [f.measureText(w_) for w_ in words]; sp = f.measureText(' ')
        total = sum(widths) + sp * (len(words) - 1); x = -total / 2; y = y0 + i * lh
        for w_, ww in zip(words, widths):
            letters = ''.join(ch for ch in w_ if ch.isalpha())
            is_hi = len(letters) >= 3 and letters.isupper()
            a = alpha; pop = 1.0
            if reveal is not None:
                if wi > reveal: a = int(alpha * 0.45)
                elif wi == int(reveal): pop = 1.0 + 0.10 * math.sin(math.pi * min(1.0, (reveal - int(reveal)) * 2.5))
            c.save(); c.translate(x + ww / 2, y - size * 0.35); c.scale(pop, pop); c.translate(-(x + ww / 2), -(y - size * 0.35))
            c.drawString(w_, x, y, f, P(color=col(stroke, a), stroke=size * 0.2))
            c.drawString(w_, x, y, f, P(color=col(hi if is_hi else fill, a)))
            c.restore()
            x += ww + sp; wi += 1
    c.restore()

def caption(c, text, t_since, y=430, dur=None):
    """Untertitel mit Pop-in und Wort-für-Wort-Hervorhebung. t_since = Sekunden seit Sprechbeginn, dur = Dauer der Zeile."""
    if text is None or t_since < 0: return
    s = 0.55 + 0.45 * ease_back(prog(t_since, 0, 0.42), 2.2)
    yy = y + math.sin(t_since * 2.0) * 6
    al = int(255 * prog(t_since, 0, 0.15))
    n = len(text.split())
    reveal = None if not dur else min(n + 1.0, t_since / max(dur, 0.3) * n * 1.08)
    c.save(); c.translate(0, 10)
    text_block(c, text, W / 2, yy, scale=s, alpha=int(al * 0.35), fill='#0b1a3a', hi='#0b1a3a', stroke='#0b1a3a')
    c.restore()
    text_block(c, text, W / 2, yy, scale=s, alpha=al, reveal=reveal)

# ---------------- Audio ----------------
def tts(text, out, speed=0.86):
    global _kok
    if os.path.exists(out): return read_wav(out)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    if _kok is None:
        _kok = Kokoro(os.path.join(KOKORO_DIR, 'kokoro-v1.0.onnx'), os.path.join(KOKORO_DIR, 'voices-v1.0.bin'))
    a, sr = _kok.create(text, voice=VOICE, speed=speed, lang='en-gb' if VOICE.startswith('b') else 'en-us')
    tmp = out + '.raw.wav'; sf.write(tmp, a, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-ar', str(SR), '-ac', '1',
                    '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5,volume=1.3', out], check=True)
    os.remove(tmp)
    return read_wav(out)

def read_wav(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

def pluck(freq, dur, decay=0.996):
    n = int(SR * dur); N = max(2, int(SR / freq))
    buf = np.random.uniform(-1, 1, N); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = decay * 0.5 * (buf[i % N] + buf[(i + 1) % N])
    return out

def music(total, bpm=104, seed=3):
    np.random.seed(seed)
    beat = 60 / bpm; out = np.zeros(int(SR * (total + 2)))
    nf = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog_ = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
    cache = {}
    def note(m, d):
        k = (m, d)
        if k not in cache: cache[k] = pluck(nf(m), d)
        return cache[k]
    t = 0.0; bar = 0
    pattern = [0, 1, 2, 1, 0, 2, 1, 2]
    while t < total + 1:
        ch = prog_[bar % 4]
        for i, idx in enumerate(pattern):
            m = ch[idx] + (12 if i in (2, 6) else 0)
            s = int(SR * (t + i * beat / 2)); n = note(m, beat * 1.5)
            if s >= len(out): continue
            e = min(len(out), s + len(n)); out[s:e] += n[:e - s] * (0.9 if i % 2 == 0 else 0.6)
        b = note(ch[0] - 12, beat * 3); s = int(SR * t); e = min(len(out), s + len(b))
        if s < len(out): out[s:e] += b[:e - s] * 0.8
        t += beat * 4; bar += 1
    out = out[:int(SR * total)]
    fade = int(SR * 1.5); out[-fade:] *= np.linspace(1, 0, fade)
    return out / (np.abs(out).max() + 1e-9)

def sfx(kind):
    if kind == 'pop':
        d = 0.12; t = np.arange(int(SR * d)) / SR
        f = 900 * np.exp(-t * 18) + 300
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    if kind == 'boing':
        d = 0.35; t = np.arange(int(SR * d)) / SR
        f = 220 + 180 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    if kind == 'whoosh':
        d = 0.6; t = np.arange(int(SR * d)) / SR
        n = np.random.randn(len(t)); k = np.ones(40) / 40
        return np.convolve(n, k, 'same') * np.sin(np.pi * t / d) * 2.5
    if kind == 'sparkle':
        d = 0.8; t = np.arange(int(SR * d)) / SR; out = np.zeros(len(t))
        for i, m in enumerate([84, 88, 91, 96]):
            s = int(SR * i * 0.08); fr = 440 * 2 ** ((m - 69) / 12)
            seg = t[: len(t) - s]
            out[s:] += np.sin(2 * np.pi * fr * seg) * np.exp(-seg * 7)
        return out * 0.5
    if kind == 'ding':      # channel signature: soft two-tone "aha"
        d = 0.9; t = np.arange(int(SR * d)) / SR; out = np.zeros(len(t))
        for m, off, g in [(88, 0.0, 1.0), (95, 0.07, 0.7)]:
            s0 = int(SR * off); seg = t[: len(t) - s0]; fr = 440 * 2 ** ((m - 69) / 12)
            out[s0:] += (np.sin(2 * np.pi * fr * seg) + 0.25 * np.sin(4 * np.pi * fr * seg)) * np.exp(-seg * 5.5) * g
        return out * 0.45
    if kind == 'click':
        d = 0.05; t = np.arange(int(SR * d)) / SR
        return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * 0.6
    if kind == 'chime':     # channel signature: outro
        d = 1.4; t = np.arange(int(SR * d)) / SR; out = np.zeros(len(t))
        for i, m in enumerate([76, 81, 85, 88]):
            s0 = int(SR * i * 0.11); seg = t[: len(t) - s0]; fr = 440 * 2 ** ((m - 69) / 12)
            out[s0:] += np.sin(2 * np.pi * fr * seg) * np.exp(-seg * 3.5)
        return out * 0.3
    raise ValueError(kind)

def ambience(kind, dur, seed=1):
    """Soft background bed (not music): 'wind', 'water', 'space', 'forest'. Returns array at unit level."""
    rng = np.random.default_rng(seed); n = int(SR * dur); t = np.arange(n) / SR
    def lp(x, k):
        return np.convolve(x, np.ones(k) / k, 'same')
    if kind == 'wind':
        x = lp(rng.standard_normal(n), 60) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.07 * t + 1))
    elif kind == 'water':
        x = lp(rng.standard_normal(n), 25) * 0.7
        for _ in range(int(dur * 3)):
            s0 = rng.integers(0, max(1, n - SR // 5)); f0 = rng.uniform(500, 1100); seg = np.arange(SR // 6) / SR
            x[s0:s0 + len(seg)] += np.sin(2 * np.pi * (f0 + 2500 * seg) * seg) * np.exp(-seg * 30) * 0.5
    elif kind == 'space':
        x = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 0.5) + 0.3 * np.sin(2 * np.pi * 110.3 * t)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
        x += lp(rng.standard_normal(n), 200) * 2
    elif kind == 'forest':
        x = lp(rng.standard_normal(n), 80) * 0.5
        for _ in range(int(dur / 3)):
            s0 = rng.integers(0, max(1, n - SR)); seg = np.arange(int(SR * 0.25)) / SR; f0 = rng.uniform(2500, 4000)
            x[s0:s0 + len(seg)] += np.sin(2 * np.pi * (f0 + 600 * np.sin(2 * np.pi * 14 * seg)) * seg) * np.exp(-seg * 10) * 0.3
    else:
        raise ValueError(kind)
    x /= (np.abs(x).max() + 1e-9)
    fade = min(n // 2, SR); x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
    return x

# ---------------- Episode-Pipeline ----------------
def build(episode, outdir, workers=2):
    """episode: dict(title, scenes=[dict(name, lines=[(sprechtext, untertitel)], draw=fn(c,t,D,cues), tail, lead, sfx=[(t,kind)])])"""
    os.makedirs(outdir, exist_ok=True); vdir = os.path.join(outdir, 'voice'); os.makedirs(vdir, exist_ok=True)
    timeline = []; t_global = 0.0
    voice_track = []
    for si, sc in enumerate(episode['scenes']):
        lead = sc.get('lead', 0.35); gap = sc.get('gap', 0.3); tail = sc.get('tail', 0.6)
        cues = []; t = lead
        for li, (spoken, cap) in enumerate(sc['lines']):
            wav = tts(spoken, os.path.join(vdir, f'{si:02d}_{li:02d}.wav'))
            d = len(wav) / SR
            cues.append(dict(start=t, end=t + d, caption=cap))
            voice_track.append((t_global + t, wav)); t += d + gap
        D = max(t - gap + tail, sc.get('min_dur', 0))
        timeline.append(dict(si=si, start=t_global, D=D, cues=cues))
        t_global += D
    total = t_global
    # Audio
    v = np.zeros(int(SR * (total + 1)))
    for st, wav in voice_track:
        s = int(SR * st); v[s:s + len(wav)] += wav
    fx = np.zeros_like(v)
    for tl, sc in zip(timeline, episode['scenes']):
        evs = [(cu['start'], 'pop') for cu in tl['cues']] + list(sc.get('sfx_fn', lambda D, cues: [])(tl['D'], tl['cues']))
        for t, kind in evs:
            x = sfx(kind); s = int(SR * (tl['start'] + t)); e = min(len(fx), s + len(x)); fx[s:e] += x[:e - s]
    mus = np.zeros_like(v)
    if episode.get('music', True):
        m = music(total); mus[:len(m)] = m
    # Ducking: Musik leiser, wenn gesprochen wird
    env = np.convolve(np.abs(v), np.ones(4410) / 4410, 'same'); duck = 1 - 0.55 * np.clip(env * 12, 0, 1)
    amb = np.zeros_like(v)
    for tl, sc in zip(timeline, episode['scenes']):
        kind = sc.get('ambience', episode.get('ambience'))
        if kind:
            a = ambience(kind, tl['D'] + 0.8, seed=tl['si'] + 1); s0 = int(SR * tl['start']); e = min(len(amb), s0 + len(a)); amb[s0:e] += a[:e - s0]
    mixed = amb * 0.04 + v * 1.0 + mus * float(os.environ.get('WARUM_MUSIC_VOL', '0.16')) * duck + fx * 0.22
    mixed = mixed[:int(SR * total)]; mixed /= max(1.0, np.abs(mixed).max() / 0.95)
    audio = os.path.join(outdir, 'audio.wav'); write_wav(audio, mixed)
    json.dump([dict(si=t['si'], start=t['start'], D=t['D'], cues=t['cues']) for t in timeline],
              open(os.path.join(outdir, 'timeline.json'), 'w'), indent=1, ensure_ascii=False)
    return timeline, total, audio

XFADE = 0.4

def draw_full(sc, c, t, D, cues):
    c.save()
    z = 1.0 + 0.035 * ease_in_out(clamp(t / max(D, 0.1)))
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    sc['draw'](c, t, D, cues)
    c.restore()
    if sc.get('captions', True):
        cur = None
        for cu in cues:
            if t >= cu['start'] - 0.05: cur = cu
        if cur: caption(c, cur['caption'], t - cur['start'] + 0.05, sc.get('cap_y', 430), cur['end'] - cur['start'])
    vignette(c)

def render_scene(args):
    episode_mod, si, D, cues, outdir, prev = args
    import importlib; ep = importlib.import_module(episode_mod).EPISODE
    sc = ep['scenes'][si]
    tmp = os.path.join(outdir, f'scene_{si:02d}.tmp.mp4'); final = os.path.join(outdir, f'scene_{si:02d}.mp4')
    n = int(round(D * FPS))
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{OW}x{OH}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-tune', 'animation', '-profile:v', 'high',
                             '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    surf = skia.Surface(OW, OH)
    for i in range(n):
        t = i / FPS
        render_into(surf.getCanvas(), ep, si, t, D, cues, prev)
        proc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    proc.stdin.close(); rc = proc.wait()
    if rc == 0: os.replace(tmp, final)
    return final

TRANSITIONS = ['fade', 'slide', 'wipe', 'punch']  # cycled per scene -> no type more than twice in 8 scenes

def render_into(c, ep, si, t, D, cues, prev):
    global FACES
    FACES = ep.get('faces', True)
    c.clear(skia.ColorWHITE)
    c.resetMatrix(); c.scale(OW / W, OH / H)
    sc = ep['scenes'][si]
    if prev is not None and t < XFADE:
        pD, pcues = prev
        kind = sc.get('trans', TRANSITIONS[(si - 1) % len(TRANSITIONS)])
        a = ease_in_out(t / XFADE)
        if kind == 'slide':      # new scene pushes the old one up
            c.save(); c.translate(0, -H * a); draw_full(ep['scenes'][si - 1], c, pD + t, pD + XFADE, pcues); c.restore()
            c.save(); c.translate(0, H * (1 - a)); draw_full(sc, c, t, D, cues); c.restore()
        elif kind == 'wipe':     # circle reveal from the centre
            draw_full(ep['scenes'][si - 1], c, pD + t, pD + XFADE, pcues)
            c.save(); pth = skia.Path(); pth.addCircle(W / 2, H / 2, math.hypot(W, H) / 2 * a); c.clipPath(pth, doAntiAlias=True)
            draw_full(sc, c, t, D, cues); c.restore()
        elif kind == 'punch':    # quick zoom-through
            c.save(); z = 1 + 0.25 * a; c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
            draw_full(ep['scenes'][si - 1], c, pD + t, pD + XFADE, pcues); c.restore()
            c.saveLayerAlpha(None, int(255 * a)); c.save(); z = 0.85 + 0.15 * a
            c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2); draw_full(sc, c, t, D, cues); c.restore(); c.restore()
        else:
            draw_full(ep['scenes'][si - 1], c, pD + t, pD + XFADE, pcues)
            c.saveLayerAlpha(None, int(255 * a)); draw_full(sc, c, t, D, cues); c.restore()
    else:
        draw_full(sc, c, t, D, cues)

def frame(episode, si, t, D, cues, path, prev=None):
    surf = skia.Surface(OW, OH); render_into(surf.getCanvas(), episode, si, t, D, cues, prev)
    surf.makeImageSnapshot().save(path, skia.kJPEG)

def assemble(outdir, n_scenes, audio, out):
    lst = os.path.join(outdir, 'list.txt')
    with open(lst, 'w') as f:
        for i in range(n_scenes): f.write(f"file 'scene_{i:02d}.mp4'\n")
    tmp = out + '.tmp.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', audio,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, out)

# ---------------- Space, Moon, Earth, Weather (added for ep_002+) ----------------
def stars(c, t, seed=21, n=110, y0=0, y1=1550, a=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(y0, y1); tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(1.5, 4) + i)
        c.drawCircle(x, y, rnd.uniform(1.5, 4.5), P(color=col('#ffffff', int((90 + 160 * tw) * a))))

def space(c, t, seed=21, n=130):
    sky(c, '#03040b', '#1c2145', mid='#0b0e24'); stars(c, t, seed, n, y1=H)

def follow_button(c, t, start, x=540, y=1530):
    if t <= start: return
    b = ease_back(prog(t, start, 0.55), 2.2); bob = 1 + 0.05 * math.sin(t * 6)
    c.save(); c.translate(x, y); c.scale(b * bob, b * bob)
    c.drawRoundRect(skia.Rect(-250, -66, 250, 94), 80, 80, P(color=col('#000000', 60), blur=10))
    c.drawRoundRect(skia.Rect(-250, -80, 250, 80), 80, 80, lin(c, (0, -80, 0, 80), [col('#ff5c85'), col('#e8264f')]))
    c.drawRoundRect(skia.Rect(-250, -80, 250, 80), 80, 80, P(color=col('#ffffff'), stroke=8))
    text_block(c, '+ Follow', 0, 0, size=80, fill='#ffffff', stroke='#b8183f')
    c.restore()

_CONT = [(0.00, -0.35, 0.30, 0.22), (0.08, 0.15, 0.22, 0.30), (0.30, -0.10, 0.34, 0.40), (0.42, 0.45, 0.18, 0.16),
         (0.58, -0.45, 0.30, 0.18), (0.66, 0.05, 0.20, 0.28), (0.82, 0.30, 0.26, 0.22), (0.90, -0.20, 0.16, 0.20)]
def earth(c, x, y, r, t, rot=0.0, mood='happy', face_on=True, sun_dir=None, night=0.62):
    """Side view globe. rot = turns (continents scroll). sun_dir = angle in degrees pointing to the sun (180 = left) -> night side shaded."""
    c.drawCircle(x, y, r * 1.25, rad(x, y, r * 1.25, [col('#7fd0ff', 110), col('#7fd0ff', 0)]))
    c.save(); clip = skia.Path(); clip.addCircle(x, y, r); c.clipPath(clip, doAntiAlias=True)
    c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.35, r * 1.6, [col('#6cc8ff'), col('#2f80ff'), col('#1a4fb8')], [0, 0.5, 1]))
    for lon, lat, w, h in _CONT:
        a = 2 * math.pi * (lon + rot); ca = math.cos(a)
        if ca <= 0.02: continue
        cx = x + math.sin(a) * r * math.sqrt(max(0, 1 - lat * lat)); cy = y + lat * r
        ww = w * r * ca
        c.drawOval(skia.Rect(cx - ww, cy - h * r, cx + ww, cy + h * r), P(color=col('#5fd068')))
        c.drawOval(skia.Rect(cx - ww * 0.6, cy - h * r * 0.5, cx + ww * 0.5, cy + h * r * 0.4), P(color=col('#46b553')))
    c.drawOval(skia.Rect(x - r * 0.35, y - r * 1.04, x + r * 0.35, y - r * 0.88), P(color=col('#ffffff', 230)))
    c.drawOval(skia.Rect(x - r * 0.3, y + r * 0.9, x + r * 0.3, y + r * 1.04), P(color=col('#ffffff', 230)))
    if sun_dir is not None:
        c.save(); c.translate(x, y); c.rotate(sun_dir)
        c.drawRect(skia.Rect(-r * 1.1, -r * 1.1, r * 1.1, r * 1.1), lin(c, (r * 0.15, 0, -r * 0.25, 0), [col('#0a1238', 0), col('#0a1238', int(255 * night))], vertical=False))
        c.restore()
    c.restore()
    c.drawCircle(x, y, r, P(color=col('#ffffff', 70), stroke=r * 0.03))
    c.drawOval(skia.Rect(x - r * 0.6, y - r * 0.75, x - r * 0.1, y - r * 0.45), P(color=col('#ffffff', 90), blur=r * 0.06))
    if face_on: face(c, x, y + r * 0.08, r * 0.85, t, 1.3, mood)

def earth_top(c, x, y, r, t, rot=0.0, sun_dir=180, night=0.65):
    """North-pole view: disc with continents rotating around the centre; half facing sun_dir is lit."""
    c.drawCircle(x, y, r * 1.2, rad(x, y, r * 1.2, [col('#7fd0ff', 100), col('#7fd0ff', 0)]))
    c.save(); clip = skia.Path(); clip.addCircle(x, y, r); c.clipPath(clip, doAntiAlias=True)
    c.drawCircle(x, y, r, rad(x, y, r, [col('#4aa8ff'), col('#2f80ff'), col('#1a4fb8')], [0, 0.6, 1]))
    c.save(); c.translate(x, y); c.rotate(rot * 360)
    for i, (dx, dy, rr) in enumerate([(-0.45, -0.3, 0.32), (0.4, -0.45, 0.25), (0.5, 0.35, 0.3), (-0.3, 0.5, 0.26), (0.05, 0.05, 0.18)]):
        c.drawCircle(dx * r, dy * r, rr * r, P(color=col('#5fd068')))
    c.drawCircle(0, 0, r * 0.22, P(color=col('#ffffff', 235)))
    c.restore()
    c.save(); c.translate(x, y); c.rotate(sun_dir)
    c.drawRect(skia.Rect(-r * 1.1, -r * 1.1, 0, r * 1.1), P(color=col('#0a1238', int(255 * night))))
    c.restore(); c.restore()
    c.drawCircle(x, y, r, P(color=col('#ffffff', 80), stroke=r * 0.03))

def house(c, x, y, s=1.0, ang=0.0, lit=True):
    """x,y = bottom centre; ang = rotation in degrees (0 = upright)."""
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    c.drawRect(skia.Rect(-40, -60, 40, 0), P(color=col('#fff1d6' if lit else '#8a8fb0')))
    rf = skia.Path(); rf.moveTo(-55, -55); rf.lineTo(0, -100); rf.lineTo(55, -55); rf.close()
    c.drawPath(rf, P(color=col('#ff6b6b' if lit else '#9a4a5a')))
    c.drawRect(skia.Rect(-10, -30, 10, 0), P(color=col('#8a5a3a')))
    c.drawRect(skia.Rect(16, -48, 32, -32), P(color=col('#ffd23f' if not lit else '#8fd3ff')))
    c.drawRect(skia.Rect(-40, -60, 40, 0), P(color=col('#2b1d0e', 120), stroke=3))
    c.restore()

def zzz(c, x, y, t, size=60, alpha=255):
    for i in range(3):
        u = (t * 0.5 + i / 3) % 1.0
        a = int(alpha * math.sin(u * math.pi))
        text_block(c, 'z', x + u * 60 + i * 8, y - u * 140, size=int(size * (0.6 + 0.6 * u)), fill='#ffffff', stroke='#3a4a8a', alpha=a)

def moon(c, x, y, r, t, phase=0.5, face_on=True, mood='happy', glow=True, dark_a=150, lit_left=False):
    """phase: 0 = new, 0.25 = right half lit, 0.5 = full, 0.75 = left half lit. lit_left mirrors (for 'sun on the left' diagrams use moon_lit)."""
    ph = phase % 1.0
    if glow:
        k = (1 - math.cos(2 * math.pi * ph)) / 2
        c.drawCircle(x, y, r * 1.7, rad(x, y, r * 1.7, [col('#fff6c8', int(110 * k)), col('#fff6c8', 0)]))
    c.drawCircle(x, y, r, P(color=col('#4a5274', dark_a)))
    c.drawCircle(x, y, r, P(color=col('#8a93c0', int(dark_a * 0.8)), stroke=r * 0.03))
    lit = moon_lit_path(x, y, r, ph)
    if lit is not None:
        c.save(); c.clipPath(lit, doAntiAlias=True)
        c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.35, r * 1.5, [col('#fffdf0'), col('#fff1b8'), col('#f2d77a')], [0, 0.5, 1]))
        for dx, dy, rr in [(-0.35, -0.3, 0.16), (0.3, 0.25, 0.13), (0.1, -0.5, 0.09), (-0.45, 0.4, 0.08), (0.5, -0.15, 0.07)]:
            c.drawCircle(x + dx * r, y + dy * r, rr * r, P(color=col('#e6c96a', 160)))
        c.restore()
    if face_on: face(c, x, y + r * 0.05, r * 0.85, t, 2.1, mood)

def moon_lit_path(x, y, r, ph, lit_dir=0.0):
    """Lit region of the moon disc. lit_dir rotates the terminator (degrees)."""
    ph = ph % 1.0
    if ph < 0.004 or ph > 0.996: return None
    disc = skia.Path(); disc.addCircle(x, y, r)
    if abs(ph - 0.5) < 0.004: return disc
    half = skia.Path()
    if ph < 0.5: half.addRect(x, y - r - 2, x + r + 2, y + r + 2)
    else: half.addRect(x - r - 2, y - r - 2, x, y + r + 2)
    half = skia.Op(disc, half, skia.PathOp.kIntersect_PathOp)
    w = abs(math.cos(2 * math.pi * ph)) * r
    ell = skia.Path(); ell.addOval(skia.Rect(x - w, y - r, x + w, y + r))
    crescent = ph < 0.25 or ph > 0.75
    out = skia.Op(half, ell, skia.PathOp.kDifference_PathOp if crescent else skia.PathOp.kUnion_PathOp)
    if lit_dir:
        out.transform(skia.Matrix.RotateDeg(lit_dir, (x, y)))
    return out

def half_lit_ball(c, x, y, r, t, sun_dir=180, face_on=False, mood='happy', base='#fff1b8', dark='#3a4166'):
    """Moon seen from above / from the side: the half pointing to sun_dir (degrees) is bright."""
    c.drawCircle(x, y, r, P(color=col(dark)))
    c.save(); clip = skia.Path(); clip.addCircle(x, y, r); c.clipPath(clip, doAntiAlias=True)
    c.translate(x, y); c.rotate(sun_dir)
    c.drawRect(skia.Rect(0, -r - 2, r + 2, r + 2), P(color=col(base)))
    c.restore()
    c.drawCircle(x, y, r, P(color=col('#ffffff', 90), stroke=max(2, r * 0.05)))
    if face_on: face(c, x, y + r * 0.05, r * 0.85, t, 2.1, mood)

def raindrop(c, x, y, r, t, seed=0, face_on=True, mood='happy', shape='tear', alpha=255, squash=0.0):
    """x,y = centre of the round belly. shape: 'tear' | 'round' | 'bun'."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.scale(1 + squash, 1 - squash)
    pth = skia.Path()
    if shape == 'tear':
        pth.moveTo(0, -r * 1.9); pth.cubicTo(r * 0.35, -r * 1.2, r, -r * 0.6, r, 0)
        pth.arcTo(skia.Rect(-r, -r, r, r), 0, 180, False); pth.cubicTo(-r, -r * 0.6, -r * 0.35, -r * 1.2, 0, -r * 1.9); pth.close()
    elif shape == 'round':
        pth.addCircle(0, 0, r)
    else:
        pth.moveTo(-r * 1.2, r * 0.45); pth.cubicTo(-r * 1.35, -r * 1.25, r * 1.35, -r * 1.25, r * 1.2, r * 0.45)
        pth.quadTo(0, r * 0.25, -r * 1.2, r * 0.45); pth.close()
    c.drawPath(pth, rad(-r * 0.3, -r * 0.5, r * 2.0, [col('#e8f7ff', a), col('#6cc4ff', a), col('#2f80ff', a)], [0, 0.45, 1]))
    c.drawPath(pth, P(color=col('#1f63c9', int(a * 0.5)), stroke=max(2, r * 0.06)))
    c.drawOval(skia.Rect(-r * 0.55, -r * 0.6, -r * 0.2, -r * 0.05), P(color=col('#ffffff', int(a * 0.8)), blur=r * 0.04))
    if face_on and a > 200:
        face(c, 0, r * (0.05 if shape != 'bun' else -0.2), r * (0.85 if shape != 'bun' else 0.75), t, seed, mood)
    c.restore()

def vapor(c, x, y, s, t, seed=0, alpha=255):
    """Wiggly see-through puff of water vapor."""
    a = int(alpha)
    pth = skia.Path()
    for i in range(14):
        u = i / 13; yy = y - u * 90 * s; xx = x + math.sin(t * 3 + seed + u * 6) * 14 * s
        (pth.moveTo if i == 0 else pth.lineTo)(xx, yy)
    c.drawPath(pth, P(color=col('#ffffff', int(a * 0.55)), stroke=12 * s, blur=4 * s))
    c.drawPath(pth, P(color=col('#ffffff', int(a * 0.8)), stroke=4 * s))

def sea(c, y, t, c1='#3fa9ff', c2='#1a5fc9'):
    p = skia.Path(); p.moveTo(0, y)
    for i in range(0, W + 41, 40):
        p.lineTo(i, y + math.sin(i * 0.02 + t * 2) * 12)
    p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, y, 0, H), [col(c1), col(c2)]))
    for k in range(3):
        yy = y + 50 + k * 70
        for i in range(6):
            x0 = (i * 220 + t * (30 + k * 10) + k * 90) % (W + 200) - 100
            c.drawLine(x0, yy, x0 + 70, yy, P(color=col('#ffffff', 90), stroke=6))

def cloud_char(c, x, y, s, t, seed=0, mood='happy', gray=0.0, face_on=True):
    """Big cloud with a face. gray 0..1 makes it a rain cloud."""
    parts = [(-130, 20, 85), (-60, -40, 105), (50, -55, 115), (140, 0, 90), (-20, 40, 90), (80, 45, 85), (-170, 55, 55), (190, 55, 55)]
    top = mix_hex('#ffffff', '#9aa7bd', gray); sh = mix_hex('#b9d6ee', '#6f7d95', gray)
    for dx, dy, r in parts: c.drawCircle(x + dx * s, y + (dy + 16) * s, r * s, P(color=sh))
    for dx, dy, r in parts: c.drawCircle(x + dx * s, y + dy * s, r * s, P(color=top))
    for dx, dy, r in parts[1:3]: c.drawCircle(x + (dx - 15) * s, y + (dy - 20) * s, r * 0.45 * s, P(color=col('#ffffff', int(150 * (1 - gray * 0.6))), blur=8 * s))
    if face_on: face(c, x, y + 10 * s, 105 * s, t, seed, mood)

def curved_arrow(c, cx, cy, r, a0, a1, colr='#ffffff', w=14, alpha=255):
    """Arc arrow from angle a0 to a1 (degrees, clockwise positive)."""
    pth = skia.Path(); pth.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), a0, a1 - a0)
    c.drawPath(pth, P(color=col(colr, alpha), stroke=w))
    ang = math.radians(a1); ex, ey = cx + math.cos(ang) * r, cy + math.sin(ang) * r
    d = 1 if a1 > a0 else -1; tx, ty = -math.sin(ang) * d, math.cos(ang) * d
    nx, ny = math.cos(ang), math.sin(ang); L = w * 2.2
    hd = skia.Path(); hd.moveTo(ex + tx * L, ey + ty * L); hd.lineTo(ex + nx * L * 0.8, ey + ny * L * 0.8); hd.lineTo(ex - nx * L * 0.8, ey - ny * L * 0.8); hd.close()
    c.drawPath(hd, P(color=col(colr, alpha)))

# ---------------- Rainbow, salt, bees (added for ep_005+) ----------------
RAINBOW = ['#ff3b3b', '#ff9f1c', '#ffe14d', '#4cd964', '#2fa8ff', '#3a5bff', '#9b4dff']

def rainbow(c, cx, cy, r, band=26, grow=1.0, alpha=255, a0=180, sweep=180):
    """Rainbow arc centred at cx,cy (outer radius r). grow 0..1 draws it from the left. Red outside, violet inside."""
    if grow <= 0: return
    for i, h in enumerate(RAINBOW):
        rr = r - band * (i + 0.5)
        pth = skia.Path(); pth.addArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), a0, sweep * grow)
        p = P(color=col(h, alpha), stroke=band + 1); p.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawPath(pth, p)
    pth = skia.Path(); pth.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), a0, sweep * grow)
    c.drawPath(pth, P(color=col('#ffffff', int(alpha * 0.25)), stroke=band * 3, blur=band))

def salt_crystal(c, x, y, s, t, seed=0, face_on=True, mood='happy', alpha=255, rot=0.0):
    """Cute little salt cube (x,y = centre)."""
    a = int(alpha); r = 50 * s
    c.save(); c.translate(x, y + math.sin(t * 3 + seed) * 4 * s); c.rotate(rot + math.sin(t * 2 + seed) * 4)
    top = skia.Path(); top.moveTo(-r, -r * 0.55); top.lineTo(-r * 0.45, -r * 1.05); top.lineTo(r * 1.05, -r * 1.05); top.lineTo(r, -r * 0.55); top.close()
    side = skia.Path(); side.moveTo(r, -r * 0.55); side.lineTo(r * 1.05, -r * 1.05); side.lineTo(r * 1.05, r * 0.5); side.lineTo(r, r); side.close()
    c.drawPath(top, P(color=col('#ffffff', a)))
    c.drawPath(side, P(color=col('#cfe3f2', a)))
    c.drawRoundRect(skia.Rect(-r, -r * 0.55, r, r), r * 0.12, r * 0.12, lin(c, (0, -r, 0, r), [col('#ffffff', a), col('#e3f1fb', a)]))
    c.drawRoundRect(skia.Rect(-r, -r * 0.55, r, r), r * 0.12, r * 0.12, P(color=col('#9fbdd6', a), stroke=max(2, r * 0.06)))
    c.drawLine(-r * 0.7, -r * 0.35, -r * 0.35, -r * 0.35, P(color=col('#ffffff', a), stroke=r * 0.08))
    if face_on and a > 200: face(c, 0, r * 0.25, r * 0.8, t, seed, mood)
    c.restore()

def rock(c, x, y, s, t, seed=0, face_on=True, mood='happy', worn=0.0):
    """Friendly grey rock, x,y = bottom centre. worn 0..1 makes it smaller/rounder."""
    k = 1 - 0.35 * worn
    c.save(); c.translate(x, y); c.scale(s * k, s * k)
    c.drawOval(skia.Rect(-150, -14, 150, 14), P(color=col('#000000', 50), blur=8))
    pth = skia.Path(); pth.moveTo(-140, 0); pth.cubicTo(-170, -120, -90, -200, 0, -200); pth.cubicTo(110, -210, 170, -110, 140, 0); pth.close()
    c.drawPath(pth, lin(c, (0, -210, 0, 0), [col('#b7bfcc'), col('#7d8799')]))
    for dx, dy, rr in [(-70, -60, 14), (60, -130, 10), (85, -45, 8), (-30, -150, 7)]:
        c.drawCircle(dx, dy, rr, P(color=col('#6b7486', 150)))
    c.drawOval(skia.Rect(-90, -180, -30, -150), P(color=col('#ffffff', 80), blur=6))
    if face_on: face(c, 0, -95, 85, t, seed, mood)
    c.restore()

def flower(c, x, y, s, t, seed=0, petal='#ff8fab', stem=True, face_on=True):
    """x,y = centre of the blossom."""
    sway = math.sin(t * 1.6 + seed) * 4
    if stem:
        c.drawLine(x, y, x + sway, y + 260 * s, P(color=col('#3fae4a'), stroke=14 * s))
        lf = skia.Path(); lf.moveTo(x + sway * 0.5, y + 170 * s); lf.quadTo(x + 70 * s, y + 120 * s, x + 90 * s, y + 160 * s); lf.quadTo(x + 50 * s, y + 190 * s, x + sway * 0.5, y + 170 * s); lf.close()
        c.drawPath(lf, P(color=col('#4cc35a')))
    c.save(); c.translate(x, y); c.rotate(sway * 2 + t * 6)
    for i in range(6):
        c.save(); c.rotate(i * 60)
        c.drawOval(skia.Rect(-28 * s, -95 * s, 28 * s, -25 * s), P(color=col(petal)))
        c.drawOval(skia.Rect(-28 * s, -95 * s, 28 * s, -25 * s), P(color=col('#ffffff', 90), stroke=3 * s))
        c.restore()
    c.restore()
    c.drawCircle(x, y, 40 * s, rad(x - 10 * s, y - 12 * s, 60 * s, [col('#ffe680'), col('#ffb703')]))
    if face_on: face(c, x, y + 3 * s, 36 * s, t, seed)

def bee(c, x, y, s, t, seed=0, mood='happy', flip=False, cheeks_full=0.0):
    """Round cute honeybee, x,y = body centre. flip = facing left."""
    c.save(); c.translate(x, y + math.sin(t * 6 + seed) * 6 * s); c.scale(-s if flip else s, s)
    flap = math.sin(t * 60 + seed) * 0.5 + 0.5
    for dx, rot in [(-18, -25), (22, 20)]:
        c.save(); c.translate(dx, -55); c.rotate(rot - flap * 20 * (1 if dx > 0 else -1))
        c.drawOval(skia.Rect(-30, -80, 30, 0), P(color=col('#ffffff', 170)))
        c.drawOval(skia.Rect(-30, -80, 30, 0), P(color=col('#9fd3ff', 200), stroke=3))
        c.restore()
    body = skia.Rect(-80, -60, 70, 60)
    c.save(); clip = skia.Path(); clip.addOval(body); c.clipPath(clip, doAntiAlias=True)
    c.drawOval(body, rad(-20, -30, 120, [col('#fff07a'), col('#ffc93c')]))
    for sx in (-45, -5):
        c.drawRect(skia.Rect(sx, -70, sx + 22, 70), P(color=col('#3a2a1a')))
    c.restore()
    c.drawOval(body, P(color=col('#3a2a1a', 160), stroke=3))
    st = skia.Path(); st.moveTo(-78, -8); st.lineTo(-104, 0); st.lineTo(-78, 8); st.close()
    c.drawPath(st, P(color=col('#3a2a1a')))
    hx = 78
    c.drawCircle(hx, -5, 52, rad(hx - 15, -20, 70, [col('#fff07a'), col('#ffc93c')]))
    c.drawCircle(hx, -5, 52, P(color=col('#3a2a1a', 160), stroke=3))
    for ax in (-12, 18):
        a = skia.Path(); a.moveTo(hx + ax, -52); a.quadTo(hx + ax + 10, -90, hx + ax + 24, -92)
        c.drawPath(a, P(color=col('#3a2a1a'), stroke=5)); c.drawCircle(hx + ax + 24, -92, 8, P(color=col('#3a2a1a')))
    if cheeks_full > 0:
        c.drawCircle(hx + 30, 15, 14 * cheeks_full, P(color=col('#ffb703', 200)))
    face(c, hx + 6, 0, 46, t, seed, mood)
    c.restore()

def hexagon_path(x, y, r):
    p = skia.Path()
    for i in range(6):
        a = math.radians(60 * i + 30)
        (p.moveTo if i == 0 else p.lineTo)(x + math.cos(a) * r, y + math.sin(a) * r)
    p.close(); return p

def honeycomb(c, x0, y0, cols_, rows, r, fill=None, t=0.0):
    """Grid of hexagon cells. fill(i, j) -> (honey 0..1, capped 0..1)."""
    w = math.sqrt(3) * r
    for j in range(rows):
        for i in range(cols_):
            x = x0 + i * w + (w / 2 if j % 2 else 0); y = y0 + j * r * 1.5
            hx = hexagon_path(x, y, r * 0.94)
            c.drawPath(hx, P(color=col('#ffe7a3')))
            h, cap = fill(i, j) if fill else (0, 0)
            if h > 0:
                c.drawPath(hexagon_path(x, y, r * 0.78 * (0.4 + 0.6 * h)), P(color=col('#ffb703', int(140 + 115 * h))))
                c.drawCircle(x - r * 0.2, y - r * 0.25, r * 0.12, P(color=col('#ffffff', int(150 * h))))
            if cap > 0:
                c.drawPath(hexagon_path(x, y, r * 0.8 * cap), P(color=col('#fff2c2')))
                c.drawPath(hexagon_path(x, y, r * 0.8 * cap), P(color=col('#e0b04a'), stroke=3))
            c.drawPath(hx, P(color=col('#d99a1e'), stroke=r * 0.12))

def honey_jar(c, x, y, s, t, fill=1.0, face_on=True):
    """x,y = bottom centre."""
    c.save(); c.translate(x, y); c.scale(s, s)
    body = skia.Rect(-110, -230, 110, 0)
    c.drawRoundRect(body, 60, 60, P(color=col('#ffffff', 80)))
    c.save(); clip = skia.Path(); clip.addRoundRect(body, 60, 60); c.clipPath(clip, doAntiAlias=True)
    c.drawRect(skia.Rect(-120, -230 * fill, 120, 0), lin(c, (0, -230, 0, 0), [col('#ffcc33'), col('#e88a00')]))
    c.restore()
    c.drawRoundRect(body, 60, 60, P(color=col('#ffffff', 200), stroke=6))
    c.drawRoundRect(skia.Rect(-95, -275, 95, -225), 16, 16, P(color=col('#ff6b6b')))
    c.drawRoundRect(skia.Rect(-80, -140, 80, -60), 14, 14, P(color=col('#fff6dc')))
    text_block(c, 'HONEY', 0, -100, size=40, fill='#c06a00', hi='#c06a00', stroke='#fff6dc')
    if face_on and fill > 0.6: face(c, 0, -175, 55, t, 5)
    c.restore()

def beehive(c, x, y, s, t, face_on=True):
    """Classic dome hive (skep), x,y = bottom centre."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect(-190, -14, 190, 18), P(color=col('#000000', 50), blur=8))
    dome = skia.Path(); dome.moveTo(-180, 0); dome.cubicTo(-200, -260, -110, -380, 0, -380); dome.cubicTo(110, -380, 200, -260, 180, 0); dome.close()
    c.drawPath(dome, lin(c, (0, -380, 0, 0), [col('#f7c873'), col('#d9952e')]))
    c.save(); c.clipPath(dome, doAntiAlias=True)
    for k in range(1, 6):
        yy = -380 + k * 66
        c.drawLine(-220, yy, 220, yy, P(color=col('#b9771f'), stroke=8))
    c.restore()
    c.drawPath(dome, P(color=col('#a8661a'), stroke=6))
    c.drawOval(skia.Rect(-45, -95, 45, -25), P(color=col('#4a2a0c')))
    if face_on: face(c, 0, -230, 95, t, 6)
    c.restore()


def trail(c, pts_hist, hexcol, width=14):
    """Smooth fading motion trail (butt caps, so overlapping segments don't show as beads)."""
    n = len(pts_hist)
    for i in range(1, n):
        p = P(color=col(hexcol, int(170 * i / n)), stroke=max(1.0, width * i / n))
        p.setStrokeCap(skia.Paint.kButt_Cap)
        c.drawLine(*pts_hist[i - 1], *pts_hist[i], p)
# ---------------- Leaves, seasons, storms (added for ep_008+) ----------------
def mix_hx(h1, h2, t):
    """Like mix_hex but returns a '#rrggbb' string (can be nested)."""
    h1, h2 = h1.lstrip('#'), h2.lstrip('#')
    return '#' + ''.join('%02x' % int(lerp(int(h1[i:i+2], 16), int(h2[i:i+2], 16), clamp(t))) for i in (0, 2, 4))

AUTUMN = ['#ffd23f', '#ff9f1c', '#ff6b2c', '#e8382f', '#c9302c']

def leaf_path(r):
    """Pointed leaf shape, tip at (0,-r*1.5), stem end at (0, r)."""
    p = skia.Path(); p.moveTo(0, r)
    p.cubicTo(-r * 1.25, r * 0.55, -r * 1.05, -r * 0.9, 0, -r * 1.5)
    p.cubicTo(r * 1.05, -r * 0.9, r * 1.25, r * 0.55, 0, r); p.close()
    return p

def leaf(c, x, y, s, t, colr='#5cc94a', seed=0, face_on=True, mood='happy', rot=0.0, alpha=255, layer=None):
    """Cute leaf character, x,y = centre. colr can be any hex. layer=(hex, 0..1) draws a second colour on top (e.g. green 'blanket')."""
    a = int(alpha); r = 60 * s
    c.save(); c.translate(x, y); c.rotate(rot + math.sin(t * 1.8 + seed) * 5)
    c.drawLine(0, r * 0.9, 0, r * 1.6, P(color=col('#8a5a2b', a), stroke=r * 0.12))
    pth = leaf_path(r)
    c.drawPath(pth, rad(-r * 0.3, -r * 0.5, r * 2.0, [col('#ffffff', a), col(colr, a), col(colr, a)], [0, 0.25, 1]))
    if layer is not None and layer[1] > 0:
        c.save(); c.clipPath(pth, doAntiAlias=True)
        top = lerp(r * 1.1, -r * 1.6, layer[1])
        c.drawRect(skia.Rect(-r * 1.5, top, r * 1.5, r * 1.2), rad(-r * 0.3, -r * 0.5, r * 2.0, [col('#b7f0a0', a), col(layer[0], a), col(layer[0], a)], [0, 0.25, 1]))
        if layer[1] < 1: c.drawLine(-r * 1.5, top, r * 1.5, top, P(color=col('#2f8f3a', a), stroke=r * 0.08))
        c.restore()
    vein = col('#000000', int(a * 0.18))
    c.drawLine(0, r * 0.9, 0, -r * 1.2, P(color=vein, stroke=r * 0.06))
    for k, (yy, dx) in enumerate([(0.3, 0.55), (-0.25, 0.5), (-0.75, 0.32)]):
        for sx in (-1, 1): c.drawLine(0, yy * r + r * 0.15, sx * dx * r, yy * r - r * 0.2, P(color=vein, stroke=r * 0.045))
    c.drawPath(pth, P(color=col('#000000', int(a * 0.15)), stroke=max(2, r * 0.05)))
    if face_on and a > 200: face(c, 0, -r * 0.05, r * 0.72, t, seed, mood)
    c.restore()

def leafy_tree(c, x, y, s, t, autumn=0.0, seed=0, bare=0.0, face_on=False, mood='happy'):
    """Big round tree, x,y = trunk bottom. autumn 0..1 turns blobs from green to yellow/orange/red (staggered). bare 0..1 removes leaves."""
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(math.sin(t * 1.2 + seed) * 1.2)
    c.drawOval(skia.Rect(-170, -16, 170, 16), P(color=col('#000000', 45), blur=8))
    tr = skia.Path(); tr.moveTo(-38, 0); tr.cubicTo(-28, -120, -24, -200, -20, -300); tr.lineTo(20, -300); tr.cubicTo(24, -200, 28, -120, 38, 0); tr.close()
    c.drawPath(tr, lin(c, (-40, 0, 40, 0), [col('#8a5a2b'), col('#6b4423')], vertical=False))
    for sx, ang in [(-1, -40), (1, 35), (-1, -65)]:
        c.save(); c.translate(0, -230 - (ang == -65) * 60); c.rotate(ang)
        c.drawLine(0, 0, 0, -130, P(color=col('#6b4423'), stroke=16)); c.restore()
    rnd = random.Random(seed + 40)
    blobs = [(0, -470, 120), (-120, -400, 100), (120, -395, 105), (-60, -540, 90), (75, -545, 92), (-170, -320, 75), (170, -315, 78), (0, -360, 100), (-55, -440, 80), (60, -455, 80)]
    for i, (dx, dy, r) in enumerate(blobs):
        k = clamp(autumn * 1.6 - rnd.random() * 0.6)
        tgt = AUTUMN[(i + seed) % len(AUTUMN)]
        g = mix_hex('#5cc94a', tgt, k); g2 = mix_hex('#2f8f3a', '#b5481c', k)
        b = clamp(bare * 1.5 - rnd.random() * 0.5)
        if b >= 1: continue
        rr = r * (1 - b)
        c.drawCircle(dx, dy, rr, rad(dx - rr * 0.3, dy - rr * 0.4, rr * 1.5, [g, g2]))
    if face_on and bare < 0.5: face(c, 0, -420, 95, t, seed, mood)
    c.restore()

def falling_leaves(c, t, seed=3, n=10, colors=None, y0=0, y1=H, s=0.35, speed=90, alpha=255):
    rnd = random.Random(seed); colors = colors or AUTUMN
    for i in range(n):
        x0 = rnd.uniform(0, W); ph = rnd.uniform(0, 1); sp = speed * rnd.uniform(0.7, 1.3)
        y = y0 + ((t * sp + ph * (y1 - y0)) % (y1 - y0))
        x = x0 + math.sin(t * 1.5 + i) * 60
        leaf(c, x, y, s * rnd.uniform(0.7, 1.2), t, colors[i % len(colors)], i, face_on=False, rot=math.sin(t * 2 + i) * 40 + i * 30, alpha=alpha)

def lightning_bolt(c, x0, y0, x1, y1, t=0.0, seed=0, w=26, alpha=255, branches=True):
    """Zig-zag bolt from (x0,y0) to (x1,y1) with glow."""
    rnd = random.Random(seed); n = 7; pts = [(x0, y0)]
    for i in range(1, n):
        u = i / n; pts.append((lerp(x0, x1, u) + rnd.uniform(-70, 70), lerp(y0, y1, u) + rnd.uniform(-20, 20)))
    pts.append((x1, y1))
    def poly(ps):
        p = skia.Path(); p.moveTo(*ps[0])
        for q in ps[1:]: p.lineTo(*q)
        return p
    paths = [(poly(pts), w)]
    if branches:
        for bi in (2, 4):
            bx, by = pts[bi]; d = 1 if rnd.random() > 0.5 else -1
            paths.append((poly([(bx, by), (bx + d * 70, by + 60), (bx + d * 60, by + 120), (bx + d * 120, by + 190)]), w * 0.5))
    a = int(alpha)
    for p, ww in paths: c.drawPath(p, P(color=col('#b9d9ff', int(a * 0.6)), stroke=ww * 3.2, blur=ww * 1.2))
    for p, ww in paths: c.drawPath(p, P(color=col('#fff6a8', a), stroke=ww))
    for p, ww in paths: c.drawPath(p, P(color=col('#ffffff', a), stroke=ww * 0.4))

def sound_rings(c, x, y, t, start, n=4, colr='#ffffff', speed=420, life=1.2, w=14, a0=-60, sweep=120, both=True):
    """Expanding sound-wave arcs, emitted from start, every 0.25 s."""
    for i in range(n):
        tt = t - start - i * 0.25
        if tt < 0 or tt > life: continue
        r = 60 + speed * tt; al = int(230 * (1 - tt / life))
        for base in ([a0, a0 + 180] if both else [a0]):
            pth = skia.Path(); pth.addArc(skia.Rect(x - r, y - r, x + r, y + r), base, sweep)
            c.drawPath(pth, P(color=col(colr, al), stroke=w))

def tilted_earth(c, x, y, r, t, tilt=23.5, sun_dir=None, face_on=True, mood='happy', spin=True, axis=True, night=0.55):
    """Earth with a visible, tilted axis stick. tilt in degrees (positive = top leans right)."""
    c.save(); c.translate(x, y); c.rotate(tilt)
    if axis: c.drawLine(0, -r * 1.45, 0, r * 1.45, P(color=col('#ffffff', 220), stroke=max(3, r * 0.05)))
    c.restore()
    c.save(); c.translate(x, y); c.rotate(tilt)
    earth(c, 0, 0, r, t, rot=(t * 0.12 if spin else 0), mood=mood, face_on=False, sun_dir=None if sun_dir is None else sun_dir - tilt, night=night)
    c.restore()
    if axis:
        c.save(); c.translate(x, y); c.rotate(tilt)
        c.drawCircle(0, -r * 1.45, max(5, r * 0.07), P(color=col('#ff6b6b')))
        c.restore()
    if face_on: face(c, x, y + r * 0.08, r * 0.8, t, 1.3, mood)

def flashlight(c, x, y, ang, s=1.0, on=1.0):
    """Torch whose lamp end is at x,y, pointing at angle ang (deg, 90 = straight down)."""
    c.save(); c.translate(x, y); c.rotate(ang - 90); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-32, -260, 32, -60), 22, 22, lin(c, (-32, 0, 32, 0), [col('#ff7b7b'), col('#d93a4a')], vertical=False))
    hd = skia.Path(); hd.moveTo(-34, -70); hd.lineTo(-58, 0); hd.lineTo(58, 0); hd.lineTo(34, -70); hd.close()
    c.drawPath(hd, lin(c, (-58, 0, 58, 0), [col('#c9d3e0'), col('#8d99ab')], vertical=False))
    c.drawRect(skia.Rect(-56, -6, 56, 4), P(color=col('#fff6b0', int(255 * on))))
    c.drawRoundRect(skia.Rect(-12, -200, 12, -170), 6, 6, P(color=col('#ffd23f')))
    c.restore()

def snowflake(c, x, y, r, t, seed=0, alpha=255):
    c.save(); c.translate(x, y); c.rotate(t * 30 + seed * 20)
    p = P(color=col('#ffffff', alpha), stroke=max(2, r * 0.14))
    for k in range(6):
        c.save(); c.rotate(k * 60); c.drawLine(0, 0, 0, -r, p); c.drawLine(0, -r * 0.55, r * 0.3, -r * 0.8, p); c.drawLine(0, -r * 0.55, -r * 0.3, -r * 0.8, p); c.restore()
    c.restore()

def snow(c, t, seed=4, n=40, y0=0, y1=H, alpha=230):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W); ph = rnd.uniform(0, 1); sp = rnd.uniform(50, 110)
        y = y0 + ((t * sp + ph * (y1 - y0)) % (y1 - y0)); x = x0 + math.sin(t + i) * 30
        snowflake(c, x, y, rnd.uniform(8, 18), t, i, alpha)

# ---------------- Water, ice, fish, butterflies (added for ep_011+) ----------------
def water_molecule(c, x, y, r, t, seed=0, rot=0.0, face_on=True, alpha=255, mood='happy'):
    """Cute H2O: big blue oxygen ball with face, two small white hydrogen 'ears' (104.5 deg apart). rot in degrees."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(rot)
    for sx in (-1, 1):
        ang = math.radians(90 + sx * 52.25); hx, hy = math.cos(ang) * r * 1.0, -math.sin(ang) * r * 1.0
        c.drawCircle(hx, hy, r * 0.52, rad(hx - r * 0.18, hy - r * 0.2, r * 0.8, [col('#ffffff', a), col('#f1f4fa', a), col('#c9d3e3', a)], [0, 0.5, 1]))
        c.drawCircle(hx, hy, r * 0.52, P(color=col('#93a3bf', a), stroke=max(1.5, r * 0.06)))
    c.drawCircle(0, 0, r, rad(-r * 0.3, -r * 0.35, r * 1.5, [col('#e6f7ff', a), col('#62c2ff', a), col('#2a86e0', a)], [0, 0.4, 1]))
    c.drawCircle(0, 0, r, P(color=col('#1f6fc4', a), stroke=max(1.5, r * 0.06)))
    c.drawOval(skia.Rect(-r * 0.6, -r * 0.72, -r * 0.15, -r * 0.42), P(color=col('#ffffff', int(a * 0.55)), blur=r * 0.05))
    c.restore()
    if face_on and a > 200: face(c, x, y + r * 0.12, r * 0.8, t, seed, mood)

def ice_cube(c, x, y, s, t, seed=0, face_on=True, mood='happy', alpha=255, rot=0.0):
    """Glassy ice cube with a face, x,y = centre of the front face (front face is 200*s wide)."""
    a = int(alpha); r = 100 * s; d = r * 0.35
    c.save(); c.translate(x, y); c.rotate(rot)
    top = skia.Path(); top.moveTo(-r, -r); top.lineTo(-r + d, -r - d); top.lineTo(r + d, -r - d); top.lineTo(r, -r); top.close()
    side = skia.Path(); side.moveTo(r, -r); side.lineTo(r + d, -r - d); side.lineTo(r + d, r - d); side.lineTo(r, r); side.close()
    c.drawPath(top, lin(c, (0, -r - d, 0, -r), [col('#ffffff', a), col('#dff3ff', a)]))
    c.drawPath(side, lin(c, (r, 0, r + d, 0), [col('#a9dcfa', a), col('#c9ebff', a)], vertical=False))
    front = skia.Rect(-r, -r, r, r)
    c.drawRoundRect(front, r * 0.14, r * 0.14, rad(-r * 0.4, -r * 0.5, r * 2.2, [col('#ffffff', a), col('#cdeeff', a), col('#8fd0f7', a)], [0, 0.45, 1]))
    for p_ in (top, side): c.drawPath(p_, P(color=col('#7fbfe6', a), stroke=max(2, r * 0.03)))
    c.drawRoundRect(front, r * 0.14, r * 0.14, P(color=col('#6fb3e0', a), stroke=max(2, r * 0.035)))
    hl = skia.Path(); hl.moveTo(-r * 0.75, r * 0.35); hl.lineTo(-r * 0.75, -r * 0.7); hl.lineTo(-r * 0.3, -r * 0.7)
    c.drawPath(hl, P(color=col('#ffffff', int(a * 0.85)), stroke=r * 0.09))
    c.drawCircle(r * 0.62, r * 0.62, r * 0.07, P(color=col('#ffffff', int(a * 0.7))))
    c.restore()
    if face_on and a > 200: face(c, x, y + r * 0.1, r * 0.72, t, seed, mood)

def bubble(c, x, y, r, alpha=200):
    a = int(alpha)
    c.drawCircle(x, y, r, P(color=col('#e9f8ff', int(a * 0.25))))
    c.drawCircle(x, y, r, P(color=col('#ffffff', a), stroke=max(1.5, r * 0.13)))
    c.drawArc(skia.Rect(x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6), 200, 60, False, P(color=col('#ffffff', a), stroke=max(1.5, r * 0.16)))

def rising_bubbles(c, t, seed=5, n=14, x0=0, x1=W, y0=620, y1=1700, rmin=6, rmax=16, speed=120, alpha=190):
    rnd = random.Random(seed)
    for i in range(n):
        bx = rnd.uniform(x0, x1); ph = rnd.uniform(0, 1); sp = speed * rnd.uniform(0.7, 1.3); r = rnd.uniform(rmin, rmax)
        y = y1 - ((t * sp + ph * (y1 - y0)) % (y1 - y0))
        bubble(c, bx + math.sin(t * 2 + i) * 12, y, r, alpha)

def seaweed(c, x, y, h, t, seed=0, colr='#3fbf6a', w=26):
    pth = skia.Path(); pth.moveTo(x, y)
    for k in range(1, 9):
        u = k / 8; pth.lineTo(x + math.sin(t * 1.6 + seed + u * 4) * 26 * u, y - h * u)
    c.drawPath(pth, P(color=col(colr), stroke=w))
    c.drawPath(pth, P(color=col('#ffffff', 45), stroke=w * 0.3))

def underwater(c, t, seed=1, floor=1660, rays=True, weeds=True):
    sky(c, '#4fd0ff', '#0b3f8f', mid='#1f8fe0')
    if rays:
        for i in range(5):
            x = 120 + i * 230 + math.sin(t * 0.6 + i) * 40
            p = skia.Path(); p.moveTo(x - 40, 0); p.lineTo(x + 40, 0); p.lineTo(x + 220, H); p.lineTo(x + 60, H); p.close()
            c.drawPath(p, lin(c, (0, 0, 0, H), [col('#ffffff', 55), col('#ffffff', 0)]))
    sand = skia.Path(); sand.moveTo(0, floor); sand.cubicTo(300, floor - 60, 650, floor + 40, W, floor - 30); sand.lineTo(W, H); sand.lineTo(0, H); sand.close()
    c.drawPath(sand, lin(c, (0, floor - 60, 0, H), [col('#ffe3a3'), col('#e9b968')]))
    rnd = random.Random(seed + 7)
    for i in range(18):
        sx, sy = rnd.uniform(0, W), rnd.uniform(floor + 30, H - 20)
        c.drawOval(skia.Rect(sx - 9, sy - 5, sx + 9, sy + 5), P(color=col('#c99a4e', 140)))
    if weeds:
        for i, (wx, hh, cc) in enumerate([(70, 330, '#3fbf6a'), (130, 230, '#2fa65a'), (960, 300, '#3fbf6a'), (1010, 200, '#2fa65a'), (560, 150, '#47c96f')]):
            seaweed(c, wx, floor + 40, hh, t, i * 1.7, cc)
        for x, cc in [(300, '#ff8fab'), (780, '#ffb35c')]:
            for k in range(5):
                a = math.radians(-160 + k * 35)
                c.drawLine(x, floor + 20, x + math.cos(a) * 60, floor + 20 + math.sin(a) * 70, P(color=col(cc), stroke=16))

def fish(c, x, y, s, t, body='#ffc93c', belly='#fff2b3', fin='#ff7a45', flip=False, gill=0.0, mouth=0.0, seed=0, kind='fish', stripes=True, wiggle=1.0):
    """Side-view cute fish facing right (flip=True faces left). x,y = body centre. gill 0..1 opens the gill flap; mouth 0..1 opens the mouth.
    kind='shark' draws a friendly rounded shark."""
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    wag = math.sin(t * 7 + seed) * 12 * wiggle
    shark = kind == 'shark'
    L = 190 if shark else 130; Hh = 70 if shark else 80
    if shark: body, belly, fin = '#7fa6c9', '#eef5fb', '#5f86ab'
    # tail
    c.save(); c.translate(-L + 15, 0); c.rotate(wag)
    tl = skia.Path()
    if shark:
        tl.moveTo(10, 0); tl.cubicTo(-30, -20, -70, -70, -95, -105); tl.cubicTo(-80, -40, -70, -10, -60, 5); tl.cubicTo(-70, 30, -80, 55, -75, 70); tl.cubicTo(-50, 40, -20, 20, 10, 0)
    else:
        tl.moveTo(10, 0); tl.cubicTo(-30, -30, -70, -85, -90, -80); tl.cubicTo(-70, -30, -70, 30, -90, 80); tl.cubicTo(-70, 85, -30, 30, 10, 0)
    tl.close(); c.drawPath(tl, lin(c, (-90, 0, 10, 0), [col(fin), col(mix_hx(fin, '#ffffff', 0.25))], vertical=False))
    c.drawPath(tl, P(color=col('#000000', 40), stroke=4))
    c.restore()
    # top & bottom fins
    tf = skia.Path()
    if shark: tf.moveTo(-60, -Hh + 12); tf.cubicTo(-40, -Hh - 40, -10, -Hh - 95, 10, -Hh - 100); tf.cubicTo(5, -Hh - 50, 20, -Hh - 10, 40, -Hh + 8)
    else: tf.moveTo(-70, -Hh + 20); tf.cubicTo(-50, -Hh - 50, 20, -Hh - 45, 40, -Hh + 12)
    tf.close(); c.drawPath(tf, P(color=col(fin))); c.drawPath(tf, P(color=col('#000000', 40), stroke=4))
    bf = skia.Path(); bf.moveTo(-50, Hh - 15); bf.cubicTo(-40, Hh + 35, 0, Hh + 30, 20, Hh - 8); bf.close()
    c.drawPath(bf, P(color=col(fin))); c.drawPath(bf, P(color=col('#000000', 40), stroke=4))
    # body
    bp = skia.Path(); bp.moveTo(-L + 10, 0)
    bp.cubicTo(-L + 30, -Hh * 1.1, L * 0.55, -Hh * 1.25, L, -Hh * 0.05)
    bp.cubicTo(L * 0.55, Hh * 1.2, -L + 30, Hh * 1.05, -L + 10, 0); bp.close()
    c.drawPath(bp, lin(c, (0, -Hh, 0, Hh), [col(mix_hx(body, '#ffffff', 0.25)), col(body), col(body), col(belly)], [0, 0.35, 0.62, 1]))
    c.save(); c.clipPath(bp, doAntiAlias=True)
    if stripes and not shark:
        for sx_ in (-55, 5):
            st = skia.Path(); st.moveTo(sx_, -Hh * 1.3); st.quadTo(sx_ + 22, 0, sx_, Hh * 1.3); st.lineTo(sx_ + 24, Hh * 1.3); st.quadTo(sx_ + 46, 0, sx_ + 24, -Hh * 1.3); st.close()
            c.drawPath(st, P(color=col(mix_hx(body, '#ff6a00', 0.45), 150)))
    if shark:
        for k in range(4):
            gx = L * 0.28 - k * 16; gp = skia.Path(); gp.moveTo(gx, -22); gp.quadTo(gx - 9, 0, gx, 22)
            c.drawPath(gp, P(color=col('#3f6488', 170), stroke=4))
    c.drawOval(skia.Rect(-L * 0.4, -Hh * 0.85, L * 0.3, -Hh * 0.45), P(color=col('#ffffff', 70), blur=8))
    c.restore()
    c.drawPath(bp, P(color=col('#000000', 45), stroke=4))
    # gill flap (fish only)
    if not shark:
        gx = L * 0.35
        if gill > 0:
            for k in range(4):
                gp = skia.Path(); gp.moveTo(gx - 6 - k * 7, -40 + k * 3); gp.quadTo(gx - 22 - k * 7, 0, gx - 6 - k * 7, 40 - k * 3)
                c.drawPath(gp, P(color=col('#e8384f', int(230 * gill)), stroke=6))
        c.save(); c.translate(gx, -48); c.rotate(-16 * gill)
        fl = skia.Path(); fl.moveTo(0, 0); fl.quadTo(-26, 48, 0, 96)
        c.drawPath(fl, P(color=col(mix_hx(body, '#7a3a10', 0.45)), stroke=7))
        c.restore()
    # eye
    ex, ey, er = L * 0.62, -Hh * 0.22, (17 if shark else 22)
    ph = (t * 0.7 + seed * 0.37) % 3.2
    if ph < 0.12:
        c.drawArc(skia.Rect(ex - er, ey - er * 0.5, ex + er, ey + er * 0.5), 10, 160, False, P(color=col('#2b1d0e'), stroke=5))
    else:
        c.drawCircle(ex, ey, er * 1.25, P(color=col('#ffffff')))
        c.drawCircle(ex + 3, ey, er * 0.85, P(color=col('#2b1d0e')))
        c.drawCircle(ex - 2, ey - er * 0.35, er * 0.32, P(color=col('#ffffff')))
        c.drawCircle(ex + er * 0.3, ey + er * 0.3, er * 0.14, P(color=col('#ffffff')))
    c.drawOval(skia.Rect(ex - 22, ey + er + 4, ex + 8, ey + er + 22), P(color=col('#ff6f8a', 150), blur=3))
    # mouth
    mx, my = L * 0.9, Hh * 0.18
    if mouth > 0.05:
        c.drawOval(skia.Rect(mx - 26 * mouth, my - 18 * mouth, mx + 6, my + 18 * mouth), P(color=col('#7a2626')))
        c.drawOval(skia.Rect(mx - 20 * mouth, my + 2, mx, my + 14 * mouth), P(color=col('#ff8a8a')))
    else:
        mp = skia.Path(); mp.moveTo(mx - 26, my - 2); mp.quadTo(mx - 12, my + 14, mx + 2, my - 4)
        c.drawPath(mp, P(color=col('#5a1f1f'), stroke=5))
    c.restore()

def caterpillar_pts(x, y, s, t, n=7, hang=0.0, crawl=True, seed=0):
    """Segment centres, tail first, head last. hang 0..1 morphs from crawling (head right) to a 'J' hanging from (x,y)."""
    sp = 46 * s; out = []
    for i in range(n):
        u = i / (n - 1)
        bump = (math.sin(t * 5 - i * 0.9 + seed) * 0.5 + 0.5) * 18 * s if crawl else 0
        cx, cy = x - (n - 1 - i) * sp + (n - 1) * sp / 2, y - bump
        # J: tail at the attach point, body goes straight down, head curls up
        k = i * sp; straight = sp * (n - 1) * 0.6
        if k <= straight: hx, hy = x, y + k
        else:
            a = (k - straight) / (sp * 1.6); R = sp * 1.6
            hx, hy = x + R - R * math.cos(a), y + straight + R * math.sin(a)
        out.append((lerp(cx, hx, hang), lerp(cy, hy, hang)))
    return out

def caterpillar(c, pts, s, t, seed=0, mood='happy', body='#7ed957', spot='#ffd23f', alpha=255, munch=0.0):
    """Draw a caterpillar from caterpillar_pts (tail first, head last)."""
    a = int(alpha); r = 34 * s
    for i, (px, py) in enumerate(pts[:-1]):
        rr = r * (0.8 + 0.2 * i / max(1, len(pts) - 2))
        c.drawLine(px - rr * 0.35, py + rr * 0.8, px - rr * 0.45, py + rr * 1.15, P(color=col('#3f8a2c', a), stroke=rr * 0.22))
        c.drawLine(px + rr * 0.35, py + rr * 0.8, px + rr * 0.45, py + rr * 1.15, P(color=col('#3f8a2c', a), stroke=rr * 0.22))
    for i, (px, py) in enumerate(pts[:-1]):
        rr = r * (0.8 + 0.2 * i / max(1, len(pts) - 2))
        c.drawCircle(px, py, rr, rad(px - rr * 0.35, py - rr * 0.45, rr * 1.6, [col('#d9ffb8', a), col(body, a), col(mix_hx(body, '#1f5a1a', 0.45), a)], [0, 0.45, 1]))
        c.drawCircle(px, py, rr, P(color=col('#2f6a22', int(a * 0.5)), stroke=max(1.5, rr * 0.07)))
        c.drawCircle(px, py - rr * 0.35, rr * 0.18, P(color=col(spot, a)))
    hx, hy = pts[-1]; px, py = pts[-2]; hr = r * 1.25
    ang = math.degrees(math.atan2(hy - py, hx - px))
    for sx in (-1, 1):
        c.save(); c.translate(hx, hy); c.rotate(ang + 35)
        ap = skia.Path(); ap.moveTo(sx * hr * 0.35, -hr * 0.8); ap.quadTo(sx * hr * 0.5, -hr * 1.5, sx * hr * 0.85, -hr * 1.6 + math.sin(t * 4 + sx) * 4)
        c.drawPath(ap, P(color=col('#2f6a22', a), stroke=hr * 0.09))
        c.drawCircle(sx * hr * 0.85, -hr * 1.6 + math.sin(t * 4 + sx) * 4, hr * 0.14, P(color=col('#ff6b6b', a)))
        c.restore()
    c.drawCircle(hx, hy, hr, rad(hx - hr * 0.35, hy - hr * 0.45, hr * 1.6, [col('#e6ffc9', a), col(body, a), col(mix_hx(body, '#1f5a1a', 0.4), a)], [0, 0.45, 1]))
    c.drawCircle(hx, hy, hr, P(color=col('#2f6a22', int(a * 0.5)), stroke=max(1.5, hr * 0.06)))
    if a > 200:
        face(c, hx, hy + hr * 0.05, hr * 0.85, t, seed, 'wow' if munch > 0.5 else mood)

def chrysalis_path(x, y, s):
    """Hanging teardrop, attach point at x,y (top)."""
    p = skia.Path(); p.moveTo(x, y + 40 * s)
    p.cubicTo(x + 95 * s, y + 70 * s, x + 105 * s, y + 230 * s, x + 30 * s, y + 330 * s)
    p.quadTo(x, y + 360 * s, x - 30 * s, y + 330 * s)
    p.cubicTo(x - 105 * s, y + 230 * s, x - 95 * s, y + 70 * s, x, y + 40 * s); p.close()
    return p

def chrysalis(c, x, y, s, t, seed=0, shake=0.0, alpha=255, clear=0.0, face_on=True, mood='happy'):
    """Green hanging chrysalis with gold dots; attach point (x,y). clear 0..1 makes it see-through (just before hatching)."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(math.sin(t * 9) * 6 * shake + math.sin(t * 1.3 + seed) * 2); c.translate(-x, -y)
    c.drawLine(x, y - 10, x, y + 45 * s, P(color=col('#6b4423', a), stroke=8 * s))
    p = chrysalis_path(x, y, s)
    g1 = mix_hx('#9ef07a', '#ffcf8a', clear); g2 = mix_hx('#3fae4a', '#ff8a3d', clear)
    c.drawPath(p, rad(x - 30 * s, y + 140 * s, 260 * s, [col('#e6ffd0', a), col(g1, a), col(g2, a)], [0, 0.35, 1]))
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawLine(x - 90 * s, y + 120 * s, x + 90 * s, y + 120 * s, P(color=col('#2f8a3a', int(a * 0.45)), stroke=6 * s))
    for k in range(-2, 3):
        c.drawCircle(x + k * 26 * s, y + 120 * s, 7 * s, P(color=col('#ffd23f', a)))
    c.drawOval(skia.Rect(x - 70 * s, y + 140 * s, x - 35 * s, y + 280 * s), P(color=col('#ffffff', int(a * 0.35)), blur=8 * s))
    c.restore()
    c.drawPath(p, P(color=col('#2f7a33', int(a * 0.6)), stroke=4 * s))
    if face_on and a > 200: face(c, x, y + 215 * s, 62 * s, t, seed, mood)
    c.restore()

BUTTERFLY_WINGS = ('#ff9f1c', '#ffd23f', '#3a2a1a')

def butterfly(c, x, y, s, t, flap=None, seed=0, colors=BUTTERFLY_WINGS, unfold=1.0, face_on=True, mood='happy', rot=0.0, alpha=255):
    """Front-view butterfly, x,y = body centre. flap = 0..1 wing opening (None = auto flapping). unfold 0..1: crumpled -> full wings."""
    a = int(alpha)
    if flap is None: flap = 0.72 + 0.28 * math.cos(t * 9 + seed)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    wc, wl, edge = colors
    ws = 0.35 + 0.65 * unfold
    for sx in (-1, 1):
        c.save(); c.scale(sx * max(0.08, flap) * ws, ws)
        up = skia.Path(); up.moveTo(8, -12); up.cubicTo(60, -150, 200, -170, 205, -95); up.cubicTo(210, -30, 120, 5, 8, 8); up.close()
        lo = skia.Path(); lo.moveTo(8, 4); lo.cubicTo(110, 10, 170, 70, 140, 140); lo.cubicTo(110, 190, 30, 140, 8, 40); lo.close()
        for wp, cx_, cy_, rr in ((lo, 70, 70, 140), (up, 110, -80, 170)):
            c.drawPath(wp, rad(cx_ - 50, cy_ - 30, rr, [col(wl, a), col(wc, a)]))
            c.save(); c.clipPath(wp, doAntiAlias=True)
            c.drawPath(wp, P(color=col(edge, a), stroke=34))
            c.restore()
            c.drawPath(wp, P(color=col(edge, a), stroke=5))
        for dx, dy, rr in ((180, -110, 9), (192, -80, 7), (170, -138, 7), (130, 140, 8), (100, 160, 6)):
            c.drawCircle(dx, dy, rr, P(color=col('#ffffff', a)))
        c.drawCircle(110, -70, 22, P(color=col('#ffffff', int(a * 0.35))))
        c.restore()
    bd = skia.Rect(-16, -60, 16, 110)
    c.drawRoundRect(bd, 16, 16, lin(c, (-16, 0, 16, 0), [col('#5a4030', a), col('#2b1d14', a)], vertical=False))
    for k in range(4): c.drawLine(-12, 10 + k * 22, 12, 10 + k * 22, P(color=col('#7a5a40', a), stroke=3))
    for sx in (-1, 1):
        ap = skia.Path(); ap.moveTo(sx * 10, -95); ap.quadTo(sx * 30, -160, sx * 60, -175 + math.sin(t * 3 + sx) * 4)
        c.drawPath(ap, P(color=col('#2b1d14', a), stroke=5))
        c.drawCircle(sx * 60, -175 + math.sin(t * 3 + sx) * 4, 10, P(color=col('#2b1d14', a)))
    c.drawCircle(0, -85, 40, rad(-12, -100, 60, [col('#7a5a40', a), col('#3a2a1a', a)]))
    if face_on and a > 200: face(c, 0, -82, 38, t, seed, mood)
    c.restore()

def egg(c, x, y, r, t, crack=0.0, alpha=255):
    a = int(alpha)
    p = skia.Path(); p.addOval(skia.Rect(x - r * 0.8, y - r, x + r * 0.8, y + r))
    c.drawPath(p, rad(x - r * 0.3, y - r * 0.4, r * 1.6, [col('#ffffff', a), col('#fff3c9', a), col('#e9d48a', a)], [0, 0.5, 1]))
    c.drawPath(p, P(color=col('#c9b060', a), stroke=max(1.5, r * 0.06)))
    for k in range(5): c.drawLine(x - r * 0.4 + k * r * 0.2, y - r * 0.9, x - r * 0.45 + k * r * 0.22, y + r * 0.85, P(color=col('#d8c27a', int(a * 0.5)), stroke=max(1, r * 0.04)))
    if crack > 0:
        cp = skia.Path(); n = 6
        for k in range(n + 1):
            xx = x - r * 0.75 + k * r * 1.5 / n; yy = y - r * 0.2 + (r * 0.18 if k % 2 else -r * 0.1)
            (cp.moveTo if k == 0 else cp.lineTo)(xx, yy)
        c.save(); c.clipRect(skia.Rect(x - r, y - r * 1.2, x - r + 2 * r * crack, y + r))
        c.drawPath(cp, P(color=col('#7a5a20', a), stroke=max(2, r * 0.08))); c.restore()

def magnifier(c, cx, cy, r, inner, t=0.0, alpha=255):
    """Round zoom lens: inner(c) draws the zoomed world, clipped to the circle."""
    c.save(); clip = skia.Path(); clip.addCircle(cx, cy, r); c.clipPath(clip, doAntiAlias=True)
    inner(c)
    c.restore()
    c.drawCircle(cx, cy, r, P(color=col('#ffffff', alpha), stroke=26))
    c.drawCircle(cx, cy, r + 14, P(color=col('#3a5fa8', alpha), stroke=6))
    c.drawArc(skia.Rect(cx - r + 40, cy - r + 40, cx + r - 40, cy + r - 40), 200, 50, False, P(color=col('#ffffff', 120), stroke=16))

def oxygen_dot(c, x, y, r, t, seed=0, alpha=255, face_on=False, hexcol='#5ff0ff'):
    """Small glowing oxygen bit."""
    a = int(alpha)
    c.drawCircle(x, y, r * 2.0, rad(x, y, r * 2.0, [col(hexcol, int(a * 0.55)), col(hexcol, 0)]))
    c.drawCircle(x, y, r, rad(x - r * 0.35, y - r * 0.4, r * 1.6, [col('#ffffff', a), col(hexcol, a), col(mix_hx(hexcol, '#0a6a9a', 0.35), a)], [0, 0.4, 1]))
    if face_on and a > 200: face(c, x, y + r * 0.08, r * 0.9, t, seed)

# ---------------- Stars, volcanoes, Sun core (added for ep_014+) ----------------
def star_path(r, inner=0.48, n=5):
    p = skia.Path()
    for k in range(2 * n):
        ang = -math.pi / 2 + k * math.pi / n; rr = r if k % 2 == 0 else r * inner
        (p.moveTo if k == 0 else p.lineTo)(math.cos(ang) * rr, math.sin(ang) * rr)
    p.close(); return p

def star_char(c, x, y, r, t, seed=0, mood='happy', face_on=True, bright=1.0, rot=0.0, alpha=255, glow=True,
              body=('#fffbd6', '#ffe14d', '#ffb627'), edge='#f08c00'):
    """Cute rounded 5-point star with a face. bright scales the glow (use for twinkling)."""
    a = int(alpha)
    if glow:
        gr = r * (1.6 + 0.9 * bright)
        c.drawCircle(x, y, gr, rad(x, y, gr, [col('#fff6b0', int(a * 0.55 * clamp(bright, 0, 1.5) / 1.5 + a * 0.15)), col('#fff6b0', 0)]))
    c.save(); c.translate(x, y); c.rotate(rot)
    pth = star_path(r)
    fill = rad(-r * 0.25, -r * 0.35, r * 1.3, [col(body[0], a), col(body[1], a), col(body[2], a)], [0, 0.5, 1])
    fill.setPathEffect(skia.CornerPathEffect.Make(r * 0.22))
    c.drawPath(pth, fill)
    st = P(color=col(edge, int(a * 0.8)), stroke=r * 0.05); st.setPathEffect(skia.CornerPathEffect.Make(r * 0.22))
    c.drawPath(pth, st)
    c.drawOval(skia.Rect(-r * 0.32, -r * 0.62, -r * 0.08, -r * 0.3), P(color=col('#ffffff', int(a * 0.55)), blur=r * 0.05))
    c.restore()
    if face_on and a > 200:
        face(c, x, y + r * 0.08, r * 0.52, t, seed, mood)

def twinkle(c, x, y, r, colr='#ffffff', alpha=255, rot=0.0):
    """4-point sparkle (a 'twinkle' glint)."""
    a = int(alpha)
    c.drawCircle(x, y, r * 0.9, rad(x, y, r * 0.9, [col(colr, int(a * 0.6)), col(colr, 0)]))
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); w = r * 0.16
    p.moveTo(0, -r); p.quadTo(w, -w, r, 0); p.quadTo(w, w, 0, r); p.quadTo(-w, w, -r, 0); p.quadTo(-w, -w, 0, -r); p.close()
    c.drawPath(p, P(color=col(colr, a)))
    c.restore()
    c.drawCircle(x, y, r * 0.14, P(color=col('#ffffff', a)))

def night_sky(c, t, seed=21, n=90, y1=1450):
    sky(c, '#0b1036', '#3b3f8f', mid='#1a1f5c'); stars(c, t, seed, n, y1=y1)

def puff(c, x, y, r, alpha=200, colr='#e9e4f2', shade='#b9b0cc'):
    """Soft round smoke/steam puff."""
    a = int(alpha)
    for dx, dy, k in [(-0.55, 0.15, 0.62), (0.55, 0.12, 0.66), (0.0, -0.2, 0.8), (-0.2, 0.3, 0.6), (0.3, 0.3, 0.6)]:
        c.drawCircle(x + dx * r, y + (dy + 0.08) * r, k * r, P(color=col(shade, int(a * 0.6))))
    for dx, dy, k in [(-0.55, 0.15, 0.62), (0.55, 0.12, 0.66), (0.0, -0.2, 0.8), (-0.2, 0.3, 0.6), (0.3, 0.3, 0.6)]:
        c.drawCircle(x + dx * r, y + dy * r, k * r, P(color=col(colr, a)))
    c.drawCircle(x - r * 0.15, y - r * 0.35, r * 0.32, P(color=col('#ffffff', int(a * 0.6)), blur=r * 0.08))

def volcano_path(x, y, s, crater=1.0):
    """Cone with a dip at the top. x,y = middle of the base."""
    hw, h, cw = 470 * s, 560 * s, 120 * s * crater
    p = skia.Path(); p.moveTo(x - hw, y)
    p.cubicTo(x - hw * 0.62, y - h * 0.25, x - cw * 1.4, y - h * 0.82, x - cw, y - h)
    p.quadTo(x, y - h + 38 * s, x + cw, y - h)
    p.cubicTo(x + cw * 1.4, y - h * 0.82, x + hw * 0.62, y - h * 0.25, x + hw, y)
    p.close(); return p

def volcano(c, x, y, s, t, face_on=True, mood='happy', glow=0.4, lava_drips=0.0, snow=False, seed=0,
            rock=('#b7774e', '#8a5236', '#5e3424')):
    """Friendly volcano. glow = crater glow 0..1, lava_drips = 0..1 length of lava streams down the sides."""
    h = 560 * s; cw = 120 * s
    c.drawOval(skia.Rect(x - 520 * s, y - 25 * s, x + 520 * s, y + 25 * s), P(color=col('#000000', 45), blur=12 * s))
    pth = volcano_path(x, y, s)
    c.drawPath(pth, lin(c, (0, y - h, 0, y), [col(rock[0]), col(rock[1]), col(rock[2])], pos=[0, 0.55, 1]))
    c.save(); c.clipPath(pth, doAntiAlias=True)
    # side shading + ridges
    c.drawRect(skia.Rect(x + 40 * s, y - h, x + 600 * s, y), lin(c, (x + 40 * s, 0, x + 520 * s, 0), [col('#3a1c10', 0), col('#3a1c10', 70)], vertical=False))
    for k, (dx, ln) in enumerate([(-250, 0.55), (-110, 0.75), (60, 0.7), (230, 0.5)]):
        rp = skia.Path(); x0 = x + dx * s * 0.35; rp.moveTo(x0, y - h * 0.86)
        rp.quadTo(x + dx * s * 0.8, y - h * 0.5, x + dx * s * 1.3, y - h * (0.86 - ln))
        c.drawPath(rp, P(color=col('#4a2616', 60), stroke=9 * s))
    if snow:
        sp = skia.Path(); sp.moveTo(x - 260 * s, y - h * 0.55)
        for k in range(7):
            sp.quadTo(x - 260 * s + (k + 0.5) * 520 * s / 7, y - h * (0.47 if k % 2 else 0.6), x - 260 * s + (k + 1) * 520 * s / 7, y - h * 0.55)
        sp.lineTo(x + 300 * s, y - h - 50 * s); sp.lineTo(x - 300 * s, y - h - 50 * s); sp.close()
        c.drawPath(sp, P(color=col('#ffffff', 235)))
    if lava_drips > 0:
        for k, (dx, ln, w) in enumerate([(-95, 0.55, 30), (95, 0.72, 36), (-55, 0.28, 26)]):
            L = h * ln * ease_out(clamp(lava_drips * (1.2 - k * 0.1)))
            lp = skia.Path(); x0 = x + dx * s; y0 = y - h + 10 * s
            lp.moveTo(x0, y0)
            for q in range(1, 9):
                u = q / 8; yy = y0 + L * u; xx = x0 + dx * s * 1.6 * u + math.sin(u * 7 + k) * 14 * s
                lp.lineTo(xx, yy)
            p_ = P(stroke=w * s); p_.setShader(skia.GradientShader.MakeLinear(points=[(0, y0), (0, y0 + max(L, 1))], colors=[col('#ffe14d'), col('#ff7a1a'), col('#e8382f')]))
            c.drawPath(lp, p_)
            c.drawCircle(xx, yy, w * s * 0.62, P(color=col('#e8382f')))
    c.restore()
    # crater
    c.drawOval(skia.Rect(x - cw, y - h - 18 * s, x + cw, y - h + 26 * s), P(color=col('#4a2616')))
    if glow > 0:
        c.drawOval(skia.Rect(x - cw * 0.85, y - h - 10 * s, x + cw * 0.85, y - h + 22 * s), rad(x, y - h + 6 * s, cw, [col('#fff3a0', int(255 * glow)), col('#ff8a1a', int(230 * glow)), col('#e8382f', int(120 * glow))]))
        c.drawCircle(x, y - h, cw * 2.2, rad(x, y - h, cw * 2.2, [col('#ff9f1c', int(110 * glow)), col('#ff9f1c', 0)]))
    c.drawPath(pth, P(color=col('#3a1c10', 90), stroke=5 * s))
    if face_on:
        face(c, x, y - h * 0.42, 150 * s, t, seed, mood)

def magma_blob(c, x, y, r, t, seed=0, face_on=True, mood='happy', alpha=255, cool=0.0):
    """Wobbly glowing blob of magma/lava. cool 0..1 turns it into dark rock."""
    a = int(alpha)
    if cool < 1:
        c.drawCircle(x, y, r * 1.8, rad(x, y, r * 1.8, [col('#ff8a1a', int(a * 0.45 * (1 - cool))), col('#ff8a1a', 0)]))
    p = skia.Path()
    for k in range(25):
        ang = k / 24 * 2 * math.pi
        rr = r * (1 + 0.07 * math.sin(ang * 3 + t * 3 + seed) + 0.04 * math.sin(ang * 5 - t * 2 + seed * 2))
        (p.moveTo if k == 0 else p.lineTo)(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
    p.close()
    hot = rad(x - r * 0.3, y - r * 0.35, r * 1.5, [col(mix_hx('#fff3a0', '#8a8f9c', cool), a), col(mix_hx('#ff9f1c', '#5b5f6b', cool), a), col(mix_hx('#e8382f', '#3b3e47', cool), a)], [0, 0.45, 1])
    hot.setPathEffect(skia.CornerPathEffect.Make(r * 0.3))
    c.drawPath(p, hot)
    if cool > 0.5:
        for k in range(4):
            ang = k * 1.7 + seed
            c.drawCircle(x + math.cos(ang) * r * 0.55, y + math.sin(ang) * r * 0.5, r * 0.09, P(color=col('#2a2c33', int(a * (cool - 0.5) * 2))))
    if face_on and a > 200:
        face(c, x, y + r * 0.06, r * 0.82, t, seed, mood)

# ---------------- Flight, ships, plants (added for ep_017+) ----------------
def airplane(c, x, y, s=1.0, rot=0.0, t=0.0, body='#ffffff', accent='#ff5c85', wing='#2f9bff', alpha=255, flame=False):
    """Side-view jet airliner, nose pointing right. x,y = centre, s=1 -> ~520 px long. rot in degrees (positive = nose down)."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    # far wing (behind fuselage)
    fw = skia.Path(); fw.moveTo(30, -10); fw.lineTo(-70, -95); fw.lineTo(-40, -95); fw.lineTo(90, -10); fw.close()
    c.drawPath(fw, P(color=mix_hex(wing, '#1b2a4a', 0.35, a)))
    # tail fin
    tf = skia.Path(); tf.moveTo(-200, -20); tf.lineTo(-262, -150); tf.lineTo(-222, -150); tf.lineTo(-140, -22); tf.close()
    c.drawPath(tf, lin(c, (0, -150, 0, -20), [col(accent, a), col(mix_hx(accent, '#b8183f', 0.5), a)]))
    # fuselage
    fu = skia.Path(); fu.moveTo(-250, -18)
    fu.cubicTo(-120, -40, 150, -42, 215, -30); fu.cubicTo(262, -22, 272, 6, 250, 18)
    fu.cubicTo(200, 34, -100, 34, -200, 18); fu.lineTo(-262, -6); fu.close()
    c.drawPath(fu, lin(c, (0, -42, 0, 34), [col(body, a), col('#dfe8f5', a)]))
    c.drawPath(fu, P(color=col('#1b2a4a', int(a * 0.25)), stroke=3))
    # cheat line + windows
    c.drawRect(skia.Rect(-210, 8, 230, 14), P(color=col(accent, int(a * 0.9))))
    for i in range(16):
        wx = -170 + i * 22
        c.drawRoundRect(skia.Rect(wx, -14, wx + 11, -2), 4, 4, P(color=col('#1b2a4a', int(a * 0.8))))
    cp = skia.Path(); cp.moveTo(218, -24); cp.quadTo(240, -22, 250, -10); cp.lineTo(222, -10); cp.close()
    c.drawPath(cp, P(color=col('#1b2a4a', a)))
    # tailplane
    tp = skia.Path(); tp.moveTo(-190, -4); tp.lineTo(-270, 12); tp.lineTo(-240, 14); tp.lineTo(-160, 4); tp.close()
    c.drawPath(tp, P(color=col(mix_hx(wing, '#1b2a4a', 0.2), a)))
    # near wing
    nw = skia.Path(); nw.moveTo(40, 8); nw.lineTo(-90, 120); nw.lineTo(-50, 122); nw.lineTo(105, 12); nw.close()
    c.drawPath(nw, lin(c, (0, 8, 0, 122), [col(wing, a), col(mix_hx(wing, '#1b2a4a', 0.3), a)]))
    # engine under near wing
    c.drawRoundRect(skia.Rect(-20, 40, 60, 70), 15, 15, lin(c, (0, 40, 0, 70), [col('#e9eef6', a), col('#b8c4d6', a)]))
    c.drawOval(skia.Rect(52, 41, 66, 69), P(color=col('#1b2a4a', a)))
    if flame:
        fl = 0.7 + 0.3 * math.sin(t * 40)
        c.drawOval(skia.Rect(-20 - 60 * fl, 46, -14, 64), rad(-20, 55, 60, [col('#fff3a0', int(a * 0.8)), col('#ffffff', 0)]))
    c.restore()

def airfoil_path(cx, cy, chord, thick=0.13, camber=0.06):
    """Cambered wing cross-section centred on (cx,cy), leading edge on the left."""
    n = 40; up = []; lo = []
    for i in range(n + 1):
        u = (1 - math.cos(math.pi * i / n)) / 2
        yt = 5 * thick * (0.2969 * math.sqrt(u) - 0.126 * u - 0.3516 * u * u + 0.2843 * u ** 3 - 0.1036 * u ** 4)
        yc = camber * (2 * 0.4 * u - u * u) / 0.16 if u < 0.4 else camber * ((1 - 0.8) + 0.8 * u - u * u) / 0.36
        x = cx + (u - 0.5) * chord
        up.append((x, cy - (yc + yt) * chord)); lo.append((x, cy - (yc - yt) * chord))
    p = skia.Path(); p.moveTo(*up[0])
    for q in up[1:]: p.lineTo(*q)
    for q in reversed(lo): p.lineTo(*q)
    p.close()
    return p

def draw_airfoil(c, cx, cy, chord, aoa=6.0, colr='#ffffff', alpha=255):
    c.save(); c.translate(cx, cy); c.rotate(aoa); c.translate(-cx, -cy)
    p = airfoil_path(cx, cy, chord)
    c.drawPath(p, P(color=col('#0b1a3a', int(alpha * 0.25)), blur=10))
    c.drawPath(p, lin(c, (0, cy - chord * 0.15, 0, cy + chord * 0.08), [col(colr, alpha), col('#c9d6ea', alpha)]))
    c.drawPath(p, P(color=col('#1b2a4a', int(alpha * 0.7)), stroke=5))
    c.restore()

def arrow(c, x0, y0, x1, y1, colr='#ffffff', w=16, alpha=255, head=1.0):
    """Straight arrow with rounded shaft and a solid head."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1: return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L; hl = w * 2.4 * head; hw = w * 1.7 * head
    bx, by = x1 - ux * hl, y1 - uy * hl
    c.drawLine(x0, y0, bx + ux * 2, by + uy * 2, P(color=col(colr, alpha), stroke=w))
    p = skia.Path(); p.moveTo(x1, y1); p.lineTo(bx - uy * hw, by + ux * hw); p.lineTo(bx + uy * hw, by - ux * hw); p.close()
    c.drawPath(p, P(color=col(colr, alpha)))

def label_pill(c, text, x, y, size=54, fill='#1b2a4a', bg='#ffffff', k=1.0, alpha=240, hi=None):
    """White rounded label (used for on-stage annotations)."""
    if k <= 0: return
    w_ = font(size).measureText(text) / 2 + size * 0.6
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawRoundRect(skia.Rect(-w_, -size * 0.8, w_, size * 0.8), size * 0.8, size * 0.8, P(color=col('#0b1a3a', int(50 * alpha / 240)), blur=8))
    c.drawRoundRect(skia.Rect(-w_, -size * 0.8, w_, size * 0.8), size * 0.8, size * 0.8, P(color=col(bg, alpha)))
    text_block(c, text, 0, 0, size=size, fill=fill, hi=hi or fill, stroke=bg, maxw=2000, alpha=min(255, int(alpha * 255 / 240)))
    c.restore()

def water_body(c, y, t, x0=0, x1=W, y1=H, c1='#4fb3ff', c2='#1a5fc9', amp=10, a=255):
    """Water surface with gentle waves from x0..x1, filled down to y1."""
    p = skia.Path(); p.moveTo(x0, y1); p.lineTo(x0, y)
    steps = 48
    for i in range(steps + 1):
        x = lerp(x0, x1, i / steps)
        p.lineTo(x, y + math.sin(x * 0.012 + t * 2.0) * amp + math.sin(x * 0.031 - t * 1.3) * amp * 0.4)
    p.lineTo(x1, y1); p.close()
    c.drawPath(p, lin(c, (0, y - amp, 0, y1), [col(c1, a), col(c2, a)]))
    hl = skia.Path(); first = True
    for i in range(steps + 1):
        x = lerp(x0, x1, i / steps); yy = y + math.sin(x * 0.012 + t * 2.0) * amp + math.sin(x * 0.031 - t * 1.3) * amp * 0.4
        (hl.moveTo if first else hl.lineTo)(x, yy); first = False
    c.drawPath(hl, P(color=col('#ffffff', int(a * 0.7)), stroke=6))

def water_level(x, y, t, amp=10):
    return y + math.sin(x * 0.012 + t * 2.0) * amp + math.sin(x * 0.031 - t * 1.3) * amp * 0.4

def tank(c, x0, y0, x1, y1, level, t, water=True, front=False):
    """Glass tank. Call with front=False before contents (back + water), front=True after (glass rim)."""
    if not front:
        c.drawRoundRect(skia.Rect(x0, y0, x1, y1), 26, 26, P(color=col('#ffffff', 60)))
        if water:
            c.save(); cl = skia.Path(); cl.addRoundRect(skia.Rect(x0 + 6, y0, x1 - 6, y1 - 6), 22, 22); c.clipPath(cl, doAntiAlias=True)
            water_body(c, level, t, x0, x1, y1, amp=6, a=215)
            c.restore()
    else:
        c.drawRoundRect(skia.Rect(x0, y0, x1, y1), 26, 26, P(color=col('#ffffff', 230), stroke=10))
        c.drawLine(x0 + 30, y0 + 40, x0 + 30, y1 - 60, P(color=col('#ffffff', 110), stroke=10))

def steel_block(c, x, y, w_, h_, rot=0.0, alpha=255):
    c.save(); c.translate(x, y); c.rotate(rot)
    r = skia.Rect(-w_ / 2, -h_ / 2, w_ / 2, h_ / 2)
    c.drawRoundRect(r, 14, 14, lin(c, (0, -h_ / 2, 0, h_ / 2), [col('#c9d3df', alpha), col('#7d8a9c', alpha)]))
    c.drawRoundRect(r, 14, 14, P(color=col('#4a566a', alpha), stroke=5))
    c.drawLine(-w_ / 2 + 18, -h_ / 2 + 16, w_ / 2 - 30, -h_ / 2 + 16, P(color=col('#ffffff', int(alpha * 0.6)), stroke=6))
    c.restore()

def steel_bowl(c, x, y, w_, h_, rot=0.0, alpha=255, fill=0.0, t=0.0):
    """Open steel bowl / hull cross-section; x,y = centre of the rim line. fill 0..1 = water inside."""
    c.save(); c.translate(x, y); c.rotate(rot)
    outer = skia.Path(); outer.moveTo(-w_ / 2, 0); outer.cubicTo(-w_ / 2, h_ * 1.25, w_ / 2, h_ * 1.25, w_ / 2, 0); outer.close()
    th = 16
    inner = skia.Path(); inner.moveTo(-w_ / 2 + th, 0); inner.cubicTo(-w_ / 2 + th, h_ * 1.25 - th * 1.6, w_ / 2 - th, h_ * 1.25 - th * 1.6, w_ / 2 - th, 0); inner.close()
    c.drawPath(outer, lin(c, (0, 0, 0, h_), [col('#c9d3df', alpha), col('#7d8a9c', alpha)]))
    c.drawPath(inner, P(color=col('#eaf6ff', int(alpha * 0.85))))
    if fill > 0:
        c.save(); c.clipPath(inner, doAntiAlias=True)
        top = lerp(h_ * 0.95, 0, fill)
        c.drawRect(skia.Rect(-w_, top, w_, h_ * 2), lin(c, (0, top, 0, h_), [col('#4fb3ff', alpha), col('#1a5fc9', alpha)]))
        c.restore()
    c.drawPath(outer, P(color=col('#4a566a', alpha), stroke=5))
    c.drawLine(-w_ / 2 - 6, 0, -w_ / 2 + th + 4, 0, P(color=col('#4a566a', alpha), stroke=10))
    c.drawLine(w_ / 2 - th - 4, 0, w_ / 2 + 6, 0, P(color=col('#4a566a', alpha), stroke=10))
    c.restore()

def ship(c, x, y, s=1.0, t=0.0, kind='cargo', rock=True, alpha=255, marks=False):
    """Side-view ship. x,y = waterline centre at s=1 (hull draft ~70 px below). kind 'cargo' | 'carrier'."""
    a = int(alpha); ang = math.sin(t * 1.3) * 1.2 if rock else 0
    c.save(); c.translate(x, y + (math.sin(t * 1.7) * 4 if rock else 0)); c.rotate(ang); c.scale(s, s)
    hull = skia.Path(); hull.moveTo(-330, -70); hull.lineTo(330, -70); hull.lineTo(360, -110)
    hull.lineTo(375, -110); hull.cubicTo(360, 20, 300, 70, 250, 70); hull.lineTo(-290, 70); hull.cubicTo(-320, 70, -335, 30, -340, -70); hull.close()
    c.drawPath(hull, lin(c, (0, -110, 0, 70), [col('#1b2a4a', a), col('#0f1830', a)]))
    # red underside below waterline
    c.save(); c.clipPath(hull, doAntiAlias=True)
    c.drawRect(skia.Rect(-400, 0, 400, 100), P(color=col('#e8394f', a)))
    c.drawRect(skia.Rect(-400, -8, 400, 0), P(color=col('#ffffff', a)))
    c.restore()
    if marks:
        mx = -150
        c.drawCircle(mx, -26, 24, P(color=col('#ffffff', a), stroke=5)); c.drawLine(mx - 34, -26, mx + 34, -26, P(color=col('#ffffff', a), stroke=5))
        for j, (dy, lab) in enumerate([(-50, 'F'), (-34, 'T'), (-18, 'S')]):
            c.drawLine(mx + 60, dy, mx + 110, dy, P(color=col('#ffffff', a), stroke=5))
    if kind == 'carrier':
        deck = skia.Path(); deck.moveTo(-360, -70); deck.lineTo(380, -70); deck.lineTo(380, -92); deck.lineTo(-380, -92); deck.close()
        c.drawPath(deck, P(color=col('#5b6b82', a)))
        c.drawLine(-320, -81, 340, -81, P(color=col('#ffffff', int(a * 0.6)), stroke=3))
        c.drawRoundRect(skia.Rect(80, -190, 170, -92), 10, 10, lin(c, (0, -190, 0, -92), [col('#c9d3df', a), col('#8a97aa', a)]))
        c.drawRect(skia.Rect(118, -235, 128, -190), P(color=col('#8a97aa', a)))
        for i in range(3): c.drawRect(skia.Rect(92 + i * 26, -170, 108 + i * 26, -158), P(color=col('#1b2a4a', a)))
    else:
        # containers
        cols_ = ['#ff5c85', '#ffd23f', '#2f9bff', '#ffffff', '#ff9f1c', '#2f9bff', '#ff5c85', '#ffd23f']
        for i in range(8):
            for j in range(2 if i % 3 else 3):
                bx = -300 + i * 62; by = -70 - (j + 1) * 38
                c.drawRoundRect(skia.Rect(bx, by, bx + 58, by + 35), 4, 4, P(color=col(cols_[(i + j * 3) % 8], a)))
                for k in range(4): c.drawLine(bx + 10 + k * 12, by + 6, bx + 10 + k * 12, by + 29, P(color=col('#000000', int(a * 0.15)), stroke=3))
        c.drawRoundRect(skia.Rect(210, -200, 300, -70), 10, 10, lin(c, (0, -200, 0, -70), [col('#ffffff', a), col('#dfe8f5', a)]))
        for i in range(3): c.drawRect(skia.Rect(222 + i * 26, -185, 238 + i * 26, -172), P(color=col('#1b2a4a', a)))
        c.drawRect(skia.Rect(230, -235, 262, -200), P(color=col('#ff5c85', a)))
    c.restore()

def grass_blade_path(x, y, h, w_, bend):
    p = skia.Path(); p.moveTo(x - w_ / 2, y)
    p.quadTo(x - w_ * 0.3 + bend * 0.5, y - h * 0.55, x + bend, y - h)
    p.quadTo(x + w_ * 0.35 + bend * 0.5, y - h * 0.5, x + w_ / 2, y); p.close()
    return p

def grass_field(c, y, t, seed=3, n=70, hmin=120, hmax=260, x0=-20, x1=W + 20, dark=False, wind=1.0):
    """Row of swaying grass blades standing on y."""
    rnd = random.Random(seed)
    greens = [('#7ed957', '#3f9a2e'), ('#5fc94a', '#2f7d24'), ('#9be36a', '#4fa83a')]
    if dark: greens = [('#4fa83a', '#25601c'), ('#3f9a2e', '#1f5016')]
    blades = []
    for i in range(n):
        blades.append((rnd.uniform(x0, x1), rnd.uniform(hmin, hmax), rnd.uniform(18, 30), rnd.random() * 6, rnd.choice(greens), rnd.uniform(-30, 30)))
    blades.sort(key=lambda b: b[1])
    for (bx, h, w_, ph, (g1, g2), lean) in blades:
        bend = lean + math.sin(t * 1.6 + ph + bx * 0.004) * 22 * wind
        p = grass_blade_path(bx, y + 4, h, w_, bend)
        c.drawPath(p, lin(c, (0, y - h, 0, y), [col(g1), col(g2)]))
    c.drawRect(skia.Rect(x0, y, x1, H), lin(c, (0, y, 0, H), [col('#3f9a2e'), col('#2a6b1f')]))

# ---------------- Plants, onions, skin (added for ep_020+) ----------------
def co2_molecule(c, x, y, r, t, seed=0, alpha=255, rot=0.0):
    """CO2: dark grey carbon in the middle, two red oxygens in a straight line (no face)."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot + math.sin(t * 2 + seed) * 8)
    for sx in (-1, 1):
        ox = sx * r * 1.15
        c.drawCircle(ox, 0, r * 0.78, rad(ox - r * 0.25, -r * 0.3, r * 1.2, [col('#ffd0d0', a), col('#ff5a5a', a), col('#c92a2a', a)], [0, 0.45, 1]))
        c.drawCircle(ox, 0, r * 0.78, P(color=col('#9b1c1c', a), stroke=max(1.5, r * 0.07)))
    c.drawCircle(0, 0, r * 0.82, rad(-r * 0.25, -r * 0.3, r * 1.3, [col('#c9ced8', a), col('#5b6476', a), col('#2c3240', a)], [0, 0.45, 1]))
    c.drawCircle(0, 0, r * 0.82, P(color=col('#1d222c', a), stroke=max(1.5, r * 0.07)))
    c.restore()

def sugar_cubes(c, x, y, s, t=0.0, alpha=255, rot=0.0):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s); c.rotate(rot)
    for dx, dy in ((-40, 20), (40, 20), (0, -40)):
        c.drawRoundRect(skia.Rect(dx - 40, dy - 38, dx + 40, dy + 42), 10, 10, P(color=col('#0b1a3a', int(a * 0.18)), blur=5))
        c.drawRoundRect(skia.Rect(dx - 40, dy - 40, dx + 40, dy + 40), 10, 10, lin(c, (0, dy - 40, 0, dy + 40), [col('#ffffff', a), col('#e9eef5', a)]))
        c.drawRoundRect(skia.Rect(dx - 40, dy - 40, dx + 40, dy + 40), 10, 10, P(color=col('#b9c4d3', a), stroke=4))
        for k in range(5):
            rr = random.Random(k + dx * 7 + dy)
            c.drawCircle(dx + rr.uniform(-28, 28), dy + rr.uniform(-28, 28), 3, P(color=col('#d3dbe6', a)))
    c.restore()

def soil(c, y, t=0.0, x0=0, x1=W, y1=H, seed=4):
    """Brown soil cross-section with pebbles from y down."""
    c.drawRect(skia.Rect(x0, y, x1, y1), lin(c, (0, y, 0, y1), [col('#8a5a35'), col('#5e3a20')]))
    c.drawRect(skia.Rect(x0, y - 6, x1, y + 14), P(color=col('#6b4423')))
    rnd = random.Random(seed)
    for i in range(int((x1 - x0) * (y1 - y) / 9000)):
        px, py = rnd.uniform(x0, x1), rnd.uniform(y + 30, y1); r = rnd.uniform(5, 16)
        c.drawOval(skia.Rect(px - r * 1.3, py - r, px + r * 1.3, py + r), P(color=col(rnd.choice(['#a5774f', '#734a2b', '#9a6a44']))))

def root_paths(x, y, s=1.0, seed=2):
    rnd = random.Random(seed); out = []
    for i in range(7):
        ang = math.radians(-60 + i * 20 + rnd.uniform(-6, 6)); L = s * rnd.uniform(180, 300)
        p = skia.Path(); p.moveTo(x, y)
        mx, my = x + math.sin(ang) * L * 0.5 + rnd.uniform(-20, 20) * s, y + math.cos(ang) * L * 0.5
        ex, ey = x + math.sin(ang) * L, y + math.cos(ang) * L
        p.quadTo(mx, my, ex, ey); out.append((p, (x, y), (mx, my), (ex, ey)))
    return out

def plant(c, x, y, s, t, seed=1, roots=True, root_k=1.0, leaves=6, pot=False, glow=0.0):
    """Young plant: stem from (x,y) up, leaves alternating, optional roots below y. glow = yellow sugar glow in leaves."""
    c.save()
    if roots and root_k > 0:
        for (p, a, m, e) in root_paths(x, y, s, seed):
            meas = skia.PathMeasure(p, False); L = meas.getLength(); seg = skia.Path()
            meas.getSegment(0, L * root_k, seg, True)
            c.drawPath(seg, P(color=col('#f3e2c0'), stroke=10 * s)); c.drawPath(seg, P(color=col('#c9a877'), stroke=3 * s))
    h = 520 * s; sw = math.sin(t * 1.3 + seed) * 10 * s
    stem = skia.Path(); stem.moveTo(x, y); stem.quadTo(x + sw * 0.3, y - h * 0.5, x + sw, y - h)
    c.drawPath(stem, P(color=col('#2f7d24'), stroke=26 * s)); c.drawPath(stem, P(color=col('#5fc94a'), stroke=16 * s))
    for i in range(leaves):
        k = (i + 1) / (leaves + 1); side = -1 if i % 2 == 0 else 1
        lx, ly = x + sw * k * k, y - h * k
        leaf(c, lx + side * 70 * s * (1.1 - k * 0.3), ly - 20 * s, s * (1.05 - k * 0.35), t, colr='#5cc94a', seed=i + seed,
             face_on=False, rot=side * 62 + math.sin(t * 1.5 + i) * 4)
        if glow > 0:
            gx, gy = lx + side * 70 * s, ly - 30 * s
            c.drawCircle(gx, gy, 70 * s, rad(gx, gy, 70 * s, [col('#ffe14d', int(120 * glow)), col('#ffe14d', 0)]))
    leaf(c, x + sw, y - h - 30 * s, s * 0.6, t, colr='#7ed957', seed=seed + 9, face_on=False, rot=math.sin(t) * 6)
    if pot:
        pp = skia.Path(); pp.moveTo(x - 170 * s, y - 20 * s); pp.lineTo(x + 170 * s, y - 20 * s); pp.lineTo(x + 130 * s, y + 230 * s); pp.lineTo(x - 130 * s, y + 230 * s); pp.close()
        c.drawPath(pp, lin(c, (x - 170 * s, 0, x + 170 * s, 0), [col('#e07a4a'), col('#c25a2c')], vertical=False))
        c.drawRoundRect(skia.Rect(x - 190 * s, y - 60 * s, x + 190 * s, y), 14 * s, 14 * s, lin(c, (0, y - 60 * s, 0, y), [col('#f08d5c'), col('#cf6334')]))
        c.drawOval(skia.Rect(x - 165 * s, y - 64 * s, x + 165 * s, y - 34 * s), P(color=col('#6b4423')))
    c.restore()

def stoma(c, x, y, s, open_k, t=0.0, alpha=255):
    """Leaf pore: two bean-shaped guard cells; open_k 0..1 opens the gap."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    gap = 8 + 30 * open_k
    c.drawOval(skia.Rect(-gap * 0.9, -95, gap * 0.9, 95), P(color=col('#1f4d1a', a)))
    for sx in (-1, 1):
        p = skia.Path(); p.addOval(skia.Rect(-60, -110, 60, 110))
        c.save(); c.translate(sx * (gap + 52), 0)
        c.drawPath(p, rad(-15 * sx, -30, 140, [col('#c8f5a8', a), col('#7ed957', a), col('#4fa83a', a)], [0, 0.5, 1]))
        c.drawPath(p, P(color=col('#2f7d24', a), stroke=6))
        for k in range(4):
            c.drawOval(skia.Rect(-14 + sx * 10, -70 + k * 38, 14 + sx * 10, -50 + k * 38), P(color=col('#3f9a2e', int(a * 0.8))))
        c.restore()
    c.restore()

def onion(c, x, y, s, t, rot=0.0, alpha=255, half=False, cut=0.0):
    """Onion bulb (x,y = centre). half=True draws the cut face with rings. cut 0..1 = slices fall away on the right."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    body = skia.Path(); body.moveTo(0, -200); body.cubicTo(60, -150, 190, -110, 190, 20); body.cubicTo(190, 150, 90, 190, 0, 190)
    body.cubicTo(-90, 190, -190, 150, -190, 20); body.cubicTo(-190, -110, -60, -150, 0, -200); body.close()
    c.drawOval(skia.Rect(-170, 170, 170, 210), P(color=col('#0b1a3a', int(a * 0.18)), blur=10))
    if half:
        c.drawPath(body, rad(0, 20, 210, [col('#ffffff', a), col('#f6eefc', a), col('#e5d3f0', a)], [0, 0.6, 1]))
        for k in range(1, 7):
            sc_ = 1 - k * 0.13
            c.save(); c.translate(0, 20 * (1 - sc_)); c.scale(sc_, sc_)
            c.drawPath(body, P(color=col('#cdb2e0', a), stroke=6 / sc_)); c.restore()
        c.drawPath(body, P(color=col('#9c5bb8', a), stroke=12))
    else:
        c.drawPath(body, rad(-60, -60, 300, [col('#f3c08a', a), col('#c9773a', a), col('#8f4a1f', a)], [0, 0.55, 1]))
        for k in (-120, -60, 0, 60, 120):
            ln = skia.Path(); ln.moveTo(0, -195); ln.cubicTo(k * 0.6, -120, k * 1.25, 60, k * 0.35, 188)
            c.drawPath(ln, P(color=col('#8f4a1f', int(a * 0.45)), stroke=4))
        c.drawPath(body, P(color=col('#7a3d17', a), stroke=7))
        tip = skia.Path(); tip.moveTo(-14, -190); tip.quadTo(0, -250, 22, -270); tip.quadTo(10, -230, 14, -190); tip.close()
        c.drawPath(tip, P(color=col('#b9773f', a)))
        for k in range(-3, 4):
            c.drawLine(k * 12, 188, k * 22, 214, P(color=col('#d8c3a0', a), stroke=4))
    c.restore()

def knife(c, x, y, s=1.0, rot=0.0, alpha=255):
    """Kitchen knife, (x,y) = middle of the blade edge; blade points right."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    bl = skia.Path(); bl.moveTo(-160, 0); bl.lineTo(230, 0); bl.quadTo(200, -70, 120, -90); bl.lineTo(-160, -90); bl.close()
    c.drawPath(bl, lin(c, (0, -90, 0, 0), [col('#f4f7fb', a), col('#c3ccd8', a)]))
    c.drawLine(-160, -2, 225, -2, P(color=col('#ffffff', a), stroke=4))
    c.drawPath(bl, P(color=col('#8793a6', a), stroke=4))
    c.drawRoundRect(skia.Rect(-400, -78, -150, -12), 26, 26, lin(c, (0, -78, 0, -12), [col('#3a4458', a), col('#1f2533', a)]))
    for k in (-340, -270, -200): c.drawCircle(k, -45, 7, P(color=col('#c3ccd8', a)))
    c.restore()

def cutting_board(c, x, y, w_=760, h_=70):
    c.drawRoundRect(skia.Rect(x - w_ / 2, y + 8, x + w_ / 2, y + h_ + 14), 24, 24, P(color=col('#0b1a3a', 50), blur=10))
    c.drawRoundRect(skia.Rect(x - w_ / 2, y, x + w_ / 2, y + h_), 24, 24, lin(c, (0, y, 0, y + h_), [col('#e8b77c'), col('#c48a4c')]))
    for k in range(4): c.drawLine(x - w_ / 2 + 40, y + 16 + k * 14, x + w_ / 2 - 40, y + 18 + k * 13, P(color=col('#b07a40', 90), stroke=3))

def gas_wisp(c, x, y, s, t, seed=0, alpha=180, colr='#c9f27a'):
    """Soft rising wisp (irritant gas / vapour), centre x,y."""
    a = int(alpha); rnd = random.Random(seed)
    for k in range(4):
        dx = math.sin(t * 2 + seed + k) * 14 * s + rnd.uniform(-20, 20) * s; dy = -k * 34 * s
        r = (40 - k * 6) * s
        c.drawCircle(x + dx, y + dy, r, rad(x + dx, y + dy, r, [col(colr, a), col(colr, 0)]))

def human_eye(c, x, y, s, t, alpha=255, iris='#5b8fd6', tear=0.0, squint=0.0):
    """Plain almond eye (no cartoon features). tear 0..1 = tear wells up and runs down. squint narrows it."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    blink = 1.0 if (t % 3.3) > 0.14 else 0.15
    o = blink * (1 - 0.45 * squint)
    ep = skia.Path(); ep.moveTo(-130, 0); ep.quadTo(0, -105 * o, 130, 0); ep.quadTo(0, 95 * o, -130, 0); ep.close()
    c.drawPath(ep, P(color=col('#ffffff', a)))
    if tear > 0:
        c.drawPath(ep, P(color=col('#ff9aa8', int(a * 0.35 * tear))))
    c.save(); c.clipPath(ep, doAntiAlias=True)
    c.drawCircle(0, 0, 56, rad(0, 0, 56, [col(mix_hx(iris, '#ffffff', 0.4), a), col(iris, a), col(mix_hx(iris, '#000000', 0.4), a)], [0, 0.6, 1]))
    c.drawCircle(0, 0, 24, P(color=col('#0b1a3a', a)))
    c.drawCircle(-16, -18, 11, P(color=col('#ffffff', a)))
    c.restore()
    c.drawPath(ep, P(color=col('#1b2a4a', a), stroke=9))
    lash = skia.Path(); lash.moveTo(-138, -4); lash.quadTo(0, -118 * o, 138, -4)
    c.drawPath(lash, P(color=col('#1b2a4a', a), stroke=14))
    if tear > 0:
        ty = 40 + 200 * clamp(tear * 1.4 - 0.4)
        tr = 16 + 6 * clamp(tear * 2)
        dp = skia.Path(); dp.moveTo(60, ty - tr * 2.2); dp.cubicTo(60 + tr * 1.1, ty - tr * 0.6, 60 + tr, ty + tr, 60, ty + tr); dp.cubicTo(60 - tr, ty + tr, 60 - tr * 1.1, ty - tr * 0.6, 60, ty - tr * 2.2); dp.close()
        c.drawPath(dp, rad(55, ty, tr * 1.5, [col('#ffffff', a), col('#8fd3ff', a), col('#3fa9ff', a)], [0, 0.4, 1]))
        c.drawPath(dp, P(color=col('#2a86e0', a), stroke=3))
    c.restore()

def skin_section(c, y, t, x0=0, x1=W, y1=1600, bump=0.0, hairs=(200, 540, 880), hair_up=0.0, muscle=True, muscle_k=0.0, show_muscle=1.0):
    """Cross-section of skin: surface at y, hairs in follicles. hair_up 0..1 raises hairs, bump raises the skin around them.
    muscle_k 0..1 = arrector pili contraction (glows coral)."""
    surf = skia.Path(); surf.moveTo(x0, y)
    step = 6
    for xx in range(int(x0), int(x1) + step, step):
        b = 0
        for hx in hairs: b += bump * 46 * math.exp(-((xx - hx) / 70) ** 2)
        surf.lineTo(xx, y - b)
    surf.lineTo(x1, y1); surf.lineTo(x0, y1); surf.close()
    c.drawPath(surf, lin(c, (0, y - 50, 0, y1), [col('#ffd9c2'), col('#f6b99b'), col('#e89a85')], ))
    c.save(); c.clipPath(surf, doAntiAlias=True)
    c.drawRect(skia.Rect(x0, y + 120, x1, y1), lin(c, (0, y + 120, 0, y1), [col('#f2b39a', 0), col('#e6917f', 160)]))
    c.drawRect(skia.Rect(x0, y + 420, x1, y1), lin(c, (0, y + 420, 0, y1), [col('#fff2c9', 0), col('#ffe9a8', 200)]))
    c.restore()
    c.drawPath(surf, P(color=col('#d98572'), stroke=6))
    for hx in hairs:
        b = bump * 46
        fy = y + 260
        # follicle (tilted)
        c.save(); c.translate(hx, fy)
        tilt = lerp(-38, -6, hair_up)
        c.rotate(tilt)
        c.drawRoundRect(skia.Rect(-26, -270, 26, 30), 26, 26, P(color=col('#f0a58c')))
        c.drawRoundRect(skia.Rect(-26, -270, 26, 30), 26, 26, P(color=col('#c9705c'), stroke=4))
        c.drawCircle(0, 10, 30, rad(0, 10, 30, [col('#d8735e'), col('#b85540')]))
        c.drawLine(0, 10, 0, -270 - b, P(color=col('#4a3426'), stroke=11))
        hp = skia.Path(); hp.moveTo(0, -270 - b); hp.quadTo(-10, -420 - b, -6 + hair_up * 6, -520 - b)
        c.drawPath(hp, P(color=col('#4a3426'), stroke=10))
        c.restore()
        if muscle and show_muscle > 0:
            # arrector pili: from follicle side (lower) to just under the surface, on the side the hair leans away from
            r = math.radians(tilt)
            lx_, ly_ = 24, -110
            mx0, my0 = hx + lx_ * math.cos(r) - ly_ * math.sin(r), fy + lx_ * math.sin(r) + ly_ * math.cos(r)
            mx1, my1 = hx + lerp(120, 90, muscle_k), y + 60 - b * 0.4
            mc = mix_hx('#e56b6b', '#ff2d55', muscle_k)
            w_ = lerp(16, 26, muscle_k)
            if muscle_k > 0.05:
                c.drawLine(mx0, my0, mx1, my1, P(color=col('#ff5c85', int(110 * muscle_k * show_muscle)), stroke=w_ * 2.4, blur=8))
            c.drawLine(mx0, my0, mx1, my1, P(color=col(mc, int(255 * show_muscle)), stroke=w_))
            for k in range(1, 4):
                u = k / 4
                c.drawLine(lerp(mx0, mx1, u) - 8, lerp(my0, my1, u) - 4, lerp(mx0, mx1, u) + 8, lerp(my0, my1, u) + 4, P(color=col('#ffffff', int(90 * show_muscle)), stroke=3))

# ---------------- Wind, magnets, heart (added for ep_023+) ----------------
def flag(c, x, y, s=1.0, t=0.0, wind=1.0, colr='#ff5c85', pole_h=520, alpha=255):
    """Flag on a pole standing at (x, y) (ground). wind 0 = hanging limp, 1 = flying straight out to the right, flapping."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect(-40, -10, 40, 10), P(color=col('#0b1a3a', int(a * 0.18)), blur=6))
    c.drawRoundRect(skia.Rect(-9, -pole_h, 9, 0), 9, 9, lin(c, (0, -pole_h, 0, 0), [col('#e9eef6', a), col('#9aa7bd', a)]))
    c.drawCircle(0, -pole_h - 6, 14, P(color=col('#ffd23f', a)))
    L, Hh, n = 300, 190, 24
    droop = math.radians(lerp(72, 3, clamp(wind)))      # 0 = flying straight out, larger = fly end hangs down
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        wave = math.sin(u * 7.0 - t * 9.0 * (0.4 + wind)) * 22 * u * (0.25 + wind)
        px = u * L * math.cos(droop); py = -pole_h + 4 + u * L * math.sin(droop) + wave
        top.append((px, py)); bot.append((px, py + Hh * (1 - 0.12 * u)))
    p = skia.Path(); p.moveTo(*top[0])
    for q in top[1:]: p.lineTo(*q)
    for q in reversed(bot): p.lineTo(*q)
    p.close()
    c.drawPath(p, lin(c, (0, -pole_h, L, 0), [col(colr, a), col(mix_hx(colr, '#1b2a4a', 0.25), a)], vertical=False))
    for i in range(1, n, 3):   # cloth folds
        sh = math.sin(i / n * 7.0 - t * 9.0 * (0.4 + wind))
        if sh > 0.3:
            c.drawLine(top[i][0], top[i][1] + 6, bot[i][0], bot[i][1] - 6, P(color=col('#ffffff', int(a * 0.22 * sh)), stroke=10))
    c.drawPath(p, P(color=col(mix_hx(colr, '#1b2a4a', 0.4), a), stroke=3))
    c.restore()

def wind_lines(c, t, y0=700, y1=1500, n=8, speed=900, seed=7, alpha=200, colr='#ffffff', direction=1, curl=True, x0=-200, x1=W + 200):
    """Flowing streamlines with a curl at the end; direction 1 = left->right, -1 = right->left."""
    rnd = random.Random(seed)
    for i in range(n):
        y = rnd.uniform(y0, y1); L = rnd.uniform(160, 300); sp = speed * rnd.uniform(0.8, 1.2)
        span = (x1 - x0) + L
        u = (t * sp + rnd.uniform(0, span)) % span
        hx = x0 + u if direction > 0 else x1 - u
        tx = hx - L * direction
        fade = min(1.0, u / 200, (span - u) / 200)
        a = int(alpha * max(0, fade))
        if a <= 0: continue
        p = skia.Path(); p.moveTo(tx, y)
        p.cubicTo(tx + L * 0.35 * direction, y - 14, hx - L * 0.35 * direction, y + 14, hx, y)
        if curl:
            r = 26; p.cubicTo(hx + r * 1.4 * direction, y, hx + r * 1.4 * direction, y - r * 1.6, hx + r * 0.4 * direction, y - r * 1.5)
        c.drawPath(p, P(color=col(colr, a), stroke=9))

def thermometer(c, x, y, s=1.0, level=0.5, hot='#ff5c85', alpha=255):
    """Upright thermometer, bulb at (x, y); level 0..1 fills the tube."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-30, -330, 30, 0), 30, 30, P(color=col('#ffffff', a)))
    c.drawCircle(0, 0, 52, P(color=col('#ffffff', a)))
    c.drawRoundRect(skia.Rect(-30, -330, 30, 0), 30, 30, P(color=col('#1b2a4a', a), stroke=6))
    c.drawCircle(0, 0, 52, P(color=col('#1b2a4a', a), stroke=6))
    c.drawCircle(0, 0, 49, P(color=col('#ffffff', a)))
    fill_top = lerp(-40, -300, clamp(level))
    c.drawRoundRect(skia.Rect(-15, fill_top, 15, 0), 15, 15, P(color=col(hot, a)))
    c.drawCircle(0, 0, 36, P(color=col(hot, a)))
    for i in range(5):
        yy = -80 - i * 50; c.drawLine(14, yy, 26, yy, P(color=col('#1b2a4a', int(a * 0.6)), stroke=4))
    c.drawCircle(-12, -12, 10, P(color=col('#ffffff', int(a * 0.6))))
    c.restore()

def air_dots(c, x0, y0, x1, y1, t, n=30, spread=1.0, seed=3, colr='#ffffff', r=11, alpha=230, jiggle=1.0):
    """Gas particles jiggling in a box; spread < 1 packs them towards the box centre (denser air)."""
    rnd = random.Random(seed); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for i in range(n):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        f1, f2, ph = rnd.uniform(1.5, 3.0), rnd.uniform(1.5, 3.0), rnd.uniform(0, 6.3)
        px = cx + (bx - cx) * spread + math.sin(t * f1 * (0.6 + jiggle) + ph) * 18 * jiggle
        py = cy + (by - cy) * spread + math.cos(t * f2 * (0.6 + jiggle) + ph) * 18 * jiggle
        c.drawCircle(px, py, r * 1.9, rad(px, py, r * 1.9, [col(colr, int(alpha * 0.35)), col(colr, 0)]))
        c.drawCircle(px, py, r, P(color=col(colr, alpha)))

MAG_N, MAG_S = '#ff5c85', '#2f9bff'
def bar_magnet(c, x, y, s=1.0, rot=0.0, alpha=255, w_=380, h_=120, labels=True):
    """Bar magnet centred at (x, y); north (coral, 'N') on the left at rot=0, south (blue, 'S') on the right."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    r = skia.Rect(-w_ / 2, -h_ / 2, w_ / 2, h_ / 2)
    c.drawRoundRect(skia.Rect(-w_ / 2 + 6, -h_ / 2 + 14, w_ / 2 + 6, h_ / 2 + 14), 22, 22, P(color=col('#0b1a3a', int(a * 0.22)), blur=10))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(r, 22, 22), doAntiAlias=True)
    c.drawRect(skia.Rect(-w_ / 2, -h_ / 2, 0, h_ / 2), lin(c, (0, -h_ / 2, 0, h_ / 2), [col('#ff8aa6', a), col(MAG_N, a), col('#d63e66', a)], pos=[0, 0.4, 1]))
    c.drawRect(skia.Rect(0, -h_ / 2, w_ / 2, h_ / 2), lin(c, (0, -h_ / 2, 0, h_ / 2), [col('#7cc6ff', a), col(MAG_S, a), col('#1f6fc4', a)], pos=[0, 0.4, 1]))
    c.drawRect(skia.Rect(-w_ / 2, -h_ / 2, w_ / 2, -h_ / 2 + 14), P(color=col('#ffffff', int(a * 0.28))))
    c.restore()
    c.drawRoundRect(r, 22, 22, P(color=col('#1b2a4a', a), stroke=5))
    if labels:
        for sx, L in ((-1, 'N'), (1, 'S')):
            c.save(); c.translate(sx * w_ / 4, 0); c.rotate(-rot)
            text_block(c, L, 0, 0, size=int(h_ * 0.62), fill='#ffffff', stroke='#1b2a4a', alpha=a)
            c.restore()
    c.restore()

def paperclip(c, x, y, s=1.0, rot=0.0, alpha=255, colr='#c3ccd9'):
    """Steel paperclip, long axis vertical at rot=0, centred at (x, y), ~150 px long."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path()
    p.moveTo(-12, 40); p.lineTo(-12, -50); p.arcTo(skia.Rect(-12, -68, 12, -32), 180, 180, False)
    p.lineTo(12, 55); p.arcTo(skia.Rect(-24, 37, 24, 85), 0, 180, False)
    p.lineTo(-24, -60); p.arcTo(skia.Rect(-24, -84, 24, -36), 180, 180, False); p.lineTo(24, 20)
    c.drawPath(p, P(color=col('#0b1a3a', int(a * 0.25)), stroke=11, blur=3))
    c.drawPath(p, P(color=col('#6b778a', a), stroke=10))
    c.drawPath(p, P(color=col(colr, a), stroke=6))
    c.restore()

def compass(c, x, y, r, needle_ang, t=0.0, alpha=255):
    """Compass rose; needle_ang in degrees (0 = needle's red north end points up)."""
    a = int(alpha)
    c.drawCircle(x, y + r * 0.08, r * 1.04, P(color=col('#0b1a3a', int(a * 0.25)), blur=10))
    c.drawCircle(x, y, r, lin(c, (0, y - r, 0, y + r), [col('#ffe58a', a), col('#e0a92a', a)]))
    c.drawCircle(x, y, r * 0.86, P(color=col('#ffffff', a)))
    c.drawCircle(x, y, r * 0.86, P(color=col('#1b2a4a', int(a * 0.5)), stroke=4))
    for i in range(16):
        ang = math.radians(i * 22.5); L = r * (0.12 if i % 4 == 0 else 0.06)
        c.drawLine(x + math.sin(ang) * r * 0.84, y - math.cos(ang) * r * 0.84, x + math.sin(ang) * (r * 0.84 - L), y - math.cos(ang) * (r * 0.84 - L), P(color=col('#1b2a4a', int(a * 0.6)), stroke=4))
    c.save(); c.translate(x, y); c.rotate(needle_ang)
    n = skia.Path(); n.moveTo(0, -r * 0.72); n.lineTo(r * 0.11, 0); n.lineTo(-r * 0.11, 0); n.close()
    sth = skia.Path(); sth.moveTo(0, r * 0.72); sth.lineTo(r * 0.11, 0); sth.lineTo(-r * 0.11, 0); sth.close()
    c.drawPath(n, P(color=col(MAG_N, a))); c.drawPath(sth, P(color=col('#9aa7bd', a)))
    c.drawCircle(0, 0, r * 0.07, P(color=col('#1b2a4a', a)))
    c.restore()
    text_block(c, 'N', x, y - r * 0.6, size=int(r * 0.26), fill='#1b2a4a', stroke='#ffffff', alpha=a)

def field_lines(c, x, y, s=1.0, k=1.0, alpha=200, colr='#ffffff', t=0.0, n=5, rot=0.0):
    """Dipole field lines around a horizontal magnet centred at (x, y) (N left). k 0..1 draws them on; dots flow N->S."""
    if k <= 0: return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for i in range(1, n + 1):
        hgt = 70 + i * 70; half = 190
        for sy in (-1, 1):
            p = skia.Path(); p.moveTo(-half + 20, 0)
            p.cubicTo(-half - i * 60, sy * hgt * 1.25, half + i * 60, sy * hgt * 1.25, half - 20, 0)
            meas = skia.PathMeasure(p, False); L = meas.getLength()
            seg = skia.Path(); meas.getSegment(0, L * k, seg, True)
            c.drawPath(seg, P(color=col(colr, int(alpha * (1 - i * 0.1))), stroke=6))
            if k >= 1:
                u = ((t * 0.25 + i * 0.17) % 1.0)
                pos, _ = meas.getPosTan(L * u)
                c.drawCircle(pos.x(), pos.y(), 9, P(color=col('#ffd23f', int(alpha))))
    c.restore()

def spin_electron(c, x, y, r, t, up=True, alpha=255, seed=0):
    """Electron as a small glowing ball spinning, with a magnet arrow (up or down)."""
    a = int(alpha)
    c.drawCircle(x, y, r * 2.0, rad(x, y, r * 2.0, [col('#7cc6ff', int(a * 0.45)), col('#7cc6ff', 0)]))
    c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.35, r * 1.4, [col('#ffffff', a), col('#5fb4ff', a), col('#1f6fc4', a)], [0, 0.4, 1]))
    sw = (t * 360 * 0.8 + seed * 50) % 360
    pth = skia.Path(); pth.addArc(skia.Rect(x - r * 1.45, y - r * 0.5, x + r * 1.45, y + r * 0.5), sw, 250)
    c.drawPath(pth, P(color=col('#ffffff', int(a * 0.8)), stroke=r * 0.12))
    d = -1 if up else 1
    arrow(c, x, y - d * r * 0.2 * -1, x, y + d * r * 2.0, colr='#ffd23f', w=r * 0.22, alpha=a)

def domains(c, x0, y0, w_, h_, align, t=0.0, seed=4, cols_=4, rows=3, alpha=255, arrows_per=4, tint=True, target=0.0):
    """Iron block split into magnetic domains; each patch holds arrows. align 0 = random directions, 1 = all point to `target` degrees."""
    rnd = random.Random(seed); a = int(alpha)
    c.save(); r = skia.Rect(x0, y0, x0 + w_, y0 + h_)
    c.drawRoundRect(skia.Rect(x0 + 6, y0 + 16, x0 + w_ + 6, y0 + h_ + 16), 26, 26, P(color=col('#0b1a3a', int(a * 0.2)), blur=12))
    c.drawRoundRect(r, 26, 26, lin(c, (0, y0, 0, y0 + h_), [col('#dfe5ee', a), col('#aeb8c7', a)]))
    c.clipRRect(skia.RRect.MakeRectXY(r, 26, 26), doAntiAlias=True)
    cw, ch = w_ / cols_, h_ / rows
    # jittered grid corners -> irregular patches
    pts = [[(x0 + i * cw + (rnd.uniform(-0.22, 0.22) * cw if 0 < i < cols_ else 0), y0 + j * ch + (rnd.uniform(-0.22, 0.22) * ch if 0 < j < rows else 0)) for j in range(rows + 1)] for i in range(cols_ + 1)]
    tints = ['#ffd9e2', '#d6ecff', '#fff3c4', '#e3f7dc', '#efe1ff']
    for i in range(cols_):
        for j in range(rows):
            q = [pts[i][j], pts[i + 1][j], pts[i + 1][j + 1], pts[i][j + 1]]
            p = skia.Path(); p.moveTo(*q[0]); [p.lineTo(*v) for v in q[1:]]; p.close()
            base = rnd.uniform(0, 360)
            ang = base + ((target - base + 180) % 360 - 180) * clamp(align)
            if tint: c.drawPath(p, P(color=col(tints[(i * 3 + j) % len(tints)], int(a * 0.55 * (1 - align) + a * 0.15))))
            c.drawPath(p, P(color=col('#7d8798', int(a * 0.6 * (1 - align * 0.7))), stroke=4))
            mx, my = sum(v[0] for v in q) / 4, sum(v[1] for v in q) / 4
            for k in range(arrows_per):
                ox = (k % 2 - 0.5) * cw * 0.42; oy = (k // 2 - 0.5) * ch * 0.42
                wob = math.sin(t * 3 + i + j * 2 + k) * 4 * (1 - align)
                L = min(cw, ch) * 0.17; rr = math.radians(ang + wob)
                ax, ay = mx + ox, my + oy
                arrow(c, ax - math.cos(rr) * L, ay - math.sin(rr) * L, ax + math.cos(rr) * L, ay + math.sin(rr) * L, colr=MAG_N if align < 0.98 else '#e8264f', w=7, alpha=a)
    c.restore()
    c.drawRoundRect(r, 26, 26, P(color=col('#5b6476', a), stroke=5))

# --- heart (plain infographic style, no face) ---
HEART_O2, HEART_LOW = '#ff4f6e', '#6f8fe8'   # oxygen-rich / oxygen-poor blood (diagram convention)
def _heart_outline():
    p = skia.Path()
    p.moveTo(20, 330)
    p.cubicTo(-120, 260, -300, 130, -300, -40)
    p.cubicTo(-300, -200, -190, -275, -80, -250)
    p.cubicTo(-30, -240, 0, -215, 10, -200)
    p.cubicTo(30, -230, 90, -270, 170, -255)
    p.cubicTo(280, -235, 320, -120, 300, 0)
    p.cubicTo(280, 140, 150, 270, 20, 330)
    p.close(); return p

def heart(c, x, y, s=1.0, t=0.0, squeeze=0.0, chambers=0.0, valves=0.0, glow=0.0, alpha=255, flow=0.0, spark=-1.0, vessels=True, hi=None):
    """Infographic heart (front view, as if facing the viewer: the heart's RIGHT side is on the viewer's LEFT).
    squeeze 0..1 contracts it; chambers 0..1 fades in a cut-away of the four chambers; valves 0..1 = open..closed
    (both AV valves); spark = 0..1 position of the electrical wave (top -> bottom), <0 hides it; hi = list of
    chamber names to highlight: 'RA','LA','RV','LV'."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.scale(s, s)
    sq = 1 - 0.07 * squeeze
    if glow > 0:
        c.drawCircle(0, 30, 470, rad(0, 30, 470, [col('#ff5c85', int(110 * glow * a / 255)), col('#ff5c85', 0)]))
    if vessels:
        # vena cava into the right atrium (viewer left), pulmonary artery (blue) and aorta arch (red) on top
        c.drawLine(-190, -200, -190, -420, P(color=col('#3d5bb8', a), stroke=78))
        c.drawLine(-190, -200, -190, -420, P(color=col(HEART_LOW, a), stroke=62))
        pa = skia.Path(); pa.moveTo(-50, -150); pa.cubicTo(-50, -270, 60, -300, 190, -285)
        c.drawPath(pa, P(color=col('#3d5bb8', a), stroke=76)); c.drawPath(pa, P(color=col(HEART_LOW, a), stroke=60))
        ao = skia.Path(); ao.moveTo(20, -170); ao.cubicTo(0, -450, 230, -460, 250, -320)
        c.drawPath(ao, P(color=col('#b51d3c', a), stroke=88)); c.drawPath(ao, P(color=col(HEART_O2, a), stroke=72))
        c.drawPath(ao, P(color=col('#ffffff', int(a * 0.25)), stroke=16))
    c.scale(sq, sq)
    o = _heart_outline()
    c.drawPath(o, P(color=col('#0b1a3a', int(a * 0.25)), blur=16))
    c.drawPath(o, rad(-90, -120, 520, [col('#ff8fa3', a), col('#f0506e', a), col('#b8213f', a)], [0, 0.5, 1]))
    c.drawPath(o, P(color=col('#8a1530', a), stroke=6))
    if chambers < 0.99:
        # surface groove + highlight (closed heart)
        g = skia.Path(); g.moveTo(10, -190); g.cubicTo(-30, -40, -20, 140, 30, 300)
        c.drawPath(g, P(color=col('#b8213f', int(a * (1 - chambers) * 0.8)), stroke=10))
        c.drawOval(skia.Rect(-230, -200, -110, -90), P(color=col('#ffffff', int(a * 0.35 * (1 - chambers))), blur=14))
    if chambers > 0:
        ca = int(a * chambers)
        hs = set(hi or [])
        def ch(name, path, colr):
            k = 1.0 if (not hs or name in hs) else 0.35
            c.drawPath(path, P(color=col(colr, int(ca * k))))
            c.drawPath(path, P(color=col('#7a1029', int(ca * 0.6)), stroke=4))
            if name in hs:
                c.drawPath(path, P(color=col('#ffffff', int(ca * (0.6 + 0.4 * math.sin(t * 6)))), stroke=8))
        ra = skia.Path(); ra.addOval(skia.Rect(-250, -205, -50, -25))
        la = skia.Path(); la.addOval(skia.Rect(40, -215, 250, -45))
        cs = 1 - 0.12 * squeeze
        rv = skia.Path(); rv.moveTo(-245, 5); rv.lineTo(-30, 5); rv.lineTo(-30, 255 * cs); rv.cubicTo(-120, 215 * cs, -230, 120 * cs, -245, 5); rv.close()
        lv = skia.Path(); lv.moveTo(35, 5); lv.lineTo(250, 5); lv.cubicTo(245, 120 * cs, 160, 230 * cs, 35, 285 * cs); lv.close()
        ch('RA', ra, HEART_LOW); ch('RV', rv, HEART_LOW); ch('LA', la, HEART_O2); ch('LV', lv, HEART_O2)
        # septum
        c.drawLine(2, -200, 2, 300, P(color=col('#8a1530', ca), stroke=16))
        # AV valves: two flaps each; open = flaps hang down, closed = horizontal
        for vx in (-140, 145):
            for sx in (-1, 1):
                ang = math.radians(lerp(75, 8, clamp(valves)))
                bx, by = vx + sx * 62, -10
                ex, ey = bx - sx * math.cos(ang) * 58, by + math.sin(ang) * 58
                c.drawLine(bx, by, ex, ey, P(color=col('#ffffff', ca), stroke=12))
    if spark >= 0:
        yy = lerp(-230, 330, clamp(spark))
        c.save(); c.clipPath(o, doAntiAlias=True)
        c.drawRect(skia.Rect(-320, yy - 40, 320, yy + 40), lin(c, (0, yy - 40, 0, yy + 40), [col('#fff6b0', 0), col('#fff6b0', int(a * 0.85)), col('#fff6b0', 0)]))
        c.restore()
    c.restore()
