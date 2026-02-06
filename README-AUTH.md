# Git Authentication Setup Guide

This guide explains how to set up authentication for cloning private repositories from GitHub organizations, GitLab groups, or Bitbucket workspaces.

## Authentication Methods

The script supports three authentication methods:

1. **Token Authentication (HTTPS)** - Recommended for organizations
2. **SSH Key Authentication** - Good for personal use
3. **None** - Public repositories only

## Method 1: Token Authentication (Recommended for Organizations)

### For GitHub Organizations

1. **Create a Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Name: `Batch Repo Updates`
   - Expiration: Choose based on your security policy
   - Scopes: Select ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

2. **Configure your config.sh:**
   ```bash
   GIT_AUTH_METHOD="token"
   GIT_USERNAME="your-github-username"
   GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"  # Will use environment variable
   GIT_BASE_URL="https://github.com/your-org-name"
   ```

3. **Set the token as an environment variable:**
   ```bash
   export GIT_AUTH_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ./repo_batch_update.sh
   ```

### For GitLab Groups

1. **Create a Personal Access Token:**
   - Go to https://gitlab.com/-/profile/personal_access_tokens
   - Name: `Batch Repo Updates`
   - Expiration: Set expiration date
   - Scopes: Select ✅ `read_repository` and ✅ `write_repository`
   - Click "Create personal access token"
   - Copy the token (format: `glpat-xxxxxxxxxxxxxxxxxxxx`)

2. **Configure your config.sh:**
   ```bash
   GIT_AUTH_METHOD="token"
   GIT_USERNAME="your-gitlab-username"
   GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"
   GIT_BASE_URL="https://gitlab.com/your-group-name"
   ```

3. **Set the token and run:**
   ```bash
   export GIT_AUTH_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
   ./repo_batch_update.sh
   ```

### For Bitbucket Workspaces

1. **Create an App Password:**
   - Go to https://bitbucket.org/account/settings/app-passwords/
   - Click "Create app password"
   - Label: `Batch Repo Updates`
   - Permissions: Select ✅ Repositories: Read, Write
   - Click "Create"
   - Copy the password

2. **Configure your config.sh:**
   ```bash
   GIT_AUTH_METHOD="token"
   GIT_USERNAME="your-bitbucket-username"
   GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"
   GIT_BASE_URL="https://bitbucket.org/your-workspace"
   ```

3. **Set the token and run:**
   ```bash
   export GIT_AUTH_TOKEN="your-app-password"
   ./repo_batch_update.sh
   ```

## Method 2: SSH Key Authentication

### Setup

1. **Ensure SSH keys are loaded:**
   ```bash
   # Check if ssh-agent is running and has keys
   ssh-add -l
   
   # If not, start ssh-agent and add your key
   eval $(ssh-agent -s)
   ssh-add ~/.ssh/id_rsa  # or your key file
   ```

2. **Configure your config.sh:**
   ```bash
   GIT_AUTH_METHOD="ssh"
   GIT_BASE_URL="git@github.com:your-org-name"
   # GIT_USERNAME and GIT_AUTH_TOKEN not needed for SSH
   ```

3. **Run the script:**
   ```bash
   ./repo_batch_update.sh
   ```

### SSH Key Setup for Organizations

**GitHub:**
- Add your SSH key at: https://github.com/settings/keys
- Your key must have access to the organization's repositories

**GitLab:**
- Add your SSH key at: https://gitlab.com/-/profile/keys
- Your key must have access to the group's repositories

**Bitbucket:**
- Add your SSH key at: https://bitbucket.org/account/settings/ssh-keys/
- Your key must have access to the workspace's repositories

## Method 3: No Authentication (Public Repos Only)

```bash
GIT_AUTH_METHOD="none"
GIT_BASE_URL="https://github.com/your-org-name"
```

This will only work for public repositories.

## Security Best Practices

### 1. Use Environment Variables for Tokens

**Never hardcode tokens in config.sh**

Create a `.env` file:
```bash
# .env
export GIT_AUTH_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export GIT_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # For PR creation
```

Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

Load before running:
```bash
source .env
./repo_batch_update.sh
```

### 2. Use One Token for All Operations

The script uses a single token (`GIT_AUTH_TOKEN`) for both cloning and PR creation:

```bash
# Single token for everything
export GIT_AUTH_TOKEN="ghp_xxx_single_token"
./repo_batch_update.sh
```

No need for separate `GIT_TOKEN` - one token with proper scopes is sufficient.

### 3. Set Token Expiration

- Set tokens to expire after 90 days
- Rotate tokens regularly
- Use organization policy for token expiration

### 4. Use Minimal Permissions

**For read-only operations:**
- GitHub: `repo` scope (can't be more granular for private repos)
- GitLab: `read_repository` only

**For this script (needs write):**
- GitHub: `repo` scope
- GitLab: `read_repository` + `write_repository`

### 5. Revoke Tokens After Use

If this is a one-time operation:
```bash
# After running
# Go to GitHub settings and revoke the token
```

### 6. Use Organization Secrets in CI/CD

For automated runs:

**GitHub Actions:**
```yaml
env:
  GIT_AUTH_TOKEN: ${{ secrets.ORG_GIT_TOKEN }}
```

**GitLab CI:**
```yaml
variables:
  GIT_AUTH_TOKEN: $CI_JOB_TOKEN  # Or use protected variable
```

## Troubleshooting

### "ERROR: GIT_AUTH_TOKEN is not set"

```bash
# Check if token is set
echo $GIT_AUTH_TOKEN

# If empty, set it
export GIT_AUTH_TOKEN="your_token_here"
```

### "Authentication failed" or "remote: Invalid username or password"

**Causes:**
- Token has expired
- Token doesn't have required permissions
- Username is incorrect
- Token is for wrong platform (GitHub token on GitLab, etc.)

**Solutions:**
1. Verify token hasn't expired
2. Check token has `repo` scope (GitHub) or `read_repository`+`write_repository` (GitLab)
3. Verify `GIT_USERNAME` matches your account
4. Generate a new token

### "ERROR: no SSH keys are loaded"

```bash
# Start ssh-agent and add key
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

# Verify key is loaded
ssh-add -l
```

### "Permission denied (publickey)"

For SSH authentication:
- Ensure your SSH key is added to your Git provider account
- Verify you have access to the organization/group
- Test SSH connection:
  ```bash
  ssh -T git@github.com
  # Should see: "Hi username! You've successfully authenticated..."
  ```

### Using Both Token Auth and PR Creation

The same token is used for both cloning and creating PRs - no need for separate tokens:

```bash
# In config.sh - GIT_AUTH_TOKEN is used for everything
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"

# Just set it once
export GIT_AUTH_TOKEN="ghp_xxx_single_token"
./repo_batch_update.sh
```

The token needs the same scopes regardless:
- **GitHub**: `repo` scope (covers both operations)
- **GitLab**: `api` scope (covers both operations)
- **Bitbucket**: Repository Write + Pull Request Write

## Complete Example for GitHub Organization

```bash
# 1. Create token at https://github.com/settings/tokens with 'repo' scope

# 2. Edit config.sh
cat > config.sh << 'EOF'
GIT_AUTH_METHOD="token"
GIT_USERNAME="john-doe"
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"
GIT_BASE_URL="https://github.com/acme-corp"

REPO_LIST_FILE="repos.txt"
BRANCH_NAME="security-updates"
# ... rest of config
EOF

# 3. Create repos list
cat > repos.txt << 'EOF'
frontend-app
backend-api
mobile-app
EOF

# 4. Set token and run
export GIT_AUTH_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
./repo_batch_update.sh

# 5. Check results
cat batch_update_log.txt
```

## Token Scopes Reference

### GitHub Organization Repos
Minimum required scopes:
- ✅ `repo` - Full control (required for private repos)
  - Includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

### GitLab Group Repos
Minimum required scopes:
- ✅ `read_repository` - Read access
- ✅ `write_repository` - Write access (for pushing branches)
- ✅ `api` - For creating merge requests (if CREATE_PR=true)

### Bitbucket Workspace Repos
Minimum required permissions:
- ✅ Repositories: Read
- ✅ Repositories: Write
- ✅ Pull requests: Write (if CREATE_PR=true)

---

## Corporate Proxy / Firewall Configuration

If your organization uses a corporate proxy or firewall, you may need additional configuration for PR creation to work.

### Symptoms of Proxy Issues

- PR creation fails with connection errors
- GitHub API returns 407 (Proxy Authentication Required)
- Timeouts when trying to create PRs
- Works with `git` commands but fails with API calls

### Proxy Configuration

#### Environment Variables (Recommended)

```bash
# Set proxy settings
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\your-username"
export PROXY_PASSWORD="your-password"

# Run script
python3 repo_batch_update.py
```

**Note:** For domain accounts, use format: `DOMAIN\username` or `domain\username`

#### In config.sh

```bash
# In config.sh
USE_PROXY=true
PROXY_URL="http://proxy.company.com:8080"
PROXY_USERNAME="DOMAIN\username"
PROXY_PASSWORD="your_password"
```

**Security Note:** Using environment variables is more secure than storing credentials in config files.

### NTLM Proxy Support

Many corporate proxies use NTLM authentication. For best compatibility:

```bash
# Install NTLM support
pip install requests-ntlm

# Set credentials
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="your-password"

# Run script
python3 repo_batch_update.py
```

The script will automatically use NTLM authentication if `requests-ntlm` is installed.

### Testing Proxy Configuration

Test if your proxy is working:

```bash
# Test with curl (matches working command format)
curl -v -x http://proxy.company.com:8080 \
  -U "DOMAIN\username:password" \
  -L api.github.com \
  --proxy-ntlm

# Should return GitHub API response
```

### Proxy Configuration Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PROXY_URL` | Proxy server address | `http://proxy.company.com:8080` |
| `PROXY_USERNAME` | Domain\username | `DOMAIN\jdoe` |
| `PROXY_PASSWORD` | Your password | `your_password` |
| `USE_PROXY` | Enable proxy (auto if URL set) | `true` |

### Troubleshooting Proxy Issues

**"407 Proxy Authentication Required"**
```bash
# Install NTLM support
pip install requests-ntlm

# Verify credentials are set
echo $PROXY_USERNAME
echo $PROXY_URL
```

**"Connection timeout"**
```bash
# Test proxy with curl
curl -v -x $PROXY_URL https://api.github.com

# Verify proxy URL includes port
export PROXY_URL="http://proxy.company.com:8080"
```

**Git operations work but PR creation fails**
```bash
# Git uses different network path than Python
# Configure proxy for Python only:
export PROXY_URL="http://proxy.company.com:8080"
export PROXY_USERNAME="DOMAIN\username"
export PROXY_PASSWORD="password"
```

### Git Through Proxy (Optional)

If you also need Git operations to go through proxy:

```bash
# Configure Git proxy globally
git config --global http.proxy http://proxy.company.com:8080
git config --global https.proxy http://proxy.company.com:8080

# Or with authentication
git config --global http.proxy http://username:password@proxy.company.com:8080
```

### Corporate Firewall Whitelist

If PR creation still fails, request IT to whitelist:
- `api.github.com` (port 443)
- `github.com` (port 443)
- Your Git host URL
