# Defaults to .local/{branch_name}/PR_SUMMARY.md
FILE=${1:-.local/$(git branch --show-current)/PR_SUMMARY.md}

TITLE=$(sed -n '/<TITLE>/,/<\/TITLE>/p' "$FILE" | sed '1d;$d')
BODY=$(sed -n '/<BODY>/,/<\/BODY>/p' "$FILE" | sed '1d;$d')

echo "Title: $TITLE"
echo "Body: $BODY"

gh pr create --title "$TITLE" --body "$BODY"

