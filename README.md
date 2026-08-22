# The Monday Brief

A weekly personal podcast: produced Sunday evening, published automatically,
listened to on a 6:00am Monday commute. This file is the single source of
truth for how the pieces fit; `SKILL-monday-brief.md` governs what an episode
contains.

## Architecture

```
Sunday ~5pm   Claude on the Mac follows SKILL-monday-brief.md
                ├── full personal script  -> scripts-private/YYYY-MM-DD.txt   (never committed)
                └── sanitized public cut  -> scripts/monday-brief-YYYY-MM-DD.txt
                                             git commit + push
                                                   |
                          push to scripts/** triggers .github/workflows/publish.yml
                                                   v
GitHub Actions   preflight (token can push, size headroom)   <- fails BEFORE TTS spend
                 publish.py --script ... --date ...
                   OpenAI TTS -> ffmpeg master (-16 LUFS) -> repo/episodes/YYYY-MM-DD.mp3
                   rebuild feed.xml -> push to the public feed repo
                                                   v
GitHub Pages     serves feed.xml  ->  Spotify / Apple / Overcast poll it

Monday 10:30 UTC  watchdog.yml checks the live feed has today's episode;
                  files an issue if not.
```

Two repos, on purpose:

- **`jtdancy-jarvis/monday-brief-source` (public since 2026-08-09, this
  folder).** Scripts, publisher, mastering, assets, CI. It started private and
  the split was originally justified by keeping episode text unpublished; that
  is no longer true and the reason for two repos is now narrower — the feed repo
  stays separate so 7.5 MB of audio a week does not accumulate alongside the
  source, and so Pages serves only what it needs to.
- **`jtdancy-jarvis/monday-brief` (public).** Only finished mp3s, `feed.xml`,
  `cover.jpg`. Public because free GitHub Pages only serves public repos.

> **Everything tracked here is world-readable.** Name, email and city are in
> tracked files by explicit decision. Family names, forward travel dates, payday
> figures, health and account detail must never be committed — those belong in
> `scripts-private/`, which is gitignored.

Two script folders, on purpose:

- **`scripts/`** — sanitized public cuts. Anything date-stamped that lands here
  and gets pushed IS published to the open internet. The public cut is the
  private script minus the calendar/inbox segment and anything referencing
  family, travel dates, or money.
- **`scripts-private/`** — full personal episodes. Gitignored, never a CI
  trigger, stay on the Mac until the private-hosting question is settled.

## Weekly rhythm

Sunday's producer session writes the public cut into `scripts/`. `./ship`
commits and pushes it. CI does the rest. Failures surface as GitHub issues on
the source repo (publish failures from `publish.yml`, missing episodes from
`watchdog.yml`).

**Who runs `./ship` depends on where the producer ran.** A session with git
credentials pushes for itself. A scheduled/sandboxed run has none by design, so
the push has to happen on the Mac — either by running `./ship` yourself, or by
installing the launchd agent in `launchd/`, which watches `scripts/` and ships
anything new. The agent is what makes the week genuinely hands-off; without it,
one command on Monday morning is the whole manual step.

`./ship` exists because `git add -A` is unsafe in this folder. It stages
explicit paths under `scripts/` only, ships new episodes but requires
`--republish` to re-push an edited one, and refuses text that fails the two TTS
greps or has no `[[TRANSITION]]` markers. It also forces iCloud to materialise
tracked files first and aborts if any are still evicted, rather than committing
on top of a tree git cannot actually read.

## Manual operations

All of these run from this folder. `--date` is always required — it names the
episode's slot in the feed, and an implicit "today" once overwrote a
published episode.

```bash
# Ship whatever new episode is sitting in scripts/ (the normal path):
./ship
./ship --dry-run      # show what would go, touch nothing
./ship --republish    # also push edits to an already-published script
./ship --force        # ship despite the TTS text warnings

# Publish a specific script (what CI runs):
./publish.py --script scripts/monday-brief-2026-08-17.txt --date 2026-08-17

# Rehearse without pushing (still spends TTS money):
./publish.py --script ... --date ... --dry-run

# Publish existing audio, skipping TTS entirely:
./publish.py --audio path/to/episode.mp3 --date 2026-08-17

# Re-run CI by hand: Actions -> Publish Monday Brief -> Run workflow
# (optionally name a script/date; tick dry_run to stop before the push).
```

Editing an old script and pushing it republishes that episode: same filename
date, same feed slot, same GUID. Usually what you want; worth knowing before
fixing a typo in a six-month-old script.

### Episode GUIDs — the one thing not to break

Each item's `<guid>` is `monday-brief-YYYY-MM-DD` with `isPermaLink="false"`.
It is deliberately **not** the enclosure URL.

A GUID is an episode's identity to every podcast client. When it was the
enclosure URL, changing where audio lived — GitHub Releases, or a real podcast
host — rewrote every GUID and re-issued the entire back catalogue as unheard
episodes in every subscriber's app. Decoupled, the audio can move anywhere and
nobody notices.

So: `podcast.guid_prefix` in `config.json` is frozen. Renaming the show, the
repo, or the GitHub account is all safe. Changing that prefix is not.

### Changing feed metadata without re-narrating

Show title, description, artwork, category — anything feed-wide — takes effect
by rebuilding the feed from the episodes already published:

```bash
./publish.py --feed-only --dry-run   # inspect repo/feed.xml first
./publish.py --feed-only             # rebuild and push
```

No TTS, no audio, no new episode. This is the path for the pending show-name
decision.

## Recovery

- **CI failed after narration?** The mastered mp3 is attached to the run as an
  artifact (30-day retention). `gh run download <run-id> --repo
  jtdancy-jarvis/monday-brief-source`, then publish it with `--audio` — no
  TTS re-spend.
- **Feed repo diverged locally?** `repo/` is just a checkout; `git -C repo
  pull --rebase` and push again.

## One-time setup (new machine)

1. `./setup.sh` — installs tools, logs into GitHub, creates/wires the public
   repo, enables Pages.
2. Secrets on the source repo (Settings → Secrets → Actions):
   - `OPENAI_API_KEY` — for narration.
   - `FEED_DEPLOY_KEY` — the **private** half of an ssh keypair whose public
     half is registered on `jtdancy-jarvis/monday-brief` as a write-enabled
     deploy key. Deploy keys are scoped to one repo and never expire, which
     is why this is not a personal access token: a PAT's expiry date is a
     silent Sunday-night failure waiting to happen.

   To rotate it:

   ```bash
   ssh-keygen -t ed25519 -N "" -C monday-brief-ci -f /tmp/feedkey
   gh repo deploy-key add /tmp/feedkey.pub --repo jtdancy-jarvis/monday-brief \
     --title "monday-brief-ci (Actions publisher)" --allow-write
   gh secret set FEED_DEPLOY_KEY --repo jtdancy-jarvis/monday-brief-source < /tmp/feedkey
   rm /tmp/feedkey /tmp/feedkey.pub
   ```
3. The feed URL, already claimed on Spotify:
   `https://jtdancy-jarvis.github.io/monday-brief/feed.xml`
4. Optional, for hands-off Mondays — the auto-ship agent:

   ```bash
   cp launchd/com.jtdancy.monday-brief.ship.plist ~/Library/LaunchAgents/
   launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.jtdancy.monday-brief.ship.plist
   launchctl enable  gui/$UID/com.jtdancy.monday-brief.ship
   tail -f ~/Library/Logs/monday-brief-ship.log
   ```

   A LaunchAgent, not a daemon: it runs in the logged-in GUI session, which is
   what lets git reach the login keychain for the push credential. The paths in
   the plist are absolute — edit them on a machine that is not this one.

## Known limits

- **The 1 GB wall.** Pages stops serving at 1 GB; ~7.5 MB/episode ≈ 2.5 years
  of runway. CI warns at 700 MB. The eventual fix is a real podcast host
  (Transistor, Buzzsprout, Captivate) downstream of this same pipeline — they
  also solve private feeds, which is the `scripts-private/` blocker.
- **This folder lives in iCloud Drive.** Right-click → *Keep Downloaded*, or
  a git operation can hit a file that looks present but is evicted.
- **TTS cost** is the only per-episode spend: roughly $0.10–0.30/week at
  current length on `gpt-4o-mini-tts`.
