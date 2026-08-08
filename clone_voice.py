#!/usr/bin/env python3
"""
Clone your voice at ElevenLabs and wire it into the Monday Brief.

One-time setup. Needs the official SDK for this step only:

    pip3 install elevenlabs

The weekly pipeline stays dependency-free; publish.py talks to ElevenLabs over
plain REST once the voice ID is in config.json.

  ./clone_voice.py --record-guide          what to record, and how
  ./clone_voice.py --name "Tyler" recordings/*.wav
  ./clone_voice.py --list                  voices already on the account
  ./clone_voice.py --set-config VOICE_ID   point the podcast at a voice

Instant Voice Cloning is a few minutes of audio and is usually good enough for
narration. Professional Voice Cloning wants ~30 minutes, takes hours to train,
and is noticeably better on long reads. Start instant; upgrade if the seams
show over twelve minutes.
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"

GUIDE = """
Recording a clone source
========================

Quality of the clone is set almost entirely by the source audio. Three minutes
of clean recording beats thirty minutes of noisy.

WHAT TO RECORD
  Read your own script. scripts-private/ has one. Reading the actual show gets
  you a clone tuned to the register you actually publish in, rather than to
  whatever a generic paragraph pulled out of you.

  Aim for three to five minutes for an instant clone. More is not better past
  that point; consistency is.

HOW TO RECORD
  Quiet room. Soft furnishings help, bare walls hurt. Turn off any fan or air
  conditioning you can hear once you start listening for it.

  Phone voice memos are acceptable. A USB microphone is better. Either way,
  four to six inches from your mouth, slightly off-axis so plosives do not
  thump the capsule.

  Record one continuous take if you can. Do not edit out breaths. The clone
  learns your pacing from them, and a de-breathed source produces a narrator
  that sounds like it never needs air.

  Do not apply noise reduction, EQ, compression, or normalization. Send it dry.
  The pipeline masters the output; processing the input just teaches the clone
  your plugin chain.

WHAT TO AVOID
  Background music or television. Other voices, even faint ones. Clipping, so
  watch the meters and leave headroom. Wildly varying distance from the mic.

  Do not perform. Read at the pace and warmth you want the show to have. The
  clone reproduces the delivery you give it, so a bored source read produces a
  bored narrator for every episode after.

FORMAT
  WAV or MP3, mono or stereo, any common sample rate. Keep each file under
  10 MB or split into several; multiple files are supported and help.
"""


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def client():
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        die("the elevenlabs SDK is not installed. Run: pip3 install elevenlabs")
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        die("ELEVENLABS_API_KEY is not set. Add it to ~/.zshrc:\n"
            "  echo 'export ELEVENLABS_API_KEY=\"...\"' >> ~/.zshrc && source ~/.zshrc")
    from elevenlabs.client import ElevenLabs
    return ElevenLabs(api_key=key)


def set_config(voice_id, model="eleven_multilingual_v2"):
    cfg = json.loads(CONFIG.read_text())
    old = dict(cfg["tts"])
    cfg["tts"] = {
        "provider": "elevenlabs",
        "model": model,
        "voice": voice_id,
        "max_chars": 4000,
        "voice_settings": {
            # Higher stability suits a twelve-minute read; low stability drifts
            # in tone across a long script. Style at zero keeps it level, which
            # is the register the show is written for.
            "stability": 0.55,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    cfg["tts"]["_previous_openai"] = {k: v for k, v in old.items()
                                      if k != "_previous_openai"}
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")
    print(f"  config.json now points at elevenlabs voice {voice_id}")
    print( "  previous OpenAI settings kept under tts._previous_openai")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="audio files to clone from")
    ap.add_argument("--name", default="Tyler Dancy")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--set-config", metavar="VOICE_ID")
    ap.add_argument("--record-guide", action="store_true")
    ap.add_argument("--model", default="eleven_multilingual_v2")
    args = ap.parse_args()

    if args.record_guide:
        print(GUIDE)
        return 0
    if args.set_config:
        set_config(args.set_config, args.model)
        return 0

    el = client()

    if args.list:
        for v in el.voices.get_all().voices:
            print(f"  {v.voice_id}  {v.name}  ({getattr(v, 'category', '')})")
        return 0

    if not args.files:
        die("give me audio files, or --record-guide to see what to record")
    paths = [Path(f) for f in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        die(f"not found: {', '.join(str(p) for p in missing)}")

    total = sum(p.stat().st_size for p in paths) / 1e6
    print(f"  cloning from {len(paths)} file(s), {total:.1f} MB total")
    for p in paths:
        print(f"    {p.name}  {p.stat().st_size/1e6:.1f} MB")
        if p.stat().st_size > 10e6:
            die(f"{p.name} exceeds the 10 MB per-file limit; split it")

    from io import BytesIO
    voice = el.voices.ivc.create(
        name=args.name,
        files=[BytesIO(p.read_bytes()) for p in paths])
    print(f"\n  voice created: {voice.voice_id}")
    print(f"  wiring it into config.json…")
    set_config(voice.voice_id, args.model)
    print(f"\n  now audition it:  ./voice_sample.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
