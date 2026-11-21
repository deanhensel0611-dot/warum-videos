"""Episode 28 (EN, general audience): How do spiders make webs?
Facts checked (Natural History Museum London "What are spider webs made of?", National Geographic "Spiderwebs
explained", Live Science "How do spiders make silk?", Smithsonian "Ask Smithsonian: How do spiders make webs?",
EarthSky "How does a spider spin a web between two trees?", Australian Museum "Silk: the spider's success story"):
- Silk is made in silk glands as a liquid protein; it is drawn out through the spinnerets and turns into a solid
  fibre as it is pulled (the proteins line up), not simply by drying.
- Orb-weavers start with a bridge line: they release a thread into the breeze and let it drift until it catches
  on something, then tighten it.
- Then they build a frame and radial threads (spokes) of non-sticky silk, then a temporary spiral, then the sticky
  capture spiral, laid from the outside in. The spider walks on the dry, non-sticky threads.
- Spider dragline silk is, weight for weight, stronger than steel, and very stretchy.
- Many orb-weavers eat their old web and recycle the silk proteins, often rebuilding daily; an orb web can be
  built in about an hour or less.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def garden_bg(c, t, top='#22456a', bot='#2f6b5e'):
    sky(c, top, bot)
    dust(c, t, seed=6, n=18, a=70, colr='#ffffff')

def stem(c, x, y0, y1, t, bend=30, seed=0):
    p = skia.Path(); p.moveTo(x, y0); p.cubicTo(x + bend, lerp(y0, y1, 0.33), x - bend, lerp(y0, y1, 0.66), x + bend * 0.3, y1)
    c.drawPath(p, P(color=col('#1f4a33'), stroke=26)); c.drawPath(p, P(color=col('#4f9a52'), stroke=16))
    for i, u in enumerate((0.2, 0.45, 0.7)):
        yy = lerp(y0, y1, u); sx = -1 if (i + seed) % 2 else 1
        leaf(c, x + sx * 40, yy, 0.6, t, colr='#5cc94a', seed=i + seed, face_on=False, rot=sx * 50 + 4 * math.sin(t + i))

def twigs(c, t, left=True, right=True):
    if left: stem(c, 120, 1720, 640, t, bend=24, seed=0)
    if right: stem(c, 960, 1720, 660, t, bend=-24, seed=1)

ANCH = None
def spdr(c, *a, **k):
    k.setdefault('body', '#a08ce0')
    spider(c, *a, **k)

def web_scene(c, t, frame, spokes, spiral, cx=540, cy=1110, R=330, alpha=255):
    anchors = [((128, 820), (cx - R * 0.6, cy - R * 0.75)), ((952, 840), (cx + R * 0.6, cy - R * 0.75)),
               ((124, 1480), (cx - R * 0.55, cy + R * 0.8)), ((958, 1500), (cx + R * 0.55, cy + R * 0.8))]
    return orb_web(c, cx, cy, R, t, frame=frame, spokes=spokes, spiral=spiral, anchors=anchors, alpha=alpha)

# ---------- 1: Hook (cold open: web already being spun) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    garden_bg(c, t)
    twigs(c, t)
    sp = lerp(0.35, 0.75, clamp(t / D))
    end = web_scene(c, t, 1.0, 1.0, sp)
    if end: spdr(c, end[0], end[1], 0.5, t, walk=1.0, rot=(t * 60) % 360)
    label_pill(c, '~1 HOUR', 760, 700, size=46, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        label_pill(c, 'from its own BODY', 540, 1600, size=46, k=ease_back(prog(t, t1 + 1.0, 0.4)), fill=NAVY, hi='#9b4dff')

def s1_sfx(D, cues): return [(0.0, 'whoosh'), (0.3, 'pop'), (cues[1]['start'] + 1.0, 'pop')]

# ---------- 2: Liquid protein -> pulled through spinnerets -> solid thread ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f3efff', '#e4ecff')
    z = ease_in_out(prog(t, t0, 1.0))
    # big spider, abdomen cut open to show the silk glands
    SX, SY, SS = 330, 1010, 1.9
    spdr(c, SX, SY, SS * lerp(0.9, 1.0, z), t, body='#5a4a85')
    ss = SS * lerp(0.9, 1.0, z)
    c.save(); c.translate(SX, SY); c.scale(ss, ss)
    c.save(); c.clipPath(skia.Path().addOval(skia.Rect(-50, -8, 50, 108)), doAntiAlias=True)
    c.drawOval(skia.Rect(-50, -8, 50, 108), P(color=col('#f4efff')))
    for i, (gx, gy, gw) in enumerate(((-24, 30, 16), (4, 18, 14), (26, 40, 13))):
        c.drawOval(skia.Rect(gx - gw, gy - gw * 1.4, gx + gw, gy + gw * 1.4), P(color=col('#ffffff')))
        lvl = gy - gw * 0.3 + 2.5 * math.sin(t * 3 + i)
        c.save(); c.clipPath(skia.Path().addOval(skia.Rect(gx - gw, gy - gw * 1.4, gx + gw, gy + gw * 1.4)), doAntiAlias=True)
        c.drawRect(skia.Rect(gx - gw, lvl, gx + gw, gy + gw * 1.5), P(color=col('#7cc6ff')))
        c.restore()
        c.drawOval(skia.Rect(gx - gw, gy - gw * 1.4, gx + gw, gy + gw * 1.4), P(color=col('#1b2a4a', 200), stroke=2))
        c.drawLine(gx, gy + gw * 1.4, 0, 104, P(color=col('#7cc6ff'), stroke=3))
    c.restore()
    c.drawOval(skia.Rect(-50, -8, 50, 108), P(color=col('#1b2a4a'), stroke=2.5))
    for dx in (-6, 6): c.drawRoundRect(skia.Rect(dx - 5, 110, dx + 5, 128), 4, 4, P(color=col('#3a2f5c')))
    c.restore()
    label_pill(c, 'LIQUID protein', 600, 690, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        ex, ey = 330, 1010 + 128 * 1.9
        L = ease_out(prog(t, t1 + 0.2, 1.6))
        # thread pulled out and away to the right/up
        tx, ty = lerp(ex, 900, L), lerp(ey, 1380, L)
        c.drawLine(ex, ey, tx, ty, P(color=col('#8f7ad0'), stroke=7))
        c.drawLine(ex, ey, tx, ty, P(color=col('#9ab0d0'), stroke=2))
        c.drawCircle(tx, ty, 10, P(color=col('#ffffff')))
        label_pill(c, 'SPINNERETS', 330, 1520, size=44, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#9b4dff')
        label_pill(c, 'pulled = SOLID', 760, 1270, size=44, k=ease_back(prog(t, t1 + 2.0, 0.4)), fill=NAVY, hi='#ff5c85')

def s2_sfx(D, cues): return [(cues[0]['start'], 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[1]['start'] + 0.2, 'whoosh'), (cues[1]['start'] + 0.6, 'pop'), (cues[1]['start'] + 2.0, 'pop')]

# ---------- 3: Bridge line on the breeze ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t, top='#1f4166', bot='#2c6560')
    twigs(c, t)
    wind_lines(c, t, y0=750, y1=1400, n=6, speed=500, alpha=150)
    sx, sy = 200, 900
    spdr(c, sx, sy - 40, 0.45, t, rot=60)
    u = ease_in_out(prog(t, t0 + 0.4, 3.6))
    tip_x = lerp(sx + 20, 955, u); tip_y = sy - 10 + 140 * math.sin(u * math.pi) * (1 - u) + (-60 * u)
    snag = u >= 1.0
    p = skia.Path(); p.moveTo(sx + 20, sy - 10)
    sag = 0 if t > t1 + 1.0 else 120 * (1 - u) + 30
    tight = ease_in_out(prog(t, t1 + 0.6, 0.8))
    midx, midy = (sx + tip_x) / 2, (sy + tip_y) / 2 + lerp(sag + 40 * math.sin(t * 3) * (1 - u), 0, tight)
    p.quadTo(midx, midy, tip_x, tip_y)
    c.drawPath(p, P(color=col('#ffffff'), stroke=5))
    c.drawPath(p, P(color=col('#8aa0c0', 120), stroke=1.5))
    if snag:
        c.drawCircle(tip_x, tip_y, 12, P(color=col('#ffd23f')))
    label_pill(c, 'on the BREEZE', 540, 720, size=46, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'the BRIDGE', 540, 1240, size=50, k=ease_back(prog(t, t1 + 0.3, 0.4)), fill=NAVY, hi='#ff5c85')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 4.0, 'click'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 4: Frame + spokes (bike wheel), dry silk ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t)
    twigs(c, t)
    fr = ease_in_out(prog(t, t0 + 0.2, 1.4)); sp = ease_in_out(prog(t, t0 + 1.4, 2.6))
    web_scene(c, t, fr, sp, 0.0)
    spdr(c, 540, 1110, 0.5, t, walk=0.6 if sp < 1 else 0.0)
    # bike wheel inset
    wk = ease_back(prog(t, t0 + 2.6, 0.5))
    if wk > 0 and t < t1 + 0.4:
        c.save(); c.translate(800, 1560); c.scale(wk, wk); c.rotate(t * 60)
        c.drawCircle(0, 0, 95, P(color=col(NAVY), stroke=14))
        for i in range(12):
            ang = math.radians(i * 30); c.drawLine(0, 0, math.cos(ang) * 90, math.sin(ang) * 90, P(color=col('#8a96ad'), stroke=4))
        c.drawCircle(0, 0, 12, P(color=col(NAVY)))
        c.restore()
    label_pill(c, 'SPOKES', 300, 1600, size=46, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'DRY, not sticky', 540, 720, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi='#ff9f1c')

def s4_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 2.0, 'pop'), (cues[0]['start'] + 2.6, 'pop'), (cues[1]['start'] + 0.4, 'pop')]

# ---------- 5: Sticky spiral, outside in; walks on the dry spokes (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t)
    twigs(c, t)
    sp = ease_in_out(prog(t, t0 + 0.2, max(1.0, t1 - t0 + 1.2)))
    z = ease_in_out(prog(t, t1 + 0.3, 1.2))
    c.save(); c.translate(540, 1110); s_ = lerp(1.0, 1.8, z); c.scale(s_, s_); c.translate(-540 + 60 * z, -1110 + 40 * z)
    end = web_scene(c, t, 1.0, 1.0, sp)
    if end and z < 0.01:
        spdr(c, end[0], end[1], 0.42, t, walk=1.0, rot=(t * 70) % 360)
    if z >= 0.01:
        # spider standing on a spoke (dry)
        spdr(c, 540, 1110 - 175, 0.36, t, rot=0)
    c.restore()
    label_pill(c, 'STICKY spiral', 540, 720, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#e0a800')
    if t > t1:
        label_pill(c, 'walks on DRY lines', 540, 1590, size=46, k=ease_back(prog(t, t1 + 1.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'pop'), (cues[1]['start'] + 0.3, 'whoosh'), (cues[1]['start'] + 1.6, 'ding')]

# ---------- 6: Stronger than steel, weight for weight; stretchy ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#eef2fa', '#dfe6f3')
    # balance scale: silk vs steel of equal weight
    bk = ease_back(prog(t, t0 + 0.3, 0.5))
    if bk > 0:
        c.save(); c.translate(540, 1080); c.scale(bk, bk)
        c.drawLine(0, -200, 0, 200, P(color=col(NAVY), stroke=14))
        c.drawLine(-280, -200, 280, -200, P(color=col(NAVY), stroke=12))
        c.drawRoundRect(skia.Rect(-80, 190, 80, 230), 16, 16, P(color=col(NAVY)))
        for sx, kind in ((-1, 'silk'), (1, 'steel')):
            px = sx * 280
            c.drawLine(px, -200, px - 70, -60, P(color=col('#8a96ad'), stroke=4)); c.drawLine(px, -200, px + 70, -60, P(color=col('#8a96ad'), stroke=4))
            c.drawRoundRect(skia.Rect(px - 100, -64, px + 100, -44), 10, 10, P(color=col('#8a96ad')))
            if kind == 'silk':
                for j in range(5):
                    c.drawArc(skia.Rect(px - 60 + j * 4, -150 + j * 4, px + 60 - j * 4, -60 - j * 4), 180, 180, False, P(color=col('#8f7ad0'), stroke=6))
                    c.drawArc(skia.Rect(px - 60 + j * 4, -150 + j * 4, px + 60 - j * 4, -60 - j * 4), 180, 180, False, P(color=col('#9ab0d0'), stroke=1.5))
            else:
                c.drawLine(px - 70, -80, px + 70, -80, P(color=col('#7d869a'), stroke=14))
                c.drawLine(px - 70, -80, px + 70, -80, P(color=col('#c6ccd8'), stroke=6))
        c.restore()
        label_pill(c, 'SILK', 260, 1240, size=44, k=bk, fill=NAVY, hi='#9b4dff')
        label_pill(c, 'steel', 820, 1240, size=44, k=bk, fill=NAVY)
    sk = ease_back(prog(t, t0 + 2.4, 0.5), 2.4)
    if sk > 0:
        c.save(); c.translate(540, 760); c.scale(sk, sk)
        c.drawRoundRect(skia.Rect(-280, -70, 280, 70), 35, 35, P(color=col('#ffd23f')))
        c.drawRoundRect(skia.Rect(-280, -70, 280, 70), 35, 35, P(color=col(NAVY), stroke=6))
        text_block(c, 'STRONGER', 0, 0, size=72, fill=NAVY, hi=NAVY, stroke='#ffd23f')
        c.restore()
    if t > t1:
        # insect hitting a stretchy thread
        u = ((t - t1 - 0.4) % 2.0) / 2.0 if t > t1 + 0.4 else 0
        dip = 120 * math.sin(math.pi * clamp(u / 0.6)) * math.exp(-u * 2)
        y0 = 1480
        p = skia.Path(); p.moveTo(160, y0); p.quadTo(540, y0 + dip * 2, 920, y0)
        c.drawPath(p, P(color=col('#8f7ad0'), stroke=6)); c.drawPath(p, P(color=col('#9ab0d0'), stroke=1.5))
        fx = 540; fy = lerp(1300, y0 + dip - 18, clamp(u / 0.3)) if u < 0.3 else y0 + dip - 18
        c.drawOval(skia.Rect(fx - 18, fy - 12, fx + 18, fy + 12), P(color=col('#3a3a4a')))
        for sx in (-1, 1): c.drawOval(skia.Rect(fx + sx * 4 - (26 if sx < 0 else 0), fy - 30, fx + sx * 4 + (26 if sx > 0 else 0), fy - 6), P(color=col('#9fb6d6', 230)))
        label_pill(c, 'STRETCHY', 800, 1360, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[0]['start'] + 2.4, 'pop'), (cues[1]['start'] + 0.4, 'boing'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 7: Wild part: they eat their old web and recycle it ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    garden_bg(c, t, top='#3a2f5c', bot='#6a3f5a')
    twigs(c, t)
    gone = ease_in_out(prog(t, t0 + 1.0, 3.0))
    if t < t1 + 0.6:
        web_scene(c, t, 1.0 - gone, 1.0 - gone, 1.0 - gone)
        spdr(c, 540, 1110, 0.55, t, walk=0.4)
    else:
        nb = ease_in_out(prog(t, t1 + 0.6, 2.4))
        web_scene(c, t, clamp(nb * 3), clamp(nb * 3 - 0.8), clamp(nb * 1.6 - 0.6))
        spdr(c, 540, 1110, 0.55, t, walk=0.6)
    if t > t0 + 1.0 and t < t1 + 0.6:
        # silk strands drawn into the spider
        for i in range(6):
            u = ((t * 0.9 + i / 6) % 1.0)
            ang = i * 1.05
            r_ = lerp(320, 30, u)
            c.drawCircle(540 + math.cos(ang) * r_, 1110 + math.sin(ang) * r_, 7, P(color=col('#ffffff', int(230 * (1 - u)))))
    label_pill(c, 'EATS its web', 540, 720, size=48, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        label_pill(c, 'RECYCLED silk', 540, 1600, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi='#3fbf6a')

def s7_sfx(D, cues): return [(cues[0]['start'] + 1.0, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.4, 'pop'), (cues[1]['start'] + 0.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    garden_bg(c, t)
    twigs(c, t)
    web_scene(c, t, 1.0, 1.0, 1.0, cy=1060, R=300)
    spdr(c, 540, 1060, 0.5, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: why we BRUSH', 540, 700, size=48, k=kk, fill=NAVY, hi='#2f9bff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='How do spiders make webs?',
    music=False, faces=False, ambience='forest',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('How do spiders make webs?', 'How do spiders make WEBS?'),
            ('A garden spider can spin this in about an hour, all from its own body.', 'All from its own BODY')], tail=0.8),
        dict(name='silk', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Silk starts as a liquid protein, stored in glands inside the spider.', 'It starts as a LIQUID'),
            ('As it gets pulled out through nozzles called spinnerets, it turns into a solid thread.', 'PULLED into a thread')], tail=0.8),
        dict(name='bridge', draw=s3, sfx_fn=s3_sfx, lines=[
            ('To cross a gap, the spider lets a thread drift away on the breeze until it snags on something.', 'It floats on the BREEZE'),
            ('That first line is the bridge.', 'The first line: a BRIDGE')], tail=0.8),
        dict(name='spokes', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Next comes a frame, and spokes running to the center, like a bicycle wheel.', 'A frame and SPOKES'),
            ('These lines are dry, not sticky.', 'DRY lines')], tail=0.8),
        dict(name='spiral', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Then it lays a spiral of sticky silk, round and round, from the outside in.', 'Then a STICKY spiral'),
            ("And it walks on the dry spokes, so it doesn't get stuck in its own trap.", 'It walks on the DRY lines')], tail=1.2),
        dict(name='steel', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Weight for weight, spider silk is stronger than steel.', 'Stronger than STEEL'),
            ('And stretchy enough to catch a flying insect without snapping.', 'And very STRETCHY')], tail=0.8),
        dict(name='recycle', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: many orb-weavers eat their old web,", 'They EAT their old web'),
            ('and recycle the silk to build a fresh one, sometimes every single day.', 'and RECYCLE the silk')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So: liquid silk, a bridge on the breeze, spokes, then a sticky spiral.', 'Bridge, spokes, sticky SPIRAL'),
            ('Next up: why we have to brush our teeth.', 'Next: why we BRUSH'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
