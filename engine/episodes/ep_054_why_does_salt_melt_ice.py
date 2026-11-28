"""Episode 54 (EN, general audience): Why does salt melt ice?
Facts checked (Scientific American "Salt Doesn't Melt Ice - Here's How It Makes Winter Streets Safer"; PBS NewsHour
"Why does salt melt road ice?"; HowStuffWorks "Why Does Salt Melt Ice on the Roads in Winter?"; University of
Minnesota MnLTAP SmartWinterSalt "Deicing use"):
- Salt needs liquid water to work; ice is usually covered by a thin film of liquid water, and salt dissolves in it.
- At the ice/water boundary, water molecules constantly leave the ice (melting) and join it (freezing); at 32 F / 0 C
  the two rates are equal.
- Dissolved salt splits into sodium and chloride ions, which get in the way of water molecules re-freezing; melting
  continues, so the balance tips toward melting (freezing-point depression). Salt water freezes below 32 F.
- Rock salt (sodium chloride) works poorly at low pavement temperatures; MnLTAP gives ~15 F as its practical lowest
  melting temperature (its eutectic limit is about -6 F / -21 C).
- Ice + salt mixtures get colder than 32 F (the melting draws heat from the mix); classic hand-crank ice cream makers
  surround the cream can with ice and rock salt for this reason.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
ICE = '#bfe6ff'

# ---------- shared scenery ----------
def winter_bg(c, t, y=1240):
    sky(c, '#cfe8ff', '#eef7ff', mid='#dff0ff')
    clouds(c, t, seed=3, n=2, y0=640, y1=820, a=170)
    # snowy verge + sidewalk
    c.drawRect(skia.Rect(0, y - 70, W, y), lin(c, (0, y - 70, 0, y), [col('#ffffff'), col('#e6eef7')]))
    c.drawRect(skia.Rect(0, y, W, H), lin(c, (0, y, 0, H), [col('#b9c3d1'), col('#8d99ab')]))
    for i in range(1, 4):
        xx = i * 270 + 20
        c.drawLine(xx, y, xx - 60, H, P(color=col('#7d8899', 160), stroke=5))
    # ice sheet
    p = skia.Path(); p.addRoundRect(skia.Rect(60, y + 40, W - 60, y + 330), 60, 60)
    c.drawPath(p, lin(c, (0, y + 40, 0, y + 330), [col('#e8f7ff', 210), col('#9fd6f5', 200)]))
    c.drawPath(p, P(color=col('#ffffff', 200), stroke=4))
    for (x0, y0, x1, y1) in ((150, y + 90, 330, y + 70), (640, y + 110, 860, y + 85), (420, y + 250, 560, y + 235)):
        c.drawLine(x0, y0, x1, y1, P(color=col('#ffffff', 220), stroke=9))

GRAINS = [(220, 1330), (330, 1440), (470, 1360), (610, 1470), (720, 1350), (850, 1430), (390, 1520), (780, 1530), (560, 1300)]

def salt_on_ice(c, t, drop0=0.0, wet=0.0, dry=False):
    for i, (gx, gy) in enumerate(GRAINS):
        k = prog(t, drop0 + i * 0.07, 0.35)
        if k <= 0: continue
        yy = lerp(gy - 700, gy, ease_in_out(k))
        if k >= 1 and wet > 0 and not dry:
            rr = 22 + 70 * wet * (0.8 + 0.2 * math.sin(i))
            c.drawOval(skia.Rect(gx - rr * 1.3, gy - rr * 0.45 + 18, gx + rr * 1.3, gy + rr * 0.45 + 18), lin(c, (0, gy - rr, 0, gy + rr), [col('#5fb6ec', 170), col('#2f86d0', 150)]))
            c.drawOval(skia.Rect(gx - rr * 1.3, gy - rr * 0.45 + 18, gx + rr * 1.3, gy + rr * 0.45 + 18), P(color=col('#ffffff', 150), stroke=3))
        salt_crystal(c, gx, yy, 0.5 * (1 - 0.55 * wet * (0 if dry else 1)), t, seed=i, face_on=False)

# ---------- shared micro view (water molecules at the ice surface) ----------
SURF = 1120          # liquid / ice boundary at the start
ROWS, COLS, DX, DY = 5, 9, 104, 90

def slot(r, k):
    return 124 + k * DX + (DX / 2 if r % 2 else 0), SURF + 40 + r * DY

def micro(c, t, t0=0.0, swap=1.0, ions=0.0, melt=0.0, block=0.0, ions_in=0.0, temp_hint=None):
    """t0 = when the exchange starts; swap 0..1 strength of melting/freezing back and forth; ions 0..1 shows ions;
    melt 0..1 removes the top ice rows (they drift into the liquid)."""
    sky(c, '#d8efff', '#9fd0ff')
    # liquid band and ice block
    top_y = SURF - 260
    c.drawRect(skia.Rect(0, top_y, W, SURF + 10), lin(c, (0, top_y, 0, SURF), [col('#7cc4ff', 90), col('#4fb3ff', 150)]))
    surf = SURF + melt * 1.6 * DY
    c.drawRect(skia.Rect(0, surf, W, H), lin(c, (0, surf, 0, H), [col('#e9f7ff', 235), col('#b5e0fa', 235)]))
    c.drawLine(0, surf, W, surf, P(color=col('#ffffff', 230), stroke=6))
    rnd = random.Random(4)
    # free liquid molecules
    for i in range(9):
        bx = rnd.uniform(90, 990); by = rnd.uniform(top_y + 50, SURF - 60); ph = rnd.uniform(0, 6)
        x = bx + math.sin(t * 1.3 + ph) * 40; y = by + math.cos(t * 1.1 + ph * 2) * 26
        water_molecule(c, x, y, 26, t, seed=i, rot=(t * 40 + ph * 50) % 360, face_on=False)
    # ice lattice; top row molecules swap / melt away
    for r in range(ROWS - 1, -1, -1):
        for k in range(COLS):
            x, y = slot(r, k)
            gone_k = 0.0
            if r == 0: gone_k = prog(melt, k / COLS * 0.55, 0.45)
            elif r == 1: gone_k = prog(melt, 0.55 + k / COLS * 0.3, 0.15)
            ex = 0.0
            if r == 0 and swap > 0 and gone_k <= 0 and k % 2 == 0:
                ph = ((t - t0) / 2.6 + k * 0.23) % 1.0 if t > t0 else 0
                up = ease_in_out(prog(ph, 0.15, 0.3)) - ease_in_out(prog(ph, 0.6, 0.3))
                ex = up * swap
            if gone_k > 0:
                drift = ease_out(gone_k)
                x += math.sin(k * 2.1) * 120 * drift + math.sin(t * 1.4 + k) * 24 * drift
                y -= (y - (SURF - 120 - 60 * math.cos(k * 1.7))) * drift
            y -= ex * 190
            wob = math.sin(t * 6 + r * 1.3 + k) * (2.5 + 20 * gone_k)
            water_molecule(c, x + wob, y, 26, t, seed=r * 9 + k, rot=180 + 10 * math.sin(t * 2 + k) + 140 * gone_k, face_on=False)
    # ions wandering in the film, right at the surface
    if ions > 0:
        rni = random.Random(7)
        for i in range(8):
            bx = 110 + i * 120 + rni.uniform(-20, 20); ph = rni.uniform(0, 6)
            yy = lerp(SURF - 600, SURF - 50 - rni.uniform(0, 140), ease_out(prog(ions_in, i * 0.06, 0.5)))
            x = bx + math.sin(t * 1.6 + ph) * 34; y = yy + math.cos(t * 1.2 + ph) * 18
            ion(c, x, y, 24, 1 if i % 2 == 0 else -1, alpha=int(255 * ions))

# ---------- 1: Hook (cold open: salt already landing on ice) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    winter_bg(c, t)
    wet = ease_in_out(prog(t, 0.9, D - 1.2))
    salt_on_ice(c, t, drop0=0.0, wet=wet)
    label_pill(c, 'SALT on ice', 540, 720, size=50, k=ease_back(prog(t, 0.3, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=SKYB)
    if t > t1:
        label_pill(c, 'NOT melting it', 540, 720, size=50, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, 'stops REFREEZING', 540, 860, size=50, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi=SKYB)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.05, 'sparkle'), (0.3, 'pop'), (t1 + 0.6, 'pop'), (t1 + 2.0, 'pop')]

# ---------- 2: A thin film of water ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    winter_bg(c, t)
    k = ease_out(prog(t, t0 + 0.2, 0.8))
    def inner(cc):
        micro(cc, t, t0=99, swap=0)
    magnifier(c, 540, 1180, 330 * (0.3 + 0.7 * k) if k > 0 else 1, inner, t)
    label_pill(c, 'liquid FILM', 540, 720, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=SKYB)
    arrow(c, 540, 770, 540, 905, colr=NAVY, w=12, alpha=int(230 * prog(t, t0 + 1.6, 0.3)))
    label_pill(c, 'ICE', 540, 1560, size=48, k=ease_back(prog(t, t0 + 2.4, 0.4)), fill=NAVY, hi=SKYB)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.4, 'pop'), (t0 + 2.4, 'pop')]

# ---------- 3: Melting and freezing in balance ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    micro(c, t, t0=t0 + 0.3, swap=ease_out(prog(t, t0 + 0.3, 0.5)))
    label_pill(c, 'LEAVING  vs  JOINING', 540, 720, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.3, 0.4))
        # balance scale icon
        if k > 0:
            c.save(); c.translate(540, 1590); c.scale(k, k)
            c.drawRoundRect(skia.Rect(-250, -50, 250, 50), 50, 50, P(color=col('#ffffff', 240)))
            text_block(c, '32°F: EVEN', 0, 0, size=50, fill=NAVY, hi=SKYB, stroke='#ffffff', maxw=2000)
            c.restore()

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.8, 'pop'), (t1 + 0.3, 'click')]

# ---------- 4: Salt dissolves into ions ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    micro(c, t, t0=0, swap=1.0, ions=prog(t, t0 + 1.4, 0.3), ions_in=prog(t, t0 + 1.4, 1.6))
    # salt grain dropping into the film and dissolving
    dk = prog(t, t0 + 0.1, 0.8); sk = 1 - prog(t, t0 + 1.0, 0.6)
    if sk > 0:
        salt_crystal(c, 540, lerp(640, 900, ease_in_out(dk)), 1.4 * (0.4 + 0.6 * sk), t, face_on=False, alpha=int(255 * sk))
    label_pill(c, 'Na+  and  Cl–', 540, 720, size=50, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=GOLD)
    label_pill(c, 'charged IONS', 540, 1590, size=46, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=HOT)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.1, 'whoosh'), (t0 + 1.2, 'sparkle'), (t0 + 2.0, 'pop'), (t0 + 2.6, 'pop')]

# ---------- 5: Ions block refreezing -> melting wins (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    mk = ease_in_out(prog(t, t1 - 0.6, D - t1 - 0.2))
    micro(c, t, t0=0, swap=1.0 - 0.8 * prog(t, t0 + 0.5, 1.0), ions=1.0, ions_in=1.0, melt=mk)
    # blocked return attempts: X marks
    for i, xx in enumerate((230, 540, 850)):
        bk = prog(t, t0 + 0.8 + i * 0.5, 0.3) * (1 - prog(t, t1 + 0.4, 0.4))
        if bk > 0:
            L = 26 * ease_back(min(1, bk * 1.4))
            for sx in (-1, 1):
                pp = P(color=col(HOT, int(255 * bk)), stroke=11); pp.setStrokeCap(skia.Paint.kRound_Cap)
                c.drawLine(xx - L, 990 - L * sx, xx + L, 990 + L * sx, pp)
    label_pill(c, 'ions BLOCK the way', 540, 720, size=46, k=ease_back(prog(t, t0 + 0.6, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'MELTING wins', 540, 720, size=56, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 0.8, 'click'), (t0 + 1.3, 'click'), (t0 + 1.8, 'click'), (t1 + 0.2, 'ding')]

# ---------- 6: Salt water freezes lower; weak below ~15 F ----------
def glass(c, x, y, frozen=0.0, salty=False, t=0.0):
    """Drinking glass with water; (x, y) = bottom centre. frozen 0..1 turns the water into white-blue ice."""
    w0, w1, h = 150, 175, 420
    p = skia.Path(); p.moveTo(x - w1, y - h); p.lineTo(x + w1, y - h); p.lineTo(x + w0, y); p.lineTo(x - w0, y); p.close()
    lv = y - h * 0.78
    wp = skia.Path(); k = (y - lv) / h; wl = lerp(w0, w1, k)
    wp.moveTo(x - wl, lv); wp.lineTo(x + wl, lv); wp.lineTo(x + w0, y); wp.lineTo(x - w0, y); wp.close()
    c.drawPath(wp, lin(c, (0, lv, 0, y), [col(mix_hx('#4fb3ff', '#e9f7ff', frozen), 230), col(mix_hx('#1a7fd9', '#a9dcfa', frozen), 230)]))
    if frozen > 0:
        rnd = random.Random(3)
        for i in range(14):
            ax = x + rnd.uniform(-120, 120); ay = rnd.uniform(lv + 30, y - 30)
            L = rnd.uniform(18, 40) * frozen
            for ang in (0, 60, 120):
                r_ = math.radians(ang)
                c.drawLine(ax - math.cos(r_) * L, ay - math.sin(r_) * L, ax + math.cos(r_) * L, ay + math.sin(r_) * L, P(color=col('#ffffff', int(220 * frozen)), stroke=4))
    else:
        for i in range(5):
            ph = (t * 0.4 + i * 0.2) % 1
            c.drawCircle(x - 90 + i * 45, lerp(y - 40, lv + 20, ph), 7, P(color=col('#ffffff', int(150 * math.sin(ph * math.pi)))))
    if salty:
        rnd = random.Random(8)
        for i in range(16):
            ion(c, x + rnd.uniform(-115, 115), rnd.uniform(lv + 40, y - 40) + math.sin(t * 2 + i) * 8, 13, 1 if i % 2 else -1)
    c.drawPath(p, P(color=col('#ffffff', 70)))
    c.drawPath(p, P(color=col('#ffffff', 235), stroke=7))
    c.drawLine(x - w1 + 30, y - h + 30, x - w0 + 25, y - 40, P(color=col('#ffffff', 160), stroke=10))

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#d8efff', '#9fd0ff')
    c.drawRect(skia.Rect(0, 1420, W, H), lin(c, (0, 1420, 0, H), [col('#f4f7fb'), col('#c9d6e6')]))
    c.drawLine(0, 1420, W, 1420, P(color=col(NAVY, 70), stroke=4))
    if t < t1:
        fz = ease_in_out(prog(t, t0 + 0.8, 1.6))
        glass(c, 290, 1420, frozen=fz, t=t)
        glass(c, 790, 1420, frozen=0.0, salty=True, t=t)
        snow(c, t, seed=4, n=20, y0=600, y1=1000, alpha=int(180 * prog(t, t0 + 0.3, 0.6)))
        label_pill(c, 'WATER: frozen', 290, 760, size=40, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'SALT WATER: liquid', 790, 860, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
    else:
        winter_bg(c, t)
        salt_on_ice(c, t, drop0=t1 - 0.2, wet=0.0, dry=True)
        snow(c, t, seed=4, n=30, y0=600, y1=1240, alpha=int(220 * prog(t, t1, 0.6)))
        thermometer(c, 900, 1000, 1.0, level=0.5 - 0.35 * ease_in_out(prog(t, t1 + 0.2, 1.0)), hot=HOT)
        label_pill(c, 'below ~15°F: barely works', 470, 760, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 0.8, 'sparkle'), (t0 + 1.4, 'pop'), (t1, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 7: Wild part: ice + salt gets colder (ice cream maker) ----------
def bucket(c, x, y, t, salt_k=0.0, frost=0.0):
    """Wooden-style bucket seen from the front with a metal can inside, ice + salt around it. (x, y) = rim centre."""
    rw, h = 300, 420
    p = skia.Path(); p.moveTo(x - rw, y); p.lineTo(x + rw, y); p.lineTo(x + rw * 0.8, y + h); p.lineTo(x - rw * 0.8, y + h); p.close()
    c.drawPath(p, lin(c, (x - rw, 0, x + rw, 0), [col('#a8693d'), col('#d9a06a'), col('#b07444')], vertical=False, pos=[0, 0.45, 1]))
    for i in range(1, 6):
        xx = x - rw + i * rw / 3
        c.drawLine(xx, y + 4, lerp(xx, x, 0.2), y + h - 4, P(color=col('#7a4a28', 120), stroke=4))
    for yy in (y + 90, y + h - 90):
        k = (yy - y) / h; ww = rw * (1 - 0.2 * k)
        c.drawRect(skia.Rect(x - ww, yy - 12, x + ww, yy + 12), lin(c, (0, yy - 12, 0, yy + 12), [col('#c9d3e2'), col('#7d8aa3')]))
    # metal can
    c.drawRect(skia.Rect(x - 110, y - 160, x + 110, y + 30), lin(c, (x - 110, 0, x + 110, 0), [col('#9aa6ba'), col('#eef2f7'), col('#8a96aa')], vertical=False, pos=[0, 0.45, 1]))
    c.drawOval(skia.Rect(x - 110, y - 185, x + 110, y - 135), P(color=col('#dfe6ef')))
    c.drawOval(skia.Rect(x - 110, y - 185, x + 110, y - 135), P(color=col('#7d8aa3'), stroke=4))
    if frost > 0:
        rnd = random.Random(2)
        for i in range(40):
            fx = x + rnd.uniform(-105, 105); fy = y + rnd.uniform(-150, 20)
            c.drawCircle(fx, fy, rnd.uniform(3, 7), P(color=col('#ffffff', int(220 * frost))))
    # ice cubes around the can
    for i, (dx, dy, r_) in enumerate(((-210, -40, 12), (-160, -10, -8), (170, -35, 10), (220, -5, -14), (-240, 10, 4), (245, 15, 6))):
        ice_cube(c, x + dx, y + dy, 0.42, t, seed=i, face_on=False, rot=r_)
    if salt_k > 0:
        rnd = random.Random(9)
        for i in range(26):
            k = prog(salt_k, i / 40, 0.4)
            if k <= 0: continue
            sx = x + rnd.choice((-1, 1)) * rnd.uniform(130, 270); sy = y + rnd.uniform(-60, 30)
            salt_crystal(c, sx, lerp(sy - 400, sy, ease_in_out(k)), 0.18, t, seed=i, face_on=False)

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#d8efff', '#9fd0ff')
    c.drawRect(skia.Rect(0, 1480, W, H), lin(c, (0, 1480, 0, H), [col('#f4f7fb'), col('#c9d6e6')]))
    sk = prog(t, t0 + 0.6, 1.2)
    fr = ease_in_out(prog(t, t0 + 1.8, 2.0))
    bucket(c, 470, 1060, t, salt_k=sk, frost=fr)
    thermometer(c, 900, 1200, 1.2, level=0.5 - 0.32 * fr, hot=HOT)
    label_pill(c, 'ICE + SALT', 470, 720, size=50, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
    if fr > 0.3:
        label_pill(c, 'below 32°F', 860, 1580, size=42, k=ease_back(prog(t, t0 + 2.6, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        label_pill(c, 'ICE CREAM, frozen', 470, 840, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=HOT)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.6, 'sparkle'), (t0 + 2.6, 'pop'), (t1 + 0.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    winter_bg(c, t)
    salt_on_ice(c, t, drop0=-5, wet=1.0)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0: label_pill(c, 'salt BLOCKS refreezing', 540, 700, size=46, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: GLOW STICKS', 540, 820, size=44, k=kk, fill=NAVY, hi=HOT)
        glow_stick(c, 540, 960, 0.5 * kk, -12, '#7dff5a', glow=1.0, crack=1.0, t=t)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why does salt melt ice?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why does salt melt ice?', 'Why does SALT melt ice?'),
            ("Here's the twist: it doesn't melt anything. It stops water from freezing back.", 'It stops REFREEZING')], tail=0.9),
        dict(name='film', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Zoom in, and ice is usually coated in a thin film of liquid water.', 'A thin FILM of water')], tail=1.2),
        dict(name='balance', draw=s3, sfx_fn=s3_sfx, ambience='water', lines=[
            ('Right at the surface, molecules keep breaking free and freezing back on, like a busy doorway.', 'Leaving and JOINING'),
            ('At thirty-two degrees, both happen equally fast.', 'At 32°F: a TIE')], tail=1.0),
        dict(name='ions', draw=s4, sfx_fn=s4_sfx, ambience='water', lines=[
            ('Salt dissolves in that film and splits into charged bits: sodium and chloride.', 'Salt splits into IONS')], tail=1.2),
        dict(name='block', draw=s5, sfx_fn=s5_sfx, trans='punch', ambience='water', lines=[
            ('Those bits get in the way. Fewer molecules make it back onto the ice,', 'They BLOCK refreezing'),
            ('but melting carries on. So the ice disappears.', 'Melting WINS')], tail=1.2),
        dict(name='limit', draw=s6, sfx_fn=s6_sfx, lines=[
            ('That means salt water freezes below thirty-two degrees.', 'Salt water freezes LOWER'),
            ('But below about fifteen degrees, rock salt barely works.', 'Weak below 15°F')], tail=1.1),
        dict(name='icecream', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: ice plus salt gets colder than ice alone.", 'Ice + salt gets COLDER'),
            ("That's how old-school ice cream makers freeze the cream.", 'Old-school ICE CREAM')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ("So salt doesn't melt ice. It blocks the refreezing.", 'Salt BLOCKS refreezing'),
            ('Next: how glow sticks glow.', 'Next: GLOW STICKS'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
