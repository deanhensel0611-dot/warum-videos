"""Episode 36 (EN, general audience): How does a seed grow into a plant?
Facts checked (Britannica "Germination", University of Minnesota "Introduction to Seed Germination" (Horticulture),
EBSCO Research Starters "Germination and seedling development", Wikipedia "Germination", National Geographic /
Science 2008 Sallon et al. "Germination of a 2,000-year-old date palm seed", AIP Inside Science):
- A seed holds an embryo (baby plant: embryonic root = radicle, shoot = plumule), a food store (cotyledons /
  endosperm) and a protective seed coat.
- Seeds can stay dormant for long periods; germination needs water, oxygen and a suitable temperature (light only for
  some species).
- Germination starts with imbibition: the seed soaks up water and swells until the coat splits.
- The radicle (root) emerges first and grows downward - roots sense gravity (gravitropism); the shoot grows upward.
- In many seedlings (e.g. beans) the shoot pushes through soil bent in a hook that protects the delicate tip; it
  straightens in light. Until the first leaves photosynthesise, the seedling lives on the stored food.
- 2005: a ~2,000-year-old Judean date palm seed from Masada (Israel) was germinated; the plant was named Methuselah.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
GREEN = '#3fae3a'
SOIL_Y = 1080

def garden_bg(c, t, soil_y=SOIL_Y, sun_on=0.0):
    sky(c, '#8fd0ff', '#e8f6ff')
    if sun_on > 0:
        c.saveLayerAlpha(None, int(255 * sun_on)); sun(c, 880, 760, 80, t); c.restore()
    soil(c, soil_y, t, y1=H, seed=4)

# ---------- 1: Hook (cold open: time-lapse sprout already growing) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    g = clamp(t / (D - 0.5))
    garden_bg(c, t, sun_on=1.0)
    sx, sy = 540, 1240
    seedling(c, sx, sy - 30, 1.0, t, root=clamp(0.5 + g), shoot=clamp(0.35 + g * 0.9), unhook=clamp(g * 2.2 - 0.6),
             leaves=clamp(g * 2.2 - 1.0), hairs=clamp(g * 2 - 0.5))
    bean_seed(c, sx, sy, 0.7, t, swell=1.0, crack=1.0)
    soil_cover = skia.Rect(0, SOIL_Y - 6, W, SOIL_Y + 14)
    c.drawRect(soil_cover, P(color=col('#6b4423')))
    day = 1 + int(g * 9)
    label_pill(c, f'DAY {day}', 540, 690, size=52, k=ease_back(prog(t, 0.2, 0.4)), fill=NAVY, hi=GREEN)
    if t > t1:
        label_pill(c, 'ONE seed, one whole plant', 540, 1640, size=40, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi=GREEN)

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.2, 'pop'), (cues[1]['start'] + 1.0, 'pop')]

# ---------- 2: Inside: baby plant, food, coat (lunchbox) ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#fff4e6', '#ffe3c4'); dust(c, t, seed=8, n=10, a=70)
    sk = ease_back(prog(t, t0, 0.5))
    sec = ease_in_out(prog(t, t0 + 1.0, 0.8))
    bean_seed(c, 540, 1130, 3.2 * max(sk, 0.01), t, section=sec, rot=math.sin(t * 0.8) * 2)
    label_pill(c, 'a packed LUNCHBOX', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        d = t - t1
        for i, (txt, lx, ly, px, py, hi) in enumerate((('BABY plant', 250, 900, 430, 1020, GREEN),
                                                       ('FOOD store', 820, 900, 700, 1080, '#e0a000'),
                                                       ('tough COAT', 780, 1430, 760, 1260, '#c46a4a'))):
            k = ease_back(prog(d, 0.3 + i * 1.0, 0.4))
            if k > 0:
                c.drawLine(lx, ly, lerp(lx, px, min(1, k)), lerp(ly, py, min(1, k)), P(color=col(NAVY, 200), stroke=5))
                c.drawCircle(px, py, 10 * min(1, k), P(color=col(NAVY)))
                label_pill(c, txt, lx, ly, size=40, k=k, fill=NAVY, hi=hi)

def s2_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'pop'), (t0 + 1.0, 'whoosh'), (t1 + 0.3, 'pop'), (t1 + 1.3, 'pop'), (t1 + 2.3, 'pop')]

# ---------- 3: Waits for water, air, warmth ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t)
    bean_seed(c, 540, 1300, 0.9, t, rot=-8 + math.sin(t * 0.5) * 1.5)
    # calendar pages flipping (years of waiting)
    ck = ease_back(prog(t, t0 + 0.4, 0.4))
    if ck > 0:
        c.save(); c.translate(540, 880); c.scale(ck, ck)
        c.drawRoundRect(skia.Rect(-110, -100, 110, 100), 20, 20, P(color=col('#ffffff')))
        c.drawRoundRect(skia.Rect(-110, -100, 110, -40), 20, 20, P(color=col('#ff5c85')))
        c.drawRect(skia.Rect(-110, -60, 110, -40), P(color=col('#ff5c85')))
        yrs = 1 + int(max(0, t - t0 - 0.4) * 1.6) % 9
        text_block(c, f'{yrs} yr', 0, 30, size=56, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.drawRoundRect(skia.Rect(-110, -100, 110, 100), 20, 20, P(color=col(NAVY), stroke=5))
        c.restore()
    label_pill(c, 'it can WAIT for years', 540, 700, size=44, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        d = t - t1
        icons = [(260, 'WATER'), (540, 'AIR'), (820, 'WARMTH')]
        for i, (ix, name) in enumerate(icons):
            k = ease_back(prog(d, 0.4 + i * 0.6, 0.4))
            if k <= 0: continue
            c.save(); c.translate(ix, 1560); c.scale(k, k)
            c.drawCircle(0, 0, 70, P(color=col('#ffffff', 235)))
            c.drawCircle(0, 0, 70, P(color=col(NAVY), stroke=5))
            if name == 'WATER': raindrop(c, 0, 4, 34, t, face_on=False)
            elif name == 'AIR':
                for j in range(3):
                    c.drawCircle(-22 + j * 22, -8 + (j % 2) * 18, 13, P(color=col('#5fd0ff')))
                    c.drawCircle(-22 + j * 22, -8 + (j % 2) * 18, 13, P(color=col(NAVY), stroke=3))
            else: thermometer(c, 0, 34, s=0.22, level=0.6, hot='#ff8a3d')
            c.restore()
            label_pill(c, name, ix, 1450, size=34, k=k, fill=NAVY, hi=['#2f9bff', '#2f9bff', '#ff8a3d'][i])

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'pop'), (t0 + 0.8, 'pop'), (t1 + 0.4, 'pop'), (t1 + 1.0, 'pop'), (t1 + 1.6, 'pop')]

# ---------- 4: Soaks up water, swells, coat splits ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t)
    # water seeping into the soil
    wk = prog(t, t0 + 0.2, 1.0)
    rnd = random.Random(9)
    for i in range(14):
        u = ((t - t0) * 0.5 + rnd.random()) % 1.0
        x = rnd.uniform(200, 880); y = lerp(SOIL_Y + 20, 1280, u)
        raindrop(c, x, y, 12, t, face_on=False, alpha=int(200 * wk * (1 - u)))
    sw = ease_in_out(prog(t, t0 + 0.6, t1 - t0 + 0.4))
    wob = math.sin(t * 20) * 3 * prog(t, t1, 0.2) * (1 - prog(t, t1 + 0.8, 0.4))
    cr = ease_out(prog(t, t1 + 0.5, 0.5))
    bean_seed(c, 540 + wob, 1330, 1.4, t, swell=sw, crack=cr)
    label_pill(c, 'SOAKS up water', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi='#2f9bff')
    label_pill(c, 'like a SPONGE', 540, 1620, size=42, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'the coat SPLITS', 540, 900, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#c46a4a')

def s4_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.4, 'pop'), (t0 + 1.8, 'pop'), (t1 + 0.5, 'click'), (t1 + 0.6, 'pop')]

# ---------- 5: Root first, always down (gravity) - aha ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t, soil_y=760)
    # left: normal seed; right: seed planted upside down - root still turns down
    rk = ease_out(prog(t, t0 + 0.3, 2.6))
    for x, rot, rdir in ((330, 0, 100), (760, 180, -80)):
        if x > 600 and t < t1: continue
        k = rk if x < 600 else ease_out(prog(t, t1 + 0.2, 2.2))
        seedling(c, x - 10, 1010 if rot == 0 else 990, 0.9, t, root=k, hairs=clamp(k * 2 - 1), root_dir=rdir)
        bean_seed(c, x, 1000, 0.75, t, swell=1.0, crack=1.0, rot=rot)
    if t > t1:
        gk = prog(t, t1 + 1.4, 0.4)
        arrow(c, 560, 1180, 560, 1440, colr='#ffd23f', w=18, alpha=int(255 * gk))
        label_pill(c, 'GRAVITY', 560, 1520, size=46, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi='#c48a00')
        label_pill(c, 'even UPSIDE DOWN', 760, 880, size=36, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill=NAVY, hi='#ff5c85')
    label_pill(c, 'ROOT comes first', 540, 690, size=46, k=ease_back(prog(t, t0 + 0.5, 0.4)), fill=NAVY, hi=GREEN)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 0.5, 'pop'), (t1 + 0.2, 'whoosh'), (t1 + 0.5, 'pop'), (t1 + 1.4, 'ding')]

# ---------- 6: Shoot pushes up in a hook, then leaves open in the light ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sun_k = prog(t, t1 + 0.2, 0.8)
    garden_bg(c, t, sun_on=sun_k)
    if sun_k > 0:
        sunbeams(c, 880, 760, t, a=int(30 * sun_k), n=8)
    sx, sy = 540, 1380
    sh = ease_in_out(prog(t, t0 + 0.2, t1 - t0 + 0.2))
    unh = ease_in_out(prog(t, t1 + 0.4, 1.2)); lv = ease_out(prog(t, t1 + 1.2, 1.4))
    seedling(c, sx, sy - 25, 1.0, t, root=1.0, shoot=0.15 + 0.85 * sh, unhook=unh, leaves=lv, hairs=1.0)
    bean_seed(c, sx, sy, 0.75, t, swell=1.0, crack=1.0, alpha=int(255 * (1 - 0.5 * lv)))
    c.drawRect(skia.Rect(0, SOIL_Y - 6, W, SOIL_Y + 14), P(color=col('#6b4423')))
    label_pill(c, 'shoot bent like a HOOK', 540, 700, size=42, k=ease_back(prog(t, t0 + 0.6, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi=GREEN)
    fk = ease_back(prog(t, t0 + 1.6, 0.4)) * (1 - prog(t, t1 + 1.6, 0.3))
    label_pill(c, 'eats its packed FOOD', 540, 1640, size=40, k=fk, fill=NAVY, hi='#e0a000')
    if t > t1:
        label_pill(c, 'LIGHT: leaves open', 540, 700, size=44, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi='#e0a000')

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.6, 'pop'), (t0 + 1.6, 'pop'), (t1 + 0.3, 'pop'), (t1 + 1.2, 'sparkle')]

# ---------- 7: Wild part: 2,000-year-old date palm seed ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#ffe9c7', '#ffd39a', mid='#ffdcae')
    # desert dunes
    p = skia.Path(); p.moveTo(0, 1360); p.cubicTo(300, 1260, 600, 1400, W, 1300); p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, lin(c, (0, 1260, 0, H), [col('#f2c27a'), col('#d99a4f')]))
    n = int(2000 * ease_out(prog(t, t0 + 1.0, 2.0)))
    kk = ease_back(prog(t, t0 + 1.0, 0.4))
    if kk > 0:
        c.save(); c.translate(540, 820); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-300, -80, 300, 80), 40, 40, P(color=col('#ffffff', 240)))
        text_block(c, f'{n:,} YEARS', 0, -4, size=76, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    grow = ease_out(prog(t, t1 + 0.3, 2.0))
    if grow > 0:
        palm_sapling(c, 540, 1330, 1.5 * grow, t)
    sa = 1 - prog(t, t1 + 0.3, 0.6)
    if sa > 0:
        c.save(); c.translate(540, 1150); c.rotate(-20)
        c.drawOval(skia.Rect(-70, -32, 70, 32), lin(c, (0, -32, 0, 32), [col('#c08a55', int(255 * sa)), col('#7a5030', int(255 * sa))]))
        c.drawLine(-50, 0, 50, 0, P(color=col('#5a3820', int(200 * sa)), stroke=5))
        c.restore()
    if t > t1:
        label_pill(c, 'METHUSELAH (2005)', 540, 1600, size=42, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi=GREEN)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 1.0, 'pop'), (t0 + 1.2, 'click'), (t1 + 0.3, 'sparkle'), (t1 + 1.6, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    garden_bg(c, t, sun_on=1.0)
    seedling(c, 260, 1355, 1.0, t, root=1.0, shoot=1.0, unhook=1.0, leaves=1.0, hairs=1.0)
    bean_seed(c, 260, 1380, 0.75, t, swell=1.0, crack=1.0, alpha=128)
    c.drawRect(skia.Rect(0, SOIL_Y - 6, W, SOIL_Y + 14), P(color=col('#6b4423')))
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: SOUND to your ears', 540, 700, size=44, k=kk, fill=NAVY, hi='#2f9bff')
        c.restore()
    follow_button(c, t, cues[2]['start'], x=620, y=1560)

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How does a seed grow into a plant?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How does a seed grow into a plant?', 'How does a SEED become a plant?'),
            ('Everything it needs to start is already packed inside.', "It's all PACKED inside")], tail=0.8),
        dict(name='inside', draw=s2, sfx_fn=s2_sfx, lines=[
            ('A seed is like a packed lunchbox.', 'Like a packed LUNCHBOX'),
            ('Inside: a tiny baby plant, a store of food, and a tough coat around it all.', 'Baby PLANT, food, tough coat')], tail=1.0),
        dict(name='wait', draw=s3, sfx_fn=s3_sfx, lines=[
            ('It can rest, dry and inactive, for months or even years,', 'It can WAIT for years'),
            ('until it gets three things: water, air and the right warmth.', 'Water, AIR and warmth')], tail=0.8),
        dict(name='soak', draw=s4, sfx_fn=s4_sfx, lines=[
            ('First, it soaks up water like a sponge and swells,', 'It soaks up WATER and swells'),
            ('until the coat splits open.', 'The coat SPLITS open')], tail=0.8),
        dict(name='root', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('The root comes out first, and it heads down.', 'The ROOT comes out first'),
            ('Even if the seed lies upside down, the root turns around, because it can sense gravity.', 'Roots can sense GRAVITY')], tail=1.2),
        dict(name='shoot', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Then the shoot pushes up, bent like a hook to protect its tip, living on its packed food.', 'The shoot pushes up like a HOOK'),
            ('In the light, it straightens, and the first leaves open to make food from sunlight.', 'In the LIGHT, leaves open')], tail=1.0),
        dict(name='palm', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: in 2005, scientists sprouted a date palm seed about two thousand years old.", 'A 2,000-YEAR-OLD seed sprouted'),
            ('They named the plant Methuselah.', 'Its name: METHUSELAH')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So a seed is a baby plant with a packed lunch, just waiting for water.', 'A baby plant with a LUNCH'),
            ('Next: how sound gets into your ears.', 'Next: how SOUND reaches your ears'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
