#!/bin/bash

# ============================================================================
# BATCH UPDATE CONFIGURATION FILE
# ============================================================================
# Edit this file to customize your batch update settings.
# This file is sourced by repo_batch_update.sh
# ============================================================================

# File containing repo names (one per line)
REPO_LIST_FILE="repos.txt"

# Branch name to create
BRANCH_NAME="update-strings"

# Git remote base URL (will be combined with repo name)
# Examples:
#   For GitHub: "https://github.com/username"
#   For GitLab: "https://gitlab.com/username"
#   For SSH: "git@github.com:username"
GIT_BASE_URL="https://github.com/yourusername"

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

# GitHub/GitLab/Bitbucket Personal Access Token
# For GitHub: Create at https://github.com/settings/tokens (needs 'repo' scope)
# For GitLab: Create at https://gitlab.com/-/profile/personal_access_tokens (needs 'api' scope)
# For Bitbucket: Create at https://bitbucket.org/account/settings/app-passwords/ (needs 'pullrequest:write' scope)
# You can also set this as an environment variable: export GIT_TOKEN="your_token_here"
GIT_TOKEN="${GIT_TOKEN:-}"  # Will use environment variable if set, otherwise empty
