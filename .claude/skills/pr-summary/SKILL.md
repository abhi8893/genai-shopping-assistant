---
name: pr-summary
description: Generate a structured PR summary document for the current branch. Analyzes git changes, creates markdown summary with TITLE/BODY sections, code examples, and saves to .local/{branch_name}/PR_SUMMARY.md
context: fork
agent: general-purpose
allowed-tools: Bash(git *)
---

# Pull Request Summary Generator

Generate a comprehensive, structured PR summary document for the current branch following the project's PR summary format defined in `.claude/rules/pr-summary-format.md`.

## Workflow

### 1. Get Branch Information

Get the current branch name and analyze changes:

```bash
branch_name=$(git branch --show-current)
git log main..HEAD --oneline
git diff main...HEAD --stat
git diff HEAD~1..HEAD
```

### 2. Analyze Changes

Examine the changes to understand:
- **What** changed (files, functions, configuration)
- **Why** it changed (purpose, motivation)
- **How** it impacts the system (benefits, testing)

Read modified files to understand the full context of changes.

### 3. Create Directory

```bash
mkdir -p .local/$branch_name
```

### 4. Generate Summary Document

Create a structured markdown document at `.local/{branch_name}/PR_SUMMARY.md` with:

#### Required Structure

```markdown
<TITLE>
{Concise PR title describing the main change}
</TITLE>

<BODY>
## Summary

{2-3 sentence overview of what changed and why}

## Changes

### 1. {Component/File/Area Name}

#### {Subsection describing specific change}

{Description with context}

```{language}
{Code examples showing key changes or before/after}
```

### 2. {Next Component/Area}

{Continue for each major change area}

## Benefits

1. **{Benefit Category}**: {Description}
2. **{Benefit Category}**: {Description}

## Testing

{Instructions for testing the changes}

```bash
{Example commands}
```

</BODY>
```

#### Formatting Requirements

- Use `##` for major sections (Summary, Changes, Benefits, Testing)
- Use `###` for change areas (numbered: 1., 2., 3.)
- Use `####` for subsections within change areas
- Use fenced code blocks with language tags: ` ```bash `, ` ```python `, ` ```yaml `, etc.
- Use inline backticks for: commands, file paths, variable names, flags
- Show before/after for refactorings using comments or separate blocks

#### Content Guidelines

**Summary Section:**
- 2-3 sentences maximum
- Focus on "what" and "why" at high level
- Mention primary motivation

**Changes Section:**
- Group related changes together
- Number major areas (1., 2., 3.)
- Include code examples for significant changes
- Reference files with relative paths
- Show before/after for modifications

**Benefits Section:**
- List concrete benefits
- Use bold category labels: **Performance**, **Maintainability**, etc.

**Testing Section:**
- Provide clear verification instructions
- Include copy-pastable commands
- Show expected outcomes

## Important Notes

- Keep concise but comprehensive
- Focus on changes that matter to reviewers
- Highlight breaking changes or migration steps
- Use consistent terminology from the codebase
- Include all language tags for code blocks
- Follow the exact `<TITLE></TITLE>` and `<BODY></BODY>` format

## Reference

Full format specification: `.claude/rules/pr-summary-format.md`

## Output

Save the generated summary to `.local/{branch_name}/PR_SUMMARY.md` and confirm the file path to the user.
