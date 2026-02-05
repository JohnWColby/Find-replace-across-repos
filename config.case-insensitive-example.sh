#!/bin/bash

# Example: Case-Insensitive URL Updates
# This config shows how to replace URLs regardless of case

REPO_LIST_FILE="repos.txt"
BRANCH_NAME="normalize-urls"
GIT_BASE_URL="https://github.com/mycompany"
WORK_DIR="./repos_temp"
LOG_FILE="./url_normalization.txt"

COMMIT_MESSAGE="Normalize API URLs to lowercase

All API URLs have been normalized to use lowercase.
This ensures consistent URL handling across the codebase.

- api.example.com (was API.EXAMPLE.COM, Api.Example.Com, etc.)
- Updated in configuration files, documentation, and code"

# Case-insensitive replacements
# Will match: API.EXAMPLE.COM, api.example.com, Api.Example.Com, etc.
declare -a REPLACEMENTS=(
    "API.EXAMPLE.COM|api.example.com"
    "STAGING.EXAMPLE.COM|staging.example.com"
    "DEV.EXAMPLE.COM|dev.example.com"
)

# Set to false for case-insensitive matching
CASE_SENSITIVE=false

FILE_PATTERNS="*.py *.js *.yaml *.yml *.json *.md"

# PR Configuration
CREATE_PR=true
GIT_PLATFORM="github"
PR_TITLE="Normalize API URLs to lowercase"
PR_DESCRIPTION="## Summary
Normalizes all API URLs to use lowercase format for consistency.

## Changes
All instances of API URLs have been converted to lowercase, regardless of original casing:
- API.EXAMPLE.COM → api.example.com
- Api.Example.Com → api.example.com
- STAGING URLs normalized
- DEV URLs normalized

## Impact
- No functional changes (URLs are case-insensitive in DNS)
- Improves code consistency and readability
- Prevents confusion from mixed-case URLs"

PR_BASE_BRANCH="main"

# Authentication
GIT_AUTH_METHOD="token"
GIT_USERNAME="your-username"
GIT_AUTH_TOKEN="${GIT_AUTH_TOKEN:-}"
