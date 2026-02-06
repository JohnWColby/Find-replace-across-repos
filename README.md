# Repo Batch Update Tool

A powerful tool for automating bulk updates across multiple Git repositories. Clone repos, create branches, perform find/replace operations, commit changes, push to remote, and automatically create Pull Requests—all in one command.

**Available in two versions:**
- 🐍 **Python** (Recommended for large batches: 50-100x faster)
- 🐚 **Bash** (Good for small batches, no dependencies)

See [README-PYTHON.md](README-PYTHON.md) and [README-BASH.md](README-BASH.md) for version-specific instructions.

## Features

- ✅ Clone multiple repositories from a list
- ✅ Create branches with custom names (or use existing branches)
- ✅ Perform find/replace operations across all files
- ✅ Case-sensitive or case-insensitive matching
- ✅ Support for multiple file patterns (e.g., `*.py *.js *.md`)
- ✅ Commit changes with multi-line commit messages
- ✅ Push branches to remote
- ✅ Automatically create Pull Requests (GitHub, GitLab, Bitbucket)
- ✅ Colored console output with progress tracking
- ✅ Detailed logging with all matches shown
- ✅ Error handling - skips failed repos and continues
- ✅ Tab-separated log file with PR URLs
- ✅ Support for HTTPS (token) and SSH authentication
- ✅ Works with private organization repositories

## Prerequisites

- Git installed and configured
- Write access to target repositories
- Authentication credentials (token or SSH keys)

### Platform-Specific Requirements

**Linux/macOS:**
- Bash 4.0+ (for bash version)
- Python 3.6+ (for Python version)

**Windows:**
- WSL (Windows Subsystem for Linux) - **Required**
- See [Windows Setup](#windows-setup) below

## Windows Setup

**The scripts require a Unix-like environment and will NOT run in PowerShell or CMD.**

### Option 1: WSL (Recommended)

WSL provides a full Linux environment on Windows.

#### Install WSL

1. **Open PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```

2. **Restart your computer** when prompted

3. **Open "Ubuntu" from Start Menu**
   - First launch will take a few minutes
   - Create a Linux username and password

4. **Update package list:**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

#### Install Prerequisites in WSL

```bash
# Install Git
sudo apt install git

# For Python version
sudo apt install python3 python3-pip
pip3 install requests

# For Bash version (already included)
# No additional installation needed
```

#### Access Windows Files from WSL

Your Windows drives are mounted at `/mnt/`:
```bash
# Navigate to your project folder
cd /mnt/c/Users/YourUsername/Documents/batch-update

# Or use Windows path
cd $(wslpath "C:\Users\YourUsername\Documents\batch-update")
```

#### Run Scripts in WSL

```bash
# Make executable
chmod +x repo_batch_update.py
chmod +x repo_batch_update.sh

# Run Python version
python3 repo_batch_update.py

# Run Bash version
./repo_batch_update.sh
```

### Option 2: Git Bash (Limited Support)

Git Bash provides basic Unix tools but has limitations:

⚠️ **Warning:** Some features may not work correctly in Git Bash. WSL is strongly recommended.

1. **Install Git for Windows** from https://git-scm.com/download/win
   - During installation, select "Use Git and optional Unix tools from Command Prompt"

2. **Open Git Bash**

3. **For Python version:**
   - Install Python from https://www.python.org/downloads/
   - In Git Bash:
     ```bash
     pip install requests
     python repo_batch_update.py
     ```

4. **For Bash version:**
   ```bash
   ./repo_batch_update.sh
   ```

**Known Git Bash limitations:**
- Some sed commands may behave differently
- File path handling may have issues
- Performance may be slower

### Recommendation for Windows Users

✅ **Use WSL** for best compatibility and performance
- Full Linux environment
- All features work correctly
- Better performance
- Same commands as Linux/macOS

## Quick Start

1. **Choose your version:**
   - **Large batches** (100+ repos, 50+ rules): Use Python version
   - **Small batches** (< 20 repos, < 20 rules): Either version works

2. **Create repository list:**
   ```bash
   cat > repos.txt << EOF
   my-first-repo
   my-second-repo
   another-project
   EOF
   ```

3. **Configure settings** in `config.sh`

4. **Set up authentication:**
   ```bash
   export GIT_AUTH_TOKEN="your_token_here"
   ```

5. **Run:**
   ```bash
   # Python version (recommended for large batches)
   python3 repo_batch_update.py
   
   # Bash version
   ./repo_batch_update.sh
   ```

## Configuration

All settings are in `config.sh`. Both versions use the same configuration file.

### Git Authentication

Required for private repositories:

```bash
# Token authentication (HTTPS)
GIT_AUTH_METHOD="token"
GIT_USERNAME="your-username"
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"  # Set via environment
GIT_BASE_URL="https://github.com/your-org"

# OR SSH authentication
GIT_AUTH_METHOD="ssh"
GIT_BASE_URL="git@github.com:your-org"
```

**Create tokens:**
- GitHub: https://github.com/settings/tokens (needs `repo` scope)
- GitLab: https://gitlab.com/-/profile/personal_access_tokens (needs `api` scope)
- Bitbucket: https://bitbucket.org/account/settings/app-passwords/

See [AUTHENTICATION.md](AUTHENTICATION.md) for detailed setup.

### Repository Configuration

```bash
# File containing repo names (one per line)
REPO_LIST_FILE="repos.txt"

# Branch name to create
BRANCH_NAME="update-strings"

# Git remote base URL
GIT_BASE_URL="https://github.com/your-org"

# Working directory for cloning repos
WORK_DIR="./repos_temp"

# Log file for results
LOG_FILE="./batch_update_log.txt"
```

### Find/Replace Rules

```bash
# Replacement mappings
declare -a REPLACEMENTS=(
    "oldString1|newString1"
    "oldString2|newString2"
    "api.old.com|api.new.com"
)

# Case sensitivity
CASE_SENSITIVE=true  # or false for case-insensitive

# File patterns to process
FILE_PATTERNS="*.py *.js *.md"  # or "*" for all files
```

### Pull Request Configuration

```bash
# Enable PR creation
CREATE_PR=true

# Platform
GIT_PLATFORM="github"  # or "gitlab" or "bitbucket"

# PR details
PR_TITLE="Update deprecated strings"
PR_DESCRIPTION="This PR updates several deprecated strings..."
PR_BASE_BRANCH="main"
```

### Proxy Configuration (Corporate Firewalls)

**Only needed if your organization uses a corporate proxy/firewall**

```bash
# Environment variables (recommended)
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="your-password"

# Or in config.sh
USE_PROXY=true
PROXY_URL="http://proxy.company.com:8080"
PROXY_USERNAME="DOMAIN\username"
PROXY_PASSWORD="password"
```

**For NTLM proxies (most corporate environments):**
```bash
pip3 install requests-ntlm
```

See [AUTHENTICATION.md](AUTHENTICATION.md#corporate-proxy--firewall-configuration) for details.

## Repository List Format

Create a text file with one repository name per line:

```text
# repos.txt
# Lines starting with # are ignored
# Empty lines are ignored

my-first-repo
my-second-repo
frontend-app
backend-api
```

The tool generates Git URLs by combining `GIT_BASE_URL` with each repo name:
- `https://github.com/your-org/my-first-repo.git`
- `https://github.com/your-org/my-second-repo.git`

## Case Sensitivity

Control whether replacements match case:

```bash
# Case-sensitive (default)
CASE_SENSITIVE=true
# "API" matches "API" but NOT "api", "Api"

# Case-insensitive
CASE_SENSITIVE=false
# "API" matches "API", "api", "Api", "aPi", etc.
```

**Use case-insensitive for:**
- URL normalization: `"API.EXAMPLE.COM|api.example.com"`
- Fixing inconsistent capitalization
- Brand name corrections: `"Javascript|JavaScript"`

## Output and Logs

### Console Output

Both versions provide colored, detailed output:

```
[INFO] =========================================
[INFO] Processing repository: my-first-repo
[INFO] =========================================
[INFO] Cloning repository...
[INFO] Creating branch: update-strings
[INFO] Performing string replacements...
[INFO] ----------------------------------------
[INFO] Rule 1/3: 'oldString1' → 'newString1'
[INFO] ----------------------------------------
[INFO]   📝 File: src/config.py (3 occurrence(s))
[INFO]      Line 15: API_URL = "oldString1/endpoint"
[INFO]      Line 47: DEFAULT_URL = "oldString1/default"
[INFO]      Line 89: BACKUP_URL = "oldString1/backup"
[INFO]      ✓ Replaced
[INFO] ========================================
[INFO] Creating Pull Request for my-first-repo
[INFO] ========================================
[INFO] ✓ Pull Request created: https://github.com/org/my-first-repo/pull/42
```

### Log File

Tab-separated file for easy parsing:

```
Repository	Result
my-first-repo	https://github.com/org/my-first-repo/pull/42
my-second-repo	https://github.com/org/my-second-repo/pull/18
another-project	No changes (replacements did not match any content)
frontend-app	Failed: Failed to clone repository
backend-api	Branch pushed (PR not created)
```

**Parse logs:**
```bash
# Get all PR URLs
awk -F'\t' '$2 ~ /^https:/ {print $2}' batch_update_log.txt

# Get failed repos
awk -F'\t' '$2 ~ /^Failed:/ {print $1}' batch_update_log.txt

# Count successes
awk -F'\t' '$2 ~ /^https:/ {count++} END {print count}' batch_update_log.txt
```

## Common Use Cases

### Example 1: API Endpoint Updates

```bash
BRANCH_NAME="update-api-endpoints"
declare -a REPLACEMENTS=(
    "api.old-domain.com/v1|api.new-domain.com/v2"
    "OLD_API_KEY|NEW_API_KEY"
)
FILE_PATTERNS="*.py *.js *.yaml *.json"
```

### Example 2: Copyright Year Update

```bash
BRANCH_NAME="update-copyright-2026"
declare -a REPLACEMENTS=(
    "Copyright 2025|Copyright 2026"
    "© 2025|© 2026"
)
FILE_PATTERNS="*.py *.js *.java *.go"
CASE_SENSITIVE=true
```

### Example 3: Case-Insensitive URL Normalization

```bash
BRANCH_NAME="normalize-urls"
declare -a REPLACEMENTS=(
    "API.EXAMPLE.COM|api.example.com"
    "STAGING.EXAMPLE.COM|staging.example.com"
)
CASE_SENSITIVE=false  # Matches any case variation
```

### Example 4: Dependency Version Bump

```bash
BRANCH_NAME="bump-react-version"
FILE_PATTERNS="package.json"
declare -a REPLACEMENTS=(
    '"react": "17.0.2"|"react": "18.2.0"'
    '"react-dom": "17.0.2"|"react-dom": "18.2.0"'
)
```

## Error Handling

The tool handles errors gracefully and continues processing:

- **Clone fails**: Logs error, moves to next repo
- **Branch exists**: Checks out existing branch and continues
- **No matches found**: Logs "no changes", moves to next repo
- **Push fails**: Logs error with specific reason (auth, permissions, etc.)
- **PR creation fails**: Logs error but branch is still pushed

All errors are logged to the log file with specific error messages.

## Security Best Practices

1. **Never commit tokens to version control**
   ```bash
   echo ".env" >> .gitignore
   echo "config.sh" >> .gitignore  # If it contains tokens
   ```

2. **Use environment variables for tokens**
   ```bash
   export GIT_AUTH_TOKEN="your_token_here"
   ```

3. **Rotate tokens regularly**
   - Set expiration dates (90 days recommended)
   - Generate new tokens periodically

4. **Use minimal token permissions**
   - GitHub: `repo` scope only
   - GitLab: `api` scope only
   - Bitbucket: Repository Write + Pull Request Write

5. **Review changes before running**
   - Test on 1-2 repos first
   - Use `CREATE_PR=false` for initial testing

## Multiple Configuration Files

Maintain separate configs for different scenarios:

```bash
config.api-update.sh       # API endpoint updates
config.copyright.sh        # Copyright year updates
config.dependency-bump.sh  # Dependency updates
```

Run with specific config:
```bash
# Python
python3 repo_batch_update.py --config ./config.api-update.sh

# Bash
CONFIG_FILE="./config.api-update.sh" ./repo_batch_update.sh
```

## Limitations

- Only processes text files (binary files are skipped)
- Requires network access for cloning and pushing
- Rate limited by Git platform APIs
- Find/replace uses literal strings (regex patterns in special cases only)
- Failed repos are skipped and logged (script continues)

## When to Use Which Version

### Use Python Version When:
- Processing 50+ repositories
- Using 20+ replacement rules
- Total processing time > 30 minutes
- Need faster performance

### Use Bash Version When:
- Processing < 20 repositories
- Using < 20 replacement rules
- Don't want Python dependency
- Debugging/testing on a few repos

See [PERFORMANCE.md](PERFORMANCE.md) for detailed comparison.

## Support Files

- [README-PYTHON.md](README-PYTHON.md) - Python version setup and usage
- [README-BASH.md](README-BASH.md) - Bash version setup and usage
- [AUTHENTICATION.md](AUTHENTICATION.md) - Detailed auth setup guide
- [PERFORMANCE.md](PERFORMANCE.md) - Performance comparison
- [config.sh](config.sh) - Configuration file template
- [repos.txt](repos.txt) - Repository list template

## Troubleshooting

### Common Issues

**"Failed to clone repository"**
- Check `GIT_AUTH_TOKEN` is set
- Verify repository names are correct
- Ensure you have access to the repositories

**"Branch already exists"**
- Tool will automatically checkout existing branch and continue
- This is normal when re-running the script

**"No changes to commit"**
- Replacement patterns didn't match any content
- Check `FILE_PATTERNS` matches your files
- Verify search strings exist in the repositories

**"Failed to create PR"**
- Check HTTP status and error message in output
- Verify `GIT_AUTH_TOKEN` has correct permissions
- Ensure `PR_BASE_BRANCH` exists in the repository

See version-specific READMEs for more troubleshooting.

## Contributing

Suggestions for improvement:
1. Test changes thoroughly
2. Document new features
3. Submit feedback

## License

This tool is provided as-is for use in your projects. Modify as needed.
