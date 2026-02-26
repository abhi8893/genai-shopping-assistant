# Defaults to .local/{branch_name}/PR_SUMMARY.md
FILE=${1:-.local/$(git branch --show-current)/PR_SUMMARY.md}

TITLE=$(sed -n -e '/<TITLE>/,/<\/TITLE>/p' -e '/<\/TITLE>/q' "$FILE" | sed '1d;$d')
BODY=$(sed -n -e '/<BODY>/,/<\/BODY>/p' -e '/<\/BODY>/q' "$FILE" | sed '1d;$d')

echo "Title: $TITLE"
echo "Body: $BODY"

gh pr create --title "$TITLE" --body "$BODY"

