#!/usr/bin/env bash
# One-time setup: create the GitHub repo that hosts your podcast feed.
# Safe to re-run -- every step checks before it acts.

set -euo pipefail
cd "$(dirname "$0")"

USER=$(python3 -c "import json;print(json.load(open('config.json'))['github']['username'])")
REPO=$(python3 -c "import json;print(json.load(open('config.json'))['github']['repo'])")
NAME=$(python3 -c "import json;print(json.load(open('config.json'))['podcast']['author'])")
EMAIL=$(python3 -c "import json;print(json.load(open('config.json'))['podcast']['email'])")

say()  { printf "\n\033[1m==> %s\033[0m\n" "$1"; }
ok()   { printf "    \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "    \033[33m!\033[0m %s\n" "$1"; }

# ---------------------------------------------------------- 1. tools
say "Checking tools"

if ! command -v brew >/dev/null 2>&1; then
  warn "Homebrew not found. Install it first:"
  echo '    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  exit 1
fi
ok "homebrew"

for tool in git gh ffmpeg; do
  if command -v "$tool" >/dev/null 2>&1; then
    ok "$tool"
  else
    warn "installing $tool..."
    brew install "$tool"
  fi
done

# ---------------------------------------------------------- 2. git identity
say "Checking git identity"
if [ -z "$(git config --global user.name || true)" ]; then
  git config --global user.name "$NAME";  ok "set user.name to $NAME"
else
  ok "user.name = $(git config --global user.name)"
fi
if [ -z "$(git config --global user.email || true)" ]; then
  git config --global user.email "$EMAIL"; ok "set user.email to $EMAIL"
else
  ok "user.email = $(git config --global user.email)"
fi

# ---------------------------------------------------------- 3. github auth
say "Checking GitHub login"
if gh auth status >/dev/null 2>&1; then
  ok "already logged in as $(gh api user --jq .login)"
else
  warn "opening a browser to log in to GitHub..."
  gh auth login --hostname github.com --git-protocol https --web
fi

ACTUAL=$(gh api user --jq .login)
if [ "$ACTUAL" != "$USER" ]; then
  warn "config.json says username '$USER' but you're logged in as '$ACTUAL'."
  warn "Fix the username in config.json, then re-run this script."
  exit 1
fi

# ---------------------------------------------------------- 4. the repo
say "Setting up $USER/$REPO"
if gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  ok "repo already exists"
else
  gh repo create "$USER/$REPO" --public \
    --description "Feed and audio for The Monday Brief"
  ok "created public repo"
fi

mkdir -p repo/episodes
cd repo

if [ ! -d .git ]; then
  git init -q
  ok "initialized local repo"
else
  ok "local repo already initialized"
fi

git branch -M main

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/$USER/$REPO.git"
else
  git remote add origin "https://github.com/$USER/$REPO.git"
fi

# .nojekyll stops GitHub Pages from mangling the directory
touch .nojekyll
[ -f .gitkeep ] || touch episodes/.gitkeep

git add -A
if [ -n "$(git status --porcelain)" ]; then
  git commit -q -m "Set up podcast hosting"
fi

if ! git rev-parse --verify -q refs/remotes/origin/main >/dev/null || \
   [ -n "$(git rev-list origin/main..main 2>/dev/null)" ]; then
  git push -u origin main
  ok "pushed to GitHub"
else
  ok "nothing new to push"
fi

cd ..

# ---------------------------------------------------------- 5. pages
say "Enabling GitHub Pages"
if gh api "repos/$USER/$REPO/pages" >/dev/null 2>&1; then
  ok "Pages already enabled"
else
  gh api -X POST "repos/$USER/$REPO/pages" \
    -f "source[branch]=main" -f "source[path]=/" >/dev/null
  ok "Pages enabled on main branch"
fi

# ---------------------------------------------------------- done
cat <<EOF

$(printf "\033[1mDone.\033[0m")

Your feed will be served at:
    https://$USER.github.io/$REPO/feed.xml

Next:
  1. export OPENAI_API_KEY="sk-..."      (add to ~/.zshrc to make it stick)
  2. ./publish.py --audio "8-3-26 Podcast.mp3" --date 2026-08-03 --dry-run
  3. listen to repo/episodes/2026-08-03.mp3, then re-run without --dry-run
  4. paste the feed URL into podcasters.spotify.com to claim the show

Pages can take 1-2 minutes to serve for the first time.
EOF
