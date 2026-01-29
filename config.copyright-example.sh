#!/bin/bash

# Configuration for copyright year updates

REPO_LIST_FILE="all_repos.txt"
BRANCH_NAME="update-copyright-2026"
GIT_BASE_URL="https://github.com/mycompany"
WORK_DIR="./repos_temp"
LOG_FILE="./copyright_update_2026.txt"

COMMIT_MESSAGE="Update copyright year to 2026"

declare -a REPLACEMENTS=(
    "Copyright 2025|Copyright 2026"
    "© 2025|© 2026"
    "Copyright (c) 2025|Copyright (c) 2026"
)

FILE_PATTERNS="*.py *.js *.java *.go *.md *.html"

# PR Configuration
CREATE_PR=true
GIT_PLATFORM="github"
PR_TITLE="Update copyright year to 2026"
PR_DESCRIPTION="Annual update of copyright year in all source files."
PR_BASE_BRANCH="main"
GIT_TOKEN="${GIT_TOKEN:-}"
