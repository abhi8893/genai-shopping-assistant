# `/pr-summary` Skill

A custom Claude Code skill that generates structured PR summary documents for the current branch.

## Usage

### Manual Invocation

```bash
/pr-summary
```

### Automatic Invocation

Claude will automatically use this skill when you ask:
- "Generate a PR summary"
- "Create a PR summary document"
- "Summarize the changes in this branch"
- "Prepare PR documentation"

## What It Does

1. **Analyzes Changes**: Examines git commits and diffs comparing current branch to `main`
2. **Generates Summary**: Creates a structured markdown document with:
   - Title and overview
   - Detailed change descriptions
   - Code examples with syntax highlighting
   - Benefits analysis
   - Testing instructions
3. **Saves Document**: Writes to `.local/{branch_name}/PR_SUMMARY.md`

## Output Format

The generated summary follows this structure:

```markdown
<TITLE>
Concise PR title
</TITLE>

<BODY>
## Summary
Brief overview (2-3 sentences)

## Changes
### 1. Component/Area Name
Detailed changes with code examples

### 2. Next Component
More changes...

## Benefits
Concrete benefits of the changes

## Testing
How to test the changes
</BODY>
```

## Files

- `SKILL.md` - Main skill definition (Claude Code reads this)
- `example-output.md` - Example of expected output format
- `README.md` - This file

## Related

- `.claude/rules/pr-summary-format.md` - Complete format specification
- `.local/{branch_name}/PR_SUMMARY.md` - Where outputs are saved

## Tips

- The skill works best on branches with clear, focused changes
- Ensure your commits have descriptive messages for better summaries
- The skill analyzes both individual commits and overall diff from `main`
- All code blocks use proper language tags for syntax highlighting
