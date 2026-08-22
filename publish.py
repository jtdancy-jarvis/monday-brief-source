#!/usr/bin/env python3
"""
Publish an episode of the Monday Brief.

Pipeline:
  script (.md/.txt)  ->  chunked OpenAI TTS  ->  ffmpeg concat  ->  mp3
  mp3 -> repo/episodes/YYYY-MM-DD.mp3 -> regenerate feed.xml -> git push

Spotify (and Apple, Overcast, etc.) pull the feed from GitHub Pages.
Nothing is uploaded to Spotify directly -- there is no supported API for that.

Usage (--date is always required; it names the episode's slot in the feed):
  ./publish.py --date 2026-08-17 --dry-run      # build everything, don't push
  ./publish.py --date 2026-08-17                # build and push
  ./publish.py --date 2026-08-17 --audio ep.mp3 # skip TTS, publish existing mp3
  ./publish.py --date 2026-08-17 --script scripts/monday-brief-2026-08-17.txt

Normally none of this is run by hand: CI (.github/workflows/publish.yml) runs it
when a script lands in scripts/, passing --script and --date picked from the
filename.
"""

import argparse
import datetime as dt
import email.utils
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import audio_post

ROOT = Path(__file__).resolve().parent
ITUNES = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ATOM = "http://www.w3.org/2005/Atom"
CONTENT = "http://purl.org/rss/1.0/modules/content/"


# ---------------------------------------------------------------- helpers

def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        die(f"{' '.join(cmd)}\n{r.stderr.strip()}")
    return r


def load_config():
    p = ROOT / "config.json"
    if not p.exists():
        die("config.json not found next to publish.py")
    return json.loads(p.read_text())


def need(binary):
    if shutil.which(binary) is None:
        die(f"'{binary}' is not installed or not on PATH")


# ---------------------------------------------------------------- text

def clean_for_speech(text):
    """Strip markdown so the narrator doesn't read asterisks and brackets."""
    text = re.sub(r"^---+$", "", text, flags=re.M)          # hrules
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)      # headings
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)        # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)    # links -> label
    text = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", text)      # code
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)         # bold
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)            # italic
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)    # bullets
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk(text, limit):
    """Split into <=limit pieces, preferring paragraph then sentence breaks."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, cur = [], ""

    def flush():
        nonlocal cur
        if cur.strip():
            chunks.append(cur.strip())
        cur = ""

    for p in paras:
        if len(p) > limit:
            flush()
            sentences = re.split(r"(?<=[.!?])\s+", p)
            for s in sentences:
                if len(s) > limit:                      # pathological: hard split
                    for i in range(0, len(s), limit):
                        flush()
                        chunks.append(s[i:i + limit].strip())
                    continue
                if len(cur) + len(s) + 1 > limit:
                    flush()
                cur = f"{cur} {s}".strip()
            flush()
            continue
        if len(cur) + len(p) + 2 > limit:
            flush()
        cur = f"{cur}\n\n{p}".strip()
    flush()
    return chunks


# ---------------------------------------------------------------- audio

def post_audio(req, label, attempts=4):
    """Fetch TTS audio, retrying transient failures.

    Unattended runs are the whole point of this script, so a dropped connection
    or a rate limit must not end the episode. 4xx other than 429 are permanent
    (bad key, bad request) and fail immediately rather than burning retries.
    """
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            if not (e.code == 429 or e.code >= 500) or attempt == attempts:
                die(f"{label} returned {e.code}: {detail}")
            reason = f"{e.code}"
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == attempts:
                die(f"{label} unreachable after {attempts} attempts: {e}")
            reason = type(e).__name__
        wait = 2 ** attempt
        print(f"    {label} {reason}, retry {attempt}/{attempts - 1} in {wait}s")
        time.sleep(wait)


def tts_elevenlabs(chunks, cfg, work, start=1):
    """ElevenLabs REST. Returns 44.1k mp3, which matches the mastering chain
    better than OpenAI's 24k output."""
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        die("ELEVENLABS_API_KEY is not set (add it to ~/.zshrc next to the OpenAI key)")
    voice_id = cfg["tts"]["voice"]
    model = cfg["tts"].get("model", "eleven_multilingual_v2")
    settings = cfg["tts"].get("voice_settings") or {
        "stability": 0.5, "similarity_boost": 0.75,
        "style": 0.0, "use_speaker_boost": True,
    }
    parts = []
    for i, c in enumerate(chunks, start):
        out = work / f"part{i:03d}.mp3"
        print(f"  tts {i}  ({len(c)} chars)  elevenlabs/{model}")
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            f"?output_format=mp3_44100_128",
            data=json.dumps({"text": c, "model_id": model,
                             "voice_settings": settings}).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json"})
        out.write_bytes(post_audio(req, "ElevenLabs TTS"))
        parts.append(out)
    return parts


def tts(chunks, cfg, work, start=1):
    if cfg["tts"].get("provider", "openai") == "elevenlabs":
        return tts_elevenlabs(chunks, cfg, work, start)
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        die("OPENAI_API_KEY is not set (add it to your shell profile or the launchd plist)")
    parts = []
    for i, c in enumerate(chunks, start):
        out = work / f"part{i:03d}.mp3"
        print(f"  tts {i}  ({len(c)} chars)  openai/{cfg['tts']['model']}")
        payload = {
            "model": cfg["tts"]["model"],
            "voice": cfg["tts"]["voice"],
            "input": c,
        }
        # `instructions` steers delivery (pace, register, emphasis) but is only
        # honoured by gpt-4o-mini-tts. tts-1 ignores it, so only send it when
        # it's configured, and let the model choice decide whether it applies.
        if cfg["tts"].get("instructions"):
            payload["instructions"] = cfg["tts"]["instructions"]
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/audio/speech",
            data=body,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
        )
        out.write_bytes(post_audio(req, "OpenAI TTS"))
        parts.append(out)
    return parts


def concat(parts, dest, work):
    if len(parts) == 1:
        shutil.copy(parts[0], dest)
        return dest
    listing = work / "concat.txt"
    listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(listing), "-c", "copy", str(dest)])
    return dest


def duration_hms(path):
    r = run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)])
    secs = int(float(r.stdout.strip()))
    return f"{secs // 3600:02d}:{secs % 3600 // 60:02d}:{secs % 60:02d}"


# ---------------------------------------------------------------- releases

def upload_release(mp3, date, title, cfg, dry_run):
    """Host this episode's audio as a GitHub Release asset, return its URL.

    Release assets do not count against the 1 GB GitHub Pages limit and never
    enter git history, so the feed repo stops growing by ~8 MB a week.

    Authenticated by GH_TOKEN, not the deploy key: releases are a REST API
    concept and ssh keys cannot reach the API at all.
    """
    need("gh")
    gh_cfg = cfg["github"]
    slug = f"{gh_cfg['username']}/{gh_cfg['repo']}"
    tag = f"ep-{date}"
    url = f"https://github.com/{slug}/releases/download/{tag}/{mp3.name}"

    if dry_run:
        print(f"  [dry run] would upload {mp3.name} to release {tag}")
        return url

    exists = run(["gh", "release", "view", tag, "--repo", slug],
                 check=False).returncode == 0
    if exists:
        # Republishing an edited episode: replace the asset in place so the
        # enclosure URL, and every listener's download link, stays valid.
        print(f"  release {tag} exists, replacing asset")
        run(["gh", "release", "upload", tag, str(mp3),
             "--repo", slug, "--clobber"])
    else:
        run(["gh", "release", "create", tag, str(mp3),
             "--repo", slug,
             "--title", title,
             "--notes", f"Audio for {title}. Published automatically; the feed "
                        f"at {gh_cfg['username']}.github.io/{gh_cfg['repo']}/"
                        f"feed.xml is the thing to subscribe to."])
        print(f"  release {tag} created")

    # Never let feed.xml reference an asset that is not actually downloadable.
    # A dead enclosure is worse than a missing item: clients cache and retry it,
    # and Apple and Spotify flag the show for it.
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=120) as r:
            if r.status != 200:
                die(f"release asset returned {r.status}: {url}")
    except urllib.error.URLError as e:
        die(f"release asset is not reachable, refusing to write it into the "
            f"feed: {url} ({e})")
    print(f"  asset verified: {url}")
    return url


# ---------------------------------------------------------------- feed

def build_feed(cfg, repo_dir):
    gh, pod = cfg["github"], cfg["podcast"]
    base = f"https://{gh['username']}.github.io/{gh['repo']}"

    # Frozen, and intentionally not derived from the repo or show name: both of
    # those can change, and a GUID that changes is a re-issued back catalogue.
    guid_prefix = pod.get("guid_prefix", "monday-brief")

    ET.register_namespace("itunes", ITUNES)
    ET.register_namespace("atom", ATOM)
    ET.register_namespace("content", CONTENT)

    rss = ET.Element("rss", {"version": "2.0"})
    ch = ET.SubElement(rss, "channel")

    def sub(parent, tag, text=None, **attrs):
        e = ET.SubElement(parent, tag, attrs)
        if text is not None:
            e.text = text
        return e

    sub(ch, "title", pod["title"])
    sub(ch, "link", base + "/")
    sub(ch, "description", pod["description"])
    sub(ch, "language", pod["language"])
    sub(ch, "copyright", pod["copyright"])
    sub(ch, "lastBuildDate", email.utils.format_datetime(
        dt.datetime.now(dt.timezone.utc)))
    ET.SubElement(ch, f"{{{ATOM}}}link", {
        "href": f"{base}/feed.xml", "rel": "self",
        "type": "application/rss+xml"})

    sub(ch, f"{{{ITUNES}}}author", pod["author"])
    sub(ch, f"{{{ITUNES}}}subtitle", pod["subtitle"])
    sub(ch, f"{{{ITUNES}}}summary", pod["description"])
    sub(ch, f"{{{ITUNES}}}explicit", pod["explicit"])
    sub(ch, f"{{{ITUNES}}}type", "episodic")
    ET.SubElement(ch, f"{{{ITUNES}}}image", {"href": f"{base}/cover.jpg"})
    owner = ET.SubElement(ch, f"{{{ITUNES}}}owner")
    sub(owner, f"{{{ITUNES}}}name", pod["author"])
    sub(owner, f"{{{ITUNES}}}email", pod["email"])
    cat = ET.SubElement(ch, f"{{{ITUNES}}}category", {"text": pod["category"]})
    if pod.get("subcategory"):
        ET.SubElement(cat, f"{{{ITUNES}}}category",
                      {"text": pod["subcategory"]})

    # The .json sidecar is the source of truth, not the .mp3. Episode audio
    # lives on Releases now and is never checked out here, so the feed has to
    # be buildable without it. Sidecars are a couple of hundred bytes each.
    eps = sorted((repo_dir / "episodes").glob("*.json"),
                 key=lambda p: p.stem, reverse=True)
    if not eps:
        die("no episode metadata (*.json) found in repo/episodes/")

    for meta_path in eps:
        meta = json.loads(meta_path.read_text())
        date = dt.datetime.strptime(meta_path.stem, "%Y-%m-%d").replace(
            hour=9, tzinfo=dt.timezone.utc)

        # url and length are recorded at publish time, because only the
        # publishing run has the audio in hand. Episodes published before the
        # move to Releases have their mp3 sitting beside them instead.
        url, length = meta.get("url"), meta.get("length")
        mp3 = meta_path.with_suffix(".mp3")
        if not url or not length:
            if not mp3.exists():
                die(f"{meta_path.name} has no url/length and no mp3 beside it")
            url = url or f"{base}/episodes/{mp3.name}"
            length = length or mp3.stat().st_size

        it = ET.SubElement(ch, "item")
        sub(it, "title", meta.get("title",
            f"{pod['title']} — {date:%B %-d, %Y}"))
        sub(it, "description", meta.get("description", pod["subtitle"]))
        sub(it, "pubDate", email.utils.format_datetime(date))
        ET.SubElement(it, "enclosure", {
            "url": url,
            "length": str(length),
            "type": "audio/mpeg"})

        # The GUID is the episode's identity to every podcast client, and it is
        # deliberately NOT the enclosure URL. When it was the URL, any change of
        # host -- GitHub Releases, or a real podcast host later -- rewrote every
        # GUID and re-issued the entire back catalogue as unheard episodes in
        # every subscriber's app. Derived from the date instead, the audio can
        # move anywhere and subscribers never notice.
        #
        # Changing guid_prefix re-issues the whole back catalogue. Don't.
        sub(it, "guid", f"{guid_prefix}-{meta_path.stem}", isPermaLink="false")
        sub(it, f"{{{ITUNES}}}duration",
            meta.get("duration") or duration_hms(mp3))  # mp3 only for pre-Release episodes
        sub(it, f"{{{ITUNES}}}explicit", pod["explicit"])
        sub(it, f"{{{ITUNES}}}episodeType", "full")

    ET.indent(rss, space="  ")
    xml = ET.tostring(rss, encoding="unicode", xml_declaration=True)
    (repo_dir / "feed.xml").write_text(xml + "\n")
    return len(eps), base


# ---------------------------------------------------------------- git

def git_push(repo_dir, date, dry_run, message=None):
    if not (repo_dir / ".git").exists():
        die(f"{repo_dir} is not a git repo -- run ./setup.sh first")
    run(["git", "add", "-A"], cwd=repo_dir)
    status = run(["git", "status", "--porcelain"], cwd=repo_dir).stdout.strip()
    if not status:
        print("  nothing changed, skipping commit")
        return
    if dry_run:
        print("  [dry run] would commit and push:")
        print("   ", status.replace("\n", "\n    "))
        return
    run(["git", "commit", "-m", message or f"Episode {date}"], cwd=repo_dir)
    run(["git", "push"], cwd=repo_dir)
    print("  pushed")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="build everything locally but do not push")
    ap.add_argument("--audio", help="publish an existing mp3 instead of running TTS")
    ap.add_argument("--script", help="path to a specific script file")
    ap.add_argument("--title", help="episode title")
    ap.add_argument("--date", help="episode date, YYYY-MM-DD (required)")
    ap.add_argument("--feed-only", action="store_true",
                    help="rebuild feed.xml from the episodes already published "
                         "and push it; no TTS, no audio, no new episode")
    args = ap.parse_args()

    need("ffmpeg")
    need("ffprobe")
    need("git")

    cfg = load_config()
    paths = cfg["paths"]
    repo_dir = ROOT / paths["repo_dir"]
    work = ROOT / paths["work_dir"]
    work.mkdir(exist_ok=True)
    (repo_dir / "episodes").mkdir(parents=True, exist_ok=True)

    # Changing feed-wide metadata -- the show title, the GUID scheme -- has to
    # reach the live feed without re-narrating the back catalogue at TTS cost.
    if args.feed_only:
        count, base = build_feed(cfg, repo_dir)
        print(f"  feed.xml rebuilt with {count} episode(s), no audio touched")
        git_push(repo_dir, None, args.dry_run,
                 message="Rebuild feed.xml (metadata only, no new episode)")
        print()
        print(f"  feed:  {base}/feed.xml")
        if args.dry_run:
            print("  (dry run -- nothing was pushed)")
        return

    # The date names the episode's slot in the feed. Defaulting it to "today"
    # once overwrote a published episode when a test ran on the wrong day, so
    # it must always be stated.
    if not args.date:
        die("--date is required; it names the episode file and its feed slot")
    date = args.date
    try:
        dt.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        die(f"--date must be YYYY-MM-DD, got {date!r}")

    # Audio is built in work/ and uploaded as a Release asset. It deliberately
    # never lands in repo/episodes/ any more -- committing it there is what put
    # the feed repo on course for the 1 GB Pages wall. Only the .json sidecar
    # and feed.xml get committed.
    dest = work / f"{date}.mp3"

    # --- get the audio -------------------------------------------------
    if args.audio:
        src = Path(args.audio)
        if not src.is_absolute():
            src = ROOT / src
        if not src.exists():
            die(f"audio file not found: {src}")
        print(f"using existing audio: {src.name}")
        shutil.copy(src, dest)
        description = cfg["podcast"]["subtitle"]
    else:
        script_dir = ROOT / paths["script_dir"]
        if args.script:
            script = Path(args.script)
            if not script.is_absolute():
                script = ROOT / script
        else:
            candidates = sorted(
                [p for p in script_dir.glob("*") if p.suffix in (".md", ".txt")],
                key=lambda p: p.stat().st_mtime, reverse=True)
            if not candidates:
                die(f"no .md or .txt script found in {script_dir}")
            script = candidates[0]
        if not script.exists():
            die(f"script not found: {script}")

        print(f"script: {script.name}")
        text = clean_for_speech(script.read_text())

        # Markers become real silence and stings in the timeline. They are
        # stripped from anything sent to TTS, so the narrator never reads them.
        timeline = audio_post.build_timeline(text)
        spoken = audio_post.strip_markers(text)
        n_marks = sum(1 for kind, _ in timeline if kind != "speech")
        print(f"  {len(spoken)} chars, {n_marks} pause/transition marker(s)")

        parts, idx, seq = [], 0, 1
        for kind, payload in timeline:
            if kind == "speech":
                pieces = chunk(payload, cfg["tts"]["max_chars"])
                # seq must keep climbing across blocks, or the second block
                # overwrites part001.mp3 from the first and the concat repeats
                # a chunk instead of advancing.
                parts.extend(tts(pieces, cfg, work, start=seq))
                seq += len(pieces)
            elif kind == "silence":
                idx += 1
                parts.append(audio_post.silence_file(
                    payload, work / f"gap{idx:03d}.mp3"))
            elif kind == "sting":
                idx += 1
                parts.append(audio_post.sting_file(
                    work / f"sting{idx:03d}.mp3"))

        raw = work / "raw.mp3"
        concat(parts, raw, work)

        print("  mastering: de-ess, EQ, compress, -16 LUFS, room tone, music")
        audio_post.master(raw, dest,
                          intro=audio_post.ASSETS / "intro.wav",
                          outro=audio_post.ASSETS / "outro.wav")
        m = audio_post.report(dest)
        print(f"  {m['lufs']:.2f} LUFS, true peak {m['true_peak']:.2f} dBTP")

        for p in parts:
            Path(p).unlink(missing_ok=True)
        raw.unlink(missing_ok=True)
        description = " ".join(spoken.split()[:60]) + "…"

    dur = duration_hms(dest)
    length = dest.stat().st_size
    print(f"  episode: {dest.name}  {dur}  {length / 1e6:.1f} MB")

    title = (args.title or f"{cfg['podcast']['title']} — "
             f"{dt.datetime.strptime(date, '%Y-%m-%d'):%B %-d, %Y}")

    # Upload BEFORE writing the sidecar and rebuilding the feed. If this fails,
    # the run dies here with the feed untouched -- far better than committing a
    # feed entry whose audio does not exist.
    url = upload_release(dest, date, title, cfg, args.dry_run)

    (repo_dir / "episodes" / f"{date}.json").write_text(json.dumps({
        "title": title,
        "description": description,
        "duration": dur,
        "url": url,
        "length": length,
    }, indent=2) + "\n")

    # --- feed + push ---------------------------------------------------
    count, base = build_feed(cfg, repo_dir)
    print(f"  feed.xml rebuilt with {count} episode(s)")
    git_push(repo_dir, date, args.dry_run)

    print()
    print(f"  feed:  {base}/feed.xml")
    if args.dry_run:
        print("  (dry run -- nothing was pushed)")
    else:
        print("  Pages can take a minute to serve the new file.")


if __name__ == "__main__":
    main()
