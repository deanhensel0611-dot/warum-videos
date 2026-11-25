"""Episode 42 (EN, general audience): Why is Mars red?
Facts checked (NASA/JPL "NASA Study on Why Mars Is Red Supports Potentially Habitable Past" 2025-02-25,
Brown University news 2025-02-25, ESA "Lab-made martian dust" 2025, Valantinas et al. 2025 Nature Communications,
NASA Mars facts, NASA/JPL Curiosity drill-hole images and "Curiosity's sunset" 2015):
- Mars looks red because its surface dust contains iron oxides (rust).
- Iron in Martian rock reacted with water and oxygen to form rust; over billions of years it was broken down into very
  fine dust (finer than flour/talc) and spread across the planet by winds and dust storms.
- The red is only a thin coating: underneath, the basaltic rock is dark gray; rover drill holes show gray powder.
- 2025 study (Valantinas et al.): the dust matches ferrihydrite best, an iron oxide with water in its structure; it
  forms quickly in the presence of cool water, so Mars likely rusted while it still had liquid water.
- Martian sunsets look blue: the fine dust lets blue light pass forward near the Sun's direction (NASA/Curiosity).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'
RUST = '#c4531f'

def mars_ground(c, y, t=0.0, x0=-20, x1=W + 20, dusk=0.0):
    p = skia.Path(); p.moveTo(x0, y + 20)
    p.cubicTo(220, y - 50, 420, y + 10, 600, y - 10); p.cubicTo(780, y - 30, 920, y + 30, x1, y - 10)
    p.lineTo(x1, H); p.lineTo(x0, H); p.close()
    c.drawPath(p, lin(c, (0, y - 40, 0, H), [col(mix_hx('#d9733a', '#6e3420', dusk)), col(mix_hx('#8a3a1a', '#2a140c', dusk))]))
    rnd = random.Random(5)
    for i in range(14):
        rx, ry = rnd.uniform(0, W), rnd.uniform(y + 60, y + 340)
        space_rock(c, rx, ry, rnd.uniform(8, 22), rot=rnd.uniform(0, 90), seed=i, colr=mix_hx('#7a3a20', '#3a1c10', dusk))

def nail(c, x, y, s, rust=0.0, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    metal = [col(mix_hx('#e3e8ef', '#c4531f', rust), a), col(mix_hx('#8b96a8', '#7a2e14', rust), a)]
    c.drawRoundRect(skia.Rect(-70, -170, 70, -140), 10, 10, lin(c, (0, -170, 0, -140), metal))
    p = skia.Path(); p.moveTo(-18, -142); p.lineTo(18, -142); p.lineTo(18, 150); p.lineTo(0, 200); p.lineTo(-18, 150); p.close()
    c.drawPath(p, lin(c, (-18, 0, 18, 0), metal, vertical=False))
    c.drawPath(p, P(color=col(NAVY, a), stroke=4))
    c.drawRoundRect(skia.Rect(-70, -170, 70, -140), 10, 10, P(color=col(NAVY, a), stroke=4))
    if rust > 0:
        rnd = random.Random(2)
        for i in range(int(16 * rust)):
            rx, ry = rnd.uniform(-14, 14), rnd.uniform(-130, 140)
            c.drawCircle(rx, ry, rnd.uniform(4, 9), P(color=col('#a8431a', int(a * 0.8)), blur=1.5))
    c.drawLine(-8, -120, -8, 120, P(color=col('#ffffff', int(a * 0.5 * (1 - rust))), stroke=5))
    c.restore()

# ---------- 1: Hook (cold open: Mars already turning) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    space(c, t, seed=4)
    z = 1 + 0.06 * ease_out(prog(t, t1, 1.5))
    mars(c, 540, 1120, 330 * z, t, rot=0.15 + t * 0.03)
    label_pill(c, 'the RED planet', 540, 700, size=48, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        k = ease_back(prog(t, t1 + 0.3, 0.5))
        def inner(cc):
            cc.drawRect(skia.Rect(560, 1100, 940, 1500), P(color=col('#b8501f')))
            rr = random.Random(3)
            for j in range(40):
                space_rock(cc, rr.uniform(580, 920), rr.uniform(1120, 1480), rr.uniform(10, 24), rot=rr.uniform(0, 90), seed=j,
                           colr=mix_hx('#e07a3f', '#9a3a18', rr.random()))
        if k > 0:
            c.drawLine(560, 1080, 720, 1180, P(color=col('#ffffff', int(200 * min(1, k))), stroke=5))
            magnifier(c, 750, 1300, 170 * k, inner, t)
            label_pill(c, 'RUST', 750, 1520, size=48, k=k, fill=NAVY, hi=RUST)

def s1_sfx(D, cues):
    return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 2: Iron + water + oxygen = rust ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9a46e', '#f6d6b0')
    mars_ground(c, 1460, t)
    if t < t1 + 0.3:
        fo = 1 - prog(t, t1, 0.3)
        c.saveLayerAlpha(None, int(255 * fo))
        k = ease_back(prog(t, t0, 0.5))
        if k > 0:
            c.save(); c.translate(540, 1215); c.scale(k, k)
            space_rock(c, 0, 0, 300, rot=10, seed=7, colr='#5d5a57')
            rnd = random.Random(4)
            for j in range(16):
                gx, gy = rnd.uniform(-200, 200), rnd.uniform(-190, 190)
                if gx * gx + gy * gy < 200 ** 2:
                    tw = 0.5 + 0.5 * math.sin(t * 4 + j)
                    twinkle(c, gx, gy, 14 + 6 * tw, colr='#cfe0ff', alpha=int(200 * prog(t, t0 + 0.6, 0.5)))
            c.restore()
        label_pill(c, 'full of IRON', 540, 760, size=48, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=SKYB)
        c.restore()
    if t > t1:
        u = t - t1
        nail(c, 680, 1120, 1.6, rust=ease_in_out(prog(t, t1 + 1.0, 2.5)), alpha=255 * prog(t, t1, 0.3))
        rnd = random.Random(9)
        for i in range(10):
            ph = (u * 0.9 + i / 10) % 1.0
            if u * 0.9 + i / 10 >= 1.0 or ph > i / 10:
                raindrop(c, 300 + rnd.uniform(0, 480), lerp(640, 1400, ph), 12, t, seed=i, face_on=False, alpha=170)
        for j, (txt, hc) in enumerate((('IRON', SKYB), ('+ WATER', SKYB), ('+ AIR', SKYB))):
            label_pill(c, txt, 260, 800 + j * 120, size=50, k=ease_back(prog(t, t1 + 0.3 + j * 0.35, 0.4)), fill=NAVY, hi=hc)
        label_pill(c, '= RUST', 260, 1180, size=58, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=RUST)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'pop'), (t0 + 0.8, 'pop'), (t1 + 0.3, 'click'), (t1 + 0.65, 'click'), (t1 + 1.0, 'click'), (t1 + 1.6, 'pop')]

# ---------- 3: Ground to dust, spread by storms ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    if t < t1 + 0.4:
        sky(c, '#e9a46e', '#f6d6b0')
        mars_ground(c, 1460, t)
        fo = 1 - prog(t, t1, 0.4)
        c.saveLayerAlpha(None, int(255 * fo))
        u = ease_in_out(prog(t, t0 + 0.3, 2.2))
        rnd = random.Random(12)
        hk = ease_out(prog(t, t0 + 1.2, 1.6))
        hp = skia.Path(); hp.moveTo(260, 1440); hp.cubicTo(400, 1440 - 170 * hk, 680, 1440 - 170 * hk, 820, 1440); hp.close()
        c.drawPath(hp, lin(c, (0, 1260, 0, 1440), [col('#e88a4c'), col('#b8501f')]))
        for j in range(170):
            bx, by = 540 + rnd.uniform(-160, 160), 1050 + rnd.uniform(-160, 160)
            if (bx - 540) ** 2 + (by - 1050) ** 2 > 160 ** 2: continue
            tx, ty = 540 + rnd.uniform(-240, 240), 1430 - rnd.uniform(0, 150) * hk
            x, y = lerp(bx, tx, u), lerp(by, ty, u * u)
            r = lerp(rnd.uniform(18, 30), rnd.uniform(3, 5), u)
            if u > 0.98 and rnd.random() < 0.6: continue
            space_rock(c, x, y, r, rot=j * 13 + t * 40 * u, seed=j, colr=mix_hx('#e07a3f', '#9a3a18', rnd.random()))
        label_pill(c, 'finer than FLOUR', 540, 760, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=GOLD)
        label_pill(c, 'billions of years', 540, 1560, size=38, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=SKYB)
        c.restore()
    if t > t1:
        space(c, t, seed=8)
        st = ease_in_out(prog(t, t1 + 0.4, 2.0))
        mars(c, 540, 1110, 310, t, rot=0.4 + t * 0.03, storm=st)
        rnd = random.Random(2)
        for i in range(36):  # dust swirling around the globe
            ang = rnd.uniform(0, 2 * math.pi) + (t - t1) * rnd.uniform(0.4, 0.9)
            rr = rnd.uniform(320, 380)
            x, y = 540 + math.cos(ang) * rr, 1110 + math.sin(ang) * rr * 0.32 + rnd.uniform(-160, 160)
            if math.sin(ang) > -0.2:
                c.drawCircle(x, y, rnd.uniform(3, 7), P(color=col('#f3c18c', int(200 * st))))
        label_pill(c, 'planet-wide DUST STORMS', 540, 700, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=RUST)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.4, 'pop'), (t1 + 0.3, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 4: Only skin deep: gray rock below, drill holes are gray ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#e9a46e', '#f6d6b0')
    gy = 930  # ground surface
    cut = ease_out(prog(t, t0 + 0.2, 0.8))
    # cross-section: thin rust layer over dark basalt
    c.drawRect(skia.Rect(0, gy, W, H), lin(c, (0, gy, 0, H), [col('#56524f'), col('#363432')]))
    rnd = random.Random(6)
    for i in range(26):
        space_rock(c, rnd.uniform(0, W), rnd.uniform(gy + 120, 1700), rnd.uniform(14, 40), rot=rnd.uniform(0, 90), seed=i,
                   colr=mix_hx('#6a6662', '#46423f', rnd.random()))
    lay = lerp(400, 34, cut)
    c.drawRect(skia.Rect(0, gy, W, gy + lay), lin(c, (0, gy, 0, gy + lay), [col('#e07a3f'), col('#b8501f')]))
    c.drawLine(0, gy, W, gy, P(color=col('#f6a46a'), stroke=6))
    label_pill(c, 'red dust: a THIN coat', 540, 760, size=44, k=ease_back(prog(t, t0 + 0.9, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=RUST)
    label_pill(c, 'GRAY rock below', 540, 1250, size=44, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=NAVY)
    if t > t1:
        # drill rig comes down and bores in, gray powder piles up
        dk = ease_out(prog(t, t1 + 0.1, 0.6))
        bx = 760; top = lerp(560, 700, dk)
        depth = 230 * ease_in_out(prog(t, t1 + 0.8, 2.0))
        if depth > 5:
            c.drawRect(skia.Rect(bx - 18, gy, bx + 18, gy + depth + 6), P(color=col('#24221f')))
            pile = depth / 230 * 1.6
            p = skia.Path(); p.moveTo(bx - 20 - 90 * pile, gy); p.quadTo(bx - 20 - 30 * pile, gy - 50 * pile, bx - 20, gy); p.close()
            c.drawPath(p, P(color=col('#7b7671')))
            p2 = skia.Path(); p2.moveTo(bx + 20 + 90 * pile, gy); p2.quadTo(bx + 20 + 30 * pile, gy - 50 * pile, bx + 20, gy); p2.close()
            c.drawPath(p2, P(color=col('#7b7671')))
        c.drawRoundRect(skia.Rect(bx - 70, top - 60, bx + 70, top + 40), 18, 18, lin(c, (0, top - 60, 0, top + 40), [col('#ffffff'), col('#c9d3e2')]))
        c.drawRoundRect(skia.Rect(bx - 70, top - 60, bx + 70, top + 40), 18, 18, P(color=col(NAVY), stroke=5))
        c.drawRect(skia.Rect(bx - 12, top + 40, bx + 12, gy + depth), lin(c, (bx - 12, 0, bx + 12, 0), [col('#e3e8ef'), col('#8b96a8')], vertical=False))
        spin = (t * 8) % 1.0
        for k in range(6):
            yy = top + 60 + ((k / 6 + spin) % 1.0) * (gy + depth - top - 60)
            c.drawLine(bx - 12, yy, bx + 12, yy + 10, P(color=col('#5d6b82'), stroke=3))
        label_pill(c, 'GRAY powder', 400, 760, size=40, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi=NAVY)

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.9, 'pop'), (t0 + 1.8, 'pop'), (t1 + 0.1, 'whoosh'), (t1 + 0.8, 'click'), (t1 + 2.0, 'pop')]

# ---------- 5: 2025 study: water-rich rust -> Mars rusted when wet (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    space(c, t, seed=12)
    if t < t1 + 0.4:
        fo = 1 - prog(t, t1, 0.4)
        c.saveLayerAlpha(None, int(255 * fo))
        k = ease_back(prog(t, t0, 0.5))
        def inner(cc):
            cc.drawRect(skia.Rect(200, 760, 880, 1440), P(color=col('#b8501f')))
            rr = random.Random(5)
            for j in range(7):
                gx, gy = 540 + rr.uniform(-200, 200), 1100 + rr.uniform(-200, 200)
                space_rock(cc, gx, gy, rr.uniform(60, 90), rot=rr.uniform(0, 90), seed=j, colr=mix_hx('#e07a3f', '#a8431a', rr.random()))
                wk = prog(t, t0 + 1.0 + j * 0.15, 0.4)
                if wk > 0:
                    water_molecule(cc, gx, gy, 22 * ease_back(wk), t, seed=j, rot=t * 40 + j * 50, face_on=False)
        if k > 0: magnifier(c, 540, 1100, 320 * k, inner, t)
        label_pill(c, 'rust with WATER inside', 540, 700, size=44, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi=SKYB)
        label_pill(c, '2025 study', 540, 1500, size=38, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=GOLD)
        c.restore()
    if t > t1:
        u = ease_in_out(prog(t, t1 + 0.6, 2.6))
        R = 300
        mars(c, 540, 1110, R, t, rot=0.6 + t * 0.03)
        if u < 1:  # ancient lakes and seas drying up
            c.save(); clip = skia.Path(); clip.addCircle(540, 1110, R); c.clipPath(clip, doAntiAlias=True)
            for (dx, dy, w_, h_) in ((-120, 90, 170, 90), (90, -60, 120, 70), (60, 170, 110, 50)):
                c.drawOval(skia.Rect(540 + dx - w_, 1110 + dy - h_, 540 + dx + w_, 1110 + dy + h_), P(color=col('#3f8fe0', int(220 * (1 - u))), blur=12))
            c.restore()
        label_pill(c, 'Mars rusted when it was WET', 540, 700, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.0, 'sparkle'), (t1 + 0.6, 'ding')]

# ---------- 6: Wild part: Martian sunsets are blue ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    dusk = ease_in_out(prog(t, t0, 2.5))
    c.drawRect(skia.Rect(0, 0, W, H), lin(c, (0, 0, 0, 1500), [col(mix_hx('#d98a55', '#3a2a3e', dusk)), col(mix_hx('#e9a46e', '#8a5a48', dusk))]))
    sy = lerp(1080, 1300, dusk); sx = 560
    glow = 0.3 + 0.7 * dusk
    c.drawCircle(sx, sy, 380, rad(sx, sy, 380, [col('#7fb8ff', int(230 * glow)), col('#4f8fe0', int(120 * glow)), col('#4f8fe0', 0)], [0, 0.45, 1]))
    c.drawCircle(sx, sy, 34, P(color=col('#f2fbff')))
    c.drawCircle(sx, sy, 34, P(color=col('#ffffff', 160), blur=10))
    mars_ground(c, 1380, t, dusk=dusk * 0.8)
    label_pill(c, 'SUNSET on Mars', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    if t > t1:
        kk = ease_out(prog(t, t1 + 0.2, 0.6))
        rnd = random.Random(7)
        for i in range(24):
            px, py = rnd.uniform(140, 940), rnd.uniform(820, 1250)
            c.drawCircle(px, py, 5, P(color=col('#f3c18c', int(220 * kk))))
        # blue light passing forward through the dust towards the viewer
        for j in range(3):
            ph = ((t - t1) * 0.8 + j / 3) % 1.0
            y0 = sy - 10 + (j - 1) * 30
            arrow(c, sx - 40, y0, lerp(sx - 40, 160, ph), lerp(y0, y0 + 200, ph), colr='#7fb8ff', w=12, alpha=int(230 * kk * (1 - ph * 0.6)))
        label_pill(c, 'dust sends BLUE forward', 540, 1560, size=40, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 0.6, 'sparkle'), (t1 + 0.2, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 7: Outro ----------
def s7(c, t, D, cues):
    space(c, t, seed=4)
    mars(c, 540, 1100, 300, t, rot=0.15 + t * 0.03)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.4, 0.4)) * fo
    if k0 > 0:
        label_pill(c, 'red DUST = RUST', 540, 700, size=46, k=k0, fill=NAVY, hi=RUST)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if t > cues[1]['start'] and kk > 0:
        for i in range(3):
            ant(c, 300 + i * 120 + (t - cues[1]['start']) * 60, 1490, 0.9, t, rot=0, colr='#2a1a12', gaster='#2a1a12', alpha=255 * min(1, kk))
        label_pill(c, 'next: how ANTS find home', 540, 820, size=42, k=kk, fill=NAVY, hi=HOT)
    follow_button(c, t, cues[2]['start'], y=1560)

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why is Mars red?',
    music=False, faces=False, ambience='wind',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, ambience='space', lines=[
            ('Why is Mars red?', 'Why is MARS red?'),
            ('Because the whole planet is coated in rust.', 'The planet is coated in RUST')], tail=0.6),
        dict(name='iron', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Mars rocks are full of iron, just like rocks on Earth.', 'Rocks full of IRON'),
            ('Iron plus water and oxygen makes rust, like a nail left out in the rain.', 'Iron + water = RUST')], tail=0.7),
        dict(name='dust', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Over billions of years, that rust was ground into dust finer than flour.', 'Dust finer than FLOUR'),
            ('And giant dust storms spread it over the entire planet.', 'STORMS spread it everywhere')], tail=0.7),
        dict(name='under', draw=s4, sfx_fn=s4_sfx, lines=[
            ("But it's only skin deep. Under the dust, the rock is dark gray.", 'Under the dust: GRAY rock'),
            ('When rovers drill into it, the powder comes out gray.', 'Drill holes come out GRAY')], tail=0.9),
        dict(name='water', draw=s5, sfx_fn=s5_sfx, trans='punch', ambience='space', lines=[
            ('A 2025 study found the rust is a kind that holds water inside it.', 'Rust with WATER inside'),
            ('That kind forms fast in cool water, so Mars likely rusted while it was still wet.', 'Mars rusted when it was WET')], tail=1.0),
        dict(name='sunset', draw=s6, sfx_fn=s6_sfx, lines=[
            ("Here's the wild part: sunsets on Mars are blue.", 'Martian sunsets are BLUE'),
            ('The fine dust lets blue light through toward you, so the sky glows blue around the Sun.', 'Dust sends BLUE light forward')], tail=1.2),
        dict(name='outro', draw=s7, sfx_fn=s7_sfx, ambience='space', lines=[
            ('So Mars is red because its dust is rust.', 'Red dust = RUST'),
            ('Next: how ants find their way home.', 'Next: how ANTS get home'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
