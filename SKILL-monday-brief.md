# Monday Brief — canonical show spec

**This file is the single source of truth for HOW the show is made.**

Restructured 2026-09-15, at Tyler's direction: the podcast is now an
appointments-shape-plus-news recap only. Culture picks (watch/read/listen)
moved out entirely, to a weekly email — see `_moved_to_weekly_queue` below.
Superseded the 2026-08-07 merge, which had this show carrying the picks.

Tyler Dancy, Kannapolis NC (America/New_York). A personal weekly show,
listened to on a 6:00am Monday commute. Deliver a plain-text script. No audio
generation — `publish.py` does that.

`PODCAST_DIR` = `~/Library/Mobile Documents/com~apple~CloudDocs/Claude/JARVIS Podcast`

---

## PRECEDENCE — read this before anything else

| Question | Authority |
|---|---|
| **How** the show is made — segments, runtime, TTS, markers, sourcing, output | **This file** |
| Sports, AI/tech and Disney sourcing detail, question bank, refinement log | `podcast-preferences.md` |
| Suggestions (watch/read/listen), taste, the weekly email | The `weekly-queue` scheduled task and the `JARVIS Content Memory` Gmail draft — **not this file, not this show** |

The scheduled task at `~/Claude/Scheduled/monday-brief-podcast/SKILL.md` is a
thin pointer to this file and carries no rules of its own. If you are reading
rules there, they are stale — trust this file.

---

## `_moved_to_weekly_queue` — what left this show and why

Until 2026-09-14, this show carried a Watch/Read/Listen segment (three picks,
~750 words) and closed with two taste-calibration questions. Both are gone.

**Why.** Tyler asked to reformat the show to be an appointments-and-news
recap only, with the recommendation content moved to a weekly email instead.
Two things made this the right split rather than just a preference:

1. **The show is public.** `scripts/` auto-publishes to a Spotify feed on a
   public GitHub repo. Suggestions never needed to be public — they were
   here because the show was the only delivery surface that existed yet.
   An email is a cleaner fit for content that is inherently personal-taste
   and needed private, so it can talk like it, and it never has to be
   filtered for a stranger's ears.
2. **It decouples this show from the JARVIS Content Memory entirely.** That
   memory object has had a live, unresolved size-ceiling problem for
   weeks (see `podcast-preferences.md`'s refinement log, September 2026)
   that has repeatedly blocked writes. This show no longer reads or writes
   that memory at all — it has no `week_picks`, no taste rules, no ledger,
   no research pass. One less thing for that ceiling to break.

The recommendation engine — taste rules, exclusions, streaming tiers,
subjects, the ledger, the volume cap, the two taste-calibration questions —
now lives entirely under the `weekly-queue` scheduled task
(`~/Claude/Scheduled/weekly-queue/SKILL.md`), which researches, emails Tyler
directly, and renders the interactive artifact with feedback buttons. If you
are working on picks, taste, or the email, you are in the wrong file — go
there instead.

---

## OUTPUT ROUTING AND THE TWO RULES THAT COME FIRST

**There is one format, and the show is still public.** Every episode goes to
`PODCAST_DIR/scripts/`, which auto-publishes: a push there triggers GitHub
Actions, which narrates the script and pushes to
`github.com/jtdancy-jarvis/monday-brief` — a **public** repo serving a feed
claimed on Spotify. Everything written for the show is written for strangers,
including the new appointments segment.

Two rules outlive any format question, because audio outlives its context and
a passenger may be in the car, and because this is now the rule that keeps
Tyler's calendar off a public feed:

- **Never read account numbers, dollar balances, health or medical detail,
  or family names, on air, ever.** Not hedged, not abbreviated, not at all.
- **Never say or imply that Tyler is traveling, about to travel, or that the
  house will be or is empty.** This is the single most important rule in
  this file. See "THIS WEEK AHEAD" below for exactly how the appointments
  segment enforces it — when in doubt, that segment skips itself rather than
  risk it, the same way AI & Tech already skips itself when nothing clears
  its bar.

Filenames must contain the date: `monday-brief-YYYY-MM-DD.txt`, dated for the
**Monday it airs**. CI reads the date off the filename — a script without one
fails the run.

`scripts-private/` remains discontinued from the prior format. Do not write
to it, do not restore a second format, and do not treat the new, franker
appointments segment as a reason to reconsider that — this segment is
deliberately built to be safe for a public feed, not an excuse to loosen the
feed's privacy bar.

---

## RUNTIME — seasonal

Cut roughly in half from the old spec now that the show has no culture
segment. Confirmed with Tyler 2026-09-15.

| Season | Words | Minutes at 150 wpm |
|---|---|---|
| **May–Oct** (offseason) | **900–1,150** | 6–8 |
| **Nov–Apr** (UNC basketball) | **1,300–1,700** | 9–11 |

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

| Segment | Offseason | In-season delta |
|---|---|---|
| 1. Cold open | 80 | — |
| 2. AI & tech | 150, often 0 | — |
| 3. This week ahead | 100, sometimes 0 | — |
| 4. Sports | 500 | → 950 |
| 5. Disney | 160 | — |
| 6. Sign-off | 45 | — |
| | **~1,035** | |

### 1. COLD OPEN (~80)
"Good morning, Tyler. It's [Weekday], [Month] [day]." State the runtime.
Preview the biggest news story, the calendar's shape if the segment is
running this week, and one sports item. Hand off.

### 2. AI & TECH (~150, and often zero)
Unchanged from before. **Minimized.** Skip the segment entirely on an
ordinary week rather than filling it. When you skip it, say so in one line.

Clears the bar: a real capability jump with verifiable evidence; a major
safety or security incident; regulation that actually binds; a chip or
company move that reshapes the market.

Does not clear it: incremental model releases, funding rounds, product
updates, benchmark scores, executive shuffles, anything an aggregator is
excited about. No week-ahead earnings or macro beat.

Sourcing, with a domain allowlist: company engineering and research blogs,
Reuters, Bloomberg, WSJ, Fortune, Ars Technica, TechTarget, MIT Technology
Review, Nature. Content farms garble details and occasionally invent whole
events. Verify every dramatic claim against a primary source. **Unconfirmed
means excluded, not hedged.** Attribute contested reporting out loud.

### 3. THIS WEEK AHEAD (~100, sometimes zero) — NEW, read the guardrails

This replaces the old calendar-free rule with something deliberately
narrower than "recap Tyler's appointments" sounds like. **The show does not
describe Tyler's week. It describes the week's shape, in three fixed tiers,
and nothing else.**

**Source.** The "Home Life" calendar on Tyler's primary Google account,
`mcp__bb2c4eb0-a755-4dba-b81a-dccf6864dc15__list_events`, the coming 7 days
from the Monday this airs.

**What you are allowed to say — the entire vocabulary:**
- One of exactly three shape words, picked by counting non-work "Home Life"
  events in the window: **light** (0–2), **typical** (3–5), **full** (6+).
- Optionally, ONE generic clause naming a broad category if — and only
  if — at least two independent events on the calendar plainly belong to
  that category with nothing else identifying about them: "family things,"
  "errands," "the usual mix." Never a specific event title, never a count
  of the category, never which day.

That is the entire inventory. There is no fourth thing to add. Do not name a
day of the week an appointment falls on. Do not name a time. Do not name a
location, even generically ("downtown," "the coast"). Do not name who is
involved, family or otherwise. Do not mention anything health- or
appointment-type-specific — a specific mention of "doctor," "dentist,"
"school," "work trip" etc. is exactly the kind of specific the tier system
exists to avoid, even though none of those words is dangerous on its own;
the rule is categorical, not case-by-case judgment on a live run.

**The travel and absence rule — this is why the segment exists to be able to
skip itself.** If ANYTHING on the calendar in the window signals travel, an
out-of-office block, a multi-day event, or any reasonable inference that the
house will be empty, **do not run this segment at all this week.** Do not
try to describe around it, do not fold it into "full," do not mention that
you're skipping because of travel. Just skip it exactly the way AI & Tech
skips when nothing clears its bar — one line, "nothing on the calendar worth
a shape this week," and move on. A skipped segment reveals nothing. A
segment that visibly avoids a topic reveals that there was something to
avoid, which is its own leak — so the skip line must be the same
one-liner whether the reason is travel, an empty calendar, or anything
else. Never let the skip reason be inferable from the wording.

**Worked example of the whole segment, light tier:** "The week ahead looks
light, mostly the usual mix." That is a complete, correct instance — nothing
else is owed.

**Why so narrow.** Multi-week pattern-matching is the actual threat model
for a public feed, not any single episode. A stalker or a burglar does not
need one episode to say "Tyler is away" — a run of "full" weeks followed
abruptly by silence, or a "light" week that reliably correlates with a
trip, teaches the same thing over months. The fixed three-word vocabulary
and the mandatory silent skip on travel signals exist specifically to
prevent the segment from becoming a distinguishable signal over time, not
just to sanitize any one week's script.

### 4. SPORTS (~500; ~950 in-season)
Unchanged from before. **UNC men's basketball leads year-round**, with one
standing exception: inside three weeks of a football game, football leads.
Basketball still gets its beat.

- In season: this week's games, opponents, tip times ET, channels. Last week
  in a sentence or two. Rotation, roster, injuries, ACC standings, national
  picture, and where the season stands as an arc.
- Offseason: roster moves, portal, staff, recruiting, program storylines.

Sourcing: goheels.com, 247Sports, On3, Inside Carolina, News & Observer, CBS
Sports, ESPN. **Never report recruiting rumor or coaching speculation as
fact.** Flag unconfirmed items and name who is reporting.

Then **golf**. In are architecture, design, travel, destination. Out are
player profiles and tour personality pieces. Tournament results are news and
belong here — lead with the ground, not the leaderboard, when there is
anything to say about the course.

Then briefly UNC football, Carolina Panthers, Charlotte Hornets: day, time
ET, channel, one line on stakes. Out-of-season teams get a clause. Skip
Charlotte FC and NASCAR.

### 5. DISNEY (~160)
Unchanged from before. Standing segment. Rotate across parks news, new
attractions, crowd calendars and booking windows, Imagineering and design
history, Pixar and animation, notable company news. Sources: Disney Parks
Blog, WDWNT, Blog Mickey, Attractions Magazine, Laughing Place.

**Distinguish confirmed announcements from rumor.** Skip the segment rather
than padding it.

### 6. SIGN-OFF (~45)
One sentence recapping the concrete news items plus any can't-miss sports
event. No mention of the email or the artifact — this show doesn't carry
picks anymore, so there's nothing here to point at. Then exactly:
**"Have a good one, Tyler. See you next Monday."**

---

## TTS FORMATTING

Unchanged from before. The file goes straight into text-to-speech.

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

`audio_post.py` implements these and they become real audio. They are
stripped before the text reaches the narrator, so they are never spoken.

Each on its own line, blank line either side.

- `[[TRANSITION]]` — a short music sting, padded with 0.35s of silence on
  each side so the music registers as a break rather than a blip against the
  next line of speech. **One before each major segment.** Never inside a
  segment. With four segment transitions now (AI & Tech, This Week Ahead,
  Sports, Disney) rather than the old five, expect one fewer than before.
- `[[PAUSE]]` — 0.85s. Before a line that should land. One or two an
  episode now that the show is shorter — the old "two or three" guidance
  scaled down with everything else.
- `[[BEAT]]` — 1.7s. A longer hold. Once an episode at most, usually before
  the sign-off.

`audio_post.py`'s own docstring and `MARKERS`/`STING_PAD` constants are the
source of truth for the exact numbers; this file states them for reference
only, and the two must not drift again — see that file's changelog entry
from 2026-09-13 for why this matters.

**A script with zero markers narrates as one unbroken block.** Confirm
before finishing:

```
python3 -c "import sys;sys.path.insert(0,'.');import audio_post,pathlib;\
tl=audio_post.build_timeline(pathlib.Path('SCRIPT').read_text());\
print('non-speech blocks:', sum(1 for k,_ in tl if k!='speech'))"
```

Each `[[TRANSITION]]` expands to three non-speech blocks (silence, sting,
silence). For a typical shorter episode — three or four section transitions
plus one or two pauses and at most one beat — expect roughly eleven to
fifteen, not the old eighteen to twenty. What to actually check is the
marker count in the raw script text, not the expanded block count.

### Emphasis

`tts-1` supports no SSML and no delivery control, so emphasis comes from the
writing. Short sentences land harder than long ones. Put the important word
at the end of the sentence. Never use capitals or italics for stress.

---

## OUTPUT CHECKLIST

1. Save to `PODCAST_DIR/scripts/monday-brief-YYYY-MM-DD.txt`, dated for the
   Monday it airs. There is no second destination.
2. Word count in range, on stripped text (900–1,150 offseason, 1,300–1,700
   in-season).
3. Both TTS greps clean. Marker count in the expected range.
4. **No dollar figures, account numbers, family names, travel signals, or
   health detail anywhere in the script — it publishes to a public feed.**
   Re-read "This Week Ahead" specifically against its own vocabulary limit:
   if it says anything beyond one shape word and one permitted generic
   clause, cut it back before shipping, not after.
5. Confirm the file is on disk and non-empty. If `PODCAST_DIR` is
   unreachable (it is iCloud-synced and may not mount on a scheduled run),
   write to outputs and **say loudly in chat** that the script did not reach
   the publish folder.
6. `present_files` with the script path.
7. In chat, three or four lines: word count and runtime; the lead story;
   whether This Week Ahead ran or skipped (and if it skipped, don't say
   why); confirmation the script landed on disk.

This show no longer touches the `JARVIS Content Memory` Gmail draft at all —
there is no memory-protocol step here anymore, no `pending_marks`, no
`week_picks`, nothing to write back. If a run finds itself reading that
draft while producing this show, it has picked up stale instructions from
before 2026-09-15 — stop and re-read this file from the top.

---

## CHANGELOG

**2026-09-15** — Restructured at Tyler's direction: this show is now
appointments-shape plus news only. Removed the Watch/Read/Listen segment and
the two on-air taste questions entirely; both moved to the `weekly-queue`
scheduled task, which now also sends a weekly email with the picks and
questions rather than only rendering the interactive artifact. Added "This
Week Ahead," a new segment with a deliberately narrow three-word vocabulary
(light/typical/full plus one optional generic clause) and a hard rule to
silently skip itself on any travel or absence signal, because the show
remains public and multi-week pattern-matching on a public feed is a real
threat model, not a hypothetical one. Cut runtime targets roughly in half
(900–1,150 offseason, 1,300–1,700 in-season) now that the 750-word culture
segment is gone. This show no longer reads or writes the `JARVIS Content
Memory` draft at all, which also takes it out of the blast radius of that
memory's ongoing size-ceiling problem (see `podcast-preferences.md`).

Prior history (the 2026-08-07 through 2026-08-23 merges, the volume cap, the
two-surface contract as it applied to this show, the private-hosting
decision) is preserved in git history and in `podcast-preferences.md`'s
refinement log, but is no longer reproduced here since most of it described
a segment this show no longer has.
