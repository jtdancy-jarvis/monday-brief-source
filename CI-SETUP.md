# Moving publishing off the Mac

The publish step runs on GitHub Actions instead of launchd. The Mac's only
remaining job is writing the script and pushing it.

```
Sunday 5pm   Claude (Cowork, on the Mac)  writes scripts/monday-brief-YYYY-MM-DD.txt
                                          git commit + push
                        |
                        v  push to scripts/** triggers the workflow
GitHub Actions (ubuntu)  installs ffmpeg
                         checks out THIS repo (private)  -> source
                         checks out monday-brief (public) -> repo/
                         python3 publish.py --script ... --date ...
                           OpenAI TTS -> ffmpeg mastering -> repo/episodes/*.mp3
                           rebuild feed.xml -> git push to the public repo
                        |
                        v
GitHub Pages serves feed.xml -> Spotify polls it
```

Two repos, on purpose:

- **This one, private.** Scripts, `publish.py`, `audio_post.py`, `config.json`,
  `assets/`. Episode text never becomes public.
- **`jtdancy-jarvis/monday-brief`, public.** Only finished `.mp3`, `feed.xml`,
  and `cover.jpg`. Exactly what it holds today. Unchanged.

Going private-first is the reversible direction. A private repo can be opened
up later; text already in a public git history cannot be taken back.

---

## What only you can do

### 1. Create the private source repo

On github.com, new repo, **Private**, named something like
`monday-brief-source`. Do not add a README or .gitignore, this folder has one.

Then, in this folder:

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude/JARVIS\ Podcast
git init -b main
git add -A
git commit -m "Monday Brief source: scripts, publisher, assets, CI"
git remote add origin https://github.com/jtdancy-jarvis/monday-brief-source.git
git push -u origin main
```

Check `git status` before that commit. `.gitignore` already excludes `repo/`,
`work/`, `scripts-private/`, and the two loose mp3s. `scripts-private/` staying
out is deliberate — see the `private-hosting` thread.

### 2. Create a token so the runner can push to the public repo

The runner gets a token for the repo it runs in, but not for a second one.

github.com → Settings → Developer settings → Personal access tokens →
**Fine-grained tokens** → Generate new token.

- Repository access: **Only select repositories** → `jtdancy-jarvis/monday-brief`
- Permissions: **Contents: Read and write**
- Expiry: set a calendar reminder for whatever you pick, an expired token here
  fails silently on a Sunday night

### 3. Add both secrets to the private repo

In `monday-brief-source` → Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `OPENAI_API_KEY` | the same key currently in your `~/.zshrc` |
| `FEED_REPO_TOKEN` | the fine-grained token from step 2 |

`ELEVENLABS_API_KEY` is referenced by the workflow too, but is only read if you
switch `config.json` to `"provider": "elevenlabs"`. Leave it unset for now.

### 4. Test it without spending anything real

Actions tab → **Publish Monday Brief** → Run workflow → tick **dry_run**.

It narrates, masters, rebuilds the feed, and stops before pushing. The finished
mp3 is attached to the run as an artifact, so you can download and listen before
anything goes near the feed.

### 5. Turn off the launchd job

Once a real run has pushed successfully:

```
launchctl bootout gui/$(id -u)/com.jtdancy.mondaybrief
rm ~/Library/LaunchAgents/com.jtdancy.mondaybrief.plist
```

Leave `run_weekly.sh` and `com.jtdancy.mondaybrief.plist` in the folder as a
fallback path. Neither runs unless the job is loaded.

---

## Things that will bite you later

**Script selection changed, and it had to.** `publish.py` picks the newest
script by modification time. In CI every file in a fresh checkout has the same
mtime, so "newest" is arbitrary and you would eventually publish the wrong
episode. The workflow now chooses by the `YYYY-MM-DD` in the filename and passes
`--script` and `--date` explicitly. **Every script must have a date in its
filename** or the run fails loudly.

**`--date` no longer defaults to today.** That was the bug waiting in
`run_weekly.sh`, which ran bare `./publish.py`. Publishing on any day other than
the episode date would have stamped the wrong `pubDate`.

**Editing an old script republishes that episode.** The date comes from the
filename, so it overwrites that episode's mp3 and keeps the same GUID. Usually
what you want. Worth knowing before you fix a typo in a six-month-old script.

**The 1 GB wall.** Every episode adds about 7.5 MB to the public repo, roughly
390 MB a year, against a 1 GB published-site limit on GitHub Pages. That is
about two and a half years of runway. Bandwidth is not a concern: the 100 GB per
month soft limit is roughly 14,000 downloads.

When you hit it, the fix is a real podcast host — Transistor, Buzzsprout,
Captivate. They also support private and unlisted feeds, which is the actual
answer to the `private-hosting` blocker. They do not do text-to-speech, so they
would sit downstream of this workflow rather than replace it.
