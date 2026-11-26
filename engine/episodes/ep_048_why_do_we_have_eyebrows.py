"""Episode 48 (EN, general audience): Why do we have eyebrows?
Facts checked (Healthline "Why do we have eyebrows?"; HowStuffWorks "Why do we have eyebrows?"; Mental Floss "Why do
we have eyebrows?"; American Academy of Ophthalmology "Why do humans have eyebrows and eyelashes?"; Sadr, Jarudi &
Sinha 2003, Perception 32:285-293 "The role of eyebrows in face recognition" (PubMed 12729380); Godinho, Spikins &
O'Higgins 2018, Nature Ecology & Evolution "Supraorbital morphology and social dynamics in human evolution"):
- Eyebrows help keep sweat and rain out of the eyes: the arched shape and the hairs growing sideways/outward guide
  moisture toward the sides of the face. Sweat contains salt and can sting/irritate the eyes and blur vision.
- Eyebrows are important for non-verbal communication: raising, lowering and drawing them together signal surprise,
  worry, anger etc.; the quick "eyebrow flash" is a widespread greeting signal.
- Hypothesis (Godinho et al. 2018): as the heavy bony brow ridge of earlier humans shrank, a flatter forehead with
  mobile eyebrows allowed more subtle social signalling. Presented as "scientists think".
- Sadr et al. 2003: recognition of famous faces dropped more when the eyebrows were digitally removed than when the
  eyes were removed.
"""
import math, random
from lib import *

NAVY = '#1b2a4a'
SKYB = '#2f9bff'
HOT = '#ff5c85'
GOLD = '#e0a000'

def drop(c, x, y, r, alpha=255):
    a = int(alpha)
    dp = skia.Path(); dp.moveTo(x, y - r * 2); dp.cubicTo(x + r, y - r * 0.6, x + r, y + r, x, y + r); dp.cubicTo(x - r, y + r, x - r, y - r * 0.6, x, y - r * 2); dp.close()
    c.drawPath(dp, rad(x - r * 0.3, y, r * 1.5, [col('#ffffff', a), col('#8fd3ff', a), col('#3fa9ff', a)], [0, 0.4, 1]))
    c.drawPath(dp, P(color=col('#2a86e0', a), stroke=3))

def brow_path(sx, cx, cy, s):
    """Brow centreline (in screen space) for a big close-up; sx = side."""
    p = skia.Path(); p.moveTo(cx + sx * 60 * s, cy + 20 * s)
    p.cubicTo(cx + sx * 150 * s, cy - 50 * s, cx + sx * 280 * s, cy - 60 * s, cx + sx * 380 * s, cy + 30 * s)
    return p

def card(c, x, y, w, h, k):
    if k <= 0: return False
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawRoundRect(skia.Rect(-w / 2, -h / 2 + 10, w / 2, h / 2 + 10), 30, 30, P(color=col('#0b1a3a', 50), blur=10))
    c.drawRoundRect(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), 30, 30, P(color=col('#ffffff')))
    c.restore(); return True

# ---------- 1: Hook (cold open: brows already moving) ----------
def s1(c, t, D, cues):
    t1 = cues[1]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    r = 0.5 + 0.5 * math.sin(t * 4.5)
    brows = 1.0
    if t1 - 0.2 < t < t1 + 1.2: brows = 1 - prog(t, t1 - 0.2, 0.3)
    if t >= t1 + 1.2: brows = prog(t, t1 + 1.2, 0.3)
    plain_face(c, 540, 1150, 1.15, t, raise_=r * 0.8 if t < t1 else 0.0, brows=brows)
    label_pill(c, 'what are they FOR?', 540, 700, size=48, k=ease_back(prog(t, 0.2, 0.4)), fill=NAVY, hi=HOT)
    if t > t1 + 1.2:
        label_pill(c, '2 big JOBS', 540, 1560, size=50, k=ease_back(prog(t, t1 + 1.3, 0.4)), fill=NAVY, hi=SKYB)

def s1_sfx(D, cues):
    t1 = cues[1]['start']
    return [(0.0, 'whoosh'), (0.2, 'pop'), (t1 - 0.2, 'whoosh'), (t1 + 1.3, 'pop')]

# ---------- 2: Job 1: sweat and rain ----------
def s2(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#7a8fa8', '#c9d6e6')
    rnd = random.Random(5)
    for i in range(40):
        x = rnd.uniform(0, W); sp = rnd.uniform(500, 800)
        y = (rnd.uniform(0, H) + t * sp) % (H + 200) - 100
        c.drawLine(x, y, x - 8, y + 40, P(color=col('#ffffff', 120), stroke=4))
    plain_face(c, 540, 1150, 1.15, t, sweat=(t * 0.35) % 1.0 if t > t0 else 0.0)
    label_pill(c, 'SWEAT + RAIN', 540, 700, size=48, k=ease_back(prog(t, t0 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'kept OUT of eyes', 540, 1580, size=44, k=ease_back(prog(t, t0 + 1.8, 0.4)), fill=NAVY, hi=HOT)

def s2_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.6, 'pop'), (t0 + 1.8, 'pop')]

# ---------- 3: The arch + sideways hairs = a gutter ----------
def s3(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    skin = '#f2c9a6'
    c.drawRect(skia.Rect(0, 0, W, H), rad(540, 1000, 1200, [col(mix_hx(skin, '#ffffff', 0.2)), col(skin), col(mix_hx(skin, '#c98a6a', 0.3))], [0, 0.6, 1]))
    cx, cy, s = 90, 1060, 1.9
    # big close-up of the viewer's-right brow and eye
    human_eye(c, cx + 420, cy + 280, 1.3, t)
    bp = brow_path(1, cx, cy, s / 1.9 * 1.4)
    c.drawPath(bp, P(color=col('#3a2a20'), stroke=70))
    m = skia.PathMeasure(bp, False); L = m.getLength()
    hk = prog(t, t0 + 1.0, 0.4)
    for k in range(26):
        pos, tan = m.getPosTan(L * (0.03 + 0.036 * k))
        if pos is None: continue
        dx, dy = tan.x(), tan.y()
        c.drawLine(pos.x() - dx * 20, pos.y() - dy * 20 + 18, pos.x() + dx * 26, pos.y() + dy * 26 - 14, P(color=col('#5a4030'), stroke=7))
    if hk > 0:
        for k in range(4):
            pos, tan = m.getPosTan(L * (0.2 + 0.2 * k))
            arrow(c, pos.x() - tan.x() * 20, pos.y() - 60, pos.x() + tan.x() * 50, pos.y() - 60 + tan.y() * 50, colr='#ffffff', w=8, alpha=int(230 * hk))
    label_pill(c, 'hairs point SIDEWAYS', 470, 690, size=42, k=ease_back(prog(t, t0 + 1.1, 0.4)), fill=NAVY, hi=SKYB)
    # drops sliding along the brow to the side
    if t > t1:
        for i in range(3):
            u = ((t - t1) * 0.45 + i / 3) % 1.0
            if u < 0.25:
                x, y = 200 + i * 120, lerp(820, 1000, u / 0.25)
            else:
                pos, _ = m.getPosTan(L * lerp(0.15 + i * 0.1, 1.0, (u - 0.25) / 0.75))
                x, y = pos.x(), pos.y() - 50
                if u > 0.92: y += (u - 0.92) * 3000
            drop(c, x, y, 22, alpha=255 * min(1, (1 - u) * 8))
        label_pill(c, 'like a roof GUTTER', 520, 1560, size=44, k=ease_back(prog(t, t1 + 0.8, 0.4)), fill=NAVY, hi=GOLD)

def s3_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0, 'whoosh'), (t0 + 1.1, 'pop'), (t1 + 0.3, 'whoosh'), (t1 + 0.8, 'pop')]

# ---------- 4: Why it matters: salty sweat stings and blurs ----------
def s4(c, t, D, cues):
    t0 = cues[0]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    u = prog(t, t0 + 0.3, 1.0)
    drop(c, 540, lerp(640, 980, ease_in_out(u)), 34, alpha=255 * (1 - prog(t, t0 + 1.3, 0.2)))
    sq = prog(t, t0 + 1.3, 0.4)
    human_eye(c, 540, 1100, 1.6, t, tear=sq * 0.8, squint=sq)
    if sq > 0:
        c.drawCircle(540, 1100, 260, P(color=col('#ffffff', int(90 * sq)), blur=40))
    label_pill(c, 'SALT stings', 300, 1460, size=44, k=ease_back(prog(t, t0 + 1.5, 0.4)), fill=NAVY, hi=HOT)
    label_pill(c, 'vision BLURS', 760, 1560, size=44, k=ease_back(prog(t, t0 + 2.3, 0.4)), fill=NAVY, hi=SKYB)

def s4_sfx(D, cues):
    t0 = cues[0]['start']
    return [(t0 + 0.3, 'whoosh'), (t0 + 1.3, 'boing'), (t0 + 1.5, 'pop'), (t0 + 2.3, 'pop')]

# ---------- 5: Job 2: talking without words (aha) ----------
def s5(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    moods = [('SURPRISE', 1.0, 0.0), ('WORRY', 0.5, 0.0), ('FOCUS', 0.0, 0.45), ('HELLO', 0.0, 0.0)]
    i = min(3, max(0, int((t - t1 - 0.1) / 1.1))) if t > t1 else -1
    raise_, frown = 0.0, 0.0
    if i >= 0:
        name, r_, f_ = moods[i]
        loc = (t - t1 - 0.1) - i * 1.1
        k = ease_in_out(prog(loc, 0, 0.25))
        raise_, frown = r_ * k, f_ * k
        if name == 'HELLO':
            raise_ = 0.9 * math.sin(math.pi * clamp(loc / 0.45)) if loc < 0.45 else 0.0
        label_pill(c, name, 540, 1580, size=50, k=ease_back(prog(loc, 0, 0.3)), fill=NAVY, hi=HOT if i == 3 else SKYB)
    elif t > t0 + 0.4:
        raise_ = 0.35 * (0.5 + 0.5 * math.sin((t - t0) * 5))
    plain_face(c, 540, 1130, 1.1, t, raise_=raise_, frown=frown)
    label_pill(c, 'Job 2: SIGNALS', 540, 700, size=48, k=ease_back(prog(t, t0 + 0.4, 0.4)), fill=NAVY, hi=GOLD)

def s5_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.4, 'ding')] + [(t1 + 0.1 + i * 1.1, 'pop') for i in range(4)]

# ---------- 6: Brow ridge shrank, mobile brows took over ----------
def ridge_head(c, x, y, s, ridge, t, alpha=255):
    """Side-profile head silhouette, facing right; ridge 0..1 = bony brow bulge."""
    a = int(alpha); c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-160, 220); p.cubicTo(-190, 40, -170, -200, 0, -230); p.cubicTo(90, -240, 140, -190, 150, -110)
    p.cubicTo(150 + 40 * ridge, -100, 160 + 40 * ridge, -70, 140, -55)
    p.cubicTo(150, -10, 190, 30, 175, 50); p.cubicTo(165, 70, 150, 75, 150, 95); p.cubicTo(150, 140, 120, 170, 60, 180); p.lineTo(40, 260); p.lineTo(-120, 260); p.close()
    c.drawPath(p, lin(c, (0, -240, 0, 260), [col('#f2c9a6', a), col('#e0aa86', a)]))
    c.drawPath(p, P(color=col('#b07a5a', a), stroke=5))
    if ridge > 0.3:
        c.drawOval(skia.Rect(70, -120, 200, -60), P(color=col('#c9a080', int(a * 0.7 * ridge))))
    else:
        c.drawLine(95, -95, 150, -100, P(color=col('#3a2a20', a), stroke=14))
    c.drawCircle(120, -55, 9, P(color=col('#1b2a4a', a)))
    c.restore()

def s6(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    k1 = ease_back(prog(t, t0 + 0.2, 0.5))
    if card(c, 300, 1120, 420, 640, k1):
        ridge_head(c, 300, 1120, 1.0 * k1, 1.0, t)
    label_pill(c, 'heavy BROW RIDGE', 300, 1500, size=36, k=ease_back(prog(t, t0 + 0.8, 0.4)), fill=NAVY, hi=GOLD)
    k2 = ease_back(prog(t, t1, 0.5))
    if card(c, 780, 1120, 420, 640, k2):
        ridge_head(c, 780, 1120, 1.0 * k2, 0.0, t)
        lift = 12 * (0.5 + 0.5 * math.sin((t - t1) * 5))
        c.drawLine(780 + 95 * k2, 1120 - (95 + lift) * k2, 780 + 150 * k2, 1120 - (100 + lift) * k2, P(color=col('#3a2a20'), stroke=14 * k2))
    label_pill(c, 'MOBILE brows', 780, 1500, size=36, k=ease_back(prog(t, t1 + 0.6, 0.4)), fill=NAVY, hi=SKYB)
    ak = ease_out(prog(t, t1 + 0.2, 0.5))
    if ak > 0: arrow(c, 520, 1120, lerp(520, 560, ak), 1120, colr=NAVY, w=12, alpha=int(255 * ak))
    label_pill(c, 'scientists THINK', 540, 700, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)

def s6_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.2, 'whoosh'), (t0 + 0.8, 'pop'), (t1, 'whoosh'), (t1 + 0.6, 'pop')]

# ---------- 7: Wild part: faces without eyebrows are harder to recognise ----------
def s7(c, t, D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    sky(c, '#2f9bff', '#cfe8ff')
    k1 = ease_back(prog(t, t0 + 0.3, 0.5)); k2 = ease_back(prog(t, t0 + 0.8, 0.5))
    if card(c, 300, 1080, 420, 600, k1):
        c.save(); c.translate(300, 1080); c.scale(k1, k1); c.translate(-300, -1080)
        plain_face(c, 300, 1080, 0.62, t, hair='#2e2a2a', skin='#e8b48f', iris='#5b8fd6')
        c.drawRoundRect(skia.Rect(300 - 120, 1080 - 25, 300 + 120, 1080 + 45), 30, 30, P(color=col('#e8b48f'), blur=6))
        c.restore()
    if card(c, 780, 1080, 420, 600, k2):
        c.save(); c.translate(780, 1080); c.scale(k2, k2); c.translate(-780, -1080)
        plain_face(c, 780, 1080, 0.62, t, hair='#2e2a2a', skin='#e8b48f', iris='#5b8fd6', brows=0.0)
        c.restore()
    label_pill(c, 'NO EYES', 300, 1440, size=40, k=ease_back(prog(t, t0 + 1.0, 0.4)), fill=NAVY, hi=SKYB)
    label_pill(c, 'NO BROWS', 780, 1440, size=40, k=ease_back(prog(t, t0 + 1.4, 0.4)), fill=NAVY, hi=HOT)
    if t > t1:
        # result: brows-less face is harder -> red mark; eyes-less one gets the check
        kk = ease_back(prog(t, t1 + 0.6, 0.4))
        if kk > 0:
            c.save(); c.translate(780, 1580); c.scale(kk, kk)
            c.drawRoundRect(skia.Rect(-170, -55, 170, 55), 30, 30, P(color=col('#e8264f')))
            text_block(c, 'HARDER', 0, -2, size=50, fill='#ffffff', hi='#ffffff', stroke='#b8183f')
            c.restore()
        label_pill(c, 'famous faces TEST', 540, 700, size=42, k=ease_back(prog(t, t1 + 0.2, 0.4)), fill=NAVY, hi=GOLD)

def s7_sfx(D, cues):
    t0, t1 = cues[0]['start'], cues[1]['start']
    return [(t0 + 0.3, 'pop'), (t0 + 0.8, 'pop'), (t1 + 0.2, 'pop'), (t1 + 0.6, 'sparkle')]

# ---------- 8: Outro ----------
def s8(c, t, D, cues):
    night_sky(c, t)
    fo = 1 - prog(t, cues[2]['start'] - 0.3, 0.4)
    k0 = ease_back(prog(t, cues[0]['start'] + 0.3, 0.4)) * fo
    if k0 > 0:
        label_pill(c, 'GUTTERS + SIGNALS', 540, 700, size=48, k=k0, fill=NAVY, hi=SKYB)
    kk = ease_back(prog(t, cues[1]['start'], 0.5)) * fo
    if kk > 0:
        label_pill(c, 'next: how FIREFLIES glow', 540, 820, size=42, k=kk, fill=NAVY, hi=GOLD)
        for i in range(5):
            ph = t * 0.7 + i * 1.3
            firefly(c, 200 + i * 170, 1150 + 60 * math.sin(ph), 0.35 * kk, t, glow=0.5 + 0.5 * math.sin(t * 3 + i * 2), rot=20 * math.sin(ph), fly=True)
    follow_button(c, t, cues[2]['start'], y=1560)

def s8_sfx(D, cues): return [(cues[0]['start'] + 0.3, 'pop'), (cues[1]['start'], 'whoosh'), (cues[2]['start'] + 0.1, 'chime')]

EPISODE = dict(
    title='Why do we have eyebrows?',
    music=False, faces=False,
    scenes=[
        dict(name='hook', draw=s1, sfx_fn=s1_sfx, lead=0.1, lines=[
            ('Why do we have eyebrows?', 'Why do we have EYEBROWS?'),
            ('Two strips of hair, with two big jobs.', 'Two strips of hair, TWO jobs')], tail=1.0),
        dict(name='sweat', draw=s2, sfx_fn=s2_sfx, ambience='water', lines=[
            ('Job one: they keep sweat and rain out of your eyes.', 'Job 1: keep sweat OUT'),
            ('Even one drop running in can make you squint.', 'One drop makes you SQUINT')], tail=1.1),
        dict(name='gutter', draw=s3, sfx_fn=s3_sfx, lines=[
            ('The arch, and hairs that point sideways,', 'The ARCH + sideways hairs'),
            ('steer drops off to the side of your face, like a gutter on a roof.', 'Like a roof GUTTER')], tail=1.0),
        dict(name='sting', draw=s4, sfx_fn=s4_sfx, lines=[
            ('That matters. Sweat is salty, so a drip in your eye stings, and makes everything blurry.', 'Salty sweat STINGS')], tail=1.2),
        dict(name='signals', draw=s5, sfx_fn=s5_sfx, trans='punch', lines=[
            ('Job two: talking without words.', 'Job 2: talking WITHOUT words'),
            ('A tiny lift or a frown can say surprise, worry, focus, or a quick hello.', 'Surprise, worry, focus, HELLO')], tail=1.2),
        dict(name='ridge', draw=s6, sfx_fn=s6_sfx, lines=[
            ('Scientists think that as our ancestors lost their heavy brow ridge,', 'The bony BROW RIDGE shrank'),
            ('flexible eyebrows took over as signals.', 'Flexible brows took OVER')], tail=1.2),
        dict(name='faces', draw=s7, sfx_fn=s7_sfx, lines=[
            ("Here's the wild part: in one study, famous faces were harder to recognize", 'Famous faces, HARDER to spot'),
            ('with the eyebrows erased than with the eyes erased.', 'without BROWS than without eyes')], tail=1.3),
        dict(name='outro', draw=s8, sfx_fn=s8_sfx, lines=[
            ('So eyebrows are rain gutters, and a second language.', 'GUTTERS and a second language'),
            ('Next: how fireflies glow.', 'Next: how FIREFLIES glow'),
            ('Follow for more science, explained simply.', 'Follow for more SCIENCE')], tail=2.0),
    ])
