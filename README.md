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

3. **Edit the configuration file:**
   ```bash
   # Edit config.sh with your settings
   nano config.sh
   ```

4. **Run the script:**
   ```bash
   ./repo_batch_update.sh
   ```

## Configuration

All settings are stored in a separate configuration file (`config.sh` by default). This allows you to update the script without losing your settings.

### Configuration File Structure

The script loads settings from `config.sh` (or a custom config file specified via `CONFIG_FILE` environment variable).

**Default config file location:** `./config.sh`

**Use a different config file:**
```bash
CONFIG_FILE="./my-custom-config.sh" ./repo_batch_update.sh
```

### Required Settings

Edit `config.sh` and set these required values:

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

# Log file location
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

### Multiple Configuration Files

You can maintain multiple config files for different update scenarios:

```bash
# config.api-update.sh - For API endpoint updates
# config.copyright.sh - For copyright year updates
# config.dependency-bump.sh - For dependency updates
```

**Run with specific config:**
```bash
CONFIG_FILE="./config.api-update.sh" ./repo_batch_update.sh
```

Or create wrapper scripts:
```bash
#!/bin/bash
# run_api_update.sh
CONFIG_FILE="./config.api-update.sh" ./repo_batch_update.sh
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

The script automatically creates a detailed log file (default: `batch_update_log.txt`) in tab-separated format for easy parsing:

```
Repository	Result
my-first-repo	https://github.com/yourusername/my-first-repo/pull/42
my-second-repo	https://github.com/yourusername/my-second-repo/pull/18
another-project	No changes (replacements did not match any content)
frontend-app	Failed: Failed to clone repository
backend-api	Branch pushed (PR not created)
mobile-app	https://github.com/yourusername/mobile-app/pull/7
test-repo	Failed: Failed to push to remote
```

**Log Entry Format:**
Each line contains two tab-separated fields:
1. **Repository name** - The name of the repository processed
2. **Result** - One of:
   - `https://...` - Direct PR URL if PR was created successfully
   - `No changes (replacements did not match any content)` - No files were modified
   - `Branch pushed (PR not created)` - Changes pushed but PR creation was disabled or failed
   - `Failed: [reason]` - Operation failed with descriptive error message

**Benefits of Tab-Separated Format:**
- Easy to import into Excel/Google Sheets
- Simple to parse with `awk`, `cut`, or Python
- Compatible with most data processing tools
- Clickable URLs in most text editors

**Customize Log Location:**
```bash
# Default
LOG_FILE="./batch_update_log.txt"

# Timestamped logs
LOG_FILE="./logs/batch_update_$(date +%Y%m%d_%H%M%S).log"

# CSV format (also tab-separated, just different extension)
LOG_FILE="./batch_update_log.tsv"
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

**Create `config.api-update.sh`:**
```bash
#!/bin/bash

REPO_LIST_FILE="api_repos.txt"
BRANCH_NAME="update-api-endpoints"
GIT_BASE_URL="https://github.com/mycompany"
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

CREATE_PR=true
GIT_PLATFORM="github"
GIT_TOKEN="${GIT_TOKEN:-}"
```

**Run:**
```bash
CONFIG_FILE="./config.api-update.sh" ./repo_batch_update.sh
```

### Example 2: Dependency Version Bump

**Create repos list (`package_repos.txt`):**
```
frontend-app
backend-api
mobile-app
```

**Create `config.react-bump.sh`:**
```bash
#!/bin/bash

REPO_LIST_FILE="package_repos.txt"
BRANCH_NAME="bump-react-version"
GIT_BASE_URL="https://github.com/mycompany"
FILE_PATTERNS="package.json"

declare -a REPLACEMENTS=(
    '"react": "17.0.2"|"react": "18.2.0"'
    '"react-dom": "17.0.2"|"react-dom": "18.2.0"'
)

COMMIT_MESSAGE="Bump React to v18.2.0"
PR_TITLE="Bump React to v18.2.0"
CREATE_PR=true
GIT_PLATFORM="github"
GIT_TOKEN="${GIT_TOKEN:-}"
```

**Run:**
```bash
CONFIG_FILE="./config.react-bump.sh" ./repo_batch_update.sh
```

### Example 3: Copyright Year Update

**Create `config.copyright.sh`:**
```bash
#!/bin/bash

REPO_LIST_FILE="all_repos.txt"
BRANCH_NAME="update-copyright-2026"
GIT_BASE_URL="https://github.com/mycompany"
FILE_PATTERNS="*.py *.js *.java *.go"

declare -a REPLACEMENTS=(
    "Copyright 2025|Copyright 2026"
    "© 2025|© 2026"
)

COMMIT_MESSAGE="Update copyright year to 2026"
PR_TITLE="Update copyright year to 2026"
CREATE_PR=true
GIT_PLATFORM="github"
GIT_TOKEN="${GIT_TOKEN:-}"
```

**Run:**
```bash
CONFIG_FILE="./config.copyright.sh" ./repo_batch_update.sh
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

Extract information from the tab-separated log file:

```bash
# Get all successful PR URLs
awk -F'\t' '$2 ~ /^https:/ {print $2}' batch_update_log.txt

# Get all failed repos with their error messages
awk -F'\t' '$2 ~ /^Failed:/ {print $0}' batch_update_log.txt

# Get list of repos with no changes
awk -F'\t' '$2 ~ /^No changes/ {print $1}' batch_update_log.txt

# Count by status
echo "PRs created: $(awk -F'\t' '$2 ~ /^https:/ {count++} END {print count}' batch_update_log.txt)"
echo "Failed: $(awk -F'\t' '$2 ~ /^Failed:/ {count++} END {print count}' batch_update_log.txt)"
echo "No changes: $(awk -F'\t' '$2 ~ /^No changes/ {count++} END {print count}' batch_update_log.txt)"

# Create clickable HTML report
awk -F'\t' 'NR==1 {print "<table><tr><th>" $1 "</th><th>" $2 "</th></tr>"} 
     NR>1 && $2 ~ /^https:/ {print "<tr><td>" $1 "</td><td><a href=\"" $2 "\">" $2 "</a></td></tr>"} 
     NR>1 && $2 !~ /^https:/ {print "<tr><td>" $1 "</td><td>" $2 "</td></tr>"} 
     END {print "</table>"}' batch_update_log.txt > report.html

# Import into spreadsheet (works with Excel, Google Sheets, LibreOffice)
# Just open the .txt file directly - tab-separated format is auto-detected
```

### Retry Failed Repositories

Create a new repo list from failed entries:

```bash
# Extract failed repo names (skip header, get first column of failed rows)
awk -F'\t' 'NR>1 && $2 ~ /^Failed:/ {print $1}' batch_update_log.txt > failed_repos.txt

# Update script to use this list
REPO_LIST_FILE="failed_repos.txt"
./repo_batch_update.sh
```

### Python Processing Example

```python
import csv

# Read the log file
with open('batch_update_log.txt', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)  # Skip header
    
    prs_created = []
    failed_repos = []
    
    for repo, result in reader:
        if result.startswith('https://'):
            prs_created.append({'repo': repo, 'pr_url': result})
        elif result.startswith('Failed:'):
            failed_repos.append({'repo': repo, 'error': result})
    
    print(f"Created {len(prs_created)} PRs")
    print(f"Failed: {len(failed_repos)} repos")
    
    # Generate markdown report
    with open('pr_report.md', 'w') as out:
        out.write("# PR Report\n\n")
        for pr in prs_created:
            out.write(f"- [{pr['repo']}]({pr['pr_url']})\n")
```

## Security Best Practices

1. **Never commit tokens to version control**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "*token*" >> .gitignore
   echo "*.log" >> .gitignore
   echo "config.sh" >> .gitignore  # If it contains sensitive data
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

## Updating the Script

One of the key benefits of separating configuration is that you can update the script without affecting your settings:

### Update Process

1. **Backup your config file** (optional, but recommended):
   ```bash
   cp config.sh config.sh.backup
   ```

2. **Download the latest script**:
   ```bash
   # Keep your config.sh, just update the main script
   wget https://example.com/repo_batch_update.sh -O repo_batch_update.sh
   chmod +x repo_batch_update.sh
   ```

3. **Your configuration remains unchanged** - the script will automatically load your existing `config.sh`

### Version Control Best Practices

```bash
# In your repository
git add repo_batch_update.sh      # Track the script
git add config.sh.example         # Track an example config
echo "config.sh" >> .gitignore    # Ignore your actual config
echo "*.log" >> .gitignore        # Ignore log files
echo "repos_temp/" >> .gitignore  # Ignore working directory
```

This way, you can:
- Update the script via `git pull`
- Keep your personal config file untracked
- Share config templates with your team

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

### Version 1.4 (Current)
- **Separated configuration from script logic**
- Configuration now in separate `config.sh` file
- Support for multiple config files
- Easier script updates without losing settings
- Added config file validation

### Version 1.3
- Added detailed logging to file with timestamps
- Logs PR URLs for successful operations
- Continue processing on errors (skip failed repos)
- Track completion status (success, failed, no changes)
- Added log parsing utilities
- Simplified log format to tab-separated values

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
