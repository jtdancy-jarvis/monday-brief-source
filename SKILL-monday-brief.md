# Monday Brief — script generation skill

Write this week's episode of the "Monday Brief," Tyler Dancy's personal weekly
podcast, listened to on a 6:00am Monday commute. Kannapolis, NC
(America/New_York). Deliver ONLY a plain-text script file. No audio generation.

PODCAST_DIR: `~/Library/Mobile Documents/com~apple~CloudDocs/Claude/JARVIS Podcast`

---

## SECTION 0: OUTPUT ROUTING — READ FIRST

This show contains personal material: calendar, inbox, family, plans. That is
intended and correct.

**Write to `PODCAST_DIR/scripts-private/YYYY-MM-DD.txt`.**

**Never write to `PODCAST_DIR/scripts/`.** `publish.py` globs that folder, takes
the newest `.md`/`.txt` by modification time, narrates it, and pushes it to
`github.com/jtdancy-jarvis/monday-brief` — a repo that `SETUP.md` states must be
public, serving a feed claimed on Spotify and pollable by any podcast app. The
feed identifies the owner by name and email. A personal script in `scripts/`
publishes Tyler's week to the open internet at 5:15am Monday.

Publishing is a deliberate act: `./publish.py --script <file>`. Not automatic.

Two things still warrant care even in a private episode, because audio outlives
its context and a passenger may be in the car:

- Never read account numbers or dollar balances aloud. Calendar event titles
  sometimes embed amounts (there is a recurring "Outback $425"). Strip the
  figure, keep the event.
- Forward travel dates and stretches when the house is empty are fine to plan
  around, but do not belong in anything that ever gets published.

---

## RUNTIME — SEASONAL

- **November–April (UNC basketball season): 2,100–2,700 words**, 14–18 min.
- **May–October (offseason): 1,500–2,000 words**, 10–13 min.

Verify with `wc -w`. State the runtime in the cold open, computed from the FINAL
word count at 150 wpm, rounded to the nearest minute. Do not estimate it before
the script is finished.

**TONE:** Calm and brisk. NPR morning-newscast register. Short declarative
sentences. No hype, no cheerleading. Dry wit in small doses. It is 6am and he is
driving.

---

## STRUCTURE

Offseason budgets; in-season in parentheses where different.

### 1. COLD OPEN (~85 words)
"Good morning, Tyler. It's [Weekday], [Month] [day]." State the runtime. Preview
the biggest personal item, the biggest news story, and one culture or sports
item. Hand off.

### 2. YOUR WEEK (~260)
Google Calendar, Monday–Sunday, ALL three calendars:

- Home Life: `jtdancy@gmail.com`
- Work: `t6j3tg1im24h0sg0f09kj42his@group.calendar.google.com`
- Family: `family03731468257385886255@group.calendar.google.com`

Day by day with specific times. Flag the day needing advance thought. Empty
calendars are information, but do not narrate a list of empty days — name them
in one line and spend the words where there is something to say. **Watch for
anything resembling a Disney or golf trip and front-run it with planning notes.**

Then Gmail: `in:inbox newer_than:7d -category:promotions -category:social`. ONLY
action items, as one "ten minutes of admin" beat. That filter leaks newsletters
and marketing; judge by content, not by the category label.

### 3. AI & TECH (~150, and often zero)
**Minimized.** Include only when a story genuinely clears the bar. Cap at
roughly 150 words. **Skip the segment entirely on an ordinary week** rather than
filling it — a missing segment is better than a filled one, and the words go to
Watch, Read, Listen instead.

Clears the bar: a real capability jump with verifiable evidence; a major safety
or security incident; regulation that actually binds; a chip or company move
that reshapes the market.

Does not clear the bar: incremental model releases, funding rounds, product
updates, benchmark scores, executive shuffles, anything an aggregator is excited
about. No week-ahead earnings or macro beat.

**Sourcing.** Search with a domain allowlist. Trusted: company engineering and
research blogs, Reuters, Bloomberg, WSJ, Fortune, Ars Technica, TechTarget, MIT
Technology Review, Nature. Content farms and SEO aggregators garble details and
occasionally invent whole events. Verify every dramatic claim against a primary
source. **Unconfirmed means excluded, not hedged.** Attribute contested
reporting out loud.

### 4. WATCH, READ, LISTEN (~600, more on a week with no tech story)
The centre of the show. One strong pick plus a list.

**Rule 1 governs everything here: warmth beats craft.** The bail signal is a
cold, airless tone, not slow pacing. A technically accomplished thing full of
unpleasant people gets abandoned. Do not recommend prestige work whose main
selling point is atmosphere over people, however well reviewed.

**Tone floor: mid and lighter.** Real stakes and real loss are fine. Relentless
bleakness and cruelty-as-texture are not.

**Mostly new, with exactly one catalog slot per episode** for something older
worth going back for. Do not let a thin release week produce weak new picks when
the catalog is available.

**FILM/TV.** Check service tiers first. Tier 1 (Netflix, Hulu, Disney+, Prime)
recommend freely. Tier 2 (Apple TV+, HBO Max) only as a conviction pick, and
make the subscription case including what else on that service justifies the
same billing month. Tier 3 (Peacock, Paramount+, MGM+) skip. Home viewing by
default; theater only for real events. TV counts as much as film. Bill Lawrence
projects and comic ensemble mysteries are automatic flags. Note when something
works as a watch with Ty (13) or the whole family.

**Verify availability before recommending.** Do not state which service carries
a title from memory. A wrong service is the error he will notice in the car.

**BOOKS.** Two to three picks; he reads steadily and wants options. **Voice is
the criterion: is the narrator good company?** Bleak subject matter is fine;
cold tone is not. Never filter by genre label, judge tone. Note audiobook
availability, library hold likelihood, and whether it is worth owning. Golf
writing is a live category.

Hard exclusions: no AI books, no political insider books, no self-help, no
romantasy, no horror, no austere literary fiction, no dry sci-fi. Fully caught
up on Thursday Murder Club, never pitch book one.

**PODCAST.** One pick, **enthusiast deep-dive** register: hosts with real
expertise going long on a subject they love. Not celebrity interviews. Length is
never a reason to skip. Already in rotation, do not recommend: Acquired, The
Disney Dish, The Golfer's Journal.

### 5. SPORTS (~420, in-season ~950)
**UNC men's basketball leads, year-round.**

- In season: full weekly report. This week's games with opponents, tip times ET,
  channels. Last week in a sentence or two. Rotation and roster developments,
  injuries, ACC standings, national picture, and where Malone's first season
  stands as an arc.
- Offseason: roster moves, portal, staff, recruiting, program storylines.

Sourcing: goheels.com, 247Sports, On3, Inside Carolina, News & Observer, CBS
Sports, ESPN. Never report recruiting rumor or coaching speculation as fact.
Flag unconfirmed items and name who is reporting.

Then **golf** (he plays): majors and big tournaments when live, tour
storylines. Not instruction or equipment. Skip on a dead week. Then briefly UNC
football, Carolina Panthers, Charlotte Hornets: day, time ET, channel, one line
on stakes. Out-of-season teams get a clause. Skip Charlotte FC and NASCAR.

### 6. DISNEY (~140)
Standing segment. Rotate across parks news and new attractions, crowd calendars
and booking windows (the family takes trips), Imagineering and design history,
Pixar and animation releases, notable company news. Sources: Disney Parks Blog,
WDWNT, Blog Mickey, Attractions Magazine, Laughing Place.

**Distinguish confirmed announcements from rumor** — the Disney fan press runs
on speculation and he will notice. Skip the segment rather than padding it.

### 7. TWO QUESTIONS (~85)
Exactly two, from the bank in `podcast-preferences.md`. Rotate categories, never
repeat within eight weeks — check the ledger. Conversational, tell him to just
tell Claude the answers, say what each will change.

### 8. SIGN-OFF (~55)
One sentence recapping concrete commitments plus any can't-miss event. Then:
"Have a good one, Tyler. See you next Monday."

---

## TTS FORMATTING

Goes straight into text-to-speech.

- Plain prose only. No markdown, headers, bullets, asterisks, or em-dashes.
  Periods and commas.
- Spell numbers as spoken: "two hundred and fifty billion dollars," "seven
  forty," "nineteen point nine points," "twenty-four and nine."
- Expand titles: "Doctor Sumner." Keep known acronyms (AI, FBI, AMD, NBC, ACC,
  TCU, NCAA, NBA, A24).
- Paragraph breaks are the pacing tool. A one-line paragraph reads as a beat.
- No URLs or citations. Attribution spoken inline.
- Verify before finishing: `grep -n '[—*#|]' <file>` must return nothing, and
  `grep -n '[0-9]' <file>` must return nothing.

### Pause and transition markers

Three markers, each on its own line with a blank line either side. They are
stripped before the text reaches the narrator and become real audio in the
timeline, so they are never spoken.

- `[[PAUSE]]` — 0.55s. Before a line that should land. Use sparingly; two or
  three an episode. Overused, it sounds portentous.
- `[[BEAT]]` — 1.1s. A longer hold. Once an episode at most, usually before
  the sign-off.
- `[[TRANSITION]]` — a short music sting. One before each major segment. Do
  not put one inside a segment.

**Count words on the stripped text, not the raw file** — markers otherwise
inflate `wc -w`:

```
python3 -c "import sys;sys.path.insert(0,'.');import audio_post,pathlib;\
print(len(audio_post.strip_markers(pathlib.Path('SCRIPT').read_text()).split()))"
```

### Emphasis

`tts-1` supports no SSML and no delivery control, so emphasis has to come from
the writing. Short sentences land harder than long ones. A one-line paragraph
after a long one is the strongest emphasis available. Put the important word at
the end of the sentence. Do not use capitals or italics for stress — the
narrator ignores the formatting and the markdown stripper removes it anyway.

For actual delivery control, switch `config.json` to `gpt-4o-mini-tts` and add
an `instructions` string; `publish.py` sends it only when present. Something
like: *"Calm, measured NPR morning-newscast register. Unhurried. Let the
sentence ends fall rather than lifting into them."* That model costs slightly
more per character and the voice character differs, so audition it before
committing.

---

## CONTINUITY — THE EPISODE LEDGER

`PODCAST_DIR/episode-ledger.md` records every episode's picks and status.

**Before recommending anything, read the ledger.** Never repeat a book, show,
film, or podcast that has already aired. Items marked NEVER AIRED remain
available.

**After writing, append an entry** with the date, word count, lead story, every
pick by category, the two questions asked, and any follow-ups the next episode
should close out (an announcement due, a tournament result, a visit that may
become a commitment).

Read the previous entry's follow-ups and close them out where there is news. A
show that remembers what it said last week is the difference between a briefing
and a feed reader.

---

## PREFERENCES

Read `PODCAST_DIR/podcast-preferences.md` if it exists. It governs where it
conflicts with this file. If absent, use the defaults here and say so in chat.

---

## OUTPUT

1. Save to `PODCAST_DIR/scripts-private/YYYY-MM-DD.txt` for the Monday it airs.
   Never `scripts/`. See Section 0.
2. Verify: word count in range, both `grep` checks clean, no dollar figures read
   aloud.
3. List `scripts-private/` and confirm the file is there and non-empty.
4. Append the episode-ledger entry.
5. Call `present_files` with the script path.
6. In chat, four lines: word count and runtime at 150 wpm, the lead story, the
   two questions asked, and confirmation of where the file landed.
