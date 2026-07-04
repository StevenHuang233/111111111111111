# Non-Code Text and Configuration Review Draft (English)

This document organizes the current non-code text that affects model behavior, user configuration, and output structure in the football commentary harness. Runtime configuration mainly comes from `configs/styles.json`, `configs/event_types.json`, `harness/scanner.py`, `harness/commentary.py`, and `harness/bilingual.py`.

## 1. Review Scope

- Style text: style names, descriptions, prompt injections, and generation hyperparameters.
- Event type text: event IDs, names, descriptions, positive cues, and negative cues.
- Scan prompt: instructions sent to the model for low-frame-rate event scanning.
- Repair prompt: instructions used when the model returns invalid JSON or unsupported event types.
- Commentary prompt: instructions used to generate commentary from structured event data and selected keyframes.
- Bilingual translation prompt: instructions used to translate English commentary into Chinese while preserving meaning and style.
- Manual configuration parameters: manifest format, sliding-window parameters, style parameters, event type parameters, and output fields.
- Step tracing: records how the pipeline moves across modules and what each step calls.

## 2. Style Profiles

### broadcast_professional

- Intended use: stable, accurate, TV-style football commentary.
- Current parameters: `temperature=0.35`, `top_p=0.9`, `max_tokens=1200`, `thinking_mode=false`.
- Current prompt injection:

```text
Use a professional broadcast tone. Be accurate, concise, and smooth. Mention visible evidence and match context without exaggeration. Keep emotion controlled except for decisive moments.
```

### short_passionate

- Intended use: highlight clips, short-form video, and social media.
- Current parameters: `temperature=0.65`, `top_p=0.95`, `max_tokens=900`, `thinking_mode=false`.
- Current prompt injection:

```text
Use a high-energy short-video tone. Sentences should be punchy, vivid, and rhythmic. Highlight dramatic moments quickly. Do not invent facts; make the visible action feel exciting.
```

### tactical_analysis

- Intended use: post-match analysis, tactical review, and explainable commentary.
- Current parameters: `temperature=0.25`, `top_p=0.85`, `max_tokens=1400`, `thinking_mode=false`.
- Current prompt injection:

```text
Use a tactical analyst tone. Focus on spacing, transitions, defensive shape, passing lanes, pressure, and decision-making. Keep emotion secondary to explanation.
```

## 3. Event Types and Decision Descriptions

All event types are configured in `configs/event_types.json`. The scanner can only return these IDs; unsupported IDs trigger one repair attempt or a window error.

### goal

- Name: Goal
- Description: The ball appears to cross the goal line, the scoreboard changes, or players clearly celebrate a scored goal.
- Positive cues: ball inside or behind the net; goalkeeper beaten; players running away celebrating; scoreboard increment; replay of a finish.
- Negative cues: ordinary shot before the result is known; near miss; save followed by no clear celebration.

### shot

- Name: Shot
- Description: A player attempts to score by striking, heading, or redirecting the ball toward goal, but the frame does not prove it became a goal.
- Positive cues: shooting body shape; ball traveling toward goal; header at goal; defenders or goalkeeper reacting to a shot.
- Negative cues: simple pass or cross; goal already confirmed; general possession far from goal.

### save

- Name: Save
- Description: The goalkeeper or a defender prevents a likely goal or blocks a clear shot near the goal.
- Positive cues: goalkeeper diving or stretching; ball stopped near goal; defensive block on the goal line; rebound after goalkeeper contact.
- Negative cues: routine catch with no pressure; shot wide without contact; goal scored.

### dangerous_attack

- Name: Dangerous Attack
- Description: An attacking team is in or near the final third with a promising chance, but no specific shot, goal, set piece, or foul is clearly shown.
- Positive cues: fast break; attacker entering penalty area; overload near box; through ball behind defense; cross into a crowded area.
- Negative cues: slow buildup in midfield; dead-ball restart; confirmed shot or goal.

### corner

- Name: Corner Kick
- Description: A corner kick is being taken, prepared, or replayed.
- Positive cues: ball placed near corner flag; players gathered in penalty area for a corner; corner flag visible during restart.
- Negative cues: open-play cross from near the corner; throw-in; free kick from wide area.

### free_kick

- Name: Free Kick
- Description: A free kick restart is being prepared or taken outside the penalty spot context.
- Positive cues: stationary ball after foul; defensive wall; referee managing restart; free-kick taker standing over ball.
- Negative cues: corner kick; penalty kick; normal open-play pass.

### penalty

- Name: Penalty
- Description: A penalty kick is awarded, prepared, taken, saved, or scored.
- Positive cues: ball on penalty spot; single taker facing goalkeeper; players outside penalty area; referee penalty signal.
- Negative cues: free kick outside the box; open-play shot; corner kick.

### foul

- Name: Foul
- Description: Illegal physical contact, a trip, push, handball, or another stoppage-causing infringement is visible or strongly indicated.
- Positive cues: player falling after contact; referee whistle or gesture; players protesting; tackle through opponent.
- Negative cues: normal shoulder challenge; player slipping alone; card shown without visible foul context.

### card

- Name: Card
- Description: The referee shows or is clearly about to show a yellow or red card.
- Positive cues: yellow card visible; red card visible; referee holding card above head; player disciplinary reaction.
- Negative cues: ordinary foul with no card shown; substitution board; score graphic.

### substitution

- Name: Substitution
- Description: A player substitution is happening or clearly displayed.
- Positive cues: substitution board; player entering or leaving touchline; broadcast substitution graphic; coaches greeting player.
- Negative cues: injury treatment without player replacement; player warming up only.

### var_review

- Name: VAR Review
- Description: A VAR review, referee monitor check, or broadcast VAR decision sequence is visible.
- Positive cues: VAR graphic; referee at pitchside monitor; check complete or decision graphic; players waiting during review.
- Negative cues: normal replay without review context; ordinary referee discussion.

### celebration_or_replay

- Name: Celebration Or Replay
- Description: A celebration, emotional reaction, or replay of an important moment is shown when the exact live event type is not clear.
- Positive cues: players celebrating together; crowd celebration; slow-motion replay angle; close-up emotional reaction.
- Negative cues: active live attack with clear event type; routine crowd shot unrelated to play.

### period_transition

- Name: Period Transition
- Description: Kickoff, halftime, full-time, restart after halftime, or another major match-period transition is shown.
- Positive cues: players lined up for kickoff; referee starting or ending half; halftime or full-time graphic; teams leaving or entering pitch.
- Negative cues: ordinary restart after foul; random midfield possession.

### other_relevant

- Name: Other Relevant
- Description: A clearly commentary-worthy football moment that does not fit any other configured event type.
- Positive cues: injury treatment; major tactical instruction; unusual broadcast graphic; important crowd or bench reaction.
- Negative cues: ordinary possession; unclear frame; low-information scene.

### no_event

- Name: No Event
- Description: No commentary-worthy football event is visible in the frame.
- Positive cues: ordinary buildup; static midfield possession; unclear or low-information frame; broadcast shot with no significant action.
- Negative cues: clear goal; clear shot; clear set piece; visible card or substitution.

## 4. Scan Prompt Template

This prompt is used for low-frame-rate sliding-window scanning.

```text
You are a football video event scanner.

Style context for salience only:
{style.prompt_injection}

Allowed event_type values:
{allowed_types}

Event definitions and decision cues:
{event_reference}

For each frame, decide whether it contains a moment that needs commentary.
The event_type must be exactly one allowed value. Use no_event when nothing important is visible.

Frame time prefixes:
{prefixes}

Return JSON only with this schema:
{
  "frames": [
    {
      "frame_id": "same frame_id",
      "needs_commentary": true,
      "event_type": "goal",
      "confidence": 0.0,
      "evidence": "short visual evidence"
    }
  ]
}
```

## 5. Repair Prompt Template

This prompt is used once when the scanner output has invalid JSON, an unknown event type, or an unknown frame ID.

```text
Fix this football event scan response into valid JSON.
Error: {error}
Allowed event_type values: {event_types}
Event definitions and decision cues:
{event_reference}
Required frame_ids: {frame_ids}

Bad response:
{bad_text}

Return JSON only with the same schema:
{"frames":[{"frame_id":"...","needs_commentary":false,"event_type":"no_event","confidence":0.0,"evidence":"..."}]}
```

## 6. Commentary Generation Prompt Template

This prompt generates commentary for one detected event interval.

```text
You are generating football commentary for one detected event.

Use this style exactly:
{style.prompt_injection}

The narration must fit from {start_time} to {end_time}.
Do not invent player names, teams, scores, or facts that are not present in the event evidence.

Event data:
{event_json}

Return JSON only:
{
  "commentary_text": "spoken commentary text",
  "subtitle_lines": [
    {"start_sec": 0.0, "end_sec": 2.0, "text": "subtitle text"}
  ]
}
```

## 7. Configuration Parameters to Review

### Bilingual translation prompt template

This prompt translates English commentary into Chinese. Runtime calls it once per event segment.

```text
You are translating football commentary from English into Simplified Chinese.

Meaning fidelity is the first priority. Preserve the exact factual meaning, timing, numbers, names, teams, score references, and uncertainty.
Apply this commentary style only after preserving meaning:
{style.prompt_injection}

Translation rules:
- Do not add facts, player names, team names, scores, or tactical details that are not in the English source.
- Keep the same event_id, event_type, talk_start_sec, talk_end_sec, and subtitle timing.
- Translate naturally for spoken football commentary in Simplified Chinese.
- If style and meaning conflict, choose meaning.
- Return JSON only.

English source:
{source_json}

Return JSON only:
{
  "commentary_text": "Chinese spoken commentary text",
  "subtitle_lines": [
    {"start_sec": 0.0, "end_sec": 2.0, "text": "Chinese subtitle text"}
  ]
}
```

### Environment variables

| Parameter | Default | Purpose | Review suggestion |
|---|---|---|---|
| `INTERN_API_KEY` | none | Intern-S2-Preview API key | Required |
| `INTERN_BASE_URL` | `https://chat.intern-ai.org.cn/api/v1` | API base URL | Usually keep |
| `INTERN_MODEL` | `intern-s2-preview` | Model name | Usually keep |

### Style parameters

| Parameter | Meaning | Review suggestion |
|---|---|---|
| `style_id` | Unique style identifier | Use lowercase English plus underscores |
| `description` | Human-readable style description | Can be maintained bilingually |
| `prompt_injection` | Actual style-control text injected into model prompts | Highest-priority review item |
| `temperature` | Randomness and creativity | Higher for short video, lower for tactical analysis |
| `top_p` | Sampling nucleus | Usually 0.85 to 0.95 |
| `max_tokens` | Output budget per request | Increase for longer commentary |
| `thinking_mode` | Deep-thinking mode | Currently false to avoid leaking reasoning into outputs |

### Scan parameters

| Parameter | Default | Purpose | Tuning guidance |
|---|---:|---|---|
| `window_size_frames` | 6 | Number of frames read per model call | Larger reduces calls but roughens boundaries |
| `stride_frames` | 3 | How far the window moves per step | Smaller is more stable but costs more calls |
| `repair_attempts` | 1 | Number of repair attempts for invalid outputs | Usually 1 is enough |
| `event_types_path` | `None` | Custom event type config path | Use when adding a custom taxonomy |
| `merge_gap_sec` | 4.0 | Maximum gap for merging same-type event candidates | Handles one event split by sliding windows |
| `goal_replay_merge_gap_sec` | 30.0 | Maximum gap for merging a goal with nearby celebration/replay | Enables dual goal-plus-replay commentary |
| `dense_sample_fps` | 1.0 | Dense per-event manifest sampling rate used by the full runner | Reduces 4fps source frames to 1fps before dense scanning |

### Manifest fields

| Field | Type | Purpose |
|---|---|---|
| `video_id` | string | Unique video identifier |
| `source_video` | string | Original video filename or source |
| `frames[].frame_id` | string | Unique frame ID |
| `frames[].path` | string | Frame image path; relative paths resolve against the manifest directory |
| `frames[].timestamp_sec` | number | Frame timestamp in video seconds |

### Output fields

| Output | Key fields | Purpose |
|---|---|---|
| `events.json` | `event_id/event_type/start_sec/end_sec/evidence_frames/confidence/evidence_summary/phases` | Event evidence chain |
| `commentary.json` | `event_id/talk_start_sec/talk_end_sec/commentary_text/subtitle_lines` | Commentary and subtitle candidates |
| `commentary_bilingual.json` | `event_id/english/commentary_text/chinese/commentary_text/subtitle_lines` | English and Chinese commentary and subtitle candidates |
| `trace.json` | `index/elapsed_sec/step/action/detail` | Step trace and module transition log |

When `TraceRecorder(record_model_io=True)` is used, `trace.json` also records each model call:

- `model_call_input`: prompt text, frame IDs, timestamps, and local image paths.
- `model_call_output`: raw model text output.

Image base64 payloads are not written to trace files. Local image paths are recorded instead to keep logs reviewable.

### Visual commentary generation parameters

The default pipeline and `generate_commentary()` now use visual commentary generation: the model receives structured event data, `evidence_summary`, `phases`, and sampled keyframes from the event interval and each phase interval, with evidence frames prioritized.

| Parameter | Default | Purpose |
|---|---:|---|
| `max_frames_per_event` | 12 | Maximum images sent to the commentary model for one event |
| `max_frames_per_phase` | 4 | Maximum representative frames sampled from each phase |
| `context_frames_each_side` | 1 | Neighboring frames sampled on each side for visual context without widening the event interval |
| `sample_fps` | 0.5 | Visual frame sampling rate for commentary generation |

The previous summary-only generation path is still available as `generate_commentary_from_summary()`.

### Bilingual commentary parameters

The bilingual module first generates English commentary with visual frames, then translates each segment into Chinese. You can also call `translate_commentary_to_chinese()` on an existing English `CommentaryResult`.

| Parameter | Default | Purpose |
|---|---:|---|
| `target_language` | `Simplified Chinese` | Target language name injected into the translation prompt |
| `target_language_code` | `zh-CN` | Target language code in output metadata |
| `temperature` | 0.2 | Translation randomness; low by default for meaning fidelity |
| `top_p` | 0.9 | Sampling nucleus |
| `max_tokens` | 1600 | Output budget per event translation |
| `thinking_mode` | `false` | Disabled by default to avoid reasoning leakage |

Bilingual output keeps both languages under each event segment:

```json
{
  "event_id": "E001",
  "event_type": "goal",
  "english": {"commentary_text": "...", "subtitle_lines": []},
  "chinese": {"commentary_text": "...", "subtitle_lines": []}
}
```

### Composite event phases

A `goal` event can now contain multiple phases:

```json
{
  "event_type": "goal",
  "phases": [
    {"phase_type": "live_goal", "start_sec": 80.0, "end_sec": 92.0},
    {"phase_type": "replay", "start_sec": 96.0, "end_sec": 116.0}
  ]
}
```

When commentary generation sees a `goal` with both `live_goal` and `replay`, it asks the model to first describe the live goal moment, then use the replay phase for details such as shooting route, passing, positioning, defensive issues, and goalkeeper reaction when visible.

## 8. Suggested Review Focus

- Whether the event taxonomy is sufficient: consider adding `offside`, `injury`, `kickoff`, `goal_kick`, or `throw_in`.
- Whether `goal` and `celebration_or_replay` should be more strictly separated.
- Whether the boundary between `shot` and `dangerous_attack` matches your expectations.
- Whether the three built-in styles are enough for the demo; possible additions include formal CCTV-style, fan-made Bilibili style, or a named commentator-inspired style.
- Whether the default scan config `6/3` fits your frame interval. If frames are sampled every 2 seconds, the default window covers about 12 seconds and advances about 6 seconds per step.
