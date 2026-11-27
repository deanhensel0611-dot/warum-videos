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
    if kw.get('blur') and kw['blur'] > 0.01:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, kw['blur']))
    return p

# ---------------- Hintergründe ----------------
def lin(c, rect, cols, vertical=True, pos=None):
    x0, y0, x1, y1 = rect
    pts = [(0, y0), (0, y1)] if vertical else [(x0, 0), (x1, 0)]
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeLinear(points=pts, colors=cols, positions=pos))
    return p

def rad(cx, cy, r, cols, pos=None):
    r = max(r, 0.01)
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

# ---------------- props added 2026-11-21 (echoes, chameleon, spider webs) ----------------
def cliff(c, x, y_top, w_, h_=None, side=1, seed=3, c1='#c98a5b', c2='#9c5f3a', alpha=255):
    """Rock cliff face. side=1: rock body on the right with its face pointing left at x; side=-1 mirrored."""
    a = int(alpha); h_ = h_ or (H - y_top); rnd = random.Random(seed)
    p = skia.Path(); p.moveTo(x + side * w_, y_top - 40)
    pts = []
    for i in range(9):
        yy = lerp(y_top, y_top + h_, i / 8)
        pts.append((x + side * rnd.uniform(-14, 26) * (1 if 0 < i < 8 else 0.4), yy))
    p.lineTo(x + side * 30, y_top - 20)
    for (px, py) in pts: p.lineTo(px, py)
    p.lineTo(x + side * w_, y_top + h_); p.close()
    c.drawPath(p, lin(c, (x, 0, x + side * w_, 0), [col(c1, a), col(c2, a)], vertical=False))
    c.drawPath(p, P(color=col('#6e3f24', int(a * 0.8)), stroke=5))
    for i in range(6):
        yy = y_top + h_ * (0.12 + 0.15 * i)
        xx = x + side * rnd.uniform(50, w_ * 0.7)
        L = rnd.uniform(60, 140)
        c.drawLine(xx, yy, xx + side * L, yy + rnd.uniform(-8, 8), P(color=col('#7a4528', int(a * 0.45)), stroke=6))
    c.drawRect(skia.Rect(min(x, x + side * w_) - 8, y_top - 52, max(x, x + side * w_) + 8, y_top - 30), P(color=col('#6fc24a', a)))

def megaphone(c, x, y, s=1.0, rot=0.0, alpha=255, colr='#ff5c85'):
    """Plain megaphone, mouth pointing right at rot=0; (x, y) = handle end."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-20, 10, 20, 90), 12, 12, P(color=col('#1b2a4a', a)))
    c.drawRoundRect(skia.Rect(-60, -28, 10, 28), 14, 14, P(color=col('#ffffff', a)))
    c.drawRoundRect(skia.Rect(-60, -28, 10, 28), 14, 14, P(color=col('#1b2a4a', a), stroke=5))
    p = skia.Path(); p.moveTo(0, -30); p.lineTo(150, -95); p.lineTo(150, 95); p.lineTo(0, 30); p.close()
    c.drawPath(p, lin(c, (0, -95, 0, 95), [col(mix_hx(colr, '#ffffff', 0.3), a), col(colr, a)]))
    c.drawPath(p, P(color=col('#1b2a4a', a), stroke=5))
    c.drawOval(skia.Rect(132, -98, 168, 98), P(color=col('#ffffff', a)))
    c.drawOval(skia.Rect(132, -98, 168, 98), P(color=col('#1b2a4a', a), stroke=5))
    c.restore()

def stopwatch(c, x, y, r, frac, alpha=255, label=None, accent='#ff5c85'):
    """Stopwatch; frac = hand position as fraction of a turn (also fills a sector)."""
    a = int(alpha)
    c.drawRoundRect(skia.Rect(x - 22, y - r - 46, x + 22, y - r - 6), 8, 8, P(color=col('#1b2a4a', a)))
    c.drawRoundRect(skia.Rect(x - 40, y - r - 62, x + 40, y - r - 38), 12, 12, P(color=col(accent, a)))
    c.drawCircle(x, y, r + 14, P(color=col('#1b2a4a', a)))
    c.drawCircle(x, y, r, P(color=col('#ffffff', a)))
    if frac > 0:
        p = skia.Path(); p.moveTo(x, y); p.arcTo(skia.Rect(x - r * 0.9, y - r * 0.9, x + r * 0.9, y + r * 0.9), -90, 360 * min(frac, 0.9999), False); p.close()
        c.drawPath(p, P(color=col(accent, int(a * 0.35))))
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        c.drawLine(x + math.cos(ang) * r * 0.8, y + math.sin(ang) * r * 0.8, x + math.cos(ang) * r * 0.92, y + math.sin(ang) * r * 0.92,
                   P(color=col('#1b2a4a', a), stroke=6 if i % 3 == 0 else 3))
    ang = math.radians(360 * frac - 90)
    c.drawLine(x, y, x + math.cos(ang) * r * 0.78, y + math.sin(ang) * r * 0.78, P(color=col(accent, a), stroke=8))
    c.drawCircle(x, y, 12, P(color=col('#1b2a4a', a)))
    if label: text_block(c, label, x, y + r * 0.45, size=int(r * 0.32), fill='#1b2a4a', stroke='#ffffff', alpha=a)

def bat(c, x, y, s, t, flap_speed=9.0, alpha=255, colr='#3a2f55', rot=0.0):
    """Plain flying bat (no face details beyond small eyes)."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    f = math.sin(t * flap_speed)
    for sx in (-1, 1):
        lift = -60 * f
        p = skia.Path(); p.moveTo(sx * 20, -10)
        p.cubicTo(sx * 80, -40 + lift, sx * 160, -60 + lift * 1.2, sx * 210, -20 + lift * 1.3)
        p.quadTo(sx * 175, 0 + lift * 0.8, sx * 160, 20 + lift * 0.7)
        p.quadTo(sx * 130, 5 + lift * 0.5, sx * 110, 30 + lift * 0.4)
        p.quadTo(sx * 80, 15 + lift * 0.3, sx * 60, 35 + lift * 0.2)
        p.quadTo(sx * 40, 20, sx * 18, 20); p.close()
        c.drawPath(p, P(color=col(colr, a)))
    c.drawOval(skia.Rect(-28, -40, 28, 45), P(color=col(mix_hx(colr, '#000000', 0.15), a)))
    for sx in (-1, 1):
        e = skia.Path(); e.moveTo(sx * 8, -34); e.lineTo(sx * 22, -66); e.lineTo(sx * 26, -30); e.close()
        c.drawPath(e, P(color=col(mix_hx(colr, '#000000', 0.15), a)))
        c.drawCircle(sx * 10, -20, 4.5, P(color=col('#ffffff', a)))
    c.restore()

def ball(c, x, y, r, colr='#ff5c85', alpha=255, squash=0.0, axis=0.0):
    """Rubber ball with a highlight; squash 0..1 flattens along `axis` (radians, direction of impact)."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(math.degrees(axis)); c.scale(1 - 0.3 * squash, 1 + 0.25 * squash)
    c.drawCircle(0, 0, r, rad(-r * 0.3, -r * 0.3, r * 1.4, [col(mix_hx(colr, '#ffffff', 0.45), a), col(colr, a), col(mix_hx(colr, '#000000', 0.25), a)], [0, 0.55, 1]))
    c.drawCircle(-r * 0.35, -r * 0.35, r * 0.22, P(color=col('#ffffff', int(a * 0.6))))
    c.restore()

CHAM_GREEN, CHAM_ORANGE = '#3fbf6a', '#ff8a2c'
def cham_color(k):
    """Chameleon skin colour for excitement k 0..1: calm green -> yellow -> orange/red."""
    stops = ['#3fbf6a', '#9ad43a', '#ffd23f', '#ff9f1c', '#ff6a3c']
    k = clamp(k) * (len(stops) - 1); i = min(int(k), len(stops) - 2)
    return mix_hx(stops[i], stops[i + 1], k - i)

def crystal_color(k):
    """Colour reflected by the iridophore crystal lattice for spacing k 0..1 (close = blue, wide = red)."""
    stops = ['#3a6bff', '#2fa8ff', '#4cd964', '#ffe14d', '#ff9f1c', '#ff5c3b']
    k = clamp(k) * (len(stops) - 1); i = min(int(k), len(stops) - 2)
    return mix_hx(stops[i], stops[i + 1], k - i)

def branch(c, x0, y0, x1, y1, w=34, alpha=255, leaves=True, t=0.0):
    a = int(alpha)
    p = skia.Path(); p.moveTo(x0, y0); p.cubicTo(lerp(x0, x1, 0.33), y0 + 18, lerp(x0, x1, 0.66), y1 - 18, x1, y1)
    c.drawPath(p, P(color=col('#6e4a2c', a), stroke=w))
    c.drawPath(p, P(color=col('#8f6440', a), stroke=w * 0.55))
    if leaves:
        for i, u in enumerate((0.12, 0.85)):
            lx, ly = lerp(x0, x1, u), lerp(y0, y1, u)
            leaf(c, lx, ly - 30, 0.55, t, colr='#5cc94a', seed=i, face_on=False, rot=-30 + 60 * i, alpha=a)

def chameleon(c, x, y, s, t, colr=CHAM_GREEN, alpha=255, look=None, flip=False, pattern=True, tail_curl=1.0):
    """Plain side-view chameleon gripping a branch at local y=130; (x, y) = body centre. Natural turret eye, no smile."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    dark = mix_hx(colr, '#0d2a1a', 0.35); light = mix_hx(colr, '#ffffff', 0.35)
    # tail: tube of circles along a spiral
    pts = []
    for i in range(140):
        u = i / 139
        if u < 0.35:
            v = u / 0.35; px, py = lerp(-140, -270, v), lerp(30, 90, v) + 10 * math.sin(v * math.pi)
        else:
            v = (u - 0.35) / 0.65; ang = lerp(-math.pi * 0.5, -math.pi * 0.5 - 2.0 * math.pi * tail_curl, v)
            rr = lerp(75, 14, v); cx, cy = -270, 165
            px, py = cx + rr * math.cos(ang) * -1, cy + rr * math.sin(ang)
        pts.append((px, py, lerp(34, 7, u)))
    for (px, py, rr) in pts: c.drawCircle(px, py, rr + 4, P(color=col(dark, a)))
    for (px, py, rr) in pts: c.drawCircle(px, py, rr, P(color=col(colr, a)))
    # back legs
    def leg(hx, hy, fx, fy):
        c.drawLine(hx, hy, (hx + fx) / 2 - 12, (hy + fy) / 2 - 6, P(color=col(dark, a), stroke=34))
        c.drawLine((hx + fx) / 2 - 12, (hy + fy) / 2 - 6, fx, fy, P(color=col(dark, a), stroke=28))
        c.drawLine(hx, hy, (hx + fx) / 2 - 12, (hy + fy) / 2 - 6, P(color=col(colr, a), stroke=24))
        c.drawLine((hx + fx) / 2 - 12, (hy + fy) / 2 - 6, fx, fy, P(color=col(colr, a), stroke=18))
        for dx in (-14, 14): c.drawOval(skia.Rect(fx + dx - 14, fy - 8, fx + dx + 14, fy + 14), P(color=col(dark, a)))
    leg(-80, 60, -110, 128); leg(130, 50, 160, 128)
    # body
    p = skia.Path(); p.moveTo(-160, 20)
    p.cubicTo(-150, -110, 40, -175, 160, -70)
    p.cubicTo(200, -110, 230, -125, 250, -95)        # casque
    p.cubicTo(285, -70, 315, -30, 318, -5)           # snout top
    p.cubicTo(300, 25, 250, 45, 200, 50)             # jaw
    p.cubicTo(120, 85, -40, 95, -160, 20); p.close()
    c.drawPath(p, lin(c, (0, -150, 0, 90), [col(light, a), col(colr, a), col(dark, a)], pos=[0, 0.45, 1]))
    if pattern:
        c.save(); c.clipPath(p, doAntiAlias=True)
        st = skia.Path(); st.moveTo(-150, 20); st.cubicTo(-40, -30, 90, -20, 200, 20)
        c.drawPath(st, P(color=col(light, int(a * 0.8)), stroke=16))
        for i in range(5):
            bx = -110 + i * 60
            c.drawLine(bx, -95 + abs(i - 2) * 12, bx + 18, 10, P(color=col(dark, int(a * 0.35)), stroke=14))
        # dorsal crest bumps
        for i in range(9):
            bx = -130 + i * 34; by = -95 - 45 * math.sin(lerp(0.4, 2.7, i / 8))
            c.drawCircle(bx, by + 52, 9, P(color=col(light, int(a * 0.9))))
        c.restore()
    c.drawPath(p, P(color=col(dark, a), stroke=6))
    # mouth line
    m = skia.Path(); m.moveTo(312, 4); m.quadTo(270, 26, 214, 22); c.drawPath(m, P(color=col(dark, a), stroke=5))
    # front legs over body
    leg(-40, 70, -60, 130)
    # turret eye
    ex, ey = 232, -38
    c.drawCircle(ex, ey, 36, P(color=col(dark, a)))
    c.drawCircle(ex, ey, 31, rad(ex - 8, ey - 8, 40, [col(light, a), col(colr, a)]))
    for i in range(4):
        rr = 31 - i * 6
        c.drawCircle(ex, ey, rr, P(color=col(dark, int(a * 0.25)), stroke=2.5))
    lx, ly = look if look else (math.sin(t * 0.9) * 0.8, math.sin(t * 0.6 + 1) * 0.5)
    c.drawCircle(ex + lx * 10, ey + ly * 10, 10, P(color=col('#111111', a)))
    c.drawCircle(ex + lx * 10 - 3, ey + ly * 10 - 3, 3, P(color=col('#ffffff', a)))
    c.restore()

def crystal_lattice(c, x0, y0, w_, h_, spacing, t=0.0, r=9, alpha=255, colr='#e8f6ff', clip=True):
    """Grid of guanine nanocrystals (drawn as small hexagons); spacing 0..1 -> gap between them."""
    a = int(alpha); gap = lerp(26, 62, clamp(spacing))
    if clip: c.save(); c.clipRect(skia.Rect(x0, y0, x0 + w_, y0 + h_))
    cx, cy = x0 + w_ / 2, y0 + h_ / 2
    nx = int(w_ / gap / 2) + 2; ny = int(h_ / gap / 2) + 2
    for j in range(-ny, ny + 1):
        for i in range(-nx, nx + 1):
            px = cx + i * gap + (gap / 2 if j % 2 else 0); py = cy + j * gap * 0.87
            pth = hexagon_path(px, py, r)
            c.drawPath(pth, P(color=col(colr, a)))
            c.drawPath(pth, P(color=col('#7fa8c9', int(a * 0.8)), stroke=2))
    if clip: c.restore()

def soap_bubble(c, x, y, r, t, alpha=255):
    a = int(alpha)
    c.drawCircle(x, y, r, rad(x, y, r, [col('#ffffff', 0), col('#dff3ff', int(a * 0.35)), col('#ffffff', int(a * 0.7))], [0, 0.85, 1]))
    for i, hc in enumerate(RAINBOW):
        pth = skia.Path(); rr = r * (0.92 - i * 0.035)
        pth.addArc(skia.Rect(x - rr, y - rr, x + rr, y + rr), (t * 40 + i * 9) % 360, 120)
        c.drawPath(pth, P(color=col(hc, int(a * 0.55)), stroke=r * 0.035))
    c.drawCircle(x - r * 0.38, y - r * 0.4, r * 0.14, P(color=col('#ffffff', int(a * 0.85))))
    c.drawCircle(x, y, r, P(color=col('#ffffff', int(a * 0.8)), stroke=3))

def feather(c, x, y, s, t=0.0, rot=0.0, alpha=255):
    """Peacock-style tail feather with an eye-spot (structural colour)."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawLine(0, 300, 0, -170, P(color=col('#c9b27a', a), stroke=8))
    for i in range(26):
        yy = 260 - i * 17; L = 40 + 110 * math.sin(math.pi * i / 25) ** 0.7
        for sx in (-1, 1):
            c.drawLine(0, yy, sx * L, yy - 40, P(color=col(mix_hx('#3fae6a', '#a9d86e', i / 25), int(a * 0.8)), stroke=5))
    for rr, hc in ((120, '#2f7d4a'), (95, '#d9b23a'), (72, '#1f9e8a'), (50, '#2a5bd8'), (28, '#152a6e')):
        c.drawOval(skia.Rect(-rr * 0.8, -110 - rr, rr * 0.8, -110 + rr * 0.9), P(color=col(hc, a)))
    sh = 0.5 + 0.5 * math.sin(t * 2)
    c.drawOval(skia.Rect(-30, -190, 30, -120), P(color=col('#ffffff', int(a * 0.25 * sh))))
    c.restore()

def spider(c, x, y, s, t, alpha=255, body='#4a3f6b', mark='#ffd23f', walk=0.0, rot=0.0):
    """Plain garden-spider (top view, head up at rot=0): round abdomen with a pattern, 8 jointed legs. walk animates legs."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    dark = mix_hx(body, '#000000', 0.3)
    for sx in (-1, 1):
        for i in range(4):
            base_ang = [-55, -20, 15, 50][i]
            wig = 8 * math.sin(t * 10 * walk + i * 1.7 + (0 if sx > 0 else 1.5)) * walk
            ang = math.radians(base_ang + wig)
            hx, hy = sx * 18, -50 + i * 14
            kx, ky = hx + sx * math.cos(ang) * 95, hy + math.sin(ang) * 95 - 45
            fx, fy = kx + sx * math.cos(ang + sx * 0.0) * 40, ky + 75 + (i - 1.5) * 12
            if i == 0: fy = ky - 40; fx = kx + sx * 30
            p = skia.Path(); p.moveTo(hx, hy); p.lineTo(kx, ky); p.lineTo(fx, fy)
            c.drawPath(p, P(color=col(dark, a), stroke=9))
    # cephalothorax
    c.drawOval(skia.Rect(-34, -80, 34, -10), P(color=col(dark, a)))
    c.drawOval(skia.Rect(-30, -76, 30, -14), lin(c, (0, -80, 0, -10), [col(mix_hx(body, '#ffffff', 0.15), a), col(body, a)]))
    # abdomen
    c.drawOval(skia.Rect(-62, -20, 62, 120), P(color=col(dark, a)))
    c.drawOval(skia.Rect(-58, -16, 58, 116), rad(-15, 20, 110, [col(mix_hx(body, '#ffffff', 0.2), a), col(body, a)]))
    for i in range(3):
        yy = 15 + i * 30; ww = 34 - i * 8
        pth = skia.Path(); pth.moveTo(-ww, yy); pth.quadTo(0, yy + 18, ww, yy)
        c.drawPath(pth, P(color=col(mark, int(a * 0.9)), stroke=7))
    c.drawCircle(0, -5, 8, P(color=col(mark, a)))
    # small eyes on head
    for ex in (-9, 9): c.drawCircle(ex, -66, 4.5, P(color=col('#111111', a)))
    c.restore()

def orb_web(c, cx, cy, R, t=0.0, frame=1.0, spokes=1.0, spiral=1.0, n=16, alpha=255, glue=True, colr='#ffffff', anchors=None):
    """Orb web: frame polygon, radial spokes (dry), sticky capture spiral laid from outside in (spiral 0..1)."""
    a = int(alpha); rnd = random.Random(5)
    rr = [R * (0.88 + 0.12 * rnd.random()) for _ in range(n)]
    pts = [(cx + math.cos(2 * math.pi * i / n - math.pi / 2) * rr[i], cy + math.sin(2 * math.pi * i / n - math.pi / 2) * rr[i]) for i in range(n)]
    sh = P(color=col('#1b2a4a', int(a * 0.15)), stroke=6, blur=2)
    if anchors and frame > 0:
        for (ax, ay), (px, py) in anchors:
            c.drawLine(px, py, lerp(px, ax, frame), lerp(py, ay, frame), P(color=col(colr, a), stroke=4))
    if frame > 0:
        m = int(n * frame) + 1
        for i in range(min(m, n)):
            p0, p1 = pts[i], pts[(i + 1) % n]
            k = clamp(n * frame - i)
            c.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k), P(color=col(colr, a), stroke=4.5))
    if spokes > 0:
        for i in range(n):
            k = clamp(n * spokes - i)
            if k <= 0: break
            c.drawLine(cx, cy, lerp(cx, pts[i][0], k), lerp(cy, pts[i][1], k), P(color=col(colr, int(a * 0.95)), stroke=3.5))
    if spiral > 0:
        turns = 9; total = turns * n; done = int(total * spiral)
        prev = None
        for j in range(done + 1):
            ring = j / n; i = j % n
            f = lerp(0.9, 0.22, ring / turns)
            px, py = lerp(cx, pts[i][0], f), lerp(cy, pts[i][1], f)
            if prev:
                c.drawLine(prev[0], prev[1], px, py, P(color=col(colr, a), stroke=3))
                if glue:
                    for g in (0.33, 0.66):
                        c.drawCircle(lerp(prev[0], px, g), lerp(prev[1], py, g), 3.4, P(color=col('#fff3a8', a)))
            prev = (px, py)
        return prev
    return None

def tooth_path(s=1.0):
    """Molar outline (crown + two roots), centred at crown middle (0, 0); s scales."""
    p = skia.Path()
    p.moveTo(-150 * s, -40 * s)
    p.cubicTo(-160 * s, -150 * s, -110 * s, -175 * s, -75 * s, -150 * s)     # left cusp
    p.cubicTo(-40 * s, -185 * s, -15 * s, -165 * s, 0, -140 * s)
    p.cubicTo(15 * s, -165 * s, 40 * s, -185 * s, 75 * s, -150 * s)
    p.cubicTo(110 * s, -175 * s, 160 * s, -150 * s, 150 * s, -40 * s)       # right cusp
    p.cubicTo(145 * s, 40 * s, 120 * s, 80 * s, 110 * s, 120 * s)           # neck right
    p.cubicTo(100 * s, 220 * s, 90 * s, 300 * s, 60 * s, 330 * s)           # right root
    p.cubicTo(40 * s, 340 * s, 30 * s, 250 * s, 15 * s, 150 * s)
    p.cubicTo(5 * s, 130 * s, -5 * s, 130 * s, -15 * s, 150 * s)
    p.cubicTo(-30 * s, 250 * s, -40 * s, 340 * s, -60 * s, 330 * s)         # left root
    p.cubicTo(-90 * s, 300 * s, -100 * s, 220 * s, -110 * s, 120 * s)
    p.cubicTo(-120 * s, 80 * s, -145 * s, 40 * s, -150 * s, -40 * s)
    p.close(); return p

def tooth(c, x, y, s, t=0.0, plaque=0.0, tartar=0.0, cavity=0.0, section=0.0, gum=True, shine=1.0, alpha=255, weak=0.0, repair=0.0):
    """Plain molar (no face). plaque/tartar 0..1 film on the crown, cavity 0..1 hole on the left cusp,
    section 0..1 shows enamel/dentin/pulp cut-away, weak 0..1 = chalky spots, repair 0..1 = fluoride shimmer."""
    a = int(alpha); c.save(); c.translate(x, y)
    p = tooth_path(s)
    c.drawPath(p, P(color=col('#1b2a4a', int(a * 0.18)), blur=10))
    c.drawPath(p, lin(c, (-150 * s, 0, 150 * s, 0), [col('#e9f1fb', a), col('#ffffff', a), col('#dfe9f5', a)], vertical=False))
    if section > 0:
        sa = int(a * section)
        d = tooth_path(s * 0.8); c.save(); c.translate(0, 18 * s)
        c.drawPath(d, P(color=col('#f6e3b8', sa)))
        pu = skia.Path(); pu.addOval(skia.Rect(-55 * s, -70 * s, 55 * s, 40 * s))
        c.drawPath(pu, P(color=col('#ff9fb0', sa)))
        c.drawLine(-30 * s, 30 * s, -45 * s, 230 * s, P(color=col('#ff9fb0', sa), stroke=16 * s))
        c.drawLine(30 * s, 30 * s, 45 * s, 230 * s, P(color=col('#ff9fb0', sa), stroke=16 * s))
        c.restore()
    if weak > 0:
        rnd = random.Random(4)
        for i in range(7):
            px, py = rnd.uniform(-120, 120) * s, rnd.uniform(-150, -60) * s
            c.drawCircle(px, py, rnd.uniform(10, 18) * s, P(color=col('#f3ead8', int(a * weak * 0.9))))
    if cavity > 0:
        cx, cy = -80 * s, -140 * s
        hp = skia.Path(); hp.addOval(skia.Rect(cx - 45 * s * cavity, cy - 10 * s, cx + 45 * s * cavity, cy + 70 * s * cavity))
        c.save(); c.clipPath(p, doAntiAlias=True)
        c.drawPath(hp, P(color=col('#6b5a4a', a))); c.drawPath(hp, P(color=col('#4a3c30', a), stroke=4 * s))
        c.restore()
    if plaque > 0 or tartar > 0:
        c.save(); c.clipPath(p, doAntiAlias=True)
        film = skia.Path(); film.addRect(skia.Rect(-200 * s, -200 * s, 200 * s, 110 * s))
        c.drawPath(film, P(color=col('#f2e08a', int(a * 0.55 * plaque))))
        rnd = random.Random(9)
        for i in range(26):
            px, py = rnd.uniform(-150, 150) * s, rnd.uniform(-170, 100) * s
            c.drawCircle(px, py, rnd.uniform(5, 11) * s, P(color=col('#e8c94f', int(a * 0.7 * plaque))))
        if tartar > 0:
            band = skia.Path(); band.moveTo(-160 * s, 40 * s)
            for i in range(13):
                xx = lerp(-160, 160, i / 12) * s
                band.lineTo(xx, (60 - 18 * (i % 2)) * s)
            band.lineTo(160 * s, 115 * s); band.lineTo(-160 * s, 115 * s); band.close()
            c.drawPath(band, P(color=col('#cdb27a', int(a * tartar))))
            c.drawPath(band, P(color=col('#9c8150', int(a * tartar)), stroke=4 * s))
        c.restore()
    if repair > 0:
        for i in range(6):
            ang = t * 2 + i * 1.05; rr = 90 * s
            twinkle(c, math.cos(ang) * rr, -110 * s + math.sin(ang) * 30 * s, 16 * s, colr='#7fe0ff', alpha=int(a * repair))
    c.drawPath(p, P(color=col('#8aa0bf', a), stroke=5 * s))
    if shine > 0:
        hl = skia.Path(); hl.moveTo(-110 * s, -120 * s); hl.quadTo(-120 * s, -60 * s, -105 * s, 0)
        c.drawPath(hl, P(color=col('#ffffff', int(a * 0.9 * shine)), stroke=14 * s))
    if gum:
        g = skia.Path(); g.moveTo(-1300, 90 * s); g.lineTo(-260 * s, 90 * s)
        g.cubicTo(-200 * s, 60 * s, -150 * s, 70 * s, -120 * s, 105 * s)
        g.cubicTo(-60 * s, 140 * s, 60 * s, 140 * s, 120 * s, 105 * s)
        g.cubicTo(150 * s, 70 * s, 200 * s, 60 * s, 260 * s, 90 * s)
        g.lineTo(1300, 90 * s); g.lineTo(1300, 1400); g.lineTo(-1300, 1400); g.close()
        c.drawPath(g, lin(c, (0, 80 * s, 0, 400 * s), [col('#ff9fb3', a), col('#f07d97', a)]))
        c.drawPath(g, P(color=col('#d9607e', a), stroke=4 * s))
    c.restore()

def toothbrush(c, x, y, s=1.0, rot=0.0, alpha=255, handle='#2f9bff'):
    """Toothbrush, bristles pointing down at rot=0; (x, y) = centre of the bristle head."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect(60, -40, 520, -10), 15, 15, P(color=col(handle, a)))
    c.drawRoundRect(skia.Rect(-90, -46, 80, -14), 14, 14, P(color=col(handle, a)))
    c.drawRoundRect(skia.Rect(200, -34, 420, -18), 8, 8, P(color=col('#ffffff', int(a * 0.45))))
    for i in range(9):
        bx = -80 + i * 19
        c.drawRoundRect(skia.Rect(bx, -16, bx + 13, 40), 5, 5, P(color=col('#ffffff' if i % 2 else '#bfe6ff', a)))
        c.drawRoundRect(skia.Rect(bx, -16, bx + 13, 40), 5, 5, P(color=col('#8aa0bf', int(a * 0.6)), stroke=2))
    c.restore()

def bacterium(c, x, y, r, t, seed=0, alpha=255, colr='#9b7be0', rot=None):
    """Simple rod-shaped bacterium (no face), gently wobbling."""
    a = int(alpha); rnd = random.Random(seed)
    ang = rot if rot is not None else rnd.uniform(0, 180) + 12 * math.sin(t * 2 + seed)
    c.save(); c.translate(x, y); c.rotate(ang)
    c.drawRoundRect(skia.Rect(-r * 1.6, -r * 0.75, r * 1.6, r * 0.75), r * 0.75, r * 0.75, P(color=col(mix_hx(colr, '#000000', 0.25), a)))
    c.drawRoundRect(skia.Rect(-r * 1.5, -r * 0.62, r * 1.5, r * 0.62), r * 0.62, r * 0.62, lin(c, (0, -r, 0, r), [col(mix_hx(colr, '#ffffff', 0.35), a), col(colr, a)]))
    c.drawCircle(-r * 0.6, -r * 0.1, r * 0.18, P(color=col('#ffffff', int(a * 0.5))))
    c.restore()

def acid_drop(c, x, y, r, alpha=255, colr='#b6e83a'):
    a = int(alpha); p = skia.Path(); p.moveTo(x, y - r * 1.6)
    p.cubicTo(x + r * 0.9, y - r * 0.4, x + r, y + r, x, y + r); p.cubicTo(x - r, y + r, x - r * 0.9, y - r * 0.4, x, y - r * 1.6); p.close()
    c.drawPath(p, P(color=col(colr, a))); c.drawPath(p, P(color=col(mix_hx(colr, '#000000', 0.3), a), stroke=3))
    c.drawCircle(x - r * 0.35, y, r * 0.22, P(color=col('#ffffff', int(a * 0.6))))

# ---------------- Clouds / weight icons (added for ep_030) ----------------
def elephant(c, x, y, s, alpha=255, colr='#8f9bb3', t=0.0):
    """Plain side-view elephant icon (flat infographic style), facing right. x,y = feet baseline centre."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    dark = mix_hx(colr, '#1b2a4a', 0.25)
    for lx in (-62, -30, 28, 58):
        c.drawRoundRect(skia.Rect(lx - 15, -70, lx + 15, 0), 10, 10, P(color=col(dark if lx in (-30, 58) else colr, a)))
    body = skia.Path(); body.addOval(skia.Rect(-95, -165, 85, -45)); c.drawPath(body, P(color=col(colr, a)))
    tail = skia.Path(); tail.moveTo(-92, -120); tail.quadTo(-118, -95, -110, -70)
    c.drawPath(tail, P(color=col(dark, a), stroke=6))
    c.drawCircle(92, -150, 52, P(color=col(colr, a)))
    tr = skia.Path(); tr.moveTo(126, -150); tr.cubicTo(160, -120, 150, -70, 160, -40)
    c.drawPath(tr, P(color=col(colr, a), stroke=26))
    c.drawCircle(160, -40, 13, P(color=col(colr, a)))
    c.drawOval(skia.Rect(50, -185, 100, -105), P(color=col(dark, a)))
    tk = skia.Path(); tk.moveTo(118, -118); tk.quadTo(138, -100, 150, -104)
    c.drawPath(tk, P(color=col('#fffaf0', a), stroke=8))
    c.drawCircle(112, -162, 5, P(color=col('#1b2a4a', a)))
    c.restore()

def updraft(c, x, y0, y1, t, w=14, colr='#ffffff', alpha=200, speed=260, seed=0, spacing=150):
    """Column of rising chevron arrows between y0 (bottom) and y1 (top)."""
    span = y0 - y1
    for k in range(int(span // spacing) + 2):
        yy = y0 - ((t * speed + k * spacing + seed * 37) % (span + spacing))
        if yy < y1 - 20 or yy > y0: continue
        f = min(1.0, (y0 - yy) / 80, (yy - y1 + 20) / 80)
        xx = x + math.sin(t * 2 + k + seed) * 8
        p = skia.Path(); p.moveTo(xx - 32, yy + 22); p.lineTo(xx, yy - 10); p.lineTo(xx + 32, yy + 22)
        c.drawPath(p, P(color=col(colr, int(alpha * max(0, f))), stroke=w))

# ---------------- Bats / echolocation (added for ep_032) ----------------
def moth(c, x, y, s, t, flap=14.0, alpha=255, colr='#e8d3a8', rot=0.0):
    """Plain top-view moth (no face). Wings flutter by squashing horizontally."""
    a = int(alpha); f = 0.55 + 0.45 * abs(math.sin(t * flap))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    dark = mix_hx(colr, '#5a4632', 0.45)
    for sx in (-1, 1):
        c.save(); c.scale(sx * f, 1)
        fw = skia.Path(); fw.moveTo(6, -10); fw.cubicTo(40, -70, 110, -70, 120, -30); fw.cubicTo(115, 0, 60, 10, 6, 4); fw.close()
        hw = skia.Path(); hw.moveTo(6, 4); hw.cubicTo(60, 10, 95, 40, 80, 70); hw.cubicTo(55, 90, 20, 50, 6, 20); hw.close()
        c.drawPath(hw, P(color=col(dark, a))); c.drawPath(fw, P(color=col(colr, a)))
        c.drawPath(fw, P(color=col(dark, a), stroke=3))
        c.drawCircle(70, -30, 10, P(color=col(dark, int(a * 0.8))))
        c.restore()
    c.drawOval(skia.Rect(-10, -30, 10, 60), P(color=col(dark, a)))
    for sx in (-1, 1):
        an = skia.Path(); an.moveTo(sx * 3, -28); an.quadTo(sx * 18, -60, sx * 30, -66)
        c.drawPath(an, P(color=col(dark, a), stroke=3))
    c.restore()

def echo_map(c, pts, x, y, s, k, colr='#5ff0ff', t=0.0):
    """Shape drawn as glowing sonar dots; k = 0..1 how many dots are revealed."""
    n = int(len(pts) * k)
    for i, (px, py) in enumerate(pts[:n]):
        X, Y = x + px * s, y + py * s
        c.drawCircle(X, Y, 16, rad(X, Y, 16, [col(colr, 150), col(colr, 0)]))
        c.drawCircle(X, Y, 5.5, P(color=col('#ffffff', 235)))

# ---------------- Daytime moon, penguin, seed, ear (added for ep_034+) ----------------
_MARIA = [(-0.35, -0.3, 0.2), (0.25, -0.35, 0.16), (0.3, 0.2, 0.18), (-0.1, 0.05, 0.12), (-0.4, 0.35, 0.1), (0.05, 0.5, 0.09)]
def day_moon(c, x, y, r, phase=0.5, alpha=230, lit_dir=0.0):
    """Pale moon as seen in a blue daytime sky: only the lit part is visible, slightly see-through, with soft grey-blue maria."""
    lit = moon_lit_path(x, y, r, phase, lit_dir)
    if lit is None: return
    a = int(alpha)
    c.save(); c.clipPath(lit, doAntiAlias=True)
    c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.35, r * 1.6, [col('#ffffff', a), col('#f2f6fc', a), col('#d5e0ef', a)], [0, 0.5, 1]))
    for dx, dy, rr in _MARIA:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, P(color=col('#a9bbd6', int(a * 0.55)), blur=r * 0.03))
    c.restore()

def gray_moon(c, x, y, r, t=0.0, alpha=255, glow=0.0):
    """Realistic dark-grey moon (true colour ~ worn asphalt), craters + maria, full disc lit."""
    a = int(alpha)
    if glow > 0:
        c.drawCircle(x, y, r * 1.5, rad(x, y, r * 1.5, [col('#ffffff', int(90 * glow)), col('#ffffff', 0)]))
    c.save(); cl = skia.Path(); cl.addCircle(x, y, r); c.clipPath(cl, doAntiAlias=True)
    c.drawCircle(x, y, r, rad(x - r * 0.35, y - r * 0.35, r * 1.7, [col('#9a9a9e', a), col('#6f7075', a), col('#4a4b50', a)], [0, 0.55, 1]))
    for dx, dy, rr in _MARIA:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, P(color=col('#4e4f55', int(a * 0.8)), blur=r * 0.02))
    rnd = random.Random(7)
    for i in range(16):
        cx, cy, cr = x + rnd.uniform(-0.8, 0.8) * r, y + rnd.uniform(-0.8, 0.8) * r, rnd.uniform(0.03, 0.08) * r
        c.drawCircle(cx, cy, cr, P(color=col('#5b5c62', a)))
        c.drawArc(skia.Rect(cx - cr, cy - cr, cx + cr, cy + cr), 200, 140, False, P(color=col('#b4b5ba', int(a * 0.8)), stroke=max(1.5, cr * 0.25)))
    c.restore()
    c.drawCircle(x, y, r, P(color=col('#2e2f33', int(a * 0.6)), stroke=max(2, r * 0.02)))

def penguin(c, x, y, s, t, alpha=255, flip=False, flipper=0.0, sway=1.0, seed=0):
    """Plain emperor penguin, 3/4 view facing right (flip=True faces left). (x, y) = between the feet. Height ~ 400*s."""
    a = int(alpha)
    c.drawOval(skia.Rect(x - 120 * s, y - 14 * s, x + 120 * s, y + 14 * s), P(color=col('#0b1a3a', int(a * 0.18)), blur=6 * s))
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    c.rotate(math.sin(t * 1.6 + seed) * 2.5 * sway)
    # flippers (behind body)
    for side, base in ((-1, -235), (1, -235)):
        c.save(); c.translate(side * 108, base); c.rotate(side * (8 + 18 * flipper * (0.5 + 0.5 * math.sin(t * 9 + side))))
        fp = skia.Path(); fp.moveTo(0, 0); fp.cubicTo(side * 38, 20, side * 46, 120, side * 24, 175); fp.cubicTo(side * 14, 150, side * -4, 80, side * -6, 10); fp.close()
        c.drawPath(fp, lin(c, (0, 0, 0, 175), [col('#2a3142', a), col('#141821', a)])); c.restore()
    body = skia.Path(); body.moveTo(0, -335)
    body.cubicTo(112, -325, 142, -160, 122, -45); body.cubicTo(110, 4, -110, 4, -122, -45); body.cubicTo(-142, -160, -112, -325, 0, -335); body.close()
    c.drawPath(body, lin(c, (-130, 0, 130, 0), [col('#151922', a), col('#2b3345', a)], vertical=False))
    belly = skia.Path(); belly.moveTo(18, -300)
    belly.cubicTo(92, -290, 112, -150, 96, -50); belly.cubicTo(80, -8, -52, -8, -74, -50); belly.cubicTo(-90, -150, -58, -290, 18, -300); belly.close()
    c.drawPath(belly, lin(c, (0, -300, 0, -20), [col('#fff1b8', a), col('#ffffff', a), col('#e7edf5', a)], pos=[0, 0.3, 1]))
    c.drawPath(belly, P(color=col('#c9d3e0', int(a * 0.6)), stroke=3))
    # head
    c.drawCircle(8, -338, 66, rad(-10, -370, 90, [col('#2b3345', a), col('#151922', a)]))
    # golden ear patch
    ep = skia.Path(); ep.moveTo(36, -318); ep.cubicTo(70, -320, 78, -290, 62, -262); ep.cubicTo(50, -276, 34, -292, 36, -318); ep.close()
    c.drawPath(ep, lin(c, (0, -320, 0, -262), [col('#ffb020', a), col('#ffe38a', a)]))
    # beak
    bk = skia.Path(); bk.moveTo(52, -350); bk.cubicTo(90, -352, 118, -340, 134, -326); bk.cubicTo(110, -328, 80, -326, 54, -326); bk.close()
    c.drawPath(bk, P(color=col('#1a1d24', a)))
    c.drawLine(64, -329, 118, -328, P(color=col('#ff8a3d', a), stroke=6))
    # eye (natural, small)
    c.drawCircle(40, -352, 7, P(color=col('#07080c', a)))
    c.drawCircle(42, -354, 2.2, P(color=col('#ffffff', int(a * 0.8))))
    # feet
    for fx in (-38, 42):
        c.drawOval(skia.Rect(fx - 34, -12, fx + 34, 10), P(color=col('#2a2f3a', a)))
    c.restore()

def penguin_top(c, x, y, s, rot=0.0, alpha=255):
    """Penguin seen from above (for huddles): dark oval back, head with golden patches, beak pointing to rot (degrees)."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawOval(skia.Rect(-34, -26, 34, 26), P(color=col('#000000', int(a * 0.15)), blur=4))
    c.drawOval(skia.Rect(-36, -28, 30, 28), lin(c, (0, -28, 0, 28), [col('#2b3345', a), col('#151922', a)]))
    c.drawCircle(30, 0, 17, P(color=col('#1d2230', a)))
    for sy in (-1, 1):
        c.drawOval(skia.Rect(24, sy * 12 - 5, 36, sy * 12 + 5), P(color=col('#ffc23a', a)))
    c.drawLine(44, 0, 58, 0, P(color=col('#1a1d24', a), stroke=6))
    c.restore()

def bean_path(s=1.0, swell=0.0):
    """Kidney-shaped bean outline centred at 0,0 (about 200x130 at s=1; swell enlarges ~25 %)."""
    k = s * (1 + 0.25 * swell)
    p = skia.Path(); p.moveTo(-100 * k, -10 * k)
    p.cubicTo(-100 * k, -75 * k, 100 * k, -80 * k, 100 * k, -5 * k)
    p.cubicTo(100 * k, 60 * k, 30 * k, 70 * k, 10 * k, 42 * k)
    p.cubicTo(0, 30 * k, -20 * k, 30 * k, -30 * k, 45 * k)
    p.cubicTo(-60 * k, 75 * k, -100 * k, 50 * k, -100 * k, -10 * k)
    p.close(); return p

def bean_seed(c, x, y, s, t=0.0, swell=0.0, crack=0.0, section=0.0, rot=0.0, alpha=255, coat='#c46a4a'):
    """Bean seed. section 0..1 fades in the cut-away (coat ring, food store, embryo). crack splits the coat."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(rot)
    p = bean_path(s, swell); k = s * (1 + 0.25 * swell)
    c.drawPath(p, rad(-40 * k, -40 * k, 160 * k, [col('#e8907a', a), col(coat, a), col('#8e4430', a)], [0, 0.5, 1]))
    if section > 0:
        inner = bean_path(s * 0.86, swell); inner.offset(0, 2 * k)
        c.drawPath(inner, rad(-30 * k, -30 * k, 140 * k, [col('#fff6d6', int(a * section)), col('#f5deaa', int(a * section))]))
        # embryo near the hilum (inner curve)
        ep = skia.Path(); ep.moveTo(-14 * k, 26 * k); ep.cubicTo(-40 * k, 10 * k, -46 * k, -20 * k, -30 * k, -36 * k)
        c.drawPath(ep, P(color=col('#b5d36a', int(a * section)), stroke=14 * k))
        for sd in (-1, 1):
            lp = skia.Path(); lp.moveTo(-30 * k, -36 * k); lp.quadTo(-30 * k + sd * 22 * k, -60 * k, -30 * k + sd * 6 * k, -62 * k); lp.quadTo(-30 * k + sd * 4 * k, -46 * k, -30 * k, -36 * k)
            c.drawPath(lp, P(color=col('#8fc24a', int(a * section))))
        c.drawPath(inner, P(color=col('#d9b77a', int(a * section)), stroke=3))
    else:
        c.drawOval(skia.Rect(-8 * k, 30 * k, 26 * k, 42 * k), P(color=col('#5a2a1c', int(a * 0.8))))
    c.drawOval(skia.Rect(-60 * k, -50 * k, 10 * k, -28 * k), P(color=col('#ffffff', int(a * 0.35)), blur=4 * k))
    if crack > 0:
        cp = skia.Path(); cp.moveTo(-80 * k, -30 * k)
        pts = [(-50, -48), (-20, -40), (10, -55), (40, -44), (70, -52)]
        n = max(1, int(len(pts) * crack + 0.999))
        for px, py in pts[:n]: cp.lineTo(px * k, py * k)
        c.drawPath(cp, P(color=col('#fff6d6', a), stroke=7 * k))
        c.drawPath(cp, P(color=col('#5a2a1c', a), stroke=2.5 * k))
    c.drawPath(p, P(color=col('#6e321f', int(a * 0.7)), stroke=3 * k))
    c.restore()

def seedling(c, x, y, s, t, root=0.0, shoot=0.0, unhook=0.0, leaves=0.0, hairs=0.0, root_dir=90.0, alpha=255):
    """Germinating seedling growing from (x, y) (the seed). root: 0..1 primary root length (curves to straight down),
    shoot: 0..1 stem length (up), unhook: 0 = hooked tip (in soil), 1 = straight; leaves: 0..1 first leaves open."""
    a = int(alpha)
    if root > 0:
        L = 420 * s * root; p = skia.Path(); p.moveTo(x, y)
        d0 = math.radians(root_dir); n = 24; px, py = x, y
        for i in range(1, n + 1):
            u = i / n; ang = lerp(d0, math.pi / 2, ease_out(min(1, u * 1.4)))
            px += math.cos(ang) * L / n; py += math.sin(ang) * L / n; p.lineTo(px, py)
        c.drawPath(p, P(color=col('#e9d6a8', a), stroke=16 * s)); c.drawPath(p, P(color=col('#fff4d8', a), stroke=8 * s))
        if hairs > 0:
            meas = skia.PathMeasure(p, False); LL = meas.getLength()
            for j in range(14):
                d = LL * (0.25 + 0.7 * j / 14)
                pos, tan = meas.getPosTan(d)
                if pos is None: continue
                (qx, qy), (tx, ty) = pos, tan
                sd = 1 if j % 2 else -1; hl = 46 * s * hairs * (1 - j / 20)
                c.drawLine(qx, qy, qx + (-ty * sd) * hl + tx * hl * 0.5, qy + (tx * sd) * hl + ty * hl * 0.5, P(color=col('#f3e6c2', int(a * 0.9)), stroke=4 * s))
    if shoot > 0:
        Hh = 380 * s * shoot
        sw = math.sin(t * 1.3) * 6 * s * unhook
        top = (x + sw, y - Hh)
        stem = skia.Path(); stem.moveTo(x, y); stem.quadTo(x, y - Hh * 0.6, top[0], top[1])
        hook_ang = (1 - unhook) * 160
        hr = 34 * s
        # hook: arc continuing from the top, bending the tip back down
        hp = skia.Path(); hp.moveTo(*top); steps = 10; hx, hy = top
        for i in range(1, steps + 1):
            ang = math.radians(-90 + hook_ang * i / steps)
            hx += math.cos(ang) * hr * math.radians(max(hook_ang, 1)) / steps * 1.0 if hook_ang > 1 else 0
            hy += math.sin(ang) * hr * math.radians(max(hook_ang, 1)) / steps * 1.0 if hook_ang > 1 else 0
            hp.lineTo(hx, hy)
        for pth in (stem, hp):
            c.drawPath(pth, P(color=col('#3f8f2e', a), stroke=22 * s)); c.drawPath(pth, P(color=col('#7ed957', a), stroke=12 * s))
        tipx, tipy = (hx, hy) if hook_ang > 1 else top
        if leaves > 0:
            for sd in (-1, 1):
                leaf(c, tipx + sd * 90 * s * leaves, tipy - 30 * s * leaves, s * 1.05 * leaves, t, colr='#5cc94a', seed=3 + sd,
                     face_on=False, rot=sd * (70 - 10 * leaves) + math.sin(t * 1.5 + sd) * 3, alpha=a)
        else:
            c.drawOval(skia.Rect(tipx - 14 * s, tipy - 10 * s, tipx + 14 * s, tipy + 10 * s), P(color=col('#b5e06a', a)))

def palm_sapling(c, x, y, s, t, alpha=255):
    """Young date palm: short trunk with arching fronds. (x, y) = base."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-22, -180, 22, 0), 14, 14, lin(c, (-22, 0, 22, 0), [col('#a8794e', a), col('#7a5333', a)], vertical=False))
    for i in range(6):
        c.drawLine(-22, -30 - i * 28, 22, -38 - i * 28, P(color=col('#5e3f26', int(a * 0.6)), stroke=3))
    for i, ang in enumerate((-160, -130, -100, -80, -50, -20)):
        sw = math.sin(t * 1.2 + i) * 4
        ar = math.radians(ang + sw); L = 230
        ex, ey = math.cos(ar) * L, -180 + math.sin(ar) * L * 0.8
        mx, my = math.cos(ar) * L * 0.5, -180 + math.sin(ar) * L * 0.8 - 70
        fp = skia.Path(); fp.moveTo(0, -180); fp.quadTo(mx, my, ex, ey)
        c.drawPath(fp, P(color=col('#3f8f2e', a), stroke=8))
        meas = skia.PathMeasure(fp, False); LL = meas.getLength()
        for j in range(1, 12):
            pos, tan = meas.getPosTan(LL * j / 12)
            if pos is None: continue
            (qx, qy), (tx, ty) = pos, tan
            for sd in (-1, 1):
                ll = 44 * (1 - j / 14)
                c.drawLine(qx, qy, qx - ty * sd * ll + tx * ll * 0.6, qy + tx * sd * ll + ty * ll * 0.6 + ll * 0.3, P(color=col('#5cc94a', a), stroke=7))
    c.restore()

def cochlea_path(cx, cy, r0=110, turns=2.6, r1=18, steps=120):
    p = skia.Path()
    for i in range(steps + 1):
        u = i / steps; a = math.pi * 0.95 + u * turns * 2 * math.pi; r = lerp(r0, r1, u)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        (p.moveTo if i == 0 else p.lineTo)(x, y)
    return p

def stirrup(c, x, y, s=1.0, rot=0.0, alpha=255, fill='#fffaf0', edge='#b08a5a'):
    """Stapes (stirrup bone): head at left, two arches, footplate at right. (x, y) = centre; ~150*s long."""
    a = int(alpha)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    outer = skia.Path(); outer.moveTo(-75, 0); outer.cubicTo(-40, -50, 40, -58, 62, -46); outer.lineTo(62, 46); outer.cubicTo(40, 58, -40, 50, -75, 0); outer.close()
    inner = skia.Path(); inner.moveTo(-48, 0); inner.cubicTo(-24, -30, 30, -36, 50, -30); inner.lineTo(50, 30); inner.cubicTo(30, 36, -24, 30, -48, 0); inner.close()
    ring = skia.Op(outer, inner, skia.PathOp.kDifference_PathOp)
    c.drawPath(ring, lin(c, (0, -58, 0, 58), [col(fill, a), col('#efe0c4', a)]))
    c.drawPath(ring, P(color=col(edge, a), stroke=3.5))
    c.drawRoundRect(skia.Rect(56, -62, 76, 62), 8, 8, P(color=col(fill, a)))
    c.drawRoundRect(skia.Rect(56, -62, 76, 62), 8, 8, P(color=col(edge, a), stroke=3.5))
    c.drawCircle(-80, 0, 14, P(color=col(fill, a))); c.drawCircle(-80, 0, 14, P(color=col(edge, a), stroke=3.5))
    c.restore()

def ear_section(c, ox, oy, s, t, drum=0.0, bones=0.0, fluid=0.0, nerve=0.0, hi=None, alpha=255):
    """Cross-section of the ear, ~1000 x 700 units at s=1, (ox, oy) = left-middle. drum/bones/fluid 0..1 = vibration
    amount of eardrum / ossicles / cochlea fluid; nerve 0..1 = signal pulses along the hearing nerve.
    hi: optional set of part names to highlight ('pinna', 'canal', 'drum', 'bones', 'cochlea', 'nerve')."""
    a = int(alpha); hi = hi or set()
    c.save(); c.translate(ox, oy); c.scale(s, s)
    # head tissue
    head = skia.Path(); head.moveTo(170, -340); head.lineTo(940, -340); head.quadTo(1010, -340, 1010, -270); head.lineTo(1010, 270); head.quadTo(1010, 340, 940, 340); head.lineTo(170, 340)
    head.cubicTo(200, 200, 200, -200, 170, -340); head.close()
    c.drawPath(head, lin(c, (170, 0, 1010, 0), [col('#f6cdb0', a), col('#f2c09f', a)], vertical=False))
    # skull bone region around middle/inner ear
    c.drawRoundRect(skia.Rect(500, -250, 1010, 250), 120, 120, P(color=col('#f3e7d3', a)))
    # pinna
    pin = skia.Path(); pin.moveTo(190, -310); pin.cubicTo(60, -330, -10, -160, 30, -40)
    pin.cubicTo(50, 40, 110, 70, 120, 150); pin.cubicTo(128, 230, 160, 300, 200, 290); pin.lineTo(200, -310); pin.close()
    c.drawPath(pin, lin(c, (0, 0, 200, 0), [col('#f0b08a', a), col('#f6c6a4', a)], vertical=False))
    fold = skia.Path(); fold.moveTo(170, -250); fold.cubicTo(90, -250, 60, -140, 90, -60)
    c.drawPath(fold, P(color=col('#d98d6a', int(a * 0.8)), stroke=10))
    if 'pinna' in hi: c.drawPath(pin, P(color=col('#ffd23f', a), stroke=8))
    # ear canal
    can = skia.Path(); can.moveTo(150, -46); can.cubicTo(300, -60, 420, -30, 520, -40); can.lineTo(520, 40)
    can.cubicTo(420, 34, 300, 60, 150, 46); can.close()
    c.drawPath(can, P(color=col('#fff2e6', a)))
    c.drawPath(can, P(color=col('#c98a6b', a), stroke=4))
    if 'canal' in hi: c.drawPath(can, P(color=col('#ffd23f', a), stroke=8))
    # middle ear cavity
    c.drawOval(skia.Rect(520, -150, 740, 130), P(color=col('#fff8ee', a)))
    c.drawOval(skia.Rect(520, -150, 740, 130), P(color=col('#d8c3a0', a), stroke=3))
    # eardrum
    bulge = drum * 10 * math.sin(t * 40)
    dp = skia.Path(); dp.moveTo(522, -62); dp.quadTo(530 + bulge * 2, 0, 522, 62)
    c.drawPath(dp, P(color=col('#ff7f9a', a), stroke=9))
    if 'drum' in hi: c.drawCircle(526, 0, 80, rad(526, 0, 80, [col('#ffd23f', int(a * 0.6)), col('#ffd23f', 0)]))
    # ossicles
    rock = bones * 4 * math.sin(t * 40)
    bf, be = '#fffaf0', '#b08a5a'
    c.save(); c.translate(560, -110); c.rotate(rock)
    mal = skia.Path(); mal.addCircle(0, 0, 22); mal.moveTo(-8, 10); mal.lineTo(-30, 100); mal.lineTo(-20, 104); mal.lineTo(10, 14); mal.close()
    c.drawPath(mal, P(color=col(bf, a))); c.drawPath(mal, P(color=col(be, a), stroke=3))
    c.restore()
    c.save(); c.translate(600, -100); c.rotate(-rock)
    inc = skia.Path(); inc.addOval(skia.Rect(-20, -24, 26, 22)); inc.moveTo(4, 14); inc.lineTo(20, 80); inc.lineTo(32, 76); inc.lineTo(20, 10); inc.close()
    c.drawPath(inc, P(color=col(bf, a))); c.drawPath(inc, P(color=col(be, a), stroke=3))
    c.restore()
    stirrup(c, 668 + rock * 1.5, -6, 0.42, rot=10, alpha=a)
    if 'bones' in hi: c.drawCircle(610, -60, 120, rad(610, -60, 120, [col('#ffd23f', int(a * 0.55)), col('#ffd23f', 0)]))
    # semicircular canals
    for i, (cx, cy, r) in enumerate(((760, -150, 50), (810, -170, 44), (850, -130, 40))):
        c.drawCircle(cx, cy, r, P(color=col('#a8dcff', int(a * 0.9)), stroke=16))
        c.drawCircle(cx, cy, r, P(color=col('#5a9fd6', int(a * 0.6)), stroke=2))
    # cochlea
    cp = cochlea_path(840, 40)
    c.drawPath(cp, P(color=col('#5a9fd6', a), stroke=40))
    c.drawPath(cp, P(color=col('#a8e0ff', a), stroke=32))
    if fluid > 0:
        meas = skia.PathMeasure(cp, False); L = meas.getLength()
        for j in range(18):
            u = ((t * 0.5 + j / 18) % 1.0)
            pos, _ = meas.getPosTan(L * u)
            if pos is None: continue
            rr = 6 + 4 * math.sin(t * 12 + j); px_, py_ = pos
            c.drawCircle(px_, py_, rr, P(color=col('#ffffff', int(a * fluid * 0.9))))
    if 'cochlea' in hi: c.drawCircle(840, 40, 170, rad(840, 40, 170, [col('#ffd23f', int(a * 0.5)), col('#ffd23f', 0)]))
    # hearing nerve
    np_ = skia.Path(); np_.moveTo(860, 40); np_.cubicTo(920, 60, 960, 120, 1010, 130)
    c.drawPath(np_, P(color=col('#ffd23f', a), stroke=18)); c.drawPath(np_, P(color=col('#e0a800', a), stroke=4))
    if nerve > 0:
        meas = skia.PathMeasure(np_, False); L = meas.getLength()
        for j in range(3):
            u = ((t * 1.2 + j / 3) % 1.0); pos, _ = meas.getPosTan(L * u)
            if pos is not None:
                px_, py_ = pos
                c.drawCircle(px_, py_, 16, rad(px_, py_, 16, [col('#ffffff', int(a * nerve)), col('#fff36b', 0)]))
    c.restore()

# ---------------- props added 2026-11-24 (gravity, whales, owls, meteors) ----------------
def apple(c, x, y, r, rot=0.0, alpha=255):
    """Plain red apple, (x, y) = centre, radius r."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(0, -r * 0.72)
    p.cubicTo(r * 0.45, -r * 1.05, r * 1.08, -r * 0.75, r * 1.0, -r * 0.05)
    p.cubicTo(r * 0.95, r * 0.6, r * 0.55, r * 1.0, r * 0.2, r * 0.95)
    p.cubicTo(r * 0.08, r * 0.92, -r * 0.08, r * 0.92, -r * 0.2, r * 0.95)
    p.cubicTo(-r * 0.55, r * 1.0, -r * 0.95, r * 0.6, -r * 1.0, -r * 0.05)
    p.cubicTo(-r * 1.08, -r * 0.75, -r * 0.45, -r * 1.05, 0, -r * 0.72); p.close()
    c.drawPath(p, rad(-r * 0.35, -r * 0.35, r * 1.5, [col('#ff8a8a', a), col('#e8323c', a), col('#a8172a', a)], [0, 0.5, 1]))
    c.drawOval(skia.Rect(-r * 0.6, -r * 0.55, -r * 0.25, -r * 0.1), P(color=col('#ffffff', int(a * 0.45)), blur=r * 0.05))
    c.drawLine(0, -r * 0.7, r * 0.1, -r * 1.12, P(color=col('#6e4a2c', a), stroke=r * 0.1))
    lp = skia.Path(); lp.moveTo(r * 0.08, -r * 0.98); lp.cubicTo(r * 0.3, -r * 1.3, r * 0.65, -r * 1.2, r * 0.7, -r * 1.05)
    lp.cubicTo(r * 0.5, -r * 0.92, r * 0.25, -r * 0.92, r * 0.08, -r * 0.98); lp.close()
    c.drawPath(lp, lin(c, (0, -r * 1.25, 0, -r * 0.9), [col('#7ed957', a), col('#3f9e3a', a)]))
    c.restore()

def hammer(c, x, y, s=1.0, rot=0.0, alpha=255):
    """Geologist's hammer, (x, y) = centre of mass (near the head). Length ~ 330*s."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-14, -40, 14, 260), 12, 12, lin(c, (-14, 0, 14, 0), [col('#e8b77a', a), col('#b77f45', a)], vertical=False))
    c.drawRoundRect(skia.Rect(-16, 190, 16, 262), 12, 12, P(color=col('#1b2a4a', a)))
    hp = skia.Path(); hp.moveTo(-60, -62); hp.lineTo(30, -62); hp.lineTo(120, -40); hp.lineTo(120, -30); hp.lineTo(30, -22)
    hp.lineTo(-60, -22); hp.close()
    c.drawPath(hp, lin(c, (0, -62, 0, -22), [col('#e3e8f0', a), col('#9aa6b8', a), col('#6f7c90', a)], pos=[0, 0.5, 1]))
    c.drawRoundRect(skia.Rect(-72, -66, -40, -18), 6, 6, lin(c, (0, -66, 0, -18), [col('#d6dde8', a), col('#7d8aa0', a)]))
    c.drawPath(hp, P(color=col('#4a5568', int(a * 0.7)), stroke=2.5))
    c.restore()

def quill(c, x, y, s=1.0, rot=0.0, t=0.0, alpha=255, colr='#ffffff', edge='#b9c6d8'):
    """Plain white bird feather (falcon-style), (x, y) = centre, length ~ 300*s."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    v = skia.Path(); v.moveTo(0, -150)
    v.cubicTo(40, -120, 52, -20, 40, 60); v.cubicTo(32, 100, 14, 120, 4, 120)
    v.lineTo(-4, 120); v.cubicTo(-30, 100, -44, 40, -40, -40); v.cubicTo(-36, -100, -18, -140, 0, -150); v.close()
    c.drawPath(v, lin(c, (-44, 0, 52, 0), [col('#e9eef6', a), col(colr, a), col('#dfe6f0', a)], vertical=False, pos=[0, 0.5, 1]))
    for i in range(9):
        yy = -110 + i * 24
        c.drawLine(0, yy + 8, 38 - abs(i - 4) * 2, yy - 10, P(color=col(edge, int(a * 0.55)), stroke=2))
        c.drawLine(0, yy + 8, -34 + abs(i - 4) * 2, yy - 10, P(color=col(edge, int(a * 0.55)), stroke=2))
    for (yy, side) in ((-30, 1), (40, -1)):
        nk = skia.Path(); nk.moveTo(side * 44, yy); nk.lineTo(side * 26, yy + 8); nk.lineTo(side * 42, yy + 14)
        c.drawPath(nk, P(color=col('#cfd8e6', a), stroke=3))
    c.drawPath(v, P(color=col(edge, a), stroke=2.5))
    c.drawLine(0, -146, 0, 165, P(color=col('#c9b27a', a), stroke=5))
    c.restore()

def whale_blow(c, x, y, s, k, t=0.0, alpha=255):
    """Misty V-shaped spout rising from (x, y). k 0..1 = life of the blow (rises, spreads, fades)."""
    if k <= 0 or k >= 1: return
    a = alpha * (1 - k) ** 0.7 * min(1, k * 8)
    h = 380 * s * ease_out(min(1, k * 1.6))
    rnd = random.Random(5)
    for side in (-1, 1):
        for i in range(14):
            u = i / 13
            px = x + side * (30 + 120 * u) * s * (0.4 + 0.6 * k) + rnd.uniform(-10, 10) * s
            py = y - h * u - 10 * s
            rr = (26 + 70 * u) * s * (0.6 + 0.6 * k)
            c.drawCircle(px, py, rr, P(color=col('#ffffff', int(a * (0.85 - 0.45 * u))), blur=rr * 0.4))
    for i in range(10):
        dx = rnd.uniform(-160, 160) * s * k; dy = -h * rnd.uniform(0.3, 1.1) + 200 * s * k * k
        c.drawCircle(x + dx, y + dy, 5 * s, P(color=col('#d8f0ff', int(a * 0.8))))

def whale(c, x, y, s, t, alpha=255, flip=False, swim=1.0, mouth=0.0, eye=True, colr='#2f5d8f', belly='#d6e6f2'):
    """Plain blue whale, side view facing right (flip faces left). (x, y) = body centre; length ~ 900*s.
    Blowhole (local) at (190, -96) -> use whale_hole(x, y, s, flip) for screen position."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    bob = math.sin(t * 1.8) * swim
    # flukes (behind the body)
    c.save(); c.translate(-420, 0); c.rotate(10 * bob)
    fl = skia.Path(); fl.moveTo(10, -6); fl.cubicTo(-40, -20, -90, -80, -130, -78); fl.cubicTo(-110, -50, -95, -18, -70, 0)
    fl.cubicTo(-95, 18, -110, 50, -130, 78); fl.cubicTo(-90, 80, -40, 20, 10, 6); fl.close()
    c.drawPath(fl, lin(c, (0, -80, 0, 80), [col(mix_hx(colr, '#000000', 0.15), a), col(colr, a), col(mix_hx(colr, '#000000', 0.25), a)]))
    c.restore()
    body = skia.Path(); body.moveTo(455, 12)
    body.cubicTo(440, -58, 320, -98, 160, -98); body.cubicTo(0, -98, -220, -70, -340, -28)
    body.cubicTo(-380, -14, -410, -10, -425, -7 + 6 * bob); body.lineTo(-425, 7 + 6 * bob)
    body.cubicTo(-380, 18, -300, 40, -120, 78); body.cubicTo(60, 98, 320, 96, 455, 12); body.close()
    c.drawPath(body, lin(c, (0, -100, 0, 100), [col(mix_hx(colr, '#000000', 0.12), a), col(colr, a), col(mix_hx(colr, belly, 0.55), a), col(belly, a)], pos=[0, 0.35, 0.68, 1]))
    # mottled skin
    rnd = random.Random(11)
    for i in range(26):
        mx, my = rnd.uniform(-300, 380), rnd.uniform(-80, 10)
        c.drawOval(skia.Rect(mx - 9, my - 5, mx + 9, my + 5), P(color=col('#ffffff', int(a * 0.10))))
    # throat pleats
    c.save(); c.clipPath(body, doAntiAlias=True)
    for i in range(7):
        yy = 40 + i * 9
        pl = skia.Path(); pl.moveTo(430, 22 + i * 6); pl.cubicTo(320, yy + 8, 160, yy + 22, 20, yy + 26)
        c.drawPath(pl, P(color=col(mix_hx(belly, colr, 0.45), int(a * 0.7)), stroke=2.5))
    c.restore()
    # mouth line
    m = skia.Path(); m.moveTo(452, 14); m.cubicTo(400, 22 + 20 * mouth, 300, 28 + 20 * mouth, 225, 24)
    c.drawPath(m, P(color=col('#14294a', a), stroke=4))
    # dorsal fin
    df = skia.Path(); df.moveTo(-230, -62); df.cubicTo(-245, -82, -262, -96, -290, -100); df.cubicTo(-280, -80, -280, -60, -290, -48); df.close()
    c.drawPath(df, P(color=col(mix_hx(colr, '#000000', 0.12), a)))
    # flipper
    c.save(); c.translate(150, 58); c.rotate(14 + 6 * math.sin(t * 1.8 + 1) * swim)
    fp = skia.Path(); fp.moveTo(0, -8); fp.cubicTo(-30, 20, -110, 60, -150, 70); fp.cubicTo(-110, 40, -50, 10, 0, 10); fp.close()
    c.drawPath(fp, lin(c, (0, -8, 0, 70), [col(colr, a), col(mix_hx(colr, '#000000', 0.25), a)]))
    c.restore()
    # blowhole splash guard + nostrils
    c.drawOval(skia.Rect(170, -104, 210, -92), P(color=col(mix_hx(colr, '#000000', 0.3), a)))
    if eye:
        c.drawCircle(250, 30, 7, P(color=col('#0b1426', a)))
        c.drawCircle(252, 28, 2.2, P(color=col('#ffffff', int(a * 0.7))))
    c.drawPath(body, P(color=col('#14294a', int(a * 0.35)), stroke=3))
    c.restore()

def whale_hole(x, y, s, flip=False):
    return (x + (-190 if flip else 190) * s, y - 98 * s)

def lungs(c, x, y, s, fill=1.0, alpha=255, air='#2f9bff', fresh=None):
    """Simple pair of lungs (infographic). fill 0..1 = how much is filled with fresh air (from bottom)."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawLine(0, -170, 0, -90, P(color=col('#c9d3e0', a), stroke=22))
    for side in (-1, 1):
        c.drawLine(0, -95, side * 50, -60, P(color=col('#c9d3e0', a), stroke=16))
        p = skia.Path(); p.moveTo(side * 22, -110)
        p.cubicTo(side * 120, -130, side * 160, -20, side * 150, 90); p.cubicTo(side * 145, 140, side * 60, 150, side * 25, 120)
        p.cubicTo(side * 15, 40, side * 18, -40, side * 22, -110); p.close()
        c.drawPath(p, lin(c, (0, -130, 0, 150), [col('#ffd0dc', a), col('#f49ab2', a)]))
        if fill > 0:
            c.save(); c.clipPath(p, doAntiAlias=True)
            top = lerp(150, -135, fill)
            c.drawRect(skia.Rect(-170, top, 170, 160), P(color=col(fresh or air, int(a * 0.55))))
            c.restore()
        c.drawPath(p, P(color=col('#c0607a', a), stroke=5))
    c.restore()

def owl(c, x, y, s, t, yaw=0.0, alpha=255, blink=True, body='#a8774a', face='#f3e6cc', eyes='#ffc21f'):
    """Plain owl perched, front view. (x, y) = feet. Height ~ 560*s. yaw = head turn in degrees (0 = facing viewer,
    90 = profile to the right, 180 = back of head, 270 = profile to the left); the body stays put."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    dark = mix_hx(body, '#000000', 0.3); light = mix_hx(body, '#ffffff', 0.35)
    # tail
    tp = skia.Path(); tp.moveTo(-50, -40); tp.lineTo(50, -40); tp.lineTo(36, 40); tp.lineTo(-36, 40); tp.close()
    c.drawPath(tp, P(color=col(dark, a)))
    # body
    bp = skia.Path(); bp.moveTo(0, -330); bp.cubicTo(150, -330, 175, -150, 150, -60); bp.cubicTo(130, 10, -130, 10, -150, -60)
    bp.cubicTo(-175, -150, -150, -330, 0, -330); bp.close()
    c.drawPath(bp, lin(c, (0, -330, 0, 0), [col(body, a), col(mix_hx(body, '#000000', 0.12), a)]))
    chest = skia.Path(); chest.moveTo(0, -290); chest.cubicTo(95, -285, 110, -140, 92, -70); chest.cubicTo(70, -20, -70, -20, -92, -70)
    chest.cubicTo(-110, -140, -95, -285, 0, -290); chest.close()
    c.drawPath(chest, lin(c, (0, -290, 0, -20), [col(face, a), col(mix_hx(face, body, 0.25), a)]))
    c.save(); c.clipPath(chest, doAntiAlias=True)
    for r_ in range(6):
        for k in range(5):
            cx = -80 + k * 40 + (20 if r_ % 2 else 0); cy = -250 + r_ * 36
            v = skia.Path(); v.moveTo(cx - 10, cy - 4); v.lineTo(cx, cy + 6); v.lineTo(cx + 10, cy - 4)
            c.drawPath(v, P(color=col(dark, int(a * 0.7)), stroke=4))
    c.restore()
    # folded wings
    for side in (-1, 1):
        wp = skia.Path(); wp.moveTo(side * 120, -280); wp.cubicTo(side * 185, -230, side * 185, -90, side * 120, -10)
        wp.cubicTo(side * 105, -60, side * 100, -200, side * 120, -280); wp.close()
        c.drawPath(wp, lin(c, (0, -280, 0, -10), [col(mix_hx(body, '#000000', 0.08), a), col(dark, a)]))
        for i in range(4):
            yy = -200 + i * 45
            c.drawLine(side * 125, yy, side * 165, yy + 20, P(color=col(light, int(a * 0.6)), stroke=4))
    # feet
    for fx in (-40, 40):
        for d in (-14, 0, 14):
            c.drawLine(fx, -14, fx + d, 8, P(color=col('#6b5a3a', a), stroke=9))
    # head
    hy, R = -390, 150
    ya = math.radians(yaw); sy, cy_ = math.sin(ya), math.cos(ya)
    head = skia.Path(); head.addOval(skia.Rect(-R * 1.05, hy - R, R * 1.05, hy + R * 0.95))
    c.drawPath(head, rad(-30, hy - 60, R * 1.6, [col(mix_hx(body, '#ffffff', 0.12), a), col(body, a), col(dark, a)], [0, 0.6, 1]))
    c.save(); c.clipPath(head, doAntiAlias=True)
    # back-of-head speckles shift with the turn
    rnd = random.Random(3)
    for i in range(40):
        ang = rnd.uniform(0, 2 * math.pi); ry = rnd.uniform(-0.85, 0.85)
        ca = math.cos(ang + ya)
        if ca > 0.15: continue  # on the visible back half only
        sx_ = math.sin(ang + ya) * R * math.sqrt(1 - ry * ry)
        c.drawOval(skia.Rect(sx_ - 6, hy + ry * R - 3, sx_ + 6, hy + ry * R + 3), P(color=col(light, int(a * 0.5 * min(1, -ca * 3 + 0.5)))))
    if cy_ > 0.02:
        k = cy_
        dx = sy * R * 0.62
        c.save(); c.translate(dx, hy + 10); c.scale(max(0.05, k), 1)
        disc = skia.Path(); disc.moveTo(0, -95)
        disc.cubicTo(70, -140, 140, -80, 125, 0); disc.cubicTo(110, 90, 40, 115, 0, 120)
        disc.cubicTo(-40, 115, -110, 90, -125, 0); disc.cubicTo(-140, -80, -70, -140, 0, -95); disc.close()
        c.drawPath(disc, rad(0, 0, 150, [col(face, a), col(mix_hx(face, body, 0.3), a)], [0.6, 1]))
        c.drawPath(disc, P(color=col(dark, int(a * 0.6)), stroke=5))
        bl = 1.0
        if blink:
            ph = (t + 0.7) % 4.3
            if ph < 0.14: bl = max(0.08, abs(ph - 0.07) / 0.07)
        for ex in (-55, 55):
            c.drawCircle(ex, -10, 40, P(color=col(mix_hx(face, dark, 0.35), a)))
            c.save(); c.translate(ex, -10); c.scale(1, bl)
            c.drawCircle(0, 0, 33, rad(0, 0, 33, [col(eyes, a), col(mix_hx(eyes, '#d07a00', 0.6), a)], [0.5, 1]))
            c.drawCircle(0, 0, 17, P(color=col('#0b0b10', a)))
            c.drawCircle(-8, -9, 6, P(color=col('#ffffff', int(a * 0.85))))
            c.restore()
        bk = skia.Path(); bk.moveTo(-14, 30); bk.lineTo(14, 30); bk.cubicTo(10, 50, 4, 66, 0, 74); bk.cubicTo(-4, 66, -10, 50, -14, 30); bk.close()
        c.drawPath(bk, lin(c, (0, 30, 0, 74), [col('#5a4a3a', a), col('#2e2620', a)]))
        c.restore()
    c.restore()
    c.drawPath(head, P(color=col(dark, int(a * 0.5)), stroke=4))
    c.restore()

def owl_eye_section(c, x, y, s, alpha=255, label_colr='#1b2a4a'):
    """Cross-section of an owl's tubular eye held by a ring of bone (sclerotic ring). (x, y) = centre, front faces up."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-70, -120); p.cubicTo(-70, -175, 70, -175, 70, -120)
    p.lineTo(80, -40); p.cubicTo(170, -20, 190, 120, 120, 180); p.cubicTo(60, 230, -60, 230, -120, 180)
    p.cubicTo(-190, 120, -170, -20, -80, -40); p.close()
    c.drawPath(p, rad(0, 80, 220, [col('#fff6e0', a), col('#f3dcb0', a)]))
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawArc(skia.Rect(-175, -10, 175, 230), 0, 180, False, P(color=col('#ff8fa6', a), stroke=18))
    c.restore()
    for side in (-1, 1):
        for i in range(5):
            yy = -110 + i * 18
            c.drawRoundRect(skia.Rect(side * 70 - 12 + side * i * 2, yy, side * 70 + 12 + side * i * 2, yy + 15), 4, 4, P(color=col('#e8dcc4', a)))
            c.drawRoundRect(skia.Rect(side * 70 - 12 + side * i * 2, yy, side * 70 + 12 + side * i * 2, yy + 15), 4, 4, P(color=col('#a08a60', a), stroke=2.5))
    c.drawOval(skia.Rect(-55, -175, 55, -120), P(color=col('#ffc21f', a)))
    c.drawCircle(0, -125, 34, rad(-8, -132, 34, [col('#ffffff', a), col('#cfe8ff', a)]))
    c.drawPath(p, P(color=col('#8a6a40', a), stroke=5))
    c.restore()

def vertebra_chain(c, x, y0, y1, n, t=0.0, twist=0.0, alpha=255, colr='#fff6e0', edge='#b08a5a', hi=None):
    """Column of n vertebrae from y0 (top) to y1. twist = degrees spread over the chain (each bone turns a bit)."""
    a = int(alpha); step = (y1 - y0) / n
    for i in range(n):
        yy = y0 + step * (i + 0.5); ang = twist * (n - i) / n
        w_ = 70 * (0.75 + 0.5 * abs(math.cos(math.radians(ang))))
        c.save(); c.translate(x, yy)
        fill = colr if not (hi and i in hi) else '#ffd23f'
        c.drawRoundRect(skia.Rect(-w_ / 2, -step * 0.36, w_ / 2, step * 0.36), step * 0.2, step * 0.2, lin(c, (-w_ / 2, 0, w_ / 2, 0), [col(mix_hx(fill, edge, 0.25), a), col(fill, a), col(mix_hx(fill, edge, 0.35), a)], vertical=False, pos=[0, 0.4, 1]))
        off = math.sin(math.radians(ang)) * w_ * 0.45
        c.drawLine(-w_ / 2 - 18 + off * 0.3, 0, w_ / 2 + 18 + off * 0.3, 0, P(color=col(mix_hx(fill, edge, 0.2), a), stroke=step * 0.16))
        c.drawRoundRect(skia.Rect(-w_ / 2, -step * 0.36, w_ / 2, step * 0.36), step * 0.2, step * 0.2, P(color=col(edge, a), stroke=3))
        c.restore()

def space_rock(c, x, y, r, rot=0.0, seed=1, alpha=255, colr='#8d8478'):
    """Irregular rocky meteoroid / asteroid chunk."""
    a = int(alpha); rnd = random.Random(seed); c.save(); c.translate(x, y); c.rotate(rot)
    n = 11; p = skia.Path()
    pts = [(math.cos(2 * math.pi * i / n) * r * rnd.uniform(0.78, 1.05), math.sin(2 * math.pi * i / n) * r * rnd.uniform(0.78, 1.05)) for i in range(n)]
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    p.moveTo(*mids[-1])
    for i in range(n): p.quadTo(pts[i][0], pts[i][1], mids[i][0], mids[i][1])
    p.close()
    c.drawPath(p, rad(-r * 0.4, -r * 0.4, r * 1.7, [col(mix_hx(colr, '#ffffff', 0.35), a), col(colr, a), col(mix_hx(colr, '#000000', 0.45), a)], [0, 0.5, 1]))
    c.save(); c.clipPath(p, doAntiAlias=True)
    for i in range(5):
        cx, cy, cr = rnd.uniform(-0.6, 0.6) * r, rnd.uniform(-0.6, 0.6) * r, rnd.uniform(0.08, 0.18) * r
        c.drawCircle(cx, cy, cr, P(color=col(mix_hx(colr, '#000000', 0.3), a)))
        c.drawArc(skia.Rect(cx - cr, cy - cr, cx + cr, cy + cr), 200, 140, False, P(color=col(mix_hx(colr, '#ffffff', 0.4), a), stroke=max(1.5, cr * 0.25)))
    c.restore(); c.restore()

def meteor(c, x, y, ang, length, r=10, alpha=255, hot='#fff6c9', tail='#ffd23f'):
    """Glowing meteor streak; (x, y) = head, ang = direction of travel in degrees (tail points back)."""
    if length <= 1 or alpha <= 0: return
    a = int(alpha); rd = math.radians(ang); tx, ty = x - math.cos(rd) * length, y - math.sin(rd) * length
    c.drawLine(tx, ty, x, y, P(color=col(tail, int(a * 0.35)), stroke=r * 3.2, blur=r * 1.2))
    sh = skia.GradientShader.MakeLinear([skia.Point(tx, ty), skia.Point(x, y)], [col(tail, 0), col(tail, a), col(hot, a)], [0, 0.75, 1])
    pt = skia.Paint(AntiAlias=True, Shader=sh, Style=skia.Paint.kStroke_Style, StrokeWidth=r * 1.5, StrokeCap=skia.Paint.kRound_Cap)
    c.drawLine(tx, ty, x, y, pt)
    c.drawCircle(x, y, r * 3.5, rad(x, y, r * 3.5, [col(hot, a), col(tail, int(a * 0.4)), col(tail, 0)], [0, 0.4, 1]))
    c.drawCircle(x, y, r * 0.9, P(color=col('#ffffff', a)))

def comet(c, x, y, s, t, tail_ang=200.0, alpha=255, dust=True):
    """Comet: icy nucleus, glowing coma, two tails pointing to tail_ang (degrees, away from the Sun)."""
    a = int(alpha); rd = math.radians(tail_ang)
    for k, (L, w_, colr) in enumerate(((620, 120, '#9fd8ff'), (480, 170, '#fff1c4'))):
        off = 0.12 * (k * 2 - 1)
        ex, ey = x + math.cos(rd + off) * L * s, y + math.sin(rd + off) * L * s
        nx, ny = -math.sin(rd + off), math.cos(rd + off)
        p = skia.Path(); p.moveTo(x + nx * 20 * s, y + ny * 20 * s); p.lineTo(ex + nx * w_ * s, ey + ny * w_ * s)
        p.lineTo(ex - nx * w_ * s, ey - ny * w_ * s); p.lineTo(x - nx * 20 * s, y - ny * 20 * s); p.close()
        sh = skia.GradientShader.MakeLinear([skia.Point(x, y), skia.Point(ex, ey)], [col(colr, int(a * 0.75)), col(colr, 0)])
        c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14 * s)))
    if dust:
        rnd = random.Random(4)
        for i in range(40):
            u = rnd.uniform(0.05, 1.0); spread = rnd.uniform(-1, 1) * 140 * s * u
            px = x + math.cos(rd + 0.12) * 520 * s * u - math.sin(rd) * spread
            py = y + math.sin(rd + 0.12) * 520 * s * u + math.cos(rd) * spread
            c.drawCircle(px, py, rnd.uniform(1.5, 3.5) * s, P(color=col('#fff1c4', int(a * (1 - u) * (0.6 + 0.4 * math.sin(t * 3 + i))))))
    c.drawCircle(x, y, 70 * s, rad(x, y, 70 * s, [col('#ffffff', a), col('#cfeaff', int(a * 0.5)), col('#9fd8ff', 0)], [0, 0.35, 1]))
    space_rock(c, x, y, 16 * s, rot=t * 20, seed=9, alpha=a, colr='#b9b2a6')

def brain(c, x, y, s, t=0.0, glow=0.0, left=1.0, right=1.0, alpha=255):
    """Plain brain, side-by-side hemispheres seen from above-ish. left/right 0..1 = how awake each half looks
    (0 = dimmed/grey). glow 0..1 adds a warm halo."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    if glow > 0:
        c.drawCircle(0, 0, 230, rad(0, 0, 230, [col('#ffd23f', int(170 * glow)), col('#ffd23f', 0)]))
    for side, k in ((-1, left), (1, right)):
        p = skia.Path(); p.moveTo(side * 6, -120)
        p.cubicTo(side * 120, -140, side * 175, -60, side * 165, 20); p.cubicTo(side * 160, 100, side * 90, 135, side * 6, 120); p.close()
        top = mix_hx('#c9cbd6', '#ffc1d0', k); bot = mix_hx('#9a9db0', '#f49ab2', k)
        c.drawPath(p, lin(c, (0, -130, 0, 130), [col(top, a), col(bot, a)]))
        line_c = mix_hx('#7d8096', '#d0708a', k)
        for (a0, a1, b0, b1) in ((30, -90, 120, -60), (40, -30, 140, 0), (30, 40, 130, 60), (60, 90, 120, 100)):
            q = skia.Path(); q.moveTo(side * a0, a1); q.cubicTo(side * (a0 + b0) / 2, a1 - 30, side * (a0 + b0) / 2, b1 + 30, side * b0, b1)
            c.drawPath(q, P(color=col(line_c, a), stroke=6))
        c.drawPath(p, P(color=col(mix_hx('#6d7088', '#c0607a', k), a), stroke=6))
    c.restore()

# ---------------- Mars, ants, popcorn, snow (added for ep_042+) ----------------
_MARS_SPOTS = [(0.10, -0.15, 0.30, 0.13), (0.45, 0.05, 0.22, 0.16), (0.72, -0.30, 0.18, 0.10), (0.30, 0.35, 0.26, 0.09),
               (0.85, 0.25, 0.20, 0.12), (0.58, -0.45, 0.14, 0.07), (0.02, 0.30, 0.16, 0.08)]
def mars(c, x, y, r, t=0.0, rot=0.0, gray=0.0, storm=0.0, alpha=255, shade=True, caps=True):
    """Plain Mars globe. rot shifts the surface features (fraction of a turn); gray 0..1 blends the dust
    away to the dark basalt underneath; storm 0..1 veils it in a tan dust haze."""
    a = int(alpha)
    def g(hx): return mix_hx(hx, mix_hx('#4e4c4a', hx, 0.12), gray)
    c.drawCircle(x, y, r * 1.12, rad(x, y, r * 1.12, [col('#ff9a5a', int(a * 0.28)), col('#ff9a5a', 0)], [0.85, 1]))
    c.save(); clip = skia.Path(); clip.addCircle(x, y, r); c.clipPath(clip, doAntiAlias=True)
    c.drawCircle(x, y, r, rad(x - r * 0.35, y - r * 0.4, r * 1.6, [col(g('#f6a46a'), a), col(g('#d9672f'), a), col(g('#9a3a18'), a)], [0, 0.5, 1]))
    for (u, v, w_, h_) in _MARS_SPOTS:
        uu = (u + rot) % 1.0
        px = x + math.sin((uu - 0.5) * math.pi) * r          # simple globe projection
        sq = math.cos((uu - 0.5) * math.pi)
        if sq < 0.05: continue
        c.drawOval(skia.Rect(px - w_ * r * sq, y + v * r - h_ * r, px + w_ * r * sq, y + v * r + h_ * r),
                   P(color=col(g('#7a2e14'), int(a * 0.55 * sq)), blur=r * 0.04))
    # fine streaks / craters for texture
    rnd = random.Random(11)
    for i in range(18):
        uu = (rnd.random() + rot) % 1.0; vv = rnd.uniform(-0.8, 0.8)
        sq = math.cos((uu - 0.5) * math.pi)
        if sq < 0.1: continue
        px = x + math.sin((uu - 0.5) * math.pi) * r; py = y + vv * r; cr = rnd.uniform(0.02, 0.05) * r
        c.drawOval(skia.Rect(px - cr * sq, py - cr, px + cr * sq, py + cr), P(color=col(g('#8f3a1a'), int(a * 0.5))))
        c.drawArc(skia.Rect(px - cr * sq, py - cr, px + cr * sq, py + cr), 200, 140, False, P(color=col(g('#ffc49a'), int(a * 0.6)), stroke=max(1.2, cr * 0.3)))
    if caps:
        c.drawOval(skia.Rect(x - r * 0.38, y - r * 1.04, x + r * 0.38, y - r * 0.80), P(color=col('#fff6ee', int(a * 0.95)), blur=r * 0.02))
        c.drawOval(skia.Rect(x - r * 0.22, y + r * 0.86, x + r * 0.22, y + r * 1.02), P(color=col('#fff6ee', int(a * 0.8)), blur=r * 0.02))
    if storm > 0:
        for k in range(3):
            yy = y + (k - 1) * r * 0.32 + math.sin(t * 0.8 + k) * r * 0.05
            c.drawOval(skia.Rect(x - r * 1.1, yy - r * 0.16, x + r * 1.1, yy + r * 0.16), P(color=col('#f3c18c', int(a * 0.55 * storm)), blur=r * 0.08))
        c.drawCircle(x, y, r, P(color=col('#e8a66c', int(a * 0.35 * storm))))
    if shade:
        c.drawCircle(x, y, r, rad(x - r * 0.45, y - r * 0.45, r * 2.1, [col('#000000', 0), col('#000000', 0), col('#1a0a05', int(a * 0.55))], [0, 0.55, 1]))
    c.restore()

def ant(c, x, y, s, t, rot=0.0, walk=1.0, alpha=255, colr='#3b2418', gaster=None, legs_long=1.0):
    """Plain ant seen from above, head pointing along rot (degrees). walk = gait speed (0 = standing)."""
    a = int(alpha); gaster = gaster or colr
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    ph = t * 14 * walk
    lp = P(color=col(mix_hx(colr, '#000000', 0.2), a), stroke=4.2)
    LEGS = (((8, 4), (24, 24), (44, 40)), ((0, 5), (4, 30), (-4, 54)), ((-8, 4), (-24, 26), (-50, 44)))
    for side in (-1, 1):
        for i, (hip, knee, foot) in enumerate(LEGS):
            tri = (i % 2 == 0) == (side > 0)
            sw = math.sin(ph + (0 if tri else math.pi)) * 9 * min(1, walk * 3)
            kx, ky = knee[0] * legs_long + sw * 0.5, side * knee[1] * legs_long
            fx, fy = foot[0] * legs_long + sw, side * foot[1] * legs_long
            c.drawLine(hip[0], side * hip[1], kx, ky, lp); c.drawLine(kx, ky, fx, fy, lp)
    # gaster, petiole, thorax, head
    c.drawOval(skia.Rect(-54, -15, -18, 15), rad(-40, -7, 30, [col(mix_hx(gaster, '#ffffff', 0.35), a), col(gaster, a), col(mix_hx(gaster, '#000000', 0.35), a)], [0, 0.5, 1]))
    c.drawCircle(-15, 0, 6, P(color=col(colr, a)))
    c.drawOval(skia.Rect(-12, -8, 16, 8), rad(0, -4, 18, [col(mix_hx(colr, '#ffffff', 0.3), a), col(colr, a)]))
    c.drawOval(skia.Rect(14, -12, 40, 12), rad(24, -5, 20, [col(mix_hx(colr, '#ffffff', 0.3), a), col(colr, a)]))
    # antennae (elbowed)
    sway = math.sin(t * 5) * 6
    for side in (-1, 1):
        c.drawLine(36, side * 6, 48, side * (16 + sway * 0.3), lp)
        c.drawLine(48, side * (16 + sway * 0.3), 68, side * (10 + sway), lp)
    c.drawCircle(30, -7, 2.6, P(color=col('#ffffff', int(a * 0.5))))
    c.drawCircle(30, 7, 2.6, P(color=col('#ffffff', int(a * 0.5))))
    c.restore()

def kernel_path(s=1.0):
    """Popcorn kernel outline: rounded top, tapering to the tip at the bottom (origin = centre)."""
    p = skia.Path(); p.moveTo(0, -46 * s)
    p.cubicTo(30 * s, -46 * s, 40 * s, -20 * s, 34 * s, 6 * s); p.cubicTo(28 * s, 30 * s, 12 * s, 46 * s, 0, 50 * s)
    p.cubicTo(-12 * s, 46 * s, -28 * s, 30 * s, -34 * s, 6 * s); p.cubicTo(-40 * s, -20 * s, -30 * s, -46 * s, 0, -46 * s); p.close()
    return p

def popcorn_kernel(c, x, y, s, rot=0.0, section=0.0, steam=0.0, heat=0.0, swell=0.0, t=0.0, alpha=255):
    """Unpopped popcorn kernel. section 0..1 cuts it open (hull ring, starch, water drop);
    steam 0..1 turns the water drop into steam puffs; heat tints it hot; swell puffs it up a bit before bursting."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); sc = s * (1 + 0.08 * swell); c.scale(sc, sc)
    p = kernel_path(1.0)
    c.drawPath(p, lin(c, (0, -46, 0, 50), [col(mix_hx('#ffc23a', '#ff7a2c', heat * 0.6), a), col(mix_hx('#e98a0c', '#d4421a', heat * 0.6), a)]))
    # pale tip cap
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawOval(skia.Rect(-20, 30, 20, 62), P(color=col('#f6e2a8', a)))
    if section > 0:
        sa = int(a * section)
        inner = kernel_path(0.8)
        c.drawPath(inner, lin(c, (0, -40, 0, 40), [col('#fff6dc', sa), col('#f3dfa8', sa)]))
        rnd = random.Random(3)
        for i in range(14):
            gx, gy = rnd.uniform(-22, 22), rnd.uniform(-30, 26)
            c.drawCircle(gx, gy, rnd.uniform(2.5, 4.5), P(color=col('#e9cf8a', int(sa * 0.7))))
        d = 1 - steam
        if d > 0.02:
            c.drawPath(_drop_path(0, -2, 14 * d), lin(c, (0, -20, 0, 14), [col('#8fd0ff', int(sa * d)), col('#2f9bff', int(sa * d))]))
            c.drawCircle(-4, -2, 3.5 * d, P(color=col('#ffffff', int(sa * d * 0.8))))
        if steam > 0:
            for i in range(7):
                ang = i * 2 * math.pi / 7 + t * 2.5; rr = 6 + 18 * steam + 3 * math.sin(t * 6 + i)
                c.drawCircle(math.cos(ang) * rr, math.sin(ang) * rr * 1.2 - 2, 5 + 4 * steam, P(color=col('#ffffff', int(sa * 0.85 * steam)), blur=1.5))
    c.restore()
    c.drawPath(p, P(color=col('#b5560a', a), stroke=2.5))
    if section > 0:
        c.drawPath(kernel_path(0.8), P(color=col('#d99a3a', int(a * section)), stroke=2))
    c.drawOval(skia.Rect(-22, -38, -6, -8), P(color=col('#ffffff', int(a * 0.45)), blur=3))
    c.restore()

def _drop_path(x, y, r):
    p = skia.Path(); p.moveTo(x, y - r * 1.6)
    p.cubicTo(x + r * 0.6, y - r * 0.7, x + r, y - r * 0.1, x + r, y + r * 0.35)
    p.cubicTo(x + r, y + r * 0.95, x + r * 0.5, y + r * 1.2, x, y + r * 1.2)
    p.cubicTo(x - r * 0.5, y + r * 1.2, x - r, y + r * 0.95, x - r, y + r * 0.35)
    p.cubicTo(x - r, y - r * 0.1, x - r * 0.6, y - r * 0.7, x, y - r * 1.6); p.close()
    return p

def popcorn_puff(c, x, y, s, rot=0.0, k=1.0, seed=0, alpha=255, hull=True):
    """Popped popcorn: a cluster of creamy foam lobes with a few hull flakes. k 0..1 = burst growth."""
    if k <= 0: return
    a = int(alpha); rnd = random.Random(seed)
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s * k, s * k)
    lobes = [(0, 0, 40)] + [(math.cos(i * 1.15 + rnd.uniform(-0.3, 0.3)) * 36, math.sin(i * 1.15 + rnd.uniform(-0.3, 0.3)) * 30, rnd.uniform(24, 34)) for i in range(6)]
    for (lx, ly, lr) in lobes:
        c.drawCircle(lx + 3, ly + 5, lr, P(color=col('#c7a46a', int(a * 0.55))))
    for (lx, ly, lr) in lobes:
        c.drawCircle(lx, ly, lr, rad(lx - lr * 0.35, ly - lr * 0.4, lr * 1.5, [col('#ffffff', a), col('#fff4dc', a), col('#ecd6a8', a)], [0, 0.55, 1]))
    for (lx, ly, lr) in lobes[1:]:
        c.drawArc(skia.Rect(lx - lr, ly - lr, lx + lr, ly + lr), 20, 120, False, P(color=col('#e2c48c', int(a * 0.5)), stroke=2.5))
    if hull:
        for i in range(3):
            ang = rnd.uniform(0, 2 * math.pi); hx, hy = math.cos(ang) * 30, math.sin(ang) * 26 + 6
            c.save(); c.translate(hx, hy); c.rotate(math.degrees(ang))
            fp = skia.Path(); fp.moveTo(-12, -4); fp.quadTo(0, -12, 12, -4); fp.quadTo(0, 6, -12, -4); fp.close()
            c.drawPath(fp, lin(c, (0, -10, 0, 6), [col('#ffc23a', a), col('#e98a0c', a)]))
            c.restore()
    c.restore()

def gauge(c, x, y, r, frac, alpha=255, label=None, accent='#ff5c85', zones=True):
    """Pressure gauge dial (270° sweep), frac 0..1 = needle position."""
    a = int(alpha)
    c.drawCircle(x, y + 6, r + 16, P(color=col('#0b1a3a', int(a * 0.25)), blur=8))
    c.drawCircle(x, y, r + 16, lin(c, (0, y - r, 0, y + r), [col('#c9d3e2', a), col('#7d8aa3', a)]))
    c.drawCircle(x, y, r, P(color=col('#ffffff', a)))
    rect = skia.Rect(x - r * 0.82, y - r * 0.82, x + r * 0.82, y + r * 0.82)
    if zones:
        c.drawArc(rect, 135 + 270 * 0.7, 270 * 0.3, False, P(color=col(accent, int(a * 0.8)), stroke=r * 0.1))
    for i in range(11):
        ang = math.radians(135 + 27 * i)
        c.drawLine(x + math.cos(ang) * r * 0.66, y + math.sin(ang) * r * 0.66, x + math.cos(ang) * r * 0.76, y + math.sin(ang) * r * 0.76,
                   P(color=col('#1b2a4a', a), stroke=5 if i % 5 == 0 else 3))
    ang = math.radians(135 + 270 * clamp(frac))
    c.drawLine(x, y, x + math.cos(ang) * r * 0.7, y + math.sin(ang) * r * 0.7, P(color=col(accent, a), stroke=8))
    c.drawCircle(x, y, 13, P(color=col('#1b2a4a', a)))
    if label: text_block(c, label, x, y + r * 0.5, size=int(r * 0.26), fill='#1b2a4a', stroke='#ffffff', alpha=a)

def ice_crystal(c, x, y, r, rot=0.0, alpha=255, glint=0.0):
    """Clear hexagonal ice plate (transparent with pale blue edges and inner facets)."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot)
    hp = hexagon_path(0, 0, r)
    c.drawPath(hp, P(color=col('#e8f6ff', int(a * 0.28))))
    c.drawPath(hexagon_path(0, 0, r * 0.62), P(color=col('#bfe6ff', int(a * 0.35)), stroke=max(1.5, r * 0.035)))
    for k in range(6):
        ang = math.radians(k * 60 + 30)
        c.drawLine(math.cos(ang) * r * 0.62, math.sin(ang) * r * 0.62, math.cos(ang) * r * 0.97, math.sin(ang) * r * 0.97,
                   P(color=col('#bfe6ff', int(a * 0.35)), stroke=max(1.2, r * 0.025)))
    c.drawPath(hp, P(color=col('#a9dcff', a), stroke=max(2, r * 0.05)))
    c.drawLine(-r * 0.5, -r * 0.55, -r * 0.1, -r * 0.75, P(color=col('#ffffff', int(a * 0.8)), stroke=max(2, r * 0.06)))
    if glint > 0:
        c.drawCircle(r * 0.4, -r * 0.4, r * 0.35 * glint, rad(r * 0.4, -r * 0.4, r * 0.35 * glint + 0.1, [col('#ffffff', int(a * glint)), col('#ffffff', 0)]))
    c.restore()

def snow_ground(c, y, x0=-20, x1=W + 20, y1=H, seed=2, alpha=255, glow_blue=0.0):
    """Soft white snow drifts from y down."""
    a = int(alpha); rnd = random.Random(seed)
    p = skia.Path(); p.moveTo(x0, y + 30); n = 5; step = (x1 - x0) / n
    for i in range(n):
        xa = x0 + step * i; xb = xa + step
        p.cubicTo(xa + step * 0.3, y - rnd.uniform(10, 60), xa + step * 0.7, y - rnd.uniform(0, 50), xb, y + rnd.uniform(0, 40))
    p.lineTo(x1, y1); p.lineTo(x0, y1); p.close()
    c.drawPath(p, lin(c, (0, y - 60, 0, y1), [col('#ffffff', a), col('#e6f0fb', a), col(mix_hx('#c9dcf2', '#5fb6ff', glow_blue), a)], [0, 0.35, 1]))
    for i in range(30):
        sx, sy = rnd.uniform(x0, x1), rnd.uniform(y + 40, min(y1, y + 260))
        c.drawCircle(sx, sy, rnd.uniform(1.5, 3), P(color=col('#ffffff', int(a * 0.9))))

# ---------------- Bones, faces, fireflies, sunset (added for ep_046+) ----------------
BONE = '#fff6e0'; BONE_EDGE = '#b08a5a'

def long_bone(c, x, y, s, rot=0.0, alpha=255, section=0.0, hi=None, length=1.0):
    """Plain long bone (like a femur), centred at x,y, vertical. section 0..1 cuts it open: hard shell, spongy ends,
    red marrow inside. hi = highlight colour for the whole bone."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    L = 250 * length
    p = skia.Path(); p.addRoundRect(skia.Rect(-34, -L, 34, L), 30, 30)
    for sy in (-1, 1):
        for sx in (-1, 1):
            q = skia.Path(); q.addCircle(sx * 42, sy * (L + 18), 46)
            p = skia.Op(p, q, skia.PathOp.kUnion_PathOp)
    fill = hi or BONE
    c.drawPath(p, lin(c, (-80, 0, 80, 0), [col(mix_hx(fill, BONE_EDGE, 0.25), a), col(fill, a), col(mix_hx(fill, BONE_EDGE, 0.35), a)], vertical=False, pos=[0, 0.42, 1]))
    if section > 0:
        k = clamp(section)
        c.save(); c.clipPath(p, doAntiAlias=True)
        # spongy bone at both ends
        rnd = random.Random(7)
        for sy in (-1, 1):
            c.drawOval(skia.Rect(-70 * k, sy * (L + 18) - 50 * k, 70 * k, sy * (L + 18) + 50 * k), P(color=col('#f4d9b0', a)))
            for i in range(26):
                px, py = rnd.uniform(-62, 62) * k, sy * (L + 18) + rnd.uniform(-44, 44) * k
                c.drawCircle(px, py, rnd.uniform(5, 9) * k, P(color=col('#e9a0a0', int(a * 0.8))))
        # marrow cavity
        mw = 20 * k
        c.drawRoundRect(skia.Rect(-mw, -L + 30, mw, L - 30), mw, mw, lin(c, (-mw, 0, mw, 0), [col('#c9283f', a), col('#ff5c6e', a), col('#c9283f', a)], vertical=False, pos=[0, 0.5, 1]))
        c.restore()
    c.drawPath(p, P(color=col(BONE_EDGE, a), stroke=5))
    c.drawLine(-14, -L + 40, -14, L - 40, P(color=col('#ffffff', int(a * 0.55)), stroke=8))
    c.restore()

def _bone_seg(c, x0, y0, x1, y1, w, a, fill):
    c.drawLine(x0, y0, x1, y1, P(color=col(BONE_EDGE, a), stroke=w + 6))
    c.drawLine(x0, y0, x1, y1, P(color=col(fill, a), stroke=w))
    for (xx, yy) in ((x0, y0), (x1, y1)):
        c.drawCircle(xx, yy, w * 0.75, P(color=col(fill, a))); c.drawCircle(xx, yy, w * 0.75, P(color=col(BONE_EDGE, a), stroke=3))

def xray_body(c, x, y, s, t, alpha=255, bones=1.0, hi=(), hi_col='#ffd23f', arm_lift=0.0, skin=0.85):
    """Plain X-ray style body (front view): pale blue silhouette with the skeleton inside. y = feet line.
    bones 0..1 fades the skeleton in; hi = set of parts to highlight: skull, ribs, spine, pelvis, arms, legs, hands, feet.
    arm_lift 0..1 raises the right arm (viewer's right)."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    sk = int(a * skin)
    # silhouette
    body = skia.Path()
    body.addCircle(0, -880, 95)
    body.addRoundRect(skia.Rect(-38, -800, 38, -740), 20, 20)
    body.addRoundRect(skia.Rect(-150, -760, 150, -360), 70, 70)
    body.addRoundRect(skia.Rect(-130, -420, 130, -300), 50, 50)
    for sx in (-1, 1):
        body.addRoundRect(skia.Rect(sx * 75 - 52, -330, sx * 75 + 52, -20), 50, 50)
        body.addOval(skia.Rect(sx * 85 - 60, -40, sx * 85 + 60, 10))
    c.drawPath(body, lin(c, (0, -980, 0, 0), [col('#9fd2ff', sk), col('#5fa8f0', sk)]))
    arms = []
    for sx in (-1, 1):
        sx0, sy0 = sx * 132, -720
        a1 = math.radians(98) if sx < 0 else math.radians(lerp(82, -55, ease_in_out(clamp(arm_lift))))
        a2 = a1 + (math.radians(8) if sx < 0 else math.radians(lerp(-8, -20, clamp(arm_lift))))
        elx, ely = sx0 + math.cos(a1) * 200, sy0 + math.sin(a1) * 200
        hx, hy = elx + math.cos(a2) * 185, ely + math.sin(a2) * 185
        c.drawLine(sx0, sy0, elx, ely, P(color=col('#7fbcf5', sk), stroke=86))
        c.drawLine(elx, ely, hx, hy, P(color=col('#7fbcf5', sk), stroke=74))
        c.drawCircle(hx + math.cos(a2) * 40, hy + math.sin(a2) * 40, 46, P(color=col('#7fbcf5', sk)))
        arms.append((sx0, sy0, elx, ely, hx, hy, a2))
    if bones > 0:
        ba = int(a * clamp(bones))
        def F(part): return hi_col if part in hi else BONE
        # skull
        c.drawOval(skia.Rect(-70, -965, 70, -820), P(color=col(F('skull'), ba)))
        c.drawRoundRect(skia.Rect(-46, -850, 46, -790), 24, 24, P(color=col(F('skull'), ba)))
        c.drawOval(skia.Rect(-70, -965, 70, -820), P(color=col(BONE_EDGE, ba), stroke=4))
        c.drawRoundRect(skia.Rect(-46, -850, 46, -790), 24, 24, P(color=col(BONE_EDGE, ba), stroke=4))
        # spine
        for i in range(14):
            yy = -785 + i * 30
            c.drawRoundRect(skia.Rect(-15, yy, 15, yy + 22), 8, 8, P(color=col(F('spine'), ba)))
            c.drawRoundRect(skia.Rect(-15, yy, 15, yy + 22), 8, 8, P(color=col(BONE_EDGE, ba), stroke=3))
        # collarbones
        for sx in (-1, 1):
            _bone_seg(c, sx * 20, -735, sx * 140, -722, 14, ba, F('arms'))
        # ribs
        for i in range(6):
            yy = -690 + i * 42; w_ = 112 - abs(i - 2) * 6
            for sx in (-1, 1):
                rp = skia.Path(); rp.moveTo(sx * 16, yy); rp.cubicTo(sx * w_, yy - 22, sx * (w_ + 14), yy + 30, sx * (w_ - 20), yy + 48)
                c.drawPath(rp, P(color=col(BONE_EDGE, ba), stroke=16)); c.drawPath(rp, P(color=col(F('ribs'), ba), stroke=10))
        c.drawRoundRect(skia.Rect(-12, -700, 12, -520), 10, 10, P(color=col(F('ribs'), ba)))
        # pelvis
        pp = skia.Path(); pp.moveTo(-120, -400); pp.cubicTo(-130, -330, -70, -300, -30, -310); pp.lineTo(30, -310)
        pp.cubicTo(70, -300, 130, -330, 120, -400); pp.cubicTo(60, -370, -60, -370, -120, -400); pp.close()
        c.drawPath(pp, P(color=col(F('pelvis'), ba))); c.drawPath(pp, P(color=col(BONE_EDGE, ba), stroke=4))
        # legs
        for sx in (-1, 1):
            _bone_seg(c, sx * 80, -330, sx * 78, -175, 22, ba, F('legs'))
            _bone_seg(c, sx * 78, -165, sx * 82, -50, 18, ba, F('legs'))
            for k in range(5):
                c.drawLine(sx * (60 + k * 9), -30, sx * (55 + k * 14), -2, P(color=col(F('feet'), ba), stroke=7))
            c.drawOval(skia.Rect(sx * 82 - 26, -48, sx * 82 + 26, -22), P(color=col(F('feet'), ba)))
        # arms
        for (sx0, sy0, elx, ely, hx, hy, a2) in arms:
            _bone_seg(c, sx0, sy0, elx, ely, 18, ba, F('arms'))
            _bone_seg(c, elx - 6, ely, hx - 6, hy, 11, ba, F('arms'))
            _bone_seg(c, elx + 8, ely, hx + 8, hy, 10, ba, F('arms'))
            cx_, cy_ = hx + math.cos(a2) * 34, hy + math.sin(a2) * 34
            c.drawCircle(cx_, cy_, 18, P(color=col(F('hands'), ba)))
            for k in range(5):
                da = math.radians(-40 + k * 20) + a2
                c.drawLine(cx_, cy_, cx_ + math.cos(da) * 42, cy_ + math.sin(da) * 42, P(color=col(F('hands'), ba), stroke=7))
    c.restore()

def plain_face(c, x, y, s, t, alpha=255, brows=1.0, raise_=0.0, frown=0.0, skin='#f2c9a6', hair='#4a3326', iris='#6b8f5a',
               sweat=0.0, look=(0, 0)):
    """Plain, neutral adult face (front view, infographic). brows 0..1 fades the eyebrows (0 = no eyebrows);
    raise_ 0..1 lifts them (surprise), frown 0..1 pulls them down/in. No smile, no blush."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    head = skia.Path(); head.addOval(skia.Rect(-230, -300, 230, 320))
    for sx in (-1, 1):
        c.drawOval(skia.Rect(sx * 232 - 30, -40, sx * 232 + 30, 70), P(color=col(mix_hx(skin, '#c98a6a', 0.3), a)))
    c.drawPath(head, rad(-60, -80, 420, [col(mix_hx(skin, '#ffffff', 0.25), a), col(skin, a), col(mix_hx(skin, '#c98a6a', 0.35), a)], [0, 0.6, 1]))
    c.save(); c.clipPath(head, doAntiAlias=True)
    hp = skia.Path(); hp.moveTo(-260, -60); hp.cubicTo(-200, -170, -60, -205, 40, -200); hp.cubicTo(140, -195, 220, -160, 260, -90)
    hp.lineTo(260, -330); hp.lineTo(-260, -330); hp.close()
    c.drawPath(hp, lin(c, (0, -320, 0, -60), [col(mix_hx(hair, '#000000', 0.2), a), col(hair, a)]))
    c.restore()
    # eyes
    for sx in (-1, 1):
        human_eye(c, sx * 95, 10, 0.5, t + (0.4 if sx > 0 else 0), alpha=a, iris=iris)
    # eyebrows
    if brows > 0:
        ba = int(a * clamp(brows))
        for sx in (-1, 1):
            lift = -32 * raise_ + 18 * frown
            inner_dy = 22 * frown - 10 * raise_
            bp = skia.Path()
            x_in, x_out = sx * 40, sx * 165
            bp.moveTo(x_in, -62 + lift + inner_dy); bp.cubicTo(sx * 80, -96 + lift, sx * 130, -100 + lift, x_out, -66 + lift)
            c.drawPath(bp, P(color=col(mix_hx(hair, '#000000', 0.1), ba), stroke=26))
            # hair strokes pointing outward
            m = skia.PathMeasure(bp, False); Lb = m.getLength()
            for k in range(9):
                pos, tan = m.getPosTan(Lb * (0.08 + 0.1 * k))
                if pos is None: continue
                c.drawLine(pos.x(), pos.y() + 4, pos.x() + sx * 18, pos.y() - 6, P(color=col(hair, ba), stroke=5))
    # nose and neutral mouth
    np_ = skia.Path(); np_.moveTo(-8, 30); np_.cubicTo(-20, 110, -40, 140, -10, 150); np_.lineTo(18, 150)
    c.drawPath(np_, P(color=col(mix_hx(skin, '#8a5a3a', 0.45), a), stroke=7))
    c.drawLine(-62, 215, 62, 215, P(color=col('#a65a5a', a), stroke=10))
    if sweat > 0:
        for i, (dx, ph) in enumerate(((-120, 0.0), (40, 0.35), (150, 0.7))):
            u = (sweat * 1.5 + ph) % 1.0
            yy = lerp(-220, -50, u)
            r = 14
            dp = skia.Path(); dp.moveTo(dx, yy - r * 2); dp.cubicTo(dx + r, yy - r * 0.6, dx + r, yy + r, dx, yy + r); dp.cubicTo(dx - r, yy + r, dx - r, yy - r * 0.6, dx, yy - r * 2); dp.close()
            c.drawPath(dp, rad(dx - 3, yy, r * 1.4, [col('#ffffff', a), col('#8fd3ff', a), col('#3fa9ff', a)], [0, 0.4, 1]))
    c.restore()

def firefly(c, x, y, s, t, glow=1.0, rot=0.0, alpha=255, fly=False, lantern_cut=0.0):
    """Plain firefly (lightning beetle), top view, head up. glow 0..1 lights the lantern at the tail.
    fly=True opens the wing covers and flaps the clear hind wings."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    g = clamp(glow)
    if g > 0:
        c.drawCircle(0, 120, 230 * (0.6 + 0.4 * g), rad(0, 120, 230 * (0.6 + 0.4 * g), [col('#eaff6b', int(a * 0.7 * g)), col('#c8ff3a', int(a * 0.25 * g)), col('#c8ff3a', 0)], [0, 0.4, 1]))
    # legs
    for i, yy in enumerate((-20, 20, 60)):
        for sx in (-1, 1):
            sw = 6 * math.sin(t * 9 + i * 2 + sx) if not fly else 0
            c.drawLine(sx * 20, yy, sx * 70, yy + 20 + sw, P(color=col('#2a2a33', a), stroke=7))
            c.drawLine(sx * 70, yy + 20 + sw, sx * 86, yy + 60 + sw, P(color=col('#2a2a33', a), stroke=6))
    # abdomen with lantern segments
    ab = skia.Path(); ab.addOval(skia.Rect(-46, 0, 46, 190))
    c.drawPath(ab, P(color=col('#3a3530', a)))
    c.save(); c.clipPath(ab, doAntiAlias=True)
    lc = mix_hx('#d9d2a8', '#f4ff8a', g)
    c.drawRect(skia.Rect(-50, 120, 50, 200), lin(c, (0, 120, 0, 200), [col(lc, a), col(mix_hx(lc, '#ffffff', 0.4 * g), a)]))
    for yy in (138, 160):
        c.drawLine(-50, yy, 50, yy, P(color=col('#8a8460', int(a * (1 - 0.6 * g))), stroke=3))
    c.restore()
    # hind wings when flying
    if fly:
        fl = 0.5 + 0.5 * math.sin(t * 40)
        for sx in (-1, 1):
            wp = skia.Path(); wp.moveTo(sx * 10, -10); wp.cubicTo(sx * (120 + 60 * fl), -60, sx * (180 + 40 * fl), 80, sx * 30, 120); wp.close()
            c.drawPath(wp, P(color=col('#e6f2ff', int(a * 0.5))))
            c.drawPath(wp, P(color=col('#9fb8d6', int(a * 0.7)), stroke=3))
    # wing covers (elytra)
    for sx in (-1, 1):
        op = (math.radians(28) if fly else 0) * sx
        c.save(); c.translate(sx * 2, -40); c.rotate(math.degrees(op))
        ep = skia.Path(); ep.moveTo(0, 0); ep.cubicTo(sx * 52, 0, sx * 54, 90, sx * 40, 150); ep.cubicTo(sx * 26, 168, sx * 6, 160, 0, 150); ep.close()
        c.drawPath(ep, lin(c, (0, 0, 0, 160), [col('#4a443c', a), col('#2e2a26', a)]))
        c.drawPath(ep, P(color=col('#d9c27a', a), stroke=5))
        c.drawLine(sx * 18, 20, sx * 24, 120, P(color=col('#ffffff', int(a * 0.25)), stroke=6))
        c.restore()
    # shield (pronotum) with the red/yellow pattern, head under it
    c.drawOval(skia.Rect(-24, -100, 24, -60), P(color=col('#2a2a33', a)))
    sh = skia.Path(); sh.addOval(skia.Rect(-52, -82, 52, -30))
    c.drawPath(sh, lin(c, (0, -82, 0, -30), [col('#ffd23f', a), col('#ff9f1c', a)]))
    c.drawRoundRect(skia.Rect(-30, -72, 30, -40), 14, 14, P(color=col('#ff6f6f', a)))
    c.drawLine(0, -76, 0, -34, P(color=col('#2a2a33', a), stroke=6))
    c.drawPath(sh, P(color=col('#b86a10', a), stroke=3))
    # antennae
    for sx in (-1, 1):
        ap = skia.Path(); ap.moveTo(sx * 10, -96); ap.cubicTo(sx * 30, -150, sx * 60, -170, sx * 70 + 4 * math.sin(t * 3 + sx), -200)
        c.drawPath(ap, P(color=col('#2a2a33', a), stroke=6))
    c.restore()

# ---------------- Bread, Moon craters, Birds, Heat (added for ep_050-053) ----------------
DOUGH = '#f3dfb4'; CRUST = '#c9822f'; CRUMB = '#fbeccb'

def yeast_cell(c, x, y, r, t=0.0, bud=0.0, alpha=255, seed=0):
    """Plain budding yeast cell (oval, cream, with vacuole); bud 0..1 grows a daughter cell."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(20 * math.sin(seed * 1.7) + 4 * math.sin(t * 1.3 + seed))
    def cell(cx, cy, rr):
        c.drawOval(skia.Rect(cx - rr, cy - rr * 0.82, cx + rr, cy + rr * 0.82), rad(cx - rr * 0.35, cy - rr * 0.35, rr * 1.6,
                   [col('#fff8e6', a), col('#f1dca6', a), col('#d9b873', a)], [0, 0.55, 1]))
        c.drawOval(skia.Rect(cx - rr, cy - rr * 0.82, cx + rr, cy + rr * 0.82), P(color=col('#a8823c', a), stroke=max(2, rr * 0.07)))
    if bud > 0:
        br = r * 0.55 * clamp(bud)
        cell(r * 0.95 + br * 0.7, -r * 0.2, br)
    cell(0, 0, r)
    c.drawCircle(-r * 0.15, r * 0.05, r * 0.32, P(color=col('#cfe6f0', int(a * 0.85))))
    c.drawCircle(-r * 0.15, r * 0.05, r * 0.32, P(color=col('#8fb3c4', int(a * 0.8)), stroke=max(1.5, r * 0.04)))
    c.drawCircle(r * 0.38, -r * 0.25, r * 0.12, P(color=col('#b9924c', int(a * 0.8))))
    c.drawOval(skia.Rect(-r * 0.7, -r * 0.62, -r * 0.2, -r * 0.4), P(color=col('#ffffff', int(a * 0.7))))
    c.restore()

def gas_bubble(c, x, y, r, alpha=230, colr='#ffffff'):
    """Clean CO2 gas bubble with rim + highlight (for dough/liquids)."""
    if r <= 0.5: return
    a = int(alpha)
    c.drawCircle(x, y, r, rad(x - r * 0.3, y - r * 0.3, r * 1.4, [col(colr, int(a * 0.25)), col(colr, int(a * 0.55))]))
    c.drawCircle(x, y, r, P(color=col(colr, a), stroke=max(1.5, r * 0.12)))
    c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.22, P(color=col('#ffffff', a)))

def dough_path(x, y, s, rise=0.0):
    """Dough blob resting on y (bottom), width ~560*s, height 170..330*s with rise 0..1."""
    w_ = 280 * s * (1 + 0.12 * rise); h_ = lerp(170, 330, clamp(rise)) * s
    p = skia.Path(); p.moveTo(x - w_, y)
    p.cubicTo(x - w_ * 1.05, y - h_ * 0.75, x - w_ * 0.55, y - h_, x, y - h_)
    p.cubicTo(x + w_ * 0.55, y - h_, x + w_ * 1.05, y - h_ * 0.75, x + w_, y); p.close()
    return p, w_, h_

def dough(c, x, y, s, t=0.0, rise=0.0, section=0.0, bubbles=0.0, alpha=255, seed=3):
    """Ball of bread dough (side view). section 0..1 cuts it open; bubbles 0..1 grows CO2 pockets inside."""
    a = int(alpha); p, w_, h_ = dough_path(x, y, s, rise)
    c.drawOval(skia.Rect(x - w_ * 1.05, y - 18 * s, x + w_ * 1.05, y + 22 * s), P(color=col('#1b2a4a', int(a * 0.18)), blur=10 * s))
    c.drawPath(p, rad(x - w_ * 0.3, y - h_ * 0.8, w_ * 1.8, [col('#fff6df', a), col(DOUGH, a), col('#dcbc80', a)], [0, 0.5, 1]))
    if section > 0 or bubbles > 0:
        c.save(); c.clipPath(p, doAntiAlias=True)
        if section > 0:
            c.drawPath(p, P(color=col(CRUMB, int(a * section))))
        rnd = random.Random(seed)
        for i in range(26):
            bx = x + rnd.uniform(-0.82, 0.82) * w_; by = y - rnd.uniform(0.08, 0.85) * h_
            br = rnd.uniform(9, 26) * s * clamp(bubbles) * (0.6 + 0.5 * rise)
            gas_bubble(c, bx + 2 * math.sin(t * 2 + i), by, br, alpha=int(a * (0.55 + 0.45 * section)), colr='#ffffff' if section > 0.5 else '#fff9ec')
        c.restore()
    c.drawPath(p, P(color=col('#c9a462', a), stroke=max(2, 5 * s)))
    c.drawArc(skia.Rect(x - w_ * 0.6, y - h_ * 0.95, x + w_ * 0.1, y - h_ * 0.35), 200, 60, False, P(color=col('#ffffff', int(a * 0.55)), stroke=12 * s))

def gluten_net(c, x0, y0, x1, y1, t=0.0, stretch=0.0, alpha=230, colr='#e8b04a', n=6, seed=2):
    """Stretchy gluten protein network: wavy strands crossing; stretch 0..1 straightens them and spreads the cells."""
    a = int(alpha); rnd = random.Random(seed)
    amp = lerp(26, 6, clamp(stretch))
    for k in range(n):
        for horiz in (True, False):
            p = skia.Path(); f = (k + 0.5) / n; ph = rnd.uniform(0, 6)
            for i in range(41):
                u = i / 40
                if horiz:
                    px = lerp(x0, x1, u); py = lerp(y0, y1, f) + amp * math.sin(u * 14 + ph + t * 0.8)
                else:
                    px = lerp(x0, x1, f) + amp * math.sin(u * 14 + ph + t * 0.8); py = lerp(y0, y1, u)
                (p.moveTo if i == 0 else p.lineTo)(px, py)
            c.drawPath(p, P(color=col(mix_hx(colr, '#ffffff', 0.35), a), stroke=13))
            c.drawPath(p, P(color=col(colr, a), stroke=6))

def bread_loaf(c, x, y, s, cut=0.0, alpha=255, seed=5, steam=0.0, t=0.0):
    """Baked loaf (side view, resting on y). cut 0..1 reveals the crumb with its frozen gas holes."""
    a = int(alpha); w_ = 300 * s; h_ = 300 * s
    p = skia.Path(); p.moveTo(x - w_, y)
    p.cubicTo(x - w_ * 1.08, y - h_ * 0.7, x - w_ * 0.6, y - h_, x, y - h_)
    p.cubicTo(x + w_ * 0.6, y - h_, x + w_ * 1.08, y - h_ * 0.7, x + w_, y); p.close()
    c.drawOval(skia.Rect(x - w_ * 1.05, y - 18 * s, x + w_ * 1.05, y + 24 * s), P(color=col('#1b2a4a', int(a * 0.2)), blur=10 * s))
    c.drawPath(p, rad(x - w_ * 0.3, y - h_ * 0.85, w_ * 1.9, [col('#f0b45c', a), col(CRUST, a), col('#8d5418', a)], [0, 0.55, 1]))
    if cut > 0:
        c.save(); c.clipPath(p, doAntiAlias=True)
        inner = skia.Path(); m = 22 * s
        inner.moveTo(x - w_ + m, y)
        inner.cubicTo(x - w_ * 1.08 + m * 1.4, y - h_ * 0.7 + m * 0.5, x - w_ * 0.6, y - h_ + m, x, y - h_ + m)
        inner.cubicTo(x + w_ * 0.6, y - h_ + m, x + w_ * 1.08 - m * 1.4, y - h_ * 0.7 + m * 0.5, x + w_ - m, y); inner.close()
        c.saveLayerAlpha(None, int(a * clamp(cut)))
        c.drawPath(inner, rad(x, y - h_ * 0.5, w_, [col('#fff4dc'), col(CRUMB), col('#efd7a6')], [0, 0.6, 1]))
        c.save(); c.clipPath(inner, doAntiAlias=True)
        rnd = random.Random(seed)
        for i in range(70):
            hx = x + rnd.uniform(-0.9, 0.9) * w_; hy = y - rnd.uniform(0.05, 0.9) * h_
            hr = rnd.uniform(4, 15) * s; asp = rnd.uniform(0.6, 1.0)
            c.drawOval(skia.Rect(hx - hr, hy - hr * asp, hx + hr, hy + hr * asp), P(color=col('#d9b97a')))
            c.drawArc(skia.Rect(hx - hr, hy - hr * asp, hx + hr, hy + hr * asp), 20, 140, False, P(color=col('#fffaf0'), stroke=max(1.5, hr * 0.25)))
        c.restore(); c.restore(); c.restore()
    else:
        for k in range(3):
            sx = x - w_ * 0.45 + k * w_ * 0.42
            sc_ = skia.Path(); sc_.moveTo(sx - 40 * s, y - h_ * 0.62); sc_.quadTo(sx, y - h_ * 0.86, sx + 50 * s, y - h_ * 0.78)
            c.drawPath(sc_, P(color=col('#f8d9a0', a), stroke=16 * s)); c.drawPath(sc_, P(color=col('#e6b26a', a), stroke=7 * s))
    c.drawPath(p, P(color=col('#7a4612', a), stroke=max(2, 5 * s)))
    if steam > 0:
        for i in range(3):
            ph = (t * 0.5 + i / 3) % 1.0; sx = x + (i - 1) * 110 * s
            sp = skia.Path(); sp.moveTo(sx, y - h_ - 20 * s)
            sp.cubicTo(sx + 40 * s, y - h_ - 80 * s, sx - 40 * s, y - h_ - 140 * s, sx + 10 * s * math.sin(t * 2 + i), y - h_ - 200 * s)
            c.drawPath(sp, P(color=col('#ffffff', int(a * steam * 0.7 * (1 - ph) + a * steam * 0.15)), stroke=12 * s))

def oven(c, x, y, s, glow=0.0, t=0.0, alpha=255, door=True):
    """Front of a plain oven; (x, y) = window centre. Returns window rect (in canvas units) for drawing inside."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRoundRect(skia.Rect(-380, -330, 380, 360), 46, 46, lin(c, (0, -330, 0, 360), [col('#f4f6fa', a), col('#c9d1de', a)]))
    c.drawRoundRect(skia.Rect(-380, -330, 380, 360), 46, 46, P(color=col('#1b2a4a', a), stroke=7))
    c.drawRoundRect(skia.Rect(-360, -310, 360, -230), 24, 24, P(color=col('#1b2a4a', int(a * 0.9))))
    for i in range(4):
        kx = -260 + i * 130
        c.drawCircle(kx, -270, 24, P(color=col('#dfe5ec', a))); c.drawLine(kx, -270, kx + 14, -286, P(color=col('#1b2a4a', a), stroke=5))
    c.drawCircle(250, -270, 9, P(color=col('#ff5c85' if glow > 0.05 else '#55607a', a)))
    c.drawRoundRect(skia.Rect(-300, -180, 300, 260), 30, 30, P(color=col('#2a2f3a', a)))
    g = clamp(glow)
    c.drawRoundRect(skia.Rect(-280, -160, 280, 240), 22, 22, rad(0, 40, 420, [col(mix_hx('#3a3f4c', '#ffb35c', g), a), col(mix_hx('#2a2f3a', '#c2531c', g), a)]))
    for yy in (-140, 220):
        for i in range(7):
            xx = -240 + i * 80
            c.drawLine(xx, yy, xx + 50, yy, P(color=col(mix_hx('#55607a', '#ff6b2c', g), a), stroke=10))
    c.drawLine(-280, 160, 280, 160, P(color=col('#9aa3b0', a), stroke=6))
    if door:
        c.drawLine(-200, 300, 200, 300, P(color=col('#9aa3b0', a), stroke=22)); c.drawLine(-200, 300, 200, 300, P(color=col('#e8edf3', a), stroke=10))
    c.restore()

def crater(c, x, y, r, alpha=255, light=(-1, -1), squash=0.55, base='#8e8f95', fresh=0.0):
    """Bowl-shaped impact crater on a surface (oblique view): raised rim, shadowed far wall, lit near wall."""
    a = int(alpha); ry = r * squash
    rim = skia.Rect(x - r * 1.18, y - ry * 1.18, x + r * 1.18, y + ry * 1.18)
    c.drawOval(rim, P(color=col(mix_hx(base, '#ffffff', 0.25), a)))
    if fresh > 0:
        rnd = random.Random(int(x * 7 + y))
        for i in range(14):
            ang = rnd.uniform(0, 2 * math.pi); L = r * rnd.uniform(1.4, 2.4)
            c.drawLine(x + math.cos(ang) * r * 1.1, y + math.sin(ang) * ry * 1.1, x + math.cos(ang) * L, y + math.sin(ang) * L * squash,
                       P(color=col('#d8d9de', int(a * 0.6 * fresh)), stroke=r * 0.08))
    bowl = skia.Rect(x - r, y - ry, x + r, y + ry)
    c.drawOval(bowl, lin(c, (0, y - ry, 0, y + ry), [col(mix_hx(base, '#000000', 0.55), a), col(mix_hx(base, '#000000', 0.2), a), col(mix_hx(base, '#ffffff', 0.15), a)], [0, 0.55, 1]))
    c.drawOval(skia.Rect(x - r * 0.55, y - ry * 0.2, x + r * 0.55, y + ry * 0.55), P(color=col(mix_hx(base, '#000000', 0.12), int(a * 0.8))))
    c.drawArc(rim, 200, 140, False, P(color=col(mix_hx(base, '#ffffff', 0.5), a), stroke=max(2, r * 0.07)))
    c.drawArc(bowl, 20, 140, False, P(color=col(mix_hx(base, '#000000', 0.45), int(a * 0.8)), stroke=max(2, r * 0.05)))

def moon_ground(c, y, t=0.0, seed=4, x0=-20, x1=W + 20, y1=H, alpha=255, craters=True):
    """Grey lunar plain from y down, with a gentle horizon and small craters + pebbles."""
    a = int(alpha); p = skia.Path(); p.moveTo(x0, y + 10)
    for i in range(13):
        xx = lerp(x0, x1, i / 12); p.lineTo(xx, y + 14 * math.sin(i * 1.3 + seed))
    p.lineTo(x1, y1); p.lineTo(x0, y1); p.close()
    c.drawPath(p, lin(c, (0, y - 20, 0, y1), [col('#b7b8bd', a), col('#8a8b91', a), col('#6c6d73', a)], [0, 0.4, 1]))
    rnd = random.Random(seed)
    if craters:
        for i in range(9):
            cx = rnd.uniform(x0 + 40, x1 - 40); cy = rnd.uniform(y + 60, min(y1, y + 700)); cr = rnd.uniform(14, 46) * (0.5 + (cy - y) / 700)
            crater(c, cx, cy, cr, alpha=a, base='#8e8f95')
    for i in range(40):
        px = rnd.uniform(x0, x1); py = rnd.uniform(y + 20, min(y1, y + 800)); pr = rnd.uniform(2, 6)
        c.drawCircle(px, py, pr, P(color=col('#5e5f65', int(a * 0.8))))

def impact_flash(c, x, y, k, r=200, alpha=255):
    """Bright impact burst: flash + expanding ring + debris specks; k 0..1 = time since impact."""
    if k <= 0 or k >= 1: return
    a = int(alpha)
    f = max(0, 1 - k * 2.5)
    c.drawCircle(x, y, r * (0.4 + k), rad(x, y, r * (0.4 + k), [col('#ffffff', int(a * f)), col('#ffd23f', int(a * 0.6 * f)), col('#ff8a3c', 0)], [0, 0.4, 1]))
    c.drawOval(skia.Rect(x - r * 1.6 * k, y - r * 0.6 * k, x + r * 1.6 * k, y + r * 0.6 * k), P(color=col('#e8e9ee', int(a * (1 - k) * 0.8)), stroke=10 * (1 - k) + 2))
    rnd = random.Random(int(x + y))
    for i in range(18):
        ang = rnd.uniform(math.pi * 1.05, math.pi * 1.95); sp = rnd.uniform(0.5, 1.0) * r * 1.8
        px = x + math.cos(ang) * sp * k; py = y + math.sin(ang) * sp * k + 300 * k * k
        c.drawCircle(px, py, rnd.uniform(3, 8) * (1 - k * 0.5), P(color=col('#9a9ba1', int(a * (1 - k)))))

BIRD_BODY = '#5b7fa6'; BIRD_BELLY = '#eef3f8'; BIRD_WING = '#3f5f86'

def bird(c, x, y, s, t, flap=None, rot=0.0, alpha=255, body=BIRD_BODY, belly=BIRD_BELLY, wing=BIRD_WING, glide=False, section=False, fold=None):
    """Plain songbird-like flyer, side view, flying right. flap = wing phase 0..1 (0 = top of upstroke,
    0.5 = bottom of downstroke); None = flap from t. Natural small eye, no expression."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    ph = (t * 3.2) % 1.0 if flap is None else flap % 1.0
    ang = 0.0 if glide else 62 * math.cos(ph * 2 * math.pi)   # +62 = wings up, -62 = down
    def wing_shape(sign, shade):
        fk = (0.45 * max(0.0, -math.sin(ph * 2 * math.pi)) if fold is None else fold) if not glide else 0.0   # wing folds on the upstroke
        c.save(); c.translate(-10, -18); c.scale(1 - 0.25 * fk, (math.sin(math.radians(ang)) if abs(ang) > 4 else (0.07 if not glide else 0.12)) * (1 - fk))
        wp = skia.Path(); wp.moveTo(-70, 0); wp.cubicTo(-60, -sign * 120, 40, -sign * 250, 150, -sign * 300)
        wp.cubicTo(110, -sign * 200, 60, -sign * 80, 60, 0); wp.close()
        c.drawPath(wp, lin(c, (0, 0, 0, -sign * 300), [col(shade, a), col(mix_hx(shade, '#1b2a4a', 0.35), a)]))
        for k in range(4):
            fx = 40 + k * 26
            c.drawLine(fx - 70, -sign * (60 + k * 30), fx + 40, -sign * (210 + k * 18), P(color=col('#ffffff', int(a * 0.22)), stroke=4))
        c.drawPath(wp, P(color=col('#1b2a4a', int(a * 0.5)), stroke=3))
        c.restore()
    wing_shape(1, mix_hx(wing, '#1b2a4a', 0.3))   # far wing
    # tail
    tl = skia.Path(); tl.moveTo(-110, -10); tl.lineTo(-215, -40); tl.lineTo(-222, 10); tl.lineTo(-110, 14); tl.close()
    c.drawPath(tl, P(color=col(mix_hx(body, '#1b2a4a', 0.25), a)))
    # body
    bp = skia.Path(); bp.moveTo(-130, 0); bp.cubicTo(-90, -48, 60, -58, 110, -30); bp.cubicTo(130, -10, 120, 30, 80, 38)
    bp.cubicTo(20, 50, -80, 40, -130, 0); bp.close()
    c.drawPath(bp, lin(c, (0, -58, 0, 50), [col(body, a), col(mix_hx(body, belly, 0.4), a)]))
    bl = skia.Path(); bl.moveTo(-90, 18); bl.cubicTo(-20, 50, 70, 46, 110, 10); bl.cubicTo(90, 40, 0, 52, -90, 18); bl.close()
    c.drawPath(bl, P(color=col(belly, a)))
    # head + beak + eye
    c.drawCircle(118, -36, 40, lin(c, (0, -76, 0, 4), [col(body, a), col(mix_hx(body, belly, 0.3), a)]))
    bk = skia.Path(); bk.moveTo(150, -46); bk.lineTo(196, -32); bk.lineTo(150, -22); bk.close()
    c.drawPath(bk, P(color=col('#f2a541', a)))
    c.drawCircle(132, -44, 8, P(color=col('#14181f', a))); c.drawCircle(134.5, -46.5, 2.5, P(color=col('#ffffff', a)))
    if section:
        c.drawCircle(0, -4, 34, P(color=col('#ffd23f', int(a * 0.85))))
    wing_shape(1, wing)   # near wing
    c.restore()

def swift_bird(c, x, y, s, t, rot=0.0, alpha=255, colr='#2b2f3a'):
    """Common swift silhouette seen from below: slim body, long sickle wings, short forked tail."""
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    fl = 0.12 * math.sin(t * 14)
    for sx in (-1, 1):
        wp = skia.Path(); wp.moveTo(sx * 14, -10)
        wp.cubicTo(sx * 120, -40 - 60 * fl, sx * 230, -10 - 80 * fl, sx * 300, 60 - 90 * fl)
        wp.cubicTo(sx * 210, 20 - 40 * fl, sx * 110, 18, sx * 14, 22); wp.close()
        c.drawPath(wp, lin(c, (0, -60, 0, 60), [col(mix_hx(colr, '#ffffff', 0.15), a), col(colr, a)]))
    bp = skia.Path(); bp.addOval(skia.Rect(-22, -60, 22, 70))
    c.drawPath(bp, P(color=col(colr, a)))
    tl = skia.Path(); tl.moveTo(-14, 60); tl.lineTo(-30, 120); tl.lineTo(0, 92); tl.lineTo(30, 120); tl.lineTo(14, 60); tl.close()
    c.drawPath(tl, P(color=col(colr, a)))
    c.drawOval(skia.Rect(-10, -58, 10, -40), P(color=col('#d8d4cc', int(a * 0.8))))
    c.restore()

def hollow_bone(c, x, y, s, section=1.0, alpha=255, t=0.0):
    """Bird bone cut open lengthwise: thin wall, hollow inside, criss-cross struts (trabeculae)."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    outer = skia.Path(); outer.moveTo(-330, -50); outer.cubicTo(-400, -110, -430, -10, -380, 0); outer.cubicTo(-430, 10, -400, 110, -330, 50)
    outer.lineTo(330, 50); outer.cubicTo(400, 110, 430, 10, 380, 0); outer.cubicTo(430, -10, 400, -110, 330, -50); outer.close()
    c.drawPath(outer, lin(c, (0, -100, 0, 100), [col('#fffaf0', a), col('#ecdcbc', a)]))
    if section > 0:
        c.save(); c.saveLayerAlpha(None, int(a * clamp(section)))
        cav = skia.Rect(-330, -34, 330, 34)
        c.drawRoundRect(cav, 30, 30, P(color=col('#3b4a6b')))
        c.save(); cl = skia.Path(); cl.addRoundRect(cav, 30, 30); c.clipPath(cl, doAntiAlias=True)
        for i in range(12):
            xx = -310 + i * 56
            c.drawLine(xx, -34, xx + 40, 34, P(color=col('#f3e6c8'), stroke=7))
            c.drawLine(xx + 40, -34, xx, 34, P(color=col('#f3e6c8'), stroke=5))
        c.restore(); c.restore(); c.restore()
    c.drawPath(outer, P(color=col('#b08a5a', a), stroke=5))
    c.restore()

def slab(c, x, y, w_, h_, kind='metal', alpha=255, seed=1, heat=0.0):
    """Material block (oblique). kind 'metal' (brushed steel) or 'wood' (grain). (x, y) = front-top-left corner."""
    a = int(alpha); d = h_ * 0.45
    top = skia.Path(); top.moveTo(x, y); top.lineTo(x + d, y - d); top.lineTo(x + w_ + d, y - d); top.lineTo(x + w_, y); top.close()
    side = skia.Path(); side.moveTo(x + w_, y); side.lineTo(x + w_ + d, y - d); side.lineTo(x + w_ + d, y + h_ - d); side.lineTo(x + w_, y + h_); side.close()
    front = skia.Rect(x, y, x + w_, y + h_)
    if kind == 'metal':
        c.drawPath(top, lin(c, (x, 0, x + w_ + d, 0), [col('#e9eef4', a), col('#b7c1cd', a), col('#f4f7fa', a), col('#aab5c2', a)], vertical=False))
        c.drawPath(side, P(color=col('#7f8b99', a)))
        c.drawRect(front, lin(c, (0, y, 0, y + h_), [col('#c7d0db', a), col('#8e9aa8', a)]))
        rnd = random.Random(seed)
        c.save(); c.clipPath(top, doAntiAlias=True)
        for i in range(14):
            yy = y - d * rnd.uniform(0.1, 0.9); xx = x + rnd.uniform(0, w_)
            c.drawLine(xx + (y - yy), yy, xx + (y - yy) + rnd.uniform(60, 180), yy, P(color=col('#ffffff', int(a * 0.35)), stroke=2))
        c.restore()
        edge = '#5d6876'
    else:
        c.drawPath(top, lin(c, (0, y - d, 0, y), [col('#e6b67a', a), col('#c98d4e', a)]))
        c.drawPath(side, P(color=col('#8a5a2c', a)))
        c.drawRect(front, lin(c, (0, y, 0, y + h_), [col('#c2864a', a), col('#9c6534', a)]))
        rnd = random.Random(seed)
        c.save(); c.clipPath(top, doAntiAlias=True)
        for i in range(9):
            yy = y - d * (i + 0.5) / 9; wob = rnd.uniform(4, 10)
            gp = skia.Path(); gp.moveTo(x - 20 + (y - yy), yy)
            for k in range(1, 21):
                xx = x + (y - yy) + (w_ + 40) * k / 20; gp.lineTo(xx, yy + wob * math.sin(k * 0.9 + i))
            c.drawPath(gp, P(color=col('#a86d34', int(a * 0.55)), stroke=3))
        c.restore()
        for i in range(4):
            yy = y + h_ * (i + 0.5) / 4
            c.drawLine(x + 6, yy, x + w_ - 6, yy + 4 * math.sin(i), P(color=col('#7d4c22', int(a * 0.45)), stroke=3))
        edge = '#5e3a1a'
    if heat > 0:
        c.drawPath(top, P(color=col('#ff8a3c', int(a * 0.45 * clamp(heat)))))
    for p_ in (top, side): c.drawPath(p_, P(color=col(edge, a), stroke=4))
    c.drawRect(front, P(color=col(edge, a), stroke=4))

def fingertip(c, x, y, s, rot=0.0, alpha=255, skin='#f2c9a6', cold=0.0, fade_top=None):
    """Plain index finger pointing down, tip at (x, y). cold 0..1 tints the tip blue."""
    if fade_top is not None:   # fade the finger out towards the top (canvas y), keeps it out of the caption zone
        c.saveLayer(None)
        fingertip(c, x, y, s, rot, alpha, skin, cold, None)
        pm = skia.Paint(AntiAlias=True); pm.setBlendMode(skia.BlendMode.kDstIn)
        pm.setShader(skia.GradientShader.MakeLinear([skia.Point(0, fade_top), skia.Point(0, fade_top + 160)], [col('#000000', 0), col('#000000', 255)]))
        c.drawRect(skia.Rect(0, 0, W, H), pm); c.restore(); return
    a = int(alpha); c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    fp = skia.Path(); fp.moveTo(-62, -520); fp.lineTo(-62, -70); fp.cubicTo(-62, -10, -30, 8, 0, 8); fp.cubicTo(30, 8, 62, -10, 62, -70); fp.lineTo(62, -520); fp.close()
    tip = mix_hx(skin, '#9cc8ff', 0.55 * clamp(cold))
    c.drawPath(fp, lin(c, (-62, 0, 62, 0), [col(mix_hx(skin, '#c98a6a', 0.3), a), col(mix_hx(skin, '#ffffff', 0.2), a), col(mix_hx(skin, '#c98a6a', 0.35), a)], vertical=False))
    c.save(); c.clipPath(fp, doAntiAlias=True)
    c.drawRect(skia.Rect(-70, -140, 70, 20), lin(c, (0, -140, 0, 20), [col(tip, 0), col(tip, int(a * 0.9))]))
    c.restore()
    nail = skia.Path(); nail.addRoundRect(skia.Rect(-36, -150, 36, -60), 30, 30)
    c.drawPath(nail, lin(c, (0, -150, 0, -60), [col('#fbe3d6', a), col('#f3c9b8', a)]))
    c.drawPath(nail, P(color=col('#c98a6a', int(a * 0.6)), stroke=3))
    for yy in (-300, -330):
        c.drawArc(skia.Rect(-40, yy - 12, 40, yy + 12), 20, 140, False, P(color=col('#c98a6a', int(a * 0.5)), stroke=4))
    c.drawPath(fp, P(color=col('#b9805e', a), stroke=4))
    c.restore()

def heat_dot(c, x, y, r, alpha=230, colr='#ff7a3c'):
    """Small glowing heat-energy particle."""
    if alpha <= 0: return
    a = int(alpha)
    c.drawCircle(x, y, r * 2.2, rad(x, y, r * 2.2, [col(colr, int(a * 0.5)), col(colr, 0)]))
    c.drawCircle(x, y, r, P(color=col(mix_hx(colr, '#ffffff', 0.35), a)))
