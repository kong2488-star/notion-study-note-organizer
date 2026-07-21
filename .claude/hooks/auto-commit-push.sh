#!/usr/bin/env bash
# Claude Code Stop hook. Must ALWAYS exit 0 so it never blocks Claude Code
# from ending its turn.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
cd "$REPO_DIR" 2>/dev/null || exit 0

LOG_DIR="$REPO_DIR/.claude/hooks/log"
LOG_FILE="$LOG_DIR/auto-commit-push.log"
mkdir -p "$LOG_DIR" 2>/dev/null
log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"; }

git rev-parse --is-inside-work-tree > /dev/null 2>&1 || exit 0

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [ "$CURRENT_BRANCH" != "master" ]; then
  log "on branch '$CURRENT_BRANCH', not master; skipping"
  exit 0
fi

# Nothing to do on a clean tree — skip pytest entirely rather than run it every turn.
if [ -z "$(git status --porcelain)" ]; then
  exit 0
fi

log "uncommitted changes detected; running python -m pytest"
if ! python -m pytest --basetemp="$LOCALAPPDATA/claude_pytest_tmp" >> "$LOG_FILE" 2>&1; then
  log "pytest FAILED; leaving changes uncommitted"
  echo "auto-commit-push: tests failed, changes left uncommitted (see .claude/hooks/log/auto-commit-push.log)"
  exit 0
fi
log "pytest passed"

git add -A

CHANGED_FILES="$(git diff --cached --name-only | tr '\n' ' ')"
COMMIT_MSG="chore(auto): claude code auto-commit after tests pass - ${CHANGED_FILES:0:200}"

if ! git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1; then
  log "git commit FAILED"
  echo "auto-commit-push: commit failed (see log)"
  exit 0
fi
log "committed: $COMMIT_MSG"

if ! git push origin master >> "$LOG_FILE" 2>&1; then
  log "git push FAILED (commit is local-only; resolve manually next session)"
  echo "auto-commit-push: committed locally but push to origin/master failed (see log)"
  exit 0
fi
log "pushed to origin/master"
echo "auto-commit-push: committed and pushed to origin/master"
exit 0
