#!/bin/bash
# Auto-commit and push script for Flask Admin Pro

if [ $# -eq 0 ]; then
    echo "Usage: ./git-push.sh \"commit message\""
    echo "Example: ./git-push.sh \"fix: resolve table creation issue\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo "🔄 Adding all changes..."
git add .

echo "📝 Committing with message: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE"

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done! Changes pushed to GitHub."
