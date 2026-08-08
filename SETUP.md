# The Monday Brief — setup

Everything lives in this folder. Nothing gets uploaded to Spotify directly —
Spotify has no supported upload API, so instead GitHub Pages hosts the audio and
the RSS feed, and Spotify (plus Apple, Overcast, Pocket Casts, anything else)
pulls from that feed. You claim the feed once and never touch Spotify again.

```
JARVIS Podcast/
├── config.json      ← your settings, edit this first
├── setup.sh         ← run once: creates the GitHub repo
├── publish.py       ← run weekly: script → audio → feed → push
├── scripts/         ← drop your weekly script here (.md or .txt)
└── repo/            ← the git repo GitHub Pages serves
    ├── cover.jpg    ← show artwork (1500×1500)
    ├── feed.xml     ← generated, don't edit by hand
    └── episodes/    ← generated mp3s
```

## 1. Run setup

```bash
cd "~/Library/Mobile Documents/com~apple~CloudDocs/Claude/JARVIS Podcast"
./setup.sh
```

It checks for Homebrew, git, `gh`, and ffmpeg (installing what's missing), logs
you into GitHub in a browser, creates the **public** repo `jtdancy-jarvis/monday-brief`,
and turns on Pages. Safe to re-run — every step checks before it acts.

> The repo has to be public. Free GitHub Pages only serves public repos. The
> *show* can still be unlisted on Spotify; it's the storage that's public. Don't
> put anything in this repo you wouldn't post publicly.

## 2. Add your OpenAI key

TTS is the only thing that costs money — roughly **$15/year** at one 8-minute
episode a week.

```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

## 3. Publish the episode you already have

```bash
./publish.py --audio "8-3-26 Podcast.mp3" --date 2026-08-03 --dry-run
```

Check `repo/episodes/2026-08-03.mp3` sounds right, then drop `--dry-run`.

## 4. Claim the feed on Spotify

Go to <https://podcasters.spotify.com>, choose *Add your podcast*, and paste:

```
https://jtdancy-jarvis.github.io/monday-brief/feed.xml
```

Spotify emails a verification code to the address in `config.json`
(`jtdancy@gmail.com`) — it must match `itunes:owner`, which it does. Review can
take a few hours to a couple of days. After that, every push updates the show
automatically.

## Weekly use

Drop a script into `scripts/` and run:

```bash
./publish.py
```

It takes the newest script, strips the markdown, chunks it under the 4,096-char
TTS limit on paragraph boundaries, narrates each chunk, stitches with ffmpeg,
writes `episodes/YYYY-MM-DD.mp3`, rebuilds `feed.xml`, and pushes.

Useful flags: `--dry-run`, `--audio FILE`, `--script FILE`, `--title "..."`,
`--date YYYY-MM-DD`.

## Automating it

`com.jtdancy.mondaybrief.plist` runs it Mondays at 5:15am.

```bash
# put your real key in the plist first, then:
cp com.jtdancy.mondaybrief.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jtdancy.mondaybrief.plist
```

Logs go to `~/Library/Logs/mondaybrief.log`.

**Two things to know before you automate:**

1. **This folder is in iCloud Drive.** If macOS evicts files to save space, a
   background job can fail on a file that looks present but isn't downloaded.
   Right-click the folder in Finder → *Keep Downloaded* to prevent that. Moving
   the whole thing to `~/Claude/MondayBrief` avoids the issue entirely.
2. **Something has to write the script.** `publish.py` reads from `scripts/`;
   it doesn't generate content. Point your weekly Claude curation task at that
   folder, and have it run before 5:15am Monday.

## What was verified

Built and tested against your real `8-3-26 Podcast.mp3` (7:48, 7.5 MB):

- Feed parses as XML; all required channel and iTunes tags present; enclosure
  `length` matches actual file bytes; GUIDs unique; items ordered newest-first.
- Multi-episode ordering confirmed with three dated files.
- Chunking tested on five inputs including a 12,000-char single paragraph and a
  9,000-char run with no sentence breaks — every chunk under the limit, no
  content dropped in any case.
- Markdown stripping verified against headings, bold, links, code, bullets, rules.
- Bad `--date` and missing `--audio` exit with a clear error instead of a stack trace.
- Cover art is 1500×1500 JPEG, 167 KB — inside Apple/Spotify's 1400–3000px spec.

Not verified, because it needs your credentials: the actual `gh` login, repo
creation, Pages activation, and push. That's what `setup.sh` walks through.
