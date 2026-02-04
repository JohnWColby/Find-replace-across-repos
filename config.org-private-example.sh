#!/bin/bash

# Configuration for GitHub Organization Private Repositories

# ============================================================================
# GIT AUTHENTICATION CONFIGURATION
# ============================================================================

# Use token authentication for HTTPS cloning
GIT_AUTH_METHOD="token"

# Your GitHub username
GIT_USERNAME="your-github-username"

# GitHub Personal Access Token (with 'repo' scope)
# Generate at: https://github.com/settings/tokens
# Required scopes: repo (full control of private repositories)
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"  # Set via environment: export GIT_AUTH_TOKEN="ghp_xxx"

# ============================================================================
# REPOSITORY CONFIGURATION
# ============================================================================

REPO_LIST_FILE="org_repos.txt"
BRANCH_NAME="update-dependencies"

# Organization URL (HTTPS format required for token auth)
GIT_BASE_URL="https://github.com/your-org-name"

WORK_DIR="./repos_temp"
LOG_FILE="./org_update_$(date +%Y%m%d).txt"

COMMIT_MESSAGE="Update dependencies to latest versions

- Updated npm packages
- Fixed security vulnerabilities
- Bumped minimum Node version

Refs: SEC-2024-001"

declare -a REPLACEMENTS=(
    '"node": ">=14.0.0"|"node": ">=18.0.0"'
    '"lodash": "^4.17.20"|"lodash": "^4.17.21"'
)

FILE_PATTERNS="package.json"

# ============================================================================
# PULL REQUEST CONFIGURATION
# ============================================================================

CREATE_PR=true
GIT_PLATFORM="github"

PR_TITLE="[Security] Update dependencies to latest versions"
PR_DESCRIPTION="## Summary
Updates dependencies across all repositories to address security vulnerabilities.

## Changes
- Node.js minimum version: 14 → 18
- Updated lodash to patch CVE-2021-23337

## Testing
- [x] Dependencies install successfully
- [x] Existing tests pass
- [x] Security scan shows no critical issues

## Review Checklist
- [ ] Check for breaking changes in changelogs
- [ ] Verify CI/CD pipelines pass

Related: SEC-2024-001"

PR_BASE_BRANCH="main"

# Use the same token for PR creation (needs 'repo' scope)
GIT_TOKEN="${GIT_AUTH_TOKEN:-}"
