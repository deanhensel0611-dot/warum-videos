# Little Why Lab – daily production

Animated 60–75 s vertical explainer shorts: **science explained simply, for a general audience (curious adults and teens; families welcome)** – NOT kid-directed (since 2026-11-18, Dean's decision; episodes 1–13 were the old kids format). In **English**, for **TikTok and YouTube Shorts only** (Instagram is not used).
Owner: Dean. He talks German – write all chat messages to him in **German**, the videos themselves in **English**.

## Daily run (what a scheduled run does)
0. **Style analysis first** (see "Daily style analysis" below), then read `style_guide.md` and apply it to today's episodes.
1. `bash setup.sh` (installs skia-python, kokoro-onnx, downloads the voice model into /tmp/kokoro).
2. Take the **first 3 open topics** from `topics.md`.
3. For each topic:
   - Fact-check the explanation with a web search before writing (kids must not learn wrong facts). Keep it simple but true; no invented facts.
   - Write `engine/episodes/ep_NNN_<slug>.py` (next free number) following `ep_001_why_is_the_sky_blue.py` as the reference for structure and quality.
   - `python3 engine/run.py ep_NNN_<slug> /tmp/out/ep_NNN preview` → look at the preview JPGs (Read tool). Fix overlapping text, elements in the caption zone, anything cut off or ugly.
   - **Quality pass (mandatory, before rendering)** – fix until every point holds:
     - Look: only the style_guide palette + accents, one illustration style, recurring props look identical in every scene.
     - Anti-slop: all text is real typography from `text_block`/captions; no scene that looks generic or interchangeable (redo it); no shot static for more than 3 s; no transition type more than twice (the engine cycles fade/slide/wipe/punch; override with `trans=` per scene if needed).
     - Rhythm: hook lands in the first 2 s; something visibly changes every 2–4 s; tempo varies; ending recaps and teases the next topic.
     - Sound: every sfx has a reason (whoosh = movement/transition, pop/click = element appears, `ding` = the one main aha moment, `chime` = outro). Set `ambience=` ('wind', 'water', 'space', 'forest') on the episode or per scene where it fits. No music.
     - Accuracy: every fact checked against a reliable source; nothing scary, no advertising.
   - Then `... render`.
   - Check the result: duration 60–90 s (`ffprobe`), loudness ≈ −14 LUFS (`ffmpeg -i video.mp4 -af ebur128 -f null -`), one frame from the middle looks right.
   - Copy the video to `/tmp/out/<Title_With_Underscores>.mp4` and send it to Dean with SendUserFile.
   - Also save it on Dean's Mac in `~/Video automatatiom` with `mcp__remote-devices__device_commit_files` (fileUuid from SendUserFile). If the folder is not connected yet, request it once with `device_request_folder_access`. If the Mac is offline, skip this and mention it in the summary.
4. Tick the topics off in `topics.md`, commit the new episode files + `topics.md` and push (no video files in git).
5. Send Dean ONE German message (SendUserMessage) with, per video: title, length, the 1-line fact summary, and ready-to-paste English texts for both platforms: **TikTok** caption with 4–5 hashtags; **YouTube** title (max 100 characters, ending with #shorts) plus a 1–2 sentence description. Posting times target the US audience: video 1 at 12:00, video 2 at 15:00, video 3 at 19:00 US Eastern time (America/New_York) on the day after the run; give Dean each time in Japan time too (he lives in Japan, UTC+9). End with: "Antworte mit ok, dann sind sie freigegeben – oder sag mir, welches raus soll."
6. **Never post or publish anything.** Posting only happens after Dean's explicit OK in chat.

## Daily style analysis (once per run, before producing)
Uses the Windsor.ai connector (`mcp__Windsor_ai_for_Social_Media__*`, connectors `tiktok_organic` and `youtube`; call `get_fields` before `get_data`). If the tools are missing or return no data, say so in the report and change nothing.
1. Fetch per video for the last 14 days: views, average watch time / watch-time share, completion rate, likes, comments, shares, saves, follower gain – whatever the connector offers; never invent numbers.
2. Tag each video with: hook type, pacing, caption style, transitions, sound set, ambience, topic, length, posting time, format (kids/general). Episode files hold most of this.
3. Compare the top 25 % with the bottom 25 % (priority: watch time + completion, then shares/saves, then likes). Fewer than 5 videos per feature → "uncertain". Separate style effects from topic and posting-time effects.
4. Change at most 1–2 style parameters per day; keep the core identity; test each change on ≥3 videos before it becomes a rule; keep ~20 % of videos as experiments.
5. Update `style_guide.md` (rules, data behind them, change history) and put a daily report of max. 10 lines at the top of its "Daily reports" section: what worked, what didn't, what changes tomorrow, what is still uncertain. Include the report in the German summary to Dean.

## Episode format (keep it consistent – it is the channel's brand)
- 7–8 scenes, 60–75 s total. Voice `af_heart`, no background music (`music=False`), sound design via sfx + quiet ambience only (see style_guide.md).
- Set `faces=False` in EPISODE (lib then draws no faces on sun, photons, molecules, …). Do NOT use `kid()` or other child characters. Visuals stay bright, clean and simple (diagram-like, infographic feel), but not cutesy: animals may keep natural eyes, but no blush cheeks, smiles or big cartoon eyes; props in lib that draw their own blush/smile get a `cute=` flag or a new plain variant.
- Tone: curious, friendly, conversational, like a good science YouTuber talking to adults. Simple words and everyday analogies are fine (“like a pinball machine”), baby talk is not (no “tiny, tiny bits”, no “Let's find out!”, never address the viewer as a child).
- Scene 1 hook: the question + a surprising angle, e.g. “Why does ice float? Almost every other frozen liquid sinks.”
- 4–5 explanation scenes, each ONE idea, with a concrete everyday analogy.
- 1 bonus fact scene that would surprise an adult (“Here's the wild part: …”).
- Outro: one-line recap + “Follow for more science, explained simply.” with the “+ Follow” button.
- Captions: max ~7 words, the key word in CAPS (CAPS words ≥3 letters get highlighted yellow). Caption zone is y≈330–560; keep the stage between y≈620 and y≈1580; keep important things away from the right 150 px and bottom 300 px (platform UI).
- Safe for all ages: nothing scary, gross-out, dangerous to imitate, or brand/character IP. No real people.
- TikTok captions/hashtags and YouTube texts: general audience (#science #funfacts #learnontiktok #explained …), no #kidslearning/#scienceforkids.

## Engine (engine/lib.py)
- Backgrounds: `sky`, `sunbeams`, `clouds`, `cloud`, `birds`, `hills(t=, trees=, dark=)`, `tree`, `dust`, `vignette` (auto).
- Characters: `sun`, `photon(vel=)`, `molecule`, `kid(wave=, helmet=)`, `face(mood='happy'|'wow')`.
- Sound: `sfx_fn` kinds 'pop', 'click', 'boing', 'whoosh', 'sparkle', 'ding' (signature aha), 'chime' (signature outro); `ambience=` on EPISODE or scene: 'wind', 'water', 'space', 'forest'. Caption pops are automatic; final mix is loudness-normalised to −14 LUFS.
- Transitions: automatic cycle fade/slide/wipe/punch; per scene override `trans='fade'|'slide'|'wipe'|'punch'`. Captions highlight word by word automatically.
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
4. Audience: for new-format episodes (`faces=False`) click `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]` (comments allowed); for old kid-format episodes (1–13) keep `VIDEO_MADE_FOR_KIDS_MFK`. Then `#next-button` 3×.
5. Schedule: click `#second-container-expand-button`; date: click `#datepicker-trigger`, then click the `ytcp-date-picker span.calendar-day` for the wanted day (`.today` = today; typing into the date input does not stick); for the time focus+click the `ytcp-visibility-scheduler tp-yt-paper-input input`, then click the `tp-yt-paper-item` whose text is the time (setting the input value directly does NOT stick). Browser time zone is Asia/Tokyo. Target 12:00/15:00/19:00 America/New_York; convert with Python zoneinfo every time (DST changes!). In US winter time that is 02:00/05:00/09:00 JST, all on the day after the US date. Then `#done-button`. Verify the confirmation text shows the right time. Afterwards check all uploads at `…/videos/short` (title, description) and on each `/video/<id>/edit` page that the audience setting matches the episode format; fix there and click `ytcp-button#save`.
6. TikTok cannot be automated (its CSP blocks loading the file, and sounds can only be added in the app): send Dean the TikTok captions; he posts from the phone app with a trending sound at ~5–10 % volume.
7. After upload, delete the videos from littlewhylab-media again (git rm + push).
