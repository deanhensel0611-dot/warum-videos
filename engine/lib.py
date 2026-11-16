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
def face(c, x, y, r, t=0.0, blink_seed=0, mood='happy', look=(0, 0)):
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

def text_block(c, text, cx, cy, size=94, maxw=880, fill='#ffffff', hi='#ffe14d', stroke='#1b2a4a', scale=1.0, alpha=255):
    """Wörter in GROSSBUCHSTABEN (>=3 Buchstaben) werden hervorgehoben."""
    lines = wrap(text, size, maxw); f = font(size); lh = size * 1.18
    c.save(); c.translate(cx, cy); c.scale(scale, scale)
    y0 = -lh * (len(lines) - 1) / 2 + size * 0.35
    for i, ln in enumerate(lines):
        words = ln.split(' '); widths = [f.measureText(w_) for w_ in words]; sp = f.measureText(' ')
        total = sum(widths) + sp * (len(words) - 1); x = -total / 2; y = y0 + i * lh
        for w_, ww in zip(words, widths):
            letters = ''.join(ch for ch in w_ if ch.isalpha())
            is_hi = len(letters) >= 3 and letters.isupper()
            sp_ = P(color=col(stroke, alpha), stroke=size * 0.2)
            c.drawString(w_, x, y, f, sp_)
            c.drawString(w_, x, y, f, P(color=col(hi if is_hi else fill, alpha)))
            x += ww + sp
    c.restore()

def caption(c, text, t_since, y=430):
    """Untertitel mit Pop-in. t_since = Sekunden seit Erscheinen."""
    if text is None or t_since < 0: return
    s = 0.55 + 0.45 * ease_back(prog(t_since, 0, 0.42), 2.2)
    yy = y + math.sin(t_since * 2.0) * 6
    al = int(255 * prog(t_since, 0, 0.15))
    c.save(); c.translate(0, 10)
    text_block(c, text, W / 2, yy, scale=s, alpha=int(al * 0.35), fill='#0b1a3a', hi='#0b1a3a', stroke='#0b1a3a')
    c.restore()
    text_block(c, text, W / 2, yy, scale=s, alpha=al)

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
    raise ValueError(kind)

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
    mixed = v * 1.0 + mus * float(os.environ.get('WARUM_MUSIC_VOL', '0.16')) * duck + fx * 0.22
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
        if cur: caption(c, cur['caption'], t - cur['start'] + 0.05, sc.get('cap_y', 430))
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

def render_into(c, ep, si, t, D, cues, prev):
    c.clear(skia.ColorWHITE)
    c.resetMatrix(); c.scale(OW / W, OH / H)
    sc = ep['scenes'][si]
    if prev is not None and t < XFADE:
        pD, pcues = prev
        draw_full(ep['scenes'][si - 1], c, pD + t, pD + XFADE, pcues)
        a = ease_in_out(t / XFADE)
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
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
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
