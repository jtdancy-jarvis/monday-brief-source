#!/usr/bin/env python3
"""
Audition the narrator without burning a full episode.

Reads model / voice / instructions straight from config.json, narrates about
thirty seconds of real script, and runs the same mastering chain the episode
gets. Costs a fraction of a cent per run.

  ./voice_sample.py                    30s from this week's private script
  ./voice_sample.py --words 60         shorter or longer
  ./voice_sample.py --text "..."       your own line
  ./voice_sample.py --music            include intro/outro beds
  ./voice_sample.py --raw              skip mastering, hear the TTS naked
  ./voice_sample.py --voice nova       override the configured voice
  ./voice_sample.py --compare          one file per voice, all six

`instructions` in config.json only does anything on gpt-4o-mini-tts. On tts-1
it is ignored silently, which is the usual reason a changed instruction seems
to have no effect.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import audio_post

ROOT = Path(__file__).resolve().parent
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
INSTRUCTION_MODELS = ("gpt-4o-mini-tts",)


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def pick_text(words):
    """Grab a representative stretch of real script, markers stripped."""
    for d in ("scripts-private", "scripts"):
        cand = sorted((ROOT / d).glob("*.txt"), key=lambda p: p.stat().st_mtime,
                      reverse=True) + \
               sorted((ROOT / d).glob("*.md"), key=lambda p: p.stat().st_mtime,
                      reverse=True)
        if cand:
            body = audio_post.strip_markers(cand[0].read_text())
            paras = [p for p in body.split("\n\n") if len(p.split()) > 15]
            if paras:
                # Skip the cold open; the body register is more representative.
                # Accumulate whole paragraphs so the sample keeps its paragraph
                # breaks, which are the pacing cue the narrator responds to.
                picked, total = [], 0
                for p in paras[1:] or paras:
                    picked.append(p)
                    total += len(p.split())
                    if total >= words:
                        break
                # Trim the overshoot off the last paragraph, cutting only at a
                # sentence end so the sample never stops mid-thought.
                if total > words and len(picked) > 1:
                    over = total - words
                    tail = re.split(r"(?<=[.!?])\s+", picked[-1])
                    while tail and over > 0:
                        over -= len(tail[-1].split())
                        tail.pop()
                    picked[-1] = " ".join(tail)
                    if not picked[-1]:
                        picked.pop()
                return "\n\n".join(picked), cand[0].name
    return ("Good morning. This is a test of the narrator, at roughly the pace "
            "and register the show is written for."), "built-in"


def speak(text, cfg, voice, dest):
    """Delegate to publish.py so the audition uses the exact same code path as
    a real episode. One provider branch, not two that can drift apart."""
    import publish
    full = {"tts": dict(cfg)}
    full["tts"]["voice"] = voice
    if cfg.get("instructions") and cfg.get("provider", "openai") == "openai" \
            and cfg.get("model") not in INSTRUCTION_MODELS:
        print(f"  ! instructions are set but model is {cfg.get('model')!r}, "
              f"which ignores them silently. Use gpt-4o-mini-tts.")
    parts = publish.tts([text], full, dest.parent, start=0)
    Path(parts[0]).replace(dest)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", type=int, default=75,
                    help="roughly 150 wpm, so 75 words is about 30 seconds")
    ap.add_argument("--text")
    ap.add_argument("--voice")
    ap.add_argument("--music", action="store_true")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "config.json").read_text())["tts"]
    text, origin = (args.text, "argument") if args.text else pick_text(args.words)

    provider = cfg.get("provider", "openai")
    print(f"  provider     {provider}")
    print(f"  model        {cfg.get('model')}")
    print(f"  voice        {cfg.get('voice')}")
    if provider == "openai":
        print(f"  instructions {cfg.get('instructions') or '(none set)'}")
    print(f"  text from    {origin}  ({len(text.split())} words)")
    print()

    if args.compare and provider != "openai":
        die("--compare only applies to the OpenAI preset voices. For "
            "ElevenLabs, use ./clone_voice.py --list and pass --voice ID.")
    voices = VOICES if args.compare else [args.voice or cfg["voice"]]
    for v in voices:
        raw = ROOT / f".sample_raw_{v}.mp3"
        out = ROOT / (f"voice-sample-{v}.mp3" if args.compare
                      else "voice-sample.mp3")
        print(f"  {v}: narrating…")
        speak(text, cfg, v, raw)
        if args.raw:
            raw.replace(out)
        else:
            assets = audio_post.ASSETS
            audio_post.master(
                raw, out,
                intro=assets / "intro.wav" if args.music else None,
                outro=assets / "outro.wav" if args.music else None)
            raw.unlink(missing_ok=True)
        m = audio_post.report(out)
        print(f"     -> {out.name}  {m['lufs']:.2f} LUFS, "
              f"peak {m['true_peak']:.2f} dBTP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
