# Why-Videos for kids – daily production

Animated 60–75 s vertical (1080x1920, 60 fps) explainer shorts for kids (about 5–10 years old), in **English**, for **TikTok and YouTube Shorts only** (Instagram is not used).
Owner: Dean. He talks German – write all chat messages to him in **German**, the videos themselves in **English**.

## Daily run (what a scheduled run does)
1. `bash setup.sh` (installs skia-python, kokoro-onnx, downloads the voice model into /tmp/kokoro).
2. Take the **first 3 open topics** from `topics.md`.
3. For each topic:
   - Fact-check the explanation with a web search before writing (kids must not learn wrong facts). Keep it simple but true; no invented facts.
   - Write `engine/episodes/ep_NNN_<slug>.py` (next free number) following `ep_001_why_is_the_sky_blue.py` as the reference for structure and quality.
   - `python3 engine/run.py ep_NNN_<slug> /tmp/out/ep_NNN preview` → look at the preview JPGs (Read tool). Fix overlapping text, elements in the caption zone, anything cut off or ugly. Then `... render`.
   - Check the result: duration 60–90 s (`ffprobe`), one frame from the middle looks right.
   - Copy the video to `/tmp/out/<Title_With_Underscores>.mp4` and send it to Dean with SendUserFile.
4. Tick the topics off in `topics.md`, commit the new episode files + `topics.md` and push (no video files in git).
5. Send Dean ONE German message (SendUserMessage) with, per video: title, length, the 1-line fact summary, and ready-to-paste English texts for both platforms: **TikTok** caption with 4–5 hashtags; **YouTube** title (max 100 characters, ending with #shorts) plus a 1–2 sentence description. Suggested posting times: video 1 at 7:00, video 2 at 13:00, video 3 at 17:00 German time. End with: "Antworte mit ok, dann sind sie freigegeben – oder sag mir, welches raus soll."
6. **Never post or publish anything.** Posting only happens after Dean's explicit OK in chat.

## Episode format (keep it consistent – it is the channel's brand)
- 7–8 scenes, 60–75 s total. Voice `af_heart`, no background music (`music=False`), sfx only.
- Scene 1 hook: the question itself + "Let's find out!".
- 4–5 explanation scenes, each ONE idea, with a concrete kid analogy (pinball, slide, sponge …). Characters are cute with faces (sun, light balls, molecules, kid).
- 1 bonus "And guess what?" fact scene.
- Outro: "Now you know!" / "Can you explain it to a grown-up?" / "Follow for more why questions!" with the "+ Follow" button.
- Captions: max ~7 words, the key word in CAPS (CAPS words ≥3 letters get highlighted yellow). Caption zone is y≈330–560; keep the stage between y≈620 and y≈1580; keep important things away from the right 150 px and bottom 300 px (platform UI).
- Kid-safe only: nothing scary, gross-out, dangerous to imitate, or brand/character IP. No real people.

## Engine (engine/lib.py)
- Backgrounds: `sky`, `sunbeams`, `clouds`, `cloud`, `birds`, `hills(t=, trees=, dark=)`, `tree`, `dust`, `vignette` (auto).
- Characters: `sun`, `photon(vel=)`, `molecule`, `kid(wave=, helmet=)`, `face(mood='happy'|'wow')`.
- Helpers: `col`, `P(color, stroke, blur)`, `lin`, `rad`, `ease_out/ease_in_out/ease_back`, `prog(t, start, dur)`, `text_block`.
- A scene = `dict(name, draw=fn(c,t,D,cues), lines=[(spoken, caption)], sfx_fn=fn(D,cues)->[(t,'pop'|'boing'|'whoosh'|'sparkle')], tail=sec)`. `cues[i]['start']` is when line i is spoken – time animations to it.
- New characters/props are welcome – add reusable ones to lib.py so later episodes can use them.
- The engine handles voice (Kokoro), captions, crossfades, slow camera push-in and rendering.
