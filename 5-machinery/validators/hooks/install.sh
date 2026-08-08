#!/bin/sh
# Install the BofM Reader hooks into .git/hooks/.
# Run from repo root: bash 5-machinery/validators/hooks/install.sh

REPO_ROOT=$(git rev-parse --show-toplevel)

cp "$REPO_ROOT/validators/hooks/pre-commit" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

cp "$REPO_ROOT/validators/hooks/commit-msg" "$REPO_ROOT/.git/hooks/commit-msg"
chmod +x "$REPO_ROOT/.git/hooks/commit-msg"

echo "Hooks installed:"
echo "  .git/hooks/pre-commit  — runs 5-machinery/validators/run_all.py --baseline-check"
echo "                            on commits touching canon, corpus, or 5-machinery/validators/"
echo "  .git/hooks/commit-msg  — runs two checks against the staged diff +"
echo "                            commit message:"
echo "                              (1) check_canon_extensions.py — blocks"
echo "                                  canon extensions without audit evidence"
echo "                              (2) check_commit_scope.py — blocks cross-"
echo "                                  category staging-scope leaks (audio/"
echo "                                  files swept into canon commits, etc.)"
echo ""
echo "To bypass (only with explicit authorization): git commit --no-verify"
