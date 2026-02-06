# Repo Batch Update Tool - Bash Version

Pure bash implementation with no external dependencies beyond standard Unix tools.

**🐚 Simple, portable, no installation required**

## When to Use Bash Version

✅ **Use Bash version when:**
- Processing < 20 repositories
- Using < 20 replacement rules
- Don't want Python dependency
- Prefer pure shell scripts
- Debugging/testing on a few repos
- Need maximum portability

⚠️ **For larger batches, use the Python version** (50-100x faster)

See [PERFORMANCE.md](PERFORMANCE.md) for comparison.

## Prerequisites

### Required
- Bash 4.0 or higher
- Git installed and configured
- Standard Unix tools: `sed`, `grep`, `find`, `curl`

### Check Prerequisites

```bash
# Check Bash version
bash --version
# Should show 4.0 or higher

# Check Git
git --version

# Check curl (for PR creation)
curl --version
```

All other tools (`sed`, `grep`, `find`) are standard on Linux/macOS.

## Installation

### 1. Make Script Executable

```bash
chmod +x repo_batch_update.sh
```

That's it! No other installation needed.

### macOS Note (BSD sed)

macOS uses BSD `sed` which differs slightly from GNU `sed`. The script works on macOS, but for best compatibility you can install GNU sed:

```bash
brew install gnu-sed

# Then the script will automatically use it
```

## Quick Start

1. **Create configuration file** (see [README-MAIN.md](README-MAIN.md))

2. **Create repository list:**
   ```bash
   cat > repos.txt << EOF
   repo-1
   repo-2
   repo-3
   EOF
   ```

3. **Set up authentication:**
   ```bash
   export GIT_AUTH_TOKEN="your_token_here"
   ```

4. **Run the script:**
   ```bash
   ./repo_batch_update.sh
   
   # Or with custom config
   CONFIG_FILE="./my-config.sh" ./repo_batch_update.sh
   ```

## Usage

### Basic Usage

```bash
# Use default config.sh
./repo_batch_update.sh

# With custom config
CONFIG_FILE="./config.api-update.sh" ./repo_batch_update.sh

# With authentication token
export GIT_AUTH_TOKEN="ghp_xxxxxxxxxxxx"
./repo_batch_update.sh
```

### Advanced Usage

```bash
# Process only first 3 repos (for testing)
head -3 repos.txt > test_repos.txt
# Edit config.sh: REPO_LIST_FILE="test_repos.txt"
./repo_batch_update.sh

# Run in background and log output
nohup ./repo_batch_update.sh > update.log 2>&1 &

# Follow progress
tail -f update.log
```

## Configuration

Edit the `config.sh` file directly. See [README-MAIN.md](README-MAIN.md) for complete configuration options.

**Key settings:**

```bash
# Repository settings
REPO_LIST_FILE="repos.txt"
BRANCH_NAME="update-strings"
GIT_BASE_URL="https://github.com/your-org"

# Authentication
GIT_AUTH_METHOD="token"  # or "ssh" or "none"
GIT_USERNAME="your-username"
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"

# Replacements
declare -a REPLACEMENTS=(
    "oldString1|newString1"
    "oldString2|newString2"
)

# File matching
FILE_PATTERNS="*.py *.js *.md"  # or "*" for all
CASE_SENSITIVE=true  # or false

# PR settings
CREATE_PR=true
GIT_PLATFORM="github"
PR_TITLE="Update strings"
PR_BASE_BRANCH="main"
```

## Features

### All Standard Features

Everything from the main README, including:
- Multiple file pattern support (fixed!)
- Case-sensitive/insensitive matching
- Complete match logging
- Immediate PR creation after each repo
- Verbose error messages

### Bash-Specific Advantages

1. **No Dependencies**
   - Works out of the box on any Linux/Mac system
   - No installation or setup required
   - Just bash and standard Unix tools

2. **Maximum Portability**
   - Pure shell script
   - No language runtime needed
   - Easy to audit and modify

3. **System Integration**
   - Natural integration with other shell scripts
   - Easy to use in cron jobs
   - Simple to embed in larger workflows

## Output Example

```
[INFO] =========================================
[INFO] Repo Batch Update Script
[INFO] =========================================
[INFO] Starting at: 2026-02-05 14:30:00

[INFO] Configuration:
[INFO]   Config file: ./config.sh
[INFO]   Repo list: repos.txt
[INFO]   Branch name: update-strings
[INFO]   Base URL: https://github.com/myorg
[INFO]   Work directory: ./repos_temp
[INFO]   Log file: ./batch_update_log.txt
[INFO]   File patterns: *.py *.js
[INFO]   Create PR: true

[INFO] Setting up Git authentication...
[INFO] Authentication method: token
[INFO] Username: myusername
[INFO] Token: ghp_abc123... (truncated)
[INFO] ✓ Git authentication configured for github.com

[INFO] Found 3 repositories to process

[INFO] =========================================
[INFO] Repository 1 of 3: my-first-repo
[INFO] =========================================
[INFO] Git URL: https://github.com/myorg/my-first-repo.git

[INFO] Cloning repository...
[INFO] Running: git clone https://github.com/myorg/my-first-repo.git ./repos_temp/my-first-repo
Cloning into './repos_temp/my-first-repo'...
[INFO] ✓ Successfully cloned my-first-repo

[INFO] Creating branch: update-strings
[INFO] Running: git checkout -b update-strings
Switched to a new branch 'update-strings'
[INFO] Successfully created and checked out branch: update-strings

[INFO] Performing string replacements...
[INFO] File patterns: *.py *.js
[INFO] Case sensitive: true
[INFO] Number of replacement rules: 2

[INFO] Using case-sensitive matching

[INFO] ----------------------------------------
[INFO] Replacement rule: 'oldString1' → 'newString1'
[INFO] ----------------------------------------
[INFO]   📝 File: src/config.py (3 occurrence(s))
[INFO]      Line 15: API_URL = "oldString1/endpoint"
[INFO]      Line 47: DEFAULT_URL = "oldString1/default"
[INFO]      Line 89: BACKUP_URL = "oldString1/backup"
[INFO]      ✓ Replaced

[INFO]   Summary for this rule:
[INFO]     Files modified: 2
[INFO]     Total replacements: 5

[INFO] ========================================
[INFO] REPLACEMENT SUMMARY
[INFO] ========================================
[INFO] Total files searched: 45
[INFO] Total files modified: 4
[INFO] Total replacements made: 8

[INFO] Staging changes...
[INFO] Creating commit...
[INFO] Running: git commit -m "..."
[main abc1234] Update strings
 4 files changed, 8 insertions(+), 8 deletions(-)
[INFO] Successfully created commit

[INFO] Pushing branch to remote...
[INFO] Running: git push -u origin update-strings
To https://github.com/myorg/my-first-repo.git
 * [new branch]      update-strings -> update-strings
[INFO] Successfully pushed branch to remote

[INFO] =========================================
[INFO] Creating Pull Request for my-first-repo
[INFO] =========================================
[INFO] Preparing to create PR...
[INFO] Repository: myorg/my-first-repo
[INFO] Platform: github
[INFO] Branch: update-strings → main

[INFO] Using GitHub API...
[INFO] Creating GitHub PR for: myorg/my-first-repo
[INFO] API endpoint: https://api.github.com/repos/myorg/my-first-repo/pulls
[INFO] HTTP Status: 201
[INFO] ✓ Pull Request created: https://github.com/myorg/my-first-repo/pull/42

[INFO] Successfully processed my-first-repo

[INFO] =========================================
[INFO] SUMMARY
[INFO] =========================================
[INFO] Completed at: 2026-02-05 14:35:00
[INFO] Total repositories: 3
[INFO] Successful: 3
[INFO] Failed: 0

[INFO] Detailed log saved to: ./batch_update_log.txt
[INFO] ✓ All repositories processed successfully!
```

## Performance Considerations

The bash version processes one repository at a time, one rule at a time. For each rule and each file, it:
1. Calls `grep` to check if file contains pattern
2. Calls `grep` again to count occurrences
3. Calls `grep` again to get line numbers
4. Calls `sed` multiple times to get line content
5. Calls `sed` to perform replacement

**Estimated time:**
- Small repo (100 files), 10 rules: ~30 seconds
- Medium repo (500 files), 50 rules: ~5 minutes
- Large repo (2000 files), 110 rules: ~30 minutes

**For large batches, use the Python version!** It will be 50-100x faster.

## Troubleshooting

### "Permission denied"

```bash
chmod +x repo_batch_update.sh
```

### "Command not found: bash"

Make sure you're running on Linux or macOS. On Windows, use WSL (Windows Subsystem for Linux).

### "sed: command not found" (macOS)

macOS uses BSD sed. Install GNU sed for full compatibility:

```bash
brew install gnu-sed
```

### Script seems stuck

The script is likely processing many files. You can:

1. **Check progress in another terminal:**
   ```bash
   # See current git operations
   ps aux | grep git
   
   # See current file being processed
   tail -f batch_update_log.txt
   ```

2. **Test with fewer repos first:**
   ```bash
   head -2 repos.txt > test_repos.txt
   # Edit config.sh: REPO_LIST_FILE="test_repos.txt"
   ```

### "Failed to clone" but directory exists

The clone succeeded but the bash error detection had an issue with the output filtering. Check if the directory exists:

```bash
ls -la repos_temp/
```

If it exists, the clone worked. The script should continue processing.

### Multiple file patterns not working

Make sure patterns are space-separated without quotes around individual patterns:

```bash
# Correct
FILE_PATTERNS="*.py *.js *.md"

# Wrong
FILE_PATTERNS="'*.py' '*.js' '*.md'"
```

### PR creation not showing output

Make sure you're using the updated version with verbose PR logging. The script should show:
- "Preparing to create PR..."
- API endpoint
- HTTP status
- Full response

If you don't see this, you may have an older version.

## Debugging

Enable additional debugging:

```bash
# Run with bash debugging
bash -x ./repo_batch_update.sh 2>&1 | tee debug.log

# Or add to script
set -x  # At top of script
```

## Comparison with Python Version

| Feature | Bash | Python |
|---------|------|--------|
| Speed (3 repos, 10 rules) | ~2 minutes | ~10 seconds |
| Speed (200 repos, 110 rules) | ~720 hours | ~10 hours |
| Dependencies | None (just bash) | Python 3.6+, requests |
| Installation | Just chmod +x | pip install |
| Portability | High (Linux/Mac) | Very High (all platforms) |
| Error messages | Detailed | Very detailed |
| Code clarity | Good | Excellent |
| Extensibility | Moderate | Easy |

## When to Switch to Python

Consider switching to Python version when:

- Processing time exceeds 30 minutes
- Processing > 20 repositories
- Using > 20 replacement rules
- Running frequently (save time in long run)
- Need better performance

The Python version uses the same `config.sh`, so switching is easy!

## CI/CD Integration

### GitHub Actions

```yaml
name: Batch Update

on:
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run batch update
        env:
          GIT_AUTH_TOKEN: ${{ secrets.BATCH_UPDATE_TOKEN }}
        run: |
          chmod +x repo_batch_update.sh
          ./repo_batch_update.sh
```

### GitLab CI

```yaml
batch_update:
  script:
    - chmod +x repo_batch_update.sh
    - export GIT_AUTH_TOKEN=$GITLAB_TOKEN
    - ./repo_batch_update.sh
  only:
    - schedules
```

### Cron Job

```bash
# Add to crontab
0 2 * * 0 cd /path/to/script && export GIT_AUTH_TOKEN="xxx" && ./repo_batch_update.sh > /var/log/batch_update.log 2>&1
```

## Shell Script Best Practices

The bash version follows these best practices:

1. **Colored output** for readability
2. **Error checking** after each git operation
3. **Detailed logging** to file
4. **Continues on errors** (doesn't exit on first failure)
5. **Cleans up** authentication after completion
6. **Validates configuration** before starting
7. **Shows progress** for long operations

## Getting Help

1. Check this README for Bash-specific issues
2. Check [README-MAIN.md](README-MAIN.md) for general functionality
3. Check [AUTHENTICATION.md](AUTHENTICATION.md) for auth issues
4. Run with `bash -x` for detailed debugging

## License

This tool is provided as-is for use in your projects. Modify as needed.
