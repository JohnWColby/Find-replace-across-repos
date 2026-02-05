#!/bin/bash

# ============================================================================
# BATCH UPDATE CONFIGURATION FILE
# ============================================================================
# Edit this file to customize your batch update settings.
# This file is sourced by repo_batch_update.sh
# ============================================================================

# ============================================================================
# GIT AUTHENTICATION CONFIGURATION
# ============================================================================

# Git authentication method: "token", "ssh", or "none"
# - "token": Uses GitHub/GitLab personal access token for HTTPS authentication
# - "ssh": Uses SSH keys (requires SSH agent to be running with keys loaded)
# - "none": No authentication (for public repos only)
GIT_AUTH_METHOD="token"

# Git username for HTTPS authentication (only needed if GIT_AUTH_METHOD="token")
# For GitHub: your GitHub username
# For GitLab: your GitLab username
# For Bitbucket: your Bitbucket username
GIT_USERNAME="your-username"

# Git token for HTTPS authentication (only needed if GIT_AUTH_METHOD="token")
# Can also be set via environment variable: export GIT_AUTH_TOKEN="your_token"
# For GitHub: Create at https://github.com/settings/tokens (needs 'repo' scope)
# For GitLab: Create at https://gitlab.com/-/profile/personal_access_tokens (needs 'read_repository' scope)
# For Bitbucket: Use app password from https://bitbucket.org/account/settings/app-passwords/
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"

# ============================================================================
# REPOSITORY CONFIGURATION
# ============================================================================

# File containing repo names (one per line)
REPO_LIST_FILE="repos.txt"

# Branch name to create
BRANCH_NAME="update-strings"

# Git remote base URL (will be combined with repo name)
# Examples:
#   For GitHub HTTPS: "https://github.com/org-name"
#   For GitHub SSH: "git@github.com:org-name"
#   For GitLab HTTPS: "https://gitlab.com/org-name"
#   For GitLab SSH: "git@gitlab.com:org-name"
GIT_BASE_URL="https://github.com/your-org"

# Working directory for cloning repos (will be created if it doesn't exist)
WORK_DIR="./repos_temp"

# Log file for tracking completed repos and PR URLs
LOG_FILE="./batch_update_log.txt"

# Commit message (supports multi-line)
# For a single-line message, use:
# COMMIT_MESSAGE="Update string replacements across repository"
#
# For a multi-line message, use this format:
COMMIT_MESSAGE="Update string replacements across repository

This commit updates several deprecated strings:
- Updated API endpoints
- Fixed configuration values
- Modernized function names

Refs: #1234"

# Find/Replace mappings (add as many as needed)
# Format: "SEARCH_STRING|REPLACEMENT_STRING"
declare -a REPLACEMENTS=(
    "oldString1|newString1"
    "oldString2|newString2"
    "TODO: update this|DONE: updated"
)

# Case sensitivity for find/replace operations (true/false)
# true = Case-sensitive (default): "API" matches "API" but not "api" or "Api"
# false = Case-insensitive: "API" matches "API", "api", "Api", "aPi", etc.
CASE_SENSITIVE=true

# File extensions to process (leave as "*" to process all files)
# Example: "*.py *.js *.md"
FILE_PATTERNS="*"

# ============================================================================
# PULL REQUEST CONFIGURATION
# ============================================================================

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

# Base branch to target for PR (usually 'main' or 'master')
PR_BASE_BRANCH="main"

# NOTE: PR creation uses the same token as Git authentication (GIT_AUTH_TOKEN)
# No separate token needed - the token with 'repo' scope can do both
