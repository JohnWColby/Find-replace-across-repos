# SOURCE_BRANCH Configuration Guide

## Overview

The `SOURCE_BRANCH` configuration determines which branch the script will checkout before making changes. This is useful when you need to update branches other than the default (main/master) branch.

## Configuration

```bash
# In config.sh
SOURCE_BRANCH=""  # Leave empty for default branch
# OR
SOURCE_BRANCH="develop"  # Specify a branch name
```

## How It Works

### With SOURCE_BRANCH="" (Empty - Default Behavior)

1. Clone repository
2. Script uses whatever branch is the default (usually `main` or `master`)
3. Create new branch from that default branch
4. Make changes and commit
5. Push and create PR

**Example flow:**
```
Clone repo → On 'main' branch → Create 'update-strings' from 'main'
```

### With SOURCE_BRANCH="develop"

1. Clone repository
2. **Checkout `develop` branch**
3. **Fetch latest changes from remote**
4. **Check if branch is behind remote**
   - If behind AND no local commits ahead: Pull latest changes
   - If behind BUT has local commits: Skip pull (avoid conflicts)
   - If up to date: Continue
5. Create new branch from `develop`
6. Make changes and commit
7. Push and create PR (targeting `develop`)

**Example flow:**
```
Clone repo → On 'main' → Checkout 'develop' → Fetch → Pull (if safe) → Create 'update-strings' from 'develop'
```

## Common Use Cases

### Use Case 1: Standard Updates to Main

**Scenario:** Update all repos on the main branch

```bash
BRANCH_NAME="update-copyright-2026"
SOURCE_BRANCH=""  # Uses main/master
PR_BASE_BRANCH="main"
```

**Result:** PR from `update-copyright-2026` → `main`

### Use Case 2: Updates to Development Branch

**Scenario:** Update all repos on the develop branch

```bash
BRANCH_NAME="update-dependencies"
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="develop"
```

**Result:** PR from `update-dependencies` → `develop`

### Use Case 3: Hotfix to Production Branch

**Scenario:** Apply urgent fix to production branch

```bash
BRANCH_NAME="hotfix-security-patch"
SOURCE_BRANCH="production"
PR_BASE_BRANCH="production"
```

**Result:** PR from `hotfix-security-patch` → `production`

### Use Case 4: Feature Branch Updates

**Scenario:** Update all repos on a specific feature branch

```bash
BRANCH_NAME="update-feature-x-deps"
SOURCE_BRANCH="feature/big-refactor"
PR_BASE_BRANCH="feature/big-refactor"
```

**Result:** PR from `update-feature-x-deps` → `feature/big-refactor`

## Important Notes

### 1. Automatic Branch Updates

When using `SOURCE_BRANCH`, the script automatically keeps the branch up to date:

**Fetch & Pull Logic:**
1. After checking out the source branch, always fetch latest changes
2. Check if local branch is behind remote
3. If behind:
   - **No local commits ahead**: Safely pull latest changes
   - **Has local commits ahead**: Skip pull to avoid conflicts

**Example output:**
```
[INFO] Checking out source branch: develop
[INFO] ✓ Checked out source branch: develop
[INFO] Fetching latest changes from remote...
[INFO] ✓ Fetched latest changes
[INFO] Checking if branch is up to date...
[INFO] Branch is 3 commit(s) behind remote
[INFO] Pulling latest changes...
[INFO] ✓ Pulled latest changes
```

**When pull is skipped:**
```
[INFO] Branch is 2 commit(s) behind remote
[WARNING] Branch has 1 local commit(s) ahead of remote
[WARNING] Skipping pull to avoid potential conflicts
```

This ensures your changes are based on the latest code without risking merge conflicts.

### 2. SOURCE_BRANCH vs PR_BASE_BRANCH

These should **usually match**:

```bash
# CORRECT - Both set to same branch
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="develop"

# UNUSUAL - Creates PR to different branch than source
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="main"  # Creates PR from develop to main
```

**When they differ:**
- Creates branch from SOURCE_BRANCH
- But PR targets PR_BASE_BRANCH
- Only use if you intentionally want to merge across branches

### 3. Branch Must Exist

If `SOURCE_BRANCH="develop"` but the repo doesn't have a `develop` branch:

- **Python version:** Logs error and skips repo
- **Bash version:** Logs error and skips repo
- **Log entry:** `Failed: Source branch 'develop' not found`

**Solution:** Ensure all repos have the source branch, or use empty string for default.

### 4. Default Branch Varies

Different repos may have different default branches:
- GitHub: Usually `main` (older repos: `master`)
- GitLab: Usually `main` or `master`
- Bitbucket: Usually `master` or `main`

When `SOURCE_BRANCH=""`, the script uses whatever the repo's default is.

## Workflow Examples

### Example 1: Organization-Wide Dependency Update (Develop Branch)

**Goal:** Update React version on all repos' develop branch

**Configuration:**
```bash
# config-react-update.sh
BRANCH_NAME="update-react-18"
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="develop"

declare -a REPLACEMENTS=(
    '"react": "17.0.2"|"react": "18.2.0"'
    '"react-dom": "17.0.2"|"react-dom": "18.2.0"'
)

PR_TITLE="Update React to version 18"
PR_DESCRIPTION="Updates React from 17.0.2 to 18.2.0 on develop branch."
```

**What happens:**
1. Clones each repo
2. Checks out `develop` branch
3. Creates `update-react-18` branch from `develop`
4. Updates package.json files
5. Commits and pushes
6. Creates PR: `update-react-18` → `develop`

### Example 2: Hotfix Across All Production Branches

**Goal:** Apply security fix to production branches

**Configuration:**
```bash
# config-security-hotfix.sh
BRANCH_NAME="hotfix-security-cve-2026-1234"
SOURCE_BRANCH="production"
PR_BASE_BRANCH="production"

declare -a REPLACEMENTS=(
    "vulnerable-package-1.2.3|secure-package-1.2.4"
)

COMMIT_MESSAGE="Security hotfix: CVE-2026-1234

Updates vulnerable-package to secure version.
Critical security patch."

PR_TITLE="[SECURITY] Hotfix: CVE-2026-1234"
```

**What happens:**
1. Clones each repo
2. Checks out `production` branch
3. Creates `hotfix-security-cve-2026-1234` from `production`
4. Updates dependencies
5. Creates PR: `hotfix-security-cve-2026-1234` → `production`

### Example 3: Mixed Repos (Some Have Develop, Some Don't)

**Problem:** Not all repos have a `develop` branch

**Solution 1: Use Default Branch**
```bash
SOURCE_BRANCH=""  # Works for all repos
```

**Solution 2: Two Separate Runs**

Run 1 - Repos with develop:
```bash
# repos-with-develop.txt
repo-a
repo-b
repo-c

# config-develop.sh
REPO_LIST_FILE="repos-with-develop.txt"
SOURCE_BRANCH="develop"
```

Run 2 - Repos without develop:
```bash
# repos-without-develop.txt
repo-x
repo-y

# config-main.sh
REPO_LIST_FILE="repos-without-develop.txt"
SOURCE_BRANCH=""  # Uses main
```

## Troubleshooting

### Error: "Source branch 'develop' not found"

**Cause:** Repository doesn't have the specified source branch

**Solutions:**
1. Remove that repo from `repos.txt`
2. Change `SOURCE_BRANCH=""` to use default
3. Create the branch manually first:
   ```bash
   git clone <repo>
   cd <repo>
   git checkout -b develop
   git push -u origin develop
   ```

### Error: "Already on 'develop'"

**Not an error!** This is normal. The script will:
1. See it's already on the correct branch
2. Continue to create the new branch
3. Proceed normally

### PR Targets Wrong Branch

**Problem:** Created PR from develop to main, but wanted develop to develop

**Cause:** `PR_BASE_BRANCH` doesn't match `SOURCE_BRANCH`

**Fix:**
```bash
# Make sure these match
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="develop"  # Set to same as SOURCE_BRANCH
```

### Branch Not Up to Date

**Problem:** "Branch has X local commits ahead of remote" and pull is skipped

**Cause:** The cloned branch has unpushed local commits

**Why this happens:**
- Someone pushed commits to the repo but didn't push the branch
- Leftover commits from previous work
- Branch was force-pushed

**Solution:**
This is intentional behavior to avoid conflicts. The script will:
- Use the branch as-is (with local commits)
- Create your changes on top
- This is usually fine

**If you want the latest remote version:**
Manually reset the branch or reclone the repository.

### Fetch Failed

**Problem:** "Failed to fetch" warning appears

**Cause:** Network issue or branch doesn't exist on remote

**Impact:** Script continues but may not have latest changes

**Solutions:**
1. Check network connection
2. Verify branch exists on remote: `git ls-remote --heads origin develop`
3. Usually safe to continue - clone is recent

## Best Practices

### 1. Match SOURCE_BRANCH and PR_BASE_BRANCH
```bash
# Good
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="develop"

# Usually not what you want
SOURCE_BRANCH="develop"
PR_BASE_BRANCH="main"
```

### 2. Document in PR Description
```bash
PR_DESCRIPTION="Updates dependencies

**Note:** This PR is based on and targets the develop branch."
```

### 3. Test on One Repo First
```bash
# Create test list
echo "test-repo" > test_repos.txt

# Test configuration
REPO_LIST_FILE="test_repos.txt"
SOURCE_BRANCH="develop"

# Run and verify before full rollout
python3 repo_batch_update.py
```

### 4. Use Descriptive Branch Names
```bash
# Good - Shows intent and source
BRANCH_NAME="develop-update-react-18"

# Less clear
BRANCH_NAME="update-react-18"
```

## Summary

| Configuration | Behavior |
|---------------|----------|
| `SOURCE_BRANCH=""` | Uses default branch (main/master) |
| `SOURCE_BRANCH="develop"` | Checks out develop, creates branch from it |
| `SOURCE_BRANCH="staging"` | Checks out staging, creates branch from it |
| `SOURCE_BRANCH="feature/x"` | Checks out feature/x, creates branch from it |

**Remember:** Make `SOURCE_BRANCH` and `PR_BASE_BRANCH` match for typical workflows!
