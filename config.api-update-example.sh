#!/bin/bash

# Configuration for API endpoint updates

REPO_LIST_FILE="api_repos.txt"
BRANCH_NAME="update-api-endpoints"
GIT_BASE_URL="https://github.com/mycompany"
WORK_DIR="./repos_temp"
LOG_FILE="./logs/api_update_$(date +%Y%m%d).txt"

COMMIT_MESSAGE="Update API endpoints to v2

- Migrated from v1 to v2 endpoints
- Updated API domain
- Refreshed API keys

Refs: JIRA-1234"

declare -a REPLACEMENTS=(
    "api.old-domain.com/v1|api.new-domain.com/v2"
    "OLD_API_KEY|NEW_API_KEY"
)

FILE_PATTERNS="*.py *.js *.java"

# PR Configuration
CREATE_PR=true
GIT_PLATFORM="github"
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

PR_BASE_BRANCH="develop"
GIT_TOKEN="${GIT_TOKEN:-}"
