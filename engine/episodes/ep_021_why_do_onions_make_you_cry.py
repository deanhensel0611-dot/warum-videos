"""Episode 21 (EN, general audience): Why do onions make you cry?
Facts checked: onion cells store sulfur compounds (sulfoxides) separately from the enzyme alliinase. Cutting breaks the
cells, the two mix; alliinase makes sulfenic acids, which the enzyme lachrymatory-factor synthase (found by Imai et al.,
Nature 2002) turns into the volatile gas syn-propanethial-S-oxide. It reaches the eyes, stimulates sensory nerves of
the cornea, and the tear glands release tears to flush it out. Thought to be a defence against animals/microbes.
Chilling slows the reaction/volatility; a sharp knife crushes fewer cells. Low-tear onions have been bred since.
"""
import math, random
from lib import *

GAS = '#c9f27a'
NAVY = '#1b2a4a'

def kitchen(c, t, dark=0.0):
    sky(c, mix_hx('#ffe9c7', '#3a2f4a', dark), mix_hx('#ffd29a', '#2a2238', dark))
    # tiles
    for r_ in range(9):
        for q in range(7):
            x = q * 170 - 20 + (85 if r_ % 2 else 0); y = 640 + r_ * 110
            c.drawRoundRect(skia.Rect(x, y, x + 160, y + 100), 14, 14, P(color=col('#ffffff', int(55 * (1 - dark)))))
    c.drawRect(skia.Rect(0, 1520, W, H), lin(c, (0, 1520, 0, H), [col('#d9a46a'), col('#b07a40')]))

def rising_gas(c, t, t0, x, y, n=8, spread=120, height=600, seed=0, alpha=160, tx=None):
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + i * 0.3
        if t < st: continue
        u = ((t - st) / 2.4) % 1.0
        sx = x + rnd.uniform(-spread, spread)
        ex = sx if tx is None else lerp(sx, tx, 0.8)
        gx = lerp(sx, ex, u) + math.sin(u * 7 + i) * 30; gy = y - u * height
        gas_wisp(c, gx, gy, 0.9 + u * 0.8, t, seed=i, alpha=alpha * min(1, u * 4) * min(1, (1 - u) * 3), colr=GAS)

def cell_grid(c, t, cx, cy, cw, chh, rows, cols, burst=0.0, glow=0.0, seed=1):
    rnd = random.Random(seed)
    for r_ in range(rows):
        for q in range(cols):
            x = cx + (q - (cols - 1) / 2) * cw; y = cy + (r_ - (rows - 1) / 2) * chh
            bk = clamp(burst * 2 - rnd.random()) if burst > 0 else 0
            c.drawRoundRect(skia.Rect(x - cw / 2 + 6, y - chh / 2 + 6, x + cw / 2 - 6, y + chh / 2 - 6), 30, 30, P(color=col('#f6eefc')))
            # compartment (vacuole) with purple sulfur compound
            vr = skia.Rect(x - cw * 0.3, y - chh * 0.28, x + cw * 0.3, y + chh * 0.28)
            if bk < 0.5:
                c.drawRoundRect(vr, 24, 24, P(color=col('#e6d4f5')))
                c.drawRoundRect(vr, 24, 24, P(color=col('#9c5bb8'), stroke=4))
            for j in range(4):
                ang = j * 1.6 + t * 1.5 + q; spread = lerp(0.18, 0.42, bk)
                px, py = x + math.cos(ang) * cw * spread * 0.8, y + math.sin(ang * 1.3) * chh * spread * 0.6
                c.drawCircle(px, py, 9, P(color=col('#8e44ad')))
            for j in range(3):   # enzyme outside the compartment (yellow)
                ang = j * 2.1 - t * 1.2 + r_; rr = lerp(0.42, 0.2, bk)
                px, py = x + math.cos(ang) * cw * rr, y + math.sin(ang) * chh * rr
                c.drawRoundRect(skia.Rect(px - 9, py - 9, px + 9, py + 9), 4, 4, P(color=col('#f2b400')))
            if bk > 0.3:
                c.drawCircle(x, y, cw * 0.4, rad(x, y, cw * 0.4, [col(GAS, int(150 * bk * glow)), col(GAS, 0)]))
            wall = col('#9c5bb8', int(255 * (1 - 0.6 * bk)))
            c.drawRoundRect(skia.Rect(x - cw / 2 + 6, y - chh / 2 + 6, x + cw / 2 - 6, y + chh / 2 - 6), 30, 30, P(color=wall, stroke=7))

# ---------- 1: Hook (cold open: knife mid-slice, gas already rising) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    kitchen(c, t)
    cutting_board(c, 470, 1420, w_=800)
    onion(c, 400, 1230, 0.85, t, half=True)
    # slices on the right
    for i in range(3):
        sx = 720 + i * 34
        c.drawRoundRect(skia.Rect(sx - 12, 1080, sx + 12, 1415), 12, 12, P(color=col('#f6eefc')))
        c.drawRoundRect(skia.Rect(sx - 12, 1080, sx + 12, 1415), 12, 12, P(color=col('#9c5bb8'), stroke=5))
    chop = abs(math.sin(t * 3.2))
    knife(c, 640, lerp(1410, 1120, chop), 1.0, rot=-4)
    rising_gas(c, t, 0.0, 520, 1200, n=8, spread=150, height=520, seed=1, alpha=220, tx=680)
    human_eye(c, 680, 800, 1.25, t, tear=clamp((t - 1.5) / 5.0), squint=0.3 * prog(t, 1.5, 1.0))
    if t > t1:
        label_pill(c, 'CHEMISTRY', 260, 960, size=50, k=ease_back(prog(t, t1 + 0.5, 0.4)), fill='#8e44ad', hi='#8e44ad')

def s1_sfx(D, cues): return [(0.0, 'click'), (0.98, 'click'), (1.96, 'click'), (cues[1]['start'] + 0.5, 'pop')]

# ---------- 2: Cells keep two chemicals apart (glow stick) ----------
def glow_stick(c, x, y, s, snap=0.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-20)
    glow = ease_in_out(clamp(snap * 1.5 - 0.3))
    if glow > 0:
        c.drawRoundRect(skia.Rect(-60, -260, 60, 260), 60, 60, P(color=col('#7dff6a', int(120 * glow)), blur=40))
    c.drawRoundRect(skia.Rect(-34, -230, 34, 230), 34, 34, lin(c, (0, -230, 0, 230), [col(mix_hx('#e8f7ff', '#9dff8a', glow)), col(mix_hx('#c7e6f5', '#4fe04a', glow))]))
    if glow < 1:
        c.drawRoundRect(skia.Rect(-14, -150, 14, 150), 14, 14, P(color=col('#fff2a8', int(255 * (1 - glow)))))
        c.drawRoundRect(skia.Rect(-14, -150, 14, 150), 14, 14, P(color=col('#d9b300', int(255 * (1 - glow))), stroke=3))
    c.drawRoundRect(skia.Rect(-34, -230, 34, 230), 34, 34, P(color=col('#ffffff', 220), stroke=6))
    c.restore()

def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f7f0ff', '#e3d2f2')
    z = ease_in_out(prog(t, 0, 1.4))
    cell_grid(c, t, 540 - 200 * prog(t, t1, 0.6), 1100, lerp(150, 230, z), lerp(110, 170, z), 5, 5)
    label_pill(c, 'sulfur compound', 300, 1530, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill='#8e44ad', hi='#8e44ad')
    label_pill(c, 'enzyme', 760, 1530, size=40, k=ease_back(prog(t, t0 + 1.6, 0.4)), fill='#c48a00', hi='#c48a00')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        c.drawRoundRect(skia.Rect(640, 700, 940, 1440), 60, 60, P(color=col('#1b2a4a', int(220 * min(1, k)))))
        glow_stick(c, 790, 1060, 1.0 * k, snap=0.0, t=t)
        label_pill(c, 'unsnapped', 790, 1380, size=40, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY)

def s2_sfx(D, cues): return [(0.0, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[0]['start'] + 1.6, 'pop'), (cues[1]['start'] + 0.2, 'whoosh')]

# ---------- 3: Knife bursts the cells, chemicals mix ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#f7f0ff', '#e3d2f2')
    hit = t0 + 0.6
    burst = ease_out(prog(t, hit, 1.6))
    shake = math.sin(t * 60) * 8 * (1 - prog(t, hit, 0.3)) if t > hit else 0
    c.save(); c.translate(shake, 0)
    cell_grid(c, t, 540, 1120, 230, 170, 5, 5, burst=burst, glow=prog(t, t1, 0.8))
    c.restore()
    # knife sweeps down through the grid
    ky = lerp(700, 1250, ease_in_out(prog(t, 0.0, hit + 0.05)))
    kx = 560 + lerp(0, 1100, ease_in_out(prog(t, hit + 0.6, 0.8)))
    knife(c, kx, ky, 1.5, rot=0)
    if t > hit:
        for i in range(10):
            u = prog(t, hit + i * 0.03, 0.6)
            if 0 < u < 1:
                ang = i * 36
                x, y = 560 + math.cos(math.radians(ang)) * 200 * u, 1180 + math.sin(math.radians(ang)) * 120 * u
                twinkle(c, x, y, 22 * (1 - u), colr='#ffffff')
    if t > t1:
        label_pill(c, 'MIX + REACT', 540, 1540, size=50, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill='#8e44ad', hi='#5aa800')
    if t > t0 + 1.2:
        label_pill(c, 'cells BURST', 540, 760, size=48, k=ease_back(prog(t, t0 + 1.2, 0.4)), fill=NAVY, hi='#ff5c85')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.1, 'whoosh'), (cues[0]['start'] + 0.6, 'click'), (cues[0]['start'] + 0.7, 'sparkle'), (cues[0]['start'] + 1.2, 'pop'), (cues[1]['start'] + 0.4, 'pop')]

# ---------- 4: A stinging gas forms and floats up ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    kitchen(c, t)
    cutting_board(c, 540, 1420, w_=760)
    onion(c, 540, 1240, 0.8, t, half=True)
    rising_gas(c, t, 0.0, 540, 1150, n=10, spread=160, height=lerp(300, 650, prog(t, t1, 1.0)), seed=4, alpha=235)
    k = ease_back(prog(t, t0 + 1.4, 0.5))
    if k > 0:
        c.save(); c.translate(540, 760); c.scale(k, k)
        c.drawRoundRect(skia.Rect(-420, -70, 420, 70), 70, 70, P(color=col('#ffffff', 235)))
        text_block(c, 'syn-propanethial-S-oxide', 0, 0, size=50, fill='#5a8a00', hi='#5a8a00', stroke='#ffffff', maxw=2000)
        c.restore()
    if t > t1:
        for i in range(3):
            arrow(c, 380 + i * 160, 1080, 380 + i * 160, 900 - math.sin(t * 3 + i) * 20, colr='#ffffff', w=12, alpha=int(200 * prog(t, t1 + 0.3 + i * 0.15, 0.3)))

def s4_sfx(D, cues): return [(0.1, 'whoosh'), (cues[0]['start'] + 1.4, 'pop'), (cues[1]['start'] + 0.3, 'whoosh')]

# ---------- 5: Gas hits eye nerves, tears flush it ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#ffe9e4', '#ffc9c2')
    ex, ey = 540, 1080
    rising_gas(c, t, 0.0, 540, 1700, n=10, spread=260, height=700, seed=7, alpha=140)
    tear = clamp((t - t1) / 3.2) if t > t1 else 0
    human_eye(c, ex, ey, 2.0, t, tear=tear, squint=0.5 * prog(t, t0 + 0.8, 0.6) * (1 - 0.6 * tear))
    # nerve sparks
    if t0 + 0.8 < t < t1 + 1.0:
        for i in range(6):
            ang = i * 60 + t * 40
            r0 = 300 + 30 * math.sin(t * 12 + i)
            x, y = ex + math.cos(math.radians(ang)) * r0, ey + math.sin(math.radians(ang)) * r0 * 0.75
            lightning_bolt(c, x, y, x + math.cos(math.radians(ang)) * 70, y + math.sin(math.radians(ang)) * 50, t=t, seed=i, w=8, alpha=220, branches=False)
        label_pill(c, 'NERVES fire', 540, 1460, size=48, k=ease_back(prog(t, t0 + 1.0, 0.4)) * (1 - prog(t, t1 + 0.6, 0.3)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        label_pill(c, 'TEARS rinse it out', 540, 1460, size=50, k=ease_back(prog(t, t1 + 0.9, 0.4), 2.2), fill='#2f9bff', hi='#2f9bff')

def s5_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'sparkle'), (cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'] + 0.9, 'ding')]

# ---------- 6: Onion defence + kitchen tip ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    if t < t1 - 0.2:
        sky(c, '#2f9bff', '#cdeeff', mid='#7cc6ff')
        soil(c, 1100, t, seed=3)
        # onion growing in soil with shoots
        for i, dx in enumerate((-40, 0, 40)):
            sw = math.sin(t * 1.4 + i) * 10
            p = skia.Path(); p.moveTo(540 + dx * 0.4, 1100); p.quadTo(540 + dx, 900, 540 + dx * 2 + sw, 720)
            c.drawPath(p, P(color=col('#2f7d24'), stroke=26)); c.drawPath(p, P(color=col('#5fc94a'), stroke=16))
        onion(c, 540, 1270, 0.75, t)
        sh = ease_back(prog(t, t0 + 0.8, 0.5))
        if sh > 0:
            c.save(); c.translate(540, 1270); c.scale(sh, sh)
            sp = skia.Path(); sp.moveTo(0, -250); sp.cubicTo(150, -230, 220, -200, 230, -150); sp.cubicTo(230, 80, 140, 200, 0, 260)
            sp.cubicTo(-140, 200, -230, 80, -230, -150); sp.cubicTo(-220, -200, -150, -230, 0, -250); sp.close()
            c.drawPath(sp, P(color=col(GAS, 60)))
            c.drawPath(sp, P(color=col('#8fc93a', 220), stroke=10))
            c.restore()
            label_pill(c, 'DEFENSE', 540, 1560, size=50, k=sh, fill='#5a8a00', hi='#5a8a00')
    else:
        sky(c, '#e6f6ff', '#bfe3ff')
        kc = ease_back(prog(t, t1, 0.5))
        c.save(); c.translate(320, 1060); c.scale(kc, kc); c.rotate(t * 20)
        snowflake(c, 0, 0, 120, t)
        c.restore()
        label_pill(c, 'CHILL it', 320, 1300, size=48, k=kc, fill='#2f9bff', hi='#2f9bff')
        kk = ease_back(prog(t, t1 + 1.6, 0.5))
        if kk > 0:
            c.save(); c.translate(760, 1060); c.scale(kk, kk); knife(c, 0, 0, 0.75, rot=-35); c.restore()
            c.drawCircle(760 + 40, 980, 26 * kk, P(color=col('#ffffff', 220)))
            twinkle(c, 760 + 40, 980, 30 * kk)
            label_pill(c, 'SHARP knife', 720, 1300, size=48, k=kk, fill=NAVY, hi='#ff5c85')
        label_pill(c, 'less gas', 540, 1480, size=46, k=ease_back(prog(t, t1 + 2.6, 0.4)), fill='#5a8a00')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.8, 'whoosh'), (cues[1]['start'], 'pop'), (cues[1]['start'] + 1.6, 'pop'), (cues[1]['start'] + 2.6, 'click')]

# ---------- 7: Wild part: enzyme found in 2002, tearless onions ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, NAVY, '#3a2f6a', mid='#2a2a5a')
    dust(c, t, seed=3, n=24)
    # big year counter rolling to 2002
    u = ease_out(prog(t, t0 + 0.4, 1.6))
    yr = int(lerp(1900, 2002, u))
    text_block(c, str(yr), 540, 1000, size=200, fill='#ffd23f', hi='#ffd23f', stroke=NAVY, scale=0.9 + 0.1 * ease_back(prog(t, t0 + 2.0, 0.4)))
    label_pill(c, 'tear ENZYME found', 540, 760 + 40, size=46, k=ease_back(prog(t, t0 + 2.0, 0.4)) * (1 - prog(t, t1, 0.3)), fill=NAVY, hi='#ff5c85')
    if t > t1:
        k = ease_back(prog(t, t1 + 0.2, 0.5))
        onion(c, 540, 1300, 0.6 * k, t, rot=math.sin(t * 2) * 4)
        c.save(); c.translate(540, 1300); c.scale(k, k)
        c.drawCircle(150, -150, 56, P(color=col('#4cd964')))
        ck = skia.Path(); ck.moveTo(122, -150); ck.lineTo(142, -128); ck.lineTo(180, -172)
        c.drawPath(ck, P(color=col('#ffffff'), stroke=14))
        c.restore()
        label_pill(c, 'TEARLESS onions', 540, 1540, size=50, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill='#5a8a00', hi='#5a8a00')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] + 0.2, 'pop'), (cues[1]['start'] + 0.8, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    kitchen(c, t)
    cutting_board(c, 540, 1420, w_=700)
    onion(c, 540, 1210, 0.9, t, rot=math.sin(t * 1.5) * 3)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k = ease_back(prog(t, cues[1]['start'], 0.5))
    if k > 0 and fo > 0:
        label_pill(c, 'next: GOOSEBUMPS', 540, 760, size=48, k=k, fill=NAVY, hi='#ff5c85', alpha=int(240 * fo))
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'pop'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do onions make you cry?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do onions make you cry?', 'Why do ONIONS make you cry?'),
            ("Because the onion is fighting back, with chemistry.", 'The onion FIGHTS back')], tail=0.9),
        dict(name='cells', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every onion cell keeps two chemicals apart: a sulfur compound and an enzyme.', 'Two chemicals kept APART'),
            ("Like a glow stick before you snap it.", "Like a GLOW stick, unsnapped")], tail=0.9),
        dict(name='cut', draw=s3, sfx_fn=s3_sfx, lines=[
            ('When the knife goes in, the cells burst open.', 'The knife BURSTS the cells'),
            ('The two chemicals mix, and start to react.', 'The chemicals MIX')], tail=0.9),
        dict(name='gas', draw=s4, sfx_fn=s4_sfx, lines=[
            ('Within seconds they make a stinging gas, with a real tongue twister of a name.', 'A stinging GAS forms'),
            ('It floats up, right toward your face.', 'It floats UP to your face')], tail=0.9),
        dict(name='eyes', draw=s5, sfx_fn=s5_sfx, lines=[
            ('When it reaches your eyes, it sets off the nerves there.', 'It sets off eye NERVES'),
            ('So your eyes make tears, to rinse the gas away.', 'TEARS rinse it away')], tail=1.4),
        dict(name='tips', draw=s6, sfx_fn=s6_sfx, lines=[
            ("For the onion, it's a defense against animals that bite into it.", "It's the onion's DEFENSE"),
            ('Your move: chill the onion first, and use a sharp knife. Less gas, fewer tears.', 'COLD onion, SHARP knife')], tail=1.0),
        dict(name='wild', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: scientists only found the enzyme behind the tears in 2002.", 'The tear enzyme: found in 2002'),
            ('Since then, breeders have grown onions that barely make you cry.', 'TEARLESS onions exist now')], tail=1.4),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So onion tears are your eyes washing away a chemical defense.', 'Tears wash away a DEFENSE'),
            ('Next up: why we get goosebumps.', 'Next: GOOSEBUMPS'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
