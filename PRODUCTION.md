# Weekly reel production (Kobi + Dari)

Goal: 1 reel per day per account until launch (25 Nov 2026), built to win new followers.
Everything in English. Max 5 hashtags. Every caption ends with "<App> launches 25 Nov. Waitlist in bio." before the hashtags.

## Series (rotate, never two identical formats on consecutive days)
Kobi (@kobiapp.cc, voice af_heart, theme mint/navy):
- Myth or Fact (template `myth`, id `k_mfNN`): scenes myth → verdict → explain → rule → end
- Skin Quiz (`quiz`, `k_qzNN`): question → count → answer → end
- Read the Label (`word`, `k_rlNN`): a Korean label word (진정, 미백, 저자극, 보습, 각질…)
- Ingredient Explained (micro.html, `k_ieNN`, render with render_micro.py, cfg {sym,name,num,tag,chips,next,red})
Dari (@dariapp.cc, voice am_michael, theme gold/navy):
- Myth or Fact: Korea (`d_mfNN`), Korea Quiz (`d_qzNN`), Say it in Korean (`d_skNN`)

Copy the newest file of the same series in `content/episodes/` as the model (fields per scene, caption shape).
Facts must be accurate and safe; no medical claims. Viral levers: a hook that challenges a belief in the first
second, one idea, a share/save/comment CTA ("Send this to…", "Comment below", "Save this"), series numbering.

## Steps
1. Write 7 new episodes per account for the next week (`content/episodes/<id>.json`, `"id"` field included).
2. Commit + push, then dispatch voices:
   `gh api -X POST repos/raphhalimi-stack/kobi-dari-slides/actions/workflows/tts.yml/dispatches -f ref=main -f 'inputs[script]=engine/tts_ep.py'`
   Wait for the run to finish, `git pull` (audio/episodes/<id>/durations.json appears).
3. Render: `python3 engine/render_series.py <ids…>` and `python3 engine/render_micro.py <k_ie id>` (needs Playwright Chromium, ffmpeg, numpy).
4. QA: extract frames with ffmpeg, check no overflow / overlap / tofu glyphs.
5. Queue: `python3 build_week.py <first-date> kobi:<7 ids> dari:<7 ids>` (first-date = day after the last queued reel).
6. Commit + push (videos + queue.json). publish.yml posts automatically (Kobi 19:00 KST, Dari 19:30 KST).
7. Check `state2.json` for errors on already-due items; if an item failed 3× (errors), investigate.

Never print or read tokens/secrets. Never delete or archive posts. No follow/like automation.
