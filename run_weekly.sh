#!/usr/bin/env zsh
# Wrapper for the launchd job -- launchd doesn't source shell rc files,
# so pull OPENAI_API_KEY from ~/.zshrc here instead of hardcoding it in the plist.
set -euo pipefail

source "$HOME/.zshrc"

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

cd "$(dirname "$0")"
exec ./publish.py
