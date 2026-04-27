#!/bin/sh
# Install the BofM Reader pre-commit hook into .git/hooks/.
# Run from repo root: bash validators/hooks/install.sh

REPO_ROOT=$(git rev-parse --show-toplevel)
cp "$REPO_ROOT/validators/hooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"
echo "Pre-commit hook installed at .git/hooks/pre-commit"
echo "It will run validators/run_all.py --baseline-check on commits"
echo "that touch the canon, corpus, or validators/."
echo ""
echo "To bypass (only with explicit authorization): git commit --no-verify"
