#!/usr/bin/env python3
"""
Does this OpenAI account have custom-voice access?

Custom voices are gated to "eligible customers" via OpenAI sales. The endpoints
are documented and real, but a standard pay-as-you-go key is usually refused.
This asks the API directly instead of guessing. Read-only: it lists, it never
uploads or creates anything.

  ./check_custom_voice.py
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.openai.com/v1"


def get(path):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("error: OPENAI_API_KEY is not set. Run: source ~/.zshrc",
              file=sys.stderr)
        sys.exit(1)
    req = urllib.request.Request(
        f"{BASE}{path}", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except ValueError:
            pass
        return e.code, body
    except Exception as e:
        return None, str(e)


def main():
    for label, path in (("voices", "/audio/voices"),
                        ("voice consents", "/audio/voice_consents")):
        status, body = get(path)
        print(f"GET /audio/{path.split('/')[-1]}  ->  {status}")
        if status == 200:
            items = body.get("data", []) if isinstance(body, dict) else []
            print(f"  ACCESS GRANTED. {len(items)} {label} on this account.")
            for it in items[:10]:
                print(f"    {it.get('id')}  {it.get('name', '')}")
        elif status in (401,):
            print("  bad or expired API key.")
        elif status in (403, 404):
            msg = ""
            if isinstance(body, dict):
                msg = body.get("error", {}).get("message", "")
            print(f"  NOT AVAILABLE on this account. {msg}")
        else:
            print(f"  unexpected: {str(body)[:300]}")
        print()

    print("If both came back 403 or 404, custom voices are not enabled for")
    print("this key and no amount of client-side code will change that. The")
    print("route is OpenAI sales, or a different provider.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
