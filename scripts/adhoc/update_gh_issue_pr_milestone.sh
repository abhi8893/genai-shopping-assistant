#!/usr/bin/env bash
OWNER=abhi8893
REPO=genai-shopping-assistant
MILESTONE_TITLE="Release (Project) v0.1.0"
CHUNK=5

echo "Fetching milestone id…"

MID=$(gh api graphql -f query="
query {
  repository(owner:\"$OWNER\", name:\"$REPO\") {
    milestones(first:20) { nodes { title id } }
  }
}" --jq ".data.repository.milestones.nodes[] | select(.title==\"$MILESTONE_TITLE\") | .id")

echo "Milestone id: $MID"

echo "Fetching issue ids without milestone…"

ISSUE_IDS=()
while IFS= read -r id; do
  ISSUE_IDS+=("$id")
done < <(
gh api graphql -f query="
query {
  repository(owner:\"$OWNER\", name:\"$REPO\") {
    issues(first:100, states:CLOSED) { nodes { id milestone { id } } }
  }
}" --jq '
.data.repository.issues.nodes[]
| select(.milestone==null)
| .id
'
)

echo "Fetching PR ids without milestone…"

PR_IDS=()
while IFS= read -r id; do
  PR_IDS+=("$id")
done < <(
gh api graphql -f query="
query {
  repository(owner:\"$OWNER\", name:\"$REPO\") {
    pullRequests(first:100, states:MERGED) { nodes { id milestone { id } } }
  }
}" --jq '
.data.repository.pullRequests.nodes[]
| select(.milestone==null)
| .id
'
)

echo "Total issues to update: ${#ISSUE_IDS[@]}"
echo "Total PRs to update: ${#PR_IDS[@]}"

TOTAL=${#ISSUE_IDS[@]}
for ((start=0; start<TOTAL; start+=CHUNK)); do
  echo "Updating issue batch starting at $start"

  MUT="mutation{"
  for ((j=start; j<start+CHUNK && j<TOTAL; j++)); do
    MUT+="i$j:updateIssue(input:{id:\"${ISSUE_IDS[j]}\", milestoneId:\"$MID\"}){issue{id}} "
  done
  MUT+="}"

  gh api graphql -f query="$MUT"
done

TOTAL=${#PR_IDS[@]}
for ((start=0; start<TOTAL; start+=CHUNK)); do
  echo "Updating PR batch starting at $start"

  MUT="mutation{"
  for ((j=start; j<start+CHUNK && j<TOTAL; j++)); do
    MUT+="i$j:updatePullRequest(input:{pullRequestId:\"${PR_IDS[j]}\", milestoneId:\"$MID\"}){pullRequest{id}} "
  done
  MUT+="}"

  gh api graphql -f query="$MUT"
done

echo "Done."
