# Repo Batch Update Tool - Python Version

High-performance Python implementation for processing many repositories with many replacement rules.

**⚡ 50-100x faster than the bash version**

## When to Use Python Version

✅ **Use Python version when:**
- Processing 50+ repositories
- Using 20+ replacement rules
- Total time would be > 30 minutes
- Need maximum performance

**Performance:**
- 200 repos × 110 rules: ~7-14 hours (vs ~720 hours in bash!)
- 10 repos × 50 rules: ~2-5 minutes (vs ~30-60 minutes in bash)

See [PERFORMANCE.md](PERFORMANCE.md) for detailed benchmarks.

## Prerequisites

### Required
- Python 3.6 or higher
- Git installed and configured
- `requests` library (for PR creation)

### Platform Support

**Linux:** Native support, works perfectly
**macOS:** Native support, works perfectly
**Windows:** Multiple options available

### Check Prerequisites

```bash
# Check Python version
python3 --version
# Should show 3.6.0 or higher

# Check Git
git --version

# Check pip
pip3 --version
```

## Windows Installation

The Python version works great on Windows! Choose the option that works best for you:

### Option 1: Native Windows Python (Recommended for Windows)

**Easiest option - runs directly on Windows without WSL**

1. **Install Python for Windows**
   - Download from https://www.python.org/downloads/
   - During installation: ✅ Check "Add Python to PATH"
   - Recommended: Python 3.9 or higher

2. **Install Git for Windows**
   - Download from https://git-scm.com/download/win
   - Use default settings

3. **Install dependencies**
   
   Open Command Prompt or PowerShell:
   ```powershell
   pip install requests
   ```

4. **Run the script**
   ```powershell
   # Set authentication token
   $env:GIT_AUTH_TOKEN="your_token_here"
   
   # Run script
   python repo_batch_update.py
   
   # Or with custom config
   python repo_batch_update.py --config .\config.sh
   ```

**Note on config.sh:** The script will parse the bash config file even on Windows. Just make sure line endings are Unix-style (LF not CRLF).

### Option 2: WSL (Windows Subsystem for Linux)

**Best for consistency with Linux/macOS**

1. **Install WSL**
   
   Open PowerShell as Administrator:
   ```powershell
   wsl --install
   ```

2. **Restart computer** when prompted

3. **Open "Ubuntu" from Start Menu**
   - First launch takes a few minutes
   - Create username and password

4. **Install prerequisites in WSL**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   pip3 install requests
   ```

5. **Access Windows files from WSL**
   ```bash
   # Your Windows drives are at /mnt/
   cd /mnt/c/Users/YourUsername/Documents/batch-update
   
   # Or convert Windows path
   cd $(wslpath "C:\Users\YourUsername\Documents\batch-update")
   ```

6. **Run the script**
   ```bash
   chmod +x repo_batch_update.py
   export GIT_AUTH_TOKEN="your_token_here"
   ./repo_batch_update.py
   ```

### Option 3: Git Bash

**Quick option if you already have Git for Windows**

1. **Install Git for Windows** (includes Git Bash)
   - Download from https://git-scm.com/download/win

2. **Install Python** (as in Option 1)

3. **Open Git Bash**

4. **Install dependencies**
   ```bash
   pip install requests
   ```

5. **Run the script**
   ```bash
   export GIT_AUTH_TOKEN="your_token_here"
   python repo_batch_update.py
   ```

### Windows Recommendations

| Your Situation | Best Option |
|----------------|-------------|
| Just want it to work | Native Windows Python (Option 1) |
| Need Linux compatibility | WSL (Option 2) |
| Already use Git Bash | Git Bash (Option 3) |
| Using both Bash and Python versions | WSL (Option 2) |

## Installation

### 1. Install Python (if needed)

**Ubuntu/Debian (including WSL):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

**Windows (Native):**
1. Download Python from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"
3. Open Command Prompt and verify:
   ```powershell
   python --version
   pip --version
   ```

**Windows (WSL):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### 2. Install Dependencies

```bash
pip3 install requests

# Optional: For corporate proxy with NTLM authentication
pip3 install requests-ntlm
```

**For corporate environments with proxies:** See the Proxy Configuration section below.

### 3. Make Script Executable

```bash
chmod +x repo_batch_update.py
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
   ./repo_batch_update.py
   
   # Or with custom config
   ./repo_batch_update.py --config ./my-config.sh
   ```

## Usage

### Basic Usage

```bash
# Use default config.sh
python3 repo_batch_update.py

# With custom config
python3 repo_batch_update.py --config ./config.api-update.sh

# With authentication token
export GIT_AUTH_TOKEN="ghp_xxxxxxxxxxxx"
python3 repo_batch_update.py
```

### Advanced Usage

```bash
# Process only first 5 repos (for testing)
head -5 repos.txt > test_repos.txt
REPO_LIST_FILE="test_repos.txt" python3 repo_batch_update.py

# Run in background and log output
nohup python3 repo_batch_update.py > update.log 2>&1 &

# Follow progress
tail -f update.log
```

## Configuration

The Python version uses the **same `config.sh` file** as the bash version. No changes needed!

The script automatically:
- Sources the bash config file
- Extracts all variables
- Parses the `REPLACEMENTS` array
- Uses identical settings

See [README-MAIN.md](README-MAIN.md) for configuration details.

## Proxy Configuration (Corporate Firewalls)

If your organization uses a corporate proxy, you'll need to configure proxy settings for PR creation.

### Quick Setup

```bash
# Set proxy credentials
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="your-password"

# Install NTLM support (for most corporate proxies)
pip3 install requests-ntlm

# Run script
python3 repo_batch_update.py
```

### Configuration Options

**Option 1: Environment Variables (Recommended)**
```bash
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="password"
```

**Option 2: In config.sh**
```bash
USE_PROXY=true
PROXY_URL="http://proxy.company.com:8080"
PROXY_USERNAME="DOMAIN\username"
PROXY_PASSWORD="password"
```

### Testing Proxy

```bash
# Test with curl (your working command)
curl -v -x http://proxy.company.com:8080 \
  -U "DOMAIN\username:password" \
  -L api.github.com \
  --proxy-ntlm
```

If curl works, the Python script should work with the same credentials.

### NTLM Authentication

Most corporate proxies use NTLM. Install support:

```bash
pip3 install requests-ntlm
```

The script automatically detects and uses NTLM if this package is installed.

See [AUTHENTICATION.md](AUTHENTICATION.md#corporate-proxy--firewall-configuration) for detailed proxy troubleshooting.

## Features

### All Standard Features

Everything from the main README, plus:

### Python-Specific Advantages

1. **Much Faster Performance**
   - Pre-compiled regex patterns
   - Single process (no subprocess overhead)
   - Efficient in-memory processing

2. **Better Error Handling**
   - Gracefully handles Unicode errors
   - More specific exception messages
   - Cleaner error recovery

3. **More Reliable**
   - No shell quoting issues
   - Better special character handling
   - Predictable behavior

4. **Easier to Extend**
   - Simple to add parallel processing
   - Easy to add progress bars
   - Clean codebase for modifications

## Output Example

```
[INFO] =========================================
[INFO] Repo Batch Update Script (Python)
[INFO] =========================================
[INFO] Starting at: 2026-02-05 14:30:00

[INFO] Configuration:
[INFO]   Config file: ./config.sh
[INFO]   Repo list: repos.txt
[INFO]   Branch name: update-strings
[INFO]   Base URL: https://github.com/myorg
[INFO]   Replacement rules: 110

[INFO] Setting up Git authentication...
[INFO] Authentication method: token
[INFO] Username: myusername
[INFO] Token: ghp_abc123... (truncated)
[INFO] ✓ Git authentication configured for github.com

[INFO] Found 200 repositories to process

[INFO] =========================================
[INFO] Repository 1 of 200: my-first-repo
[INFO] =========================================
[INFO] Cloning repository...
[INFO] ✓ Cloned successfully
[INFO] Creating branch: update-strings
[INFO] ✓ Branch ready

[INFO] Performing string replacements...
[INFO] File patterns: *.py *.js
[INFO] Case sensitive: True
[INFO] Number of replacement rules: 110

[INFO] Found 127 files to process

[INFO] ----------------------------------------
[INFO] Rule 1/110: 'oldString1' → 'newString1'
[INFO] ----------------------------------------
[INFO]   📝 File: src/config.py (3 occurrence(s))
[INFO]      Line 15: API_URL = "oldString1/endpoint"
[INFO]      Line 47: DEFAULT_URL = "oldString1/default"
[INFO]      Line 89: BACKUP_URL = "oldString1/backup"
[INFO]      ✓ Replaced 3 occurrence(s)

[INFO]   Summary for this rule:
[INFO]     Files modified: 5
[INFO]     Total replacements: 12

[... continues for all 110 rules ...]

[INFO] ========================================
[INFO] REPLACEMENT SUMMARY
[INFO] ========================================
[INFO] Total files searched: 127
[INFO] Total files modified: 23
[INFO] Total replacements made: 156

[INFO] Staging changes...
[INFO] Creating commit...
[INFO] ✓ Committed
[INFO] Pushing to remote...
[INFO] ✓ Pushed

[INFO] =========================================
[INFO] Creating Pull Request for my-first-repo
[INFO] =========================================
[INFO] Creating GitHub PR for: myorg/my-first-repo
[INFO] API endpoint: https://api.github.com/repos/myorg/my-first-repo/pulls
[INFO] HTTP Status: 201
[INFO] ✓ Pull Request created: https://github.com/myorg/my-first-repo/pull/42

[INFO] ✓ Successfully processed my-first-repo

[... continues for all 200 repos ...]

[INFO] =========================================
[INFO] SUMMARY
[INFO] =========================================
[INFO] Completed at: 2026-02-05 22:45:00
[INFO] Total repositories: 200
[INFO] Successful: 195
[INFO] Failed: 5

[INFO] Detailed log saved to: ./batch_update_log.txt
[INFO] ✓ All repositories processed successfully!
```

## Performance Tips

### 1. Test First on Small Batch

```bash
# Create test list with 2-3 repos
head -3 repos.txt > test_repos.txt

# Update config
REPO_LIST_FILE="test_repos.txt"

# Run and verify
python3 repo_batch_update.py
```

### 2. Monitor Progress

```bash
# Run in background
python3 repo_batch_update.py > output.log 2>&1 &

# Watch progress
tail -f output.log

# Check how many repos processed
grep "Successfully processed" output.log | wc -l
```

### 3. Process in Batches

For very large repo lists, split into batches:

```bash
# Split repos.txt into batches of 50
split -l 50 repos.txt batch_

# Process each batch
for batch in batch_*; do
    REPO_LIST_FILE="$batch" python3 repo_batch_update.py
done
```

## Troubleshooting

### Windows-Specific Issues

**"python3: command not found" on Windows**

On Windows, use `python` instead of `python3`:
```powershell
# Check version
python --version

# Run script
python repo_batch_update.py

# Create alias in PowerShell (optional)
Set-Alias python3 python
```

**"pip3: command not found" on Windows**
```powershell
# Use 'pip' instead of 'pip3'
pip install requests
```

**Config file line ending issues (CRLF vs LF)**
```powershell
# Option 1: Use VS Code - Change line endings to LF
# Option 2: In WSL, use dos2unix:
sudo apt install dos2unix
dos2unix config.sh
```

**"Permission denied" on Windows**
```powershell
# No chmod needed on native Windows
python repo_batch_update.py

# In WSL, use chmod:
chmod +x repo_batch_update.py
```

**Setting environment variables on Windows**
```powershell
# PowerShell
$env:GIT_AUTH_TOKEN="your_token_here"
python repo_batch_update.py

# Command Prompt
set GIT_AUTH_TOKEN=your_token_here
python repo_batch_update.py
```

### General Issues

### "ModuleNotFoundError: No module named 'requests'"

```bash
pip3 install requests

# If permission error
pip3 install --user requests
```

### "python3: command not found"

```bash
# Ubuntu/Debian
sudo apt-get install python3

# macOS
brew install python3
```

### "SyntaxError" or Python version too old

```bash
# Check version
python3 --version

# Need 3.6 or higher. Install newer version:
# Ubuntu/Debian
sudo apt-get install python3.9

# macOS
brew install python@3.9
```

### Script seems stuck

The script is likely processing a large number of files. Check progress:

```bash
# In another terminal
tail -f batch_update_log.txt

# Or check git processes
ps aux | grep git
```

### Config parsing errors

```bash
# Validate config file syntax
bash -n config.sh

# Check for errors
echo $?  # Should be 0
```

### Unicode/Encoding errors

The Python version handles these automatically. Files with encoding issues are skipped with a warning.

### Proxy / Firewall Issues

**"407 Proxy Authentication Required"**
```bash
# Install NTLM support
pip3 install requests-ntlm

# Set proxy credentials
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"  
export PROXY_PASSWORD="your-password"
```

**"Connection timeout" or "Cannot connect to GitHub API"**
```bash
# Test proxy connection
curl -v -x $PROXY_URL https://api.github.com

# Set proxy settings
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="password"
```

**PR creation fails but git operations work**
```bash
# Git and Python use different network paths
# Configure Python proxy separately:
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="password"

# Install NTLM support
pip3 install requests-ntlm
```

See [AUTHENTICATION.md](AUTHENTICATION.md#corporate-proxy--firewall-configuration) for detailed proxy setup.

## Comparison with Bash Version

| Feature | Python | Bash |
|---------|--------|------|
| Speed (200 repos, 110 rules) | ~10 hours | ~720 hours |
| Dependencies | Python 3.6+, requests | Just bash |
| Error handling | Excellent | Good |
| Unicode support | Native | Limited |
| Code clarity | High | Medium |
| Extensibility | Easy | Hard |
| Platform support | All | Linux/Mac |

## Future Enhancements

The Python version makes these easy to add:

### Parallel Processing

Process multiple repos simultaneously:

```python
# In the code, replace sequential processing with:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(lambda r: process_repo(r, config, log_entries), repos)
```

### Progress Bar

```bash
pip3 install tqdm

# Add to code:
from tqdm import tqdm
for repo in tqdm(repos, desc="Processing repos"):
    process_repo(repo, config, log_entries)
```

### Retry Logic

```python
for attempt in range(3):
    try:
        if process_repo(repo, config, log_entries):
            break
    except Exception as e:
        if attempt == 2:
            raise
        time.sleep(5)
```

## Migration from Bash

1. **Install Python and dependencies** (see Installation section)

2. **Test on same config** - no changes needed!
   ```bash
   # Bash version
   ./repo_batch_update.sh
   
   # Python version (same config!)
   python3 repo_batch_update.py
   ```

3. **Compare results** - both should produce identical output

4. **Switch to Python** for faster processing

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
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip3 install requests
      
      - name: Run batch update
        env:
          GIT_AUTH_TOKEN: ${{ secrets.BATCH_UPDATE_TOKEN }}
        run: python3 repo_batch_update.py
```

### GitLab CI

```yaml
batch_update:
  image: python:3.9
  before_script:
    - pip install requests
  script:
    - export GIT_AUTH_TOKEN=$GITLAB_TOKEN
    - python3 repo_batch_update.py
  only:
    - schedules
```

## Getting Help

1. Check this README for Python-specific issues
2. Check [README-MAIN.md](README-MAIN.md) for general functionality
3. Check [AUTHENTICATION.md](AUTHENTICATION.md) for auth issues
4. Review error messages - Python gives detailed tracebacks

## License

This tool is provided as-is for use in your projects. Modify as needed.
