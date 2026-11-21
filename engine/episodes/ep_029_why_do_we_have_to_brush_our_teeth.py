"""Episode 29 (EN, general audience): Why do we have to brush our teeth?
Facts checked (NIDCR "The Tooth Decay Process", Healthline "Plaque vs. tartar", Colgate "Enamel decay: how it starts",
ADA MouthHealthy "Brushing your teeth", Crest/Oral-B "Plaque vs tartar"):
- Plaque is a sticky film (biofilm) of bacteria that forms on teeth every day.
- Bacteria in plaque feed on sugars and starches and produce acids; the acid removes minerals from the enamel
  (demineralisation). Repeated acid attacks can create a hole: a cavity.
- Saliva and fluoride help put minerals back (remineralisation); fluoride makes enamel more acid-resistant.
- Plaque that is not removed can harden into tartar (calculus) within roughly 24–72 hours; tartar has to be
  removed by a dental professional.
- Enamel is the hardest substance in the human body; it contains no living cells, so the body cannot regrow it.
- Dentists recommend brushing twice a day for two minutes with fluoride toothpaste (ADA).
"""
import math, random
from lib import *

NAVY = '#1b2a4a'

def bath_bg(c, t, top='#eaf6ff', bot='#d4ebff'):
    sky(c, top, bot)
    dust(c, t, seed=2, n=12, a=70, colr='#ffffff')

def swarm(c, cx, cy, t, n=8, spread=170, r=20, seed=1, alpha=255, k=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        ang = rnd.uniform(0, 6.28) + t * rnd.uniform(0.3, 0.7)
        rr = spread * rnd.uniform(0.4, 1.0) * k
        bacterium(c, cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.6, r, t, seed=i + seed,
                  colr=['#9b7be0', '#45b8a8', '#ff8fa8'][i % 3], alpha=alpha)

# ---------- 1: Hook (cold open: shiny tooth, bacteria already circling) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    bath_bg(c, t)
    tooth(c, 540, 1150, 1.45, t, shine=0.6 + 0.4 * math.sin(t * 3))
    twinkle(c, 360, 860, 26 + 6 * math.sin(t * 5), colr='#ffffff')
    label_pill(c, 'HARDEST in your body', 540, 700, size=44, k=ease_back(prog(t, 0.3, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        swarm(c, 540, 930, t, n=7, spread=260, k=ease_out(prog(t, t1 + 0.8, 1.0)), alpha=255 * prog(t, t1 + 0.8, 0.4))

def s1_sfx(D, cues): return [(0.0, 'sparkle'), (0.3, 'pop'), (cues[1]['start'] + 0.8, 'whoosh')]

# ---------- 2: Plaque: a sticky film of bacteria, every day ----------
def s2(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t)
    pl = ease_in_out(prog(t, t0 + 0.4, 3.0))
    tooth(c, 540, 1150, 1.45, t, plaque=pl, shine=1 - 0.6 * pl)
    swarm(c, 540, 1000, t, n=9, spread=200, r=18, seed=3, alpha=200)
    # day counter
    dk = ease_back(prog(t, t0 + 0.8, 0.4))
    label_pill(c, 'EVERY day', 300, 700, size=44, k=dk, fill=NAVY, hi='#ff5c85')
    if t > t1:
        kk = ease_back(prog(t, t1 + 0.3, 0.5), 2.2)
        c.save(); c.translate(720, 720); c.scale(kk, kk)
        c.drawRoundRect(skia.Rect(-180, -70, 180, 70), 35, 35, P(color=col('#f2e08a')))
        c.drawRoundRect(skia.Rect(-180, -70, 180, 70), 35, 35, P(color=col(NAVY), stroke=6))
        text_block(c, 'PLAQUE', 0, 0, size=64, fill=NAVY, hi=NAVY, stroke='#f2e08a')
        c.restore()

def s2_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[1]['start'] + 0.3, 'pop')]

# ---------- 3: Sugar in, acid out ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t, top='#fff4e6', bot='#ffe6cc')
    # sugar cubes drop in from the top-left
    sk = ease_out(prog(t, t0 + 0.2, 0.8))
    sugar_cubes(c, lerp(180, 250, sk), lerp(620, 1000, sk), 1.7)
    label_pill(c, 'SUGAR', 250, 1230, size=44, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#ff9f1c')
    # bacteria eating (pulsing) in the middle
    for i in range(3):
        bx, by = 640 + (i - 1) * 150, 1000 + 40 * i + 30 * math.sin(t * 2 + i)
        sc = 1 + 0.12 * math.sin(t * 8 + i)
        bacterium(c, bx, by, 52 * sc, t, seed=i, colr=['#9b7be0', '#45b8a8', '#ff8fa8'][i])
    arrow(c, 370, 1000, 460, 1020, colr=NAVY, w=12, alpha=int(255 * prog(t, t0 + 1.2, 0.4)))
    if t > t1:
        for j in range(6):
            u = ((t - t1) * 0.7 + j / 6) % 1.0
            acid_drop(c, 560 + (j % 3) * 110, lerp(1150, 1480, u), 32, alpha=int(255 * min(1, (1 - u) * 3)))
        label_pill(c, 'ACID', 780, 1560, size=50, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#6fae1a')

def s3_sfx(D, cues): return [(cues[0]['start'] + 0.2, 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'] + 0.3, 'boing'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 4: Acid pulls minerals out -> cavity ----------
def s4(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t)
    cav = ease_in_out(prog(t, t1 + 0.2, 2.2))
    tooth(c, 540, 1180, 1.5, t, section=ease_in_out(prog(t, t0, 0.8)), weak=ease_in_out(prog(t, t0 + 0.8, 1.5)), cavity=cav, shine=0.4)
    # minerals leaving the enamel
    for j in range(8):
        u = ((t - t0) * 0.5 + j / 8) % 1.0
        if t < t0 + 0.6: break
        x0 = 540 + (j - 3.5) * 50; y0 = 1180 - 210
        c.drawPath(hexagon_path(x0 + 20 * math.sin(u * 6 + j), lerp(y0, y0 - 260, u), 12), P(color=col('#ffffff', int(230 * (1 - u)))))
        c.drawPath(hexagon_path(x0 + 20 * math.sin(u * 6 + j), lerp(y0, y0 - 260, u), 12), P(color=col('#8aa0bf', int(200 * (1 - u))), stroke=2))
    label_pill(c, 'MINERALS out', 300, 690, size=42, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'CAVITY', 760, 1470, size=50, k=ease_back(prog(t, t1 + 1.4, 0.4)), fill=NAVY, hi='#ff5c85')

def s4_sfx(D, cues): return [(cues[0]['start'], 'whoosh'), (cues[0]['start'] + 1.0, 'pop'), (cues[1]['start'] + 1.4, 'pop')]

# ---------- 5: Brushing wipes plaque, fluoride repairs (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t)
    sw = prog(t, t0 + 0.3, max(2.5, t1 - t0 + 0.2))
    pl = 1 - ease_in_out(sw)
    rep = ease_out(prog(t, t1 + 0.4, 0.8)) * (1 - 0.3 * prog(t, t1 + 3.0, 1.0))
    tooth(c, 540, 1180, 1.45, t, plaque=pl, weak=0.7 * (1 - ease_in_out(prog(t, t1 + 0.6, 2.0))) if t > t1 else 0.7 * (1 - pl),
          repair=rep if t > t1 else 0.0, shine=1 - pl * 0.6)
    if sw < 1:
        bx = 540 + 200 * math.sin(t * 9)
        toothbrush(c, bx, 860, 0.9, rot=0)
        for j in range(4):
            u = ((t * 1.5) + j / 4) % 1.0
            c.drawCircle(bx + (j - 1.5) * 60, 860 - 80 * u, 14 * (1 - u) + 4, P(color=col('#ffffff', int(230 * (1 - u)))))
    label_pill(c, 'SCRUB it off', 540, 700, size=46, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi='#2f9bff')
    if t > t1:
        label_pill(c, 'FLUORIDE rebuilds', 540, 1560, size=46, k=ease_back(prog(t, t1 + 0.4, 0.4)), fill=NAVY, hi='#1fa8c9')

def s5_sfx(D, cues):
    return [(cues[0]['start'] + 0.3, 'whoosh'), (cues[0]['start'] + 0.8, 'pop'), (cues[0]['start'] + 1.6, 'whoosh'), (cues[1]['start'] + 0.4, 'ding')]

# ---------- 6: Skip it -> tartar ----------
def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t, top='#f3f0ea', bot='#e6e0d4')
    tt = ease_in_out(prog(t, t0 + 0.8, 2.4))
    tooth(c, 540, 1180, 1.45, t, plaque=0.8, tartar=tt, shine=0.3)
    # calendar day flips 1 -> 3
    day = 1 + int(2 * clamp((t - t0 - 0.6) / 2.4)) if t > t0 + 0.6 else 1
    ck = ease_back(prog(t, t0 + 0.4, 0.4))
    if ck > 0:
        c.save(); c.translate(800, 760); c.scale(ck, ck)
        c.drawRoundRect(skia.Rect(-80, -80, 80, 80), 16, 16, P(color=col('#ffffff')))
        c.drawRoundRect(skia.Rect(-80, -80, 80, -40), 16, 16, P(color=col('#ff5c85')))
        c.drawRect(skia.Rect(-80, -56, 80, -40), P(color=col('#ff5c85')))
        c.drawRoundRect(skia.Rect(-80, -80, 80, 80), 16, 16, P(color=col(NAVY), stroke=5))
        text_block(c, f'DAY {day}', 0, 18, size=40, fill=NAVY, hi=NAVY, stroke='#ffffff')
        c.restore()
    label_pill(c, 'hard TARTAR', 330, 760, size=44, k=ease_back(prog(t, t0 + 2.0, 0.4)), fill=NAVY, hi='#b08a3e')
    if t > t1:
        label_pill(c, 'only a DENTIST removes it', 540, 1580, size=42, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi='#2f9bff')

def s6_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 1.6, 'click'), (cues[0]['start'] + 2.0, 'pop'), (cues[1]['start'] + 0.6, 'pop')]

# ---------- 7: Wild part: enamel can't grow back ----------
def bone(c, x, y, s, crack=0.0, heal=0.0, alpha=255):
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    for sy in (-1, 1):
        for sx in (-1, 1):
            c.drawCircle(sx * 120, sy * 26, 36, P(color=col('#fff7e6', a)))
            c.drawCircle(sx * 120, sy * 26, 36, P(color=col('#c9b48a', a), stroke=4))
    c.drawRoundRect(skia.Rect(-125, -32, 125, 32), 20, 20, P(color=col('#fff7e6', a)))
    c.drawLine(-120, -32, 120, -32, P(color=col('#c9b48a', a), stroke=4)); c.drawLine(-120, 32, 120, 32, P(color=col('#c9b48a', a), stroke=4))
    if crack > 0 and heal < 1:
        p = skia.Path(); p.moveTo(-6, -34); p.lineTo(8, -10); p.lineTo(-8, 8); p.lineTo(6, 34)
        c.drawPath(p, P(color=col('#8a6a4a', int(a * crack * (1 - heal))), stroke=6))
    if heal > 0:
        c.drawCircle(0, 0, 40, P(color=col('#3fbf6a', int(a * 0.35 * heal))))
    c.restore()

def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    bath_bg(c, t, top='#efe9ff', bot='#e2ebff')
    bk = ease_back(prog(t, t0 + 0.4, 0.5))
    if bk > 0:
        bone(c, 280, 1000, 0.9 * bk, crack=1.0, heal=ease_in_out(prog(t, t0 + 1.4, 1.6)))
        label_pill(c, 'BONE heals', 280, 1140, size=42, k=bk, fill=NAVY, hi='#3fbf6a')
    tk = ease_back(prog(t, t0 + 2.4, 0.5))
    if tk > 0:
        tooth(c, 780, 1000, 0.75 * tk, t, cavity=1.0, gum=False, shine=0.5)
        label_pill(c, 'ENAMEL', 780, 1340, size=42, k=tk, fill=NAVY, hi='#2f9bff')
    if t > t1:
        xk = ease_back(prog(t, t1 + 0.5, 0.4))
        if xk > 0:
            c.save(); c.translate(780, 1460); c.scale(xk, xk)
            c.drawRoundRect(skia.Rect(-190, -50, 190, 50), 25, 25, P(color=col('#ff5c85')))
            text_block(c, "NO regrowth", 0, 0, size=46, fill='#ffffff', hi='#ffffff', stroke='#b8183f')
            c.restore()
        label_pill(c, 'no living CELLS', 540, 720, size=44, k=ease_back(prog(t, t1 + 1.2, 0.4)), fill=NAVY, hi='#9b4dff')

def s7_sfx(D, cues): return [(cues[0]['start'] + 0.4, 'pop'), (cues[0]['start'] + 1.4, 'sparkle'), (cues[0]['start'] + 2.4, 'pop'), (cues[1]['start'] + 0.5, 'click'), (cues[1]['start'] + 1.2, 'pop')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    bath_bg(c, t)
    tooth(c, 540, 1100, 1.2, t, shine=0.6 + 0.4 * math.sin(t * 3))
    toothbrush(c, 540 + 160 * math.sin(t * 5), 820, 0.7)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    kk = ease_back(prog(t, cues[1]['start'], 0.5))
    if kk > 0 and fo > 0:
        c.saveLayerAlpha(None, int(255 * fo))
        label_pill(c, 'next: CLOUDS', 540, 690, size=48, k=kk, fill=NAVY, hi='#2f9bff')
        c.restore()
    follow_button(c, t, cues[2]['start'])

def s8_sfx(D, cues): return [(cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do we have to brush our teeth?',
    music=False, faces=False, ambience='water',
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do we have to brush our teeth?', 'Why do we BRUSH our teeth?'),
            ('Enamel is the hardest thing in your body, and bacteria can still make holes in it.', 'The HARDEST thing in your body')], tail=0.8),
        dict(name='plaque', draw=s2, sfx_fn=s2_sfx, lines=[
            ('Every day, a thin, sticky film of bacteria grows on your teeth.', 'A sticky FILM of bacteria'),
            ("It's called plaque.", "It's called PLAQUE")], tail=0.8),
        dict(name='acid', draw=s3, sfx_fn=s3_sfx, lines=[
            ('Those bacteria feed on the sugar you eat,', 'They feed on SUGAR'),
            ('and they give off acid as waste.', 'and give off ACID')], tail=0.8),
        dict(name='cavity', draw=s4, sfx_fn=s4_sfx, lines=[
            ('That acid slowly pulls minerals out of the enamel, like water wearing down a stone.', 'Acid pulls out MINERALS'),
            ('Do that often enough, and you get a hole: a cavity.', 'Until a hole: a CAVITY')], tail=1.0),
        dict(name='brush', draw=s5, sfx_fn=s5_sfx, lines=[
            ('Brushing scrubs the plaque away before its acid can do damage.', 'Brushing SCRUBS it away'),
            ('And the fluoride in toothpaste helps rebuild the weak spots.', 'FLUORIDE rebuilds enamel')], tail=1.2),
        dict(name='tartar', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Skip brushing, and within a few days plaque can harden into tartar.', 'Plaque hardens into TARTAR'),
            ('That crust is something only a dentist can remove.', 'Only a DENTIST removes it')], tail=0.8),
        dict(name='enamel', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: a broken bone can heal. Enamel can't.", "Enamel can't HEAL"),
            ('It has no living cells, so once it is gone, your body cannot grow it back.', 'No CELLS, no regrowth')], tail=1.2),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ("So you brush to remove the bacteria before their acid eats your enamel.", 'Brush away the ACID makers'),
            ('Next up: how clouds float.', 'Next: how CLOUDS float'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
