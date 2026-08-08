#!/usr/bin/env python3
"""
Audio post-production for the Monday Brief.

Three jobs:

  master()        de-ess, EQ, compress, normalize to -16 LUFS, lay in a noise
                  floor, top and tail with music.
  build_timeline() turn a marker-annotated script into speech blocks
                  interleaved with real silence and transition stings.
  make_assets()   synthesize placeholder intro/outro/transition music so the
                  pipeline is testable before real music is dropped in.

CLI:
  ./audio_post.py make-assets              regenerate assets/ (placeholders)
  ./audio_post.py master in.mp3 out.mp3    run the full mastering chain
  ./audio_post.py measure file.mp3         report integrated LUFS and true peak

Markers understood in scripts (stripped before they reach TTS):
  [[PAUSE]]        0.55s beat
  [[BEAT]]         1.1s  longer hold
  [[TRANSITION]]   section sting with air either side
"""

import array
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

SR = 44100          # output sample rate; music needs more than the 24k voice
BITRATE = "128k"
CHANNELS = 2        # stereo: the voice is mono either way, but summing real
                    # music to mono risks phase cancellation and always costs
                    # width. Dual-mono voice + stereo music is the right trade.

# Music assets get trimmed to these lengths with a fade, so a long track can be
# dropped in without editing it first. Raise them if you want more music.
INTRO_MAX = 7.0     # seconds of intro before the crossfade into speech
OUTRO_MAX = 12.0
STING_MAX = 1.4     # section transitions; this one multiplies by segment count
ASSET_FADE = 0.6    # fade-out applied when an asset is trimmed

# Mastering targets. -16 LUFS is the common podcast delivery target; Spotify
# will re-normalize to about -14 on playback, Apple to -16.
TARGET_I = -16.0
TARGET_TP = -1.5
TARGET_LRA = 11.0

# Room tone level in dBFS. Digital silence between TTS phrases reads as dead
# air; a floor this low is inaudible as noise but stops the gaps sounding
# synthetic.
NOISE_DBFS = -58.0

# Voice chain, applied before loudness measurement.
#   highpass    remove rumble the 24k TTS source doesn't need
#   deesser     tame sibilance BEFORE the presence boost exaggerates it
#   250 Hz cut  clear low-mid mud
#   3.8 kHz     the requested presence lift, kept small
#   acompressor gentle: 2.5:1 with a soft knee, not a limiter
VOICE_CHAIN = (
    "highpass=f=75,"
    "deesser=i=0.12,"
    "equalizer=f=250:t=q:w=1.0:g=-1.5,"
    "equalizer=f=3800:t=q:w=1.2:g=2.5,"
    "acompressor=threshold=-18dB:ratio=2.5:attack=8:release=180:knee=6:makeup=2"
)

MARKERS = {
    "[[PAUSE]]": 0.55,
    "[[BEAT]]": 1.10,
}
MARKER_RE = re.compile(r"\[\[(PAUSE|BEAT|TRANSITION)\]\]")


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(str(c) for c in cmd)}\n{r.stderr[-2000:]}")
    return r


# ------------------------------------------------------------------ synthesis
#
# Karplus-Strong plucked string. Cheap, and unlike a raw sine it has a real
# attack and decay, so the placeholder reads as an instrument rather than a
# test tone. Real music should replace this; see assets/README.

def pluck(freq, dur, sr=SR, decay=0.996, amp=0.45):
    n = int(sr * dur)
    period = max(2, int(sr / freq))
    rng = random.Random(int(freq * 1000))
    buf = [rng.uniform(-1, 1) for _ in range(period)]
    out = []
    for i in range(n):
        cur = buf[i % period]
        nxt = buf[(i + 1) % period]
        smoothed = decay * 0.5 * (cur + nxt)
        buf[i % period] = smoothed
        out.append(cur)
    # gentle exponential tail so notes never click off
    for i in range(n):
        out[i] *= amp * math.exp(-3.0 * i / n)
    return out


def mix_into(track, samples, at, sr=SR):
    start = int(at * sr)
    need = start + len(samples)
    if len(track) < need:
        track.extend([0.0] * (need - len(track)))
    for i, s in enumerate(samples):
        track[start + i] += s


def note(name, octave):
    semis = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    base = semis[name[0]]
    if len(name) > 1 and name[1] == "#":
        base += 1
    return 440.0 * (2 ** ((base - 9) / 12 + (octave - 4)))


def write_wav(path, track, sr=SR):
    peak = max((abs(s) for s in track), default=1.0) or 1.0
    scale = 0.89 / peak
    data = array.array("h", (int(max(-1.0, min(1.0, s * scale)) * 32767) for s in track))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())


def make_assets():
    ASSETS.mkdir(exist_ok=True)

    # Intro: bright, upbeat arpeggio over a I-V-vi-IV feel. ~4.2s.
    intro = []
    prog = [
        [("C", 4), ("E", 4), ("G", 4), ("C", 5)],
        [("G", 3), ("B", 3), ("D", 4), ("G", 4)],
        [("A", 3), ("C", 4), ("E", 4), ("A", 4)],
        [("F", 3), ("A", 3), ("C", 4), ("F", 4)],
    ]
    step = 0.135
    t = 0.0
    for chord in prog:
        for j, (n, o) in enumerate(chord):
            mix_into(intro, pluck(note(n, o), 1.5, amp=0.40), t + j * step)
        # upper octave sparkle on the and-beat
        n, o = chord[-1]
        mix_into(intro, pluck(note(n, o + 1), 0.9, amp=0.20), t + 2.5 * step)
        t += step * 4
    # final accent
    mix_into(intro, pluck(note("C", 5), 2.0, amp=0.50), t)
    mix_into(intro, pluck(note("E", 5), 2.0, amp=0.35), t)
    write_wav(ASSETS / "intro.wav", intro)

    # Outro: same harmony, slower, resolving down. ~5s.
    outro = []
    t = 0.0
    for chord in [prog[3], prog[2], prog[1], prog[0]]:
        for j, (n, o) in enumerate(chord):
            mix_into(outro, pluck(note(n, o), 2.0, amp=0.34), t + j * 0.16)
        t += 0.85
    mix_into(outro, pluck(note("C", 4), 3.0, amp=0.42), t)
    mix_into(outro, pluck(note("G", 4), 3.0, amp=0.28), t)
    mix_into(outro, pluck(note("C", 5), 3.0, amp=0.20), t)
    write_wav(ASSETS / "outro.wav", outro)

    # Transition: two notes, under a second, deliberately plain.
    trans = []
    mix_into(trans, pluck(note("G", 4), 0.7, amp=0.30), 0.0)
    mix_into(trans, pluck(note("C", 5), 0.9, amp=0.26), 0.14)
    write_wav(ASSETS / "transition.wav", trans)

    (ASSETS / "README.md").write_text(
        "# assets\n\n"
        "`intro.wav`, `outro.wav`, `transition.wav` are SYNTHESIZED PLACEHOLDERS,\n"
        "generated by `audio_post.py make-assets`. They are functional, not good.\n\n"
        "Replace them with real music. Anything here is used as-is, so match the\n"
        "filenames and keep the intro under about six seconds.\n\n"
        "Genuinely free sources, check the licence on each track:\n\n"
        "- Uppbeat (uppbeat.io) free tier, no attribution on most tracks\n"
        "- Pixabay Music (pixabay.com/music) Pixabay licence\n"
        "- YouTube Audio Library, filter to no-attribution\n"
        "- Free Music Archive (freemusicarchive.org), filter by CC licence\n"
        "- Kevin MacLeod (incompetech.com), CC-BY, attribution required\n\n"
        "Do not use commercial music. The feed is public and hosted on GitHub.\n"
    )
    return [ASSETS / "intro.wav", ASSETS / "outro.wav", ASSETS / "transition.wav"]


# ------------------------------------------------------------------ timeline

def build_timeline(text):
    """Split marker-annotated script text into an ordered list of parts.

    Returns [("speech", str) | ("silence", seconds) | ("sting", None), ...]
    Speech blocks come back with markers removed, ready for TTS.
    """
    parts, pos = [], 0
    for m in MARKER_RE.finditer(text):
        chunk = text[pos:m.start()].strip()
        if chunk:
            parts.append(("speech", chunk))
        tok = m.group(0)
        if tok == "[[TRANSITION]]":
            parts.append(("sting", None))
        else:
            parts.append(("silence", MARKERS[tok]))
        pos = m.end()
    tail = text[pos:].strip()
    if tail:
        parts.append(("speech", tail))
    return parts


def strip_markers(text):
    """Belt and braces: never let a marker reach the narrator."""
    return re.sub(r"\n{3,}", "\n\n", MARKER_RE.sub("", text)).strip()


def silence_file(seconds, dest):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i",
         f"anullsrc=r={SR}:cl=stereo", "-t", f"{seconds:.3f}",
         "-c:a", "libmp3lame", "-b:a", BITRATE,
         "-ar", str(SR), "-ac", str(CHANNELS), str(dest)])
    return dest


def sting_file(dest, lufs=None):
    """Section transition, trimmed to STING_MAX. Six of these in an episode,
    so an untrimmed three-second track adds nearly twenty seconds of music."""
    src = ASSETS / "transition.wav"
    if not src.exists():
        return silence_file(0.9, dest)
    prep_asset(src, dest, lufs if lufs is not None else TARGET_I + 1.0,
               max_dur=STING_MAX, fade=0.35)
    return dest


# ------------------------------------------------------------------ mastering

def measure(path):
    """Pass one: measure loudness after the voice chain."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         f"{VOICE_CHAIN},loudnorm=I={TARGET_I}:TP={TARGET_TP}:"
         f"LRA={TARGET_LRA}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    blob = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not blob:
        raise RuntimeError("could not parse loudnorm output:\n" + r.stderr[-1500:])
    return json.loads(blob.group(0))


def _loudnorm_args(path, pre=""):
    """Two-pass loudnorm: measure, then return the corrected filter string."""
    chain = f"{pre}," if pre else ""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         f"{chain}loudnorm=I={TARGET_I}:TP={TARGET_TP}:"
         f"LRA={TARGET_LRA}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    blob = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not blob:
        raise RuntimeError("could not parse loudnorm output:\n" + r.stderr[-1500:])
    m = json.loads(blob.group(0))
    # linear=true preserves dynamics, but falls back to dynamic mode if the
    # required gain would clip. Either way TP is respected.
    return (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}"
            f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
            f":offset={m['target_offset']}:linear=true:print_format=summary")


def prep_asset(src, dest, lufs, max_dur=None, fade=ASSET_FADE):
    """Normalize a music asset, and trim it with a fade if it runs long.

    Loudness-matching matters more than it sounds: dropped-in tracks arrive
    anywhere from -8 to -20 LUFS, and an unmatched bed either buries the voice
    or vanishes under it.
    """
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    blob = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    gain = lufs - float(json.loads(blob.group(0))["input_i"])

    chain = [f"volume={gain:.2f}dB"]
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(src)],
        capture_output=True, text=True).stdout.strip())
    trimmed = False
    if max_dur and dur > max_dur:
        chain.append(f"atrim=0:{max_dur}")
        chain.append(f"afade=t=out:st={max(0.0, max_dur - fade):.3f}:d={fade}")
        trimmed = True
    chain.append(f"aformat=sample_rates={SR}:channel_layouts=stereo")

    run(["ffmpeg", "-y", "-i", str(src), "-af", ",".join(chain),
         "-ar", str(SR), "-ac", str(CHANNELS), str(dest)])
    return dest, dur, trimmed


def master(src, dest, intro=None, outro=None, noise=True):
    """Voice chain -> room tone -> music -> final loudness pass.

    The final normalize runs on the ASSEMBLED programme, not on the voice
    alone. Crossfading music into an already-normalized body shifts integrated
    loudness off target and can push true peak above 0 dBFS.
    """
    src, dest = Path(src), Path(dest)
    # Scratch goes to the system temp dir, not next to the output. The output
    # often lives in iCloud Drive, where deleting our own scratch files can be
    # refused outright and where sync would churn on every intermediate.
    work = Path(tempfile.mkdtemp(prefix="mondaybrief-master-"))

    # --- 1. voice chain + provisional levelling + room tone -----------------
    ln = _loudnorm_args(src, VOICE_CHAIN)
    body = work / "body.wav"
    stereo = f"aformat=sample_rates={SR}:channel_layouts=stereo"
    if noise:
        amp = 10 ** (NOISE_DBFS / 20.0)
        fc = (f"[0:a]{VOICE_CHAIN},{ln},aresample={SR},{stereo}[v];"
              f"anoisesrc=c=pink:r={SR}:a={amp:.6f}[n];"
              f"[n]highpass=f=200,lowpass=f=6000,{stereo}[nf];"
              f"[v][nf]amix=inputs=2:duration=first:normalize=0[out]")
        run(["ffmpeg", "-y", "-i", str(src), "-filter_complex", fc,
             "-map", "[out]", "-ar", str(SR), "-ac", str(CHANNELS), str(body)])
    else:
        run(["ffmpeg", "-y", "-i", str(src), "-af",
             f"{VOICE_CHAIN},{ln},aresample={SR},{stereo}",
             "-ar", str(SR), "-ac", str(CHANNELS), str(body)])

    # --- 2. music, matched to the voice so neither jumps --------------------
    cur = body
    for asset, xf, first, cap in ((intro, 1.2, True, INTRO_MAX),
                                  (outro, 1.5, False, OUTRO_MAX)):
        if not (asset and Path(asset).exists()):
            continue
        tag = "in" if first else "out"
        bed, orig, trimmed = prep_asset(
            asset, work / f"bed_{tag}.wav", TARGET_I + 1.0, max_dur=cap)
        if trimmed:
            print(f"    {Path(asset).name}: {orig:.1f}s trimmed to {cap:.1f}s")
        out = work / f"asm_{tag}.wav"
        a, b = (bed, cur) if first else (cur, bed)
        run(["ffmpeg", "-y", "-i", str(a), "-i", str(b), "-filter_complex",
             f"[0:a]{stereo}[x];[1:a]{stereo}[y];"
             f"[x][y]acrossfade=d={xf}:c1=tri:c2=tri[out]",
             "-map", "[out]", "-ar", str(SR), "-ac", str(CHANNELS), str(out)])
        cur = out

    # --- 3. final pass on the whole programme, plus a safety limiter --------
    final_ln = _loudnorm_args(cur)
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(cur), "-af",
         # Ceiling at -2.5 dBFS sample peak, not -1.0. Inter-sample peaks and
         # MP3 encoder overshoot both push true peak up by roughly a dB after
         # this point; measured output lands near -1.5 dBTP as intended.
         f"{final_ln},alimiter=limit=0.750:level=disabled,aresample={SR}",
         "-c:a", "libmp3lame", "-b:a", BITRATE,
         "-ar", str(SR), "-ac", str(CHANNELS), str(dest)])

    shutil.rmtree(work, ignore_errors=True)
    return dest


def report(path):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path),
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    blob = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    d = json.loads(blob.group(0))
    return {"lufs": float(d["input_i"]), "true_peak": float(d["input_tp"]),
            "lra": float(d["input_lra"])}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "make-assets":
        for p in make_assets():
            print(f"  wrote {p.relative_to(ROOT)}")
    elif cmd == "measure":
        print(json.dumps(report(sys.argv[2]), indent=2))
    elif cmd == "master":
        src, dest = sys.argv[2], sys.argv[3]
        before = report(src)
        master(src, dest,
               intro=ASSETS / "intro.wav", outro=ASSETS / "outro.wav")
        after = report(dest)
        print(f"  before  {before['lufs']:7.2f} LUFS   peak {before['true_peak']:6.2f} dBTP   LRA {before['lra']:.1f}")
        print(f"  after   {after['lufs']:7.2f} LUFS   peak {after['true_peak']:6.2f} dBTP   LRA {after['lra']:.1f}")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
