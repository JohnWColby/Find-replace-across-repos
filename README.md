# Repo Batch Update Script

A powerful bash script for automating bulk updates across multiple Git repositories. Clone repos, create branches, perform find/replace operations, commit changes, push to remote, and optionally create Pull Requests—all in one command.

## Features

- ✅ Clone multiple repositories from a list
- ✅ Create branches with custom names
- ✅ Perform find/replace operations across all files
- ✅ Commit changes with multi-line commit messages
- ✅ Push branches to remote
- ✅ Automatically create Pull Requests (GitHub, GitLab, Bitbucket)
- ✅ Colored console output with progress tracking
- ✅ Error handling and summary reporting
- ✅ Support for HTTPS and SSH Git URLs
- ✅ Continue processing on errors (failed repos are skipped)
- ✅ Detailed logging to file with PR URLs and status tracking

## Prerequisites

- Bash 4.0 or higher
- Git installed and configured
- `curl` (for PR creation)
- `sed` and `grep` (standard on most systems)
- Write access to target repositories
- (Optional) Personal access token for PR creation

## Quick Start

1. **Make the script executable:**
   ```bash
   chmod +x repo_batch_update.sh
   ```

2. **Create your repo list file:**
   ```bash
   cat > repos.txt << EOF
   my-first-repo
   my-second-repo
   another-project
   EOF
   ```

3. **Configure the script** (edit the CONFIGURATION SECTION)

4. **Run the script:**
   ```bash
   ./repo_batch_update.sh
   ```

## Configuration

Edit the `CONFIGURATION SECTION` at the top of the script:

### Required Settings

```bash
# File containing repo names (one per line)
REPO_LIST_FILE="repos.txt"

# Branch name to create
BRANCH_NAME="update-strings"

# Git remote base URL
GIT_BASE_URL="https://github.com/yourusername"
# Or for SSH:
# GIT_BASE_URL="git@github.com:yourusername"

# Find/Replace mappings
declare -a REPLACEMENTS=(
    "oldString1|newString1"
    "oldString2|newString2"
    "deprecated_function|modern_function"
)
```

### Optional Settings

```bash
# Working directory for cloning repos
WORK_DIR="./repos_temp"

# Log file for tracking completed repos and PR URLs
LOG_FILE="./batch_update_log.txt"

# File patterns to process (empty = all files)
FILE_PATTERNS="*"
# Or specific patterns:
# FILE_PATTERNS="*.py *.js *.md"

# Commit message (supports multi-line)
COMMIT_MESSAGE="Update string replacements across repository"

# Or multi-line:
COMMIT_MESSAGE="Update string replacements across repository

This commit updates several deprecated strings:
- Updated API endpoints
- Fixed configuration values
- Modernized function names

Refs: #1234"
```

### Pull Request Settings

```bash
# Create Pull Request after pushing? (true/false)
CREATE_PR=true

# Git platform (github, gitlab, or bitbucket)
GIT_PLATFORM="github"

# PR Title
PR_TITLE="Update string replacements across repository"

# PR Description/Body (supports multi-line)
PR_DESCRIPTION="This PR updates several deprecated strings across the codebase.

## Changes:
- Updated API endpoints
- Fixed configuration values
- Modernized function names

## Testing:
- [ ] All tests pass
- [ ] Manual testing completed

Refs: #1234"

# Base branch to target for PR
PR_BASE_BRANCH="main"

# Personal Access Token (recommended: use environment variable)
GIT_TOKEN="${GIT_TOKEN:-}"
```

## Repos List File Format

Create a text file with one repository name per line:

```text
# repos.txt example
# Lines starting with # are ignored
# Empty lines are ignored

my-first-repo
my-second-repo
frontend-app
backend-api
```

The script will generate Git URLs by combining `GIT_BASE_URL` with each repo name:
- `https://github.com/yourusername/my-first-repo.git`
- `https://github.com/yourusername/my-second-repo.git`

## Find/Replace Configuration

Define search and replace patterns in the `REPLACEMENTS` array:

```bash
declare -a REPLACEMENTS=(
    "old_api_v1|new_api_v2"
    "deprecatedFunction|modernFunction"
    "OLD_CONSTANT|NEW_CONSTANT"
    "http://old-domain.com|https://new-domain.com"
)
```

**Format:** `"search_string|replacement_string"`

**Notes:**
- Supports regex-like patterns (sed syntax)
- Applied to all text files (binary files are skipped)
- `.git` directory is excluded
- Replacements are applied in order

## Pull Request Setup

### 1. Choose Your Platform

Set the platform in the script:
```bash
GIT_PLATFORM="github"  # or "gitlab" or "bitbucket"
```

### 2. Create a Personal Access Token

#### GitHub
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `Batch PR Creation`
4. Scopes: Select ✅ `repo`
5. Click "Generate token"
6. Copy the token (format: `ghp_xxxx...`)

#### GitLab
1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Name: `Batch MR Creation`
3. Scopes: Select ✅ `api`
4. Click "Create personal access token"
5. Copy the token (format: `glpat-xxxx...`)

#### Bitbucket
1. Go to https://bitbucket.org/account/settings/app-passwords/
2. Click "Create app password"
3. Label: `Batch PR Creation`
4. Permissions: Select ✅ Pull requests: Write, ✅ Repositories: Write
5. Click "Create"
6. Copy the password

### 3. Set Your Token

**Method A: Environment Variable (Recommended)**
```bash
export GIT_TOKEN="your_token_here"
./repo_batch_update.sh
```

**Method B: Using .env file**
```bash
# Create .env file
echo 'export GIT_TOKEN="your_token_here"' > .env

# Add to .gitignore
echo ".env" >> .gitignore

# Source and run
source .env
./repo_batch_update.sh
```

**Method C: In Script (Not Recommended)**
```bash
# Edit script and set:
GIT_TOKEN="your_token_here"
```

### 4. Enable PR Creation

```bash
CREATE_PR=true
```

## Running the Script

### Basic Usage

```bash
./repo_batch_update.sh
```

### With Token from Environment

```bash
export GIT_TOKEN="ghp_xxxxxxxxxxxx"
./repo_batch_update.sh
```

### Dry Run (Manual Review)

To push branches without creating PRs:
```bash
# Edit script: CREATE_PR=false
./repo_batch_update.sh
```

### Running in Background

```bash
nohup ./repo_batch_update.sh > update.log 2>&1 &
```

### Running with Custom Config

```bash
# Override settings via environment
export REPO_LIST_FILE="my-repos.txt"
export BRANCH_NAME="feature/api-update"
export CREATE_PR=true
./repo_batch_update.sh
```

## Output and Logs

The script provides colored output showing:

```
[INFO] =========================================
[INFO] Processing repository: my-first-repo
[INFO] Git URL: https://github.com/username/my-first-repo.git
[INFO] =========================================
[INFO] Cloning repository...
[INFO] Creating branch: update-strings
[INFO] Performing string replacements...
[INFO]   Replacing 'oldString1' with 'newString1'
[INFO]     Updated: src/config.py
[INFO]     Updated: README.md
[INFO] Staging changes...
[INFO] Creating commit...
[INFO] Pushing branch to remote...
[INFO] Creating Pull Request...
[INFO] ✓ Pull Request created: https://github.com/username/my-first-repo/pull/42
[INFO] Successfully processed my-first-repo

[INFO] =========================================
[INFO] SUMMARY
[INFO] =========================================
[INFO] Total repositories: 5
[INFO] Successful: 4
[INFO] Failed: 1
```

### Log File

The script automatically creates a detailed log file (default: `batch_update_log.txt`) that tracks all operations:

```
=========================================
Batch Update Log - Started: 2026-01-29 14:32:15
=========================================

[2026-01-29 14:32:18] ✓ SUCCESS | my-first-repo | PR: https://github.com/yourusername/my-first-repo/pull/42
[2026-01-29 14:32:25] ✓ SUCCESS | my-second-repo | PR: https://github.com/yourusername/my-second-repo/pull/18
[2026-01-29 14:32:30] ⊘ NO CHANGES | another-project | No replacements matched
[2026-01-29 14:32:35] ✗ FAILED | frontend-app | Reason: Failed to clone repository
[2026-01-29 14:32:42] ✓ SUCCESS | backend-api | Branch pushed (no PR created)
[2026-01-29 14:32:48] ✓ SUCCESS | mobile-app | PR: https://github.com/yourusername/mobile-app/pull/7

=========================================
Summary - Completed: 2026-01-29 14:32:50
=========================================
Total repositories: 6
Successful: 4
Failed: 1
```

**Log Entry Types:**
- **✓ SUCCESS** - Repository processed successfully with PR created (includes PR URL)
- **✓ SUCCESS** - Repository processed, branch pushed but no PR created
- **⊘ NO CHANGES** - No replacements matched in the repository (skipped)
- **✗ FAILED** - Operation failed (includes failure reason)

**Customize Log Location:**
```bash
# Default
LOG_FILE="./batch_update_log.txt"

# Timestamped logs
LOG_FILE="./logs/batch_update_$(date +%Y%m%d_%H%M%S).log"

# Custom location
LOG_FILE="/var/log/batch_updates/$(date +%Y%m%d).log"
```

## Error Handling

The script handles errors gracefully and **continues processing remaining repositories** when individual repos fail. All errors are logged to the log file with detailed information.

### How Errors Are Handled

When a repository fails:
1. Error is logged to console with [ERROR] prefix
2. Error is recorded in log file with failure reason
3. Warning message displayed: "Continuing with next repository..."
4. Script proceeds to next repository in the list
5. Final summary shows count of failed repositories

This ensures that one failed repo doesn't prevent the rest from being processed.

### Common Error Scenarios

### "Failed to clone repository"
**Cause:** Invalid URL, network issue, or no access
**Solution:**
- Check `GIT_BASE_URL` is correct
- Verify repo names in `repos.txt`
- Ensure you have access to the repositories
- Check network connection

### "Failed to create branch"
**Cause:** Branch already exists
**Solution:**
- Delete the existing branch first, or
- Use a different `BRANCH_NAME`

### "No changes to commit"
**Cause:** Find/replace patterns didn't match anything
**Solution:**
- Verify `REPLACEMENTS` patterns are correct
- Check if the strings exist in the repository
- Review `FILE_PATTERNS` setting

### "Failed to push branch to remote"
**Cause:** No write access or authentication failed
**Solution:**
- Verify Git credentials are configured
- Check you have push access to the repository
- For HTTPS, ensure credentials are cached or use SSH

### "GIT_TOKEN not set. Skipping PR creation."
**Cause:** No access token provided
**Solution:**
```bash
export GIT_TOKEN="your_token_here"
```

### "Failed to create PR: Bad credentials"
**Cause:** Invalid or expired token
**Solution:**
- Verify token is correct
- Check token hasn't expired
- Ensure token has required permissions:
  - GitHub: `repo` scope
  - GitLab: `api` scope
  - Bitbucket: `pullrequest:write` scope

### "Failed to create PR: Validation Failed"
**Cause:** PR already exists or base branch doesn't exist
**Solution:**
- Check if PR already exists for this branch
- Verify `PR_BASE_BRANCH` exists in the repository
- Ensure branch was pushed successfully

## Examples

### Example 1: Update API Endpoints

```bash
# Configuration
BRANCH_NAME="update-api-endpoints"
PR_BASE_BRANCH="develop"

declare -a REPLACEMENTS=(
    "api.old-domain.com/v1|api.new-domain.com/v2"
    "OLD_API_KEY|NEW_API_KEY"
)

COMMIT_MESSAGE="Update API endpoints to v2

- Migrated from v1 to v2 endpoints
- Updated API domain
- Refreshed API keys

Refs: JIRA-1234"

PR_TITLE="[API] Update endpoints to v2"
PR_DESCRIPTION="## Summary
Migrates all API calls from v1 to v2 endpoints.

## Changes
- Updated base URL from old-domain to new-domain
- Changed API version from v1 to v2
- Updated API keys

## Testing
- [x] All unit tests pass
- [x] Integration tests updated
- [x] Manual smoke testing complete

Closes JIRA-1234"
```

### Example 2: Dependency Version Bump

```bash
# repos.txt
frontend-app
backend-api
mobile-app

# Configuration
BRANCH_NAME="bump-react-version"
FILE_PATTERNS="package.json"

declare -a REPLACEMENTS=(
    '"react": "17.0.2"|"react": "18.2.0"'
    '"react-dom": "17.0.2"|"react-dom": "18.2.0"'
)

COMMIT_MESSAGE="Bump React to v18.2.0"
PR_TITLE="Bump React to v18.2.0"
CREATE_PR=true
```

### Example 3: Copyright Year Update

```bash
BRANCH_NAME="update-copyright-2026"
FILE_PATTERNS="*.py *.js *.java *.go"

declare -a REPLACEMENTS=(
    "Copyright 2025|Copyright 2026"
    "© 2025|© 2026"
)

COMMIT_MESSAGE="Update copyright year to 2026"
PR_TITLE="Update copyright year to 2026"
```

### Example 4: Multi-Platform (GitLab)

```bash
GIT_PLATFORM="gitlab"
GIT_BASE_URL="https://gitlab.com/mycompany"
PR_BASE_BRANCH="main"

export GIT_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
./repo_batch_update.sh
```

### Example 5: SSH with Bitbucket

```bash
GIT_PLATFORM="bitbucket"
GIT_BASE_URL="git@bitbucket.org:mycompany"

# For Bitbucket, token format is username:app_password
export GIT_TOKEN="myusername:app_password_here"
./repo_batch_update.sh
```

## Advanced Usage

### Custom File Patterns

Process only specific file types:

```bash
# Python files only
FILE_PATTERNS="*.py"

# Multiple patterns
FILE_PATTERNS="*.py *.js *.jsx *.ts *.tsx"

# All markdown and config files
FILE_PATTERNS="*.md *.yml *.yaml *.json"
```

### Regex in Replacements

Use sed-style regex patterns:

```bash
declare -a REPLACEMENTS=(
    # Remove trailing whitespace
    " *$|"
    
    # Update date format YYYY-MM-DD to MM/DD/YYYY
    "\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)|\2/\3/\1"
    
    # Replace multiple spaces with single space
    "  *| "
)
```

### Conditional PR Creation

Only create PRs for specific repos:

```bash
# Modify the process_repo function to add conditions
if [[ "$repo_name" == "critical-repo" ]] && [ "$CREATE_PR" = true ]; then
    create_pull_request "$repo_name"
fi
```

### Custom Working Directory per Run

```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORK_DIR="./batch_update_${TIMESTAMP}"
```

### Parsing Log Files

Extract successful PRs from log file:
```bash
# Get all PR URLs
grep "✓ SUCCESS.*PR:" batch_update_log.txt | awk -F'PR: ' '{print $2}'

# Get failed repos
grep "✗ FAILED" batch_update_log.txt

# Count by status
grep "✓ SUCCESS" batch_update_log.txt | wc -l
grep "✗ FAILED" batch_update_log.txt | wc -l
grep "⊘ NO CHANGES" batch_update_log.txt | wc -l
```

### Retry Failed Repositories

Create a new repo list from failed entries:
```bash
# Extract failed repo names
grep "✗ FAILED" batch_update_log.txt | awk -F' | ' '{print $2}' > failed_repos.txt

# Update script to use this list
REPO_LIST_FILE="failed_repos.txt"
./repo_batch_update.sh
```

## Security Best Practices

1. **Never commit tokens to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*token*" >> .gitignore
   echo "*.log" >> .gitignore
   ```

2. **Use environment variables for tokens**
   ```bash
   # Store in .env (add to .gitignore)
   export GIT_TOKEN="your_token_here"
   ```

3. **Rotate tokens regularly**
   - Set expiration dates on tokens
   - Generate new tokens every 90 days

4. **Use minimal token permissions**
   - Only grant required scopes
   - Use read-only tokens when possible

5. **Secure your repos.txt file**
   ```bash
   chmod 600 repos.txt
   ```

6. **Review changes before running**
   - Test on a single repo first
   - Use `CREATE_PR=false` for initial testing

## CI/CD Integration

### GitHub Actions

```yaml
name: Batch Repo Update

on:
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run batch update
        env:
          GIT_TOKEN: ${{ secrets.BATCH_UPDATE_TOKEN }}
        run: |
          chmod +x repo_batch_update.sh
          ./repo_batch_update.sh
```

### GitLab CI

```yaml
batch_update:
  script:
    - chmod +x repo_batch_update.sh
    - export GIT_TOKEN=$GITLAB_TOKEN
    - ./repo_batch_update.sh
  only:
    - schedules
```

### Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        GIT_TOKEN = credentials('batch-update-token')
    }
    
    stages {
        stage('Batch Update') {
            steps {
                sh 'chmod +x repo_batch_update.sh'
                sh './repo_batch_update.sh'
            }
        }
    }
}
```

## Troubleshooting

### Viewing Detailed Logs

Check the log file for complete details on all operations:
```bash
cat batch_update_log.txt

# Or view in real-time during execution
tail -f batch_update_log.txt
```

### Script exits immediately

**Cause:** Missing repo list file or other critical configuration error
**Solution:** 
- Verify `REPO_LIST_FILE` exists and is readable
- Check file path is correct
- Review error message for specific issue
- Individual repo failures will NOT stop the script - only critical configuration errors will

### Permission denied

```bash
chmod +x repo_batch_update.sh
```

### sed: command not found (macOS)

macOS uses BSD sed. Install GNU sed:
```bash
brew install gnu-sed
# Update script to use 'gsed' instead of 'sed'
```

### Binary files modified incorrectly

The script checks file type before replacing. If issues occur:
```bash
# Add specific file patterns
FILE_PATTERNS="*.txt *.md *.py *.js"
```

### Large repositories timeout

Increase Git timeout:
```bash
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
```

### Working directory fills up disk

Clean up after each run:
```bash
# Add to end of script
rm -rf "$WORK_DIR"
```

Or manually:
```bash
rm -rf ./repos_temp
```

## Limitations

- Only processes text files (binary files are skipped)
- Requires network access for cloning and pushing
- Rate limited by Git platform APIs
- Maximum 100 repos recommended per run (API rate limits)
- Find/replace uses sed (limited regex support)
- Failed repos are skipped but logged (script continues)

## Contributing

Suggestions for improvement:

1. Fork the script
2. Test your changes
3. Document new features
4. Submit feedback

## License

This script is provided as-is for use in your projects. Modify as needed.

## Support

For issues or questions:

1. Check this README for solutions
2. Review error messages carefully
3. Test with a single repo first
4. Verify all prerequisites are met

## Changelog

### Version 1.3 (Current)
- Added detailed logging to file with timestamps
- Logs PR URLs for successful operations
- Continue processing on errors (skip failed repos)
- Track completion status (success, failed, no changes)
- Added log parsing utilities

### Version 1.2
- Added Pull Request creation support
- Multi-platform support (GitHub, GitLab, Bitbucket)
- Multi-line commit messages
- Enhanced error handling

### Version 1.1
- Added file pattern filtering
- Improved logging with colors
- Summary reporting

### Version 1.0
- Initial release
- Basic clone, replace, commit, push functionality
