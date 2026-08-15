# Monday Brief — canonical show spec

**This file is the single source of truth for HOW the show is made.**
Superseded 2026-08-07: merged from this file's previous contents and the
scheduled-task prompt, which had drifted apart on six points.

Tyler Dancy, Kannapolis NC (America/New_York). A personal weekly podcast,
listened to on a 6:00am Monday commute. Deliver a plain-text script. No audio
generation — `publish.py` does that.

`PODCAST_DIR` = `~/Library/Mobile Documents/com~apple~CloudDocs/Claude/JARVIS Podcast`

---

## PRECEDENCE — read this before anything else

Three files, three jobs. They must never overlap again.

| Question | Authority |
|---|---|
| **How** the show is made — segments, runtime, TTS, markers, sourcing, output | **This file** |
| **What** gets recommended — taste, exclusions, tiers, ledger, threads | `JARVIS Content Memory` Gmail draft |
| Question bank + refinement log | `podcast-preferences.md` |

The scheduled task at `~/Claude/Scheduled/monday-brief-podcast/SKILL.md` is a
thin pointer to this file and carries no rules of its own. If you are reading
rules there, they are stale — trust this file.

`episode-ledger.md` and the taste sections of `podcast-preferences.md` are
**historical archives**, retained as restore sources. Never read them for a
live decision.

---

## THE TWO-SURFACE CONTRACT

One research pass per week. The Brief owns it.

```
Sunday 5:04pm   Monday Brief (PRODUCER)
                reads memory, applies pending_marks, does the ONE research
                pass, writes week_picks, writes the script, writes memory back

Monday 5:54am   Weekly Queue (RENDERER)
                reads week_picks, renders with runtimes and feedback buttons,
                does the calendar review. Re-researches nothing.
```

An item can carry `surfaces: ["brief","queue"]` when it genuinely belongs to
both. That is reinforcement, not duplication; the Queue frames it as "heard it
Monday."

### THE VOLUME CAP — three picks a week, total

Set by Tyler 2026-08-07 and it governs BOTH surfaces combined.

| Slot | What | Sizing |
|---|---|---|
| **LISTEN** | one podcast episode | ≤27 min (one leg), or 50–55 (one full day) |
| **READ** | one book | audiobook competes with the listen slot — say so |
| **WATCH** | one film or TV season | evening or weekend |

That is the whole week. Not three per surface — three altogether.

**Why.** On 2026-08-07 Tyler reported he had not attempted a single one of the
four tracked picks from Aug 3–4. Not disliked: never started. That slate was
about 320 minutes of audio against a stated weekly budget of about 216, before
counting books and a four-part docuseries. The system was suggesting more than
he could consume, so most picks generated no signal at all. Ten unwatched
suggestions teach nothing; three finished ones teach everything.

Consequences, all of which are improvements:

- **No more "short list."** One watch pick, argued properly.
- **The catalog slot rotates through the three**, it is not a fourth item.
- **Music and YouTube are not standing slots.** They appear only when genuinely
  exceptional, and then they REPLACE one of the three rather than adding to it.
- **A Tier 2 subscription case may still name supporting titles**, because the
  billing-month argument needs them. Those are evidence for a decision, not
  picks: they get no button, no ledger entry, no slot.
- **Watch/Read/Listen keeps its full word budget**, so three picks get ~250
  words each instead of nine getting 80. "The fix is specificity, not volume"
  has been a stated preference since 2026-08-03; this is finally it.

If a week genuinely has four things worth his time, hold one for next week and
say so. A held pick is a stronger episode next Monday.

---

## OUTPUT ROUTING

**There is one episode format, and it is impersonal culture curation.**

Every episode goes to `PODCAST_DIR/scripts/`, which auto-publishes: a push there
triggers the GitHub Actions workflow, which narrates the script and pushes to
`github.com/jtdancy-jarvis/monday-brief` — a **public** repo serving a feed
claimed on Spotify. Everything written for the show is therefore written for
strangers.

No calendar segment. No inbox segment. No family names, travel dates, payday,
health, or account detail — not hedged, not abbreviated, not at all.

**Personal context lives on the Weekly Queue**, the Monday 5:54am artifact,
which is private to Tyler and is where the calendar review happens. If something
is worth saying but cannot be published, it belongs there, not in the script.

Filenames must contain the date: `monday-brief-YYYY-MM-DD.txt`, dated for the
**Monday it airs**. CI reads the date off the filename — a script without one
fails the run.

Two rules that outlive any format question, because audio outlives its context
and a passenger may be in the car:

- Never read account numbers or dollar balances aloud. Calendar titles sometimes
  embed amounts (there is a recurring "Outback $425"). Strip the figure, keep
  the event.
- Forward travel dates, and stretches when the house is empty, never go anywhere
  that publishes.

### Retired: the private episode format

Tyler answered the `private-hosting` question NO on 2026-08-11: public-only is
enough, no personal feed wanted. That closed the longest-running blocker in the
system and retired an entire second format — a `scripts-private/` folder holding
full personal episodes with a calendar segment and an inbox segment, which never
auto-published.

`scripts-private/` is **discontinued**. Do not write to it, do not restore the
second format, and do not treat the absence of a calendar segment as a gap to be
filled. The old two-column layout is in this file's git history if the decision
is ever reversed; it is deliberately not reproduced here, because two formats
described side by side is exactly how this file drifted the first time.

---

## RUNTIME — seasonal

Confirmed by Tyler 2026-08-07.

| Season | Words | Minutes at 150 wpm |
|---|---|---|
| **May–Oct** (offseason) | **1,500–2,000** | 10–13 |
| **Nov–Apr** (UNC basketball) | **2,100–2,700** | 14–18 |

Verify on the **stripped** text — markers otherwise inflate `wc -w`:

```
python3 -c "import sys;sys.path.insert(0,'.');import audio_post,pathlib;\
print(len(audio_post.strip_markers(pathlib.Path('SCRIPT').read_text()).split()))"
```

State the runtime in the cold open, computed from the FINAL count. Do not
estimate it before the script is done.

**TONE.** Calm and brisk. NPR morning-newscast register. Short declarative
sentences. No hype, no cheerleading. Dry wit in small doses. It is 6am and he
is driving.

---

## STRUCTURE

One layout. The words that used to go to a calendar and an inbox go to culture
and sports instead, which is why Watch/Read/Listen is the biggest segment in the
show by a wide margin.

| Segment | Offseason | In-season delta |
|---|---|---|
| 1. Cold open | 85 | — |
| 2. AI & tech | 150, often 0 | — |
| 3. Watch, read, listen | **750** | — |
| 4. Sports | **500** | → 950 |
| 5. Disney | 160 | — |
| 6. Two questions | 85 | — |
| 7. Sign-off | 55 | — |
| | **~1,785** | |

When a week is crowded, **Watch/Read/Listen grows first** — ahead of Sports,
Disney, and AI & tech. Confirmed by Tyler 2026-08-11. This matters once
in-season basketball starts pressuring the runtime in November.

### 1. COLD OPEN (~85)
"Good morning, Tyler. It's [Weekday], [Month] [day]." State the runtime.
Preview the biggest culture item, the biggest news story, and one sports item.
Hand off.

### 2. AI & TECH (~150, and often zero)
**Minimized.** Skip the segment entirely on an ordinary week rather than
filling it. When you skip it, say so in one line — it tells him the bar is
being applied, and it costs eight words.

Clears the bar: a real capability jump with verifiable evidence; a major safety
or security incident; regulation that actually binds; a chip or company move
that reshapes the market.

Does not clear it: incremental model releases, funding rounds, product updates,
benchmark scores, executive shuffles, anything an aggregator is excited about.
No week-ahead earnings or macro beat.

Sourcing, with a domain allowlist: company engineering and research blogs,
Reuters, Bloomberg, WSJ, Fortune, Ars Technica, TechTarget, MIT Technology
Review, Nature. Content farms garble details and occasionally invent whole
events. Verify every dramatic claim against a primary source. **Unconfirmed
means excluded, not hedged.** Attribute contested reporting out loud.

### 3. WATCH, READ, LISTEN (~750)
The centre of the show. **Three picks, no more** — see the volume cap above.
Taste is governed entirely by shared memory — read it, do not improvise from
this file.

With three picks and 750 words, each one gets about 250. Use them. Argue the
pick, name the comparison, flag the slow start, state the runtime and what it
fits. A pick that cannot justify 250 words is not strong enough to be one of
the three.

Four things this file does own:

- **Lead every film/TV pitch with register, not premise.** Tone is the gate he
  judges on first.
- **Lead every nonfiction pitch with shape** — the journey and the narrator —
  not the topic.
- **Name the specific episode, film, or book with a runtime.** Never a channel,
  never a series in the abstract.
- **Say the comparison out loud** when pitching against a known favourite, so
  the feedback mark is interpretable.

Close the segment with one line telling him the rest is on his Weekly Queue
page, with buttons to mark what landed.

### 4. SPORTS (~500; ~950 in-season)
**UNC men's basketball leads year-round**, with one standing exception: inside
three weeks of a football game, football leads. Basketball still gets its beat.

- In season: this week's games, opponents, tip times ET, channels. Last week in
  a sentence or two. Rotation, roster, injuries, ACC standings, national
  picture, and where the season stands as an arc.
- Offseason: roster moves, portal, staff, recruiting, program storylines.

Sourcing: goheels.com, 247Sports, On3, Inside Carolina, News & Observer, CBS
Sports, ESPN. **Never report recruiting rumor or coaching speculation as fact.**
Flag unconfirmed items and name who is reporting.

Then **golf**. Scope is set by shared memory and is narrower than it looks: in
are architecture, design, travel, destination. Out are player profiles and tour
personality pieces. Tournament results are news and belong here — but lead with
the ground, not the leaderboard, when there is anything to say about the course.

Then briefly UNC football, Carolina Panthers, Charlotte Hornets: day, time ET,
channel, one line on stakes. Out-of-season teams get a clause. Skip Charlotte FC
and NASCAR.

### 5. DISNEY (~160)
Standing segment. Rotate across parks news, new attractions, crowd calendars
and booking windows, Imagineering and design history, Pixar and animation,
notable company news. Sources: Disney Parks Blog, WDWNT, Blog Mickey,
Attractions Magazine, Laughing Place.

**Distinguish confirmed announcements from rumor** — the Disney fan press runs
on speculation and he will notice. Skip the segment rather than padding it.

### 6. TWO QUESTIONS (~85)
Exactly two, from the bank in `podcast-preferences.md`. Rotate categories, never
repeat within eight weeks — check the refinement log. Prefer questions that
close an OPEN thread in shared memory. Conversational. Say what each answer will
change, and tell him he can just tell Claude the answer.

### 7. SIGN-OFF (~55)
One sentence recapping concrete commitments plus any can't-miss event. Then
exactly: **"Have a good one, Tyler. See you next Monday."**

---

## TTS FORMATTING

The file goes straight into text-to-speech.

- Plain prose only. No markdown, headers, bullets, asterisks, or em-dashes.
  Periods and commas.
- **Spell every number as spoken.** "two hundred and fifty billion dollars,"
  "seven forty," "twenty-four and nine." No numerals survive.
- Expand titles: "Doctor Sumner." Keep known acronyms (AI, FBI, AMD, NBC, ACC,
  TCU, NCAA, NBA, A24, ESPN, PGA).
- Paragraph breaks are the pacing tool. A one-line paragraph reads as a beat.
- No URLs, no citations. Attribution spoken inline.

Two checks, both must come back empty:

```
grep -n '[—*#|]' <file>
grep -n '[0-9]'  <file>
```

### Pause and transition markers

`audio_post.py` implements these and they become real audio. They are stripped
before the text reaches the narrator, so they are never spoken.

Each on its own line, blank line either side.

- `[[TRANSITION]]` — a short music sting. **One before each major segment.**
  Never inside a segment.
- `[[PAUSE]]` — 0.55s. Before a line that should land. Two or three an episode.
  Overused, it sounds portentous.
- `[[BEAT]]` — 1.1s. A longer hold. Once an episode at most, usually before the
  sign-off.

**A script with zero markers narrates as one unbroken block.** That is a real
quality loss and it is the default failure — the 2026-08-10 episode shipped
that way. Confirm before finishing:

```
python3 -c "import sys;sys.path.insert(0,'.');import audio_post,pathlib;\
tl=audio_post.build_timeline(pathlib.Path('SCRIPT').read_text());\
print('non-speech blocks:', sum(1 for k,_ in tl if k!='speech'))"
```

Expect roughly six or seven — one sting per segment, plus a couple of holds.

### Emphasis

`tts-1` supports no SSML and no delivery control, so emphasis comes from the
writing. Short sentences land harder than long ones. A one-line paragraph after
a long one is the strongest emphasis available. Put the important word at the
end of the sentence. Never use capitals or italics for stress — the narrator
ignores them and the markdown stripper deletes them anyway.

`config.json` is currently on `gpt-4o-mini-tts` with an `instructions` string,
which does honour delivery direction. `publish.py` sends it only when present.

---

## MEMORY PROTOCOL

Full detail lives in the `_readme` of the `JARVIS Content Memory` Gmail draft.
The shape of a run:

1. **Load.** `list_drafts` with query `subject:"JARVIS Content Memory"` returns
   id and full body in one call. Strip `\r`, `JSON.parse`. Gmail rewrites bare
   URLs into `google.com/url?q=<real>` redirects — unwrap the `q` param on read,
   write them bare and expect it to happen again.
2. **If the body will not parse, STOP.** Do not overwrite it. Restore from the
   Weekly Queue artifact's mirror (`<script id="jarvis-memory-mirror">`), repair,
   and say so in chat. Never write a guessed object over memory.
3. **Apply `pending_marks`**, then set it to `[]`. UP +0.10 (ceiling 1.0), DOWN
   −0.15 (floor 0.2). Read the `why` on a DOWN and fix that reason across all
   picks. Downweight, never ban; retire a source only after three DOWNs with no
   UP since.
4. **Dedupe against `ledger`** — spans both surfaces. A source may recur; a
   specific title never repeats on either surface.
5. **Advance every OPEN and WAITING `thread`** — advance, close, or explicitly
   record no movement. Say when a check was not performed, rather than implying
   it was.
6. **Research once.** Size every audio pick: real runtime, legs = ceil(min/27).
   Prefer ≤27 min or 50–55. State a stopping point above 90.
7. **Write `week_picks`** — `{id, medium, subject, title, src, url, mins, slot,
   why, surfaces}`. `why` is reused verbatim by the Queue, so write it to be
   read as well as heard.
8. **Write memory back** with `update_draft` on the same id. Never create a
   second draft. Carry every key forward, preserve `_readme` and `_rule`
   verbatim. Then **re-apply the label** — `update_draft` moves the draft to a
   new thread and drops labels. `list_drafts` again for the new `threadId`, then
   `label_thread` with `["Label_32", "STARRED"]`.

---

## OUTPUT CHECKLIST

1. Save to `PODCAST_DIR/scripts/monday-brief-YYYY-MM-DD.txt`, dated for the
   Monday it airs. There is no second destination — see Output Routing.
2. Word count in range, on stripped text.
3. Both greps clean. Marker count in the expected range.
4. No dollar figures, account numbers, family names, travel dates or health
   detail anywhere in the script. It publishes to a public feed.
5. Confirm the file is on disk and non-empty. If `PODCAST_DIR` is unreachable
   (it is iCloud-synced and may not mount on a scheduled run), write to outputs,
   still update memory — Gmail is always reachable — and **say loudly in chat**
   that the script did not reach the publish folder.
6. Append a dated entry to the Refinement log in `podcast-preferences.md`
   recording the two questions asked.
7. `present_files` with the script path.
8. In chat, four lines: word count and runtime; the lead story; the two
   questions; confirmation the script landed and `week_picks` was written.

---

## CHANGELOG

**2026-08-17** — Collapsed to a single episode format. Tyler answered
`private-hosting` NO on 2026-08-11 (public-only is enough, no personal feed
wanted), which retired `scripts-private/` and the entire personal layout. This
file had gone on describing the impersonal format as *conditional* on that
thread being open — true by accident rather than by rule, and a trap for any
future run that noticed the thread was closed and concluded the condition no
longer applied.

Removed: the two-destination routing table, the public/private segment budget
columns, the "Your week" calendar and inbox segment, and the private-episode
variant of the cold open. Segments renumbered 1–7. The retired format is
recorded in one clearly-marked non-operative subsection and in git history,
rather than described alongside the live one — describing two formats side by
side is precisely what caused the drift this file was created to end.

Added: the 2026-08-11 answer that Watch/Read/Listen is the segment that grows
first when a week is crowded. Sharpened checklist item 4 from "no dollar
figures" to the full list of things that must never reach a public feed.

**2026-08-07** — Merged two contradicting skill files into this one. Resolved:
output routing (format follows destination, table above); offseason runtime to
1,500–2,000 and in-season to 2,100–2,700 per Tyler; continuity moved from
`episode-ledger.md` to shared memory; taste moved to shared memory; added the
two-surface contract; added separate public and private segment budgets, which
neither old file had. Fixed a dead pointer that sent the producer to
`podcast-preferences.md` for segment structure that only ever existed here.
Restored the audio-marker spec, which the scheduled task had dropped entirely —
the 2026-08-10 episode shipped with zero markers as a result.
