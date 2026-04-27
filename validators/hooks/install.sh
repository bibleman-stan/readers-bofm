#!/bin/sh
# Install the BofM Reader hooks into .git/hooks/.
# Run from repo root: bash validators/hooks/install.sh

REPO_ROOT=$(git rev-parse --show-toplevel)

cp "$REPO_ROOT/validators/hooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

cp "$REPO_ROOT/validators/hooks/commit-msg" "$REPO_ROOT/.git/hooks/commit-msg"
chmod +x "$REPO_ROOT/.git/hooks/commit-msg"

echo "Hooks installed:"
echo "  .git/hooks/pre-commit  — runs validators/run_all.py --baseline-check"
echo "                            on commits touching canon, corpus, or validators/"
echo "  .git/hooks/commit-msg  — checks for canon extensions in the diff and"
echo "                            requires audit-evidence in the commit message"
echo ""
echo "To bypass (only with explicit authorization): git commit --no-verify"
