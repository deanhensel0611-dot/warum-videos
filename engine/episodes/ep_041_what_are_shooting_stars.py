"""Episode 41 (EN, general audience): What are shooting stars?
Facts checked (NASA Science "Meteors & Meteorites: Facts" and "In Depth", NPS "Shooting stars", Britannica "Meteor",
NASA "Perseids", Space.com "Meteors and meteor showers", Genge et al. 2017 Geology "An urban collection of modern-day
large micrometeorites"):
- A shooting star (meteor) is not a star: it is the streak of light from a small piece of space rock/dust
  (meteoroid) entering Earth's atmosphere. Most are about the size of a grain of sand.
- Meteoroids are mostly debris shed by comets and asteroids, orbiting the Sun; Earth runs into them as it orbits.
- They enter the atmosphere at about 11-72 km/s (NY-LA ~3,940 km would take under a minute at 70 km/s).
- The meteoroid compresses and heats the air in front of it (not simple friction); it heats up and vaporizes, and
  the glowing streak appears about 80-120 km (50-75 miles) up. Airliners cruise at ~10-12 km.
- Most burn up completely within a second or so; pieces that survive and reach the ground are meteorites.
- Meteor showers happen when Earth crosses a comet's debris trail, around the same dates each year. The Perseids
  (peak mid-August) come from comet 109P/Swift-Tuttle.
- NASA estimates about 48.5 tons (44,000 kg) of meteoritic material fall on Earth each day; micrometeorites have
  been found in urban rooftop gutters (Genge et al. 2017).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def night(c, t, seed=21):
    sky(c, '#03040b', '#1c2145', mid='#0b0e24'); stars(c, t, seed=seed, n=130, y1=1700)

def hills_night(c, y=1560):
    p = skia.Path(); p.moveTo(-20, y + 40)
    p.cubicTo(200, y - 60, 380, y - 20, 560, y + 10); p.cubicTo(740, y + 40, 900, y - 50, 1100, y)
    p.lineTo(1100, H); p.lineTo(-20, H); p.close()
    c.drawPath(p, lin(c, (0, y - 60, 0, H), [col('#1d2a52'), col('#0b1226')]))

def streak(c, t, start, x0, y0, ang, speed=1500, life=0.7, r=7, Lmax=320):
    """One meteor flying from (x0, y0) along ang starting at time start."""
    u = t - start
    if u < 0 or u > life: return
    rd = math.radians(ang); d = speed * u
    x, y = x0 + math.cos(rd) * d, y0 + math.sin(rd) * d
    a = 255 * math.sin(math.pi * u / life)
    meteor(c, x, y, ang, min(Lmax, d), r=r, alpha=a)

# ---------- 1: Hook (cold open: meteors already streaking) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    night(c, t)
    hills_night(c)
    rnd = random.Random(4)
    for i in range(12):
        st = i * 0.55 + rnd.uniform(0, 0.3) - 0.3
        streak(c, t, st, rnd.uniform(200, 900), rnd.uniform(620, 1000), rnd.uniform(115, 145), speed=rnd.uniform(1200, 1800), life=0.7)
    label_pill(c, 'NOT stars', 540, 720, size=48, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.6, 0.5))
        if k > 0:
            c.save(); c.translate(540, 1320); c.scale(k, k)
            c.drawCircle(0, 0, 150, P(color=col('#ffffff', 235)))
            c.drawCircle(0, 0, 150, P(color=col(NAVY), stroke=6))
            rr = random.Random(2)
            for j in range(40):
                gx, gy = rr.uniform(-90, 90), rr.uniform(-90, 90)
                if gx * gx + gy * gy < 8000:
                    c.drawCircle(gx, gy, rr.uniform(4, 9), P(color=col(mix_hx('#c9a874', '#8d8478', rr.random()))))
            c.restore()
            label_pill(c, 'grains of SAND', 540, 1530, size=40, k=k, fill=NAVY, hi=GOLD)

def s1_sfx(D, cues):
    return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 2: Debris from comets; Earth drives through it ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#03040b', '#141832'); stars(c, t, seed=7, n=100, y1=H)
    # sun glow at left edge
    c.drawCircle(-40, 900, 300, rad(-40, 900, 300, [col('#ffd23f', 200), col('#ffd23f', 0)]))
    c.drawCircle(-40, 900, 130, rad(-60, 880, 140, [col('#fff6c9'), col('#ffd23f'), col('#ff9f1c')], [0, 0.6, 1]))
    if t < t1 + 0.4:
        fo = 1 - prog(t, t1, 0.4)
        c.saveLayerAlpha(None, int(255 * fo))
        ck = ease_out(prog(t, t0, 1.0))
        comet(c, lerp(900, 640, ck), lerp(700, 980, ck), 0.8, t, tail_ang=-20)
        rnd = random.Random(8)
        for i in range(30):
            u = (i / 30 + t * 0.03) % 1.0
            x = lerp(620, 120, u) + rnd.uniform(-30, 30); y = lerp(1000, 1380, u) + rnd.uniform(-40, 40)
            space_rock(c, x, y, rnd.uniform(4, 10), rot=t * 30 + i, seed=i, alpha=int(220 * prog(t, t0 + 0.5, 0.8)))
        label_pill(c, 'comet + asteroid DUST', 540, 1560, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=GOLD)
        c.restore()
    if t > t1:
        ek = ease_out(prog(t, t1 + 0.2, 0.6))
        earth(c, 540, 1150, 210 * ek, t, rot=t * 0.03, face_on=False, sun_dir=180, night=0.4)
        rnd = random.Random(3)
        for i in range(26):  # dust rushing at Earth like snow at a windshield
            u = ((t - t1) * 0.9 + i / 26) % 1.0
            ang = rnd.uniform(0, 2 * math.pi); r0 = 620
            x = 540 + math.cos(ang) * lerp(r0, 220, u); y = 1150 + math.sin(ang) * lerp(r0, 220, u) * 0.8
            if 620 < y < 1600:
                c.drawCircle(x, y, 3 + 4 * u, P(color=col('#fff1c4', int(220 * ek * u))))
        label_pill(c, 'Earth PLOWS through', 540, 720, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 3: Up to 70 km/s - NY to LA in under a minute ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night(c, t, seed=5)
    rnd = random.Random(9)
    for i in range(6):
        streak(c, t, t0 + i * 0.6, rnd.uniform(400, 900), rnd.uniform(620, 760), 150, speed=2400, life=0.5, r=6)
    k = ease_back(prog(t, t0 + 0.3, 0.5))
    if k > 0:
        c.save(); c.translate(540, 920); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-300, -110, 300, 110), 50, 50, P(color=col('#ffffff', 240)))
        c.drawRoundRect(skia.Rect(-300, -110, 300, 110), 50, 50, P(color=col(NAVY), stroke=6))
        v = int(70 * ease_out(prog(t, t0 + 0.5, 1.5)))
        text_block(c, f'{v} km/s', 0, 0, size=96, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'UP TO', 540, 760, size=38, k=ease_back(prog(t, t0 + 0.3, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        kk = ease_out(prog(t, t1 + 0.2, 0.5))
        y = 1380
        c.drawLine(180, y, 860, y, P(color=col('#ffffff', int(80 * kk)), stroke=8))
        for x, nm in ((860, 'New York'), (180, 'L.A.')):
            c.drawCircle(x, y, 18 * kk, P(color=col('#ffd23f')))
            label_pill(c, nm, x, y + 70, size=34, k=kk, fill=NAVY)
        u = prog(t, t1 + 0.6, 1.6)
        mx = lerp(860, 180, u)
        if 0 < u < 1:
            meteor(c, mx, y, 180, 180, r=8)
        sw = ease_back(prog(t, t1 + 0.6, 0.4))
        if sw > 0:
            c.save(); c.translate(540, 1185); c.scale(sw * 0.7, sw * 0.7)
            stopwatch(c, 0, 0, 110, 0.93 * u, label='< 1 min', accent=HOT)
            c.restore()

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.3, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.6, 'whoosh'), (t1 + 2.2, 'click')]

# ---------- 4: Why it glows, ~100 km up ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#03040b', '#2f6fd0', mid='#14246a'); stars(c, t, seed=3, n=60, y1=1000, a=0.8)
    # big meteoroid with a glowing cap of hot air in front
    k = ease_out(prog(t, t0, 0.6))
    x, y = lerp(800, 520, prog(t, t0, 4.0)), lerp(740, 1000, prog(t, t0, 4.0))
    hk = prog(t, t0 + 0.9, 0.8)
    if t < t1 + 0.3:
        fo = 1 - prog(t, t1, 0.3)
        c.saveLayerAlpha(None, int(255 * fo * k))
        meteor(c, x, y, 140, 420 * hk, r=26 * hk + 0.1, hot='#fff6c9', tail='#ff9f1c')
        # compressed air (arcs ahead)
        rd = math.radians(140)
        for j in range(5):
            jx, jy = x + math.cos(rd) * (60 + j * 26), y + math.sin(rd) * (60 + j * 26)
            c.drawArc(skia.Rect(jx - 70, jy - 70, jx + 70, jy + 70), 140 - 60 - 180 + 180, 120, False, P(color=col('#ffd23f', int(200 * hk * (1 - j / 5))), stroke=8))
        space_rock(c, x, y, 34, rot=t * 60, seed=2)
        label_pill(c, 'air SQUEEZED + HOT', 540, 1250, size=42, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=HOT)
        label_pill(c, 'not friction', 540, 1350, size=34, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi=SKYB)
        c.restore()
    if t > t1:
        kk = ease_out(prog(t, t1 + 0.2, 0.6))
        # altitude ruler
        x0 = 230; ytop, ybot = 680, 1560
        def alt_y(km): return lerp(ybot, ytop, km / 120)
        c.drawLine(x0, ybot, x0, lerp(ybot, ytop, kk), P(color=col('#ffffff', 220), stroke=6))
        for km in (20, 40, 60, 80, 100, 120):
            yy = alt_y(km)
            if yy > lerp(ybot, ytop, kk):
                c.drawLine(x0 - 16, yy, x0 + 16, yy, P(color=col('#ffffff'), stroke=5))
                text_block(c, f'{km} km', x0 - 105, yy, size=34, fill='#ffffff', stroke=NAVY)
        c.drawRect(skia.Rect(0, ybot, W, H), lin(c, (0, ybot, 0, H), [col('#2a3f7a'), col('#0b1226')]))
        pk = prog(t, t1 + 0.6, 0.4)
        airplane(c, 520, alt_y(11), 0.32, rot=0, t=t, alpha=int(255 * pk))
        label_pill(c, 'planes ~11 km', 760, alt_y(11) - 10, size=32, k=ease_back(pk), fill=NAVY, hi=SKYB)
        mk = prog(t, t1 + 1.2, 0.4)
        if t > t1 + 1.2:
            st = t1 + 1.2 + ((t - t1 - 1.2) // 1.8) * 1.8
            streak(c, t, st, 820, alt_y(108), 168, speed=450, life=1.5, r=9, Lmax=260)
        label_pill(c, 'meteors ~100 KM', 560, alt_y(100) - 70, size=38, k=ease_back(mk), fill=NAVY, hi=GOLD)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.0, 'pop'), (t0 + 2.0, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.6, 'pop'), (t1 + 1.2, 'pop')]

# ---------- 5: Burns up in about a second; survivors = meteorites ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    night(c, t, seed=13)
    hills_night(c, 1500)
    if t < t1 + 0.3:
        for i in range(3):
            st = t0 + 0.2 + i * 1.3
            streak(c, t, st, 700 - i * 80, 680 + i * 40, 135, speed=600, life=1.0, r=10, Lmax=380)
        sw = ease_back(prog(t, t0 + 0.4, 0.4)) * (1 - prog(t, t1, 0.3))
        if sw > 0.01:
            c.save(); c.translate(780, 1250); c.scale(sw * 0.6, sw * 0.6)
            stopwatch(c, 0, 0, 120, ((t - t0) % 1.3) / 1.3 * 0.25, label='~1 s', accent=GOLD)
            c.restore()
        label_pill(c, 'GONE in a second', 380, 1250, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=HOT)
    if t > t1:
        u = prog(t, t1 + 0.1, 1.2)
        x, y = lerp(860, 520, u), lerp(660, 1480, u)
        if u < 1:
            meteor(c, x, y, 112, 360, r=14, tail='#ff9f1c')
            space_rock(c, x, y, 18, rot=t * 90, seed=5)
        else:
            dk = prog(t, t1 + 1.3, 0.6)
            c.drawOval(skia.Rect(520 - 140 * dk - 30, 1485, 520 + 140 * dk + 30, 1515), P(color=col('#ffd23f', int(150 * (1 - dk))), blur=10))
            space_rock(c, 520, 1470, 62, rot=12, seed=5, colr='#5e5650')
            label_pill(c, 'METEORITE', 520, 1360, size=46, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'rare SURVIVORS', 540, 720, size=44, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.0, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 1.3, 'boing'), (t1 + 1.4, 'pop')]

# ---------- 6: Meteor showers = Earth crosses a comet trail (aha) ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#03040b', '#141832'); stars(c, t, seed=17, n=100, y1=H)
    cx, cy, R = 540, 1130, 330
    c.drawCircle(cx, cy, 60, rad(cx, cy, 60, [col('#fff6c9'), col('#ffd23f'), col('#ff9f1c')], [0, 0.6, 1]))
    c.drawCircle(cx, cy, 150, rad(cx, cy, 150, [col('#ffd23f', 120), col('#ffd23f', 0)]))
    ok = prog(t, t0, 0.6)
    c.drawCircle(cx, cy, R, P(color=col('#ffffff', int(70 * ok)), stroke=4))
    # comet dust trail: a band crossing the orbit at the upper right
    tk = ease_out(prog(t, t0 + 0.6, 1.0))
    p = skia.Path(); p.moveTo(980, 560); p.cubicTo(820, 760, 700, 820, 120, 900)
    seg = skia.Path(); meas = skia.PathMeasure(p, False); meas.getSegment(0, meas.getLength() * tk, seg, True)
    c.drawPath(seg, P(color=col('#fff1c4', 70), stroke=70, blur=18))
    rnd = random.Random(6)
    for i in range(int(60 * tk)):
        pos, _ = meas.getPosTan(meas.getLength() * rnd.random())
        if pos is not None:
            px, py = pos
            c.drawCircle(px + rnd.uniform(-30, 30), py + rnd.uniform(-30, 30), rnd.uniform(1.5, 3.5), P(color=col('#fff1c4', 200)))
    # Earth on its orbit, moving into the trail
    ang = lerp(-10, -62, ease_in_out(prog(t, t0 + 0.8, 3.0)))
    a = math.radians(ang); ex, ey = cx + math.cos(a) * R, cy + math.sin(a) * R
    earth(c, ex, ey, 46, t, rot=t * 0.1, face_on=False, sun_dir=180 + ang, night=0.5)
    inside = prog(t, t0 + 3.0, 0.5)
    if inside > 0:
        for i in range(10):
            st = t0 + 3.0 + i * 0.25
            rd = random.Random(i)
            u = ((t - st) % 2.5)
            if t > st and u < 0.4:
                aa = rd.uniform(0, 2 * math.pi)
                meteor(c, ex + math.cos(aa) * (60 + 180 * u), ey + math.sin(aa) * (60 + 180 * u), math.degrees(aa) + 180, 80, r=4, alpha=200)
    label_pill(c, "a comet's dust TRAIL", 540, 1560, size=42, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi=GOLD)
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.4, 0.5))
        if kk > 0:
            c.save(); c.translate(270, 1320); c.scale(kk, kk)
            c.drawRoundRect(skia.Rect(-120, -110, 120, 110), 24, 24, P(color=col('#ffffff')))
            c.drawRoundRect(skia.Rect(-120, -110, 120, -50), 24, 24, P(color=col(HOT)))
            c.drawRect(skia.Rect(-120, -74, 120, -50), P(color=col(HOT)))
            text_block(c, 'AUG', 0, -80, size=40, fill='#ffffff', stroke=HOT)
            text_block(c, '12', 0, 30, size=90, fill=NAVY, stroke='#ffffff')
            c.restore()
        label_pill(c, 'PERSEIDS', 270, 1470, size=38, k=ease_back(prog(t, t1 + 0.9, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, 'comet Swift-Tuttle', 680, 700, size=36, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=SKYB)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.2, 'pop'), (t0 + 3.0, 'ding'), (t1 + 0.4, 'pop'), (t1 + 0.9, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 7: Wild part: ~48 tons a day, found in rooftop gutters ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#1c2145', '#6b84c9'); stars(c, t, seed=2, n=50, y1=1000, a=0.6)
    rnd = random.Random(1)
    for i in range(60):  # fine dust drifting down
        x = rnd.uniform(0, W); sp = rnd.uniform(40, 90)
        y = 620 + ((t * sp + rnd.uniform(0, 1000)) % 1000)
        c.drawCircle(x, y, rnd.uniform(1.5, 3), P(color=col('#fff1c4', 170)))
    k = ease_back(prog(t, t0 + 0.4, 0.5))
    if k > 0:
        c.save(); c.translate(540, 900); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-280, -90, 280, 90), 45, 45, P(color=col('#ffffff', 240)))
        c.drawRoundRect(skia.Rect(-280, -90, 280, 90), 45, 45, P(color=col(NAVY), stroke=6))
        n = int(48 * ease_out(prog(t, t0 + 0.6, 1.6)))
        text_block(c, f'~{n} TONS', 0, -8, size=80, fill=NAVY, hi=HOT, stroke='#ffffff')
        c.restore()
        label_pill(c, 'every DAY', 540, 1040, size=40, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        hk = ease_out(prog(t, t1 + 0.2, 0.6))
        c.save(); c.translate(0, 120 * (1 - hk))
        house(c, 380, 1580, 4.0)
        # gutter along the eave
        c.drawRoundRect(skia.Rect(150, 1352, 610, 1384), 12, 12, P(color=col('#9aa6b8')))
        c.drawRoundRect(skia.Rect(150, 1352, 610, 1384), 12, 12, P(color=col(NAVY), stroke=4))
        c.restore()
        mk = ease_back(prog(t, t1 + 1.0, 0.5))
        if mk > 0:
            def inner(cc):
                cc.drawRect(skia.Rect(600, 1000, 950, 1400), P(color=col('#8b95a8')))
                for j, (dx, dy, rr) in enumerate(((-40, -20, 16), (30, 10, 22), (-10, 50, 13), (50, -45, 11))):
                    space_rock(cc, 760 + dx, 1220 + dy, rr, seed=j, colr='#5e5650')
            c.drawLine(590, 1360, 660, 1300, P(color=col('#ffffff', int(200 * min(1, mk))), stroke=4))
            magnifier(c, 760, 1220, 120 * mk, inner, t)
            label_pill(c, 'space DUST', 760, 1410, size=38, k=mk, fill=NAVY, hi=GOLD)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.6, 'whoosh'), (t0 + 1.6, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 1.0, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night(c, t, seed=21)
    hills_night(c)
    rnd = random.Random(14)
    for i in range(10):
        streak(c, t, i * 0.9 + rnd.uniform(0, 0.4), rnd.uniform(250, 900), rnd.uniform(700, 1000), rnd.uniform(120, 150), speed=1400, life=0.7)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: why MARS is red', 540, 700, size=46, k=kk, fill=NAVY, hi=HOT)
        c.restore()
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='What are shooting stars?',
    music=False, faces=False, ambience='space',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('What are shooting stars?', 'What are SHOOTING stars?'),
            ('Not stars at all. Most are specks of space dust, about the size of a grain of sand.', 'Specks the size of SAND')], tail=0.8),
        dict(name='debris', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Comets and asteroids leave bits of rock and dust drifting around the Sun.', 'Leftover comet DUST'),
            ('And Earth plows through them as it orbits, like a car driving through snow.', 'Earth PLOWS through it')], tail=0.8),
        dict(name='speed', draw=s3, sfx_fn=s3_sfx, lines=[
            ('They hit our air at up to seventy kilometers per second.', 'Up to 70 KM per second'),
            ("That's New York to Los Angeles in under a minute.", 'NY to L.A. in under a MINUTE')], tail=1.0),
        dict(name='glow', draw=s4, sfx_fn=s4_sfx, lines=[
            ('At that speed, the speck slams the air in front of it so hard that the air heats up and glows.', 'The AIR heats up and glows'),
            ('That happens about a hundred kilometers up, ten times higher than planes fly.', 'About 100 KM up')], tail=1.0),
        dict(name='meteorite', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Most specks vaporize completely in about a second.', 'GONE in about a second'),
            ('The rare chunks that survive and land are called meteorites.', 'Survivors = METEORITES')], tail=1.2),
        dict(name='shower', draw=s6, sfx_fn=s6_sfx, trans='punch', lines=[
            ("Meteor showers happen when Earth crosses a comet's old dust trail, on the same dates every year.", "Showers = a comet's TRAIL"),
            ('The Perseids every August come from a comet called Swift-Tuttle.', 'The PERSEIDS: every August')], tail=1.2),
        dict(name='dust', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: about forty-eight tons of space dust land on Earth every single day.", '~48 TONS of space dust a day'),
            ('Scientists have even found tiny grains of it in rooftop gutters.', 'Found in rooftop GUTTERS')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So a shooting star is a speck of space dust burning up high in our air.', 'Space DUST burning up'),
            ('Next: why Mars is red.', 'Next: why MARS is red'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
