#!/usr/bin/env bash

# ---------------------------------------------------------
# commit.sh – add all changes, commit, and push.
#
# Usage:
#   ./commit.sh "Your commit message"
#
# The script:
#   1. Verifies a commit message was supplied.
#   2. Runs `git add .` to stage all changes.
#   3. Commits using the supplied message.
#   4. Pushes the current branch to the default remote.
# ---------------------------------------------------------

# Exit immediately if any command fails.
set -e

# Ensure a commit message is provided.
if [ $# -eq 0 ]; then
    echo "Error: No commit message supplied."
    echo "Usage: $0 \"Your commit message\""
    exit 1
fi

# Combine all arguments into a single message (allows spaces without quotes).
COMMIT_MSG="$*"

# Stage all changes.
git add .

# Create the commit.
git commit -m "$COMMIT_MSG"

# Push the current branch to the remote repository.
git push

echo "✅ Changes have been added, committed, and pushed."
