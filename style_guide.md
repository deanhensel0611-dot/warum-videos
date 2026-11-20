# Little Why Lab – Style Guide

Read before every new episode and apply it. The daily run updates this file (rules, the data behind them, change history).

## Core identity (never changes through optimisation)
- **Logo / key visual:** the sun (profile picture), shown without a face in the general-audience format.
- **Palette (max. 5):** sky blue `#2f9bff`, sun yellow `#ffd23f`, coral `#ff5c85`, navy `#1b2a4a`, white `#ffffff`. Topic colours (leaf green, ocean blue …) only as accents inside a scene.
- **Typography:** one typeface (Noto Sans CJK Black) for everything; key word in CAPS gets the yellow highlight.
- **Illustration style:** flat 2D vector, soft gradients, rounded shapes, no photos, no 3D, no style mixing within a video.
- **Signature sounds:** `ding` (soft two-tone) on the main "aha" moment of every episode, `chime` under the outro / follow button. Same in every video.

## Current rules (version 1 – 2026-11-17, starting point, no data yet)
| Parameter | Current rule | Basis |
|---|---|---|
| Hook | Question + surprising angle within the first 2 s | best practice, unverified |
| Pacing | Visual change every 2–4 s (new element, camera move, cut); scenes 6–10 s | best practice |
| Transitions | Cycled per scene: fade → slide → wipe → punch (no type more than 2× per video) | engine default |
| Captions | Word-by-word highlight, max ~7 words, caption zone y≈330–560 | best practice |
| Static shots | Never longer than 3 s without motion (camera push-in runs always; add movement inside the scene) | best practice |
| Sound | No music. sfx with a reason only: whoosh = movement/transition, pop/click = element appears, ding = aha, ambience bed per topic (wind/water/space/forest) very quiet | Dean's brief |
| Mix | Voice on top; sfx ≈ −13 dB, ambience ≈ −28 dB under voice; final loudness −14 LUFS | Dean's brief |
| Length | 60–75 s | Dean's brief |
| Ending | One-line recap + follow CTA; ideally a teaser for the next topic so it loops | best practice |

## Experiments (≈20 % of videos)
Maximum 1–2 parameters changed per day; each change is tested on at least 3 videos before it becomes a rule. Write active experiments here:
- **E1 – Cold open (since 2026-11-18, ep_017–019, 0/3 measured):** scene 1 starts already in motion (plane flying, ship floating, grass swaying – no build-up from an empty stage), voice starts at 0.1 s (`lead=0.1` instead of 0.35), a number or claim shows on stage within ~1 s. Goal: fix the early drop-off (TikTok avg. watch time only 2.5–10 s on 63–71 s videos). Judge on TikTok avg. watch time + YouTube avg. view % vs. ep_010–016.

## Findings from the data
Insights from fewer than 5 videos per feature are marked "uncertain". Separate style effects from topic and posting-time effects.
- 2026-11-18 (n=8 TikTok, 3 YouTube – all **uncertain**): TikTok videos with the old kids captions/hashtags (#scienceforkids #kidslearning, ep_003–007) got 67–76 views and only 2.5–4.6 s avg. watch time, 0 % full watches. The first two with general captions/hashtags (#science #learnontiktok, ep_012/013) got 359 / 135 views and 10.4 / 21.0 s avg. watch time. Confounded with posting time and video age (newer = less time to grow, so the gap may be bigger); the kid-format visuals were still the same. Fits Dean's switch to the general-audience format.
- The biggest leak on every video is the first seconds (avg. watch time ≤ 10 % of length on most TikToks) → hook is the priority lever (experiment E1).
- YouTube (n=3): avg. view percentage 47–58 % on the two Shorts with data – much better retention than TikTok; one Short (rainbow) has 0 views after 3 days (check audience/visibility setting).

- 2026-11-19 (n=11 TikTok, 3 YouTube): the caption/hashtag gap holds with more data – general captions (#science #learnontiktok, ep_008–013, n=6) 290–423 views and 8.0–20.0 s avg. watch vs. #kidslearning posts (ep_003–007, n=5) 68–77 views and 3.3–5.5 s. Now n≥5 on both sides → **likely real**, but still confounded with posting date (all general-caption posts came later). Kept as rule: general-audience captions/hashtags only.
- Within the general-caption group, avg. watch time splits in two: caterpillar 20.0 s and leaves 19.5 s vs. thunder 8.0 s, seasons 8.7 s, ice 9.5 s, fish 10.4 s. Both strong ones are nature/biology topics with a visible transformation – could be topic, not style (n=2 → **uncertain**).
- E1 (cold open) still has no data: ep_017–019 are not on TikTok yet and not in the YouTube data (0/3 measured).

- 2026-11-20 (n=11 TikTok – no new posts since 11-19; YouTube now n=9 Shorts): YouTube retention is steady at 47–64 % avg. view % (ice 64 %, rain 56 %, seasons 53 %, bees 51 %, ocean 50 %); only thunder is low (30 %, 6 views). Views split hard: autumn leaves 1,558, bees 1,252, ocean 1,184 vs. 1–118 for the other six – the three winners were all posted 11-15/11-17 and are older, so age + algorithm pickup confound it. Kids vs. general format makes no visible difference on YouTube (bees/ocean are kids format) – the format effect seen on TikTok is probably driven by captions/hashtags, not visuals (uncertain).
- Topic signal across both platforms: autumn leaves is top-3 on both; caterpillar (TikTok 19.5 s) and bees (YouTube 1,252 views, 5 subs) also lead → visible nature/biology transformations keep winning (n=4, **uncertain but repeating**). This is a topic effect, not a style rule – it only affects topic order, not the style guide.
- The rainbow Short still has 1 view after 5 days → very likely a settings/visibility problem (or "made for kids" limiting it), not a style signal; Dean should check it in YouTube Studio.

## Change history
- 2026-11-20: No style change (E1 still 0 measured videos – ep_017–022 are not in the TikTok/YouTube data yet). E1 cold open continued on ep_023–025. New lib props: flag (fixed droop geometry), wind_lines, thermometer, air_dots, bar_magnet (MAG_N/MAG_S colours), paperclip, compass, field_lines, spin_electron, domains, heart (plain infographic heart with 4-chamber cut-away, valves, electrical wave).
- 2026-11-19: No new style change (E1 still unmeasured). E1 cold open continued on ep_020–022. New lib props: co2_molecule, sugar_cubes, soil, root_paths, plant, stoma, onion, knife, cutting_board, gas_wisp, human_eye (plain, with tears), skin_section (hair follicles + arrector pili, goosebump bumps).
- 2026-11-18: Experiment E1 (cold open + voice at 0.1 s) started on ep_017–019. First episodes in the new general-audience look (faces=False, no kid character). New lib props: airplane, airfoil + streamlines, arrow, label_pill, water_body, tank, steel_block/bowl, ship (cargo/carrier, load-line marks), grass_field.
- 2026-11-17: Guide created. General-audience format (no faces), word-by-word captions, 4 transition types, signature sounds ding/chime, ambience beds, −14 LUFS.

## Daily reports
(newest on top, max. 10 lines each)

**2026-11-20** (data: 11 TikToks + 9 YouTube Shorts, last 14 days via Windsor.ai)
- Worked: YouTube holds viewers well – 47–64 % avg. view % on 8 of 9 Shorts; leaves (1,558), bees (1,252) and ocean (1,184 views, 2–5 subs each) took off.
- TikTok unchanged (no new posts): leaves 20.6 s / caterpillar 19.5 s avg. watch lead; general-caption posts 293–435 views vs. 68–77 for #kidslearning.
- Pattern on both platforms: nature/biology transformations (leaves, caterpillar, bees) lead – topic effect, not style (n=4, uncertain).
- Didn't work: thunder Short (30 %, 6 views); rainbow Short still 1 view – likely a visibility/audience setting, worth a check in YouTube Studio.
- Change today: none – E1 (cold open) still has 0 measured videos (ep_017–022 not in the data yet); continued on ep_023–025.
- Uncertain: pacing, transitions, sound, posting time (views confounded with video age). Tomorrow: measure E1 as soon as ep_017+ appear in the data.

**2026-11-19** (data: 11 TikToks + 3 YouTube Shorts, last 14 days via Windsor.ai)
- Worked: general captions/hashtags – 6 posts with 290–423 views and 8–20 s avg. watch vs. 68–77 views and 3–5 s for the 5 #kidslearning posts (now n≥5 each → likely real; posting date still confounded).
- Best watch time: caterpillar (20.0 s) and autumn leaves (19.5 s) – both biology topics with a visible transformation; possibly a topic effect (uncertain, n=2).
- Didn't work: the first seconds are still the leak – avg. watch is 6–30 % of the 61–69 s length on every TikTok; likes/comments/shares near zero (seasons: 13 likes, best so far).
- YouTube: no new data (still 3 Shorts; rainbow still 0 views). ep_017–019 not in the data yet.
- Change today: none – E1 (cold open, voice at 0.1 s) has 0/3 measured videos, so ep_020–022 continue it.
- Uncertain: pacing, transitions, sound, posting time. Tomorrow: measure E1 as soon as ep_017–019 have ≥48 h of TikTok data.

**2026-11-18** (data: 8 TikToks + 3 YouTube Shorts, last 14 days via Windsor.ai)
- Worked: general captions/hashtags – ep_012/013 on TikTok 135–359 views, 10–21 s avg. watch vs. 67–76 views and 2.5–4.6 s for the #kidslearning posts (n=2 vs 5 → uncertain; posting time + age confounded).
- Didn't work: the opening seconds – most TikTok viewers leave within 3–5 s; 0 % full watches on 6 of 8 videos. Likes/shares/saves near zero → no signal yet.
- YouTube holds viewers far better (47–58 % avg. view %), but the rainbow Short shows 0 views – worth checking its settings.
- Change today (1 parameter): E1 cold open – scene 1 already in motion, voice at 0.1 s, a number/claim on stage within 1 s (ep_017–019).
- Uncertain: everything about pacing, transitions, sound and topic – fewer than 5 videos per feature; posting-time effect not separable yet.
- Tomorrow: keep E1 for 3 more videos; once ep_017–019 have ≥48 h of data, compare their first-seconds retention with ep_010–016.
