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
- Helpers: `trail(c, points, hexcol, width)` (use this lib version for motion trails, no local copy), `col`, `P(color, stroke, blur)`, `lin`, `rad`, `ease_out/ease_in_out/ease_back`, `prog(t, start, dur)`, `text_block`.
- A scene = `dict(name, draw=fn(c,t,D,cues), lines=[(spoken, caption)], sfx_fn=fn(D,cues)->[(t,'pop'|'boing'|'whoosh'|'sparkle')], tail=sec)`. `cues[i]['start']` is when line i is spoken – time animations to it.
- New characters/props are welcome – add reusable ones to lib.py so later episodes can use them.
- The engine handles voice (Kokoro), captions, crossfades, slow camera push-in and rendering.
- **Quality bar (Dean's explicit wish): very high quality.** Output is rendered supersampled at 1440x2560, 60 fps, x264 CRF 16 preset medium – do not lower these. Draw detailed, smooth, anti-aliased art; zoom into preview frames at full size and fix anything jagged, blurry, beaded or cheap-looking before rendering.

## Posting after Dean's "ok" (YouTube automated, TikTok by Dean)
Only after Dean answers "ok" in chat. Needs his Mac on with the Claude desktop app open (built-in browser, `mcp__remote-devices__Claude_Browser__*`; signed in to YouTube Studio, channel UC3LqzSWi2dBYFOyedYj62QA). The pane is usually hidden, so clicks fail – do everything with `javascript_tool`.
1. Push the videos to the PUBLIC repo `deanhensel0611-dot/littlewhylab-media` as `v/<slug>.mp4` (attach with add_repo, push access). Raw URL: `https://raw.githubusercontent.com/deanhensel0611-dot/littlewhylab-media/main/v/<slug>.mp4`.
2. Per video in YouTube Studio: open `https://studio.youtube.com/channel/UC3LqzSWi2dBYFOyedYj62QA/videos/upload?d=ud`; in JS fetch the raw URL → `new File([...])` → `DataTransfer` → set `input[type=file]`.files + dispatch `change`.
3. Title/description: wait until `ytcp-uploads-dialog #textbox[contenteditable=true]` [0]/[1] exist, then wait 3 s more (YouTube fills the title from the file name and would overwrite yours), then focus, `execCommand('selectAll')`, `execCommand('insertText', …)`. Keep each javascript_tool call under ~40 s (split steps).
4. Click `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"]`, then `#next-button` 3×.
5. Schedule: click `#second-container-expand-button`; date: click `#datepicker-trigger`, then click the `ytcp-date-picker span.calendar-day` for the wanted day (`.today` = today; typing into the date input does not stick); for the time focus+click the `ytcp-visibility-scheduler tp-yt-paper-input input`, then click the `tp-yt-paper-item` whose text is the time (setting the input value directly does NOT stick). Browser time zone is Asia/Tokyo: 7:00/13:00/17:00 Berlin = 15:00/21:00/01:00(+1 day) JST in winter. Then `#done-button`. Verify the confirmation text shows the right time. Afterwards check all uploads at `…/videos/short` (title, description) and on each `/video/<id>/edit` page that "made for kids" is checked; fix there and click `ytcp-button#save`.
6. TikTok cannot be automated (its CSP blocks loading the file, and sounds can only be added in the app): send Dean the TikTok captions; he posts from the phone app with a trending sound at ~5–10 % volume.
7. After upload, delete the videos from littlewhylab-media again (git rm + push).
